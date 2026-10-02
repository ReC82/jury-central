# DocCard

Composant interne à une carte, introduit lors de la refonte pédagogique et visuelle des
cours FSE (ticket #103).

---

# Objectif

Présenter un document support (mail, affiche, publication sur réseau social...) sous une
forme concrète et lisible, clairement séparée de son analyse — jamais un bloc de texte
brut mêlant le document et son commentaire.

---

# Quand l'utiliser

- Pour tout document fictif servant de support à une analyse (candidature par mail,
  publication avec commentaires, affiche...).
- L'analyse du document reste TOUJOURS à l'extérieur du `DocCard`, juste après, en texte,
  tableau ou liste structurée — jamais mélangée dans le document lui-même.

---

# Quand ne pas l'utiliser

- Pour un exemple résolu classique (énoncé + résolution + réponse) → `ExampleCard`.
- Pour un document officiel réel → jamais : seuls des documents fictifs, explicitement
  présentés comme tels, sont utilisés dans Jury Central (voir `docs/content_workflow.md`).

---

# Structure

```html
<div class="jc-doc">
  <div class="jc-doc-header">
    <strong>Type de document (ex. Mail)</strong>
    <span class="jc-doc-fictive-badge">Fictif</span>
  </div>
  <div class="jc-doc-body">
    <dl class="jc-doc-meta">
      <dt>De :</dt><dd>...</dd>
      <dt>À :</dt><dd>...</dd>
      <dt>Objet :</dt><dd>...</dd>
    </dl>
    <div class="jc-doc-text"><p>...</p></div>
    <div class="jc-doc-comments">
      <p class="jc-doc-comment"><strong>Nom :</strong> commentaire</p>
    </div>
  </div>
</div>
```

`.jc-doc-meta`/`.jc-doc-comments` sont optionnels selon le type de document (un mail a des
métadonnées, une affiche n'en a pas ; une publication a des commentaires).

---

# Comportement

- Toujours une étiquette « Fictif » visible (`.jc-doc-fictive-badge`) : aucun document
  présenté dans Jury Central ne doit pouvoir être pris pour un document réel.
- `break-inside: avoid` à l'impression.
- Couleurs neutres (gris clair pour l'en-tête) : le document ne doit pas entrer en
  compétition visuelle avec les cartes du Design System qui l'entourent.

---

# Composants liés

- [ExampleCard](ExampleCard.md) — carte dans laquelle un `DocCard` est généralement inséré,
  suivi de son analyse en dehors du `DocCard`.

---

# Exemple d'utilisation

```markdown
<div class="jc-doc">
<div class="jc-doc-header"><strong>Mail</strong><span class="jc-doc-fictive-badge">Fictif</span></div>
<div class="jc-doc-body">
<dl class="jc-doc-meta">
<dt>De :</dt><dd>Lucas Mertens</dd>
<dt>À :</dt><dd>Service recrutement</dd>
<dt>Objet :</dt><dd>Candidature poste de vendeur</dd>
</dl>
<div class="jc-doc-text"><p>Madame, Monsieur, ...</p></div>
</div>
</div>
```
