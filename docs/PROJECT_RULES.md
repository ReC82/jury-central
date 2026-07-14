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

# 6. Travail autonome

Lorsqu'une tâche est demandée :

- analyser le projet
- rechercher les conventions existantes
- déduire les informations manquantes

Ne poser une question que lorsqu'une information est réellement impossible à déduire.

Par défaut, travailler de manière autonome.

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

Corriger automatiquement les problèmes rencontrés.

---

# 8. Git

Toujours travailler sur la branche actuelle.

Ne jamais créer une nouvelle branche sauf demande explicite.

À la fin du travail :

- faire un commit propre
- avec un message clair

Ne jamais faire de push sans demande explicite.

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