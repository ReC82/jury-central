# Progression théorique en petites sections (`.jc-prose`, `.jc-takeaway`, `.jc-glossary`)

Introduits lors de la restructuration des blocs théoriques FSE01-17 contre l'effet « gros
bloc de texte » (ticket #120). D'abord appliqués à FSE03, puis réutilisés selon les besoins
des autres cours.

---

# Objectif

Remplacer un bloc théorique unique et dense par une progression de petites cartes, chacune
centrée sur une notion ou un petit groupe de notions : explication courte → exemple concret
→ phrase « À retenir » le cas échéant. Ne jamais empiler les paragraphes existants dans des
encadrés sans réorganiser leur contenu, et ne jamais imbriquer plusieurs cartes les unes
dans les autres.

---

# Quand l'utiliser

- Un bloc théorique couvrant plusieurs notions distinctes et conceptuellement
  indépendantes : chaque section de 2-4 paragraphes qui répond à une petite question
  compréhensible (ex. « Qui suis-je ? ») devient sa propre carte théorique (titre de bloc
  dédié, voir `app.card_kind.classify_block_title` — tout titre neutre retombe sur le type
  « theory »).
- Deux notions souvent confondues à l'intérieur d'une même section → [CompareGrid /
  DialogueComponents](DialogueComponents.md) (`.jc-compare`, variante `--a`/`--b`, pas
  `--bad`/`--good` qui est réservée à une vraie bonne/mauvaise réponse).
- Un enchaînement simple de 2 à 4 étapes (ex. traces → perception → réputation) →
  `.jc-flow` (déjà existant depuis le ticket #103, jamais utilisé en contenu réel avant ce
  ticket — voir Bug corrigé ci-dessous).
- Une liste de définitions qui répète exactement ce qui est déjà dit dans les explications
  visibles → lexique repliable `.jc-glossary` plutôt qu'une liste affichée deux fois.

# Quand ne pas l'utiliser

- Pas de découpage forcé en trois sections identiques sur tous les cours : le nombre et le
  nom des sections dépendent du sujet (cahier des charges du ticket #120, § 4).
- Une phrase « À retenir » par section seulement si elle apporte une vraie synthèse —
  jamais une sur un paragraphe qui n'en a pas besoin.
- Ne retire jamais une notion ou une nuance nécessaire à l'examen pour raccourcir : on
  réorganise, on ne supprime pas de matière (seules les répétitions disparaissent).

---

# Structure

## `.jc-prose` — largeur de lecture confortable, alignée à gauche

```html
<div class="jc-prose">
<p>Texte explicatif...</p>
</div>
```

Limite la prose à `70ch` (~65-75 caractères par ligne sur grand écran), sans toucher aux
tableaux, `.jc-doc`, `.jc-compare` ou `.jc-flow`, qui restent sur toute la largeur
disponible puisqu'ils ne portent pas cette classe. Aligné à gauche (aucune marge
automatique) : partage le même repère que le titre de la carte et tout ce qui l'entoure.

**Historique** : le ticket #124 avait centré ce bloc (`margin: 0 auto`) pour éviter un
texte plaqué à gauche avec la moitié droite de la carte vide. Après vérification visuelle
réelle du site, ce centrage s'est révélé insuffisant : il créait une colonne flottante,
toujours désalignée du titre et des blocs pleine largeur (grille, encadré) qui
l'entourent — un déséquilibre différent, pas résolu. Le ticket #126 retire le centrage :
`.jc-prose` reste réservé à une explication réellement continue, sans second volet
possible ; dès que le contenu se décompose naturellement en plusieurs idées (deux
explications de même poids, ou une explication + un exemple distinct), la bonne réponse
est `.jc-theory-cards` ou `.jc-theory-split` ci-dessous, PAS un `.jc-prose` centré ou
élargi — c'est le sens de « la limite de largeur doit être adaptée au composant, plutôt
qu'appliquée uniformément ».

## `.jc-theory-cards` — deux blocs pédagogiques courts, côte à côte (ticket #126)

```html
<div class="jc-theory-cards">
<div class="jc-theory-card">
<span class="jc-theory-card-icon" aria-hidden="true">😣</span>
<span class="jc-theory-card-title">Titre clair</span>
<p>Explication courte.</p>
<p><strong>Exemple :</strong> ...</p>
</div>
<div class="jc-theory-card">...</div>
</div>
```

Deux colonnes de largeur égale, icône + titre + paragraphes courts, fond discret
(`var(--jc-gray-bg)`) et **sans bordure propre** (pour éviter l'accumulation de bordures
dans une carte qui en a déjà une). Remplace une colonne de prose isolée quand le contenu
se décompose naturellement en deux idées de même poids — ni une comparaison stricte
(`.jc-compare`, qui oppose deux notions), ni une paire explication/exemple asymétrique
(`.jc-theory-split`).

**Quand l'utiliser** : deux idées de poids comparable, chacune avec son propre titre (voir
FSE04 — « Peut-on agir autrement ? » : « Une tension peut créer de la frustration » / « Le
groupe influence, chacun peut réagir »).

## `.jc-theory-split` — théorie à deux colonnes asymétriques (ticket #124)

```html
<div class="jc-theory-split">
<div class="jc-theory-split-main">
<p>Explication...</p>
</div>
<div class="jc-theory-split-aside">
<span class="jc-theory-split-aside-label">Situation concrète</span>
<p>Exemple ou repère pédagogique...</p>
</div>
</div>
```

Pour une section dont le contenu s'y prête réellement : explication à gauche (~60 % de la
largeur), exemple ou repère pédagogique à droite (~40 %, encadré bleu). La colonne de
texte n'a **pas** de largeur maximale propre (pas de `.jc-prose` à l'intérieur) : c'est la
grille qui la limite. S'effondre en une seule colonne sous 768px (empilée, dans l'ordre
explication puis exemple).

**Quand l'utiliser** : une section qui associe naturellement une explication générale à un
exemple concret ou une situation illustrative distincte, de poids différent de
l'explication (voir FSE04 — « Pourquoi suit-on parfois le groupe ? »). Si les deux volets
ont un poids comparable (deux idées, pas une idée + son exemple), préférer
`.jc-theory-cards` ci-dessus.

**Quand ne pas l'utiliser** : une section purement explicative sans second volet distinct
(`.jc-prose` suffit) ; une comparaison entre deux ou trois notions elles-mêmes
(`.jc-compare`/`.jc-compare--three`) ; jamais pour forcer artificiellement un contenu qui
n'a pas de second volet naturel.

## `.jc-compare--three` — comparaison à trois éléments (ticket #124, corrigé #126)

```html
<div class="jc-compare jc-compare--three">
<div class="jc-compare-item jc-compare-item--a">...</div>
<div class="jc-compare-item jc-compare-item--b">...</div>
<div class="jc-compare-item jc-compare-item--c">...</div>
</div>
```

Variante de [DialogueComponents](DialogueComponents.md) `.jc-compare` pour trois notions
(plutôt que deux) qui s'enchaînent ou se distinguent (ex. FSE04 : valeur/norme/
comportement). Troisième couleur `--c` (violet, `var(--jc-purple)`).

**Colonnes fixes, pas `auto-fit`** : `grid-template-columns: repeat(3, 1fr)` + media
queries explicites (2 colonnes sous 768px, 1 sous 576px) — même technique que
`.jc-compare`/`.jc-theory-split`/`.jc-theory-cards`. La version originale du ticket #124
utilisait `repeat(auto-fit, minmax(200px, 1fr))` pour que la grille se réorganise d'elle-
même ; au ticket #126, cette technique s'est révélée ne PAS fonctionner de façon fiable
avec l'outil de prévisualisation locale (WeasyPrint) — reproduit en isolation (grille à 2
éléments de 240px dans un conteneur de 700px, qui aurait dû tenir sur une ligne,
collapsée sur une seule colonne) avant d'écrire ce correctif. Un navigateur réel gère
normalement ce calcul correctement, mais faute de pouvoir le vérifier dans cet
environnement, la technique explicite et déjà éprouvée partout ailleurs est préférée.

## `.jc-takeaway` — phrase « À retenir » ponctuelle

```html
<div class="jc-takeaway">
<span class="jc-takeaway-label">📌 À retenir</span>
<p>Une phrase courte de synthèse.</p>
</div>
```

Couleur or (`var(--jc-gold)`), identique à la Fiche mémo (même icône 📌) — cohérence
visuelle volontaire : une phrase « À retenir » est une mini fiche mémo locale. À distinguer
de [`.jc-why-correct`](ExerciseStepCard.md), réservé à la justification d'un corrigé
d'exercice (pas la même situation pédagogique : l'un explique pourquoi une réponse est
correcte, l'autre résume une notion de théorie).

## `.jc-glossary` — lexique repliable

```html
<details class="jc-glossary">
<summary>📖 Retrouver les définitions</summary>
<div class="jc-definitions">
<div class="jc-definition">
<span class="jc-definition-term">Terme</span>
<p class="jc-definition-body">Définition courte.</p>
</div>
<!-- une .jc-definition par terme -->
</div>
</details>
```

Fermé à l'écran par défaut (accordéon natif `<details>`). Chaque terme qu'il contient DOIT
déjà apparaître dans les explications visibles au-dessus (ce lexique est un filet de
sécurité pour l'examen, jamais la seule source d'une définition).

---

# Comportement

- **HTML littéral, jamais de Markdown dans ces blocs** : `app.content.render_markdown` ne
  retraite jamais le Markdown situé à l'intérieur d'un bloc HTML brut (`<div>`,
  `<details>`...) — diagnostic ticket #112. Tout gras s'écrit `<strong>...</strong>`,
  jamais `**...**`, dans ces composants.
- **Bug corrigé par ce ticket (#120)** : `.jc-flow-step` était `display: flex` sans
  `flex-direction: column`, ce qui alignait le libellé de l'étape et son `<small>` sur la
  même ligne au lieu de les empiler (jamais remarqué avant car `.jc-flow` n'avait encore
  jamais été utilisé dans un contenu réel). Corrigé une fois pour toutes dans
  `design-system.css` — bénéficie à tout futur usage de `.jc-flow`, pas seulement FSE03.
- **Nuance ancienne publication volontaire ≠ devenue involontaire** (FSE03) : rédigée comme
  un `<blockquote>` littéral — converti en WarningCard par
  `wrapBlockquotesAsWarningCards()` (voir [WarningCard](WarningCard.md)), avec un repli CSS
  (`.content-markdown blockquote`) si le JS est désactivé.
- **Impression** : `.jc-glossary` reste disponible au lecteur à l'impression même fermé à
  l'écran, via une règle `@media print` qui force l'affichage de son contenu — à la
  différence des corrigés d'exercice (`.jc-exercise-correction`), qui restent
  volontairement masqués à l'impression. Limite connue : cette règle n'a pas pu être
  vérifiée dans un vrai navigateur (seul WeasyPrint, outil de prévisualisation local, était
  disponible — voir le rapport du ticket #120 pour le détail des limites).

---

# Traitement générique FSE02/FSE04-FSE16 (`theory_and_definitions_to_cards`)

FSE03 (ci-dessus) a reçu un traitement bespoke : trois cartes distinctes, titres propres au
sujet. Les 14 autres cours qui partagent `app.v1.fse_course_sections.build_course_sections`
(FSE02, FSE04-FSE16 — ni FSE01 ni FSE17, qui ont leur structure propre) gardent, eux, UN SEUL
bloc théorique (même titre « {code} — Théorie : notions et définitions » qu'avant ce ticket,
donc AUCUNE resynchronisation de position nécessaire dans `app.seed`, à la différence de
FSE03) dont le CONTENU est restructuré mécaniquement par
`theory_and_definitions_to_cards(theorie_brute, definitions_brutes)` :

1. **`theory_prose_to_html`** : la prose (paragraphes séparés par une ligne vide, gras
   `**...**`) devient des `<p>`/`<ul>` HTML littéraux, groupés en un ou plusieurs
   `<div class="jc-prose">` — SAUF un bloc déjà en HTML brut (schéma SVG déjà existant pour
   FSE08/FSE15, `FSE08_POWER_LEVELS_DIAGRAM_SVG`/`FSE15_CIRCUIT_DIAGRAM_SVG`), toujours laissé
   tel quel et HORS de la contrainte de largeur (il en a besoin). `fix_list_blank_lines` est
   appliqué d'abord : une liste introduite sur la même ligne qu'une phrase (ex. « ... sont
   possibles :\n- la vente : ... ») doit être séparée en son propre bloc avant d'être
   reconnue comme liste.
2. **`_definitions_bullets_to_items`** : chaque puce « - **Terme** (qualificatif optionnel)
   : explication. » devient (terme affiché, corps HTML) — SANS JAMAIS découper à l'intérieur
   d'un terme groupé (ex. FSE08 « Région (flamande, wallonne, Bruxelles-Capitale) » reste un
   seul terme avec son qualificatif, jamais trois cartes mal attribuées — risque explicitement
   identifié dans la docstring du module avant l'écriture de cette fonction). Toute puce qui
   ne correspond pas exactement à ce format est ignorée en toute sécurité plutôt que mal
   découpée ; vérifié que ce format couvre 100 % des puces des 14 cours (aucune ignorée en
   pratique).
3. Si TOUS les termes définis apparaissent déjà (en gras) dans la prose ci-dessus, la grille
   devient un lexique repliable `.jc-glossary` (même composant que FSE03) ; sinon elle reste
   une grille `.jc-definitions` VISIBLE — jamais cachée quand elle contient une information
   qui n'est pas déjà dite ailleurs. En pratique (vérifié sur les 14 cours), la comparaison
   est volontairement stricte (le terme exact doit apparaître, pas une variante
   grammaticale comme « interactifs » pour « interactivité ») : elle sous-estime parfois la
   redondance réelle, ce qui est le sens de l'erreur à privilégier — au pire la grille reste
   visible (déjà un net progrès sur une liste à tirets plate), jamais une information cachée
   à tort.

Entièrement mécanique et sûr (ni lecture ni réécriture de la matière), donc applicable aux 14
cours en un seul passage — à la différence d'une restructuration bespoke en plusieurs cartes
nommées par sujet (FSE03), qui suppose une vraie lecture éditoriale et n'a pas été jugée
nécessaire ici : garder un seul bloc théorique mais mieux organisé à l'intérieur évite aussi
une accumulation de cartes (cahier des charges du ticket #120, § 1).

**Mise à jour ticket #124** : le correctif de centrage de `.jc-prose` (ci-dessus)
s'applique automatiquement à ces 14 cours sans aucun changement de contenu — c'est la
réponse apportée à « applique la correction aux autres pages FSE présentant le même
problème » pour ce lot, sans leur forcer la structure bespoke en trois cartes de FSE04.
FSE04 est sorti de ce traitement générique (il a désormais sa propre théorie bespoke, voir
plus haut) : la liste à jour est FSE02, FSE05-FSE16.

---

# Composants liés

- [DialogueComponents](DialogueComponents.md) — `.jc-compare` (variantes `--a`/`--b` et
  `--bad`/`--good`), réutilisé ici pour des comparaisons de notions (pas de bonne/mauvaise
  réponse).
- [DefinitionGrid](DefinitionGrid.md) — `.jc-definitions`/`.jc-definition`, réutilisé tel
  quel à l'intérieur du lexique repliable.
- [ExerciseStepCard](ExerciseStepCard.md) — `.jc-why-correct`, le composant voisin dont
  `.jc-takeaway` s'inspire visuellement sans le réutiliser (situations pédagogiques
  différentes).
- [WarningCard](WarningCard.md) — citation Markdown/HTML convertie automatiquement.

---

# Exemple d'utilisation

Voir `app.v1.fse03_course` (`_section_identity()`, `_section_traces()`,
`_section_image()`) — remplace l'ancien bloc unique « FSE03 — Théorie : notions et
définitions » par trois cartes bespoke (« Qui suis-je ? », « Quelles traces je laisse ? »,
« Quelle image les autres voient-ils ? »), sur le même modèle bespoke que FSE01
(`app.v1.fse01_course`).
