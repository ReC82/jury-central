# Ticket #151 — Références documentaires ambiguës : « document 3 » non identifié dans l'examen

- Ticket : https://github.com/ReC82/jury-central/issues/151 (P0, coordonné avec #149, #129, #137)
- Branche : `fix/151-references-documentaires` — PR #162 + correctif PR #163 (fusionnées dans `develop`)
- **État réel : Installé — à tester**
- **SHA installé** : `766be0da00de16629464e57eada1c677659144e5` (+ commit de ce rapport, sans redémarrage)

## 1. Diagnostic (base réelle, lecture seule)

Les deux captures viennent de la **même session** : l'examen blanc FSE17 n° 70 (périmètre
transversal), créé le 21/10 à 19:29.

| Capture | Question servie | Document relié | Constat |
|---|---|---|---|
| Q1/20 « D'après le document 3… association environnementale » | FSE16, question 611 (v1, `short_answer`) | « Réactions fictives de trois groupes concernés » (version 61) | **Le bon document était bien affiché.** C'est réellement le document 3 du dossier FSE16 (1 = proposition, 2 = note budgétaire, 3 = réactions), comme dans le cours FSE16. Le numéro n'était pas affiché : l'écran mettait « Document de référence ». #149, installé à 23:54 le même soir (après la capture), affiche désormais « Document 3 — Réactions des groupes concernés ». Les trois réactions sont des **témoignages** d'un même document, pas trois documents. |
| Q4/20 « Le forum affirme… La note de direction mentionne 24 élèves… » | FSE07, question 485 (v1, `short_answer`) | uniquement le forum (version 46) | **Vrai renvoi orphelin.** La note de direction existe bien dans le dossier FSE07 (version 44, signée et datée, « 24 élèves »), mais la question ne pouvait relier qu'**un seul** document : seul le type `source_comparison` savait en montrer plusieurs. |

**Cause réelle :** les questions extraites d'un dossier multidocument ne pouvaient relier
qu'un document. Toute consigne qui compare ou cite deux ou trois documents du dossier n'en
montrait qu'un, à l'élève comme au correcteur (qui reçoit exactement les mêmes documents,
ticket #77). En plus, résultats et export affichaient toujours « Document de
référence » : le numéro cité dans la consigne n'y apparaissait pas.

## 2. Audit des références

J'ai audité les **621 questions actives** de la base réelle (FSE, AMPCR, Français) :
recherche automatique des renvois (« document N », « les deux/trois documents »,
« d'après le texte/tableau/schéma », « la note de direction », « le forum »…), puis relecture
manuelle des dossiers multidocuments FSE01–FSE04, FSE07, FSE10, FSE11, FSE14, FSE15 et
FSE16. Les hits AMPCR (« dossier partagé », « tableau » de calcul…) sont des faux positifs :
ce ne sont pas des renvois à un document.

- **30 questions** contiennent un renvoi documentaire détectable automatiquement.
- **11 questions corrigées** (toutes FSE) :

| Cours | Question (id réel) | Problème | Correction |
|---|---|---|---|
| FSE02 | 412 « Classe chacun de ces trois médias… » | aucun média montré | les 3 pages (Hebdo, Flash Infos, RCW) |
| FSE02 | 419 « Compare L'Hebdo du Littoral et Le Flash Infos… » | seul l'Hebdo montré | Hebdo + Flash Infos |
| FSE04 | 447 « …en t'appuyant sur les deux documents » | 1 document sur 2 | publication + témoignage de Karim |
| FSE07 | 481 « …moins fiable que la note de direction ? » | note absente | note + forum |
| FSE07 | 485 **(capture Q4)** « Le forum affirme… La note de direction… » | note absente | note + forum |
| FSE07 | 488 « …la note de direction précise… » | note absente | note + forum |
| FSE07 | 489 conclusion « …d'un document fiable pour chacun » (barème : note + groupe-classe) | 1 document sur 3 | les 3 documents du dossier |
| FSE07 | 484 remise en ordre « Classe ces trois documents… » | renvoi à des documents non montrés (type sans document) | consigne : « Classe les trois documents du dossier, décrits ci-dessous… » (les éléments décrivent déjà chaque document) |
| FSE16 | 611 **(capture Q1)** « D'après le document 3… » | numéro non visible avant #149 | consigne : « D'après le document 3 (réactions des groupes concernés)… » |
| FSE16 | 613 « …réaction de l'entreprise de transport (document 3) » | idem | « (document 3, réactions des groupes concernés) » |
| FSE16 | 615 conclusion « …fondée sur les trois documents fournis » | 1 document sur 3 | documents 1, 2 et 3 montrés ; « (documents 1, 2 et 3) » |

- **Vérifiés résolvables, sans changement** : les autres renvois numérotés FSE16
  (« document 1 », « note budgétaire (document 2) » affichés sous ce numéro), les
  « situation N »/« extrait N »/« affirmation X du tableau » (FSE05, FSE08, FSE09, FSE11, FSE13 :
  fiche numérotée dans le document relié), les « d'après le tableau/schéma » (FSE10, FSE12,
  FSE14, FSE15), FR01 (comparaison Document 1/Document 2 déjà reliée), FR05.
- **Non résolus (hors navigation)** : 10 questions de l'ancien pilote **Français C01**
  (« D'après le texte… », « Compare les deux documents fournis ») n'ont aucun texte relié en
  base. Elles ont été importées avant que ces types sachent porter un document, et la banque
  actuelle du code les relie bien. Ce cours est masqué des listes
  (`hidden_from_listing`, remplacé par FR01–FR05) mais reste accessible par URL directe.
  Voir la décision 1.

Après réparation (essai sur une copie de la base réelle), l'audit automatique ne signale
plus que ces 10 questions C01.

## 3. Changements réalisés

- `app/v1/question_types.py` : `short_answer`, `long_answer`, `classification` et
  `document_analysis` acceptent un champ optionnel `source_document_version_ids`. Il liste
  tous les documents du dossier à montrer, dans l'ordre du dossier, document principal
  inclus. Ce champ est validé (identifiants uniques, principal inclus) et exposé dans le
  payload public. Le moteur l'utilisait déjà (`_referenced_document_ids`) : **l'élève
  (entraînement, examen, quiz) et le correcteur voient la même liste**.
- `app/v1/routes_sessions.py` : résultats et export Markdown utilisent le libellé de la
  session (« Document 3 : Réactions des groupes concernés ») au lieu de « Document de
  référence ».
- `app/v1/session_service.py` : le correcteur reçoit le numéro réel dans le titre du
  document (« Document 3 — Réactions fictives… »), pour qu'un barème « s'appuie sur le
  document 3 » soit relié au bon texte.
- `app/v1/document_references.py` (nouveau) :
  - `dossier_repairs()` : la liste unique des 11 corrections ;
  - `repair_dossier_references()` : met à niveau une banque déjà importée en créant une
    **nouvelle version** de question. La réparation est idempotente et identifie les
    documents par titre exact, dans le dossier du cours concerné. Elle est appelée par
    `app.seed` ;
  - `audit_document_references()` : l'audit réutilisable.
- `app/v1/fse_bank.py` : une banque neuve crée directement le contenu corrigé.
- `docs/current_state.md` mis à jour.

**Préservation :** aucune version existante n'est modifiée. Les sessions déjà générées, y
compris la session 70 si elle est reprise, gardent la version servie, pour la navigation,
la reprise, la correction, les résultats et l'export. Seules les nouvelles sessions servent
les versions corrigées. Aucun document n'a été créé ni modifié : la note de direction, le
forum, etc. sont les versions existantes. Aucune réponse ni session utilisateur n'a été
touchée.

## 4. Tester

SHA installé : `766be0da00de16629464e57eada1c677659144e5`.

1. Examen blanc FSE07 ou entraînement FSE07 :
   https://jury-central.lodylands.com/uaa/fse-fse07 → démarrer. Si la question « Le forum
   affirme que Lucas… » sort, la **note de direction** (Athénée du Parc, 24 élèves) et le
   **forum** sont affichés l'un sous l'autre.
2. FSE16 : https://jury-central.lodylands.com/uaa/fse-fse16 → la question « D'après le
   document 3 (réactions des groupes concernés)… » affiche « Document 3 — Réactions des
   groupes concernés ». La conclusion finale montre les documents 1, 2 et 3.
3. Examen blanc transversal FSE17 : https://jury-central.lodylands.com/uaa/fse-fse17 (mêmes
   questions, tirage aléatoire).
4. Après soumission : dans les résultats, « Revoir le document — Document 3 : Réactions des
   groupes concernés ». L'export `.md` affiche le même libellé.

Le tirage étant aléatoire, une question précise peut ne pas sortir dans une session donnée.

## 5. Vérifications

- `tests/test_ticket151_document_references.py` (11 tests) : banque FSE neuve sans renvoi
  orphelin ; chaque correction est identique au contenu de la banque neuve ; cas des deux
  captures ; réparation par nouvelle version sans toucher la version servie, idempotente ;
  correcteur = mêmes documents, avec numéro ; page de session avec note + forum ; résultats
  et export avec « Document 3 » ; validation du champ.
- Tests voisins (#77, #79, #97, #98, #100, #101, #149) : 243 passés au total avec les tests
  #151.
- Suite complète (moteur partagé touché) : 1887 passés.
- `ruff check` : aucune nouvelle erreur (45 avant / 45 après sur `app/`, nouveaux fichiers
  propres).
- Essai sur une **copie** de la base réelle (dans /tmp) : 11 questions réparées, second
  passage 0, audit après réparation limité aux 10 questions C01.
- Sur le site après installation : les deux services sont actifs, `/health` répond OK en local et en public, `/uaa/fse-fse07`, `/uaa/fse-fse16` et `/uaa/fse-fse17` répondent en HTTP 200. Le seed a réparé 11 questions, toutes en version 2, avec 0 non résolue. La session 70 sert toujours les versions d'origine (611 et 485). Les compteurs utilisateurs/sessions/réponses sont inchangés (18/71/584). Les blocs de cours restent au nombre de 315 : le seed remplace comme d'habitude des blocs FSE existants, sous les mêmes titres.
- Non vérifié : rendu visuel dans un vrai navigateur. Les tests HTTP vérifient le HTML
  produit.

**Incident d'installation (sans impact) :** à la première installation (SHA `1766c14`, PR
#162), `python -m app.seed` a échoué avant son commit, avec l'erreur « type de question
inconnu ». Le registre des types n'était pas chargé dans ce contexte. Aucune écriture en
base, services non redémarrés : le site est resté sur l'ancien processus, en bonne santé.
J'ai livré le correctif (import du registre, PR #163) après un seed lancé dans un processus
neuf sur une copie de la base réelle, puis réinstallé. Sauvegardes avant chaque essai dans
`~/.local/state/jury-central-orch/backups/jury_central-pre-ticket151-*.db`.

## 6. Choix techniques faits seul

- **Pas de renumérotation inventée** : les documents sans numéro réel (FSE07, FSE02,
  FSE04) gardent leur titre (« Note de la direction — … », « Publication anonyme sur un
  forum… »). Le titre suffit à les distinguer et correspond aux mots de la consigne.
- **FSE16 garde « document 3 »**, puisque c'est la numérotation réelle du dossier et du
  cours. La consigne nomme en plus le document pour rester claire en examen transversal.
- **Remise en ordre FSE07** : ce type ne porte pas de document. J'ai reformulé la consigne
  (les éléments décrivent déjà chaque document) plutôt que d'ajouter un document à ce type.
- **QCM** : les QCM FSE qui citent un élément de dossier (« situation 9 (aide technique
  d'une province…) », « l'affirmation “24 élèves” ») sont auto-suffisants, l'élément est
  décrit dans l'énoncé. Je les ai laissés tels quels.
- **Nouvelle version plutôt que modification** : c'est la règle du modèle
  (`add_question_version`), et elle garantit la stabilité des anciennes sessions.

## 7. Décisions demandées au propriétaire

1. **Ancien pilote Français C01** (masqué, accessible par URL) : 10 questions sans texte
   relié en base. Options : (a) archiver ces questions C01 ; (b) les relier au texte prévu
   par la banque actuelle (nouvelle version, comme ici) ; (c) ne rien faire tant que C01
   reste masqué. **Recommandation : (b)**, petit correctif sans risque, à traiter dans un
   ticket dédié.

## 8. Reste à faire

- Décision C01 ci-dessus.
- #129 (nouveaux supports FSE) et #137 (quiz) : tout nouveau dossier doit utiliser
  `source_document_version_ids` dès qu'une consigne cite plusieurs documents. L'audit
  (`audit_document_references`) peut servir de contrôle.
