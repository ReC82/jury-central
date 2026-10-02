# ProfileCard, forum/recommendation variants, GroupCards

Introduits lors de l'amélioration des exemples de FSE03 (ticket #118). Composants
réutilisables, appliqués pour l'instant à FSE03 uniquement.

---

# Objectif

Présenter un ensemble de traces numériques (profil professionnel, publication, commentaire
de forum, recommandation, appartenance à des groupes) comme de vrais documents visibles,
**sans jamais révéler sur le document lui-même** la classification pédagogique qui en sera
faite (trace volontaire/involontaire, ancienne...) — cette classification reste uniquement
dans l'analyse placée après ([DecryptTitle](DecryptTitle.md)).

---

# ProfileCard (`.jc-profile-head`/`.jc-profile-portrait`)

## Structure

```html
<div class="jc-doc" id="document-profil">
  <div class="jc-doc-header"><strong>💼 Profil — réseau professionnel</strong><span class="jc-doc-fictive-badge">Fictif</span></div>
  <div class="jc-doc-body">
    <div class="jc-profile-head">
      <img src="..." alt="..." class="jc-profile-portrait" loading="lazy">
      <div>
        <p class="jc-profile-name">Nom</p>
        <p class="jc-profile-function">Fonction</p>
      </div>
    </div>
    <p class="jc-profile-summary">Résumé de parcours.</p>
  </div>
</div>
```

`.jc-profile-portrait` est volontairement petit (4,5rem, cercle) : le portrait accompagne
la carte, il ne la domine jamais — cohérent avec « dimensions raisonnables » (ticket #118).
Si l'image n'est pas disponible, un rendu de secours SVG générique (silhouette) la
remplace, jamais une image cassée.

---

# Document illustré dans une publication (`.jc-doc-scene-image`)

Pour une illustration de scène intégrée à une publication (ex. une photo d'anniversaire) :
`.jc-doc-scene-image` (largeur max 320px, coins arrondis, centrée), à l'intérieur d'un
conteneur `.jc-zoomable` (agrandissement au clic, voir le mécanisme déjà existant depuis le
ticket #110) pour une image qui mérite d'être vue en plus grand. `.jc-doc-tag` affiche une
mention neutre et factuelle (ex. « Nom identifié sur la photo ») — jamais un jugement
pédagogique (jamais « trace involontaire » écrit sur le document lui-même).

---

# GroupCards (`.jc-group-cards`/`.jc-group-card`)

## Structure

```html
<div class="jc-group-cards">
  <div class="jc-group-card">
    <span class="jc-group-icon" aria-hidden="true">🥾</span>
    <p class="jc-group-name">Nom du groupe</p>
  </div>
  <!-- une .jc-group-card par groupe -->
</div>
```

Icône + nom seulement — jamais une catégorisation du type de groupe (professionnel/loisir)
écrite sur la carte elle-même, pour la même raison que ci-dessus.

---

# Variantes de DocCard/QuoteCard déjà couvertes ailleurs

- Pour un forum (auteur, date, texte) → [DocCard](DocCard.md), `.jc-doc-meta`.
- Pour une recommandation/citation isolée → [DialogueComponents](DialogueComponents.md),
  `.jc-quote-card`.
- Pour un e-mail interne → [EmailCard](EmailCard.md), `.jc-mail-thread` à un seul message.

---

# Cohérence du personnage entre deux illustrations

Voir `app/v1/fse03_image.py` et `app.ai.image_provider.ImageProvider.edit_image()` : la
seconde illustration (scène) est générée via `POST /v1/images/edits` en utilisant la
première (portrait) comme image de référence, pas par un second appel de génération
indépendant — un appel de génération texte-seul produirait presque certainement une
apparence différente. Cette technique (et les deux appels distincts — portrait d'abord,
puis scène référençant le portrait) ne vaut que lorsque la cohérence visuelle d'un même
personnage entre plusieurs images est explicitement nécessaire.

---

# Comportement

- Texte réel, sélectionnable partout — jamais une image de texte.
- `break-inside: avoid` à l'impression (hérité de `.jc-doc`/`.jc-quote-card`).
- Aucune information nécessaire à l'analyse ou à la banque de questions n'est retirée : ces
  composants sont une présentation visuelle des mêmes textes bruts (`FSE03_*_TEXT`,
  inchangés), jamais une reformulation des faits.

---

# Exemple d'utilisation

Voir `app/v1/fse03_content.py` (les cinq documents de l'exemple 1) et
`app/v1/fse03_course.py` (`_section_examples`-équivalent, séparation document/analyse).
