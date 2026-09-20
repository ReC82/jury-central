"""Banque V1 Français — FR01→FR05 (ticket #94, PHASE A).

Même principe que `app.v1.francais_bank::import_francais_c01_to_bank` (#47/#77/#79) et
`app.v1.bank::import_mc01_legacy_to_bank` : import idempotent, hand-authored, revalidé par
le registre #40 (`validate_content`) avant stockage. **Statut explicite :
PROVISIONAL_TECHNICAL_SAMPLE** (voir `app.v1.francais_fr01_05_content`) — jamais un examen
CESS officiel.

Règle absolue du ticket #94 (§ 6/§ 8) : AUCUNE question ne référence un texte sans un
`SourceDocumentVersion` réellement rattaché (`source_document_version_id`/`_ids`) —
jamais de « D'après le texte » orphelin. Vérifié explicitement par
`tests/test_ticket94_french_20_courses.py::test_no_orphan_document_dependent_questions_in_fr01_05`."""

from sqlalchemy.orm import Session

from app.models import UAA, Module
from app.v1 import question_types  # noqa: F401 — enregistre les 26 types (#40) au chargement
from app.v1.francais_fr01_05_content import (
    FR01_D1_TEXT,
    FR01_D1_TITLE,
    FR01_D2_TEXT,
    FR01_D2_TITLE,
    FR01_MINITEST_A_TEXT,
    FR01_MINITEST_A_TITLE,
    FR01_MINITEST_B_TEXT,
    FR01_MINITEST_B_TITLE,
    FR02_ARTICLE_TEXT,
    FR02_ARTICLE_TITLE,
    FR02_INFO_TEXT,
    FR02_INFO_TITLE,
    FR02_LETTER_TEXT,
    FR02_LETTER_TITLE,
    FR02_MINITEST_TEXT,
    FR02_MINITEST_TITLE,
    FR03_MINITEST_TEXT,
    FR03_MINITEST_TITLE,
    FR03_TEXT1_TEXT,
    FR03_TEXT1_TITLE,
    FR03_TEXT2_TEXT,
    FR03_TEXT2_TITLE,
    FR04_DISORGANIZED_TEXT,
    FR04_DISORGANIZED_TITLE,
    FR04_IDEAS_JUMBLE_TEXT,
    FR04_IDEAS_JUMBLE_TITLE,
    FR04_MINITEST_TEXT,
    FR04_MINITEST_TITLE,
    FR05_FLAWED1_TEXT,
    FR05_FLAWED1_TITLE,
    FR05_FLAWED2_TEXT,
    FR05_FLAWED2_TITLE,
    FR05_MINITEST_TEXT,
    FR05_MINITEST_TITLE,
)
from app.v1.models import (
    GenerationSource,
    Question,
    create_question,
    create_source_document,
)
from app.v1.question_engine import validate_content


def _import_course(db: Session, module: Module, uaa: UAA, questions: list[tuple[str, dict]]) -> int:
    """Boucle d'import partagée par les 5 fonctions ci-dessous — même garantie
    d'idempotence que `import_francais_c01_to_bank` (scopée par `uaa_id`, jamais de
    doublon si déjà importé)."""
    already_imported = (
        db.query(Question).filter_by(uaa_id=uaa.id, generation_source=GenerationSource.IMPORTED).count()
    )
    if already_imported:
        return 0
    imported = 0
    for question_type, content in questions:
        validate_content(question_type, 1, content)
        source_doc_id = content.get("source_document_version_id")
        create_question(
            db,
            module_id=module.id,
            uaa_id=uaa.id,
            question_type=question_type,
            content_json=content,
            generation_source=GenerationSource.IMPORTED,
            source_document_version_id=source_doc_id,
        )
        imported += 1
    db.flush()
    return imported


# =============================================================================================
# FR01 — Comprendre une consigne d'examen
# =============================================================================================


def import_francais_fr01_to_bank(db: Session, module: Module, uaa: UAA) -> int:
    already_imported = (
        db.query(Question).filter_by(uaa_id=uaa.id, generation_source=GenerationSource.IMPORTED).count()
    )
    if already_imported:
        return 0

    minitest_a = create_source_document(db, title=FR01_MINITEST_A_TITLE, content_text=FR01_MINITEST_A_TEXT, module_id=module.id)
    minitest_b = create_source_document(db, title=FR01_MINITEST_B_TITLE, content_text=FR01_MINITEST_B_TEXT, module_id=module.id)
    d1 = create_source_document(db, title=FR01_D1_TITLE, content_text=FR01_D1_TEXT, module_id=module.id)
    d2 = create_source_document(db, title=FR01_D2_TITLE, content_text=FR01_D2_TEXT, module_id=module.id)
    db.flush()
    a, b, d1_id, d2_id = (
        minitest_a.current_version_id, minitest_b.current_version_id,
        d1.current_version_id, d2.current_version_id,
    )

    questions: list[tuple[str, dict]] = [
        (
            "short_answer",
            {
                "prompt": (
                    "Relève, dans le texte « Le tri des déchets sur le lieu de travail », "
                    "deux mesures concrètes proposées par le responsable qualité pour "
                    "améliorer le tri."
                ),
                "source_document_version_id": a,
                "rubric": (
                    "Bonne réponse si elle cite au moins deux mesures parmi : affiche plus "
                    "visible au-dessus de la poubelle des emballages recyclables, "
                    "présentation du tri lors de l'accueil des nouveaux employés."
                ),
                "max_length": 300,
            },
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "Résume en une seule phrase le problème principal identifié dans le "
                    "texte « La pause de midi dans les grandes entreprises »."
                ),
                "source_document_version_id": b,
                "rubric": (
                    "Bonne réponse si elle indique, en une phrase de synthèse, que la "
                    "réduction de la durée de la pause de midi peut nuire à la qualité de "
                    "l'alimentation et augmenter la fatigue en fin de journée."
                ),
                "max_length": 250,
            },
        ),
        (
            "source_comparison",
            {
                "prompt": (
                    "Compare la vision de la direction (Document 1) et celle des employés "
                    "(Document 2) sur le télétravail chez Berteau & Fils : sur quel point "
                    "précis leurs avis divergent-ils le plus ?"
                ),
                "source_document_version_ids": [d1_id, d2_id],
                "rubric": (
                    "Bonne réponse si elle identifie que la direction met en avant "
                    "l'efficacité/l'organisation alors que les employés soulignent la "
                    "perte de lien social, en s'appuyant sur un élément précis de chaque "
                    "document."
                ),
                "expected_points": [
                    "Mentionne le point de vue de la direction (organisation/productivité)",
                    "Mentionne le point de vue des employés (isolement/perte de contact)",
                    "Identifie explicitement le désaccord entre les deux",
                ],
            },
        ),
        (
            "long_answer",
            {
                "prompt": (
                    "Rédige une réponse complète à la consigne suivante appliquée au "
                    "texte « La pause de midi dans les grandes entreprises » : « Relève "
                    "une conséquence négative possible d'une pause trop courte, puis "
                    "explique en quoi l'aménagement proposé par certaines entreprises y "
                    "répond. »"
                ),
                "source_document_version_id": b,
                "rubric": (
                    "3 points : identification claire d'une conséquence négative citée "
                    "dans le texte (fatigue en fin d'après-midi liée à une alimentation "
                    "rapide) (1 point) ; explication de l'aménagement proposé (espaces de "
                    "restauration plus agréables, micro-ondes en nombre suffisant, tables "
                    "éloignées des postes de travail) (1 point) ; lien explicite établi "
                    "entre les deux, montrant en quoi l'aménagement répond au problème "
                    "(1 point)."
                ),
                "max_score": 3.0,
            },
        ),
        (
            "classification",
            {
                "prompt": (
                    "Classe chaque verbe de consigne selon ce qu'il demande le plus "
                    "souvent à l'examen."
                ),
                "categories": ["Citer un élément précis du texte", "Donner un avis personnel argumenté"],
                "elements": ["Relève", "Cite", "Apprécie", "Argumente"],
                "correct_categories": [0, 0, 1, 1],
                "explanation": (
                    "« Relève » et « Cite » demandent de repérer un élément exact du "
                    "texte ; « Apprécie » et « Argumente » demandent un avis personnel "
                    "justifié, au-delà du simple repérage."
                ),
            },
        ),
        (
            "classification",
            {
                "prompt": (
                    "La consigne suivante est donnée à l'examen : « Compare les deux "
                    "documents fournis et relève deux différences. » Classe chaque "
                    "élément de cette consigne dans la bonne catégorie."
                ),
                "categories": ["Verbe opérateur", "Nombre d'éléments attendus", "Support à utiliser"],
                "elements": ["Compare / relève", "deux différences", "les deux documents fournis"],
                "correct_categories": [0, 1, 2],
                "explanation": (
                    "« Compare / relève » indique l'action à réaliser (verbe opérateur), "
                    "« deux différences » précise le nombre d'éléments attendus, et « les "
                    "deux documents fournis » indique le support sur lequel s'appuyer."
                ),
            },
        ),
        (
            "vocabulary",
            {
                "prompt": "Que demande un correcteur quand une consigne utilise le verbe « expliciter » ?",
                "rubric": (
                    "Bonne réponse si elle indique qu'il faut rendre clair et complet ce "
                    "qui était seulement suggéré ou incomplet, en développant l'idée "
                    "plutôt qu'en se contentant de la mentionner."
                ),
            },
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "La consigne suivante comporte plusieurs exigences : « Cite deux "
                    "mesures prises par l'entreprise pour améliorer le tri des déchets, "
                    "puis explique pourquoi la deuxième mesure proposée te semble plus "
                    "efficace que la première. » Combien d'éléments distincts cette "
                    "consigne demande-t-elle, et lesquels ?"
                ),
                "source_document_version_id": a,
                "accepted_answers": [
                    "trois éléments : citer deux mesures, puis expliquer pourquoi la deuxième semble plus efficace",
                    "3 éléments : deux mesures citées et une explication comparative",
                ],
                "rubric": (
                    "Bonne réponse si elle identifie 3 éléments : (1) citer une première "
                    "mesure, (2) citer une deuxième mesure, (3) expliquer en quoi la "
                    "deuxième est jugée plus efficace que la première."
                ),
                "max_length": 300,
            },
        ),
    ]

    return _import_course(db, module, uaa, questions)


# =============================================================================================
# FR02 — Lire et comprendre un document
# =============================================================================================


def import_francais_fr02_to_bank(db: Session, module: Module, uaa: UAA) -> int:
    already_imported = (
        db.query(Question).filter_by(uaa_id=uaa.id, generation_source=GenerationSource.IMPORTED).count()
    )
    if already_imported:
        return 0

    minitest = create_source_document(db, title=FR02_MINITEST_TITLE, content_text=FR02_MINITEST_TEXT, module_id=module.id)
    article = create_source_document(db, title=FR02_ARTICLE_TITLE, content_text=FR02_ARTICLE_TEXT, module_id=module.id)
    info = create_source_document(db, title=FR02_INFO_TITLE, content_text=FR02_INFO_TEXT, module_id=module.id)
    letter = create_source_document(db, title=FR02_LETTER_TITLE, content_text=FR02_LETTER_TEXT, module_id=module.id)
    db.flush()
    m, art, inf, let = (
        minitest.current_version_id, article.current_version_id,
        info.current_version_id, letter.current_version_id,
    )

    questions: list[tuple[str, dict]] = [
        (
            "short_answer",
            {
                "prompt": "Quelle est l'idée principale du texte sur les bornes de recharge électrique ?",
                "source_document_version_id": m,
                "rubric": (
                    "Bonne réponse si elle indique que l'entreprise a installé des bornes "
                    "de recharge pour répondre à la demande croissante des employés "
                    "possédant un véhicule électrique."
                ),
                "max_length": 300,
            },
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "Relève deux idées secondaires qui complètent l'idée principale du "
                    "texte (par exemple sur le fonctionnement des bornes ou leur coût)."
                ),
                "source_document_version_id": m,
                "rubric": (
                    "Bonne réponse si elle cite au moins deux éléments parmi : le système "
                    "de réservation en ligne, la limite de deux heures par créneau, la "
                    "prise en charge du coût par l'entreprise, la réévaluation prévue "
                    "dans un an, la réaction de certains employés sans véhicule "
                    "électrique."
                ),
                "max_length": 400,
            },
        ),
        (
            "document_analysis",
            {
                "prompt": (
                    "Explique, en citant un passage précis du texte, pourquoi certains "
                    "employés ont exprimé une frustration face à l'installation des "
                    "bornes de recharge."
                ),
                "source_document_version_id": m,
                "rubric": (
                    "Bonne réponse si elle cite ou paraphrase le passage sur la gratuité "
                    "jugée réservée à une minorité, et explique que ces employés ne "
                    "bénéficient pas de cet avantage faute de véhicule électrique."
                ),
                "expected_points": [
                    "Cite ou paraphrase le passage pertinent",
                    "Explique la raison de la frustration",
                ],
            },
        ),
        (
            "vocabulary",
            {
                "prompt": "Dans le texte, que signifie l'expression « partagées équitablement » appliquée aux bornes de recharge ?",
                "source_document_version_id": m,
                "rubric": (
                    "Bonne réponse si elle indique que chaque employé peut utiliser les "
                    "bornes de façon égale, grâce au système de réservation limitant "
                    "chaque créneau à deux heures."
                ),
            },
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "Quel est le genre de ce texte (article informatif, note interne, "
                    "lettre...) ? Justifie ta réponse à l'aide d'un élément du texte."
                ),
                "source_document_version_id": m,
                "rubric": (
                    "Bonne réponse si elle identifie un texte informatif/article "
                    "d'entreprise et justifie par la présence de faits datés, chiffrés et "
                    "d'explications neutres, sans adresse directe à un destinataire "
                    "précis."
                ),
                "max_length": 300,
            },
        ),
        (
            "short_answer",
            {
                "prompt": "Dans cette lettre, qui est l'auteur, qui est le destinataire, et quelle est l'intention de l'auteur ?",
                "source_document_version_id": let,
                "rubric": (
                    "Bonne réponse si elle identifie Nadia Ferreira comme auteure, Madame "
                    "Kowalski comme destinataire, et une demande de congé comme intention."
                ),
                "max_length": 300,
            },
        ),
        (
            "classification",
            {
                "prompt": "Classe chaque affirmation suivante comme un FAIT rapporté par le texte, ou une OPINION exprimée par un employé.",
                "source_document_version_id": m,
                "categories": ["Fait", "Opinion"],
                "elements": [
                    "Six bornes de recharge ont été installées en mars.",
                    "L'avantage est réservé à une minorité.",
                    "Le nombre d'employés possédant un véhicule électrique est passé de trois à dix-sept.",
                ],
                "correct_categories": [0, 1, 0],
                "explanation": (
                    "La première et la troisième affirmations sont des faits vérifiables "
                    "décrits dans le texte ; la deuxième est un jugement exprimé par "
                    "certains employés."
                ),
            },
        ),
        (
            "document_analysis",
            {
                "prompt": (
                    "Identifie un passage de l'article qui explique pourquoi la nouvelle "
                    "ligne de bus était attendue par les entreprises de la zone "
                    "industrielle, et explique en quoi il illustre ce besoin."
                ),
                "source_document_version_id": art,
                "rubric": (
                    "Bonne réponse si elle cite ou paraphrase le passage sur la difficulté "
                    "de recruter des personnes sans permis/voiture, et explique que la "
                    "ligne de bus facilite l'accès à l'emploi."
                ),
                "expected_points": [
                    "Cite ou paraphrase un passage pertinent",
                    "Explique le lien avec le besoin des entreprises",
                ],
            },
        ),
        (
            "long_answer",
            {
                "prompt": (
                    "Résume en quelques phrases le fonctionnement d'une caisse "
                    "enregistreuse moderne décrit dans le texte, en respectant l'ordre "
                    "des informations données (gestion des stocks, puis analyse des "
                    "habitudes clients, puis sécurité)."
                ),
                "source_document_version_id": inf,
                "rubric": (
                    "3 points : mention de la gestion des stocks en temps réel (1 point) ; "
                    "mention de l'analyse des habitudes clients (1 point) ; mention des "
                    "fonctions de sécurité, dans un ordre globalement fidèle à celui du "
                    "texte (1 point). Pénaliser une réponse qui copie le texte mot pour "
                    "mot plutôt que de le résumer."
                ),
                "max_score": 3.0,
            },
        ),
    ]

    return _import_course(db, module, uaa, questions)


# =============================================================================================
# FR03 — Implicite, inférences et justification
# =============================================================================================


def import_francais_fr03_to_bank(db: Session, module: Module, uaa: UAA) -> int:
    already_imported = (
        db.query(Question).filter_by(uaa_id=uaa.id, generation_source=GenerationSource.IMPORTED).count()
    )
    if already_imported:
        return 0

    text1 = create_source_document(db, title=FR03_TEXT1_TITLE, content_text=FR03_TEXT1_TEXT, module_id=module.id)
    text2 = create_source_document(db, title=FR03_TEXT2_TITLE, content_text=FR03_TEXT2_TEXT, module_id=module.id)
    minitest = create_source_document(db, title=FR03_MINITEST_TITLE, content_text=FR03_MINITEST_TEXT, module_id=module.id)
    db.flush()
    t1, t2, m = text1.current_version_id, text2.current_version_id, minitest.current_version_id

    questions: list[tuple[str, dict]] = [
        (
            "document_analysis",
            {
                "prompt": (
                    "Le texte ne dit jamais explicitement que Karim est nerveux pour son "
                    "premier jour de travail. Relève un indice précis du texte qui le "
                    "suggère, et explique ton raisonnement en suivant la méthode INDICE → "
                    "RAISONNEMENT → CONCLUSION."
                ),
                "source_document_version_id": t1,
                "rubric": (
                    "Bonne réponse si elle cite un indice précis (arrivée très en avance, "
                    "main tremblante, reste debout au lieu de s'asseoir, répète "
                    "« enchanté », faillit renverser son porte-documents...), explique le "
                    "raisonnement qui relie cet indice à la nervosité, et conclut "
                    "clairement. Refuser une réponse qui invente un fait absent du texte."
                ),
                "expected_points": [
                    "Cite un indice précis du texte",
                    "Explique le raisonnement (pourquoi cet indice suggère la nervosité)",
                    "Formule une conclusion claire",
                ],
            },
        ),
        (
            "long_answer",
            {
                "prompt": (
                    "Le texte suggère que Karim est quelqu'un de prudent et préparé, sans "
                    "le dire explicitement. Justifie cette conclusion à l'aide d'au moins "
                    "deux indices précis du texte."
                ),
                "source_document_version_id": t1,
                "rubric": (
                    "3 points : premier indice pertinent cité (relit le plan trois fois, "
                    "arrive vingt minutes en avance, prend des notes sur un carnet malgré "
                    "l'assurance d'une formation le lendemain) (1 point) ; deuxième "
                    "indice pertinent cité et distinct du premier (1 point) ; lien "
                    "explicite établi entre les indices et la conclusion « prudent/"
                    "préparé », sans invention (1 point)."
                ),
                "max_score": 3.0,
            },
        ),
        (
            "document_analysis",
            {
                "prompt": (
                    "Le rapport du responsable qualité reste mesuré dans son ton, mais "
                    "laisse entendre que la situation de la ligne 3 est plus "
                    "préoccupante qu'il n'y paraît. Relève deux indices qui le suggèrent."
                ),
                "source_document_version_id": t2,
                "rubric": (
                    "Bonne réponse si elle cite au moins deux indices parmi : les "
                    "interventions de maintenance hors horaires habituels, le recours à "
                    "une autre ligne pour respecter les délais, la recommandation d'un "
                    "contrôle approfondi avant la fin du trimestre, la phrase soulignée "
                    "par le directeur."
                ),
                "expected_points": [
                    "Cite un premier indice pertinent",
                    "Cite un deuxième indice pertinent, distinct du premier",
                ],
            },
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "Pourquoi le directeur a-t-il souligné la dernière phrase du rapport "
                    "en réunion, selon toi ? Appuie ta réponse sur un élément précis du "
                    "texte."
                ),
                "source_document_version_id": t2,
                "rubric": (
                    "Bonne réponse si elle relie cette phrase (« la situation reste sous "
                    "contrôle, mais elle mériterait de ne pas se prolonger... ») à une "
                    "inquiétude du directeur sur la durée du problème, malgré le ton "
                    "rassurant du reste du rapport."
                ),
                "max_length": 400,
            },
        ),
        (
            "long_answer",
            {
                "prompt": (
                    "Le texte ne dit jamais explicitement pourquoi Sandra a démissionné. "
                    "Identifie au moins deux indices du texte qui suggèrent une piste "
                    "plausible, puis explique ton raisonnement complet (INDICE → "
                    "RAISONNEMENT → CONCLUSION) pour chacun."
                ),
                "source_document_version_id": m,
                "rubric": (
                    "4 points : premier indice précis cité (1 point) ; raisonnement "
                    "explicite reliant cet indice à une conclusion plausible (1 point) ; "
                    "deuxième indice précis cité, distinct du premier (1 point) ; "
                    "raisonnement explicite pour ce second indice (1 point). Accepter "
                    "toute conclusion raisonnable et bien justifiée (par exemple : "
                    "reconversion professionnelle, envie de changement de vie, projet "
                    "personnel lié à la vente) — ne jamais exiger UNE seule réponse "
                    "« correcte » : c'est la qualité du raisonnement à partir d'indices "
                    "réels qui compte, jamais une réponse inventée sans appui textuel."
                ),
                "max_score": 4.0,
            },
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "Le texte précise que Sandra a écrit sa lettre de démission à la "
                    "main, alors qu'elle affirmait habituellement tout préférer taper à "
                    "l'ordinateur. Que peut-on raisonnablement en déduire sur son état "
                    "d'esprit à ce moment-là ? Justifie."
                ),
                "source_document_version_id": m,
                "rubric": (
                    "Bonne réponse si elle relève ce contraste avec l'habitude de Sandra "
                    "et en déduit une émotion ou une réflexion plus personnelle/sincère "
                    "que d'habitude, sans inventer de détail absent du texte."
                ),
                "max_length": 350,
            },
        ),
        (
            "classification",
            {
                "prompt": "Classe chaque affirmation sur Karim comme EXPLICITE (dite clairement dans le texte) ou IMPLICITE (à déduire).",
                "source_document_version_id": t1,
                "categories": ["Explicite", "Implicite"],
                "elements": [
                    "Karim arrive vingt minutes avant l'heure indiquée sur son contrat.",
                    "Karim est stressé par son premier jour.",
                    "Thomas arrive avec dix minutes de retard.",
                ],
                "correct_categories": [0, 1, 0],
                "explanation": (
                    "La première et la troisième affirmations sont écrites noir sur "
                    "blanc dans le texte ; la deuxième est une conclusion à déduire des "
                    "indices (main tremblante, arrivée en avance, etc.), jamais affirmée "
                    "telle quelle."
                ),
            },
        ),
        (
            "vocabulary",
            {
                "prompt": "Quelle est la différence entre une « inférence » et une « invention » lorsqu'on répond à une question de compréhension de texte ?",
                "rubric": (
                    "Bonne réponse si elle explique qu'une inférence s'appuie sur des "
                    "indices réellement présents dans le texte pour conclure quelque "
                    "chose de non écrit, alors qu'une invention ajoute une information "
                    "sans aucun appui dans le texte."
                ),
            },
        ),
    ]

    return _import_course(db, module, uaa, questions)


# =============================================================================================
# FR04 — Écrire correctement et organiser ses idées
# =============================================================================================


def import_francais_fr04_to_bank(db: Session, module: Module, uaa: UAA) -> int:
    already_imported = (
        db.query(Question).filter_by(uaa_id=uaa.id, generation_source=GenerationSource.IMPORTED).count()
    )
    if already_imported:
        return 0

    ideas = create_source_document(db, title=FR04_IDEAS_JUMBLE_TITLE, content_text=FR04_IDEAS_JUMBLE_TEXT, module_id=module.id)
    disorganized = create_source_document(db, title=FR04_DISORGANIZED_TITLE, content_text=FR04_DISORGANIZED_TEXT, module_id=module.id)
    minitest = create_source_document(db, title=FR04_MINITEST_TITLE, content_text=FR04_MINITEST_TEXT, module_id=module.id)
    db.flush()
    i, d, m = ideas.current_version_id, disorganized.current_version_id, minitest.current_version_id

    questions: list[tuple[str, dict]] = [
        (
            "long_answer",
            {
                "prompt": (
                    "À partir des idées en vrac présentées dans le document, rédige un "
                    "texte organisé (introduction, développement, conclusion) proposant "
                    "un aménagement d'horaires à ta hiérarchie. Utilise des connecteurs "
                    "logiques et respecte un ordre cohérent."
                ),
                "source_document_version_id": i,
                "rubric": (
                    "4 points : introduction présentant clairement la demande (1 point) ; "
                    "développement reprenant les arguments/contraintes du document de "
                    "façon organisée, avec connecteurs logiques (1 point) ; conclusion "
                    "cohérente, par exemple la proposition de période d'essai (1 point) ; "
                    "aucune idée du document oubliée ou déformée (1 point)."
                ),
                "max_score": 4.0,
            },
        ),
        (
            "document_analysis",
            {
                "prompt": (
                    "Le document présente quatre paragraphes d'un compte-rendu de panne, "
                    "dans le désordre. Indique dans quel ordre logique ils devraient "
                    "apparaître (par leur lettre), et explique brièvement pourquoi."
                ),
                "source_document_version_id": d,
                "rubric": (
                    "Bonne réponse si elle propose l'ordre B (panne constatée), A "
                    "(intervention du technicien), D (durée/conséquence sur la "
                    "production), C (résolution et recommandation), et justifie par un "
                    "ordre chronologique logique (constat → intervention → conséquence → "
                    "résolution)."
                ),
                "expected_points": [
                    "Propose un ordre cohérent (B, A, D, C ou équivalent justifié)",
                    "Justifie par la logique chronologique du récit",
                ],
            },
        ),
        (
            "long_answer",
            {
                "prompt": (
                    "Réécris entièrement le compte-rendu de panne en remettant les "
                    "paragraphes dans un ordre logique et en ajoutant les connecteurs "
                    "nécessaires pour assurer une bonne progression du texte."
                ),
                "source_document_version_id": d,
                "rubric": (
                    "3 points : les quatre paragraphes sont présents et dans un ordre "
                    "logique (1 point) ; des connecteurs logiques assurent la "
                    "progression entre les paragraphes (1 point) ; aucune information du "
                    "texte original n'est perdue ou inventée (1 point)."
                ),
                "max_score": 3.0,
            },
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "Parmi les idées en vrac du document, laquelle constitue la "
                    "contrainte la plus importante à respecter dans la proposition "
                    "d'aménagement d'horaires ? Justifie."
                ),
                "source_document_version_id": i,
                "rubric": (
                    "Bonne réponse si elle identifie la compatibilité avec les réunions "
                    "d'équipe du lundi matin comme contrainte structurante (ou une autre "
                    "contrainte du document correctement justifiée), en expliquant "
                    "pourquoi elle conditionne la faisabilité de la demande."
                ),
                "max_length": 350,
            },
        ),
        (
            "long_answer",
            {
                "prompt": (
                    "Rédige le courriel de réclamation décrit dans la situation, en "
                    "respectant le destinataire, l'intention et le genre attendu, et en "
                    "organisant clairement les informations fournies."
                ),
                "source_document_version_id": m,
                "rubric": (
                    "4 points : formule d'ouverture et de politesse adaptées à un "
                    "courriel professionnel (1 point) ; explication claire du problème "
                    "avec la référence de commande et le nombre de boîtes concernées "
                    "(1 point) ; demande précise (remplacement avant la fin de la "
                    "semaine) (1 point) ; ton ferme mais poli, sans remettre en cause "
                    "l'ensemble de la relation commerciale (1 point)."
                ),
                "max_score": 4.0,
            },
        ),
        (
            "vocabulary",
            {
                "prompt": "Quel est le rôle d'un connecteur logique comme « cependant » ou « par conséquent » dans un texte ?",
                "rubric": (
                    "Bonne réponse si elle explique qu'un connecteur logique relie deux "
                    "idées en précisant leur relation (opposition, conséquence, "
                    "addition...), ce qui rend la progression du texte plus claire pour "
                    "le lecteur."
                ),
            },
        ),
        (
            "short_answer",
            {
                "prompt": "Cite les trois grandes parties attendues dans un texte organisé, et le rôle de chacune.",
                "accepted_answers": [
                    "introduction, développement, conclusion",
                    "une introduction, un développement et une conclusion",
                ],
                "rubric": (
                    "Bonne réponse si elle cite introduction (présente le sujet), "
                    "développement (expose les idées de façon organisée) et conclusion "
                    "(résume ou clôt le propos)."
                ),
                "max_length": 300,
            },
        ),
    ]

    return _import_course(db, module, uaa, questions)


# =============================================================================================
# FR05 — Corriger et améliorer un texte
# =============================================================================================


def import_francais_fr05_to_bank(db: Session, module: Module, uaa: UAA) -> int:
    already_imported = (
        db.query(Question).filter_by(uaa_id=uaa.id, generation_source=GenerationSource.IMPORTED).count()
    )
    if already_imported:
        return 0

    flawed1 = create_source_document(db, title=FR05_FLAWED1_TITLE, content_text=FR05_FLAWED1_TEXT, module_id=module.id)
    flawed2 = create_source_document(db, title=FR05_FLAWED2_TITLE, content_text=FR05_FLAWED2_TEXT, module_id=module.id)
    minitest = create_source_document(db, title=FR05_MINITEST_TITLE, content_text=FR05_MINITEST_TEXT, module_id=module.id)
    db.flush()
    f1, f2, m = flawed1.current_version_id, flawed2.current_version_id, minitest.current_version_id

    questions: list[tuple[str, dict]] = [
        (
            "short_answer",
            {
                "prompt": (
                    "Relève trois erreurs différentes (accord, homophone, ponctuation...) "
                    "présentes dans la note de service, et précise le type de chacune."
                ),
                "source_document_version_id": f1,
                "rubric": (
                    "Bonne réponse si elle relève au moins trois erreurs réelles parmi : "
                    "« A tout » au lieu de « À tout », « laisser » au lieu de « laissée », "
                    "« chaques » au lieu de « chaque », « on constatés » au lieu de « ont "
                    "constaté », « le évier » au lieu de « l'évier », « ou » au lieu de "
                    "« où », « périmer » au lieu de « périmés », « on été retrouvé » au "
                    "lieu de « ont été retrouvés », en identifiant correctement le type "
                    "de chaque erreur."
                ),
                "max_length": 400,
            },
        ),
        (
            "long_answer",
            {
                "prompt": (
                    "Réécris entièrement la note de service en corrigeant toutes les "
                    "erreurs que tu identifies (orthographe, accords, homophones, "
                    "ponctuation)."
                ),
                "source_document_version_id": f1,
                "rubric": (
                    "4 points : accords sujet-verbe corrigés (1 point) ; homophones "
                    "corrigés (à/a, ou/où) (1 point) ; ponctuation et majuscules "
                    "corrigées (1 point) ; sens du message intégralement conservé, sans "
                    "information ajoutée ou supprimée (1 point)."
                ),
                "max_score": 4.0,
            },
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "L'avis sur le logiciel comporte plusieurs répétitions inutiles du "
                    "mot « logiciel » ou des tournures familières à l'oral (« moi je "
                    "trouve », « sa serait bien »...). Relève deux exemples et propose "
                    "une reformulation plus soignée pour chacun."
                ),
                "source_document_version_id": f2,
                "rubric": (
                    "Bonne réponse si elle relève deux tournures orales/répétitions "
                    "réelles du texte et propose pour chacune une reformulation plus "
                    "soignée et cohérente avec le sens d'origine."
                ),
                "max_length": 400,
            },
        ),
        (
            "long_answer",
            {
                "prompt": (
                    "Réécris cet avis dans un registre plus soigné, adapté à un message "
                    "professionnel envoyé au service informatique, en corrigeant les "
                    "erreurs et en évitant les répétitions et tournures orales."
                ),
                "source_document_version_id": f2,
                "rubric": (
                    "4 points : orthographe et accords corrigés (1 point) ; registre "
                    "soigné, sans tournures orales (« moi je trouve », « sa serait ») "
                    "(1 point) ; répétitions du mot « logiciel » réduites par des "
                    "reformulations ou des pronoms (1 point) ; contenu et avis "
                    "d'origine conservés sans déformation (1 point)."
                ),
                "max_score": 4.0,
            },
        ),
        (
            "vocabulary",
            {
                "prompt": "Quelle est la différence entre un homophone grammatical (ex. « a »/« à ») et une simple faute de frappe ?",
                "rubric": (
                    "Bonne réponse si elle explique qu'un homophone grammatical est une "
                    "confusion entre deux mots qui se prononcent pareil mais ont un sens "
                    "et une orthographe différents (souvent liée à une règle de "
                    "grammaire), alors qu'une faute de frappe est une erreur accidentelle "
                    "de saisie sans lien avec la grammaire."
                ),
            },
        ),
        (
            "classification",
            {
                "prompt": "Classe chaque extrait de la note de service selon le type d'erreur qu'il contient.",
                "source_document_version_id": f1,
                "categories": ["Erreur d'accord", "Confusion d'homophone", "Ponctuation/majuscule manquante"],
                "elements": [
                    "plusieurs employés on constatés",
                    "des aliments périmer on été retrouvé",
                    "A tout le personnel",
                ],
                "correct_categories": [0, 0, 2],
                "explanation": (
                    "Les deux premiers extraits contiennent des erreurs d'accord "
                    "sujet-verbe (« on constatés »/« on été retrouvé » au lieu de « ont "
                    "constaté »/« ont été retrouvés ») ; le troisième manque une "
                    "majuscule accentuée en début de phrase (« À »)."
                ),
            },
        ),
        (
            "long_answer",
            {
                "prompt": (
                    "Corrige entièrement ce message destiné à un client en respectant un "
                    "registre professionnel soigné, sans changer le sens du message ni "
                    "ajouter d'informations absentes de l'original."
                ),
                "source_document_version_id": m,
                "rubric": (
                    "4 points : orthographe et conjugaisons corrigées (« je vous écris », "
                    "« a été retardée », « nous sommes désolés »...) (1 point) ; "
                    "homophones corrigés (a/à, notamment) (1 point) ; registre "
                    "professionnel cohérent du début à la fin (1 point) ; sens du "
                    "message d'origine intégralement conservé (1 point)."
                ),
                "max_score": 4.0,
            },
        ),
        (
            "short_answer",
            {
                "prompt": "Relève deux erreurs de conjugaison présentes dans ce message et indique la forme correcte pour chacune.",
                "source_document_version_id": m,
                "rubric": (
                    "Bonne réponse si elle relève deux erreurs réelles parmi : « je vous "
                    "écrit » au lieu de « je vous écris », « vous informez » au lieu de "
                    "« vous informer », « a était retardé » au lieu de « a été "
                    "retardée », « devrai » au lieu de « devrait », « n'hésiter pas » au "
                    "lieu de « n'hésitez pas », avec la forme correcte donnée pour "
                    "chacune."
                ),
                "max_length": 350,
            },
        ),
    ]

    return _import_course(db, module, uaa, questions)
