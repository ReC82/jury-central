"""Plan Formation sociale et économique (FSE) — CESS Professionnel (ticket #96-#101).

Contexte : aucune matière « Formation sociale et économique » n'existait dans le dépôt
avant le ticket #96. Le périmètre complet (17 mini-cours FSE01→FSE17, voir le ticket
#96 § Plan) est fixé par ChatGPT (chef de projet). Ticket #96 : FSE01 livré. Ticket #97 :
FSE02, FSE03, FSE04 livrés. Ticket #98 : FSE05, FSE06, FSE07, FSE08 livrés. Ticket #99 :
FSE09, FSE10, FSE11, FSE12 livrés. Ticket #100 : FSE13, FSE14, FSE15, FSE16 livrés.
Ticket #101 : FSE17 livré (révision transversale, sans banque propre — voir
`app.v1.session_service._start_fse_transversal_session`). Les affirmations juridiques et
institutionnelles (FSE06, FSE08-11, FSE14) sont vérifiées auprès de sources belges
officielles et référencées avec URL + date dans chaque cours concerné (§ Sources
officielles vérifiées) et dans le rapport docs/claude-reports.

Ce module suit EXACTEMENT le même schéma que `app.v1.francais_plan`/`app.v1.ampcr_plan`
(registre code→titre→contexte pédagogique borné), consulté par
`app.v1.session_service`/`app.v1.routes_sessions`/`app.main` de la même façon."""

from dataclasses import dataclass

from app.ai.schemas import PedagogicalContext

FSE_SUBJECT_NAME = "Formation sociale et économique"
FSE_MODULE_CODE = "FSE"


@dataclass(frozen=True)
class FSEUAAPlan:
    code: str
    title: str
    # Regroupement thématique du programme officiel (ticket #96 § Plan) — métadonnée
    # d'information uniquement (pas une hiérarchie DB supplémentaire, voir
    # `docs/content_workflow.md` : Subject → Module → UAA reste la seule hiérarchie
    # persistée) : "Médias" (Interactions médiatiques, programme p. 41-47) ou "Citoyen"
    # (Le citoyen et l'État, programme p. 56-64).
    theme: str
    program_pages: str
    allowed_notions: tuple[str, ...]
    competencies: tuple[str, ...]

    @property
    def slug(self) -> str:
        return f"fse-{self.code.lower()}"

    @property
    def course_key(self) -> str:
        return f"fse-{self.code.lower()}"


# Ticket #96 : FSE01. Ticket #97 : FSE02-FSE04. Ticket #98 : FSE05-FSE08. Ticket #99 :
# FSE09-FSE12. Ticket #100 : FSE13-FSE16. Ticket #101 : FSE17 (révision transversale, sans
# banque propre). Les 17 mini-cours officiels sont désormais tous enregistrés ici.
FSE_PLAN: tuple[FSEUAAPlan, ...] = (
    FSEUAAPlan(
        code="FSE01",
        title="Communiquer : le schéma de communication",
        theme="Interactions médiatiques (Médias)",
        program_pages="programme 474/2016/240, p. 43-45",
        allowed_notions=(
            "émetteur et récepteur d'un message",
            "message, code et canal (support/contact)",
            "contexte (référent) d'une communication",
            "distinction entre canal (support de transmission) et code (système de signes utilisé)",
            "schéma de la communication appliqué à un mail, une affiche et une publication sur réseau social",
            "obstacle/bruit qui perturbe la transmission d'un message",
            "rétroaction (réponse du récepteur à l'émetteur) et ses limites selon le canal",
        ),
        competencies=(
            "Identifier émetteur, récepteur, message, code, canal et contexte dans une situation de communication réelle",
            "Distinguer canal et code dans un mail, une affiche ou une publication sur réseau social",
            "Expliquer comment un obstacle (bruit) perturbe une communication et quelles conséquences il entraîne",
            "Reconnaître la rétroaction disponible (ou son absence) selon le canal utilisé",
        ),
    ),
    FSEUAAPlan(
        code="FSE02",
        title="Les médias et leurs financements",
        theme="Interactions médiatiques (Médias)",
        program_pages="programme 474/2016/240, p. 43, 45",
        allowed_notions=(
            "offre médiatique : presse, radio, télévision, sites et réseaux sociaux",
            "interactivité d'un média (possibilité pour le récepteur de réagir/participer)",
            "financement d'un média par la vente directe (achat à l'unité)",
            "financement d'un média par l'abonnement",
            "financement d'un média par la publicité",
            "financement d'un média par des fonds publics",
            "lien entre le mode de financement d'un média, sa recherche d'audience et les comportements des publics",
        ),
        competencies=(
            "Identifier le ou les modes de financement d'un média à partir d'un document",
            "Expliquer en quoi la recherche d'audience influence le contenu proposé par un média",
            "Comparer un média payant, un média gratuit financé par la publicité et un média financé par des fonds publics",
        ),
    ),
    FSEUAAPlan(
        code="FSE03",
        title="Identités, traces numériques et appartenance",
        theme="Interactions médiatiques (Médias)",
        program_pages="programme 474/2016/240, p. 44-45",
        allowed_notions=(
            "identité personnelle (ce que je suis) et identité collective (appartenance à un groupe)",
            "identité numérique, comme application particulière de l'identité à un contexte médiatique",
            "trace numérique volontaire (publiée soi-même) et trace numérique involontaire (publiée par autrui, ou déduite)",
            "réputation, construite à partir des traces numériques visibles par autrui",
            "distinction entre l'identité réelle d'une personne et l'image qu'elle donne à voir à autrui",
        ),
        competencies=(
            "Distinguer une trace numérique volontaire d'une trace numérique involontaire",
            "Expliquer la différence entre l'identité d'une personne et l'image qu'elle donne à voir à autrui",
            "Expliquer les conséquences concrètes d'anciennes publications sur une candidature ou une réputation",
        ),
    ),
    FSEUAAPlan(
        code="FSE04",
        title="Normes, valeurs et influence sociale",
        theme="Interactions médiatiques (Médias)",
        program_pages="programme 474/2016/240, p. 44-46 (ressources remobilisées de l'UAA Normes et Société)",
        allowed_notions=(
            "norme (règle de comportement attendue dans un groupe ou une société)",
            "valeur (ce qu'un groupe ou une société considère comme important ou souhaitable)",
            "besoin et comportement, et leur rapport aux normes/valeurs d'un groupe",
            "frustration liée à un besoin non satisfait ou à une norme contraignante",
            "groupe d'appartenance",
            "influence sociale et pression du groupe sur le comportement individuel",
            "socialisation (processus par lequel une personne intègre les normes et valeurs d'un groupe)",
            "limites de l'influence sociale comme explication d'un comportement (ne réduit pas tout comportement au groupe)",
        ),
        competencies=(
            "Distinguer une norme, une valeur et un comportement dans une situation donnée",
            "Expliquer comment la pression d'un groupe peut influencer un comportement individuel",
            "Reconnaître les limites de l'explication par l'influence du groupe (responsabilité individuelle)",
        ),
    ),
    FSEUAAPlan(
        code="FSE05",
        title="Image, vie privée et données personnelles",
        theme="Interactions médiatiques (Médias)",
        program_pages="programme 474/2016/240, p. 45",
        allowed_notions=(
            "droit à l'image : droit de décider si l'on peut être photographié/filmé, et si cette image peut être utilisée ou diffusée",
            "distinction entre prise de vue (photographier/filmer) et diffusion (publier/partager/transmettre)",
            "sujet principal (personne mise en avant, reconnaissable) et personne accessoire (présente par hasard, non individualisée)",
            "absence de règle absolue selon laquelle un lieu public autoriserait toute diffusion",
            "exception de l'activité strictement personnelle ou domestique (partage dans un cercle très restreint)",
            "consentement spécifique à une finalité précise (un accord pour un usage n'autorise pas automatiquement un autre usage)",
            "vie privée : droit au respect de sa sphère personnelle, y compris en ligne",
            "donnée personnelle : toute information qui permet d'identifier une personne",
            "finalité : but précis pour lequel une donnée personnelle est collectée et utilisée",
            "protection renforcée des mineurs (accord parental, association croissante de l'enfant selon son âge)",
        ),
        competencies=(
            "Distinguer, dans une situation donnée, la prise de vue et la diffusion",
            "Déterminer si une personne est sujet principal ou personne accessoire sur une image, et la conséquence sur le consentement nécessaire",
            "Identifier une exception au principe du consentement (activité personnelle/domestique) sans la généraliser",
            "Reconnaître une utilisation de données personnelles qui dépasse la finalité annoncée",
        ),
    ),
    FSEUAAPlan(
        code="FSE06",
        title="Droits et comportements illicites en ligne",
        theme="Interactions médiatiques (Médias)",
        program_pages="programme 474/2016/240, p. 45",
        allowed_notions=(
            "liberté d'expression et ses limites",
            "cyberharcèlement (propos ou actes hostiles répétés en ligne, visant une même personne)",
            "injure (propos insultant visant une personne, sans fait précis affirmé)",
            "accusation non étayée / calomnie (affirmation d'un fait précis et négatif, non prouvé, qui nuit à la réputation)",
            "menace (annonce d'un mal futur, dans le but de faire peur ou de contraindre)",
            "racisme / discrimination (traitement défavorable fondé sur une origine, une couleur de peau, une religion ou une autre caractéristique protégée)",
            "usurpation d'identité (se faire passer pour quelqu'un d'autre en ligne, sans son accord)",
            "intrusion informatique (accès non autorisé à un compte, un appareil ou des données d'autrui)",
            "diffusion malveillante (partage d'une information, d'une image ou d'une vidéo dans le but explicite de nuire)",
            "traitement de données sans base valable (collecte ou usage de données personnelles sans justification ni information des personnes concernées)",
        ),
        competencies=(
            "Reconnaître, dans un scénario donné, le ou les comportements en ligne en jeu et les indices qui permettent de les identifier",
            "Distinguer une critique ou une opinion (couverte par la liberté d'expression) d'un comportement qui en dépasse les limites",
            "Expliquer, sans citer de peine ni d'article de loi, pourquoi un comportement décrit pose problème",
        ),
    ),
    FSEUAAPlan(
        code="FSE07",
        title="Analyser un dossier médiatique",
        theme="Interactions médiatiques (Médias)",
        program_pages="programme 474/2016/240, p. 41-47",
        allowed_notions=(
            "recueillir, traiter, analyser et synthétiser des informations (méthode documentaire)",
            "fait (élément vérifiable) distinct d'une interprétation (explication discutable à partir d'un fait) et d'une opinion (jugement personnel)",
            "vérifier un document : auteur, date, contexte et preuves disponibles",
            "enjeu juridique d'une situation médiatique (ex. droit à l'image, comportement en ligne, vus en FSE05/FSE06)",
            "enjeu sociologique d'une situation médiatique (ex. normes, valeurs, influence sociale, vus en FSE04)",
            "conclusion argumentée, appuyée explicitement sur des faits et enjeux identifiés",
        ),
        competencies=(
            "Distinguer, dans un dossier donné, un fait, une interprétation et une opinion",
            "Vérifier la fiabilité d'un document (auteur, date, contexte, preuves) avant de l'utiliser dans une analyse",
            "Identifier les enjeux juridiques et sociologiques d'un dossier médiatique, en mobilisant les notions déjà enseignées (FSE01, FSE04, FSE05, FSE06)",
            "Rédiger une conclusion argumentée qui s'appuie sur les faits et enjeux identifiés",
        ),
    ),
    FSEUAAPlan(
        code="FSE08",
        title="La Belgique : État et niveaux de pouvoir",
        theme="Le citoyen et l'État (Citoyen)",
        program_pages="programme 474/2016/240, p. 56-57, 61",
        allowed_notions=(
            "monarchie constitutionnelle (le roi ne dispose que des pouvoirs attribués par la Constitution)",
            "démocratie parlementaire (le pouvoir est exercé par des représentants élus, réunis en parlements)",
            "séparation des pouvoirs : législatif (faire les lois), exécutif (les appliquer), judiciaire (trancher les litiges)",
            "niveau fédéral (compétences concernant l'ensemble du pays : justice, affaires étrangères, défense, sécurité sociale)",
            "les trois Régions (flamande, wallonne, Bruxelles-Capitale) : compétences territoriales (économie, emploi, environnement, logement)",
            "les trois Communautés (française, flamande, germanophone) : compétences liées aux personnes, à la langue et à la culture (enseignement, culture)",
            "provinces et communes : niveaux de pouvoir locaux, la commune étant le niveau le plus proche du citoyen",
            "loi (norme fédérale), décret (norme d'une Région hors Bruxelles, ou d'une Communauté), ordonnance (norme de la Région de Bruxelles-Capitale) comme vocabulaire d'identification",
        ),
        competencies=(
            "Situer une compétence citée dans un document au bon niveau de pouvoir (fédéral, Région, Communauté, province, commune)",
            "Distinguer les trois Régions et les trois Communautés, et expliquer la différence de logique entre elles (territoriale vs personnes/langue)",
            "Identifier si une norme citée est une loi, un décret ou une ordonnance, à partir du niveau de pouvoir qui l'a adoptée",
            "Expliquer en quoi la Belgique est une monarchie constitutionnelle et une démocratie parlementaire, avec la séparation des pouvoirs comme repère",
        ),
    ),
    FSEUAAPlan(
        code="FSE09",
        title="Qui décide de quoi ?",
        theme="Le citoyen et l'État (Citoyen)",
        program_pages="programme 474/2016/240, p. 61-62",
        allowed_notions=(
            "répartition des compétences entre niveaux de pouvoir (approfondit FSE08)",
            "compétences du niveau fédéral (justice, affaires étrangères, défense, sécurité sociale)",
            "compétences des Régions (économie, emploi, environnement, logement, travaux publics)",
            "compétences des Communautés (enseignement, culture, aide à la jeunesse)",
            "rôle de proximité des communes et rôle d'appui technique des provinces",
            "matières partagées entre plusieurs niveaux (ex. santé) — jamais une réponse unique trompeuse",
        ),
        competencies=(
            "Associer une situation concrète au niveau de pouvoir compétent et à la matière concernée",
            "Reconnaître qu'une situation peut impliquer plusieurs niveaux de pouvoir à la fois",
        ),
    ),
    FSEUAAPlan(
        code="FSE10",
        title="Élections et participation citoyenne",
        theme="Le citoyen et l'État (Citoyen)",
        program_pages="programme 474/2016/240, p. 61-62",
        allowed_notions=(
            "niveaux pour lesquels on vote : fédéral, régional, européen, communal, provincial",
            "scrutin proportionnel et nécessité d'une coalition",
            "obligation de vote et conditions d'âge, vérifiées par scrutin et par région à la date du cours",
            "procuration, vote valable/blanc/nul, témoin du dépouillement",
            "pétition et distinction entre consultation populaire et référendum",
        ),
        competencies=(
            "Analyser des bulletins fictifs et un tableau daté des scrutins",
            "Expliquer vote blanc/nul/procuration sans confondre abstention et vote blanc",
            "Ne jamais généraliser une règle électorale d'un scrutin ou d'une région à un autre",
        ),
    ),
    FSEUAAPlan(
        code="FSE11",
        title="Partis politiques et choix argumenté",
        theme="Le citoyen et l'État (Citoyen)",
        program_pages="programme 474/2016/240, p. 61-62",
        allowed_notions=(
            "familles politiques : socialiste, libérale, écologiste, centriste/humaniste, positions radicales",
            "axe gauche-centre-droite comme repère simplifié, jamais une vérité absolue",
            "les six partis de l'exemple 2024 (PS, MR, Ecolo, Les Engagés, PTB, Vlaams Belang), identifiés par famille à partir de sources datées",
            "comparaison neutre de propositions par valeurs, priorités et effets attendus",
        ),
        competencies=(
            "Associer des extraits sourcés aux familles politiques",
            "Comparer deux propositions sans exprimer d'opinion personnelle",
            "Reconnaître les limites de l'axe gauche-centre-droite",
        ),
    ),
    FSEUAAPlan(
        code="FSE12",
        title="Le budget de l'État",
        theme="Le citoyen et l'État (Citoyen)",
        program_pages="programme 474/2016/240, p. 61",
        allowed_notions=(
            "recettes fiscales (impôts, dont l'IPP nommée sans calcul), parafiscales (cotisations) et non fiscales",
            "dépenses de fonctionnement, d'investissement et de transfert",
            "solde budgétaire, déficit et dette comme vocabulaire d'analyse",
            "calculs simples de recettes/dépenses/solde sur données fictives",
        ),
        competencies=(
            "Classer des recettes et des dépenses selon leur type",
            "Calculer recettes, dépenses et solde en détaillant les opérations",
        ),
    ),
    FSEUAAPlan(
        code="FSE13",
        title="La sécurité sociale : rôle et financement",
        theme="Le citoyen et l'État (Citoyen)",
        program_pages="programme 474/2016/240, p. 61",
        allowed_notions=(
            "solidarité, mutualisation des risques, assurance sociale, redistribution",
            "cotisations travailleurs/employeurs, financement public et alternatif",
            "distinction entre financement, gestion et versement",
            "risques couverts (maladie/invalidité, chômage, vieillesse, accident du travail, charges familiales)",
            "repères salarié/indépendant, sans calcul de droits",
        ),
        competencies=(
            "Expliquer le trajet d'une cotisation à une prestation",
            "Identifier le risque couvert dans une situation donnée",
        ),
    ),
    FSEUAAPlan(
        code="FSE14",
        title="La sécurité sociale : organismes et enjeux",
        theme="Le citoyen et l'État (Citoyen)",
        program_pages="programme 474/2016/240, p. 61-62",
        allowed_notions=(
            "organismes et rôles : ONSS, INAMI, ONEM, SFP, FEDRIS, ONVA, INASTI",
            "allocations familiales régionalisées (FAMIWAL en Wallonie, FAMIRIS à Bruxelles)",
            "distinction collecteur/gestionnaire/intermédiaire payeur",
            "enjeux de vieillissement, d'emploi et de dépenses de santé, sans montants ni âges non vérifiés",
        ),
        competencies=(
            "Associer un organisme à son rôle et à sa branche",
            "Expliquer deux pressions sur le financement à partir d'un document daté",
        ),
    ),
    FSEUAAPlan(
        code="FSE15",
        title="Le circuit économique et les interventions de l'État",
        theme="Le citoyen et l'État (Citoyen)",
        program_pages="programme 474/2016/240, p. 43, 61-63",
        allowed_notions=(
            "agents : ménages, entreprises, État, reste du monde",
            "flux réels et flux monétaires",
            "politiques de redistribution, de régulation et de production de biens/services collectifs",
        ),
        competencies=(
            "Compléter un circuit économique et y représenter les effets d'une aide publique",
        ),
    ),
    FSEUAAPlan(
        code="FSE16",
        title="Analyser une décision publique",
        theme="Le citoyen et l'État (Citoyen)",
        program_pages="programme 474/2016/240, p. 57-58, 62-64",
        allowed_notions=(
            "méthode d'analyse : décision, niveau compétent, objectifs, agents, flux, effets attendus, limites, conséquences indirectes",
            "distinction court terme / long terme",
            "réutilisation de budget, sécurité sociale et circuit économique comme outils d'analyse",
        ),
        competencies=(
            "Analyser un dossier de 3 documents sur une décision publique",
            "Rédiger une conclusion fondée sur les documents",
        ),
    ),
    FSEUAAPlan(
        code="FSE17",
        title="Révision générale et méthode d'examen",
        theme="Synthèse (Médias + Citoyen)",
        program_pages="synthèse de FSE01-FSE16 — aucune notion nouvelle",
        allowed_notions=(
            "synthèse exclusive des notions déjà enseignées en FSE01-FSE16",
            "méthode d'examen : citer, identifier, expliquer, justifier",
        ),
        competencies=(
            "Mobiliser les notions de FSE01-FSE16 dans un contexte transversal",
            "Appliquer la méthode d'examen appropriée selon le verbe de consigne",
        ),
    ),
)

FSE_PLAN_BY_CODE: dict[str, FSEUAAPlan] = {plan.code: plan for plan in FSE_PLAN}
FSE_PLAN_BY_SLUG: dict[str, FSEUAAPlan] = {plan.slug: plan for plan in FSE_PLAN}


def get_fse_plan_by_slug(uaa_slug: str) -> FSEUAAPlan | None:
    return FSE_PLAN_BY_SLUG.get(uaa_slug)


def _build_context(plan: FSEUAAPlan) -> PedagogicalContext:
    return PedagogicalContext(
        course_key=plan.course_key,
        course_title=plan.title,
        level="CESS Professionnel — Formation sociale et économique, niveau standard",
        allowed_notions=list(plan.allowed_notions),
        competencies=list(plan.competencies),
        vocabulary=[],
        constraints=(
            "PÉRIMÈTRE STRICT (consignes CESS P 2026-2027/1, tickets #96-#101) : reste "
            "exclusivement dans les notions listées ci-dessus — n'évalue et ne valorise "
            "jamais une connaissance de budget familial, crédits, emprunts, TAEG, IPP, "
            "fiscalité immobilière, ou toute autre notion hors de ce mini-cours. Les "
            "exemples utilisés dans ce cours sont originaux, rédigés pour ce cours : ne "
            "jamais inventer de fait, d'organisme réel ou de règle juridique absent du "
            "support fourni — les organisations citées dans les exemples sont fictives "
            "sauf mention contraire explicite. Niveau adapté à un·e élève de CESS "
            "Professionnel qui reprend ses études."
        ),
    )


FSE_CONTEXTS: dict[str, PedagogicalContext] = {plan.course_key: _build_context(plan) for plan in FSE_PLAN}


def get_fse_context(course_key: str) -> PedagogicalContext | None:
    return FSE_CONTEXTS.get(course_key)


# Ticket #101 : codes FSE01→FSE16 (périmètre réel de la révision transversale FSE17 — jamais
# FSE17 lui-même, qui n'a pas de banque propre). Utilisé par
# `app.v1.session_service._start_fse_transversal_session`, même principe que
# `app.v1.mc38_transversal.MC38_SESSION_SCOPE`/`mc01_to_mc37_codes`.
FSE17_CODE = "FSE17"
FSE17_SESSION_SCOPE = "fse17_transversal"


def fse01_to_fse16_codes() -> list[str]:
    return [plan.code for plan in FSE_PLAN if plan.code != FSE17_CODE]
