"""Banque des cours du parcours « AMPCR — Pratique écrite » (ticket #193 : PR06 ; #194 : PR11 ;
#197 : PR15).

Branchement sur le moteur de sessions existant, sans nouveau système :
- un cours pratique est une UAA du module `AMPCR-PRATIQUE` (slug `ampcr-pratique-pr06`) ;
- `PRACTICAL_COURSES` liste les cours réellement rédigés (jamais un emplacement vide) et
  leur contexte pédagogique de correction (`PedagogicalContext`) ;
- les questions sont importées à la demande (`import_practical_bank`, idempotent), avec
  leurs documents structurés (tableaux) ;
- **réserves séparées** : `QuestionVersion.prompt_version` vaut
  `ampcr-pratique-<code>:practice` (exercices du cours, « S'entraîner ») ou
  `…:exam` (mini-examen, « Examen blanc ») ; `restrict_to_mode` filtre la sélection de la
  banque selon le mode de la session. Les questions des autres matières ne portent pas ce
  préfixe et ne sont jamais filtrées ;
- **pas de génération IA** pour ces cours (`is_practical_code`) : l'épreuve pratique exige
  des questions vérifiées, contextualisées et barémées ; la correction reste celle du moteur
  (IA batch avec le barème, correction locale pour la classification).
"""

from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.ai.schemas import PedagogicalContext
from app.models import UAA, Module
from app.v1 import question_types  # noqa: F401 — enregistre les types (#40) au chargement
from app.v1.ampcr_pratique_format import ExerciseDocument
from app.v1.ampcr_pratique_plan import PRACTICAL_MODULE_CODE
from app.v1.ampcr_pratique_pr06_bank import ALL_ITEMS as PR06_ITEMS
from app.v1.ampcr_pratique_pr06_bank import PR06Item
from app.v1.ampcr_pratique_pr11_bank import ALL_ITEMS as PR11_ITEMS
from app.v1.ampcr_pratique_pr15_bank import ALL_ITEMS as PR15_ITEMS
from app.v1.models import (
    GenerationSource,
    Question,
    QuestionVersion,
    create_question,
    create_source_document,
)
from app.v1.question_engine import validate_content

PROMPT_VERSION_PREFIX = "ampcr-pratique"
SHORT_ANSWER_MAX_LENGTH = 3000
LONG_ANSWER_MAX_LENGTH = 20000


@dataclass(frozen=True)
class PracticalCourse:
    code: str
    title: str
    items: tuple[PR06Item, ...]
    context: PedagogicalContext

    @property
    def slug(self) -> str:
        return f"ampcr-pratique-{self.code.lower()}"


_PR06_CONTEXT = PedagogicalContext(
    course_key="ampcr-pratique-pr06",
    course_title="AMPCR pratique écrite — PR06 Diagnostic des pannes matérielles",
    level=(
        "CESS Professionnel, option AMPCR, épreuve pratique écrite (Laboratoire + T.P. et "
        "méthodes) : réponses rédigées de technicien, sans matériel réel"
    ),
    allowed_notions=[
        "recueil des symptômes, chronologie, changements récents, données et autorisations",
        "observation, hypothèse, test, résultat, conclusion ; du plus simple au plus invasif",
        "reproduction sans aggraver, un changement à la fois, configuration minimale, test croisé avec un composant connu fonctionnel",
        "sécurité : coupure secteur, décharge résiduelle, ESD, ne jamais ouvrir un bloc d'alimentation ni une batterie gonflée",
        "chaîne de démarrage : secteur, bloc d'alimentation, carte mère, POST, firmware BIOS/UEFI, stockage, chargeur, système",
        "PC inerte, ventilateurs sans image, absence de POST, « No boot device », redémarrages, écrans bleus, extinctions sous charge",
        "bips, LED et codes POST propres à chaque fabricant (manuel)",
        "RAM (barrette, slot, compatibilité, test mémoire, ECC), processeur et refroidissement (température, throttling, arrêt de protection)",
        "bloc d'alimentation (puissance, connecteurs ATX 24, EPS, PCIe, SATA, testeur), carte mère (condensateurs, VRM, liquide)",
        "affichage (écran, entrée, câble, sortie de la carte graphique ou iGPU), stockage (HDD, SSD, SATA, M.2 SATA/NVMe, SMART comme indice), périphériques et pilotes",
        "compatibilité : socket, génération DDR, format, alimentation, PCIe, SATA/M.2, firmware ; documentation du fabricant",
        "journaux (Kernel-Power 41, codes d'arrêt), indices et preuves, escalade, priorité aux données, compte rendu",
    ],
    competencies=[
        "Rédiger une démarche de diagnostic ordonnée et justifiée à partir d'un cas écrit",
        "Interpréter un document technique fictif (relevé, journal, manuel, rapport SMART, températures)",
        "Proposer une intervention sûre, sa vérification et un compte rendu professionnel",
    ],
    vocabulary=[
        "POST", "firmware", "UEFI", "CSM", "PWR_OK", "+5 VSB", "EPS", "configuration minimale",
        "test croisé", "SMART", "throttling", "Kernel-Power 41", "ESD",
    ],
    constraints=(
        "Correction d'une réponse écrite de technicien : accepter toute formulation "
        "techniquement juste, sans exiger de mot-clé ; suivre le barème de la question ; "
        "pénaliser une action dangereuse (sous tension, ouverture d'un bloc d'alimentation ou "
        "d'une batterie) ou destructive pour les données sans sauvegarde ni accord ; ne jamais "
        "valider une correspondance universelle de bips ou de codes POST."
    ),
)

_PR11_CONTEXT = PedagogicalContext(
    course_key="ampcr-pratique-pr11",
    course_title="AMPCR pratique écrite — PR11 Messages d'erreur Windows/Linux",
    level=(
        "CESS Professionnel, option AMPCR, épreuve pratique écrite (Laboratoire + T.P. et "
        "méthodes) : réponses rédigées de technicien à partir de captures et de journaux fictifs"
    ),
    allowed_notions=[
        "recueil : texte exact, code, contexte, date, déclencheur, changements récents, périmètre, criticité, données à préserver",
        "stades : firmware/POST, chargeur, noyau/système, session, service, application, pilote, périphérique, stockage, réseau",
        "code d'erreur, cause probable, hypothèse, test de confirmation, résultat attendu, action corrective ; documentation fiable, pas de cause unique tirée d'un code ambigu",
        "ordre : sauvegarde, preuves, tests simples, réparation réversible, opération invasive avec autorisation, validation",
        "No bootable device / Operating system not found / Reboot and Select proper Boot device : détection, UEFI/GPT ou hérité/MBR, ordre de démarrage, câblage, partition EFI, chargeur",
        "Windows Boot Manager, BCD (0xc000000f), WinRE (réparation du démarrage, restauration, désinstallation de mises à jour, mode sans échec), prudence avec bootrec, bcdboot, diskpart",
        "GRUB rescue, initramfs (UUID introuvable), emergency mode, /etc/fstab, UUID, nofail, mount -a",
        "écrans bleus : code d'arrêt, fichier cité, BugCheck 1001, Kernel-Power 41, 6008, redémarrage automatique ; pilotes, RAM, disque, mise à jour, température comme hypothèses",
        "Gestionnaire de périphériques : périphérique inconnu, triangle, désactivé, Codes 10, 22, 28, 43, restaurer le pilote",
        "Observateur d'événements : Système, Application, niveau, source, ID, heure ; corrélation n'est pas causalité",
        "Gestion des disques (hors ligne, non initialisé, sans lettre, RAW, plein), services (statut, type de démarrage, compte, dépendances)",
        "ipconfig /all, ping, nslookup, tracert, sfc /scannow, DISM /RestoreHealth, chkdsk (lecture seule, /f, /r), gestionnaire des tâches, msconfig ; diagnostic ou modification",
        "Windows Update (0x80070070 espace insuffisant), profil temporaire (1511), droits, applications",
        "Linux : systemctl status/start/restart/enable, journalctl -b -u -p, dmesg, df -h, df -i, du, lsblk, mount, ip addr, ip route, ss, resolvectl/dig, lsof +L1",
        "droits rwx, propriétaire, groupe, chmod, chown, jamais chmod 777 ; apt et dnf selon la distribution",
        "réseau : APIPA 169.254, passerelle, DNS, conflit IP, imprimante hors ligne ; un poste ou tous",
        "pannes intermittentes : chronologie, conditions, changements, preuves, répétition",
        "compte rendu : demande, environnement, symptômes, preuves, hypothèses, tests, résultats, cause (ou non déterminée), action et autorisation, validation, risques, recommandation, clôture",
    ],
    competencies=[
        "Interpréter un message d'erreur, une capture ou un journal fictif et situer le stade de l'erreur",
        "Rédiger une procédure de diagnostic ordonnée et non destructive sous Windows et sous Linux",
        "Proposer une réparation réversible d'abord, avec sauvegarde et autorisation, sa validation et un compte rendu",
    ],
    vocabulary=[
        "BCD", "WinRE", "UEFI", "CSM", "GPT", "MBR", "ESP", "STOP code", "BugCheck",
        "Kernel-Power 41", "Code 43", "SFC", "DISM", "chkdsk", "GRUB", "initramfs", "fstab",
        "UUID", "systemd", "journalctl", "inode", "APIPA",
    ],
    constraints=(
        "Correction d'une réponse écrite de technicien : accepter toute formulation "
        "techniquement juste, sans exiger de mot-clé ni l'orthographe exacte d'une commande si "
        "l'outil et son rôle sont clairs ; suivre le barème de la question ; valoriser la "
        "méthode, la sécurité des données, les tests et la justification ; pénaliser un "
        "formatage, une réinstallation, une initialisation de disque, un chkdsk /r, un fsck sur "
        "un volume monté ou un chmod 777 proposés sans précaution ; ne jamais valider une cause "
        "unique affirmée à partir d'un seul code ou d'une simple coïncidence."
    ),
)

_PR15_CONTEXT = PedagogicalContext(
    course_key="ampcr-pratique-pr15",
    course_title="AMPCR pratique écrite — PR15 Câblage RJ45 T568A/B",
    level=(
        "CESS Professionnel, option AMPCR, épreuve pratique écrite (Laboratoire + T.P. et "
        "méthodes) : réponses rédigées de technicien à partir de relevés de testeur et de "
        "situations de câblage fictifs"
    ),
    allowed_notions=[
        "câble à 4 paires torsadées, 8 conducteurs, rôle de la torsade, diaphonie, détorsadage limité à environ 13 mm",
        "U/UTP, F/UTP, U/FTP, S/FTP ; UTP, FTP, STP historiques ; blindage continu de bout en bout, mise à la terre selon l'installation",
        "Cat5e (100 MHz, 1 Gb/s sur 100 m), Cat6 (250 MHz, 10 Gb/s sur longueur réduite d'environ 37 à 55 m), Cat6A (500 MHz, 10 Gb/s sur 100 m)",
        "connecteur 8P8C dit RJ45, fiche, prise, keystone, panneau de brassage, cordon ; monobrin pour l'installation, multibrin pour les cordons ; fiches adaptées",
        "orientation : contacts dorés face à soi, languette dessous, câble vers le bas, broche 1 à gauche",
        "T568B : 1 blanc/orange, 2 orange, 3 blanc/vert, 4 bleu, 5 blanc/bleu, 6 vert, 7 blanc/marron, 8 marron",
        "T568A : 1 blanc/vert, 2 vert, 3 blanc/orange, 4 bleu, 5 blanc/bleu, 6 orange, 7 blanc/marron, 8 marron",
        "A et B échangent les paires orange et verte (broches 1, 2, 3, 6) ; bleue (4-5) et marron (7-8) identiques ; positions de paire 1-2, 3-6, 4-5, 7-8 ; paire séparée (split pair)",
        "câble droit A-A ou B-B ; croisé A-B (1→3, 2→6, 3→1, 6→2) ; MDI/MDI-X ; Auto MDI-X et ses limites",
        "10/100BASE-TX sur deux paires (1-2 émission, 3-6 réception côté carte) ; 1000BASE-T sur quatre paires bidirectionnelles",
        "lien physique, négociation de vitesse et duplex, configuration IP : trois niveaux distincts",
        "fabrication : manchons, coupe, dénudage sans entailler, ordre, recoupe, butée, gaine sous la patte de maintien, sertissage, autre bout, test avant mise en service ; poinçonnage d'un keystone",
        "wiremap : circuit ouvert, court-circuit, paire inversée, paires croisées, paire séparée, défaut intermittent ; continuité, qualification, certification",
        "canal 100 m = 90 m de lien permanent + cordons ; atténuation, NEXT, blindage, rapport signal/bruit ; lien à 100 Mb/s si 4-5 ou 7-8 défectueuse",
        "chaîne baie, panneau, câble permanent, prise, cordon, PC ; étiquetage ; rapport : besoin, norme, schéma, outils, tests avant/après, résultats, défauts corrigés, validation",
    ],
    competencies=[
        "Appliquer et vérifier les brochages T568A/T568B, pour un câble droit ou croisé",
        "Interpréter un relevé de testeur ou un rapport de qualification/certification et proposer la correction",
        "Rédiger une procédure de fabrication, de raccordement ou de diagnostic et un compte rendu",
    ],
    vocabulary=[
        "8P8C", "RJ45", "T568A", "T568B", "keystone", "panneau de brassage", "monobrin",
        "multibrin", "wiremap", "split pair", "NEXT", "Auto MDI-X", "U/UTP", "F/UTP", "S/FTP",
        "Cat5e", "Cat6", "Cat6A",
    ],
    constraints=(
        "Correction d'une réponse écrite de technicien : accepter toute formulation "
        "techniquement juste, sans exiger de mot-clé ; suivre le barème de la question. Un "
        "ordre de couleurs, une broche ou une paire faux est toujours une erreur, même bien "
        "rédigé ; accepter « blanc-orange », « blanc/orange » ou « orange-blanc » pour le même "
        "fil. Ne jamais valider « Cat6 = 10 Gb/s sur 100 m », « un testeur de continuité "
        "certifie la catégorie » ni « le gigabit n'utilise que deux paires »."
    ),
)

PRACTICAL_COURSES: tuple[PracticalCourse, ...] = (
    PracticalCourse(
        code="PR06", title="Diagnostic des pannes matérielles", items=PR06_ITEMS, context=_PR06_CONTEXT
    ),
    PracticalCourse(
        code="PR11",
        title="Messages d'erreur Windows/Linux — diagnostic et interventions écrites",
        items=PR11_ITEMS,
        context=_PR11_CONTEXT,
    ),
    PracticalCourse(
        code="PR15",
        title="Câblage RJ45 T568A/B — fabrication, schémas et tests",
        items=PR15_ITEMS,
        context=_PR15_CONTEXT,
    ),
)
PRACTICAL_COURSES_BY_CODE: dict[str, PracticalCourse] = {c.code: c for c in PRACTICAL_COURSES}
PRACTICAL_COURSES_BY_SLUG: dict[str, PracticalCourse] = {c.slug: c for c in PRACTICAL_COURSES}


def get_practical_course_by_slug(uaa_slug: str) -> PracticalCourse | None:
    return PRACTICAL_COURSES_BY_SLUG.get(uaa_slug)


def is_practical_code(uaa_code: str | None) -> bool:
    return bool(uaa_code) and uaa_code in PRACTICAL_COURSES_BY_CODE


def get_practical_context(uaa_code: str | None) -> PedagogicalContext | None:
    course = PRACTICAL_COURSES_BY_CODE.get(uaa_code or "")
    return course.context if course else None


def usage_tag(code: str, usage: str) -> str:
    return f"{PROMPT_VERSION_PREFIX}-{code.lower()}:{usage}"


def restrict_to_mode(questions: list[Question], mode_value: str | None) -> list[Question]:
    """Garde, pour les questions du parcours pratique, celles de la réserve du mode
    (`practice`/`exam`). No-op pour toute autre question et quand `mode_value` est absent."""
    if mode_value is None:
        return questions
    return [q for q in questions if question_usage(q) in (None, mode_value)]


def _document_layout(document: ExerciseDocument) -> dict | None:
    if document.kind == "console":
        # Ticket #194 : capture de terminal ou extrait de journal, affiché en police à chasse
        # fixe, ligne à ligne (`_document_layouts.html`, mise en page « console »).
        return {
            "kind": "console",
            "lines": document.content_text.splitlines(),
            "notice": "Extrait fictif reconstitué pour l'exercice (messages au format réel).",
        }
    if document.kind != "tableau":
        return None
    rows = document.table_rows()
    return {"kind": "table", "columns": rows[0], "rows": rows[1:]}


def _create_documents(db: Session, module: Module, item: PR06Item) -> list[int]:
    ids = []
    for document in item.documents:
        layout = _document_layout(document)
        created = create_source_document(
            db,
            title=document.title,
            content_text=document.content_text,
            content_json={"layout": layout} if layout else None,
            module_id=module.id,
        )
        ids.append(created.current_version_id)
    db.flush()
    return ids


def item_content(item: PR06Item, document_version_ids: list[int]) -> dict:
    """Contenu `content_json` d'une question, au format d'un type existant."""
    content: dict = {"prompt": item.prompt}
    if item.question_type == "classification":
        assert item.classification is not None
        content.update(
            categories=list(item.classification.categories),
            elements=list(item.classification.elements),
            correct_categories=list(item.classification.correct),
            explanation=" ".join(item.correction),
        )
    elif item.question_type == "ordering":
        assert item.ordering is not None
        ids = [f"etape-{i + 1}" for i in range(len(item.ordering.steps))]
        content.update(
            items=[{"id": ids[i], "label": step} for i, step in enumerate(item.ordering.steps)],
            correct_order=[ids[i] for i in item.ordering.correct],
            explanation=" ".join(item.correction),
        )
    else:
        content["rubric"] = item.rubric()
        if item.question_type == "short_answer":
            content["max_length"] = SHORT_ANSWER_MAX_LENGTH
        else:
            content.update(
                expected_points=[c.expected for c in item.criteria],
                max_score=item.total_points,
                max_length=LONG_ANSWER_MAX_LENGTH,
            )
    if document_version_ids:
        content["source_document_version_id"] = document_version_ids[0]
        if len(document_version_ids) > 1:
            content["source_document_version_ids"] = list(document_version_ids)
    return content


def import_practical_bank(db: Session, module: Module, uaa: UAA) -> int:
    """Importe la banque d'un cours pratique (idempotent : rien si l'UAA a déjà ses
    questions importées)."""
    course = PRACTICAL_COURSES_BY_CODE.get(uaa.code)
    if course is None or module.code != PRACTICAL_MODULE_CODE:
        return 0
    already = (
        db.query(Question)
        .filter_by(uaa_id=uaa.id, generation_source=GenerationSource.IMPORTED)
        .count()
    )
    if already:
        return 0
    imported = 0
    for item in course.items:
        document_ids = _create_documents(db, module, item)
        content = item_content(item, document_ids)
        validate_content(item.question_type, 1, content)
        create_question(
            db,
            module_id=module.id,
            uaa_id=uaa.id,
            question_type=item.question_type,
            content_json=content,
            generation_source=GenerationSource.IMPORTED,
            prompt_version=usage_tag(course.code, item.usage),
            source_program_version="Consignes AMPCR pratique 2026-2027/1",
            source_document_version_id=document_ids[0] if document_ids else None,
        )
        imported += 1
    db.flush()
    return imported


PRACTICAL_BANK_IMPORTERS: dict[str, Callable[[Session, Module, UAA], int]] = {
    course.slug: import_practical_bank for course in PRACTICAL_COURSES
}


def _version_usage(version: QuestionVersion | None) -> str | None:
    tag = (version.prompt_version if version else None) or ""
    if not tag.startswith(PROMPT_VERSION_PREFIX) or ":" not in tag:
        return None
    return tag.rsplit(":", 1)[1]


def question_usage(question: Question) -> str | None:
    """Réserve (`practice`/`exam`) d'une question du parcours pratique, `None` sinon. Lue
    sur la version courante, sinon sur la première version marquée : une nouvelle version
    créée plus tard (correction, administration) ne change jamais de réserve."""
    usage = _version_usage(question.current_version)
    if usage is None:
        for version in sorted(question.versions, key=lambda v: v.version):
            usage = _version_usage(version)
            if usage is not None:
                break
    return usage
