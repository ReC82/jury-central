"""Banque V1 Français — FR06→FR10 (ticket #94, PHASE B).

Même principe que `app.v1.francais_fr01_05_bank` (#94 PHASE A) : import idempotent,
hand-authored, revalidé par le registre #40 (`validate_content`) avant stockage. Aucune
question ne référence un texte sans un `SourceDocumentVersion` réellement rattaché."""

from sqlalchemy.orm import Session

from app.models import UAA, Module
from app.v1 import question_types  # noqa: F401 — enregistre les 26 types (#40) au chargement
from app.v1.francais_fr06_10_content import (
    FR06_ARTICLE_TEXT,
    FR06_ARTICLE_TITLE,
    FR06_MINITEST_ARTICLE_TEXT,
    FR06_MINITEST_ARTICLE_TITLE,
    FR06_MINITEST_TOC_TEXT,
    FR06_MINITEST_TOC_TITLE,
    FR06_MULTIMEDIA_TEXT,
    FR06_MULTIMEDIA_TITLE,
    FR06_SITE_TEXT,
    FR06_SITE_TITLE,
    FR06_TOC_TEXT,
    FR06_TOC_TITLE,
    FR07_MINITEST_A_TEXT,
    FR07_MINITEST_A_TITLE,
    FR07_MINITEST_B_TEXT,
    FR07_MINITEST_B_TITLE,
    FR07_SOURCE_A_TEXT,
    FR07_SOURCE_A_TITLE,
    FR07_SOURCE_B_TEXT,
    FR07_SOURCE_B_TITLE,
    FR07_SOURCE_C_TEXT,
    FR07_SOURCE_C_TITLE,
    FR07_SOURCE_D_TEXT,
    FR07_SOURCE_D_TITLE,
    FR08_MINITEST_TEXT,
    FR08_MINITEST_TITLE,
    FR08_SOURCE1_TEXT,
    FR08_SOURCE1_TITLE,
    FR08_SOURCE2_TEXT,
    FR08_SOURCE2_TITLE,
    FR09_DOC1_TEXT,
    FR09_DOC1_TITLE,
    FR09_DOC2_TEXT,
    FR09_DOC2_TITLE,
    FR09_DOC3_TEXT,
    FR09_DOC3_TITLE,
    FR09_MINITEST_DOC1_TEXT,
    FR09_MINITEST_DOC1_TITLE,
    FR09_MINITEST_DOC2_TEXT,
    FR09_MINITEST_DOC2_TITLE,
    FR09_MINITEST_DOC3_TEXT,
    FR09_MINITEST_DOC3_TITLE,
    FR10_MINITEST_TEXT,
    FR10_MINITEST_TITLE,
    FR10_TEXT1_TEXT,
    FR10_TEXT1_TITLE,
    FR10_TEXT2_TEXT,
    FR10_TEXT2_TITLE,
)
from app.v1.models import (
    GenerationSource,
    Question,
    create_question,
    create_source_document,
)
from app.v1.question_engine import validate_content


def _import_course(db: Session, module: Module, uaa: UAA, questions: list[tuple[str, dict]]) -> int:
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
# FR06 — Rechercher et sélectionner l'information
# =============================================================================================


def import_francais_fr06_to_bank(db: Session, module: Module, uaa: UAA) -> int:
    already_imported = (
        db.query(Question).filter_by(uaa_id=uaa.id, generation_source=GenerationSource.IMPORTED).count()
    )
    if already_imported:
        return 0

    toc = create_source_document(db, title=FR06_TOC_TITLE, content_text=FR06_TOC_TEXT, module_id=module.id)
    article = create_source_document(db, title=FR06_ARTICLE_TITLE, content_text=FR06_ARTICLE_TEXT, module_id=module.id)
    site = create_source_document(db, title=FR06_SITE_TITLE, content_text=FR06_SITE_TEXT, module_id=module.id)
    multimedia = create_source_document(db, title=FR06_MULTIMEDIA_TITLE, content_text=FR06_MULTIMEDIA_TEXT, module_id=module.id)
    minitest_toc = create_source_document(db, title=FR06_MINITEST_TOC_TITLE, content_text=FR06_MINITEST_TOC_TEXT, module_id=module.id)
    minitest_article = create_source_document(db, title=FR06_MINITEST_ARTICLE_TITLE, content_text=FR06_MINITEST_ARTICLE_TEXT, module_id=module.id)
    db.flush()
    toc_id, art_id, site_id, mm_id = toc.current_version_id, article.current_version_id, site.current_version_id, multimedia.current_version_id
    mt_toc_id, mt_art_id = minitest_toc.current_version_id, minitest_article.current_version_id

    questions: list[tuple[str, dict]] = [
        (
            "short_answer",
            {
                "prompt": "D'après le sommaire, à quelle page commence le sous-chapitre consacré à la sécurité au travail ?",
                "source_document_version_id": toc_id,
                "accepted_answers": ["page 30", "p. 30", "30"],
                "rubric": "Bonne réponse si elle indique la page 30 (4.3 La sécurité au travail).",
                "max_length": 100,
            },
        ),
        (
            "short_answer",
            {
                "prompt": "Le sommaire indique un sous-chapitre sur les codes de communication au travail. Dans quel chapitre se trouve-t-il, et à quelle page commence-t-il ?",
                "source_document_version_id": toc_id,
                "rubric": "Bonne réponse si elle situe ce sous-chapitre dans le Chapitre 3 (S'intégrer dans une équipe), à la page 18.",
                "max_length": 200,
            },
        ),
        (
            "document_analysis",
            {
                "prompt": "Relève, dans l'article sur les bibliothèques, un élément qui montre le sérieux de la source (fait vérifiable, chiffre, institution citée), puis explique en quoi cet élément renforce la fiabilité de l'information.",
                "source_document_version_id": art_id,
                "rubric": "Bonne réponse si elle cite un élément précis (enquête menée auprès des usagers, recrutement de deux agents, budget culturel voté) et explique pourquoi cet élément appuie la crédibilité de l'article.",
                "expected_points": ["Cite un élément précis et vérifiable de l'article", "Explique en quoi il renforce la fiabilité"],
            },
        ),
        (
            "short_answer",
            {
                "prompt": "D'après la description du site « Ma Commune Pratique », dans quelle rubrique trouverais-tu les offres d'emploi communales ?",
                "source_document_version_id": site_id,
                "accepted_answers": ["emploi et formation", "rubrique emploi et formation", "dans emploi et formation"],
                "rubric": "Bonne réponse si elle identifie la rubrique « Emploi et formation ».",
                "max_length": 150,
            },
        ),
        (
            "vocabulary",
            {
                "prompt": "Dans la description de la vidéo, que signifie l'expression « chapitre horodaté » ?",
                "source_document_version_id": mm_id,
                "rubric": "Bonne réponse si elle indique qu'il s'agit d'un chapitre associé à un moment précis (un horodatage, ex. 03:40) permettant d'accéder directement à cette partie de la vidéo, sans devoir la regarder en entier.",
            },
        ),
        (
            "short_answer",
            {
                "prompt": "Si tu cherches uniquement à connaître les erreurs fréquentes dans une lettre de motivation, à quel moment de la vidéo devrais-tu aller directement plutôt que de tout regarder ?",
                "source_document_version_id": mm_id,
                "accepted_answers": ["03:40", "à 03:40", "3:40", "chapitre 2"],
                "rubric": "Bonne réponse si elle indique le chapitre 2 (03:40), illustrant une lecture/écoute sélective plutôt qu'intégrale.",
                "max_length": 100,
            },
        ),
        (
            "classification",
            {
                "prompt": "Classe chaque support documentaire selon le type de ressource qu'il représente.",
                "categories": ["Sommaire d'ouvrage", "Article de presse", "Ressource multimédia"],
                "elements": ["Chapitres et pages numérotées d'un guide", "Un fait d'actualité daté et localisé", "Une vidéo avec chapitres horodatés"],
                "correct_categories": [0, 1, 2],
                "explanation": "Un sommaire organise un ouvrage en chapitres/pages ; un article de presse rapporte un fait d'actualité ; une ressource multimédia (vidéo, podcast) s'organise en chapitres horodatés plutôt qu'en pages.",
            },
        ),
        (
            "source_comparison",
            {
                "prompt": "En t'appuyant sur le sommaire et l'article du dossier mini-test, indique laquelle des deux sources répond le mieux à la question « Comment signaler un nid-de-poule ? », et explique pourquoi.",
                "source_document_version_ids": [mt_toc_id, mt_art_id],
                "rubric": "Bonne réponse si elle identifie l'article (qui décrit l'application de signalement) comme source pertinente, et explique que le sommaire (guide sur les transports en commun) ne traite pas ce sujet — pertinence du sujet, pas seulement du type de document.",
                "expected_points": ["Identifie l'article comme source pertinente", "Justifie par le sujet traité, pas par le format"],
            },
        ),
        (
            "short_answer",
            {
                "prompt": "Relève, dans l'article sur l'application de signalement, une donnée chiffrée qui montre son efficacité.",
                "source_document_version_id": mt_art_id,
                "rubric": "Bonne réponse si elle cite le passage : plus de deux cents signalements traités contre une trentaine par téléphone l'année précédente.",
                "max_length": 200,
            },
        ),
    ]
    return _import_course(db, module, uaa, questions)


# =============================================================================================
# FR07 — Évaluer une source et sa fiabilité
# =============================================================================================


def import_francais_fr07_to_bank(db: Session, module: Module, uaa: UAA) -> int:
    already_imported = (
        db.query(Question).filter_by(uaa_id=uaa.id, generation_source=GenerationSource.IMPORTED).count()
    )
    if already_imported:
        return 0

    a = create_source_document(db, title=FR07_SOURCE_A_TITLE, content_text=FR07_SOURCE_A_TEXT, module_id=module.id)
    b = create_source_document(db, title=FR07_SOURCE_B_TITLE, content_text=FR07_SOURCE_B_TEXT, module_id=module.id)
    c = create_source_document(db, title=FR07_SOURCE_C_TITLE, content_text=FR07_SOURCE_C_TEXT, module_id=module.id)
    d = create_source_document(db, title=FR07_SOURCE_D_TITLE, content_text=FR07_SOURCE_D_TEXT, module_id=module.id)
    mt_a = create_source_document(db, title=FR07_MINITEST_A_TITLE, content_text=FR07_MINITEST_A_TEXT, module_id=module.id)
    mt_b = create_source_document(db, title=FR07_MINITEST_B_TITLE, content_text=FR07_MINITEST_B_TEXT, module_id=module.id)
    db.flush()
    a_id, b_id, c_id, d_id = a.current_version_id, b.current_version_id, c.current_version_id, d.current_version_id
    mt_a_id, mt_b_id = mt_a.current_version_id, mt_b.current_version_id

    questions: list[tuple[str, dict]] = [
        (
            "short_answer",
            {
                "prompt": "Dans la Source B, quel est l'objectif réel de l'article, au-delà de l'objectif déclaré de « sensibiliser les parents » ?",
                "source_document_version_id": b_id,
                "rubric": "Bonne réponse si elle identifie un objectif commercial/publicitaire (promouvoir/vendre le logiciel FamilySafe), en s'appuyant sur les renvois répétés vers la page d'achat.",
                "max_length": 300,
            },
        ),
        (
            "document_analysis",
            {
                "prompt": "La Source A cite une méthodologie précise et compare ses résultats à d'autres études. Explique en quoi cela renforce sa fiabilité par rapport à la Source C.",
                "source_document_version_id": a_id,
                "rubric": "Bonne réponse si elle explique que la méthode scientifique vérifiable (questionnaire validé, comparaison à d'autres études) donne plus de poids à l'information qu'un témoignage individuel isolé (Source C), sans pour autant rejeter la Source C comme totalement inutile (elle reste un témoignage valable en tant que tel).",
                "expected_points": ["Identifie la méthodologie comme facteur de fiabilité", "Compare explicitement à la Source C"],
            },
        ),
        (
            "short_answer",
            {
                "prompt": "La Source C est-elle plus utile pour connaître un ressenti personnel ou pour établir un fait scientifique général ? Justifie.",
                "source_document_version_id": c_id,
                "rubric": "Bonne réponse si elle indique que la Source C, témoignage individuel sans méthode ni recoupement, est utile pour un ressenti personnel mais ne permet pas d'établir un fait scientifique général.",
                "max_length": 300,
            },
        ),
        (
            "classification",
            {
                "prompt": "Classe chaque extrait des sources selon sa nature dominante.",
                "categories": ["Fait/donnée vérifiable", "Opinion/témoignage personnel", "Argument publicitaire"],
                "elements": [
                    "Différence de 23 points de pourcentage entre les deux groupes d'adolescents (Source A)",
                    "Chez moi ça a été l'horreur avec les écrans (Source C)",
                    "Découvrez comment FamilySafe peut vous aider dès aujourd'hui (Source B)",
                ],
                "correct_categories": [0, 1, 2],
                "explanation": "Le premier extrait rapporte une donnée chiffrée vérifiable ; le deuxième est un ressenti personnel non généralisable ; le troisième est un appel commercial explicite.",
            },
        ),
        (
            "source_comparison",
            {
                "prompt": "Compare la Source A et la Source D : les deux abordent le même sujet scientifique. En quoi leur fiabilité diffère-t-elle malgré cela ?",
                "source_document_version_ids": [a_id, d_id],
                "rubric": "Bonne réponse si elle explique que la Source A est la recherche originale (étude primaire) tandis que la Source D est un article de vulgarisation qui rapporte PLUSIEURS études (dont potentiellement la Source A) en les mettant en perspective — les deux sont fiables mais à des niveaux différents (source primaire vs synthèse journalistique sourcée).",
                "expected_points": ["Identifie A comme étude primaire", "Identifie D comme synthèse journalistique sourcée", "Nuance : les deux restent fiables mais différemment"],
            },
        ),
        (
            "vocabulary",
            {
                "prompt": "Que signifie « recouper une information » lorsqu'on évalue la fiabilité d'une source ?",
                "rubric": "Bonne réponse si elle explique qu'il s'agit de vérifier une information en la comparant à d'autres sources indépendantes, pour voir si elles convergent, plutôt que de se fier à une seule source isolée.",
            },
        ),
        (
            "long_answer",
            {
                "prompt": "Dans le dossier mini-test, une source (A) est publiée par une association de consommateurs sans financement des opérateurs comparés, l'autre (B) est un article sponsorisé par un seul opérateur. Explique pourquoi ces deux sources ne peuvent pas être considérées comme également fiables pour comparer objectivement des offres téléphoniques, en t'appuyant sur des éléments précis de chacune.",
                "source_document_version_id": mt_a_id,
                "rubric": "3 points : identifie l'absence de financement par les opérateurs comme gage d'indépendance pour la source A (1 point) ; identifie le financement par un seul opérateur comme biais évident pour la source B (1 point) ; conclut clairement sur la source la plus fiable pour une comparaison objective (1 point).",
                "max_score": 3.0,
            },
        ),
        (
            "short_answer",
            {
                "prompt": "Dans la Source B du dossier mini-test (article sponsorisé), relève un indice explicite qui signale au lecteur qu'il s'agit de contenu publicitaire.",
                "source_document_version_id": mt_b_id,
                "accepted_answers": ["la mention contenu partenaire", "mention « contenu partenaire »", "contenu partenaire"],
                "rubric": "Bonne réponse si elle cite la mention « Contenu partenaire » affichée en haut de page.",
                "max_length": 150,
            },
        ),
    ]
    return _import_course(db, module, uaa, questions)


# =============================================================================================
# FR08 — Réduire et résumer un texte
# =============================================================================================


def import_francais_fr08_to_bank(db: Session, module: Module, uaa: UAA) -> int:
    already_imported = (
        db.query(Question).filter_by(uaa_id=uaa.id, generation_source=GenerationSource.IMPORTED).count()
    )
    if already_imported:
        return 0

    s1 = create_source_document(db, title=FR08_SOURCE1_TITLE, content_text=FR08_SOURCE1_TEXT, module_id=module.id)
    s2 = create_source_document(db, title=FR08_SOURCE2_TITLE, content_text=FR08_SOURCE2_TEXT, module_id=module.id)
    mt = create_source_document(db, title=FR08_MINITEST_TITLE, content_text=FR08_MINITEST_TEXT, module_id=module.id)
    db.flush()
    s1_id, s2_id, mt_id = s1.current_version_id, s2.current_version_id, mt.current_version_id

    questions: list[tuple[str, dict]] = [
        (
            "short_answer",
            {
                "prompt": "Résume en UNE phrase le sujet du texte sur le compostage collectif.",
                "source_document_version_id": s1_id,
                "rubric": "Bonne réponse si elle résume en une phrase que des villes installent des composteurs collectifs permettant aux habitants sans jardin de valoriser leurs déchets alimentaires.",
                "max_length": 250,
            },
        ),
        (
            "short_answer",
            {
                "prompt": "Relève les trois avantages du compostage collectif cités dans le texte, en les hiérarchisant du plus important (selon toi) au moins important, et justifie ton choix en une phrase.",
                "source_document_version_id": s1_id,
                "rubric": "Bonne réponse si elle cite les trois avantages (réduction du poids des poubelles, production de compost, effet social) et justifie un ordre de priorité cohérent.",
                "max_length": 400,
            },
        ),
        (
            "long_answer",
            {
                "prompt": "Résume le texte sur le compostage collectif en un paragraphe de 4 à 6 phrases maximum, en conservant l'idée principale et les idées secondaires essentielles, sans recopier de phrases entières du texte source.",
                "source_document_version_id": s1_id,
                "rubric": "4 points : idée principale correctement identifiée (installation de composteurs collectifs) (1 point) ; avantages résumés fidèlement sans être recopiés mot pour mot (1 point) ; difficultés mentionnées (entretien, référent) (1 point) ; longueur respectée (4-6 phrases), neutralité de ton (pas d'opinion personnelle ajoutée) (1 point).",
                "max_score": 4.0,
            },
        ),
        (
            "short_answer",
            {
                "prompt": "Le texte sur le covoiturage courte distance mentionne un frein principal à son développement. Reformule ce frein avec tes propres mots, sans recopier la phrase du texte.",
                "source_document_version_id": s2_id,
                "rubric": "Bonne réponse si elle reformule (pas de copie mot pour mot) l'idée que la difficulté de synchroniser les horaires entre collègues freine le covoiturage.",
                "max_length": 300,
            },
        ),
        (
            "long_answer",
            {
                "prompt": "Résume le texte sur le covoiturage courte distance en un paragraphe de 4 à 6 phrases, en respectant la structure du texte source (facteurs de développement, puis frein principal).",
                "source_document_version_id": s2_id,
                "rubric": "3 points : facteurs de développement résumés fidèlement (hausse des carburants, saturation des parkings, dimension écologique) (1 point) ; frein principal mentionné (synchronisation des horaires) (1 point) ; longueur respectée, reformulation sans copie (1 point).",
                "max_score": 3.0,
            },
        ),
        (
            "vocabulary",
            {
                "prompt": "Quelle est la différence entre « résumer » et « paraphraser » un texte ?",
                "rubric": "Bonne réponse si elle explique que résumer condense et hiérarchise l'information (texte plus court, idées essentielles seulement), alors que paraphraser reformule sans nécessairement réduire la longueur (dire la même chose autrement, mais pas forcément plus court).",
            },
        ),
        (
            "long_answer",
            {
                "prompt": "Résume le texte sur le vélo-cargo en milieu urbain en un maximum de 80 mots, en couvrant à la fois les usages (familles, professionnels) et les freins à son adoption.",
                "source_document_version_id": mt_id,
                "rubric": "4 points : usage familial mentionné (1 point) ; usage professionnel/livraison mentionné (1 point) ; au moins un frein mentionné (coût, infrastructures, vol) (1 point) ; longueur respectée (environ 80 mots, tolérance de 20%) (1 point).",
                "max_score": 4.0,
            },
        ),
        (
            "short_answer",
            {
                "prompt": "Dans le texte sur le vélo-cargo, quelle est l'idée principale, en une phrase ?",
                "source_document_version_id": mt_id,
                "rubric": "Bonne réponse si elle indique que le vélo-cargo connaît un regain d'intérêt en ville, aussi bien chez les familles que dans le secteur professionnel.",
                "max_length": 250,
            },
        ),
    ]
    return _import_course(db, module, uaa, questions)


# =============================================================================================
# FR09 — Synthétiser plusieurs documents
# =============================================================================================


def import_francais_fr09_to_bank(db: Session, module: Module, uaa: UAA) -> int:
    already_imported = (
        db.query(Question).filter_by(uaa_id=uaa.id, generation_source=GenerationSource.IMPORTED).count()
    )
    if already_imported:
        return 0

    d1 = create_source_document(db, title=FR09_DOC1_TITLE, content_text=FR09_DOC1_TEXT, module_id=module.id)
    d2 = create_source_document(db, title=FR09_DOC2_TITLE, content_text=FR09_DOC2_TEXT, module_id=module.id)
    d3 = create_source_document(db, title=FR09_DOC3_TITLE, content_text=FR09_DOC3_TEXT, module_id=module.id)
    mt1 = create_source_document(db, title=FR09_MINITEST_DOC1_TITLE, content_text=FR09_MINITEST_DOC1_TEXT, module_id=module.id)
    mt2 = create_source_document(db, title=FR09_MINITEST_DOC2_TITLE, content_text=FR09_MINITEST_DOC2_TEXT, module_id=module.id)
    mt3 = create_source_document(db, title=FR09_MINITEST_DOC3_TITLE, content_text=FR09_MINITEST_DOC3_TEXT, module_id=module.id)
    db.flush()
    d1_id, d2_id, d3_id = d1.current_version_id, d2.current_version_id, d3.current_version_id
    mt1_id, mt2_id, mt3_id = mt1.current_version_id, mt2.current_version_id, mt3.current_version_id

    questions: list[tuple[str, dict]] = [
        (
            "short_answer",
            {
                "prompt": "Quelle différence essentielle y a-t-il entre résumer UN texte et synthétiser PLUSIEURS documents ?",
                "rubric": "Bonne réponse si elle explique que résumer condense un seul texte selon SON plan, alors que synthétiser organise et confronte les idées de plusieurs documents selon un plan PERSONNEL (thématique), jamais un plan « Document 1 / Document 2 / Document 3 ».",
                "max_length": 400,
            },
        ),
        (
            "source_comparison",
            {
                "prompt": "Le Document 1 (étude économique) et le Document 2 (syndicat) évoquent tous deux un frein au télétravail. Identifie ce point COMMUN entre les deux documents.",
                "source_document_version_ids": [d1_id, d2_id],
                "rubric": "Bonne réponse si elle identifie que les deux documents évoquent une difficulté liée au travail en équipe/à l'intégration à distance (délais allongés pour le travail collectif dans le Document 1, isolement des nouveaux salariés dans le Document 2) — un point commun réel, pas une simple juxtaposition.",
                "expected_points": ["Identifie un point commun réel entre les deux documents", "Précise en quoi il s'agit du même type de problème"],
            },
        ),
        (
            "source_comparison",
            {
                "prompt": "Le Document 3 (médecine du travail) apporte-t-il un COMPLÉMENT ou une DIVERGENCE par rapport aux Documents 1 et 2 ? Justifie en citant un élément précis du Document 3.",
                "source_document_version_ids": [d1_id, d2_id, d3_id],
                "rubric": "3 points : identifie qu'il s'agit surtout d'un COMPLÉMENT (nouvel angle : la santé physique, non traité par les deux premiers documents) plutôt qu'une divergence (1 point) ; cite un élément précis du Document 3 (troubles musculo-squelettiques, équipement ergonomique) (1 point) ; explique en quoi cela complète plutôt que contredit les deux premiers documents (1 point).",
                "max_score": 3.0,
            },
        ),
        (
            "source_comparison",
            {
                "prompt": "En t'appuyant sur les trois documents (étude économique, syndicat, médecine du travail), rédige une courte synthèse organisée THÉMATIQUEMENT (par exemple : effets sur la productivité, effets sur l'intégration, effets sur la santé) — jamais un plan « Document 1 / Document 2 / Document 3 ». Ta synthèse doit rester neutre, sans donner ton avis personnel.",
                "source_document_version_ids": [d1_id, d2_id, d3_id],
                "rubric": "5 points : plan thématique respecté, jamais un plan par document (2 points, éliminatoire si plan D1/D2/D3) ; effets sur la productivité/le collectif mentionnés (1 point) ; effets sur l'intégration mentionnés (1 point) ; effets sur la santé mentionnés (1 point). Neutralité : aucune opinion personnelle ajoutée par l'élève.",
                "max_score": 5.0,
            },
        ),
        (
            "vocabulary",
            {
                "prompt": "Qu'appelle-t-on un « patchwork » en synthèse de documents, et pourquoi faut-il l'éviter ?",
                "rubric": "Bonne réponse si elle explique qu'un patchwork consiste à juxtaposer des extraits ou résumés de chaque document les uns après les autres sans les confronter ni les organiser par thème — à éviter car cela ne montre aucune vraie mise en relation des documents entre eux.",
            },
        ),
        (
            "source_comparison",
            {
                "prompt": "Dans le dossier mini-test, le Document 1 (enquête nutritionnelle) et le Document 3 (diététicienne) évaluent différemment l'intérêt du menu végétarien hebdomadaire. Identifie cette NUANCE entre les deux documents.",
                "source_document_version_ids": [mt1_id, mt3_id],
                "rubric": "Bonne réponse si elle identifie que le Document 1 met en avant un effet nutritionnel mesurable (plus de légumes, moins de gaspillage), tandis que le Document 3 relativise cet effet nutritionnel et y voit surtout un intérêt pédagogique — une nuance entre deux angles complémentaires, pas une contradiction totale.",
                "expected_points": ["Identifie l'angle nutritionnel du Document 1", "Identifie la relativisation/l'angle pédagogique du Document 3", "Formule cela comme une nuance, pas une opposition totale"],
            },
        ),
        (
            "source_comparison",
            {
                "prompt": "En t'appuyant sur les trois documents du dossier mini-test (enquête nutritionnelle, témoignage de la directrice, avis de la diététicienne), rédige une synthèse organisée par thème (par exemple : effets mesurés, réception par les élèves/familles, limites de l'objectif nutritionnel). Plan personnel obligatoire, jamais un plan par document.",
                "source_document_version_ids": [mt1_id, mt2_id, mt3_id],
                "rubric": "5 points : plan thématique respecté (2 points, éliminatoire si plan par document) ; effets mesurés mentionnés (légumes, gaspillage) (1 point) ; réception/évolution des familles mentionnée (1 point) ; limite de l'objectif nutritionnel selon la diététicienne mentionnée (1 point).",
                "max_score": 5.0,
            },
        ),
    ]
    return _import_course(db, module, uaa, questions)


# =============================================================================================
# FR10 — Comprendre thèse, arguments et preuves
# =============================================================================================


def import_francais_fr10_to_bank(db: Session, module: Module, uaa: UAA) -> int:
    already_imported = (
        db.query(Question).filter_by(uaa_id=uaa.id, generation_source=GenerationSource.IMPORTED).count()
    )
    if already_imported:
        return 0

    t1 = create_source_document(db, title=FR10_TEXT1_TITLE, content_text=FR10_TEXT1_TEXT, module_id=module.id)
    t2 = create_source_document(db, title=FR10_TEXT2_TITLE, content_text=FR10_TEXT2_TEXT, module_id=module.id)
    mt = create_source_document(db, title=FR10_MINITEST_TITLE, content_text=FR10_MINITEST_TEXT, module_id=module.id)
    db.flush()
    t1_id, t2_id, mt_id = t1.current_version_id, t2.current_version_id, mt.current_version_id

    questions: list[tuple[str, dict]] = [
        (
            "short_answer",
            {
                "prompt": "Quelle est la thèse défendue dans le premier texte sur la semaine de quatre jours ?",
                "source_document_version_id": t1_id,
                "rubric": "Bonne réponse si elle indique que la thèse est qu'il faut encourager plus largement la généralisation de la semaine de quatre jours.",
                "max_length": 250,
            },
        ),
        (
            "short_answer",
            {
                "prompt": "Relève un exemple concret (une entreprise, un chiffre précis) utilisé dans le premier texte pour appuyer un argument, et précise quel argument il illustre.",
                "source_document_version_id": t1_id,
                "rubric": "Bonne réponse si elle cite un exemple précis (hausse de 4% de productivité, baisse de 30% des arrêts maladie) et identifie l'argument qu'il illustre (productivité maintenue ou effet sur la santé).",
                "max_length": 350,
            },
        ),
        (
            "document_analysis",
            {
                "prompt": "Le deuxième texte reproche au premier texte une « généralisation hâtive ». Explique ce que signifie ce reproche, en citant le passage du deuxième texte qui l'exprime.",
                "source_document_version_id": t2_id,
                "rubric": "Bonne réponse si elle cite le passage sur les expérimentations volontaires menées par des entreprises déjà favorables, et explique que le reproche porte sur le fait de généraliser une observation limitée à des cas favorables à l'ensemble des entreprises.",
                "expected_points": ["Cite le passage pertinent", "Explique le sens du reproche de généralisation hâtive"],
            },
        ),
        (
            "source_comparison",
            {
                "prompt": "Compare les deux textes : sur quel point précis leurs thèses s'opposent-elles frontalement, et sur quel point le deuxième texte nuance-t-il plutôt qu'il ne s'oppose totalement ?",
                "source_document_version_ids": [t1_id, t2_id],
                "rubric": "Bonne réponse si elle identifie l'opposition frontale (encourager largement vs risque d'une généralisation hâtive) et une nuance (le deuxième texte ne nie pas les bénéfices constatés dans les expérimentations, il en conteste la représentativité).",
                "expected_points": ["Identifie l'opposition frontale des deux thèses", "Identifie une nuance plutôt qu'une opposition totale sur un point précis"],
            },
        ),
        (
            "classification",
            {
                "prompt": "Classe chaque élément du dossier mini-test selon sa nature argumentative.",
                "categories": ["Argument appuyé sur une donnée précise", "Argument faible (impression, jugement moral)"],
                "elements": [
                    "Plusieurs accidents du travail recensés par un organisme de prévention",
                    "Tout le monde perd un temps fou sur son téléphone",
                    "Les employés n'ont qu'à se déconnecter comme avant les smartphones",
                ],
                "correct_categories": [0, 1, 1],
                "explanation": "Le premier argument s'appuie sur des données recensées par un organisme identifié ; les deux autres sont des impressions non chiffrées ou des jugements moraux, sans preuve précise.",
            },
        ),
        (
            "long_answer",
            {
                "prompt": "Dans le texte mini-test sur l'interdiction du téléphone au travail, identifie les TROIS arguments avancés, puis classe-les du plus solide au plus faible en justifiant chaque fois ton classement par la présence ou l'absence de preuves précises.",
                "source_document_version_id": mt_id,
                "rubric": "5 points : les trois arguments correctement identifiés (sécurité, productivité, comparaison avec le passé) (2 points, un point par paire d'arguments distincts manquante en moins) ; classement cohérent avec justification par la présence/absence de preuves (2 points) ; argument sécuritaire reconnu comme le plus solide (appuyé sur des données chiffrées d'un organisme de prévention) (1 point).",
                "max_score": 5.0,
            },
        ),
        (
            "short_answer",
            {
                "prompt": "Le texte mini-test évoque une « attaque personnelle simple » implicite dans l'un des arguments. Lequel, et pourquoi peut-on le qualifier ainsi ?",
                "source_document_version_id": mt_id,
                "rubric": "Bonne réponse si elle identifie l'argument sur le fait de « se déconnecter comme avant » comme relevant davantage d'un jugement moral envers les employés que d'une preuve, ignorant les usages professionnels légitimes du téléphone.",
                "max_length": 350,
            },
        ),
        (
            "vocabulary",
            {
                "prompt": "Quelle est la différence entre un « argument » et un « exemple » dans un texte argumentatif ?",
                "rubric": "Bonne réponse si elle explique qu'un argument est une idée générale qui soutient une thèse, tandis qu'un exemple illustre concrètement cet argument (un cas particulier), sans se substituer à lui — un exemple seul, sans argument général derrière, ne prouve rien à grande échelle.",
            },
        ),
    ]
    return _import_course(db, module, uaa, questions)
