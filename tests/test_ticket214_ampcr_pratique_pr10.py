"""Ticket #214 — AMPCR pratique écrite, PR10 « Comptes, pilotes, paramètres et commandes ».

Couvre : données de référence **recontrôlées ici** indépendamment (comptes et moindre privilège,
UAC et sudo, permissions Linux, états des périphériques et identifiants matériels, services,
fiches des 16 commandes du ticket et droits nécessaires, quatre procédures) ; relevés fictifs
(largeur, cohérence) ; schémas SVG (validité, accessibilité, données) ; exercices et
mini-examen (format du socle, remises en ordre et classements auto-corrigés, pas de question
d'acronyme, contexte complet) ; cours (matière du ticket, 4 procédures, 5 cas résolus,
affirmations techniques justes, supports fictifs, cartes) ; banque, seed, pages et sessions.
Aucun appel IA réel : `FakeAIProvider` partout."""

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
from app.v1.ampcr_pratique_pr10_bank import (
    E06_COMMANDS,
    E11_VENDOR,
    E12_CAN_READ,
    E12_CAN_WRITE,
    E12_FIX_MODE,
    E13_FIX,
    EXAM_ITEMS,
    EXAM_TOTAL_POINTS,
    KIND_ACCOUNT,
    KIND_COMMAND,
    KIND_DRIVER,
    KIND_ERROR,
    KIND_ORDER,
    KIND_SERVICE,
    PRACTICE_ITEMS,
    REQ,
    X04_VENDOR,
    X07_CAN_EXEC,
    validate_items,
)
from app.v1.ampcr_pratique_pr10_course import PR10_SLUG, PR10_TITLE, pr10_course_sections
from app.v1.ampcr_pratique_pr10_figures import (
    ACC_ADMIN,
    ACC_DOMAIN,
    ACC_STANDARD,
    ACCOUNT_REFUSE,
    ACCOUNT_STEPS,
    CASE5_HOST,
    CASE5_PING_GW,
    CASE5_PING_NET,
    COMMANDS,
    COMMANDS_BY_NAME,
    DEV_ENABLE,
    DEV_HARDWARE,
    DEV_INSTALL,
    DEV_ROLLBACK,
    DEVICE_ID_SCREEN,
    DEVICE_STATES_BY_CODE,
    DEVICE_TREE,
    DRIVER_SOURCES,
    DRIVER_STEPS,
    ELEV_CONSENT,
    ELEV_CREDENTIALS,
    ELEV_NONE,
    ELEV_REFUSED,
    ELEV_SUDO,
    IPCONFIG_FIGURE_SCREEN,
    LINUX,
    LS_COMPTA_SCREEN,
    NEED_ADMIN,
    NEED_CENTRAL,
    NEED_DAILY,
    NEED_SHARED,
    NET_USER_SCREEN,
    NETWORK_STEPS,
    PERM_EXAMPLE_MODE,
    PR10_FIGURES,
    PROCEDURES,
    SCREEN_WIDTH,
    SERVICE_STEPS,
    SFC_DENIED_SCREEN,
    SFC_UNREPAIRED_SCREEN,
    SVC_DIAGNOSE,
    SVC_ENABLE,
    SVC_ENABLE_START,
    SVC_OK,
    SYSTEMCTL_CUPS_SCREEN,
    WINDOWS,
    account_for,
    can_access,
    device_action,
    elevation,
    mode_octal,
    mode_string,
    needs_admin,
    parse_hardware_id,
    permission_class,
    service_fix,
    vendor_name,
)
from app.v1.ampcr_pratique_pr24_figures import ping_stats
from app.v1.ampcr_pratique_visuals import render_figure, validate_figure
from app.v1.models import Question, QuestionnaireSession, SessionMode
from app.v1.question_engine import validate_content
from app.v1.session_service import _pedagogical_context_for, available_session_lengths
from tests.test_ticket94_french_fr06_10 import (
    _answer_all_and_submit,
    _patch_fake_provider,
    _start_session,
)

SLUG = "ampcr-pratique-pr10"
TICKET_COMMANDS = ("ipconfig", "ping", "tracert", "nslookup", "sfc", "DISM", "tasklist", "net user",
                   "ip", "systemctl", "journalctl", "lsblk", "df", "chmod", "chown", "apt / dnf")


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _course_raw() -> str:
    return " ".join(c for _t, c in pr10_course_sections())


def _course_text() -> str:
    return _text(_course_raw()).replace("**", "").replace("`", "").lower()


def _all_items_text() -> str:
    return " ".join(
        " ".join((i.title, i.context, *i.instructions, *i.correction, *(c.expected for c in i.criteria),
                  *(d.content_text for d in i.documents)))
        for i in PRACTICE_ITEMS + EXAM_ITEMS
    )


def _pr10(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "PR10")
    return module, uaa


# =============================================================================================
# 1. Données de référence, recontrôlées indépendamment
# =============================================================================================


def test_least_privilege_and_elevation():
    assert account_for(NEED_DAILY) == ACC_STANDARD.name
    assert account_for(NEED_ADMIN) == ACC_ADMIN.name
    assert account_for(NEED_CENTRAL) == ACC_DOMAIN.name
    assert account_for(NEED_SHARED) == ACCOUNT_REFUSE
    # UAC par défaut : standard → identifiants d'un administrateur ; administrateur → Oui/Non.
    assert elevation(WINDOWS, is_admin=False, needs_admin=True) == ELEV_CREDENTIALS
    assert elevation(WINDOWS, is_admin=True, needs_admin=True) == ELEV_CONSENT
    assert elevation(LINUX, is_admin=True, needs_admin=True) == ELEV_SUDO
    assert elevation(LINUX, is_admin=False, needs_admin=True) == ELEV_REFUSED
    for os_name in (WINDOWS, LINUX):
        for admin in (True, False):
            assert elevation(os_name, is_admin=admin, needs_admin=False) == ELEV_NONE
    with pytest.raises(ValueError):
        elevation("macOS", is_admin=True, needs_admin=True)
    assert "sudoers" in ELEV_REFUSED and "Oui / Non" in ELEV_CONSENT
    assert ACCOUNT_STEPS[0][0] == "Recueillir le besoin" and "net user nom * /add" in ACCOUNT_STEPS[2][1]


def test_linux_permissions():
    assert mode_string("755") == "rwxr-xr-x" and mode_string("640") == "rw-r-----"
    assert mode_string("770") == "rwxrwx---" and mode_string("600") == "rw-------"
    assert mode_octal("-rw-r-----") == "640" and mode_octal("drwxr-x---") == "750"
    for octal in ("000", "111", "644", "751", "777"):
        assert mode_octal(mode_string(octal)) == octal
    with pytest.raises(ValueError):
        mode_string("78")
    with pytest.raises(ValueError):
        mode_octal("rwxr-xr-q")
    # La première classe qui correspond s'applique, sans « repli » sur le groupe.
    assert permission_class("anne", ("anne", "compta"), "anne", "compta") == "propriétaire"
    assert not can_access("anne", ("anne", "compta"), "anne", "compta", "----rw----", "r")
    assert can_access("julie", ("compta",), "anne", "compta", PERM_EXAMPLE_MODE, "r")
    assert not can_access("julie", ("compta",), "anne", "compta", PERM_EXAMPLE_MODE, "w")
    assert not can_access("paul", ("paul",), "anne", "compta", PERM_EXAMPLE_MODE, "r")
    assert (E12_CAN_READ, E12_CAN_WRITE, E12_FIX_MODE) == (True, False, "rwxrwx---")
    assert X07_CAN_EXEC is False


def test_device_states_and_hardware_ids():
    assert set(DEVICE_STATES_BY_CODE) == {28, 22, 10, 43}
    assert "ne sont pas installés. (Code 28)" in DEVICE_STATES_BY_CODE[28].message
    assert "désactivé. (Code 22)" in DEVICE_STATES_BY_CODE[22].message
    assert "(Code 43)" in DEVICE_STATES_BY_CODE[43].message and "signalé des problèmes" in DEVICE_STATES_BY_CODE[43].message
    assert device_action(28) == DEV_INSTALL and device_action(22) == DEV_ENABLE
    assert device_action(10, after_driver_update=True) == DEV_ROLLBACK and device_action(10) == DEV_INSTALL
    assert device_action(43) == DEV_HARDWARE
    hw = parse_hardware_id("PCI\\VEN_14E4&DEV_43A0&SUBSYS_0619106B")
    assert (hw.bus, hw.vendor_id, hw.device_id) == ("PCI", "14E4", "43A0")
    assert vendor_name("PCI\\VEN_14E4&DEV_43A0") == "Broadcom" and vendor_name("PCI\\VEN_10ec&DEV_8168") == "Realtek"
    usb = parse_hardware_id("USB\\VID_04F9&PID_0062&REV_0100")
    assert (usb.bus, usb.vendor_id, usb.device_id) == ("USB", "04F9", "0062")
    assert vendor_name("USB\\VID_046D&PID_C52B") == "Logitech" and vendor_name("USB\\VID_FFFF&PID_0001") is None
    assert (E11_VENDOR, X04_VENDOR) == ("Intel", "Brother")
    with pytest.raises(ValueError):
        parse_hardware_id("HDAUDIO\\FUNC_01")
    assert "À refuser" in DRIVER_SOURCES[-1][1] and DRIVER_SOURCES[0][0].startswith("Windows Update")
    assert "PCI\\VEN_14E4&DEV_43A0" in " ".join(DEVICE_ID_SCREEN)


def test_service_rule():
    assert service_fix(enabled=True, running=True) == SVC_OK
    assert service_fix(enabled=False, running=False) == SVC_ENABLE_START == E13_FIX
    assert service_fix(enabled=False, running=True) == SVC_ENABLE
    assert service_fix(enabled=True, running=False) == SVC_DIAGNOSE
    assert service_fix(enabled=True, running=False, failed=True) == SVC_DIAGNOSE
    cups = " ".join(SYSTEMCTL_CUPS_SCREEN)
    assert "disabled;" in cups and "inactive (dead)" in cups and "Scheduler is not running" in cups


def test_commands_cover_ticket_with_rights_and_risks():
    assert tuple(c.name for c in COMMANDS) == TICKET_COMMANDS
    for command in COMMANDS:
        for field in (command.syntax, command.role, command.output, command.rights, command.risk):
            assert field.strip(), (command.name, field)
    # Droits : documentation Microsoft et pages de manuel.
    for name in ("sfc", "DISM"):
        assert "administrateur" in COMMANDS_BY_NAME[name].rights
    assert COMMANDS_BY_NAME["DISM"].syntax == "DISM /Online /Cleanup-Image /RestoreHealth"
    assert COMMANDS_BY_NAME["sfc"].syntax == "sfc /scannow"
    assert "/release" in COMMANDS_BY_NAME["ipconfig"].rights and "/release" in COMMANDS_BY_NAME["ipconfig"].risk
    assert "sudo" in COMMANDS_BY_NAME["chown"].rights and "777" in COMMANDS_BY_NAME["chmod"].risk
    assert "*" in COMMANDS_BY_NAME["net user"].risk
    # needs_admin : lecture → standard ; modification → élévation.
    for read_only in ("ipconfig /all", "ping 192.168.1.1", "tracert -d 203.0.113.10", "nslookup www.exemple.be",
                      "tasklist", "net user", "net user marie", "ip a", "systemctl status cups", "journalctl -u cups",
                      "lsblk -f", "df -h", "chmod 640 budget.ods", "apt search vlc"):
        assert not needs_admin(read_only), read_only
    for admin in ("ipconfig /release", "ipconfig /flushdns", "sfc /scannow", "DISM /Online /Cleanup-Image /RestoreHealth",
                  "net user julie * /add", "net localgroup Administrateurs marie /delete", "sudo systemctl restart cups",
                  "systemctl enable cups", "chown anne x", "sudo apt install vlc", "dnf install vlc"):
        assert needs_admin(admin), admin
    assert [needs_admin(c) for c in E06_COMMANDS].count(True) == 5


def test_procedures_order():
    assert len(PROCEDURES) == 4
    driver = [label for label, _d in DRIVER_STEPS]
    assert driver[0] == "Identifier le périphérique" and driver[-1] == "Contrôler"
    assert driver.index("Créer un point de restauration") < driver.index("Installer ou restaurer")
    service = [label for label, _d in SERVICE_STEPS]
    assert service.index("Lire son état") < service.index("Chercher la cause") < service.index("Corriger et démarrer")
    network = [label for label, _d in NETWORK_STEPS]
    assert network.index("Tester la passerelle") < network.index("Tester une adresse Internet") < network.index("Tester le nom")


def test_screens_readable_and_consistent():
    screens = (NET_USER_SCREEN, SFC_DENIED_SCREEN, SFC_UNREPAIRED_SCREEN, SYSTEMCTL_CUPS_SCREEN, LS_COMPTA_SCREEN,
               DEVICE_ID_SCREEN, IPCONFIG_FIGURE_SCREEN, CASE5_PING_NET)
    for screen in screens:
        assert max(len(line) for line in screen) <= SCREEN_WIDTH
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        for document in item.documents:
            assert max(len(line) for line in document.content_text.split("\n")) <= SCREEN_WIDTH, item.key
    assert "*Administrateurs" in " ".join(NET_USER_SCREEN)
    assert "drwxr-x--- 2 root compta" in " ".join(LS_COMPTA_SCREEN) and "1005(compta)" in " ".join(LS_COMPTA_SCREEN)
    # Cas 5 : passerelle mal saisie, qui ne répond pas ; après correction, Internet répond.
    assert CASE5_HOST.gateway == "192.168.1.254" and ping_stats(CASE5_PING_GW) == (4, 0, 4)
    assert ping_stats(CASE5_PING_NET) == (4, 4, 0)
    assert "   Passerelle défaut. : 192.168.1.254" in IPCONFIG_FIGURE_SCREEN


# =============================================================================================
# 2. Schémas
# =============================================================================================


def test_figures_valid_accessible_and_unique():
    keys = [f.key for f in PR10_FIGURES]
    assert len(keys) == len(set(keys)) == 10
    for figure in PR10_FIGURES:
        assert validate_figure(figure) == [], figure.key
        html = str(render_figure(figure))
        assert 'role="img"' in html and "(schéma non officiel)" in html and not figure.official


def test_figures_drawn_from_data():
    by_key = {f.key: f for f in PR10_FIGURES}
    for key, steps in (("pr10-comptes", ACCOUNT_STEPS), ("pr10-pilote", DRIVER_STEPS),
                       ("pr10-service", SERVICE_STEPS), ("pr10-reseau", NETWORK_STEPS)):
        svg = by_key[key].svg
        for index, (label, _detail) in enumerate(steps, start=1):
            assert f"{index}. {escape(label)}" in svg, (key, label)
    perm = by_key["pr10-permissions"].svg
    assert re.findall(r'data-chars="([^"]+)"', perm) == ["-", "rw-", "r--", "---"]
    assert "chmod 640" in perm and "= 6" in perm and "= 4" in perm and "= 0" in perm
    assert by_key["pr10-peripherique"].svg.count("data-step=") == len(DEVICE_TREE)
    for key in ("pr10-net-user", "pr10-id-materiel", "pr10-systemctl", "pr10-ipconfig"):
        assert "fictive" in by_key[key].caption.lower() and "Capture fictive" in by_key[key].svg, key


# =============================================================================================
# 3. Exercices et mini-examen
# =============================================================================================


def test_items_valid_and_counts_match_ticket():
    assert validate_items() == []
    assert len(PRACTICE_ITEMS) >= 16 and len(EXAM_ITEMS) == 10  # ticket : ≥ 16 exercices, mini-examen /20
    assert sum(i.total_points for i in EXAM_ITEMS) == EXAM_TOTAL_POINTS == 20
    kinds = [i.kind for i in PRACTICE_ITEMS]
    for kind, minimum in ((KIND_ORDER, 3), (KIND_ACCOUNT, 4), (KIND_DRIVER, 2), (KIND_SERVICE, 1),
                          (KIND_COMMAND, 4), (KIND_ERROR, 1)):
        assert kinds.count(kind) >= minimum, kind
    keys = [i.key for i in PRACTICE_ITEMS + EXAM_ITEMS]
    assert len(keys) == len(set(keys))
    covered = {r for i in PRACTICE_ITEMS + EXAM_ITEMS for r in i.requirement_ids}
    assert REQ <= covered
    assert set(plan.COURSE_SLOTS_BY_CODE["PR10"].requirement_ids) == REQ
    types = [i.question_type for i in PRACTICE_ITEMS]
    assert types.count("ordering") == 3 and types.count("classification") == 5
    # Ticket : exercices avec extraits de console et captures.
    assert sum(1 for i in PRACTICE_ITEMS if any(d.kind == "console" for d in i.documents)) >= 8


def test_auto_corrected_answers():
    by_key = {i.key: i for i in PRACTICE_ITEMS}

    def ordered(key: str) -> list[str]:
        o = by_key[key].ordering
        return [o.steps[i].split(" — ")[0] for i in o.correct]

    assert ordered("E01") == [label for label, _d in ACCOUNT_STEPS]
    assert ordered("E02") == [label for label, _d in DRIVER_STEPS]
    assert ordered("E03") == [label for label, _d in SERVICE_STEPS]

    def answers(key: str) -> dict[str, str]:
        c = by_key[key].classification
        return dict(zip(c.elements, (c.categories[i] for i in c.correct), strict=True))

    e04 = answers("E04")
    assert next(v for k, v in e04.items() if "passerelle et le serveur DNS" in k) == "ipconfig"
    assert next(v for k, v in e04.items() if "routeur" in k) == "tracert"
    assert next(v for k, v in e04.items() if "magasin" in k) == "DISM"
    assert next(v for k, v in e04.items() if "spoolsv" in k) == "tasklist"
    e05 = answers("E05")
    assert next(v for k, v in e05.items() if "UUID" in k) == "lsblk"
    assert next(v for k, v in e05.items() if "propriété" in k) == "chown"
    assert next(v for k, v in e05.items() if "exécutable" in k) == "chmod"
    e06 = answers("E06")
    assert e06["ipconfig /all"] == "Compte standard" and e06["ipconfig /release"].startswith("Administrateur")
    assert e06["sfc /scannow"].startswith("Administrateur") and e06["systemctl status cups"] == "Compte standard"
    e07 = answers("E07")
    assert next(v for k, v in e07.items() if "stagiaire" in k) == ACCOUNT_REFUSE
    assert next(v for k, v in e07.items() if "contrôleur de domaine" in k) == ACC_DOMAIN.name
    assert next(v for k, v in e07.items() if "secrétaire" in k) == ACC_STANDARD.name
    e08 = answers("E08")
    assert next(v for k, v in e08.items() if "mise à jour de son pilote" in k) == DEV_ROLLBACK
    assert next(v for k, v in e08.items() if "Code 22" in k) == DEV_ENABLE
    assert next(v for k, v in e08.items() if "Code 43" in k) == DEV_HARDWARE
    for item in PRACTICE_ITEMS:  # aucune remise en ordre déjà dans l'ordre attendu
        if item.ordering:
            assert list(item.ordering.correct) != list(range(len(item.ordering.steps))), item.key


def test_no_false_technical_claims_anywhere():
    text = _course_text() + " " + _all_items_text().lower()
    for right in ("moindre privilège", "compte de domaine", "contrôleur de domaine", "net user nom * /add",
                  "net localgroup administrateurs", "usermod -ag", "lpadmin", "uac", "sudoers", "chmod 770",
                  "chmod u+x", "chown anne:compta", "jamais 777", "restaurer le pilote", "point de restauration",
                  "code 28", "code 43", "id du matériel", "ven_", "vid_", "64 bits", "services.msc",
                  "enable --now", "journalctl -u", "dism /online /cleanup-image /restorehealth", "sfc /scannow",
                  "invite de commandes en administrateur", "ipconfig /all", "tracert -d", "nslookup",
                  "default via", "network is unreachable", "lsblk -f", "df -h", "apt update",
                  "documentation de l'éditeur fait foi"):
        assert right in text, right
    for wrong in ("désactiver l'uac pour", "chmod -r 777 pour corriger", "sfc répare sans droits",
                  "un compte commun est recommandé", "sfc /scannow puis dism", "ipconfig /release sans risque",
                  "tout le monde administrateur", "pilote 32 bits sur un windows 64 bits fonctionne"):
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


def test_five_resolved_cases_four_procedures_and_exam_not_in_course():
    text = _text(_course_raw())
    for case in ("Cas 1 — Pilote absent", "Cas 2 — Droits insuffisants", "Cas 3 — Service arrêté",
                 "Cas 4 — Périphérique USB", "Cas 5 — Configuration réseau"):
        assert case in text, case
    assert text.count("Conclusion rédigée.") == 5
    for i in range(1, 5):
        assert f"Procédure {i} —" in text, i
    course = _course_raw()
    for item in EXAM_ITEMS:
        assert item.context not in course and escape(item.context) not in course, item.key
    for item in PRACTICE_ITEMS:
        assert escape(item.context) in course, item.key


def test_course_teaches_every_mandatory_point():
    titles = [t for t, _ in pr10_course_sections()]
    assert len(titles) == len(set(titles))
    text = _course_text()
    for notion in (
        # matière du ticket, dans l'ordre du cahier des charges
        "comptes locaux", "domaine", "utilisateur", "administrateur", "groupes", "uac", "sudo",
        "moindre privilège", "installation", "mettre à jour", "restaurer", "périphérique inconnu",
        "compatibilité", "paramètres", "gestionnaire de périphériques", "services", "démarrage",
        "ipconfig", "ping", "tracert", "nslookup", "sfc", "dism", "tasklist", "net user", "ip a", "systemctl",
        "journalctl", "lsblk", "df", "chmod", "chown", "apt", "dnf",
        "syntaxe", "rôle", "sortie attendue", "droits nécessaires", "risques",
        # encadrés
        "objectifs", "procédure professionnelle", "erreur fréquente", "à l'écrit", "repère rapide", "glossaire",
    ):
        assert notion in text, notion
    for name in TICKET_COMMANDS:  # une fiche par commande
        assert f"### {name}" in _course_raw(), name


def test_course_flags_requirements_links_and_fictive_supports():
    raw = _course_raw()
    text = _text(raw)
    for req in ("AP-05", "AP-11", "AP-12"):
        assert req in text
    assert "Compléments pédagogiques" in text and "fictif" in text.lower()
    assert "aucune n'est une question officielle" in text.lower()
    assert "aucun schéma n'est tiré d'une image générée" in text.lower()
    assert "conventions du cours" in text.lower() and "en anglais" in text.lower() and "en français" in text.lower()
    for link in ("/uaa/ampcr-mc10", "/uaa/ampcr-mc11", "/uaa/ampcr-mc12", "/uaa/ampcr-pratique-pr07",
                 "/uaa/ampcr-pratique-pr08", "/uaa/ampcr-pratique-pr09", "/uaa/ampcr-pratique-pr11",
                 "/uaa/ampcr-pratique-pr20", "/uaa/ampcr-pratique-pr24", f"/uaa/{PR10_SLUG}/practice",
                 f"/uaa/{PR10_SLUG}/exam"):
        assert link in raw, link
    # PR12 et PR22 ne sont pas encore publiés : renvoi en texte seulement.
    for unpublished in ("/uaa/ampcr-pratique-pr12", "/uaa/ampcr-pratique-pr22"):
        assert unpublished not in raw
    anchors = set(re.findall(r'id="(pr10-e\d\d)"', raw))
    assert anchors == {f"pr10-{i.key.lower()}" for i in PRACTICE_ITEMS}
    assert "(#pr10-" not in raw


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(t) for t, _ in pr10_course_sections()]
    assert kinds[:13] == ["theory"] * 13
    assert kinds[13:] == ["example", "warning", "exercise", "exam", "summary", "info"]


# =============================================================================================
# 5. Banque, seed et intégration au moteur
# =============================================================================================


def test_plan_slot_matches_ticket():
    slot = plan.COURSE_SLOTS_BY_CODE["PR10"]
    assert slot.ticket == 214 and slot.title == PR10_TITLE == PRACTICAL_COURSES_BY_CODE["PR10"].title


def test_seed_publishes_pr10_in_practical_module_idempotently(db_session):
    module, uaa = _pr10(db_session)
    assert uaa.slug == SLUG and uaa.is_published and uaa.title == PR10_TITLE and uaa.position == 10
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="PR10").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(pr10_course_sections())
    assert {"PR09", "PR10", "PR11"} <= set(plan.published_uaas(db_session))
    ordered = [u.code for u in sorted(module.uaas, key=lambda u: (u.position, u.id))]
    assert ordered.index("PR09") < ordered.index("PR10") < ordered.index("PR11")
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_reserves_and_documents(db_session):
    module, uaa = _pr10(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert import_practical_bank(db_session, module, uaa) == len(PRACTICE_ITEMS) + len(EXAM_ITEMS)
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    usages = [question_usage(q) for q in questions]
    assert usages.count("practice") == len(PRACTICE_ITEMS) and usages.count("exam") == 10


def test_correction_context_is_pr10_specific():
    context = _pedagogical_context_for("PR10")
    assert context is get_practical_context("PR10")
    assert context.course_key == SLUG
    notions = " ".join(context.allowed_notions)
    for notion in ("net user nom * /add", "moindre privilège", "Code 28", "VEN_xxxx", "enable --now",
                   "DISM puis SFC", "default via", "chmod -R 777", "lpadmin"):
        assert notion in notions, notion
    assert ".\\nom" in notions and "PCI\\VEN_" in notions
    assert "mot-clé" in context.constraints and "UAC" in context.constraints


# =============================================================================================
# 6. Pages et sessions
# =============================================================================================


def test_course_page_renders_figures_and_exercises(client, db_session):
    _pr10(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert set(ids) >= {f"fig-{f.key}" for f in PR10_FIGURES}
    assert html.count('class="jc-exercise-card"') == len(PRACTICE_ITEMS)
    assert "<details open" not in html
    assert 'href="/ampcr-pratique"' in html and f"/uaa/{SLUG}/exam" in html
    assert "<table" in html and "jc-pr-console" in html


def test_practical_home_and_matrix_show_pr10(client, db_session):
    _pr10(db_session)
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and re.search(r"\d+ cours publiés sur 30 prévus", _text(home))  # PR12 (#215) publié ensuite
    for req in REQ:
        assert plan.requirement_status(req, {"PR10"}) == plan.STATUS_PARTIAL
    assert plan.VALIDATED_REQUIREMENT_IDS == audit_proven_ids()  # « validé » : preuves de l'audit #235
    assert client.get("/ampcr-pratique/matrice").status_code == 200


@pytest.mark.parametrize("mode", ["practice", "exam"])
def test_sessions_draw_only_from_their_reserve_without_generation(authenticated_client, db_session, monkeypatch, mode):
    fake = _patch_fake_provider(monkeypatch)
    _pr10(db_session)
    assert authenticated_client.get(f"/uaa/{SLUG}/{mode}").status_code == 200
    session_url = _start_session(authenticated_client, db_session, SLUG, mode)
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert {question_usage(sq.question_version.question) for sq in session.session_questions} == {mode}
    assert session.question_count == 10
    assert fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"PR10"}
    if mode == "exam":
        page = authenticated_client.get(f"{session_url}?q=1").text
        assert "Corrigé de référence" not in page and "Barème" not in page


def test_exam_lengths_limited_and_score_on_20(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _pr10(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    from app.v1.models import User

    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="PR10", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "/ 20" in html


def test_practice_sessions_with_classification_and_ordering_submit(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr10(db_session)
    for _ in range(2):  # 17 exercices : deux sessions de 10 couvrent toute la réserve
        session_url = _start_session(authenticated_client, db_session, SLUG, "practice")
        _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
        assert authenticated_client.get(session_url).status_code == 200
