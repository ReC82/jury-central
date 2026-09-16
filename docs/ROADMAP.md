# Jury Central - Roadmap

Ce document décrit les grandes étapes du développement de Jury Central.

Il représente la feuille de route officielle du projet.

Le contenu de ce document doit être mis à jour uniquement lorsqu'une étape est terminée ou qu'une nouvelle étape est décidée.

---

# VS001 - Fondation du projet

## Objectifs

- Structure du projet
- Documentation
- Hiérarchie des contenus
- Administration
- Import automatique des sources

## Statut

✅ Terminé

---

# VS002 - Design System

## Objectifs

Créer une interface utilisateur moderne et réutilisable.

Comprend notamment :

- cartes
- composants UI
- responsive
- amélioration des quiz
- amélioration des exercices
- progression
- rendu homogène

## Statut

🔄 En cours

Livré : cartes réutilisables (Théorie/Exemple/Exercice/Quiz/Attention/Résumé, voir
`docs/UI_GUIDELINES.md` et `docs/components/INDEX.md`), tableaux pédagogiques éditables,
exercices rédigés interactifs, quiz avec explication systématique — appliqué aux pages
UAA (`/uaa/{slug}`).

Restant : les pages de listing (matière, module) affichent encore de simples liens plutôt
que des `CourseCard` (voir `docs/current_state.md`, section « Points ouverts »).

---

# VS003 - Composants d'exercices interactifs

## Objectifs

Remplacer l'affichage texte brut des exercices par une structure de données que le
frontend transforme en composant interactif, plutôt qu'un générateur qui produirait du
HTML.

Générateur Python → JSON → composant frontend → interface interactive.

Voir `docs/EXERCISE_TYPES.md` pour le format complet.

## Statut

🔄 En cours

Livré (VS003, VS003.1) : moteur `InteractiveExercise`, premier composant `value_table`
(tableau de valeurs vérifié cellule par cellule), câblé sur le générateur
`maths.functions.constant_function` ; renderer de contenu riche unique
(`app/content.py` + `app/static/js/rich_content.js`) utilisé par les cours, quiz et
exercices générés.

Restant : sur les 10 types d'exercices décrits dans `docs/EXERCISE_TYPES.md`, seul
`value_table` est implémenté (numeric, text, QCM, vrai/faux, equation, matching,
drag & drop, geometry, graph restent à faire). L'ancien moteur `GeneratedExercise`
(texte + réponse unique, utilisé par `maths.equations.linear_equation`) coexiste encore
sans plan de dépréciation.

Distinct de VS003 : l'automatisation de l'**import** d'une UAA depuis `docs/sources_cours/`
(analyse du HTML source, génération de composants sans intervention manuelle) n'est pas
implémentée — aucun script d'import n'existe à ce jour (voir `docs/current_state.md`).
Les UAA importées (MB32 UAA1, UAA2) l'ont été manuellement. Si ce chantier redémarre, il
doit faire l'objet d'un ticket dédié plutôt que d'être confondu avec VS003.

---

# Priorité produit (depuis le ticket #4, 2026-09-16)

Avant de poursuivre VS004/VS005/VS006 ci-dessous, la priorité produit est désormais :

1. **Informatique — AMPCR**
2. **Français — CESS Professionnel**

Voir [docs/content_plan_informatique_francais.md](content_plan_informatique_francais.md)
pour l'inventaire, la cartographie des deux matières et le découpage en tickets. VS004,
VS005 et VS006 restent valides mais passent derrière ces deux matières.

---

# VS004 - Import complet MB32

## Objectifs

Importer automatiquement toutes les UAA MB32.

Le résultat doit être directement publiable.

## Statut

⏳ À faire (après Informatique AMPCR et Français CESS P, voir ci-dessus)

---

# VS005 - Import complet MQ32

## Objectifs

Importer automatiquement toutes les UAA MQ32.

## Statut

⏳ À faire

---

# VS006 - Import complet MQ34

## Objectifs

Importer automatiquement toutes les UAA MQ34.

## Statut

⏳ À faire

---

# VS007 - Autres matières

## Objectifs

Importer, dans cet ordre de priorité (voir
[docs/content_plan_informatique_francais.md](content_plan_informatique_francais.md)) :

1. Informatique (AMPCR)
2. Français
3. Sciences, Social, Économie, ...

## Statut

⏳ À faire — Informatique et Français en sont au stade planification (ticket #4), aucune
source encore disponible dans le dépôt.

---

# VS008 - Plateforme

## Objectifs

Ajouter :

- comptes étudiants
- statistiques
- progression
- examens
- favoris

## Statut

⏳ À faire

---

# VS009 - Fonctionnalités avancées

## Objectifs

Ajouter notamment :

- IA d'assistance
- recommandations
- nouvelles activités pédagogiques
- amélioration continue des contenus

## Statut

⏳ À faire

---

# Règle

Une étape doit être considérée comme terminée uniquement lorsque :

- le développement est terminé ;
- les tests sont validés ;
- la documentation est à jour ;
- un commit Git a été réalisé.