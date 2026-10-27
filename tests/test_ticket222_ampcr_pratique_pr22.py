"""Ticket #222 — AMPCR pratique écrite, PR22 « Domaine, groupe de travail, comptes et groupes ».

Couvre : données de référence et calculs **recontrôlés ici** indépendamment (comptes locaux d'un
groupe de travail, comparaison avec le domaine, formes des noms de connexion, prérequis de la
jonction, imbrication des groupes, droits par les groupes et reconnexion, audit d'une fiche de
comptes, choix du modèle, ordre du dépannage d'une connexion) ; relevés fictifs (format, largeur) ;
schémas SVG (validité, accessibilité, données dessinées, schémas à compléter sans leurs réponses,
fichiers statiques) ; exercices et mini-examen (format du socle, classements et remises en ordre
auto-corrigés, nombres des corrigés) ; cours (matière du ticket, 3 procédures, 5 cas résolus,
liens, supports fictifs, cartes) ; banque, seed, pages et sessions.
Aucun appel IA réel : `FakeAIProvider` partout."""

import re
from html import escape
from pathlib import Path

import pytest

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
from app.v1.ampcr_pratique_pr22_bank import (
    E18_ACCOUNTS,
    E20_ERRORS,
    EXAM_ITEMS,
    EXAM_TOTAL_POINTS,
    KIND_ACCOUNT,
    KIND_DIAG,
    KIND_MODEL,
    KIND_ORDER,
    KIND_SCHEMA,
    KIND_SHEET,
    PRACTICE_ITEMS,
    REQ,
    X02_ACCOUNTS,
    validate_items,
)
from app.v1.ampcr_pratique_pr22_course import CASES, PR22_SLUG, PR22_TITLE, pr22_course_sections
from app.v1.ampcr_pratique_pr22_figures import (
    ACCOUNT_COUNTS,
    ADMINS_DOMAIN,
    BOX_IP,
    CHECK_KEYS,
    D_ACCOUNT,
    D_DNS,
    D_NET,
    D_OK,
    D_RIGHTS,
    D_TIME,
    D_TRUST,
    DC_IP,
    DNS_DOMAIN,
    JOIN_STEPS,
    LIFECYCLE_STEPS,
    LOCAL_NESTING,
    MAX_CLOCK_SKEW_MIN,
    MODEL_DOMAIN,
    MODEL_WG,
    NETBIOS_DOMAIN,
    PR22_FIGURES,
    PROCEDURES,
    SCOPE_DOMAIN,
    SCOPE_LOCAL,
    SCREEN_WIDTH,
    STATIC_FIGURES,
    TROUBLE_STEPS,
    USERS_DOMAIN,
    WG_ACCOUNTS,
    Account,
    AccountRow,
    Organisation,
    Workstation,
    access_of,
    account_errors,
    account_scope,
    all_capture_lines,
    count_accounts,
    first_failure,
    ipconfig_dns_lines,
    join_blockers,
    local_groups_of,
    logon_checks,
    logon_diagnosis,
    logon_forms,
    net_user_lines,
    nslookup_lines,
    recommend_model,
    secure_channel_lines,
    static_svg,
    time_lines,
    whoami_groups_lines,
    workgroup_accounts,
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

SLUG = "ampcr-pratique-pr22"
STATIC_DIR = Path(__file__).resolve().parent.parent / "app" / "static"


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _course_raw() -> str:
    return " ".join(c for _t, c in pr22_course_sections())


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


def _pr22(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "PR22")
    return module, uaa


# =============================================================================================
# 1. Données de référence et calculs, recontrôlés indépendamment
# =============================================================================================


def test_workgroup_accounts_counted_independently():
    # Référence : 4 personnes, Marc sur PC-4 et PC-2, tout le monde ouvre le partage de PC-1.
    assert WG_ACCOUNTS == {
        "PC-1": ("anne", "marc", "paul", "sara"),
        "PC-2": ("marc", "paul"),
        "PC-3": ("sara",),
        "PC-4": ("marc",),
    }
    assert count_accounts(WG_ACCOUNTS) == 8
    assert E18_ACCOUNTS == {"PC-A": ("ines", "lea", "noah"), "PC-B": ("ines", "noah"), "PC-C": ("ines",)}
    assert "emma" not in X02_ACCOUNTS["PC-3"]  # X02 : pas de compte d'Emma sur PC-3
    assert workgroup_accounts({"a": ("P1",)}, None, ()) == {"P1": ("a",)}
    # Organisation type : n postes, partage sur P01 (n comptes), n//4 second poste
    for n, wg, dom in ACCOUNT_COUNTS:
        # chacun sur son poste (n) + les n − 1 autres sur le poste qui partage + n // 4 seconds postes
        assert dom == n and wg == n + (n - 1) + n // 4
    assert [wg for _n, wg, _d in ACCOUNT_COUNTS] == [5, 10, 21, 44]
    assert all(wg > dom for _n, wg, dom in ACCOUNT_COUNTS)


def test_logon_names_and_scope():
    forms = logon_forms("jmartin", computer="PC-03")
    assert forms == {
        "local (ce poste)": ".\\jmartin",
        "local (poste nommé)": "PC-03\\jmartin",
        "domaine (NetBIOS)": "DUPONT\\jmartin",
        "domaine (UPN)": "jmartin@ad.dupont.example",
    }
    for kind, value in forms.items():
        assert account_scope(value) == (SCOPE_DOMAIN if kind.startswith("domaine") else SCOPE_LOCAL)
    assert account_scope("dupont\\x") == SCOPE_DOMAIN and account_scope("x@autre.example") == SCOPE_LOCAL
    with pytest.raises(ValueError):
        account_scope("jmartin")
    assert len(NETBIOS_DOMAIN) <= 15 and DNS_DOMAIN.endswith(".example")


def test_join_prerequisites():
    ok = Workstation("PC-03", "192.168.20.13", (DC_IP,))
    assert join_blockers(ok) == []
    assert join_blockers(Workstation("PC-03", "192.168.20.13", (BOX_IP,))) == ["DNS"]
    assert join_blockers(Workstation("PC-03", "192.168.20.13", (DC_IP, BOX_IP))) == ["DNS"]
    assert join_blockers(Workstation("PC-03", "192.168.20.13", (DC_IP,), edition="Windows 11 Famille")) == ["Édition"]
    assert join_blockers(Workstation("PC-COMPTABILITE-01", "192.168.20.13", (DC_IP,))) == ["Nom du poste"]
    assert join_blockers(ok, existing_names=("pc-03",)) == ["Nom du poste"]
    assert join_blockers(Workstation("PC-03", "192.168.1.13", (DC_IP,))) == ["Réseau"]
    assert join_blockers(Workstation("PC-03", "192.168.20.13", (DC_IP,), clock_offset_min=MAX_CLOCK_SKEW_MIN)) == []
    assert join_blockers(Workstation("PC-03", "192.168.20.13", (DC_IP,), clock_offset_min=-6)) == ["Heure"]
    assert MAX_CLOCK_SKEW_MIN == 5


def test_groups_nesting_and_access_after_reconnection():
    assert dict(LOCAL_NESTING) == {ADMINS_DOMAIN: "Administrateurs", USERS_DOMAIN: "Utilisateurs"}
    assert local_groups_of((USERS_DOMAIN,)) == ("Utilisateurs",)
    julie = Account("jmartin", "Julie", (USERS_DOMAIN, "G_Compta"))
    assert access_of(julie, "Compta") == "Modification" and access_of(julie, "Direction") == "Aucun accès"
    assert access_of(julie, "Commun") == "Modification"
    boss = Account("cdupont", "Claire", (USERS_DOMAIN, "G_Direction"))
    assert access_of(boss, "Compta") == "Lecture" and access_of(boss, "Direction") == "Modification"
    stale = Account("jmartin", "Julie", (USERS_DOMAIN, "G_Compta"), token_groups=(USERS_DOMAIN,))
    assert access_of(stale, "Compta") == "Aucun accès"


def test_account_sheet_audit():
    rows = (
        AccountRow("a", "A", (USERS_DOMAIN,)),
        AccountRow("b", "B", (USERS_DOMAIN,), shared=True),
        AccountRow("c", "C", (USERS_DOMAIN, ADMINS_DOMAIN)),
        AccountRow("adm-c", "C", (ADMINS_DOMAIN,)),
        AccountRow("d", "D", (USERS_DOMAIN,), left=True),
        AccountRow("e", "E", (USERS_DOMAIN,), left=True, enabled=False),
        AccountRow("Invité", "", ()),
    )
    errors = account_errors(rows)
    assert [e.split(" :")[0] for e in errors] == ["b", "c", "d", "Invité"]
    assert len(E20_ERRORS) == 4


def test_model_recommendation():
    assert recommend_model(Organisation("x", 3)) == MODEL_WG
    assert recommend_model(Organisation("x", 10)) == MODEL_WG
    assert recommend_model(Organisation("x", 11)) == MODEL_DOMAIN
    for flag in ("rotation", "policies", "roaming"):
        assert recommend_model(Organisation("x", 4, **{flag: True})) == MODEL_DOMAIN


def test_logon_diagnosis_order():
    assert CHECK_KEYS == ("reseau", "dns", "heure", "approbation", "compte", "droits")
    expected = (D_NET, D_DNS, D_TIME, D_TRUST, D_ACCOUNT, D_RIGHTS)
    for key, diag in zip(CHECK_KEYS, expected, strict=True):
        assert logon_diagnosis(first_failure(key)) == diag
    ws = Workstation("PC-03", "192.168.20.13", (DC_IP,))
    user = Account("j", "J", (USERS_DOMAIN, "G_Compta"))
    assert logon_diagnosis(logon_checks(ws, user, needed_group="G_Compta")) == D_OK
    # plusieurs pannes : la première dans l'ordre l'emporte
    bad = Workstation("PC-03", "192.168.20.13", (BOX_IP,), clock_offset_min=9, secure_channel=False)
    assert logon_diagnosis(logon_checks(bad, Account("j", "J", enabled=False))) == D_DNS
    assert logon_diagnosis(logon_checks(Workstation("PC-03", "192.168.20.13", (DC_IP,), link=False), user)) == D_NET
    assert logon_diagnosis(logon_checks(ws, Account("j", "J", locked=True))) == D_ACCOUNT
    assert logon_diagnosis(logon_checks(ws, Account("j", "J", password_expired=True))) == D_ACCOUNT


def test_procedures_order():
    assert [label for label, _d in JOIN_STEPS][:4] == ["Vérifier les prérequis", "Régler le DNS du poste",
                                                       "Tester le contrôleur", "Joindre le domaine"]
    labels = [label for label, _d in LIFECYCLE_STEPS]
    assert labels.index("Départ : désactiver") < labels.index("Supprimer plus tard")
    trouble = [label for label, _d in TROUBLE_STEPS]
    assert trouble[1:7] == ["Réseau", "DNS", "Heure", "Poste", "Compte", "Droits"]
    assert len(PROCEDURES) == 3


def test_captures_format_and_width():
    ws_box = Workstation("PC-07", "192.168.20.17", (BOX_IP,))
    lines = (
        *all_capture_lines(), *ipconfig_dns_lines(ws_box), *nslookup_lines(BOX_IP, knows_domain=False),
        *nslookup_lines(DC_IP, knows_domain=True), *time_lines(Workstation("P", "192.168.20.2", (DC_IP,), clock_offset_min=9)),
        *secure_channel_lines(True), *secure_channel_lines(False),
        *net_user_lines(Account("pnoel", "Paul Noël", (USERS_DOMAIN, "G_Atelier"), locked=True)),
        *whoami_groups_lines(Account("j", "J", (USERS_DOMAIN, ADMINS_DOMAIN))),
    )
    assert all(len(line) <= SCREEN_WIDTH for line in lines), [line for line in lines if len(line) > SCREEN_WIDTH]
    assert "09:21" in time_lines(Workstation("P", "192.168.20.2", (DC_IP,), clock_offset_min=9))
    assert "Non-existent domain" in " ".join(nslookup_lines(BOX_IP, knows_domain=False))
    assert any("Verrouillé" in line for line in net_user_lines(Account("x", "X", locked=True)))
    assert "BUILTIN\\Administrateurs" in whoami_groups_lines(Account("j", "J", (USERS_DOMAIN, ADMINS_DOMAIN)))


# =============================================================================================
# 2. Schémas
# =============================================================================================


def test_figures_valid_accessible_and_unique():
    all_figures = PR22_FIGURES + tuple(f for f, _p in STATIC_FIGURES)
    keys = [f.key for f in all_figures]
    assert len(keys) == len(set(keys)) == 15 and len(PR22_FIGURES) >= 4  # ticket : ≥ 4 schémas
    for figure in all_figures:
        assert validate_figure(figure) == [], figure.key
        html = str(render_figure(figure))
        assert 'role="img"' in html and "(schéma non officiel)" in html and not figure.official


def test_figures_drawn_from_data():
    by_key = {f.key: f for f in PR22_FIGURES}
    wg = by_key["pr22-groupe-de-travail"].svg
    for pc, names in WG_ACCOUNTS.items():
        assert f'data-node="{pc}"' in wg and all(f"• {n}" in wg for n in names)
    bars = by_key["pr22-comptes-a-gerer"].svg
    for n, wg_count, dom in ACCOUNT_COUNTS:
        assert f'data-bar="{n}-groupe de travail" data-value="{wg_count}"' in bars
        assert f'data-bar="{n}-domaine" data-value="{dom}"' in bars
    domain = by_key["pr22-domaine"].svg
    assert f"IP fixe {DC_IP}/24" in domain and domain.count(f"DNS {DC_IP}") == 3 and domain.count(f"passerelle {BOX_IP}") == 3
    names = by_key["pr22-noms-du-domaine"].svg
    assert escape("DUPONT\\jmartin") in names and "jmartin@ad.dupont.example" in names
    groups = by_key["pr22-groupes"].svg
    assert "groupe local Administrateurs" in groups and "groupe local Utilisateurs" in groups
    for key, (_title, steps) in zip(("pr22-procedure-jonction", "pr22-procedure-compte", "pr22-procedure-depannage"),
                                    PROCEDURES, strict=True):
        for index, (label, _d) in enumerate(steps, start=1):
            assert f"{index}. {escape(label)}" in by_key[key].svg, (key, label)


def test_schemas_to_complete_hide_their_answers():
    by_key = {f.key: f.svg for f, _p in STATIC_FIGURES}
    domain = by_key["pr22-domaine-a-completer"]
    assert "contrôleur de domaine + DNS" not in domain and f"IP fixe {DC_IP}" not in domain
    assert all(f"{n} ?" in domain for n in "①②③④") and 'data-node="PC-03"' not in domain
    names = by_key["pr22-noms-a-completer"]
    assert ">DUPONT<" not in names and "pc-03.ad.dupont.example" not in names and "jmartin@" not in names
    wg = by_key["pr22-groupe-de-travail-a-completer"]
    assert "• anne" not in wg and "• paul" not in wg and "• sara" in wg
    groups = by_key["pr22-groupes-a-completer"]
    assert "G_Compta" not in groups and "groupe local Administrateurs" not in groups and "Compta : Lecture" not in groups


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
    assert len(PRACTICE_ITEMS) >= 16 and len(EXAM_ITEMS) == 10  # ticket : ≥ 16 exercices, mini-examen /20
    assert sum(i.total_points for i in EXAM_ITEMS) == EXAM_TOTAL_POINTS == 20
    kinds = [i.kind for i in PRACTICE_ITEMS]
    assert kinds.count(KIND_SCHEMA) == 4 and kinds.count(KIND_SHEET) >= 3
    for kind in (KIND_ORDER, KIND_MODEL, KIND_ACCOUNT, KIND_DIAG):
        assert kind in kinds
    schema_images = {d.image for i in PRACTICE_ITEMS for d in i.documents if d.image}
    assert schema_images == {p for _f, p in STATIC_FIGURES}
    assert sum(1 for i in PRACTICE_ITEMS if any(d.kind == "console" for d in i.documents)) >= 5
    keys = [i.key for i in PRACTICE_ITEMS + EXAM_ITEMS]
    assert len(keys) == len(set(keys))
    covered = {r for i in PRACTICE_ITEMS + EXAM_ITEMS for r in i.requirement_ids}
    assert covered == REQ == set(plan.COURSE_SLOTS_BY_CODE["PR22"].requirement_ids)
    types = [i.question_type for i in PRACTICE_ITEMS]
    assert types.count("ordering") == 3 and types.count("classification") == 4


def test_auto_corrected_answers():
    def ordered(key: str) -> list[str]:
        item = _item(key)
        return [item.ordering.steps[i].split(" — ")[0] for i in item.ordering.correct]

    assert ordered("E01") == [label for label, _d in JOIN_STEPS]
    assert ordered("E02") == [label for label, _d in LIFECYCLE_STEPS]
    assert ordered("E03") == [label for label, _d in TROUBLE_STEPS]

    def find(key: str, needle: str) -> str:
        c = _item(key).classification
        index = next(i for i, e in enumerate(c.elements) if needle in e)
        return c.categories[c.correct[index]]

    assert find("E04", "14 postes") == MODEL_DOMAIN and find("E04", "Garage") == MODEL_WG
    assert find("E04", "intérim") == MODEL_DOMAIN and find("E04", "Association") == MODEL_WG
    assert find("E04", "verrouillage") == MODEL_DOMAIN
    assert find("E05", ".\\support") == SCOPE_LOCAL and find("E05", "jmartin@") == SCOPE_DOMAIN
    assert find("E05", "PC-ACCUEIL") == SCOPE_LOCAL and find("E05", "DUPONT\\adm") == SCOPE_DOMAIN
    assert find("E06", "câble") == D_NET and find("E06", "box") == D_DNS and find("E06", "9 minutes") == D_TIME
    assert find("E06", "approbation") == D_TRUST and find("E06", "désactivé") == D_ACCOUNT
    assert find("E06", "G_Compta") == D_RIGHTS and find("E06", "verrouillé") == D_ACCOUNT
    assert find("E07", "quitte").startswith("Désactiver") and find("E07", "oublié").startswith("Réinitialiser")
    assert find("E07", "cinq essais").startswith("Déverrouiller") and find("E07", "directeur").startswith("Ajouter")
    for item in PRACTICE_ITEMS:
        if item.ordering is not None:
            assert list(item.ordering.correct) != list(range(len(item.ordering.steps))), item.key
        if item.classification is not None:
            correct = list(item.classification.correct)
            # ticket #150 : la première catégorie n'est jamais la réponse de tous les premiers éléments
            assert correct[: len(item.classification.categories)] != list(range(len(item.classification.categories))), item.key
            assert len(set(correct)) == len(item.classification.categories), item.key


def test_numbers_in_corrections_match_calculations():
    def text(key: str) -> str:
        item = _item(key)
        return " ".join((*item.correction, *(c.expected for c in item.criteria)))

    assert "8 comptes" in text("E10") and "4 comptes" in text("E10")
    assert "6 comptes" in text("E18") and "PC-A : ines, lea, noah" in text("E18")
    assert "4 erreurs" in text("E20") and "mvincent" in text("E20") and "Invité" in text("E20")
    assert DC_IP in text("E12") and BOX_IP in text("E12") and "Non-existent domain" in text("E12")
    assert "9 minutes" in text("E13") and "12 minutes" in text("X04")
    assert "Test-ComputerSecureChannel" in text("E14") and "Verrouillé" in text("E15")
    assert "Aucun accès" in text("E16") and "modification" in text("E16")
    assert DNS_DOMAIN in text("E19") and ".local" in text("E19")
    assert "Domaine Active Directory" in text("X01") and "désactive" in text("X06")


def test_schema_documents_point_to_static_files():
    item = _item("E08")
    layout = _document_layout(item.documents[0])
    assert layout["kind"] == "figure" and layout["src"] == "/static/img/ampcr-pratique/pr22-domaine-a-completer.svg"
    assert "DC01" in layout["alt"] and "non officiel" in layout["notice"]


def test_no_false_technical_claims_anywhere():
    text = _course_text() + " " + _all_items_text().lower()
    for right in ("groupe de travail", "comptes locaux", "active directory", "contrôleur de domaine", "dns",
                  "kerberos", "5 minutes", "compte d'ordinateur", "netbios", "admins du domaine",
                  "utilisateurs du domaine", "stratégie", "moindre privilège", "désactiv", "verrouill",
                  "relation d'approbation", "whoami /groups", "famille"):
        assert right in text, right
    for wrong in ("dns = box", "supprimer le compte immédiatement est préférable", "le nom du groupe de travail donne les droits d'accès",
                  "windows famille peut rejoindre", "désactiver l'uac", "tout le monde administrateur est"):
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
    for figure in PR22_FIGURES:
        assert f'id="fig-{figure.key}"' in course, figure.key


def test_course_teaches_every_mandatory_point():
    titles = [t for t, _ in pr22_course_sections()]
    assert len(titles) == len(set(titles))
    text = _course_text()
    for notion in (
        # matière du ticket, dans l'ordre du cahier des charges
        "groupe de travail", "comptes locaux", "décentralisée", "domaine windows", "active directory",
        "centralisée", "contrôleur de domaine", "dns", "authentification", "comptes d'utilisateurs",
        "compte d'ordinateur", "joindre", "groupes", "stratégies de groupe", "domaine dns",
        "domaine d'administration", "compte local", "compte du domaine", "administrateur", "utilisateur standard",
        "mot de passe", "moindre privilège", "désactive", "réseau", "heure", "droits", "3 à 20 postes",
        # encadrés
        "objectifs", "procédure professionnelle", "erreur fréquente", "à l'écrit", "repère rapide", "glossaire",
    ):
        assert notion in text, notion


def test_course_flags_requirements_links_and_fictive_supports():
    raw = _course_raw()
    text = _text(raw)
    assert "AP-24" in text
    assert "Compléments pédagogiques" in text and "fictif" in text.lower()
    assert "aucune n'est une question officielle" in text.lower()
    assert "aucun schéma n'est tiré d'une image générée" in text.lower()
    for link in ("/uaa/ampcr-mc33", "/uaa/ampcr-mc10", "/uaa/ampcr-pratique-pr10", "/uaa/ampcr-pratique-pr20",
                 "/uaa/ampcr-pratique-pr21", "/uaa/ampcr-pratique-pr24", f"/uaa/{PR22_SLUG}/practice",
                 f"/uaa/{PR22_SLUG}/exam"):
        assert link in raw, link
    for unpublished in ("/uaa/ampcr-pratique-pr23", "/uaa/ampcr-pratique-pr25"):
        assert unpublished not in raw, unpublished
    anchors = set(re.findall(r'id="(pr22-e\d\d)"', raw))
    assert anchors == {f"pr22-{i.key.lower()}" for i in PRACTICE_ITEMS}
    assert "(#pr22-" not in raw


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(t) for t, _ in pr22_course_sections()]
    assert kinds[:10] == ["theory"] * 10
    assert kinds[10:] == ["example", "warning", "exercise", "exam", "summary", "info"]


def test_plan_slot_matches_ticket():
    slot = plan.COURSE_SLOTS_BY_CODE["PR22"]
    assert slot.ticket == 222 and slot.title == PR22_TITLE == PRACTICAL_COURSES_BY_CODE["PR22"].title
    assert slot.requirement_ids == ("AP-24",)


# =============================================================================================
# 5. Seed, banque, correction
# =============================================================================================


def test_seed_publishes_pr22_in_practical_module_idempotently(db_session):
    module, uaa = _pr22(db_session)
    assert uaa.slug == SLUG and uaa.is_published and uaa.title == PR22_TITLE and uaa.position == 22
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="PR22").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(pr22_course_sections())
    assert {"PR21", "PR22", "PR24"} <= set(plan.published_uaas(db_session))
    ordered = [u.code for u in sorted(module.uaas, key=lambda u: (u.position, u.id))]
    assert ordered.index("PR21") < ordered.index("PR22") < ordered.index("PR24")
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_reserves_and_documents(db_session):
    module, uaa = _pr22(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert import_practical_bank(db_session, module, uaa) == len(PRACTICE_ITEMS) + len(EXAM_ITEMS)
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    usages = [question_usage(q) for q in questions]
    assert usages.count("practice") == len(PRACTICE_ITEMS) and usages.count("exam") == 10


def test_correction_context_is_pr22_specific():
    context = _pedagogical_context_for("PR22")
    assert context is get_practical_context("PR22")
    assert context.course_key == SLUG
    notions = " ".join(context.allowed_notions)
    for notion in ("gestion décentralisée", "contrôleur", "5 minutes", "DUPONT\\nom", "Famille",
                   "Admins du domaine devient membre du groupe local Administrateurs", "prochaine ouverture de session",
                   "désactiver le jour même", "relation d'approbation"):
        assert notion in notions, notion
    assert "mot-clé" in context.constraints and "compte commun" in context.constraints


# =============================================================================================
# 6. Pages et sessions
# =============================================================================================


def test_course_page_renders_figures_and_exercises(client, db_session):
    _pr22(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert set(ids) >= {f"fig-{f.key}" for f in PR22_FIGURES}
    assert html.count('class="jc-exercise-card"') == len(PRACTICE_ITEMS)
    assert "<details open" not in html
    assert 'href="/ampcr-pratique"' in html and f"/uaa/{SLUG}/exam" in html
    assert "<table" in html and 'class="jc-pr-console"' in html
    for _figure, path in STATIC_FIGURES:
        assert client.get(f"/static/{path}").status_code == 200
    for theory in ("ampcr-mc33", "ampcr-mc10"):
        assert client.get(f"/uaa/{theory}").status_code == 200, theory


def test_practical_home_and_matrix_show_pr22(client, db_session):
    _pr22(db_session)
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and re.search(r"\d+ cours publiés sur 30 prévus", _text(home))  # PR23 (#223) publié ensuite
    for req in REQ:
        assert plan.requirement_status(req, {"PR22"}) == plan.STATUS_PARTIAL
    assert plan.VALIDATED_REQUIREMENT_IDS == frozenset()
    assert client.get("/ampcr-pratique/matrice").status_code == 200


@pytest.mark.parametrize("mode", ["practice", "exam"])
def test_sessions_draw_only_from_their_reserve_without_generation(authenticated_client, db_session, monkeypatch, mode):
    fake = _patch_fake_provider(monkeypatch)
    _pr22(db_session)
    assert authenticated_client.get(f"/uaa/{SLUG}/{mode}").status_code == 200
    session_url = _start_session(authenticated_client, db_session, SLUG, mode)
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert {question_usage(sq.question_version.question) for sq in session.session_questions} == {mode}
    assert session.question_count == 10
    assert fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"PR22"}
    if mode == "exam":
        page = authenticated_client.get(f"{session_url}?q=1").text
        assert "Corrigé de référence" not in page and "Barème" not in page


def test_exam_lengths_limited_and_score_on_20(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _pr22(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    from app.v1.models import User

    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="PR22", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "/ 20" in html


def test_practice_sessions_with_schemas_classification_and_ordering_submit(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr22(db_session)
    for _ in range(2):  # 20 exercices : deux sessions de 10
        session_url = _start_session(authenticated_client, db_session, SLUG, "practice")
        _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
        assert authenticated_client.get(session_url).status_code == 200
