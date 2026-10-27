"""Ticket #207 — AMPCR pratique écrite, PR07 « Systèmes d'exploitation, GUI/CLI et prérequis
d'installation ».

Couvre : données de référence **recontrôlées ici** indépendamment (fonctions du système,
éditions de Windows, prérequis de Windows 11 et verdicts, limite 32 bits, installation propre
ou mise à niveau, virtualisation, outils GUI/CLI, trois procédures) ; schémas SVG (validité,
accessibilité, étapes et couches cohérentes avec les données) ; exercices et mini-examen
(format du socle, remises en ordre et classements auto-corrigés, pas de question d'acronyme,
contexte complet) ; cours (matière du ticket, 3 procédures, 4 scénarios corrigés, affirmations
techniques justes, supports fictifs, cartes) ; banque, seed, pages et sessions.
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
from app.v1.ampcr_pratique_pr07_bank import (
    E04_CATEGORIES,
    E06_RESULTS,
    E11_USABLE,
    E15_LEFT,
    E15_OK,
    EXAM_ITEMS,
    EXAM_TOTAL_POINTS,
    KIND_CHOICE,
    KIND_ERROR,
    KIND_ORDER,
    KIND_PREREQ,
    KIND_TOOLS,
    PRACTICE_ITEMS,
    REQ,
    X02_BLOCKERS,
    X02_VERDICT,
    X08_LEFT,
    X08_OK,
    validate_items,
)
from app.v1.ampcr_pratique_pr07_course import PR07_SLUG, PR07_TITLE, pr07_course_sections
from app.v1.ampcr_pratique_pr07_figures import (
    BOOT_LEGACY_ENTRY,
    BOOT_MENU_SCREEN,
    BOOT_UEFI_ENTRY,
    CASE2_BLOCKERS,
    CASE2_SETTINGS,
    CASE2_VERDICT,
    CHECK_STEPS,
    EDITION_FEATURES,
    EDITION_HOME,
    EDITION_PRO,
    FN_DRIVER,
    FN_FS,
    FN_INTERFACE,
    FN_KERNEL,
    FN_SERVICE,
    INSTALL_BACKUP_FIRST,
    INSTALL_CLEAN,
    INSTALL_NONE,
    INSTALL_PLAN_STEPS,
    INSTALL_TREE,
    INSTALL_UPGRADE,
    LINUX_STACK,
    LIVE_CHECK_SCREEN,
    MEDIA_STEPS,
    MSINFO_SCREEN,
    OS_FUNCTIONS,
    PR07_FIGURES,
    PROCEDURES,
    SCREEN_WIDTH,
    TOOLS_BY_TASK,
    TYPE1_STACK,
    TYPE2_STACK,
    W11_NO,
    W11_OK,
    W11_SETTINGS,
    WIN11_REQUIREMENTS,
    WINDOWS_STACK,
    PcSpec,
    edition_needed,
    install_type,
    max_addressable_gib,
    usable_ram_gib,
    vm_plan,
    win11_check,
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

SLUG = "ampcr-pratique-pr07"


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _course_raw() -> str:
    return " ".join(c for _t, c in pr07_course_sections())


def _course_text() -> str:
    return _text(_course_raw()).replace("**", "").replace("`", "").lower()


def _all_items_text() -> str:
    return " ".join(
        " ".join((i.title, i.context, *i.instructions, *i.correction, *(c.expected for c in i.criteria),
                  *(d.content_text for d in i.documents)))
        for i in PRACTICE_ITEMS + EXAM_ITEMS
    )


def _pr07(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "PR07")
    return module, uaa


def _pc(**changes) -> PcSpec:
    base = {"cpu": "test", "cpu_64bit": True, "cpu_listed": True, "cores": 4, "ghz": 2.5, "ram_gb": 8, "storage_gb": 256,
                "uefi_capable": True, "firmware_mode": "UEFI", "secure_boot_on": True, "tpm_version": 2.0,
                "tpm_enabled": True, "disk_table": "GPT"}
    base.update(changes)
    return PcSpec(**base)


# =============================================================================================
# 1. Données de référence, recontrôlées indépendamment
# =============================================================================================


def test_windows11_requirements_and_verdicts():
    # Prérequis publiés par Microsoft : 64 bits de la liste, 2 cœurs, 1 GHz, 4 Go, 64 Go, UEFI
    # compatible démarrage sécurisé, TPM 2.0.
    table = {r.key: r.minimum for r in WIN11_REQUIREMENTS}
    assert "64 bits" in table["cpu"] and "2 cœurs" in table["cpu"] and "1 GHz" in table["cpu"]
    assert table["ram"] == "4 Go" and table["storage"] == "64 Go" and "2.0" in table["tpm"]
    assert "UEFI" in table["firmware"] and "démarrage sécurisé" in table["firmware"]
    assert win11_check(_pc()) == (W11_OK, (), ())
    # Mode hérité sur MBR : conversion AVANT la bascule en UEFI.
    verdict, blockers, settings = win11_check(_pc(firmware_mode="Hérité", disk_table="MBR", secure_boot_on=False))
    assert verdict == W11_SETTINGS and blockers == ()
    assert "mbr2gpt" in settings[0] and "UEFI" in settings[1]
    # TPM intégré désactivé : réglage, pas blocage.
    assert win11_check(_pc(tpm_enabled=False))[0] == W11_SETTINGS
    # Démarrage sécurisé seulement désactivé : recommandation, pas blocage.
    verdict, _b, settings = win11_check(_pc(secure_boot_on=False))
    assert verdict == W11_OK and settings == ("activer le démarrage sécurisé (recommandé)",)
    for change in ({"cpu_listed": False}, {"cpu_64bit": False}, {"tpm_version": 1.2}, {"ram_gb": 2},
                   {"storage_gb": 32}, {"uefi_capable": False}, {"cores": 1}, {"dx12": False}):
        verdict, blockers, settings = win11_check(_pc(**change))
        assert verdict == W11_NO and blockers and settings == (), change
    assert (CASE2_VERDICT, CASE2_BLOCKERS) == (W11_SETTINGS, ())
    assert len([s for s in CASE2_SETTINGS if "recommandé" not in s]) == 2
    assert X02_VERDICT == W11_NO and X02_BLOCKERS == ("processeur absent de la liste de compatibilité",)
    assert [r[0] for r in E06_RESULTS] == [W11_OK, W11_SETTINGS, W11_NO, W11_SETTINGS, W11_NO, W11_OK]


def test_editions_architecture_install_type_and_vm():
    assert edition_needed(()) == EDITION_HOME
    home = [need for need, ok in EDITION_FEATURES if ok]
    assert edition_needed(tuple(home)) == EDITION_HOME
    for need, ok in EDITION_FEATURES:
        assert edition_needed((need,)) == (EDITION_HOME if ok else EDITION_PRO), need
    pro_only = " ".join(need for need, ok in EDITION_FEATURES if not ok)
    for feature in ("domaine", "BitLocker", "hôte Bureau à distance", "Hyper-V", "gpedit"):
        assert feature in pro_only, feature
    with pytest.raises(ValueError):
        edition_needed(("faire le café",))
    # 2^32 octets = 4 Gio.
    assert max_addressable_gib(32) == 2**32 // 2**30 == 4 and max_addressable_gib(64) is None
    assert usable_ram_gib(8, 32) == 4 == E11_USABLE and usable_ram_gib(8, 64) == 8 and usable_ram_gib(2, 32) == 2
    with pytest.raises(ValueError):
        max_addressable_gib(16)
    kw = {"backup_ok": True, "requirements_ok": True, "same_family_and_arch": True, "system_healthy": True, "keep_programs": True}
    assert install_type(**kw) == INSTALL_UPGRADE
    assert install_type(**{**kw, "backup_ok": False}) == INSTALL_BACKUP_FIRST
    assert install_type(**{**kw, "backup_ok": False, "requirements_ok": False}) == INSTALL_BACKUP_FIRST
    assert install_type(**{**kw, "requirements_ok": False}) == INSTALL_NONE
    for key in ("same_family_and_arch", "system_healthy", "keep_programs"):
        assert install_type(**{**kw, key: False}) == INSTALL_CLEAN, key
    assert len(INSTALL_TREE) == 5 and "Sauvegarder" in INSTALL_TREE[0][1]
    assert (E15_LEFT, E15_OK) == (10, True) and (X08_LEFT, X08_OK) == (4, True)
    assert vm_plan(8, (4, 2)) == (2, False)


def test_os_functions_tools_and_screens():
    names = [f.name for f in OS_FUNCTIONS]
    assert names[:2] == [FN_KERNEL, FN_DRIVER] and {FN_FS, FN_SERVICE, FN_INTERFACE} <= set(names)
    assert "systemd" in next(f.linux for f in OS_FUNCTIONS if f.name == FN_SERVICE)
    assert "uname -m" not in TOOLS_BY_TASK["Version du système"].linux_cli  # uname -r = noyau
    assert "cat /etc/os-release" in TOOLS_BY_TASK["Version du système"].linux_cli
    assert "ipconfig /all" == TOOLS_BY_TASK["Réseau"].windows_cli
    assert "tpm.msc" in TOOLS_BY_TASK["Firmware et sécurité"].windows_gui
    assert "mokutil --sb-state" in TOOLS_BY_TASK["Firmware et sécurité"].linux_cli
    # Piles : du haut (applications) vers le bas (matériel) ; type 1 sans système hôte.
    for stack in (WINDOWS_STACK, LINUX_STACK):
        assert stack[0].startswith("Applications") and stack[-1].startswith("Matériel")
        assert any("Noyau" in layer for layer in stack) and any("UEFI" in layer for layer in stack)
    assert any("hôte" in layer for layer in TYPE2_STACK) and not any("hôte" in layer for layer in TYPE1_STACK)
    for stack in (TYPE1_STACK, TYPE2_STACK):
        assert "VT-x" in stack[-1] and "AMD-V" in stack[-1]
    # Captures : lisibles sur mobile, et cohérentes avec les verdicts.
    for screen in (MSINFO_SCREEN, BOOT_MENU_SCREEN, LIVE_CHECK_SCREEN):
        assert max(len(line) for line in screen) <= SCREEN_WIDTH
    joined = " ".join(MSINFO_SCREEN)
    assert "Hérité" in joined and "Non pris en charge" in joined and "2.0" in joined and "MBR" in joined
    assert BOOT_UEFI_ENTRY.startswith("UEFI: ") and not BOOT_LEGACY_ENTRY.startswith("UEFI")
    assert BOOT_LEGACY_ENTRY in BOOT_UEFI_ENTRY  # même clé, deux modes
    live = " ".join(LIVE_CHECK_SCREEN)
    assert "x86_64" in live and "/sys/firmware/efi" in live and "Aucun fichier" in live


def test_procedures_order():
    assert len(PROCEDURES) == 3
    plan_labels = [label for label, _d in INSTALL_PLAN_STEPS]
    assert plan_labels[0] == "Sauvegarder" and plan_labels[-1] == "Contrôler et documenter"
    assert plan_labels.index("Préparer le média") < plan_labels.index("Régler le firmware") < plan_labels.index("Installer")
    assert plan_labels.index("Installer") < plan_labels.index("Installer les pilotes") < plan_labels.index("Sécuriser")
    media = [label for label, _d in MEDIA_STEPS]
    assert media.index("Télécharger l'image") < media.index("Contrôler l'image") < media.index("Écrire la clé")
    assert "SHA-256" in MEDIA_STEPS[1][1] and "UEFI" in MEDIA_STEPS[-1][1]
    check = [label for label, _d in CHECK_STEPS]
    assert check[0] == "Relever le besoin" and check[-1] == "Conclure par écrit"
    assert check.index("Relever le firmware") < check.index("Comparer aux prérequis")


# =============================================================================================
# 2. Schémas
# =============================================================================================


def test_figures_valid_accessible_and_unique():
    keys = [f.key for f in PR07_FIGURES]
    assert len(keys) == len(set(keys)) == 8
    for figure in PR07_FIGURES:
        assert validate_figure(figure) == [], figure.key
        html = str(render_figure(figure))
        assert 'role="img"' in html and "(schéma non officiel)" in html and not figure.official


def test_figures_drawn_from_data():
    by_key = {f.key: f for f in PR07_FIGURES}
    for key, steps in (("pr07-prerequis", CHECK_STEPS), ("pr07-media", MEDIA_STEPS),
                       ("pr07-plan-installation", INSTALL_PLAN_STEPS)):
        svg = by_key[key].svg
        for index, (label, _detail) in enumerate(steps, start=1):
            assert f"{index}. {escape(label)}" in svg, (key, label)
    layers = re.findall(r'data-layer="([^"]+)"', by_key["pr07-couches"].svg)
    assert layers == [escape(x) for x in WINDOWS_STACK + LINUX_STACK]
    vm_layers = re.findall(r'data-layer="([^"]+)"', by_key["pr07-virtualisation"].svg)
    assert vm_layers == [escape(x) for x in TYPE2_STACK + TYPE1_STACK]
    assert by_key["pr07-propre-ou-mise-a-niveau"].svg.count("data-step=") == len(INSTALL_TREE)
    for layer in WINDOWS_STACK:
        assert layer in by_key["pr07-couches"].alt
    assert "fictive" in by_key["pr07-msinfo"].caption and "fictive" in by_key["pr07-menu-demarrage"].caption


# =============================================================================================
# 3. Exercices et mini-examen
# =============================================================================================


def test_items_valid_and_counts_match_ticket():
    assert validate_items() == []
    assert len(PRACTICE_ITEMS) >= 15 and len(EXAM_ITEMS) == 10  # ticket : ≥ 15 exercices, mini-examen /20
    assert sum(i.total_points for i in EXAM_ITEMS) == EXAM_TOTAL_POINTS == 20
    kinds = [i.kind for i in PRACTICE_ITEMS]
    for kind, minimum in ((KIND_ORDER, 3), (KIND_CHOICE, 4), (KIND_PREREQ, 4), (KIND_TOOLS, 1), (KIND_ERROR, 1)):
        assert kinds.count(kind) >= minimum, kind
    keys = [i.key for i in PRACTICE_ITEMS + EXAM_ITEMS]
    assert len(keys) == len(set(keys))
    covered = {r for i in PRACTICE_ITEMS + EXAM_ITEMS for r in i.requirement_ids}
    assert REQ <= covered and {"AP-10", "AP-C03"} <= covered
    assert set(plan.COURSE_SLOTS_BY_CODE["PR07"].requirement_ids) == REQ
    types = [i.question_type for i in PRACTICE_ITEMS]
    assert types.count("ordering") == 3 and types.count("classification") == 4


def test_auto_corrected_answers():
    by_key = {i.key: i for i in PRACTICE_ITEMS}

    def ordered(key: str) -> list[str]:
        o = by_key[key].ordering
        return [o.steps[i].split(" — ")[0] for i in o.correct]

    assert ordered("E01") == [label for label, _d in INSTALL_PLAN_STEPS]
    assert ordered("E02") == [label for label, _d in MEDIA_STEPS]
    assert ordered("E03") == [label for label, _d in CHECK_STEPS]

    def answers(key: str) -> dict[str, str]:
        c = by_key[key].classification
        return dict(zip(c.elements, (c.categories[i] for i in c.correct), strict=True))

    e04 = answers("E04")
    assert set(by_key["E04"].classification.categories) == set(E04_CATEGORIES)
    assert next(v for k, v in e04.items() if "temps du processeur" in k) == FN_KERNEL
    assert next(v for k, v in e04.items() if "Wi-Fi" in k) == FN_DRIVER
    assert next(v for k, v in e04.items() if "impressions" in k) == FN_SERVICE
    assert next(v for k, v in e04.items() if "ipconfig" in k) == FN_INTERFACE
    e05 = answers("E05")
    assert next(v for k, v in e05.items() if "domaine" in k) == EDITION_PRO
    assert next(v for k, v in e05.items() if "client Bureau à distance" in k) == EDITION_HOME
    assert next(v for k, v in e05.items() if "hôte Bureau à distance" in k) == EDITION_PRO
    e06 = answers("E06")
    assert next(v for k, v in e06.items() if "mode hérité" in k) == W11_SETTINGS
    assert next(v for k, v in e06.items() if "TPM 1.2" in k) == W11_NO
    assert next(v for k, v in e06.items() if "32 Go" in k) == W11_NO
    assert next(v for k, v in e06.items() if "démarrage sécurisé désactivé" in k) == W11_OK
    e07 = answers("E07")
    assert next(v for k, v in e07.items() if "32 bits" in k) == INSTALL_CLEAN
    assert next(v for k, v in e07.items() if "infecté" in k) == INSTALL_CLEAN
    assert next(v for k, v in e07.items() if "gardant tous ses logiciels" in k) == INSTALL_UPGRADE
    assert next(v for k, v in e07.items() if "TPM 1.2" in k) == INSTALL_NONE
    for item in PRACTICE_ITEMS:  # aucune remise en ordre déjà dans l'ordre attendu
        if item.ordering:
            assert list(item.ordering.correct) != list(range(len(item.ordering.steps))), item.key


def test_no_false_technical_claims_anywhere():
    text = _course_text() + " " + _all_items_text().lower()
    for right in ("64 bits", "tpm 2.0", "mbr2gpt", "/allowfullos", "sha-256", "« uefi: »", "sauvegarde vérifiée",
                  "14 octobre 2025", "shim", "mok", "4 gio", "instantané", "n'est pas une sauvegarde",
                  "charger un pilote", "compte standard", "page officielle de l'éditeur fait foi"):
        assert right in text, right
    for wrong in ("désactiver le démarrage sécurisé pour installer linux", "mise à niveau de 32 à 64 bits possible",
                  "windows 11 famille peut rejoindre", "un instantané est une sauvegarde", "windows 11 existe en 32 bits",
                  "contourner les prérequis", "linux ne démarre pas avec le démarrage sécurisé."):
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


def test_four_corrected_scenarios_three_procedures_and_exam_not_in_course():
    text = _text(_course_raw())
    for case in ("Scénario 1 — Choisir le système", "Scénario 2 — Prérequis de Windows 11",
                 "Scénario 3 — Installation propre ou mise à niveau", "Scénario 4 — Plan d'installation"):
        assert case in text, case
    for i in range(1, 4):
        assert f"Procédure {i} —" in text, i
    course = _course_raw()
    for item in EXAM_ITEMS:
        assert item.context not in course and escape(item.context) not in course, item.key
    for item in PRACTICE_ITEMS:
        assert escape(item.context) in course, item.key


def test_course_teaches_every_mandatory_point():
    titles = [t for t, _ in pr07_course_sections()]
    assert len(titles) == len(set(titles))
    text = _course_text()
    for notion in (
        # rôle et fonctions
        "système d'exploitation", "noyau", "pilote", "système de fichiers", "comptes", "services", "interface",
        # systèmes du marché, sans figer les versions
        "windows", "distribution", "ubuntu", "debian", "linux mint", "fedora", "macos", "chromeos", "lts",
        "gnome", "xfce", "apt", "fin de support", "page officielle",
        # éditions
        "famille", "professionnel", "domaine", "bitlocker", "hyper-v",
        # GUI / CLI
        "interface graphique", "ligne de commande", "powershell", "bash", "terminal", "systeminfo",
        "ipconfig /all", "msinfo32", "cat /etc/os-release", "uname -m", "free -h", "lsblk", "sudo", "ssh",
        # prérequis matériel et firmware
        "32 bits", "64 bits", "x64", "arm64", "uefi", "mode hérité", "csm", "démarrage sécurisé", "secure boot",
        "tpm 2.0", "intel ptt", "amd ftpm", "mbr2gpt", "contrôle d'intégrité du pc",
        # préparation
        "sauvegarde", "accord écrit", "licence", "oem", "activation", "installation propre", "mise à niveau",
        # média et démarrage
        "iso", "sha-256", "rufus", "clé usb", "ordre de démarrage", "menu de démarrage", "gpt", "esp",
        # partitions, pilotes
        "partition de données", "double démarrage", "vmd", "charger un pilote", "chipset", "pilotes additionnels",
        # comptes et sécurité
        "compte administrateur", "compte standard", "uac", "mises à jour", "defender", "pare-feu", "ufw",
        "chiffrement", "clé de récupération",
        # virtualisation
        "virtualisation", "hyperviseur", "virtualbox", "vt-x", "amd-v", "tpm virtuel", "instantané",
        # encadrés
        "objectifs", "procédure professionnelle", "erreur fréquente", "à l'écrit", "repère rapide", "glossaire",
    ):
        assert notion in text, notion


def test_course_flags_requirements_links_and_fictive_supports():
    raw = _course_raw()
    text = _text(raw)
    for req in ("AP-08", "AP-12", "AP-10", "AP-C03"):
        assert req in text
    assert "Compléments pédagogiques" in text and "fictif" in text.lower()
    assert "aucun n'est une question officielle" in text.lower()
    assert "aucun schéma n'est tiré d'une image générée" in text.lower()
    assert "convention du cours" in text.lower()
    for link in ("/uaa/ampcr-mc07", "/uaa/ampcr-mc08", "/uaa/ampcr-mc09", "/uaa/ampcr-mc10", "/uaa/ampcr-mc11",
                 "/uaa/ampcr-mc12", "/uaa/ampcr-pratique-pr01", "/uaa/ampcr-pratique-pr04",
                 "/uaa/ampcr-pratique-pr05", "/uaa/ampcr-pratique-pr11", f"/uaa/{PR07_SLUG}/practice",
                 f"/uaa/{PR07_SLUG}/exam"):
        assert link in raw, link
    # PR08 à PR10 ne sont pas encore publiés : renvoi en texte seulement.
    for unpublished in ("/uaa/ampcr-pratique-pr08", "/uaa/ampcr-pratique-pr09", "/uaa/ampcr-pratique-pr10"):
        assert unpublished not in raw
    anchors = set(re.findall(r'id="(pr07-e\d\d)"', raw))
    assert anchors == {f"pr07-{i.key.lower()}" for i in PRACTICE_ITEMS}
    assert "(#pr07-" not in raw


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(t) for t, _ in pr07_course_sections()]
    assert kinds[:15] == ["theory"] * 15
    assert kinds[15:] == ["example", "warning", "exercise", "exam", "summary", "info"]


# =============================================================================================
# 5. Banque, seed et intégration au moteur
# =============================================================================================


def test_plan_slot_matches_ticket():
    slot = plan.COURSE_SLOTS_BY_CODE["PR07"]
    assert slot.ticket == 207 and slot.title == PR07_TITLE == PRACTICAL_COURSES_BY_CODE["PR07"].title


def test_seed_publishes_pr07_in_practical_module_idempotently(db_session):
    module, uaa = _pr07(db_session)
    assert uaa.slug == SLUG and uaa.is_published and uaa.title == PR07_TITLE and uaa.position == 7
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="PR07").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(pr07_course_sections())
    assert {"PR01", "PR05", "PR06", "PR07", "PR11"} <= set(plan.published_uaas(db_session))
    # Navigation : EX01 (position 6, après PR06) reste avant PR07.
    ordered = [u.code for u in sorted(module.uaas, key=lambda u: (u.position, u.id))]
    assert ordered.index("PR06") < ordered.index("EX01") < ordered.index("PR07")
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_reserves_and_documents(db_session):
    module, uaa = _pr07(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert import_practical_bank(db_session, module, uaa) == len(PRACTICE_ITEMS) + len(EXAM_ITEMS)
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    usages = [question_usage(q) for q in questions]
    assert usages.count("practice") == len(PRACTICE_ITEMS) and usages.count("exam") == 10


def test_correction_context_is_pr07_specific():
    context = _pedagogical_context_for("PR07")
    assert context is get_practical_context("PR07")
    assert context.course_key == SLUG
    notions = " ".join(context.allowed_notions)
    assert "mbr2gpt" in notions and "TPM 2.0" in notions and "SHA-256" in notions and "VT-x" in notions
    assert "mot-clé" in context.constraints and "32 à 64" in context.constraints


# =============================================================================================
# 6. Pages et sessions
# =============================================================================================


def test_course_page_renders_figures_and_exercises(client, db_session):
    _pr07(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert len(ids) == len(set(ids)) and set(ids) >= {f"fig-{f.key}" for f in PR07_FIGURES}
    assert html.count('class="jc-exercise-card"') == len(PRACTICE_ITEMS)
    assert "<details open" not in html
    assert 'href="/ampcr-pratique"' in html and f"/uaa/{SLUG}/exam" in html
    assert "<table" in html


def test_practical_home_and_matrix_show_pr07(client, db_session):
    _pr07(db_session)
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and re.search(r"12 cours publiés sur 30 prévus", _text(home))
    for req in REQ:
        assert plan.requirement_status(req, {"PR07"}) == plan.STATUS_PARTIAL
    assert plan.VALIDATED_REQUIREMENT_IDS == frozenset()
    assert client.get("/ampcr-pratique/matrice").status_code == 200


@pytest.mark.parametrize("mode", ["practice", "exam"])
def test_sessions_draw_only_from_their_reserve_without_generation(authenticated_client, db_session, monkeypatch, mode):
    fake = _patch_fake_provider(monkeypatch)
    _pr07(db_session)
    assert authenticated_client.get(f"/uaa/{SLUG}/{mode}").status_code == 200
    session_url = _start_session(authenticated_client, db_session, SLUG, mode)
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert {question_usage(sq.question_version.question) for sq in session.session_questions} == {mode}
    assert session.question_count == 10
    assert fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"PR07"}
    if mode == "exam":
        page = authenticated_client.get(f"{session_url}?q=1").text
        assert "Corrigé de référence" not in page and "Barème" not in page


def test_exam_lengths_limited_and_score_on_20(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _pr07(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    from app.v1.models import User

    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="PR07", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "/ 20" in html


def test_practice_sessions_with_classification_and_ordering_submit(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr07(db_session)
    for _ in range(2):  # 16 exercices : deux sessions de 10 couvrent toute la réserve
        session_url = _start_session(authenticated_client, db_session, SLUG, "practice")
        _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
        assert authenticated_client.get(session_url).status_code == 200
