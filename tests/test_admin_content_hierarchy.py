from app.models import UAA, BlockType, LessonBlock, Module, Subject
from app.seed import UAA1_BLOCKS, UAA1_TITLE, UAA2_BLOCKS, seed


def test_create_subject_via_admin(admin_client, db_session):
    response = admin_client.post(
        "/admin/subjects/new", data={"name": "Français", "slug": ""}, follow_redirects=False
    )
    assert response.status_code == 303

    subject = db_session.query(Subject).filter_by(name="Français").first()
    assert subject is not None
    assert subject.slug == "francais"


def test_create_subject_rejects_duplicate_slug(admin_client, db_session):
    db_session.add(Subject(name="Histoire", slug="sciences"))
    db_session.commit()

    response = admin_client.post("/admin/subjects/new", data={"name": "Sciences", "slug": "sciences"})
    assert response.status_code == 400


def test_create_subject_rejects_duplicate_name(admin_client, db_session):
    db_session.add(Subject(name="Histoire", slug="histoire"))
    db_session.commit()

    response = admin_client.post("/admin/subjects/new", data={"name": "Histoire", "slug": "histoire-2"})
    assert response.status_code == 400


def test_create_subject_rejects_empty_name(admin_client):
    response = admin_client.post("/admin/subjects/new", data={"name": "   ", "slug": ""})
    assert response.status_code == 400


def test_update_subject(admin_client, db_session):
    subject = Subject(name="Sciences", slug="sciences")
    db_session.add(subject)
    db_session.commit()

    response = admin_client.post(
        f"/admin/subjects/{subject.id}/edit",
        data={"name": "Sciences naturelles", "slug": "sciences-naturelles"},
        follow_redirects=False,
    )
    assert response.status_code == 303

    db_session.refresh(subject)
    assert subject.name == "Sciences naturelles"
    assert subject.slug == "sciences-naturelles"


def test_create_module_under_subject(admin_client, db_session):
    subject = Subject(name="Mathématiques", slug="mathematiques")
    db_session.add(subject)
    db_session.commit()

    response = admin_client.post(
        f"/admin/subjects/{subject.id}/modules/new",
        data={"code": "MQ32", "slug": ""},
        follow_redirects=False,
    )
    assert response.status_code == 303

    module = db_session.query(Module).filter_by(code="MQ32").first()
    assert module is not None
    assert module.subject_id == subject.id
    assert module.slug == "mq32"


def test_create_module_rejects_duplicate_slug(admin_client, db_session):
    subject = Subject(name="Mathématiques", slug="mathematiques")
    db_session.add(subject)
    db_session.flush()
    db_session.add(Module(code="MB32", slug="mb32", subject=subject))
    db_session.commit()

    response = admin_client.post(
        f"/admin/subjects/{subject.id}/modules/new", data={"code": "MB32-bis", "slug": "mb32"}
    )
    assert response.status_code == 400


def test_create_uaa_under_module(admin_client, db_session):
    subject = Subject(name="Mathématiques", slug="mathematiques")
    db_session.add(subject)
    db_session.flush()
    module = Module(code="MB32", slug="mb32", subject=subject)
    db_session.add(module)
    db_session.commit()

    response = admin_client.post(
        f"/admin/modules/{module.id}/uaa/new",
        data={
            "code": "UAA2",
            "title": "Nouvelle UAA",
            "slug": "",
            "position": "2",
            "is_published": "on",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303

    uaa = db_session.query(UAA).filter_by(code="UAA2").first()
    assert uaa is not None
    assert uaa.module_id == module.id
    assert uaa.slug == "mb32-uaa2"
    assert uaa.position == 2
    assert uaa.is_published is True


def test_update_uaa_changes_title_position_and_publication(admin_client, db_session):
    subject = Subject(name="Mathématiques", slug="mathematiques")
    db_session.add(subject)
    db_session.flush()
    module = Module(code="MB32", slug="mb32", subject=subject)
    db_session.add(module)
    db_session.flush()
    uaa = UAA(code="UAA2", title="Titre initial", slug="mb32-uaa2", position=1, module=module)
    db_session.add(uaa)
    db_session.commit()

    response = admin_client.post(
        f"/admin/uaa/{uaa.id}/edit",
        data={
            "code": "UAA2",
            "title": "Titre corrigé",
            "slug": "mb32-uaa2",
            "position": "5",
            "is_published": "on",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303

    db_session.refresh(uaa)
    assert uaa.title == "Titre corrigé"
    assert uaa.position == 5
    assert uaa.is_published is True


def test_admin_hierarchy_routes_require_login(client):
    for path in [
        "/admin/subjects",
        "/admin/subjects/new",
        "/admin/subjects/1",
        "/admin/subjects/1/edit",
        "/admin/subjects/1/modules/new",
        "/admin/modules/1",
        "/admin/modules/1/edit",
        "/admin/modules/1/uaa/new",
        "/admin/uaa/1/edit",
    ]:
        response = client.get(path, follow_redirects=False)
        assert response.status_code == 303, path
        assert response.headers["location"] == "/admin/login"


def test_admin_hierarchy_write_routes_require_login(client):
    response = client.post("/admin/subjects/new", data={"name": "X", "slug": "x"}, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/admin/login"


def test_delete_subject_cascades_to_modules_uaas_and_blocks(admin_client, db_session):
    subject = Subject(name="Mathématiques", slug="mathematiques")
    db_session.add(subject)
    db_session.flush()
    module = Module(code="MB32", slug="mb32", subject=subject)
    db_session.add(module)
    db_session.flush()
    uaa = UAA(code="UAA1", title="Test", slug="mb32-uaa1", module=module)
    db_session.add(uaa)
    db_session.flush()
    db_session.add(
        LessonBlock(uaa=uaa, title="Bloc", type=BlockType.MARKDOWN, content="x", position=1)
    )
    db_session.commit()
    subject_id = subject.id

    response = admin_client.post(f"/admin/subjects/{subject_id}/delete", follow_redirects=False)
    assert response.status_code == 303

    db_session.expire_all()  # la suppression a eu lieu via une autre session (la requête HTTP)
    assert db_session.get(Subject, subject_id) is None
    assert db_session.query(Module).count() == 0
    assert db_session.query(UAA).count() == 0
    assert db_session.query(LessonBlock).count() == 0


def test_unpublished_uaa_is_not_listed_and_returns_404(admin_client, db_session):
    subject = Subject(name="Mathématiques", slug="mathematiques")
    db_session.add(subject)
    db_session.flush()
    module = Module(code="MB32", slug="mb32", subject=subject)
    db_session.add(module)
    db_session.flush()
    uaa = UAA(
        code="UAA9", title="Brouillon", slug="mb32-uaa9", position=1, is_published=False, module=module
    )
    db_session.add(uaa)
    db_session.commit()

    list_response = admin_client.get("/modules/mb32")
    assert "Brouillon" not in list_response.text

    detail_response = admin_client.get("/uaa/mb32-uaa9")
    assert detail_response.status_code == 404


def test_published_uaa_is_listed_and_accessible(admin_client, db_session):
    subject = Subject(name="Mathématiques", slug="mathematiques")
    db_session.add(subject)
    db_session.flush()
    module = Module(code="MB32", slug="mb32", subject=subject)
    db_session.add(module)
    db_session.flush()
    uaa = UAA(
        code="UAA9", title="Publiée", slug="mb32-uaa9", position=1, is_published=True, module=module
    )
    db_session.add(uaa)
    db_session.commit()

    list_response = admin_client.get("/modules/mb32")
    assert "Publiée" in list_response.text

    detail_response = admin_client.get("/uaa/mb32-uaa9")
    assert detail_response.status_code == 200


def test_seed_is_idempotent(db_session):
    seed()
    seed()

    assert db_session.query(Subject).count() == 1
    assert db_session.query(Module).count() == 3
    assert db_session.query(UAA).count() == 2
    assert db_session.query(LessonBlock).count() == len(UAA1_BLOCKS) + len(UAA2_BLOCKS)


def test_seed_does_not_overwrite_a_manually_edited_uaa_title(db_session):
    seed()

    uaa = db_session.query(UAA).filter_by(code="UAA1").first()
    uaa.title = "Titre modifié depuis l'admin"
    db_session.commit()

    seed()

    db_session.refresh(uaa)
    assert uaa.title == "Titre modifié depuis l'admin"
    assert uaa.title != UAA1_TITLE


def test_seed_does_not_overwrite_a_manually_edited_block_content(db_session):
    seed()

    block = db_session.query(LessonBlock).filter_by(title="Plan de l'UAA").first()
    block.content = "Contenu modifié depuis l'admin"
    db_session.commit()

    seed()

    db_session.refresh(block)
    assert block.content == "Contenu modifié depuis l'admin"
