# Composants de dialogue : ChatThread, QuoteCard, couleurs génériques d'intervenant

Introduits lors de l'extension de la présentation de FSE01 à FSE02-17 (ticket #115).
Composants réutilisables, appliqués pour l'instant à FSE02, FSE04, FSE07 et FSE16 — à
étendre à d'autres cours selon les besoins identifiés lors de la validation cours par
cours.

---

# Objectif

Donner une forme réaliste à un échange à plusieurs voix (groupe en ligne, chat de classe,
réactions de plusieurs parties prenantes) sans réinventer un composant par cours : chaque
intervenant garde une couleur stable, partout où il apparaît dans le même document.

---

# Couleurs génériques d'intervenant (`.jc-social-avatar--p1` à `--p5`)

Cinq classes de couleur (bleu, violet, vert, orange, or — mêmes variables `--jc-*` que le
reste du Design System), à attribuer **par ordre d'apparition** dans un document donné,
jamais au hasard ni de façon incohérente d'un document à l'autre. Utilisées sur
`.jc-social-avatar` (cercle d'initiales, déjà existant depuis FSE01) dans tous les
composants ci-dessous.

---

# ChatThread (`.jc-chat-thread`/`.jc-chat-message`)

## Quand l'utiliser

Pour un échange de messages successifs avec horodatage (chat de groupe, messagerie) —
plus léger que [EmailCard](EmailCard.md) (pas d'en-tête de/à, juste auteur + heure).

## Structure

```html
<div class="jc-chat-thread">
  <div class="jc-chat-message">
    <span class="jc-social-avatar jc-social-avatar--sm jc-social-avatar--p1">Y</span>
    <div>
      <div class="jc-chat-meta"><span class="jc-chat-author">Yasmine</span><span class="jc-chat-time">12 mars, 12h41</span></div>
      <p class="jc-chat-text">« ... »</p>
    </div>
  </div>
  <!-- un .jc-chat-message par message, même pNN pour la même personne -->
</div>
```

## Exemple d'utilisation

`app/v1/fse07_content.py::FSE07_CHAT_CARD_HTML` (4 élèves, 7 messages).

---

# QuoteCard (`.jc-quote-card`)

## Quand l'utiliser

Pour une ou plusieurs voix isolées (témoignage, réaction d'une partie prenante) — pas un
fil de discussion, chaque citation est indépendante des autres.

## Structure

```html
<div class="jc-quote-card">
  <span class="jc-social-avatar jc-social-avatar--p1">🏠</span>
  <div>
    <span class="jc-quote-author">Un ménage concerné</span>
    <p class="jc-quote-text">« ... »</p>
  </div>
</div>
```

L'avatar peut porter des initiales ou un pictogramme représentant le rôle (ex. 🏠 pour un
ménage, 🚌 pour une entreprise de transport) plutôt qu'un vrai nom, quand la source est un
rôle générique et non une personne identifiée.

## Exemple d'utilisation

`app/v1/fse04_content.py::FSE04_TESTIMONY_CARD_HTML` (un témoignage isolé),
`app/v1/fse16_content.py::FSE16_REACTIONS_CARD_HTML` (trois réactions de parties prenantes
différentes).

---

# Pages de médias réalistes (ticket #115, FSE02 uniquement pour l'instant)

Composants ad hoc (`.jc-webpage-masthead`, `.jc-pricing-cards`, `.jc-ad-banner`,
`.jc-webpage-feature`...) construits sur [DocCard](DocCard.md) pour représenter une page de
média (abonnement, actualité, institutionnel) — voir `app/v1/fse02_content.py` pour
l'exemple complet (L'Hebdo du Littoral, Le Flash Infos, Radio Communauté Wallonie). Pas
encore généralisés en composant nommé unique : chaque page de média a une structure propre
(cartes de tarifs, bannières publicitaires, fonctionnalité institutionnelle) choisie selon
ce que le document doit montrer, conformément à la consigne de ne pas forcer un même
gabarit partout.

---

# Comportement commun

- Texte réel, sélectionnable — jamais une image.
- `break-inside: avoid` à l'impression (`.jc-chat-message`, `.jc-quote-card`).
- Aucune information nécessaire à l'analyse ou à la banque de questions n'est retirée : ces
  composants sont une présentation visuelle des mêmes textes bruts (`FSE0N_*_TEXT`,
  inchangés), jamais une reformulation des faits.

---

# Composants liés

- [SocialPostCard](SocialPostCard.md) — publication + commentaires avec réactions
  (compteur, partages), cas plus complet qu'un simple ChatThread/QuoteCard.
- [DocCard](DocCard.md) — habillage externe commun (en-tête, étiquette Fictif).
