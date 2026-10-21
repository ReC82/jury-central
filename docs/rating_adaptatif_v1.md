# Rating adaptatif V1 (ticket #45)

Code : `app/v1/rating.py` (algorithme), branché dans `app/v1/session_service.py`
(sélection et fin de correction) et `app/v1/bank.py` (ordre de sélection).
Tests : `tests/test_ticket45_adaptive_rating.py`.

## Principes

- La difficulté **déclarée** (`Question.difficulty_declared` : easy/medium/hard) reste une
  métadonnée, jamais modifiée par le rating.
- Chaque question a une difficulté **empirique** `Question.difficulty_rating` (vide tant
  qu'aucune réponse n'a été notée) et un nombre de réponses notées `rating_sample_size`.
  `times_served` / `times_correct` comptent les passages en questionnaire terminé et les
  réussites complètes (taux de réussite = `times_correct / times_served`).
- Chaque utilisateur a un niveau **par module** (`UserModuleRating`, ex. AMPCR, FSE,
  Français) — jamais un niveau global unique.
- Mise à jour **après un questionnaire terminé et entièrement corrigé**
  (`SessionStatus.COMPLETED`), jamais après chaque question.

## Algorithme « elo-v1 » (déterministe)

Échelle commune utilisateur/question, centrée sur 1000, bornée à [400, 1600].

| Élément | Valeur |
|---|---|
| Niveau de départ utilisateur (par module) | 1000 |
| Rating initial question | facile 900, moyen 1000, difficile 1100, non déclaré 1000 |
| Réussite attendue | `p = 1 / (1 + 10^((R_question − R_user) / 400))` |
| Score observé | `points obtenus / points max`, borné à [0, 1] (points partiels proportionnels) |
| K utilisateur | `max(16, 64 / (1 + n / 5))`, n = questionnaires déjà terminés dans le module |
| K question | `max(8, 40 / (1 + n / 10))`, n = réponses déjà notées sur la question |

À la fin d'un questionnaire :

1. Tous les attendus `p` sont calculés avec les ratings **d'avant** le questionnaire.
2. Utilisateur : `ΔU = K_user × moyenne(score − p)` sur toutes les questions corrigées
   (une question laissée vide compte comme un échec de l'utilisateur).
3. Question : `ΔQ = K_question × (p − score)`, seulement si l'utilisateur a réellement
   répondu (une réponse vide ne renseigne pas sur la difficulté de la question).
4. Les deux résultats sont bornés à [400, 1600] et arrondis au centième.

Exemple : utilisateur neuf (1000) qui réussit 10 questions neuves « moyennes » :
`p = 0,5` partout, niveau 1000 → 1032, chaque question 1000 → 980.

Ajustement progressif : K diminue avec l'expérience — les premiers questionnaires font
bouger le niveau vite, puis il se stabilise ; une question se stabilise au fil des
réponses.

## Garanties

- **Une seule fois par questionnaire** : le détail appliqué (niveau avant/après, K, chaque
  question avant/après) est figé dans `QuestionnaireSession.parameters_json["rating"]` ;
  une session qui le porte n'est jamais recomptée (relance d'un job, retry…).
- **Aucun impact rétroactif** : le score d'une session n'est jamais modifié ; les sessions
  terminées avant l'installation ne sont pas rejouées ; la comparaison de sévérité
  (simulation) ne touche pas au rating.
- Un échec du calcul (inattendu) n'empêche jamais la finalisation d'une correction
  (savepoint annulé, erreur journalisée).
- Correction incomplète (`CORRECTION_INCOMPLETE`) : pas de rating tant que la session
  n'est pas terminée ; appliqué au moment où la reprise de correction la termine.

## Option « Adaptatif » (page de démarrage)

- Le choix « Adaptatif (selon ton niveau dans ce module) » est disponible à côté de
  Facile / Moyen / Difficile, avec l'affichage du niveau actuel dans le module.
- Sélection : même mécanique à deux passes que la difficulté déclarée — d'abord les
  questions dont le rating est à ±150 du niveau de l'utilisateur (diversité de types
  conservée), puis complément avec le reste si la bande ne suffit pas. Jamais d'exclusion
  ni de session raccourcie pour ce motif. Les règles existantes (anti-répétition, jamais
  de doublon, plafond des réponses longues) restent prioritaires.
- Banque : ordre préférentiel par tranches de 50 points autour du niveau (l'aléatoire est
  conservé dans une même tranche).
- Génération IA de complément (AMPCR, Français) : niveau demandé « facile » sous 950,
  « difficile » au-dessus de 1050, « moyen » sinon.
- Tant que la banque n'a pas de ratings empiriques et que l'utilisateur est à 1000,
  « Adaptatif » se comporte comme une sélection sans préférence.

## Affichage

- Page de démarrage (entraînement / évaluation) : niveau actuel dans le module et nombre
  de questionnaires terminés.
- Page de résultats : « Niveau dans le module : avant → après (±Δ) » pour les sessions
  terminées après l'installation.
- Admin (rating, tentatives, taux de réussite par question) : ticket #46 — les données
  sont prêtes (`difficulty_rating`, `rating_sample_size`, `times_served`, `times_correct`).
