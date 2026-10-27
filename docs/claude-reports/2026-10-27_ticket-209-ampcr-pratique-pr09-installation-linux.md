# Ticket #209 — [AMPCR pratique PR09] Installation complète de Linux — préparation et dépannage

- Ticket : https://github.com/ReC82/jury-central/issues/209
- **État réel : Installé — à tester**
- SHA installé : `b088a16bda333d8224f4bc5892e22a083aac735f` (fusion de la PR #269 dans `develop`)
- Date : 2026-10-27 (session jcorch autonome)

## 1. Résultat

Le cours **PR09 « Installation complète de Linux — préparation et dépannage »** est publié dans
le parcours **Informatique AMPCR → Pratique écrite** (module `AMPCR-PRATIQUE`, distinct de la
théorie MC : cours, banque, examen et progression séparés ; liens croisés vers MC07, MC08, MC11 et
MC30 seulement). C'est le neuvième cours de l'ordre pédagogique, placé juste après PR08
(position 9). **Numérotation vérifiée** : l'emplacement PR09 du plan installé (`_COURSE_ROWS`,
numérotation définitive de #236) porte bien le sujet du ticket (« PR09, ticket 209, Installation
complète de Linux — préparation et dépannage », exigence AP-10) : aucun écart, aucun autre cours
touché ni renuméroté.

Contenu (19 blocs) :

- **12 chapitres de théorie**, chacun avec objectifs, théorie, **procédure professionnelle à
  rédiger**, **erreur fréquente**, « à l'écrit », repère rapide et renvoi aux exercices liés :
  1. **demande, accord écrit et inventaire** (fiche en 7 rubriques, dont puces Wi-Fi/graphique
     et Windows/BitLocker à garder) ;
  2. **choix de la distribution selon l'usage** (tableau Ubuntu LTS, Linux Mint, Debian, Fedora,
     Pop!_OS : famille, `apt`/`dnf`, chargeur, système de fichiers, durée de support ; tableau
     « usage → choix », convention du cours) ;
  3. **image ISO, contrôle d'intégrité** (`sha256sum -c SHA256SUMS --ignore-missing`, OK /
     FAILED) et **clé USB** (Etcher, Rufus GPT/UEFI, `dd` sur le disque entier identifié par
     `lsblk -d`) ;
  4. **firmware UEFI, démarrage sécurisé** laissé actif (shim, clé **MOK** à enrôler pour un
     pilote compilé) et **session live** pour tester le matériel ;
  5. **sauvegarde et double démarrage avec prudence** (clé BitLocker, démarrage rapide
     désactivé, C: réduite depuis Windows, ESP réutilisée **sans formatage**, jamais « Effacer
     le disque ») ;
  6. **partitions** : ESP `/boot/efi`, racine `/` en **ext4** (≥ 25 Go), `/home` facultative,
     **swap selon le besoin** (tableau de repères), **/etc/fstab et UUID** ;
  7. **l'installateur et le chargeur** GRUB ou systemd-boot, ordre des entrées (`efibootmgr`) ;
  8. **comptes et sudo** (groupe `sudo`/`wheel`, compte standard, pas de session root) ;
  9. **réseau, mises à jour `apt`/`dnf` et pilotes** (`ip a`, `lspci -nnk`, « Pilotes
     additionnels ») ;
  10. **services et tests** (`systemctl status`, `enable --now`, `--failed`) ;
  11. **dépannage par six familles** — exactement les diagnostics du ticket : disque non vu,
      chargeur, fstab/UUID, réseau absent, permissions et sudo, espace disque (symptôme,
      vérification, action, « ne jamais ») ;
  12. **liste de contrôle finale** (10 points, commande et résultat attendu) et **rapport
      d'intervention** (7 rubriques).
- **3 procédures illustrées** : préparer (6 étapes), installer de la clé au bureau (8 étapes),
  finaliser et valider (6 étapes).
- **5 cas résolus** : installation de Linux seul ; double démarrage Windows 11 + Ubuntu ;
  PC qui démarre toujours sous Windows (ordre UEFI) ; mode d'urgence fstab/UUID après un
  remplacement de disque ; Wi-Fi Broadcom sans pilote.
- **Pièges fréquents**, **fiche mémo + glossaire**, **sources et compléments**.
- **17 exercices corrigés** (ticket : ≥ 16) : **3 remises en ordre**, **4 classements**
  auto-corrigés (symptôme → famille, points de montage, double démarrage, avant / pendant /
  après), ISO « FAILED », clé écrite avec `dd`, partitions avant un double démarrage, menu GRUB
  absent (`efibootmgr`), mode d'urgence (fstab/UUID), Wi-Fi sans pilote (`lspci -nnk`),
  « Permission denied » (propriétaire root), racine pleine (`df`/`du`/`journalctl`), rapport à
  rédiger, procédure d'un collègue à corriger. Chacun : contexte complet, documents, consignes,
  barème analytique, corrigé.
- **Mini-examen 10 questions /20** (2 pts chacune, réponses libres) dans « Examen blanc », jamais
  affiché dans le cours (distribution et partitions d'un PC ancien, plan de partitions d'un poste
  de développement, préparation d'un double démarrage chiffré, SSD non vu derrière Intel RST,
  pilote NVIDIA et MOK, réseau filaire NO-CARRIER, sudoers, `/dev/sdb1` dans fstab, liste de
  contrôle, « Effacer le disque » pour un double démarrage).
- **9 schémas SVG** produits depuis des données testées : 3 procédures, deux plans de partitions
  (Linux seul / double démarrage), arbre « Linux ne démarre pas après l'installation », 4
  terminaux **clairement identifiés comme fictifs** (contrôle ISO + choix de la clé, partitions
  avant double démarrage, `efibootmgr`, racine pleine). Alt complet, légende, mention « schéma
  non officiel », responsive. **Aucune image générée ni photographie.**

### Fichiers

- `app/v1/ampcr_pratique_pr09_figures.py` — inventaire, distributions et commandes
  (`DISTRIBUTIONS`, `PACKAGE_COMMANDS`, `USAGE_CHOICES`), `checksum_verdict`, partitions
  (`LINUX_ONLY_LAYOUT`, `DUAL_BOOT_LAYOUT`), `swap_advice`, `dual_boot_action`,
  `first_boot_entry`, tableau `TROUBLESHOOTING` (six familles), arbre de démarrage, 3 procédures,
  liste de contrôle, rubriques du rapport, terminaux fictifs, figures
- `app/v1/ampcr_pratique_pr09_bank.py` — 17 exercices + 10 questions d'examen
- `app/v1/ampcr_pratique_pr09_course.py` — 19 blocs du cours
- `app/v1/ampcr_pratique_bank.py` — déclaration PR09 + contexte de correction IA spécifique
- `app/seed.py` — `_seed_uaa(…, "PR09", …, position 9)` dans le module pratique (additif)
- `tests/test_ticket209_ampcr_pratique_pr09.py` (30 tests) ; comptages adaptés dans
  `tests/test_admin_content_hierarchy.py` et `tests/test_ticket208_ampcr_pratique_pr08.py`
  (nombre de cours publiés)
- `docs/current_state.md`, `docs/ampcr_pratique_v1.md`, `docs/changelog.md`

## 2. Liens pour tester

- Cours : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr09
- S'entraîner (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr09/practice
- Examen blanc /20 (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr09/exam
- Accueil du parcours pratique : https://jury-central.lodylands.com/ampcr-pratique
- Matrice : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte : ouvrir le cours, parcourir les séquences (chapitres 1 → 12, cas résolus,
exercices) ; lancer une session « S'entraîner » (10 exercices tirés des 17, dont des remises en
ordre et des classements auto-corrigés) puis un « Examen blanc » (10 questions, note sur 20) ;
vérifier la correction et le barème après envoi. Dans l'accueil du parcours, PR09 apparaît après
PR08 (« 14 cours publiés sur 30 prévus »).

## 3. Vérifications effectuées

- Tests ciblés `tests/test_ticket209_ampcr_pratique_pr09.py` : **30 passed** — gestionnaires de
  paquets et chargeurs par distribution, verdict `sha256sum` (OK / FAILED / rien vérifié),
  partitions et points de montage, repères du swap (tableau Red Hat), règle du double démarrage
  (ESP réutilisée sans formatage, Windows et données jamais touchés, arrêt sans sauvegarde ET
  accord), ordre des entrées `efibootmgr`, six familles de dépannage couvertes, ordre des 3
  procédures, liste de contrôle et rapport, terminaux (largeur mobile ≤ 56 caractères,
  cohérence), schémas (validité, accessibilité, étapes et partitions = données), remises en ordre
  et classements auto-corrigés, absence de question d'acronyme et d'affirmation fausse, matière
  du ticket présente, 5 cas résolus, examen absent du cours, liens (MC07, MC08, MC11, MC30,
  PR04-PR08, PR11, PR24 ; pas de lien vers PR10/PR12 non publiés), seed idempotent et position
  après PR08, réserves séparées, contexte de correction, pages, sessions entraînement/examen,
  note /20, aucune génération IA.
- Tests liés (PR07, PR08, numérotation #236, hiérarchie admin) : **144 passed** avec PR09.
- **Suite complète** (une exécution, `seed.py` étant partagé) : **2 657 passed** en 21 min, aucun échec.
- `ruff check` sur les fichiers créés et modifiés : **All checks passed**.
- Contrôle visuel (navigateur sans interface, 440 px de large) des 9 schémas ; libellé d'une
  question de l'arbre raccourci après ce contrôle.
- Installation : arbre propre sur `develop`, sauvegarde de la base
  (`~/.local/state/jury-central-orch/backups/jury_central-pre-ticket209-20261027-035035.db`),
  fast-forward `d1fdaff → b088a16`, seed idempotent (1 UAA créée ; les 71 blocs « créés » =
  19 blocs PR09 + le remplacement habituel des 52 blocs FSE pilotés par le code, sans doublon),
  redémarrage des deux services (actifs), `/health` local et public OK, pages du cours, de
  l'accueil, de la matrice et de PR08 en HTTP 200 (entraînement/examen : 303 vers la connexion,
  normal sans session), « 14 cours publiés sur 30 prévus » sur l'accueil, 17 cartes d'exercice et
  9 figures servies, capture mobile (440 px) de la page servie conforme. Compteurs
  utilisateurs/sessions/réponses inchangés (18 / 81 / 638).

Non effectué : validation pédagogique humaine (au propriétaire) ; passage d'une session réelle
avec la vraie correction IA (les tests utilisent `FakeAIProvider`) ; capture pleine page mobile
du cours installé (même composant de page que les cours déjà publiés ; les 9 schémas ont été
contrôlés visuellement à 440 px) ; exécution réelle des commandes sur une machine Linux (les
sorties sont des reconstitutions fictives, abrégées, vérifiées par relecture).

## 4. Choix techniques faits seul

- **Sorties de terminal en anglais** (système réglé en anglais ou `LANG=C`), signalé dans le
  cours : les traductions françaises de `df`, `apt`, `sudo`… varient selon les versions ; montrer
  la sortie anglaise d'origine garantit des messages exacts, et c'est ce que l'on trouve en
  cherchant un message d'erreur.
- **Distribution de référence : Ubuntu / Linux Mint** (famille Debian, `apt`), avec les
  équivalents Fedora (`dnf`, groupe `wheel`) et Pop!_OS (systemd-boot) là où le ticket les
  demande ; libellés d'installateur datés (octobre 2026), « la documentation de la distribution
  fait foi ». Exemple d'image : Ubuntu 24.04.3 LTS (version LTS réelle).
- **ext4 dans tout le cours** (exigence du ticket), avec la nuance que Fedora propose Btrfs par
  défaut.
- **Repère du swap** tiré du tableau de recommandations de la documentation Red Hat, présenté
  comme **repère indicatif** (convention du cours) ; de même pour le tableau « usage →
  distribution », la liste de contrôle et les rubriques du rapport.
- **Règles codées et partagées** par les tableaux, les schémas, les classements et les
  corrigés : `checksum_verdict`, `swap_advice`, `dual_boot_action`, `first_boot_entry`,
  `TROUBLESHOOTING`. Énoncé, cours et corrigé ne peuvent pas diverger.
- **Jamais d'effacement sans autorisation** : chaque cas et chaque corrigé passent par l'accord
  écrit et la sauvegarde vérifiée ; en double démarrage, l'ESP de Windows est réutilisée sans
  formatage ; « Effacer le disque » est traité comme une faute (X10).
- **Pas de contournement** : démarrage sécurisé laissé actif (enrôlement MOK enseigné), pas de
  `chmod -R 777`, pas de session root, pas de pilote ou paquet d'un site inconnu.
- **Recouvrement limité** : choix du système et prérequis renvoyés à PR07, Windows à PR08,
  partitions à PR05, disque à PR06, messages `grub rescue` / mode d'urgence à PR11, réseau à
  PR24 (publiés, liens) ; PR10 (comptes, commandes, permissions détaillées) et PR12
  (restauration) cités **en texte seulement** (non publiés). Exigence AP-10 (plan installé) et
  complément AP-C03 ; statut « partiel » dans la matrice, jamais « validé ».
- Pas de photographie ni d'image générée : les sujets (procédures, partitions, terminaux) sont
  techniques et produits en SVG depuis des données testées, avec les assistants existants
  (`step_flow_svg`, `partition_map_svg`, `decision_tree_svg`, `screen_svg`) ; aucun nouvel
  assistant partagé, aucune nouvelle dépendance ; constructeurs d'items réutilisés depuis PR04,
  type d'item de PR06.

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Éléments restant à réaliser

- Validation pédagogique et visuelle par le propriétaire.
- Suite de l'ordre pédagogique : PR10 « Comptes, pilotes, paramètres et commandes » (#214).
- Améliorations repérées, non implémentées (hors périmètre) : (1) PR07 et PR08 citent PR09 en
  texte seulement ; un lien vers `/uaa/ampcr-pratique-pr09` pourrait y être ajouté (leurs tests
  vérifient aujourd'hui l'absence de ce lien et seraient à adapter) ; (2) dans l'arbre de
  décision partagé (`decision_tree_svg`), l'étiquette « NON » chevauche la flèche sur mobile
  (déjà signalé pour PR02 à PR08, visible aussi sur l'arbre de PR09).
