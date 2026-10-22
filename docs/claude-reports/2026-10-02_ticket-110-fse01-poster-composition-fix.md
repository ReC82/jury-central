# Rapport — Ticket #110 : recomposition de l'affiche FSE01 en une seule composition

Branche : `fix/108-fse01-poster-composition` (depuis `develop`). PR #111 fusionnée dans
`develop`, puis installée sur `jury-central.lodylands.com`.

**SHA installé : `f7356ad`** (merge commit de la PR #111 dans `develop`). Fait suite au
ticket #108 (PR #109, SHA `8b57101`) et au retour visuel de l'utilisateur.

---

## 1. Diagnostic du retour

Le rendu livré au ticket #108 empilait trois blocs visuellement disjoints : l'illustration,
puis un bandeau rouge plein largeur (slogan/sous-titre), puis une ligne de mentions grises
— ce qui donnait l'impression d'« une illustration suivie d'un bandeau », pas d'une
affiche. Aucune largeur maximale n'était fixée : l'image (1024×1536, format portrait)
s'étalait à la pleine largeur de la carte sur grand écran, d'où l'effet « trop grand ».

---

## 2. Dimensions

- `.jc-poster-wrap { max-width: 440px; margin: 0 auto; }` : affiche centrée, largeur
  bornée sur ordinateur.
- `.jc-poster-image { width: 100%; height: auto; }` (inchangé) : proportions de l'image
  toujours préservées, jamais d'étirement ni de recadrage.
- Sur téléphone, `max-width` cède la place à la largeur réelle de l'écran (pas de largeur
  fixe) : la composition occupe toute la largeur disponible jusqu'à 440px.
- **Agrandissement au clic** : nouveau comportement générique `.jc-zoomable`
  (`enableZoomableImages()`, `app/static/js/design_system.js`) — au clic (ou Entrée/Espace
  au clavier), l'élément passe en position fixe et s'agrandit sur place
  (`width: min(94vw, 620px)`) avec un fond semi-opaque ; un second clic (ou Échap, ou clic
  sur le fond) referme. La composition complète s'agrandit — texte superposé inclus —
  plutôt qu'un lien vers le fichier image brut (qui aurait perdu le slogan/l'identité/le
  QR, absents du PNG lui-même). Réutilisable par tout futur visuel marqué `.jc-zoomable`.
- Grandes zones vides supprimées : plus de bandeau ni de ligne de mentions séparés en
  dessous ; le slogan/sous-titre utilise l'espace déjà présent dans le haut de
  l'illustration plutôt que d'ajouter de la hauteur supplémentaire à la carte.

---

## 3. Composition unique

Slogan, sous-titre, identité d'émetteur et QR code sont désormais superposés en HTML/SVG
**directement sur l'illustration**, dans un seul conteneur `.jc-poster-visual` :

- **Slogan + sous-titre** : zone absolue en haut de l'image (`.jc-poster-slogan-zone`),
  dans l'espace déjà vide de l'illustration générée.
- **Identité graphique d'émetteur** (bas à droite) : un badge circulaire générique
  (monogramme « SPW ») + étiquette texte « Sécurité routière Wallonie » — **jamais une
  tentative de reproduire le véritable logo/blason du SPW** : un simple cercle avec un
  monogramme, clairement un badge générique, pas une copie d'un symbole officiel réel.
- **QR code** (bas à gauche) : un vrai visuel de QR code scannable (voir § 4), sur un fond
  blanc pour garantir le contraste.
- Dimensionnement en unités `cqw` (container query, `container-type: inline-size` sur
  `.jc-poster-visual`) : le texte reste proportionné à la largeur réelle de la composition,
  que ce soit 320px (téléphone), 440px (ordinateur) ou 620px (agrandie) — sans recalcul JS.

Les phrases placeholder « Logo (bas à droite, fictif) : ... » et « QR code (bas à gauche,
fictif) : ... » ont été supprimées. La mention « Document pédagogique fictif — pas une
véritable campagne officielle » reste présente, mais **à l'extérieur** de la composition
(`.jc-poster-caption`, sous l'affiche), discrète (texte gris, taille réduite), avec en plus
un lien texte explicite vers la vraie destination du QR code (utile aux lecteurs qui ne
peuvent pas scanner un QR affiché à l'écran).

---

## 4. QR code réel, vérifié, cohérent avec l'analyse

- **Génération** : bibliothèque `qrcode` (Python), utilisée comme **outil de
  développement local uniquement** — jamais ajoutée comme dépendance du projet
  (`pyproject.toml` inchangé). Le fichier généré (`app/static/img/fse01_qr_vitesse.svg`,
  vectoriel) est committé comme asset statique, lu et inliné dans la composition au
  chargement du module (lecture disque, pas un appel réseau).
- **Destination vérifiée avant utilisation** : recherche web, puis lecture de page pour
  confirmer qu'il s'agit d'une page réelle et pertinente :
  **`https://www.awsr.be/securite-routiere/vitesse/`** — page officielle de l'Agence
  wallonne pour la Sécurité routière (AWSR), consacrée à la vitesse (1 accident mortel sur
  3 lié à une vitesse excessive/inadaptée, adaptation de la vitesse en zone résidentielle,
  distances d'arrêt). Cohérente avec le texte du document, **inchangé**
  (`FSE01_AFFICHE_TEXT` : « une page d'information sur les limitations de vitesse en zone
  habitée »).
- **QR décodé et vérifié techniquement** avant livraison : test de décodage avec
  OpenCV (`cv2.QRCodeDetector`), confirmant que le code encode exactement
  `https://www.awsr.be/securite-routiere/vitesse/`, aucune faute de frappe.
- **Cohérence avec l'analyse existante** (non modifiée) : `app.v1.fse01_course`, section
  Exemples, précise déjà que la rétroaction de l'affiche est « indirecte (vers une page
  d'information, pas vers l'émetteur) » — le nouveau QR réel reste parfaitement cohérent
  avec cette nuance : consulter une page d'information ne constitue toujours pas, à lui
  seul, une réponse adressée au SPW.

---

## 5. Livraison : image réutilisée, aucune nouvelle génération

L'illustration générée au ticket #108 (silhouette d'enfant au passage piéton, voiture qui
ralentit) convenait déjà après recomposition — **aucun nouvel appel à l'API de génération
d'images n'a été nécessaire**. Le fichier `app/static/img/fse01_affiche_securite_routiere.png`
et ses métadonnées (`.json`) sont inchangés.

---

## 6. Tests exécutés (ciblés, pas la suite complète de 1 419 tests)

| Lot | Résultat |
|---|---|
| `tests/test_card_kind.py`, `tests/test_ticket96_fse01.py`, `tests/test_admin_content_hierarchy.py`, `tests/ai/test_image_provider.py`, `tests/test_ticket108_fse01_poster_image.py` | 67/67 ✅ |
| `tests/test_ticket102_coverage.py` | 52/52 ✅ |

Exécutés deux fois : sur la branche avant fusion, puis sur le checkout de production après
fast-forward, avant le seed.

**Vérification structurelle de la page réelle en production** (`/uaa/fse-fse01`) : tous les
nouveaux sélecteurs de composition présents, les deux phrases placeholder absentes, la
mention fictive présente, l'URL réelle du QR présente dans la page (lien texte), l'ancien
bandeau/footer séparés absents, CSS et JS des nouvelles règles chargés en 200, asset SVG du
QR servi en 200.

**Prévisualisation visuelle locale** (HTML réel → PDF → image, WeasyPrint, outil de
développement uniquement, jamais une dépendance du projet) à deux largeurs : ~440px
(ordinateur) et ~350px (téléphone) — composition cohérente dans les deux cas, slogan et
sous-titre bien positionnés dans l'espace vide du haut de l'illustration, badge et QR
lisibles en bas, aucun chevauchement avec l'illustration, aucun débordement visible.

**Limite explicite, identique aux rapports précédents** : aucun navigateur réel (Chrome/
Firefox headless, Playwright) disponible dans cet environnement — l'interaction
d'agrandissement au clic n'a pas pu être testée en conditions réelles (clic, focus clavier,
fermeture), seule la logique JS/CSS a été relue et validée syntaxiquement (`node --check`).
La vérification visuelle finale dans un vrai navigateur reste à faire par l'utilisateur.

**Comptes et données vérifiés intacts** après le seed de production : 18 utilisateurs, 67
sessions, 536 réponses — identiques avant/après. Sauvegarde de `jury_central.db` effectuée
avant le seed : `jury_central.db.bak-pre-ticket110-<horodatage>`.

---

## 7. Fichiers modifiés/créés

- `app/v1/fse01_content.py` — composition de l'affiche entièrement reprise (texte brut
  `FSE01_AFFICHE_TEXT` inchangé).
- `app/static/css/design-system.css` — nouvelles règles `.jc-poster-wrap/-visual/
  -slogan-zone/-badge/-qr/-caption`, `.jc-zoomable--active`, `.jc-zoom-backdrop` ; anciennes
  règles `.jc-poster-textblock`/`.jc-poster-footer` retirées.
- `app/static/js/design_system.js` — `enableZoomableImages()` (générique, réutilisable).
- `app/static/img/fse01_qr_vitesse.svg` (nouveau) — vrai QR code vers la page AWSR.
- `docs/components/PosterCard.md` — réécrit pour refléter la nouvelle composition.

---

## 8. Lien à tester

- Page de cours FSE01 : **https://jury-central.lodylands.com/uaa/fse-fse01**

À vérifier en particulier : taille de l'affiche sur grand écran (doit rester compacte,
~440px), lisibilité du slogan/sous-titre/badge/QR sur téléphone, fonctionnement du clic
pour agrandir (et de la fermeture), rendu à l'impression.

---

## 9. Arrêt avant extension aux autres cours

Conformément à la demande initiale (ticket #108) et à celle-ci, le travail reste limité à
FSE01. Les composants restent prêts à être étendus à FSE02-17 sur confirmation visuelle
explicite.
