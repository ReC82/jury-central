# Jury Central — Français V1 : état fonctionnel de l'UAA pilote `francais-c01` (ticket #47)

Pilote de VALIDATION TECHNIQUE, jamais présenté comme un examen CESS officiel (voir
`app.v1.francais_content`, docstring) : aucun contenu Français officiel ou brouillon
ChatGPT n'existait dans le dépôt avant le ticket #47 (voir
`docs/content_plan_informatique_francais.md` § 3.3). Objectif : prouver que tout le
parcours (`SourceDocument` partagé, practice/exam, autosave, reprise, correction batch IA,
résultats détaillés, sévérité, export, impression, historique) fonctionne réellement pour
une matière qui n'est PAS de l'Informatique — sans dupliquer ni redéfinir le moteur
générique (#40 question engine, #55/#58/#62 sessions AMPCR).

Ce document couvre l'état livré à l'issue de la mission de nuit du 2026-09-19 (rebase sur
`develop`, corpus étendu, corrections de bugs, couverture de tests Phase 8-13). Branche :
`feature/47-francais-v1`, non mergée, non déployée — voir
`docs/claude-reports/2026-09-19_francais-overnight-functional.md` pour le détail des
travaux de cette nuit.

---

# 1. Ce qui fonctionne pour l'utilisateur

`/uaa/francais-c01`, `/uaa/francais-c01/practice`, `/uaa/francais-c01/exam` offrent
exactement le même parcours que les mini-cours AMPCR (voir `docs/ampcr_v1_functional.md`),
via le moteur générique partagé :

1. navigation à 3 onglets Cours/S'entraîner/S'évaluer (`_uaa_space_nav.html`, ticket #22),
   avec l'onglet actif correctement surligné (bug corrigé cette nuit, § 6) ;
2. **practice** : 10 questions ; **exam** : 20 questions (le corpus de 40 questions le
   permet désormais — avant le corpus étendu, l'examen Français aurait dû rester à 10,
   comme les mini-cours AMPCR non-MC38) ;
3. autosave à chaque réponse, reprise d'une session en cours ;
4. aucune correction visible avant la fin ; un seul appel IA batch à la soumission ;
5. résultats détaillés par question (réponse donnée, attendu/critères, points, points
   forts, erreurs, éléments manquants, explication), score global, session immuable après
   soumission ;
6. sévérité de correction réglable (1 à 5, UI ticket #62), export Markdown, impression/PDF,
   historique (`/mes-sessions`) — tous vérifiés spécifiquement pour le Français cette nuit
   (§ 6), alors qu'ils n'avaient jusqu'ici été testés que pour AMPCR.

---

# 2. Corpus — 5 documents, 40 questions

Cinq `SourceDocument` partagés (jamais dupliqués dans le contenu d'une question — voir
`app.v1.session_service.build_question_display`) :

| Document | Titre | ~mots |
|---|---|---|
| `main` | (texte d'exemple pilote initial) | — |
| `second` | (texte d'exemple pilote initial, comparaison) | — |
| `digital_life` | Le numérique dans la vie quotidienne : une présence discrète mais constante | 694 |
| `training` | La formation professionnelle à l'heure du numérique | 715 |
| `coding_debate` | Faut-il apprendre les bases de la programmation à l'école, dès le secondaire ? | 254 |

40 questions au total (`app.v1.francais_bank._francais_c01_questions`), répartition par
type :

| Type | Nombre |
|---|---|
| `short_answer` | 22 |
| `vocabulary` | 5 |
| `classification` | 2 |
| `document_analysis` | 4 |
| `long_answer` | 3 |
| `source_comparison` | 4 |

Chaque question référence son (ses) document(s) par `source_document_version_id(s)`,
jamais par texte dupliqué (contrat #40). `build_question_display` (session_service.py) ne
résout que le(s) document(s) réellement référencé(s) par la question affichée — jamais les
5 à la fois — et le template (`v1_session_question.html`) les rend dans un accordéon
scindé (un seul document déplié par défaut), à hauteur bornée et défilable
(`max-height: 50vh; overflow-y: auto`), pour rester lisible sur mobile pendant que
l'élève répond, sans avoir à faire défiler la page. Vérifié par
`test_document_accordion_is_scoped_and_bounded` et
`test_source_document_panel_is_shown_for_document_referencing_questions`
(`tests/test_ticket47_francais_v1.py`).

---

# 3. Grille de correction pédagogique (rubric) — neutralité d'opinion et feedback structuré

Le moteur de correction hybride (`app.v1.hybrid_correction.correct_session_hybrid`) est
générique et partagé avec AMPCR — jamais modifié pour le Français. Le comportement
spécifique au Français vit entièrement dans le champ `rubric` (niveau contenu) de chaque
question concernée, transmis tel quel jusqu'au prompt IA
(`app.ai.prompts.build_correct_semantic_messages`, `Grille de correction : {rubric}`) :

- **`_OPINION_NEUTRALITY_CLAUSE`** (questions d'opinion/justification personnelle,
  `source_comparison` notamment) : la sévérité ne doit jamais juger l'opinion exprimée
  elle-même, seulement la qualité et la cohérence de l'argumentation.
- **`_LONG_ANSWER_FEEDBACK_STRUCTURE_CLAUSE`** (`long_answer`) : impose au feedback IA une
  structure en 4 points (STRUCTURE, ARGUMENTATION, UTILISATION DU DOCUMENT, LANGUE/
  CLARTÉ), pour un retour plus pédagogique qu'un simple score.

Ces deux clauses ont été vérifiées cette nuit jusqu'au bout de la chaîne réelle (pas
seulement leur présence dans `francais_bank.py`) : un espion sur
`FakeAIProvider.correct_semantic_batch` confirme qu'elles atteignent bien l'appel IA
(`test_opinion_neutrality_clause_reaches_the_ai_correction_prompt`,
`test_long_answer_feedback_structure_clause_reaches_the_ai_correction_prompt`). Aucun
appel OpenAI réel dans les tests.

---

# 4. Réponses longues — aucune troncature (ticket #73, cherry-pické sur cette branche)

Le plafond de longueur par défaut (`LongAnswerContent.max_length` et les 5 autres types
texte libre : `diagnostic`/`procedure`/`document_analysis`/`source_comparison`/
`troubleshooting`) est passé de 2000 à 20 000 caractères, avec compteur de caractères
visible côté formulaire. Vérifié bout en bout (autosave → rechargement → soumission →
correction → résultats → export) pour des réponses de 10 000 et 20 000 caractères, sans
troncature à aucune étape.

Une question `long_answer` du corpus Français avait un `max_length: 6000` codé en dur dans
son contenu (`francais_bank.py`), qui aurait silencieusement contourné le nouveau défaut
global — corrigé à `20_000` (voir commentaire dans le fichier).

---

# 5. Non-régression AMPCR

`_start_session_for_uaa` (routes_sessions.py) est la fonction partagée qui décide du
nombre de questions (`question_count`) pour AMPCR ET Français. Étendre sa condition
d'examen à 20 questions pour le Français (§ 1) a été vérifié comme ne changeant rien pour
AMPCR (`tests/test_ticket55_urgent_ampcr_full.py`, `tests/test_ticket58_ampcr_content_and_mc38.py` :
90 passed). Suite complète du dépôt : 1065 passed après l'ensemble des travaux de cette
nuit.

---

# 6. Bug corrigé cette nuit (partagé avec AMPCR, pas spécifique au Français)

En vérifiant explicitement la navigation Cours/S'entraîner/S'évaluer pour le Français
(§ Phase 13 de la mission de nuit), découverte d'un bug pré-existant datant du ticket #22 :
`render_practice_landing`/`render_exam_landing` (routes_sessions.py) ne passaient jamais
`active_space` au contexte de `v1_session_start.html`, donc aucun onglet n'était jamais
surligné actif sur les pages `/practice` et `/exam` — pour AMPCR comme pour Français.
Corrigé par l'ajout de la clé de contexte manquante (`"active_space": "practice"` /
`"exam"`), sans toucher au template ni à l'architecture partagée.

---

# 7. Limites assumées, non corrigées cette nuit (hors périmètre explicite)

Ces points ont été identifiés mais **délibérément non corrigés**, pour respecter la
consigne « ne refais aucune architecture générique » — ce sont des décisions produit qui
appartiennent à ChatGPT :

- **`LONG_SEMANTIC_TYPES` / `MAX_LONG_SEMANTIC_PER_SESSION`** (session_service.py, partagé
  avec AMPCR) ne comptent pas `document_analysis`/`source_comparison` parmi les réponses
  longues plafonnées à 3 par session — une session Français pourrait donc contenir plus de
  3 questions à réponse longue au total (long_answer + document_analysis +
  source_comparison combinés) sans déclencher le plafond prévu pour `long_answer`/
  `diagnostic`/`procedure`/`troubleshooting`.
- **`BRIDGE_TYPES`** (`app.v1.ai_bridge`, 7 types) ne couvre pas `procedure`/
  `document_analysis`/`source_comparison`/`troubleshooting` pour
  `answer_json_to_submitted`/`describe_submitted_answer` — gap pré-existant (pas introduit
  par le Français), contourné côté Français par son propre remapping de type pour la
  correction, jamais en modifiant le pont générique.
- **Regroupement UI « PARTIE A / B / C »** de l'examen (lecture / grammaire-vocabulaire /
  expression écrite, structure CESS typique) : non implémenté. L'examen Français actuel
  affiche ses 20 questions dans un flux unique, une à la fois, comme tout examen AMPCR —
  aucune séparation visuelle par partie.
- **Contenu pédagogique** : le corpus de 40 questions reste un pilote de VALIDATION
  TECHNIQUE écrit par Claude à partir d'une consigne de structure (jamais un contenu
  Français officiel ou validé par un professeur de Français) — voir avertissement
  « provisoire » affiché sur la page Cours.

---

# 8. Fichiers clés

- `app/v1/francais_content.py` — textes des 5 documents source.
- `app/v1/francais_bank.py` — les 40 questions, `import_francais_c01_to_bank`, clauses de
  grille de correction.
- `app/v1/francais_plan.py` — `FRANCAIS_MODULE_CODE`, `FRANCAIS_SUBJECT_NAME`,
  `FRANCAIS_PLAN_BY_CODE`, `get_francais_context`.
- `app/v1/routes_sessions.py` — `_start_session_for_uaa` (question_count), landings
  practice/exam (`active_space`).
- `app/v1/session_service.py` — `build_question_display` (résolution des documents
  scopée), `submit_session` (contextes documentaires).
- `tests/test_ticket47_francais_v1.py` — 30 tests, aucun appel OpenAI réel.
