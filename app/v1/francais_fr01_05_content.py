"""Textes support — Français FR01→FR05 (ticket #94, PHASE A).

Statut explicite : **PROVISIONAL_TECHNICAL_SAMPLE**, comme `app.v1.francais_content`
(ticket #47/#77/#79) — textes ORIGINAUX rédigés pour ce ticket (jamais un examen CESS
officiel, jamais un texte protégé par le droit d'auteur), réalistes et suffisamment
développés pour permettre de vraies questions de lecture/inférence/argumentation, niveau
CESS Professionnel.

Chaque texte devient une `SourceDocumentVersion` distincte (`app.v1.francais_fr01_05_bank`)
— jamais dupliqué dans le `content_json` d'une question (registre #40, § 6/§ 8 du ticket
#94 : AUCUNE question ne peut dire « D'après le texte » sans un document réellement
rattaché et accessible à l'élève ET à l'IA — AI_SOURCE_IDS == STUDENT_SOURCE_IDS)."""

# =============================================================================================
# FR01 — Comprendre une consigne d'examen
# =============================================================================================

FR01_LEARNING_A_TITLE = "Le covoiturage dans l'entreprise"
FR01_LEARNING_A_TEXT = """Depuis deux ans, l'entreprise Delvaux Logistique encourage ses employés à pratiquer le \
covoiturage pour se rendre sur le site de production. Un panneau d'affichage dans le hall \
d'entrée permet à chacun de proposer ou de chercher un trajet, et une application interne \
met en relation les conducteurs et les passagers selon leur quartier d'habitation.

Les responsables des ressources humaines expliquent que cette initiative répond à trois \
objectifs. D'abord, réduire le nombre de voitures sur le parking, devenu trop petit depuis \
l'embauche de nouveaux ouvriers. Ensuite, diminuer les frais de déplacement pour les \
employés qui habitent loin du site, certains faisant plus de quarante kilomètres chaque \
jour. Enfin, limiter les émissions de gaz à effet de serre liées aux trajets domicile-travail, \
un engagement pris publiquement par la direction lors de son dernier rapport annuel.

Après un an de fonctionnement, le bilan reste toutefois partagé. Une trentaine d'employés \
utilisent régulièrement le covoiturage, mais beaucoup renoncent après quelques semaines, \
invoquant des horaires trop différents ou la difficulté de s'organiser avec des collègues \
qu'ils connaissent peu. La direction envisage désormais d'ajouter une place de parking \
réservée aux covoitureurs, plus proche de l'entrée, pour rendre l'initiative plus attractive."""

FR01_LEARNING_B_TITLE = "L'apprentissage en alternance"
FR01_LEARNING_B_TEXT = """L'alternance permet à un jeune de partager son temps entre un centre de formation et une \
entreprise, généralement à raison de deux ou trois jours par semaine dans chaque lieu. \
Ce mode d'apprentissage existe depuis longtemps dans les métiers manuels, mais il se \
développe aujourd'hui dans des secteurs plus variés, comme la vente, l'informatique ou la \
gestion administrative.

Pour l'entreprise, l'intérêt est de former un futur employé selon ses propres méthodes de \
travail, sans attendre qu'il ait terminé ses études. Pour l'apprenti, l'avantage est de \
percevoir une rémunération pendant sa formation et d'acquérir une expérience concrète, \
souvent plus valorisée par les recruteurs qu'un diplôme obtenu uniquement en classe.

Ce système comporte cependant des exigences. L'apprenti doit s'adapter rapidement à un \
rythme professionnel, parfois plus soutenu que celui de l'école, tout en continuant à \
suivre des cours théoriques et à réussir ses évaluations. Certains employeurs signalent \
aussi que l'encadrement d'un jeune alternant demande du temps, un collègue expérimenté \
devant régulièrement l'accompagner sur le terrain. Malgré ces contraintes, la majorité des \
entreprises qui accueillent des alternants renouvellent l'expérience l'année suivante."""

FR01_D1_TITLE = "Document 1 — Le télétravail vu par la direction"
FR01_D1_TEXT = """Pour la direction de l'entreprise Berteau & Fils, le télétravail est d'abord une question \
d'organisation. Deux jours par semaine, les employés des services administratifs peuvent \
travailler depuis leur domicile, à condition d'être joignables aux heures habituelles et de \
participer aux réunions par visioconférence. La direction met en avant une baisse des \
retards liés aux embouteillages et une meilleure concentration sur les tâches nécessitant \
peu d'interruptions, comme la rédaction de rapports ou la comptabilité. Elle rappelle \
toutefois que cette souplesse reste un choix de l'entreprise, révisable si la productivité \
venait à baisser, et non un droit acquis pour les employés."""

FR01_D2_TITLE = "Document 2 — Le télétravail vu par les employés"
FR01_D2_TEXT = """Du côté des employés de Berteau & Fils, l'avis sur le télétravail est plus partagé. \
Plusieurs apprécient de gagner du temps de trajet et de mieux organiser leur vie de \
famille les jours de télétravail. D'autres regrettent en revanche la perte de contact avec \
leurs collègues, expliquant que certaines questions se règlent plus vite en se levant pour \
aller voir quelqu'un plutôt qu'en attendant une réponse par message. Un délégué du \
personnel note aussi que les employés les plus jeunes, récemment engagés, se sentent \
parfois isolés lorsqu'ils travaillent depuis chez eux, faute d'avoir encore développé de \
vraies relations avec leurs collègues sur place."""

FR01_MINITEST_A_TITLE = "Le tri des déchets sur le lieu de travail"
FR01_MINITEST_A_TEXT = """Depuis la rénovation de ses locaux, l'entreprise Corentin Distribution a installé trois \
poubelles de couleurs différentes dans chaque espace de pause : une pour le papier et le \
carton, une pour les emballages recyclables, et une dernière pour les déchets non \
recyclables. Des affiches expliquent, avec des pictogrammes simples, ce que chaque \
poubelle doit contenir.

Six mois après cette installation, un responsable du service qualité a mené un contrôle. \
Il constate que le tri fonctionne bien pour le papier, presque toujours correctement séparé, \
mais que de nombreux emballages recyclables se retrouvent encore dans la poubelle des \
déchets non recyclables, notamment les gobelets en plastique utilisés à la machine à café. \
Il propose d'ajouter, juste au-dessus de cette poubelle, une affiche plus visible rappelant \
que les gobelets doivent être jetés avec les emballages recyclables, et non avec le reste. \
Il suggère également d'organiser une courte présentation du tri lors de l'accueil des \
nouveaux employés, pour que les bonnes habitudes se prennent dès le premier jour."""

FR01_MINITEST_B_TITLE = "La pause de midi dans les grandes entreprises"
FR01_MINITEST_B_TEXT = """Dans beaucoup de grandes entreprises, la pause de midi ne dure plus une heure complète \
comme autrefois, mais souvent une demi-heure, parfois même moins pour les employés qui \
doivent respecter des horaires de production stricts. Cette évolution s'explique en partie \
par la volonté de terminer la journée de travail plus tôt, une demande fréquente des \
employés ayant des enfants à récupérer à l'école.

Certains syndicats s'inquiètent toutefois des effets d'une pause trop courte, en particulier \
sur la qualité de l'alimentation. Manger rapidement, souvent devant un écran, ne permet \
pas toujours de faire une vraie coupure dans la journée, ce qui peut augmenter la fatigue \
en fin d'après-midi. Plusieurs entreprises ont réagi en aménageant des espaces de \
restauration plus agréables, avec des micro-ondes en nombre suffisant et des tables \
disposées loin des postes de travail, pour encourager les employés à vraiment sortir de \
leur environnement professionnel pendant cette courte pause."""


# =============================================================================================
# FR02 — Lire et comprendre un document
# =============================================================================================

FR02_ARTICLE_TITLE = "Article — Une nouvelle ligne de bus pour la zone industrielle"
FR02_ARTICLE_TEXT = """La société de transport public régionale a annoncé la création d'une nouvelle ligne de \
bus desservant la zone industrielle de Hennuyères, où travaillent plus de deux mille \
personnes réparties dans une vingtaine d'entreprises. Jusqu'à présent, seuls les employés \
disposant d'une voiture pouvaient rejoindre facilement ce site, situé à l'écart des axes \
principaux de transport en commun.

La nouvelle ligne, numérotée 47, circulera toutes les vingt minutes aux heures de pointe et \
reliera la gare centrale au cœur de la zone industrielle en moins de vingt-cinq minutes. \
Plusieurs entreprises du site avaient demandé cette liaison depuis des années, expliquant \
qu'elle facilitera le recrutement de personnes ne possédant pas de permis de conduire, \
notamment des jeunes en début de carrière.

La mise en service est prévue pour la rentrée de septembre. Un abonnement mensuel à tarif \
réduit sera proposé aux employés de la zone, en partenariat avec les entreprises \
concernées, qui prendront en charge une partie du coût. La société de transport précise \
que la fréquentation de cette ligne sera évaluée après six mois, afin de décider si des \
bus supplémentaires doivent être ajoutés en cas de forte demande."""

FR02_INFO_TITLE = "Texte informatif — Le fonctionnement d'une caisse enregistreuse moderne"
FR02_INFO_TEXT = """Une caisse enregistreuse moderne ne se contente plus d'additionner des prix. Elle est \
reliée à un système informatique central qui gère en temps réel les stocks du magasin. \
Chaque article scanné à la caisse est automatiquement retiré du stock affiché aux \
gestionnaires, ce qui permet de déclencher une commande de réapprovisionnement lorsque \
la quantité disponible descend sous un seuil défini à l'avance.

Ce système enregistre également des informations utiles pour analyser les habitudes des \
clients : les heures de forte affluence, les produits souvent achetés ensemble, ou encore \
les moyens de paiement les plus utilisés. Ces données aident les responsables de magasin à \
adapter les horaires du personnel ou l'organisation des rayons.

La caisse moderne intègre enfin des fonctions de sécurité. Chaque opération est associée à \
l'identifiant de l'employé qui l'a réalisée, ce qui permet de retrouver facilement l'origine \
d'une erreur de caisse ou d'une remise appliquée par erreur. En cas de panne du système \
informatique central, la plupart des caisses conservent malgré tout une fonction de secours \
limitée, permettant d'encaisser les clients en espèces le temps que la panne soit résolue."""

FR02_LETTER_TITLE = "Lettre professionnelle — Demande de congé"
FR02_LETTER_TEXT = """Madame Kowalski,

Je me permets de vous écrire afin de solliciter un congé de deux semaines, du 14 au 25 \
juillet, pour accompagner ma famille lors d'un déménagement prévu de longue date dans une \
autre région.

Je suis consciente que cette période correspond à un moment chargé pour notre service, en \
raison de l'inventaire annuel. C'est pourquoi je propose de former dès à présent ma \
collègue Aurélie aux tâches que je gère habituellement pendant l'inventaire, afin qu'elle \
puisse assurer la continuité du travail pendant mon absence. Je resterai par ailleurs \
joignable par téléphone en cas de question urgente durant la première semaine de mon congé.

Je vous remercie d'avance de l'attention que vous porterez à cette demande et reste à votre \
disposition pour en discuter si nécessaire.

Cordialement,
Nadia Ferreira"""

FR02_MINITEST_TITLE = "L'installation de bornes de recharge électrique sur le parking du personnel"
FR02_MINITEST_TEXT = """Depuis le mois de mars, l'entreprise Vandenberghe Industries a fait installer six bornes de \
recharge pour véhicules électriques sur le parking réservé au personnel. Cette décision \
répond à une demande croissante des employés : l'an dernier, seuls trois d'entre eux \
possédaient une voiture électrique, mais ce nombre est monté à dix-sept en l'espace de \
quelques mois, encouragé par une prime régionale à l'achat de véhicules propres.

Les bornes fonctionnent selon un système de réservation en ligne, accessible depuis \
l'application interne de l'entreprise. Chaque employé peut réserver un créneau de deux \
heures maximum, afin que les six bornes puissent être partagées équitablement tout au long \
de la journée. Un panneau d'affichage près de l'entrée rappelle également qu'il est \
interdit de laisser un véhicule branché plus longtemps que le créneau réservé, sous peine \
d'un rappel à l'ordre du service des ressources humaines.

Le coût de l'électricité consommée est actuellement pris en charge par l'entreprise, \
présentée comme un avantage supplémentaire pour les employés ayant fait le choix d'un \
véhicule plus respectueux de l'environnement. La direction précise toutefois que cette \
gratuité sera réévaluée dans un an, en fonction du nombre de véhicules électriques \
supplémentaires qui viendraient s'ajouter, afin de vérifier que le coût total reste \
raisonnable pour l'entreprise.

Certains employés ne possédant pas de véhicule électrique ont exprimé une légère \
frustration face à cet avantage, qu'ils jugent réservé à une minorité. Le comité \
d'entreprise a répondu en rappelant que d'autres avantages, comme la prime de transport en \
commun, bénéficient de leur côté aux employés utilisant le bus ou le train, et que \
l'ensemble de ces mesures vise à encourager des déplacements plus respectueux de \
l'environnement, quel que soit le mode de transport choisi."""


# =============================================================================================
# FR03 — Implicite, inférences et justification
# =============================================================================================

FR03_TEXT1_TITLE = "Le premier jour de Karim"
FR03_TEXT1_TEXT = """Karim arriva sur le parking vingt minutes avant l'heure indiquée sur son contrat. Il resta \
assis dans sa voiture, relisant une troisième fois le plan des bâtiments qu'on lui avait \
envoyé par courriel, avant de se décider à sortir. Dans le hall d'accueil, il tendit sa \
carte d'identité à la réceptionniste d'une main légèrement tremblante et attendit, debout, \
que quelqu'un vienne le chercher, alors qu'un canapé était pourtant disponible à quelques \
mètres de lui.

Lorsque son responsable d'équipe, Thomas, arriva enfin avec dix minutes de retard, Karim se \
leva si vite qu'il faillit renverser le porte-documents posé sur ses genoux. Il serra la \
main tendue avec une poignée un peu trop ferme, répétant deux fois « enchanté » avant même \
que Thomas n'ait fini de se présenter. Pendant la visite des ateliers, il posa de nombreuses \
questions sur les procédures de sécurité, notant certaines réponses sur un petit carnet \
qu'il avait apporté, alors que Thomas lui assurait que tout serait expliqué plus en détail \
le lendemain, lors de la formation officielle.

À la pause de midi, Karim resta un moment devant la porte de la cafétéria, observant les \
groupes déjà installés, avant de choisir une table où était assise une seule personne, \
plutôt que de s'approcher d'un groupe plus animé installé un peu plus loin."""

FR03_TEXT2_TITLE = "Le rapport du responsable qualité"
FR03_TEXT2_TEXT = """Le responsable qualité de l'usine Meurisse a rédigé son rapport mensuel dans des termes \
mesurés, comme il le fait habituellement. Il note que « la ligne de production numéro 3 a \
connu quelques arrêts supplémentaires ce mois-ci, sans que cela affecte significativement \
les délais de livraison annoncés aux clients ». Il précise également que « l'équipe de \
maintenance a été sollicitée à plusieurs reprises, parfois en dehors des horaires \
habituels, pour intervenir sur cette même ligne ».

Plus loin dans le rapport, il indique que deux commandes ont dû être partiellement \
réalisées sur la ligne numéro 1, habituellement réservée à un autre type de produit, « afin \
de respecter malgré tout les délais promis à certains clients prioritaires ». Il conclut en \
recommandant « un contrôle approfondi de la ligne 3 dès que le planning de production le \
permettra, idéalement avant la fin du trimestre », tout en ajoutant qu'aucune commande n'a \
finalement été perdue ni annulée ce mois-ci.

Le rapport se termine par une phrase que le directeur a soulignée en réunion : « la \
situation reste sous contrôle, mais elle mériterait de ne pas se prolonger sur plusieurs \
mois sans intervention technique. »"""

FR03_MINITEST_TITLE = "La démission de Sandra"
FR03_MINITEST_TEXT = """Sandra travaillait comme vendeuse dans le même magasin de vêtements depuis six ans lorsqu'elle \
annonça sa démission à sa responsable, un mardi matin, juste après l'ouverture. Elle avait \
rédigé sa lettre à la main la veille au soir, alors qu'elle affirmait habituellement tout \
préférer taper à l'ordinateur, même les messages les plus courts.

Dans les jours qui suivirent l'annonce, plusieurs collègues remarquèrent qu'elle proposait \
systématiquement de fermer le magasin le soir, une tâche qu'elle avait pourtant longtemps \
évitée en raison des trajets de bus qui se faisaient plus rares après dix-neuf heures. Elle \
prit également le temps, entre deux clients, de réexpliquer en détail à la nouvelle \
employée la procédure de gestion des retours, alors que ce n'était pas son rôle habituel.

Sa responsable, surprise par cette démission qu'elle jugeait soudaine, chercha à en \
comprendre les raisons lors d'un entretien. Sandra expliqua simplement qu'elle « avait \
besoin de changer d'air », sans donner davantage de détails sur sa destination ni sur le \
métier qu'elle envisageait ensuite. Elle ajouta seulement, avec un sourire, qu'elle \
emporterait avec elle « quelques bonnes habitudes prises ici », en particulier sa manière \
d'organiser le rayon des nouveautés chaque lundi matin — une méthode qu'elle avait mis des \
mois à perfectionner et qu'elle prit soin d'écrire, point par point, sur une feuille laissée \
dans le classeur de l'équipe avant son dernier jour de travail."""


# =============================================================================================
# FR04 — Écrire correctement et organiser ses idées
# =============================================================================================

FR04_IDEAS_JUMBLE_TITLE = "Idées en vrac — Proposer un aménagement d'horaires"
FR04_IDEAS_JUMBLE_TEXT = """- je voudrais commencer une heure plus tôt le matin
- comme ça je finirais aussi une heure plus tôt le soir
- mon fils termine l'école à 16h et personne ne peut aller le chercher avant 17h en ce moment
- je fais ce travail depuis trois ans et je n'ai jamais eu de retard
- je peux proposer une période d'essai d'un mois avant que ce soit définitif
- il faudrait que mes horaires restent compatibles avec les réunions d'équipe du lundi matin
- ma responsable directe est déjà d'accord sur le principe, il ne manque que l'accord des ressources humaines"""

FR04_DISORGANIZED_TITLE = "Paragraphes désorganisés — Compte-rendu d'une panne de machine"
FR04_DISORGANIZED_TEXT = """[Paragraphe A] Le technicien de maintenance est intervenu vers 14h30, après avoir été \
prévenu par téléphone. Il a identifié un problème au niveau du moteur d'entraînement, \
probablement dû à une surchauffe liée à un manque d'entretien régulier.

[Paragraphe B] La machine numéro 4 s'est arrêtée brutalement vers 13h15, en pleine \
production, sans qu'aucun signal d'alerte n'ait été observé au préalable par les employés \
présents sur la ligne.

[Paragraphe C] La machine a pu être remise en service à 17h, après remplacement de la \
pièce défectueuse. Il est recommandé de programmer un entretien préventif chaque trimestre \
afin d'éviter qu'un incident similaire ne se reproduise.

[Paragraphe D] La production a donc été interrompue pendant près de quatre heures, ce qui a \
retardé la livraison d'une commande initialement prévue pour le lendemain matin."""

FR04_MINITEST_TITLE = "Mini-test — Rédiger un courriel de réclamation à un fournisseur"
FR04_MINITEST_TEXT = """Situation : Tu travailles dans le service des achats d'une entreprise. Le fournisseur \
Materio SA vous a livré, la semaine dernière, une commande de cent boîtes de vis \
métalliques destinées à la production. En ouvrant les boîtes ce matin, ton équipe a \
constaté que trente d'entre elles contenaient des vis d'un diamètre différent de celui \
commandé, rendant leur utilisation impossible sur la ligne de montage.

Destinataire : le service commercial de Materio SA, avec qui l'entreprise travaille \
régulièrement depuis plusieurs années.

Intention : obtenir un remplacement rapide des trente boîtes non conformes, sans remettre \
en cause l'ensemble de la relation commerciale.

Genre attendu : un courriel professionnel, poli mais ferme, comportant une formule \
d'ouverture, une explication claire du problème, une demande précise, et une formule de \
politesse finale.

Informations à organiser dans le courriel :
- référence de la commande : BC-4471, livrée le 12 du mois
- trente boîtes sur cent contiennent des vis de diamètre 4 mm au lieu de 5 mm
- besoin d'un remplacement avant la fin de la semaine pour ne pas retarder la production
- proposition de retourner les boîtes non conformes dès réception du remplacement"""


# =============================================================================================
# FR05 — Corriger et améliorer un texte
# =============================================================================================

FR05_FLAWED1_TITLE = "Texte imparfait 1 — Note de service"
FR05_FLAWED1_TEXT = """A tout le personnel du deuxième étage. Suite a plusieurs remarques du personnel nous \
rappelons que la salle de pause doit être laisser propre après chaques utilisation. \
Plusieurs employés on constatés que de la vaisselle sale rester parfois plusieurs jours \
dans le évier. Nous vous demandons donc de laver votre vaisselle immédiatement après \
utilisation, ou de la ramener chez vous si vous ne pouvez pas la laver tout de suite. \
Cette note concerne également le frigo commun, ou des aliments périmer on été retrouvé la \
semaine dernière. Un grand nettoyage du frigo aura lieu vendredi, tout aliments non \
identifié sera jeté. Merci de votre compréhension."""

FR05_FLAWED1_CORRECTED = """À tout le personnel du deuxième étage. Suite à plusieurs remarques du personnel, nous \
rappelons que la salle de pause doit être laissée propre après chaque utilisation. \
Plusieurs employés ont constaté que de la vaisselle sale reste parfois plusieurs jours dans \
l'évier. Nous vous demandons donc de laver votre vaisselle immédiatement après utilisation, \
ou de la ramener chez vous si vous ne pouvez pas la laver tout de suite. Cette note \
concerne également le frigo commun, où des aliments périmés ont été retrouvés la semaine \
dernière. Un grand nettoyage du frigo aura lieu vendredi ; tout aliment non identifié sera \
jeté. Merci de votre compréhension."""

FR05_FLAWED2_TITLE = "Texte imparfait 2 — Avis sur un logiciel interne"
FR05_FLAWED2_TEXT = """Le nouveau logiciel il est vraiment pas pratique, moi je trouve. Déjà il met un temps fou \
à charger le matin, après il plante souvent quand on essaye d'exporter un fichier, et en \
plus de ça les icones son toutes petite et on comprend rien du tout à quoi elles servent. \
Le logiciel d'avant était mieu je trouve, même si il était un peu vieux il marchait bien au \
moins. Franchement sa serait bien qu'on nous redemande notre avis avant de changer de \
logiciel la prochaine fois, parce que là personne il été content dans le service."""

FR05_FLAWED2_CORRECTED = """Le nouveau logiciel n'est vraiment pas pratique, à mon avis. Il met déjà un temps fou à \
charger le matin ; ensuite, il plante souvent lorsqu'on essaie d'exporter un fichier ; et, \
de plus, les icônes sont toutes petites, si bien qu'on ne comprend pas à quoi elles \
servent. Le logiciel précédent était meilleur, je trouve : même s'il était un peu ancien, \
il fonctionnait bien. Il serait donc bienvenu qu'on nous redemande notre avis avant de \
changer de logiciel la prochaine fois, car personne n'a été satisfait dans le service."""

FR05_MINITEST_TITLE = "Mini-test — Corriger un message destiné à un client"
FR05_MINITEST_TEXT = """Bonjour Madame, je vous écrit pour vous informez que votre commande a était retardé a \
cause d'un problème avec notre fournisseur. Nous somme vraiment désolé pour ce contretemps \
independant de notre volonté. Votre colis devrai maintenant arrivé dans les 3 a 5 jours \
ouvrable. Si vous avez besoin d'aide supplémentaire, n'hésiter pas a nous recontacter, on \
reste disponible pour vous aidez. Encore désolé pour la gene occasionner."""
