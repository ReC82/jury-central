# Ticket #152 — Clarifier les consignes FSE et fournir le contexte des questions extraites de dossiers

- Ticket : https://github.com/ReC82/jury-central/issues/152 (P0, coordonné avec #149, #150, #151, #153, #129)
- Branche : `fix/152-consignes-fse-contexte` — PR #165 et #166 (21/10), **PR #190 (22/10, retour du propriétaire)**, toutes fusionnées dans `develop`
- **État réel : Installé — à tester**
- **SHA installé** : `bd633c1f16155e54bf2b3d49fe60d44c994c0a92` (PR #190 ; + commit de ce rapport, sans redémarrage)
- Synthèse du 22/10 : la question « D'après le document 3… » vue sans le document 1 venait
  d'un examen blanc **créé avant** la correction du 21/10 et repris ensuite (version 1 figée).
  Les nouvelles sessions servaient déjà la bonne version. Les anciennes sessions affichent
  maintenant elles aussi le document 1 avant le document 3, marqué « ajouté », et la
  correction reçoit les mêmes documents. La note budgétaire FSE16 n'est plus servie sans la
  proposition. Détail : section « Mise à jour du 22/10 » en fin de rapport.

## 1. Diagnostic (base réelle, lecture seule)

Les quatre captures viennent de la **même session** : l'examen blanc transversal FSE17 n° 70
(21/10, 19:29, en cours). Toutes les questions viennent de la banque partagée des cours FSE.

| Capture | Question servie | Objectif réel (cours source) | Défaut constaté |
|---|---|---|---|
| Q2/20 « Classe chaque réaction selon l'agent qui l'exprime » | FSE16, question 610 | FSE16 « Analyser une décision publique », étape 3 de la méthode : distinguer effets attendus et limites | L'auteur de chaque réaction est **déjà écrit** dans le document : l'exercice revenait à recopier une étiquette. « Association » était mise au même niveau que les catégories d'agents économiques. Le document 3 commence par « Cette aide… », mais l'aide (la proposition, document 1) n'était pas affichée. |
| Q3/20 « Remets dans l'ordre les étapes de la méthode face à un scénario en ligne » | FSE06, question 472 | Rappel de la méthode du cours FSE06 (« procède dans cet ordre »), **sans scénario** | Méthode et catégories non nommées (« catégories vues en cours »). La consigne parle d'un scénario absent. L'étape « vérifier qu'il ne s'agit pas d'une simple opinion » peut légitimement précéder la qualification : un autre ordre raisonnable était sanctionné. |
| Q7/20 « …quel agent reçoit le premier flux monétaire, et que fait-il ensuite de cet argent ? » | FSE15, question 597 | Lecture du circuit d'une aide publique (FSE15) | « Premier flux » sans point de départ ; deux actions dans une seule question ; le document parle d'un usage **partiel** de l'aide. Le renvoi « voir FSE02 » et les annotations-réponses du document étaient visibles sur la capture. **Déjà corrigé par #149**, installé le 21/10 à 23:54, après la capture : ils ne sont plus affichés. |
| Q8/20 « Associe maintenant ces trois autres situations… » | FSE09, question 512 | FSE09 « Qui décide de quoi ? » : associer une matière au niveau compétent | « Maintenant / autres » dépend de la question précédente du dossier, perdue en examen transversal. Le document servi **nommait l'acteur** de chaque situation (« Une région modifie… », « Une communauté adapte… », « Une commune décide… »), donc la réponse. |

Les réponses visibles sur les captures sont des réponses de l'élève. Elles n'ont pas été
traitées comme des corrigés. Le texte « C'est quoi cette question pas claire du tout. »
(Q7) est un retour sur la question, pas une erreur de connaissance.

**Défaut technique trouvé en reproduisant Q3 (entraînement et examen, pas le quiz) :**
une remise en ordre enregistrée sans choisir de position, ou avec la même position
partout, était triée par identifiant (e1, e2, e3…). Dans la banque, c'est presque toujours
l'ordre correct : **passer la question sans rien choisir donnait tous les points**, et
l'écran affichait ensuite 1/2/3/4 comme si l'élève les avait choisis. Le quiz contrôlait
déjà la saisie (#150) ; l'entraînement et l'examen non.

## 2. Changements réalisés

### Consignes et supports (24 questions corrigées + document FSE09)

**Remises en ordre de méthode (15 questions, FSE02 à FSE16).** J'ai relu chacune avec la
section « Méthode étape par étape » de son cours. Chacune devient un rappel annoncé :
« Rappel de méthode (cours FSE06 « Droits et comportements illicites en ligne », sans
document à analyser) : remets dans l'ordre les étapes pour qualifier un comportement en
ligne décrit dans un scénario. Chaque étape s'appuie sur le résultat de la précédente. »
Seules restent des étapes dont l'ordre est réellement contraint : chacune utilise le
résultat de la précédente. Les étapes interchangeables, facultatives (« si demandé ») ou
qui sont des mises en garde ont été regroupées dans l'étape qui les utilise. Le contenu
reste celui du cours.

| Cours | Avant | Après |
|---|---|---|
| FSE06 (capture Q3) | 4 étapes, dont « vérifier qu'il ne s'agit pas d'une simple opinion » placée arbitrairement en 3e position et « catégories vues en cours » | 3 étapes : relever les indices (répétition, menace, accusation sans preuve…) → qualifier (injure, calomnie, menace, cyberharcèlement, usurpation, intrusion, diffusion malveillante… **ou** simple critique/opinion) → justifier par les indices relevés |
| FSE02 | 6 étapes, dont 3 recherches d'indices interchangeables | 3 : repérer les indices de financement → en déduire le mode principal → le relier au comportement du média |
| FSE03 | 4, dont 3 analyses parallèles | 3 : relever les traces (volontaire/involontaire) → image donnée à voir vs identité réelle → conséquence concrète |
| FSE04 | 5, la valeur avant l'observation des comportements | 3 : décrire (valeur, norme, comportements) → expliquer par l'influence sociale → nuancer (responsabilité individuelle) |
| FSE05 | 5, dont 3 vérifications parallèles | 3 : préciser l'acte (prise de vue / diffusion) → appliquer les critères → conclure sur le consentement |
| FSE07 | 5, classement et comparaison interchangeables | 4 : fiabilité → confrontation à la lumière de la fiabilité → enjeux à partir des faits établis → conclusion |
| FSE08 | 4, dont une vérification finale | 3 : étendue de la matière → niveau compétent → nom de la norme selon le niveau |
| FSE09 | 4 | 3 : matière → niveau (en vérifiant un partage) → justification |
| FSE10 | 4, deux thèmes sans lien (bulletins, participation) | 3 : scrutin → règles de ce scrutin → application au cas |
| FSE11 | 4, valeur et priorité interchangeables | 3 : valeur et priorité → effets attendus → famille politique si demandé |
| FSE12 | 4, deux additions indépendantes en deux étapes | 4 : classer → les deux totaux → solde → nommer le solde |
| FSE13 | 4, dont « ne jamais calculer » présentée comme une étape | 3 : risque → trajet de l'argent → solidarité (« sans calculer de montant » passe dans la consigne) |
| FSE14 | 4, deux étapes alternatives présentées comme successives | 3 : organisme et branche → rôle → action concrète |
| FSE15 | 4, une étape indépendante | 3 : agents → flux réel/monétaire → effet d'une intervention de proche en proche |
| FSE16 | étapes déjà contraintes | consigne annoncée comme rappel, étapes inchangées |

Inchangées (vérifiées) : FSE01 « étapes d'une communication » (chronologie réelle), FSE01
« mail à Point-Repère » (scénario complet fourni), FSE07 « classement des documents par
fiabilité » (corrigé par #151).

**Autres consignes (9 questions).**

| Question | Avant | Après |
|---|---|---|
| FSE16 610 (capture Q2) | « Classe chaque réaction selon l'agent qui l'exprime » — catégories Ménage/Entreprise/Association | Rappel exact de la proposition (document 1), puis « classe chaque extrait selon qu'il exprime un effet attendu de cette aide ou une limite/un coût ». 5 extraits ; catégories « Effet attendu » / « Limite ou coût » ; documents 1 et 3 affichés |
| FSE16 611 et 613 (#151) | document 3 seul | document 1 + document 3 (« Cette aide » a son antécédent) |
| FSE15 597 (capture Q7) | « quel agent reçoit le premier flux monétaire… » | « D'après le document, l'État verse une aide publique à un média local. (a) Qui reçoit cette aide, et dans quelle catégorie d'agent économique le classes-tu (ménages, entreprises, État ou reste du monde) ? (b) Selon le document, à quoi ce bénéficiaire utilise-t-il une partie de cette aide ? » La grille accepte les formulations équivalentes (« média local », « entreprise de presse », « payer son personnel »…) et n'exige ni le mot « flux », ni que toute l'aide finance les salaires, ni les dépenses ultérieures des salariés |
| FSE09 512 (capture Q8) | « Associe maintenant ces trois autres situations… » | « Pour chacune des situations 5, 6 et 7, indique qui décide : le niveau fédéral, une Région ou une Communauté ? » Chaque élément décrit la situation (« Situation 6 — normes environnementales pour les entreprises situées en Wallonie ») |
| FSE09 511 | « Classe chaque situation… » (seules 4 sur 10) | « Classe les situations 1 à 4… », éléments décrits |
| FSE09 510 | « …(aide technique d'une province aux communes)… » : la réponse était dans la consigne | « …(aide technique aux communes d'un même territoire)… » |
| FSE09 504 | « Après avoir vu … en FSE08, … » | « Parmi ces matières, laquelle reste gérée au niveau fédéral… » |
| FSE09 515 | « situation 10 (coordination fédéral/régional) » : les niveaux attendus étaient dans la consigne | « situation 10 (réforme fiscale et règles sur le logement) : quelles compétences, à quels niveaux, pourquoi une coordination ? » |
| FSE06 470 | « Classe maintenant ces trois autres scénarios… » | « Classe les scénarios 6, 7 et 8 du document… » |
| FSE12 554 | « À présent, range chacune de ces lignes… » | « Range chaque ligne de dépense du tableau dans la bonne catégorie : fonctionnement, investissement ou transfert. » |

**Document FSE09 d'examen.** Le document « Dix situations — qui décide de quoi ? » servi en
entraînement, en examen et en quiz est une nouvelle version. Chaque situation y décrit la
matière et son étendue sans nommer qui décide : « Les aides financières destinées aux
entreprises qui s'installent en Wallonie sont modifiées », « Les programmes de cours des
écoles francophones sont adaptés », « Des militaires belges sont envoyés à l'étranger… ».
Les commentaires éditoriaux sur la réponse attendue (« exemple volontairement présenté
comme partagé… ») sont retirés. Les situations 8 et 10 gardent leurs indices (assurance
maladie-invalidité + matières personnalisables ; fiscalité générale + logement). Une mise en
page dédiée (fiches numérotées, #149) est enregistrée pour ce texte. Le **cours** FSE09
garde le texte d'origine pour ses exemples commentés. Les 14 questions FSE09 ont été
relues : les grilles restent valables avec ce texte.

### Remise en ordre : plus de fausse réussite (entraînement et examen)

- `app/v1/routes_sessions.py` : un ordre n'est enregistré que si chaque élément a une
  position distincte de 1 à n. Sinon la question reste **sans réponse** : 0 point si elle
  est soumise ainsi, aucune note attribuée par défaut. Les choix partiels sont conservés
  (`positions`) et réaffichés à la reprise. La navigation reste libre.
- `app/templates/v1_session_question.html` : état initial « Choisir une position », consigne
  « Attribue une position différente… Tant que chaque position n'est pas utilisée une seule
  fois, la question reste sans réponse », libellé accessible par étape. Quiz : même libellé
  initial (sa validation existait déjà).
- Ordre d'affichage : aucun nouvel algorithme. Les permutations persistées de #150 (jamais
  l'ordre de résolution affiché) s'appliquent aux nouvelles versions. Le glisser-déposer
  reste le périmètre de #153.

### Mécanique (même principe que #151)

- `app/v1/prompt_clarity.py` (nouveau) est la seule liste des corrections
  (`clarity_repairs`, avec pour chacune la raison de la correction) :
  - `apply_clarity` : une banque neuve crée directement le contenu corrigé (appelé dans
    chaque import FSE de `app/v1/fse_bank.py`) ;
  - `repair_prompt_clarity` : appelé par `app.seed`, il met à niveau la banque en place par
    une **nouvelle version** de question (au plus une par question) et une nouvelle version
    du document FSE09. Il est idempotent ;
  - `audit_prompt_clarity` : l'audit réutilisable (consignes « maintenant / à présent / ces
    trois autres / après avoir vu », « catégories vues en cours », méthode non annoncée,
    « cette aide/décision » sans antécédent affiché).
- `app/v1/document_references.py` (#151) : FSE16 611 et 613 montrent désormais les
  documents 1 et 3.
- `app/v1/fse09_content.py`, `app/v1/document_layouts.py` : version d'examen FSE09 et sa
  mise en page.

**Préservation des données :** aucune version existante n'est modifiée. Les sessions déjà
générées, dont la session 70, gardent les questions et le document servis, pour la
reprise, la correction, les résultats et l'export. Seules les nouvelles sessions servent les
versions corrigées. Aucune réponse, note ni session n'a été touchée ni recalculée.

**Anciennes sessions possiblement affectées par la fausse réussite (documentées, non
recalculées) :** 22 réponses de remise en ordre (entraînement/examen) sont enregistrées
exactement dans l'ordre des identifiants. Pour 12 d'entre elles, c'est l'ordre correct, notée
juste. Rien ne permet de distinguer un vrai choix de l'élève d'une question passée sans
choix. Sessions concernées : 1, 13, 15, 20, 21, 24, 27, 28, 44, 47, 48, 60 et 70 (en cours).

## 3. Tester

SHA installé : `9900ca141cc514f7e6254da651720a8612609ea2`. Le tirage est aléatoire : une question précise peut ne pas sortir
dans une session donnée. L'entraînement d'un cours tire dans sa banque complète (14
questions) ; démarrer deux entraînements suffit en général.

1. FSE16 : https://jury-central.lodylands.com/uaa/fse-fse16 → entraînement. La question
   « Le document 1 présente une proposition… effet attendu de cette aide ou une limite/un
   coût » affiche le document 1 (proposition) puis le document 3 (réactions).
2. FSE06 : https://jury-central.lodylands.com/uaa/fse-fse06 → la remise en ordre commence
   par « Rappel de méthode (cours FSE06 … sans document à analyser) » et propose 3 étapes.
   Chaque liste affiche « Choisir une position ».
3. Fausse réussite : sur une remise en ordre, cliquer « Suivant » sans rien choisir, puis
   revenir : la question est toujours vide (« Choisir une position »), pas 1/2/3/4. Une saisie
   partielle est conservée.
4. FSE15 : https://jury-central.lodylands.com/uaa/fse-fse15 → question « D'après le
   document, l'État verse une aide publique à un média local. (a) … (b) … ».
5. FSE09 : https://jury-central.lodylands.com/uaa/fse-fse09 → « Pour chacune des situations
   5, 6 et 7, indique qui décide… ». Le document affiché ne dit plus « Une région modifie… ».
6. Examen blanc transversal : https://jury-central.lodylands.com/uaa/fse-fse17 (mêmes
   questions, tirage sur l'ensemble des cours).

## 4. Vérifications

- `tests/test_ticket152_prompt_clarity.py` (13 tests) :
  - la banque FSE neuve passe l'audit sans alerte ;
  - chaque correction correspond à exactement une question ;
  - les 15 méthodes sont annoncées comme rappels, avec le cours nommé ;
  - les quatre cas des captures sont corrigés ;
  - une banque « d'avant #152 » est mise à niveau par 29 nouvelles versions et 1 document,
    puis 0 au second passage ;
  - une session existante garde la version et le document servis ;
  - le contenu réparé est identique à celui d'une banque neuve ;
  - remise en ordre : vide, positions en double ou saisie incomplète donnent 0 point et
    « sans réponse », choix partiels conservés ; une saisie complète est enregistrée par
    positions explicites et notée juste seulement si elle est correcte.
- Tests #149 et #151 adaptés aux deux changements voulus (document 1 affiché avec le
  document 3 ; une mise en page de plus) : 80 passés.
- Suite complète (seed et routes de session touchés) : 1898 passés et 2 échecs du contrôle anti-quasi-doublons. Les consignes FSE09 « situations 1 à 4 » et « 5, 6 et 7 » étaient trop proches ; la seconde a été reformulée et les fichiers de test concernés (#99, #102, #149, #151, #152) relancés : 189 passés.
- `ruff check` : aucune nouvelle erreur sur les fichiers modifiés.
- Essai sur une **copie** de la base réelle (/tmp), seed lancé dans un processus neuf :
  - 29 questions mises à niveau, 1 document d'examen, 2 renvois #151 (611, 613) ;
  - second passage : 0 ;
  - audit #152 vide sur les 230 questions FSE actives ;
  - audit #151 inchangé : il signale seulement les 10 questions de l'ancien pilote C01, déjà
    connues ;
  - la session 70 sert toujours ses versions d'origine ;
  - compteurs inchangés (18 utilisateurs, 71 sessions, 584 réponses).
- Sur le site : sauvegarde de la base avant installation, seed : 29 questions clarifiées, 1 document d'examen, 2 renvois #151 (611, 613), 0 non résolue. Les deux services sont actifs, `/health` répond OK en local et en public, `/uaa/fse-fse06`, `fse-fse09`, `fse-fse15`, `fse-fse16` et `fse-fse17` répondent en HTTP 200. Les compteurs utilisateurs/sessions/réponses sont inchangés (18/71/584). La session 70 sert toujours ses versions d'origine (610, 472, 597, 512).
- Non vérifié : rendu dans un vrai navigateur (pas de navigateur sur le serveur). Les tests
  HTTP vérifient le HTML produit.

## 5. Choix techniques faits seul

- **FSE16 610, objectif « analyser » plutôt que « reconnaître l'auteur »** : l'auteur est
  écrit en toutes lettres dans le document. Le ticket proposait cette option et l'étape 3 de
  la méthode FSE16 vise ce travail (effets attendus / limites). L'auteur reste indiqué devant
  chaque extrait pour situer la citation, sans être une catégorie à classer.
- **« Limite ou coût » en une seule catégorie** : la question 613 du même cours et sa grille
  emploient déjà « limite/coût ». Le coût de capacité n'est pas une « limite » au sens strict
  du cours (condition nécessaire), d'où le regroupement explicite.
- **FSE15 597 en une seule question à deux parties (a)/(b)** plutôt que deux questions : une
  nouvelle question dans une banque déjà importée aurait changé les tirages et les
  statistiques de la question. La difficulté déclarée reste « moyen ».
- **Remises en ordre** : je garde le type « ordering » (rappel de méthode assumé) plutôt
  qu'une analyse de cas, mais avec des étapes à dépendance réelle. Le texte des cours n'est
  pas modifié : chaque étape regroupe des étapes du cours dans le même ordre.
- **Document FSE09** : nouvelle version réservée aux questions, le cours garde l'original.
  « En Wallonie » / « écoles francophones » donnent l'étendue de la matière (territoire,
  communauté linguistique), ce que la méthode FSE08/FSE09 demande d'analyser, sans nommer le
  niveau. Les faits restent ceux du document d'origine : aucune compétence nouvelle.
- **Pas de recalcul** des anciennes remises en ordre : impossible de distinguer un choix réel
  d'une absence de choix. Elles sont listées ci-dessus.
- **Pas d'appel IA** : toutes les reformulations sont écrites à la main.

## 6. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 7. Éléments restant à réaliser / suites proposées

- **#153** : glisser-déposer des remises en ordre. Ce ticket a corrigé les consignes, l'état
  initial neutre et la validation serveur, pas l'interaction.
- **Hors périmètre, signalé** :
  - FSE16 609 (court/long terme) est une lecture directe du document 2, déclarée
    « moyen » ;
  - FSE07 487 et FSE14 587 citent un prérequis (« notion vue en FSE04 / FSE13 »), accepté
    par le ticket.
  Pas d'autre consigne trop facile repérée.
- Les 10 questions de l'ancien pilote Français C01 (décision 1 de #151) ne sont pas
  concernées.


---

## Mise à jour du 22/10 — retour du propriétaire (examen blanc, question 1/20 sans document 1)

### Cause établie (base réelle, lecture seule, sans donnée personnelle)

| Élément | Constat |
|---|---|
| Session concernée | Examen blanc FSE17 n° 70 (périmètre `fse17_transversal`, 20 questions, **en cours**, 8 réponses enregistrées). C'est la seule session qui a servi une version des questions 610/611. C'est aussi la session des captures du 21/10. |
| Date de création | **21/10/2026 19:29 UTC** |
| Question 1/20 | Question 611, **version 1** (version 611) : consigne « D'après le document 3, quelle limite… » (texte exact du retour), document 61 (document 3) seul |
| Correction #152 | Version 2 le 21/10 à 22:45 UTC, version 3 (documents 59 puis 61, soit document 1 puis document 3) le 21/10 à 23:18 UTC, **après** la création de la session |
| Nouvelles sessions | Une seule fonction crée les questions servies (`add_session_question`) et elle prend toujours la version courante. Les sessions 71 à 77 (quiz, entraînement, renforcement) n'ont servi aucune ancienne version de 610/611. |

Cause : **ancienne session reprise, qui conserve la version 1** (règle de versionnement :
une session garde la version qu'elle a servie). Ce n'est ni une nouvelle session qui aurait
servi une ancienne version, ni un rendu qui ignorerait les documents supplémentaires. Le
même cas touchait la question 2/20 (610 v1). La correction aurait aussi reçu uniquement le
document 3, comme l'élève.

### Changements (PR #190)

1. **Anciennes sessions : contexte restauré explicitement, rien modifié en base.**
   `session_question_document_ids` (`app/v1/session_service.py`) : si la version courante
   de la **même** question est du même type, conserve **tous** les documents de la version
   figée et en ajoute seulement d'autres, alors la question affiche les documents dans l'ordre
   de la version courante (document 1 puis document 3). Les documents ajoutés portent le badge
   « ajouté », sous un message « Contexte complété : … ta réponse et la question restent
   celles de ta session, et la correction tiendra compte des mêmes documents ». Dans tous les
   autres cas (document retiré ou remplacé, type changé), seuls les documents figés sont
   utilisés : deux versions incompatibles ne sont jamais mélangées. La même liste sert à
   l'écran de question (entraînement, examen, quiz, renforcement), à la **correction IA**
   (`_document_contexts_for`), aux résultats et à l'export (`_build_results_rows`, badge
   « ajouté depuis le début de la session »). La session 70 garde sa version 611 et ses
   réponses. Les notes et les versions ne sont pas touchées.
2. **Audit « cette aide / la subvention / la proposition » (dossiers FSE).** Nouvelle règle
   dans `audit_prompt_clarity` : un document affiché qui parle de « la subvention », de « la
   proposition », de « cette mesure »… doit être accompagné d'un texte qui l'**introduit**
   (« propose de… », « une aide… »). Répéter le mot ne suffit plus. Sur la base réelle, elle
   a repéré **2 questions** : FSE16 609 et 614, où la note budgétaire (document 2, qui commence
   par « La subvention serait financée… ») était servie seule. Elles montrent maintenant le
   **document 1 (proposition) puis le document 2**, avec une consigne qui le dit. La règle est
   limitée aux dossiers FSE (un texte Français complet introduit autrement sa décision).
3. **FSE09 (cas #129, permanence)** : « Et pour ces trois autres demandes… » (dépendait de la
   question précédente) devient « D'après les fiches de la permanence, quel niveau de pouvoir
   est compétent pour les demandes 1, 6 et 7 ? ».
4. Mise à jour par **nouvelles versions** (seed idempotent sur le site : 3 questions, 0
   document, 0 non résolue). Les sessions existantes sont intactes.

Le document 1 affiché est le texte source existant : un gouvernement régional fictif propose
de subventionner une partie du prix des abonnements de transport collectif (bus, train
régional) pour les travailleurs à revenus modestes, financée par le budget régional, avec ses
deux objectifs. Rien n'a été inventé ou paraphrasé. Ce document ne contient pas la réponse
attendue (la capacité du réseau).

### SHA installé et liens pour tester

SHA : `bd633c1f16155e54bf2b3d49fe60d44c994c0a92`.

1. **Ta session n° 70** (Mes entraînements → examen blanc FSE17 en cours, ou
   https://jury-central.lodylands.com/sessions/70?q=1) : la question 1/20 affiche
   « Contexte complété », puis DOCUMENT 1 (badge « ajouté »), puis DOCUMENT 3. La question 2
   s'affiche de la même façon. Tes 8 réponses sont toujours là.
2. **Nouvel examen blanc** : https://jury-central.lodylands.com/uaa/fse-fse17 (la question
   apparaît selon le tirage, sans message « ajouté » puisque la version est déjà à jour).
3. **FSE16** : https://jury-central.lodylands.com/uaa/fse-fse16 (questions sur la note
   budgétaire : document 1 puis document 2).
4. FSE09 : https://jury-central.lodylands.com/uaa/fse-fse09.

### Vérifications effectuées

- Tests : 8 nouveaux tests (`tests/test_ticket152_context_restored.py`) : ancienne session
  avec document 1 puis 3 et badge, correction et résultats avec les mêmes documents, page
  HTML, aucun mélange si un document est remplacé, nouvelles sessions FSE17/FSE16 toujours en
  version courante avec document 1 en tête, note budgétaire, règle d'audit, FSE09. Les tests
  #152 existants ont été adaptés : les cas #129 sont importés comme en production, 31 versions
  au lieu de 29.
- **Suite complète, une fois** (moteur de sessions et de correction touché) : 2147 passés,
  1 échec (`test_ticket94_french_fr06_10` : la nouvelle règle d'audit signalait des textes
  Français complets). La règle a été limitée aux dossiers FSE, puis les tests concernés ont
  été relancés : 52 passés (#152, #151, Français FR06-10). ruff propre sur les fichiers
  modifiés.
- **Copie de la base réelle** (`/tmp`, jamais la base du site) : réparation idempotente
  (3 puis 0), audit FSE vide. La session 70 donne les documents [59, 61], ajouté [59], et la
  correction reçoit bien le document 59. Sur **40 nouvelles sessions** (30 examens blancs
  FSE17 à difficultés variées et 10 FSE16), **0 version obsolète** servie ; 609, 610, 611,
  613, 614 et 615 montrent toujours le document 1 en premier.
- **Parcours navigateur connecté** (Chromium headless, code de la PR sur la copie de la base,
  compte local de vérification créé dans la copie uniquement) :
  - nouvel examen blanc FSE17, question 13/20 = 611 → « DOCUMENT 1 | Proposition — carte de
    transport collectif subventionnée », puis « DOCUMENT 3 | Réactions des groupes concernés »,
    sans badge ;
  - copie exacte des versions figées de la session 70 (q=1 et q=2) → message « Contexte
    complété », 1 badge « ajouté », DOCUMENT 1 puis DOCUMENT 3, consigne d'origine.
- **Après installation** : services actifs, `/health` OK en local et en public, pages
  FSE16, FSE17 et FSE09 en 200. Compteurs utilisateurs/sessions/réponses 18/77/631
  inchangés. Session 70 relue en lecture seule avec le code installé : documents [59, 61],
  ajouté [59], correction avec le document 59. Sauvegarde :
  `~/.local/state/jury-central-orch/backups/jury_central-pre-ticket152-20261022-123021.db`.
- Non fait : parcours navigateur sur le site public avec ton compte (je n'utilise pas tes
  identifiants et je n'ai pas créé de compte sur la base réelle). Je n'ai pas non plus
  vérifié le quiz et le renforcement dans un navigateur : ils utilisent la même fonction
  d'affichage, couverte par les tests.

### Choix techniques faits seul

- **Pas de copie ni de modification de la session 70.** Le contexte est restauré à
  l'affichage, signalé explicitement, et repris à l'identique par la correction. Une
  « reprise » qui recréerait la session aurait perdu tes réponses ou changé les versions.
- Restauration **limitée aux ajouts de documents**, jamais à un changement de consigne ou de
  barème : la consigne et la correction attendue restent celles de la version servie. Pour
  610 v1 (« classe chaque réaction selon l'agent »), l'ancienne consigne reste affichée, avec
  le document 1 en plus.
- Le seed a aussi créé 52 blocs de cours déjà présents dans `develop` (tickets précédents),
  sans lien avec #152 (opération idempotente).
- Les signalements de l'audit sur les textes Français FR02 (« Cette décision » après « a fait
  installer ») sont de faux positifs connus, exclus comme avant.

### Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire. Option possible si tu la préfères : au lieu
d'afficher le contexte dans l'ancienne session, proposer un bouton « recommencer cet examen
avec les versions à jour » (nouvelle session, l'ancienne restant consultable). Ma
recommandation est de garder l'affichage actuel, qui ne fait perdre aucune réponse.

### Reste à faire

Rien pour ce retour. Hors périmètre, signalé seulement : l'audit des renvois documentaires
signale encore des questions de l'ancien pilote C01 (« d'après le texte » sans document), qui
existaient déjà avant ce ticket.
