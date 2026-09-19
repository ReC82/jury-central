# Ticket #82 — BUG RÉEL : doublons intra-session

**Branche** : `feature/82-no-intrasession-duplicates`, base `develop` (486f35c, PR #81
mergée). Aucun merge, aucun déploiement effectué.

---

# 1. Cause racine

Rapportée : « Dans une même évaluation, la question 1 et la question 10 étaient
exactement identiques. »

Trouvée dans `app.v1.session_service` : DEUX occurrences identiques du même motif
(`start_session` pour le parcours per-MC/global, `_start_mc38_transversal_session` pour
MC38), dans le « dernier repli » déclenché quand banque + génération ne suffisent pas à
atteindre `question_count` :

```python
pool = selected or fallback_pool
while len(selected) < question_count and pool:
    selected.append(pool[len(selected) % len(pool)])
```

`pool[len(selected) % len(pool)]` **cycle mécaniquement** dès que `pool` est plus petit
que le manque à combler — exactement le bug rapporté. Aucune vérification que l'élément
ajouté n'était pas déjà dans `selected`.

---

# 2. Fix

## 2.1 Garde finale (`deduplicate_intra_session`)

Nouvelle fonction dans `session_service.py`, appliquée par `_finalize_session` **juste
avant** l'insertion des `SessionQuestion` — le seul point de passage commun à TOUS les
parcours de création de session. Élimine, en gardant la première occurrence :

- même `Question.id` plus d'une fois ;
- même `current_version_id` plus d'une fois ;
- même énoncé EXACT (normalisé) avec un `question_id` différent ;
- quasi-doublon manifeste (réutilise tel quel le mécanisme #64 :
  `question_signature`/`is_near_duplicate`).

`question_count` de la session reflète désormais le nombre RÉEL de questions retenues
après cette garde — jamais le nombre initialement demandé si la garde en a retiré.

## 2.2 Fin du cyclage (`_extend_selection_without_duplicates`)

Remplace le `while ... % len(pool)` aux deux endroits :

```python
def _extend_selection_without_duplicates(selected, fallback_pool, question_count):
    return deduplicate_intra_session([*selected, *fallback_pool])[:question_count]
```

Concatène puis déduplique une seule fois, tronque à `question_count` — ne cycle jamais.
Si le pool ne fournit pas assez d'éléments uniques, la session est **plus courte que
demandé**, jamais dupliquée. Hiérarchie de repli respectée : (1) nouvelle génération,
déjà tentée en amont ; (2) questions anciennes mais uniques ; (3) session plus courte ;
(4) jamais de doublon.

## 2.3 Effet de bord découvert et corrigé : `FakeAIProvider`

En écrivant les tests, découverte que `app.ai.fake_provider._fake_question` produisait un
contenu **100% fixe par type** (ex. tout `multiple_choice` factice = même prompt, mêmes
options, littéralement) — deux appels de génération pour le même type au sein d'un même
lot (fréquent : `BRIDGE_TYPES` n'a que 7 types, un lot de 10-20 questions doit forcément
répéter des types) produisaient des questions structurellement ET textuellement
identiques. Ce n'était PAS un bug de production (un vrai fournisseur IA varie son
contenu), mais un défaut du double de test qui **masquait** la classe de bug #82 dans
tous les tests existants utilisant ce stub — une fois la garde #82 en place, ces
questions factices identiques étaient (à raison) rejetées, réduisant artificiellement le
nombre de questions dans de nombreux tests déjà existants.

Corrigé : `_fake_question` reçoit désormais un `index` et ajoute un suffixe garanti
distinct (`_variation_clause`, deux jetons numériques indépendants) au prompt **et** aux
champs structurels comparés par #64 (`accepted_answers` pour `short_answer`/`vocabulary`/
`fill_blank`, en plus des options/catégories/éléments déjà couverts). Seul le LIBELLÉ
varie — la position de la bonne réponse (`correct_indexes`/`correct_categories`/etc.)
reste inchangée, aucun test de correction ne peut être affecté.

Calibrage vérifié empiriquement (voir docstring de `_variation_clause`) : un seul jeton
qui varie reste insuffisant sur les prompts courts sans champ structurel comparable
(`diagnostic`/`long_answer`/etc., seuil de recouvrement lexical #64 = 0.72) — deux jetons
indépendants ramènent le recouvrement sous 0.64 dans tous les cas testés, y compris le
pire cas réaliste (un type répété jusqu'à 3 fois dans un lot de 20).

---

# 3. Effet de bord découvert : 2 questions Français quasi-identiques

En relançant la suite complète, 3 tests Français ont commencé à échouer
(`test_exam_session_has_twenty_questions`, `test_francais_exam_still_composes_normally`,
`test_course_mapping_data_exposed_in_results_without_a_button`) : la banque Français (40
questions, hors périmètre Informatique de cette mission) contient **2 questions
`classification`** (Fait/Opinion, une par document) partageant un gabarit de prompt et
des catégories (`["Fait", "Opinion"]`) strictement identiques — le mécanisme #64
(inchangé) les traite à raison comme un quasi-doublon dès qu'elles sont toutes les deux
tirées dans la même session.

**Décision** (conformément à « si une phase bloque sur une décision produit : documente
et passe à la suivante ») : **pas touché au contenu Français** (hors périmètre explicite
de cette mission). Les 3 tests concernés ont été mis à jour pour accepter une fourchette
(9-10 ou 19-20 selon le tirage) au lieu d'un nombre fixe — comportement correct et non
flaky. Recommandation pour un futur ticket Français : varier légèrement le prompt/les
catégories de l'une des deux questions de classification pour lever cette quasi-collision
et retrouver systématiquement 40/40 questions disponibles.

---

# 4. Tests

Nouveau fichier `tests/test_ticket82_no_intrasession_duplicates.py` (12 tests) :

1. `deduplicate_intra_session` : garde le premier exemplaire (même `question_id`
   répété) ; rejette un doublon exact-texte à `question_id` différent ; rejette un
   quasi-doublon (#64) ; garde des questions génuinement différentes.
2. **Reproduction directe du bug rapporté** : un générateur qui renvoie toujours la MÊME
   question (`_AlwaysIdenticalProvider`), banque vide, `question_count=10` → session à 1
   question, jamais 10 doublons.
3. **Banque presque épuisée** : 3 questions réellement distinctes en banque, génération
   indisponible, `question_count=10` demandé → session à 3, jamais un doublon pour
   compléter.
4. **Non-régression** (bases suffisamment fournies, garantie testée explicitement à
   chaque fois via `_assert_no_intra_session_duplicates`) : practice 10Q (MC01), exam 10Q
   (MC01), exam 20Q (examen blanc global AMPCR — le scénario le plus à risque avant #82,
   entièrement généré), MC38 transversal practice 10Q et exam 20Q.
5. **Garde finale toujours appliquée** : `_finalize_session` appelée directement avec un
   `selected` contenant délibérément 4 fois la même Question → session à 1 question,
   prouve que la garde ne dépend d'aucun appelant « bien élevé ».

Suite complète du dépôt : **1106 passed** (1094 + 12). Ruff : **0 nouvelle erreur** (36
pré-existantes, hors fichiers touchés, confirmé par comparaison directe avec `develop`).

---

# 5. Fichiers modifiés

- `app/v1/session_service.py` — `deduplicate_intra_session`,
  `_extend_selection_without_duplicates`, `_finalize_session` (garde finale), les deux
  fallbacks « dernier recours » (`start_session`/`_start_mc38_transversal_session`).
- `app/ai/fake_provider.py` — `_fake_question`/`_variation_clause` (contenu factice
  réellement distinct par question).
- `tests/test_ticket82_no_intrasession_duplicates.py` — nouveau, 12 tests.
- `tests/test_ticket68_ipv4_domain_validation.py` — 1 test mis à jour (comportement de
  repli désormais correct : 1 question, pas 2, en répétant un fallback unique).
- `tests/test_ticket47_francais_v1.py`, `tests/test_ticket77_hidden_source_document.py`,
  `tests/test_ticket79_source_document_ui.py` — 4 assertions Français mises à jour
  (fourchette au lieu d'un nombre fixe, voir § 3).
