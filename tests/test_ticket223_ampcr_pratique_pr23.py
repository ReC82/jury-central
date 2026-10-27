"""Ticket #223 — AMPCR pratique écrite, PR23 « Partage de dossiers, imprimantes et permissions ».

Couvre : données de référence et calculs **recontrôlés ici** indépendamment (chemins UNC, droit
d'un compte dans une barrière avec cumul et refus, héritage NTFS, combinaison partage + NTFS par
le réseau et en local, matrice des droits, droits Unix rwx, ACL, Samba, ordre des diagnostics
d'accès et d'impression) ; relevés fictifs (format, largeur) ; schémas SVG (validité,
accessibilité, données dessinées, schémas à compléter sans leurs réponses, fichiers statiques) ;
exercices et mini-examen (format du socle, classements et remises en ordre auto-corrigés, valeurs
des corrigés) ; cours (matière du ticket, 3 procédures, 5 cas résolus, liens, rendu des chemins
UNC, supports fictifs, cartes) ; banque, seed, pages et sessions.
Aucun appel IA réel : `FakeAIProvider` partout."""

import re
from html import escape
from pathlib import Path

import pytest

from app.content import render_markdown
from app.models import UAA, Module
from app.seed import seed
from app.v1 import ampcr_pratique_plan as plan
from app.v1.ampcr_pratique_bank import (
    PRACTICAL_BANK_IMPORTERS,
    PRACTICAL_COURSES_BY_CODE,
    _document_layout,
    get_practical_context,
    import_practical_bank,
    item_content,
    question_usage,
)
from app.v1.ampcr_pratique_pr23_bank import (
    EXAM_ITEMS,
    EXAM_TOTAL_POINTS,
    KIND_DIAG,
    KIND_MATRIX,
    KIND_ORDER,
    KIND_PRINT,
    KIND_SCHEMA,
    PRACTICE_ITEMS,
    REQ,
    validate_items,
)
from app.v1.ampcr_pratique_pr23_course import CASES, PR23_SLUG, PR23_TITLE, pr23_course_sections
from app.v1.ampcr_pratique_pr23_figures import (
    ACCESS_MATRIX,
    AUTH_USERS,
    CLAIRE,
    EVERYONE,
    JULIE,
    LEVEL_FULL,
    LEVEL_MODIFY,
    LEVEL_NONE,
    LEVEL_READ,
    LIMIT_NTFS,
    LIMIT_SHARE,
    LX_USERS,
    NET_PRINTER_IP,
    NTFS_TREE,
    P_DEVICE,
    P_DRIVER,
    P_HOST,
    P_OK,
    P_QUEUE,
    P_RIGHT,
    PR23_FIGURES,
    PRINT_KEYS,
    PRINTER_STEPS,
    PROCEDURES,
    S_AUTH,
    S_NAME,
    S_NET,
    S_OK,
    S_RIGHTS,
    S_SHARE,
    S_SMB,
    SAM,
    SCREEN_WIDTH,
    SERVER_IP,
    SERVER_NAME,
    SHARE_KEYS,
    SHARE_ROOT,
    SHARE_STEPS,
    SHARES,
    STATIC_FIGURES,
    TROUBLE_STEPS,
    AccessState,
    Ace,
    Folder,
    LinuxUser,
    PrintState,
    SambaShare,
    access_matrix,
    all_capture_lines,
    effective_access,
    first_failure,
    get_printer_lines,
    icacls_lines,
    layer_level,
    limiting_layer,
    linux_effective,
    mode_string,
    net_share_lines,
    net_use_lines,
    net_view_lines,
    ntfs_acl,
    ping_lines,
    port_test_lines,
    print_checks,
    print_diagnosis,
    samba_level,
    share_checks,
    share_diagnosis,
    static_svg,
    unc,
    unc_parts,
    unix_access,
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

SLUG = "ampcr-pratique-pr23"
STATIC_DIR = Path(__file__).resolve().parent.parent / "app" / "static"
COMPTA, PAIE, ARCHIVES = (f"{SHARE_ROOT}\\Compta", f"{SHARE_ROOT}\\Compta\\Paie", f"{SHARE_ROOT}\\Archives")


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _course_raw() -> str:
    return " ".join(c for _t, c in pr23_course_sections())


def _course_text() -> str:
    return _text(_course_raw()).replace("**", "").replace("`", "").lower()


def _all_items_text() -> str:
    return " ".join(
        " ".join((i.title, i.context, *i.instructions, *i.correction, *(c.expected for c in i.criteria),
                  *(d.content_text for d in i.documents)))
        for i in PRACTICE_ITEMS + EXAM_ITEMS
    )


def _item(key: str):
    return next(i for i in PRACTICE_ITEMS + EXAM_ITEMS if i.key == key)


def _pr23(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "PR23")
    return module, uaa


# =============================================================================================
# 1. Données de référence et calculs, recontrôlés indépendamment
# =============================================================================================


def test_unc_paths():
    assert unc(SERVER_NAME, "Compta") == "\\\\SRV-FICH\\Compta"
    assert unc_parts("\\\\SRV-FICH\\Compta\\2026\\factures.xlsx") == {
        "serveur": "SRV-FICH", "partage": "Compta", "chemin": "2026\\factures.xlsx"}
    assert unc_parts("\\\\192.168.20.20\\Commun")["serveur"] == SERVER_IP
    for bad in ("SRV-FICH\\Compta", "\\\\SRV-FICH", "C:\\Partages"):
        with pytest.raises(ValueError):
            unc_parts(bad)


def test_layer_rules_cumulative_deny_and_inheritance():
    groups = ("x", "G_A", "G_B")
    assert layer_level((Ace("G_A", "Lecture et exécution"), Ace("G_B", "Modification")), groups) == LEVEL_MODIFY
    assert layer_level((Ace("G_C", "Contrôle total"),), groups) == LEVEL_NONE
    # refus explicite : gagne contre tout
    assert layer_level((Ace("G_A", "Contrôle total"), Ace("G_B", "Contrôle total", deny=True)), groups) == LEVEL_NONE
    # refus hérité : une autorisation explicite l'emporte, une autorisation héritée non
    assert layer_level((Ace("G_A", "Modification"), Ace("G_B", "Contrôle total", deny=True, inherited=True)),
                       groups) == LEVEL_MODIFY
    assert layer_level((Ace("G_A", "Modification", inherited=True), Ace("G_B", "Contrôle total", deny=True, inherited=True)),
                       groups) == LEVEL_NONE
    # héritage
    factures = ntfs_acl(f"{COMPTA}\\Factures")
    assert all(a.inherited for a in factures) and {a.principal for a in factures} == {"G_Compta", "G_Direction", "Administrateurs"}
    assert {a.principal for a in ntfs_acl(PAIE)} == {"Administrateurs", "G_Direction"} and not NTFS_TREE[PAIE].inherit
    assert [a.inherited for a in ntfs_acl(COMPTA)] == [False, False, True]


def test_effective_access_matrix_recomputed():
    assert ACCESS_MATRIX == {
        "jmartin": {"Commun": LEVEL_MODIFY, "Compta": LEVEL_MODIFY, "Compta\\Factures": LEVEL_MODIFY,
                    "Compta\\Paie": LEVEL_NONE, "Direction": LEVEL_NONE, "Archives": LEVEL_READ},
        "cdupont": {"Commun": LEVEL_MODIFY, "Compta": LEVEL_READ, "Compta\\Factures": LEVEL_READ,
                    "Compta\\Paie": LEVEL_MODIFY, "Direction": LEVEL_MODIFY, "Archives": LEVEL_READ},
        "sroux": {"Commun": LEVEL_MODIFY, "Compta": LEVEL_NONE, "Compta\\Factures": LEVEL_NONE,
                  "Compta\\Paie": LEVEL_NONE, "Direction": LEVEL_NONE, "Archives": LEVEL_READ},
    }
    # en local : NTFS seul (Julie modifie Archives sur le serveur)
    assert access_matrix(remote=False)["jmartin"]["Archives"] == LEVEL_MODIFY
    assert limiting_layer(JULIE, ARCHIVES) == LIMIT_SHARE and limiting_layer(CLAIRE, COMPTA) == LIMIT_NTFS
    # la plus restrictive, jamais la plus forte
    for account in (JULIE, CLAIRE, SAM):
        for path in NTFS_TREE:
            if path == SHARE_ROOT:
                continue
            remote, local = effective_access(account, path), effective_access(account, path, remote=False)
            assert [LEVEL_NONE, LEVEL_READ, LEVEL_MODIFY, LEVEL_FULL].index(remote) <= \
                [LEVEL_NONE, LEVEL_READ, LEVEL_MODIFY, LEVEL_FULL].index(local)
    assert {e.principal for s in SHARES.values() for e in s.entries} <= {AUTH_USERS, "G_Direction"}
    assert EVERYONE in JULIE.all_groups() and AUTH_USERS in JULIE.all_groups()


def test_linux_rwx_acl_and_samba():
    assert mode_string(0o2770) == "drwxrws---" and mode_string(0o750) == "drwxr-x---"
    assert mode_string(0o2750, acl=True) == "drwxr-s---+" and mode_string(0o2740) == "drwxr-S---"
    assert mode_string(0o644, directory=False) == "-rw-r--r--"
    # classes non cumulées : le propriétaire n'a que ses droits
    assert unix_access(0o077, "bob", "staff", "bob", ("staff",)) == "---"
    assert unix_access(0o750, "root", "rh", "lina", ("compta",)) == "---"
    assert unix_access(0o750, "root", "rh", "lina", ("rh",)) == "r-x"
    assert unix_access(0o2770, "root", "compta", "paul", ("direction",), {"direction": "r-x"}) == "r-x"
    assert unix_access(0o2770, "root", "compta", "x", ("compta", "direction"), {"direction": "r-x"}) == "rwx"
    share = SambaShare("s", "/s", ("a", "b"), read_only=True, write_list=("a",))
    assert samba_level(share, ("a",)) == LEVEL_MODIFY and samba_level(share, ("b",)) == LEVEL_READ
    assert samba_level(share, ("c",)) == LEVEL_NONE
    assert samba_level(SambaShare("s", "/s", (), read_only=False), ("z",)) == LEVEL_MODIFY
    assert [linux_effective(u) for u in LX_USERS] == [LEVEL_MODIFY, LEVEL_READ, LEVEL_NONE]
    # Samba autorise l'écriture mais Unix ne donne rien : aucun accès
    assert linux_effective(LinuxUser("max", ("direction",)), acl={}, share=SambaShare("s", "/s", ("direction",), False)) == LEVEL_NONE


def test_share_and_print_diagnosis_order():
    assert SHARE_KEYS == ("ip", "nom", "smb", "partage", "compte", "droits")
    for key, diag in zip(SHARE_KEYS, (S_NET, S_NAME, S_SMB, S_SHARE, S_AUTH, S_RIGHTS), strict=True):
        assert share_diagnosis(first_failure(key)) == diag
    assert share_diagnosis(share_checks(AccessState())) == S_OK
    assert share_diagnosis(share_checks(AccessState(effective=LEVEL_READ, needed=LEVEL_MODIFY))) == S_RIGHTS
    assert share_diagnosis(share_checks(AccessState(name_ok=False, credentials_ok=False))) == S_NAME
    assert PRINT_KEYS == ("hote", "imprimante", "file", "pilote", "droit")
    for key, diag in zip(PRINT_KEYS, (P_HOST, P_DEVICE, P_QUEUE, P_DRIVER, P_RIGHT), strict=True):
        assert print_diagnosis(first_failure(key, PRINT_KEYS)) == diag
    assert print_diagnosis(print_checks(PrintState())) == P_OK
    assert print_diagnosis(print_checks(PrintState(device_ip="192.168.20.117"))) == P_DEVICE
    assert print_diagnosis(print_checks(PrintState(spooler_running=False, driver_ok=False))) == P_QUEUE


def test_procedures_order():
    labels = [label for label, _d in SHARE_STEPS]
    assert labels.index("Régler NTFS") < labels.index("Partager") < labels.index("Tester depuis un poste")
    printer = [label for label, _d in PRINTER_STEPS]
    assert printer.index("Fixer son adresse") < printer.index("Connecter les postes")
    trouble = [label for label, _d in TROUBLE_STEPS]
    assert trouble[1:7] == ["Adresse IP", "Nom", "Partage de fichiers", "Nom du partage", "Compte", "Permissions"]
    assert len(PROCEDURES) == 3


def test_captures_format_and_width():
    lines = (
        *all_capture_lines(), *icacls_lines(ARCHIVES), *icacls_lines(PAIE), *net_share_lines(SHARES["Archives"]),
        *net_use_lines(unc(SERVER_NAME, "Compta"), error=5), *net_use_lines(unc(SERVER_IP, "Commun")),
        *ping_lines(SERVER_NAME, ip=None), *ping_lines(SERVER_IP, ip=SERVER_IP),
        *ping_lines(NET_PRINTER_IP, ip=NET_PRINTER_IP, replies=False),
        *port_test_lines(SERVER_NAME, SERVER_IP, open_=False), *get_printer_lines("Offline"),
        *net_view_lines(SERVER_NAME, tuple(SHARES)),
    )
    assert all(len(line) <= SCREEN_WIDTH for line in lines), [line for line in lines if len(line) > SCREEN_WIDTH]
    assert "Erreur système 5." in net_use_lines("\\\\S\\P", error=5) and "Accès refusé." in net_use_lines("\\\\S\\P", error=5)
    assert "  DUPONT\\G_Compta:(I)(OI)(CI)(M)" in icacls_lines(f"{COMPTA}\\Factures")
    assert "  AUTORITE NT\\Utilisateurs authentifiés, READ" in net_share_lines(SHARES["Archives"])
    assert "TcpTestSucceeded : False" in port_test_lines("S", "1.2.3.4", open_=False)
    with pytest.raises(ValueError):
        icacls_lines(COMPTA, {**NTFS_TREE, COMPTA: Folder(COMPTA, (Ace("G_X", "Contrôle total", deny=True),))})


# =============================================================================================
# 2. Schémas
# =============================================================================================


def test_figures_valid_accessible_and_unique():
    all_figures = PR23_FIGURES + tuple(f for f, _p in STATIC_FIGURES)
    keys = [f.key for f in all_figures]
    assert len(keys) == len(set(keys)) == 16 and len(PR23_FIGURES) >= 4  # ticket : ≥ 4 schémas
    for figure in all_figures:
        assert validate_figure(figure) == [], figure.key
        html = str(render_figure(figure))
        assert 'role="img"' in html and "(schéma non officiel)" in html and not figure.official


def test_figures_drawn_from_data():
    by_key = {f.key: f for f in PR23_FIGURES}
    matrix = by_key["pr23-matrice-droits"].svg
    for login, row in ACCESS_MATRIX.items():
        for folder, value in row.items():
            assert f'data-cell="{escape(login)}|{escape(folder)}" data-value="{escape(value)}"' in matrix
    layers = by_key["pr23-deux-barrieres"].svg
    assert "→ droit du compte : Lecture" in layers and "→ droit du compte : Modification" in layers
    assert "la plus restrictive :" in layers and "NTFS seul :" in layers
    tree = by_key["pr23-heritage"].svg
    assert "héritage désactivé" in tree and "(hérité)" in tree and "(posé ici)" in tree
    unix = by_key["pr23-droits-unix"].svg
    assert "drwxrws---+" in unix and "paul (groupe direction) → Lecture" in unix and "sam (groupe secretariat) → Aucun accès" in unix
    printers = by_key["pr23-imprimantes"].svg
    assert escape("\\\\PC-ACCUEIL\\Laser-Accueil") in printers and f"IP fixe {NET_PRINTER_IP}" in printers
    unc_svg = by_key["pr23-chemin-unc"].svg
    assert escape("\\\\SRV-FICH\\Compta\\2026\\factures.xlsx") in unc_svg
    for key, (_title, steps) in zip(("pr23-procedure-partage", "pr23-procedure-imprimante", "pr23-procedure-depannage"),
                                    PROCEDURES, strict=True):
        for index, (label, _d) in enumerate(steps, start=1):
            assert f"{index}. {escape(label)}" in by_key[key].svg, (key, label)


def test_schemas_to_complete_hide_their_answers():
    by_key = {f.key: f.svg for f, _p in STATIC_FIGURES}
    unc_blank = by_key["pr23-unc-a-completer"]
    assert "SRV-FICH\\Compta\\2026" not in unc_blank and SERVER_IP not in unc_blank and all(f"{n} ?" in unc_blank for n in "①②③④")
    layers = by_key["pr23-barrieres-a-completer"]
    assert "droit du compte : Lecture" not in layers and "droit du compte : Modification" not in layers
    assert all(f"{n} ?" in layers for n in "①②③④")
    printers = by_key["pr23-imprimantes-a-completer"]
    assert "doit rester allumé" not in printers and NET_PRINTER_IP not in printers
    assert escape("\\\\PC-ACCUEIL\\Laser-Accueil") not in printers
    unix = by_key["pr23-unix-a-completer"]
    assert "rws — groupe" not in unix and "--- — tous les autres" not in unix and "→ Lecture" not in unix and "→ Aucun accès" not in unix


def test_static_figure_files_are_the_generated_svg():
    assert len(STATIC_FIGURES) == 4
    for figure, path in STATIC_FIGURES:
        content = (STATIC_DIR / path).read_text()
        assert content == static_svg(figure)
        assert content.startswith("<svg ") and "xmlns=" in content and "<title>" in content


# =============================================================================================
# 3. Exercices et mini-examen
# =============================================================================================


def test_items_valid_and_counts_match_ticket():
    assert validate_items() == []
    assert len(PRACTICE_ITEMS) >= 18 and len(EXAM_ITEMS) == 10  # ticket : ≥ 18 exercices, mini-examen /20
    assert sum(i.total_points for i in EXAM_ITEMS) == EXAM_TOTAL_POINTS == 20
    kinds = [i.kind for i in PRACTICE_ITEMS]
    assert kinds.count(KIND_SCHEMA) == 4
    assert sum(1 for k in kinds if k in (KIND_MATRIX, KIND_DIAG, KIND_PRINT, KIND_SCHEMA)) >= 17
    assert KIND_ORDER in kinds
    schema_images = {d.image for i in PRACTICE_ITEMS for d in i.documents if d.image}
    assert schema_images == {p for _f, p in STATIC_FIGURES}
    assert sum(1 for i in PRACTICE_ITEMS if any(d.kind == "console" for d in i.documents)) >= 5
    keys = [i.key for i in PRACTICE_ITEMS + EXAM_ITEMS]
    assert len(keys) == len(set(keys))
    covered = {r for i in PRACTICE_ITEMS + EXAM_ITEMS for r in i.requirement_ids}
    assert covered == REQ == set(plan.COURSE_SLOTS_BY_CODE["PR23"].requirement_ids)
    types = [i.question_type for i in PRACTICE_ITEMS]
    assert types.count("ordering") == 3 and types.count("classification") == 4


def test_auto_corrected_answers():
    def ordered(key: str) -> list[str]:
        item = _item(key)
        return [item.ordering.steps[i].split(" — ")[0] for i in item.ordering.correct]

    assert ordered("E01") == [label for label, _d in SHARE_STEPS]
    assert ordered("E02") == [label for label, _d in PRINTER_STEPS]
    assert ordered("E03") == [label for label, _d in TROUBLE_STEPS]

    def find(key: str, needle: str) -> str:
        c = _item(key).classification
        index = next(i for i, e in enumerate(c.elements) if needle in e)
        return c.categories[c.correct[index]]

    assert find("E04", "Consulter") == LEVEL_READ and find("E04", "logiciel de caisse") == LEVEL_READ
    assert find("E04", "Supprimer") == LEVEL_MODIFY and find("E04", "Renommer") == LEVEL_MODIFY
    assert find("E04", "autorisations") == LEVEL_FULL and find("E04", "possession") == LEVEL_FULL
    assert find("E05", "câble") == S_NET and find("E05", "s'ouvre, ") == S_NAME and find("E05", "Public") == S_SMB
    assert find("E05", "67") == S_SHARE and find("E05", "86") == S_AUTH and find("E05", "1219") == S_AUTH
    assert find("E05", "système 5") == S_RIGHTS and find("E05", "que Lecture") == S_RIGHTS
    assert find("E06", "éteint le soir") == P_HOST and find("E06", "192.168.20.117") == P_DEVICE
    assert find("E06", "bourrage") == P_DEVICE and find("E06", "PDF") == P_QUEUE and find("E06", "Spouleur") == P_QUEUE
    assert find("E06", "pilote") == P_DRIVER and find("E06", "G_Direction") == P_RIGHT
    assert find("E07", "lea ") == LEVEL_MODIFY and find("E07", "ines ") == LEVEL_MODIFY
    assert find("E07", "tom ") == LEVEL_READ and find("E07", "sam ") == LEVEL_READ
    assert find("E07", "max ") == LEVEL_NONE and find("E07", "zoe ") == LEVEL_NONE
    for item in PRACTICE_ITEMS:
        if item.ordering is not None:
            assert list(item.ordering.correct) != list(range(len(item.ordering.steps))), item.key
        if item.classification is not None:
            correct = list(item.classification.correct)
            # ticket #150 : la première catégorie n'est jamais la réponse de tous les premiers éléments
            assert correct[: len(item.classification.categories)] != list(range(len(item.classification.categories))), item.key
            assert len(set(correct)) == len(item.classification.categories), item.key


def test_values_in_corrections_match_calculations():
    def text(key: str) -> str:
        item = _item(key)
        return " ".join((*item.correction, *(c.expected for c in item.criteria)))

    assert "① SRV-FICH" in text("E08") and "\\\\192.168.20.20\\Compta\\2026\\factures.xlsx" in text("E08")
    assert "① Modification ; ② Lecture ; ③ Lecture ; ④ Lecture" in text("E09")
    assert "jmartin : Commun Modification" in text("E12") and "Compta\\Paie Aucun accès" in text("E12")
    assert "Archives pour jmartin" in text("E12") and "→ Lecture" in text("E12")
    assert "Modification" in text("E13") and "/inheritance:d" in text("E13")
    assert "Compta Aucun accès" in text("E14") and "Factures Aucun accès" in text("E14")
    assert "Lecture" in text("E15") and "le partage limite" in text("E15")
    assert "G_Secretariat" in text("E16") and "Sam → Lecture" in text("E16") and "Paie" in text("E16")
    assert "nslookup SRV-FICH" in text("E17") and "192.168.20.117" in text("E18") and "réservation dhcp" in text("E18").lower()
    assert "write list = @compta @direction" in text("E19") and "setfacl -m g:direction:rwx" in text("E19")
    assert "le partage limite" in text("X01") and "445" in text("X02") and "net view" in text("X03")
    assert "---" in text("X07") and "net stop spooler" in text("X09") and "1219" in text("X08")


def test_schema_documents_point_to_static_files():
    item = _item("E08")
    layout = _document_layout(item.documents[0])
    assert layout["kind"] == "figure" and layout["src"] == "/static/img/ampcr-pratique/pr23-unc-a-completer.svg"
    assert "SRV-FICH" in layout["alt"] and "non officiel" in layout["notice"]


def test_no_false_technical_claims_anywhere():
    text = _course_text() + " " + _all_items_text().lower()
    for right in ("smb", "445", "chemin unc", "profil", "pare-feu", "découverte du réseau", "autorisations du partage",
                  "ntfs", "la plus restrictive", "contrôle total", "héritage", "refus", "groupes", "samba", "rwx",
                  "acl", "file d'attente", "spouleur", "pilote", "hors connexion", "moindre privilège", "sauvegarde",
                  "accès refusé", "nom du serveur", "smb1"):
        assert right in text, right
    for wrong in ("désactiver le pare-feu pour", "réactiver smb1 pour", "chmod 777 pour que", "la plus permissive l'emporte",
                  "le partage s'applique aussi en local", "tout le monde : contrôle total est recommandé",
                  "la découverte du réseau est obligatoire"):
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
    assert len(CASES) == 5
    for title, *_r in CASES:
        assert escape(title) in _course_raw() or title in text, title
    assert text.count("Conclusion rédigée.") == 5
    for i in (1, 2, 3):
        assert f"Procédure {i} —" in text, i
    course = _course_raw()
    for item in EXAM_ITEMS:
        assert item.context not in course and escape(item.context) not in course, item.key
    for item in PRACTICE_ITEMS:
        assert escape(item.context) in course, item.key
    for figure, _path in STATIC_FIGURES:
        assert f'id="fig-{figure.key}"' in course, figure.key
    for figure in PR23_FIGURES:
        assert f'id="fig-{figure.key}"' in course, figure.key


def test_course_teaches_every_mandatory_point():
    titles = [t for t, _ in pr23_course_sections()]
    assert len(titles) == len(set(titles))
    text = _course_text()
    for notion in (
        # matière du ticket, dans l'ordre du cahier des charges
        "smb", "chemin unc", "\\\\serveur\\partage", "découverte du réseau", "authentification",
        "permissions de partage", "permissions ntfs", "combinaison effective", "lecture", "modification",
        "contrôle total", "héritage", "groupes", "samba", "rwx", "acl", "imprimante", "file d'attente",
        "accès local", "distant", "pilote", "pare-feu", "hôte", "ping ok mais accès refusé",
        "nom du serveur introuvable", "droits insuffisants", "hors connexion", "protection des données",
        "moindre privilège",
        # encadrés
        "objectifs", "procédure professionnelle", "erreur fréquente", "à l'écrit", "repère rapide", "glossaire",
    ):
        assert notion in text, notion


def test_course_flags_requirements_links_and_fictive_supports():
    raw = _course_raw()
    text = _text(raw)
    for req in ("AP-25", "AP-26", "AP-27"):
        assert req in text, req
    assert "Compléments pédagogiques" in text and "fictif" in text.lower()
    assert "aucune n'est une question officielle" in text.lower()
    assert "aucun schéma n'est tiré d'une image générée" in text.lower()
    for link in ("/uaa/ampcr-mc33", "/uaa/ampcr-mc10", "/uaa/ampcr-pratique-pr09", "/uaa/ampcr-pratique-pr10",
                 "/uaa/ampcr-pratique-pr21", "/uaa/ampcr-pratique-pr22", "/uaa/ampcr-pratique-pr24",
                 f"/uaa/{PR23_SLUG}/practice", f"/uaa/{PR23_SLUG}/exam"):
        assert link in raw, link
    assert "/uaa/ampcr-pratique-pr25" not in raw
    anchors = set(re.findall(r'id="(pr23-e\d\d)"', raw))
    assert anchors == {f"pr23-{i.key.lower()}" for i in PRACTICE_ITEMS}
    assert "(#pr23-" not in raw


def test_unc_paths_keep_both_backslashes_once_rendered():
    """Markdown mange une barre oblique inverse sur deux hors du code : aucun chemin UNC du
    cours ne doit s'afficher avec une seule barre."""
    single = re.compile(r"(?<![\\:?A-Za-zÀ-ÿ0-9])\\[A-Za-z0-9.\-]+\\")
    for title, content in pr23_course_sections():
        html = render_markdown(content)
        assert not single.findall(_text(html)), (title, single.findall(_text(html))[:3])
    assert "\\\\SRV-FICH\\Compta" in _text(render_markdown(pr23_course_sections()[1][1]))


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(t) for t, _ in pr23_course_sections()]
    assert kinds[:10] == ["theory"] * 10
    assert kinds[10:] == ["example", "warning", "exercise", "exam", "summary", "info"]


def test_plan_slot_matches_ticket():
    slot = plan.COURSE_SLOTS_BY_CODE["PR23"]
    assert slot.ticket == 223 and slot.title == PR23_TITLE == PRACTICAL_COURSES_BY_CODE["PR23"].title
    assert slot.requirement_ids == ("AP-25", "AP-26", "AP-27")


# =============================================================================================
# 5. Seed, banque, correction
# =============================================================================================


def test_seed_publishes_pr23_in_practical_module_idempotently(db_session):
    module, uaa = _pr23(db_session)
    assert uaa.slug == SLUG and uaa.is_published and uaa.title == PR23_TITLE and uaa.position == 23
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="PR23").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(pr23_course_sections())
    assert {"PR22", "PR23", "PR24"} <= set(plan.published_uaas(db_session))
    ordered = [u.code for u in sorted(module.uaas, key=lambda u: (u.position, u.id))]
    assert ordered.index("PR22") < ordered.index("PR23") < ordered.index("PR24")
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_reserves_and_documents(db_session):
    module, uaa = _pr23(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert import_practical_bank(db_session, module, uaa) == len(PRACTICE_ITEMS) + len(EXAM_ITEMS)
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    usages = [question_usage(q) for q in questions]
    assert usages.count("practice") == len(PRACTICE_ITEMS) and usages.count("exam") == 10


def test_correction_context_is_pr23_specific():
    context = _pedagogical_context_for("PR23")
    assert context is get_practical_context("PR23")
    assert context.course_key == SLUG
    notions = " ".join(context.allowed_notions)
    for notion in ("TCP 445", "\\\\serveur\\partage", "le plus restrictif du partage et de NTFS", "NTFS seul",
                   "un refus explicite l'emporte", "(I) dans icacls", "write list", "réservée",
                   "erreurs 53", "moindre privilège"):
        assert notion in notions, notion
    assert "mot-clé" in context.constraints and "chmod 777" in context.constraints


# =============================================================================================
# 6. Pages et sessions
# =============================================================================================


def test_course_page_renders_figures_and_exercises(client, db_session):
    _pr23(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert set(ids) >= {f"fig-{f.key}" for f in PR23_FIGURES}
    assert html.count('class="jc-exercise-card"') == len(PRACTICE_ITEMS)
    assert "<details open" not in html
    assert 'href="/ampcr-pratique"' in html and f"/uaa/{SLUG}/exam" in html
    assert "<table" in html and 'class="jc-pr-console"' in html
    for _figure, path in STATIC_FIGURES:
        assert client.get(f"/static/{path}").status_code == 200
    for linked in ("ampcr-mc33", "ampcr-mc10", "ampcr-pratique-pr09", "ampcr-pratique-pr22"):
        assert client.get(f"/uaa/{linked}").status_code == 200, linked


def test_practical_home_and_matrix_show_pr23(client, db_session):
    _pr23(db_session)
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and re.search(r"\d+ cours publiés sur 30 prévus", _text(home))  # PR25 (#224) publié ensuite
    for req in REQ:
        assert plan.requirement_status(req, {"PR23"}) == plan.STATUS_PARTIAL
    assert plan.VALIDATED_REQUIREMENT_IDS == frozenset()
    assert client.get("/ampcr-pratique/matrice").status_code == 200


@pytest.mark.parametrize("mode", ["practice", "exam"])
def test_sessions_draw_only_from_their_reserve_without_generation(authenticated_client, db_session, monkeypatch, mode):
    fake = _patch_fake_provider(monkeypatch)
    _pr23(db_session)
    assert authenticated_client.get(f"/uaa/{SLUG}/{mode}").status_code == 200
    session_url = _start_session(authenticated_client, db_session, SLUG, mode)
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert {question_usage(sq.question_version.question) for sq in session.session_questions} == {mode}
    assert session.question_count == 10
    assert fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"PR23"}
    if mode == "exam":
        page = authenticated_client.get(f"{session_url}?q=1").text
        assert "Corrigé de référence" not in page and "Barème" not in page


def test_exam_lengths_limited_and_score_on_20(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _pr23(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    from app.v1.models import User

    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="PR23", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "/ 20" in html


def test_practice_sessions_with_schemas_classification_and_ordering_submit(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr23(db_session)
    for _ in range(2):  # 20 exercices : deux sessions de 10
        session_url = _start_session(authenticated_client, db_session, SLUG, "practice")
        _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
        assert authenticated_client.get(session_url).status_code == 200
