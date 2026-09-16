# Ticket #22 — Refonte UX : séparer Cours, S'entraîner et S'évaluer

**Date** : 2026-09-16
**Branche** : `feature/22-separation-cours-practice-exam`
**Ticket GitHub** : #22 « Refonte UX — séparer Cours, Entraînement et Évaluation »
**Décisions ChatGPT complémentaires** (classification, routes, MC01/MC02/MC03) intégrées
intégralement à l'implémentation ci-dessous.

---

## 1. Résumé

Une page de module ne mélange plus théorie, exercices et examen dans un même flux. Chaque
UAA expose désormais trois espaces génériques, identiques pour toutes les matières :
**Cours** (`/uaa/{slug}`), **S'entraîner** (`/uaa/{slug}/practice`), **S'évaluer**
(`/uaa/{slug}/exam`). La classification d'un bloc est un champ explicite et persistant
(`LessonBlock.space`), jamais déduite du titre, de la position ou du type à l'exécution.
Le contenu existant (MC01/MC02/MC03) est reclassé explicitement dans `app/seed.py`, avec
un mécanisme de migration testé permettant à un staging déjà seedé de se mettre à jour
sans `reset-db`. Aucun contenu supprimé, aucune régression de matière.

**RUFF_NOUVELLES_PAR_#22 = 0**, **PYTEST = 288 passed** (272 + 16 nouveaux).

---

## 2. Modèle : `LessonBlock.space`

`app/models.py` — nouvel enum `BlockSpace` (`COURSE`, `PRACTICE`, `EXAM`) et nouveau champ :

```python
class BlockSpace(str, enum.Enum):
    COURSE = "course"
    PRACTICE = "practice"
    EXAM = "exam"

class LessonBlock(Base):
    ...
    space: Mapped[BlockSpace] = mapped_column(
        Enum(BlockSpace), default=BlockSpace.COURSE, server_default="COURSE"
    )
```

Conformément à la décision explicite de ChatGPT :
- `space` est un champ **explicite et persistant**, indépendant de `BlockType` (nature
  technique du bloc, ex. `MARKDOWN`, `EDITORIAL_EXERCISE`) — un même `BlockType` peut
  appartenir à des espaces différents selon le contenu (par exemple un bloc `MARKDOWN` de
  théorie est COURSE, un bloc `MARKDOWN` d'exercice est PRACTICE).
- Valeur par défaut **rétrocompatible** : `COURSE`, pour tout bloc existant avant ce
  ticket.
- **Aucune heuristique permanente** basée sur le titre : `classify_block_title()`
  (`app/card_kind.py`) continue d'exister mais reste strictement **présentationnelle**
  (choix d'icône/couleur de carte) — elle n'est ni utilisée ni consultée pour décider de
  l'espace d'un bloc.

---

## 3. Migration de schéma sans Alembic

Le projet n'a pas de système de migrations (`README.md`, `docs/development.md`). Ajouter
une colonne à une table SQLite déjà existante (staging déjà seedé) n'est **pas** couvert
par `Base.metadata.create_all()`, qui ne crée que les tables manquantes et ne modifie
jamais une table existante — c'est la première fois que ce ticket ajoute une colonne à un
modèle déjà déployé (les tickets précédents n'ajoutaient que des membres d'enum, stockés
en `VARCHAR` sans contrainte).

Nouvelle fonction `app.database.ensure_schema_migrations()`, appelée après
`Base.metadata.create_all()` dans `app/main.py` (démarrage) et `app/seed.py::seed()` :

```python
def ensure_schema_migrations() -> None:
    with engine.begin() as connection:
        table_exists = connection.exec_driver_sql(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='lesson_blocks'"
        ).fetchone()
        if table_exists is None:
            return
        columns = {row[1] for row in connection.exec_driver_sql(
            "PRAGMA table_info(lesson_blocks)"
        ).fetchall()}
        if "space" not in columns:
            connection.exec_driver_sql(
                "ALTER TABLE lesson_blocks ADD COLUMN space VARCHAR(10) "
                "NOT NULL DEFAULT 'COURSE'"
            )
```

Idempotente (vérifie la colonne via `PRAGMA table_info` avant d'agir), sans effet sur une
table déjà à jour ou absente, strictement additive (aucune ligne ni colonne existante
touchée). `'COURSE'` (nom du membre Python, pas sa valeur `"course"`) correspond
exactement à ce que SQLAlchemy `Enum(BlockSpace)` écrit pour une nouvelle ligne — même
convention déjà observée pour `BlockType` (ticket #17).

---

## 4. Migration explicite du contenu connu (MC01/MC02/MC03)

Décision de ChatGPT : migration explicite, pas d'heuristique. Chaque entrée de
`MC01_BLOCKS`/`MC02_BLOCKS`/`MC03_BLOCKS` (`app/seed.py`) porte désormais une clé
`"space"` écrite en dur, selon la règle transmise :

| Contenu | Espace |
|---|---|
| Plan, sections « — Cours »/« — Exemple », vocabulaire, fiche mémo | COURSE |
| Exercices Markdown (« — Exercices (...) »), `EDITORIAL_EXERCISE`, `AI_EXERCISE` (« Génère ton propre exercice ») | PRACTICE |
| Examen final + corrigé | EXAM |

Répartition réelle obtenue (vérifiée par test, § 8) :

| Mini-cours | COURSE | PRACTICE | EXAM | Total |
|---|---|---|---|---|
| MC01 | 13 | 8 | 2 | 23 |
| MC02 | 18 | 4 | 2 | 24 |
| MC03 | 19 | 4 | 2 | 25 |

**Mathématiques (MB32 UAA1/UAA2)** : reste COURSE par défaut, conformément à la décision
explicite de ChatGPT (« aucune classification spécifique n'est actuellement nécessaire »).
Ses blocs `quiz`/`generated_exercise` restent donc pour l'instant visibles sur la page
Cours — limite assumée, documentée en § 9, et non une omission.

---

## 5. Migration du contenu déjà seedé (staging) sans reset-db

Même problème de fond qu'au ticket #21 (voir
`docs/claude-reports/2026-09-16_ticket-21_classification-ordering.md`, § 6), mais cette
fois sur une **métadonnée** plutôt que sur le contenu d'un bloc : `_seed_uaa()` ne modifie
jamais un bloc déjà existant (matché par titre). Sur un staging seedé avant ce ticket, la
colonne `space` vient d'être ajoutée par `ensure_schema_migrations` avec sa valeur par
défaut **COURSE partout, y compris pour les exercices et l'examen déjà seedés** — sans
action supplémentaire, ce contenu resterait donc affiché sur la page Cours après
déploiement, alors qu'il devrait apparaître sur S'entraîner/S'évaluer.

**Solution** : `_seed_uaa()` accepte un nouveau paramètre optionnel `reclassified`. Pour
chaque bloc déjà existant (matché par titre), si sa valeur `space` en base diffère de
celle désormais définie dans `app/seed.py`, elle est mise à jour **en place** —
uniquement ce champ, jamais `content`, `title`, `position` ni `is_published` :

```python
existing_block = existing_by_title.get(block_data["title"])
if existing_block is not None:
    kept["blocks"] += 1
    if reclassified is not None:
        target_space = block_data.get("space", BlockSpace.COURSE)
        if existing_block.space != target_space:
            existing_block.space = target_space
            reclassified["blocks"] += 1
```

`seed()` passe `reclassified={"blocks": 0}` à tous les appels `_seed_uaa()` (MB32, MC01,
MC02, MC03) et affiche le compteur final (`Reclassé : N bloc(s)`) — 0 sur une base déjà à
jour, non nul sur un staging pré-#22, jamais sur Mathématiques (déjà COURSE partout).

**Aucun `reset-db` n'est nécessaire ni n'a été exécuté.** Ce scénario exact — un staging
qui vient de recevoir la colonne `space` (COURSE partout) migré par un seul `seed()` — est
reproduit et vérifié par
`test_staging_seeded_before_ticket_22_is_reclassified_without_reset`
(`tests/test_ticket22_no_regression.py`), **et** validé manuellement de bout en bout sur
un serveur réel (base SQLite temporaire, jamais `jury_central.db`) :

```
$ sqlite3 db "UPDATE lesson_blocks SET space = 'COURSE';"
$ python -m app.seed
  Conservé (déjà présent, non modifié) : ... 135 bloc(s)
  Reclassé (espace pédagogique COURSE/PRACTICE/EXAM mis à jour, contenu inchangé) : 22 bloc(s)
$ sqlite3 db "SELECT space, COUNT(*) FROM lesson_blocks GROUP BY space;"
COURSE|113
EXAM|6
PRACTICE|16
```

22 = 16 PRACTICE + 6 EXAM (MC01+MC02+MC03), exactement la répartition attendue.

**Procédure de déploiement réelle** : identique aux tickets précédents —
`scripts/deploy_staging.sh` puis `seed-db`. Aucune étape manuelle supplémentaire.

---

## 6. Routes génériques

Conformes à la cible validée par ChatGPT :

```
GET /uaa/{slug}            -> espace Cours (blocs space=COURSE)
GET /uaa/{slug}/practice   -> espace S'entraîner (blocs space=PRACTICE)
GET /uaa/{slug}/exam       -> espace S'évaluer (blocs space=EXAM)
```

Aucune route spécifique par cours (`/mc01/practice` etc.) — les trois routes sont
génériques, définies une seule fois dans `app/main.py`, valables pour toutes les
matières/UAA. Même comportement 404 que l'ancienne route unique (UAA introuvable ou non
publiée) sur les trois routes.

**Refactorisation** : la logique de rendu d'un bloc (déjà généreuse : Markdown, YouTube,
exercices générés, IA, éditorial, quiz — avec regroupement de quiz en groupe) a été
extraite dans `app/main.py::_render_lesson_blocks(blocks)`, une fonction pure qui ne sait
rien de l'espace appelant — le tri par `space` a lieu **avant** l'appel, dans chacune des
trois routes (`_space_blocks(uaa, BlockSpace.X)`). Aucune duplication de logique
d'affichage par type de bloc entre les trois espaces.

---

## 7. Templates et navigation

- `app/templates/_uaa_space_nav.html` (nouveau) : trois onglets (Cours / S'entraîner /
  S'évaluer) de largeur égale (`flex-fill`), classe `.jc-space-nav`, `aria-current="page"`
  sur l'onglet actif, `d-print-none`. Inclus par les trois templates de page — l'espace
  actif est toujours visuellement distinct (fond bleu plein) et annoncé aux lecteurs
  d'écran.
- `app/templates/_lesson_blocks.html` (nouveau) : boucle de rendu des blocs, extraite telle
  quelle de l'ancien `uaa_detail.html` — strictement identique quel que soit l'espace,
  paramétrée par `rendered_blocks` et `empty_message`.
- `app/templates/uaa_detail.html` (Cours) : conserve la barre de progression de lecture et
  le bouton « Marquer comme terminé » (spécifiques à la théorie), inclut le nav d'espace
  et `_lesson_blocks.html`.
- `app/templates/uaa_practice.html`, `uaa_exam.html` (nouveaux) : même structure
  (breadcrumb, en-tête, nav d'espace, `_lesson_blocks.html`), sans barre de
  progression/bouton « terminé » (sémantique de progression propre à la théorie, pas
  dupliquée ici).
- `app/static/css/design-system.css` : nouvelle section `.jc-space-nav` —
  `min-height: 44px` par onglet (cible tactile), `border-radius: 999px`, fond neutre au
  repos, fond bleu (`--jc-blue`) + texte blanc à l'état actif.

**Mobile-first** : trois onglets de largeur égale (`flex-fill`), `gap: 0.5rem`,
`white-space: nowrap` — à 360 px (largeur mobile la plus contrainte testée), avec le
padding du conteneur Bootstrap (`.container`, ~24 px) et les deux `gap` (16 px), chaque
onglet dispose d'environ 106 px de large pour ~44 px de haut, largement au-dessus des
recommandations de cible tactile (44×44 px). Aucun débordement horizontal possible (trois
éléments `flex-fill` dans un conteneur `nav`, pas de largeur fixe). **Non vérifié
visuellement** — voir § 10, même limite que les tickets #18/#21 (aucun navigateur/outil
d'automatisation disponible dans cet environnement serveur).

---

## 8. Tests

**Nouveau fichier** `tests/test_ticket22_no_regression.py` (16 tests) :
- migration de schéma : ajout de colonne sur une base pré-#22 (table sans `space`),
  idempotence (deux appels successifs), no-op si la table `lesson_blocks` n'existe pas
  encore ;
- `LessonBlock.space` vaut `COURSE` par défaut à la construction directe ;
- filtrage strict par espace sur les trois routes (UAA de test à 3 blocs, un par espace) ;
- 404 cohérent (slug inconnu, UAA non publiée) sur les trois routes ;
- navigation : les trois liens et labels sont présents sur les trois pages, un seul onglet
  actif (`aria-current="page"`) par page dans le bloc de nav (distinct du breadcrumb, qui
  porte son propre `aria-current` sur un autre élément) ;
- CSS de taille de cible tactile (`min-height: 44px`) présente pour `.jc-space-nav` ;
- **scénario complet de staging pré-#22 reclassé sans reset** (§ 5) ;
- second `seed()` ne reclasse plus rien (sortie standard vérifiée via `capsys`) ;
- répartition COURSE/PRACTICE/EXAM exacte de MC01/MC02/MC03 ;
- Mathématiques strictement COURSE (décision explicite non-régression) ;
- garde-fou : chaque entrée de `MC02_BLOCKS`/`MC03_BLOCKS` porte bien une classification
  explicite (`BlockSpace`), jamais absente.

**Tests existants ajustés** (conséquence directe et attendue de la séparation d'espaces,
pas une régression) :
- `tests/test_informatique_mc0{1,2,3}.py` : les assertions sur les exercices/examen
  pointent désormais vers `/practice`/`/exam` au lieu de `/uaa/{slug}` ; nouveau test par
  mini-cours confirmant l'absence d'exercices/examen sur la page Cours.
- `tests/test_ticket17_no_regression.py`,
  `tests/test_ticket21_no_regression.py` : mêmes ajustements de route pour les assertions
  sur les 12 exercices MC01.

**Résultat** : `pytest -q` → **288 passed** (272 avant ce ticket + 16 nouveaux), 2
warnings préexistants (dépréciations `httpx`/`anyio`, sans lien avec ce ticket).

**Ruff** : `ruff check .` → **36 erreurs**, strictement identiques (mêmes fichiers, mêmes
règles) à celles de `develop` — comparé via un worktree isolé. **0 nouvelle erreur.** Deux
nouvelles occurrences `B008` (les routes `/practice` et `/exam`, même appel
`Depends(get_db)` que la route Cours déjà existante) neutralisées par `# noqa: B008` —
même convention que le reste du projet pour ce type d'appel.

**Vérification manuelle** (base SQLite temporaire isolée, jamais `jury_central.db`,
serveur `uvicorn` réel démarré sur un port de test) :
- Les 9 combinaisons UAA × espace (MC01/MC02/MC03 × Cours/S'entraîner/S'évaluer) + une UAA
  Mathématiques : toutes 200.
- Contenu vérifié précisément par `grep` sur le HTML réel : page Cours de MC01 contient la
  théorie et la fiche mémo, ne contient ni « Exercice N — », ni « Examen final », ni
  « Génère ton propre exercice » ; page S'entraîner contient les 12 exercices et le bloc
  IA, pas la théorie ni l'examen ; page S'évaluer contient l'examen (corrigé non publié
  toujours absent), pas la théorie ni les exercices.
- Scénario de migration staging pré-#22 rejoué sur ce serveur réel (§ 5), avec vérification
  HTTP après coup que l'examen apparaît bien sur `/exam` et plus sur `/uaa/ampcr-mc01`.
- `seed()` exécuté deux fois de suite sur la même base réelle après migration : second
  appel = 0 créé, 0 reclassé, tout conservé.
- `node --check app/static/js/editorial_exercise.js` : aucune régression JS (fichier non
  modifié par ce ticket).
- `jury_central.db` (fichier de dev local, gitignoré) vérifié inchangé après la session.

**Non vérifié — limite explicite** : comme pour les tickets #18/#21, aucun navigateur ni
outil d'automatisation n'est disponible dans cet environnement serveur — le rendu visuel
réel de la navigation par onglets aux largeurs 360/390/430 px (alignement, absence de
débordement, confort du clic/toucher) n'a pas pu être observé directement. Vérifié par
lecture directe du CSS/HTML généré et calcul des dimensions réelles (§ 7). Validation
visuelle sur staging recommandée avant clôture UX complète du ticket.

---

## 9. Limites et points ouverts (assumés, pas des oublis)

- **Mathématiques (MB32) reste entièrement COURSE** : ses blocs `quiz` et
  `generated_exercise` restent visibles sur la page Cours plutôt que sur S'entraîner —
  décision explicite de ChatGPT pour ce ticket (« COURSE par défaut si aucune
  classification spécifique n'est actuellement nécessaire »), pas une incohérence.
  Reclassifier Mathématiques fera l'objet d'un ticket dédié si souhaité.
- **8 exercices MC01/MC02/MC03 restent en Markdown** dans PRACTICE (pas encore
  `editorial_exercise`) : hors périmètre de ce ticket, qui ne fait que déplacer le contenu
  existant vers le bon espace sans le restructurer davantage — voir ticket #21 pour le
  détail de ce qui reste à migrer (`long_answer`).
- **Pas de constructeur multi-modules** (sélection de plusieurs modules, nombre de
  questions, difficulté, génération d'un questionnaire transversal) : explicitement hors
  périmètre (« NE construis pas encore #24 »), l'architecture (espaces génériques,
  `space` en champ explicite, routes génériques) est posée pour l'accueillir.
- **Pas de génération d'examen multi-modules ni de correction après soumission globale** :
  explicitement hors périmètre (« NE construis pas encore #25 »).

---

## 10. Fichiers modifiés

- `app/models.py` — `BlockSpace`, `LessonBlock.space`.
- `app/database.py` — `ensure_schema_migrations()`.
- `app/main.py` — `Base.metadata.create_all` + `ensure_schema_migrations()` au démarrage ;
  `_render_lesson_blocks()` (extraction), `_get_published_uaa()`, `_space_blocks()` ;
  routes `uaa_detail` (filtrée COURSE), `uaa_practice`, `uaa_exam` (nouvelles).
- `app/seed.py` — import `BlockSpace`/`ensure_schema_migrations` ; `MC01_BLOCKS`,
  `MC02_BLOCKS`, `MC03_BLOCKS` : classification explicite (`"space"` sur chaque entrée) ;
  `_seed_uaa()` : paramètre `reclassified` ; `seed()` : compteur `reclassified`, appel
  `ensure_schema_migrations()`, affichage du bilan de reclassification.
- `app/templates/_uaa_space_nav.html`, `_lesson_blocks.html` — nouveaux.
- `app/templates/uaa_detail.html` — restructuré (Cours uniquement, nav d'espace).
- `app/templates/uaa_practice.html`, `uaa_exam.html` — nouveaux.
- `app/static/css/design-system.css` — section `.jc-space-nav`.
- `tests/test_ticket22_no_regression.py` — nouveau.
- `tests/test_informatique_mc01.py`, `test_informatique_mc02.py`, `test_informatique_mc03.py`,
  `test_ticket17_no_regression.py`, `test_ticket21_no_regression.py` — routes ajustées.
- `docs/UI_GUIDELINES.md` — section « Une leçon » réécrite (trois espaces).
- `docs/current_state.md` — navigation publique, statut du socle éditorial.
- `docs/changelog.md` — entrée de ticket.
- `docs/claude-reports/2026-09-16_ticket-22_separation-cours-practice-exam.md` — ce rapport.

---

## Statut

Implémentation, tests, vérification manuelle et documentation terminés jusqu'au commit +
push. **Aucun merge, aucun déploiement.** En attente de revue et de fusion par ChatGPT,
puis d'un déploiement staging explicitement autorisé
(`scripts/deploy_staging.sh` + `seed-db`, voir § 5).
