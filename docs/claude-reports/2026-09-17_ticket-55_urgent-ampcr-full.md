# Ticket #55 — URGENT AMPCR complet MC01→MC38 (recadré, <48h avant examens)

**Date** : 2026-09-17
**Branche** : `feature/55-urgent-ampcr-full`

---

## 0. Deux cadrages successifs dans le même ticket

Ce ticket a été livré en deux temps, dans la même session :

1. **Cadrage initial** : MVP MC01 seul (Informatique), condensant #41/#42/#43/#44/#24/#25.
2. **Recadrage explicite de ChatGPT**, reçu en cours d'implémentation : périmètre étendu
   à l'intégralité du programme AMPCR (MC01→MC38), avant tout démarrage du Français.

Le recadrage est arrivé après que l'implémentation MC01 avait déjà commencé sur la
branche `feature/55-urgent-mvp-informatique`. Cette branche a été **renommée** en
`feature/55-urgent-ampcr-full` (même historique de commits, aucun travail perdu) plutôt
que recréée depuis zéro, car tout le travail MC01 (moteur de session, bridge IA, routes,
templates) est directement réutilisé — sans aucune modification d'architecture — pour
les 37 autres mini-cours. Ce rapport couvre le périmètre final recadré.

---

## 1. Ascendance Git — corrigée après rebase sur `develop`

À la livraison initiale de ce ticket, `origin/develop` était encore à `fe6a19b` (merge du
ticket #39) et ne contenait pas le commit `#40` ; le SHA `f4a6e44810293577162971ad15d2274d05b40874`
annoncé par le recadrage n'existait alors dans aucune branche du dépôt. La branche avait
donc été construite directement sur `feature/40-v1-question-engine` (commit `2ac1d3d`),
signalé comme écart transparent dans la première version de ce rapport.

Depuis, `#40` a été mergé dans `develop` (PR #54, merge commit `f4a6e44`, confirmé
ancêtre de `origin/develop` par `git merge-base --is-ancestor`). La branche
`feature/55-urgent-ampcr-full` a été **rebasée** sur `origin/develop` :

- `git rebase origin/develop` s'est effectué **sans conflit** : Git a reconnu que le
  commit `2ac1d3d` (contenu de `#40`) était strictement identique dans les deux
  historiques et l'a supprimé de la branche sans le dupliquer ni le rejouer.
- Résultat : `feature/55-urgent-ampcr-full` descend directement de `origin/develop`
  (`f4a6e44`), un seul commit fonctionnel `#55` au-dessus (ancien SHA `d69aed3` →
  nouveau SHA `b837d8f`), aucun commit `#40` dupliqué.
- Aucune modification fonctionnelle : `git diff origin/develop...HEAD --stat` liste
  exactement les 25 fichiers du commit `#55` d'origine ; `app/v1/question_engine.py` et
  `app/v1/question_types.py` (propriété de `#40`) n'apparaissent pas dans ce diff.
- Revalidation complète sur l'état rebasé : `pytest -q` → 819 passed (identique
  avant/après rebase) ; Ruff → 36 erreurs, 0 nouvelle ; `git diff --check
  origin/develop...HEAD` → propre.
- `git push --force-with-lease origin feature/55-urgent-ampcr-full` (seule méthode
  utilisée, jamais `--force` simple), car cette branche feature venait d'être rebasée.

---

## 2. Ce qui a été livré

Résumé fonctionnel complet dans `docs/ampcr_v1_functional.md` (tableau MC01→MC38,
détail banque/génération/correction, limites assumées). Points clés :

- **38 contextes pédagogiques** (`app/v1/ampcr_plan.py`) couvrant MC01 à MC38 sans trou :
  riches pour MC01-03 (contenu déjà rédigé, tickets #10/#12/#14), minimaux (titre +
  consigne « reste dans ton sujet ») pour MC04-38, faute de contenu pédagogique détaillé
  existant dans le dépôt pour ces 35 mini-cours (voir § 2 de `ampcr_v1_functional.md` —
  aucune notion technique n'a été inventée par Claude, conformément à la règle du
  projet).
- **Moteur de session unique** (`app/v1/session_service.py`) réutilisé identiquement par
  les 38 mini-cours ET par le parcours global AMPCR : sélection banque → composition
  diversifiée (≤3 questions sémantiques longues/10) → génération complémentaire en UN
  seul appel IA si besoin → repli sur répétition si la banque et l'IA sont toutes deux
  insuffisantes → jamais de crash, session créée avec ce qui est disponible (ou 503
  explicite si strictement rien n'est disponible).
- **Bridge IA** (`app/v1/ai_bridge.py`) : réutilise tel quel le moteur de génération/
  correction #23 déjà validé et déployé en staging, plutôt que d'en reconstruire un
  second contre le registre #40 — décision de minimisation de risque avant l'échéance.
- **Banque** (`app/v1/bank.py`) : import idempotent des 12 questions historiques MC01
  (`generation_source=IMPORTED`) ; sélection préférant les questions non vues
  (`UserQuestionHistory`) avec repli sur les questions déjà vues ; persistance des
  questions générées après validation stricte par le registre #40
  (`validate_content()`), jamais de solution exposée publiquement.
- **Colonne `Question.uaa_id`** (migration additive dans `ensure_schema_migrations()`) :
  nécessaire car les 38 mini-cours partagent un seul `Module` AMPCR — sans elle, aucune
  isolation de banque par mini-cours n'était possible.
- **Routes** (`app/v1/routes_sessions.py`) : par mini-cours (`/uaa/{slug}/practice`,
  `/uaa/{slug}/exam`) ET globales (`/modules/ampcr/practice` — 10 questions,
  `/modules/ampcr/exam` — 20 questions), plus l'API JSON d'autosave
  `POST /api/v1/sessions/{id}/answers/{session_question_id}` (réponse strictement
  `{"saved": true}`, jamais de correction).
- **UX mobile-first** : une question à la fois, compteur « Question N/10 », navigation
  Précédent/Suivant, autosave silencieux à chaque changement, aucune correction visible
  avant la soumission finale, bouton unique « Terminer et corriger » / « Terminer
  l'évaluation » (avec confirmation explicite pour l'examen).
- **Reprise de session** : une session `IN_PROGRESS` existante est proposée en priorité
  (entraînement et examen) ; l'examen empêche explicitement la création d'un doublon
  concurrent pour le même mini-cours.
- **Correction globale** : types déterministes corrigés localement (aucun réseau), tous
  les types nécessitant l'IA regroupés en **un seul** appel batch
  (`correct_semantic_batch` via `app.ai.questionnaire.correct_questionnaire`, #23,
  inchangé) ; repli local + message explicite « correction indisponible » si le
  fournisseur IA échoue ou n'est pas configuré, au lieu d'un crash serveur.
- **Rendu legacy préservé** : `app.editorial_exercise`, `uaa_practice.html`/
  `uaa_exam.html` restent inchangés et continuent de servir toute UAA non-AMPCR
  (Mathématiques, futur Français) ; seules les UAA du plan AMPCR délèguent au nouveau
  moteur (`app/main.py`, test `get_plan_by_slug(uaa.slug) is not None`).
- **Contenu historique non supprimé** : les 12 exercices MC01 restent en base
  (`app.editorial_exercise`/`LessonBlock`), simplement plus rendus par la nouvelle route ;
  ils servent de source à l'import banque.
- **35 UAA stub créées** (`app/seed.py`, `AMPCR_STUB_MODULE_BLOCKS`) pour MC04-38 : un
  seul bloc COURS honnête (« contenu détaillé pas encore rédigé ») par mini-cours, pour
  que chaque UAA existe et soit publique dès maintenant, sans jamais fabriquer un faux
  cours détaillé à la place de l'équipe pédagogique.

---

## 3. Fichiers

**Nouveaux** :
- `app/v1/ai_bridge.py`, `app/v1/ampcr_plan.py`, `app/v1/bank.py`,
  `app/v1/session_service.py`, `app/v1/routes_sessions.py`
- `app/templates/v1_session_start.html`, `v1_session_question.html`,
  `v1_session_submit_confirm.html`, `v1_session_results.html`
- `docs/ampcr_v1_functional.md`
- `docs/claude-reports/2026-09-17_ticket-55_urgent-ampcr-full.md` (ce rapport)
- `tests/test_ticket55_urgent_ampcr_full.py` (29 tests)

**Modifiés** :
- `app/v1/models.py` (colonne `Question.uaa_id` + index composite)
- `app/database.py` (migration additive de la colonne)
- `app/seed.py` (35 UAA stub MC04-38)
- `app/main.py` (délégation conditionnelle practice/exam vers le nouveau moteur pour les
  UAA du plan AMPCR)
- `tests/test_admin_content_hierarchy.py` (comptage UAA/blocs mis à jour)
- `tests/test_informatique_mc01.py`, `mc02.py`, `mc03.py` (assertions sur la nouvelle
  page d'atterrissage au lieu du rendu legacy)
- `tests/test_ticket17_no_regression.py`, `ticket21_no_regression.py`,
  `ticket22_no_regression.py`, `ticket29_no_regression.py`,
  `ticket37_mc01_practice_order.py` (maintenance requise par le changement de rendu
  intentionnel des routes `/uaa/ampcr-mc0{1,2,3}/{practice,exam}` ; les vérifications au
  niveau des données, elles, sont inchangées — `ticket37` vérifie désormais l'ordre
  directement en base plutôt que par scraping HTML, l'ordre n'étant plus affiché
  publiquement sur MC01)

---

## 4. Tests

`tests/test_ticket55_urgent_ampcr_full.py` (29 tests) couvre : 38 entrées `AMPCR_PLAN`
sans trou ; 38 UAA seedées et publiées ; rejet anonyme (par mini-cours et global) ;
cours toujours public ; création de session practice/exam pour des mini-cours
représentatifs (MC01/MC17/MC38, MC01/MC25) avec exactement 10 questions ; génération
bornée à un seul appel même banque partiellement peuplée ; session créée depuis une
banque partielle sans IA disponible ; échec propre (503) si banque vide ET IA
indisponible ; aucune fuite de correction/solution avant soumission (vérifié sur les 10
questions, nombreux noms de champs privés) ; autosave persistant ; API JSON ne révèle
jamais la correction ; reprise de session ; examen empêche un doublon concurrent ;
soumission déclenche correction locale + un seul appel batch IA ; session `COMPLETED`
immuable (409 sur autosave tardif) ; résultats affichent la réponse de l'utilisateur ;
practice et exam distincts ; parcours global practice (10q) et exam (20q) ; contenu
MC01-03 non affecté ; contenu legacy MC01 préservé en base ; HTML mobile (viewport,
absence de bouton de correction par question) ; import banque idempotent.

Aucun appel OpenAI réel : `FakeAIProvider` (monkeypatch) partout où une génération/
correction IA est exercée.

---

## 5. Résultat pytest (suite complète)

```
819 passed, 2 warnings in 146.01s (0:02:26)
```

(790 avant ce ticket + 29 nouveaux — `tests/test_ticket55_urgent_ampcr_full.py`). Les 2
warnings sont préexistants (httpx/anyio), sans lien avec ce ticket.

---

## 6. Résultat Ruff

```
Found 36 errors.
```

Identique à la base (`app/admin.py`/`app/main.py` B008 Depends, `tests/conftest.py`
RUF100, `tests/test_rich_content.py` I001 — tous préexistants, aucun dans les fichiers
de ce ticket). **0 nouvelle erreur.** Ajustements effectués pendant le développement :
import du registre de types manquant dans `bank.py` (nécessaire — le registre #40 se
peuple par effet de bord à l'import), simplification RUF034 (if/else redondant) et
SIM102 (condition imbriquée inutile dans `start_exam_session`).

---

## 7. `git diff --check`

```
$ git diff --check
(aucune sortie, exit code 0)
```

---

## 8. Non-régression

- MC01/MC02/MC03 : cours (rendu public) inchangé ; contenu historique MC01 toujours en
  base, sert désormais de source d'import banque.
- Mathématiques : totalement non affecté (aucune UAA du plan AMPCR).
- 14 tests préexistants ont nécessité une mise à jour d'assertions (rendu HTML changé
  intentionnellement par ce ticket sur les routes practice/exam des UAA AMPCR) — jamais
  de perte de couverture fonctionnelle, uniquement un déplacement de la vérification du
  rendu HTML legacy vers le nouveau rendu (ou, pour `ticket37`, vers une vérification
  directe en base quand l'information n'est plus exposée publiquement).

---

## 9. Limites assumées (§19-20 du recadrage)

- **Banque pré-chargée uniquement pour MC01** (12 questions importées) ; MC02-38
  démarrent à vide et comptent sur la génération à la demande (1 appel IA/session,
  validé par #40). Détaillé et justifié dans `docs/ampcr_v1_functional.md` § 4 — produire
  manuellement ~185 questions éditoriales pour 37 mini-cours dans le délai n'était pas
  réaliste, et l'aurait forcé à inventer du contenu technique non vérifié (risque
  explicitement écarté par la règle du projet).
- **Contexte pédagogique minimal (titre seul) pour MC04-38** — aucune notion technique
  détaillée n'a été rédigée par Claude ; ce contenu reste à produire par l'équipe
  pédagogique.
- **Composition du parcours global** ne pondère pas encore précisément par catégorie
  (hardware/systems/réseaux/...) — tirage parmi toutes les questions déjà taguées,
  plusieurs sessions successives restant nécessaires pour couvrir tout le programme
  (explicitement accepté par le recadrage).
- Hors périmètre, non commencé : Français, #45 (notation avancée), #46 (admin complet),
  #48 (visuels avancés), paiement, quotas réels, analytics avancées.

---

## 10. Prochaines dépendances

- Merge de `#40` dans `develop` (préalable non bloquant pour ce ticket, mais à faire
  avant toute mise en production propre — voir § 1).
- Rédaction du contenu pédagogique détaillé MC04-38 (objectifs, notions autorisées/hors
  scope) par l'équipe pédagogique, pour enrichir `app/v1/ampcr_plan.py` sans toucher au
  moteur.
- #47 (Français) : peut réutiliser le même moteur de session (`session_service.py`,
  `routes_sessions.py`) une fois le plan et les contextes Français fournis par
  ChatGPT — aucune reconstruction d'architecture nécessaire.

---

## Statut

Implémentation, tests et documentation terminés. `pytest -q` (suite complète) : 819
passed. Ruff : 36 erreurs, 0 nouvelle. `git diff --check` : propre. Aucun appel OpenAI
réel. Aucune modification de `jury_central.db` (uniquement des bases SQLite temporaires
isolées pour la vérification manuelle). Prêt pour commit/push. **Aucun merge, aucun
déploiement.** Le Français, #45, #46 et #48 n'ont pas été démarrés.
