# Rapport — Finalisation du ticket #126 : composition réelle de la théorie FSE

Installé sur `jury-central.lodylands.com`.

**SHA installé : `a54a205`** (merge de la PR #130).

**Statut : installée, à valider visuellement.** Ce rapport documente ce qui a été
construit et vérifié de mon côté (y compris, cette fois, avec un vrai navigateur) — il ne
remplace pas votre propre validation visuelle sur le site, qui reste à faire.

---

## 1. Ce qui a changé par rapport aux tentatives précédentes

Les deux livraisons précédentes de ce ticket n'avaient été vérifiées qu'avec des rendus
PDF locaux (WeasyPrint) ou un simple contrôle HTML/CSS — jamais un vrai navigateur. Cette
fois, Playwright + Chromium ont été installés comme outils de développement (jamais ajoutés
aux dépendances du projet, supprimés en fin de tâche) pour examiner réellement les pages,
à largeur ordinateur (1280px) et téléphone (390px), avant et après chaque correction.

Premier constat, confirmé avec le vrai navigateur : **FSE04 « Peut-on agir autrement ? »
était déjà correct** (deux cartes côte à côte, alignement cohérent, bon comportement
mobile) — la correction précédente avait fonctionné pour cette section précise. Le
problème restait concentré sur **FSE03 « Quelle image les autres voient-ils ? »**, qui
n'avait reçu qu'un simple alignement à gauche (pas de recomposition), insuffisant à
largeur réelle d'ordinateur (un paragraphe capé à 70 caractères par ligne reste
visiblement étroit face à une carte de ~1100px).

---

## 2. FSE03 « Quelle image les autres voient-ils ? » — nouvelle composition

Exactement la disposition demandée :

A. Titre (géré par le gabarit générique) + introduction courte, pleine largeur.
B. Schéma « Traces visibles → Perception des autres → Réputation » (inchangé — déjà
   équilibré, vérifié avec le navigateur réel dès le premier diagnostic).
C. Les trois limites, auparavant un seul paragraphe, deviennent trois cartes de largeur
   égale (`.jc-theory-cards.jc-theory-cards--three`, nouveau) : « Une image partielle »
   (🧩), « Une trace ancienne » (🕰️), « Un contexte manquant » (🖼️) — icône, titre clair,
   explication courte, fond discret, sans bordure propre.
D. Rangée à deux colonnes (`.jc-theory-split`) : « Identité réelle et image perçue »
   (explication, sans jamais assimiler l'identité réelle à l'image publique) à gauche,
   « Exemple concret » (le recruteur qui découvre un commentaire vieux de cinq ans) à
   droite.
E. Encadré « À retenir » compact, texte exact demandé : « La réputation est une image
   perçue : elle ne résume pas qui est réellement une personne. »
F. Lexique repliable des 7 définitions, inchangé.

Toutes les nuances d'origine restent expliquées dans les cartes (ex. « jamais la personne
tout entière », « ne dit rien de certain... aujourd'hui », « détaché de ce contexte ») —
seule la phrase de l'encadré est une synthèse volontairement courte.

---

## 3. Sections génériques (FSE02/05-16) — grille de définitions toujours visible

En examinant les 16 cours FSE un par un avec le navigateur réel (pas seulement FSE03/04),
trois cours se sont distingués des autres : **FSE05, FSE10, FSE13**. Leur théorie compte 4
à 6 paragraphes consécutifs sans aucune liste ni schéma — et leur grille de définitions,
jugée entièrement redondante avec la prose par la règle introduite au ticket #120, se
repliait automatiquement en lexique caché. Résultat réel à l'écran : plus aucune
respiration visuelle, un mur de texte pur, sans la grille de cartes qui rendait les 10
autres cours génériques lisibles.

Corrigé en retirant le repli automatique : la grille de définitions reste désormais
**toujours visible**, même quand tous ses termes sont déjà mentionnés dans la prose. Les
13 autres cours génériques (déjà satisfaisants : prose à largeur raisonnable suivie d'une
grille de cartes pleine largeur, vérifié un par un avec le navigateur réel) n'ont pas été
retouchés, conformément à la consigne de préserver ce qui fonctionne déjà.

---

## 4. Contrôles effectués

| Contrôle | Nature |
|---|---|
| `tests/test_ticket126_fse_theory_composition.py` (24 cas : composition FSE03, grille toujours visible, régressions de rafraîchissement de contenu) | technique |
| `test_ticket97_fse02_04.py`, `card_kind`, `admin_content_hierarchy`, `test_ticket120_fse03_theory.py`, `test_ticket120_fse_theory_generic.py`, `test_ticket124_fse_theory_layout.py` — 147 passants au total | technique |
| **FSE03** (desktop 1280px + mobile 390px), **FSE04** (re-vérifié), **FSE05/FSE10/FSE13** (desktop, FSE05 aussi en mobile) | **navigateur réel (Playwright/Chromium)** |
| **FSE02, FSE06, FSE07, FSE08, FSE09, FSE11, FSE12, FSE14, FSE15, FSE16** | **navigateur réel, desktop** — tous jugés déjà satisfaisants |
| Page réelle en production après déploiement (FSE03 desktop + mobile, FSE05/10/13) | **navigateur réel contre le site installé**, pas seulement la structure HTML |

Les tests techniques (HTML/CSS) vérifient l'absence de fuite Markdown, la présence des
bons textes/classes et la non-régression de rafraîchissement de contenu — **ils ne
prouvent pas qu'une page est agréable à regarder**. C'est la vérification au navigateur
réel, cette fois effectuée systématiquement à l'écran (captures consultées une par une, à
deux largeurs), qui constitue le contrôle visuel de cette livraison. Elle reste cependant
mon propre jugement, pas une validation de votre part.

**Limite honnête** : je n'ai pas pu tester d'interactions utilisateur réelles (clic sur le
lexique repliable, zoom, lecteur d'écran) ni un vrai appareil physique — uniquement un
Chromium headless à deux largeurs de viewport fixes. L'impression n'a pas été re-testée à
ce tour (déjà vérifiée aux tickets précédents, structure inchangée pour les règles
d'impression).

**Comptes et données vérifiés intacts** à chaque étape : 18 utilisateurs, 68 sessions, 546
réponses — stables avant/après le seed (les variations observées au fil de la journée
proviennent d'une utilisation réelle du site, jamais du seed lui-même). Sauvegarde de
`jury_central.db` effectuée avant le seed :
`jury_central.db.bak-pre-ticket126-final-<horodatage>`.

---

## 5. Fichiers modifiés

- `app/v1/fse03_course.py` — nouvelle composition de `_section_image()`.
- `app/v1/fse_course_sections.py` — `theory_and_definitions_to_cards()` ne replie plus
  jamais la grille de définitions.
- `app/static/css/design-system.css` — `.jc-theory-cards--three`,
  `.jc-theory-split-main-title`.
- `app/seed.py` — « FSE03 — Quelle image les autres voient-ils ? » ajouté à
  `obsolete_titles`.
- `tests/test_ticket126_fse_theory_composition.py` (étendu, 24 cas),
  `tests/test_ticket120_fse_theory_generic.py` (mis à jour).

---

## 6. Liens à vérifier

- **FSE03 (section corrigée)** : https://jury-central.lodylands.com/uaa/fse-fse03
- **FSE04 (re-confirmé)** : https://jury-central.lodylands.com/uaa/fse-fse04
- **FSE05, FSE10, FSE13 (grille désormais visible)** : fse-fse05, fse-fse10, fse-fse13

**Livraison installée, à valider visuellement par vous** — je ne considère pas le problème
définitivement clos sur la seule base de mes propres contrôles, même avec un navigateur
réel cette fois.
