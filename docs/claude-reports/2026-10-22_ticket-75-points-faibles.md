# Ticket #75 — Weakness V1 : détecter les points faibles et proposer un renforcement ciblé

- Ticket : https://github.com/ReC82/jury-central/issues/75
- **État réel : Installé — à tester** (V1 ; limites listées en § 8)
- Branche : `feature/75-weakness-v1` — PR #172 (fusionnée dans `develop`)
- **SHA installé : `6c43bc045c9dfefb42256e6fd9c382e13819034b`** sur https://jury-central.lodylands.com

## 1. Réconciliation

Avant ce travail, rien n'existait pour ce ticket (ni branche, ni PR, ni rapport, ni code). Les
tables `v1_concepts` / `v1_question_concepts` (notions) existaient depuis #38 mais sont
vides en base. Le moteur Quiz (#137) offrait déjà le cycle « une question à la fois +
correction immédiate » : il a été réutilisé.

## 2. Ce qui est livré (comportement visible)

**Page « Mes points faibles »** — `/points-faibles` (lien « Points faibles » dans la barre de
navigation, bouton dans « Mes entraînements », bloc dans la page de résultats) :
- une ligne par cours (ou par notion si la question est étiquetée), groupée par matière ;
- niveau **Prioritaire / Fragile / À consolider / Fort** (aucun score chiffré affiché),
  mention « peu de données » sous 3 réponses, date de la dernière erreur, tendance
  (s'améliore / stable / se dégrade / première série) ;
- actions « S'entraîner sur ce point » et « Relire le cours » ;
- « Travailler mes points faibles » : mélange des 3 principaux points faibles actifs ;
- « Examen ciblé points faibles » par matière : 10 ou 20 questions ;
- renforcements en cours (reprise) et derniers renforcements terminés ;
- explication courte du calcul (« Comment sont calculés les niveaux ? »).

**Renforcement ciblé** — `/renforcement/{id}` (nouveau mode `reinforcement`) :
- une question à la fois → « Valider ma réponse » → réponse verrouillée, verdict
  (juste / partiel / faux), bonne réponse, explication « Pourquoi ? », bouton « Relire le
  cours », puis « Question suivante » ;
- 6 questions au départ ; après une erreur ou une réponse partielle, une **autre** question
  du même cours (jamais la même ni un quasi-doublon) est ajoutée en fin de session (10 au
  maximum), avec le message « Une autre question sur cette notion t'attend plus loin » ;
- bilan final : réussite par notion, niveau avant → maintenant, revoir chaque question.
- QCM, classements et remises en ordre seulement (correction locale, aucun appel IA).

**Examen ciblé** — examen blanc ordinaire (`/sessions/{id}`) composé uniquement de questions
des 5 principaux points faibles actifs de la matière : aucune correction avant la soumission,
correction, sévérité, résultats et rating habituels.

**Page de résultats** : sous « Cours à relire en priorité », bouton « Renforcer ces notions
(correction immédiate) » sur les cours ratés de la session, et lien « Mes points faibles ».

## 3. Calcul du profil (choix techniques)

- Aucune table nouvelle : le profil est recalculé depuis les réponses déjà enregistrées
  (`SessionAnswer` → `SessionQuestion` → `QuestionVersion` → `Question.uaa` /
  `Question.concepts`). Une réponse = une observation. La « comparaison d'une autre
  sévérité » (#70) n'écrit jamais en base : elle ne peut pas être comptée deux fois.
- Sources : entraînements et examens blancs terminés, réponses corrigées des renforcements.
  Exclus : quiz, sessions non terminées, réponses en erreur technique ou en attente.
- Score interne 0-100, mise à jour dans l'ordre chronologique :
  `score ← score + α × (100 × (1 − r) − score)` avec `r` = points obtenus / points max ;
  erreur α = 0,5 (× 1,2 question facile, × 0,8 difficile) ; réussite α = 0,35 (× 0,8 facile,
  × 1,2 difficile, × 1,15 en examen, × 0,9 en renforcement). Exemples : deux erreurs
  50 → 75 ; une réussite ensuite 75 → 49 (pas de remise à zéro) ; quatre réussites → < 20.
- Niveaux : Prioritaire ≥ 65, Fragile ≥ 40, À consolider ≥ 20 (= point faible actif), Fort.
- Détail : `docs/weakness_v1.md`.

## 4. Fichiers

- Nouveaux : `app/v1/weakness.py`, `app/v1/routes_weakness.py`,
  `app/templates/weakness_home.html`, `app/templates/weakness_reinforcement_done.html`,
  `docs/weakness_v1.md`, `tests/test_ticket75_weakness.py`.
- Modifiés (ajouts limités) : `app/v1/models.py` (mode `REINFORCEMENT`, aucune migration),
  `app/v1/session_service.py` (helper `add_session_question` factorisé depuis
  `_finalize_session`, exclusion du renforcement des routes entraînement/examen et de
  l'historique, marqueur `weakness_exam` ignoré par la reprise d'examen d'un cours/global,
  libellé d'historique), `app/v1/quiz_service.py` (crochet `on_validated`, helper
  `incomplete_answer_echo` partagé), `app/v1/routes_quiz.py`, `app/v1/routes_sessions.py`
  (redirection d'une session de renforcement), `app/v1/parcours.py` (renforcement exclu de
  la progression), `app/main.py`, `app/templates/base.html`, `quiz_question.html`
  (paramétré, quiz inchangé), `v1_session_results.html`, `v1_history.html`,
  `app/static/css/jc-theme.css` (`.jc-pill-danger`), `docs/current_state.md`, `docs/INDEX.md`.

## 5. Tester

1. Se connecter, ouvrir https://jury-central.lodylands.com/points-faibles — les cours déjà
   travaillés apparaissent avec leur niveau (calculé sur l'historique existant).
2. « S'entraîner sur ce point » sur un cours Fragile/Prioritaire : répondre faux à la
   première question → correction immédiate + explication ; le compteur passe de 6 à 7.
3. Finir le renforcement → bilan (niveau avant → maintenant), revenir sur
   `/points-faibles` : le niveau/la tendance ont bougé.
4. « Examen ciblé points faibles » (10 questions) : aucune correction visible avant
   « Terminer », puis résultats habituels.
5. Page de résultats d'un entraînement terminé avec erreurs
   (https://jury-central.lodylands.com/mes-sessions → une session) : bouton « Renforcer ces
   notions ».

## 6. Vérifications

- `tests/test_ticket75_weakness.py` : 18 tests (erreur crée/augmente, partiel < erreur,
  réussites répétées réduisent, une réussite ne remet pas à zéro, difficulté, re-cotation
  sans double comptage, quiz/sessions non terminées/erreurs techniques exclus, tendance,
  ciblage des plus fortes, page et actions, correction immédiate + verrouillage + variante,
  bilan, depuis la page résultats, isolation des routes practice/exam et du parcours,
  isolation par utilisateur, examen ciblé sans correction avant la fin et non repris comme
  examen de cours). Aucun appel IA réel (`FakeAIProvider`).
- Suite complète : **1936 passed**. Ruff : **0 nouvelle erreur** (65 avant / 65 après).
- Calcul exécuté sur une copie temporaire de la base réelle (supprimée ensuite) : 30
  entrées de profil, 22 points faibles actifs, tous avec des questions de renforcement
  disponibles — aucune erreur.
- Installation : sauvegarde de la base, ff-only, redémarrage des deux services (actifs),
  `/health` local et public OK, `/points-faibles` redirige vers la connexion hors session
  (attendu), aucune erreur dans le journal ; compteurs utilisateurs/sessions/réponses
  inchangés (18 / 71 / 584).
- Non effectué : parcours manuel connecté dans un navigateur (validation propriétaire).

## 7. Décisions demandées au propriétaire

1. **Étiquetage par notion fine** (MC17 / incrément, MC15 / T568B…). Le moteur le gère déjà
   (`Question.concepts`) mais la banque n'a aucune notion étiquetée : le profil est donc par
   mini-cours (repli prévu par le ticket § B). Options : (a) rester par cours ; (b) ticket
   de contenu pour étiqueter la banque (liste de notions par cours fournie par ChatGPT) ;
   (c) étiquetage automatique par IA à la génération. Recommandation : (b), en commençant
   par MC17/MC15/MC20/MC31.
2. **Réponses rédigées en renforcement** : aujourd'hui seuls QCM/classement/remise en ordre
   (correction locale immédiate, sans IA). Inclure les réponses courtes/longues demande une
   correction IA question par question (asynchrone, comme #88). Recommandation : ticket
   séparé si le Français doit en bénéficier (peu de questions objectives en Français).
3. **Variantes générées par IA** (§ I) : la V1 puise les variantes dans la banque existante
   (jamais vues d'abord, sans quasi-doublon). Générer une variante dédiée quand la banque est
   épuisée est possible ensuite. Recommandation : seulement si la banque s'avère trop courte
   à l'usage.

Aucune de ces décisions ne bloque la V1 livrée.

## 8. Restant à réaliser / limites

- Notions fines (décision 1), réponses rédigées en renforcement (décision 2), variantes IA
  (décision 3).
- Point d'entrée « page matière » non ajouté (« éventuellement » dans le ticket).
- Le score est recalculé à chaque affichage (volume actuel très faible) ; un cache serait à
  envisager seulement si l'historique devient très volumineux.
