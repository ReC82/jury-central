# Ticket #137 — Quiz ludiques par matière et multi-matières du parcours CESS P

- Ticket : https://github.com/ReC82/jury-central/issues/137 (P1)
- Branche : `feature/137-quiz-ludiques` — PR #142 (fusionnée dans `develop`)
- **État réel : Partiel — installé, reste à faire** (première version fonctionnelle à tester ; illustrations IA et extension des banques restent à faire, voir § 8)
- **SHA installé** : `37eb7c687cd479b37f65a56a4ff485cb53538d9c` (+ commit de ce rapport, sans redémarrage)

## 1. Synthèse

Un espace **Quiz du parcours** est installé : choisir un cours, une matière, plusieurs
matières ou « Tout mon parcours » → récapitulatif → partie (une question à la fois, validation,
correction et explication) → résultat (points forts, cours à relire) → rejouer ou reprendre
ses erreurs avec de nouveaux cas. Le chemin multi-matières applique réellement la sélection et
répartit les questions de façon équilibrée.

Couverture réelle (banques en place sur le site au 21/10) :

| Matière | Cours ayant des questions de quiz | Questions de quiz |
|---|---|---|
| Informatique AMPCR (option) | 10 cours : MC01-04, MC11, MC17, MC26, MC31, MC37, MC38 | 159 |
| Français | 5 cours : FR01→FR05 | 16 |
| FSE | 16 cours : FSE01→FSE16 (FSE17 = révision sans banque propre) | 99 |

Les cours sans questions (ex. MC05) sont affichés « pas encore de questions de quiz » et ne
sont jamais présentés comme couverts. Mathématiques (MB32) reste hors du parcours.

## 2. Ce qui change à l'écran

- **En-tête** : nouvel onglet « Quiz ». **Mon parcours** : encart « Quiz du parcours — Jouer ».
- **Page matière** (`/modules/ampcr`, `/modules/fse`, `/modules/francais`) : bouton « Quiz sur
  toute la matière » et lien « Quiz » sur chaque cours qui a des questions.
- **`/quiz`** : « Tout mon parcours », une tuile par matière (cases à cocher, nombre de
  questions et de questions jamais vues), « Choisir des cours » par matière, longueur
  5/10/20, niveau Facile/Moyen/Difficile/Adapté ; parties en cours (reprise) et terminées,
  bilan de bonnes réponses par matière.
- **Récapitulatif** : répartition prévue par matière et « Bon à savoir » (partie courte ne
  couvrant pas tous les cours, banque insuffisante, questions déjà vues, difficulté non
  renseignée pour AMPCR/Français, cours sans questions).
- **Partie** : barre de progression, matière et cours de la question, type, mention
  « Plusieurs réponses attendues » si besoin, documents source (mêmes que pour la correction),
  grandes réponses tactiles (lettres A, B, C…), bouton « Valider ma réponse ». Après validation :
  verdict (Bonne réponse / Presque / Pas tout à fait), bonne réponse surlignée, tableau pour
  les classements, bon ordre pour les remises en ordre, « Pourquoi ? » si la question a une
  explication, lien vers le cours, puis « Question suivante ». Pas de chronomètre.
- **Résultat** : message mesuré (≥ 80 % confettis, sauf animations réduites), score par
  matière, points forts, cours à relire (liens), « Reprendre mes erreurs (nouveaux cas) »,
  « Rejouer », revue de chaque question.

## 3. Liens directs pour tester

1. https://jury-central.lodylands.com/quiz (connecté, parcours choisi)
2. https://jury-central.lodylands.com/quiz/apercu?uaa=ampcr-mc01&questions=5 — quiz sur un cours
3. https://jury-central.lodylands.com/quiz/apercu?matiere=FSE&questions=10 — une matière
4. https://jury-central.lodylands.com/quiz/apercu?matiere=FRANCAIS&matiere=FSE&questions=10 — multi-matières
5. https://jury-central.lodylands.com/quiz/apercu?parcours=1&questions=20 — tout le parcours
6. https://jury-central.lodylands.com/modules/ampcr — boutons Quiz sur le chemin de cours
7. https://jury-central.lodylands.com/mon-parcours — encart Quiz

Procédure courte : lancer une partie de 5 questions sur MC01 ; essayer de valider sans
répondre (message, rien n'est compté) ; se tromper exprès une fois ; quitter au milieu puis
revenir sur `/quiz` → « À reprendre » ; finir → résultat → « Reprendre mes erreurs ». Puis une
partie multi-matières Français + FSE et vérifier la répartition annoncée. Tester au téléphone.

## 4. Vérifications

- Tests nouveaux `tests/test_ticket137_quiz.py` (14) : périmètre borné au parcours et aux
  formats objectifs, page d'accueil et connexion requise, récapitulatif et limites, partie
  complète (aucune solution avant validation, réponse incomplète refusée sans rien enregistrer,
  double validation sans effet, reprise exacte, résultat et liens cours), activité distincte
  (progression, `/mes-sessions`, rating, routes `/sessions/...`), multi-matières appliqué et
  équilibré sans doublon, tout le parcours, questions jamais vues d'abord, difficulté
  préférée, reprise des erreurs sans les questions ratées, erreur technique jamais comptée
  fausse, double démarrage, points d'entrée.
- **Suite complète** (modèle et moteur partagés touchés) : **1750 passed**.
- Ruff : aucune nouvelle erreur (les 4 B008 de `app/main.py` préexistent).
- Essai sur une **copie** de la base réelle (dans /tmp, supprimée ensuite) : parties de 20
  questions (tout le parcours, Difficile) et de 10 (Français + FSE, Facile) jouées jusqu'au
  bout, documents FSE affichés, aucune erreur ; temps : accueil 0,15 s, récapitulatif 0,06 s,
  création 0,3-0,5 s.
- Installation : sauvegarde de la base, fast-forward `77c0496 → 37eb7c6`, redémarrage des 2
  services (actifs), `/health` local et public OK, pages publiques en 200, `/quiz` → connexion
  (normal), liens Quiz présents sur les pages matière. Compteurs utilisateurs/sessions/réponses :
  18/69/566 avant et après.
- **Non fait** : validation visuelle dans un navigateur réel (pas de session de test sur le
  site) — **la validation visuelle reste la tienne**.

## 5. Choix techniques faits seul

1. **Extension du moteur, pas de copie** : une partie est une `QuestionnaireSession` en
   nouveau mode `SessionMode.QUIZ` (colonne texte sans contrainte → aucune migration) créée
   par `_finalize_session` ; mêmes banques, historique, anti-doublon (#64/#82).
2. **Formats objectifs seulement** (QCM, classement, remise en ordre) : correction locale
   déterministe immédiate. Les réponses courtes rédigées sont exclues (la comparaison
   textuelle stricte donnerait de faux « faux » immédiats), comme les productions longues,
   documents longs et l'oral (ticket : ne pas forcer en QCM).
3. **Aucune IA pendant une partie** (ni génération ni correction) : la clé API du serveur est
   refusée (voir #136) et une partie doit rester instantanée ; la variété vient des banques.
4. **Activité distincte** : le quiz ne compte ni comme entraînement ni comme examen blanc,
   n'apparaît pas dans « Mes entraînements » et ne modifie pas le niveau de module (#45). Les
   questions vues en quiz sont en revanche notées dans l'historique commun (règle du ticket :
   réutiliser historique et déduplication) : les entraînements/examens privilégieront donc
   d'autres questions.
5. **Équilibre** : tourniquet matière → cours, matière de départ et ordre des cours tirés au
   sort ; jamais vues d'abord, puis difficulté demandée ; jamais de répétition pour combler.
6. **Score** : 1 point par question, crédit partiel pour les classements (règle existante) ;
   une erreur technique n'est ni juste ni fausse (exclue du total).
7. **Reprise des erreurs** : nouvelle partie sur les cours des erreurs, en excluant les
   questions ratées et leurs quasi-doublons ; si plus rien de neuf, message honnête.
8. **Compte requis** (score et reprise persistés), comme S'entraîner.

## 6. Décisions demandées au propriétaire

1. **Illustrations et nouveaux supports générés par l'API OpenAI.** Non réalisés : la clé
   du serveur est refusée (401, constaté au #136). Le quiz utilise le langage visuel de #136
   (icônes, couleurs de matière) et les documents existants. Options : (a) remplacer la clé
   puis une prochaine session génère et persiste les illustrations ; (b) garder l'habillage
   actuel. **Recommandation : (a).**
2. **Peu de questions de quiz pour une partie des cours** (Français : 16 au total, 2-4 par
   cours ; AMPCR : 28 cours sans banque ; peu d'explications écrites en AMPCR, 4/159). Options :
   (a) un ticket de contenu pour rédiger des QCM/classements avec explication par cours (ou les
   générer via l'IA une fois la clé valide, puis les relire) ; (b) laisser tel quel.
   **Recommandation : (a)**, en commençant par Français et les cours AMPCR les plus suivis.

## 7. Bibliothèques

Aucune nouvelle : Bootstrap Icons, police Lexend et canvas-confetti déjà intégrés au #136.

## 8. Restant à réaliser

- Illustrations IA et supports générés (dépend de la clé, décision 1).
- Élargir les banques de questions objectives avec explications (décision 2) ; génération de
  nouveaux cas pendant la partie si souhaité, une fois la clé valide.
- Visuels riches par question (#129) : le quiz affichera automatiquement les supports que
  ce ticket ajoutera aux questions.
- Futurs jeux (hors périmètre) : chrono optionnel, défis, etc.
