# Jury Central - Workflow d'import des cours

Ce document décrit la procédure officielle d'intégration d'une nouvelle UAA dans Jury Central.

Ce workflow doit être suivi à chaque import de contenu.

---

# Objectif

L'intégration d'une nouvelle UAA doit être la plus automatisée possible.

L'objectif est que l'utilisateur puisse simplement déposer les sources officielles dans :

```
docs/sources_cours/
```

puis demander :

> Importe MB32 UAA2.

sans autre intervention.

---

# Source des données

Toutes les sources sont stockées dans :

```
docs/sources_cours/
```

Chaque UAA contient obligatoirement :

```
cours.html
cours.pdf
metadata.yaml
```

Le fichier `cours.html` est toujours la source principale.

Le fichier `cours.pdf` est uniquement utilisé pour vérifier que le contenu est complet.

Les fichiers présents dans `docs/sources_cours` sont considérés comme immuables.

Ils ne doivent jamais être modifiés.

---

# Procédure d'import

## 1. Lire les sources

Lire :

- metadata.yaml
- cours.html
- cours.pdf

Déterminer automatiquement :

- niveau
- orientation
- matière
- module
- UAA
- titre

Ne jamais demander ces informations si elles peuvent être déduites.

---

## 2. Vérifier l'existence

Vérifier que :

- la matière existe ;
- le module existe ;
- l'UAA existe.

Créer uniquement les éléments manquants.

Ne jamais créer de doublons.

---

## 3. Intégrer le contenu

Transformer le contenu du fichier HTML afin de l'intégrer dans Jury Central.

Le contenu doit conserver :

- les titres ;
- les paragraphes ;
- les listes ;
- les tableaux ;
- les illustrations ;
- les formules ;
- les exercices ;
- les quiz ;
- les fiches mémo.

Ne jamais résumer.

Ne jamais reformuler.

Ne jamais supprimer une partie du contenu.

---

## 4. Respecter les conventions du projet

Réutiliser systématiquement :

- les modèles existants ;
- les vues existantes ;
- les templates existants ;
- les composants existants.

Ne jamais créer une nouvelle architecture.

---

## 5. Vérifications

Avant de terminer :

- vérifier que toutes les pages s'affichent ;
- vérifier les routes ;
- vérifier les menus ;
- vérifier les liens ;
- vérifier les imports ;
- vérifier les éventuelles erreurs.

Corriger automatiquement les erreurs rencontrées.

---

## 6. Documentation

Si l'import modifie le fonctionnement général du projet :

- mettre à jour la documentation concernée.

Ne jamais créer un nouveau document si un document existant doit simplement être mis à jour.

---

## 7. Git

À la fin :

- rester sur la branche courante ;
- faire un commit propre.

Ne jamais effectuer de push sans demande explicite.

---

# Travail autonome

Claude doit travailler de manière autonome.

Avant de poser une question :

1. lire la documentation ;
2. analyser le code ;
3. rechercher une convention existante ;
4. regarder comment une autre UAA est intégrée.

Si la réponse peut être déduite du projet, aucune question ne doit être posée.

---

# UAA de référence

L'UAA de référence est :

```
MB32 UAA1
```

Toute nouvelle UAA doit respecter les mêmes conventions de structure, de navigation et de présentation.

---

# Critères de réussite

Une UAA est considérée comme correctement intégrée lorsque :

- elle est accessible depuis la navigation ;
- tous les liens fonctionnent ;
- le contenu est complet ;
- aucun élément officiel n'a été perdu ;
- les exercices et quiz sont présents ;
- le projet fonctionne sans erreur ;
- un commit a été réalisé.

Le travail est terminé uniquement lorsque tous ces critères sont remplis.

# Règle importante

L'import d'une UAA est une opération de contenu.

Elle ne doit modifier l'architecture du projet que si cela est strictement indispensable.

En cas de besoin d'une évolution de l'architecture, terminer d'abord l'import avec les composants existants, puis proposer l'amélioration séparément.