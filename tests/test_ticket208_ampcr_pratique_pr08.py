"""Ticket #208 — AMPCR pratique écrite, PR08 « Installation complète de Windows — préparation et
dépannage ».

Couvre : données de référence **recontrôlées ici** indépendamment (activation selon la licence,
règle de suppression des partitions, disposition GPT standard, dépannage par familles, codes
fabricants, trois procédures, liste de contrôle et rapport) ; schémas SVG (validité,
accessibilité, étapes cohérentes avec les données) ; exercices et mini-examen (format du socle,
remises en ordre et classements auto-corrigés, pas de question d'acronyme, contexte complet) ;
cours (matière du ticket, 3 procédures, 5 cas résolus, affirmations techniques justes, supports
fictifs, cartes) ; banque, seed, pages et sessions.
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
from app.v1.ampcr_pratique_pr08_bank import (
    E06_RESULTS,
    E11_VENDORS,
    EXAM_ITEMS,
    EXAM_TOTAL_POINTS,
    KIND_ERROR,
    KIND_INSTALL,
    KIND_ORDER,
    KIND_POST,
    KIND_PREP,
    KIND_TROUBLE,
    PRACTICE_ITEMS,
    REQ,
    WHEN_AFTER,
    WHEN_BEFORE,
    WHEN_DURING,
    X01_RESULT,
    X02_ACTIONS,
    X06_VENDOR,
    validate_items,
)
from app.v1.ampcr_pratique_pr08_course import PR08_SLUG, PR08_TITLE, pr08_course_sections
from app.v1.ampcr_pratique_pr08_figures import (
    ACTIVATES,
    CHECKLIST,
    DEVMGR_SCREEN,
    FINAL_STEPS,
    INSTALLER_DISKS_SCREEN,
    LIC_DIGITAL,
    LIC_OEM,
    LIC_RETAIL,
    MBR_ERROR_SCREEN,
    NO_DRIVE_SCREEN,
    NO_DRIVE_TREE,
    NOT_ACTIVATED,
    PART_DELETE,
    PART_KEEP,
    PART_STOP,
    PR08_FIGURES,
    PREP_STEPS,
    PROCEDURES,
    REPORT_SECTIONS,
    SCREEN_WIDTH,
    SETUP_STEPS,
    STANDARD_LAYOUT,
    TR_BOOT,
    TR_CATEGORIES,
    TR_DRIVER,
    TR_LICENCE,
    TR_PARTITION,
    TR_STORAGE,
    TROUBLES_BY_CATEGORY,
    activation_result,
    partition_action,
    vendor_of,
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

SLUG = "ampcr-pratique-pr08"


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _course_raw() -> str:
    return " ".join(c for _t, c in pr08_course_sections())


def _course_text() -> str:
    return _text(_course_raw()).replace("**", "").replace("`", "").lower()


def _all_items_text() -> str:
    return " ".join(
        " ".join((i.title, i.context, *i.instructions, *i.correction, *(c.expected for c in i.criteria),
                  *(d.content_text for d in i.documents)))
        for i in PRACTICE_ITEMS + EXAM_ITEMS
    )


def _pr08(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "PR08")
    return module, uaa


# =============================================================================================
# 1. Données de référence, recontrôlées indépendamment
# =============================================================================================


def test_activation_follows_licence_and_edition():
    assert activation_result(LIC_OEM, "Famille", "Famille", same_pc=True)[0] == ACTIVATES
    # Édition différente de la licence : jamais activé, quel que soit le type.
    for lic in (LIC_OEM, LIC_RETAIL, LIC_DIGITAL):
        assert activation_result(lic, "Famille", "Professionnel", same_pc=True)[0] == NOT_ACTIVATED, lic
    # OEM et numérique liées au PC ; commerciale transférable si retirée de l'ancien PC.
    assert activation_result(LIC_OEM, "Pro", "Pro", same_pc=False)[0] == NOT_ACTIVATED
    assert activation_result(LIC_DIGITAL, "Pro", "Pro", same_pc=False)[0] == NOT_ACTIVATED
    assert activation_result(LIC_RETAIL, "Pro", "Pro", same_pc=False, removed_from_old_pc=True)[0] == ACTIVATES
    assert activation_result(LIC_RETAIL, "Pro", "Pro", same_pc=False, removed_from_old_pc=False)[0] == NOT_ACTIVATED
    with pytest.raises(ValueError):
        activation_result("craquée", "Pro", "Pro", same_pc=True)
    assert [r for r, _w in E06_RESULTS] == [ACTIVATES, NOT_ACTIVATED, NOT_ACTIVATED, ACTIVATES, ACTIVATES, NOT_ACTIVATED]
    assert X01_RESULT == NOT_ACTIVATED


def test_partition_rule_never_erases_without_backup_and_consent():
    for backup in (True, False):
        for consent in (True, False):
            assert partition_action(on_target_disk=False, backup_verified=backup, written_consent=consent) == PART_KEEP
            expected = PART_DELETE if backup and consent else PART_STOP
            assert partition_action(on_target_disk=True, backup_verified=backup, written_consent=consent) == expected
    assert X02_ACTIONS == (PART_DELETE, PART_KEEP)


def test_standard_gpt_layout():
    # Documentation Microsoft (UEFI/GPT) : ESP FAT32, MSR 16 Mo, Windows NTFS, Récupération.
    keys = [p.key for p in STANDARD_LAYOUT]
    assert keys == ["esp", "msr", "windows", "recovery"]
    by_key = {p.key: p for p in STANDARD_LAYOUT}
    assert by_key["esp"].filesystem == "FAT32" and "100 Mo" in by_key["esp"].size_label
    assert by_key["msr"].size_label == "16 Mo"
    assert by_key["windows"].filesystem == "NTFS" and "C:" in by_key["windows"].name
    assert "WinRE" in by_key["recovery"].role


def test_troubleshooting_families_and_vendor_ids():
    assert TR_CATEGORIES == (TR_STORAGE, TR_BOOT, TR_PARTITION, TR_DRIVER, TR_LICENCE)
    for category in TR_CATEGORIES:  # les cinq variantes du ticket sont couvertes
        assert TROUBLES_BY_CATEGORY[category], category
    storage = " ".join(t.action for t in TROUBLES_BY_CATEGORY[TR_STORAGE])
    assert "Charger un pilote" in storage
    partition = " ".join(t.action + t.never for t in TROUBLES_BY_CATEGORY[TR_PARTITION])
    assert "mbr2gpt" in partition and "mode hérité" in partition
    boot_never = " ".join(t.never for t in TROUBLES_BY_CATEGORY[TR_BOOT])
    assert "Désactiver le démarrage sécurisé" in boot_never
    assert all(t.never for t in TROUBLES_BY_CATEGORY[TR_LICENCE])
    # PCI-SIG : 8086 Intel, 10EC Realtek, 10DE NVIDIA, 1022 AMD, 14E4 Broadcom.
    assert vendor_of("PCI\\VEN_8086&DEV_2725") == "Intel"
    assert vendor_of("PCI\\VEN_10ec&DEV_8168") == "Realtek"
    assert vendor_of("PCI\\VEN_10DE&DEV_1F82") == "NVIDIA"
    assert vendor_of("USB\\VID_046D") is None and vendor_of("PCI\\VEN_FFFF") is None
    assert E11_VENDORS == ("NVIDIA", "Broadcom") and X06_VENDOR == "Realtek"
    assert len(NO_DRIVE_TREE) == 4 and "firmware" in NO_DRIVE_TREE[0][0]


def test_procedures_order_checklist_and_report():
    assert len(PROCEDURES) == 3
    prep = [label for label, _d in PREP_STEPS]
    assert prep[0] == "Recueillir la demande" and prep.index("Sauvegarder") < prep.index("Préparer le média")
    setup = [label for label, _d in SETUP_STEPS]
    assert setup[0] == "Régler le firmware" and setup[-1] == "Configuration initiale"
    assert setup.index("Clé et édition") < setup.index("Type d'installation") < setup.index("Disque et partitions")
    assert "UEFI:" in SETUP_STEPS[1][1]
    final = [label for label, _d in FINAL_STEPS]
    assert final[0] == "Pilotes" and final[-1] == "Contrôler et documenter"
    assert final.index("Mises à jour") < final.index("Activation") < final.index("Sécurité")
    points = [p for p, _w, _e in CHECKLIST]
    for point in ("Activation", "Démarrage", "Disque", "Pilotes", "Mises à jour", "Sécurité", "Données et logiciels"):
        assert point in points, point
    assert REPORT_SECTIONS[0][0] == "Demande" and "accord écrit" in REPORT_SECTIONS[0][1]


def test_screens_readable_and_consistent():
    for screen in (INSTALLER_DISKS_SCREEN, NO_DRIVE_SCREEN, MBR_ERROR_SCREEN, DEVMGR_SCREEN):
        assert max(len(line) for line in screen) <= SCREEN_WIDTH
    assert "Charger un pilote" in " ".join(NO_DRIVE_SCREEN) and "VMD" in " ".join(NO_DRIVE_SCREEN)
    mbr = " ".join(MBR_ERROR_SCREEN)
    assert "GPT" in mbr and "list disk" in mbr
    disk0, disk1 = (line for line in MBR_ERROR_SCREEN if line.strip().startswith("Disque "))
    assert not disk0.rstrip().endswith("*") and disk1.rstrip().endswith("*")  # disque 0 en MBR, clé en GPT
    disks = " ".join(INSTALLER_DISKS_SCREEN)
    assert "Lecteur 0" in disks and "Lecteur 1" in disks and "DONNEES" in disks
    assert "VEN_10EC" in " ".join(DEVMGR_SCREEN) and "Carte graphique de base Microsoft" in " ".join(DEVMGR_SCREEN)


# =============================================================================================
# 2. Schémas
# =============================================================================================


def test_figures_valid_accessible_and_unique():
    keys = [f.key for f in PR08_FIGURES]
    assert len(keys) == len(set(keys)) == 9
    for figure in PR08_FIGURES:
        assert validate_figure(figure) == [], figure.key
        html = str(render_figure(figure))
        assert 'role="img"' in html and "(schéma non officiel)" in html and not figure.official


def test_figures_drawn_from_data():
    by_key = {f.key: f for f in PR08_FIGURES}
    for key, steps in (("pr08-preparer", PREP_STEPS), ("pr08-installer", SETUP_STEPS), ("pr08-finaliser", FINAL_STEPS)):
        svg = by_key[key].svg
        for index, (label, _detail) in enumerate(steps, start=1):
            assert f"{index}. {escape(label)}" in svg, (key, label)
    partitions = re.findall(r'data-partition="([^"]+)"', by_key["pr08-partitions-gpt"].svg)
    assert partitions == [p.key for p in STANDARD_LAYOUT]
    assert by_key["pr08-disque-introuvable"].svg.count("data-step=") == len(NO_DRIVE_TREE)
    for key in ("pr08-choix-disque", "pr08-aucun-lecteur", "pr08-disque-mbr", "pr08-gestionnaire-peripheriques"):
        assert "fictive" in by_key[key].caption.lower() and "Capture fictive" in by_key[key].svg, key


# =============================================================================================
# 3. Exercices et mini-examen
# =============================================================================================


def test_items_valid_and_counts_match_ticket():
    assert validate_items() == []
    assert len(PRACTICE_ITEMS) >= 16 and len(EXAM_ITEMS) == 10  # ticket : ≥ 16 exercices, mini-examen /20
    assert sum(i.total_points for i in EXAM_ITEMS) == EXAM_TOTAL_POINTS == 20
    kinds = [i.kind for i in PRACTICE_ITEMS]
    for kind, minimum in ((KIND_ORDER, 3), (KIND_PREP, 3), (KIND_INSTALL, 2), (KIND_TROUBLE, 3), (KIND_POST, 1),
                          (KIND_ERROR, 1)):
        assert kinds.count(kind) >= minimum, kind
    keys = [i.key for i in PRACTICE_ITEMS + EXAM_ITEMS]
    assert len(keys) == len(set(keys))
    covered = {r for i in PRACTICE_ITEMS + EXAM_ITEMS for r in i.requirement_ids}
    assert REQ <= covered and "AP-C03" in covered
    assert set(plan.COURSE_SLOTS_BY_CODE["PR08"].requirement_ids) == REQ
    types = [i.question_type for i in PRACTICE_ITEMS]
    assert types.count("ordering") == 3 and types.count("classification") == 4


def test_auto_corrected_answers():
    by_key = {i.key: i for i in PRACTICE_ITEMS}

    def ordered(key: str) -> list[str]:
        o = by_key[key].ordering
        return [o.steps[i].split(" — ")[0] for i in o.correct]

    assert ordered("E01") == [label for label, _d in PREP_STEPS]
    assert ordered("E02") == [label for label, _d in SETUP_STEPS]
    assert ordered("E03") == [label for label, _d in FINAL_STEPS]

    def answers(key: str) -> dict[str, str]:
        c = by_key[key].classification
        return dict(zip(c.elements, (c.categories[i] for i in c.correct), strict=True))

    e04 = answers("E04")
    assert next(v for k, v in e04.items() if "aucun lecteur" in k) == TR_STORAGE
    assert next(v for k, v in e04.items() if "disques GPT" in k) == TR_PARTITION
    assert next(v for k, v in e04.items() if "choix de la langue" in k) == TR_BOOT
    assert next(v for k, v in e04.items() if "Ethernet" in k) == TR_DRIVER
    assert next(v for k, v in e04.items() if "activé" in k) == TR_LICENCE
    assert next(v for k, v in e04.items() if "débranche" in k) == TR_PARTITION
    e05 = answers("E05")
    assert next(v for k, v in e05.items() if "DONNEES" in k) == PART_KEEP
    assert next(v for k, v in e05.items() if "téléphone" in k) == PART_STOP
    assert next(v for k, v in e05.items() if "pas encore signé" in k) == PART_STOP
    assert next(v for k, v in e05.items() if k.startswith("Partition C: de l'ancien")) == PART_DELETE
    e06 = answers("E06")
    assert next(v for k, v in e06.items() if "parce que c'est mieux" in k) == NOT_ACTIVATED
    assert next(v for k, v in e06.items() if "mis au rebut" in k) == NOT_ACTIVATED
    assert next(v for k, v in e06.items() if "désinstallée de l'ancien PC" in k) == ACTIVATES
    e07 = answers("E07")
    assert next(v for k, v in e07.items() if "VMD" in k) == WHEN_BEFORE
    assert next(v for k, v in e07.items() if "BitLocker" in k) == WHEN_BEFORE
    assert next(v for k, v in e07.items() if "Je n'ai pas de clé" in k) == WHEN_DURING
    assert next(v for k, v in e07.items() if "point de restauration" in k) == WHEN_AFTER
    for item in PRACTICE_ITEMS:  # aucune remise en ordre déjà dans l'ordre attendu
        if item.ordering:
            assert list(item.ordering.correct) != list(range(len(item.ordering.steps))), item.key


def test_no_false_technical_claims_anywhere():
    text = _course_text() + " " + _all_items_text().lower()
    for right in ("accord écrit", "sauvegarde vérifiée", "charger un pilote", "« uefi: »", "gpt", "mbr2gpt",
                  "/allowfullos", "espace non alloué", "je n'ai pas de clé", "édition de la licence",
                  "inaccessible_boot_device", "windows boot manager", "id du matériel", "vous êtes à jour",
                  "clé de récupération", "n'est pas une sauvegarde", "documentation de microsoft fait foi",
                  "maj + f10", "ne pas toucher"):
        assert right in text, right
    for wrong in ("désactiver le démarrage sécurisé pour installer", "passer en mode hérité pour installer windows 11",
                  "une licence oem se transfère", "le ssd est en panne", "un point de restauration est une sauvegarde",
                  "supprimer toutes les partitions des deux disques est", "utiliser un activateur pour"):
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


def test_five_resolved_cases_three_procedures_and_exam_not_in_course():
    text = _text(_course_raw())
    for case in ("Cas 1 — Installation propre complète avec migration", "Cas 2 — Stockage non détecté",
                 "Cas 3 — Échec de démarrage", "Cas 4 — Pilotes manquants", "Cas 5 — Partitionnement incorrect"):
        assert case in text, case
    assert text.count("Conclusion rédigée.") == 5
    for i in range(1, 4):
        assert f"Procédure {i} —" in text, i
    course = _course_raw()
    for item in EXAM_ITEMS:
        assert item.context not in course and escape(item.context) not in course, item.key
    for item in PRACTICE_ITEMS:
        assert escape(item.context) in course, item.key


def test_course_teaches_every_mandatory_point():
    titles = [t for t, _ in pr08_course_sections()]
    assert len(titles) == len(set(titles))
    text = _course_text()
    for notion in (
        # préparation
        "inventaire", "numéro de série", "accord écrit", "compatibilité", "version visée", "licence", "oem",
        "licence numérique", "sauvegarde", "copie vérifiée", "confidentiel",
        # média, firmware, démarrage
        "clé usb", "outil de création", "iso", "sha-256", "rufus", "uefi", "démarrage sécurisé", "tpm 2.0",
        "menu de démarrage", "ordre de démarrage", "csm",
        # installateur
        "langue", "clavier", "édition", "personnalisée", "lecteur 0",
        # disque et partitions
        "gpt", "mbr", "esp", "msr", "récupération", "winre", "espace non alloué", "diskpart", "list disk",
        # compte, réseau, mises à jour, pilotes
        "compte microsoft", "compte standard", "réseau", "confidentialité", "windows update", "pilotes",
        "gestionnaire de périphériques", "chipset", "vmd", "rst", "f6",
        # activation, restauration, sécurité, validation
        "activation", "slmgr", "defender", "pare-feu", "bitlocker", "point de restauration",
        "lecteur de récupération", "restauration", "liste de contrôle", "rapport d'intervention",
        # variantes du ticket
        "installation propre", "migration", "mise à niveau", "aucun lecteur", "échec de démarrage",
        "pilotes manquants", "partitionnement incorrect",
        # encadrés
        "objectifs", "procédure professionnelle", "erreur fréquente", "à l'écrit", "repère rapide", "glossaire",
    ):
        assert notion in text, notion


def test_course_flags_requirements_links_and_fictive_supports():
    raw = _course_raw()
    text = _text(raw)
    for req in ("AP-10", "AP-C03"):
        assert req in text
    assert "Compléments pédagogiques" in text and "fictif" in text.lower()
    assert "aucun n'est une question officielle" in text.lower()
    assert "aucun schéma n'est tiré d'une image générée" in text.lower()
    assert "conventions du cours" in text.lower()
    for link in ("/uaa/ampcr-mc07", "/uaa/ampcr-mc08", "/uaa/ampcr-mc09", "/uaa/ampcr-mc10", "/uaa/ampcr-mc12",
                 "/uaa/ampcr-pratique-pr04", "/uaa/ampcr-pratique-pr05", "/uaa/ampcr-pratique-pr06",
                 "/uaa/ampcr-pratique-pr07", "/uaa/ampcr-pratique-pr11", f"/uaa/{PR08_SLUG}/practice",
                 f"/uaa/{PR08_SLUG}/exam"):
        assert link in raw, link
    # PR09, PR10 et PR12 ne sont pas encore publiés : renvoi en texte seulement.
    for unpublished in ("/uaa/ampcr-pratique-pr09", "/uaa/ampcr-pratique-pr10", "/uaa/ampcr-pratique-pr12"):
        assert unpublished not in raw
    anchors = set(re.findall(r'id="(pr08-e\d\d)"', raw))
    assert anchors == {f"pr08-{i.key.lower()}" for i in PRACTICE_ITEMS}
    assert "(#pr08-" not in raw


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(t) for t, _ in pr08_course_sections()]
    assert kinds[:14] == ["theory"] * 14
    assert kinds[14:] == ["example", "warning", "exercise", "exam", "summary", "info"]


# =============================================================================================
# 5. Banque, seed et intégration au moteur
# =============================================================================================


def test_plan_slot_matches_ticket():
    slot = plan.COURSE_SLOTS_BY_CODE["PR08"]
    assert slot.ticket == 208 and slot.title == PR08_TITLE == PRACTICAL_COURSES_BY_CODE["PR08"].title


def test_seed_publishes_pr08_in_practical_module_idempotently(db_session):
    module, uaa = _pr08(db_session)
    assert uaa.slug == SLUG and uaa.is_published and uaa.title == PR08_TITLE and uaa.position == 8
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="PR08").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(pr08_course_sections())
    assert {"PR07", "PR08", "PR11"} <= set(plan.published_uaas(db_session))
    ordered = [u.code for u in sorted(module.uaas, key=lambda u: (u.position, u.id))]
    assert ordered.index("EX01") < ordered.index("PR07") < ordered.index("PR08") < ordered.index("PR11")
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_reserves_and_documents(db_session):
    module, uaa = _pr08(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert import_practical_bank(db_session, module, uaa) == len(PRACTICE_ITEMS) + len(EXAM_ITEMS)
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    usages = [question_usage(q) for q in questions]
    assert usages.count("practice") == len(PRACTICE_ITEMS) and usages.count("exam") == 10


def test_correction_context_is_pr08_specific():
    context = _pedagogical_context_for("PR08")
    assert context is get_practical_context("PR08")
    assert context.course_key == SLUG
    notions = " ".join(context.allowed_notions)
    for notion in ("Charger un pilote", "mbr2gpt", "accord écrit", "INACCESSIBLE_BOOT_DEVICE", "VEN"):
        assert notion in notions, notion
    assert "mot-clé" in context.constraints and "disque cible" in context.constraints


# =============================================================================================
# 6. Pages et sessions
# =============================================================================================


def test_course_page_renders_figures_and_exercises(client, db_session):
    _pr08(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert len(ids) == len(set(ids)) and set(ids) >= {f"fig-{f.key}" for f in PR08_FIGURES}
    assert html.count('class="jc-exercise-card"') == len(PRACTICE_ITEMS)
    assert "<details open" not in html
    assert 'href="/ampcr-pratique"' in html and f"/uaa/{SLUG}/exam" in html
    assert "<table" in html


def test_practical_home_and_matrix_show_pr08(client, db_session):
    _pr08(db_session)
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and re.search(r"\d+ cours publiés sur 30 prévus", _text(home))  # PR09 (#209) publié ensuite
    for req in REQ:
        assert plan.requirement_status(req, {"PR08"}) == plan.STATUS_PARTIAL
    assert plan.VALIDATED_REQUIREMENT_IDS == audit_proven_ids()  # « validé » : preuves de l'audit #235
    assert client.get("/ampcr-pratique/matrice").status_code == 200


@pytest.mark.parametrize("mode", ["practice", "exam"])
def test_sessions_draw_only_from_their_reserve_without_generation(authenticated_client, db_session, monkeypatch, mode):
    fake = _patch_fake_provider(monkeypatch)
    _pr08(db_session)
    assert authenticated_client.get(f"/uaa/{SLUG}/{mode}").status_code == 200
    session_url = _start_session(authenticated_client, db_session, SLUG, mode)
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert {question_usage(sq.question_version.question) for sq in session.session_questions} == {mode}
    assert session.question_count == 10
    assert fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"PR08"}
    if mode == "exam":
        page = authenticated_client.get(f"{session_url}?q=1").text
        assert "Corrigé de référence" not in page and "Barème" not in page


def test_exam_lengths_limited_and_score_on_20(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _pr08(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    from app.v1.models import User

    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="PR08", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "/ 20" in html


def test_practice_sessions_with_classification_and_ordering_submit(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr08(db_session)
    for _ in range(2):  # 16 exercices : deux sessions de 10 couvrent toute la réserve
        session_url = _start_session(authenticated_client, db_session, SLUG, "practice")
        _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
        assert authenticated_client.get(session_url).status_code == 200
