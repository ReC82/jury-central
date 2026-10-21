# Ticket #46 — Admin V1 — banque de questions, génération, signalements et usage IA

- Ticket : https://github.com/ReC82/jury-central/issues/46
- **État réel : Installé — à tester**
- Branche : `feature/46-admin-banque` — PR : #144 (fusionnée dans `develop`)
- **SHA installé** : `1b6757ad0b29837f2dbc40d3d4772cec3915fc73` (merge de la PR #144, installé le 2026-10-21)
- Documentation fonctionnelle : `docs/admin.md`, § « Banque de questions V1 »

## 1. Résultat

Nouvelle administration de la banque de questions, accessible depuis le tableau de bord
admin (bouton « Banque de questions »). Aucune suppression physique n'est possible :
une question retirée change de statut, et seules les questions **actives** sont
proposées aux élèves (règle déjà en place dans la sélection).

### Par module — https://jury-central.lodylands.com/admin/bank

Pour chaque module (AMPCR, FRANCAIS, FSE…) :
- questions par statut (active, archivée, signalée, invalide, obsolète, à revoir),
  questions signalées, questions **à contrôler** ;
- rating empirique min / médian / max (#45) ;
- tentatives et réussite moyenne ;
- génération IA **ACTIVE / PAUSED**, avec bouton pour basculer ;
- questions générées par IA / importées, réutilisées (servies dans ≥ 2 sessions),
  passages en session ;
- usage IA du mois et total : appels, questions générées, questions corrigées, jetons
  entrée/sortie, **coût estimé**.

### Questions — https://jury-central.lodylands.com/admin/bank/questions

- Recherche (texte de l'énoncé ou numéro) et filtres module / mini-cours / type / statut /
  rating min-max / « à contrôler » ; pagination par 50.
- Détail d'une question : métadonnées, énoncé, **toutes les versions** (JSON + nombre de
  passages par version), **modifier → nouvelle version** (le JSON est vérifié par le
  registre des types ; les sessions passées gardent leur version), **statut**
  (activer/réactiver, archiver, signalée, invalide, obsolète, à revoir),
  **régénérer une variante** (IA), signalements à marquer traités/rouvrir.

### Signalements élèves

- Sur la page de résultats d'une session, chaque question a un lien « Signaler un problème
  sur cette question » : trop facile, trop difficile, ambiguë, question ou correction
  incorrecte, image incorrecte, réponse contestable, autre + commentaire facultatif.
- Liste admin : https://jury-central.lodylands.com/admin/bank/feedback (à traiter / tous).

### Génération en pause

En PAUSED, les sessions du module se composent uniquement depuis la banque (questions
déjà vues en dernier recours, comme lors d'une panne IA) ; la correction IA n'est pas
concernée.

### Usage IA

Chaque génération de session, correction (worker et synchrone), comparaison de sévérité
et variante admin est comptée (nouvelle table `v1_ai_usage_events`, par module) et
l'agrégat mensuel par utilisateur `v1_ai_usage` (déjà prévu depuis #38, jamais alimenté)
est mis à jour. Les jetons sont lus dans la réponse de l'API OpenAI (`usage`). Comptage à
partir de cette installation (aucune reprise de l'historique).

### Fichiers

- Nouveaux : `app/v1/bank_admin.py`, `app/v1/routes_admin_bank.py`, `app/v1/feedback.py`,
  `app/v1/ai_usage.py`, `app/v1/generation_control.py`, templates `admin_bank*.html`,
  `_admin_bank_nav.html`, `tests/test_ticket46_admin_bank.py` (15 tests).
- Modifiés : `app/v1/models.py` (table `v1_ai_usage_events`, colonne
  `v1_question_feedback.resolved_at`), `app/database.py` (ajout additif de la colonne),
  `app/ai/openai_provider.py` (lecture des jetons consommés), `app/config.py` (tarifs
  d'estimation), `app/v1/session_service.py` (pause + comptage), `app/v1/routes_sessions.py`
  (route de signalement, comptage comparaison de sévérité), `app/main.py` (routeur),
  `app/templates/v1_session_results.html`, `app/templates/admin_dashboard.html`,
  `docs/admin.md`, `docs/current_state.md`, `docs/architecture_v1_data_model.md`.

## 2. Comment tester

1. Se connecter à l'admin : https://jury-central.lodylands.com/admin/login, puis
   « Banque de questions ».
2. https://jury-central.lodylands.com/admin/bank : vérifier les chiffres par module.
3. « Questions » : filtrer (ex. module AMPCR, type `classification`), ouvrir une question.
4. Sur une question : modifier un mot de l'énoncé dans le JSON → « Enregistrer une nouvelle
   version » → la version v2 apparaît « (courante) ».
5. Archiver puis réactiver une question.
6. Sur une question AMPCR (mini-cours MC01…MC37) : « Générer une variante » → nouvelle
   question au statut « À revoir » (lien affiché) ; l'activer si elle convient.
7. Côté élève : terminer un entraînement, ouvrir le résultat, « Signaler un problème sur
   cette question » → message de confirmation ; côté admin, le signalement apparaît dans
   « Signalements » et la question dans « À contrôler ».
8. Mettre la génération d'un module en pause, lancer un entraînement : il se compose sans
   appel IA. Remettre ACTIVE ensuite.

## 3. Vérifications

- `tests/test_ticket46_admin_bank.py` : 15 tests verts (statistiques, filtres,
  versionnement et ancienne session intacte, refus JSON invalide/identique/non conforme,
  archivage exclu de la sélection, pause = aucun appel IA, comptage jetons OpenAI,
  événement + agrégat mensuel, comptage par le worker de correction, signalement HTTP avec
  CSRF/sans doublon/sans changement de statut, refus session en cours ou d'un autre élève,
  pages admin protégées, parcours admin complet, variante IA « à revoir » + refus en pause,
  refus FSE).
- Suite complète : 1765 passed (une exécution, 12 min 27).
- `ruff check` sur les fichiers modifiés/créés : aucune nouvelle erreur (les 4 erreurs B008
  de `app/main.py` sont préexistantes sur `develop`).
- Installation : sauvegarde de la base faite avant ; avance rapide `0e76515` → `1b6757a` ;
  colonne `resolved_at` et table `v1_ai_usage_events` créées au démarrage (ajout additif) ;
  services `jury-central` et `jury-central-correction-worker` actifs ; `/health` local et
  public OK ; `/admin/bank*` en 303 vers `/admin/login` sans connexion (normal) ; aucune
  erreur dans les journaux ; compteurs utilisateurs/sessions/réponses identiques
  avant/après (18 / 69 / 566). Les pages admin ont aussi été rendues (HTTP 200) sur une
  **copie temporaire** de la base réelle, supprimée ensuite : 621 questions listées,
  ex. AMPCR = 259 actives, 247 générées par IA, 12 importées, 114 réutilisées,
  584 passages en session.
- Non vérifié : rendu visuel dans un navigateur réel ; une variante générée par la vraie IA
  (testée uniquement avec le fournisseur factice).

## 4. Choix techniques faits seul

- **Admin = compte admin existant** (`/admin/login`, `require_admin`), pas les rôles V1 :
  cohérent avec tout `/admin/*`.
- **Modification = JSON de la version courante** : 26 types de questions aux contenus
  différents ; un formulaire par type serait disproportionné. Le JSON est validé par le
  registre #40 avant création de la nouvelle version ; le type ne change pas.
- **Signalement ≠ changement de statut** : un élève ne peut pas retirer une question ; la
  question passe dans « À contrôler », l'admin décide. Un même élève qui renvoie le même
  type de signalement pour la même question de la même session met à jour son commentaire
  (pas de doublon). Signalement possible seulement après soumission (page de résultats).
- **Signalements traités** : nouvelle colonne `resolved_at` (ajout additif, jamais de
  suppression).
- **Variante = nouvelle question au statut « À revoir »**, jamais servie avant activation ;
  mêmes validations que la génération normale (structure, domaine, qualité, anti-doublon).
  Refusée pour FSE (banque rédigée à la main, principe #96), MC38 (contexte méta, #58),
  questions liées à un document source, types non générables, et génération en pause.
- **« Réutilisées »** = questions servies dans au moins 2 sessions distinctes.
- **Usage IA par module** : nouvelle table d'événements (l'agrégat `v1_ai_usage` existant
  n'a pas de module). Coût **estimé** avec des tarifs configurables
  (`AI_COST_INPUT_PER_MILLION`, `AI_COST_OUTPUT_PER_MILLION`, défauts 1,25 / 10 USD par
  million de jetons) — valeurs indicatives, à ajuster au tarif réel du modèle utilisé.
- **Pause** : sans configuration, un module reste ACTIVE (comportement inchangé).
- Un échec d'enregistrement de l'usage IA n'interrompt jamais une session ou une
  correction (savepoint, erreur journalisée).
- CSRF vérifié sur toutes les nouvelles actions (élève et admin).

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

(Information : si le tarif réel du modèle IA diffère de 1,25 / 10 USD par million de
jetons, il suffit d'ajouter `AI_COST_INPUT_PER_MILLION` / `AI_COST_OUTPUT_PER_MILLION` au
`.env` ; aucune modification de code.)

## 6. Reste à faire / suites proposées

- Rien d'obligatoire pour ce ticket.
- Suites possibles (non implémentées, hors périmètre) : formulaire d'édition guidé par
  type de question ; signalement aussi pendant la session ; export CSV des statistiques.
