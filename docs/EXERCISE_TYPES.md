# Moteur d'exercices interactifs

Ce document définit le format officiel des exercices interactifs de Jury Central.

L'objectif est que tous les générateurs produisent une structure standardisée plutôt qu'un simple texte.

Le frontend choisit ensuite automatiquement le bon composant d'affichage.

---

# Objectifs

Un exercice doit pouvoir être :

- interactif
- auto-corrigé
- responsive
- imprimable (version papier)
- réutilisable dans plusieurs UAA
- indépendant du cours concerné

Le générateur ne produit jamais du HTML.

Il produit uniquement des données.

---

# Architecture

```
Générateur Python
        ↓
JSON
        ↓
Renderer Frontend
        ↓
Interface interactive
```

Le frontend choisit automatiquement le composant adapté.

---

# Types d'exercices

## 1. Numeric

Réponse numérique.

Exemple :

```
Calcule :

5 × 8
```

Affichage :

```
[__________]
```

Validation :

égalité numérique.

---

## 2. Text

Réponse textuelle.

Exemple :

```
Comment appelle-t-on...
```

Validation :

comparaison texte.

---

## 3. Multiple Choice

QCM.

Affichage :

○

○

○

○

Correction immédiate.

Explication obligatoire.

---

## 4. True / False

Deux boutons :

Vrai

Faux

Explication obligatoire.

---

## 5. Value Table

Le générateur fournit :

- les colonnes
- les lignes
- les cellules à compléter

Exemple :

```
        x
-------------------
-3 | [ ]
 5 | [ ]
12 | [ ]
```

Le frontend dessine automatiquement le tableau.

Chaque cellule est vérifiée individuellement.

Correction cellule par cellule.

---

## 6. Equation

Affichage spécialisé.

Support futur :

- fractions
- exposants
- racines
- π
- √
- clavier mathématique

---

## 7. Matching

Relier deux colonnes.

Exemple :

Cube

↓

Polyèdre

---

## 8. Drag & Drop

Déplacer des éléments.

Exemple :

placer les sommets

placer les faces

etc.

---

## 9. Geometry

Affichage d'une figure.

Le générateur fournit :

- l'image
- les zones interactives
- les réponses

---

## 10. Graph

Graphique interactif.

Peut être :

- lecture graphique

- placer un point

- tracer une droite

- lire une pente

etc.

---

# Structure JSON

Tous les exercices suivent la même structure.

```
{
    "type": "...",

    "question": "...",

    "data": { },

    "answer": { },

    "hint": "...",

    "explanation": "...",

    "difficulty": 1,

    "seed": 12345
}
```

Le champ "data" dépend du type d'exercice.

---

# Exemple Value Table

```
{
  "type": "value_table",

  "question": "Complète le tableau.",

  "data":
  {
      "columns":[-3,-5,-10],

      "rows":
      [
          {
              "label":"f(x)",
              "editable":[true,true,true]
          }
      ]
  },

  "answer":
  {
      "cells":[2,2,2]
  }
}
```

Le frontend dessine entièrement le tableau.

---

# Clavier mathématique

Les exercices numériques doivent pouvoir afficher un clavier virtuel.

Minimum :

- π

- √

- ∞

- ≤

- ≥

- ≠

- ±

- fraction

- puissance

Ce clavier sera utilisé progressivement par les futures UAA.

---

# Correction

Une correction ne se limite jamais à :

"Correct"

ou

"Incorrect"

Elle contient toujours :

- la bonne réponse

- les étapes

- une explication

- éventuellement un rappel du cours

---

# Responsive

Tous les composants doivent fonctionner :

- PC
- tablette
- smartphone

Les tableaux deviennent scrollables horizontalement.

Les zones de saisie restent utilisables au doigt.

---

# Impression

Chaque exercice possède deux modes :

Mode interactif

- champs éditables

- boutons

- quiz

Mode impression

- zones vides

- aucune correction

- aucune interaction

Le navigateur choisit automatiquement le mode impression via CSS.

---

# Règle fondamentale

Le générateur ne produit jamais :

- du HTML

- du CSS

- du JavaScript

Il produit uniquement des données.

Le rendu appartient exclusivement au frontend.

Cette séparation permet :

- d'améliorer le design sans modifier les générateurs ;

- de créer facilement de nouveaux types d'exercices ;

- de conserver une interface cohérente dans tout Jury Central.