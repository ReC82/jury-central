# Ticket #37 — MC01 Practice : corriger l'ordre d'affichage des exercices 9 et 11

**Date** : 2026-09-17
**Branche** : `feature/37-mc01-practice-order`

---

## 1. Cause exacte

`LessonBlock.lesson_blocks` (relation SQLAlchemy, `app/models.py:78`) trie avec
`order_by="LessonBlock.position"` **uniquement** — aucune clé de tri secondaire. Le
système de tri lui-même n'a **pas** été modifié par ce ticket (conformément à la
consigne) : le problème vient bien des données, pas du tri.

`_seed_uaa` (`app/seed.py`) garantit explicitement, par conception, qu'un bloc déjà
existant (matché par son titre) n'est **jamais** modifié sur `content`, `title`,
`position` ou `is_published` — seule sa métadonnée `space` peut être resynchronisée
(mécanisme `reclassified`, ticket #22). Cette garantie existe parce que `position` (comme
`content`) est éditable depuis l'admin (`app/admin.py`, formulaire de bloc) : un seed ne
doit jamais écraser silencieusement une modification faite depuis l'admin.

Conséquence directe : 6 blocs MC01 créés **avant** le ticket #29 (au ticket #21 ou avant)
ont gardé leur position de l'époque, alors que les 8 nouveaux blocs d'exercices insérés
par #29 (Ex3/4/5/6/7/8/10/12) ont reçu la position **actuellement** déclarée dans
`MC01_BLOCKS` — un layout différent de celui qui existait au moment où les 6 blocs
legacy avaient été créés. Résultat : plusieurs blocs partagent la même valeur de
`position`, et l'ordre d'affichage, pour les positions à égalité, dépend alors de l'ordre
d'insertion (rowid SQLite) plutôt que du numéro d'exercice voulu.

---

## 2. Positions avant correction (relevées sur la base staging réelle)

| id | titre | position en base | position déclarée dans `MC01_BLOCKS` (avant ce ticket) | créé au ticket |
|---|---|---|---|---|
| 135 | Exercice 9 — Lancement d'un programme (ordering) | **17** | 21 | #21 |
| 136 | Exercice 11 — Entrée, sortie ou mixte (classification) | **18** | 23 | #21 |
| 79 | Architecture d'un PC — Génère ton propre exercice (IA) | **16** | 25 | #10 |
| 80 | Fiche mémo — Architecture générale d'un PC | **17** | 26 | #10 |
| 81 | Examen final — Architecture générale d'un PC (…) | **18** | 27 | #10 |
| 82 | Examen final — Corrigé (réservé formateur, non publié) | **19** | 28 | #10 |
| 137–144 | Exercice 3/4/5/6/7/8/10/12 | 15,16,17,18,19,20,22,24 | (identique — créés directement avec cette valeur) | #29 |

Collisions observées (identique au constat du rapport de validation staging #29) :
`position=16` (AI_EXERCISE, Exercice 4), `position=17` (fiche mémo, Exercice 9, Exercice
5), `position=18` (examen, Exercice 11, Exercice 6), `position=19` (corrigé, Exercice 7).

Ordre public résultant, confirmé sur `https://jury-central.lodylands.com/uaa/ampcr-mc01/practice`
au moment de la validation staging #29 :

```
1, 2, 3, 4, 9, 5, 11, 6, 7, 8, 10, 12
```

---

## 3. Stratégie de correction

**La source de vérité (`MC01_BLOCKS`, `app/seed.py`) était déjà correcte** : ses 28
positions déclarées sont uniques et strictement séquentielles de 1 à 28, avec les
positions 13 à 24 correspondant exactement, dans l'ordre, aux exercices 1 à 12 (vérifié
explicitement par un nouveau test, voir § 8). Le problème n'était donc pas dans la
définition du contenu, mais dans le fait qu'un staging déjà seedé ne recevait jamais la
mise à jour de `position` pour les blocs déjà existants.

**Aucun tri spécial par numéro n'a été ajouté au template ou à la requête** — le système
continue de trier normalement, exclusivement, par `LessonBlock.position`
(`order_by="LessonBlock.position"`, inchangé).

**Correction retenue : migration scopée et explicite, jamais un mécanisme générique.**

Nouvelle constante `MC01_PRACTICE_REPOSITION_TITLES` (`app/seed.py`), qui liste
explicitement et uniquement les 6 titres concernés (Exercice 9, Exercice 11, le bloc IA,
la fiche mémo, l'examen et son corrigé). Nouveaux paramètres optionnels de `_seed_uaa` :
`reposition_titles` (le filtre par titre) et `repositioned` (compteur pour le résumé
affiché par `seed()`). Pour un bloc déjà existant dont le titre figure dans
`reposition_titles`, si sa `position` en base diffère de celle déclarée dans `blocks`
(`MC01_BLOCKS`), elle est resynchronisée en place — **rien d'autre n'est modifié**
(`content`, `title`, `is_published`, `space` restent strictement inchangés pour ces
blocs, et pour tout autre bloc du projet, cette logique n'est jamais invoquée : le
paramètre n'est passé qu'au seul appel `_seed_uaa(..., ampcr, MC01_CODE, ...)`).

### Pourquoi pas un mécanisme générique (comme `reclassified` pour `space`)

`space` n'est éditable nulle part dans l'admin (aucun champ `space` dans
`app/templates/admin_block_form.html`) : la resynchroniser pour **tous** les blocs à
chaque seed est donc sans risque, et c'est pourquoi le mécanisme `reclassified` (#22)
l'applique largement. `position`, à l'inverse, **est** éditable depuis l'admin
(`app/admin.py`, `block.position = position`) — un mécanisme générique équivalent pour
`position` écraserait silencieusement, à chaque `seed-db`, toute réorganisation manuelle
faite depuis l'admin sur n'importe quel bloc du site. C'est précisément l'invariant que
`_seed_uaa` garantit depuis l'origine (« jamais `content`, `title`, `position` ni
`is_published` d'un bloc déjà existant »). La liste explicite et bornée
(`MC01_PRACTICE_REPOSITION_TITLES`) limite l'effet à exactement les 6 blocs connus pour
avoir dérivé à cause de l'historique #10/#21/#29 — aucun autre bloc, présent ou futur,
n'est concerné.

---

## 4. Positions après correction

Après un `seed()` sur un staging dans l'état drifté ci-dessus, les 6 blocs sont
resynchronisés sur la valeur déjà déclarée dans `MC01_BLOCKS` :

| titre | position après migration |
|---|---|
| Exercice 9 | 21 |
| Exercice 11 | 23 |
| Architecture d'un PC — Génère ton propre exercice (IA) | 25 |
| Fiche mémo — Architecture générale d'un PC | 26 |
| Examen final — Architecture générale d'un PC (…) | 27 |
| Examen final — Corrigé (…) | 28 |

Les 28 positions de MC01 sont alors uniques, de 1 à 28, sans collision. Ordre public
résultant pour les 12 exercices PRACTICE :

```
1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
```

(vérifié par `tests/test_ticket37_mc01_practice_order.py::
test_seed_fixes_the_order_on_a_drifted_staging_state`, qui parse le HTML public de
`/uaa/ampcr-mc01/practice` après reconstruction fidèle de l'état staging drifté suivie
d'un seul `seed()`.)

---

## 5. Mécanisme de migration staging (sans reset-db)

Identique en esprit aux mécanismes des tickets #21/#22/#29 (`MC01_OBSOLETE_TITLES`,
`reclassified`) : purement additif, jamais de suppression ni de recréation de blocs, et
`seed-db` reste la seule commande à exécuter sur staging après déploiement — aucune
commande, script ou requête SQL supplémentaire n'est nécessaire. La correction est
intégrée directement dans `seed()`, donc appliquée automatiquement au prochain
`seed-db`.

---

## 6. Preuve d'idempotence

`tests/test_ticket37_mc01_practice_order.py::
test_seed_second_pass_is_idempotent_no_further_change` : reconstruit l'état drifté,
exécute un premier `seed()` (positions corrigées), capture les positions de tous les
blocs MC01, exécute un second `seed()`, et vérifie que **rien** n'a changé (aucune
position modifiée). `test_seed_second_pass_creates_no_duplicate_blocks` vérifie en plus
qu'aucun bloc n'est dupliqué au second passage (même nombre de blocs, mêmes titres,
tous uniques).

Confirmé également manuellement pour l'ensemble du seed complet (pas seulement MC01),
via `pytest` (voir § 8) : aucune régression sur MB32/MQ32/MQ34/MC02/MC03.

---

## 7. Vérifications de non-régression

Tous confirmés par les nouveaux tests (§ 8), sur l'état reconstruit puis migré :

- 12 exercices toujours présents.
- 12/12 restent `EDITORIAL_EXERCISE`.
- Les 12 restent `space=PRACTICE`.
- Aucun bloc `MARKDOWN` dont le titre contient « exercice » (aucun ancien Markdown
  réapparu).
- Correction locale (classification, Exercice 1) toujours fonctionnelle après
  repositionnement (`POST /practice/api/editorial/{id}/verify` → 200, `correct: true`).
- Le bloc `AI_EXERCISE` reste présent, seul, en PRACTICE (le mécanisme de correction IA
  lui-même n'a pas été touché par ce ticket — aucun changement dans `app/practice.py`,
  `app/editorial_ai_correction.py` ni `app/ai/`).
- Les 13 blocs COURSE (12 chapitres + fiche mémo) restent au nombre de 13.
- Les 2 blocs EXAM (énoncé + corrigé) restent présents, inchangés.
- Aucun contenu pédagogique modifié : `content`, `title`, `is_published`, `space`
  identiques avant/après migration pour tous les blocs (comparaison explicite dans
  `test_repositioning_never_changes_pedagogical_content`).

---

## 8. Tests ajoutés

`tests/test_ticket37_mc01_practice_order.py` (16 tests) :

1. `test_drifted_state_reproduces_the_reported_wrong_order` — l'état reconstruit
   reproduit fidèlement l'ordre public erroné observé en staging (1,2,3,4,9,5,11,6,7,8,
   10,12), preuve que la reconstruction du scénario est réaliste.
2. `test_drifted_state_has_position_collisions` — confirme les collisions avant
   correction.
3. `test_seed_fixes_the_order_on_a_drifted_staging_state` — un seul `seed()` corrige
   l'ordre public en 1→12 strict.
4. `test_seed_removes_all_position_collisions` — 0 collision après migration.
5. `test_fresh_seed_already_has_the_correct_order` — une base neuve (jamais seedée)
   affiche directement le bon ordre, sans migration nécessaire.
6. `test_seed_second_pass_is_idempotent_no_further_change` — 2ᵉ seed : 0 changement.
7. `test_seed_second_pass_creates_no_duplicate_blocks` — 2ᵉ seed : 0 doublon.
8. `test_repositioning_never_changes_pedagogical_content` — contenu strictement
   inchangé.
9. `test_twelve_exercises_still_present_and_structured_after_fix`
10. `test_course_blocks_unaffected_by_repositioning`
11. `test_exam_blocks_unaffected_by_repositioning`
12. `test_local_correction_still_works_after_fix`
13. `test_ai_exercise_block_still_present_and_unaffected`
14. `test_reposition_titles_scoped_to_exactly_the_drifted_blocks` — la liste des titres
    repositionnables reste exactement bornée aux 6 blocs connus (pas de mécanisme
    générique).
15. `test_declared_mc01_blocks_positions_are_already_sequential_and_unique` — la source
    de vérité `MC01_BLOCKS` ne contient aucune collision.
16. `test_exercise_positions_in_mc01_blocks_match_exercise_numbering` — les positions
    13 à 24 de `MC01_BLOCKS` correspondent exactement, dans l'ordre, aux exercices 1 à
    12.

La reconstruction de l'état drifté (`_build_drifted_staging_state`) reproduit non
seulement les valeurs de position historiques, mais aussi l'**ordre d'insertion réel**
(les blocs antérieurs à #29 insérés avant les 8 blocs ajoutés par #29), condition
nécessaire pour que le test reproduise fidèlement le départage par rowid SQLite observé
sur le staging réel — une première version de ce test, qui n'insérait que dans l'ordre de
`MC01_BLOCKS` (ordre pédagogique), ne reproduisait pas l'ordre erroné réellement observé ;
corrigée avant validation finale (voir historique de développement de ce ticket).

---

## 9. Résultat pytest

```
455 passed, 2 warnings in 19.58s
```

(439 avant ce ticket + 16 nouveaux). Les 2 warnings sont préexistants
(`httpx`/`anyio`), sans lien avec ce ticket.

---

## 10. Résultat Ruff

```
Found 36 errors.
```

Identique, fichier par fichier et règle par règle, à la base `develop` (comparé via un
worktree isolé). **0 nouvelle erreur.**

---

## 11. Fichiers modifiés

- `app/seed.py` — nouvelle constante `MC01_PRACTICE_REPOSITION_TITLES` ; `_seed_uaa`
  gagne les paramètres optionnels `reposition_titles`/`repositioned` (jamais appliqués
  par défaut, jamais à un autre appel que celui de MC01) ; `seed()` initialise le
  compteur et l'affiche dans son résumé si des blocs ont été repositionnés.
- `tests/test_ticket37_mc01_practice_order.py` (nouveau) — 16 tests.
- `docs/claude-reports/2026-09-17_ticket-37_mc01-practice-order.md` — ce rapport.

Aucune modification de `app/main.py`, `app/models.py`, `app/templates/`, du moteur de
correction locale/IA, ni de la table `jury_central.db` réelle (confirmé inchangée par
`md5sum` avant/après ce ticket — toutes les vérifications se sont faites sur des bases
SQLite temporaires isolées, via `pytest`, jamais sur le fichier réel).

---

## Statut

Implémentation, tests, documentation terminés. `pytest -q` : 455 passed. Ruff : 36
erreurs, 0 nouvelle. `jury_central.db` réel non modifié. Prêt pour commit/push. **Aucun
merge, aucun déploiement.**
