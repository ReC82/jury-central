"""Contenu de cours — FSE17 « Révision générale et méthode d'examen » (ticket #101, cahier
des charges détaillé).

Structure propre à FSE17 (différente du schéma en 10 points des autres cours, conformément
au prompt pédagogique spécifique du ticket #101) : 1. Carte des deux thèmes — 2. Tableau
notion → savoir-faire → exemple (FSE01→FSE16) — 3. Lexique transversal — 4. Confusions
fréquentes — 5. Fiches méthode (citer/identifier/expliquer/justifier) — 6. Répartition
indicative des 120 minutes (conseil pédagogique, non officiel) — 7. Douze exercices
transversaux — 8. Corrigés séparés des douze exercices — 9. Les trois examens blancs
(accès, non officiel).

FSE17 ne réapprend AUCUNE notion nouvelle (ticket #101 : « reprendre exclusivement
FSE01-FSE16, sans ajouter de nouvelle matière ») et n'a pas sa propre banque de questions :
son entraînement/examen réutilise la banque transversale FSE01-FSE16 via
`app.v1.session_service._start_fse_transversal_session` (voir ce module et
`app.v1.fse17_transversal` pour le mécanisme, strictement banque — jamais de génération IA,
le volume existant de 16 cours × 14 questions suffit très largement)."""


def fse17_course_markdown() -> str:
    return """# FSE17 — Révision générale et méthode d'examen

**Ce cours ne contient aucune notion nouvelle.** Il synthétise FSE01 à FSE16 et propose une \
méthode pour aborder l'épreuve. Les trois « examens blancs » (§ 9) sont des **simulations \
pédagogiques du Jury, non officielles** : ils t'aident à t'entraîner dans des conditions \
proches de l'examen, mais ne remplacent jamais l'épreuve réelle ni ses consignes officielles.

## 1. Carte des deux thèmes

Le programme CESS Professionnel couvre deux thèmes officiels :

**Thème « Interactions médiatiques » (Médias)** — FSE01 à FSE07 :
- FSE01 — Communiquer : le schéma de communication
- FSE02 — Les médias et leurs financements
- FSE03 — Identités, traces numériques et appartenance
- FSE04 — Normes, valeurs et influence sociale
- FSE05 — Image, vie privée et données personnelles
- FSE06 — Droits et comportements illicites en ligne
- FSE07 — Analyser un dossier médiatique

**Thème « Le citoyen et l'État » (Citoyen)** — FSE08 à FSE16 :
- FSE08 — La Belgique : État et niveaux de pouvoir
- FSE09 — Qui décide de quoi ?
- FSE10 — Élections et participation citoyenne
- FSE11 — Partis politiques et choix argumenté
- FSE12 — Le budget de l'État
- FSE13 — La sécurité sociale : rôle et financement
- FSE14 — La sécurité sociale : organismes et enjeux
- FSE15 — Le circuit économique et les interventions de l'État
- FSE16 — Analyser une décision publique

## 2. Tableau notion → ce que je dois savoir faire → exemple

| Cours | Ce que je dois savoir faire | Exemple |
|---|---|---|
| FSE01 | Identifier émetteur/récepteur/message/code/canal/contexte, distinguer canal et code | Un mail professionnel : code = langue écrite, canal = messagerie |
| FSE02 | Identifier le mode de financement d'un média et son effet sur son contenu | Un média gratuit financé par la publicité recherche l'audience |
| FSE03 | Distinguer trace volontaire/involontaire, identité réelle/image donnée | Une ancienne publication qui ressurgit lors d'une candidature |
| FSE04 | Distinguer norme/valeur/comportement, limites de l'influence sociale | Un groupe qui banalise un comportement, sans effacer la responsabilité individuelle |
| FSE05 | Distinguer prise de vue/diffusion, sujet principal/personne accessoire | Publier une photo prise en privé dans un groupe public |
| FSE06 | Reconnaître un comportement en ligne à partir d'indices, sans citer d'article de loi | Répétition de messages hostiles malgré une demande d'arrêt = cyberharcèlement |
| FSE07 | Distinguer fait/interprétation/opinion, vérifier auteur/date/contexte/preuves | Une publication anonyme non datée, moins fiable qu'une note signée |
| FSE08 | Situer une compétence au bon niveau, distinguer loi/décret/ordonnance | Bruxelles adopte des ordonnances, pas des décrets |
| FSE09 | Reconnaître qu'une matière peut être partagée entre plusieurs niveaux | La santé dépend du fédéral (remboursement) et des Communautés |
| FSE10 | Distinguer vote valable/blanc/nul, vérifier obligation par scrutin et région | Vote non obligatoire aux communales en Flandre depuis 2024 |
| FSE11 | Associer un extrait à une famille politique, comparer sans juger | PS = famille socialiste ; comparer deux propositions par valeurs/priorités |
| FSE12 | Classer recettes/dépenses, calculer le solde budgétaire | IPP = recette fiscale (jamais calculée) ; solde = recettes − dépenses |
| FSE13 | Identifier le risque couvert, distinguer financement/gestion/versement | Perte d'emploi → risque chômage |
| FSE14 | Associer organisme et rôle, situer les allocations familiales régionalisées | ONSS = collecteur ; FAMIWAL = intermédiaire payeur en Wallonie |
| FSE15 | Distinguer flux réel/monétaire, tracer une intervention publique | Une aide à une entreprise se propage ensuite en salaires |
| FSE16 | Analyser une décision publique : agents, effets, limites, court/long terme | Une aide au transport dépend de la capacité réelle du réseau |

## 3. Lexique transversal

- **Émetteur/récepteur/message/code/canal/contexte** (FSE01) — éléments du schéma de \
communication.
- **Interactivité, financement** (FSE02) — caractéristiques d'un média.
- **Trace numérique, réputation** (FSE03) — identité en ligne.
- **Norme, valeur, influence sociale, socialisation** (FSE04) — fonctionnement d'un groupe.
- **Droit à l'image, consentement, finalité** (FSE05) — protection de l'image et des données.
- **Cyberharcèlement, usurpation d'identité, liberté d'expression** (FSE06) — comportements \
en ligne.
- **Fait, interprétation, opinion, fiabilité** (FSE07) — analyse documentaire.
- **Monarchie constitutionnelle, séparation des pouvoirs, Région, Communauté** (FSE08-09) — \
organisation de l'État.
- **Scrutin proportionnel, vote blanc/nul, procuration** (FSE10) — élections.
- **Famille politique, axe gauche-centre-droite** (FSE11) — partis politiques.
- **Recette fiscale/parafiscale/non fiscale, déficit, dette** (FSE12) — budget de l'État.
- **Solidarité, mutualisation des risques, assurance sociale** (FSE13) — sécurité sociale.
- **Collecteur, gestionnaire, intermédiaire payeur** (FSE14) — organismes de sécurité \
sociale.
- **Flux réel, flux monétaire, agent économique** (FSE15) — circuit économique.
- **Effet attendu, limite, conséquence indirecte** (FSE16) — analyse d'une décision publique.

## 4. Confusions fréquentes entre cours

- **Norme sociale (FSE04) et règle juridique (FSE06)** : une norme sociale est une attente \
de comportement dans un groupe ; un comportement illicite en ligne dépasse les limites de la \
liberté d'expression, indépendamment des normes d'un groupe précis.
- **Vie privée/image (FSE05) et données personnelles collectées en ligne (FSE06)** : le \
droit à l'image porte sur une photo/vidéo d'une personne ; le traitement de données sans \
base valable porte plus largement sur toute information identifiante.
- **Région (territoire, FSE08-09) et Communauté (personnes/langue/culture, FSE08-09)** : ne \
jamais les confondre, même si leurs noms se ressemblent.
- **Recette parafiscale (cotisations, FSE12) et recette fiscale (impôts, dont l'IPP, \
FSE12)** : deux origines différentes de recettes pour l'État.
- **Financement (FSE13) et versement (FSE13-14)** : le financement est l'origine de \
l'argent ; le versement est le paiement concret à la personne, parfois via un intermédiaire \
différent du gestionnaire.
- **Flux réel et flux monétaire (FSE15)** : un bien/service/travail (réel) n'est pas la même \
chose que le paiement qui l'accompagne (monétaire).

## 5. Fiches méthode — verbes d'examen

**CITER** : reproduire exactement un élément présent dans un document fourni (une phrase, un \
chiffre, un nom), sans le reformuler ni l'interpréter.

**IDENTIFIER** : nommer précisément un élément (un niveau de pouvoir, un risque couvert, un \
type de recette...) à partir d'indices présents dans l'énoncé ou le document, sans décrire \
ni justifier davantage.

**EXPLIQUER** : décrire le mécanisme ou le raisonnement qui relie une cause à une \
conséquence (ex. pourquoi un déficit augmente la dette), en plusieurs étapes si nécessaire.

**JUSTIFIER** : appuyer une réponse par un élément précis du document ou de la théorie \
(« parce que... », en citant ou paraphrasant la source de ta réponse), jamais par une simple \
affirmation sans preuve.

## 6. Répartition indicative des 120 minutes (conseil pédagogique, non officiel)

Cette répartition est une suggestion pour t'entraîner, **pas une consigne officielle de \
l'épreuve réelle** :
- Environ 45 minutes pour les questions courtes (identification, classement, définitions).
- Environ 45 minutes pour les questions de justification courte et d'analyse de cas.
- Environ 20 minutes pour l'analyse de document/dossier la plus complète.
- Environ 10 minutes de relecture finale.

## 7. Douze exercices transversaux

<details>
<summary>Exercice 1 (FSE01/FSE07) — Identifie le code et le canal d'un message professionnel \
envoyé par SMS.</summary>
Essaie avant de consulter le corrigé en section 8.
</details>

<details>
<summary>Exercice 2 (FSE02/FSE04) — Explique comment le financement publicitaire d'un média \
peut influencer les normes de contenu qu'il publie.</summary>
Essaie avant de consulter le corrigé en section 8.
</details>

<details>
<summary>Exercice 3 (FSE03/FSE05) — Une personne publie une photo ancienne d'elle-même sur \
un réseau public : identifie la trace numérique ET la question de droit à l'image \
concernées.</summary>
Essaie avant de consulter le corrigé en section 8.
</details>

<details>
<summary>Exercice 4 (FSE04/FSE06) — Distingue une norme de groupe qui banalise un \
comportement et un comportement qui franchit la limite de la liberté d'expression.</summary>
Essaie avant de consulter le corrigé en section 8.
</details>

<details>
<summary>Exercice 5 (FSE07) — Classe trois affirmations d'un dossier fictif en fait, \
interprétation ou opinion.</summary>
Essaie avant de consulter le corrigé en section 8.
</details>

<details>
<summary>Exercice 6 (FSE08/FSE09) — Identifie le niveau de pouvoir compétent pour une \
décision sur l'enseignement, et explique pourquoi la santé peut dépendre de plusieurs \
niveaux.</summary>
Essaie avant de consulter le corrigé en section 8.
</details>

<details>
<summary>Exercice 7 (FSE10) — Un bulletin comporte deux cases cochées : vote valable, blanc \
ou nul ? Justifie.</summary>
Essaie avant de consulter le corrigé en section 8.
</details>

<details>
<summary>Exercice 8 (FSE11) — Associe un court extrait à une famille politique, en précisant \
la limite de l'axe gauche-centre-droite.</summary>
Essaie avant de consulter le corrigé en section 8.
</details>

<details>
<summary>Exercice 9 (FSE12) — Calcule un solde budgétaire à partir de recettes et dépenses \
fictives, et nomme le résultat.</summary>
Essaie avant de consulter le corrigé en section 8.
</details>

<details>
<summary>Exercice 10 (FSE13/FSE14) — Identifie le risque couvert et l'organisme gestionnaire \
pour une personne en incapacité de travail après un accident survenu au travail.</summary>
Essaie avant de consulter le corrigé en section 8.
</details>

<details>
<summary>Exercice 11 (FSE15) — Trace les flux réels et monétaires d'un échange entre un \
ménage et une entreprise.</summary>
Essaie avant de consulter le corrigé en section 8.
</details>

<details>
<summary>Exercice 12 (FSE16) — Identifie un effet attendu et une limite dans un court extrait \
sur une décision publique fictive.</summary>
Essaie avant de consulter le corrigé en section 8.
</details>

## 8. Corrigés des douze exercices (séparés, à consulter après avoir essayé)

<details>
<summary>Corrigé 1</summary>
Dans un SMS professionnel, le code est la langue écrite (souvent familière/abrégée) et le \
canal est le réseau de messagerie texte du téléphone — à distinguer, comme vu en FSE01 : le \
canal est le support de transmission, le code est le système de signes utilisé.
</details>

<details>
<summary>Corrigé 2</summary>
Un média financé par la publicité recherche l'audience la plus large possible (FSE02) ; \
cette recherche d'audience peut l'inciter à privilégier des contenus qui suivent les normes \
valorisées par son public (FSE04, ex. humour, sensationnalisme), plutôt que des contenus \
moins immédiatement attractifs.
</details>

<details>
<summary>Corrigé 3</summary>
La photo ancienne est une trace numérique volontaire (FSE03, publiée par la personne \
elle-même). La republier ou la laisser visible pose une question de droit à l'image (FSE05) \
si la personne y est sujet principal : un consentement renouvelé peut être nécessaire selon \
le contexte de diffusion.
</details>

<details>
<summary>Corrigé 4</summary>
Une norme de groupe qui banalise un comportement (FSE04, ex. « tout le monde filme ») \
explique une tendance fréquente, mais n'efface jamais la responsabilité individuelle ; un \
comportement qui franchit la limite de la liberté d'expression (FSE06, ex. une accusation \
non étayée) reste problématique indépendamment de la norme du groupe qui l'entoure.
</details>

<details>
<summary>Corrigé 5</summary>
Une donnée datée et vérifiable (ex. une date de publication confirmée) est un fait ; une \
explication proposée à partir de cette donnée (ex. « cela montre que... ») est une \
interprétation ; un jugement personnel (ex. « c'est regrettable ») est une opinion — voir \
FSE07, § 2.
</details>

<details>
<summary>Corrigé 6</summary>
L'enseignement relève de la Communauté (matière liée aux personnes/langue/culture, FSE08- \
09). La santé peut dépendre de plusieurs niveaux parce que le remboursement des soins \
(assurance maladie-invalidité) est fédéral, alors que certains aspects de la santé \
(prévention, aide aux personnes) sont des matières personnalisables gérées par les \
Communautés — un partage explicite, jamais une réponse à un seul niveau (FSE09).
</details>

<details>
<summary>Corrigé 7</summary>
Deux cases cochées pour deux listes différentes rendent impossible de connaître l'intention \
de l'électeur pour une seule liste : c'est un vote nul (FSE10), à distinguer du vote blanc \
(bulletin totalement vierge).
</details>

<details>
<summary>Corrigé 8</summary>
L'association à une famille politique se fait à partir des éléments explicites du texte \
(valeurs, priorités citées), voir FSE11. L'axe gauche-centre-droite reste un repère \
simplifié : un même parti peut combiner des positions qui ne s'y laissent pas toutes \
ranger clairement.
</details>

<details>
<summary>Corrigé 9</summary>
Le solde budgétaire se calcule par total des recettes − total des dépenses (FSE12). Si le \
résultat est négatif, il se nomme un déficit ; s'il est positif, un excédent — toujours \
détailler l'addition de chaque côté avant de soustraire.
</details>

<details>
<summary>Corrigé 10</summary>
Un accident survenu au travail relève du risque « accident du travail » (FSE13), géré par \
FEDRIS (FSE14) — à distinguer d'une maladie ordinaire, qui relèverait de l'INAMI.
</details>

<details>
<summary>Corrigé 11</summary>
Entre un ménage et une entreprise : le travail fourni par le ménage est un flux réel ; le \
salaire versé par l'entreprise est le flux monétaire correspondant (FSE15). Si le ménage \
achète ensuite un bien à cette entreprise, le bien livré est un flux réel et le paiement est \
le flux monétaire correspondant, en sens inverse.
</details>

<details>
<summary>Corrigé 12</summary>
Un effet attendu est la conséquence visée par la décision (ex. réduire un problème \
identifié) ; une limite est une condition nécessaire pour que cet effet se réalise \
réellement (FSE16) — toujours vérifier si le document mentionne une telle condition avant de \
présenter l'effet comme acquis.
</details>

## 9. Les trois examens blancs (accès, non officiel)

Ce cours donne accès, via les boutons « S'entraîner » et « S'évaluer » ci-dessous, à une \
**révision transversale** qui tire ses questions de l'ensemble des cours FSE01 à FSE16 \
(jamais de FSE17 lui-même, qui n'a pas de banque propre). En choisissant la difficulté au \
démarrage de l'évaluation, tu accèdes aux **trois examens blancs progressifs** :

- **Facile** : questions d'identification et de définition.
- **Moyen** : mélange de classements, de justifications courtes et de cas à analyser.
- **Difficile** : inclut les analyses de document et justifications longues les plus \
proches de l'autonomie attendue à l'examen réel. Ces questions restent plafonnées à 3 par \
examen, quel que soit le nombre de cours couverts : c'est une règle générale de la \
plateforme (jamais plus de 3 réponses longues/sémantiques dans une même session), qui \
évite qu'un examen entier ne soit composé uniquement de longues analyses. La progression \
vers le niveau difficile se traduit donc par la présence de ces 3 analyses exigeantes \
(absentes des niveaux facile et moyen), pas par un remplacement intégral du contenu.

**Ce sont des simulations pédagogiques du Jury, non officielles** : elles couvrent les deux \
thèmes du programme (Médias et Citoyen), avec une correction, des points partiels et un \
corrigé détaillé pour chaque question, exactement comme pour les autres cours FSE — mais \
elles ne remplacent jamais l'épreuve réelle, son barème officiel ni ses consignes propres.
"""
