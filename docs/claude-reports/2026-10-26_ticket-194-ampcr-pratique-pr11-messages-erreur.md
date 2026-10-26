# Ticket #194 — [P0][AMPCR pratique PR11] Messages d'erreur Windows/Linux — diagnostic et interventions écrites

Ticket : [#194](https://github.com/ReC82/jury-central/issues/194) · branche `feature/194-pr11-messages-erreur` · PR [#241](https://github.com/ReC82/jury-central/pull/241) (cours) et [#242](https://github.com/ReC82/jury-central/pull/242) (correctif d'affichage de l'arbre)

**État réel : Installé — à tester.**

**SHA installé : `26bb9d7`** (merge de la PR #242 sur `develop`, 26/10/2026 ; le cours lui-même est arrivé avec `f534e12`, PR #241).

## Liens pour tester

- Cours : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr11
- S'entraîner (16 exercices, 10 tirés par session, correction après envoi) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr11/practice
- Examen blanc (mini-examen 10 questions, note /20) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr11/exam
- Accueil du parcours (« 2 cours publiés sur 30 prévus ») : https://jury-central.lodylands.com/ampcr-pratique
- Matrice (AP-09 et AP-13 passent « partiel ») : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte : se connecter ; ouvrir le cours sur téléphone puis sur PC, parcourir les
séquences ou « Afficher tout le cours sur une page » ; vérifier l'arbre de décision, le flux
d'intervention, le plan de partitionnement et les 8 captures fictives (mention « Capture
fictive » sous chaque écran) ; ouvrir quelques corrigés (repliés par défaut) ; lancer
« S'entraîner » (une remise en ordre et un classement peuvent sortir), puis « Examen blanc »
(10 questions jamais vues dans le cours, aucune correction pendant la passation, documents
« terminal » en police à chasse fixe) ; envoyer et lire « Soit x / 20 », le corrigé et le
barème. Imprimer le cours (A4) si souhaité. Vérifier que `/modules/ampcr` (théorie MC01–MC38)
et PR06 sont inchangés.

## 1. Réconciliation

- Aucune branche, PR, rapport ni contenu PR11 existant avant cette session (worktree créé
  depuis `origin/develop` = `e6c543e`).
- Dépendances livrées : #192 (socle, matrice, modèles, checklist, PDF officiel) et #236
  (numérotation) installés ; `_COURSE_ROWS` place bien PR11 = « Messages d'erreur
  Windows/Linux — diagnostic et interventions écrites », module P2, exigences AP-09, AP-13,
  AP-15. Modèle d'intégration repris de PR06 (#193, `docs/ampcr_pratique_v1.md` § 2).

## 2. Ce qui a été livré

### Cours (`/uaa/ampcr-pratique-pr11`, 16 blocs)

Toute la matière obligatoire du ticket, dans l'ordre 1 → 6 :

| Bloc | Contenu (points du ticket) |
|---|---|
| Objectifs et place dans l'épreuve | 6 objectifs observables ; AP-09, AP-13, AP-15 (texte exact, page) ; AP-C01 et AP-C03 signalés compléments ; liens théorie MC07, MC08, MC10, MC11, MC12, MC29, MC30, MC31, MC36 et PR06 ; mention « supports fictifs » |
| 1. Méthode universelle | recueil (texte exact, code, contexte, date, déclencheur, modifications, périmètre, criticité, données) ; 10 stades + arbre de décision ; code / cause probable / hypothèse / test / résultat / action ; documentation fiable, jamais de cause unique tirée d'un code ambigu ; ordre sauvegarde → preuves → tests → réversible → invasif autorisé → validation + flux SVG |
| 2. Démarrage (Windows) | 4 messages « no boot » et les 6 vérifications (détection, UEFI/Legacy, ordre, câblage, partitions, chargeur) ; Windows Boot Manager, BCD (capture 0xc000000f), WinRE (capture + tableau rôle/limites) ; prudence bootrec/bcdboot/diskpart (`clean`) |
| 2. Démarrage (Linux, MBR/GPT) | GRUB rescue, unknown filesystem, initramfs (UUID introuvable), emergency mode, fstab, UUID, `nofail`, `mount -a` (capture lsblk/fstab) ; tableau MBR/GPT, partition EFI, plan GPT Windows/Linux ; jamais de formatage réflexe |
| 3. Windows (1) | écran bleu, STOP code, « Ce qui a échoué », redémarrage automatique, BugCheck 1001, minidump, tableau de 6 codes d'arrêt → hypothèses ; Gestionnaire de périphériques (inconnu, triangle, flèche, Codes 10/22/28/43, restaurer le pilote) ; Observateur d'événements (journaux, niveau, source, ID, 8 événements réels), corrélation ≠ causalité ; 3 captures |
| 3. Windows (2) | Gestion des disques (hors ligne, non initialisé, sans lettre, RAW, non alloué, plein) ; services (statut, type de démarrage, compte, dépendances) ; tableau des commandes avec colonne diagnostic / modification (ipconfig, ping, nslookup, tracert, sfc, DISM, chkdsk sans paramètre, /f, /r, gestionnaire des tâches, msconfig) ; Windows Update (0x80070070), profil temporaire (1511), droits, applications — sans solution magique |
| 4. Linux (1) | 11 messages fréquents (emergency, failed, dependency, inactive, permission denied, read-only, no space, command not found, mount, réseau) ; systemctl / journalctl (-b, -u, -p, -x) / dmesg, lecture vs action ; df -h, df -i, du, lsblk, mount/findmnt, ip addr, ip route, ping, ss, resolvectl/dig ; fichier supprimé encore ouvert (lsof +L1) ; 2 captures |
| 4. Linux (2) | droits rwx (schéma `ls -l`), chmod/chown, jamais `chmod 777` ; apt vs dnf et leurs messages réels |
| 5. Réseau et corrélation | « Connectivité limitée », APIPA 169.254, média déconnecté, passerelle, DNS, conflit IP, imprimante hors ligne ; ordre des tests et périmètre ; bips/codes POST propres au constructeur (renvoi PR06) ; pannes intermittentes (chronologie, conditions, changements, preuves, répétition) |
| 6. Compte rendu | modèle en 13 rubriques (dont « cause non déterminée ») ; ce qu'on attend d'une réponse écrite + exemple |
| Exemples : 5 cas résolus | 1 absence de boot (BCD 0xc000000f) ; 2 BSOD après pilote ; 3 périphérique Code 43 ; 4 Linux service failed (ssh) ; 5 « No space left on device » |
| Pièges | 12 encadrés |
| Exercices corrigés (16) | cartes : contexte, documents (tableaux, terminaux), consignes, corrigé étape par étape + barème (replié) |
| Mini-examen /20 : mode d'emploi | 10 thèmes et points, déroulement, grille analytique (méthode, sécurité, tests, justification), nature de la correction |
| Fiche mémo, Sources et compléments | sources des messages, codes et commandes ; compléments signalés ; supports fictifs |

### Visuels (11 figures SVG construites sur données testées, aucune image générée)

1. Arbre de décision « À quelle étape l'erreur survient-elle ? » (9 questions dans l'ordre du
   démarrage, piste par stade) ; 2. flux « Lire → Hypothèse → Test → Action → Validation » ;
3. plan de partitionnement GPT (disque Windows : ESP FAT32 100 Mo, MSR 16 Mo, C: NTFS,
   récupération ; disque Linux : ESP, /, swap — exemple fictif, cases non proportionnelles) ;
4-11. **captures fictives** identifiées comme telles : Windows Boot Manager (0xc000000f), WinRE
   (options avancées), écran bleu (0xD1, nom de pilote inventé), Observateur d'événements
   (41, 6008, 1001, 20003), Gestionnaire de périphériques (Code 43, symboles écrits en
   toutes lettres), terminal `systemctl status` + `journalctl -u ssh`, terminal `df -h`/`du`,
   terminal `lsblk`/`fstab`. Texte alternatif complet, légende, « schéma non officiel »,
   lignes ≤ 56 caractères (testé), information jamais portée par la seule couleur.

### Exercices et mini-examen

- 16 exercices (ticket : ≥ 15) : **6 analyses de captures/journaux** (≥ 5 : stades, Observateur
  d'événements, codes du Gestionnaire, mode d'urgence fstab, « Permission denied », inodes),
  **6 procédures ordonnées** (≥ 5 : méthode universelle et DISM → SFC en remise en ordre ;
  No bootable device après mise à jour du firmware, grub rescue, 0x80070070, chkdsk), **4 cas
  croisés** matériel/système/réseau (≥ 3 : APIPA, imprimante hors ligne après changement de
  box, gels intermittents et disque, Linux en lecture seule).
- Mini-examen : 10 questions à réponse libre (6 courtes, 4 analyses de documents dont un
  compte rendu), 2 points chacune avec grille analytique ; jamais affichées dans le cours ; pas
  de développé d'acronyme ni de message isolé (contexte ≥ 150 caractères, testé).

### Intégration (moteur existant, aucune table, aucune migration)

- `app/v1/ampcr_pratique_pr11_{course,figures,bank}.py` ; PR11 ajouté à `PRACTICAL_COURSES`
  avec son `PedagogicalContext` de correction (`app/v1/ampcr_pratique_bank.py`) ; seed
  idempotent `_seed_uaa(…, "PR11", …)` (`app/seed.py`).
- Partagé, additif : type `Ordering` + `ordering` dans `item_content` (remises en ordre de la
  banque pratique) ; document `kind="console"` → mise en page `console` dans
  `_document_layouts.html` (police à chasse fixe, ligne à ligne, mention « extrait fictif »)
  et CSS `.jc-sd-console`/`.jc-pr-console` (fond clair à l'impression) ; helper
  `partition_map_svg` (`ampcr_pratique_visuals.py`) ; `_exercise_card` de PR06 paramétré
  (ancre, affichage des étapes à ordonner, terminaux).
- Docs : `current_state.md`, `ampcr_pratique_v1.md` (cours publiés + § 2.5 documents console
  et ordering), `changelog.md`.

## 3. Vérifications

- `tests/test_ticket194_ampcr_pratique_pr11.py` : 25 tests (stades et arbre dans l'ordre,
  flux, messages et codes des captures, df cohérent, partitions dessinées dans l'ordre du
  disque, lignes de capture ≤ 56 caractères, figures valides/accessibles/fictives, nombres
  d'exercices par type, 10 questions = 20 points en réponse libre, contenus conformes aux
  schémas des types existants, remises en ordre jamais déjà ordonnées, 5 cas, examen absent du
  cours, avertissement présent à côté de chkdsk /r, chmod 777, fsck, diskpart, 115 notions
  de la matière 1-6, types de cartes, seed idempotent et renommage de bloc, import 26 questions
  avec documents console et tableau, contexte de correction, page cours (figures uniques,
  16 cartes, terminaux, corrigés repliés), accueil « 2 cours publiés », matrice, sessions
  practice/exam tirées de leur seule réserve sans génération, document console rendu en
  session, longueur d'examen 10, note /20, deux sessions d'entraînement complètes soumises).
- Tests adaptés : PR06 (`published_uaas` contient PR06, comptage de l'UAA PR06 seule,
  « cours publiés ») et comptage du seed (+1 UAA, +16 blocs).
- **Suite complète : 2286 réussis, 0 échec** (17 min, avant le correctif #242) ; après le
  correctif : PR11 + PR06 + seed (68) verts. Tests #192, #236, mises en page de documents
  (#149), sources (#79), remise en ordre (#153), composition (#148) : verts.
- `ruff check` sans erreur sur tous les fichiers Python touchés.
- Installation (deux passes, sous verrou) : sauvegardes
  `jury_central-pre-ticket194-20261026-184223.db` et `…-fix-20261026-184517.db` ;
  fast-forward `e6c543e` → `f534e12` → `26bb9d7` ; `pyproject.toml` inchangé ; seed idempotent
  (1 UAA + 16 blocs, puis 1 bloc renommé ; les 52 blocs FSE sont recréés à l'identique à chaque
  seed, comportement existant) ; services actifs ; `/health` OK local et public ; PR11, PR06,
  `/ampcr-pratique`, matrice, `/modules/ampcr`, MC01, FSE01, `/` en 200 (practice/exam : 303
  vers la connexion, attendu) ; 11 figures et 16 cartes servies ; compteurs 18 comptes /
  80 sessions / 636 → 637 réponses (activité d'un utilisateur pendant l'installation, aucune
  baisse).
- **Rendu réel** (Chromium/Playwright sur le site installé) : 390 px et 1280 px sans
  débordement horizontal, 11 figures lisibles (captures contrôlées une à une à 390 px) ;
  le contrôle a révélé deux libellés de l'arbre qui touchaient le bord de leur case → corrigés
  (PR #242) puis recontrôlés ; impression A4 générée (≈ 62 pages), carte d'exercice avec
  terminaux contrôlée en mode impression (fond clair, lignes repliées).
- **Non vérifié** : qualité réelle de la correction IA sur ces grilles (tests avec
  `FakeAIProvider` uniquement) ; rendu sur un vrai téléphone ; PDF A4 non relu page par page ;
  sessions vues uniquement par les tests (pas de compte de test utilisé sur le site).

## 4. Checklist de validation éditoriale et visuelle (#192 § 3)

- [x] Toute la matière obligatoire enseignée, dans l'ordre 1 → 6 (test des notions).
- [x] Sections rattachées à AP-09/AP-13/AP-15 ; AP-C01, AP-C03 et compléments signalés.
- [x] Messages, codes et commandes vérifiés et sources citées (bloc « Sources » ; § 5 ci-dessous).
- [x] Aucune modalité, durée, question « officielle » ou valeur inventée ; supports marqués fictifs.
- [x] Sécurité des données rappelée avant toute action ; aucune action destructive en premier
      réflexe ; avertissement à côté de chkdsk /r, diskpart, fsck, chmod 777 (testé).
- [x] Renvois vers la théorie MC et PR06 au lieu de dupliquer.
- [x] Chaque question : contexte, données, tâche, barème, corrigé ; pas de développé d'acronyme ni de message isolé.
- [x] Correction invisible avant envoi ; formulation libre acceptée (grille et contexte de correction).
- [x] 5 cas, 16 exercices (6/6/4), mini-examen 10 questions /20.
- [x] Schémas SVG depuis des données testées ; sens de lecture indiqué (haut → bas, début → fin du disque).
- [x] Légende, texte alternatif, « non officiel » ; information non portée par la seule couleur.
- [x] Lisible à 390 px, contrôlé ; A4 généré (non relu page par page).
- [x] Aucune image générée (coût API : 0).
- [x] UAA du module `AMPCR-PRATIQUE`, seed idempotent ; matrice à jour ; MC01–MC38 et PR06 inchangés.
- [x] Tests ciblés et suite complète verts, ruff propre ; rapport, commentaire ; email par l'orchestrateur.

## 5. Choix techniques faits seul

1. **Langue des captures** : messages Windows en français (version FR, wording vérifié :
   BCD, écran bleu, Code 43, événements) ; terminaux Linux en anglais (locale la plus courante
   sur un serveur ; la version française du message « No space left on device » est citée dans
   les Sources). Le cours précise que la présentation varie selon la version et la langue.
2. **Faits techniques retenus** (sources Microsoft Learn, pages de manuel, manuel GRUB,
   documentation Debian/Fedora, RFC 3927) : 0xc000000f = BCD manquant/erroné ; 0xD1, 0xA,
   0x1A, 0x50, 0x7B, 0xEF, 0x116, 0x124 ; Kernel-Power 41, EventLog 6008, BugCheck 1001,
   disk 7 et 153, SCM 7000/7009/7031/7038, User Profile Service 1511, WindowsUpdateClient
   19/20, UserPnp 20003 ; 0x80070070 = disque plein ; Codes 10/22/28/43 ; DISM avant SFC ;
   chkdsk sans paramètre = lecture seule, /f corrige, /r = /f + secteurs ; systemd/journald
   (`-b -1` seulement avec journal persistant) ; ext4 `errors=remount-ro` ; inodes fixés à la
   création ; fichier supprimé encore ouvert (`lsof +L1`) ; APIPA 169.254.0.0/16 ;
   Windows 11 = UEFI ; MBR 4 partitions principales et 2 Tio ; GPT 128 partitions sous Windows.
   Les noms de machines, pilotes (« wlanxv64.sys »), UUID et dates sont inventés et signalés.
3. **Remises en ordre (`ordering`)** pour 2 des 6 procédures : correction locale tout ou rien,
   utile à l'entraînement ; les 4 autres procédures restent rédigées (compétence de l'épreuve).
   Pas d'`ordering` dans le mini-examen (réponses libres exigées).
4. **Documents « console »** : nouvelle mise en page `console` (au lieu d'un texte en
   paragraphes) pour que journaux et terminaux restent lisibles ligne à ligne ; le texte du
   document reste transmis tel quel au correcteur.
5. **Pas de figures répétées** : les cas renvoient aux captures des sections (identifiants HTML
   uniques, testé).
6. **Correctif après contrôle visuel** : bloc « Méthode universelle » renommé (ancien titre en
   `PR11_OBSOLETE_TITLES`) pour que le seed idempotent remplace le contenu déjà seedé —
   mécanisme existant du seed.
7. Matrice : AP-09, AP-13 passent « partiel » (EX02 pas encore publié) ;
   `VALIDATED_REQUIREMENT_IDS` reste vide (validation par le propriétaire).
8. Aucune image générée par API : tous les supports utiles sont des schémas ou des captures
   texte, plus exacts qu'une image (et la règle interdit les captures générées).

## 6. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 7. Reste à réaliser / suites proposées

- Validation pédagogique et visuelle par le propriétaire (puis, quand EX02 sera publié et relu,
  ajout éventuel d'AP-09/AP-13 à `VALIDATED_REQUIREMENT_IDS`).
- EX02 (#231) peut réutiliser les captures et le format « console » de PR11 ; PR12 (#215,
  dépannage logiciel et restauration) prolonge les sections 2-3 sans les dupliquer.
- Remarque hors périmètre (non modifiée) : la mise en page `console` est désormais disponible
  pour d'autres matières (journaux, sorties de commandes) si un ticket le demande.
