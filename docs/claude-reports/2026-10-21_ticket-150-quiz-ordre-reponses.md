# Ticket #150 — Quiz : sélectionner systématiquement la première réponse permet de réussir

- Ticket : https://github.com/ReC82/jury-central/issues/150 (P0, lié à #137 et #80)
- Branche : `fix/150-quiz-melange-reponses` — PR #160 (fusionnée dans `develop`)
- **État réel : Installé — à tester**
- **SHA installé** : `36793cb73ee2b2ab232782663b1bfff498579eba` (+ commit de ce rapport, sans redémarrage)

## 1. Cause constatée

Bug reproduit sur la base réelle (lecture seule) :

- **Les banques rédigées à la main stockent la bonne réponse en premier.** Sur les 146 QCM
  actifs, la bonne réponse est en première position pour **107** : FSE 45/49, AMPCR MC04,
  MC11, MC31, MC37 100 %, MC38 35/54, Français 2/4.
- **L'écran affichait les options dans l'ordre de la banque.** Le mélange livré par #80
  (`shuffle_multiple_choice_options`) ne s'applique qu'aux contenus **importés** (éditorial
  legacy) ou **générés par l'IA**. Les banques FSE/AMPCR/Français créées directement par
  `create_question` le contournent. Aucun mélange n'était fait à l'affichage.
- **La seule partie de quiz terminée sur le site** contenait 10 QCM, tous avec la bonne
  réponse en premier, et la première option a été choisie 10 fois sur 10 : c'est exactement
  le constat du ticket.

Les quatre hypothèses du ticket :

| # | Hypothèse | Constat |
|---|---|---|
| 1 | Bonne réponse toujours en premier (banque, rendu sans mélange) | **Oui : c'est la cause** |
| 2 | Erreur de mapping après permutation (index affiché ≠ identifiant) | Non : le formulaire envoie l'`option_id` et aucune permutation n'existait |
| 3 | Correction qui accepte la 1re option ou n'importe quelle réponse | Non : correction serveur par identifiant, égalité exacte des ensembles (`_mc_check` / `correct_locally`) |
| 4 | Retour visuel différent du résultat persisté | Non : le retour est lu depuis la réponse persistée (`feedback_json`, `points_awarded`) |

## 2. Correction

- Nouveau `app/v1/display_order.py` : à la création de **chaque session** (quiz,
  entraînement, examen blanc, point unique `_finalize_session`), chaque question servie
  reçoit sa propre permutation. Elle est persistée dans
  `SessionQuestion.content_snapshot_json = {"display_order": {...}}` : une colonne qui
  existait déjà mais restait inutilisée, donc **aucune migration**. Elle contient seulement
  des identifiants, jamais la solution.
  - QCM : tirage uniforme (`SystemRandom`). La bonne réponse peut tomber en premier par
    hasard (1 chance sur n), mais ce n'est plus un indice. Pas d'alternance déterministe, pas
    de règle « jamais en premier » (ce serait un autre indice).
  - Options dont le sens dépend de leur place (« toutes les réponses ci-dessus », « aucune
    des réponses précédentes », « A et B ») : elles restent à leur place et les autres sont
    mélangées autour. Aucune n'existe aujourd'hui dans les banques actives (vérifié).
  - Un QCM marqué `shuffle: false` par son auteur garde son ordre.
  - Remise en ordre : les éléments ne sont jamais affichés déjà dans le bon ordre. 23 des 58
    remises en ordre actives étaient stockées dans l'ordre exact.
  - Classement : inchangé (rien à deviner par la position).
- La permutation est réappliquée partout où les réponses sont listées : écran de question du
  quiz et de l'entraînement/examen (`build_question_display`), correction affichée après
  validation dans le quiz (`feedback_view`) et payloads des résultats (`routes_sessions`).
  Elle reste identique après navigation, rafraîchissement et reprise.
- **Banque et versions jamais modifiées.** La correction reste faite sur le contenu privé et
  par identifiant : l'ordre affiché n'intervient jamais dans le score.
- Sessions créées avant ce correctif : elles n'ont pas de permutation et gardent l'ordre de la
  banque, pour que l'élève revoie exactement ce qu'il a vu.

Fichiers : `app/v1/display_order.py` (nouveau), `app/v1/session_service.py`,
`app/v1/quiz_service.py`, `app/v1/routes_sessions.py`,
`tests/test_ticket150_quiz_answer_order.py` (nouveau), `docs/quiz_v1.md`,
`docs/current_state.md`.

## 3. Liens directs pour tester

1. https://jury-central.lodylands.com/quiz/apercu?matiere=FSE&questions=10 : lancer une
   partie FSE (la banque la plus touchée).
2. https://jury-central.lodylands.com/quiz/apercu?uaa=ampcr-mc04&questions=5 : un cours AMPCR
   où toutes les bonnes réponses étaient en premier.
3. https://jury-central.lodylands.com/quiz : « Tout mon parcours ».

Procédure courte :

1. Jouer une partie en cochant **toujours la première réponse** : le score doit être bas et
   varié, plus 100 %.
2. Rafraîchir une question avant de valider : l'ordre des réponses ne change pas.
3. Quitter puis reprendre la partie : même ordre.
4. Après validation, la correction liste les réponses dans le même ordre qu'à l'écran.
5. Faire aussi un entraînement ou un examen blanc FSE : les réponses sont mélangées de la même
   façon et la correction reste correcte.

## 4. Vérifications

- Nouveaux tests `tests/test_ticket150_quiz_answer_order.py` (12), avec des permutations
  contrôlées (graines fixes ou permutation posée explicitement), sans tirage aléatoire
  fragile :
  - une réponse fausse affichée en premier et choisie ⇒ « Pas tout à fait », 0 point, score
    0 / 1 persisté ;
  - la bonne réponse affichée en 1re, 2e ou 4e position est toujours reconnue (1 point) ;
  - chaque option d'un QCM connu essayée dans des parties isolées : une seule est créditée
    (`{a:1, b:0, c:0, d:0}`) ;
  - QCM à plusieurs réponses : un sous-ensemble faux, une seule réponse ou toutes les réponses
    valent 0 ; seule la bonne paire, dans n'importe quel ordre, vaut 1. À l'écran, cocher
    tout est refusé (422, rien n'est compté) ;
  - permutation persistée, identique d'un affichage à l'autre, correction affichée dans le
    même ordre ; banque inchangée ;
  - double validation : aucune recorrection ;
  - sur 40 graines fixes, les 4 options apparaissent en premier et la bonne réponse n'est
    pas majoritairement en tête ;
  - option « toutes les réponses ci-dessus » gardée à sa place, `shuffle: false` respecté,
    remise en ordre jamais affichée résolue, ancienne session sans permutation inchangée ;
  - entraînement et examen blanc : permutation persistée et appliquée à l'affichage.
- **Suite complète** (moteur de sessions partagé touché, lancée une fois) : **1876 passed** (14 min).
- Ruff sur les fichiers modifiés : aucune erreur. Les erreurs signalées ailleurs dans
  `app/v1/` (imports FSE, `timezone.utc`) existaient avant ce ticket.
- Installation : sauvegarde de la base (état du site avant installation), fast-forward `6048e0b → 36793cb`, pas de changement de dépendances ni de seed, redémarrage des 2 services (actifs), `/health` local et public OK, `/`, `/modules/fse`, `/login` en 200, `/quiz` → connexion (303, normal). Compteurs utilisateurs/sessions/réponses : 18/71/584 avant et après.
- **Non fait** : partie jouée dans un vrai navigateur sur le site (aucun compte de test
  utilisé). **La validation visuelle et fonctionnelle reste la tienne.**

## 5. Portée sur les anciennes parties (aucune donnée modifiée)

Mesure en lecture seule sur la base réelle, avant installation :

| Activité | QCM servis | dont bonne réponse en 1er | QCM répondus | dont 1re option choisie |
|---|---|---|---|---|
| Quiz (1 partie terminée) | 10 | 10 | 10 | 10 |
| Entraînements | 80 | 41 | 24 | 15 |
| Examens blancs | 98 | 65 | 57 | 41 |

Les scores déjà enregistrés des QCM de ces sessions ont pu être favorisés par la position. On
ne peut pas distinguer une bonne réponse réfléchie d'un choix « par défaut ». **Rien n'a été
effacé ni recalculé** (consigne du ticket). Voir la décision n° 1.

## 6. Choix techniques faits seul

1. **Permutation par session, pas de modification de la banque.** C'est ce que demande le
   ticket : les anciennes versions et les sessions passées restent intactes.
2. **Appliquée aussi à l'entraînement et à l'examen blanc.** Ils servent les mêmes banques
   par le même point de création (`_finalize_session`) et avaient le même défaut. Le ticket
   demande de vérifier l'absence de régression : la correction différée des examens est
   inchangée, puisque la correction ne lit pas l'ordre affiché.
3. **Stockage dans `content_snapshot_json`** : colonne prévue pour « options affichées » et
   jusque-là vide, donc aucune migration.
4. **Tirage uniforme**, sans « jamais en premier » ni alternance, pour ne créer aucun nouvel
   indice.
5. **Anciennes sessions sans permutation** : ordre de la banque conservé, y compris pour les
   parties en cours. Une reprise doit montrer exactement ce qui a été vu.
6. **Classements non permutés** : la réponse est un index de catégorie et aucune position ne
   donne d'indice ; une permutation ajouterait un risque de mapping sans gain.

## 7. Décisions demandées au propriétaire

1. **Anciennes sessions potentiellement faussées** (tableau du § 5 : 1 quiz, 41 entraînements
   et examens avec des QCM dont la bonne réponse était en tête). Options :
   (a) ne rien changer ;
   (b) afficher une mention « score QCM possiblement favorisé (ordre des réponses, corrigé le
   21/10) » sur ces sessions ;
   (c) les exclure du rating de module (#45).
   **Recommandation : (a) ou (b).** Il y a peu de sessions, et tout recalcul serait
   arbitraire.
2. **Banques sources** : faut-il en plus remélanger physiquement les options des banques
   FSE/AMPCR/Français ? Ce serait une nouvelle version par question. **Recommandation : non.**
   Le mélange par session suffit et couvre aussi les futures banques rédigées à la main.

## 8. Restant à réaliser

- Validation par le propriétaire sur le site (§ 3).
- Décisions ci-dessus. Aucune n'empêche d'utiliser le correctif.
