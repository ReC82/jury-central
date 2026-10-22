# Points faibles V1 (ticket #75)

Page **Mes points faibles** (`/points-faibles`, compte requis, lien « Points faibles » dans
la barre de navigation, depuis « Mes entraînements » et depuis la page de résultats).

Code : `app/v1/weakness.py` (calcul, sélection), `app/v1/routes_weakness.py` (routes),
gabarits `weakness_home.html`, `weakness_reinforcement_done.html` et `quiz_question.html`
(partagé avec le quiz, paramétré).

## Profil de fragilité

- **Aucune table nouvelle** : le profil est recalculé à chaque affichage depuis les réponses
  déjà enregistrées (`SessionAnswer` → `SessionQuestion` → `QuestionVersion` → `Question`).
  Une réponse = une observation. La « comparaison d'une autre sévérité » (#70) ne modifie
  jamais la correction enregistrée : elle ne peut pas compter deux fois.
- **Sources** : entraînements et examens blancs `COMPLETED`, réponses corrigées des
  renforcements ciblés (dès leur validation). Exclus : quiz (#137), sessions non terminées,
  réponses `FAILED` / en attente, questions sans cours (UAA).
- **Granularité** : chaque notion liée à la question (`Question.concepts`, tables
  `v1_concepts` / `v1_question_concepts`) ; sans notion, repli sur le cours (UAA). La banque
  n'a aujourd'hui aucune notion étiquetée : le profil est donc par cours.
- **Score 0-100** (interne, jamais affiché) : mise à jour séquentielle, de la plus ancienne à
  la plus récente réponse : `score ← score + α × (100 × (1 − r) − score)`, `r` = points
  obtenus / points max.
  - erreur (`r < 0,5`) : α = 0,5 (× 1,2 question facile, × 0,8 difficile) ;
  - réussite (`r ≥ 0,5`) : α = 0,35 (× 0,8 facile, × 1,2 difficile ; × 1,15 en examen,
    × 0,9 en renforcement).
  - Difficulté : déclarée, sinon difficulté empirique (#45 : < 950 facile, > 1050 difficile).
- **Niveaux affichés** : Prioritaire (≥ 65), Fragile (≥ 40), À consolider (≥ 20), Fort.
  Point faible « actif » à partir de « À consolider ». « Peu de données » sous 3 réponses.
- **Tendance** : score actuel comparé au score d'avant la dernière session ayant porté sur
  la notion (± 8) : s'améliore / stable / se dégrade ; « première série » s'il n'y a
  qu'une session.

## Renforcement ciblé

- `SessionMode.REINFORCEMENT` : une question à la fois, « Valider ma réponse », correction
  immédiate (moteur du quiz : correction locale déterministe, réponse verrouillée,
  explication, bonne réponse, « Relire le cours », puis « Question suivante »).
- Formats objectifs seulement (QCM, classement, remise en ordre — comme le quiz) : pas
  d'appel IA pendant la session.
- Lancement : « Travailler mes points faibles » (3 principaux points faibles actifs, en
  alternance), « S'entraîner sur ce point » (une notion), « Renforcer ces notions »
  (cours ratés d'une session terminée, page résultats).
- 6 questions au départ ; après une erreur ou une réponse partielle, une **autre**
  question du même cours/notion (jamais la même ni un quasi-doublon) est ajoutée en fin de
  session, jusqu'à 10 questions.
- Choix des questions : jamais vues d'abord, puis les moins récemment vues.
- Le renforcement n'est ni un entraînement, ni un examen blanc : absent de « Mes
  entraînements » et de la progression du parcours, aucun effet sur le rating (#45).
- Une session identique encore en cours est reprise plutôt que recréée.

## Examen ciblé points faibles

- Examen blanc ordinaire (`SessionMode.EXAM`, `parameters_json["scope"] = "weakness_exam"`) :
  10 ou 20 questions sur les 5 principaux points faibles actifs d'une matière, tous formats
  corrigeables, 3 réponses longues au plus ; aucune correction avant la soumission ;
  correction, sévérité, résultats et rating habituels.
- Jamais repris comme examen d'un cours ni comme examen global (`get_in_progress_session`).

## Limites V1

- Pas de génération IA de variantes : les variantes viennent de la banque existante.
- Pas d'étiquetage par notion fine dans la banque actuelle (repli cours).
- Les réponses rédigées (courtes/longues) ne sont pas proposées en renforcement : correction
  IA immédiate non branchée.
