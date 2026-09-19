# Ticket #70 — Recotation + points partiels + feedback pédagogique

**Branche** : `feature/70-regrading-partial-feedback`, base `develop` (486f35c, PR #81
mergée). Aucun merge, aucun déploiement effectué.

---

# A. Re-cotation non destructive

Nouvelle fonction `simulate_severity_comparison` (`app/v1/session_service.py`) —
« Comparer une autre sévérité » sur une session **terminée** :

- Refuse toute session non `COMPLETED` (`SessionNotCompletedError`).
- Ne fait **aucune écriture en base** (aucun `db.add`, aucun `db.commit`) — recalculée à
  chaque demande, jamais une seconde vérité stockée.
- Réutilise `correct_session_hybrid` (même moteur que `submit_session`) : les questions
  déterministes restent TOUJOURS verrouillées sur `correct_locally`, indépendant de la
  sévérité (`_lock_score_keep_ai_explanation`, inchangé) — seules les questions
  sémantiques peuvent réellement varier entre `original_score` et `comparative_score`.
  Vérifié explicitement par test (un QCM correct garde le même score sur les 5 niveaux de
  sévérité).

Nouvelle route `POST /sessions/{id}/compare-severity` — réaffiche l'écran de résultats
habituel avec un encart « Score original : X / Score sévérité Y : Z ». Formulaire
« Comparer une autre sévérité » ajouté à `v1_session_results.html`, visible uniquement sur
une session `COMPLETED`. Erreur IA gérée proprement (message clair, jamais un crash).

`_build_questionnaire_inputs`/`_contexts_for_session` : extraits de `submit_session` pour
être partagés avec `simulate_severity_comparison` sans risque de divergence entre les
deux (même construction de `Questionnaire`/réponses/contexte).

---

# B. Points partiels — classification/matching

`app/ai/local_correction.py` : `classification`/`matching` notent désormais au prorata du
nombre d'éléments correctement associés (`_partial_credit_classification`/
`_partial_credit_matching`, `Fraction` exacte) — remplace l'ancien tout-ou-rien
(`indexes == question.correct_categories`). Exemple exact du ticket vérifié : 4 items, 2
corrects → 0.5/1.0. `correct` (booléen, verrouillé pour feedback #62) reste `True`
uniquement si 100 % des éléments sont corrects.

**`ordering` explicitement EXCLU** (§ AUDIT du ticket) : un crédit partiel
position-par-position serait TROMPEUR — attendu `[A,B,C,D]`, soumis `[B,A,C,D]` (une
seule inversion adjacente, intuitivement « presque juste ») ne scorerait que 2/4 en
comparaison position par position, alors qu'un décalage global comme `[D,A,B,C]` (chaque
élément à la bonne position RELATIVE, juste décalé d'un cran) scorerait 0/4 —
sous-évaluant fortement une réponse presque correcte. Une métrique honnête (paires
adjacentes correctement ordonnées, ou plus proche sous-séquence commune) est une vraie
décision pédagogique, hors du périmètre minimal de ce ticket — documentée, non
implémentée, `ordering` reste tout-ou-rien (vérifié par test de non-régression explicite).

Garde-fou à l'import (`local_correction.py`) : `_CHECKERS` (tout-ou-rien) ∪
`_PARTIAL_CREDIT_CHECKERS` (crédit partiel) doit couvrir exactement les types
corrigeables localement, sans chevauchement — assertion mise à jour en conséquence.

---

# C. Feedback IA plus pédagogique

`app.ai.prompts.CORRECT_SEMANTIC_SYSTEM_PROMPT` (système, s'applique à TOUTE correction
sémantique, tous sujets confondus) : nouvelle exigence générique — pour toute réponse
incorrecte/partielle, le champ `feedback` doit couvrir, dans l'ordre pertinent : (1) où se
situe l'erreur, (2) la bonne réponse, (3) le raisonnement, (4) la règle/formule/méthode
générale, (5) un exemple/mnémo si utile, (6) la notion/le cours à revoir. Ajout explicite
: utiliser tels quels les « faits de référence » du contexte pédagogique (jamais
recalculés approximativement) ; ne jamais reprocher une étape de vérification que le
candidat a explicitement dit avoir déjà faite.

**Faits de référence concrets** (`app/v1/ampcr_plan.py`,
`_CORRECTION_REFERENCE_FACTS_BY_CODE`) — reproduits **verbatim** depuis les « CAS RÉELS À
COUVRIR » du ticket, jamais inventés (règle du projet : Claude ne redéfinit jamais le
contenu pédagogique), injectés dans le contexte pédagogique de 2 mini-cours précis :

- **MC17** (subnetting) : `/24` = `255.255.255.0` ; `/25` → masque `255.255.255.128`,
  incrément 128 ; `/28` → masque `255.255.255.240`, incrément 16, 14 hôtes ; règle des
  bits contigus (un masque comme `255.255.232.0` est invalide, bits non contigus).
- **MC15** (câblage RJ45) : ordre complet T568B broche par broche ; différence T568A/
  T568B (inversion paires verte/orange) ; règle explicite : ne jamais reprocher une
  « absence de contrôle de continuité » si le candidat a déjà cité un testeur RJ45.

Vérifié qu'aucun autre mini-cours ne « fuite » ces faits (test explicite sur MC20).

Aucun appel OpenAI réel dans les tests — la qualité RÉELLE du feedback généré par un vrai
modèle ne peut pas être vérifiée par pytest ; ce qui est vérifié, c'est que l'INSTRUCTION
et les FAITS corrects atteignent bien le prompt envoyé au fournisseur (même principe de
test que les tickets #47/#77 pour les clauses de rubric Français).

---

# Tests

Nouveau fichier `tests/test_ticket70_regrading_partial_feedback.py` (16 tests, aucun
appel OpenAI réel) :

- **A** (5) : session non terminée rejetée ; résultat original jamais modifié (score,
  `points_awarded`, `feedback_json` identiques après simulation) ; score déterministe
  invariant sur les 5 sévérités ; round-trip HTTP réel affichant les deux scores ; erreur
  IA gérée sans crash.
- **B** (6) : exemple exact du ticket (2/4 → 0.5) ; 100 % correct → score plein ;
  `matching` partiel ; soumission malformée → 0 (pas de crash) ; `ordering` non touché
  (non-régression explicite) ; bout en bout via `submit_session`.
- **C** (5) : structure en 6 points présente dans le prompt système ; règle
  anti-pénalisation d'une vérification déjà faite ; faits MC17/MC15 présents ; aucune
  fuite vers un autre mini-cours.

Suite complète du dépôt : **1110 passed**. Ruff : **0 nouvelle erreur** (36
pré-existantes, hors fichiers touchés, confirmé par comparaison directe avec `develop`).

---

# Fichiers modifiés

- `app/v1/session_service.py` — `simulate_severity_comparison`, `SeverityComparison`,
  `SessionNotCompletedError`, `_build_questionnaire_inputs`/`_contexts_for_session`
  (extraits de `submit_session`).
- `app/v1/routes_sessions.py` — route `POST /sessions/{id}/compare-severity`, contexte
  enrichi de `view_session`.
- `app/templates/v1_session_results.html` — encart de comparaison + formulaire.
- `app/ai/local_correction.py` — crédit partiel classification/matching.
- `app/ai/prompts.py` — structure en 6 points du feedback pédagogique.
- `app/v1/ampcr_plan.py` — faits de référence MC17/MC15.
- `tests/test_ticket70_regrading_partial_feedback.py` — nouveau, 16 tests.
