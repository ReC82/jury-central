# PosterCard

Variante de [DocCard](DocCard.md), introduite lors de l'amélioration visuelle de FSE01
(ticket #108). Composant réutilisable, mais appliqué à FSE01 uniquement pour cette étape —
l'extension à d'autres cours attend un retour visuel explicite de l'utilisateur.

---

# Objectif

Présenter une affiche comme un vrai visuel (illustration + slogan + mentions), plutôt
qu'une description textuelle de ce à quoi elle ressemble. Le slogan et les mentions restent
en HTML, jamais intégrés à l'image elle-même, pour garantir leur exactitude et leur
lisibilité quelle que soit l'image utilisée.

---

# Quand l'utiliser

- Pour un document à dominante visuelle (affiche, campagne, visuel publicitaire) où une
  illustration réelle apporte davantage qu'une description textuelle.

---

# Quand ne pas l'utiliser

- Pour un mail → [EmailCard](EmailCard.md) ; pour une publication → [SocialPostCard](SocialPostCard.md).
- Pour un document officiel réel ou une reproduction d'une campagne existante → jamais :
  l'illustration est générée, jamais une reproduction d'un visuel réel, et la carte doit
  toujours indiquer explicitement qu'il s'agit d'une reconstitution pédagogique fictive,
  pas d'une véritable campagne officielle (voir `docs/content_workflow.md`).

---

# Structure

```html
<div class="jc-doc jc-poster">
  <div class="jc-doc-header">
    <strong>🪧 Affiche — ...</strong>
    <span class="jc-doc-fictive-badge">Reconstitution pédagogique fictive — pas une véritable campagne officielle</span>
  </div>
  <img src="/static/img/....png" alt="..." class="jc-poster-image" loading="lazy">
  <!-- OU, si l'image n'a pas pu être générée : -->
  <div class="jc-poster-fallback" role="img" aria-label="...">
    <svg>...</svg>
  </div>
  <div class="jc-poster-textblock">
    <p class="jc-poster-slogan">SLOGAN EN MAJUSCULES</p>
    <p class="jc-poster-subtitle">Sous-titre.</p>
  </div>
  <div class="jc-poster-footer">
    <span>Logo (fictif) : ...</span>
    <span>QR code (fictif) : ...</span>
  </div>
</div>
```

---

# Choix technique : image statique générée une fois, jamais à la demande

Voir `app/v1/fse01_image.py` pour le mécanisme complet (ticket #108 § 4) :

- L'illustration est générée **une seule fois** via l'API OpenAI
  (`app.ai.image_provider.ImageProvider`, `POST /v1/images/generations`) et **enregistrée
  durablement** comme fichier statique (`app/static/img/`) — jamais un appel API à
  l'ouverture du cours, jamais une régénération automatique au seed ou au déploiement.
- Le slogan, le sous-titre et les mentions (logo, QR code) restent du texte HTML
  (`.jc-poster-textblock`/`.jc-poster-footer`), jamais intégrés dans l'image elle-même : un
  modèle de génération d'images ne garantit pas un texte exact ni toujours lisible.
- Le prompt exact et le modèle utilisé sont conservés dans un fichier de métadonnées
  sidecar (`<nom-image>.json`), à côté de l'image — pour audit et reproductibilité.
- Remplacement manuel : `generate-fse01-poster-image --force` (voir `pyproject.toml`,
  `[project.scripts]`) régénère l'image (au maximum une seconde tentative en cas d'échec
  technique) ; sans `--force`, la commande ne fait rien si l'image existe déjà.
- Si l'image n'a jamais été générée (ou a été supprimée), `_poster_visual_html()` (dans
  `app/v1/fse01_content.py`) bascule automatiquement sur `.jc-poster-fallback` : un rendu
  pédagogique de secours en SVG pur, jamais une image cassée ni un faux succès.

---

# Comportement

- `.jc-poster-image { width: 100%; height: auto; }` : responsive, jamais de défilement
  horizontal, jamais de texte coupé (le texte n'est de toute façon pas dans l'image).
- `.jc-poster-textblock` (fond rouge plein, texte blanc) : contraste garanti
  indépendamment du contenu de l'image, plutôt qu'un texte superposé en transparence sur
  l'image (risque de lisibilité variable selon l'image générée).
- `break-inside: avoid` hérité de `.jc-doc` ; à l'impression, l'image est plafonnée en
  hauteur (`object-fit: cover`) pour ne jamais faire déborder la page.

---

# Composants liés

- [DocCard](DocCard.md) — habillage externe commun.
- [Diagram](Diagram.md) — autre cas d'usage SVG (schéma relationnel plutôt qu'illustration).

---

# Exemple d'utilisation

Voir `app/v1/fse01_content.py::FSE01_AFFICHE_CARD_HTML` et `app/v1/fse01_image.py`
(affiche de sécurité routière, silhouette d'enfant traversant devant une voiture qui
ralentit).
