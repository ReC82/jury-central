# Ticket #48 — Informatique V1 : assets visuels et questions d'identification de composants

- Ticket : #48 — https://github.com/ReC82/jury-central/issues/48
- **État réel : Installé — à tester**
- PR : #146 (fusionnée dans `develop`) — branche `feature/48-assets-visuels`
- **SHA installé : `0d9fb66b625b7cc4a97850ee05310b12a17d9e9d`**

## Résultat

L'informatique dispose maintenant d'une première chaîne de ressources visuelles
réutilisables, et MC01 « Architecture générale d'un PC » propose 10 questions
d'identification de composants à partir d'images.

- **Trois natures de visuels distinguées** : photo réelle, illustration générée, schéma
  technique. Pour chacune : source, licence, auteur et provenance. Ces informations sont
  enregistrées et affichées sous l'image.
- **9 visuels** :
  - 7 photos réelles sous licence libre, issues de Wikimedia Commons : barrette de RAM,
    processeur (face arrière), alimentation, disque dur ouvert, SSD, carte mère, carte
    graphique ;
  - 1 illustration générée par IA (carte graphique, SVG) ;
  - 1 schéma technique de carte mère avec des repères A à F.
- **10 questions** dans la banque MC01 :
  - 8 questions `image_identification` : 7 à choix et 1 à réponse écrite (« carte
    graphique » / « GPU » / « carte vidéo » acceptés) ;
  - 1 question `diagram_labeling` : associer chaque repère A–F du schéma à socket CPU,
    emplacements RAM, emplacements PCIe, connecteurs de stockage, connecteurs E/S ou
    chipset. Les points partiels sont comptés ;
  - 1 question « que désigne le repère B ? ». Elle réutilise **le même** schéma : un
    asset sert à deux versions de question sans être dupliqué.
- Ces questions sont servies en **S'entraîner** et **S'évaluer** MC01, ainsi que dans la
  révision transversale MC38. La correction est locale, sans appel IA. Les images
  apparaissent sur la question et dans les résultats.
- **Mobile** : l'image prend toute la largeur avec une hauteur limitée, et un lien
  « agrandir » l'ouvre dans un nouvel onglet pour zoomer. Capture vérifiée à 390 px.
- **Admin `/admin/bank/assets`** (nouvel onglet « Visuels ») : liste des visuels avec
  aperçu, nature, licence, source, statut et questions qui les utilisent. La fiche d'une
  question affiche aussi ses visuels. Actions disponibles :
  - **marquer incorrect**, avec un motif et une demande de régénération ou de
    remplacement : les questions qui utilisent ce visuel ne sont plus proposées ;
  - **réactiver**.
- **Régénération** d'un visuel IA : commande manuelle sur le serveur
  (`python -m app.v1.assets regenerate`, appel IA réel). Elle crée un nouveau visuel et
  une nouvelle version de chaque question concernée. Elle n'est jamais automatique et
  n'est pas possible pour une photo ou un schéma, qui se remplacent manuellement.
- Modifier une question visuelle dans l'admin (ce qui crée une nouvelle version)
  **conserve son image**.
- Les élèves pouvaient déjà signaler « image incorrecte » depuis les résultats (#46).

Fichiers principaux :
- `app/v1/assets.py` (service des visuels) ;
- `app/v1/ampcr_visual_bank.py` (banque MC01) ;
- `app/static/img/ampcr/` (9 fichiers) ;
- `app/v1/ai_bridge.py` (correction des 2 types) ;
- `app/v1/bank.py` (retrait du tirage des questions dont le visuel est invalide) ;
- `app/v1/session_service.py`, `app/v1/routes_sessions.py`, `app/v1/routes_admin_bank.py`,
  `app/v1/bank_admin.py` ;
- templates `_question_assets.html`, `_admin_asset_card.html`, `admin_bank_assets.html`,
  `v1_session_question.html`, `v1_session_results.html` ;
- documentation `docs/assets_visuels_v1.md`, `docs/admin.md` et `docs/current_state.md`.

## Tester

1. Connecte-toi, puis ouvre https://jury-central.lodylands.com/uaa/ampcr-mc01/practice et
   lance une session. Les questions visuelles sont réparties avec les autres types,
   environ 1 à 3 par session. Il faut plusieurs sessions pour les voir toutes, car les
   questions déjà vues passent en dernier.
2. Vérifie sur téléphone : lisibilité de l'image, lien « agrandir », listes déroulantes
   des repères A–F.
3. Termine la session et vérifie que les images et les réponses données apparaissent dans
   les résultats.
4. Ouvre l'admin https://jury-central.lodylands.com/admin/bank/assets. La liste se remplit
   après la première ouverture de MC01 « S'entraîner » ou « S'évaluer ». Ensuite, marque
   un visuel incorrect, vérifie que ses questions ne sortent plus, puis réactive-le.

Liens :
- https://jury-central.lodylands.com/uaa/ampcr-mc01/practice
- https://jury-central.lodylands.com/uaa/ampcr-mc01/exam
- https://jury-central.lodylands.com/admin/bank/assets
- https://jury-central.lodylands.com/static/img/ampcr/mc01_schema_carte_mere.svg

## Vérifications

- `tests/test_ticket48_visual_assets.py` : 14 tests, tous verts. Ils couvrent :
  - fichiers et licences ;
  - aucune paire de quasi-doublons ;
  - import idempotent, sans asset dupliqué, schéma partagé par 2 versions ;
  - contrat d'assets par type ;
  - parcours HTTP complet : images affichées, réponses, correction 10/10, résultats ;
  - points partiels du schéma ;
  - retrait du tirage puis réactivation ;
  - édition qui garde l'image ;
  - régénération avec un faux fournisseur, refus pour une photo ;
  - pages et actions admin.
- Suite complète (moteur partagé touché) : 1 760 tests passés et 19 échecs au premier
  passage, tous des tests MC01 :
  - un test #55 supposait une banque MC01 sans assez de questions non rédactionnelles. Je
    l'ai adapté en neutralisant l'import visuel, pour garder son intention ;
  - les autres tests attendaient des identifiants d'options numériques. Je les ai alignés
    sur cette convention.
- Les 38 fichiers de tests liés à MC01 ont ensuite été relancés : 827 passés, 0 échec.
  **La suite complète n'a pas été relancée intégralement après ces deux corrections.**
- `ruff check` sur tous les fichiers modifiés : aucune erreur.
- Installation :
  - `/health` local et public OK ;
  - visuels servis (200) ;
  - `/uaa/ampcr-mc01` 200 ;
  - pages protégées en 303 vers la connexion ;
  - compteurs (utilisateurs, sessions, réponses) inchangés, 18/69/566 ;
  - sauvegarde de la base faite avant l'installation.
- Non fait : test réel connecté sur le site, pour ne pas créer de compte. La validation
  visuelle revient au propriétaire.

## Choix techniques faits seul

- **Aucune migration** : la nature du visuel est stockée dans `metadata_json` de la table
  `v1_assets` existante (#38). Format, origine, licence, source et provenance utilisent
  les colonnes existantes.
- **Anti-doublon par empreinte SHA-256 du fichier**, plutôt que par chemin.
- **Illustration « générée »** : je n'ai pas pu appeler le générateur d'images, car cela
  demande la clé du serveur, interdite dans le worktree. L'illustration est donc un SVG
  généré par IA (Claude Code), marqué « généré par IA », avec sa consigne conservée.
  Elle pourra être régénérée en PNG avec la commande de régénération.
- **Photos** :
  - Wikimedia Commons, licences CC0, domaine public, CC BY-SA 3.0 et 4.0 ;
  - auteur et licence affichés sous l'image, comme l'exige CC BY-SA ;
  - miniatures 800 px ré-encodées ;
  - sur le SSD, la mention imprimée du type de composant est floutée car elle donnait la
    réponse. Cette modification est signalée dans la provenance.
- Ces types visuels ne sont **jamais générés par l'IA de questions**, seulement servis
  et corrigés. Une question visuelle exige une image réelle déjà enregistrée.
- **Correction** : `image_identification` est traitée comme un QCM (mode choix) ou une
  réponse courte (mode texte), et `diagram_labeling` comme une classification. L'image
  n'est jamais envoyée au correcteur.
- **`hotspot` (zones cliquables) préparé mais pas branché**. Le ticket le permet (« sans
  l'imposer »). Le schéma à repères lettrés couvre le besoin sans interaction tactile
  complexe.
- **Aucune difficulté déclarée** sur ces questions, comme le reste d'AMPCR. Cela évite
  qu'un choix de difficulté remplisse une session uniquement de questions visuelles.
- `image_identification` accepte désormais aussi le SVG, pour un schéma technique.
- **Import au premier accès MC01**, comme la banque MC01 existante. Le seed n'a pas
  changé.

## Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## Reste à réaliser / suites proposées

- Créer de vraies illustrations raster par le générateur d'images, si souhaité : marquer
  l'illustration incorrecte avec « régénération », puis lancer la commande sur le serveur.
- Étendre la banque visuelle aux autres mini-cours matériel : MC02 connectiques, MC03
  barrettes et sockets, MC04 stockage, MC05 connecteurs d'alimentation, MC15 RJ45.
- Brancher `hotspot` (clic sur l'image) dans un ticket dédié, si besoin.
