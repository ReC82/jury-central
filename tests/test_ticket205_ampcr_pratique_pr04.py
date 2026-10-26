"""Ticket #205 — AMPCR pratique écrite, PR04 « Reconditionnement, entretien et contrôles après
intervention ».

Couvre : données de référence **recontrôlées ici** indépendamment (cinq procédures, quatre
opérations, décision sur les données, techniques d'effacement par support, verdicts SMART,
batterie et températures, tri des déchets) ; schémas SVG (validité, accessibilité, repères et
étapes cohérents avec les données) ; exercices et mini-examen (format du socle, remises en ordre
et classements auto-corrigés, décisions de protection des données, pas de question d'acronyme,
contexte complet) ; cours (matière du ticket, 5 procédures, 4 cas résolus, affirmations
techniques justes, supports fictifs, cartes) ; banque, seed, pages et sessions. Aucun appel IA
réel : `FakeAIProvider` partout."""

import re
from html import escape

import pytest

from app.models import UAA, Module
from app.seed import seed
from app.v1 import ampcr_pratique_plan as plan
from app.v1.ampcr_pratique_bank import (
    PRACTICAL_BANK_IMPORTERS,
    PRACTICAL_COURSES_BY_CODE,
    get_practical_context,
    import_practical_bank,
    item_content,
    question_usage,
)
from app.v1.ampcr_pratique_pr04_bank import (
    E04_CATEGORIES,
    E05_CATEGORIES,
    E06_CATEGORIES,
    E06_MEDIA,
    E07_HDD_VERDICT,
    E07_NVME_VERDICT,
    E08_VERDICTS,
    E09_CATEGORIES,
    E15_HEALTH,
    E15_VERDICT,
    EXAM_ITEMS,
    EXAM_TOTAL_POINTS,
    KIND_DATA,
    KIND_ERROR,
    KIND_FORM,
    KIND_ORDER,
    KIND_TESTS,
    PRACTICE_ITEMS,
    REQ,
    validate_items,
)
from app.v1.ampcr_pratique_pr04_course import PR04_SLUG, PR04_TITLE, pr04_course_sections
from app.v1.ampcr_pratique_pr04_figures import (
    AFTER_TESTS_STEPS,
    CASE2_SCREEN,
    CASE2_SMART,
    CASE3_DESIGN,
    CASE3_FULL,
    CASE3_SCREEN,
    CASE4_AFTER,
    CASE4_BEFORE,
    CASE4_LIMIT,
    CLEAN_STEPS,
    CLEANING_FIGURE,
    CLEANING_POINTS,
    DATA_TREE,
    DECISION_BACKUP_FIRST,
    DECISION_ERASE,
    DECISION_ERASE_OR_DESTROY,
    DECISION_KEEP,
    DECISION_NO_CONSENT,
    DEST_NEW_USER,
    DEST_RECYCLING,
    DEST_SAME_CLIENT,
    ERASE_BY_MEDIA,
    ERASE_STEPS,
    FIRMWARE_STEPS,
    MEDIA_HDD,
    MEDIA_NVME_SSD,
    MEDIA_SATA_SSD,
    OP_ERASE,
    OP_RECON,
    OP_REPAIR,
    OP_RESET,
    OPERATIONS,
    PR04_FIGURES,
    PROCEDURES,
    RECON_STEPS,
    SCREEN_WIDTH,
    SMART_OK,
    SMART_REPLACE,
    SMART_WATCH,
    WASTE_BATTERY,
    WASTE_DEEE,
    WASTE_ITEMS,
    battery_health_percent,
    battery_verdict,
    data_decision,
    erase_method_ok,
    smart_verdict,
    temperature_verdict,
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

SLUG = "ampcr-pratique-pr04"


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _course_raw() -> str:
    return " ".join(c for _t, c in pr04_course_sections())


def _course_text() -> str:
    return _text(_course_raw()).replace("**", "").lower()


def _all_items_text() -> str:
    return " ".join(
        " ".join((i.title, i.context, *i.instructions, *i.correction, *(c.expected for c in i.criteria),
                  *(d.content_text for d in i.documents)))
        for i in PRACTICE_ITEMS + EXAM_ITEMS
    )


def _pr04(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "PR04")
    return module, uaa


# =============================================================================================
# 1. Données de référence, recontrôlées indépendamment
# =============================================================================================


def test_data_decision_requires_owner_consent_and_verified_backup():
    # Sans accord écrit du propriétaire : jamais d'effacement, quelle que soit la destination.
    for dest in (DEST_SAME_CLIENT, DEST_NEW_USER, DEST_RECYCLING):
        for wants in (True, False):
            assert data_decision(owner_consent=False, wants_data=wants, backup_verified=True,
                                 destination=dest) == DECISION_NO_CONSENT
    # Le propriétaire veut ses données, aucune copie vérifiée : sauvegarde d'abord.
    for dest in (DEST_SAME_CLIENT, DEST_NEW_USER, DEST_RECYCLING):
        assert data_decision(owner_consent=True, wants_data=True, backup_verified=False,
                             destination=dest) == DECISION_BACKUP_FIRST
    assert data_decision(owner_consent=True, wants_data=True, backup_verified=True,
                         destination=DEST_SAME_CLIENT) == DECISION_KEEP
    assert data_decision(owner_consent=True, wants_data=False, backup_verified=False,
                         destination=DEST_NEW_USER) == DECISION_ERASE
    assert data_decision(owner_consent=True, wants_data=False, backup_verified=False,
                         destination=DEST_RECYCLING) == DECISION_ERASE_OR_DESTROY
    with pytest.raises(ValueError):
        data_decision(owner_consent=True, wants_data=False, backup_verified=True, destination="poubelle")
    assert len(DATA_TREE) == 3 and "accord écrit" in DATA_TREE[0][0]


def test_erase_techniques_match_the_media():
    assert set(ERASE_BY_MEDIA) == {MEDIA_HDD, MEDIA_SATA_SSD, MEDIA_NVME_SSD} == set(E06_MEDIA)
    for media in ERASE_BY_MEDIA:
        assert not erase_method_ok(media, "formatage rapide")
        assert not erase_method_ok(media, "suppression des fichiers et corbeille vidée")
        ok, ko, _why = ERASE_BY_MEDIA[media]
        assert not set(ok) & set(ko) and any("destruction physique" in t for t in ok)
    for ssd in (MEDIA_SATA_SSD, MEDIA_NVME_SSD):
        assert not erase_method_ok(ssd, "passes d'écrasement multiples avec un logiciel de PC")
        assert not erase_method_ok(ssd, "défragmentation")
        assert erase_method_ok(ssd, "effacement cryptographique si le SSD est chiffré (clé détruite)")
        assert any("Sanitize" in t for t in ERASE_BY_MEDIA[ssd][0])
    assert erase_method_ok(MEDIA_HDD, "écrasement complet du disque (une passe suffit sur un disque récent)")
    assert not erase_method_ok(MEDIA_HDD, "suppression des partitions")
    with pytest.raises(ValueError):
        erase_method_ok(MEDIA_HDD, "aimant de frigo")


def test_smart_battery_and_temperature_rules():
    assert smart_verdict(dict(CASE2_SMART)) == SMART_REPLACE  # « PASSED » mais secteurs en attente
    assert smart_verdict({"Reallocated_Sector_Ct": 3}) == SMART_WATCH
    assert smart_verdict({"Reallocated_Sector_Ct": 0, "Current_Pending_Sector": 0}) == SMART_OK
    assert smart_verdict({"Offline_Uncorrectable": 1}) == SMART_REPLACE
    assert smart_verdict({"Percentage_Used": 104, "Available_Spare": 100, "Available_Spare_Threshold": 10}) == SMART_REPLACE
    assert smart_verdict({"Percentage_Used": 85, "Available_Spare": 100}) == SMART_WATCH
    assert smart_verdict({"Percentage_Used": 10, "Available_Spare": 5, "Available_Spare_Threshold": 10}) == SMART_REPLACE
    assert smart_verdict({"Percentage_Used": 10, "Media_Errors": 2}) == SMART_REPLACE
    assert E07_HDD_VERDICT == SMART_OK and E07_NVME_VERDICT == SMART_REPLACE
    assert "PASSED" in " ".join(CASE2_SCREEN)
    # Batterie : 38 080 / 56 000 = 68 % ; 43 500 / 50 000 = 87 %.
    assert battery_health_percent(CASE3_DESIGN, CASE3_FULL) == 68 and battery_verdict(CASE3_DESIGN, CASE3_FULL) == "à remplacer"
    assert E15_HEALTH == 87 and E15_VERDICT == "bonne"
    assert battery_verdict(100, 80) == "bonne" and battery_verdict(100, 79) == "à remplacer"
    with pytest.raises(ValueError):
        battery_health_percent(0, 10)
    # Températures (seuil de PR03) : avant nettoyage à surveiller, après normal.
    assert temperature_verdict(CASE4_BEFORE[-1][1], CASE4_LIMIT) == "à surveiller"
    assert all(temperature_verdict(t, CASE4_LIMIT) == "normal" for _m, t in CASE4_AFTER)
    assert E08_VERDICTS == ("normal", "à surveiller", "normal", "normal")
    assert max(len(line) for line in CASE2_SCREEN + CASE3_SCREEN) <= SCREEN_WIDTH


def test_operations_procedures_and_waste():
    assert [op.name for op in OPERATIONS] == [OP_REPAIR, OP_RECON, OP_RESET, OP_ERASE]
    reset = next(op for op in OPERATIONS if op.name == OP_RESET)
    assert "pas forcément illisibles" in reset.data
    erase = next(op for op in OPERATIONS if op.name == OP_ERASE)
    assert "accord écrit" in erase.data and "Certificat" in erase.proof
    assert len(PROCEDURES) == 5
    labels = [label for label, _d in RECON_STEPS]
    assert labels.index("Réceptionner") < labels.index("Autoriser") < labels.index("Diagnostiquer")
    assert labels.index("Diagnostiquer") < labels.index("Protéger les données") < labels.index("Nettoyer")
    assert labels.index("Tester") < labels.index("Remettre") == len(labels) - 1
    assert "débranché" in CLEAN_STEPS[0][1] and "pales" in CLEAN_STEPS[3][1] and "impulsions" in CLEAN_STEPS[4][1]
    assert "BitLocker suspendu" in FIRMWARE_STEPS[3][1] and "jamais couper" in FIRMWARE_STEPS[4][1]
    assert ERASE_STEPS[0][0] == "Accord écrit" and "formatage rapide n'efface rien" in ERASE_STEPS[3][1]
    assert "30 minutes" in AFTER_TESTS_STEPS[-1][1]
    streams = dict(WASTE_ITEMS)
    assert streams["Pile bouton CR2032 remplacée"] == streams["Batterie de portable gonflée"] == WASTE_BATTERY
    assert streams["Carte mère hors d'usage"] == streams["Disque dur effacé puis déclassé"] == WASTE_DEEE
    assert [p.number for p in CLEANING_POINTS] == list(range(1, len(CLEANING_POINTS) + 1))


# =============================================================================================
# 2. Schémas
# =============================================================================================


def test_figures_valid_accessible_and_unique():
    keys = [f.key for f in PR04_FIGURES]
    assert len(keys) == len(set(keys)) == 9
    for figure in PR04_FIGURES:
        assert validate_figure(figure) == [], figure.key
        html = str(render_figure(figure))
        assert 'role="img"' in html and "(schéma non officiel)" in html and not figure.official


def test_figures_drawn_from_data():
    points = re.findall(r'data-point="(\d+)" data-zone="([^"]+)"', CLEANING_FIGURE.svg)
    assert [(int(n), z) for n, z in points] == [(p.number, escape(p.zone)) for p in CLEANING_POINTS]
    by_key = {f.key: f for f in PR04_FIGURES}
    for key, steps in (("pr04-reconditionner", RECON_STEPS), ("pr04-nettoyer", CLEAN_STEPS),
                       ("pr04-firmware", FIRMWARE_STEPS), ("pr04-effacement", ERASE_STEPS),
                       ("pr04-controles", AFTER_TESTS_STEPS)):
        svg = by_key[key].svg
        for index, (label, _detail) in enumerate(steps, start=1):
            assert f"{index}. {escape(label)}" in svg, (key, label)
    assert by_key["pr04-decision-donnees"].svg.count("data-step=") == len(DATA_TREE) == 3
    chart = by_key["pr04-temperatures-nettoyage"].svg
    assert re.findall(r'data-x="(\d+)" data-y="(\d+)"', chart) == [(str(m), str(t)) for m, t in CASE4_AFTER]


# =============================================================================================
# 3. Exercices et mini-examen
# =============================================================================================


def test_items_valid_and_counts_match_ticket():
    assert validate_items() == []
    assert len(PRACTICE_ITEMS) >= 15 and len(EXAM_ITEMS) == 10
    assert sum(i.total_points for i in EXAM_ITEMS) == EXAM_TOTAL_POINTS == 20
    kinds = [i.kind for i in PRACTICE_ITEMS]
    for kind, minimum in ((KIND_ORDER, 3), (KIND_DATA, 4), (KIND_TESTS, 3), (KIND_FORM, 3), (KIND_ERROR, 1)):
        assert kinds.count(kind) >= minimum, kind
    keys = [i.key for i in PRACTICE_ITEMS + EXAM_ITEMS]
    assert len(keys) == len(set(keys))
    covered = {r for i in PRACTICE_ITEMS + EXAM_ITEMS for r in i.requirement_ids}
    assert REQ <= covered and "AP-C03" in covered
    assert set(plan.COURSE_SLOTS_BY_CODE["PR04"].requirement_ids) == REQ | {"AP-C03"}
    # Le ticket demande des décisions de protection des données dans les exercices.
    assert sum(1 for i in PRACTICE_ITEMS if i.kind == KIND_DATA) >= 4


def test_auto_corrected_answers():
    by_key = {i.key: i for i in PRACTICE_ITEMS}

    def ordered(key: str) -> list[str]:
        o = by_key[key].ordering
        return [o.steps[i].split(" — ")[0] for i in o.correct]

    assert ordered("E01") == [label for label, _d in RECON_STEPS]
    assert ordered("E02") == [label for label, _d in CLEAN_STEPS]
    assert ordered("E03") == [label for label, _d in FIRMWARE_STEPS]

    def answers(key: str, categories: tuple[str, ...]) -> dict[str, str]:
        c = by_key[key].classification
        return dict(zip(c.elements, (categories[i] for i in c.correct), strict=True))

    e04 = answers("E04", E04_CATEGORIES)
    assert e04["« Réinitialiser ce PC » à la demande du client qui garde l'ordinateur"] == OP_RESET
    assert all(v == OP_REPAIR for k, v in e04.items() if "ventilateur" in k or "écran fêlé" in k)
    assert sum(v == OP_ERASE for v in e04.values()) == 2 and sum(v == OP_RECON for v in e04.values()) == 2
    e05 = answers("E05", E05_CATEGORIES)
    assert e05["Le fils d'un client téléphone : « effacez tout sur le PC de mon père, il est d'accord »"].startswith("Ne rien effacer")
    assert next(v for k, v in e05.items() if "sûrement d'accord" in k).startswith("Ne rien effacer")
    assert next(v for k, v in e05.items() if "aucune sauvegarde" in k).startswith("Sauvegarder")
    assert next(v for k, v in e05.items() if "association" in k) == "Effacement sécurisé autorisé"
    e06 = answers("E06", E06_CATEGORIES)
    for element, verdict in e06.items():
        weak = any(w in element for w in ("formatage rapide", "sept passes", "défragmentation", "partitions"))
        assert (verdict == "Technique insuffisante") is weak, element
    e09 = answers("E09", E09_CATEGORIES)
    assert e09 == dict(WASTE_ITEMS)
    for item in PRACTICE_ITEMS:  # aucune remise en ordre déjà dans l'ordre attendu
        if item.ordering:
            assert list(item.ordering.correct) != list(range(len(item.ordering.steps))), item.key


def test_no_false_technical_claims_anywhere():
    text = _course_text() + " " + _all_items_text().lower()
    for right in ("une remise à zéro n'est pas un effacement sécurisé", "pas d'accord écrit, pas d'effacement",
                  "un formatage rapide n'efface rien", "la défragmentation n'efface rien", "une passe suffit",
                  "un bloc d'alimentation ne s'ouvre jamais", "pas d'aspirateur", "bitlocker",
                  "ne suffit jamais", "certificat", "poubelle barrée", "bebat", "recupel"):
        assert right in text, right
    for wrong in ("le formatage rapide efface", "sept passes sont nécessaires", "défragmenter pour effacer",
                  "passer l'aspirateur sur la carte pour", "ouvrir le bloc pour", "percer la batterie pour la",
                  "passed, le disque est sain", "sur simple appel, effacer"):
        assert wrong not in text, wrong


def test_no_acronym_question_and_full_context():
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        text = " ".join((item.title, item.context, *item.instructions))
        assert not re.search(r"que signifie|que veut dire|développe[rz]? l'acronyme", text, re.IGNORECASE), item.key
        assert len(item.context) >= 150, item.key
        assert "officiel" not in item.title.lower(), item.key


def test_items_content_matches_existing_question_types():
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        content = item_content(item, [1, 2][: len(item.documents)])
        validate_content(item.question_type, 1, content)


# =============================================================================================
# 4. Cours
# =============================================================================================


def test_four_resolved_cases_five_procedures_and_exam_not_in_course():
    text = _text(_course_raw())
    for case in ("Cas 1 — Reconditionner un lot de PC", "Cas 2 — Un disque « PASSED » à remplacer",
                 "Cas 3 — La batterie d'un portable de prêt", "Cas 4 — Portable qui chauffe"):
        assert case in text, case
    for i in range(1, 6):
        assert f"Procédure {i} —" in text, i
    course = _course_raw()
    for item in EXAM_ITEMS:
        assert item.context not in course and escape(item.context) not in course, item.key
    for item in PRACTICE_ITEMS:
        assert escape(item.context) in course, item.key


def test_course_teaches_every_mandatory_point():
    titles = [t for t, _ in pr04_course_sections()]
    assert len(titles) == len(set(titles))
    text = _course_text()
    for notion in (
        # distinctions
        "réparation", "reconditionnement", "remise à zéro", "effacement sécurisé",
        # réception et diagnostic
        "état initial", "inventaire", "numéro de série", "accessoires", "photos", "fiche de réception",
        "diagnostic", "avant toute intervention",
        # données
        "consentement", "accord écrit", "sauvegarde vérifiée", "confidentialité", "refus", "hdd", "ssd",
        "écrasement complet", "sanitize", "effacement cryptographique", "nist sp 800-88", "destruction",
        # nettoyage et refroidissement
        "nettoyage non destructif", "poussière", "air sec", "pales", "pinceau antistatique",
        "alcool isopropylique", "pâte thermique", "refroidissement", "baisse sa fréquence",
        # pièces et mises à jour
        "remplacement", "compatibilité", "cr2032", "so-dimm", "firmware", "notes de version", "bitlocker",
        "pilotes", "windows update",
        # tests
        "memtest86", "smart", "températures", "ports", "stabilité", "powercfg /batteryreport",
        # remise, déchets, rapport
        "check-list", "remise", "deee", "2012/19/ue", "batterie gonflée", "rapport", "traçabilité",
        "étiquette", "formulaire", "vue annotée",
        # encadrés
        "objectifs", "procédure professionnelle", "erreur fréquente", "à l'écrit", "repère rapide", "glossaire",
    ):
        assert notion in text, notion
    assert "aucune manipulation ne se fait sous tension" in text and "un bloc d'alimentation ne s'ouvre jamais" in text


def test_course_flags_requirements_links_and_fictive_supports():
    raw = _course_raw()
    text = _text(raw)
    for req in ("AP-14", "AP-C03"):
        assert req in text
    assert "Compléments pédagogiques" in text and "fictif" in text.lower()
    assert "aucun n'est une question officielle" in text.lower()
    assert "aucun schéma n'est tiré d'une image générée" in text.lower()
    assert "conventions du cours" in text.lower()  # seuils signalés comme non normatifs
    for link in ("/uaa/ampcr-mc06", "/uaa/ampcr-mc32", "/uaa/ampcr-pratique-pr02", "/uaa/ampcr-pratique-pr03",
                 "/uaa/ampcr-pratique-pr06", f"/uaa/{PR04_SLUG}/practice", f"/uaa/{PR04_SLUG}/exam"):
        assert link in raw, link
    assert "/uaa/ampcr-pratique-pr05" not in raw  # PR05 pas encore publié : renvoi en texte seulement
    anchors = set(re.findall(r'id="(pr04-e\d\d)"', raw))
    assert anchors == {f"pr04-{i.key.lower()}" for i in PRACTICE_ITEMS}
    assert "(#pr04-" not in raw


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(t) for t, _ in pr04_course_sections()]
    assert kinds[:14] == ["theory"] * 14
    assert kinds[14:] == ["example", "warning", "exercise", "exam", "summary", "info"]


# =============================================================================================
# 5. Banque, seed et intégration au moteur
# =============================================================================================


def test_plan_slot_matches_ticket():
    slot = plan.COURSE_SLOTS_BY_CODE["PR04"]
    assert slot.ticket == 205 and slot.title == PR04_TITLE == PRACTICAL_COURSES_BY_CODE["PR04"].title


def test_seed_publishes_pr04_in_practical_module_idempotently(db_session):
    module, uaa = _pr04(db_session)
    assert uaa.slug == SLUG and uaa.is_published and uaa.title == PR04_TITLE and uaa.position == 4
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="PR04").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(pr04_course_sections())
    assert {"PR01", "PR02", "PR03", "PR04", "PR06", "PR11", "PR15", "PR16", "PR20", "PR24"} <= set(
        plan.published_uaas(db_session)
    )
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_reserves_and_documents(db_session):
    module, uaa = _pr04(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert import_practical_bank(db_session, module, uaa) == len(PRACTICE_ITEMS) + len(EXAM_ITEMS)
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    usages = [question_usage(q) for q in questions]
    assert usages.count("practice") == len(PRACTICE_ITEMS) and usages.count("exam") == 10


def test_correction_context_is_pr04_specific():
    context = _pedagogical_context_for("PR04")
    assert context is get_practical_context("PR04")
    assert context.course_key == SLUG
    notions = " ".join(context.allowed_notions)
    assert "Sanitize" in notions and "seul le propriétaire décide" in notions and "Bebat" in notions
    assert "formatage rapide efface" in context.constraints and "mot-clé" in context.constraints


# =============================================================================================
# 6. Pages et sessions
# =============================================================================================


def test_course_page_renders_figures_and_exercises(client, db_session):
    _pr04(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert len(ids) == len(set(ids)) and set(ids) >= {f"fig-{f.key}" for f in PR04_FIGURES}
    assert html.count('class="jc-exercise-card"') == len(PRACTICE_ITEMS)
    assert "<details open" not in html
    assert 'href="/ampcr-pratique"' in html and f"/uaa/{SLUG}/exam" in html
    assert "<table" in html


def test_practical_home_and_matrix_show_pr04(client, db_session):
    _pr04(db_session)
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and "10 cours publiés" in home
    for req in REQ:
        assert plan.requirement_status(req, {"PR04"}) == plan.STATUS_PARTIAL
    assert plan.VALIDATED_REQUIREMENT_IDS == frozenset()
    assert client.get("/ampcr-pratique/matrice").status_code == 200


@pytest.mark.parametrize("mode", ["practice", "exam"])
def test_sessions_draw_only_from_their_reserve_without_generation(authenticated_client, db_session, monkeypatch, mode):
    fake = _patch_fake_provider(monkeypatch)
    _pr04(db_session)
    assert authenticated_client.get(f"/uaa/{SLUG}/{mode}").status_code == 200
    session_url = _start_session(authenticated_client, db_session, SLUG, mode)
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert {question_usage(sq.question_version.question) for sq in session.session_questions} == {mode}
    assert session.question_count == 10
    assert fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"PR04"}
    if mode == "exam":
        page = authenticated_client.get(f"{session_url}?q=1").text
        assert "Corrigé de référence" not in page and "Barème" not in page


def test_exam_lengths_limited_and_score_on_20(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _pr04(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    from app.v1.models import User

    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="PR04", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "/ 20" in html


def test_practice_sessions_with_classification_and_ordering_submit(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr04(db_session)
    for _ in range(2):  # 16 exercices : deux sessions de 10 couvrent toute la réserve
        session_url = _start_session(authenticated_client, db_session, SLUG, "practice")
        _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
        assert authenticated_client.get(session_url).status_code == 200
