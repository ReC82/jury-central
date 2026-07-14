# Jury Central - UI Guidelines

Ce document définit les règles d'interface utilisateur de Jury Central.

Toutes les pages du site doivent respecter ces conventions.

L'objectif est d'offrir une expérience d'apprentissage moderne, agréable et cohérente.

Ces règles s'appliquent à toutes les matières.

---

# Philosophie

Jury Central est une plateforme d'apprentissage.

Le but n'est pas uniquement d'afficher un cours.

Le but est d'aider l'étudiant à apprendre.

L'interface doit donc être :

- simple ;
- claire ;
- moderne ;
- aérée ;
- interactive ;
- agréable à utiliser.

---

# Principes

Toujours privilégier :

- une lecture confortable ;
- des contenus découpés ;
- des interactions fréquentes ;
- peu de texte affiché simultanément.

Éviter les "murs de texte".

---

# Largeur des pages

Le contenu ne doit jamais occuper toute la largeur de l'écran.

Utiliser un conteneur centré.

Les lignes trop longues rendent la lecture difficile.

---

# Espacement

Chaque section importante doit être clairement séparée.

Toujours prévoir :

- marges généreuses ;
- espaces entre les cartes ;
- respiration visuelle.

---

# Les cartes

Une carte constitue le composant principal de Jury Central.

Chaque notion importante doit être présentée dans une carte.

Exemples :

- théorie ;
- exemple ;
- exercice ;
- quiz ;
- fiche mémo ;
- définition ;
- attention ;
- méthode.

---

# Types de cartes

## Information

Fond neutre.

Utilisée pour :

- définition ;
- rappel ;
- vocabulaire.

---

## Exemple

Présente un exemple entièrement résolu.

Toujours afficher :

- l'énoncé ;
- la résolution ;
- la réponse finale.

---

## Attention

Couleur différente.

Utilisée pour :

- erreurs fréquentes ;
- pièges ;
- points importants.

---

## Méthode

Explique une procédure étape par étape.

---

## Fiche mémo

Toujours très compacte.

Uniquement les éléments essentiels.

---

# Une leçon

Une leçon suit toujours cette organisation :

Présentation

↓

Théorie

↓

Exemples

↓

Exercice guidé

↓

Exercices

↓

Quiz

↓

Résumé

---

# Théorie

Ne jamais afficher une très longue page.

Découper naturellement le contenu.

Une notion importante = une carte.

---

# Tableaux

Tous les tableaux doivent être :

- responsives ;
- lisibles ;
- correctement alignés.

Les colonnes doivent toujours être cohérentes.

Les tableaux larges doivent défiler horizontalement.

---

# Exercices

Un exercice doit être interactif.

Ne jamais afficher immédiatement la correction.

Toujours proposer :

- un champ de réponse ;
- un bouton Vérifier.

Après validation :

si correct :

✅ Correct

si incorrect :

❌ Incorrect

Afficher ensuite :

- une explication ;
- éventuellement un indice ;
- la correction uniquement sur demande.

---

# Exercices à compléter

Lorsqu'un exercice demande de compléter :

- un tableau ;
- une phrase ;
- une formule ;

des champs de saisie doivent être présents.

Le texte ne doit jamais être affiché comme une simple correction.

---

# Quiz

Les quiz doivent fonctionner comme un parcours.

Une seule question visible à la fois.

Toujours afficher :

- numéro de la question ;
- progression ;
- score.

Après chaque réponse :

- expliquer pourquoi la réponse est correcte ou incorrecte ;
- rappeler la notion du cours.

Ne jamais se limiter à :

Correct

ou

Incorrect

---

# Illustrations

Une illustration vaut souvent mieux qu'un long texte.

Lorsque cela apporte une valeur pédagogique, utiliser :

- SVG ;
- Canvas ;
- Plotly.

Les illustrations doivent être légères.

---

# Formules

Les formules doivent utiliser MathJax.

Toujours centrées.

Toujours bien espacées.

---

# Code couleur

Utiliser une palette simple.

Éviter les couleurs agressives.

Les couleurs doivent toujours avoir une signification.

Exemple :

- bleu → information
- vert → réussite
- orange → méthode
- rouge → erreur
- gris → information secondaire

---

# Icônes

Les icônes facilitent la lecture.

Exemples :

📘 Théorie

💡 Astuce

⚠️ Attention

📝 Exercice

🎯 Quiz

📌 À retenir

---

# Progression

L'étudiant doit toujours savoir où il en est.

Afficher :

- progression de la leçon ;
- progression de l'UAA ;
- progression du quiz.

---

# Mini-tests

Les mini-tests doivent ressembler à un examen.

Une question à la fois.

Navigation :

Précédent

Suivant

Terminer

---

# Responsive

Le site doit être utilisable sur :

- ordinateur ;
- tablette ;
- smartphone.

Aucun débordement horizontal.

---

# Accessibilité

Toujours prévoir :

- contraste suffisant ;
- tailles de police lisibles ;
- boutons suffisamment grands ;
- navigation clavier.

---

# Performance

Éviter les bibliothèques lourdes.

Privilégier :

- HTML
- CSS
- JavaScript natif

Bootstrap est utilisé pour la mise en page.

---

# Objectif final

Chaque nouvelle UAA doit donner l'impression d'avoir été conçue spécialement pour Jury Central.

Le lecteur ne doit jamais avoir l'impression qu'un document HTML a simplement été importé.

Le contenu officiel doit être transformé en une véritable expérience d'apprentissage.