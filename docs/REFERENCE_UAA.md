# Jury Central - UAA de référence

Ce document décrit l'UAA de référence utilisée comme modèle pour toutes les futures intégrations.

L'UAA de référence est actuellement :

**MB32 UAA1 — Fonction constante**

Cette référence restera valable jusqu'à ce qu'une autre UAA soit officiellement désignée comme nouvelle référence.

Ce document décrit le résultat attendu dans Jury Central, indépendamment de son implémentation technique.

Toute nouvelle UAA doit respecter les conventions décrites ci-dessous.

---

# Objectif

Cette UAA sert de modèle pour toutes les futures intégrations.

Elle définit :

- la structure générale d'une UAA ;
- l'organisation des leçons ;
- les types de contenus ;
- l'expérience utilisateur ;
- les conventions de présentation.

---

# Structure générale

Une UAA est organisée selon la structure suivante :

```
Plan de l'UAA

↓

Leçon 1

↓

Leçon 2

↓

Leçon 3

↓

...
```

Chaque leçon est indépendante.

---

# Structure d'une leçon

Une leçon suit autant que possible l'organisation suivante :

1. Présentation
2. Théorie
3. Exemples résolus
4. Exercice guidé
5. Exercices générés
6. Quiz
7. Fiche mémo

Cette structure constitue la référence du projet.

---

# UAA de référence

**Module**

MB32

**UAA**

UAA1

**Titre**

Tableaux, graphiques, formules

**Leçon de référence**

Fonction constante

**Compétence principale**

Traiter un problème en utilisant un tableau, un graphique ou une formule.

---

# Ce qui ne doit pas changer

Une nouvelle UAA doit conserver :

- la même navigation ;
- la même organisation générale ;
- le même style graphique ;
- les mêmes conventions de présentation ;
- le même niveau de qualité.

---

# Éléments facultatifs

Selon le contenu officiel de l'UAA, certains éléments peuvent être absents.

Exemples :

- graphique interactif ;
- exercice généré ;
- fiche mémo spécifique ;
- illustration SVG.

Ces éléments ne doivent être ajoutés que lorsqu'ils apportent une réelle valeur pédagogique.

---

# Critères de conformité

Une nouvelle UAA est considérée comme conforme lorsqu'elle respecte les critères suivants.

## Structure

- présence d'un plan de l'UAA ;
- organisation en leçons ;
- découpage cohérent du contenu.

## Théorie

- fidèle au cours officiel ;
- complète ;
- non résumée ;
- non reformulée inutilement.

## Exercices

- exercices guidés présents lorsque le cours en contient ;
- exercices générés lorsque cela est pertinent.

## Quiz

- intégrés naturellement à la leçon ;
- regroupés lorsqu'ils forment un parcours logique.

## Navigation

- accessible depuis les menus ;
- liens fonctionnels ;
- progression disponible.

## Présentation

- cohérente avec les autres UAA ;
- homogène visuellement ;
- compatible avec le reste du site.

---

# Objectif final

À terme, toute nouvelle UAA devra pouvoir être intégrée automatiquement à partir des fichiers présents dans :

```
docs/sources_cours/
```

sans intervention manuelle sur la structure du site.

Le résultat obtenu devra être équivalent, en qualité et en organisation, à cette UAA de référence.