# Quiz ludiques du parcours (ticket #137)

Espace `/quiz` : parties courtes (5, 10 ou 20 questions) sur un cours, une matière, plusieurs
matières ou « Tout mon parcours », une question à la fois, correction et explication juste
après la validation de chaque réponse. Code : `app/v1/quiz_service.py` (logique),
`app/v1/routes_quiz.py` (routes), gabarits `quiz_*.html`.

## Moteur réutilisé (aucune copie indépendante)

- Une partie est une `QuestionnaireSession` en `SessionMode.QUIZ` (nouvelle valeur d'enum,
  colonne VARCHAR sans contrainte : aucune migration), créée par `_finalize_session` : mêmes
  banques et versions immuables, même `UserQuestionHistory`, même garde anti-doublon
  intra-session (`deduplicate_intra_session`), même `SessionQuestion`/`SessionAnswer`.
- Correction : `app.ai.local_correction.correct_locally` via `app.v1.ai_bridge` (déjà
  utilisée par les entraînements) — déterministe, **sans IA**, au moment de la validation.
- Documents source : partial `_source_documents.html`, le même que la session
  d'entraînement/examen (les documents affichés sont ceux référencés par la question).

## Règles

- **Périmètre** : uniquement les cours publiés (`listed_uaas`) des matières du parcours choisi
  (`app.v1.parcours`) ; tout code ou slug étranger est ignoré. Un cours ou une matière sans
  question de quiz est affiché « pas encore de questions de quiz », jamais comme couvert.
- **Formats** : `multiple_choice`, `classification`, `ordering` uniquement
  (`QUIZ_QUESTION_TYPES`). Les réponses rédigées, documents longs et l'oral restent dans
  S'entraîner / Examen blanc (pas de faux négatif immédiat, pas de QCM prétendant mesurer une
  production longue). QCM à plusieurs réponses signalé avant de répondre.
- **Sélection** : tourniquet matière → cours (`_pick_balanced`), matière de départ et ordre des
  cours tirés au sort ; jamais vues d'abord (id + quasi-doublon), puis déjà vues ; à
  l'intérieur, difficulté demandée d'abord (`_difficulty_predicate`, partagé ; « Adaptée » =
  rating du module, #45). Jamais de répétition pour combler : une partie peut être plus courte.
- **Récapitulatif obligatoire** (`/quiz/apercu`) : répartition prévue par matière et limites
  annoncées (contenu sans questions, partie courte ne couvrant pas tous les cours, banque
  insuffisante, questions déjà vues, difficulté non renseignée).
- **Validation** : `POST /quiz/parties/{id}/valider` ; réponse incomplète refusée (422, rien
  enregistré) ; réponse validée verrouillée, double validation sans effet ; solution et
  explication envoyées au navigateur **seulement après** validation serveur.
- **Erreur technique** : réponse gardée en `FAILED`, exclue du score (ni juste ni fausse).
- **Reprise exacte** : `/quiz/parties/{id}` affiche la première question non validée.
- **Résultat** : score sur les questions corrigées, par matière, points forts (cours sans
  erreur), cours à relire (liens `/uaa/{slug}`), « Rejouer » (même périmètre) et « Reprendre
  mes erreurs » (cours des erreurs, en excluant les questions ratées et leurs quasi-doublons).
- **Activité distincte** : exclue de la progression « entraîné / examen blanc »
  (`user_uaa_progress`), de `/mes-sessions` (`list_user_sessions`) et du rating de module ;
  les routes `/sessions/...` ne la modifient jamais (`get_owned_session(include_quiz=False)`
  par défaut, `/sessions/{id}` redirige vers le quiz).
- Anti double-clic : bouton désactivé + même partie renvoyée si la même demande arrive dans
  les 30 s sans réponse (`find_recent_duplicate_start`).

## Routes

| Route | Rôle |
|---|---|
| `GET /quiz` | Choix (tout le parcours / matières / cours), longueur, difficulté ; parties en cours et terminées ; bilan par matière |
| `GET /quiz/apercu?parcours=1&matiere=…&uaa=…&questions=…&difficulte=…` | Récapitulatif avant départ |
| `POST /quiz/demarrer` | Crée la partie (CSRF) |
| `GET /quiz/parties/{id}` (`?vu=n`) | Question courante, correction d'une question validée, ou résultat |
| `POST /quiz/parties/{id}/valider` | Valide une réponse (CSRF) |
| `POST /quiz/parties/{id}/rejouer`, `/erreurs` | Nouvelle partie (CSRF) |

Points d'entrée : en-tête « Quiz », encart sur `/mon-parcours`, bouton « Quiz sur toute la
matière » et lien « Quiz » par cours sur `/modules/{slug}` (seulement s'il y a des questions).

## Limites connues

- Pas de génération IA pendant une partie : la variété dépend des banques déjà constituées
  (beaucoup de cours AMPCR n'ont pas encore de banque ; voir le rapport du ticket).
- Explications : affichées quand la question en porte une (`explanation`) ; sinon bonne
  réponse + lien vers le cours.
