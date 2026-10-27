"""Ticket #194 — AMPCR pratique écrite, PR11 « Messages d'erreur Windows/Linux ».

Couvre : données des schémas et captures fictives (stades, arbre, flux, codes et messages
vérifiés, valeurs df cohérentes, partitionnement GPT, largeur des lignes), contenu du cours
(matière 1-6, 5 cas, 16 exercices, mini-examen), banque (types existants dont `ordering`,
documents « console », réserves séparées, idempotence), seed, pages et sessions (strictement
banque, 10 questions, note sur 20). Aucun appel IA réel : `FakeAIProvider` partout."""

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
from app.v1.ampcr_pratique_pr11_bank import (
    EXAM_ITEMS,
    KIND_ANALYSIS,
    KIND_CROSS,
    KIND_PROCEDURE,
    PRACTICE_ITEMS,
    validate_items,
)
from app.v1.ampcr_pratique_pr11_course import PR11_TITLE, pr11_course_sections
from app.v1.ampcr_pratique_pr11_figures import (
    BCD_SCREEN,
    BSOD_SCREEN,
    DEVICE_SCREEN,
    DF_H,
    ERROR_FLOW,
    EVENT_LOG,
    LINUX_GPT,
    PARTITION_FIGURE,
    PR11_FIGURES,
    SCREEN_MAX_CHARS,
    SCREENS,
    STAGE_TREE,
    STAGE_TREE_FIGURE,
    STAGES,
    SYSTEMCTL_SCREEN,
    WINDOWS_GPT,
    WINRE_OPTIONS,
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

SLUG = "ampcr-pratique-pr11"


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _course_text() -> str:
    return _text(" ".join(c for _t, c in pr11_course_sections())).lower()


def _pr11(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "PR11")
    return module, uaa


# =============================================================================================
# 1. Schémas et captures fictives : données vérifiées
# =============================================================================================


def test_stages_and_decision_tree_follow_the_ticket_order():
    assert STAGES == (
        "Firmware / POST", "Chargeur d'amorçage", "Noyau / système", "Ouverture de session", "Service",
        "Application", "Pilote", "Périphérique", "Stockage", "Réseau",
    )
    questions = " ".join(q for q, _ in STAGE_TREE).lower()
    order = [questions.index(w) for w in ("firmware", "chargeur", "système démarre", "session", "services",
                                          "application", "matériel", "données", "réseau")]
    assert order == sorted(order)
    assert [int(n) for n in re.findall(r'data-step="(\d+)"', STAGE_TREE_FIGURE.svg)] == list(range(1, len(STAGE_TREE) + 1))
    advice = " ".join(n for _, n in STAGE_TREE).lower()
    assert "formater" not in advice and "réinstaller" not in advice


def test_error_flow_is_read_hypothesis_test_action_validation():
    assert [step for step, _ in ERROR_FLOW] == ["Lire", "Hypothèse", "Test", "Action", "Validation"]


def test_capture_texts_use_verified_messages_and_codes():
    assert "Code d'erreur : 0xc000000f" in BCD_SCREEN
    assert "Fichier : \\EFI\\Microsoft\\Boot\\BCD" in BCD_SCREEN
    assert "Code d'arrêt : DRIVER_IRQL_NOT_LESS_OR_EQUAL" in BSOD_SCREEN
    assert any("(Code 43)" in line for line in DEVICE_SCREEN)
    assert {(source, event_id) for _l, _w, source, event_id, _m in EVENT_LOG} >= {
        ("Kernel-Power", 41), ("EventLog", 6008), ("BugCheck", 1001)
    }
    # 0xD1 = DRIVER_IRQL_NOT_LESS_OR_EQUAL : même code dans l'écran bleu et le journal.
    assert any("0x000000d1" in m for *_r, m in EVENT_LOG)
    joined = "\n".join(SYSTEMCTL_SCREEN)
    for fragment in ("Active: failed (Result: exit-code)", "ExecStartPre=/usr/sbin/sshd -t",
                     "status=255/EXCEPTION", "Bad", "configuration option: PermitRootLogn"):
        assert fragment in joined
    assert WINRE_OPTIONS[0][0] == "Outil de redémarrage système"


def test_df_values_coherent_and_disk_full():
    for _fs, size, used, free, pct, _mount in DF_H:
        assert 0 <= pct <= 100
    root = next(row for row in DF_H if row[5] == "/")
    assert root[3] == "0" and root[4] == 100


def test_partition_map_drawn_from_data_in_disk_order():
    assert [s.key for s in WINDOWS_GPT] == ["esp", "msr", "c", "winre"]
    assert WINDOWS_GPT[0].lines[1] == "FAT32" and WINDOWS_GPT[1].lines[2] == "16 Mo"
    assert LINUX_GPT[0].key == "esp" and LINUX_GPT[0].lines[1] == "FAT32"
    drawn = re.findall(r'data-partition="([a-z]+)"', PARTITION_FIGURE.svg)
    assert drawn == [s.key for s in WINDOWS_GPT] + [s.key for s in LINUX_GPT]


def test_screen_lines_fit_and_figures_are_valid_accessible_and_fictive():
    for name, lines in SCREENS.items():
        assert all(len(line) <= SCREEN_MAX_CHARS for line in lines), name
    assert len(PR11_FIGURES) >= 10
    keys = [f.key for f in PR11_FIGURES]
    assert len(set(keys)) == len(keys)
    for figure in PR11_FIGURES:
        assert validate_figure(figure) == [], figure.key
        html = str(render_figure(figure))
        assert 'role="img"' in html and "<title" in html and "<desc" in html and "schéma non officiel" in html
    captures = [f for f in PR11_FIGURES if "fictive" in (f.title + f.caption).lower()]
    assert len(captures) >= 8
    for figure in captures:
        if "capture fictive" in figure.title.lower():
            assert "Capture fictive" in figure.svg, figure.key


# =============================================================================================
# 2. Exercices et mini-examen
# =============================================================================================


def test_items_valid_and_counts_match_ticket():
    assert validate_items() == []
    assert len(PRACTICE_ITEMS) >= 15
    kinds = [i.kind for i in PRACTICE_ITEMS]
    assert kinds.count(KIND_ANALYSIS) >= 5
    assert kinds.count(KIND_PROCEDURE) >= 5
    assert kinds.count(KIND_CROSS) >= 3
    assert len(EXAM_ITEMS) == 10 and sum(i.total_points for i in EXAM_ITEMS) == 20
    assert {i.question_type for i in EXAM_ITEMS} <= {"short_answer", "long_answer", "document_analysis"}
    keys = [i.key for i in PRACTICE_ITEMS + EXAM_ITEMS]
    assert len(set(keys)) == len(keys)


def test_no_acronym_question_and_no_isolated_message():
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        text = " ".join((item.title, item.context, *item.instructions))
        assert not re.search(r"que signifie|que veut dire|développe[rz]? l'acronyme", text, re.IGNORECASE), item.key
        assert len(item.context) >= 150, item.key  # situation, lieu, déclencheur : jamais un message seul


def test_items_content_matches_existing_question_types():
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        content = item_content(item, [1, 2][: len(item.documents)])
        validate_content(item.question_type, 1, content)
    ordering = [i for i in PRACTICE_ITEMS if i.question_type == "ordering"]
    assert len(ordering) >= 2
    for item in ordering:
        content = item_content(item, [])
        assert content["correct_order"] != [x["id"] for x in content["items"]]  # jamais déjà dans l'ordre


def test_five_cases_of_the_ticket_and_exam_not_in_course():
    text = _text(" ".join(c for _t, c in pr11_course_sections()))
    for case in ("Cas 1 — Absence de démarrage", "Cas 2 — Écran bleu après l'installation d'un pilote",
                 "Cas 3 — Périphérique en Code 43", "Cas 4 — Linux : service en échec",
                 "Cas 5 — « No space left on device »"):
        assert case in text, case
    course = " ".join(content for _title, content in pr11_course_sections())
    for item in EXAM_ITEMS:
        assert item.context not in course and escape(item.context) not in course, item.key
    for item in PRACTICE_ITEMS:
        assert escape(item.context) in course, item.key


def test_destructive_actions_always_come_with_a_warning():
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        correction = " ".join(item.correction).lower()
        for risky in ("chkdsk /r", "chmod 777", "fsck", "diskpart"):
            if risky in correction:
                assert re.search(r"sauvegard|jamais|ne doit|refus|danger|faille|d'abord|après", correction), (item.key, risky)


# =============================================================================================
# 3. Cours : toute la matière obligatoire (sections 1 à 6 du ticket)
# =============================================================================================


def test_course_teaches_every_mandatory_point():
    sections = pr11_course_sections()
    titles = [t for t, _ in sections]
    assert len(titles) == len(set(titles))
    text = _course_text()
    for notion in (
        # 1 — méthode universelle
        "texte exact", "code", "contexte", "date et heure", "événement déclencheur", "modifications récentes",
        "périmètre", "criticité", "données à préserver", "firmware / post", "chargeur", "ouverture de session",
        "cause probable", "hypothèse", "test de confirmation", "résultat attendu", "action corrective",
        "documentation fiable", "ne jamais inventer une cause unique", "réparation réversible",
        "seulement avec autorisation",
        # 2 — démarrage et partitions
        "no bootable device", "operating system not found", "boot device not found",
        "reboot and select proper boot device", "uefi", "legacy", "ordre de démarrage", "esp",
        "windows boot manager", "bcd", "winre", "réparation du démarrage", "restauration du système",
        "grub", "initramfs", "/etc/fstab", "uuid", "mbr", "gpt", "partition efi",
        "jamais de formatage ni de réinstallation comme premier réflexe",
        # 3 — Windows
        "écran bleu", "stop code", "redémarrage automatique", "gestionnaire de périphériques",
        "périphérique inconnu", "point d'exclamation", "code 10", "code 43", "observateur d'événements",
        "un événement corrélé n'est pas une preuve de causalité", "gestion des disques", "hors ligne",
        "non initialisé", "sans lettre", "services.msc", "dépendances", "ipconfig /all", "nslookup", "tracert",
        "sfc /scannow", "dism /online /cleanup-image /restorehealth", "chkdsk c: /f", "chkdsk c: /r",
        "gestionnaire des tâches", "msconfig", "diagnostic / modification", "windows update", "profil",
        "permissions",
        # 4 — Linux
        "emergency mode", "dependency failed", "permission denied", "read-only file system",
        "no space left on device", "command not found", "journalctl -b", "journalctl -u", "journalctl -p err",
        "systemctl status", "systemctl enable", "dmesg", "df -h", "df -i", "lsblk", "mount", "ip addr",
        "ip route", "ss -tulpn", "resolvectl", "dig", "chmod", "chown", "ne jamais recommander `chmod 777`",
        "apt", "dnf",
        # 5 — réseau, périphériques, corrélation
        "connectivité limitée", "169.254", "dns", "passerelle", "conflit d'adresse ip", "hors ligne",
        "dépendent du constructeur", "chronologie", "coïncidence",
        # 6 — compte rendu
        "demande", "environnement", "preuves", "cause non déterminée", "risques résiduels", "recommandation",
        "clôture", "étapes ordonnées", "justification",
    ):
        assert notion in text, notion


def test_course_flags_requirements_complements_and_fictive_supports():
    text = _text(" ".join(c for _t, c in pr11_course_sections()))
    for req in ("AP-09", "AP-13", "AP-15", "AP-C01", "AP-C03"):
        assert req in text
    assert "Compléments pédagogiques" in text and "fictif" in text.lower()
    assert "aucun n'est une question officielle" in text.lower()


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(t) for t, _ in pr11_course_sections()]
    assert kinds.count("exam") == 1 and kinds.count("exercise") == 1 and kinds.count("example") == 1
    assert kinds[-1] == "info" and "summary" in kinds and "warning" in kinds


# =============================================================================================
# 4. Banque, seed et intégration au moteur
# =============================================================================================


def test_seed_publishes_pr11_in_practical_module_idempotently(db_session):
    module, uaa = _pr11(db_session)
    assert uaa.slug == SLUG and uaa.is_published and uaa.title == PR11_TITLE
    assert PRACTICAL_COURSES_BY_CODE["PR11"].title == plan.COURSE_SLOTS_BY_CODE["PR11"].title == PR11_TITLE
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="PR11").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(pr11_course_sections())
    assert {"PR06", "PR11"} <= set(plan.published_uaas(db_session))
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_reserves_and_console_documents(db_session):
    module, uaa = _pr11(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert import_practical_bank(db_session, module, uaa) == len(PRACTICE_ITEMS) + len(EXAM_ITEMS)
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    usages = [question_usage(q) for q in questions]
    assert usages.count("practice") == len(PRACTICE_ITEMS) and usages.count("exam") == 10
    layouts = [
        (q.current_version.source_document_version.content_json or {}).get("layout", {}).get("kind")
        for q in questions if q.current_version.source_document_version_id
    ]
    assert "console" in layouts and "table" in layouts


def test_correction_context_is_pr11_specific():
    context = _pedagogical_context_for("PR11")
    assert context is get_practical_context("PR11")
    assert context.course_key == "ampcr-pratique-pr11"
    assert "chmod 777" in context.constraints and "mot-clé" in context.constraints


# =============================================================================================
# 5. Pages et sessions
# =============================================================================================


def test_course_page_renders_figures_exercises_and_consoles(client, db_session):
    _pr11(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    assert html.count('class="jc-tech-figure') >= len(PR11_FIGURES)
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert len(ids) == len(set(ids))  # aucune figure répétée (identifiants uniques)
    assert html.count('class="jc-exercise-card"') == len(PRACTICE_ITEMS)
    assert 'class="jc-pr-console"' in html
    assert "<details open" not in html
    assert 'href="/ampcr-pratique"' in html and f"/uaa/{SLUG}/exam" in html


def test_practical_home_and_matrix_show_pr11(client, db_session):
    _pr11(db_session)
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and "cours publiés" in home  # PR15 (#197) publié ensuite
    matrix = _text(client.get("/ampcr-pratique/matrice").text)
    assert "partiel" in matrix
    assert plan.VALIDATED_REQUIREMENT_IDS == audit_proven_ids()  # « validé » : preuves de l'audit #235


@pytest.mark.parametrize("mode", ["practice", "exam"])
def test_sessions_draw_only_from_their_reserve_without_generation(authenticated_client, db_session, monkeypatch, mode):
    fake = _patch_fake_provider(monkeypatch)
    _pr11(db_session)
    assert authenticated_client.get(f"/uaa/{SLUG}/{mode}").status_code == 200
    session_url = _start_session(authenticated_client, db_session, SLUG, mode)
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert {question_usage(sq.question_version.question) for sq in session.session_questions} == {mode}
    assert session.question_count == 10
    assert fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"PR11"}
    if mode == "exam":
        page = authenticated_client.get(f"{session_url}?q=1").text
        assert "Corrigé de référence" not in page and "Barème" not in page


def test_console_document_rendered_in_session(authenticated_client, db_session, monkeypatch):
    _patch_fake_provider(monkeypatch)
    _pr11(db_session)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    for position, sq in enumerate(session.session_questions, start=1):
        doc = sq.question_version.source_document_version
        if doc is not None and (doc.content_json or {}).get("layout", {}).get("kind") == "console":
            page = authenticated_client.get(f"{session_url}?q={position}").text
            assert 'class="jc-sd-console"' in page
            break
    else:
        pytest.fail("aucune question avec document console dans l'examen")


def test_exam_lengths_limited_and_score_on_20(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _pr11(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    from app.v1.models import User

    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="PR11", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "/ 20" in html


def test_practice_session_with_ordering_and_classification_submits(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr11(db_session)
    for _ in range(2):  # 16 exercices : deux sessions couvrent toute la réserve
        session_url = _start_session(authenticated_client, db_session, SLUG, "practice")
        _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
        assert authenticated_client.get(session_url).status_code == 200


def test_obsolete_block_title_is_replaced_on_reseed(db_session):
    from app.models import LessonBlock
    from app.v1.ampcr_pratique_pr11_course import PR11_OBSOLETE_TITLES

    _module, uaa = _pr11(db_session)
    old_title = next(iter(PR11_OBSOLETE_TITLES))
    db_session.add(LessonBlock(uaa_id=uaa.id, title=old_title, type="markdown", content="ancien", position=2))
    db_session.commit()
    seed()
    db_session.expire_all()
    titles = [b.title for b in db_session.get(UAA, uaa.id).lesson_blocks]
    assert old_title not in titles and len(titles) == len(pr11_course_sections())
