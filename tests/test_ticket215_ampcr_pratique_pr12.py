"""Ticket #215 — AMPCR pratique écrite, PR12 « Dépannage logiciel et restauration du système ».

Couvre : données de référence **recontrôlées ici** indépendamment (familles de causes et arbre
d'isolement, échelle des interventions avec effets et précautions, outils de WinRE, empreintes
SHA-256 recalculées avec `hashlib`, espace disque et arrondi de `df`, commandes Linux, panne
réseau logicielle ou physique, cinq procédures) ; relevés fictifs (largeur, cohérence) ;
schémas SVG (validité, accessibilité, données) ; exercices et mini-examen (format du socle,
remises en ordre et classements auto-corrigés, pas de question d'acronyme, contexte complet) ;
cours (matière du ticket, 5 procédures, 5 cas résolus, affirmations techniques justes, supports
fictifs, cartes) ; banque, seed, pages et sessions. Aucun appel IA réel : `FakeAIProvider`
partout."""

import hashlib
import re
from html import escape

import pytest

from app.models import UAA, Module
from app.seed import seed
from app.v1 import ampcr_pratique_plan as plan
from app.v1.ampcr_pratique_audit import proven_requirement_ids as audit_proven_ids
from app.v1.ampcr_pratique_bank import (
    PRACTICAL_BANK_IMPORTERS,
    PRACTICAL_COURSES_BY_CODE,
    get_practical_context,
    import_practical_bank,
    item_content,
    question_usage,
)
from app.v1.ampcr_pratique_pr12_bank import (
    E11_WINDOWS_LETTER,
    E15_BAD,
    E15_ROWS,
    E16_CAN_READ,
    E16_CAN_WRITE,
    EXAM_ITEMS,
    EXAM_TOTAL_POINTS,
    KIND_CAUSE,
    KIND_DATA,
    KIND_ERROR,
    KIND_LINUX,
    KIND_NETWORK,
    KIND_ORDER,
    KIND_WINDOWS,
    PRACTICE_ITEMS,
    REQ,
    X06_PCT,
    X10_APIPA,
    validate_items,
)
from app.v1.ampcr_pratique_pr12_course import PR12_SLUG, PR12_TITLE, pr12_course_sections
from app.v1.ampcr_pratique_pr12_figures import (
    BACKUP_FILES,
    BACKUP_STEPS,
    BOOT_STEPS,
    CASE5_AVAIL_AFTER,
    CASE5_AVAIL_BEFORE,
    CASE5_DF_AFTER,
    CASE5_DU,
    CASE5_RESERVED,
    CASE5_SIZE,
    CASE5_USED_AFTER,
    CASE5_USED_BEFORE,
    CASE5_VAR,
    CAUSE_ACCOUNT,
    CAUSE_APP,
    CAUSE_DRIVER,
    CAUSE_MALWARE,
    CAUSE_OS,
    CAUSE_SERVICE,
    CAUSE_STORAGE,
    CAUSES,
    COPY_BAD,
    COPY_OK,
    DISK_SCREEN,
    DPKG_SCREEN,
    EFFECT_ALL,
    EFFECT_NOTHING,
    EFFECT_PROGRAMS,
    GRUB_SCREEN,
    ISOLATION_TREE,
    LADDER,
    LADDER_BY_NAME,
    LINUX_SERVICE_STEPS,
    MEDIA_DISCONNECTED_SCREEN,
    METHOD_STEPS,
    NET_APP,
    NET_DHCP,
    NET_DNS,
    NET_INTERNET,
    NET_LOCAL,
    NET_PHYSICAL,
    NETWORK_TREE,
    NGINX_SCREEN,
    PR12_FIGURES,
    PREC_BACKUP,
    PREC_NOTE,
    PREC_WRITTEN,
    PRECAUTIONS,
    PROCEDURES,
    PROFILE_STEPS,
    RESTORE_STEPS,
    RESTORED_SCREEN,
    SCREEN_WIDTH,
    TEMP_PROFILE_SCREEN,
    WINRE_TOOLS,
    copy_check,
    df_use_percent,
    effect_of,
    isolate,
    network_layer,
    precaution_for,
    sha256_hex,
)
from app.v1.ampcr_pratique_visuals import render_figure, validate_figure
from app.v1.models import Question, QuestionnaireSession, SessionMode
from app.v1.question_engine import validate_content
from app.v1.session_service import _pedagogical_context_for, available_session_lengths
from tests.test_ticket94_french_fr06_10 import (
    _answer_all_and_submit,
    _patch_fake_provider,
    _start_session,
)

SLUG = "ampcr-pratique-pr12"
_OK = {"disk_ok": True, "several_apps": True, "other_account": True, "safe_mode": True, "scan_clean": True}


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _course_raw() -> str:
    return " ".join(c for _t, c in pr12_course_sections())


def _course_text() -> str:
    return _text(_course_raw()).replace("**", "").replace("`", "").lower()


def _all_items_text() -> str:
    return " ".join(
        " ".join((i.title, i.context, *i.instructions, *i.correction, *(c.expected for c in i.criteria),
                  *(d.content_text for d in i.documents)))
        for i in PRACTICE_ITEMS + EXAM_ITEMS
    )


def _pr12(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "PR12")
    return module, uaa


# =============================================================================================
# 1. Données de référence, recontrôlées indépendamment
# =============================================================================================


def test_seven_cause_families_and_isolation():
    assert {c.name for c in CAUSES} == {CAUSE_OS, CAUSE_APP, CAUSE_DRIVER, CAUSE_SERVICE, CAUSE_ACCOUNT,
                                        CAUSE_MALWARE, CAUSE_STORAGE}
    for cause in CAUSES:
        assert cause.signs and cause.test and cause.first_action, cause.name
    assert isolate(**_OK) == CAUSE_OS
    expected = {"disk_ok": CAUSE_STORAGE, "several_apps": CAUSE_APP, "other_account": CAUSE_ACCOUNT,
                "safe_mode": CAUSE_DRIVER, "scan_clean": CAUSE_MALWARE}
    for key, cause in expected.items():
        assert isolate(**{**_OK, key: False}) == cause, key
    # Le stockage passe avant tout : un disque plein l'emporte sur les autres observations.
    assert isolate(**{k: False for k in _OK}) == CAUSE_STORAGE
    assert [k for k, _q, _n in ISOLATION_TREE] == list(expected)
    # Mode sans échec : seuls pilotes et services de base → la panne qui disparaît vient d'un tiers.
    assert "mode sans échec" in ISOLATION_TREE[3][1].lower()


def test_intervention_ladder_effects_and_precautions():
    names = [i.name for i in LADDER]
    assert names[0] == "Annuler le dernier changement" and names[-1] == "Réinstallation complète"
    # Documentation Microsoft : effets de chaque outil.
    assert effect_of(LADDER_BY_NAME["Restauration du système"]) == EFFECT_PROGRAMS
    assert effect_of(LADDER_BY_NAME["Réparer les fichiers système"]) == EFFECT_ALL
    assert effect_of(LADDER_BY_NAME["Réinstaller via Windows Update"]) == EFFECT_ALL
    assert effect_of(LADDER_BY_NAME["Réinitialiser en conservant les fichiers"]) == EFFECT_PROGRAMS
    assert effect_of(LADDER_BY_NAME["Réinstallation complète"]) == EFFECT_NOTHING
    # Précautions : jamais décroissantes en montant l'échelle ; accord écrit pour toute réinitialisation.
    levels = [PRECAUTIONS.index(precaution_for(i)) for i in LADDER]
    assert levels == sorted(levels)
    assert precaution_for(LADDER[0]) == PREC_NOTE
    assert precaution_for(LADDER_BY_NAME["Restauration du système"]) == PREC_BACKUP
    assert precaution_for(LADDER_BY_NAME["Réinitialiser en conservant les fichiers"]) == PREC_WRITTEN
    assert precaution_for(LADDER_BY_NAME["Réinstallation complète"]) == PREC_WRITTEN
    assert "/RestoreHealth puis sfc /scannow" in LADDER_BY_NAME["Réparer les fichiers système"].detail
    tools = " ".join(t for t, _r, _e in WINRE_TOOLS)
    for tool in ("réparation du démarrage", "mode sans échec", "Désinstaller des mises à jour",
                 "Restauration du système", "Invite de commandes", "Réinitialiser ce PC"):
        assert tool in tools, tool


def test_sha256_fingerprints_recomputed_with_hashlib():
    for f in BACKUP_FILES:
        assert sha256_hex(f.original) == hashlib.sha256(f.original).hexdigest()
        assert len(sha256_hex(f.original)) == 64
        assert copy_check(f) == (COPY_OK if f.original == f.copy else COPY_BAD)
    assert E15_BAD == ("photos-chantier.zip",)
    for name, original, copy in E15_ROWS:
        same = next(f for f in BACKUP_FILES if f.name == name)
        assert (original == copy) == (same.original == same.copy)
    # Un seul octet de différence change l'empreinte.
    assert sha256_hex(b"Bonjour") != sha256_hex(b"bonjour")


def test_disk_space_figures_are_consistent():
    assert df_use_percent(28.5, 0) == 100
    assert df_use_percent(20.6, 7.9) == 73  # arrondi au-dessus, comme GNU df
    assert CASE5_AVAIL_BEFORE == 0
    assert round(CASE5_USED_AFTER + CASE5_AVAIL_AFTER + CASE5_RESERVED, 6) == CASE5_SIZE
    assert round(CASE5_USED_BEFORE + CASE5_AVAIL_BEFORE + CASE5_RESERVED, 6) == CASE5_SIZE
    assert "100% /" in DISK_SCREEN[2] and "29G" in DISK_SCREEN[2] and "30G" in DISK_SCREEN[2]
    assert f"{df_use_percent(CASE5_USED_AFTER, CASE5_AVAIL_AFTER)}% /" in CASE5_DF_AFTER[2]
    assert "7.9G" in CASE5_DF_AFTER[2] and "21G" in CASE5_DF_AFTER[2]
    # du : sous-dossiers classés par taille (sort -h), total supérieur à leur somme.
    sizes = [size for _p, size in CASE5_VAR]
    assert sizes == sorted(sizes) and CASE5_DU[-1].endswith("/var") and CASE5_DU[-1].startswith("12G")
    assert max(CASE5_VAR, key=lambda v: v[1])[0] == "/var/log"
    assert X06_PCT == 100


def test_network_software_or_physical():
    assert network_layer(link=False, valid_ip=True, gateway_ok=True, internet_ok=True, dns_ok=True) == NET_PHYSICAL
    assert network_layer(link=True, valid_ip=False, gateway_ok=False, internet_ok=False, dns_ok=False) == NET_DHCP
    assert network_layer(link=True, valid_ip=True, gateway_ok=False, internet_ok=False, dns_ok=False) == NET_LOCAL
    assert network_layer(link=True, valid_ip=True, gateway_ok=True, internet_ok=False, dns_ok=False) == NET_INTERNET
    assert network_layer(link=True, valid_ip=True, gateway_ok=True, internet_ok=True, dns_ok=False) == NET_DNS
    assert network_layer(link=True, valid_ip=True, gateway_ok=True, internet_ok=True, dns_ok=True) == NET_APP
    assert len(NETWORK_TREE) == 5 and "Média déconnecté" in NETWORK_TREE[0][0]
    assert "Média déconnecté" in " ".join(MEDIA_DISCONNECTED_SCREEN)
    apipa = " ".join(X10_APIPA)
    assert "169.254.31.7" in apipa and "255.255.0.0" in apipa and "Carte réseau sans fil Wi-Fi" in apipa


def test_procedures_order():
    assert len(PROCEDURES) == 5
    method = [label for label, _d in METHOD_STEPS]
    assert method[0] == "Recueillir les faits" and method[-1] == "Contrôler et rédiger"
    assert method.index("Protéger les données") < method.index("Corriger par étapes")
    backup = [label for label, _d in BACKUP_STEPS]
    assert backup.index("Copier sans déplacer") < backup.index("Vérifier la copie") < backup.index("Obtenir l'accord")
    restore = [label for label, _d in RESTORE_STEPS]
    assert restore[0] == "Vérifier la sauvegarde" and restore.index("Choisir le point") < restore.index("Lancer et attendre")
    boot = [label for label, _d in BOOT_STEPS]
    assert boot.index("Réparation du démarrage") < boot.index("Mode sans échec") < boot.index("Mise à jour, restauration")
    linux = [label for label, _d in LINUX_SERVICE_STEPS]
    assert linux.index("Tester la configuration") < linux.index("Redémarrer le service")
    profile = [label for label, _d in PROFILE_STEPS]
    assert profile[0] == "Ne rien enregistrer" and profile.index("Sauvegarder l'ancien profil") < profile.index("Créer un nouveau profil")


def test_screens_readable_and_consistent():
    screens = (TEMP_PROFILE_SCREEN, NGINX_SCREEN, DPKG_SCREEN, RESTORED_SCREEN, GRUB_SCREEN, DISK_SCREEN,
               CASE5_DF_AFTER, MEDIA_DISCONNECTED_SCREEN, X10_APIPA)
    for screen in screens:
        assert max(len(line) for line in screen) <= SCREEN_WIDTH
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        for document in item.documents:
            if document.kind == "console":
                assert max(len(line) for line in document.content_text.split("\n")) <= SCREEN_WIDTH, item.key
    assert "ID 1511" in " ".join(TEMP_PROFILE_SCREEN) and "profil temporaire" in " ".join(TEMP_PROFILE_SCREEN)
    nginx = " ".join(NGINX_SCREEN)
    assert "failed (Result: exit-code)" in nginx and "boutique:14" in nginx and "test failed" in nginx
    assert "sudo dpkg --configure -a" in " ".join(DPKG_SCREEN)
    grub = " ".join(GRUB_SCREEN)
    assert "6.8.0-49-generic" in grub and "* Ubuntu, with Linux 6.8.0-47-generic" in grub
    assert "root root" in " ".join(RESTORED_SCREEN) and "Permission denied" in " ".join(RESTORED_SCREEN)
    assert (E16_CAN_READ, E16_CAN_WRITE) == (True, False)
    assert E11_WINDOWS_LETTER == "D:"


# =============================================================================================
# 2. Schémas
# =============================================================================================


def test_figures_valid_accessible_and_unique():
    keys = [f.key for f in PR12_FIGURES]
    assert len(keys) == len(set(keys)) == 11  # ticket : au moins 4 schémas ou documents
    for figure in PR12_FIGURES:
        assert validate_figure(figure) == [], figure.key
        html = str(render_figure(figure))
        assert 'role="img"' in html and "(schéma non officiel)" in html and not figure.official


def test_figures_drawn_from_data():
    by_key = {f.key: f for f in PR12_FIGURES}
    for key, steps in (("pr12-demarche", METHOD_STEPS), ("pr12-sauvegarde", BACKUP_STEPS),
                       ("pr12-restauration", RESTORE_STEPS), ("pr12-demarrage", BOOT_STEPS),
                       ("pr12-service-linux", LINUX_SERVICE_STEPS)):
        svg = by_key[key].svg
        for index, (label, _detail) in enumerate(steps, start=1):
            assert f"{index}. {escape(label)}" in svg, (key, label)
    assert by_key["pr12-isoler"].svg.count("data-step=") == len(ISOLATION_TREE)
    assert by_key["pr12-reseau"].svg.count("data-step=") == len(NETWORK_TREE)
    ladder = by_key["pr12-echelle"].svg
    assert re.findall(r'data-files="(\d)" data-programs="(\d)"', ladder) == [
        (str(int(i.keeps_files)), str(int(i.keeps_programs))) for i in LADDER
    ]
    assert "✓" in ladder and "✗" in ladder
    for key in ("pr12-profil", "pr12-nginx", "pr12-espace"):
        assert "fictive" in by_key[key].caption.lower() and "Capture fictive" in by_key[key].svg, key


# =============================================================================================
# 3. Exercices et mini-examen
# =============================================================================================


def test_items_valid_and_counts_match_ticket():
    assert validate_items() == []
    assert len(PRACTICE_ITEMS) >= 16 and len(EXAM_ITEMS) == 10  # ticket : ≥ 16 exercices, mini-examen /20
    assert sum(i.total_points for i in EXAM_ITEMS) == EXAM_TOTAL_POINTS == 20
    kinds = [i.kind for i in PRACTICE_ITEMS]
    for kind, minimum in ((KIND_ORDER, 3), (KIND_CAUSE, 2), (KIND_WINDOWS, 3), (KIND_LINUX, 3),
                          (KIND_DATA, 3), (KIND_NETWORK, 1), (KIND_ERROR, 1)):
        assert kinds.count(kind) >= minimum, kind
    keys = [i.key for i in PRACTICE_ITEMS + EXAM_ITEMS]
    assert len(keys) == len(set(keys))
    covered = {r for i in PRACTICE_ITEMS + EXAM_ITEMS for r in i.requirement_ids}
    assert REQ <= covered
    assert set(plan.COURSE_SLOTS_BY_CODE["PR12"].requirement_ids) == REQ
    types = [i.question_type for i in PRACTICE_ITEMS]
    assert types.count("ordering") == 3 and types.count("classification") == 5
    # Ticket : exercices documentés (relevés, consoles, tableaux).
    assert sum(1 for i in PRACTICE_ITEMS if i.documents) >= 8


def test_auto_corrected_answers():
    by_key = {i.key: i for i in PRACTICE_ITEMS}

    def ordered(key: str) -> list[str]:
        o = by_key[key].ordering
        return [o.steps[i].split(" — ")[0] for i in o.correct]

    assert ordered("E01") == [label for label, _d in METHOD_STEPS]
    assert ordered("E02") == [label for label, _d in RESTORE_STEPS]
    assert ordered("E03") == [label for label, _d in BACKUP_STEPS]

    def answers(key: str) -> dict[str, str]:
        c = by_key[key].classification
        return dict(zip(c.elements, (c.categories[i] for i in c.correct), strict=True))

    e04 = answers("E04")
    assert next(v for k, v in e04.items() if "mode sans échec" in k and "Écran noir" in k) == CAUSE_DRIVER
    assert next(v for k, v in e04.items() if ".locked" in k) == CAUSE_MALWARE
    assert next(v for k, v in e04.items() if "profil temporaire" in k) == CAUSE_ACCOUNT
    assert next(v for k, v in e04.items() if "0,4 Go" in k) == CAUSE_STORAGE
    assert next(v for k, v in e04.items() if "SFC" in k) == CAUSE_OS
    e05 = answers("E05")
    assert next(v for k, v in e05.items() if "rstrui" in k) == EFFECT_PROGRAMS
    assert next(v for k, v in e05.items() if "Supprimer tout" in k) == EFFECT_NOTHING
    assert next(v for k, v in e05.items() if "Windows Update »" in k) == EFFECT_ALL
    e06 = answers("E06")
    assert next(v for k, v in e06.items() if "Conserver mes fichiers" in k) == PREC_WRITTEN
    assert next(v for k, v in e06.items() if "Restaurer le pilote" in k) == PREC_NOTE
    e07 = answers("E07")
    assert next(v for k, v in e07.items() if "panne de courant" in k) == "sudo dpkg --configure -a"
    assert next(v for k, v in e07.items() if "démontée" in k or "démonté" in k) == "sudo fsck -f /dev/sdb1"
    assert next(v for k, v in e07.items() if "session d'avant" in k) == "journalctl -b -1 -p err"
    e08 = answers("E08")
    assert next(v for k, v in e08.items() if "Média déconnecté" in k) == NET_PHYSICAL
    assert next(v for k, v in e08.items() if "169.254" in k) == NET_DHCP
    assert next(v for k, v in e08.items() if "proxy" in k) == NET_APP
    assert next(v for k, v in e08.items() if "délai expiré" in k) == NET_DNS
    for item in PRACTICE_ITEMS:  # aucune remise en ordre déjà dans l'ordre attendu, aucun classement trivial
        if item.ordering:
            assert list(item.ordering.correct) != list(range(len(item.ordering.steps))), item.key
        if item.classification:
            assert list(item.classification.correct) != list(range(len(item.classification.elements))), item.key


def test_no_false_technical_claims_anywhere():
    text = _course_text() + " " + _all_items_text().lower()
    for right in ("dism /online /cleanup-image /restorehealth puis sfc /scannow", "/offwindir", "mode sans échec",
                  "rstrui", "rechercher les programmes concernés", "ne contient pas les documents",
                  "profil temporaire", "1511", "désinstaller des mises à jour", "suspendre", "revenir en arrière",
                  "réinitialiser ce pc", "conserver mes fichiers", "supprimer tout", "accord écrit",
                  "sauvegarde vérifiée", "sha-256", "get-filehash", "certutil -hashfile", "sha256sum",
                  "copier sans déplacer", "analyse hors ligne de microsoft defender", "ne jamais payer",
                  "systemctl --failed", "journalctl -u", "nginx -t", "advanced options", "update-grub",
                  "dpkg --configure -a", "apt --fix-broken install", "fsck", "démontée", "df -h", "du -xh -d1",
                  "journalctl --vacuum-size", "apt clean", "chown -r anne:anne", "média déconnecté", "169.254",
                  "documentation de l'éditeur fait foi"):
        assert right in text, right
    for wrong in ("sfc /scannow puis dism", "un point de restauration contient les documents",
                  "fsck sur la partition montée est sans risque", "réinstaller d'abord", "payer la rançon",
                  "désactiver l'antivirus est recommandé", "chmod 777 pour", "supprimer winsxs pour",
                  "brancher le disque de sauvegarde pour récupérer"):
        assert wrong not in text, wrong


def test_no_acronym_question_and_full_context():
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        text = " ".join((item.title, item.context, *item.instructions))
        assert not re.search(r"que signifie|que veut dire|développe[rz]? l'acronyme", text, re.IGNORECASE), item.key
        assert len(item.context) >= 150, item.key
        assert "officiel" not in item.title.lower(), item.key


def test_items_content_matches_existing_question_types():
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        content = item_content(item, list(range(1, len(item.documents) + 1)))
        validate_content(item.question_type, 1, content)


# =============================================================================================
# 4. Cours
# =============================================================================================


def test_five_resolved_cases_procedures_and_exam_not_in_course():
    text = _text(_course_raw())
    for case in ("Cas 1 — Démarrage", "Cas 2 — Service", "Cas 3 — Profil", "Cas 4 — Mise à jour",
                 "Cas 5 — Espace disque"):
        assert case in text, case
    assert text.count("Conclusion rédigée.") == 5
    for i in range(1, 6):
        assert f"Procédure {i} —" in text, i
    course = _course_raw()
    for item in EXAM_ITEMS:
        assert item.context not in course and escape(item.context) not in course, item.key
    for item in PRACTICE_ITEMS:
        assert escape(item.context) in course, item.key


def test_course_teaches_every_mandatory_point():
    titles = [t for t, _ in pr12_course_sections()]
    assert len(titles) == len(set(titles))
    text = _course_text()
    for notion in (
        # matière du ticket, dans l'ordre du cahier des charges
        "système d'exploitation", "application", "pilote", "compte", "service", "malveillant", "stockage",
        "symptôme", "journaux", "reproductibilité", "changements récents",
        "démarrage avancé", "winre", "point de restauration", "sfc", "dism", "mises à jour", "profil",
        "systemd", "journalctl", "grub", "permissions", "paquets", "système de fichiers", "espace disque",
        "sauvegarde", "restauration", "intégrité", "faire perdre",
        "autorisation", "réinstallation", "logicielle", "physique",
        # encadrés
        "objectifs", "procédure professionnelle", "erreur fréquente", "à l'écrit", "repère rapide", "glossaire",
    ):
        assert notion in text, notion


def test_course_flags_requirements_links_and_fictive_supports():
    raw = _course_raw()
    text = _text(raw)
    for req in ("AP-15", "AP-C03"):
        assert req in text
    assert "Compléments pédagogiques" in text and "fictif" in text.lower()
    assert "aucune n'est une question officielle" in text.lower()
    assert "aucun schéma n'est tiré d'une image générée" in text.lower()
    assert "conventions du cours" in text.lower() and "en anglais" in text.lower() and "en français" in text.lower()
    for link in ("/uaa/ampcr-mc30", "/uaa/ampcr-mc32", "/uaa/ampcr-pratique-pr05", "/uaa/ampcr-pratique-pr06",
                 "/uaa/ampcr-pratique-pr08", "/uaa/ampcr-pratique-pr09", "/uaa/ampcr-pratique-pr10",
                 "/uaa/ampcr-pratique-pr11", "/uaa/ampcr-pratique-pr20", "/uaa/ampcr-pratique-pr24",
                 f"/uaa/{PR12_SLUG}/practice", f"/uaa/{PR12_SLUG}/exam"):
        assert link in raw, link
    # PR28 n'est pas encore publié : renvoi en texte seulement.
    assert "/uaa/ampcr-pratique-pr28" not in raw and "PR28" in raw
    anchors = set(re.findall(r'id="(pr12-e\d\d)"', raw))
    assert anchors == {f"pr12-{i.key.lower()}" for i in PRACTICE_ITEMS}
    assert "(#pr12-" not in raw


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(t) for t, _ in pr12_course_sections()]
    assert kinds[:14] == ["theory"] * 14
    assert kinds[14:] == ["example", "warning", "exercise", "exam", "summary", "info"]


# =============================================================================================
# 5. Banque, seed et intégration au moteur
# =============================================================================================


def test_plan_slot_matches_ticket():
    slot = plan.COURSE_SLOTS_BY_CODE["PR12"]
    assert slot.ticket == 215 and slot.title == PR12_TITLE == PRACTICAL_COURSES_BY_CODE["PR12"].title


def test_seed_publishes_pr12_in_practical_module_idempotently(db_session):
    module, uaa = _pr12(db_session)
    assert uaa.slug == SLUG and uaa.is_published and uaa.title == PR12_TITLE and uaa.position == 12
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="PR12").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(pr12_course_sections())
    assert {"PR10", "PR11", "PR12"} <= set(plan.published_uaas(db_session))
    ordered = [u.code for u in sorted(module.uaas, key=lambda u: (u.position, u.id))]
    assert ordered.index("PR10") < ordered.index("PR11") < ordered.index("PR12") < ordered.index("PR15")
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_reserves_and_documents(db_session):
    module, uaa = _pr12(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert import_practical_bank(db_session, module, uaa) == len(PRACTICE_ITEMS) + len(EXAM_ITEMS)
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    usages = [question_usage(q) for q in questions]
    assert usages.count("practice") == len(PRACTICE_ITEMS) and usages.count("exam") == 10


def test_correction_context_is_pr12_specific():
    context = _pedagogical_context_for("PR12")
    assert context is get_practical_context("PR12")
    assert context.course_key == SLUG
    notions = " ".join(context.allowed_notions)
    for notion in ("profil temporaire", "rstrui.exe", "DISM /Online /Cleanup-Image /RestoreHealth puis sfc /scannow",
                   "/offwindir", "dpkg --configure -a", "fsck seulement sur une partition démontée", "SHA-256",
                   "accord écrit", "Média déconnecté", "Réinitialiser ce PC"):
        assert notion in notions, notion
    assert "mot-clé" in context.constraints and "point de restauration et sauvegarde" in context.constraints


# =============================================================================================
# 6. Pages et sessions
# =============================================================================================


def test_course_page_renders_figures_and_exercises(client, db_session):
    _pr12(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert set(ids) >= {f"fig-{f.key}" for f in PR12_FIGURES}
    assert html.count('class="jc-exercise-card"') == len(PRACTICE_ITEMS)
    assert "<details open" not in html
    assert 'href="/ampcr-pratique"' in html and f"/uaa/{SLUG}/exam" in html
    assert "<table" in html and "jc-pr-console" in html


def test_practical_home_and_matrix_show_pr12(client, db_session):
    _pr12(db_session)
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and re.search(r"\d+ cours publiés sur 30 prévus", _text(home))  # PR13 (#216) publié ensuite
    for req in REQ:
        assert plan.requirement_status(req, {"PR12"}) == plan.STATUS_PARTIAL
    assert plan.VALIDATED_REQUIREMENT_IDS == audit_proven_ids()  # « validé » : preuves de l'audit #235
    assert client.get("/ampcr-pratique/matrice").status_code == 200


@pytest.mark.parametrize("mode", ["practice", "exam"])
def test_sessions_draw_only_from_their_reserve_without_generation(authenticated_client, db_session, monkeypatch, mode):
    fake = _patch_fake_provider(monkeypatch)
    _pr12(db_session)
    assert authenticated_client.get(f"/uaa/{SLUG}/{mode}").status_code == 200
    session_url = _start_session(authenticated_client, db_session, SLUG, mode)
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert {question_usage(sq.question_version.question) for sq in session.session_questions} == {mode}
    assert session.question_count == 10
    assert fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"PR12"}
    if mode == "exam":
        page = authenticated_client.get(f"{session_url}?q=1").text
        assert "Corrigé de référence" not in page and "Barème" not in page


def test_exam_lengths_limited_and_score_on_20(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _pr12(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    from app.v1.models import User

    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="PR12", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "/ 20" in html


def test_practice_sessions_with_classification_and_ordering_submit(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr12(db_session)
    for _ in range(2):  # 17 exercices : deux sessions de 10 couvrent toute la réserve
        session_url = _start_session(authenticated_client, db_session, SLUG, "practice")
        _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
        assert authenticated_client.get(session_url).status_code == 200
