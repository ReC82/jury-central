"""Consignes FSE autonomes et contexte des questions extraites de dossiers (ticket #152).

Une question servie seule (entraînement, examen blanc transversal FSE17, quiz) doit se
comprendre sans le cours ni la question précédente : action demandée, objet analysé et
catégories explicites, données propres à la situation fournies (« cette aide » montre la
proposition qui la décrit), aucun renvoi à un ordre de dossier perdu (« maintenant »,
« ces trois autres »), et un support qui ne donne pas la réponse attendue (« Une région
modifie… » à côté de « quel niveau de pouvoir est compétent ? »).

Remises en ordre de méthode : chaque question annonce un rappel de méthode, nomme le
cours et l'objet de la méthode, et ne garde que des étapes dont l'ordre est réellement
contraint (chaque étape utilise le résultat de la précédente). Les étapes facultatives ou
interchangeables du cours (« si demandé », vérifications parallèles, mises en garde) sont
regroupées dans l'étape qui les utilise, pour ne jamais sanctionner un ordre raisonnable.

`clarity_repairs()` est la seule liste des corrections : `app.v1.fse_bank` l'applique à une
banque neuve (`apply_clarity`) et `repair_prompt_clarity` met à niveau une banque déjà
importée par une NOUVELLE `QuestionVersion` (jamais une version modifiée en place : les
sessions déjà générées gardent la version servie, pour la reprise, la correction, les
résultats et l'export). Même principe pour le document FSE09 (`DOCUMENT_UPGRADES`) :
nouvelle `SourceDocumentVersion`, les anciennes versions restent servies aux anciennes
sessions.

`audit_prompt_clarity` relit les questions actives et liste les consignes dépendantes d'un
contexte absent."""

import re
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.models import UAA
from app.v1 import question_types  # noqa: F401 — enregistre les types (seed hors banque)
from app.v1.models import (
    ContentStatus,
    Question,
    QuestionVersion,
    SourceDocument,
    SourceDocumentVersion,
    add_question_version,
    add_source_document_version,
)
from app.v1.question_engine import validate_content


def _method_prompt(code: str, title: str, goal: str) -> str:
    return (
        f"Rappel de méthode (cours {code} « {title} », sans document à analyser) : remets "
        f"dans l'ordre les étapes pour {goal}. Chaque étape s'appuie sur le résultat de la "
        "précédente."
    )


def _steps(*labels: str) -> dict:
    items = [{"id": f"e{index}", "label": label} for index, label in enumerate(labels, start=1)]
    return {"items": items, "correct_order": [item["id"] for item in items]}


@dataclass(frozen=True)
class ClarityRepair:
    uaa_code: str
    question_type: str
    # Consignes reconnues (ancienne(s) formulation(s) ; la nouvelle est ajoutée d'office).
    old_prompts: tuple[str, ...]
    # Champs du contenu remplacés (jamais les identifiants de document).
    fields: dict
    # Titres exacts des documents à montrer, dans l'ordre du dossier (None : inchangés).
    document_titles: tuple[str, ...] | None = None
    # Discriminant quand deux questions partagent la même consigne (FSE06).
    first_element: str | None = None
    reason: str = ""
    prompts: tuple[str, ...] = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "prompts", (*self.old_prompts, self.fields["prompt"]))


def _method_repairs() -> tuple[ClarityRepair, ...]:
    reason = "méthode non nommée ; étapes interchangeables ou facultatives dans l'ordre strict"
    return (
        ClarityRepair(
            "FSE02",
            "ordering",
            ("Remets dans l'ordre les étapes de la méthode pour analyser le financement d'un média à partir d'un document.",),
            {
                "prompt": _method_prompt(
                    "FSE02", "Les médias et leurs financements",
                    "analyser le financement d'un média présenté dans un document",
                ),
                **_steps(
                    "Repérer dans le document les indices de financement : prix ou abonnement, "
                    "publicités, dotation ou mission de service public",
                    "En déduire le mode de financement principal du média",
                    "Relier ce mode de financement au comportement du média (recherche "
                    "d'audience ou non)",
                ),
                "explanation": "Le mode de financement se déduit des indices relevés ; on ne peut le relier "
                "au comportement du média qu'une fois ce financement identifié.",
            },
            reason=reason,
        ),
        ClarityRepair(
            "FSE03",
            "ordering",
            ("Remets dans l'ordre les étapes de la méthode pour analyser un ensemble de traces numériques concernant une personne.",),
            {
                "prompt": _method_prompt(
                    "FSE03", "Identités, traces numériques et appartenance",
                    "analyser les traces numériques laissées par une personne",
                ),
                **_steps(
                    "Relever chaque trace et préciser si elle est volontaire (publiée par la "
                    "personne) ou involontaire (publiée par un tiers, ou ancienne et redevenue "
                    "visible)",
                    "Décrire l'image que ces traces donnent à un observateur extérieur, en la "
                    "distinguant de l'identité réelle de la personne",
                    "Expliquer la conséquence concrète de cette image sur une situation réelle "
                    "(candidature, relation)",
                ),
                "explanation": "On part des traces relevées, on en tire l'image donnée à voir, puis on "
                "explique l'effet de cette image sur une situation réelle.",
            },
            reason=reason,
        ),
        ClarityRepair(
            "FSE04",
            "ordering",
            ("Remets dans l'ordre les étapes de la méthode pour analyser une situation de groupe.",),
            {
                "prompt": _method_prompt(
                    "FSE04", "Normes, valeurs et influence sociale",
                    "analyser le comportement d'un groupe décrit dans une situation",
                ),
                **_steps(
                    "Décrire la situation : la valeur en jeu, la norme suivie par le groupe et "
                    "les comportements réellement décrits",
                    "Expliquer en quoi l'influence sociale (pression, désir d'intégration) rend "
                    "ce comportement fréquent dans le groupe",
                    "Nuancer cette explication : elle ne supprime pas la responsabilité "
                    "individuelle, d'autres membres du groupe agissent autrement",
                ),
                "explanation": "On décrit d'abord la situation, on l'explique ensuite par l'influence "
                "sociale, puis on nuance cette explication.",
            },
            reason=reason,
        ),
        ClarityRepair(
            "FSE05",
            "ordering",
            ("Remets dans l'ordre les étapes de la méthode face à une situation impliquant une image ou une donnée personnelle.",),
            {
                "prompt": _method_prompt(
                    "FSE05", "Image, vie privée et données personnelles",
                    "décider si un consentement est nécessaire pour une image ou une donnée "
                    "personnelle",
                ),
                **_steps(
                    "Préciser l'acte en cause : prise de vue, diffusion, ou les deux (à traiter "
                    "séparément)",
                    "Appliquer les critères à cet acte : sujet principal ou personne accessoire, "
                    "cadre strictement personnel ou public plus large, finalité annoncée pour "
                    "une donnée",
                    "Conclure sur la nécessité ou non d'un consentement, sans invoquer la seule "
                    "présence dans un lieu public",
                ),
                "explanation": "Les critères s'appliquent à un acte précis (prise de vue ou diffusion) ; "
                "la conclusion sur le consentement découle de ces critères.",
            },
            reason=reason,
        ),
        # Retour du 22/10 : cas nouveau #129 (permanence), même défaut que ci-dessus.
        ClarityRepair(
            "FSE09",
            "classification",
            ("Et pour ces trois autres demandes, quel niveau de pouvoir est compétent ?",),
            {"prompt": "D'après les fiches de la permanence, quel niveau de pouvoir est compétent "
             "pour les demandes 1, 6 et 7 ?"},
            reason="« ces trois autres » dépend d'une question précédente",
        ),
        ClarityRepair(
            "FSE06",
            "ordering",
            ("Remets dans l'ordre les étapes de la méthode face à un scénario en ligne.",),
            {
                "prompt": _method_prompt(
                    "FSE06", "Droits et comportements illicites en ligne",
                    "qualifier un comportement en ligne décrit dans un scénario",
                ),
                **_steps(
                    "Relever les indices concrets décrits : répétition, menace, accusation sans "
                    "preuve, usage du nom ou de la photo d'autrui, accès non autorisé, intention "
                    "de nuire",
                    "Qualifier le comportement à partir de ces indices (injure, calomnie, "
                    "menace, cyberharcèlement, usurpation d'identité, intrusion informatique, "
                    "diffusion malveillante…), ou conclure à une simple critique ou opinion s'il "
                    "n'y a ni insulte ni accusation non prouvée",
                    "Justifier la qualification retenue en citant les indices précis relevés, "
                    "sans article de loi ni peine",
                ),
                "explanation": "La qualification (y compris « simple opinion ») se fait à partir des "
                "indices relevés, et la justification cite ces mêmes indices.",
            },
            reason="méthode et catégories non nommées ; « scénario » absent ; la vérification "
            "« simple opinion » peut légitimement précéder la qualification",
        ),
        ClarityRepair(
            "FSE07",
            "ordering",
            ("Remets dans l'ordre les étapes de la méthode face à un dossier de plusieurs documents.",),
            {
                "prompt": _method_prompt(
                    "FSE07", "Analyser un dossier médiatique",
                    "analyser un dossier de plusieurs documents",
                ),
                **_steps(
                    "Évaluer la fiabilité de chaque document : auteur, date, contexte, preuves",
                    "Confronter les documents à la lumière de cette fiabilité : retenir les "
                    "faits établis, écarter les interprétations, opinions et affirmations "
                    "contredites par un document plus fiable",
                    "Identifier les enjeux juridiques et sociologiques à partir des faits établis",
                    "Rédiger une conclusion argumentée appuyée sur ces faits et ces enjeux",
                ),
                "explanation": "La fiabilité permet de trier les affirmations ; les enjeux s'identifient à "
                "partir des faits retenus ; la conclusion s'appuie sur les deux.",
            },
            reason=reason,
        ),
        ClarityRepair(
            "FSE08",
            "ordering",
            ("Remets dans l'ordre les étapes de la méthode face à une compétence ou une norme citée dans un document.",),
            {
                "prompt": _method_prompt(
                    "FSE08", "La Belgique : État et niveaux de pouvoir",
                    "attribuer une compétence ou une norme au bon niveau de pouvoir",
                ),
                **_steps(
                    "Déterminer l'étendue de la matière : pays entier, territoire précis, "
                    "personnes/langue/culture, ou affaire très locale",
                    "En déduire le niveau de pouvoir compétent : fédéral, Région, Communauté, "
                    "province ou commune",
                    "Si une norme est citée, en déduire son nom à partir du niveau qui l'adopte : "
                    "loi, décret ou ordonnance (exception de Bruxelles)",
                ),
                "explanation": "L'étendue de la matière désigne le niveau compétent, et le nom de la "
                "norme dépend du niveau qui l'adopte.",
            },
            reason=reason,
        ),
        ClarityRepair(
            "FSE09",
            "ordering",
            ("Remets dans l'ordre les étapes de la méthode pour déterminer le niveau compétent dans une situation.",),
            {
                "prompt": _method_prompt(
                    "FSE09", "Qui décide de quoi ?",
                    "déterminer le niveau de pouvoir compétent dans une situation",
                ),
                **_steps(
                    "Identifier la matière concernée (justice, économie, enseignement, voirie "
                    "locale…)",
                    "Associer cette matière au niveau compétent, en vérifiant si la situation "
                    "décrit un partage entre plusieurs niveaux",
                    "Justifier la réponse par la matière elle-même, sans supposition non "
                    "confirmée par l'énoncé",
                ),
                "explanation": "Le niveau compétent se déduit de la matière, et la justification "
                "s'appuie sur cette même matière.",
            },
            reason=reason,
        ),
        ClarityRepair(
            "FSE10",
            "ordering",
            ("Remets dans l'ordre les étapes de la méthode face à une question sur les élections.",),
            {
                "prompt": _method_prompt(
                    "FSE10", "Élections et participation citoyenne",
                    "répondre à une question sur une élection",
                ),
                **_steps(
                    "Identifier le scrutin précis concerné : fédéral, régional, européen, "
                    "communal ou provincial",
                    "Retrouver les règles en vigueur pour ce scrutin et, si nécessaire, pour "
                    "cette région (obligation de vote, âge), sans les généraliser à un autre "
                    "scrutin",
                    "Appliquer ces règles au cas posé et justifier la réponse",
                ),
                "explanation": "Les règles dépendent du scrutin (et parfois de la région) ; on ne peut "
                "les appliquer qu'une fois le scrutin identifié.",
            },
            reason=reason,
        ),
        ClarityRepair(
            "FSE11",
            "ordering",
            ("Remets dans l'ordre les étapes de la méthode face à un extrait ou une proposition politique.",),
            {
                "prompt": _method_prompt(
                    "FSE11", "Partis politiques et choix argumenté",
                    "analyser un extrait ou une proposition politique",
                ),
                **_steps(
                    "Identifier la valeur mise en avant et la priorité affichée",
                    "Déduire de cette priorité les effets attendus : qui en bénéficie, qui y "
                    "contribue",
                    "Si demandé, associer ces éléments à une famille politique, comme simple "
                    "repère gauche-centre-droite et sans jugement personnel",
                ),
                "explanation": "Les effets attendus découlent de la priorité affichée ; l'association à "
                "une famille politique s'appuie sur la valeur, la priorité et les effets.",
            },
            reason=reason,
        ),
        ClarityRepair(
            "FSE12",
            "ordering",
            ("Remets dans l'ordre les étapes de la méthode pour analyser un tableau de recettes/dépenses.",),
            {
                "prompt": _method_prompt(
                    "FSE12", "Le budget de l'État",
                    "analyser un tableau de recettes et de dépenses publiques",
                ),
                **_steps(
                    "Classer chaque ligne du tableau : recette (fiscale, parafiscale, non "
                    "fiscale) ou dépense (fonctionnement, investissement, transfert)",
                    "Additionner séparément le total des recettes et le total des dépenses",
                    "Calculer le solde budgétaire : total des recettes − total des dépenses",
                    "Nommer le solde obtenu : déficit s'il est négatif, excédent s'il est positif",
                ),
                "explanation": "Les totaux supposent les lignes classées, le solde suppose les deux "
                "totaux, et on ne nomme le solde qu'une fois calculé.",
            },
            reason="deux additions indépendantes présentées comme deux étapes ordonnées",
        ),
        ClarityRepair(
            "FSE13",
            "ordering",
            ("Remets dans l'ordre les étapes de la méthode face à une situation de sécurité sociale.",),
            {
                "prompt": _method_prompt(
                    "FSE13", "La sécurité sociale : rôle et financement",
                    "analyser une situation de sécurité sociale, sans calculer de montant",
                ),
                **_steps(
                    "Identifier le risque couvert : maladie-invalidité, chômage, vieillesse, "
                    "accident du travail, charges familiales…",
                    "Décrire le trajet de l'argent pour ce risque : qui finance (cotisations), "
                    "qui gère, qui verse la prestation",
                    "Relier ce trajet au principe de solidarité et de mutualisation",
                ),
                "explanation": "Le trajet de l'argent dépend du risque couvert, et la solidarité "
                "s'explique à partir de ce trajet.",
            },
            reason="mise en garde (« ne jamais calculer ») présentée comme une étape",
        ),
        ClarityRepair(
            "FSE14",
            "ordering",
            ("Remets dans l'ordre les étapes de la méthode face à un organisme ou un enjeu de sécurité sociale.",),
            {
                "prompt": _method_prompt(
                    "FSE14", "La sécurité sociale : organismes et enjeux",
                    "analyser le rôle d'un organisme de sécurité sociale",
                ),
                **_steps(
                    "Identifier l'organisme concerné et la branche de sécurité sociale qu'il "
                    "couvre",
                    "Déterminer son rôle dans le trajet de l'argent : collecteur, gestionnaire "
                    "ou intermédiaire payeur",
                    "Expliquer, à partir de ce rôle, ce que l'organisme fait concrètement dans "
                    "la situation (par exemple verser les allocations familiales de la Région "
                    "concernée)",
                ),
                "explanation": "Le rôle se détermine pour un organisme identifié, et ce qu'il fait "
                "concrètement découle de ce rôle.",
            },
            reason="étapes alternatives (« pour les allocations familiales… », « pour un enjeu "
            "de financement… ») présentées comme successives",
        ),
        ClarityRepair(
            "FSE15",
            "ordering",
            ("Remets dans l'ordre les étapes de la méthode face à un circuit économique à compléter ou analyser.",),
            {
                "prompt": _method_prompt(
                    "FSE15", "Le circuit économique et les interventions de l'État",
                    "analyser un circuit économique",
                ),
                **_steps(
                    "Identifier les agents concernés : ménages, entreprises, État, reste du monde",
                    "Pour chaque échange entre ces agents, préciser s'il s'agit d'un flux réel "
                    "(bien, service, travail) ou d'un flux monétaire (paiement)",
                    "Suivre l'effet d'une intervention de l'État d'un agent à l'autre (par "
                    "exemple aide → salaires → consommation)",
                ),
                "explanation": "Les flux relient des agents identifiés, et l'effet d'une intervention se "
                "suit de flux en flux.",
            },
            reason=reason,
        ),
        ClarityRepair(
            "FSE16",
            "ordering",
            ("Remets dans l'ordre les étapes de la méthode pour analyser une décision publique.",),
            {
                "prompt": _method_prompt(
                    "FSE16", "Analyser une décision publique",
                    "analyser une décision publique",
                ),
                **_steps(
                    "Identifier la décision, le niveau compétent et ses objectifs",
                    "Identifier les agents concernés et les flux engendrés",
                    "Distinguer effets à court terme et effets possibles à long terme, avec "
                    "leurs limites",
                    "Rédiger une conclusion fondée sur les documents",
                ),
                "explanation": "La méthode part de la décision, identifie agents/flux, distingue "
                "court/long terme, puis conclut.",
            },
            reason="méthode non annoncée comme rappel (étapes inchangées, ordre déjà contraint)",
        ),
    )


FSE09_EXAM_TITLE = "Dix situations — qui décide de quoi ?"


@dataclass(frozen=True)
class DocumentUpgrade:
    title: str
    old_text: str
    new_text: str


def document_upgrades() -> tuple[DocumentUpgrade, ...]:
    from app.v1.fse09_content import (
        FSE09_SITUATIONS_EXAM_TEXT,
        FSE09_SITUATIONS_TEXT,
        FSE09_SITUATIONS_TITLE,
    )

    return (DocumentUpgrade(FSE09_SITUATIONS_TITLE, FSE09_SITUATIONS_TEXT, FSE09_SITUATIONS_EXAM_TEXT),)


def _context_repairs() -> tuple[ClarityRepair, ...]:
    from app.v1.fse16_content import (
        FSE16_BUDGET_NOTE_TITLE,
        FSE16_PROPOSAL_TITLE,
        FSE16_REACTIONS_TITLE,
    )

    return (
        # Retour du 22/10 (audit « la subvention / la proposition ») : la note budgétaire
        # (document 2) commence par « La subvention serait financée… » sans dire laquelle ;
        # la proposition (document 1) est affichée avant elle, comme pour le document 3.
        ClarityRepair(
            "FSE16",
            "classification",
            ("Classe chaque élément selon qu'il relève du court terme ou du long terme (incertain).",),
            {
                "prompt": "D'après la note budgétaire (document 2), qui accompagne la proposition "
                "du document 1, classe chaque élément selon qu'il relève du court terme ou du "
                "long terme (incertain).",
            },
            document_titles=(FSE16_PROPOSAL_TITLE, FSE16_BUDGET_NOTE_TITLE),
            reason="« La subvention » du document 2 sans la proposition qui la décrit",
        ),
        ClarityRepair(
            "FSE16",
            "document_analysis",
            ("Analyse la note budgétaire (document 2) : pourquoi présente-t-elle la compensation par de nouvelles recettes comme une hypothèse plutôt qu'un fait acquis ?",),
            {
                "prompt": "Analyse la note budgétaire (document 2), qui accompagne la proposition du "
                "document 1 : pourquoi présente-t-elle la compensation par de nouvelles recettes "
                "comme une hypothèse plutôt qu'un fait acquis ?",
            },
            document_titles=(FSE16_PROPOSAL_TITLE, FSE16_BUDGET_NOTE_TITLE),
            reason="« La subvention » du document 2 sans la proposition qui la décrit",
        ),
        # Q2/20 de la capture : recopier l'auteur déjà écrit dans le document → analyse des
        # effets et limites (étape 3 de la méthode FSE16), avec la proposition (document 1)
        # qui donne son antécédent à « Cette aide ».
        ClarityRepair(
            "FSE16",
            "classification",
            ("Classe chaque réaction selon l'agent qui l'exprime.",),
            {
                "prompt": "Le document 1 présente une proposition : un gouvernement régional "
                "subventionnerait une partie du prix des abonnements de transport collectif pour "
                "les travailleurs à revenus modestes. D'après le document 3 (réactions des groupes "
                "concernés), classe chaque extrait selon qu'il exprime un effet attendu de cette "
                "aide ou une limite/un coût.",
                "categories": ["Effet attendu", "Limite ou coût"],
                "elements": [
                    "Le ménage : « Cette aide me permettrait d'accepter un emploi plus loin de chez moi »",
                    "L'entreprise de transport : « Nous nous attendons à une hausse de la fréquentation »",
                    ("L'entreprise de transport : « …mais aussi à des coûts supplémentaires pour "
                     "augmenter la capacité de nos lignes les plus demandées »"),
                    ("L'association environnementale : « Nous saluons l'effet attendu de réduction "
                     "de l'usage de la voiture individuelle »"),
                    ("L'association environnementale : « …cet effet dépendra de la capacité réelle "
                     "du réseau à absorber la demande supplémentaire »"),
                ],
                "correct_categories": [0, 0, 1, 0, 1],
                "explanation": "Accepter un emploi plus loin, la hausse de fréquentation et la réduction "
                "de l'usage de la voiture sont des effets attendus de l'aide ; les coûts "
                "supplémentaires de capacité et la dépendance à la capacité réelle du réseau "
                "sont une limite ou un coût.",
            },
            document_titles=(FSE16_PROPOSAL_TITLE, FSE16_REACTIONS_TITLE),
            reason="l'auteur est déjà écrit dans le document (exercice de recopie) ; « Cette "
            "aide » sans la proposition ; « Association » mêlée aux catégories d'agents",
        ),
        # Q7/20 : point de départ explicite, deux actions séparées, usage partiel accepté.
        ClarityRepair(
            "FSE15",
            "short_answer",
            ("Dans l'exemple de l'aide publique au média, quel agent reçoit le premier flux monétaire, et que fait-il ensuite de cet argent ?",),
            {
                "prompt": "D'après le document, l'État verse une aide publique à un média local. "
                "(a) Qui reçoit cette aide, et dans quelle catégorie d'agent économique le "
                "classes-tu (ménages, entreprises, État ou reste du monde) ? (b) Selon le "
                "document, à quoi ce bénéficiaire utilise-t-il une partie de cette aide ?",
                "rubric": "Deux éléments attendus. (a) Le bénéficiaire est le média local, classé "
                "parmi les entreprises (accepter « le média », « le média local », « une entreprise "
                "de presse »…). (b) Il utilise une partie de l'aide pour payer les salaires de ses "
                "employés (accepter « verser des salaires », « payer son personnel »…). Le "
                "document indique un usage PARTIEL : ne pas exiger que toute l'aide finance les "
                "salaires, ni que la réponse décrive les dépenses ultérieures des employés. Une "
                "formulation différente mais correcte est acceptée ; le mot « flux » n'est pas "
                "exigé.",
                "max_length": 400,
            },
            reason="« premier flux monétaire » sans point de départ ; deux actions dans une "
            "seule question ; usage partiel de l'aide non pris en compte",
        ),
        # Q8/20 et voisines : tâches autonomes, situations décrites dans la consigne.
        ClarityRepair(
            "FSE09",
            "classification",
            ("Associe maintenant ces trois autres situations au bon niveau de pouvoir.",),
            {
                # Formulation distincte de la question « situations 1 à 4 » (contrôle des
                # quasi-doublons, `app.v1.dedup`).
                "prompt": "Pour chacune des situations 5, 6 et 7, indique qui décide : le niveau "
                "fédéral, une Région ou une Communauté ?",
                "elements": [
                    "Situation 5 — militaires belges envoyés en mission internationale",
                    "Situation 6 — normes environnementales pour les entreprises situées en Wallonie",
                    "Situation 7 — campagne culturelle dans des bibliothèques publiques francophones",
                ],
            },
            reason="« maintenant… ces trois autres » dépend d'une question précédente",
        ),
        ClarityRepair(
            "FSE09",
            "classification",
            ("Classe chaque situation selon le niveau de pouvoir compétent.",),
            {
                "prompt": "Classe les situations 1 à 4 du document selon le niveau de pouvoir "
                "compétent.",
                "elements": [
                    "Situation 1 — règles de procédure pénale pour tout le pays",
                    "Situation 2 — aides aux entreprises qui s'installent en Wallonie",
                    "Situation 3 — programmes de cours des écoles francophones",
                    "Situation 4 — bancs publics et trottoirs d'une localité",
                ],
            },
            reason="« chaque situation » alors que seules quatre sont classées",
        ),
        ClarityRepair(
            "FSE09",
            "multiple_choice",
            ("Dans la situation 9 (aide technique d'une province aux communes), le niveau concerné est...",),
            {"prompt": "Dans la situation 9 (aide technique aux communes d'un même territoire), le "
             "niveau de pouvoir concerné est..."},
            reason="la réponse (« province ») était écrite dans la consigne",
        ),
        ClarityRepair(
            "FSE09",
            "multiple_choice",
            ("Après avoir vu les compétences régionales et communautaires en FSE08, quelle matière reste gérée au niveau fédéral, pour l'ensemble du pays ?",),
            {"prompt": "Parmi ces matières, laquelle reste gérée au niveau fédéral, pour "
             "l'ensemble du pays ?"},
            reason="consigne dépendante de l'ordre des cours",
        ),
        ClarityRepair(
            "FSE09",
            "document_analysis",
            ("Analyse la situation 10 (coordination fédéral/régional) : quelles compétences sont en jeu, et pourquoi une coordination est-elle nécessaire ?",),
            {"prompt": "Analyse la situation 10 (réforme fiscale et règles sur le logement) : "
             "quelles compétences sont en jeu, à quels niveaux de pouvoir, et pourquoi une "
             "coordination est-elle nécessaire ?"},
            reason="les niveaux attendus (« fédéral/régional ») étaient écrits dans la consigne",
        ),
        ClarityRepair(
            "FSE06",
            "classification",
            (
                "Classe maintenant ces trois autres scénarios selon le comportement qu'ils illustrent.",
                "Classe chaque scénario selon le comportement principal qu'il illustre.",
            ),
            {"prompt": "Classe les scénarios 6, 7 et 8 du document selon le comportement qu'ils "
             "illustrent."},
            first_element="Scénario 6 (faux profil au nom d'un camarade)",
            reason="« maintenant… ces trois autres » dépend d'une question précédente",
        ),
        ClarityRepair(
            "FSE12",
            "classification",
            ("À présent, range chacune de ces lignes de dépense dans la bonne catégorie.",),
            {"prompt": "Range chaque ligne de dépense du tableau dans la bonne catégorie : "
             "fonctionnement, investissement ou transfert."},
            reason="« À présent » dépend d'une question précédente",
        ),
    )


def clarity_repairs() -> tuple[ClarityRepair, ...]:
    return (*_method_repairs(), *_context_repairs())


# =========================================================================================
# Application
# =========================================================================================


def _matches(repair: ClarityRepair, question_type: str, content: dict) -> bool:
    if question_type != repair.question_type or content.get("prompt") not in repair.prompts:
        return False
    if repair.first_element is not None:
        return (content.get("elements") or [None])[0] == repair.first_element
    return True


def _module_documents(db: Session, module_id: int | None) -> dict[str, int]:
    """Titre → version COURANTE des documents du module (la plus récente en cas
    d'homonymie)."""
    query = db.query(SourceDocument).filter(SourceDocument.current_version_id.isnot(None))
    if module_id is not None:
        query = query.filter(SourceDocument.module_id == module_id)
    current_ids = [doc.current_version_id for doc in query]
    if not current_ids:
        return {}
    titles: dict[str, int] = {}
    for version in (
        db.query(SourceDocumentVersion)
        .filter(SourceDocumentVersion.id.in_(current_ids))
        .order_by(SourceDocumentVersion.id)
    ):
        titles[version.title] = version.id
    return titles


def _apply(repair: ClarityRepair, content: dict, documents: dict[str, int]) -> dict | None:
    """Contenu corrigé, ou None si un document nécessaire est introuvable."""
    patched = {**content, **repair.fields}
    if repair.document_titles is None:
        return patched
    wanted = [documents.get(title) for title in repair.document_titles]
    if None in wanted:
        return None
    primary = content.get("source_document_version_id")
    if primary not in wanted:
        primary = wanted[0]
    patched["source_document_version_id"] = primary
    if len(wanted) > 1:
        patched["source_document_version_ids"] = wanted
    else:
        patched.pop("source_document_version_ids", None)
    return patched


def apply_clarity(db: Session, uaa: UAA, question_type: str, content: dict) -> dict:
    """Banque neuve : contenu corrigé de cette question si elle figure dans
    `clarity_repairs()` (sinon inchangé)."""
    for repair in clarity_repairs():
        if repair.uaa_code == uaa.code and _matches(repair, question_type, content):
            patched = _apply(repair, content, _module_documents(db, uaa.module_id))
            if patched is None:
                raise ValueError(f"Document introuvable pour la correction #152 : {repair.document_titles}")
            validate_content(question_type, 1, patched)
            return patched
    return content


def _upgrade_documents(db: Session) -> tuple[dict[int, int], int]:
    """Nouvelle version des documents de `document_upgrades()` (idempotent) ; renvoie la
    correspondance ancienne version → version d'examen, pour réorienter les questions."""
    mapping: dict[int, int] = {}
    created = 0
    for upgrade in document_upgrades():
        candidates = (
            db.query(SourceDocument)
            .join(SourceDocumentVersion, SourceDocumentVersion.id == SourceDocument.current_version_id)
            .filter(SourceDocumentVersion.title == upgrade.title)
            .all()
        )
        for document in candidates:
            current = db.get(SourceDocumentVersion, document.current_version_id)
            if current.content_text == upgrade.old_text:
                current = add_source_document_version(
                    db, document, title=upgrade.title, content_text=upgrade.new_text
                )
                db.flush()
                created += 1
            if current.content_text != upgrade.new_text:
                continue
            for version in db.query(SourceDocumentVersion).filter_by(source_document_id=document.id):
                if version.id != current.id and version.content_text == upgrade.old_text:
                    mapping[version.id] = current.id
    return mapping, created


def _repoint(content: dict, mapping: dict[int, int]) -> dict:
    patched = dict(content)
    if patched.get("source_document_version_id") in mapping:
        patched["source_document_version_id"] = mapping[patched["source_document_version_id"]]
    if patched.get("source_document_version_ids"):
        patched["source_document_version_ids"] = [mapping.get(i, i) for i in patched["source_document_version_ids"]]
    return patched


def repair_prompt_clarity(db: Session) -> dict[str, int]:
    """Met à niveau une banque déjà importée (idempotent) : au plus une nouvelle version
    par question (consigne corrigée et/ou document d'examen), anciennes versions et
    sessions intactes."""
    mapping, documents_created = _upgrade_documents(db)
    by_uaa: dict[str, list[ClarityRepair]] = {}
    for repair in clarity_repairs():
        by_uaa.setdefault(repair.uaa_code, []).append(repair)
    codes = set(by_uaa)
    if mapping:
        codes.add("FSE09")
    repaired = 0
    unresolved = 0
    for uaa in db.query(UAA).filter(UAA.code.in_(codes)).all():
        documents = _module_documents(db, uaa.module_id)
        questions = (
            db.query(Question)
            .filter(Question.uaa_id == uaa.id, Question.status == ContentStatus.ACTIVE)
            .order_by(Question.id)
            .all()
        )
        for question in questions:
            version = question.current_version
            if version is None:
                continue
            content = dict(version.content_json or {})
            patched = _repoint(content, mapping)
            for repair in by_uaa.get(uaa.code, ()):
                if _matches(repair, version.question_type, patched):
                    result = _apply(repair, patched, documents)
                    if result is None:
                        unresolved += 1
                    else:
                        patched = result
                    break
            if patched == content:
                continue
            validate_content(version.question_type, version.schema_version, patched)
            add_question_version(
                db,
                question,
                question_type=version.question_type,
                content_json=patched,
                generator_model=version.generator_model,
                prompt_version=version.prompt_version,
                source_program_version=version.source_program_version,
                source_document_version_id=patched.get("source_document_version_id"),
            )
            repaired += 1
    db.flush()
    return {"repaired": repaired, "unresolved": unresolved, "documents": documents_created}


# =========================================================================================
# Audit
# =========================================================================================

# Consigne qui dépend d'une question précédente ou de l'ordre des cours.
_SEQUENCE = re.compile(
    r"\bmaintenant\b|\bà présent\b|\b(?:ces|les) (?:deux|trois|quatre) autres\b|\baprès avoir vu\b",
    re.IGNORECASE,
)
# Renvoi à un contenu de cours non nommé.
_VAGUE = re.compile(r"\b(?:catégories|notions|étapes) vues en cours\b", re.IGNORECASE)
# « Cette aide / cette décision… » : un antécédent doit figurer dans la consigne ou dans
# un document affiché.
_DEMONSTRATIVE = re.compile(r"\bcette (aide|décision|mesure|proposition|réforme)\b", re.IGNORECASE)
_ANTECEDENT = re.compile(r"\baide\b|subvention|propos|\bdécision|\bmesure\b|réforme", re.IGNORECASE)
# Retour du 22/10 : « la subvention / la proposition » (article défini) renvoie aussi à une
# mesure déjà présentée quand un DOCUMENT affiché l'emploie ; il faut qu'un texte affiché
# (document ou consigne) l'INTRODUISE (« propose de… », « une
# aide… »), pas seulement qu'il répète le mot — sinon un document d'accompagnement servi
# seul (note budgétaire, réactions) passait l'audit.
_DEFINITE = re.compile(r"\b(?:la|cette) (?:aide|subvention|proposition|mesure|décision|réforme)\b", re.IGNORECASE)
_INTRODUCED = re.compile(
    r"\bpropose(?:nt)? de\b|\bune (?:aide|subvention|proposition|mesure|décision|réforme)\b|"
    r"\bdécide(?:nt)? de\b|\ba décidé\b|\bverse une aide\b",
    re.IGNORECASE,
)


def _is_fse_dossier(version: QuestionVersion) -> bool:
    """Règle « la subvention / la proposition » réservée aux dossiers FSE (pièces courtes
    qui s'accompagnent) : un texte Français complet introduit autrement sa décision
    (« a fait installer… Cette décision », FR02)."""
    uaa = version.question.uaa if version.question else None
    return bool(uaa and uaa.code.startswith("FSE"))


def clarity_problems(db: Session, version: QuestionVersion) -> list[str]:
    from app.v1.document_references import _shown_documents

    content = version.content_json or {}
    prompt = str(content.get("prompt", ""))
    labels = " ".join(
        str(item.get("label", "")) if isinstance(item, dict) else str(item)
        for item in (content.get("items") or []) + (content.get("elements") or [])
    )
    problems: list[str] = []
    if _SEQUENCE.search(prompt):
        problems.append("consigne dépendante d'une question ou d'un cours précédent")
    if _VAGUE.search(f"{prompt} {labels}"):
        problems.append("renvoi à des catégories « vues en cours » non nommées")
    if version.question_type == "ordering" and "méthode" in prompt and "Rappel de méthode" not in prompt:
        problems.append("remise en ordre de méthode non annoncée comme rappel, cours non nommé")
    shown = " ".join(doc.content_text or "" for doc in _shown_documents(db, version))
    text = f"{shown} {prompt}"
    if _DEMONSTRATIVE.search(text) and not _ANTECEDENT.search(_DEMONSTRATIVE.sub("", text)):
        problems.append("« cette aide/décision… » sans antécédent affiché")
    elif _is_fse_dossier(version) and _DEFINITE.search(shown) and not _INTRODUCED.search(text):
        problems.append("« la subvention/la proposition… » sans document qui la présente")
    return problems


def audit_prompt_clarity(db: Session, *, uaa_prefix: str = "FSE") -> dict:
    query = (
        db.query(Question, UAA.code)
        .join(UAA, UAA.id == Question.uaa_id)
        .filter(Question.status == ContentStatus.ACTIVE, UAA.code.like(f"{uaa_prefix}%"))
    )
    audited = 0
    flagged: list[dict] = []
    for question, code in query.all():
        version = question.current_version
        if version is None:
            continue
        audited += 1
        problems = clarity_problems(db, version)
        if problems:
            flagged.append({"question_id": question.id, "uaa": code, "prompt": version.content_json.get("prompt"), "problems": problems})
    return {"audited": audited, "flagged": flagged}
