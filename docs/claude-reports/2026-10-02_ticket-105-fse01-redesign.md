# Rapport — Ticket #105 : refonte pédagogique et visuelle de FSE01 (pilote)

Branche : `feature/105-fse-redesign-fse01` (depuis `develop`). PR #106 fusionnée dans
`develop`, puis installée sur `jury-central.lodylands.com` — autorisation couverte par
`docs/PROJECT_RULES.md` § 8 (travail explicitement demandé par l'utilisateur).

**SHA installé : `3c9a815`** (merge commit de la PR #106 dans `develop`).

---

## 1. Diagnostic du rendu actuel (demande § 1)

Deux causes distinctes identifiées avant toute modification visuelle :

1. **Architecture** : chaque mini-cours FSE (FSE01-17) est livré comme **un seul bloc
   Markdown « Cours complet »**, donc **une seule carte indifférenciée**
   (`app.card_kind.classify_block_title` ne peut distinguer théorie/méthode/exemples/mémo
   dans un contenu non découpé). Le Design System (cartes, encadrés, couleurs — déjà
   documenté dans `docs/UI_GUIDELINES.md` et `docs/components/`) existait déjà mais n'était
   simplement jamais exploité pour FSE : le problème n'était pas un manque de composants,
   mais l'absence de découpage du contenu.
2. **Bug de rendu Markdown confirmé par test direct** (`app.content.render_markdown`,
   bibliothèque `markdown`, extensions `fenced_code`/`tables` uniquement, **sans**
   `sane_lists`) : une liste à tirets non précédée d'une ligne vide n'est pas convertie en
   `<ul><li>` — elle est fondue dans le paragraphe précédent sous forme de texte brut avec
   des tirets littéraux. Vérifié par un appel direct à `render_markdown()` avec et sans
   ligne vide : le second cas produit un vrai `<ul>`, le premier un seul `<p>`. C'est la
   cause exacte du rendu « mur de texte avec des tirets entre les notions » signalé —
   corrigé structurellement, pas par CSS, en remplaçant les listes concernées par des
   tableaux ou en respectant systématiquement la ligne vide.

---

## 2. Présentation commune réutilisable (demande § 2)

Aucune nouvelle macro de carte n'a été nécessaire : le Design System existant
(`app/card_kind.py`, `_cards.html`, `design-system.css`) couvre déjà TheoryCard,
MethodCard, ExampleCard, ExerciseCard, SummaryCard, WarningCard (via les citations `>` —
mécanisme déjà existant, `wrapBlockquotesAsWarningCards()`). Deux mots-clés ajoutés à
`app.card_kind.classify_block_title()` pour que le **titre** d'un bloc pilote correctement
son type : `"méthode"` → MethodCard, `"source"` → carte d'information (en plus de
`"ressource"` déjà présent).

Quatre **composants internes à une carte** ont été ajoutés (CSS + documentation complète
dans `docs/components/`, suivant la structure imposée par `docs/components/INDEX.md`) car
aucun composant existant ne couvrait ce besoin :

- **DefinitionGrid** (`docs/components/DefinitionGrid.md`) — grille de cartes
  terme/explication/exemple.
- **CompareGrid** (`docs/components/CompareGrid.md`) — comparaison visuelle à deux colonnes
  (variantes bonne/mauvaise réponse, notion A/notion B), empilée sur mobile (`<576px`).
- **DocCard** (`docs/components/DocCard.md`) — document support (mail/affiche/réseau
  social) **toujours étiqueté « Fictif »**, strictement séparé de son analyse.
- **Diagram** (`docs/components/Diagram.md`) — conteneur de schéma SVG responsive.

Chaque composant inclut `@media print { break-inside: avoid; }`. Corrigés d'exercices :
mécanisme natif `<details>`/`<summary>` déjà utilisé dans le contenu FSE précédent,
conservé (plus simple et plus robuste que le découpage automatique JS existant, et déjà
fermé par défaut sans attribut `open` — vérifié par recherche explicite de `<details open`
dans le rendu, absent).

---

## 3. Schémas en caractères remplacés par du SVG (demande § 3)

**Aucune bibliothèque de diagrammes introduite** — décision documentée et justifiée dans
`docs/components/Diagram.md` après vérification explicite :
- aucune dépendance JS de diagramme n'existait déjà dans le projet (`app/static/js/`,
  `pyproject.toml`) ;
- `docs/UI_GUIDELINES.md` (section Illustrations) recommande explicitement SVG, Canvas ou
  Plotly — jamais une bibliothèque externe type Mermaid ;
- le composant `.jc-flow` (CSS pur, déjà existant) reste réservé aux enchaînements
  linéaires simples et ne convient pas à une boucle de rétroaction.

Schéma écrit à la main (`app/v1/fse01_content.py::FSE01_COMMUNICATION_DIAGRAM_SVG`) :
émetteur, récepteur, message, code, canal, contexte, obstacle et boucle de rétroaction
représentés comme 8 éléments **distincts et non confondus** (code et canal sur deux lignes
séparées ; obstacle positionné sur le trajet, pas fondu dans la flèche ; rétroaction en
chemin courbe séparé, avec sa propre flèche). `viewBox="0 0 900 440"` sans attribut
`width` fixe + CSS `max-width:100%; height:auto` → mise à l'échelle responsive native,
aucun défilement horizontal, rendu vectoriel fiable à l'impression (`break-inside: avoid`).
`role="img"` + `aria-label` complet pour l'accessibilité.

---

## 4. FSE01 repris entièrement (demande § 4)

`app/v1/fse01_course.py` : l'ancienne fonction `fse01_course_markdown() -> str` (un seul
bloc) est remplacée par `fse01_course_sections() -> list[tuple[str, str]]`, **7 blocs
titrés** (chaque titre pilote son type de carte) :

1. **FSE01 — Présentation et objectifs** (théorie)
2. **FSE01 — Théorie : le schéma de communication** (théorie — grille de définitions,
   schéma SVG, pièges en citations `>` auto-converties en WarningCard)
3. **FSE01 — Méthode** (MethodCard — 8 étapes numérotées `<ol>`)
4. **FSE01 — Exemples commentés : mail, affiche, réseau social** (ExampleCard — 3
   DocCard séparées de leur analyse, chacune suivie d'un **tableau** à 2 colonnes
   « Élément du schéma » / « Ce qu'on observe », jamais d'une liste à tirets fondue)
5. **FSE01 — Comparer pour ne pas confondre** (théorie — CompareGrid pour code/canal,
   réponse directe/réponse immédiate, et mauvaise/bonne réponse)
6. **FSE01 — Exercices guidés** (ExerciseCard — 2 exercices guidés + 1 question flash,
   corrigés dans des `<details>` imbriqués, fermés par défaut)
7. **FSE01 — Fiche mémo** (SummaryCard — liste concise finale)

Aucune notion, nuance ou terme à apprendre n'a été supprimé — seules les reformulations et
répétitions ont été allégées. Les trois documents restent **fictifs** et clairement
étiquetés comme tels (badge renforcé « Reconstitution pédagogique, fictive » pour
l'affiche). Les textes bruts exacts des trois documents
(`FSE01_MAIL_TEXT`/`FSE01_AFFICHE_TEXT`/`FSE01_SOCIAL_TEXT`, `app/v1/fse01_content.py`)
sont restés **strictement inchangés**, octet pour octet, car ils alimentent
`app.v1.fse_bank.import_fse01_to_bank` (banque de questions, correction IA) — seules de
nouvelles constantes d'affichage (`*_CARD_HTML`) ont été ajoutées à côté.

La distinction code/canal et réponse directe/réponse immédiate est explicitement maintenue
à trois endroits indépendants (théorie, CompareGrid dédié, mémo) — jamais fondue.

---

## 5. Migration des données (non-régression)

`app/seed.py` : nouvelle fonction `_fse_course_blocks()` (générique, réutilisable pour
FSE02-17) transforme une liste de sections en blocs `LessonBlock`. L'appel `_seed_uaa` pour
FSE01 passe désormais `obsolete_titles=frozenset({"Cours complet"})` : au prochain seed,
l'ancien bloc unique est supprimé et les 7 nouveaux sont créés — mécanisme déjà utilisé
sans incident pour MC01/AMPCR (`MC01_OBSOLETE_TITLES`). `LessonBlock` n'a aucune relation
avec `Question`/`QuestionnaireSession` : aucune session déjà jouée n'est affectée.

---

## 6. Tests exécutés (ciblés, PAS la suite complète de 1 419 tests)

Conformément à l'instruction explicite de ne pas relancer la suite monolithique :

| Fichier | Résultat |
|---|---|
| `tests/test_card_kind.py` (2 nouveaux cas : `"méthode"`, `"source"`) | 8/8 ✅ |
| `tests/test_ticket96_fse01.py` (moteur FSE01 : banque, sessions, difficulté/sévérité) | 30/30 ✅ |
| `tests/test_admin_content_hierarchy.py` (comptage dynamique de blocs) | 18/18 ✅ |
| `tests/test_ticket102_coverage.py` (adapté : accepte `*_course_sections()` en plus de `*_course_markdown()`) | 52/52 ✅ |
| `tests/test_ticket97_fse02_04.py` / `98` / `99_fse09_12.py` / `100_fse13_16.py` / `101_fse17.py` (non-régression FSE02-17, inchangés) | 220/220 ✅ |
| Vérification structurelle ad hoc de la page réelle `/uaa/fse-fse01` (locale puis en production après installation) | voir § 7 |

**Total ciblé : 328/328 tests verts.** Aucune régression constatée.

---

## 7. Vérifications de rendu effectuées

Sur la page en production (`curl` + analyse structurelle du HTML renvoyé, aucun outil de
capture d'écran disponible dans cet environnement) :

- 7 cartes distinctes générées (`class="jc-card...`), avec les bons types
  (`jc-card--method`, `jc-card--example`, `jc-card--exercise`, `jc-card--summary`).
- `<svg>` et conteneur `.jc-diagram` bien présents (schéma réellement rendu, pas de bloc de
  code juste avant).
- 3 badges `jc-doc-fictive-badge` présents (les 3 documents restent identifiables comme
  fictifs) et au moins un `<table>` (analyse séparée du document, jamais en liste fondue).
- `.jc-definitions` et `.jc-compare` présents.
- Aucun `<details open` (corrigés bien fermés par défaut) ; au moins 2 `<details>`.
- **Zéro paragraphe contenant des tirets de liste littéraux** — le bug diagnostiqué au § 1
  n'est plus présent sur cette page.
- Assets statiques `design-system.css` et `design_system.js` répondent en 200.
- `.jc-diagram svg { max-width:100%; height:auto }` et `.jc-compare` passe en 1 colonne
  sous 576px (vérifié dans le CSS) — garantit l'absence de défilement horizontal et de
  texte coupé sur mobile ; `break-inside: avoid` sur tous les nouveaux composants garantit
  un rendu correct à l'impression.

**Limite explicite** : ces vérifications sont structurelles (HTML/CSS), pas visuelles —
aucun outil de capture d'écran ou de rendu de navigateur n'est disponible dans cet
environnement. La vérification visuelle réelle sur ordinateur, téléphone et à l'impression
reste à faire par l'utilisateur via les liens ci-dessous.

Comptes/données vérifiés intacts après seed : 18 utilisateurs (`v1_users`), 67 sessions
(`v1_questionnaire_sessions`), 536 réponses (`v1_session_answers`) — comptes identiques
avant/après, aucune perte. Sauvegarde de `jury_central.db` effectuée avant le seed :
`jury_central.db.bak-pre-ticket105-20261002-180356` (point de restauration, conservé dans
`/srv/jury-central`).

---

## 8. Pages/fichiers modifiés

- `app/card_kind.py` — 2 mots-clés ajoutés (`méthode`, `source`).
- `app/static/css/design-system.css` — 4 nouveaux composants (DefinitionGrid, CompareGrid,
  DocCard, Diagram), tous responsive + impression.
- `app/v1/fse01_content.py` — 3 nouvelles constantes `*_CARD_HTML` + schéma SVG ; textes
  bruts des 3 documents inchangés.
- `app/v1/fse01_course.py` — réécrit intégralement (`fse01_course_sections()`).
- `app/seed.py` — `_fse_course_blocks()` (générique), `FSE01_BLOCKS` basé sur les sections,
  `obsolete_titles` pour FSE01.
- `docs/components/{CompareGrid,DefinitionGrid,DocCard,Diagram}.md` — nouveaux.
- `docs/components/INDEX.md` — section des composants internes à une carte.
- `tests/test_card_kind.py`, `tests/test_ticket102_coverage.py` — adaptés.

---

## 9. Liens à tester

- Page de cours FSE01 : `https://jury-central.lodylands.com/uaa/fse-fse01`
- Entraînement (fonctionnalité inchangée, non retouchée dans ce ticket) :
  `https://jury-central.lodylands.com/uaa/fse-fse01/practice`
- Examen (inchangé) : `https://jury-central.lodylands.com/uaa/fse-fse01/exam`

À vérifier en particulier : lisibilité du schéma de communication sur téléphone (sans
zoomer ni défiler horizontalement), aspect des 3 cartes-documents (mail/affiche/réseau
social), absence de tout texte à tirets « mur de texte », rendu à l'impression de la page
(Ctrl+P / aperçu).

---

## 10. Suite (non démarrée sans confirmation intermédiaire, par instruction explicite)

Les cours FSE02-17 restent, à ce stade, dans leur état d'origine (un seul bloc « Cours
complet » par cours, listes à tirets non corrigées). L'extension du même système
(composants + découpage en blocs titrés + correction du bug de liste) à FSE02-17 va
démarrer immédiatement après ce rapport, sans confirmation intermédiaire, conformément à
la demande.
