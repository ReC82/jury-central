"""Ticket #231 — AMPCR pratique écrite, EX02 « Examen blanc écrit — installation et dépannage
des systèmes ».

Couvre : données des dossiers **recontrôlées ici** indépendamment (prérequis de Windows 11 et
édition, service désactivé, écran de l'installateur, identifiants de fabricants, comptes,
double démarrage et swap, fstab et noms de disques, permissions en octal, points de
restauration, empreintes SHA-256 recalculées avec `hashlib`) ; schémas (validité,
accessibilité, fichiers statiques identiques au SVG produit) ; questions (10 × 10 points = 100,
réponses libres, 3 dossiers, matière du ticket, exigences de l'emplacement, pas de question
d'acronyme) ; sujet (version candidat sans corrigé, lignes de réponse imprimables, barème
global) ; banque, seed, navigation (pas d'entraînement), session d'examen (corrigé masqué avant
remise, schémas dans leurs questions, note sur 100) ; EX01 et les cours PR inchangés.
Aucun appel IA réel : `FakeAIProvider` partout."""

import hashlib
import re

from app.models import UAA, Module
from app.seed import seed
from app.v1 import ampcr_pratique_plan as plan
from app.v1.ampcr_pratique_bank import (
    PRACTICAL_BANK_IMPORTERS,
    PRACTICAL_COURSES_BY_CODE,
    _document_layout,
    get_practical_context,
    import_practical_bank,
    is_practical_exam_code,
    item_content,
    question_usage,
)
from app.v1.ampcr_pratique_ex02_bank import (
    ALL_ITEMS,
    DOSSIER_A,
    DOSSIER_B,
    DOSSIER_C,
    DOSSIER_DOCUMENTS,
    EXAM_ITEMS,
    EXAM_TOTAL_POINTS,
    ITEM_COURSES,
    ITEM_PARTS,
    PRACTICE_ITEMS,
    validate_items,
)
from app.v1.ampcr_pratique_ex02_course import (
    EX02_SLUG,
    EX02_TITLE,
    METHOD_LADDER_FIGURE,
    ex02_course_sections,
)
from app.v1.ampcr_pratique_ex02_figures import (
    BACKUP_HASHES,
    BACKUP_SET,
    BAD_COPIES,
    CUPS_FIX,
    CUPS_SCREEN,
    DATA_UUID,
    DEVICE_FIRST_ACTION,
    DEVICE_VENDORS,
    DUAL_BOOT_ACTIONS,
    DUAL_BOOT_ACTIONS_WITHOUT_BACKUP,
    DUAL_BOOT_SWAP_GB,
    DUAL_BOOT_SWAP_HIBERNATION_GB,
    EMERGENCY_SCREEN,
    EX02_FIGURES,
    FSTAB_BAD_LINE,
    FSTAB_FIXED_LINE,
    INSTALL_HERE,
    INSTALLER_ACTIONS,
    INSTALLER_SCREEN,
    LSBLK_SCREEN,
    PERMISSIONS_SCREEN,
    RESTORE_POINT_TO_USE,
    SCREEN_WIDTH,
    SCREENS,
    SHARE_DIR_OCTAL,
    SHARE_FILE_OCTAL,
    STAFF_ACCOUNTS,
    STATIC_FIGURES,
    STATION_CHECKS,
    STATION_EDITIONS,
    STATIONS,
    STOP_SCREEN,
    access,
    static_svg,
)
from app.v1.ampcr_pratique_visuals import render_figure, validate_figure
from app.v1.assets import STATIC_DIR
from app.v1.models import Question, QuestionnaireSession, SessionMode, User
from app.v1.question_engine import validate_content
from app.v1.session_service import _pedagogical_context_for, available_session_lengths
from tests.test_ticket94_french_fr06_10 import (
    _answer_all_and_submit,
    _patch_fake_provider,
    _start_session,
)

SLUG = "ampcr-pratique-ex02"
MODULE_COURSES = {"PR07", "PR08", "PR09", "PR10", "PR11", "PR12"}


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _subject_raw() -> str:
    return " ".join(c for _t, c in ex02_course_sections())


def _item(key: str):
    return next(i for i in EXAM_ITEMS if i.key == key)


def _expected(key: str) -> str:
    item = _item(key)
    return " ".join(c.expected for c in item.criteria) + " " + " ".join(item.correction)


def _items_text() -> str:
    return " ".join(
        " ".join((i.title, i.context, *i.instructions, *i.correction, *(c.expected for c in i.criteria),
                  *(d.content_text for d in i.documents)))
        for i in EXAM_ITEMS
    ).lower()


def _ex02(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "EX02")
    return module, uaa


# =============================================================================================
# 1. Données des dossiers, recontrôlées indépendamment
# =============================================================================================


def test_windows11_verdicts_and_editions():
    s1, s2, s3 = STATIONS
    # Poste 1 : tout est là, mais en mode hérité + MBR + TPM désactivé → réglages, dans l'ordre.
    verdict, blockers, settings = STATION_CHECKS[s1.name]
    assert verdict == "Compatible après réglages du firmware" and blockers == ()
    assert "mbr2gpt" in settings[0] and "UEFI" in settings[1] and "TPM" in settings[2]
    # Poste 2 : processeur hors liste et TPM 1.2 → aucun réglage ne suffit.
    assert not s2.spec.cpu_listed and s2.spec.tpm_version == 1.2
    assert STATION_CHECKS[s2.name][0] == "Non compatible (matériel)" and len(STATION_CHECKS[s2.name][1]) == 2
    assert STATION_CHECKS[s3.name] == ("Compatible tel quel", (), ())
    # BitLocker + hôte Bureau à distance → Professionnel ; usage courant → Famille.
    assert STATION_EDITIONS[s3.name] == "Windows 11 Professionnel"
    assert STATION_EDITIONS[s1.name] == "Windows 11 Famille"
    expected = _expected("X01")
    assert "14 octobre 2025" in expected and "AVANT" in expected and "Confirm-SecureBootUEFI" in expected
    assert "ChromeOS Flex" in expected and "Linux" in expected


def test_cups_service_disabled_and_fix():
    screen = "\n".join(CUPS_SCREEN)
    assert "disabled; preset: enabled" in screen and "inactive (dead)" in screen
    assert CUPS_FIX == "Activer au démarrage et démarrer"
    assert "sudo systemctl enable --now cups" in _expected("X02")


def test_installer_screen_and_partition_choices():
    screen = "\n".join(INSTALLER_SCREEN)
    assert "Disque 2 Espace non alloué" in screen and "931,5 Go" in screen
    # 1 To (≈ 1,0002 × 10^12 octets) ≈ 931,5 Gio ; 2 To ≈ 1863,0 Gio.
    assert round(1_000_204_886_016 / 2**30, 1) == 931.5 and round(2_000_398_934_016 / 2**30, 1) == 1863.0
    targets = [name for name, action in INSTALLER_ACTIONS.items() if action == INSTALL_HERE]
    assert targets == ["Disque 2 Espace non alloué"]
    assert all(action == "Ne pas toucher" for name, action in INSTALLER_ACTIONS.items() if name not in targets)
    expected = _expected("X03")
    for needle in ("ESP", "FAT32", "MSR", "NTFS", "Récupération", "GPT", "Mode BIOS : UEFI", "débrancher"):
        assert needle in expected, needle


def test_drivers_vendors_and_actions():
    assert DEVICE_VENDORS == {
        "Contrôleur Ethernet": "Realtek",
        "Périphérique inconnu": "Brother",
        "Carte graphique de base Microsoft": "NVIDIA",
    }
    assert set(DEVICE_FIRST_ACTION.values()) == {"Installer le bon pilote"}
    expected = _expected("X04")
    assert "autre PC" in expected and "point de restauration" in expected.lower() and "driver booster" in expected


def test_accounts_least_privilege():
    assert STAFF_ACCOUNTS["Thomas"] == "Compte administrateur nominatif"
    assert [a for p, a in STAFF_ACCOUNTS.items() if p != "Thomas"] == ["Compte standard (utilisateur)"] * 4
    expected = _expected("X05")
    assert "net user karim * /add" in expected and "net localgroup Administrateurs thomas /add" in expected
    assert "groupe de travail" in expected and "contrôleur de domaine" in expected


def test_dual_boot_actions_and_swap():
    assert DUAL_BOOT_ACTIONS == {
        "esp": "Réutiliser sans formater (/boot/efi)",
        "msr": "Ne pas toucher",
        "windows": "Ne pas toucher",
        "recovery": "Ne pas toucher",
        "free": "Créer les partitions de Linux",
    }
    assert set(DUAL_BOOT_ACTIONS_WITHOUT_BACKUP.values()) == {"Arrêter : sauvegarde et accord d'abord"}
    # Repère du cours (PR09) : 8 Go de mémoire → 8 Go sans hibernation, 16 Go avec.
    assert (DUAL_BOOT_SWAP_GB, DUAL_BOOT_SWAP_HIBERNATION_GB) == (8, 16)
    expected = _expected("X06")
    assert "BitLocker" in expected and "démarrage rapide" in expected and "sans formatage" in expected


def test_fstab_device_name_changed():
    emergency = "\n".join(EMERGENCY_SCREEN)
    assert "dev-sdb1.device" in emergency and "local-fs.target" in emergency and "emergency mode" in emergency
    lsblk = "\n".join(LSBLK_SCREEN)
    # Le disque neuf « sdb » n'a aucune partition (pas de sdb1) ; les données sont sur sdc1.
    assert "sdb    931.5G\n" in lsblk + "\n" and "sdb1" not in lsblk.replace(FSTAB_BAD_LINE, "")
    assert "└─sdc1   1.8T ext4   PARTAGE" in lsblk and DATA_UUID in lsblk
    assert FSTAB_BAD_LINE.startswith("/dev/sdb1") and FSTAB_FIXED_LINE.startswith(f"UUID={DATA_UUID}")
    assert "nofail" in FSTAB_FIXED_LINE and re.fullmatch(r"[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}", DATA_UUID)
    assert "findmnt --verify" in _expected("X07")


def test_permissions_recomputed():
    assert (SHARE_DIR_OCTAL, SHARE_FILE_OCTAL) == ("770", "640")
    # Lucie hors du groupe : « autres » --- ; Marc dans le groupe : lecture seule ; Jean propriétaire.
    assert not access("lucie", ("drwxrwx---", "jean", "benevoles", ""), "x")
    assert access("marc", ("-rw-r-----", "jean", "benevoles", ""), "r")
    assert not access("marc", ("-rw-r-----", "jean", "benevoles", ""), "w")
    assert access("marc", ("-rw-rw----", "jean", "benevoles", ""), "w")
    screen = "\n".join(PERMISSIONS_SCREEN)
    assert "Permission denied" in screen and "lucie is not in the sudoers file." in screen
    assert "groups=1002(lucie)" in screen and "1001(benevoles)" in screen
    expected = _expected("X08")
    assert "sudo usermod -aG benevoles lucie" in expected and "chmod g+w" in expected and "777" in expected


def test_boot_failure_and_restore_point():
    stop = "\n".join(STOP_SCREEN)
    assert "SYSTEM_THREAD_EXCEPTION_NOT_HANDLED" in stop and "gfxdrv64.sys" in stop
    assert RESTORE_POINT_TO_USE[0].startswith("26/10/2026 18:41")
    expected = _expected("X09")
    assert "mode sans échec" in expected and "Restaurer le pilote" in expected and "Restauration du système" in expected


def test_backup_hashes_recomputed_with_hashlib():
    for f, (name, original, copy) in zip(BACKUP_SET, BACKUP_HASHES, strict=True):
        assert name == f.name and len(original) == 64
        assert original == hashlib.sha256(f.original).hexdigest() and copy == hashlib.sha256(f.copy).hexdigest()
    assert BAD_COPIES == ("photos-biens.zip",)
    expected = _expected("X10")
    assert "Get-FileHash" in expected and "Conserver mes fichiers" in expected and "Windows Update" in expected


def test_screens_fit_the_width():
    for name, lines in SCREENS.items():
        assert all(len(line) <= SCREEN_WIDTH for line in lines), name


# =============================================================================================
# 2. Schémas
# =============================================================================================


def test_figures_valid_accessible_and_unique():
    figures = (*EX02_FIGURES, METHOD_LADDER_FIGURE)
    assert len({f.key for f in figures}) == len(figures) == 4
    for figure in figures:
        assert validate_figure(figure) == []
        html = str(render_figure(figure))
        assert 'role="img"' in html and "schéma non officiel" in html


def test_static_figure_files_are_the_generated_svg():
    assert len(STATIC_FIGURES) == 3
    for figure, path in STATIC_FIGURES:
        content = (STATIC_DIR / path).read_text()
        assert content == static_svg(figure)
        assert content.startswith("<svg ") and "xmlns=" in content and "<title>" in content


def test_schema_documents_point_to_static_files():
    images = {d.image for i in EXAM_ITEMS for d in i.documents if d.image}
    assert images == {path for _f, path in STATIC_FIGURES}
    x06 = _item("X06")
    layout = _document_layout(next(d for d in x06.documents if d.image))
    assert layout["kind"] == "figure" and layout["src"] == "/static/img/ampcr-pratique/ex02-partitions-double-demarrage.svg"
    assert "175 Go" in layout["alt"] and "non officiel" in layout["notice"]


# =============================================================================================
# 3. Questions
# =============================================================================================


def test_items_valid_and_scored_on_100():
    assert validate_items() == []
    assert len(EXAM_ITEMS) == 10 and ALL_ITEMS == EXAM_ITEMS and PRACTICE_ITEMS == ()
    assert all(i.usage == "exam" and i.total_points == 10 for i in EXAM_ITEMS)
    assert sum(i.total_points for i in EXAM_ITEMS) == EXAM_TOTAL_POINTS == 100
    assert all(i.question_type in ("long_answer", "document_analysis") for i in EXAM_ITEMS)
    assert [i.key for i in EXAM_ITEMS] == [f"X{n:02d}" for n in range(1, 11)]
    for item in EXAM_ITEMS:
        assert len(item.criteria) >= 3 and len(item.correction) >= 3
        # PR05 (partitions et formatage, module 1) est un renvoi de révision utile pour X03 et X06.
        assert set(ITEM_COURSES[item.key]) <= MODULE_COURSES | {"PR05"}
    assert {c for codes in ITEM_COURSES.values() for c in codes} >= MODULE_COURSES


def test_three_dossiers_with_documents():
    for dossier in (DOSSIER_A, DOSSIER_B, DOSSIER_C):
        assert len(DOSSIER_DOCUMENTS[dossier]) >= 5
        items = [i for i in EXAM_ITEMS if ITEM_PARTS[i.key] == dossier]
        assert len(items) >= 2 and all(i.documents for i in items)
        used = {d.title for i in items for d in i.documents}
        assert used == {d.title for d in DOSSIER_DOCUMENTS[dossier]}  # chaque document sert


def test_ticket_subjects_are_all_evaluated():
    text = _items_text()
    for needle in (
        "windows 11", "édition", "prérequis", "linux", "ubuntu", "debian", "uefi", "gpt", "partition système efi",
        "partition", "format", "pilote", "compte", "groupe", "domaine", "ligne de commande", "systemctl",
        "service", "écran d'arrêt", "winre", "mode d'urgence", "permission", "restauration", "sauvegarde",
        "accord écrit", "vérif",
    ):
        assert needle in text, needle


def test_items_cover_the_slot_requirements():
    slot = plan.EXERCISE_SLOTS_BY_CODE["EX02"]
    assert slot.ticket == 231 and slot.title == EX02_TITLE == PRACTICAL_COURSES_BY_CODE["EX02"].title
    covered = {r for i in EXAM_ITEMS for r in i.requirement_ids}
    assert set(slot.requirement_ids) <= covered
    assert covered <= set(plan.REQUIREMENTS_BY_ID)


def test_no_acronym_question_and_no_official_claim():
    for item in EXAM_ITEMS:
        prompt = item.prompt.lower()
        assert "que signifie" not in prompt and "développe" not in prompt
        assert "officiel" not in item.title.lower()
    text = _items_text()
    for wrong in ("formater l'esp", "chmod 777 suffit", "désactiver le démarrage sécurisé pour installer"):
        assert wrong not in text


def test_items_content_matches_existing_question_types():
    for item in EXAM_ITEMS:
        ids = list(range(1, len(item.documents) + 1))
        content = item_content(item, ids)
        validate_content(item.question_type, 1, content)
        assert "Barème" in content["rubric"] and content["max_score"] == 10


# =============================================================================================
# 4. Sujet (version candidat)
# =============================================================================================


def test_subject_has_questions_without_corrections():
    raw = _subject_raw()
    for number, item in enumerate(EXAM_ITEMS, start=1):
        assert f"Question {number} — " in raw
        for step in item.correction:
            assert step[:60] not in raw
        for criterion in item.criteria:
            assert criterion.expected[:60] not in raw
    assert raw.count('class="jc-ex-answer"') == 10 and raw.count('class="jc-ex-dossier"') == 3
    assert "Corrigé de référence" not in raw and "<details" not in raw


def test_subject_presents_scoring_and_sources():
    text = _text(_subject_raw()).replace("**", "")
    assert "10 questions à réponse rédigée" in text and "sur 100" in text
    assert "pas la durée officielle" in text and "fictifs" in text
    assert "/uaa/ampcr-pratique-ex02/exam" in text and "Ctrl + P" in text
    for code in plan.EXERCISE_SLOTS_BY_CODE["EX02"].requirement_ids:
        assert code in text
    for code in MODULE_COURSES:
        assert f"/uaa/ampcr-pratique-{code.lower()}" in text


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(title) for title, _c in ex02_course_sections()]
    assert kinds == ["theory", "theory", "theory", "theory", "theory", "method", "info"]


# =============================================================================================
# 5. Banque, seed, pages, sessions
# =============================================================================================


def test_seed_publishes_ex02_after_pr12_idempotently(db_session):
    module, uaa = _ex02(db_session)
    assert uaa.slug == SLUG == EX02_SLUG and uaa.is_published and uaa.title == EX02_TITLE
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="EX02").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(ex02_course_sections())
    from app.v1.parcours import listed_uaas

    codes = [u.code for u in listed_uaas(db_session.get(Module, module.id))]
    assert codes.index("EX02") == codes.index("PR12") + 1
    assert codes.index("EX01") == codes.index("PR06") + 1  # EX01 inchangé
    assert {"EX01", "EX02"} <= set(plan.published_uaas(db_session))
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_exam_reserve_only(db_session):
    module, uaa = _ex02(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert is_practical_exam_code("EX02") and not is_practical_exam_code("PR12")
    assert import_practical_bank(db_session, module, uaa) == 10
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    assert [question_usage(q) for q in questions] == ["exam"] * 10


def test_correction_context_is_ex02_specific():
    context = _pedagogical_context_for("EX02")
    assert context is get_practical_context("EX02") and context.course_key == SLUG
    assert context is not get_practical_context("EX01")
    notions = " ".join(context.allowed_notions)
    assert "mbr2gpt" in notions and "nofail" in notions and "chmod" in notions and "SHA-256" in notions
    assert "/100" in context.level and "mot-clé" in context.constraints


def test_subject_page_navigation_and_home(client, db_session):
    _ex02(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    assert "Sujet" in html and f'href="/uaa/{SLUG}/practice"' not in html and f"/uaa/{SLUG}/exam" in html
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert set(ids) >= {f"fig-{f.key}" for f in (*EX02_FIGURES, METHOD_LADDER_FIGURE)}
    assert html.count('class="jc-ex-question"') == 10
    assert "examen blanc EX02" in html
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and re.search(r"\d+ cours publiés sur 30 prévus\s+· 2 examens blancs sur 6", home)
    assert client.get("/ampcr-pratique/matrice").status_code == 200
    pr12 = client.get("/uaa/ampcr-pratique-pr12").text
    assert 'href="/uaa/ampcr-pratique-pr12/practice"' in pr12


def test_practice_redirects_to_exam(authenticated_client, db_session):
    _ex02(db_session)
    response = authenticated_client.get(f"/uaa/{SLUG}/practice", follow_redirects=False)
    assert response.status_code == 303 and response.headers["location"] == f"/uaa/{SLUG}/exam"
    assert db_session.query(QuestionnaireSession).count() == 0


def test_exam_session_hides_corrections_and_scores_on_100(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _ex02(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="EX02", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert session.question_count == 10 and fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"EX02"}
    shown = set()
    for position in range(1, 11):
        page = authenticated_client.get(f"{session_url}?q={position}").text
        assert "Corrigé de référence" not in page and "Barème" not in page
        shown |= {path for _f, path in STATIC_FIGURES if path in page}
    assert shown == {path for _f, path in STATIC_FIGURES}  # les trois schémas dans leurs questions
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-100" in html and "/ 100" in html and "data-score-on-20" in html
