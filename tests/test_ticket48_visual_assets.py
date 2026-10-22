"""Ticket #48 — Informatique V1 : assets visuels et questions d'identification de
composants (MC01). Aucun appel IA réel : correction via `FakeAIProvider`, régénération
d'image via un faux fournisseur local."""

import itertools
import re

import pytest

from app.ai.fake_provider import FakeAIProvider
from app.models import UAA
from app.seed import seed
from app.v1.ai_bridge import CORRECTABLE_TYPES, describe_submitted_answer
from app.v1.ampcr_visual_bank import (
    ASSET_SPECS,
    VISUAL_BANK_VERSION,
    VISUAL_QUESTIONS,
    import_mc01_visual_questions,
)
from app.v1.assets import (
    AssetError,
    AssetSpec,
    VisualType,
    asset_visual_type,
    assets_for_version,
    get_or_create_asset,
    link_asset,
    mark_asset_incorrect,
    reactivate_asset,
    regenerate_asset,
    static_path,
    unusable_asset_question_ids,
)
from app.v1.bank import select_bank_questions
from app.v1.bank_admin import edit_question_content
from app.v1.dedup import is_near_duplicate, question_signature
from app.v1.models import (
    Asset,
    AssetKind,
    AssetSourceType,
    ContentStatus,
    GenerationSource,
    Question,
    QuestionAsset,
    QuestionVersion,
    SessionDifficultyRequest,
    SessionMode,
    SessionStatus,
    User,
    create_question,
)
from app.v1.question_engine import validate_content


def _csrf(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "jeton CSRF introuvable"
    return match.group(1)


def _mc01(db):
    seed()
    uaa = db.query(UAA).filter_by(slug="ampcr-mc01").one()
    return uaa.module, uaa


def _visual_questions(db, uaa) -> list[Question]:
    return (
        db.query(Question)
        .join(QuestionVersion, QuestionVersion.id == Question.current_version_id)
        .filter(Question.uaa_id == uaa.id, QuestionVersion.prompt_version == VISUAL_BANK_VERSION)
        .order_by(Question.id)
        .all()
    )


# --- 1. Contenu de la banque visuelle -----------------------------------------------------------


def test_asset_files_exist_and_photos_carry_source_and_license():
    for spec in ASSET_SPECS.values():
        assert static_path(spec.storage_ref).is_file(), spec.storage_ref
        assert spec.license and spec.provenance and spec.alt_text
        if spec.visual_type == VisualType.PHOTO:
            assert spec.source_url.startswith("https://commons.wikimedia.org/")
            assert spec.author
    natures = {spec.visual_type for spec in ASSET_SPECS.values()}
    assert natures == {VisualType.PHOTO, VisualType.ILLUSTRATION, VisualType.DIAGRAM}


def test_visual_questions_are_valid_correctable_and_never_near_duplicates():
    for asset_key, question_type, content in VISUAL_QUESTIONS:
        assert asset_key in ASSET_SPECS
        assert question_type in CORRECTABLE_TYPES
        validate_content(question_type, 1, content)
    signatures = [question_signature(t, c) for _, t, c in VISUAL_QUESTIONS]
    for a, b in itertools.combinations(signatures, 2):
        assert not is_near_duplicate(a, b)


def test_choice_answers_are_not_always_in_the_same_position():
    positions = {
        [o["option_id"] for o in content["options"]].index(content["correct_option_ids"][0])
        for _, question_type, content in VISUAL_QUESTIONS
        if question_type == "image_identification" and content["response_mode"] == "choice"
    }
    assert len(positions) >= 3


# --- 2. Import idempotent, assets sans doublon, réutilisation par ID ----------------------------


def test_import_is_idempotent_and_assets_are_not_duplicated(db_session):
    module, uaa = _mc01(db_session)
    assert import_mc01_visual_questions(db_session, module, uaa) == len(VISUAL_QUESTIONS)
    db_session.commit()
    assert import_mc01_visual_questions(db_session, module, uaa) == 0
    db_session.commit()

    assert db_session.query(Asset).count() == len(ASSET_SPECS)
    questions = _visual_questions(db_session, uaa)
    assert len(questions) == len(VISUAL_QUESTIONS)
    for question in questions:
        assert question.generation_source == GenerationSource.MANUAL
        assert question.difficulty_declared is None
        assert len(assets_for_version(db_session, question.current_version_id)) == 1

    diagram = db_session.query(Asset).filter_by(storage_ref=ASSET_SPECS["motherboard_diagram"].storage_ref).one()
    assert db_session.query(QuestionAsset).filter_by(asset_id=diagram.id).count() == 2
    assert asset_visual_type(diagram) == VisualType.DIAGRAM


def test_get_or_create_asset_reuses_same_file_even_under_another_key(db_session):
    first = get_or_create_asset(db_session, ASSET_SPECS["ram"])
    same_file = AssetSpec(**{**ASSET_SPECS["ram"].__dict__, "key": "autre-cle"})
    assert get_or_create_asset(db_session, same_file).id == first.id
    assert db_session.query(Asset).count() == 1


def test_link_asset_respects_question_type_contract(db_session):
    module, uaa = _mc01(db_session)
    asset = get_or_create_asset(db_session, ASSET_SPECS["ram"])
    question = create_question(
        db_session, module_id=module.id, uaa_id=uaa.id, question_type="short_answer",
        content_json={"prompt": "Que signifie RAM ?", "accepted_answers": ["mémoire vive"]},
        generation_source=GenerationSource.MANUAL,
    )
    with pytest.raises(AssetError):
        link_asset(db_session, question.current_version, asset)


def test_mc01_bank_selection_includes_visual_questions(client, authenticated_client, db_session):
    seed()
    assert authenticated_client.get("/uaa/ampcr-mc01/practice").status_code == 200
    uaa = db_session.query(UAA).filter_by(slug="ampcr-mc01").one()
    assert len(_visual_questions(db_session, uaa)) == len(VISUAL_QUESTIONS)
    user = db_session.query(User).one()
    selected = select_bank_questions(
        db_session, user_id=user.id, module_id=uaa.module_id, uaa_id=uaa.id, limit=200
    )
    types = {q.current_version.question_type for q in selected}
    assert {"image_identification", "diagram_labeling"} <= types


# --- 3. Parcours élève complet : affichage, réponses, correction, résultats ----------------------


def _correct_form(question: Question) -> dict:
    content = question.current_version.content_json
    if question.current_version.question_type == "diagram_labeling":
        return {f"zone__{zone}": label for zone, label in content["correct_mapping"].items()}
    if content["response_mode"] == "choice":
        return {"option_id": content["correct_option_ids"]}
    return {"text": "Carte graphique"}


def test_full_session_renders_images_and_corrects_visual_answers(authenticated_client, db_session, monkeypatch):
    from app.v1.session_service import (
        _finalize_session,
        claim_next_pending_correction_job,
        run_correction_job,
    )

    seed()
    assert authenticated_client.get("/uaa/ampcr-mc01/practice").status_code == 200
    uaa = db_session.query(UAA).filter_by(slug="ampcr-mc01").one()
    questions = _visual_questions(db_session, uaa)
    user = db_session.query(User).one()
    session = _finalize_session(
        db_session, user=user, module_id=uaa.module_id, mode=SessionMode.PRACTICE,
        difficulty=SessionDifficultyRequest.MEDIUM, selected=questions,
    )
    url = f"/sessions/{session.id}"
    total = len(questions)
    for position, question in enumerate(questions, start=1):
        page = authenticated_client.get(f"{url}?q={position}")
        assert page.status_code == 200
        asset = assets_for_version(db_session, question.current_version_id)[0]
        assert f'src="/static/{asset.storage_ref}"' in page.text
        assert 'class="img-fluid' in page.text
        if question.current_version.question_type == "diagram_labeling":
            assert 'name="zone__A"' in page.text
        data = {"csrf_token": _csrf(page.text), "position": position,
                "direction": "submit" if position == total else "next", **_correct_form(question)}
        response = authenticated_client.post(f"{url}/answer", data=data, follow_redirects=False)
        assert response.status_code == 303

    confirm = authenticated_client.get(f"{url}/submit-confirm")
    response = authenticated_client.post(f"{url}/submit", data={"csrf_token": _csrf(confirm.text)},
                                         follow_redirects=False)
    assert response.status_code == 303
    job = claim_next_pending_correction_job(db_session)
    run_correction_job(db_session, job=job, provider=FakeAIProvider())

    db_session.expire_all()
    session = db_session.get(type(session), session.id)
    assert session.status == SessionStatus.COMPLETED
    assert all(sq.answer.points_awarded == 1.0 for sq in session.session_questions)

    results = authenticated_client.get(url)
    assert results.status_code == 200
    assert "/static/img/ampcr/mc01_schema_carte_mere.svg" in results.text
    assert "Repère A → Emplacements PCIe" in results.text
    assert "CC BY-SA 4.0" in results.text and "Photo réelle" in results.text
    assert authenticated_client.get("/static/img/ampcr/mc01_schema_carte_mere.svg").status_code == 200


def test_diagram_labeling_gives_partial_credit_and_describes_answer(db_session):
    from app.ai.local_correction import correct_locally
    from app.v1.ai_bridge import answer_json_to_submitted, content_to_questionnaire_question

    content = next(c for _, t, c in VISUAL_QUESTIONS if t == "diagram_labeling")
    question = content_to_questionnaire_question(
        question_id="q1", question_type="diagram_labeling", content=content, points_max=1.0
    )
    half = {"mapping": {"A": "pcie", "B": "ram_slots", "C": "socket", "D": "io", "E": "chipset", "F": "pcie"}}
    result = correct_locally(question, answer_json_to_submitted("diagram_labeling", content, half))
    assert 0 < result.points_awarded < 1
    assert describe_submitted_answer("diagram_labeling", content, {"mapping": {}}) == "(sans réponse)"
    assert "Repère B → Emplacements RAM" in describe_submitted_answer("diagram_labeling", content, half)


# --- 4. Signalement admin, exclusion, réactivation, édition, régénération -----------------------


def test_flagged_asset_removes_its_questions_until_reactivated(db_session):
    module, uaa = _mc01(db_session)
    import_mc01_visual_questions(db_session, module, uaa)
    db_session.commit()
    diagram = db_session.query(Asset).filter_by(storage_ref=ASSET_SPECS["motherboard_diagram"].storage_ref).one()

    mark_asset_incorrect(db_session, diagram, reason="repère mal placé", request_regeneration=True)
    db_session.commit()
    excluded = unusable_asset_question_ids(db_session)
    assert len(excluded) == 2
    selected_ids = {q.id for q in select_bank_questions(
        db_session, user_id=999, module_id=module.id, uaa_id=uaa.id, limit=200)}
    assert not (selected_ids & excluded)

    reactivate_asset(db_session, diagram)
    db_session.commit()
    assert unusable_asset_question_ids(db_session) == set()


def test_admin_edit_keeps_the_question_image(db_session):
    module, uaa = _mc01(db_session)
    import_mc01_visual_questions(db_session, module, uaa)
    db_session.commit()
    question = _visual_questions(db_session, uaa)[0]
    old_version_id = question.current_version_id
    content = dict(question.current_version.content_json, prompt="Quel composant vois-tu sur cette photo ?")
    import json

    version = edit_question_content(db_session, question, json.dumps(content))
    assert version.id != old_version_id
    assert [a.id for a in assets_for_version(db_session, version.id)] == [
        a.id for a in assets_for_version(db_session, old_version_id)
    ]


class _FakeImageProvider:
    _model = "fake-image-model"

    def __init__(self):
        self.calls = 0

    def generate_image(self, prompt, size="1024x1024", quality="high"):
        self.calls += 1
        return b"\x89PNG\r\n\x1a\nfake-" + prompt[:10].encode()


def test_regenerate_ai_asset_creates_new_asset_and_new_version(db_session, monkeypatch, tmp_path):
    monkeypatch.setattr("app.v1.assets.STATIC_DIR", tmp_path)
    module, uaa = _mc01(db_session)
    old = Asset(kind=AssetKind.IMAGE, storage_ref="img/x.png", mime_type="image/png",
                source_type=AssetSourceType.AI_GENERATED, license="Créé pour Jury Central",
                metadata_json={"visual_type": "illustration", "generation_prompt": "a RAM stick",
                               "alt_text": "illustration"})
    db_session.add(old)
    db_session.flush()
    question = create_question(
        db_session, module_id=module.id, uaa_id=uaa.id, question_type="image_identification",
        content_json=VISUAL_QUESTIONS[0][2], generation_source=GenerationSource.MANUAL,
    )
    first_version_id = question.current_version_id
    link_asset(db_session, question.current_version, old)
    mark_asset_incorrect(db_session, old, request_regeneration=True)

    provider = _FakeImageProvider()
    new = regenerate_asset(db_session, old, provider)
    db_session.commit()

    assert provider.calls == 1
    assert new.id != old.id and new.status == ContentStatus.ACTIVE
    assert (tmp_path / new.storage_ref).is_file()
    assert question.current_version_id != first_version_id
    assert [a.id for a in assets_for_version(db_session, question.current_version_id)] == [new.id]
    assert [a.id for a in assets_for_version(db_session, first_version_id)] == [old.id]
    assert old.status == ContentStatus.INVALID and old.metadata_json["replaced_by_asset_id"] == new.id
    assert question.id not in unusable_asset_question_ids(db_session)


def test_photo_cannot_be_regenerated_automatically(db_session):
    photo = get_or_create_asset(db_session, ASSET_SPECS["ram"])
    with pytest.raises(AssetError):
        regenerate_asset(db_session, photo, _FakeImageProvider())


def test_admin_assets_pages_flag_and_reactivate(admin_client, db_session):
    module, uaa = _mc01(db_session)
    import_mc01_visual_questions(db_session, module, uaa)
    db_session.commit()
    question = _visual_questions(db_session, uaa)[0]
    asset = assets_for_version(db_session, question.current_version_id)[0]

    page = admin_client.get("/admin/bank/assets")
    assert page.status_code == 200
    assert "Photo réelle" in page.text and "Schéma technique" in page.text and "Illustration générée" in page.text
    detail = admin_client.get(f"/admin/bank/questions/{question.id}")
    assert "Visuels de la version courante" in detail.text

    r = admin_client.post(f"/admin/bank/assets/{asset.id}/flag", data={
        "csrf_token": _csrf(detail.text), "reason": "mauvaise photo", "request_regeneration": "1",
        "next_question": str(question.id)}, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == f"/admin/bank/questions/{question.id}?done=asset_flagged"
    db_session.expire_all()
    assert db_session.get(Asset, asset.id).status == ContentStatus.INVALID
    detail = admin_client.get(r.headers["location"])
    assert "Régénération demandée" in detail.text

    r = admin_client.post(f"/admin/bank/assets/{asset.id}/reactivate", data={
        "csrf_token": _csrf(detail.text)}, follow_redirects=False)
    assert r.headers["location"] == "/admin/bank/assets?done=asset_reactivated"
    db_session.expire_all()
    assert db_session.get(Asset, asset.id).status == ContentStatus.ACTIVE
