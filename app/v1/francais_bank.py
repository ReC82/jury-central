"""Banque V1 Français — corpus d'entraînement (ticket #47, étendu en overnight mission du
2026-09-19, § Phases 5-7).

Suit le même principe que `app/v1/bank.py::import_mc01_legacy_to_bank` : import idempotent
d'un socle initial de questions hand-authored, toutes revalidées par le registre #40
(`validate_content`) avant stockage, jamais de solution exposée publiquement.

**Statut explicite : PROVISIONAL_TECHNICAL_SAMPLE** (voir `app.v1.francais_content` pour
les textes source et le détail du statut — contenu d'entraînement original, jamais un
examen CESS officiel). 5 SourceDocument, 40 questions couvrant short_answer, long_answer,
document_analysis, source_comparison, vocabulary et classification — toujours rattachées à
un SourceDocument (jamais de texte dupliqué par question, chaque question ne porte qu'une
référence `source_document_version_id`/`_ids`, conformément au registre #40). Répartition
par document et par compétence détaillée dans `docs/francais_v1_functional.md`."""

from sqlalchemy.orm import Session

from app.models import UAA, Module
from app.v1 import question_types  # noqa: F401 — enregistre les 26 types (#40) au chargement
from app.v1.francais_content import (
    CODING_DEBATE_DOCUMENT_TEXT,
    CODING_DEBATE_DOCUMENT_TITLE,
    DIGITAL_LIFE_DOCUMENT_TEXT,
    DIGITAL_LIFE_DOCUMENT_TITLE,
    MAIN_DOCUMENT_TEXT,
    MAIN_DOCUMENT_TITLE,
    SECOND_DOCUMENT_TEXT,
    SECOND_DOCUMENT_TITLE,
    TRAINING_DOCUMENT_TEXT,
    TRAINING_DOCUMENT_TITLE,
)
from app.v1.models import (
    GenerationSource,
    Question,
    create_question,
    create_source_document,
)
from app.v1.question_engine import validate_content

# Grille de correction générique pour une réponse d'opinion/justification personnelle
# (§ Phase 11 du ticket : la sévérité ne doit jamais juger l'opinion elle-même, seulement
# la qualité de l'argumentation) — réutilisée telle quelle par toutes les questions de ce
# type, pour ne jamais l'oublier sur l'une d'elles.
_OPINION_NEUTRALITY_CLAUSE = (
    "Toute position (d'accord ou pas d'accord, pour ou contre) est acceptée si elle est "
    "justifiée de manière cohérente. Ne juge JAMAIS l'opinion exprimée elle-même — "
    "seulement la qualité et la cohérence de la justification."
)

# Grille de correction enrichie pour les réponses longues argumentées (§ Phase 10 du
# ticket : le feedback IA doit être plus pédagogique qu'un simple score). Le contrat #23
# n'a pas de champ dédié à une structure de feedback imposée — cette instruction vit dans
# le `rubric` de CHAQUE question longue, transmis tel quel au correcteur IA
# (`app.ai.prompts.build_correct_semantic_messages`), plutôt que de modifier le moteur de
# correction générique partagé avec l'Informatique (aucune nouvelle architecture).
_LONG_ANSWER_FEEDBACK_STRUCTURE_CLAUSE = (
    "Dans ton champ `feedback`, structure ton retour pédagogique avec ces éléments, "
    "dans cet ordre, chacun sur une ligne : STRUCTURE (introduction/développement/"
    "conclusion présents ou non), ARGUMENTATION (nombre et qualité des arguments), "
    "UTILISATION DU DOCUMENT (référence ou non au texte, à propos), LANGUE / CLARTÉ "
    "(qualité de l'expression), puis une phrase d'EXEMPLE D'AMÉLIORATION concrète (une "
    "reformulation ciblée d'un passage précis de la copie, jamais une réécriture "
    "complète du texte de l'utilisateur à sa place). Utilise `strengths` pour les points "
    "forts, `missing` pour les éléments manquants, `errors` uniquement pour de vraies "
    "erreurs (jamais l'opinion choisie)."
)


def _francais_c01_questions(doc_ids: dict[str, int]) -> list[tuple[str, dict]]:
    """`doc_ids` : {"main": ..., "second": ..., "digital_life": ..., "training": ...,
    "coding_debate": ...} — les `current_version_id` des 5 SourceDocument importés."""
    main = doc_ids["main"]
    second = doc_ids["second"]
    digital_life = doc_ids["digital_life"]
    training = doc_ids["training"]
    coding_debate = doc_ids["coding_debate"]

    return [
        # ============================================================================
        # Document pilote initial (smartphone) — inchangé depuis le ticket #47, hors le
        # correctif de l'explication Fait/Opinion (voir commentaire sur cette question).
        # ============================================================================
        (
            "short_answer",
            {
                "prompt": (
                    "D'après le texte, cite deux avantages du smartphone mentionnés pour "
                    "un usage professionnel."
                ),
                "source_document_version_id": main,
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
                "source_document_version_id": main,
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
                "source_document_version_id": main,
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
                "source_document_version_id": main,
                "categories": ["Fait", "Opinion"],
                "elements": [
                    "Plusieurs écoles ont interdit le smartphone pendant les heures de cours.",
                    "Le smartphone n'est ni un ennemi ni un allié absolu.",
                    (
                        "Certaines entreprises ont mis en place un droit de ne pas "
                        "répondre aux emails après une certaine heure."
                    ),
                ],
                # Bug identifié en review (#47) : l'explication disait auparavant « les
                # deux premières affirmations rapportent des faits [...] ; la deuxième
                # est un jugement de valeur » — contradictoire (la 2e ne peut pas être à
                # la fois un fait ET un jugement). `correct_categories=[0, 1, 0]` était
                # déjà correct (élément 0=Fait, 1=Opinion, 2=Fait) ; seul le texte de
                # l'explication était faux. Corrigé pour refléter fidèlement le mapping.
                "correct_categories": [0, 1, 0],
                "explanation": (
                    "La première et la troisième affirmations rapportent des faits "
                    "observables décrits dans le texte ; la deuxième est un jugement de "
                    "valeur de l'auteur."
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
                "source_document_version_id": main,
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
                "source_document_version_id": main,
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
                "source_document_version_id": main,
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
                "source_document_version_id": main,
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
                "rubric": f"{_OPINION_NEUTRALITY_CLAUSE}",
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
                "source_document_version_id": main,
                "rubric": (
                    "Évalue : (1) présence d'une structure claire (introduction, "
                    "arguments, conclusion) ; (2) au moins deux arguments distincts et "
                    "justifiés, en lien avec le sujet ; (3) référence possible (mais pas "
                    "obligatoire) au texte fourni ; (4) qualité de l'expression écrite "
                    "adaptée au niveau CESS. Ne juge jamais la position choisie "
                    "(pour/contre/nuancée) elle-même, seulement la qualité argumentative "
                    f"et structurelle. {_LONG_ANSWER_FEEDBACK_STRUCTURE_CLAUSE}"
                ),
                "expected_points": [
                    "Structure claire (introduction/développement/conclusion)",
                    "Au moins deux arguments distincts et justifiés",
                    "Expression écrite cohérente et adaptée au niveau CESS",
                ],
                # Ticket #73 : 6000 était déjà généreux mais restait sous le plancher de
                # 10 000 caractères réellement supportés désormais — aligné sur le nouveau
                # défaut (`LongAnswerContent.max_length`, app/v1/question_types.py).
                "max_length": 20_000,
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
                "source_document_version_ids": [main, second],
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
        # ============================================================================
        # Comparaison (smartphone, suite) — 3 questions supplémentaires sur la MÊME
        # paire de documents (§ Phase 7 : renforcer la compétence « comparaison »).
        # ============================================================================
        (
            "source_comparison",
            {
                "prompt": (
                    "Les deux textes évoquent tous deux un effet du smartphone sur la "
                    "concentration. Quel est ce point commun, et quelle différence "
                    "observes-tu dans l'importance que chaque texte lui accorde ?"
                ),
                "source_document_version_ids": [main, second],
                "rubric": (
                    "Bonne réponse si elle identifie que les deux textes évoquent la "
                    "perte de concentration comme un risque du smartphone, mais que le "
                    "texte principal le présente comme UN risque parmi d'autres (vision "
                    "équilibrée), alors que le second texte en fait l'argument CENTRAL et "
                    "décisif justifiant une interdiction totale."
                ),
                "expected_points": [
                    "Identifie le point commun (effet sur la concentration)",
                    "Identifie la différence de poids accordé à cet argument",
                ],
            },
        ),
        (
            "source_comparison",
            {
                "prompt": (
                    "Le texte principal propose une « troisième voie » entre "
                    "interdiction totale et usage libre. Le second texte accepte-t-il "
                    "cette idée de compromis ? Justifie avec un passage du second texte."
                ),
                "source_document_version_ids": [main, second],
                "rubric": (
                    "Bonne réponse si elle indique que le second texte REJETTE "
                    "explicitement l'idée d'un compromis nuancé (« Contrairement à une "
                    "position nuancée qui chercherait un équilibre »), et défend au "
                    "contraire une règle simple et non négociable."
                ),
                "expected_points": [
                    "Identifie le rejet du compromis par le second texte",
                    "S'appuie sur un passage précis du second texte",
                ],
            },
        ),
        (
            "source_comparison",
            {
                "prompt": (
                    "D'après le second texte, pourquoi une règle simple et non "
                    "négociable serait-elle plus facile à faire respecter qu'un usage "
                    "« raisonné » ? Le texte principal répond-il à cet argument précis ?"
                ),
                "source_document_version_ids": [main, second],
                "rubric": (
                    "Bonne réponse si elle explique que le second texte juge une règle "
                    "simple plus facile à appliquer car elle ne dépend pas du jugement "
                    "individuel de chaque élève, et observe que le texte principal ne "
                    "traite pas directement de la facilité d'application — il met plutôt "
                    "l'accent sur la responsabilisation individuelle."
                ),
                "expected_points": [
                    "Explique l'argument de facilité d'application du second texte",
                    "Observe que le texte principal ne le contredit pas frontalement",
                ],
            },
        ),
        # ============================================================================
        # Document 1 — Compréhension/argumentation (numérique au quotidien)
        # ============================================================================
        (
            "short_answer",
            {
                "prompt": (
                    "D'après le texte, cite deux démarches ou services qui se font "
                    "désormais très largement en ligne."
                ),
                "source_document_version_id": digital_life,
                "rubric": (
                    "Réponse correcte si elle cite au moins deux éléments parmi : "
                    "démarches administratives, gestion d'un compte bancaire, prise de "
                    "rendez-vous médical, achats en ligne."
                ),
                "max_length": 300,
            },
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "Pourquoi, selon le texte, la facilité d'accès à une information en "
                    "ligne ne garantit-elle pas sa fiabilité ?"
                ),
                "source_document_version_id": digital_life,
                "rubric": (
                    "Bonne réponse si elle indique que toutes les informations "
                    "disponibles en ligne ne se valent pas, et qu'il faut savoir "
                    "distinguer une source sérieuse d'une source douteuse."
                ),
                "max_length": 400,
            },
        ),
        (
            "vocabulary",
            {
                "prompt": "Que désigne l'expression « fracture numérique » utilisée dans le texte ?",
                "source_document_version_id": digital_life,
                "rubric": (
                    "Bonne réponse si elle indique qu'il s'agit de l'écart entre les "
                    "personnes qui maîtrisent les outils numériques et celles qui en sont "
                    "exclues (par exemple pour des démarches essentielles)."
                ),
            },
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "Le texte ne dit jamais explicitement que certaines personnes sont "
                    "désavantagées par la numérisation des services, mais le suggère "
                    "fortement. Quel passage te permet de l'affirmer ?"
                ),
                "source_document_version_id": digital_life,
                "rubric": (
                    "Bonne réponse si elle cite ou paraphrase le passage sur la « "
                    "fracture numérique » : les personnes âgées ou peu à l'aise avec le "
                    "numérique peuvent être exclues de démarches essentielles (document "
                    "d'identité, aides sociales)."
                ),
                "max_length": 400,
            },
        ),
        (
            "classification",
            {
                "prompt": (
                    "Classe chaque affirmation suivante comme un FAIT rapporté par le "
                    "texte, ou une OPINION/un jugement de l'auteur."
                ),
                "source_document_version_id": digital_life,
                "categories": ["Fait", "Opinion"],
                "elements": [
                    "Le télétravail s'est largement développé ces dernières années.",
                    "Le numérique n'est ni une simple commodité ni une menace uniforme.",
                    "Les formations en ligne permettent d'apprendre de nouvelles compétences sans se déplacer.",
                ],
                "correct_categories": [0, 1, 0],
                "explanation": (
                    "La première et la troisième affirmations rapportent des faits "
                    "décrits dans le texte (développement du télétravail, existence des "
                    "formations en ligne) ; la deuxième est la conclusion/le jugement "
                    "personnel de l'auteur sur le numérique en général."
                ),
            },
        ),
        (
            "short_answer",
            {
                "prompt": "Quelle est l'idée principale du texte ? Résume-la en une phrase.",
                "source_document_version_id": digital_life,
                "rubric": (
                    "Bonne réponse si elle indique que le numérique transforme "
                    "profondément plusieurs aspects du quotidien (information, services, "
                    "relations sociales, travail/formation), avec des bénéfices réels "
                    "mais des effets qui ne touchent pas tout le monde de la même façon."
                ),
                "max_length": 400,
            },
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "Es-tu d'accord avec l'idée que le numérique « ne remplace pas les "
                    "relations humaines, mais en modifie clairement les formes » ? "
                    "Justifie ta réponse en 2 à 3 phrases."
                ),
                "rubric": f"{_OPINION_NEUTRALITY_CLAUSE}",
                "max_length": 500,
            },
        ),
        (
            "document_analysis",
            {
                "prompt": (
                    "Identifie un passage du texte qui illustre un bénéfice concret du "
                    "télétravail, et explique en quoi il illustre ce bénéfice."
                ),
                "source_document_version_id": digital_life,
                "rubric": (
                    "Bonne réponse si elle cite ou paraphrase le passage sur la "
                    "flexibilité nouvelle dans l'organisation du temps offerte par le "
                    "télétravail, et explique en quoi c'est un bénéfice concret."
                ),
                "expected_points": [
                    "Cite ou paraphrase un exemple concret du texte",
                    "Explique en quoi cet exemple est un bénéfice",
                ],
            },
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "Selon le texte, quel effet le temps passé sur les écrans peut-il "
                    "avoir sur les interactions sociales ?"
                ),
                "source_document_version_id": digital_life,
                "rubric": (
                    "Bonne réponse si elle indique que le temps passé sur les écrans "
                    "peut se substituer à des interactions en face à face, et que "
                    "l'exposition aux publications d'autrui peut alimenter un sentiment "
                    "de comparaison sociale inconfortable."
                ),
                "max_length": 400,
            },
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "Reformule en une phrase l'idée développée dans le paragraphe "
                    "consacré au travail et à la formation."
                ),
                "source_document_version_id": digital_life,
                "rubric": (
                    "Bonne réponse si elle résume que le numérique (télétravail, "
                    "formations en ligne) apporte plus de flexibilité, mais demande une "
                    "capacité d'organisation personnelle plus importante."
                ),
                "max_length": 300,
            },
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "Le texte conclut qu'une « position tranchée semble difficile à "
                    "défendre » à propos du numérique. Es-tu d'accord avec cette "
                    "conclusion ? Justifie ta réponse en t'appuyant sur au moins un "
                    "exemple du texte."
                ),
                "source_document_version_id": digital_life,
                "rubric": (
                    f"{_OPINION_NEUTRALITY_CLAUSE} Attendu en plus : la justification "
                    "s'appuie sur au moins un exemple concret tiré du texte (fracture "
                    "numérique, télétravail, réseaux sociaux, fiabilité de "
                    "l'information...)."
                ),
                "max_length": 600,
            },
        ),
        # ============================================================================
        # Document 2 — Synthèse (formation professionnelle et numérique)
        # ============================================================================
        (
            "short_answer",
            {
                "prompt": (
                    "D'après le texte, quel est le principal avantage de l'apprentissage "
                    "en ligne pour une personne qui travaille à temps plein ?"
                ),
                "source_document_version_id": training,
                "rubric": (
                    "Bonne réponse si elle indique que ces formations peuvent être "
                    "suivies à n'importe quel moment (souvent le soir ou le week-end), "
                    "sans devoir demander un congé ni réorganiser toute sa semaine."
                ),
                "max_length": 300,
            },
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "Quel problème documenté par les chercheurs en pédagogie le texte "
                    "associe-t-il aux formations en ligne non accompagnées ?"
                ),
                "source_document_version_id": training,
                "rubric": (
                    "Bonne réponse si elle indique que le taux d'abandon y est nettement "
                    "plus élevé que dans une formation classique en présentiel, faute de "
                    "motivation suffisante ou de temps réellement dégagé."
                ),
                "max_length": 400,
            },
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "Selon le texte, pourquoi certaines formations courtes et intensives "
                    "de reconversion sont-elles critiquées par certains employeurs ?"
                ),
                "source_document_version_id": training,
                "rubric": (
                    "Bonne réponse si elle indique qu'une formation aussi courte est "
                    "jugée incapable de remplacer entièrement un parcours plus complet, "
                    "notamment pour les aspects les plus techniques ou théoriques d'un "
                    "métier."
                ),
                "max_length": 400,
            },
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "D'après le texte, pourquoi le phénomène de reconversion "
                    "professionnelle s'est-il accéléré ces dernières années ?"
                ),
                "source_document_version_id": training,
                "rubric": (
                    "Bonne réponse si elle indique que certains métiers disparaissent "
                    "progressivement pendant que d'autres, liés au numérique, "
                    "connaissent une forte demande de main-d'œuvre."
                ),
                "max_length": 400,
            },
        ),
        (
            "long_answer",
            {
                "prompt": (
                    "Rédige une synthèse courte (5 à 8 phrases) du texte, reprenant les "
                    "idées essentielles (apprentissage en ligne, reconversion "
                    "professionnelle, certifications) SANS reprendre les détails "
                    "secondaires ni recopier des phrases du texte."
                ),
                "source_document_version_id": training,
                "rubric": (
                    "Évalue : (1) sélection correcte des idées essentielles (les 3 axes "
                    "du texte) plutôt que des détails secondaires (exemples précis de "
                    "métiers, noms de plateformes) ; (2) reformulation réelle, jamais une "
                    "copie de phrases du texte ; (3) concision réelle (5 à 8 phrases) ; "
                    f"(4) lisibilité/structure de la synthèse. {_LONG_ANSWER_FEEDBACK_STRUCTURE_CLAUSE}"
                ),
                "expected_points": [
                    "Reprend les 3 idées essentielles sans les détails secondaires",
                    "Reformule sans copier le texte",
                    "Reste concis (5 à 8 phrases)",
                ],
                "max_length": 20_000,
            },
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "Propose un titre différent de celui du texte, qui reflète "
                    "fidèlement l'ensemble de son contenu (pas un seul aspect isolé)."
                ),
                "source_document_version_id": training,
                "rubric": (
                    "Bonne réponse si le titre proposé couvre la diversification des "
                    "formes de formation professionnelle liées au numérique (pas "
                    "seulement l'e-learning, ou seulement la reconversion, pris "
                    "isolément) — évaluation souple sur la formulation exacte."
                ),
                "max_length": 200,
            },
        ),
        (
            "vocabulary",
            {
                "prompt": "Que désigne le terme « e-learning » tel qu'il est utilisé dans le texte ?",
                "source_document_version_id": training,
                "rubric": (
                    "Bonne réponse si elle indique qu'il s'agit de l'apprentissage/la "
                    "formation en ligne via des plateformes numériques spécialisées."
                ),
            },
        ),
        (
            "document_analysis",
            {
                "prompt": (
                    "Identifie un passage qui illustre une limite des certifications "
                    "numériques par rapport à un diplôme traditionnel, et explique en "
                    "quoi il illustre cette limite."
                ),
                "source_document_version_id": training,
                "rubric": (
                    "Bonne réponse si elle cite ou paraphrase le passage indiquant que "
                    "ces certifications ne bénéficient pas toujours de la même "
                    "reconnaissance qu'un diplôme officiel, en particulier en dehors du "
                    "secteur technologique."
                ),
                "expected_points": [
                    "Cite ou paraphrase le passage sur la reconnaissance limitée",
                    "Explique en quoi c'est une limite concrète",
                ],
            },
        ),
        (
            "vocabulary",
            {
                "prompt": "Que désigne l'expression « formation continue » dans le texte ?",
                "source_document_version_id": training,
                "rubric": (
                    "Bonne réponse si elle indique qu'il s'agit de la possibilité, pour "
                    "un employé, de continuer à se former pendant sa carrière (ex. accès "
                    "à des plateformes en ligne mis à disposition par l'entreprise)."
                ),
            },
        ),
        # ============================================================================
        # Document 5 — Opinion argumentée (débat : programmation à l'école)
        # ============================================================================
        (
            "short_answer",
            {
                "prompt": (
                    "Quel argument les partisans de l'enseignement de la programmation à "
                    "l'école avancent-ils, selon le texte ?"
                ),
                "source_document_version_id": coding_debate,
                "rubric": (
                    "Bonne réponse si elle indique que le numérique est présent dans "
                    "presque tous les métiers, et qu'une compréhension même basique de "
                    "la logique de programmation aiderait les élèves à mieux comprendre "
                    "le monde (comparaison avec l'apprentissage des sciences)."
                ),
                "max_length": 400,
            },
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "Quel argument concernant le temps scolaire les opposants à cette "
                    "idée avancent-ils ?"
                ),
                "source_document_version_id": coding_debate,
                "rubric": (
                    "Bonne réponse si elle indique que le temps scolaire est déjà "
                    "largement occupé, et qu'ajouter une matière obligatoire "
                    "supplémentaire se ferait au détriment d'autres apprentissages jugés "
                    "tout aussi essentiels."
                ),
                "max_length": 400,
            },
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "Le texte évoque un désaccord sur ce que signifierait concrètement "
                    "« apprendre à programmer » à l'école. Quelles sont les deux "
                    "interprétations possibles évoquées ?"
                ),
                "source_document_version_id": coding_debate,
                "rubric": (
                    "Bonne réponse si elle mentionne (1) apprendre un langage de "
                    "programmation précis (avec le risque qu'il devienne obsolète), et "
                    "(2) apprendre une « pensée computationnelle » générale — décomposer "
                    "un problème en étapes logiques."
                ),
                "max_length": 500,
            },
        ),
        (
            "vocabulary",
            {
                "prompt": "Que désigne l'expression « pensée computationnelle » dans le texte ?",
                "source_document_version_id": coding_debate,
                "rubric": (
                    "Bonne réponse si elle indique qu'il s'agit d'une manière générale "
                    "de décomposer un problème en étapes logiques, distincte de "
                    "l'apprentissage d'un langage de programmation précis."
                ),
            },
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "Penses-tu que la « pensée computationnelle » est une compétence "
                    "utile même pour des métiers non liés à l'informatique ? Justifie en "
                    "2 à 3 phrases."
                ),
                # Contrairement aux questions d'opinion similaires (ex. « Es-tu d'accord
                # avec l'affirmation que le smartphone est... ») qui citent la position
                # jugée EN ENTIER dans le prompt, ce terme technique n'est pas défini ici
                # — sa définition vit dans une AUTRE question (vocabulaire), non garantie
                # d'être tirée dans la même session (#79 § 4) : le document reste
                # nécessaire pour comprendre le terme avant d'exprimer un avis dessus.
                "source_document_version_id": coding_debate,
                "rubric": f"{_OPINION_NEUTRALITY_CLAUSE}",
                "max_length": 500,
            },
        ),
        (
            "long_answer",
            {
                "prompt": (
                    "En t'appuyant sur le texte et sur ton propre avis, rédige un texte "
                    "argumenté (introduction, au moins deux arguments justifiés avec des "
                    "exemples, conclusion) donnant ta position sur la question : "
                    "faut-il enseigner les bases de la programmation à tous les élèves "
                    "du secondaire ?"
                ),
                "source_document_version_id": coding_debate,
                "rubric": (
                    "Évalue : (1) structure claire (introduction/arguments/conclusion) ; "
                    "(2) au moins deux arguments distincts, justifiés et illustrés par un "
                    "exemple ; (3) usage de connecteurs logiques ; (4) référence possible "
                    "(mais pas obligatoire) aux arguments du texte ; (5) qualité de "
                    "l'expression écrite adaptée au niveau CESS. Ne juge JAMAIS la "
                    "position choisie (pour/contre/nuancée) elle-même — aucune opinion "
                    "politique ou polémique n'est en jeu ici, uniquement la qualité "
                    f"argumentative et structurelle. {_LONG_ANSWER_FEEDBACK_STRUCTURE_CLAUSE}"
                ),
                "expected_points": [
                    "Structure claire (introduction/développement/conclusion)",
                    "Au moins deux arguments distincts, justifiés et illustrés",
                    "Connecteurs logiques présents",
                    "Expression écrite cohérente et adaptée au niveau CESS",
                ],
                "max_length": 20_000,
            },
        ),
    ]


def import_francais_c01_to_bank(db: Session, module: Module, uaa: UAA) -> int:
    """Importe le corpus Français C01 (5 SourceDocument + 40 questions) dans la banque
    V1, scopé à `uaa`. Idempotent au niveau processus : si des Question existent déjà
    pour cette UAA avec `generation_source=IMPORTED`, ne réimporte rien — même garantie
    que `app.v1.bank.import_mc01_legacy_to_bank`."""
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
    digital_life_document = create_source_document(
        db, title=DIGITAL_LIFE_DOCUMENT_TITLE, content_text=DIGITAL_LIFE_DOCUMENT_TEXT, module_id=module.id
    )
    training_document = create_source_document(
        db, title=TRAINING_DOCUMENT_TITLE, content_text=TRAINING_DOCUMENT_TEXT, module_id=module.id
    )
    coding_debate_document = create_source_document(
        db, title=CODING_DEBATE_DOCUMENT_TITLE, content_text=CODING_DEBATE_DOCUMENT_TEXT, module_id=module.id
    )
    db.flush()

    doc_ids = {
        "main": main_document.current_version_id,
        "second": second_document.current_version_id,
        "digital_life": digital_life_document.current_version_id,
        "training": training_document.current_version_id,
        "coding_debate": coding_debate_document.current_version_id,
    }

    imported = 0
    for question_type, content in _francais_c01_questions(doc_ids):
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
