"""Banque V1 Français — pilote technique provisoire (ticket #47).

Suit le même principe que `app/v1/bank.py::import_mc01_legacy_to_bank` : import idempotent
d'un socle initial de questions hand-authored, toutes revalidées par le registre #40
(`validate_content`) avant stockage, jamais de solution exposée publiquement.

**Statut explicite : PROVISIONAL_TECHNICAL_SAMPLE** (voir `app.v1.francais_content` pour le
texte source et le détail du statut). 11 questions couvrant les 5 types prioritaires du
ticket (short_answer, long_answer, document_analysis, source_comparison, vocabulary) plus
classification, toutes rattachées au(x) même(s) SourceDocument — jamais de texte dupliqué
par question (chaque question ne porte qu'un `source_document_version_id`/`_ids`,
référence, jamais le texte lui-même, conformément au registre #40)."""

from sqlalchemy.orm import Session

from app.models import UAA, Module
from app.v1 import question_types  # noqa: F401 — enregistre les 26 types (#40) au chargement
from app.v1.francais_content import (
    MAIN_DOCUMENT_TEXT,
    MAIN_DOCUMENT_TITLE,
    SECOND_DOCUMENT_TEXT,
    SECOND_DOCUMENT_TITLE,
)
from app.v1.models import (
    GenerationSource,
    Question,
    create_question,
    create_source_document,
)
from app.v1.question_engine import validate_content


def _francais_c01_questions(main_doc_version_id: int, second_doc_version_id: int) -> list[tuple[str, dict]]:
    return [
        (
            "short_answer",
            {
                "prompt": (
                    "D'après le texte, cite deux avantages du smartphone mentionnés pour "
                    "un usage professionnel."
                ),
                "rubric": (
                    "Réponse correcte si elle mentionne au moins deux éléments parmi : "
                    "facilite la communication entre collègues, permet de consulter les "
                    "emails professionnels en déplacement, donne accès à des outils "
                    "d'organisation (calendriers partagés, listes de tâches)."
                ),
                "max_length": 300,
            },
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "Le texte explique que le smartphone peut réduire la qualité du "
                    "sommeil. Explique avec tes propres mots pourquoi, selon le texte."
                ),
                "rubric": (
                    "Bonne réponse si elle explique que la lumière des écrans et/ou la "
                    "stimulation mentale du défilement de contenu perturbent le sommeil, "
                    "reformulé avec ses propres mots (pas une copie mot pour mot du "
                    "texte)."
                ),
                "max_length": 400,
            },
        ),
        (
            "vocabulary",
            {
                "prompt": (
                    "Dans le texte, à quoi fait référence l'expression « une utilisation "
                    "raisonnée » du smartphone ?"
                ),
                "rubric": (
                    "Bonne réponse si elle indique qu'il s'agit d'utiliser le smartphone "
                    "avec des limites choisies consciemment (par exemple des règles "
                    "personnelles comme ne pas l'utiliser pendant les repas), plutôt que "
                    "de l'interdire totalement ou de l'utiliser sans aucune limite."
                ),
            },
        ),
        (
            "classification",
            {
                "prompt": (
                    "Classe chaque affirmation suivante comme un FAIT rapporté par le "
                    "texte, ou une OPINION/un jugement."
                ),
                "categories": ["Fait", "Opinion"],
                "elements": [
                    "Plusieurs écoles ont interdit le smartphone pendant les heures de cours.",
                    "Le smartphone n'est ni un ennemi ni un allié absolu.",
                    (
                        "Certaines entreprises ont mis en place un droit de ne pas "
                        "répondre aux emails après une certaine heure."
                    ),
                ],
                "correct_categories": [0, 1, 0],
                "explanation": (
                    "Les deux premières affirmations rapportent des faits observables "
                    "décrits dans le texte ; la deuxième est un jugement de valeur de "
                    "l'auteur."
                ),
            },
        ),
        (
            "document_analysis",
            {
                "prompt": (
                    "Identifie un passage du texte qui illustre un usage positif du "
                    "smartphone à l'école, et explique en quoi il illustre cette idée."
                ),
                "source_document_version_id": main_doc_version_id,
                "rubric": (
                    "Bonne réponse si elle cite ou paraphrase un passage pertinent (ex. "
                    "accès immédiat à l'information, applications pédagogiques "
                    "interactives) et explique en quoi ce passage illustre un usage "
                    "positif à l'école."
                ),
                "expected_points": [
                    "Cite ou paraphrase un exemple concret du texte",
                    "Explique en quoi cet exemple est positif",
                ],
            },
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "Reformule en une phrase l'idée développée dans le paragraphe "
                    "consacré à la vie personnelle."
                ),
                "rubric": (
                    "Bonne réponse si elle résume en une phrase que le smartphone "
                    "facilite le contact avec les proches et l'accès à des contenus "
                    "variés, mais peut aussi perturber le sommeil et créer une forme de "
                    "dépendance."
                ),
                "max_length": 300,
            },
        ),
        (
            "short_answer",
            {
                "prompt": "Quelle est l'idée principale du texte ? Résume-la en une ou deux phrases.",
                "rubric": (
                    "Bonne réponse si elle indique que le smartphone présente à la fois "
                    "des avantages réels et des risques documentés, et que le texte "
                    "défend un usage raisonné plutôt qu'une interdiction totale ou un "
                    "usage sans limite."
                ),
                "max_length": 400,
            },
        ),
        (
            "document_analysis",
            {
                "prompt": (
                    "Le texte présente à la fois des avantages et des inconvénients du "
                    "smartphone à l'école, au travail et dans la vie personnelle. "
                    "Identifie deux éléments du texte qui montrent que l'auteur adopte un "
                    "point de vue nuancé plutôt que tranché."
                ),
                "source_document_version_id": main_doc_version_id,
                "rubric": (
                    "Bonne réponse si elle identifie au moins deux éléments montrant la "
                    "nuance : présentation systématique des deux côtés (école/travail/vie "
                    "personnelle), refus explicite d'une position tranchée dans la "
                    "conclusion, proposition d'une « troisième voie »."
                ),
                "expected_points": [
                    "Identifie au moins deux éléments de nuance",
                    "S'appuie sur des passages précis du texte",
                ],
            },
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "Es-tu d'accord avec l'affirmation que le smartphone est « ni un "
                    "ennemi ni un allié absolu » ? Justifie ta réponse en 2 à 3 phrases."
                ),
                "rubric": (
                    "Toute position (d'accord ou pas d'accord) est acceptée si elle est "
                    "justifiée de manière cohérente, éventuellement en lien avec le texte "
                    "ou l'expérience personnelle. Pas de bonne ou mauvaise opinion : "
                    "évaluer la qualité de la justification, pas la position choisie."
                ),
                "max_length": 500,
            },
        ),
        (
            "long_answer",
            {
                "prompt": (
                    "En t'appuyant sur le texte et sur ton expérience personnelle, "
                    "rédige un texte argumenté (plusieurs paragraphes) donnant ton "
                    "opinion sur l'usage du smartphone à l'école. Structure ta réponse "
                    "avec une introduction, au moins deux arguments justifiés, et une "
                    "conclusion."
                ),
                "rubric": (
                    "Évalue : (1) présence d'une structure claire (introduction, "
                    "arguments, conclusion) ; (2) au moins deux arguments distincts et "
                    "justifiés, en lien avec le sujet ; (3) référence possible (mais pas "
                    "obligatoire) au texte fourni ; (4) qualité de l'expression écrite "
                    "adaptée au niveau CESS. Ne juge jamais la position choisie "
                    "(pour/contre/nuancée) elle-même, seulement la qualité argumentative "
                    "et structurelle."
                ),
                "expected_points": [
                    "Structure claire (introduction/développement/conclusion)",
                    "Au moins deux arguments distincts et justifiés",
                    "Expression écrite cohérente et adaptée au niveau CESS",
                ],
                "max_length": 6000,
            },
        ),
        (
            "source_comparison",
            {
                "prompt": (
                    "Compare la position du texte principal avec celle du second texte "
                    "concernant l'usage du smartphone à l'école. Identifie au moins une "
                    "différence claire entre les deux points de vue."
                ),
                "source_document_version_ids": [main_doc_version_id, second_doc_version_id],
                "rubric": (
                    "Bonne réponse si elle identifie que le texte principal défend un "
                    "usage raisonné et nuancé (ni interdiction totale ni usage libre), "
                    "alors que le second texte défend une interdiction totale et stricte "
                    "pendant toute la journée de cours, jugée plus simple à faire "
                    "respecter."
                ),
                "expected_points": [
                    "Identifie la position nuancée du texte principal",
                    "Identifie la position stricte du second texte",
                    "Formule une différence claire entre les deux",
                ],
            },
        ),
    ]


def import_francais_c01_to_bank(db: Session, module: Module, uaa: UAA) -> int:
    """Importe le socle initial Français C01 (2 SourceDocument + 11 questions) dans la
    banque V1, scopé à `uaa`. Idempotent au niveau processus : si des Question existent
    déjà pour cette UAA avec `generation_source=IMPORTED`, ne réimporte rien — même
    garantie que `app.v1.bank.import_mc01_legacy_to_bank`."""
    already_imported = (
        db.query(Question).filter_by(uaa_id=uaa.id, generation_source=GenerationSource.IMPORTED).count()
    )
    if already_imported:
        return 0

    main_document = create_source_document(
        db, title=MAIN_DOCUMENT_TITLE, content_text=MAIN_DOCUMENT_TEXT, module_id=module.id
    )
    second_document = create_source_document(
        db, title=SECOND_DOCUMENT_TITLE, content_text=SECOND_DOCUMENT_TEXT, module_id=module.id
    )
    db.flush()

    imported = 0
    for question_type, content in _francais_c01_questions(
        main_document.current_version_id, second_document.current_version_id
    ):
        validate_content(question_type, 1, content)
        create_question(
            db,
            module_id=module.id,
            uaa_id=uaa.id,
            question_type=question_type,
            content_json=content,
            generation_source=GenerationSource.IMPORTED,
            source_document_version_id=content.get("source_document_version_id"),
        )
        imported += 1
    db.flush()
    return imported
