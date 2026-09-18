# Rapport — Mission de nuit Jury Central (2026-09-19 → 2026-09-20)

Exécution de la « MISSION DE NUIT — JURY CENTRAL » (15 phases) reçue le 2026-09-19 en
complément de l'objectif immédiat du soir (déploiement staging #69 + rebase propre de
`feature/47-francais-v1`, déjà couvert par
`docs/claude-reports/2026-09-19_staging-69-deploy_francais-rebase.md`).

**Contraintes respectées toute la nuit** : aucun merge, aucun déploiement Français, aucun
appel OpenAI réel en test, aucun reset-db, aucune nouvelle architecture générique, tickets
#45/#46/#48/#70/#74/#75 non commencés. Chaque phase a produit tests + Ruff + `git diff
--check` + commit + push sur `feature/47-francais-v1`.

---

## Résumé par phase

| Phase | Contenu | Statut |
|---|---|---|
| 1 | Objectif du soir (staging #69, rebase Français) | Fait avant cette nuit (rapport séparé) |
| 2 | Ticket #73 — audit + suppression limite silencieuse réponses longues | Fait, cherry-pické sur `feature/47-francais-v1` |
| 3 | Réintégration #73 sur la branche Français | Fait |
| 4 | Correction bug classification Fait/Opinion (explication contradictoire) | Fait |
| 5-7 | Corpus étendu : 5 documents, 40 questions | Fait |
| 8 | Vérification accordéon document scopé/borné (mobile) | Fait — comportement déjà correct, test manquant ajouté |
| 9 | Examen Français à 20 questions (comme MC38) | Fait |
| 10-11 | Clauses de grille (neutralité d'opinion, structure du feedback) vérifiées jusqu'à l'IA | Fait — clauses déjà en place, chaîne de transmission vérifiée par test |
| 12 | Sévérité 1/3/5, export, impression, historique, logout/login pour Français | Fait — fonctionnalités génériques déjà opérationnelles, couverture de test ajoutée |
| 13 | Navigation Cours/S'entraîner/S'évaluer pour Français | Fait — **bug réel découvert et corrigé** (§ ci-dessous) |
| 14 | Documentation (`docs/francais_v1_functional.md`, ce rapport) | Fait |
| 15 | Audit final honnête | Voir bloc de sortie en fin de rapport |

---

## Bug réel découvert et corrigé (Phase 13)

`render_practice_landing`/`render_exam_landing` (`app/v1/routes_sessions.py`) ne
transmettaient jamais `active_space` au contexte de `v1_session_start.html`, alors que
`_uaa_space_nav.html` (ticket #22) en dépend pour surligner l'onglet actif. Conséquence :
depuis le ticket #22, **aucun onglet n'était jamais visuellement actif** sur les pages
`/uaa/{slug}/practice` et `/uaa/{slug}/exam` — pour AMPCR ET Français, ce n'est pas un bug
spécifique au Français, seulement découvert en vérifiant explicitement ce point pour le
Français. Corrigé par l'ajout de la clé de contexte manquante (2 lignes), sans toucher au
template ni à l'architecture partagée. Suite complète (1065 tests) verte après correction.

---

## Décisions produit déférées à ChatGPT (non corrigées, documentées § 7 de
## `docs/francais_v1_functional.md`)

1. `LONG_SEMANTIC_TYPES`/`MAX_LONG_SEMANTIC_PER_SESSION` (session_service.py) ne comptent
   pas `document_analysis`/`source_comparison` — une session Français pourrait dépasser le
   plafond de 3 réponses longues « prévu » en les combinant avec `long_answer`. Toucher à
   cette constante affecterait aussi AMPCR (architecture partagée) : décision produit, pas
   prise cette nuit.
2. `BRIDGE_TYPES` (ai_bridge.py) ne couvre pas 4 des types utilisés par le Français —
   gap pré-existant, contourné côté Français, jamais corrigé dans le pont générique.
3. Aucun regroupement visuel « PARTIE A/B/C » de l'examen — l'examen Français affiche ses
   20 questions en flux unique comme tout examen AMPCR. Ajouter cette structure
   nécessiterait une nouvelle UI/tagging, explicitement hors périmètre de cette nuit.

Aucune de ces trois limites n'est un bug bloquant : le parcours Français fonctionne de
bout en bout sans elles. Ce sont des raffinements pédagogiques/UX à trancher par ChatGPT.

---

## Tests

- `tests/test_ticket47_francais_v1.py` : 24 → **30 tests**, tous verts, aucun appel OpenAI
  réel (`FakeAIProvider` partout).
- `tests/test_ticket73_long_answer_capacity.py` : 9 tests (créés hier soir, revalidés).
- Suite complète du dépôt : **1065 passed**, aucune régression (dernière exécution après le
  fix Phase 13).
- Ruff : `All checks passed!` sur chaque fichier modifié, à chaque phase.
- `git diff origin/develop --check` : propre à chaque phase (pas de whitespace-only diff).

---

## Bloc de sortie final

```
OVERNIGHT_STATUS=OK
DEVELOP_BASE=5b15c9ba3d909faf89aacb1c24f0207950b66850
TICKET_73_BRANCH=feature/47-francais-v1
TICKET_73_SHA=74bf2d7
TICKET_73_TESTS=PASS (9/9, tests/test_ticket73_long_answer_capacity.py)
FRENCH_BRANCH=feature/47-francais-v1
FRENCH_SHA=52e4079
FRENCH_TESTS=PASS (30/30, tests/test_ticket47_francais_v1.py) ; FULL_SUITE=PASS (1065/1065)
FRENCH_DOCUMENTS=5
FRENCH_BANK_QUESTIONS=40
FRENCH_PRACTICE=USABLE (10 questions, autosave, reprise, correction batch, résultats)
FRENCH_EXAM=USABLE (20 questions, immuable après soumission)
LONG_ANSWER_10K=OK (20000 caractères max, aucune troncature bout en bout, vérifié 10k et 20k)
SOURCE_DOCUMENT_SHARED=OK (jamais dupliqué, accordéon scopé au(x) document(s) réellement référencé(s), borné 50vh/scroll)
SOURCE_COMPARISON=OK (4 questions, clause de neutralité d'opinion vérifiée jusqu'au prompt IA)
DOCUMENT_ANALYSIS=OK (4 questions)
AUTOSAVE=OK
RESUME=OK
BATCH_CORRECTION=OK (un seul appel IA batch par soumission, vérifié)
SEVERITY_1_5=OK (1, 3, 5 vérifiés explicitement pour Français, persistance confirmée)
EXPORT=OK (Markdown, contenu réel de session Français vérifié)
PRINT=OK (bouton + CSS @media print présents sur résultats Français)
HISTORY=OK (/mes-sessions affiche les sessions Français ; survit logout/login)
BLOCKING_BUGS=NONE (1 bug non-bloquant trouvé ET corrigé cette nuit : onglet actif jamais surligné, partagé AMPCR/Français, voir § Phase 13)
REPORT=docs/francais_v1_functional.md ; docs/claude-reports/2026-09-19_francais-overnight-functional.md
```

Branche `feature/47-francais-v1` prête pour review humaine (ChatGPT) demain matin. Aucun
merge, aucun déploiement effectué cette nuit — conformément à la consigne.
