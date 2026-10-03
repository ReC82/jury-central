# Rapport — Ticket #120 : lisibilité des blocs théoriques FSE01-17

Deux lots installés sur `jury-central.lodylands.com` :

1. **FSE03** (restructuration bespoke en trois cartes progressives) — PR #121,
   corrigée par PR #122 (bug de position trouvé en vérifiant l'installation).
2. **FSE02, FSE04-FSE16** (restructuration générique et mécanique, un seul bloc par
   cours mais mieux organisé à l'intérieur) — PR #123.

**SHA installé : `1e8fc95`** (merge de la PR #123, qui inclut tout le travail précédent du
ticket, SHA `fe1265b` inclus).

---

## 1. FSE03 — trois cartes progressives (demande bespoke du cahier des charges)

Remplace le bloc unique « Théorie : notions et définitions » par trois cartes, chacune
centrée sur une petite question :

- **« Qui suis-je ? »** : comparaison identité personnelle/identité collective
  (`.jc-compare`), groupe d'appartenance, identité numérique présentée comme l'expression
  en ligne de ces deux identités.
- **« Quelles traces je laisse ? »** : comparaison trace volontaire/trace involontaire, puis
  un encadré (converti automatiquement en carte Attention) qui distingue explicitement
  l'acte de publication initiale (volontaire) de la perte de maîtrise de sa visibilité
  ultérieure — une ancienne publication volontaire ne devient jamais automatiquement
  involontaire.
- **« Quelle image les autres voient-ils ? »** : petit schéma (`.jc-flow`) traces visibles →
  perception des autres → réputation, puis distinction identité réelle / image perçue, puis
  un lexique repliable (`.jc-glossary`) qui reprend les 7 définitions d'origine — chacune
  déjà présente dans les explications visibles au-dessus, jamais une information cachée qui
  ne serait dite nulle part ailleurs.

Trois nouveaux composants réutilisables pour la suite : `.jc-prose` (largeur de lecture
~70 caractères/ligne), `.jc-takeaway` (phrase « À retenir » ponctuelle, même code couleur
que la Fiche mémo), `.jc-glossary` (lexique repliable, disponible à l'impression même
fermé). Voir `docs/components/TheoryProgression.md`.

**Bug trouvé et corrigé en vérifiant l'installation** : `.jc-flow-step` (composant déjà
présent dans `design-system.css` depuis le ticket #103 mais jamais utilisé dans un contenu
réel avant ce ticket) était `display: flex` sans `flex-direction: column`, ce qui alignait
le libellé de l'étape et son sous-texte sur la même ligne au lieu de les empiler — corrigé
une fois pour toutes, bénéficie à tout futur usage.

**Second bug trouvé et corrigé après la première installation** : sur un staging déjà
seedé avant ce ticket, les blocs « Méthode »/« Comparer pour ne pas confondre »/« Fiche
mémo » existaient déjà avec leur ancienne position (jamais dans `obsolete_titles`, donc
jamais recréés). Le passage de un à trois blocs de théorie a décalé la position de tous les
blocs suivants, et sans resynchronisation explicite, ces trois blocs restaient en collision
de position avec les nouvelles cartes, inversant l'ordre d'affichage (Fiche mémo avant
Exercices guidés). Trouvé en vérifiant l'ordre réel des blocs sur l'installation de
production (pas seulement en local), corrigé par `FSE03_REPOSITION_TITLES` (même mécanisme
que `MC01_PRACTICE_REPOSITION_TITLES`, ticket #37), avec un test qui reproduit exactement
l'état pré-ticket pour éviter une régression future.

---

## 2. FSE02, FSE04-FSE16 — restructuration générique et mécanique

FSE01 et FSE17 ont une structure propre (non touchée : déjà bien décomposée en plusieurs
blocs avec grilles de définitions, schéma, citations — pas un « mur de texte »). Les 14
autres cours partagent `app.v1.fse_course_sections.build_course_sections` : plutôt qu'une
restructuration bespoke en plusieurs cartes nommées par sujet (qui suppose une vraie
lecture éditoriale cours par cours), une transformation mécanique et sûre a été appliquée
uniformément, pour les raisons suivantes : elle est strictement sans risque de perte ou de
déformation de la matière, vérifiable automatiquement sur les 14 cours à la fois, et évite
une accumulation de cartes (le cahier des charges du ticket demande explicitement d'éviter
cet écueil).

Le titre du bloc (« {Cours} — Théorie : notions et définitions ») reste identique à avant :
seul son contenu change, donc **aucune** resynchronisation de position n'a été nécessaire
pour ce lot (à la différence de FSE03, qui passait d'un à trois blocs).

**Transformation appliquée à chaque cours** (`theory_and_definitions_to_cards`) :

1. La prose (paragraphes + éventuelle liste introduite par une phrase sur la même ligne, ex.
   « Quatre modes de financement sont possibles : - la vente... ») devient du HTML littéral
   (`<p>`/`<ul>`), groupé en un ou plusieurs `.jc-prose` (largeur de lecture limitée) — sauf
   un schéma déjà présent dans le texte (FSE08 : niveaux de pouvoir ; FSE15 : circuit
   économique), qui reste intact et en dehors de cette contrainte de largeur, puisqu'il a
   besoin de toute la largeur disponible.
2. Chaque définition devient une carte `.jc-definitions` — le terme n'est **jamais**
   découpé à l'intérieur d'un groupe (ex. FSE08 « Région (flamande, wallonne,
   Bruxelles-Capitale) » reste un seul terme avec son qualificatif, jamais trois cartes mal
   attribuées — risque identifié avant l'écriture de cette fonction et explicitement évité).
3. La grille devient un lexique repliable `.jc-glossary` seulement quand **tous** les termes
   sont déjà présents (en gras) dans la prose visible au-dessus (FSE04, FSE05, FSE10, FSE13
   dans ce lot) ; sinon elle reste une grille **visible** sous la théorie — jamais cachée
   quand elle pourrait contenir une information qui n'est pas redite ailleurs. Cette
   comparaison est volontairement stricte (une variante grammaticale comme « interactifs »
   pour « interactivité » ne compte pas comme trouvée) : elle sous-estime parfois la
   redondance réelle, ce qui est le sens d'erreur à privilégier.

Aucune notion retirée : chaque cours conserve exactement les mêmes définitions, nuances et
exemples qu'avant — seule leur présentation change.

---

## 3. Contrôles effectués

| Lot | Tests | Résultat |
|---|---|---|
| FSE03 (fonctions + page réelle + reproduction du bug de position) | `test_ticket120_fse03_theory.py` (9 cas) | ✅ |
| FSE02/FSE04-16 (fonctions unitaires + 14 cours réels + aller-retour HTTP) | `test_ticket120_fse_theory_generic.py` (48 cas) | ✅ |
| Non-régression FSE01-17 complète | `test_ticket96_fse01.py`, `test_ticket97_fse02_04.py` à `test_ticket101_fse17.py`, `test_ticket102_coverage.py`, `test_card_kind.py`, `test_admin_content_hierarchy.py`, `test_ticket118_fse03_sophie_images.py` | ✅ (349 passants au total) |

Exécutés avant fusion, puis à nouveau sur le checkout de production après chaque
fast-forward, avant chaque seed.

**Vérification de la page réelle en production** (les 14 cours du second lot +
FSE01/FSE03/FSE17 par sondage) : `.jc-prose`/`.jc-definitions` présents, aucune fuite
Markdown (`**` littéral), aucune mention « provisoire », titre de bloc inchangé, schémas
SVG de FSE08/FSE15 toujours servis intacts (balise `<svg>` présente) après le passage par
la nouvelle fonction de restructuration.

**Prévisualisation visuelle locale** (HTML réel → PDF → image, WeasyPrint, outil de
développement uniquement, jamais une dépendance du projet) : FSE03 (trois cartes, grilles
de comparaison, schéma à trois étapes, lexique replié) et un échantillon du second lot
(FSE02 : prose + liste de financement + grille de définitions ; FSE15 : schéma du circuit
économique rendu intact en pleine largeur, grille de définitions en dessous) — rendu
conforme à l'intention dans les deux cas. FSE08 n'a pas pu être rendu par cet outil local
(temps de rendu anormalement long avec son schéma SVG spécifique, tué après plusieurs
minutes sans résultat) — la vérification pour ce cours s'est limitée à la structure HTML
(balise `<svg>` présente et intacte, aucune fuite) et aux tests unitaires, qui couvrent
exactement le même chemin de code que FSE15 (passage du bloc HTML brut).

**Limite explicite, identique aux rapports précédents** : aucun navigateur réel (Chrome/
Firefox headless, Playwright) disponible dans cet environnement — la lisibilité réelle sur
téléphone, l'ouverture/fermeture effective des accordéons `.jc-glossary`, et le
comportement à l'impression du lexique repliable (force-ouvert par une règle `@media
print`, non vérifiable sans navigateur réel) restent à confirmer par l'utilisateur.

**Comptes et données vérifiés intacts** après chaque seed : 18 utilisateurs, 67 sessions,
536 réponses — identiques avant/après, aux deux étapes. Sauvegardes de `jury_central.db`
effectuées avant chaque seed (`jury_central.db.bak-pre-ticket120-<horodatage>` et
`jury_central.db.bak-pre-ticket120-batch2-<horodatage>`).

---

## 4. Fichiers modifiés/créés

- `app/v1/fse03_course.py` — trois sections bespoke (`_section_identity`,
  `_section_traces`, `_section_image`) remplaçant `build_course_sections` pour la théorie.
- `app/v1/fse_course_sections.py` — nouvelles fonctions génériques
  `theory_prose_to_html`, `_definitions_bullets_to_items`,
  `theory_and_definitions_to_cards`, câblées dans `build_course_sections`.
- `app/static/css/design-system.css` — `.jc-prose`, `.jc-takeaway`, `.jc-glossary`,
  correctif `flex-direction` sur `.jc-flow-step`.
- `app/seed.py` — `FSE03_REPOSITION_TITLES` (nouveau mécanisme de resynchronisation),
  ajout de « Théorie : notions et définitions » à `obsolete_titles` pour FSE02-FSE16.
- `docs/components/TheoryProgression.md` (nouveau) — documente les trois nouveaux
  composants et le traitement générique.
- `tests/test_ticket120_fse03_theory.py`, `tests/test_ticket120_fse_theory_generic.py`
  (nouveaux).

---

## 5. Liens à tester

- FSE03 : **https://jury-central.lodylands.com/uaa/fse-fse03**
- FSE02 : **https://jury-central.lodylands.com/uaa/fse-fse02**
- FSE04 à FSE16 : `https://jury-central.lodylands.com/uaa/fse-fseNN` (NN = 04 à 16)
- FSE01/FSE17 (non modifiés, pour comparaison) : **fse-fse01**, **fse-fse17**

À vérifier en particulier : lisibilité réelle de la prose sur téléphone, ouverture des
lexiques repliables (FSE03, FSE04, FSE05, FSE10, FSE13), rendu du schéma FSE08 (niveaux de
pouvoir) dans un vrai navigateur.

---

## 6. Suite

Le reste du périmètre du ticket (« je vérifierai chaque cours ensuite ») est prêt à être
examiné cours par cours. FSE01 et FSE17 n'ont volontairement pas été touchés : leur
structure était déjà jugée satisfaisante (grilles, schéma, citations déjà en place).
