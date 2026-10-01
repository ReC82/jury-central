"""Banque V1 FSE — FSE01 « Communiquer : le schéma de communication » (ticket #96,
cahier des charges détaillé du ticket #97).

Même principe que `app.v1.francais_fr01_05_bank::import_francais_fr01_to_bank` (#94) :
import idempotent, hand-authored, revalidé par le registre #40 (`validate_content`) avant
stockage — aucune question ne référence un texte sans un `SourceDocumentVersion`
réellement rattaché quand le type le permet (`short_answer`/`vocabulary`/
`classification`/`document_analysis`/`long_answer` portent un `source_document_version_id`
optionnel ou requis selon le type ; `multiple_choice`/`ordering` n'ont pas ce champ dans le
registre #40 — ces questions restent volontairement conceptuelles, jamais un résumé
dupliqué d'un document).

14 questions couvrant les trois applications explicitement demandées par le ticket #97
(mail, affiche, publication sur réseau social), variées dans leur type (identification,
classement, justification courte, analyse de document) — jamais uniquement des QCM."""

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
from app.v1.models import (
    GenerationSource,
    Question,
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

    questions: list[tuple[str, dict]] = [
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
        ),
        (
            "classification",
            {
                "prompt": (
                    "Pour chacun de ces trois canaux, indique si une rétroaction directe "
                    "et immédiate vers l'émetteur est possible ou non."
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
                    "une réponse rapide et visible (le service recrutement répond à "
                    "Karim ; des commentaires répondent à Techno Services). Une affiche, "
                    "elle, ne permet aucune rétroaction directe vers son émetteur."
                ),
            },
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
                    "rétroaction directe (le conducteur ne peut pas répondre immédiatement "
                    "à l'émetteur depuis son véhicule) (1 point)."
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
                    "constituent une rétroaction visible et rapide (1 point) ; mise en "
                    "évidence que ce canal permet un dialogue (l'entreprise répond "
                    "elle-même à un commentaire) (1 point)."
                ),
                "expected_points": [
                    "Identifie l'absence d'information sur le salaire comme obstacle",
                    "Relie cet obstacle au commentaire de Julien P.",
                    "Identifie les commentaires/partages comme rétroaction",
                    "Mentionne que l'entreprise répond elle-même à un commentaire (dialogue)",
                ],
                "max_score": 3.0,
            },
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
                    "(le mail), qui permet à Karim de corriger rapidement sa candidature "
                    "(1 point)."
                ),
                "expected_points": [
                    "Identifie la coupure de connexion comme obstacle",
                    "Explique la conséquence concrète (message incomplet, sans CV)",
                    "Explique comment la rétroaction (réponse du recruteur) permet de résoudre le problème",
                ],
                "max_score": 3.0,
            },
        ),
    ]

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
