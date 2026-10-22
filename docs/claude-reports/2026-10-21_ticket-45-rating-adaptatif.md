# Ticket #45 — Rating adaptatif V1 — difficulté empirique des questions et niveau par module

- Ticket : https://github.com/ReC82/jury-central/issues/45
- **État réel : Installé — à tester**
- Branche : `feature/45-adaptive-rating` — PR : #138 (fusionnée dans `develop`)
- **SHA installé** : `a54710db1342a3df57f1ef6bc1e14f992890b390` (merge de la PR #138, installé le 2026-10-21)
- Documentation fonctionnelle : `docs/rating_adaptatif_v1.md`

## 1. Résultat

Le rating adaptatif est en place sur le moteur de sessions V1, pour toutes les matières
(Informatique AMPCR, Français, FSE) :

- **Niveau de l'utilisateur par module** (`UserModuleRating`, jamais un niveau global),
  départ à 1000, recalculé **une fois après chaque questionnaire entièrement corrigé**.
- **Difficulté empirique de chaque question** (`Question.difficulty_rating`), ajustée
  progressivement selon les réussites/échecs observés ; la difficulté déclarée
  (facile/moyen/difficile) reste une simple métadonnée, jamais modifiée. Le nombre de
  tentatives et de réussites complètes est maintenant compté (`times_served`,
  `times_correct`, `rating_sample_size`) — données prêtes pour l'admin (#46).
- **Option « Adaptatif »** réellement disponible sur la page de démarrage (entraînement et
  évaluation), à la place de « Adaptatif (bientôt disponible) » : sélectionne en priorité
  les questions dont le rating est proche du niveau de l'utilisateur dans le module.
- **Affichages** : page de démarrage → « Ton niveau actuel dans le module X : 1000 (…) » ;
  page de résultats → « Niveau dans le module : 1000 → 1032 (+32) ».

### Algorithme (déterministe, « elo-v1 »)

- Réussite attendue `p = 1 / (1 + 10^((R_question − R_user)/400))`.
- Score observé = points obtenus / points max (points partiels proportionnels).
- Utilisateur : `ΔU = K_user × moyenne(score − p)` ; `K_user = max(16, 64/(1 + n/5))`.
- Question : `ΔQ = K_question × (p − score)` si l'utilisateur a répondu ;
  `K_question = max(8, 40/(1 + n/10))`.
- Rating initial d'une question : facile 900, moyen 1000, difficile 1100.
- Bornes [400, 1600] ; tous les attendus calculés avec les ratings d'avant le
  questionnaire.

### Fichiers

- `app/v1/rating.py` (nouveau) : algorithme, bornes, ordre de proximité, application
  idempotente.
- `app/v1/session_service.py` : application du rating à la fin des deux chemins de
  correction (synchrone et asynchrone/worker) ; sélection adaptative (parcours par
  mini-cours, AMPCR global, MC38, FSE17) ; niveau demandé à la génération IA en mode
  adaptatif.
- `app/v1/bank.py` : ordre préférentiel par proximité de rating en mode adaptatif.
- `app/v1/routes_sessions.py`, `app/templates/v1_session_start.html`,
  `app/templates/v1_session_results.html` : option Adaptatif, niveau, évolution.
- `app/v1/models.py` : commentaires uniquement (aucun changement de schéma — tables et
  colonnes existaient depuis #38).
- `docs/rating_adaptatif_v1.md` (nouveau), `docs/current_state.md`,
  `docs/architecture_v1_data_model.md`.
- `tests/test_ticket45_adaptive_rating.py` (nouveau, 20 tests).

## 2. Comment tester

1. Ouvrir un entraînement, par ex.
   https://jury-central.lodylands.com/uaa/ampcr-mc01/practice — vérifier le choix
   « Adaptatif (selon ton niveau dans ce module) » et la ligne « Ton niveau actuel dans le
   module AMPCR : 1000 (niveau de départ…) ».
2. Lancer l'entraînement en « Adaptatif » (ou toute autre difficulté), répondre, terminer.
3. Sur la page de résultats : « Niveau dans le module : 1000 → … (±…) ».
4. Revenir sur la page de démarrage : le niveau mis à jour et « 1 questionnaire terminé ».
5. Un autre module (ex. FSE : https://jury-central.lodylands.com/subjects) garde son
   propre niveau, indépendant.

Autres pages concernées : https://jury-central.lodylands.com/modules/ampcr/practice et
https://jury-central.lodylands.com/modules/ampcr/exam.

## 3. Vérifications

- `tests/test_ticket45_adaptive_rating.py` : 20 tests verts — formules, K décroissants,
  rating initial, progression (réussite), régression (échec), points partiels, réponse
  vide, bornes, convergence progressive, déterminisme, une seule application par
  session, pas de rating sur session non terminée, séparation par module, score jamais
  modifié, application via le worker de correction, sélection adaptative (bande + complément
  + no-op sans niveau), `start_session` adaptatif, parcours HTTP complet.
- Suite complète : 1720 passed (une exécution, 14 min).
- `ruff check` sur les fichiers modifiés/créés : aucune erreur (les ~14 erreurs
  préexistantes d'autres fichiers `app/v1/fse*` sont inchangées).
- Installation (sauvegarde de la base faite avant) : services `jury-central` et
  `jury-central-correction-worker` actifs, `/health` local et public OK, `/subjects` en
  200, pages d'entraînement/évaluation en 303 vers `/login` (authentification requise,
  normal), aucune erreur dans les journaux, compteurs utilisateurs/sessions/réponses
  identiques avant/après (18 / 69 / 566).
- Non vérifié : rendu visuel dans un navigateur réel (validation propriétaire).

## 4. Choix techniques faits seul

- **Elo logistique** (échelle 400, centre 1000) : déterministe, documenté, et déjà
  anticipé par le modèle #38 (`DEFAULT_MODULE_RATING = 1000`, « convention Elo-like »).
- **Mise à jour par questionnaire, moyenne des écarts** : un questionnaire de 20 questions
  ne pèse pas deux fois plus qu'un de 10 sur le niveau ; respecte « après chaque
  questionnaire, pas après chaque question ».
- **Entraînement ET évaluation comptent** : les deux mesurent la maîtrise du module.
- **Réponse vide** : compte comme échec de l'utilisateur, mais ne rend pas la question
  « plus difficile » (aucune information sur sa difficulté).
- **Sévérité de correction** : le rating utilise le score réellement attribué ; la
  comparaison de sévérité (simulation) ne modifie rien.
- **Pas de rattrapage rétroactif** : les sessions terminées avant l'installation ne sont
  pas rejouées (« aucun impact rétroactif ») ; une session en correction incomplète reçoit
  son rating quand sa correction se termine.
- **Sélection adaptative = bande ±150 puis complément**, même mécanique que la
  difficulté déclarée (#96) : jamais de session raccourcie ni d'exclusion ; anti-répétition,
  anti-doublon et plafond des réponses longues restent prioritaires. Tant que la banque
  n'a pas de rating empirique et que l'utilisateur est à 1000, « Adaptatif » équivaut à
  « sans préférence » — l'effet apparaît avec l'usage.
- **Génération IA en adaptatif** : « facile » sous 950, « difficile » au-dessus de 1050,
  « moyen » sinon.
- **Robustesse** : le calcul tourne dans un savepoint ; un échec inattendu est journalisé
  et n'empêche jamais la finalisation d'une correction.
- **Aucune migration** : tables/colonnes déjà présentes en base depuis #38.

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Reste à faire / suites proposées

- Admin (rating, tentatives, taux de réussite par question, à la place du comptage
  Facile/Moyen/Difficile) : ticket #46 — les données sont désormais alimentées.
- Éventuellement, plus tard : afficher le niveau par module dans l'historique/le compte ;
  calibrer les constantes (K, bande) quand il y aura assez de données réelles.
