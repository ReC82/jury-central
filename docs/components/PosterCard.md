# PosterCard

Introduit lors de l'amélioration visuelle de FSE01 (ticket #108), recomposé en une seule
composition après un premier retour visuel (ticket #110 : le premier essai ressemblait à
une illustration suivie d'un bandeau séparé). Composant réutilisable, mais appliqué à FSE01
uniquement pour cette étape — l'extension à d'autres cours attend un retour visuel
explicite de l'utilisateur.

---

# Objectif

Présenter une affiche comme une **seule composition visuelle crédible** : slogan,
sous-titre, identité graphique d'émetteur et QR code superposés directement sur
l'illustration — jamais des blocs de texte empilés en dessous. Largeur bornée (~440px sur
ordinateur), proportions toujours préservées, agrandissable au clic.

---

# Quand l'utiliser

- Pour un document à dominante visuelle (affiche, campagne, visuel publicitaire) où une
  illustration réelle, avec ses éléments intégrés, apporte davantage qu'une description
  textuelle ou qu'une image suivie d'un bloc de texte séparé.

---

# Quand ne pas l'utiliser

- Pour un mail → [EmailCard](EmailCard.md) ; pour une publication → [SocialPostCard](SocialPostCard.md).
- Pour un document officiel réel ou une reproduction d'une campagne existante → jamais :
  l'illustration est générée, jamais une reproduction d'un visuel réel ; une mention
  « Document pédagogique fictif » reste visible à l'extérieur de la composition, et aucun
  logo inventé ne doit être présenté comme le logo officiel de l'organisme cité (l'identité
  graphique à l'intérieur de l'affiche reste un badge générique, jamais une tentative de
  reproduire un véritable blason/logo d'État).

---

# Structure

```html
<div class="jc-poster-wrap">
  <figure class="jc-poster">
    <div class="jc-poster-visual jc-zoomable" role="img" aria-label="Description complète">
      <img src="/static/img/....png" alt="" class="jc-poster-image" loading="lazy">
      <!-- OU, si l'image n'a pas pu être générée : -->
      <div class="jc-poster-fallback-visual"><svg>...</svg></div>

      <div class="jc-poster-slogan-zone">
        <p class="jc-poster-slogan">SLOGAN EN MAJUSCULES</p>
        <p class="jc-poster-subtitle">Sous-titre.</p>
      </div>
      <div class="jc-poster-badge" aria-hidden="true">
        <div class="jc-poster-badge-circle"><svg>...</svg></div>
        <span class="jc-poster-badge-label">Nom de l'émetteur</span>
      </div>
      <div class="jc-poster-qr" aria-hidden="true">
        <div class="jc-poster-qr-box"><svg>...vrai QR code...</svg></div>
      </div>
    </div>
  </figure>
  <p class="jc-poster-caption">Document pédagogique fictif — pas une véritable campagne
  officielle. Cliquer sur l'affiche pour l'agrandir. Le QR code renvoie vers une vraie page
  d'information : <a href="https://...">...</a>.</p>
</div>
```

Un seul conteneur (`.jc-poster-visual`) porte l'image ET les trois superpositions
(slogan/sous-titre, identité, QR) en position absolue — tout est à l'intérieur de la même
composition. La légende « Document pédagogique fictif » reste à l'extérieur
(`.jc-poster-caption`), discrète, jamais à l'intérieur de l'affiche elle-même.

---

# Choix technique

## Dimensionnement : `max-width` + unités `cqw` (container query), pas de JS

`.jc-poster-wrap { max-width: 440px; margin: 0 auto; }` centre et borne la largeur sur
ordinateur ; sur téléphone, la largeur s'adapte naturellement à l'écran (pas de largeur
fixe). `.jc-poster-visual` déclare `container-type: inline-size` : le texte superposé
(slogan, sous-titre, étiquette de l'identité) est dimensionné en `cqw` (pourcentage de la
largeur du conteneur, pas du viewport) — il reste proportionné que la composition fasse
320px (téléphone), 440px (ordinateur) ou 620px (agrandie au clic), sans recalcul JS.
L'image garde `width:100%; height:auto` : jamais d'étirement ni de recadrage.

## Agrandissement au clic : le même élément s'agrandit, pas une image séparée

`.jc-zoomable` (voir `enableZoomableImages()` dans `design_system.js`, générique et
réutilisable par tout visuel, pas seulement l'affiche) : au clic, l'élément passe en
`position: fixed` et s'agrandit sur place (`.jc-zoomable--active`, voir
`design-system.css`) avec un fond semi-opaque derrière — la composition complète (texte
superposé inclus) reste visible en grand, contrairement à un lien vers le fichier image
brut qui perdrait le slogan/l'identité/le QR (non présents dans le PNG lui-même).

## Image statique générée une fois, jamais à la demande

Voir `app/v1/fse01_image.py` (ticket #108 § 4) : l'illustration est générée **une seule
fois** via l'API OpenAI et **enregistrée durablement** comme fichier statique
(`app/static/img/`) — jamais un appel API à l'ouverture du cours, jamais une régénération
automatique au seed/déploiement. Remplacement manuel : `generate-fse01-poster-image --force`.
Si l'image n'a jamais été générée (ou a été supprimée), `_poster_visual_inner_html()` (dans
`app/v1/fse01_content.py`) bascule automatiquement sur `.jc-poster-fallback-visual` : un
rendu pédagogique de secours en SVG pur, jamais une image cassée.

## QR code : un vrai visuel scannable, vers une destination réelle et vérifiée

Généré une fois avec la bibliothèque `qrcode` (outil de développement, jamais une
dépendance du projet — voir `app/static/img/fse01_qr_vitesse.svg`), encodant une URL
réelle, vérifiée avant utilisation, et cohérente avec l'analyse du document existante
(le QR renvoie vers une page d'information, jamais vers un canal de réponse à l'émetteur —
voir la nuance déjà présente dans `app.v1.fse01_course`, section Exemples : une page
d'information consultée ne constitue pas, à elle seule, une rétroaction adressée à
l'émetteur). Le SVG est lu depuis le fichier à l'import du module et ses attributs
`width`/`height` figés sont retirés pour laisser `.jc-poster-qr-box svg` contrôler la
taille d'affichage.

## Identité graphique de l'émetteur : un badge générique, jamais un logo inventé présenté comme officiel

Un simple cercle avec un monogramme (ex. « SPW ») plus une étiquette texte — jamais une
tentative de reproduire le véritable blason/logo de l'organisme cité. Le document reste de
toute façon étiqueté comme fictif (`.jc-poster-caption`).

---

# Comportement

- `break-inside: avoid` implicite (le `<figure>` ne se scinde pas à l'impression) ;
  `max-width` réduite à l'impression pour ne jamais déborder une page A4.
- `.jc-poster-badge`/`.jc-poster-qr` sont ancrés par `bottom`/`right`/`left` (jamais `top`) :
  un contenu plus long (ex. une étiquette sur plusieurs lignes) pousse vers le haut, ne
  déborde jamais sous l'image.
- Aucune information nécessaire à l'analyse n'est retirée : le texte brut du document
  (`FSE01_AFFICHE_TEXT`, utilisé par la banque de questions) reste inchangé par ce
  composant, qui n'en est qu'une présentation visuelle.

---

# Composants liés

- [DocCard](DocCard.md) — habillage utilisé par EmailCard/SocialPostCard ; PosterCard a sa
  propre structure (`.jc-poster-wrap`/`.jc-poster`), plus compacte, sans
  `.jc-doc-header`/badge pleine largeur.
- [Diagram](Diagram.md) — autre cas d'usage SVG (schéma relationnel plutôt qu'illustration).

---

# Exemple d'utilisation

Voir `app/v1/fse01_content.py::FSE01_AFFICHE_CARD_HTML`, `app/v1/fse01_image.py` (génération
de l'illustration) et `app/static/img/fse01_qr_vitesse.svg` (QR code vers
`https://www.awsr.be/securite-routiere/vitesse/`, vérifiée avant utilisation).
