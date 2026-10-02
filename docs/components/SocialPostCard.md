# SocialPostCard

Variante de [DocCard](DocCard.md), introduite lors de l'amélioration visuelle de FSE01
(ticket #108). Composant réutilisable, mais appliqué à FSE01 uniquement pour cette étape —
l'extension à d'autres cours attend un retour visuel explicite de l'utilisateur.

---

# Objectif

Présenter une publication de réseau social comme un vrai post (auteur, texte, réactions,
fil de commentaires), avec un texte réel et sélectionnable — jamais une image, jamais un
bloc de texte brut imitant vaguement un fil de commentaires.

---

# Quand l'utiliser

- Pour tout document support de type publication/réseau social, notamment lorsque des
  commentaires (y compris une réponse de l'émetteur) doivent être visibles.

---

# Quand ne pas l'utiliser

- Pour un mail → [EmailCard](EmailCard.md).
- Pour une affiche ou un document à dominante visuelle → [PosterCard](PosterCard.md).
- Pour un document officiel réel → jamais (voir `docs/content_workflow.md`).

---

# Structure

```html
<div class="jc-doc jc-social">
  <div class="jc-doc-header">
    <strong>📱 Publication — ...</strong>
    <span class="jc-doc-fictive-badge">Fictif</span>
  </div>
  <div class="jc-doc-body">
    <div class="jc-social-post-head">
      <span class="jc-social-avatar">AB</span>
      <div class="jc-social-meta">
        <span class="jc-social-author">Nom de la page</span>
        <span class="jc-social-time">Publié il y a 3 heures</span>
      </div>
    </div>
    <p class="jc-social-text">« ... »</p>
    <div class="jc-social-reactions">
      <span>👍 24 réactions</span><span>💬 7 commentaires</span><span>🔁 5 partages</span>
    </div>
    <div class="jc-social-comments">
      <div class="jc-social-comment">
        <span class="jc-social-avatar jc-social-avatar--sm">XY</span>
        <div><strong>Nom</strong><p>« ... »</p></div>
      </div>
      <div class="jc-social-comment jc-social-comment--company">
        <span class="jc-social-avatar jc-social-avatar--sm">AB</span>
        <div><strong>Nom de la page</strong><span class="jc-social-reply-badge">Réponse de l'entreprise</span><p>« ... »</p></div>
      </div>
    </div>
  </div>
</div>
```

`.jc-social-comment--company` (fond bleu clair) + `.jc-social-reply-badge` distinguent
visuellement une réponse de l'émetteur au milieu des commentaires des autres utilisateurs,
sans avoir à la décrire en toutes lettres dans le texte du commentaire lui-même.

---

# Comportement

- Avatar = initiales dans un cercle orange (`var(--jc-orange)`) — jamais une vraie photo.
- Les réactions (`.jc-social-reactions`) sont un simple résumé texte, pas des boutons
  interactifs : ce document n'est jamais modifiable par l'élève.
- `break-inside: avoid` hérité de `.jc-doc` à l'impression.
- Texte réel (jamais une image) : sélectionnable, copiable, accessible.

---

# Composants liés

- [DocCard](DocCard.md) — habillage externe commun.
- [EmailCard](EmailCard.md) — document de type mail.

---

# Exemple d'utilisation

Voir `app/v1/fse01_content.py::FSE01_SOCIAL_CARD_HTML` (offre d'emploi avec commentaires et
réponse de l'entreprise).
