"""Audit final de couverture officielle du parcours « AMPCR — Pratique écrite » (ticket #235).

Une exigence AP-xx n'est « prouvée » que si les preuves suivantes sont TOUTES réunies dans le
contenu réellement publié (cours rendus et banques de questions, ceux que `app.seed` et
`import_practical_bank` installent) — jamais sur la seule déclaration du plan :

1. chaque cours PRxx que le plan rattache à l'exigence est rédigé (`PRACTICAL_COURSES`) ;
2. le texte de ces cours contient chaque terme-témoin de `REQUIREMENT_TERMS` (la notion
   officielle y est réellement enseignée, pas seulement citée dans un titre de plan) ;
3. au moins un exercice corrigé (« S'entraîner ») porte l'exigence ;
4. au moins une question d'un examen blanc EX01–EX06 porte l'exigence.

`proven_requirement_ids()` alimente le test qui garde `VALIDATED_REQUIREMENT_IDS` (plan)
aligné : la matrice ne peut afficher « validé » que pour une exigence prouvée ici. La
validation pédagogique finale reste celle du propriétaire.
"""

import html
import importlib
import re
from dataclasses import dataclass
from functools import cache, lru_cache

from app.v1 import ampcr_pratique_plan as plan
from app.v1.ampcr_pratique_bank import PRACTICAL_COURSES_BY_CODE

AUDIT_TICKET = 235
AUDIT_DATE = "2026-10-27"

# Termes-témoins par exigence : tous doivent figurer dans le texte des cours liés (casse
# ignorée). Choisis dans le libellé officiel (pp. 5-6) ; une notion absente fait échouer
# l'audit au lieu d'être déclarée couverte.
REQUIREMENT_TERMS: dict[str, tuple[str, ...]] = {
    "AP-01": ("unité centrale", "périphérique", "carte mère"),
    "AP-02": ("processeur", "RAM", "ROM", "BIOS", "UEFI"),
    "AP-03": ("disque dur", "SSD", "formatage", "défragmentation"),
    "AP-04": ("puissance", "80 PLUS", "ATX"),
    "AP-05": ("entrée", "sortie", "pilote"),
    "AP-06": ("USB", "HDMI", "SATA"),
    "AP-07": ("socket", "chipset", "slot"),
    "AP-08": ("Windows", "Linux", "macOS"),
    "AP-09": ("message", "erreur", "code"),
    "AP-10": ("installation", "partition", "pilote", "Windows", "Linux"),
    "AP-11": ("paramètre", "commande", "ipconfig", "systemctl"),
    "AP-12": ("interface graphique", "ligne de commande"),
    "AP-13": ("message", "interpréter", "intervention"),
    "AP-14": ("montage", "démontage", "reconditionnement"),
    "AP-15": ("hypothèse", "test", "panne"),
    "AP-16": ("vocabulaire", "glossaire"),
    "AP-17": ("compatibilité",),
    "AP-18": ("UTP", "FTP", "STP", "coaxial"),
    "AP-19": ("débit", "Gb/s", "Mb/s"),
    "AP-20": ("atténuation", "impédance", "blindage", "parasite", "100 m"),
    "AP-21": ("fibre", "monomode", "multimode", "atténuation", "LC"),
    "AP-22": ("fibre", "cuivre", "comparaison"),
    "AP-23": ("topologie", "étoile", "bus", "anneau"),
    "AP-24": ("domaine", "groupe de travail", "compte", "groupe"),
    "AP-25": ("partage", "imprimante", "dossier"),
    "AP-26": ("partage", "réseau", "document"),
    "AP-27": ("permission", "droit", "NTFS"),
    "AP-28": ("croisé", "MDI-X", "deux PC"),
    "AP-29": ("TCP/IP", "OSI", "NetBEUI"),
    "AP-30": ("adresse IP", "adresse MAC", "masque", "ipconfig"),
    "AP-31": ("hub", "switch", "passerelle", "routeur", "modem"),
    "AP-32": ("Internet", "DNS", "passerelle", "ping"),
    "AP-33": ("Wi-Fi", "WPA2", "WPA3", "répéteur", "chiffrement"),
    "AP-34": ("RJ45", "T568A", "T568B", "blanc/orange", "sertir"),
    "AP-35": ("BNC", "50 Ω", "terminaison", "sertir"),
    "AP-36": ("câblage", "baie", "panneau de brassage", "plan"),
    "AP-37": ("accès au réseau", "ping", "câble"),
    "AP-38": ("mini-réseau", "switch", "adresse"),
    "AP-C01": ("justifi", "compte rendu"),
    "AP-C02": ("ESD", "bracelet", "débrancher"),
    "AP-C03": ("sauvegarde", "autorisation", "confidentialité"),
}

_TAG = re.compile(r"<[^>]+>")


def _plain(markup: str) -> str:
    return html.unescape(_TAG.sub(" ", markup))


@cache
def course_text(code: str) -> str:
    """Texte du cours tel que publié (blocs rendus par `<code>_course_sections`, balises ôtées)."""
    module = importlib.import_module(f"app.v1.ampcr_pratique_{code.lower()}_course")
    sections = getattr(module, f"{code.lower()}_course_sections")()
    return "\n".join(f"{title}\n{_plain(body)}" for title, body in sections)


@dataclass(frozen=True)
class RequirementEvidence:
    requirement: plan.Requirement
    course_codes: tuple[str, ...]  # cours liés par le plan
    missing_courses: tuple[str, ...]  # cours liés non rédigés
    missing_exam_codes: tuple[str, ...]  # examens blancs liés non rédigés
    missing_terms: tuple[str, ...]  # termes-témoins absents du texte des cours liés
    practice_items: tuple[str, ...]  # « PR01/E03 » : exercices corrigés portant l'exigence
    mini_exam_items: tuple[str, ...]  # questions des mini-examens PRxx
    mock_exam_items: tuple[str, ...]  # questions des examens blancs EX01–EX06

    @property
    def proven(self) -> bool:
        return (
            bool(self.course_codes)
            and not self.missing_courses
            and not self.missing_exam_codes
            and not self.missing_terms
            and bool(self.practice_items)
            and bool(self.mock_exam_items)
        )


def requirement_evidence(requirement_id: str) -> RequirementEvidence:
    requirement = plan.REQUIREMENTS_BY_ID[requirement_id]
    course_codes = tuple(c.code for c in plan.courses_for_requirement(requirement_id))
    exam_codes = tuple(e.code for e in plan.exercises_for_requirement(requirement_id))
    missing_courses = tuple(c for c in course_codes if c not in PRACTICAL_COURSES_BY_CODE)
    text = " ".join(course_text(c) for c in course_codes if c not in missing_courses).casefold()
    missing_terms = tuple(
        t for t in REQUIREMENT_TERMS.get(requirement_id, ()) if t.casefold() not in text
    )
    practice, mini_exam, mock_exam = [], [], []
    for course in PRACTICAL_COURSES_BY_CODE.values():
        for item in course.items:
            if requirement_id not in item.requirement_ids:
                continue
            ref = f"{course.code}/{item.key}"
            if course.code.startswith("EX"):
                mock_exam.append(ref)
            elif item.usage == "exam":
                mini_exam.append(ref)
            else:
                practice.append(ref)
    return RequirementEvidence(
        requirement=requirement,
        course_codes=course_codes,
        missing_courses=missing_courses,
        missing_exam_codes=tuple(e for e in exam_codes if e not in PRACTICAL_COURSES_BY_CODE),
        missing_terms=missing_terms,
        practice_items=tuple(practice),
        mini_exam_items=tuple(mini_exam),
        mock_exam_items=tuple(mock_exam),
    )


@lru_cache(maxsize=1)
def audit_rows() -> tuple[RequirementEvidence, ...]:
    return tuple(requirement_evidence(r.id) for r in plan.ALL_REQUIREMENTS)


def proven_requirement_ids() -> frozenset[str]:
    return frozenset(e.requirement.id for e in audit_rows() if e.proven)


def evidence_by_id() -> dict[str, RequirementEvidence]:
    return {e.requirement.id: e for e in audit_rows()}
