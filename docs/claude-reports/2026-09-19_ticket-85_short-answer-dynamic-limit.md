# Ticket #85 — Limite de longueur des `short_answer` trop basse

**Portée :** intégré directement dans `integration/informatique-6-tickets` (puis `develop`).

## Cas réel

Question HDD / SSD SATA / SSD NVMe : l'utilisateur avait une bonne réponse mais voulait la
compléter. Le textarea s'est arrêté à 200/200 caractères — trop court.

## Cause racine

`ShortAnswerContent.max_length` (`app/v1/question_types.py`) a un défaut Pydantic fixe de
200. Ni la génération IA (`app/v1/ai_bridge.py::questionnaire_question_to_content`) ni
l'import éditorial legacy (`app/v1/bank.py::_editorial_item_to_v1_content`) ne
fournissaient jamais de valeur explicite pour ce champ — toute question `short_answer`/
`vocabulary`, quelle que soit sa nature réelle (rappel factuel ou réponse développée),
retombait donc systématiquement sur cette même limite de 200 caractères. Le template
(`v1_session_question.html`) lisait déjà correctement `payload.max_length` de façon
dynamique (héritage du correctif #73 sur `long_answer`/`diagnostic`) — le bug était
entièrement en amont, dans la construction du contenu.

## Correctif

Nouveau module `app/v1/short_answer_limits.py` :

- `compute_short_answer_max_length(prompt) -> int` : détecte les déclencheurs d'une
  réponse développée (explique, justifie, compare, décris, démarche, pourquoi, « N
  éléments/raisons/étapes... ») — retourne 1500 si détecté, 300 sinon (§ 85.A : 100-300
  pour du factuel, 800-1500 pour du développé — bornes hautes retenues par défaut pour ne
  jamais risquer de tronquer une réponse correcte, § 85.B).
- `is_max_length_incoherent(prompt, max_length) -> bool` : détecteur d'incohérence
  indépendant, réutilisé à la fois par la garde serveur et par la migration § 85.C.

Câblage (construction du contenu, préventif) :
- `app/v1/ai_bridge.py::questionnaire_question_to_content` (génération IA Informatique) —
  `max_length` calculé désormais à chaque question `short_answer`/`vocabulary`.
- `app/v1/bank.py::_editorial_item_to_v1_content` (import éditorial legacy, MC01
  Informatique) — même correctif.

Garde serveur (filet de sécurité, § 85.B) : `app/v1/quality_validation.py::
check_short_answer_length_coherence`, enregistrée dans `QUALITY_VALIDATORS` — rejette
toute question `short_answer`/`vocabulary` dont l'énoncé demande explicitement une
réponse développée mais dont `max_length` est resté ≤ 300, quelle que soit son origine.

Migration additive (§ 85.C) : `app/v1/bank.py::migrate_short_answer_max_length(db)` —
relève `max_length` des questions déjà persistées, question par question, uniquement
quand `is_max_length_incoherent` le confirme (jamais une élévation aveugle ; une question
réellement factuelle garde sa limite d'origine à l'identique, y compris 200). Non
destructive : `add_question_version` (déjà existant dans le registre #40) crée une
nouvelle version immuable plutôt que de muter une version existante. Idempotente (testé).

## Décision de conception documentée

Un premier jet de la migration augmentait `max_length` dès que la valeur calculée
(`compute_short_answer_max_length`, 300 par défaut pour du factuel) dépassait la valeur
existante — y compris pour des questions réellement factuelles bloquées à 200,
contredisant directement « conserver 200 si réellement factuelle ». Corrigé : la
migration utilise exclusivement `is_max_length_incoherent` (même détecteur que la garde
serveur) comme condition de déclenchement, jamais une simple comparaison numérique — un
bug détecté par le test `test_migration_never_decreases_or_touches_genuinely_factual_questions`
avant intégration.

## Tests (`tests/test_ticket85_short_answer_dynamic_limit.py`, 24 tests)

Calcul dynamique (factuel/développé/déclencheurs individuels/insensibilité aux accents),
garde d'incohérence (rejet/acceptation/portée par type/câblage dans
`validate_question_quality`), câblage génération IA (`short_answer`/`vocabulary`),
câblage import éditorial, migration (augmente le cas développé bloqué à 200, ne touche
jamais un cas réellement factuel, idempotente).

## Fichiers

- `app/v1/short_answer_limits.py` (nouveau)
- `app/v1/ai_bridge.py` (câblage génération IA)
- `app/v1/bank.py` (câblage import éditorial + `migrate_short_answer_max_length`)
- `app/v1/quality_validation.py` (garde § 85.B)
- `tests/test_ticket85_short_answer_dynamic_limit.py` (nouveau, 24 tests)
- `docs/claude-reports/2026-09-19_ticket-85_short-answer-dynamic-limit.md` (ce rapport)
