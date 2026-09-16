# Jury Central - Règles du projet

Ce document contient les règles permanentes du projet.

Ces règles doivent toujours être respectées, quel que soit le travail demandé.

---

# 1. Philosophie du projet

Jury Central est une plateforme de préparation aux examens des Jurys de la Fédération Wallonie-Bruxelles.

L'objectif principal est de produire une plateforme :

- simple ;
- maintenable ;
- évolutive ;
- cohérente ;
- facilement automatisable.

Toute décision technique doit respecter cette philosophie.

Public cible : des étudiants qui préparent un jury et reprennent leurs études, parfois
depuis longtemps. Le niveau pédagogique part de zéro et les explications doivent rester
accessibles à une personne qui n'a pas suivi les cours récemment.

---

# 2. Architecture

L'architecture existante est la référence.

Tu ne modifies jamais l'architecture sans validation explicite.

Tu ne crées jamais une nouvelle façon de faire si une solution existe déjà dans le projet.

Toujours réutiliser :

- modèles
- vues
- templates
- composants
- services
- helpers
- conventions

---

# 3. Conventions de développement

Avant toute modification :

- lire la documentation du dossier `docs/`
- analyser le code existant
- comprendre le fonctionnement actuel

Toujours privilégier la cohérence avec le projet plutôt qu'une nouvelle implémentation.

---

# 4. Import des cours

Les cours officiels sont stockés dans :

docs/sources_cours/

Chaque UAA contient :

- cours.html
- cours.pdf
- metadata.yaml

Le HTML est toujours la source principale.

Le PDF est uniquement utilisé pour vérifier que le contenu est complet.

Les fichiers sources ne doivent jamais être modifiés.

Ils sont considérés comme des documents de référence.

---

# 5. Contenu pédagogique

Le contenu officiel ne doit jamais être réécrit.

Ne jamais :

- résumer
- simplifier
- supprimer une partie
- reformuler

Le rôle de Jury Central est d'intégrer le contenu, pas de le réécrire.

Les améliorations pédagogiques viendront plus tard.

---

# 6. Pilotage et travail autonome

Mode de travail du projet :

- **ChatGPT** est chef de projet : il gère le backlog, les priorités et les critères
  d'acceptation.
- **Claude Code** réalise le développement, sur AWS via tmux.
- **GitHub** (issues) est la source de vérité pour les tâches et leur historique.

Toute nouvelle tâche de développement doit être rattachée à un ticket GitHub. Claude Code
lit intégralement le ticket avant toute modification, reste strictement dans son périmètre
et n'élargit jamais ce périmètre sans validation explicite — une amélioration identifiée
en cours de route est signalée, pas implémentée (voir § 11).

Dans le périmètre d'un ticket, lorsqu'une information est manquante :

- analyser le projet ;
- rechercher les conventions existantes ;
- déduire les informations manquantes.

Ne poser une question que lorsqu'une information est réellement impossible à déduire ou
qu'elle relève d'une décision produit (voir § 11). Par défaut, travailler de manière
autonome jusqu'au commit et au push (voir § 8).

---

# 7. Qualité

Avant de terminer une tâche :

- vérifier que le projet compile
- vérifier les erreurs éventuelles
- vérifier les routes
- vérifier les liens
- vérifier les menus
- vérifier les imports
- vérifier les migrations si nécessaire
- exécuter la suite de tests automatiques (`pytest`) et vérifier qu'elle reste au vert
- fournir une procédure de test manuel lorsque le changement affecte un comportement
  visible (page, formulaire, route) et n'est pas déjà entièrement couvert par les tests
  automatiques

Corriger automatiquement les problèmes rencontrés. Une tâche n'est pas terminée tant que
ces vérifications ne sont pas faites.

---

# 8. Git

- `main` est la branche stable : aucun développement direct dessus.
- `develop` est la branche d'intégration.
- Chaque ticket est développé dans une branche dédiée créée depuis `develop`, nommée
  `feature/<numero-ticket>-<slug>` (nouvelle fonctionnalité) ou `fix/<numero-ticket>-<slug>`
  (correction), jamais directement sur `develop` ou `main`.
- Ne jamais créer de branche hors de ce cadre (un ticket = une branche) sauf demande
  explicite.
- Une fois les tests exécutés et la documentation mise à jour, Claude Code commit et push
  la branche du ticket sur `origin`.
- **Aucun merge vers `develop` ou `main` sans validation explicite.**
- **Aucun déploiement sans demande explicite.**
- Convention de commit : `type: description`, avec les types `feat`, `fix`, `docs`,
  `refactor`, `style`, `test`, `chore`.

---

# 9. Documentation

Toute modification importante du projet doit être répercutée dans la documentation.

Mettre à jour les fichiers concernés plutôt que créer une nouvelle documentation.

Éviter les doublons.

---

# 10. Administration

L'administration sert uniquement à :

- gérer les contenus
- gérer les utilisateurs
- effectuer des corrections ponctuelles

Elle n'est pas destinée à créer intégralement les cours.

Les cours sont générés automatiquement à partir des sources officielles.

---

# 11. Évolutions

Lorsqu'une amélioration est identifiée :

- terminer d'abord le travail demandé
- proposer ensuite l'amélioration

Ne jamais modifier le fonctionnement général du projet sans validation.

En cas de contradiction rencontrée dans le code ou la documentation qui nécessite une
décision produit (choix de dépendance, orientation technique, périmètre fonctionnel), la
signaler explicitement plutôt que d'inventer une règle ou de trancher silencieusement.

---

# 12. Priorités

En cas de conflit entre plusieurs choix :

1. Respecter les conventions existantes.
2. Préserver la compatibilité avec le contenu déjà intégré.
3. Éviter les duplications.
4. Favoriser la simplicité.
5. Limiter les modifications au strict nécessaire.

---

# 13. Objectif

L'objectif est de pouvoir intégrer de nouvelles UAA avec un minimum d'intervention humaine.

Le workflow idéal est :

1. déposer les sources officielles dans `docs/sources_cours/`
2. demander l'import d'une UAA
3. vérifier le résultat
4. publier le contenu

Tout développement doit tendre vers cet objectif.

---

# 14. Sécurité

- Aucun secret dans Git (identifiants, clés — toujours via `.env`, jamais commités).
- Validation des entrées et des réponses toujours effectuée côté serveur.
- Aucun `eval()`, ni équivalent, à quelque niveau que ce soit.
- Protection contre le CSRF sur les formulaires d'administration.

---

# 15. Interface et expérience utilisateur

Toujours privilégier :

- peu de clics ;
- une navigation simple ;
- une interface claire et responsive ;
- la lisibilité et l'accessibilité.

L'étudiant doit toujours savoir où il est, ce qu'il lui reste à faire, et comment
continuer.

---

# 16. Ce qu'il ne faut jamais faire

- Créer un deuxième système alors qu'une solution existe déjà (voir § 2).
- Créer des routes ou des modèles dupliqués.
- Créer une banque d'exercices fixe lorsqu'un générateur est possible.
- Réécrire entièrement une fonctionnalité existante plutôt que l'étendre.
- Supprimer une fonctionnalité sans migration ni justification.
- Ajouter une dépendance lourde sans justification.
- Introduire Docker.
- Intégrer de l'IA dans l'application elle-même (Claude sert uniquement au
  développement, jamais à la génération de contenu ou de réponses en production).
- Modifier nginx, Certbot ou la définition active du service systemd sans ticket dédié et
  instruction explicite (voir `docs/deployment_staging.md`).
- Déployer sur staging, ou redémarrer le service en production, sans instruction
  explicite (§ 8) — un push de branche n'implique jamais un déploiement.

---

# 17. Vertical Slice

Le développement se fait tranche par tranche, pas UAA entière par UAA entière.

Une tranche (un chapitre, une fonctionnalité) n'est considérée comme terminée que
lorsqu'elle réunit, selon ce qui est pertinent pour la tâche : contenu, générateur, quiz,
progression, administration, documentation et tests — puis commit et push (§ 8).

La tranche suivante ne démarre qu'une fois la précédente terminée.