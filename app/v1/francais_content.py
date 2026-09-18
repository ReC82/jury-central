"""Contenu Français V1 — corpus d'entraînement technique (ticket #47, étendu en overnight
mission du 2026-09-19 pour passer d'un pilote à un outil d'étude réellement utilisable).

**Statut explicite : PROVISIONAL_TECHNICAL_SAMPLE / contenu d'entraînement ORIGINAL, pas
un document officiel CESS.** Aucun contenu Français officiel n'existait dans le dépôt au
moment du ticket #47 (voir `docs/content_plan_informatique_francais.md` § 3.3). Ce module
fournit 5 textes support COURTS, ORIGINAUX et NEUTRES (rédigés spécifiquement pour ce
ticket, aucun texte protégé copié) : le pilote initial (smartphone, texte principal +
second texte de comparaison) plus 3 nouveaux textes (numérique au quotidien, formation
professionnelle, débat sur la programmation à l'école) — voir
`docs/francais_v1_functional.md` pour le détail des compétences couvertes par chacun.
**Aucun de ces textes ne doit jamais être présenté comme un examen CESS officiel** à un
élève réel. Le vrai corpus pédagogique Français, s'il diffère de celui-ci, remplacera ces
textes dès qu'il sera fourni par l'équipe pédagogique."""

MAIN_DOCUMENT_TITLE = "Le smartphone au quotidien : outil précieux ou distraction permanente ?"

MAIN_DOCUMENT_TEXT = """Le smartphone au quotidien : outil précieux ou distraction permanente ?

Il y a une quinzaine d'années à peine, le téléphone portable servait surtout à passer des
appels et à envoyer de courts messages. Aujourd'hui, le smartphone est devenu un outil
central de la vie quotidienne, aussi bien à l'école qu'au travail ou dans la vie
personnelle. Cette transformation rapide soulève une question simple mais importante :
le smartphone est-il devenu un allié indispensable, ou représente-t-il surtout une source
de distraction qu'il faudrait mieux encadrer ?

À l'école, l'usage du smartphone divise. D'un côté, l'appareil permet un accès immédiat à
une quantité considérable d'informations : un élève peut vérifier une date historique,
consulter la traduction d'un mot ou revoir une notion mal comprise en quelques secondes.
Certains enseignants utilisent également des applications pédagogiques qui rendent les
cours plus interactifs, par exemple pour faire des quiz en temps réel ou partager des
documents facilement. De l'autre côté, de nombreux enseignants constatent que la présence
du smartphone en classe favorise les distractions : notifications qui interrompent
l'attention, tentation de consulter les réseaux sociaux pendant un cours, ou encore
difficulté à se concentrer sur une lecture longue quand on a l'habitude de messages
courts et rapides. Plusieurs écoles ont d'ailleurs choisi d'interdire totalement le
smartphone pendant les heures de cours, estimant que les bénéfices ne compensent pas les
pertes de concentration observées.

Au travail, la situation est assez similaire. Le smartphone facilite la communication
entre collègues, permet de consulter ses emails professionnels en déplacement et donne
accès à des outils d'organisation comme les calendriers partagés ou les listes de tâches.
Pour de nombreux métiers, notamment ceux qui impliquent des déplacements, il est devenu un
outil de travail à part entière. Cependant, cette même facilité d'accès pose un problème
nouveau : la frontière entre vie professionnelle et vie privée devient de plus en plus
floue. Beaucoup de travailleurs se sentent obligés de répondre à des messages
professionnels en dehors de leurs heures de travail, ce qui peut augmenter le stress et
réduire le temps de repos réellement disponible. Certaines entreprises ont commencé à
mettre en place des règles explicites, comme le droit de ne pas répondre aux emails après
une certaine heure, précisément pour limiter cet effet.

Dans la vie personnelle, le smartphone occupe également une place particulière. Il permet
de rester en contact facilement avec sa famille et ses amis, même à distance, grâce aux
appels vidéo et aux messageries instantanées. Il donne aussi accès à une immense variété
de contenus : musique, films, actualités, jeux. Mais plusieurs études ont montré qu'une
utilisation excessive, en particulier juste avant de dormir, peut perturber la qualité du
sommeil, notamment à cause de la lumière des écrans et de la stimulation mentale
provoquée par le défilement continu de contenus. Certains utilisateurs décrivent aussi un
sentiment de dépendance : difficulté à rester longtemps sans vérifier leur téléphone,
même en l'absence de notification réelle.

Face à ce constat partagé, une position tranchée semble difficile à défendre. Interdire
complètement le smartphone reviendrait à se priver d'un outil réellement utile pour
l'accès à l'information, la communication et l'organisation. Mais l'utiliser sans aucune
limite comporte des risques bien documentés : perte de concentration, confusion entre
temps de travail et temps de repos, dépendance et sommeil perturbé. La plupart des
spécialistes s'accordent aujourd'hui sur une troisième voie : apprendre à utiliser le
smartphone de manière raisonnée, en fixant soi-même des limites claires (par exemple,
pas de téléphone pendant les repas, ou une heure fixe après laquelle on ne consulte plus
ses messages professionnels), plutôt que de le rejeter ou de l'accepter sans réflexion. Le
smartphone n'est donc ni un ennemi ni un allié absolu : c'est un outil, et comme tout
outil, son effet dépend largement de la manière dont on l'utilise.
"""

SECOND_DOCUMENT_TITLE = "Un second avis : pourquoi certaines écoles interdisent le smartphone en classe"

SECOND_DOCUMENT_TEXT = """Un second avis : pourquoi certaines écoles interdisent le smartphone en classe

Plusieurs établissements scolaires ont choisi une position plus stricte que celle décrite
dans le texte précédent : l'interdiction complète du smartphone pendant toute la journée
de cours, y compris pendant les pauses. Pour les directions qui défendent cette règle,
les arguments pédagogiques l'emportent largement sur les avantages pratiques de
l'appareil. Selon elles, même un usage ponctuel et autorisé du smartphone en classe crée
une habitude de vérification constante qui nuit à la capacité de concentration sur le
long terme, bien au-delà du seul moment où l'appareil est utilisé.

Ces établissements notent également un effet sur les relations entre élèves pendant les
récréations : lorsque le smartphone est autorisé, une grande partie des échanges
verbaux directs entre élèves diminue au profit d'un usage individuel de l'appareil. Une
interdiction totale, disent-ils, encourage davantage les interactions sociales réelles
pendant les temps de pause. Contrairement à une position nuancée qui chercherait un
équilibre, ces écoles défendent donc une règle simple et non négociable, qu'elles jugent
plus facile à faire respecter qu'un usage « raisonné » laissé à l'appréciation de chaque
élève.
"""


# --- Nouveaux documents (overnight mission du 2026-09-19, § Phase 5) -----------------------

DIGITAL_LIFE_DOCUMENT_TITLE = "Le numérique dans la vie quotidienne : une présence discrète mais constante"

DIGITAL_LIFE_DOCUMENT_TEXT = """Le numérique dans la vie quotidienne : une présence discrète mais constante

Se lever, consulter la météo, vérifier ses messages, prendre les transports en commun
grâce à une application, payer son pain sans sortir d'espèces : en l'espace de quelques
décennies, le numérique s'est glissé dans presque tous les gestes de la vie quotidienne,
souvent sans que l'on y prête vraiment attention. Cette présence discrète soulève
pourtant des questions concrètes, aussi bien pour les individus que pour la société dans
son ensemble.

Le premier domaine transformé est celui de l'accès à l'information. Il y a encore vingt
ans, trouver une information précise demandait souvent de consulter un livre, un
dictionnaire ou d'appeler une personne compétente. Aujourd'hui, une recherche sur
Internet permet d'obtenir une réponse en quelques secondes, que ce soit pour vérifier une
adresse, comprendre un terme technique ou suivre l'actualité en direct. Cette rapidité a
un avantage évident : elle fait gagner du temps et permet une prise de décision plus
informée. Elle comporte cependant un risque tout aussi réel, largement documenté par les
chercheurs en éducation aux médias : toutes les informations disponibles en ligne ne se
valent pas, et la facilité d'accès ne garantit en rien leur fiabilité. Savoir distinguer
une source sérieuse d'une source douteuse devient donc une compétence à part entière,
que l'école cherche de plus en plus à enseigner explicitement.

Le numérique a également transformé la manière dont les services du quotidien
fonctionnent. Les démarches administratives, la gestion d'un compte bancaire, la prise de
rendez-vous médical ou encore les achats se font désormais très largement en ligne. Pour
une grande partie de la population, cette évolution représente un gain de confort
indéniable : plus besoin de se déplacer, les démarches peuvent se faire à toute heure, et
certaines procédures autrefois longues sont désormais quasi instantanées. Mais cette
même évolution laisse de côté une partie non négligeable de la population, en particulier
les personnes âgées ou celles qui n'ont pas eu l'occasion de développer une aisance avec
les outils numériques. On parle aujourd'hui couramment de « fracture numérique » pour
désigner cet écart entre ceux qui maîtrisent ces outils et ceux qui s'en trouvent
exclus, parfois pour des démarches essentielles comme le renouvellement d'un document
d'identité ou l'accès à certaines aides sociales.

La vie sociale n'échappe pas non plus à cette transformation. Les réseaux sociaux et les
messageries instantanées permettent de rester en contact avec des proches éloignés, de
partager des moments de vie ou d'organiser des événements en quelques clics. De
nombreuses études montrent que ces outils jouent un rôle réel dans le maintien de liens
familiaux ou amicaux, en particulier à distance. En parallèle, d'autres recherches
pointent un effet moins positif : le temps passé sur les écrans peut se substituer à des
interactions en face à face, et l'exposition permanente aux publications d'autrui
alimenterait, chez certains utilisateurs, un sentiment de comparaison sociale
inconfortable. Le numérique ne remplace donc pas les relations humaines, mais il en
modifie clairement les formes et les habitudes.

Enfin, le monde du travail et de la formation a lui aussi été profondément marqué par
cette évolution. Le télétravail, rendu possible par les outils numériques, s'est
largement développé ces dernières années, offrant à de nombreux travailleurs une
flexibilité nouvelle dans l'organisation de leur temps. Les formations en ligne
permettent également d'apprendre de nouvelles compétences sans nécessairement se
déplacer vers un centre de formation. Ces changements ouvrent des possibilités réelles,
en particulier pour les personnes qui concilient emploi, famille et apprentissage. Ils
demandent toutefois une capacité d'organisation personnelle plus importante qu'un cadre
plus traditionnel, ce qui ne convient pas à tout le monde de la même façon.

Au terme de ce parcours rapide à travers plusieurs domaines de la vie quotidienne, un
constat s'impose : le numérique n'est ni une simple commodité ni une menace uniforme. Il
transforme en profondeur la manière dont les individus s'informent, accèdent aux
services, entretiennent leurs relations et se forment, avec des bénéfices réels mais
aussi des effets qui ne touchent pas tout le monde de la même façon. Comprendre ces
transformations, plutôt que les subir passivement, semble être la condition nécessaire
pour en tirer parti de manière équilibrée.
"""

TRAINING_DOCUMENT_TITLE = "La formation professionnelle à l'heure du numérique"

TRAINING_DOCUMENT_TEXT = """La formation professionnelle à l'heure du numérique

Pendant longtemps, se former à un métier signifiait suivre un parcours largement fixé à
l'avance : une école, un horaire de cours, un formateur présent physiquement, et un
diplôme obtenu au terme d'un cursus de plusieurs années. Ce modèle reste aujourd'hui
largement dominant, en particulier pour les métiers qui demandent une pratique concrète
et encadrée, comme les métiers techniques ou manuels. Mais depuis une dizaine d'années,
de nouvelles formes de formation professionnelle se sont développées en parallèle,
portées principalement par les outils numériques, et elles changent progressivement la
manière dont de nombreux adultes envisagent leur évolution professionnelle.

La première évolution majeure concerne l'apprentissage en ligne, souvent désigné par le
terme anglais e-learning. Des plateformes spécialisées proposent aujourd'hui des cours
dans des domaines très variés : langues étrangères, programmation informatique, gestion
de projet, comptabilité, ou encore compétences dites « douces » comme la communication
ou le management d'équipe. Ces formations présentent un avantage évident : elles peuvent
être suivies à n'importe quel moment, souvent depuis un smartphone ou un ordinateur
personnel, ce qui les rend compatibles avec un emploi du temps chargé. Un employé qui
travaille à temps plein peut ainsi suivre une formation le soir ou le week-end, sans
devoir demander un congé ou réorganiser toute sa semaine. Certaines entreprises
encouragent d'ailleurs activement cette pratique, en mettant à disposition de leurs
employés un accès gratuit à ce type de plateforme, dans le cadre de ce qu'on appelle la
formation continue.

Cette flexibilité a cependant un revers bien documenté par les chercheurs en pédagogie :
le taux d'abandon dans les formations en ligne non accompagnées est nettement plus élevé
que dans une formation classique en présentiel. Sans horaire fixe ni interaction directe
avec un formateur ou d'autres apprenants, de nombreuses personnes commencent une
formation en ligne avec de bonnes intentions, puis l'abandonnent après quelques semaines,
faute de motivation suffisante ou par manque de temps réellement dégagé. Pour répondre à
ce problème, certaines plateformes ont commencé à intégrer des éléments qui rapprochent
l'apprentissage en ligne d'un cadre plus structuré : des groupes de discussion entre
apprenants, des rendez-vous individuels avec un accompagnateur, ou encore des échéances
fixes pour rendre certains travaux, un peu à la manière d'un cours traditionnel.

Une seconde évolution concerne la reconversion professionnelle, c'est-à-dire le fait de
changer complètement de métier au cours de sa carrière. Ce phénomène n'est pas nouveau en
soi, mais il s'est accéléré ces dernières années, notamment parce que certains métiers
disparaissent progressivement pendant que d'autres, liés justement au numérique,
connaissent une forte demande de main-d'œuvre. Des personnes qui travaillaient auparavant
dans des secteurs très différents se forment aujourd'hui à des métiers comme le
développement de sites web, l'analyse de données ou la cybersécurité, souvent via des
formations courtes et intensives, parfois financées par des organismes publics de l'emploi.
Ces formations accélérées permettent d'acquérir des compétences opérationnelles en
quelques mois plutôt qu'en plusieurs années, ce qui répond à un besoin réel du marché du
travail. Elles sont cependant critiquées par certains employeurs, qui estiment qu'une
formation aussi courte ne peut pas remplacer entièrement un parcours plus complet,
notamment pour les aspects les plus techniques ou théoriques d'un métier.

Enfin, le numérique a également transformé la manière dont les compétences acquises sont
validées et reconnues. À côté des diplômes traditionnels délivrés par les écoles et les
universités, des certifications spécifiques à un outil ou à une compétence précise se
sont multipliées, souvent délivrées directement par des entreprises technologiques ou des
plateformes de formation en ligne. Ces certifications ont l'avantage d'être rapides à
obtenir et directement liées à des compétences concrètes recherchées par les employeurs.
Elles ne bénéficient cependant pas toujours de la même reconnaissance qu'un diplôme
officiel, en particulier en dehors du secteur technologique, ce qui peut compliquer la
tâche d'une personne qui souhaiterait faire valoir ces compétences dans un tout autre
contexte professionnel.

Au total, le paysage de la formation professionnelle s'est nettement diversifié : il
coexiste aujourd'hui, à côté du modèle traditionnel, plusieurs formes d'apprentissage
rendues possibles par le numérique, chacune avec ses avantages propres et ses limites
réelles. Cette diversification élargit les possibilités pour les travailleurs qui
souhaitent évoluer ou se reconvertir, mais elle demande aussi, de leur part, une capacité
à s'orienter parmi des options nombreuses et de qualité inégale.
"""

CODING_DEBATE_DOCUMENT_TITLE = "Faut-il apprendre les bases de la programmation à l'école, dès le secondaire ?"

CODING_DEBATE_DOCUMENT_TEXT = """Faut-il apprendre les bases de la programmation à l'école, dès le secondaire ?

Dans plusieurs pays, des voix s'élèvent pour que la programmation informatique devienne
une matière enseignée à tous les élèves du secondaire, au même titre que les
mathématiques ou les langues, et non plus seulement dans les filières techniques ou
professionnelles qui y préparent directement. Les partisans de cette idée avancent que le
numérique est désormais présent dans la quasi-totalité des métiers, et qu'une
compréhension même basique de la logique de programmation aiderait les élèves à mieux
comprendre le monde dans lequel ils évoluent, un peu comme l'apprentissage des sciences
permet de comprendre des phénomènes naturels du quotidien.

D'autres estiment au contraire que le temps scolaire est déjà largement occupé, et
qu'ajouter une matière supplémentaire obligatoire se ferait nécessairement au détriment
d'autres apprentissages jugés tout aussi essentiels. Ils soulignent également que tous
les élèves ne se destinent pas à des métiers liés à l'informatique, et qu'il existe déjà
des filières spécifiques pour ceux qui souhaitent approfondir ce domaine — un peu comme
il existe des options artistiques ou sportives pour d'autres centres d'intérêt.

Un point de désaccord porte aussi sur ce que signifierait concrètement « apprendre à
programmer » à l'école : s'agit-il d'apprendre un langage de programmation précis, avec
le risque que ce langage devienne obsolète en quelques années, ou plutôt d'apprendre une
manière générale de décomposer un problème en étapes logiques, une compétence que
certains qualifient de « pensée computationnelle » et qu'ils jugent utile bien au-delà de
l'informatique elle-même.
"""
