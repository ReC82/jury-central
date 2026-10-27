"""Ticket #209 — AMPCR pratique écrite, PR09 « Installation complète de Linux — préparation et
dépannage ».

Couvre : données de référence **recontrôlées ici** indépendamment (distributions et commandes
apt/dnf, contrôle d'intégrité, partitions et points de montage, repère du swap, règle du double
démarrage, ordre des entrées UEFI, dépannage par six familles, trois procédures, liste de
contrôle et rapport) ; terminaux fictifs (largeur, cohérence) ; schémas SVG (validité,
accessibilité, données) ; exercices et mini-examen (format du socle, remises en ordre et
classements auto-corrigés, pas de question d'acronyme, contexte complet) ; cours (matière du
ticket, 3 procédures, 5 cas résolus, affirmations techniques justes, supports fictifs, cartes) ;
banque, seed, pages et sessions.
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
from app.v1.ampcr_pratique_pr09_bank import (
    E08_VERDICT,
    E11_FIRST_AFTER,
    E11_FIRST_BEFORE,
    EXAM_ITEMS,
    EXAM_TOTAL_POINTS,
    KIND_ERROR,
    KIND_INSTALL,
    KIND_ORDER,
    KIND_POST,
    KIND_PREP,
    KIND_TROUBLE,
    MP_ESP,
    MP_HOME,
    MP_ROOT,
    MP_SWAP,
    PRACTICE_ITEMS,
    REQ,
    WHEN_AFTER,
    WHEN_BEFORE,
    WHEN_DURING,
    X01_SWAP,
    X02_SWAP,
    X02_SWAP_HIB,
    validate_items,
)
from app.v1.ampcr_pratique_pr09_course import PR09_SLUG, PR09_TITLE, pr09_course_sections
from app.v1.ampcr_pratique_pr09_figures import (
    APT,
    BOOT_TREE,
    CHECKLIST,
    DB_CREATE,
    DB_KEEP,
    DB_REUSE,
    DB_STOP,
    DF_FULL_SCREEN,
    DISTRIBUTIONS_BY_NAME,
    DNF,
    DUAL_BOOT_LAYOUT,
    DUAL_BOOT_SCREEN,
    EFIBOOT_SCREEN,
    FINAL_STEPS,
    ISO_BAD,
    ISO_CHECK_SCREEN,
    ISO_NAME,
    ISO_OK,
    ISO_UNKNOWN,
    LINUX_ONLY_LAYOUT,
    PACKAGE_COMMANDS,
    PK_DATA,
    PK_ESP,
    PK_FREE,
    PK_MSR,
    PK_RECOVERY,
    PK_WINDOWS,
    PR09_FIGURES,
    PREP_STEPS,
    PROCEDURES,
    REPORT_SECTIONS,
    SCREEN_WIDTH,
    SETUP_STEPS,
    TR_BOOT,
    TR_CATEGORIES,
    TR_DISK,
    TR_FSTAB,
    TR_NET,
    TR_PERM,
    TR_SPACE,
    TROUBLES_BY_CATEGORY,
    checksum_verdict,
    dual_boot_action,
    first_boot_entry,
    package_manager_of,
    swap_advice,
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

SLUG = "ampcr-pratique-pr09"


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _course_raw() -> str:
    return " ".join(c for _t, c in pr09_course_sections())


def _course_text() -> str:
    return _text(_course_raw()).replace("**", "").replace("`", "").lower()


def _all_items_text() -> str:
    return " ".join(
        " ".join((i.title, i.context, *i.instructions, *i.correction, *(c.expected for c in i.criteria),
                  *(d.content_text for d in i.documents)))
        for i in PRACTICE_ITEMS + EXAM_ITEMS
    )


def _pr09(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "PR09")
    return module, uaa


# =============================================================================================
# 1. Données de référence, recontrôlées indépendamment
# =============================================================================================


def test_distributions_and_package_commands():
    # Gestionnaires de paquets et chargeurs par défaut (documentation des distributions).
    for name in ("Ubuntu LTS", "Linux Mint", "Debian stable", "Pop!_OS"):
        assert package_manager_of(name) == APT, name
    assert package_manager_of("Fedora Workstation") == DNF
    assert DISTRIBUTIONS_BY_NAME["Pop!_OS"].bootloader == "systemd-boot"
    assert DISTRIBUTIONS_BY_NAME["Ubuntu LTS"].bootloader == "GRUB"
    assert DISTRIBUTIONS_BY_NAME["Fedora Workstation"].default_fs == "Btrfs"
    assert DISTRIBUTIONS_BY_NAME["Ubuntu LTS"].default_fs == "ext4"
    with pytest.raises(KeyError):
        package_manager_of("Windows 11")
    commands = {action: (a, d) for action, a, d in PACKAGE_COMMANDS}
    assert commands["Installer les mises à jour"] == ("sudo apt upgrade", "sudo dnf upgrade")
    assert commands["Rafraîchir la liste des paquets"][0] == "sudo apt update"
    for apt_cmd, dnf_cmd in commands.values():
        assert apt_cmd.split()[0] in ("sudo", "apt") and "apt" in apt_cmd


def test_checksum_verdict():
    assert checksum_verdict(f"{ISO_NAME}: OK") == ISO_OK
    assert checksum_verdict(f"{ISO_NAME}: FAILED") == ISO_BAD
    assert checksum_verdict(f"{ISO_NAME}: FAILED open or read") == ISO_BAD
    assert checksum_verdict("sha256sum: WARNING: no file was verified") == ISO_UNKNOWN
    assert E08_VERDICT == ISO_BAD
    assert f"{ISO_NAME}: OK" in ISO_CHECK_SCREEN
    assert "sha256sum -c SHA256SUMS --ignore-missing" in " ".join(ISO_CHECK_SCREEN)


def test_partitions_and_mount_points():
    by_key = {p.key: p for p in LINUX_ONLY_LAYOUT}
    assert [p.key for p in LINUX_ONLY_LAYOUT] == ["esp", "root", "swap", "home"]
    assert by_key["esp"].mount_point == "/boot/efi" and "FAT32" in by_key["esp"].filesystem
    assert by_key["root"].mount_point == "/" and by_key["root"].filesystem == "ext4"
    assert "25 Go" in by_key["root"].size_label  # configuration recommandée d'Ubuntu Desktop
    assert by_key["home"].mount_point == "/home" and "facultative" in by_key["home"].name
    assert "hibernation" in by_key["swap"].role


def test_swap_advice_follows_reference_table():
    # Tableau Red Hat : ≤ 2 Go → 2× (3× avec hibernation) ; 2-8 Go → = RAM (2×) ;
    # 8-64 Go → au moins 4 Go (1,5×) ; > 64 Go → 4 Go, hibernation déconseillée.
    assert swap_advice(2, hibernation=False) == 4 and swap_advice(2, hibernation=True) == 6
    assert swap_advice(4, hibernation=False) == 4 and swap_advice(8, hibernation=True) == 16
    assert swap_advice(16, hibernation=False) == 4 and swap_advice(16, hibernation=True) == 24
    assert swap_advice(128, hibernation=False) == 4 and swap_advice(128, hibernation=True) is None
    with pytest.raises(ValueError):
        swap_advice(0, hibernation=False)
    assert (X01_SWAP, X02_SWAP, X02_SWAP_HIB) == (4, 4, 24)


def test_dual_boot_rule_never_formats_esp_or_touches_windows():
    for kind in (PK_ESP, PK_MSR, PK_WINDOWS, PK_RECOVERY, PK_DATA, PK_FREE):
        for backup, consent in ((True, False), (False, True), (False, False)):
            assert dual_boot_action(kind, backup_verified=backup, written_consent=consent) == DB_STOP
    ok = {"backup_verified": True, "written_consent": True}
    assert dual_boot_action(PK_ESP, **ok) == DB_REUSE
    assert dual_boot_action(PK_FREE, **ok) == DB_CREATE
    for kind in (PK_MSR, PK_WINDOWS, PK_RECOVERY, PK_DATA):
        assert dual_boot_action(kind, **ok) == DB_KEEP
    assert "sans formater" in DB_REUSE
    with pytest.raises(ValueError):
        dual_boot_action("swap", **ok)
    assert [kind for _k, kind, _l, _w in DUAL_BOOT_LAYOUT] == [PK_ESP, PK_MSR, PK_WINDOWS, PK_RECOVERY, PK_FREE]


def test_efibootmgr_order():
    assert E11_FIRST_BEFORE == "Windows Boot Manager" and E11_FIRST_AFTER == "ubuntu"
    assert first_boot_entry(EFIBOOT_SCREEN) == "ubuntu"
    assert "$ sudo efibootmgr -o 0001,0000,0002" in EFIBOOT_SCREEN


def test_troubleshooting_six_families():
    assert TR_CATEGORIES == (TR_DISK, TR_BOOT, TR_FSTAB, TR_NET, TR_PERM, TR_SPACE)
    for category in TR_CATEGORIES:  # les six diagnostics du ticket sont couverts
        assert TROUBLES_BY_CATEGORY[category], category
        assert all(t.never for t in TROUBLES_BY_CATEGORY[category]), category
    fstab = " ".join(t.check + t.action + t.never for t in TROUBLES_BY_CATEGORY[TR_FSTAB])
    assert "UUID" in fstab and "nofail" in fstab and "findmnt --verify" in fstab and "/dev/sdb1" in fstab
    perm_never = " ".join(t.never for t in TROUBLES_BY_CATEGORY[TR_PERM])
    assert "chmod -R 777" in perm_never
    boot = " ".join(t.action + t.never for t in TROUBLES_BY_CATEGORY[TR_BOOT])
    assert "efibootmgr -o" in boot and "Désactiver le démarrage sécurisé" in boot
    space = " ".join(t.action + t.never for t in TROUBLES_BY_CATEGORY[TR_SPACE])
    assert "apt clean" in space and "/usr" in space
    assert len(BOOT_TREE) == 4 and "firmware" in BOOT_TREE[0][0]


def test_procedures_order_checklist_and_report():
    assert len(PROCEDURES) == 3
    prep = [label for label, _d in PREP_STEPS]
    assert prep[0] == "Recueillir la demande"
    assert prep.index("Sauvegarder") < prep.index("Télécharger et contrôler l'ISO") < prep.index("Créer la clé USB")
    setup = [label for label, _d in SETUP_STEPS]
    assert setup[0] == "Régler le firmware" and setup[-1] == "Copie et redémarrage"
    assert setup.index("Tester en session live") < setup.index("Type d'installation") < setup.index("Partitions")
    assert "UEFI:" in SETUP_STEPS[1][1]
    final = [label for label, _d in FINAL_STEPS]
    assert final[0] == "Mettre à jour" and final[-1] == "Contrôler et documenter"
    assert "apt update puis sudo apt upgrade" in FINAL_STEPS[0][1]
    points = {p: (w, e) for p, w, e in CHECKLIST}
    assert points["Démarrage sécurisé"] == ("mokutil --sb-state", "« SecureBoot enabled »")
    assert points["Services"][0] == "systemctl --failed" and "0 loaded units listed" in points["Services"][1]
    assert REPORT_SECTIONS[0][0] == "Demande" and "accord écrit" in REPORT_SECTIONS[0][1]


def test_screens_readable_and_consistent():
    for screen in (ISO_CHECK_SCREEN, DUAL_BOOT_SCREEN, EFIBOOT_SCREEN, DF_FULL_SCREEN):
        assert max(len(line) for line in screen) <= SCREEN_WIDTH
    iso = " ".join(ISO_CHECK_SCREEN)
    assert "sdb      14.6G usb" in iso and "sda     931.5G sata" in iso
    dual = " ".join(DUAL_BOOT_SCREEN)
    assert "nvme0n1p1   100M vfat" in dual and "WinRE" in dual and "iso9660" in dual
    df_line = next(line for line in DF_FULL_SCREEN if line.startswith("/dev/"))
    assert df_line.split()[-2:] == ["100%", "/"]
    assert "Filesystem      Size  Used Avail Use% Mounted on" in DF_FULL_SCREEN


# =============================================================================================
# 2. Schémas
# =============================================================================================


def test_figures_valid_accessible_and_unique():
    keys = [f.key for f in PR09_FIGURES]
    assert len(keys) == len(set(keys)) == 9
    for figure in PR09_FIGURES:
        assert validate_figure(figure) == [], figure.key
        html = str(render_figure(figure))
        assert 'role="img"' in html and "(schéma non officiel)" in html and not figure.official


def test_figures_drawn_from_data():
    by_key = {f.key: f for f in PR09_FIGURES}
    for key, steps in (("pr09-preparer", PREP_STEPS), ("pr09-installer", SETUP_STEPS), ("pr09-finaliser", FINAL_STEPS)):
        svg = by_key[key].svg
        for index, (label, _detail) in enumerate(steps, start=1):
            assert f"{index}. {escape(label)}" in svg, (key, label)
    partitions = re.findall(r'data-partition="([^"]+)"', by_key["pr09-partitions"].svg)
    assert partitions == [p.key for p in LINUX_ONLY_LAYOUT] + [k for k, *_r in DUAL_BOOT_LAYOUT]
    assert by_key["pr09-demarrage"].svg.count("data-step=") == len(BOOT_TREE)
    for key in ("pr09-controle-iso", "pr09-double-demarrage", "pr09-efibootmgr", "pr09-disque-plein"):
        assert "fictive" in by_key[key].caption.lower() and "Capture fictive" in by_key[key].svg, key


# =============================================================================================
# 3. Exercices et mini-examen
# =============================================================================================


def test_items_valid_and_counts_match_ticket():
    assert validate_items() == []
    assert len(PRACTICE_ITEMS) >= 16 and len(EXAM_ITEMS) == 10  # ticket : ≥ 16 exercices, mini-examen /20
    assert sum(i.total_points for i in EXAM_ITEMS) == EXAM_TOTAL_POINTS == 20
    kinds = [i.kind for i in PRACTICE_ITEMS]
    for kind, minimum in ((KIND_ORDER, 3), (KIND_PREP, 3), (KIND_INSTALL, 3), (KIND_TROUBLE, 5), (KIND_POST, 1),
                          (KIND_ERROR, 1)):
        assert kinds.count(kind) >= minimum, kind
    keys = [i.key for i in PRACTICE_ITEMS + EXAM_ITEMS]
    assert len(keys) == len(set(keys))
    covered = {r for i in PRACTICE_ITEMS + EXAM_ITEMS for r in i.requirement_ids}
    assert REQ <= covered and "AP-C03" in covered
    assert set(plan.COURSE_SLOTS_BY_CODE["PR09"].requirement_ids) == REQ
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
    assert next(v for k, v in e04.items() if "Intel RST" in k) == TR_DISK
    assert next(v for k, v in e04.items() if "sans menu" in k) == TR_BOOT
    assert next(v for k, v in e04.items() if "emergency" in k) == TR_FSTAB
    assert next(v for k, v in e04.items() if "NO-CARRIER" in k) == TR_NET
    assert next(v for k, v in e04.items() if "sudoers" in k) == TR_PERM
    assert next(v for k, v in e04.items() if "No space" in k) == TR_SPACE
    e05 = answers("E05")
    assert next(v for k, v in e05.items() if "shim" in k) == MP_ESP
    assert next(v for k, v in e05.items() if "/etc/fstab" in k) == MP_ROOT
    assert next(v for k, v in e05.items() if "réinstalle" in k) == MP_HOME
    assert next(v for k, v in e05.items() if "hibernation" in k) == MP_SWAP
    e06 = answers("E06")
    assert next(v for k, v in e06.items() if "partition système EFI" in k) == DB_REUSE
    assert next(v for k, v in e06.items() if "Windows réduit" in k) == DB_KEEP
    assert next(v for k, v in e06.items() if "Photos" in k) == DB_KEEP
    assert next(v for k, v in e06.items() if k.startswith("Espace libre de 100 Go")) == DB_CREATE
    assert next(v for k, v in e06.items() if "accord oral" in k) == DB_STOP
    e07 = answers("E07")
    assert next(v for k, v in e07.items() if "BitLocker" in k) == WHEN_BEFORE
    assert next(v for k, v in e07.items() if "démarrage rapide" in k) == WHEN_BEFORE
    assert next(v for k, v in e07.items() if "session live" in k) == WHEN_DURING
    assert next(v for k, v in e07.items() if "apt upgrade" in k) == WHEN_AFTER
    for item in PRACTICE_ITEMS:  # aucune remise en ordre déjà dans l'ordre attendu
        if item.ordering:
            assert list(item.ordering.correct) != list(range(len(item.ordering.steps))), item.key


def test_no_false_technical_claims_anywhere():
    text = _course_text() + " " + _all_items_text().lower()
    for right in ("accord écrit", "sauvegarde vérifiée", "sha256sum -c", "--ignore-missing", "of=/dev/sdb",
                  "/boot/efi", "sans formatage", "ext4", "/home", "swap", "uuid", "nofail", "findmnt --verify",
                  "mount -a", "efibootmgr -o", "grub", "systemd-boot", "shim", "enroll mok", "mokutil --sb-state",
                  "usermod -ag sudo", "apt update", "apt upgrade", "dnf upgrade", "kernel driver in use",
                  "bcmwl-kernel-source", "systemctl --failed", "df -h", "apt clean", "journalctl --vacuum-size",
                  "chown", "démarrage rapide", "réduire le volume", "documentation de la distribution fait foi"):
        assert right in text, right
    for wrong in ("linux ne supporte pas le démarrage sécurisé.", "désactiver le démarrage sécurisé pour installer",
                  "formater l'esp de windows pour", "of=/dev/sdb1", "chmod -r 777 pour corriger",
                  "la taille du fichier prouve", "apt upgrade suffit sans", "travailler en root est recommandé",
                  "/dev/sdb1 est plus fiable"):
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
    for case in ("Cas 1 — Installation complète de Linux seul", "Cas 2 — Double démarrage",
                 "Cas 3 — Après l'installation, le PC démarre toujours sous Windows",
                 "Cas 4 — Mode d'urgence : fstab et UUID", "Cas 5 — Réseau absent"):
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
    titles = [t for t, _ in pr09_course_sections()]
    assert len(titles) == len(set(titles))
    text = _course_text()
    for notion in (
        # matière du ticket, dans l'ordre du cahier des charges
        "distribution", "usage", "iso", "intégrité", "sha-256", "clé usb", "uefi", "gpt", "esp", "session live",
        "sauvegarde", "racine", "/home", "facultative", "swap", "ext4", "grub", "systemd-boot", "comptes", "sudo",
        "réseau", "mises à jour", "apt", "dnf", "pilotes", "services", "tests", "double démarrage", "prudence",
        # diagnostics du ticket
        "disque non vu", "chargeur", "fstab", "uuid", "réseau absent", "permissions", "espace disque",
        # compléments utiles
        "démarrage sécurisé", "mok", "bitlocker", "lsblk", "efibootmgr", "lspci", "ip a", "systemctl", "df -h",
        "liste de contrôle", "rapport d'intervention",
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
    assert "conventions du cours" in text.lower() and "en anglais" in text.lower()
    for link in ("/uaa/ampcr-mc07", "/uaa/ampcr-mc08", "/uaa/ampcr-mc11", "/uaa/ampcr-mc30",
                 "/uaa/ampcr-pratique-pr04", "/uaa/ampcr-pratique-pr05", "/uaa/ampcr-pratique-pr06",
                 "/uaa/ampcr-pratique-pr07", "/uaa/ampcr-pratique-pr08", "/uaa/ampcr-pratique-pr11",
                 "/uaa/ampcr-pratique-pr24", f"/uaa/{PR09_SLUG}/practice", f"/uaa/{PR09_SLUG}/exam"):
        assert link in raw, link
    # PR10 et PR12 ne sont pas encore publiés : renvoi en texte seulement.
    for unpublished in ("/uaa/ampcr-pratique-pr10", "/uaa/ampcr-pratique-pr12"):
        assert unpublished not in raw
    anchors = set(re.findall(r'id="(pr09-e\d\d)"', raw))
    assert anchors == {f"pr09-{i.key.lower()}" for i in PRACTICE_ITEMS}
    assert "(#pr09-" not in raw


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(t) for t, _ in pr09_course_sections()]
    assert kinds[:13] == ["theory"] * 13
    assert kinds[13:] == ["example", "warning", "exercise", "exam", "summary", "info"]


# =============================================================================================
# 5. Banque, seed et intégration au moteur
# =============================================================================================


def test_plan_slot_matches_ticket():
    slot = plan.COURSE_SLOTS_BY_CODE["PR09"]
    assert slot.ticket == 209 and slot.title == PR09_TITLE == PRACTICAL_COURSES_BY_CODE["PR09"].title


def test_seed_publishes_pr09_in_practical_module_idempotently(db_session):
    module, uaa = _pr09(db_session)
    assert uaa.slug == SLUG and uaa.is_published and uaa.title == PR09_TITLE and uaa.position == 9
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="PR09").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(pr09_course_sections())
    assert {"PR08", "PR09", "PR11"} <= set(plan.published_uaas(db_session))
    ordered = [u.code for u in sorted(module.uaas, key=lambda u: (u.position, u.id))]
    assert ordered.index("PR08") < ordered.index("PR09") < ordered.index("PR11")
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_reserves_and_documents(db_session):
    module, uaa = _pr09(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert import_practical_bank(db_session, module, uaa) == len(PRACTICE_ITEMS) + len(EXAM_ITEMS)
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    usages = [question_usage(q) for q in questions]
    assert usages.count("practice") == len(PRACTICE_ITEMS) and usages.count("exam") == 10


def test_correction_context_is_pr09_specific():
    context = _pedagogical_context_for("PR09")
    assert context is get_practical_context("PR09")
    assert context.course_key == SLUG
    notions = " ".join(context.allowed_notions)
    for notion in ("sha256sum -c", "/boot/efi sans formatage", "UUID", "efibootmgr -o", "usermod -aG sudo", "MOK"):
        assert notion in notions, notion
    assert "mot-clé" in context.constraints and "ESP de Windows" in context.constraints


# =============================================================================================
# 6. Pages et sessions
# =============================================================================================


def test_course_page_renders_figures_and_exercises(client, db_session):
    _pr09(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert set(ids) >= {f"fig-{f.key}" for f in PR09_FIGURES}
    assert html.count('class="jc-exercise-card"') == len(PRACTICE_ITEMS)
    assert "<details open" not in html
    assert 'href="/ampcr-pratique"' in html and f"/uaa/{SLUG}/exam" in html
    assert "<table" in html and "jc-pr-console" in html


def test_practical_home_and_matrix_show_pr09(client, db_session):
    _pr09(db_session)
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and re.search(r"14 cours publiés sur 30 prévus", _text(home))
    for req in REQ:
        assert plan.requirement_status(req, {"PR09"}) == plan.STATUS_PARTIAL
    assert plan.VALIDATED_REQUIREMENT_IDS == frozenset()
    assert client.get("/ampcr-pratique/matrice").status_code == 200


@pytest.mark.parametrize("mode", ["practice", "exam"])
def test_sessions_draw_only_from_their_reserve_without_generation(authenticated_client, db_session, monkeypatch, mode):
    fake = _patch_fake_provider(monkeypatch)
    _pr09(db_session)
    assert authenticated_client.get(f"/uaa/{SLUG}/{mode}").status_code == 200
    session_url = _start_session(authenticated_client, db_session, SLUG, mode)
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert {question_usage(sq.question_version.question) for sq in session.session_questions} == {mode}
    assert session.question_count == 10
    assert fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"PR09"}
    if mode == "exam":
        page = authenticated_client.get(f"{session_url}?q=1").text
        assert "Corrigé de référence" not in page and "Barème" not in page


def test_exam_lengths_limited_and_score_on_20(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _pr09(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    from app.v1.models import User

    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="PR09", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "/ 20" in html


def test_practice_sessions_with_classification_and_ordering_submit(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr09(db_session)
    for _ in range(2):  # 17 exercices : deux sessions de 10 couvrent toute la réserve
        session_url = _start_session(authenticated_client, db_session, SLUG, "practice")
        _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
        assert authenticated_client.get(session_url).status_code == 200
