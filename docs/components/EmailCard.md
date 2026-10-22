# EmailCard

Variante de [DocCard](DocCard.md), introduite lors de l'amélioration visuelle de FSE01
(ticket #108). Composant réutilisable, mais appliqué à FSE01 uniquement pour cette étape —
l'extension à d'autres cours attend un retour visuel explicite de l'utilisateur.

---

# Objectif

Présenter un mail comme un vrai message de messagerie (en-tête, avatar, objet, fil de
réponse), avec un texte réel et sélectionnable — jamais une image, jamais un simple bloc de
texte brut imitant vaguement un mail.

---

# Quand l'utiliser

- Pour tout document support de type mail/messagerie, notamment lorsqu'un échange
  (message + réponse) doit être visible dans le même document.

---

# Quand ne pas l'utiliser

- Pour une publication de réseau social → [SocialPostCard](SocialPostCard.md).
- Pour une affiche ou un document à dominante visuelle → [PosterCard](PosterCard.md).
- Pour un document officiel réel → jamais : seuls des documents fictifs, explicitement
  présentés comme tels, sont utilisés dans Jury Central (voir `docs/content_workflow.md`).

---

# Structure

```html
<div class="jc-doc jc-mail">
  <div class="jc-doc-header">
    <strong>✉️ Mail — ...</strong>
    <span class="jc-doc-fictive-badge">Fictif</span>
  </div>
  <div class="jc-mail-thread">
    <div class="jc-mail-message">
      <div class="jc-mail-message-head">
        <span class="jc-mail-avatar">AB</span>
        <div class="jc-mail-meta">
          <span class="jc-mail-from">Nom <span class="jc-mail-address">&lt;mail&gt;</span></span>
          <span class="jc-mail-to">à destinataire@...</span>
        </div>
        <span class="jc-mail-date">12 mars, 9h04</span>
      </div>
      <p class="jc-mail-subject">Objet du message</p>
      <div class="jc-mail-body">
        <p>...</p>
        <p class="jc-mail-interrupted">⚠️ Message interrompu ici...</p>
      </div>
    </div>
    <div class="jc-mail-message jc-mail-message--reply">
      <!-- même structure, avatar .jc-mail-avatar--reply (couleur différente) -->
    </div>
  </div>
</div>
```

`.jc-mail-message--reply` (fond légèrement teinté + avatar de couleur différente) distingue
visuellement une réponse du message initial, sans dupliquer l'en-tête `.jc-doc-header`.
`.jc-mail-interrupted` encadre un passage interrompu ou anormal (ex. coupure de connexion)
en rouge pointillé — à utiliser uniquement quand le document en contient réellement un,
jamais systématiquement.

---

# Comportement

- Avatar = initiales dans un cercle de couleur (`var(--jc-blue)` pour le message initial,
  `var(--jc-green)` pour une réponse) — jamais une vraie photo.
- `.jc-mail-message-head` passe en colonne sous 576px (adresse/objet souvent longs) : pas de
  défilement horizontal, texte toujours entièrement lisible.
- `break-inside: avoid` hérité de `.jc-doc` à l'impression.
- Texte réel (jamais une image) : sélectionnable, copiable, accessible aux lecteurs d'écran
  et aux outils de recherche dans la page.

---

# Composants liés

- [DocCard](DocCard.md) — habillage externe commun (en-tête, étiquette Fictif).
- [SocialPostCard](SocialPostCard.md) — publication de réseau social.

---

# Exemple d'utilisation

Voir `app/v1/fse01_content.py::FSE01_MAIL_CARD_HTML` (candidature par mail interrompue par
une coupure de connexion, avec la réponse du service recrutement).
