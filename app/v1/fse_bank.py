"""Banque V1 FSE — FSE01-FSE08 (ticket #96 : FSE01 ; ticket #97 : FSE02-FSE04 ; ticket #98 :
FSE05-FSE08), cahiers des charges détaillés des tickets correspondants.

Même principe que `app.v1.francais_fr01_05_bank` (#94, plusieurs cours dans un seul
fichier de banque) : import idempotent, hand-authored, revalidé par le registre #40
(`validate_content`) avant stockage — aucune question ne référence un texte sans un
`SourceDocumentVersion` réellement rattaché quand le type le permet (`short_answer`/
`vocabulary`/`classification`/`document_analysis`/`long_answer` portent un
`source_document_version_id` optionnel ou requis selon le type ; `multiple_choice`/
`ordering` n'ont pas ce champ dans le registre #40 — ces questions restent volontairement
conceptuelles, jamais un résumé dupliqué d'un document).

Chaque question porte une difficulté déclarée (`Question.difficulty_declared`, ticket #96
review) : réellement honorée par `app.v1.bank._prioritize_by_difficulty`/
`app.v1.session_service.compose_selection` lors de la sélection d'une session."""

from sqlalchemy.orm import Session

from app.models import UAA, Module
from app.v1 import question_types  # noqa: F401 — enregistre les 26 types (#40) au chargement
from app.v1.fse01_content import (
    FSE01_AFFICHE_TEXT,
    FSE01_AFFICHE_TITLE,
    FSE01_MAIL_TEXT,
    FSE01_MAIL_TITLE,
    FSE01_SOCIAL_TEXT,
    FSE01_SOCIAL_TITLE,
)
from app.v1.fse02_content import (
    FSE02_FREE_AD_TEXT,
    FSE02_FREE_AD_TITLE,
    FSE02_PAID_TEXT,
    FSE02_PAID_TITLE,
    FSE02_PUBLIC_TEXT,
    FSE02_PUBLIC_TITLE,
)
from app.v1.fse03_content import (
    FSE03_HR_NOTE_TEXT,
    FSE03_HR_NOTE_TITLE,
    FSE03_PROFILE_TEXT,
    FSE03_PROFILE_TITLE,
)
from app.v1.fse04_content import (
    FSE04_GROUP_TEXT,
    FSE04_GROUP_TITLE,
    FSE04_TESTIMONY_TEXT,
    FSE04_TESTIMONY_TITLE,
)
from app.v1.fse05_content import FSE05_SITUATIONS_TEXT, FSE05_SITUATIONS_TITLE
from app.v1.fse06_content import FSE06_SCENARIOS_TEXT, FSE06_SCENARIOS_TITLE
from app.v1.fse07_content import (
    FSE07_CHAT_TEXT,
    FSE07_CHAT_TITLE,
    FSE07_FORUM_TEXT,
    FSE07_FORUM_TITLE,
    FSE07_SCHOOL_TEXT,
    FSE07_SCHOOL_TITLE,
)
from app.v1.fse08_content import FSE08_MAP_TEXT, FSE08_MAP_TITLE
from app.v1.models import (
    GenerationSource,
    Question,
    QuestionDifficulty,
    create_question,
    create_source_document,
)
from app.v1.question_engine import validate_content


def import_fse01_to_bank(db: Session, module: Module, uaa: UAA) -> int:
    already_imported = (
        db.query(Question).filter_by(uaa_id=uaa.id, generation_source=GenerationSource.IMPORTED).count()
    )
    if already_imported:
        return 0

    mail = create_source_document(db, title=FSE01_MAIL_TITLE, content_text=FSE01_MAIL_TEXT, module_id=module.id)
    affiche = create_source_document(db, title=FSE01_AFFICHE_TITLE, content_text=FSE01_AFFICHE_TEXT, module_id=module.id)
    social = create_source_document(db, title=FSE01_SOCIAL_TITLE, content_text=FSE01_SOCIAL_TEXT, module_id=module.id)
    db.flush()
    mail_id, affiche_id, social_id = (
        mail.current_version_id, affiche.current_version_id, social.current_version_id,
    )

    # Difficulté déclarée (ticket #96, review) : jugée sur la complexité cognitive réelle
    # de chaque question — identification directe d'un élément nommé dans le document
    # (EASY), explication reliant plusieurs éléments ou une définition simple (MEDIUM),
    # analyse complète croisant plusieurs notions avec justification rédigée (HARD).
    # Répartition : 6 EASY, 5 MEDIUM, 3 HARD.
    questions: list[tuple[str, dict, QuestionDifficulty]] = [
        (
            "short_answer",
            {
                "prompt": (
                    "Dans le mail de Karim Haddad, identifie l'émetteur et le récepteur "
                    "de cette communication."
                ),
                "source_document_version_id": mail_id,
                "rubric": (
                    "Bonne réponse si elle identifie Karim Haddad (le candidat) comme "
                    "émetteur et le service recrutement des Entrepôts Dufresne comme "
                    "récepteur."
                ),
                "max_length": 300,
            },
            QuestionDifficulty.EASY,
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "Quel obstacle a perturbé la communication de Karim Haddad, et quelle "
                    "en a été la conséquence concrète pour le récepteur ?"
                ),
                "source_document_version_id": mail_id,
                "rubric": (
                    "Bonne réponse si elle identifie la coupure de connexion internet "
                    "comme obstacle, et explique que le message envoyé automatiquement "
                    "était incomplet (phrase coupée, aucune pièce jointe), empêchant le "
                    "service recrutement d'évaluer la candidature."
                ),
                "max_length": 400,
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "Quel code (système de signes) est utilisé dans l'affiche de sécurité "
                    "routière pour transmettre son message ?"
                ),
                "source_document_version_id": affiche_id,
                "rubric": (
                    "Bonne réponse si elle cite au moins deux éléments du code utilisé : "
                    "un texte court et percutant, une image (silhouette d'enfant), des "
                    "couleurs porteuses de sens (le rouge signale le danger), un logo "
                    "institutionnel."
                ),
                "max_length": 300,
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "multiple_choice",
            {
                "prompt": "Le canal (ou contact) d'une communication désigne...",
                "options": [
                    {"option_id": "a", "label": "Le système de signes utilisé pour construire le message (langue, images, couleurs)"},
                    {"option_id": "b", "label": "Le support matériel ou technique par lequel le message circule"},
                    {"option_id": "c", "label": "La personne qui reçoit le message"},
                    {"option_id": "d", "label": "La situation dans laquelle le message est émis"},
                ],
                "correct_option_ids": ["b"],
                "explanation": (
                    "Le canal est PAR OÙ passe le message (une connexion internet, une "
                    "feuille affichée, une plateforme en ligne) — à ne jamais confondre "
                    "avec le code, le système de signes AVEC LEQUEL le message est "
                    "construit."
                ),
            },
            QuestionDifficulty.EASY,
        ),
        (
            "multiple_choice",
            {
                "prompt": "Le contexte (ou référent) d'une communication désigne...",
                "options": [
                    {"option_id": "a", "label": "La situation, le sujet ou les circonstances qui donnent son sens exact au message"},
                    {"option_id": "b", "label": "La personne qui envoie le message"},
                    {"option_id": "c", "label": "Le support technique utilisé pour transmettre le message"},
                    {"option_id": "d", "label": "La réponse du récepteur à l'émetteur"},
                ],
                "correct_option_ids": ["a"],
                "explanation": (
                    "Le contexte, c'est la situation qui permet de donner son sens exact "
                    "au message : un même message peut être compris différemment selon "
                    "le contexte dans lequel il est émis."
                ),
            },
            QuestionDifficulty.EASY,
        ),
        (
            "multiple_choice",
            {
                "prompt": "La rétroaction, dans le schéma de communication, désigne...",
                "options": [
                    {"option_id": "a", "label": "Un obstacle qui perturbe la transmission du message"},
                    {"option_id": "b", "label": "Le système de signes utilisé pour construire le message"},
                    {"option_id": "c", "label": "La réponse que le récepteur peut renvoyer à l'émetteur"},
                    {"option_id": "d", "label": "Le support matériel utilisé pour transmettre le message"},
                ],
                "correct_option_ids": ["c"],
                "explanation": (
                    "La rétroaction est la réponse du récepteur à l'émetteur ; sa "
                    "possibilité dépend directement du canal utilisé — certains canaux "
                    "la permettent facilement, d'autres ne la permettent pas du tout."
                ),
            },
            QuestionDifficulty.EASY,
        ),
        (
            "classification",
            {
                "prompt": (
                    "Classe chaque élément de l'affiche de sécurité routière dans la "
                    "bonne catégorie du schéma de communication."
                ),
                "source_document_version_id": affiche_id,
                "categories": ["Émetteur", "Récepteur", "Message", "Canal"],
                "elements": [
                    "Le Service public de Wallonie",
                    "Les automobilistes circulant sur cette route",
                    "Inciter à ralentir à l'approche d'un passage piéton",
                    "Un panneau d'affichage fixe installé en bordure de route",
                ],
                "correct_categories": [0, 1, 2, 3],
                "explanation": (
                    "Le SPW est l'organisme à l'origine de la campagne (émetteur), les "
                    "automobilistes en sont les destinataires (récepteur), le fait "
                    "d'inciter à ralentir est ce qui est réellement transmis (message), "
                    "et le panneau d'affichage est le support matériel utilisé (canal)."
                ),
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "classification",
            {
                "prompt": (
                    "Pour chacun de ces trois canaux, indique si une rétroaction directe "
                    "(une réponse que le récepteur peut adresser à l'émetteur par ce "
                    "même canal, quel que soit le délai avant qu'elle n'arrive) est "
                    "possible ou non."
                ),
                "categories": ["Rétroaction directe possible", "Rétroaction directe impossible"],
                "elements": [
                    "Le mail de candidature de Karim Haddad",
                    "La publication sur le réseau social de Techno Services Wallonie",
                    "L'affiche de sécurité routière",
                ],
                "correct_categories": [0, 0, 1],
                "explanation": (
                    "Un mail et une publication sur réseau social permettent tous deux "
                    "d'adresser une réponse directement à l'émetteur (le service "
                    "recrutement répond à Karim — avec un jour de délai dans ce document, "
                    "ce qui ne change rien : seul le canal permet ou empêche la "
                    "rétroaction, jamais sa rapidité ; des commentaires répondent de même "
                    "à Techno Services). Une affiche, elle, ne permet aucune rétroaction "
                    "directe vers son émetteur, quel que soit le délai."
                ),
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "vocabulary",
            {
                "prompt": "Définis le canal (ou contact) dans le schéma de communication.",
                "direction": "term_to_definition",
                "rubric": (
                    "Bonne réponse si elle définit le canal comme le support matériel ou "
                    "technique par lequel le message circule (ex. une connexion "
                    "internet, une feuille affichée, une plateforme en ligne), distinct "
                    "du code."
                ),
            },
            QuestionDifficulty.EASY,
        ),
        (
            "vocabulary",
            {
                "prompt": "Définis un obstacle (ou bruit) dans le schéma de communication.",
                "direction": "term_to_definition",
                "rubric": (
                    "Bonne réponse si elle définit l'obstacle comme tout ce qui perturbe "
                    "ou empêche la bonne transmission d'un message, en donnant un exemple "
                    "technique (ex. une coupure de connexion) OU lié au contenu (ex. une "
                    "information manquante ou une formulation ambiguë)."
                ),
            },
            QuestionDifficulty.EASY,
        ),
        (
            "ordering",
            {
                "prompt": (
                    "Remets dans l'ordre les étapes d'une communication, de l'émission du "
                    "message à la rétroaction."
                ),
                "items": [
                    {"id": "e1", "label": "L'émetteur formule un message"},
                    {"id": "e2", "label": "Le message est mis en forme à l'aide d'un code"},
                    {"id": "e3", "label": "Le message est transmis via un canal"},
                    {"id": "e4", "label": "Le récepteur reçoit le message"},
                    {"id": "e5", "label": "Le récepteur interprète le message selon le contexte"},
                    {"id": "e6", "label": "Le récepteur peut renvoyer une rétroaction à l'émetteur"},
                ],
                "correct_order": ["e1", "e2", "e3", "e4", "e5", "e6"],
                "explanation": (
                    "Le message est d'abord formulé puis codé, transmis via un canal, "
                    "reçu, interprété selon le contexte, et peut enfin donner lieu à une "
                    "rétroaction — si le canal le permet."
                ),
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "document_analysis",
            {
                "prompt": (
                    "Analyse complète de l'affiche de sécurité routière : identifie les "
                    "six éléments du schéma de communication (émetteur, récepteur, "
                    "message, code, canal, contexte), puis explique pourquoi ce canal ne "
                    "permet pas de rétroaction directe vers l'émetteur."
                ),
                "source_document_version_id": affiche_id,
                "rubric": (
                    "4 points : les six éléments du schéma correctement identifiés et "
                    "justifiés par un élément précis de l'affiche (2 points) ; distinction "
                    "correcte entre code (texte, image, couleurs, logo) et canal (panneau "
                    "d'affichage) (1 point) ; explication correcte de l'absence de "
                    "rétroaction directe (le conducteur n'a aucun moyen de s'adresser "
                    "directement à l'émetteur depuis son véhicule, quel que soit le "
                    "délai) (1 point)."
                ),
                "expected_points": [
                    "Identifie l'émetteur (SPW) et le récepteur (automobilistes)",
                    "Résume le message (inciter à ralentir près d'un passage piéton)",
                    "Décrit le code (texte, image, couleurs, logo) sans le confondre avec le canal",
                    "Identifie le canal (panneau d'affichage) et le contexte (sécurité routière)",
                    "Explique pourquoi aucune rétroaction directe n'est possible via ce canal",
                ],
                "max_score": 4.0,
            },
            QuestionDifficulty.HARD,
        ),
        (
            "document_analysis",
            {
                "prompt": (
                    "Analyse la publication de Techno Services Wallonie : identifie un "
                    "obstacle présent dans cette communication, puis explique en quoi les "
                    "commentaires qui suivent la publication constituent une rétroaction."
                ),
                "source_document_version_id": social_id,
                "rubric": (
                    "3 points : identification de l'absence d'information sur le salaire "
                    "comme obstacle, appuyée sur le commentaire de Julien P. (1 point) ; "
                    "explication que les commentaires/partages/réponse de l'entreprise "
                    "constituent une rétroaction directement adressée à l'émetteur et "
                    "publique (1 point) ; mise en évidence que ce canal permet un "
                    "dialogue (l'entreprise répond elle-même à un commentaire) (1 point)."
                ),
                "expected_points": [
                    "Identifie l'absence d'information sur le salaire comme obstacle",
                    "Relie cet obstacle au commentaire de Julien P.",
                    "Identifie les commentaires/partages comme rétroaction",
                    "Mentionne que l'entreprise répond elle-même à un commentaire (dialogue)",
                ],
                "max_score": 3.0,
            },
            QuestionDifficulty.HARD,
        ),
        (
            "long_answer",
            {
                "prompt": (
                    "Rédige une réponse complète : à partir du mail de Karim Haddad, "
                    "identifie l'obstacle qui a perturbé cette communication, explique sa "
                    "conséquence concrète, puis explique comment la rétroaction du "
                    "service recrutement permet de résoudre la situation."
                ),
                "source_document_version_id": mail_id,
                "rubric": (
                    "3 points : identification claire de l'obstacle (coupure de "
                    "connexion ayant interrompu l'envoi du message) (1 point) ; "
                    "explication de la conséquence concrète (message incomplet, sans "
                    "pièce jointe, empêchant l'évaluation de la candidature) (1 point) ; "
                    "explication du rôle de la rétroaction, rendue possible par le canal "
                    "(le mail) : même arrivée avec un jour de délai, elle permet à Karim "
                    "d'être informé du problème et de renvoyer une candidature complète "
                    "(1 point)."
                ),
                "expected_points": [
                    "Identifie la coupure de connexion comme obstacle",
                    "Explique la conséquence concrète (message incomplet, sans CV)",
                    "Explique comment la rétroaction (réponse du recruteur) permet de résoudre le problème",
                ],
                "max_score": 3.0,
            },
            QuestionDifficulty.HARD,
        ),
    ]

    imported = 0
    for question_type, content, difficulty in questions:
        validate_content(question_type, 1, content)
        source_doc_id = content.get("source_document_version_id")
        create_question(
            db,
            module_id=module.id,
            uaa_id=uaa.id,
            question_type=question_type,
            content_json=content,
            generation_source=GenerationSource.IMPORTED,
            difficulty_declared=difficulty,
            source_document_version_id=source_doc_id,
        )
        imported += 1
    db.flush()
    return imported


# =============================================================================================
# FSE02 — Les médias et leurs financements (ticket #97)
# =============================================================================================


def import_fse02_to_bank(db: Session, module: Module, uaa: UAA) -> int:
    already_imported = (
        db.query(Question).filter_by(uaa_id=uaa.id, generation_source=GenerationSource.IMPORTED).count()
    )
    if already_imported:
        return 0

    paid = create_source_document(db, title=FSE02_PAID_TITLE, content_text=FSE02_PAID_TEXT, module_id=module.id)
    free_ad = create_source_document(db, title=FSE02_FREE_AD_TITLE, content_text=FSE02_FREE_AD_TEXT, module_id=module.id)
    public = create_source_document(db, title=FSE02_PUBLIC_TITLE, content_text=FSE02_PUBLIC_TEXT, module_id=module.id)
    db.flush()
    paid_id, free_ad_id, public_id = paid.current_version_id, free_ad.current_version_id, public.current_version_id

    questions: list[tuple[str, dict, QuestionDifficulty]] = [
        (
            "short_answer",
            {
                "prompt": "Par quel(s) moyen(s) L'Hebdo du Littoral se finance-t-il ?",
                "source_document_version_id": paid_id,
                "rubric": (
                    "Bonne réponse si elle cite la vente à l'unité (2,50 €) et/ou "
                    "l'abonnement (9 ou 14 €/mois), et précise l'absence de publicité."
                ),
                "max_length": 300,
            },
            QuestionDifficulty.EASY,
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "Quel élément du document du Flash Infos prouve qu'il se finance par "
                    "la publicité ?"
                ),
                "source_document_version_id": free_ad_id,
                "rubric": (
                    "Bonne réponse si elle cite les bannières publicitaires visibles sur "
                    "la page et/ou la phrase du texte confirmant que le site vit des "
                    "revenus publicitaires."
                ),
                "max_length": 300,
            },
            QuestionDifficulty.EASY,
        ),
        (
            "short_answer",
            {
                "prompt": "Pourquoi RCW ne diffuse-t-elle aucune publicité commerciale ?",
                "source_document_version_id": public_id,
                "rubric": (
                    "Bonne réponse si elle explique que RCW est financée par une dotation "
                    "publique, et n'a donc pas besoin de la publicité pour fonctionner."
                ),
                "max_length": 300,
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "multiple_choice",
            {
                "prompt": "Un média financé principalement par la publicité cherche avant tout à...",
                "options": [
                    {"option_id": "a", "label": "Maximiser son audience (le nombre de personnes qui le consultent)"},
                    {"option_id": "b", "label": "Minimiser ses coûts d'impression papier"},
                    {"option_id": "c", "label": "Obtenir une dotation publique plus importante"},
                    {"option_id": "d", "label": "Vendre le plus d'abonnements possible"},
                ],
                "correct_option_ids": ["a"],
                "explanation": (
                    "Plus l'audience d'un média financé par la publicité est grande, plus "
                    "les annonceurs sont prêts à payer pour y être visibles."
                ),
            },
            QuestionDifficulty.EASY,
        ),
        (
            "multiple_choice",
            {
                "prompt": "L'abonnement, comme mode de financement d'un média, consiste à...",
                "options": [
                    {"option_id": "a", "label": "Payer une somme régulière pour accéder à l'ensemble des contenus pendant une période"},
                    {"option_id": "b", "label": "Payer une seule fois pour un contenu précis et ponctuel"},
                    {"option_id": "c", "label": "Laisser des annonceurs financer le média en échange de publicité"},
                    {"option_id": "d", "label": "Recevoir une dotation financée par la collectivité"},
                ],
                "correct_option_ids": ["a"],
                "explanation": (
                    "L'abonnement se distingue de la vente à l'unité par son caractère "
                    "régulier et par l'accès à l'ensemble des contenus, pas un seul."
                ),
            },
            QuestionDifficulty.EASY,
        ),
        (
            "multiple_choice",
            {
                "prompt": "Quel terme désigne le nombre de personnes qui consultent un média ?",
                "options": [
                    {"option_id": "a", "label": "L'audience"},
                    {"option_id": "b", "label": "L'interactivité"},
                    {"option_id": "c", "label": "La dotation"},
                    {"option_id": "d", "label": "L'abonnement"},
                ],
                "correct_option_ids": ["a"],
                "explanation": "L'audience est un enjeu central pour un média financé par la publicité.",
            },
            QuestionDifficulty.EASY,
        ),
        (
            "classification",
            {
                "prompt": "Classe chacun de ces trois médias selon son mode de financement principal.",
                "categories": ["Vente/abonnement", "Publicité", "Fonds publics"],
                "elements": ["L'Hebdo du Littoral", "Le Flash Infos", "Radio Communauté Wallonie (RCW)"],
                "correct_categories": [0, 1, 2],
                "explanation": (
                    "L'Hebdo du Littoral vend ses numéros et propose des abonnements ; Le "
                    "Flash Infos est gratuit et financé par la publicité ; RCW est "
                    "financée par une dotation publique."
                ),
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "classification",
            {
                "prompt": (
                    "Classe chaque indice selon le mode de financement qu'il révèle."
                ),
                "categories": ["Indice d'un financement publicitaire", "Indice d'un financement par fonds publics"],
                "elements": [
                    "Présence de bannières publicitaires sur la page",
                    "Les revenus augmentent avec le nombre de vues d'un article",
                    "Une dotation publique votée chaque année",
                    "Aucune dépendance à l'audience pour obtenir des revenus",
                ],
                "correct_categories": [0, 0, 1, 1],
                "explanation": (
                    "Les deux premiers indices montrent une dépendance à l'audience "
                    "publicitaire ; les deux derniers montrent une indépendance "
                    "caractéristique d'un financement par fonds publics."
                ),
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "vocabulary",
            {
                "prompt": "Définis l'audience d'un média.",
                "direction": "term_to_definition",
                "rubric": (
                    "Bonne réponse si elle définit l'audience comme le nombre de "
                    "personnes qui consultent un média, en précisant son importance pour "
                    "un média financé par la publicité."
                ),
            },
            QuestionDifficulty.EASY,
        ),
        (
            "vocabulary",
            {
                "prompt": "Définis l'interactivité d'un média.",
                "direction": "term_to_definition",
                "rubric": (
                    "Bonne réponse si elle définit l'interactivité comme la possibilité, "
                    "pour le récepteur, de réagir au message (commenter, appeler, "
                    "partager), immédiatement ou en différé."
                ),
            },
            QuestionDifficulty.EASY,
        ),
        (
            "ordering",
            {
                "prompt": (
                    "Remets dans l'ordre les étapes de la méthode pour analyser le "
                    "financement d'un média à partir d'un document."
                ),
                "items": [
                    {"id": "e1", "label": "Identifier le type de média"},
                    {"id": "e2", "label": "Chercher un prix mentionné (abonnement, numéro à l'unité)"},
                    {"id": "e3", "label": "Chercher la présence de publicités"},
                    {"id": "e4", "label": "Chercher une mention de dotation ou de service public"},
                    {"id": "e5", "label": "Identifier un élément d'interactivité"},
                    {"id": "e6", "label": "Relier le financement identifié au comportement du média"},
                ],
                "correct_order": ["e1", "e2", "e3", "e4", "e5", "e6"],
                "explanation": (
                    "La méthode part de l'identification du média, cherche les indices "
                    "de chaque mode de financement, puis relie ce financement à son effet "
                    "sur le comportement du média."
                ),
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "document_analysis",
            {
                "prompt": (
                    "Analyse complète du Flash Infos : identifie son mode de "
                    "financement, puis explique en quoi ce financement peut influencer "
                    "le choix des sujets traités."
                ),
                "source_document_version_id": free_ad_id,
                "rubric": (
                    "3 points : identification correcte du financement publicitaire, "
                    "appuyée sur un élément précis du document (1 point) ; explication du "
                    "lien entre vues et revenus (1 point) ; explication de l'effet "
                    "possible sur le choix des sujets (privilégier les sujets qui "
                    "attirent des clics) (1 point)."
                ),
                "expected_points": [
                    "Identifie le financement publicitaire",
                    "Explique le lien entre nombre de vues et revenus",
                    "Explique l'effet possible sur le choix des sujets traités",
                ],
                "max_score": 3.0,
            },
            QuestionDifficulty.HARD,
        ),
        (
            "document_analysis",
            {
                "prompt": (
                    "Analyse RCW : identifie son mode de financement, puis explique "
                    "pourquoi elle peut traiter des sujets peu populaires sans perdre de "
                    "revenus."
                ),
                "source_document_version_id": public_id,
                "rubric": (
                    "3 points : identification correcte du financement par fonds publics "
                    "(1 point) ; explication de l'indépendance vis-à-vis de l'audience et "
                    "de la publicité (1 point) ; lien explicite avec la possibilité de "
                    "traiter des sujets peu populaires (1 point)."
                ),
                "expected_points": [
                    "Identifie le financement par fonds publics (dotation)",
                    "Explique l'indépendance vis-à-vis de l'audience/la publicité",
                    "Relie cette indépendance à la possibilité de traiter des sujets peu populaires",
                ],
                "max_score": 3.0,
            },
            QuestionDifficulty.HARD,
        ),
        (
            "long_answer",
            {
                "prompt": (
                    "Compare L'Hebdo du Littoral et Le Flash Infos : lequel des deux "
                    "dépend le plus de son audience pour obtenir des revenus ? Justifie "
                    "ta réponse."
                ),
                "source_document_version_id": paid_id,
                "rubric": (
                    "3 points : identifie que Le Flash Infos dépend le plus de son "
                    "audience (financement publicitaire lié aux vues) (1 point) ; "
                    "explique que L'Hebdo du Littoral dépend plutôt de la fidélité de ses "
                    "abonnés/acheteurs (1 point) ; justification appuyée sur un élément "
                    "précis de chaque document (1 point)."
                ),
                "expected_points": [
                    "Identifie Le Flash Infos comme le plus dépendant de l'audience",
                    "Explique la dépendance de L'Hebdo du Littoral à la fidélité de son public payant",
                    "Appuie la comparaison sur des éléments précis des deux documents",
                ],
                "max_score": 3.0,
            },
            QuestionDifficulty.HARD,
        ),
    ]

    imported = 0
    for question_type, content, difficulty in questions:
        validate_content(question_type, 1, content)
        source_doc_id = content.get("source_document_version_id")
        create_question(
            db,
            module_id=module.id,
            uaa_id=uaa.id,
            question_type=question_type,
            content_json=content,
            generation_source=GenerationSource.IMPORTED,
            difficulty_declared=difficulty,
            source_document_version_id=source_doc_id,
        )
        imported += 1
    db.flush()
    return imported


# =============================================================================================
# FSE03 — Identités, traces numériques et appartenance (ticket #97)
# =============================================================================================


def import_fse03_to_bank(db: Session, module: Module, uaa: UAA) -> int:
    already_imported = (
        db.query(Question).filter_by(uaa_id=uaa.id, generation_source=GenerationSource.IMPORTED).count()
    )
    if already_imported:
        return 0

    profile = create_source_document(db, title=FSE03_PROFILE_TITLE, content_text=FSE03_PROFILE_TEXT, module_id=module.id)
    hr_note = create_source_document(db, title=FSE03_HR_NOTE_TITLE, content_text=FSE03_HR_NOTE_TEXT, module_id=module.id)
    db.flush()
    profile_id, hr_note_id = profile.current_version_id, hr_note.current_version_id

    questions: list[tuple[str, dict, QuestionDifficulty]] = [
        (
            "short_answer",
            {
                "prompt": (
                    "La photo d'anniversaire sur laquelle Sophie est identifiée par une "
                    "amie est-elle une trace volontaire ou involontaire pour Sophie ? "
                    "Justifie."
                ),
                "source_document_version_id": profile_id,
                "rubric": (
                    "Bonne réponse si elle répond « involontaire » et justifie par le "
                    "fait que c'est l'amie, pas Sophie, qui a publié et identifié la "
                    "photo."
                ),
                "max_length": 300,
            },
            QuestionDifficulty.EASY,
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "Pourquoi le commentaire de Sophie sur le forum de jeux vidéo "
                    "est-il une trace volontaire, même s'il est ancien ?"
                ),
                "source_document_version_id": profile_id,
                "rubric": (
                    "Bonne réponse si elle explique que c'est bien Sophie elle-même qui "
                    "a écrit ce commentaire, sous son vrai nom — l'ancienneté ne change "
                    "rien au fait qu'elle en est l'autrice."
                ),
                "max_length": 350,
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "D'après la note du recruteur, quel élément de la présence en ligne "
                    "de Sophie renforce une impression positive ?"
                ),
                "source_document_version_id": hr_note_id,
                "rubric": (
                    "Bonne réponse si elle cite la recommandation professionnelle d'un "
                    "ancien collègue et/ou son appartenance au groupe professionnel de "
                    "gestionnaires de stock."
                ),
                "max_length": 300,
            },
            QuestionDifficulty.EASY,
        ),
        (
            "multiple_choice",
            {
                "prompt": "Une trace numérique involontaire désigne...",
                "options": [
                    {"option_id": "a", "label": "Un contenu publié par la personne elle-même, en connaissance de cause"},
                    {"option_id": "b", "label": "Un contenu publié par quelqu'un d'autre concernant la personne, ou redevenu visible sans qu'elle en maîtrise la visibilité"},
                    {"option_id": "c", "label": "Un contenu que la personne a supprimé elle-même"},
                    {"option_id": "d", "label": "Un contenu visible uniquement par les membres d'un groupe privé"},
                ],
                "correct_option_ids": ["b"],
                "explanation": (
                    "Une trace involontaire échappe au contrôle direct de la personne : "
                    "elle est publiée par un tiers, ou redevient visible sans son "
                    "intervention."
                ),
            },
            QuestionDifficulty.EASY,
        ),
        (
            "multiple_choice",
            {
                "prompt": "L'identité numérique désigne...",
                "options": [
                    {"option_id": "a", "label": "Une identité totalement différente de l'identité réelle de la personne"},
                    {"option_id": "b", "label": "L'identité personnelle et collective telle qu'elle s'exprime dans un contexte médiatique"},
                    {"option_id": "c", "label": "Le nom d'utilisateur choisi sur un réseau social"},
                    {"option_id": "d", "label": "L'ensemble des mots de passe d'une personne"},
                ],
                "correct_option_ids": ["b"],
                "explanation": (
                    "L'identité numérique n'est pas une identité à part : c'est "
                    "l'application de l'identité personnelle et collective au contexte "
                    "médiatique."
                ),
            },
            QuestionDifficulty.EASY,
        ),
        (
            "multiple_choice",
            {
                "prompt": "La réputation d'une personne, au sens de ce cours, désigne...",
                "options": [
                    {"option_id": "a", "label": "L'image qu'elle donne à voir à autrui, construite à partir de ses traces visibles"},
                    {"option_id": "b", "label": "Son identité réelle, telle qu'elle est en privé"},
                    {"option_id": "c", "label": "Le nombre de ses abonnés sur un réseau social"},
                    {"option_id": "d", "label": "Un document officiel résumant son parcours"},
                ],
                "correct_option_ids": ["a"],
                "explanation": (
                    "La réputation est une image perçue par autrui, qui peut différer de "
                    "l'identité réelle de la personne, surtout à cause de traces anciennes "
                    "ou sorties de leur contexte."
                ),
            },
            QuestionDifficulty.EASY,
        ),
        (
            "classification",
            {
                "prompt": "Classe chacune de ces traces de Sophie Lambert comme volontaire ou involontaire.",
                "source_document_version_id": profile_id,
                "categories": ["Trace volontaire", "Trace involontaire"],
                "elements": [
                    "Sa photo de profil professionnelle",
                    "La photo d'anniversaire publiée et identifiée par une amie",
                    "Son commentaire sur le forum de jeux vidéo",
                    "La recommandation écrite par un ancien collègue",
                ],
                "correct_categories": [0, 1, 0, 1],
                "explanation": (
                    "La photo de profil et le commentaire ont été publiés par Sophie "
                    "elle-même (volontaires) ; la photo d'anniversaire et la "
                    "recommandation ont été publiées par d'autres personnes "
                    "(involontaires pour Sophie)."
                ),
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "classification",
            {
                "prompt": (
                    "Classe chaque élément selon qu'il relève de l'identité réelle de "
                    "Sophie ou de l'image qu'elle donne à voir hors contexte."
                ),
                "source_document_version_id": hr_note_id,
                "categories": ["Identité réelle", "Image donnée à voir (hors contexte)"],
                "elements": [
                    "La recommandation d'un collègue qui la connaît professionnellement",
                    "Un commentaire isolé vieux de cinq ans, dans un contexte de loisir",
                    "Son parcours et ses compétences réelles au travail",
                ],
                "correct_categories": [0, 1, 0],
                "explanation": (
                    "La recommandation et le parcours professionnel reflètent l'identité "
                    "réelle de Sophie ; le commentaire ancien, sorti de son contexte, ne "
                    "donne qu'une image partielle et potentiellement trompeuse."
                ),
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "vocabulary",
            {
                "prompt": "Définis une trace numérique volontaire.",
                "direction": "term_to_definition",
                "rubric": (
                    "Bonne réponse si elle définit la trace volontaire comme un contenu "
                    "publié par la personne elle-même, en connaissance de cause."
                ),
            },
            QuestionDifficulty.EASY,
        ),
        (
            "vocabulary",
            {
                "prompt": "Définis la réputation, au sens de ce cours.",
                "direction": "term_to_definition",
                "rubric": (
                    "Bonne réponse si elle définit la réputation comme l'image qu'une "
                    "personne donne à voir à autrui, construite à partir de l'ensemble de "
                    "ses traces visibles."
                ),
            },
            QuestionDifficulty.EASY,
        ),
        (
            "ordering",
            {
                "prompt": (
                    "Remets dans l'ordre les étapes de la méthode pour analyser un "
                    "ensemble de traces numériques concernant une personne."
                ),
                "items": [
                    {"id": "e1", "label": "Déterminer, pour chaque trace, si elle est volontaire ou involontaire"},
                    {"id": "e2", "label": "Identifier les groupes d'appartenance visibles à travers ces traces"},
                    {"id": "e3", "label": "Distinguer l'identité réelle de l'image donnée à voir"},
                    {"id": "e4", "label": "Expliquer la conséquence concrète d'une trace précise sur une situation réelle"},
                ],
                "correct_order": ["e1", "e2", "e3", "e4"],
                "explanation": (
                    "La méthode classe d'abord chaque trace, identifie les groupes "
                    "d'appartenance, distingue identité réelle et image, puis relie à une "
                    "conséquence concrète si la situation l'exige."
                ),
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "document_analysis",
            {
                "prompt": (
                    "Analyse l'ensemble de la présence en ligne de Sophie Lambert : "
                    "classe chaque trace (volontaire/involontaire) et identifie ses "
                    "groupes d'appartenance visibles."
                ),
                "source_document_version_id": profile_id,
                "rubric": (
                    "4 points : les quatre traces correctement classées volontaire/"
                    "involontaire, chacune justifiée (2 points) ; les deux groupes "
                    "d'appartenance identifiés (randonneurs, gestionnaires de stock) "
                    "(1 point) ; aucune confusion entre apparaître sur une trace et "
                    "l'avoir publiée soi-même (1 point)."
                ),
                "expected_points": [
                    "Classe les 4 traces en volontaire/involontaire, chacune justifiée",
                    "Identifie les deux groupes d'appartenance visibles",
                    "Ne confond jamais apparaître sur une trace et l'avoir publiée soi-même",
                ],
                "max_score": 4.0,
            },
            QuestionDifficulty.HARD,
        ),
        (
            "document_analysis",
            {
                "prompt": (
                    "Analyse la note du recruteur : explique comment le commentaire "
                    "ancien influence son impression, puis explique pourquoi le "
                    "recruteur distingue quand même ce commentaire de l'identité "
                    "professionnelle réelle de Sophie."
                ),
                "source_document_version_id": hr_note_id,
                "rubric": (
                    "3 points : explique l'effet négatif du commentaire ancien sur la "
                    "première impression (1 point) ; relève que le recruteur reconnaît "
                    "explicitement que ce commentaire ne reflète pas les compétences "
                    "professionnelles de Sophie (1 point) ; relie cette distinction à la "
                    "différence entre identité réelle et image donnée à voir hors "
                    "contexte (1 point)."
                ),
                "expected_points": [
                    "Explique l'effet négatif du commentaire ancien sur l'impression",
                    "Relève que le recruteur distingue ce commentaire des compétences réelles",
                    "Relie cette distinction à identité réelle vs image hors contexte",
                ],
                "max_score": 3.0,
            },
            QuestionDifficulty.HARD,
        ),
        (
            "long_answer",
            {
                "prompt": (
                    "Explique les conséquences concrètes que le commentaire ancien du "
                    "forum pourrait avoir sur la candidature de Sophie, et ce qui permet "
                    "malgré tout de nuancer cette impression."
                ),
                "source_document_version_id": hr_note_id,
                "rubric": (
                    "3 points : explique la conséquence possible (impression négative "
                    "chez un recruteur qui découvre ce commentaire hors contexte) "
                    "(1 point) ; identifie les éléments qui nuancent cette impression "
                    "(ancienneté, contexte de loisir sans lien avec le poste, "
                    "recommandation professionnelle positive) (1 point) ; conclusion "
                    "cohérente sans minimiser ni exagérer l'impact (1 point)."
                ),
                "expected_points": [
                    "Explique la conséquence négative possible sur la candidature",
                    "Identifie les éléments qui nuancent cette impression",
                    "Conclut sans minimiser ni exagérer l'impact réel",
                ],
                "max_score": 3.0,
            },
            QuestionDifficulty.HARD,
        ),
    ]

    imported = 0
    for question_type, content, difficulty in questions:
        validate_content(question_type, 1, content)
        source_doc_id = content.get("source_document_version_id")
        create_question(
            db,
            module_id=module.id,
            uaa_id=uaa.id,
            question_type=question_type,
            content_json=content,
            generation_source=GenerationSource.IMPORTED,
            difficulty_declared=difficulty,
            source_document_version_id=source_doc_id,
        )
        imported += 1
    db.flush()
    return imported


# =============================================================================================
# FSE04 — Normes, valeurs et influence sociale (ticket #97)
# =============================================================================================


def import_fse04_to_bank(db: Session, module: Module, uaa: UAA) -> int:
    already_imported = (
        db.query(Question).filter_by(uaa_id=uaa.id, generation_source=GenerationSource.IMPORTED).count()
    )
    if already_imported:
        return 0

    group = create_source_document(db, title=FSE04_GROUP_TITLE, content_text=FSE04_GROUP_TEXT, module_id=module.id)
    testimony = create_source_document(db, title=FSE04_TESTIMONY_TITLE, content_text=FSE04_TESTIMONY_TEXT, module_id=module.id)
    db.flush()
    group_id, testimony_id = group.current_version_id, testimony.current_version_id

    questions: list[tuple[str, dict, QuestionDifficulty]] = [
        (
            "short_answer",
            {
                "prompt": (
                    "Quelle valeur semble primer dans le groupe « Fous rires du "
                    "quotidien », d'après la publication ?"
                ),
                "source_document_version_id": group_id,
                "rubric": (
                    "Bonne réponse si elle identifie que l'humour/le divertissement "
                    "prime sur le respect de la personne filmée."
                ),
                "max_length": 300,
            },
            QuestionDifficulty.EASY,
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "Quel commentaire, parmi ceux affichés sous la publication, "
                    "s'écarte de la norme dominante du groupe ? Cite-le."
                ),
                "source_document_version_id": group_id,
                "rubric": (
                    "Bonne réponse si elle cite le commentaire du membre D (« c'est "
                    "méchant de se moquer comme ça, elle n'a rien demandé »)."
                ),
                "max_length": 300,
            },
            QuestionDifficulty.EASY,
        ),
        (
            "short_answer",
            {
                "prompt": "D'après son témoignage, Karim a-t-il ressenti une pression du groupe ? Justifie.",
                "source_document_version_id": testimony_id,
                "rubric": (
                    "Bonne réponse si elle répond « oui » et cite le passage où Karim "
                    "décrit un réflexe de sourire parce que tout le monde autour de lui "
                    "trouvait ça drôle."
                ),
                "max_length": 350,
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "multiple_choice",
            {
                "prompt": "Une norme désigne...",
                "options": [
                    {"option_id": "a", "label": "Une règle de comportement concrète, attendue dans un groupe ou une société"},
                    {"option_id": "b", "label": "Ce qu'un groupe considère comme important ou souhaitable, de façon générale"},
                    {"option_id": "c", "label": "Une action réellement observée chez une personne"},
                    {"option_id": "d", "label": "Un besoin fondamental commun à tous les êtres humains"},
                ],
                "correct_option_ids": ["a"],
                "explanation": (
                    "La norme est la règle concrète de comportement, souvent issue d'une "
                    "valeur plus générale."
                ),
            },
            QuestionDifficulty.EASY,
        ),
        (
            "multiple_choice",
            {
                "prompt": "Une valeur désigne...",
                "options": [
                    {"option_id": "a", "label": "Ce qu'un groupe ou une société considère comme important ou souhaitable"},
                    {"option_id": "b", "label": "Une règle concrète de comportement à respecter"},
                    {"option_id": "c", "label": "Une action réellement observée chez une personne"},
                    {"option_id": "d", "label": "Un groupe auquel une personne appartient"},
                ],
                "correct_option_ids": ["a"],
                "explanation": "La valeur est l'idée générale ; la norme en est la règle concrète qui en découle.",
            },
            QuestionDifficulty.EASY,
        ),
        (
            "multiple_choice",
            {
                "prompt": "L'influence sociale, telle que vue dans ce cours, explique...",
                "options": [
                    {"option_id": "a", "label": "Une tendance fréquente dans un groupe, jamais une obligation individuelle absolue"},
                    {"option_id": "b", "label": "Une obligation à laquelle aucun membre d'un groupe ne peut échapper"},
                    {"option_id": "c", "label": "Un trait de caractère individuel sans lien avec le groupe"},
                    {"option_id": "d", "label": "Une loi qui s'impose à tous les membres d'une société"},
                ],
                "correct_option_ids": ["a"],
                "explanation": (
                    "L'influence sociale explique pourquoi un comportement est fréquent "
                    "dans un groupe, sans jamais effacer la responsabilité individuelle "
                    "de chaque membre."
                ),
            },
            QuestionDifficulty.EASY,
        ),
        (
            "classification",
            {
                "prompt": (
                    "Classe chacun de ces commentaires selon qu'il suit la norme "
                    "dominante du groupe (moquerie/partage) ou s'en écarte."
                ),
                "source_document_version_id": group_id,
                "categories": ["Suit la norme dominante du groupe", "S'écarte de la norme dominante du groupe"],
                "elements": [
                    "Membre A : « Hahaha, il a trop la honte ! »",
                    "Membre C : « Je l'ai aussi envoyée à mes potes, trop drôle »",
                    "Membre E : « Allez, c'est juste pour rire, personne n'est blessé »",
                    "Membre D : « Franchement, c'est méchant de se moquer comme ça »",
                ],
                "correct_categories": [0, 0, 0, 1],
                "explanation": (
                    "Les membres A, C et E suivent ou justifient la moquerie dominante "
                    "dans le groupe ; seul le membre D exprime un désaccord explicite."
                ),
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "classification",
            {
                "prompt": "Classe chaque élément selon qu'il s'agit d'une valeur, d'une norme ou d'un comportement.",
                "source_document_version_id": group_id,
                "categories": ["Valeur", "Norme", "Comportement"],
                "elements": [
                    "L'humour prime sur le respect d'autrui, dans ce groupe",
                    "Partager ce type de vidéo est valorisé dans ce groupe",
                    "Le membre C partage la vidéo à ses propres amis",
                ],
                "correct_categories": [0, 1, 2],
                "explanation": (
                    "La primauté de l'humour est la valeur implicite ; le fait que "
                    "partager ce contenu soit valorisé est la norme qui en découle ; le "
                    "partage effectif par le membre C est le comportement observé."
                ),
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "vocabulary",
            {
                "prompt": "Définis l'influence sociale.",
                "direction": "term_to_definition",
                "rubric": (
                    "Bonne réponse si elle définit l'influence sociale comme la façon "
                    "dont les normes et comportements d'un groupe orientent le "
                    "comportement d'une personne, même sans obligation formelle."
                ),
            },
            QuestionDifficulty.EASY,
        ),
        (
            "vocabulary",
            {
                "prompt": "Définis la socialisation.",
                "direction": "term_to_definition",
                "rubric": (
                    "Bonne réponse si elle définit la socialisation comme le processus "
                    "progressif par lequel une personne intègre les normes et valeurs "
                    "d'un ou plusieurs groupes."
                ),
            },
            QuestionDifficulty.EASY,
        ),
        (
            "ordering",
            {
                "prompt": "Remets dans l'ordre les étapes de la méthode pour analyser une situation de groupe.",
                "items": [
                    {"id": "e1", "label": "Identifier la valeur implicite en jeu dans la situation"},
                    {"id": "e2", "label": "Identifier la norme concrète que le groupe semble suivre"},
                    {"id": "e3", "label": "Observer les comportements réellement décrits dans le document"},
                    {"id": "e4", "label": "Expliquer en quoi l'influence sociale explique la fréquence du comportement"},
                    {"id": "e5", "label": "Rappeler la limite : la responsabilité individuelle reste entière"},
                ],
                "correct_order": ["e1", "e2", "e3", "e4", "e5"],
                "explanation": (
                    "La méthode part de la valeur, identifie la norme qui en découle, "
                    "observe les comportements réels, explique l'influence sociale, puis "
                    "rappelle toujours sa limite."
                ),
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "document_analysis",
            {
                "prompt": (
                    "Analyse la publication du groupe « Fous rires du quotidien » : "
                    "identifie la valeur implicite, la norme qui en découle, et donne un "
                    "exemple de comportement qui suit cette norme ET un exemple qui s'en "
                    "écarte."
                ),
                "source_document_version_id": group_id,
                "rubric": (
                    "4 points : valeur implicite correctement identifiée (1 point) ; "
                    "norme du groupe correctement formulée (1 point) ; exemple de "
                    "comportement qui suit la norme, appuyé sur un commentaire précis "
                    "(1 point) ; exemple de comportement qui s'en écarte, appuyé sur le "
                    "commentaire du membre D (1 point)."
                ),
                "expected_points": [
                    "Identifie la valeur implicite (humour prime sur le respect)",
                    "Formule la norme du groupe (partage/moquerie valorisés)",
                    "Donne un exemple de comportement qui suit la norme",
                    "Donne un exemple de comportement qui s'en écarte (membre D)",
                ],
                "max_score": 4.0,
            },
            QuestionDifficulty.HARD,
        ),
        (
            "document_analysis",
            {
                "prompt": (
                    "Analyse le témoignage de Karim : explique en quoi il illustre à la "
                    "fois l'existence de l'influence sociale ET ses limites."
                ),
                "source_document_version_id": testimony_id,
                "rubric": (
                    "3 points : identifie que Karim décrit bien ressentir une pression "
                    "du groupe (le réflexe de sourire partagé) (1 point) ; explique que "
                    "cette pression ne l'a pas empêché de choisir de ne pas participer au "
                    "partage moqueur (1 point) ; relie explicitement ce choix à la limite "
                    "de l'explication par l'influence sociale (la responsabilité "
                    "individuelle reste entière) (1 point)."
                ),
                "expected_points": [
                    "Identifie la pression du groupe ressentie par Karim",
                    "Explique que Karim a choisi de ne pas suivre cette pression",
                    "Relie ce choix à la limite de l'explication par l'influence sociale",
                ],
                "max_score": 3.0,
            },
            QuestionDifficulty.HARD,
        ),
        (
            "long_answer",
            {
                "prompt": (
                    "Explique pourquoi on ne peut pas dire que « le groupe a obligé "
                    "tout le monde à se moquer », en t'appuyant sur les deux documents."
                ),
                "source_document_version_id": group_id,
                "rubric": (
                    "3 points : identifie le membre D comme preuve qu'un comportement "
                    "différent est possible au sein même du groupe (1 point) ; s'appuie "
                    "sur le témoignage de Karim pour montrer qu'un membre peut ressentir "
                    "la pression du groupe sans pour autant y céder (1 point) ; "
                    "conclusion explicite reliant ces deux éléments à la responsabilité "
                    "individuelle (1 point)."
                ),
                "expected_points": [
                    "S'appuie sur le commentaire du membre D",
                    "S'appuie sur le témoignage de Karim",
                    "Conclut explicitement sur la responsabilité individuelle",
                ],
                "max_score": 3.0,
            },
            QuestionDifficulty.HARD,
        ),
    ]

    imported = 0
    for question_type, content, difficulty in questions:
        validate_content(question_type, 1, content)
        source_doc_id = content.get("source_document_version_id")
        create_question(
            db,
            module_id=module.id,
            uaa_id=uaa.id,
            question_type=question_type,
            content_json=content,
            generation_source=GenerationSource.IMPORTED,
            difficulty_declared=difficulty,
            source_document_version_id=source_doc_id,
        )
        imported += 1
    db.flush()
    return imported


def import_fse05_to_bank(db: Session, module: Module, uaa: UAA) -> int:
    already_imported = (
        db.query(Question).filter_by(uaa_id=uaa.id, generation_source=GenerationSource.IMPORTED).count()
    )
    if already_imported:
        return 0

    situations = create_source_document(
        db, title=FSE05_SITUATIONS_TITLE, content_text=FSE05_SITUATIONS_TEXT, module_id=module.id
    )
    db.flush()
    situations_id = situations.current_version_id

    questions: list[tuple[str, dict, QuestionDifficulty]] = [
        (
            "multiple_choice",
            {
                "prompt": "La diffusion d'une image désigne...",
                "options": [
                    {"option_id": "a", "label": "Le fait de publier, partager ou transmettre cette image à d'autres personnes"},
                    {"option_id": "b", "label": "Le fait de photographier ou de filmer une personne"},
                    {"option_id": "c", "label": "Le fait de demander l'accord d'une personne avant de la photographier"},
                    {"option_id": "d", "label": "Le fait de supprimer une image après l'avoir prise"},
                ],
                "correct_option_ids": ["a"],
                "explanation": "La diffusion est l'acte de publier ou transmettre une image, distinct de la prise de vue.",
            },
            QuestionDifficulty.EASY,
        ),
        (
            "multiple_choice",
            {
                "prompt": "Une personne accessoire sur une image est...",
                "options": [
                    {"option_id": "a", "label": "Une personne présente par hasard, non individualisée ni mise en évidence"},
                    {"option_id": "b", "label": "Une personne mise en avant et parfaitement reconnaissable"},
                    {"option_id": "c", "label": "Une personne qui a donné son accord explicite pour être photographiée"},
                    {"option_id": "d", "label": "Une personne qui a pris la photo elle-même"},
                ],
                "correct_option_ids": ["a"],
                "explanation": "La personne accessoire se trouve par hasard sur l'image, sans y être individualisée.",
            },
            QuestionDifficulty.EASY,
        ),
        (
            "vocabulary",
            {
                "prompt": "Définis le droit à l'image.",
                "direction": "term_to_definition",
                "rubric": (
                    "Bonne réponse si elle définit le droit à l'image comme le droit de décider "
                    "si l'on peut être photographié/filmé, et si cette image peut être utilisée "
                    "ou diffusée."
                ),
            },
            QuestionDifficulty.EASY,
        ),
        (
            "vocabulary",
            {
                "prompt": "Définis la finalité, en matière de données personnelles.",
                "direction": "term_to_definition",
                "rubric": (
                    "Bonne réponse si elle définit la finalité comme le but précis pour lequel "
                    "une donnée personnelle est collectée et utilisée."
                ),
            },
            QuestionDifficulty.EASY,
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "Les passants présents sur la photo du monument touristique (situation 1) "
                    "sont-ils sujet principal ou personne accessoire ? Justifie en une phrase."
                ),
                "source_document_version_id": situations_id,
                "rubric": (
                    "Bonne réponse si elle répond « personne accessoire » et justifie par le "
                    "fait qu'ils sont présents par hasard, en arrière-plan, non individualisés."
                ),
                "max_length": 300,
            },
            QuestionDifficulty.EASY,
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "Quelle information manque dans le formulaire du site décrit en situation 6 "
                    "concernant les données collectées ?"
                ),
                "source_document_version_id": situations_id,
                "rubric": (
                    "Bonne réponse si elle identifie l'absence de finalité précisée (on ne sait "
                    "pas à quel usage précis les données serviront au-delà du concours)."
                ),
                "max_length": 300,
            },
            QuestionDifficulty.EASY,
        ),
        (
            "multiple_choice",
            {
                "prompt": "Un accord donné pour être photographié...",
                "options": [
                    {"option_id": "a", "label": "N'autorise pas automatiquement la diffusion de cette photo"},
                    {"option_id": "b", "label": "Autorise automatiquement toute diffusion future de cette photo"},
                    {"option_id": "c", "label": "N'a de valeur que si la photo est prise dans un lieu public"},
                    {"option_id": "d", "label": "Rend inutile tout accord ultérieur, quel que soit l'usage"},
                ],
                "correct_option_ids": ["a"],
                "explanation": "Prise de vue et diffusion sont deux actes distincts, chacun pouvant nécessiter un accord propre.",
            },
            QuestionDifficulty.EASY,
        ),
        (
            "classification",
            {
                "prompt": "Classe la personne concernée dans chaque situation selon qu'elle est sujet principal ou personne accessoire.",
                "source_document_version_id": situations_id,
                "categories": ["Sujet principal", "Personne accessoire"],
                "elements": [
                    "Les passants en arrière-plan de la photo du monument (situation 1)",
                    "Nabil, photographié en train de souffler ses bougies (situation 2)",
                    "Les participants filmés en foule pendant la manifestation (situation 3)",
                    "L'enfant de 9 ans photographié en vacances (situation 5)",
                ],
                "correct_categories": [1, 0, 1, 0],
                "explanation": (
                    "Nabil et l'enfant sont mis en avant et identifiables (sujet principal) ; "
                    "les passants et la foule de la manifestation sont présents par hasard, non "
                    "individualisés (personne accessoire)."
                ),
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "classification",
            {
                "prompt": "Classe chaque action décrite selon qu'il s'agit d'une prise de vue ou d'une diffusion.",
                "source_document_version_id": situations_id,
                "categories": ["Prise de vue", "Diffusion"],
                "elements": [
                    "Thomas photographie Nabil en train de souffler ses bougies",
                    "Thomas publie cette photo sur son compte public",
                    "Un reporter filme la foule pendant la manifestation",
                    "Chloé publie la photo reçue dans un groupe public de 500 membres",
                ],
                "correct_categories": [0, 1, 0, 1],
                "explanation": "Photographier/filmer est une prise de vue ; publier/partager est une diffusion, acte distinct.",
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "Le fait que Chloé ait reçu la photo dans un cadre personnel restreint "
                    "(situation 4) l'autorise-t-il à la publier dans un groupe de 500 membres ? "
                    "Justifie."
                ),
                "source_document_version_id": situations_id,
                "rubric": (
                    "Bonne réponse si elle répond « non » et explique que la diffusion dans un "
                    "groupe de 500 membres est un acte distinct et plus large, qui nécessiterait "
                    "en principe un accord spécifique des personnes présentes sur la photo."
                ),
                "max_length": 350,
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "ordering",
            {
                "prompt": "Remets dans l'ordre les étapes de la méthode face à une situation impliquant une image ou une donnée personnelle.",
                "items": [
                    {"id": "e1", "label": "Identifier s'il s'agit d'une question de prise de vue, de diffusion, ou des deux"},
                    {"id": "e2", "label": "Déterminer si la personne concernée est sujet principal ou personne accessoire"},
                    {"id": "e3", "label": "Vérifier si le contexte est une activité strictement personnelle/domestique ou un public plus large"},
                    {"id": "e4", "label": "Vérifier, pour une donnée personnelle, si une finalité précise est annoncée"},
                    {"id": "e5", "label": "Conclure sur la nécessité ou non d'un consentement, sans invoquer le seul lieu public"},
                ],
                "correct_order": ["e1", "e2", "e3", "e4", "e5"],
                "explanation": "La méthode distingue d'abord prise de vue/diffusion, puis le statut de la personne, le contexte, la finalité, avant de conclure.",
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "document_analysis",
            {
                "prompt": (
                    "Analyse la situation 2 (Thomas et Nabil) : la prise de vue pose-t-elle "
                    "problème ? La diffusion pose-t-elle problème ? Justifie séparément chaque "
                    "réponse."
                ),
                "source_document_version_id": situations_id,
                "rubric": (
                    "3 points : identifie que la prise de vue, dans un cadre amical, ne pose pas "
                    "nécessairement problème en elle-même (1 point) ; identifie que Nabil est "
                    "sujet principal, reconnaissable et mis en avant (1 point) ; conclut que la "
                    "diffusion sur un compte public nécessiterait en principe un accord "
                    "spécifique de Nabil, distinct de la prise de vue (1 point)."
                ),
                "expected_points": [
                    "La prise de vue, en soi, dans un cadre amical, ne pose pas nécessairement problème",
                    "Nabil est sujet principal, reconnaissable et mis en avant",
                    "La diffusion sur un compte public nécessiterait un accord spécifique, distinct",
                ],
                "max_score": 3.0,
            },
            QuestionDifficulty.HARD,
        ),
        (
            "document_analysis",
            {
                "prompt": (
                    "Compare la situation 1 (monument touristique) et la situation 5 (enfant en "
                    "vacances) : laquelle montre un sujet principal, et pourquoi cela change la "
                    "réponse quant au consentement nécessaire ?"
                ),
                "source_document_version_id": situations_id,
                "rubric": (
                    "3 points : identifie que l'enfant de la situation 5 est sujet principal, "
                    "identifiable et mis en avant (1 point) ; identifie que les passants de la "
                    "situation 1 sont accessoires, non individualisés (1 point) ; conclut que "
                    "c'est ce critère (principal/accessoire), pas l'âge ni le lieu, qui "
                    "détermine la réponse, et mentionne la protection renforcée des mineurs "
                    "(1 point)."
                ),
                "expected_points": [
                    "L'enfant de la situation 5 est sujet principal, identifiable et mis en avant",
                    "Les passants de la situation 1 sont personnes accessoires, non individualisés",
                    "Le critère pertinent est principal/accessoire, avec une protection renforcée pour les mineurs",
                ],
                "max_score": 3.0,
            },
            QuestionDifficulty.HARD,
        ),
        (
            "long_answer",
            {
                "prompt": (
                    "Explique pourquoi on ne peut pas dire qu'« un lieu public autorise toute "
                    "diffusion d'image », en t'appuyant sur au moins deux situations différentes "
                    "du document."
                ),
                "source_document_version_id": situations_id,
                "rubric": (
                    "3 points : s'appuie sur la situation 1 ou 3 (personnes accessoires en lieu "
                    "public, diffusion sans accord possible) (1 point) ; s'appuie sur une "
                    "situation où une personne est mise en avant et identifiable (sujet "
                    "principal), même potentiellement en public (1 point) ; conclusion "
                    "explicite que le critère déterminant est le statut principal/accessoire, "
                    "jamais le seul lieu (1 point)."
                ),
                "expected_points": [
                    "S'appuie sur une situation où la personne est accessoire en lieu public",
                    "S'appuie sur une situation où la personne est sujet principal",
                    "Conclut que le critère déterminant est principal/accessoire, pas le lieu",
                ],
                "max_score": 3.0,
            },
            QuestionDifficulty.HARD,
        ),
    ]

    imported = 0
    for question_type, content, difficulty in questions:
        validate_content(question_type, 1, content)
        source_doc_id = content.get("source_document_version_id")
        create_question(
            db,
            module_id=module.id,
            uaa_id=uaa.id,
            question_type=question_type,
            content_json=content,
            generation_source=GenerationSource.IMPORTED,
            difficulty_declared=difficulty,
            source_document_version_id=source_doc_id,
        )
        imported += 1
    db.flush()
    return imported


def import_fse06_to_bank(db: Session, module: Module, uaa: UAA) -> int:
    already_imported = (
        db.query(Question).filter_by(uaa_id=uaa.id, generation_source=GenerationSource.IMPORTED).count()
    )
    if already_imported:
        return 0

    scenarios = create_source_document(
        db, title=FSE06_SCENARIOS_TITLE, content_text=FSE06_SCENARIOS_TEXT, module_id=module.id
    )
    db.flush()
    scenarios_id = scenarios.current_version_id

    questions: list[tuple[str, dict, QuestionDifficulty]] = [
        (
            "multiple_choice",
            {
                "prompt": "Le cyberharcèlement se caractérise surtout par...",
                "options": [
                    {"option_id": "a", "label": "Des propos ou actes hostiles répétés dans le temps, visant une même personne"},
                    {"option_id": "b", "label": "Un unique commentaire négatif, même isolé"},
                    {"option_id": "c", "label": "Toute critique sévère d'un produit ou d'un service"},
                    {"option_id": "d", "label": "Le simple fait de ne pas répondre à un message"},
                ],
                "correct_option_ids": ["a"],
                "explanation": "La répétition dans le temps, ciblant une même personne, est l'indice central du cyberharcèlement.",
            },
            QuestionDifficulty.EASY,
        ),
        (
            "multiple_choice",
            {
                "prompt": "Une accusation non étayée (calomnie) se distingue d'une injure parce qu'elle...",
                "options": [
                    {"option_id": "a", "label": "Affirme un fait précis et négatif sur une personne, sans preuve"},
                    {"option_id": "b", "label": "Se limite à une insulte sans affirmer de fait précis"},
                    {"option_id": "c", "label": "Ne vise jamais une personne en particulier"},
                    {"option_id": "d", "label": "Est toujours accompagnée d'une menace"},
                ],
                "correct_option_ids": ["a"],
                "explanation": "L'accusation non étayée affirme un fait précis et négatif, sans preuve ; l'injure n'affirme aucun fait précis.",
            },
            QuestionDifficulty.EASY,
        ),
        (
            "vocabulary",
            {
                "prompt": "Définis l'usurpation d'identité.",
                "direction": "term_to_definition",
                "rubric": (
                    "Bonne réponse si elle définit l'usurpation d'identité comme le fait de se "
                    "faire passer pour quelqu'un d'autre en ligne (faux compte, utilisation de "
                    "sa photo ou de son nom) sans son accord."
                ),
            },
            QuestionDifficulty.EASY,
        ),
        (
            "vocabulary",
            {
                "prompt": "Définis l'intrusion informatique.",
                "direction": "term_to_definition",
                "rubric": (
                    "Bonne réponse si elle définit l'intrusion informatique comme un accès non "
                    "autorisé à un compte, un appareil ou des données appartenant à autrui."
                ),
            },
            QuestionDifficulty.EASY,
        ),
        (
            "short_answer",
            {
                "prompt": "Quel indice du scénario 1 (Sarah) permet de conclure au cyberharcèlement plutôt qu'à un simple désaccord ?",
                "source_document_version_id": scenarios_id,
                "rubric": (
                    "Bonne réponse si elle identifie la répétition dans le temps (« depuis "
                    "plusieurs semaines », « chaque jour ») et le fait que Sarah ait demandé "
                    "d'arrêter sans effet."
                ),
                "max_length": 300,
            },
            QuestionDifficulty.EASY,
        ),
        (
            "short_answer",
            {
                "prompt": "Quelle information manque pour que la collecte des adresses e-mail du scénario 9 respecte un traitement de données valable ?",
                "source_document_version_id": scenarios_id,
                "rubric": (
                    "Bonne réponse si elle identifie l'absence d'information des participants "
                    "sur l'usage (revente à des fins publicitaires) fait de leurs données."
                ),
                "max_length": 300,
            },
            QuestionDifficulty.EASY,
        ),
        (
            "multiple_choice",
            {
                "prompt": "Le scénario 10 (critique du restaurant) correspond à...",
                "options": [
                    {"option_id": "a", "label": "Une opinion couverte par la liberté d'expression, sans insulte ni accusation non prouvée"},
                    {"option_id": "b", "label": "Un cyberharcèlement, car la critique est sévère"},
                    {"option_id": "c", "label": "Une accusation non étayée, car elle nuit à la réputation du restaurant"},
                    {"option_id": "d", "label": "Une diffusion malveillante, car elle est publiée en ligne"},
                ],
                "correct_option_ids": ["a"],
                "explanation": "Sans insulte, accusation non prouvée, menace ou répétition ciblée, une critique sévère reste une opinion.",
            },
            QuestionDifficulty.EASY,
        ),
        (
            "classification",
            {
                "prompt": "Classe chaque scénario selon le comportement principal qu'il illustre.",
                "source_document_version_id": scenarios_id,
                "categories": ["Injure", "Accusation non étayée (calomnie)", "Menace", "Racisme/discrimination"],
                "elements": [
                    "Scénario 2 (« Tu es vraiment un idiot fini »)",
                    "Scénario 3 (commerçant accusé de voler sans preuve)",
                    "Scénario 4 (« tu vas le regretter »)",
                    "Scénario 5 (candidats écartés en raison de leur origine)",
                ],
                "correct_categories": [0, 1, 2, 3],
                "explanation": "Chaque scénario correspond à un indice précis : insulte sans fait, fait non prouvé, annonce d'un mal, traitement défavorable selon une origine.",
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "classification",
            {
                "prompt": "Classe chaque scénario selon le comportement principal qu'il illustre.",
                "source_document_version_id": scenarios_id,
                "categories": ["Usurpation d'identité", "Intrusion informatique", "Diffusion malveillante"],
                "elements": [
                    "Scénario 6 (faux profil au nom d'un camarade)",
                    "Scénario 7 (mot de passe deviné pour lire des messages privés)",
                    "Scénario 8 (photo intime partagée pour humilier)",
                ],
                "correct_categories": [0, 1, 2],
                "explanation": "Faux compte = usurpation d'identité ; accès non autorisé = intrusion informatique ; partage dans le but de nuire = diffusion malveillante.",
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "short_answer",
            {
                "prompt": "Explique pourquoi le scénario 8 est une diffusion malveillante et pas seulement un partage ordinaire.",
                "source_document_version_id": scenarios_id,
                "rubric": (
                    "Bonne réponse si elle identifie que la photo a été reçue en privé et "
                    "partagée dans plusieurs groupes avec l'intention explicite d'humilier la "
                    "personne concernée."
                ),
                "max_length": 350,
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "ordering",
            {
                "prompt": "Remets dans l'ordre les étapes de la méthode face à un scénario en ligne.",
                "items": [
                    {"id": "e1", "label": "Repérer les indices concrets décrits dans le scénario"},
                    {"id": "e2", "label": "Associer ces indices à une ou plusieurs catégories vues en cours"},
                    {"id": "e3", "label": "Vérifier qu'il ne s'agit pas d'une simple critique ou opinion"},
                    {"id": "e4", "label": "Expliquer la réponse en citant les indices précis du scénario"},
                ],
                "correct_order": ["e1", "e2", "e3", "e4"],
                "explanation": "La méthode part des indices concrets, les associe à une catégorie, écarte la simple opinion, puis justifie par les indices.",
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "document_analysis",
            {
                "prompt": "Analyse le scénario 1 (Sarah) : quels indices précis permettent de l'associer au cyberharcèlement plutôt qu'à un simple conflit ponctuel ?",
                "source_document_version_id": scenarios_id,
                "rubric": (
                    "3 points : identifie la répétition dans le temps (1 point) ; identifie que "
                    "Sarah a demandé que cela cesse, sans effet (1 point) ; conclut explicitement "
                    "que c'est la combinaison répétition + demande ignorée qui distingue le "
                    "cyberharcèlement d'un conflit ponctuel (1 point)."
                ),
                "expected_points": [
                    "Identifie la répétition dans le temps",
                    "Identifie que Sarah a demandé que cela cesse, sans effet",
                    "Conclut sur la combinaison de ces deux indices",
                ],
                "max_score": 3.0,
            },
            QuestionDifficulty.HARD,
        ),
        (
            "document_analysis",
            {
                "prompt": "Compare le scénario 3 (commerçant accusé) et le scénario 10 (critique du restaurant) : pourquoi l'un pose-t-il problème et pas l'autre ?",
                "source_document_version_id": scenarios_id,
                "rubric": (
                    "3 points : identifie que le scénario 3 affirme un fait précis et négatif "
                    "sans preuve (1 point) ; identifie que le scénario 10 porte sur une "
                    "expérience vécue par l'auteur, sans fait extérieur invérifiable ni insulte "
                    "(1 point) ; conclut que le critère pertinent est la présence d'un fait "
                    "précis non prouvé, pas la sévérité du ton (1 point)."
                ),
                "expected_points": [
                    "Le scénario 3 affirme un fait précis et négatif sans preuve",
                    "Le scénario 10 porte sur une expérience vécue, sans fait invérifiable ni insulte",
                    "Conclut que le critère est la présence d'un fait non prouvé, pas le ton",
                ],
                "max_score": 3.0,
            },
            QuestionDifficulty.HARD,
        ),
        (
            "long_answer",
            {
                "prompt": "Explique pourquoi le scénario 9 (association et adresses e-mail) n'est ni un cyberharcèlement ni une menace, mais bien un traitement de données sans base valable, en t'appuyant sur des indices précis.",
                "source_document_version_id": scenarios_id,
                "rubric": (
                    "3 points : élimine explicitement le cyberharcèlement et la menace, faute "
                    "d'indices (répétition hostile ciblée, annonce d'un mal) (1 point) ; "
                    "identifie l'indice central du traitement de données sans base valable "
                    "(transmission à une entreprise de publicité sans information des "
                    "participants) (1 point) ; conclusion explicite et cohérente avec les "
                    "définitions du cours (1 point)."
                ),
                "expected_points": [
                    "Élimine le cyberharcèlement et la menace, faute d'indices",
                    "Identifie l'absence d'information des participants sur l'usage de leurs données",
                    "Conclut explicitement sur le traitement de données sans base valable",
                ],
                "max_score": 3.0,
            },
            QuestionDifficulty.HARD,
        ),
    ]

    imported = 0
    for question_type, content, difficulty in questions:
        validate_content(question_type, 1, content)
        source_doc_id = content.get("source_document_version_id")
        create_question(
            db,
            module_id=module.id,
            uaa_id=uaa.id,
            question_type=question_type,
            content_json=content,
            generation_source=GenerationSource.IMPORTED,
            difficulty_declared=difficulty,
            source_document_version_id=source_doc_id,
        )
        imported += 1
    db.flush()
    return imported


def import_fse07_to_bank(db: Session, module: Module, uaa: UAA) -> int:
    already_imported = (
        db.query(Question).filter_by(uaa_id=uaa.id, generation_source=GenerationSource.IMPORTED).count()
    )
    if already_imported:
        return 0

    school = create_source_document(db, title=FSE07_SCHOOL_TITLE, content_text=FSE07_SCHOOL_TEXT, module_id=module.id)
    chat = create_source_document(db, title=FSE07_CHAT_TITLE, content_text=FSE07_CHAT_TEXT, module_id=module.id)
    forum = create_source_document(db, title=FSE07_FORUM_TITLE, content_text=FSE07_FORUM_TEXT, module_id=module.id)
    db.flush()
    school_id, chat_id, forum_id = school.current_version_id, chat.current_version_id, forum.current_version_id

    questions: list[tuple[str, dict, QuestionDifficulty]] = [
        (
            "multiple_choice",
            {
                "prompt": "Un fait, dans l'analyse d'un dossier médiatique, est...",
                "options": [
                    {"option_id": "a", "label": "Un élément vérifiable, que plusieurs personnes indépendantes pourraient constater de la même façon"},
                    {"option_id": "b", "label": "Un jugement personnel sur une situation"},
                    {"option_id": "c", "label": "Une explication proposée à partir d'un autre élément"},
                    {"option_id": "d", "label": "Toute phrase présente dans un document, quel qu'il soit"},
                ],
                "correct_option_ids": ["a"],
                "explanation": "Le fait est vérifiable et constatable de façon similaire par plusieurs personnes indépendantes.",
            },
            QuestionDifficulty.EASY,
        ),
        (
            "vocabulary",
            {
                "prompt": "Définis l'interprétation, dans l'analyse d'un dossier.",
                "direction": "term_to_definition",
                "rubric": (
                    "Bonne réponse si elle définit l'interprétation comme une explication "
                    "proposée à partir d'un ou plusieurs faits, qui reste discutable."
                ),
            },
            QuestionDifficulty.EASY,
        ),
        (
            "vocabulary",
            {
                "prompt": "Définis l'opinion, dans l'analyse d'un dossier.",
                "direction": "term_to_definition",
                "rubric": (
                    "Bonne réponse si elle définit l'opinion comme un jugement personnel, qui "
                    "exprime un point de vue plutôt qu'un fait."
                ),
            },
            QuestionDifficulty.EASY,
        ),
        (
            "multiple_choice",
            {
                "prompt": "Pour évaluer la fiabilité d'un document, il faut vérifier...",
                "options": [
                    {"option_id": "a", "label": "Son auteur, sa date, son contexte et les preuves qu'il fournit"},
                    {"option_id": "b", "label": "Uniquement si le document est long ou court"},
                    {"option_id": "c", "label": "Uniquement le ton employé par l'auteur"},
                    {"option_id": "d", "label": "Uniquement le nombre de personnes qui l'ont partagé"},
                ],
                "correct_option_ids": ["a"],
                "explanation": "Auteur, date, contexte et preuves sont les quatre critères de fiabilité d'un document.",
            },
            QuestionDifficulty.EASY,
        ),
        (
            "short_answer",
            {
                "prompt": "Qui est l'auteur de la note de direction, et à quelle date a-t-elle été écrite ?",
                "source_document_version_id": school_id,
                "rubric": "Bonne réponse si elle cite M. Devos (directeur adjoint) et la date du 14 mars 2026.",
                "max_length": 200,
            },
            QuestionDifficulty.EASY,
        ),
        (
            "short_answer",
            {
                "prompt": "Pourquoi le document du forum est-il moins fiable que la note de direction ? Cite un indice précis.",
                "source_document_version_id": forum_id,
                "rubric": (
                    "Bonne réponse si elle cite l'anonymat de l'auteur (« parent_inquiet93 ») "
                    "et/ou l'absence de date, par opposition à la note de direction signée et "
                    "datée."
                ),
                "max_length": 300,
            },
            QuestionDifficulty.EASY,
        ),
        (
            "multiple_choice",
            {
                "prompt": "Dans ce dossier, l'affirmation « le groupe de discussion compte 24 élèves » est...",
                "options": [
                    {"option_id": "a", "label": "Un fait, car il provient d'un document signé et daté"},
                    {"option_id": "b", "label": "Une opinion, car elle dépend du point de vue de chacun"},
                    {"option_id": "c", "label": "Une interprétation, car elle reste discutable"},
                    {"option_id": "d", "label": "Une menace déguisée"},
                ],
                "correct_option_ids": ["a"],
                "explanation": "Cette information, vérifiable et tirée de la note de direction signée et datée, est un fait.",
            },
            QuestionDifficulty.EASY,
        ),
        (
            "classification",
            {
                "prompt": "Classe chacune de ces phrases du groupe-classe selon qu'il s'agit d'un fait, d'une interprétation ou d'une opinion.",
                "source_document_version_id": chat_id,
                "categories": ["Fait", "Interprétation", "Opinion"],
                "elements": [
                    "« La vidéo a été partagée le jour même dans le groupe »",
                    "« Je trouve que ça craint »",
                    "« De toute façon tout le monde filme tout le temps, c'est normal maintenant »",
                ],
                "correct_categories": [0, 2, 1],
                "explanation": "Le partage daté est un fait ; le jugement d'Elena est une opinion ; la généralisation de Thibault est une interprétation.",
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "ordering",
            {
                "prompt": "Classe ces trois documents du plus fiable au moins fiable, selon les critères auteur/date/contexte/preuves.",
                "items": [
                    {"id": "school", "label": "Note de la direction (signée, datée, faits précis)"},
                    {"id": "chat", "label": "Messages du groupe-classe (prénoms connus, mélange faits/opinions/interprétations)"},
                    {"id": "forum", "label": "Publication anonyme sur un forum (non datée, sans preuve)"},
                ],
                "correct_order": ["school", "chat", "forum"],
                "explanation": "La note de direction est la plus fiable (signée, datée, faits précis) ; le forum, anonyme et non daté, est le moins fiable.",
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "short_answer",
            {
                "prompt": (
                    "Le forum affirme que Lucas a été « humilié devant toute l'école ». La note "
                    "de direction mentionne un groupe de 24 élèves. Quel fait retiens-tu, et "
                    "pourquoi ?"
                ),
                "source_document_version_id": forum_id,
                "rubric": (
                    "Bonne réponse si elle retient le fait de la note de direction (groupe de 24 "
                    "élèves, document signé et daté) plutôt que l'affirmation anonyme et non "
                    "datée du forum, non confirmée par les autres documents."
                ),
                "max_length": 350,
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "ordering",
            {
                "prompt": "Remets dans l'ordre les étapes de la méthode face à un dossier de plusieurs documents.",
                "items": [
                    {"id": "e1", "label": "Identifier auteur, date, contexte et preuves de chaque document"},
                    {"id": "e2", "label": "Classer les affirmations importantes en faits, interprétations ou opinions"},
                    {"id": "e3", "label": "Comparer les documents entre eux et repérer les contradictions"},
                    {"id": "e4", "label": "Identifier les enjeux juridiques et sociologiques présents"},
                    {"id": "e5", "label": "Rédiger une conclusion argumentée appuyée sur les faits et enjeux identifiés"},
                ],
                "correct_order": ["e1", "e2", "e3", "e4", "e5"],
                "explanation": "La méthode part de la fiabilité des documents, classe les affirmations, compare, identifie les enjeux, puis conclut.",
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "document_analysis",
            {
                "prompt": (
                    "Analyse les messages du groupe-classe : identifie la norme implicite "
                    "dominante et explique en quoi certains messages montrent les limites de "
                    "l'influence sociale (notion vue en FSE04)."
                ),
                "source_document_version_id": chat_id,
                "rubric": (
                    "3 points : identifie la norme qui banalise le fait de filmer/partager "
                    "(Yasmine, Thibault) (1 point) ; identifie que Karim et Elena s'en écartent "
                    "explicitement (1 point) ; relie ce contraste à la limite de l'influence "
                    "sociale vue en FSE04 (la pression du groupe n'efface pas les positions "
                    "individuelles) (1 point)."
                ),
                "expected_points": [
                    "Identifie la norme qui banalise le fait de filmer/partager",
                    "Identifie que Karim et Elena s'en écartent explicitement",
                    "Relie ce contraste à la limite de l'influence sociale (FSE04)",
                ],
                "max_score": 3.0,
            },
            QuestionDifficulty.HARD,
        ),
        (
            "document_analysis",
            {
                "prompt": (
                    "Le forum affirme que « la direction n'a strictement rien fait ». Sachant "
                    "que la note de direction précise que « la vidéo a été supprimée du groupe à "
                    "la demande de la direction », évalue la fiabilité de cette affirmation du "
                    "forum et explique ta démarche."
                ),
                "source_document_version_id": forum_id,
                "rubric": (
                    "3 points : identifie la contradiction entre les deux documents (1 point) ; "
                    "explique que le forum, anonyme et non daté, est moins fiable que la note de "
                    "direction signée et datée (1 point) ; conclut que l'affirmation du forum ne "
                    "doit pas être traitée comme un fait établi (1 point)."
                ),
                "expected_points": [
                    "Identifie la contradiction entre les deux documents",
                    "Explique pourquoi le forum est moins fiable (anonyme, non daté)",
                    "Conclut que l'affirmation du forum n'est pas un fait établi",
                ],
                "max_score": 3.0,
            },
            QuestionDifficulty.HARD,
        ),
        (
            "long_answer",
            {
                "prompt": (
                    "Rédige une conclusion argumentée pour ce dossier : identifie un enjeu "
                    "juridique et un enjeu sociologique, en citant au moins un élément précis "
                    "d'un document fiable pour chacun."
                ),
                "source_document_version_id": school_id,
                "rubric": (
                    "3 points : identifie l'enjeu juridique (droit à l'image, filmer/diffuser "
                    "sans consentement) en s'appuyant sur la note de direction (1 point) ; "
                    "identifie l'enjeu sociologique (normes/influence sociale) en s'appuyant sur "
                    "les messages du groupe-classe (1 point) ; conclusion qui ne s'appuie pas "
                    "sur le document le moins fiable (forum) (1 point)."
                ),
                "expected_points": [
                    "Identifie l'enjeu juridique en s'appuyant sur la note de direction",
                    "Identifie l'enjeu sociologique en s'appuyant sur le groupe-classe",
                    "Ne s'appuie pas sur le document le moins fiable (forum)",
                ],
                "max_score": 3.0,
            },
            QuestionDifficulty.HARD,
        ),
    ]

    imported = 0
    for question_type, content, difficulty in questions:
        validate_content(question_type, 1, content)
        source_doc_id = content.get("source_document_version_id")
        create_question(
            db,
            module_id=module.id,
            uaa_id=uaa.id,
            question_type=question_type,
            content_json=content,
            generation_source=GenerationSource.IMPORTED,
            difficulty_declared=difficulty,
            source_document_version_id=source_doc_id,
        )
        imported += 1
    db.flush()
    return imported


def import_fse08_to_bank(db: Session, module: Module, uaa: UAA) -> int:
    already_imported = (
        db.query(Question).filter_by(uaa_id=uaa.id, generation_source=GenerationSource.IMPORTED).count()
    )
    if already_imported:
        return 0

    tableau = create_source_document(db, title=FSE08_MAP_TITLE, content_text=FSE08_MAP_TEXT, module_id=module.id)
    db.flush()
    tableau_id = tableau.current_version_id

    questions: list[tuple[str, dict, QuestionDifficulty]] = [
        (
            "multiple_choice",
            {
                "prompt": "Le niveau fédéral est compétent pour...",
                "options": [
                    {"option_id": "a", "label": "La justice, les affaires étrangères et la défense nationale"},
                    {"option_id": "b", "label": "L'enseignement et la culture"},
                    {"option_id": "c", "label": "L'urbanisme local et la propreté publique"},
                    {"option_id": "d", "label": "Le logement et l'environnement"},
                ],
                "correct_option_ids": ["a"],
                "explanation": "Ces matières concernent l'ensemble du pays et relèvent du niveau fédéral.",
            },
            QuestionDifficulty.EASY,
        ),
        (
            "multiple_choice",
            {
                "prompt": "Les Régions sont définies selon une logique...",
                "options": [
                    {"option_id": "a", "label": "Territoriale"},
                    {"option_id": "b", "label": "Liée uniquement à la langue parlée"},
                    {"option_id": "c", "label": "Liée uniquement à l'âge des habitants"},
                    {"option_id": "d", "label": "Identique à celle des Communautés"},
                ],
                "correct_option_ids": ["a"],
                "explanation": "Les trois Régions (flamande, wallonne, Bruxelles-Capitale) sont définies par un territoire.",
            },
            QuestionDifficulty.EASY,
        ),
        (
            "multiple_choice",
            {
                "prompt": "Les Communautés sont définies selon une logique...",
                "options": [
                    {"option_id": "a", "label": "Liée aux personnes, à la langue et à la culture"},
                    {"option_id": "b", "label": "Purement territoriale"},
                    {"option_id": "c", "label": "Liée uniquement à la taille de la population"},
                    {"option_id": "d", "label": "Identique à celle des provinces"},
                ],
                "correct_option_ids": ["a"],
                "explanation": "Les trois Communautés (française, flamande, germanophone) sont définies par les personnes, la langue et la culture.",
            },
            QuestionDifficulty.EASY,
        ),
        (
            "vocabulary",
            {
                "prompt": "Définis la monarchie constitutionnelle.",
                "direction": "term_to_definition",
                "rubric": (
                    "Bonne réponse si elle définit la monarchie constitutionnelle comme un "
                    "régime où le roi ne dispose que des pouvoirs attribués par la Constitution."
                ),
            },
            QuestionDifficulty.EASY,
        ),
        (
            "vocabulary",
            {
                "prompt": "Définis la démocratie parlementaire.",
                "direction": "term_to_definition",
                "rubric": (
                    "Bonne réponse si elle définit la démocratie parlementaire comme un régime "
                    "où le pouvoir est exercé par des représentants élus, réunis en parlements."
                ),
            },
            QuestionDifficulty.EASY,
        ),
        (
            "short_answer",
            {
                "prompt": "D'après le tableau, quel est le niveau de pouvoir le plus proche du citoyen ?",
                "source_document_version_id": tableau_id,
                "rubric": "Bonne réponse si elle répond « la commune ».",
                "max_length": 150,
            },
            QuestionDifficulty.EASY,
        ),
        (
            "short_answer",
            {
                "prompt": "L'affirmation A du tableau (« le niveau fédéral s'occupe de la justice et de la défense nationale ») est-elle vraie ou fausse ? Justifie en une phrase.",
                "source_document_version_id": tableau_id,
                "rubric": "Bonne réponse si elle répond « vraie » et justifie par le fait que justice et défense concernent l'ensemble du pays.",
                "max_length": 250,
            },
            QuestionDifficulty.EASY,
        ),
        (
            "classification",
            {
                "prompt": "Classe chaque compétence selon le niveau de pouvoir dont elle relève.",
                "source_document_version_id": tableau_id,
                "categories": ["Niveau fédéral", "Région", "Communauté"],
                "elements": ["La justice", "L'enseignement", "Le logement", "La défense nationale"],
                "correct_categories": [0, 2, 1, 0],
                "explanation": "Justice et défense = fédéral ; enseignement = Communauté (personnes/langue/culture) ; logement = Région (territoire).",
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "classification",
            {
                "prompt": "Classe chaque norme selon le niveau de pouvoir qui l'adopte.",
                "source_document_version_id": tableau_id,
                "categories": ["Niveau fédéral", "Région (hors Bruxelles) ou Communauté", "Région de Bruxelles-Capitale"],
                "elements": ["Une loi", "Un décret", "Une ordonnance"],
                "correct_categories": [0, 1, 2],
                "explanation": "Loi = fédéral ; décret = Région (sauf Bruxelles) ou Communauté ; ordonnance = Région de Bruxelles-Capitale.",
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "short_answer",
            {
                "prompt": "L'affirmation B du tableau (« la Région de Bruxelles-Capitale adopte des décrets, comme la Wallonie et la Flandre ») est-elle vraie ou fausse ? Précise l'exception.",
                "source_document_version_id": tableau_id,
                "rubric": "Bonne réponse si elle répond « fausse » et précise que Bruxelles adopte des ordonnances, pas des décrets.",
                "max_length": 250,
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "ordering",
            {
                "prompt": "Remets dans l'ordre les étapes de la méthode face à une compétence ou une norme citée dans un document.",
                "items": [
                    {"id": "e1", "label": "Demander si la matière concerne le pays entier, un territoire précis, ou les personnes/langue/culture"},
                    {"id": "e2", "label": "Vérifier s'il s'agit plutôt d'une compétence de province ou de commune"},
                    {"id": "e3", "label": "Identifier qui a adopté la norme pour en déduire son nom (loi/décret/ordonnance)"},
                    {"id": "e4", "label": "Vérifier qu'aucune généralisation incorrecte n'est faite (ex. exception de Bruxelles)"},
                ],
                "correct_order": ["e1", "e2", "e3", "e4"],
                "explanation": "La méthode part du type de matière, descend vers les niveaux locaux si besoin, identifie la norme, puis vérifie les exceptions.",
            },
            QuestionDifficulty.MEDIUM,
        ),
        (
            "document_analysis",
            {
                "prompt": "Analyse l'affirmation C du tableau (« il existe trois Communautés et trois Régions, qui se superposent exactement sur le même territoire ») : vraie ou fausse ? Explique la différence de logique entre Régions et Communautés.",
                "source_document_version_id": tableau_id,
                "rubric": (
                    "3 points : conclut que l'affirmation est fausse (1 point) ; explique que "
                    "les Régions suivent une logique territoriale et les Communautés une logique "
                    "de personnes/langue/culture (1 point) ; illustre avec un exemple de "
                    "non-superposition (ex. Bruxelles) (1 point)."
                ),
                "expected_points": [
                    "Conclut que l'affirmation est fausse",
                    "Explique la différence de logique (territoire vs personnes/langue)",
                    "Illustre avec un exemple de non-superposition",
                ],
                "max_score": 3.0,
            },
            QuestionDifficulty.HARD,
        ),
        (
            "document_analysis",
            {
                "prompt": "Analyse l'affirmation E du tableau (« le roi dispose de tous les pouvoirs qu'il souhaite exercer ») : vraie ou fausse ? Relie ta réponse à la notion de monarchie constitutionnelle.",
                "source_document_version_id": tableau_id,
                "rubric": (
                    "3 points : conclut que l'affirmation est fausse (1 point) ; explique que le "
                    "roi ne dispose que des pouvoirs attribués par la Constitution (1 point) ; "
                    "relie explicitement à la notion de monarchie constitutionnelle (1 point)."
                ),
                "expected_points": [
                    "Conclut que l'affirmation est fausse",
                    "Explique que le roi n'a que les pouvoirs attribués par la Constitution",
                    "Relie explicitement à la monarchie constitutionnelle",
                ],
                "max_score": 3.0,
            },
            QuestionDifficulty.HARD,
        ),
        (
            "long_answer",
            {
                "prompt": "Explique pourquoi la Belgique peut être à la fois une monarchie et une démocratie parlementaire, sans contradiction, en t'appuyant sur la séparation des pouvoirs.",
                "source_document_version_id": tableau_id,
                "rubric": (
                    "3 points : explique que le roi occupe une fonction limitée par la "
                    "Constitution (1 point) ; explique que le pouvoir réel est exercé par des "
                    "représentants élus (parlements) (1 point) ; relie ces deux éléments à la "
                    "séparation des pouvoirs (législatif/exécutif/judiciaire) pour montrer "
                    "l'absence de contradiction (1 point)."
                ),
                "expected_points": [
                    "Explique que le roi a une fonction limitée par la Constitution",
                    "Explique que le pouvoir réel est exercé par des représentants élus",
                    "Relie ces éléments à la séparation des pouvoirs",
                ],
                "max_score": 3.0,
            },
            QuestionDifficulty.HARD,
        ),
    ]

    imported = 0
    for question_type, content, difficulty in questions:
        validate_content(question_type, 1, content)
        source_doc_id = content.get("source_document_version_id")
        create_question(
            db,
            module_id=module.id,
            uaa_id=uaa.id,
            question_type=question_type,
            content_json=content,
            generation_source=GenerationSource.IMPORTED,
            difficulty_declared=difficulty,
            source_document_version_id=source_doc_id,
        )
        imported += 1
    db.flush()
    return imported
