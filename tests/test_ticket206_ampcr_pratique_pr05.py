"""Ticket #206 — AMPCR pratique écrite, PR05 « Stockage, partitions, formatage et
défragmentation ».

Couvre : données de référence **recontrôlées ici** indépendamment (unités Go/Gio, limite MBR,
choix MBR/GPT, systèmes de fichiers et limite FAT32, plans de partitions, entretien HDD/SSD,
lecture SMART et câble, cohérence mode de démarrage/table, cinq procédures) ; schémas SVG
(validité, accessibilité, étapes et partitions cohérentes avec les données) ; exercices et
mini-examen (format du socle, remises en ordre et classements auto-corrigés, calculs, pas de
question d'acronyme, contexte complet) ; cours (matière du ticket, 5 procédures, 4 cas résolus,
affirmations techniques justes, supports fictifs, cartes) ; banque, seed, pages et sessions.
Aucun appel IA réel : `FakeAIProvider` partout."""

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
from app.v1.ampcr_pratique_pr05_bank import (
    E04_CATEGORIES,
    E05_BOTH,
    E05_CATEGORIES,
    E05_HDD,
    E05_SSD,
    E06_CATEGORIES,
    E07_HDD_GIB,
    E07_SSD_GIB,
    E08_C_GIB,
    E08_D_MIB,
    E09_HOME_GIB,
    E12_DEFRAG,
    E13_CABLE,
    E13_VERDICT,
    E15_OK_AFTER,
    E15_OK_BEFORE,
    EXAM_ITEMS,
    EXAM_TOTAL_POINTS,
    KIND_CALC,
    KIND_CHOICE,
    KIND_DIAG,
    KIND_ERROR,
    KIND_ORDER,
    PRACTICE_ITEMS,
    REQ,
    X04_LOST_GIB,
    X04_MBR_GIB,
    X06_CABLE,
    X06_VERDICT,
    X09_CABLE,
    X09_VERDICT,
    validate_items,
)
from app.v1.ampcr_pratique_pr05_course import PR05_SLUG, PR05_TITLE, pr05_course_sections
from app.v1.ampcr_pratique_pr05_figures import (
    CASE1_GIB,
    CASE1_SCREEN,
    CASE4_C_GIB,
    CASE4_FIGURE,
    CASE4_HDD_PLAN,
    CASE4_SSD_PLAN,
    FAT32_MAX_FILE,
    FILESYSTEMS_BY_NAME,
    FS_EXFAT,
    FS_EXT4,
    FS_FAT32,
    FS_NTFS,
    LINUX_NEW_DISK_STEPS,
    LINUX_UEFI_PLAN,
    LSBLK_SCREEN,
    MBR_LIMIT_BYTES,
    MEDIA,
    MEDIA_HDD,
    MEDIA_NVME_SSD,
    MEDIA_SATA_SSD,
    MISSING_TREE,
    NOT_DETECTED_STEPS,
    OPT_DEFRAG,
    OPT_TRIM,
    OPTIMISE_SCREEN,
    OPTIMISE_STEPS,
    PLANS,
    PLANS_FIGURE,
    PR05_FIGURES,
    PROCEDURES,
    SAFE_STEPS,
    SCREEN_WIDTH,
    SMART_OK,
    SMART_REPLACE,
    SMART_WATCH,
    SYMPTOMS_BY_KEY,
    TABLE_GPT,
    TABLE_MBR,
    USE_ESP,
    USE_LEGACY_DEVICE,
    USE_LINUX,
    USE_SHARED_REMOVABLE,
    USE_WINDOWS_DATA,
    USE_WINDOWS_SYSTEM,
    WIN_NEW_DISK_STEPS,
    WINDOWS_BIOS_PLAN,
    WINDOWS_UEFI_PLAN,
    boot_mode_consistent,
    clusters_used,
    filesystem_for,
    fits_on_fat32,
    gb_to_gib,
    mbr_usable_bytes,
    needs_defrag,
    optimisation_for,
    partition_table_choice,
    plan_fits,
    smart_reading,
    tb_to_tib,
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

SLUG = "ampcr-pratique-pr05"


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _course_raw() -> str:
    return " ".join(c for _t, c in pr05_course_sections())


def _course_text() -> str:
    return _text(_course_raw()).replace("**", "").replace("`", "").lower()


def _all_items_text() -> str:
    return " ".join(
        " ".join((i.title, i.context, *i.instructions, *i.correction, *(c.expected for c in i.criteria),
                  *(d.content_text for d in i.documents)))
        for i in PRACTICE_ITEMS + EXAM_ITEMS
    )


def _pr05(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "PR05")
    return module, uaa


# =============================================================================================
# 1. Données de référence, recontrôlées indépendamment
# =============================================================================================


def test_units_and_capacity_calculations():
    # 10^12 / 2^30 = 931,32… ; 500 × 10^9 / 2^30 = 465,66… ; 2 × 10^12 / 2^30 = 1862,64…
    assert gb_to_gib(1000) == pytest.approx(931.32, abs=0.01) == E07_HDD_GIB
    assert gb_to_gib(500) == pytest.approx(465.66, abs=0.01) == E07_SSD_GIB
    assert gb_to_gib(2000) == pytest.approx(1862.65, abs=0.01) == CASE1_GIB
    assert tb_to_tib(2) == pytest.approx(1.82, abs=0.01)
    assert "1862,65 Go" in " ".join(CASE1_SCREEN) and "Non initialisé" in " ".join(CASE1_SCREEN)
    # Plans chiffrés : D: 300 Gio = 307 200 Mio ; C: = 931,32 − (100 + 16 + 750 + 307 200) / 1024.
    assert E08_D_MIB == 307_200
    assert E08_C_GIB == pytest.approx(931.32 - (100 + 16 + 750 + 307_200) / 1024, abs=0.02)
    assert E09_HOME_GIB == pytest.approx(238.42 - 0.5 - 50 - 4, abs=0.02)
    assert CASE4_C_GIB == pytest.approx(465.66 - 866 / 1024, abs=0.02)
    with pytest.raises(ValueError):
        plan_fits(1.0, (2048,))
    # Clusters : un fichier occupe des clusters entiers.
    assert clusters_used(1) == 1 and clusters_used(4096) == 1 and clusters_used(4097) == 2 and clusters_used(0) == 0


def test_partition_tables_mbr_limit_and_choice():
    assert MBR_LIMIT_BYTES == 2**41 and X04_MBR_GIB == 2048
    assert mbr_usable_bytes(3 * 10**12) == 2**41 and mbr_usable_bytes(500 * 10**9) == 500 * 10**9
    assert X04_LOST_GIB == pytest.approx(3e12 / 2**30 - 2048, abs=0.01)
    assert partition_table_choice(disk_bytes=500 * 10**9, boots_os=True, firmware_uefi=False) == TABLE_MBR
    assert partition_table_choice(disk_bytes=500 * 10**9, boots_os=True, firmware_uefi=True) == TABLE_GPT
    assert partition_table_choice(disk_bytes=4 * 10**12, boots_os=False, firmware_uefi=False) == TABLE_GPT
    with pytest.raises(ValueError):
        partition_table_choice(disk_bytes=3 * 10**12, boots_os=True, firmware_uefi=False)
    assert boot_mode_consistent(TABLE_GPT, "UEFI") and boot_mode_consistent(TABLE_MBR, "BIOS")
    assert not boot_mode_consistent(TABLE_GPT, "BIOS") and not boot_mode_consistent(TABLE_MBR, "UEFI")
    assert E15_OK_BEFORE and not E15_OK_AFTER


def test_filesystems_and_choice_by_use():
    assert FAT32_MAX_FILE == 4 * 2**30 - 1
    assert fits_on_fat32(FAT32_MAX_FILE) and not fits_on_fat32(4 * 2**30) and not fits_on_fat32(6 * 10**9)
    assert filesystem_for(USE_WINDOWS_SYSTEM) == filesystem_for(USE_WINDOWS_DATA) == FS_NTFS
    assert filesystem_for(USE_LINUX) == FS_EXT4 and filesystem_for(USE_ESP) == FS_FAT32
    assert filesystem_for(USE_SHARED_REMOVABLE, largest_file_bytes=8 * 10**9) == FS_EXFAT
    assert filesystem_for(USE_LEGACY_DEVICE, largest_file_bytes=10**6) == FS_FAT32
    with pytest.raises(ValueError):
        filesystem_for(USE_LEGACY_DEVICE, largest_file_bytes=6 * 10**9)
    fs = FILESYSTEMS_BY_NAME
    assert fs[FS_NTFS].journal and fs[FS_NTFS].permissions and fs[FS_NTFS].macos == "lecture seule"
    assert fs[FS_EXT4].journal and fs[FS_EXT4].permissions and "non lu" in fs[FS_EXT4].windows
    assert not fs[FS_EXFAT].permissions and not fs[FS_FAT32].journal
    assert fs[FS_EXFAT].macos == fs[FS_EXFAT].windows == "lecture et écriture"


def test_exact_partition_plans():
    assert [table for _t, table, _fw, _p in PLANS] == [TABLE_GPT, TABLE_MBR, TABLE_GPT]
    assert [(p.name, p.filesystem, p.size_mib) for p in WINDOWS_UEFI_PLAN] == [
        ("EFI (ESP)", FS_FAT32, 100), ("MSR", "aucun", 16), ("C: Windows", FS_NTFS, None), ("Récupération", FS_NTFS, 750),
    ]
    assert WINDOWS_BIOS_PLAN[0].name == "Réservé au système" and "active" in WINDOWS_BIOS_PLAN[0].role
    assert LINUX_UEFI_PLAN[0].filesystem == FS_FAT32 and "/boot/efi" in LINUX_UEFI_PLAN[0].role
    assert LINUX_UEFI_PLAN[1].filesystem == FS_EXT4
    # Tout plan UEFI commence par l'ESP en FAT32 ; le plan BIOS n'en a pas.
    for _t, table, firmware, partitions in PLANS:
        has_esp = partitions[0].filesystem == FS_FAT32 and "ESP" in partitions[0].name
        assert has_esp is (firmware == "UEFI") and boot_mode_consistent(table, firmware)
    assert [p.key for p in CASE4_SSD_PLAN] == [p.key for p in WINDOWS_UEFI_PLAN]
    assert "464,8" in CASE4_SSD_PLAN[2].size_label and CASE4_HDD_PLAN[0].filesystem == FS_NTFS


def test_optimisation_smart_and_symptoms():
    assert optimisation_for(MEDIA_HDD) == OPT_DEFRAG
    assert optimisation_for(MEDIA_SATA_SSD) == optimisation_for(MEDIA_NVME_SSD) == OPT_TRIM
    assert "jamais de défragmentation" in OPT_TRIM
    with pytest.raises(ValueError):
        optimisation_for("disquette")
    assert needs_defrag(MEDIA_HDD, 27) and not needs_defrag(MEDIA_HDD, 4) and not needs_defrag(MEDIA_NVME_SSD, 60)
    assert E12_DEFRAG == ("E:",)
    assert (E13_VERDICT, E13_CABLE) == (SMART_REPLACE, False)
    assert (X06_VERDICT, X06_CABLE) == (SMART_OK, True)  # erreurs CRC : câble, pas les plateaux
    assert (X09_VERDICT, X09_CABLE) == (SMART_WATCH, False)
    assert smart_reading({"UDMA_CRC_Error_Count": 0})[1] is False
    raw = SYMPTOMS_BY_KEY["raw"]
    assert "Refuser le formatage" in raw.first_action and "formatage" in raw.never
    assert "ne rien initialiser" in SYMPTOMS_BY_KEY["non-initialise"].first_action
    assert "matériel" in SYMPTOMS_BY_KEY["absent-uefi"].never
    assert "C:\\Windows" in SYMPTOMS_BY_KEY["plein"].never
    assert set(MEDIA) == {MEDIA_HDD, MEDIA_SATA_SSD, MEDIA_NVME_SSD}
    for screen in (CASE1_SCREEN, LSBLK_SCREEN, OPTIMISE_SCREEN):
        assert max(len(line) for line in screen) <= SCREEN_WIDTH


def test_procedures_order():
    assert len(PROCEDURES) == 5
    labels = [label for label, _d in SAFE_STEPS]
    assert labels.index("Identifier le disque") < labels.index("Lire l'état SMART") < labels.index("Sauvegarder")
    assert labels.index("Sauvegarder") < labels.index("Vérifier la copie") < labels.index("Agir") < labels.index("Contrôler")
    win = [label for label, _d in WIN_NEW_DISK_STEPS]
    assert win.index("Vérifier l'UEFI") < win.index("Initialiser en GPT") < win.index("Nouveau volume simple") < win.index("Formater")
    linux = " ".join(d for _l, d in LINUX_NEW_DISK_STEPS)
    for command in ("lsblk -f", "mklabel gpt", "mkpart", "mkfs.ext4", "mount", "blkid", "/etc/fstab", "mount -a", "df -h"):
        assert command in linux, command
    assert linux.index("lsblk") < linux.index("mklabel") < linux.index("mkfs.ext4") < linux.index("fstab")
    assert "jamais de défragmentation" in OPTIMISE_STEPS[3][1]
    assert "hors tension" in NOT_DETECTED_STEPS[1][1]
    assert "Disque neuf" in MISSING_TREE[2][1] and "RAW" in MISSING_TREE[3][1]


# =============================================================================================
# 2. Schémas
# =============================================================================================


def test_figures_valid_accessible_and_unique():
    keys = [f.key for f in PR05_FIGURES]
    assert len(keys) == len(set(keys)) == 11
    for figure in PR05_FIGURES:
        assert validate_figure(figure) == [], figure.key
        html = str(render_figure(figure))
        assert 'role="img"' in html and "(schéma non officiel)" in html and not figure.official


def test_figures_drawn_from_data():
    by_key = {f.key: f for f in PR05_FIGURES}
    for key, steps in (("pr05-avant-operation", SAFE_STEPS), ("pr05-disque-windows", WIN_NEW_DISK_STEPS),
                       ("pr05-disque-linux", LINUX_NEW_DISK_STEPS), ("pr05-optimiser", OPTIMISE_STEPS),
                       ("pr05-disque-non-detecte", NOT_DETECTED_STEPS)):
        svg = by_key[key].svg
        for index, (label, _detail) in enumerate(steps, start=1):
            assert f"{index}. {escape(label)}" in svg, (key, label)
    partitions = re.findall(r'data-partition="([^"]+)"', PLANS_FIGURE.svg)
    assert partitions == [p.key for _t, _tab, _fw, plan_ in PLANS for p in plan_]
    for _t, table, _fw, plan_ in PLANS:
        assert f"table {table}" in PLANS_FIGURE.svg
        for p in plan_:
            assert escape(p.size_label) in PLANS_FIGURE.svg and p.name in PLANS_FIGURE.alt
    assert re.findall(r'data-partition="([^"]+)"', CASE4_FIGURE.svg) == ["esp", "msr", "c", "winre", "d"]
    assert by_key["pr05-disque-invisible"].svg.count("data-step=") == len(MISSING_TREE) == 4


# =============================================================================================
# 3. Exercices et mini-examen
# =============================================================================================


def test_items_valid_and_counts_match_ticket():
    assert validate_items() == []
    assert len(PRACTICE_ITEMS) >= 16 and len(EXAM_ITEMS) == 10
    assert sum(i.total_points for i in EXAM_ITEMS) == EXAM_TOTAL_POINTS == 20
    kinds = [i.kind for i in PRACTICE_ITEMS]
    for kind, minimum in ((KIND_ORDER, 3), (KIND_CHOICE, 4), (KIND_DIAG, 4), (KIND_CALC, 1), (KIND_ERROR, 1)):
        assert kinds.count(kind) >= minimum, kind
    keys = [i.key for i in PRACTICE_ITEMS + EXAM_ITEMS]
    assert len(keys) == len(set(keys))
    covered = {r for i in PRACTICE_ITEMS + EXAM_ITEMS for r in i.requirement_ids}
    assert REQ <= covered and "AP-C03" in covered
    assert set(plan.COURSE_SLOTS_BY_CODE["PR05"].requirement_ids) == REQ
    # Le ticket demande des exercices de choix de système de fichiers et de plans de partitions.
    titles = " ".join(i.title for i in PRACTICE_ITEMS).lower()
    assert "système de fichiers" in titles and titles.count("plan de partitions") >= 2


def test_auto_corrected_answers():
    by_key = {i.key: i for i in PRACTICE_ITEMS}

    def ordered(key: str) -> list[str]:
        o = by_key[key].ordering
        return [o.steps[i].split(" — ")[0] for i in o.correct]

    assert ordered("E01") == [label for label, _d in SAFE_STEPS]
    assert ordered("E02") == [label for label, _d in WIN_NEW_DISK_STEPS]
    assert ordered("E03") == [label for label, _d in LINUX_NEW_DISK_STEPS]

    def answers(key: str, categories: tuple[str, ...]) -> dict[str, str]:
        c = by_key[key].classification
        return dict(zip(c.elements, (categories[i] for i in c.correct), strict=True))

    e04 = answers("E04", E04_CATEGORIES)
    assert next(v for k, v in e04.items() if "vidéos de 6 Go" in k) == FS_EXFAT
    assert next(v for k, v in e04.items() if "Partition EFI" in k) == FS_FAT32
    assert next(v for k, v in e04.items() if "firmware" in k) == FS_FAT32
    assert next(v for k, v in e04.items() if "Windows 11" in k) == FS_NTFS
    assert sorted(e04.values()) == sorted([FS_NTFS, FS_NTFS, FS_FAT32, FS_FAT32, FS_EXFAT, FS_EXFAT, FS_EXT4, FS_EXT4])
    e05 = answers("E05", E05_CATEGORIES)
    assert next(v for k, v in e05.items() if "défragmentation" in k) == E05_HDD
    assert next(v for k, v in e05.items() if "TRIM" in k) == E05_SSD
    assert next(v for k, v in e05.items() if "SMART" in k) == E05_BOTH
    e06 = answers("E06", E06_CATEGORIES)
    mbr = {k for k, v in e06.items() if v == TABLE_MBR}
    assert mbr == {k for k in e06 if k.startswith("Disque système") and "sans UEFI" in k} and len(mbr) == 2
    assert next(v for k, v in e06.items() if "3 To" in k) == TABLE_GPT  # disque de données, même sur PC BIOS
    for item in PRACTICE_ITEMS:  # aucune remise en ordre déjà dans l'ordre attendu
        if item.ordering:
            assert list(item.ordering.correct) != list(range(len(item.ordering.steps))), item.key


def test_no_false_technical_claims_anywhere():
    text = _course_text() + " " + _all_items_text().lower()
    for right in ("formater n'efface pas", "un formatage rapide n'efface pas", "la défragmentation n'efface rien",
                  "la défragmentation n'apporte rien à un ssd", "trim", "2 tio", "4 gio moins 1",
                  "ne suffit jamais", "un bon relevé ne garantit", "sauvegarde vérifiée", "jamais sur une autre partition",
                  "1 073 741 824", "la notice", "exfat", "uuid", "list disk"):
        assert right in text, right
    for wrong in ("le formatage rapide efface", "défragmenter le ssd pour", "fat32 accepte les fichiers de plus",
                  "mbr gère plus de 2", "passed, le disque est sain", "initialiser le disque pour récupérer",
                  "supprimer la partition efi pour"):
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
    for case in ("Cas 1 — Un disque dur neuf invisible", "Cas 2 — Une clé USB qui refuse",
                 "Cas 3 — PC lent", "Cas 4 — Le plan de partitions"):
        assert case in text, case
    for i in range(1, 6):
        assert f"Procédure {i} —" in text, i
    course = _course_raw()
    for item in EXAM_ITEMS:
        assert item.context not in course and escape(item.context) not in course, item.key
    for item in PRACTICE_ITEMS:
        assert escape(item.context) in course, item.key


def test_course_teaches_every_mandatory_point():
    titles = [t for t, _ in pr05_course_sections()]
    assert len(titles) == len(set(titles))
    text = _course_text()
    for notion in (
        # supports et interfaces
        "disque dur", "ssd sata", "ssd nvme", "plateaux", "têtes", "sata", "m.2", "2280", "pci express", "6 gbit/s",
        # secteurs, usure, unités
        "secteur", "cluster", "pages", "blocs", "endurance", "tbw", "répartition de l'usure", "wear leveling",
        "go", "gio", "2^30", "10^9",
        # partitions et démarrage
        "mbr", "gpt", "4 principales", "étendue", "partition efi", "esp", "uefi", "bios", "partition active",
        "msr", "récupération", "volume", "point de montage", "initialiser", "ordre de démarrage",
        # formatage et systèmes de fichiers
        "formatage logique", "formatage rapide", "formatage complet", "bas niveau", "ntfs", "fat32", "exfat", "ext4",
        "journal", "droits", "choix", "usage",
        # Windows et Linux
        "gestion des disques", "diskpart", "étendre", "réduire", "lettre", "clean", "lsblk", "parted", "mkfs.ext4",
        "fstab", "blkid", "mount -a", "df -h", "/dev/nvme0n1",
        # sauvegarde, SMART, entretien
        "sauvegarde", "non destructi", "accord écrit", "3-2-1", "image", "smart", "réalloués", "en attente",
        "crc", "prudence", "trim", "défragmentation", "fstrim", "optimiser les lecteurs",
        # symptômes
        "non initialisé", "raw", "espace plein", "nettoyage de disque", "no bootable device", "inaccessible_boot_device",
        "démarrage impossible",
        # encadrés
        "objectifs", "procédure professionnelle", "erreur fréquente", "à l'écrit", "repère rapide", "glossaire",
    ):
        assert notion in text, notion


def test_course_flags_requirements_links_and_fictive_supports():
    raw = _course_raw()
    text = _text(raw)
    for req in ("AP-03", "AP-C03"):
        assert req in text
    assert "Compléments pédagogiques" in text and "fictif" in text.lower()
    assert "aucun n'est une question officielle" in text.lower()
    assert "aucun schéma n'est tiré d'une image générée" in text.lower()
    assert "conventions du cours" in text.lower()  # seuils signalés comme non normatifs
    for link in ("/uaa/ampcr-mc04", "/uaa/ampcr-mc08", "/uaa/ampcr-mc07", "/uaa/ampcr-pratique-pr01",
                 "/uaa/ampcr-pratique-pr02", "/uaa/ampcr-pratique-pr03", "/uaa/ampcr-pratique-pr04",
                 "/uaa/ampcr-pratique-pr06", "/uaa/ampcr-pratique-pr11", f"/uaa/{PR05_SLUG}/practice",
                 f"/uaa/{PR05_SLUG}/exam"):
        assert link in raw, link
    # PR07 à PR09 ne sont pas encore publiés : renvoi en texte seulement.
    for unpublished in ("/uaa/ampcr-pratique-pr07", "/uaa/ampcr-pratique-pr08", "/uaa/ampcr-pratique-pr09"):
        assert unpublished not in raw
    anchors = set(re.findall(r'id="(pr05-e\d\d)"', raw))
    assert anchors == {f"pr05-{i.key.lower()}" for i in PRACTICE_ITEMS}
    assert "(#pr05-" not in raw


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(t) for t, _ in pr05_course_sections()]
    assert kinds[:15] == ["theory"] * 15
    assert kinds[15:] == ["example", "warning", "exercise", "exam", "summary", "info"]


# =============================================================================================
# 5. Banque, seed et intégration au moteur
# =============================================================================================


def test_plan_slot_matches_ticket():
    slot = plan.COURSE_SLOTS_BY_CODE["PR05"]
    assert slot.ticket == 206 and slot.title == PR05_TITLE == PRACTICAL_COURSES_BY_CODE["PR05"].title


def test_seed_publishes_pr05_in_practical_module_idempotently(db_session):
    module, uaa = _pr05(db_session)
    assert uaa.slug == SLUG and uaa.is_published and uaa.title == PR05_TITLE and uaa.position == 5
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="PR05").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(pr05_course_sections())
    assert {"PR01", "PR02", "PR03", "PR04", "PR05", "PR06", "PR11", "PR15", "PR16", "PR20", "PR24"} <= set(
        plan.published_uaas(db_session)
    )
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_reserves_and_documents(db_session):
    module, uaa = _pr05(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert import_practical_bank(db_session, module, uaa) == len(PRACTICE_ITEMS) + len(EXAM_ITEMS)
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    usages = [question_usage(q) for q in questions]
    assert usages.count("practice") == len(PRACTICE_ITEMS) and usages.count("exam") == 10


def test_correction_context_is_pr05_specific():
    context = _pedagogical_context_for("PR05")
    assert context is get_practical_context("PR05")
    assert context.course_key == SLUG
    notions = " ".join(context.allowed_notions)
    assert "2^30" in notions and "exFAT" in notions and "TRIM" in notions and "UDMA_CRC" in notions
    assert "défragmenter un SSD" in context.constraints and "mot-clé" in context.constraints


# =============================================================================================
# 6. Pages et sessions
# =============================================================================================


def test_course_page_renders_figures_and_exercises(client, db_session):
    _pr05(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert len(ids) == len(set(ids)) and set(ids) >= {f"fig-{f.key}" for f in PR05_FIGURES}
    assert html.count('class="jc-exercise-card"') == len(PRACTICE_ITEMS)
    assert "<details open" not in html
    assert 'href="/ampcr-pratique"' in html and f"/uaa/{SLUG}/exam" in html
    assert "<table" in html


def test_practical_home_and_matrix_show_pr05(client, db_session):
    _pr05(db_session)
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and "cours publiés" in home  # PR07 (#207) publié ensuite
    for req in REQ:
        assert plan.requirement_status(req, {"PR05"}) == plan.STATUS_PARTIAL
    assert plan.VALIDATED_REQUIREMENT_IDS == frozenset()
    assert client.get("/ampcr-pratique/matrice").status_code == 200


@pytest.mark.parametrize("mode", ["practice", "exam"])
def test_sessions_draw_only_from_their_reserve_without_generation(authenticated_client, db_session, monkeypatch, mode):
    fake = _patch_fake_provider(monkeypatch)
    _pr05(db_session)
    assert authenticated_client.get(f"/uaa/{SLUG}/{mode}").status_code == 200
    session_url = _start_session(authenticated_client, db_session, SLUG, mode)
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert {question_usage(sq.question_version.question) for sq in session.session_questions} == {mode}
    assert session.question_count == 10
    assert fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"PR05"}
    if mode == "exam":
        page = authenticated_client.get(f"{session_url}?q=1").text
        assert "Corrigé de référence" not in page and "Barème" not in page


def test_exam_lengths_limited_and_score_on_20(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _pr05(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    from app.v1.models import User

    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="PR05", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "/ 20" in html


def test_practice_sessions_with_classification_and_ordering_submit(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr05(db_session)
    for _ in range(2):  # 16 exercices : deux sessions de 10 couvrent toute la réserve
        session_url = _start_session(authenticated_client, db_session, SLUG, "practice")
        _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
        assert authenticated_client.get(session_url).status_code == 200
