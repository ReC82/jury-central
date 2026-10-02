# Diagram

Composant interne à une carte, introduit lors de la refonte pédagogique et visuelle des
cours FSE (ticket #103), pour remplacer les schémas en caractères (ASCII) par de vrais
rendus graphiques.

---

# Objectif

Représenter une notion relationnelle (schéma, hiérarchie, circuit) par un vrai dessin —
blocs lisibles, flèches, libellés — plutôt que par de l'art ASCII dans un bloc de code, qui
ne fonctionne ni sur mobile ni à l'impression de façon fiable.

---

# Choix technique : SVG natif, pas de nouvelle dépendance

Avant d'introduire une bibliothèque de diagrammes, vérification de l'existant : le projet
n'a aucune dépendance JS de diagramme (recherche dans `app/static/js/`, `pyproject.toml`).
`docs/UI_GUIDELINES.md` (section « Illustrations ») recommande explicitement SVG, Canvas ou
Plotly, et un composant `.jc-flow` (CSS pur, HTML) existe déjà pour les enchaînements
linéaires simples.

Décision : **SVG écrit à la main**, inline dans le Markdown (passé tel quel par
`app/content.py`, comme tout HTML brut) :
- aucune dépendance supplémentaire (ni CDN, ni paquet Python/JS) ;
- redimensionnement responsive natif via `viewBox` + `max-width: 100%` (CSS) ;
- impression fiable (vecteur, jamais de texte coupé) ;
- cohérent avec la palette de couleurs du Design System (variables CSS `--jc-*`) ;
- une bibliothèque de diagrammes (type Mermaid) n'a pas été retenue : dépendance
  supplémentaire, chargement JS côté client, et rendu moins contrôlable pour des schémas
  non strictement arborescents (ex. boucle de rétroaction, obstacle positionné sur un
  trajet) que le cas d'usage réel de ce ticket nécessite.

`.jc-flow` (déjà existant) reste réutilisé pour les enchaînements VRAIMENT linéaires
(étape 1 → étape 2 → étape 3, sans branche ni boucle) : seuls les schémas relationnels plus
riches (boucle de rétroaction, hiérarchie à plusieurs niveaux, circuit à plusieurs agents)
utilisent ce composant SVG.

---

# Quand l'utiliser

- Pour un schéma relationnel (plusieurs éléments reliés par des flèches, éventuellement une
  boucle de retour) qui ne se représente pas naturellement comme un enchaînement linéaire.

---

# Quand ne pas l'utiliser

- Pour un enchaînement simple d'étapes → `.jc-flow` (déjà existant, plus léger).
- Pour une donnée chiffrée (graphique, histogramme) → Plotly (déjà intégré au projet pour
  d'autres besoins, voir `needs_plotly` dans `app/main.py`), pas ce composant.

---

# Structure

```html
<div class="jc-diagram" role="img" aria-label="Description textuelle complète du schéma">
  <svg viewBox="0 0 900 440" xmlns="http://www.w3.org/2000/svg">
    ...
  </svg>
</div>
```

`role="img"` + `aria-label` obligatoires : le contenu du SVG (texte dans des `<text>`,
souvent de petite taille) n'est pas un substitut fiable pour les lecteurs d'écran.

---

# Comportement

- `svg { max-width: 100%; height: auto; }` : jamais de défilement horizontal, jamais de
  texte coupé sur mobile — le `viewBox` garantit la mise à l'échelle proportionnelle.
- `break-inside: avoid` à l'impression.
- Couleurs tirées des variables `--jc-*` existantes (jamais de nouvelle palette).

---

# Composants liés

- `.jc-flow` (`design-system.css`) — enchaînement linéaire simple, cas plus fréquent, à
  préférer quand il convient.

---

# Exemple d'utilisation

Voir `app/v1/fse01_content.py` (schéma de la communication : émetteur, récepteur, message,
code, canal, contexte, obstacle, boucle de rétroaction).
