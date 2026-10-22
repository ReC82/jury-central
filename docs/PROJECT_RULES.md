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

## Comptes rendus permanents de Claude Code

Consigne explicite de l'utilisateur du 1 octobre 2026, applicable à chaque ticket,
review, diagnostic, incident, correction et livraison :

- Rédiger le compte rendu complet dans un fichier Markdown versionné sous
  `docs/claude-reports/`, même si aucun code applicatif n'a été modifié.
- Nommer le fichier `YYYY-MM-DD_ticket-<numero>-<sujet>.md` ; pour un incident sans
  numéro, `YYYY-MM-DD_incident-<sujet>.md`. Réutiliser le rapport du ticket pour ses
  compléments ; conserver la chronologie des incidents et leurs étapes.
- Commit et push du rapport sur la branche de travail autorisée : un fichier seulement
  présent sur le serveur ou un compte rendu uniquement affiché dans tmux ne constitue
  pas une livraison. Respecter § 8 : cela n'autorise aucun merge ou déploiement.
- Fournir dans le message final le lien GitHub direct vers le fichier sur la branche
  poussée, le nom de la branche et le SHA livré. Le message terminal reste bref :
  résultat, blocages éventuels et lien ; ne pas demander à l'utilisateur de copier un
  long compte rendu ou d'envoyer des captures pour la review.
- ChatGPT lit directement ce rapport depuis GitHub pour vérifier la livraison et donner
  la suite.

Le rapport contient, selon la tâche :
1. demande, périmètre, branche et référence des commits concernés ;
2. diagnostic : faits observés, preuves, hypothèses et incertitudes distingués ;
3. changements et actions effectivement effectués, notamment sur les services ou bases ;
4. tests et résultats exacts, en distinguant automatisés, manuels et non réalisés ;
5. état final et limites ; pour un incident, état des services et vérifications HTTP
   locale/publique, ou raison explicite de leur absence ;
6. procédure de vérification et points restant à résoudre.

Ne jamais publier de secrets, de contenu de `.env`, de cookies, de jetons ou de données
personnelles tirées des logs. Expurger les preuves avant de les committer.

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

---

# 18. Prévisualisation avant validation

**Mise à jour du 1 octobre 2026 (même jour, consigne explicite ultérieure et plus
spécifique — prévaut sur la règle générale ci-dessous tant qu'elle n'est pas révoquée)** :
`https://jury-central.lodylands.com` sert la plateforme d'essai personnelle de
l'utilisateur. Pour cette plateforme précise, et uniquement sur instruction explicite au
cas par cas, l'utilisateur peut autoriser l'installation directe du code d'une branche de
ticket (non fusionnée) sur ce site, AVANT la suite de tests complète et avant toute
fusion — ceci déroge explicitement au § 8/§ 16 (aucun déploiement sans demande explicite,
jamais une branche autre que `develop`) pour ce cas précis, jamais par défaut. Ordre à
respecter quand cette autorisation est donnée :

1. Sauvegarder la base réelle (`jury_central.db`, copie `sqlite3 ... ".backup ..."`) et
   relever le commit actuellement en place, pour permettre un retour arrière — préserver
   comptes, sessions, autres matières et configuration IA existante (`.env` jamais modifié).
2. Commit/push des changements sur la branche du ticket, puis installation sur le site par
   le mécanisme déjà utilisé (checkout du commit exact dans `/srv/jury-central`, seed
   idempotent, redémarrage des services existants) — jamais de nouvelle infrastructure
   pour ce besoin.
3. Contrôles rapides uniquement (site accessible, fonctionnalité visible, parcours de
   démarrage, worker opérationnel) — pas la suite de tests complète à ce stade.
4. Lien direct transmis dès que la fonctionnalité est utilisable ; attendre le retour de
   l'utilisateur avant de relancer des tests longs ou de poursuivre.
5. Développement et préparation des changements : toujours dans un `git worktree` séparé
   (jamais directement dans `/srv/jury-central`, dont le `WorkingDirectory` est partagé
   avec le(s) service(s) live — voir `docs/claude-reports/2026-10-01_incident-502.md` § 7).
6. Suite de tests complète, Ruff, et mise à jour des rapports : après la validation
   utilisateur de l'aperçu installé, avant toute intégration définitive (fusion vers
   `develop`).

Cette dérogation est strictement scopée à cette plateforme et vaut pour la demande qui l'a
autorisée — elle ne s'étend pas automatiquement à un autre site ni à un ticket futur sans
nouvelle instruction explicite. **Hors de ce cas précis**, la règle générale ci-dessous
reste la référence par défaut :

Consigne explicite de l'utilisateur du 1 octobre 2026, applicable à tout changement visible
(page, parcours, formulaire) avant la suite de tests complète et la finalisation d'un
ticket :

- Avant d'exécuter la suite de tests complète et de finaliser un ticket qui modifie un
  comportement visible, proposer une prévisualisation fonctionnelle que l'utilisateur peut
  essayer lui-même, dans son navigateur (PC et téléphone) — jamais seulement une adresse
  `localhost` inaccessible depuis l'extérieur.
- Réutiliser une infrastructure de prévisualisation déjà en place si elle existe. Sinon,
  mettre en place un accès isolé, **sans jamais modifier le fonctionnement, la
  configuration nginx/systemd active, ou les données du site public** (voir § 16) :
  code depuis la branche du ticket (de préférence un `git worktree` dédié, voir § 2/§ 17 —
  jamais le répertoire de travail du service live), base de données de démonstration
  séparée (jamais de donnée réelle), serveur et worker applicatifs séparés de ceux du site
  public. Voir `docs/preview_procedure.md` pour la procédure technique détaillée et les
  options concrètes selon les contraintes réseau rencontrées (port dédié vs sous-domaine
  dédié).
- Avant de transmettre le lien, effectuer uniquement les contrôles rapides nécessaires et
  un parcours fonctionnel court (pas la suite de tests complète à ce stade) : l'objectif
  est de confirmer que la prévisualisation fonctionne, pas de refaire la recette complète
  en double.
- Indiquer clairement, pour toute fonctionnalité de correction/génération : si elle utilise
  un fournisseur IA réellement configuré ou un mécanisme simulé — une simulation ne valide
  jamais la qualité pédagogique d'une correction réelle, uniquement le mécanisme, le
  parcours et l'interface.
- Si l'accès externe (port, sous-domaine, certificat) se heurte à une contrainte
  d'infrastructure hors de portée (ex. pare-feu/groupe de sécurité cloud) : ne jamais
  tenter de la contourner ni de modifier une configuration d'infrastructure sensible sans
  autorisation explicite pour CETTE action précise — signaler le blocage, présenter les
  options concrètes de déblocage, et attendre la décision de l'utilisateur (§ 11).
- Attendre la validation visuelle et fonctionnelle explicite de l'utilisateur sur cette
  prévisualisation avant de lancer la suite de tests complète et la finalisation
  (commit/push de clôture, mise à jour des rapports). Les tests complets restent
  obligatoires avant toute fusion/déploiement (§ 7/§ 8) — cette consigne change seulement
  l'ORDRE (aperçu visuel d'abord), jamais l'exigence elle-même.