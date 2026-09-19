# Ticket #74 — Lien vers le cours à relire

**Branche** : `feature/74-course-recommendations`, base `develop` (486f35c, PR #81
mergée). Aucun merge, aucun déploiement effectué.

---

# Ce qui a été fait

Réutilise directement `course_title`/`course_slug` déjà exposés par `_build_results_rows`
(ticket #79 § 13, prévus explicitement « pour qu'un futur ticket (#74) puisse ajouter un
bouton sans nouvelle architecture ») — complété d'un `course_code` (ex. « MC17 »).

Nouvelles fonctions pures (`app/v1/routes_sessions.py`) :

- `_is_incorrect_or_partial(row)` : vrai si `feedback.correct` n'est pas strictement
  `True` — couvre à la fois « faux » et « partiel » (crédit partiel #70 § B), et traite
  une question jamais corrigée comme « à revoir » plutôt que de l'ignorer silencieusement.
- `_courses_to_review(results, limit=5)` : agrège les questions incorrectes/partielles
  par UAA, triées par nombre d'erreurs décroissant, limitées à 5 (3-5 demandé par le
  ticket). Ignore les questions sans UAA connue (rien de concret à « relire »).

**Par question incorrecte/partielle** (résultats, export, impression) :
```
Cours concerné : MCxx — <titre>
[ Relire le cours ]
```
**Synthèse globale**, affichée si au moins un cours est concerné :
```
Cours à relire en priorité
1. MC17 — Subnetting 1 — 3 erreurs
2. MC15 — Câblage Ethernet — 1 erreur
```

Le bouton « Relire le cours » pointe vers `/uaa/{slug}` — la page Cours, déjà publique
(aucune route nouvelle). Inclus dans l'export Markdown (`# Cours à relire en priorité` +
`*Cours concerné : ...*` par question) et à l'impression : la référence textuelle
(« Cours concerné », la liste de synthèse) reste visible à l'impression, seuls les boutons
interactifs sont masqués (`d-print-none`) — même principe que le panneau documents (#77).

---

# Architecture générique (Français inclus)

`_build_results_rows`/`_is_incorrect_or_partial`/`_courses_to_review` ne contiennent
aucune référence à l'Informatique — dérivés uniquement de `SessionQuestion.question_version.question.uaa`,
déjà partagé par toutes les matières. Une session Français mélangeant plusieurs UAA (si
un jour c'est le cas) bénéficierait de la même fonctionnalité sans code supplémentaire.

---

# Limite assumée, non implémentée (décision documentée, pas une nouvelle architecture)

Le ticket mentionne aussi :
```
À revoir :
<micro-notion>
```
plus granulaire qu'un cours entier (ex. « masques de sous-réseau » au lieu de « MC17 »).
**Aucune donnée structurée de ce niveau n'existe** dans le modèle actuel — une `Question`
n'est rattachée qu'à une `UAA`, jamais à une micro-notion distincte. Implémenter cela
demanderait soit un nouveau champ édité par ChatGPT (contenu pédagogique, hors du
périmètre de Claude), soit une extraction automatique non fiable (hors périmètre du
projet, § principes du ticket #69 : « pas de NLP côté serveur »). Seul le rattachement au
COURS (déjà existant) est utilisé — documenté ici plutôt qu'inventé.

---

# Tests

Nouveau fichier `tests/test_ticket74_course_recommendations.py` (10 tests, aucun appel
OpenAI réel) :

- Unité : `_is_incorrect_or_partial` (faux/jamais corrigé → vrai, correct → faux) ;
  `_courses_to_review` (tri par nombre d'erreurs, limite à 5, ignore les lignes sans UAA
  connue, ignore les réponses correctes).
- HTTP réel : lien par question affiché pour une session avec réponses fausses ; synthèse
  « Cours à relire en priorité » affichée avec le bon décompte ; export Markdown contient
  la synthèse et la référence par question ; impression — référence texte visible, bouton
  masqué.
- Non-régression : aucune UI « à revoir » si toutes les réponses sont correctes (vérifié
  au niveau service, `_build_results_rows`/`_courses_to_review`).

Suite complète du dépôt : **1104 passed**. Ruff : **0 nouvelle erreur** (36
pré-existantes, hors fichiers touchés, confirmé par comparaison directe avec `develop`).

---

# Fichiers modifiés

- `app/v1/routes_sessions.py` — `course_code` ajouté aux lignes de résultat,
  `_is_incorrect_or_partial`, `_courses_to_review`, câblés dans `view_session` et
  `_build_session_export_markdown`.
- `app/templates/v1_session_results.html` — synthèse « Cours à relire en priorité » +
  lien par question incorrecte/partielle.
- `tests/test_ticket74_course_recommendations.py` — nouveau, 10 tests.
