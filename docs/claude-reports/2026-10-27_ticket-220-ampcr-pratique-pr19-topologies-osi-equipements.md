# Ticket #220 — [AMPCR pratique PR19] Topologies, OSI, TCP/IP, NetBEUI et équipements

- Ticket : https://github.com/ReC82/jury-central/issues/220
- **État réel : Installé — à tester**
- SHA installé : `50509621881781849379dc16355eecc53e12d711` (fusion de la PR #287 dans `develop`)
- Date : 2026-10-27 (session jcorch autonome)

## 1. Résultat

Le cours **PR19 « Topologies, OSI, TCP/IP, NetBEUI et équipements »** est publié dans le parcours
**Informatique AMPCR → Pratique écrite** (module `AMPCR-PRATIQUE`), séparé de la théorie MC
(cours, banque, examen et progression distincts ; liens seulement vers MC13, MC14, MC21 et MC23).
Il occupe la position 19 de l'ordre pédagogique : après PR18, avant PR20.

**Numérotation vérifiée** : dans le plan installé (`_COURSE_ROWS`, numérotation définitive de
#236), l'emplacement PR19 porte bien le sujet du ticket (« PR19, ticket 220, Topologies, OSI,
TCP/IP, NetBEUI et équipements », exigences officielles AP-23, AP-29 et AP-31). Aucun autre cours
touché ni renuméroté.

### Contenu (16 blocs)

**9 chapitres**, chacun avec objectifs, théorie, procédure professionnelle à rédiger, erreur
fréquente, attendu « à l'écrit », repère rapide et renvoi aux exercices liés :

1. **Topologies** bus, étoile, anneau, maillage : principe, exemple, avantages, défauts, effet
   d'une panne (calculé sur des modèles : étoile, étoile étendue, bus, anneau simple et double,
   maillage) ; nombre de liaisons n × (n − 1) ÷ 2 ; topologie physique et logique.
2. **Modèles OSI (7 couches) et TCP/IP (4 couches)** : rôle, unité de données, protocoles,
   équipement par couche.
3. **Encapsulation et trame Ethernet 802.3** : tailles (TCP 20, UDP 8, IPv4 20, Ethernet 14 + FCS
   4), MTU 1 500, trame 64 à 1 518 octets, bourrage, champs et types (0x0800, 0x0806, 0x86DD).
4. **Adresses MAC et IP, ARP, ports TCP/UDP** (table de ports), **protocole / service /
   équipement**.
5. **NetBEUI**, protocole historique non routable (noms NetBIOS, diffusion, remplacé par TCP/IP),
   comparé à TCP/IP et IPX/SPX.
6. **Équipements** : répéteur, hub (L1), pont, switch, point d'accès (L2), routeur (L3), modem,
   passerelle (par défaut), box ; procédure de choix.
7. **Domaines de collision et de diffusion** (comptage calculé) ; **VLAN** en complément.
8. **Chemin d'un paquet** PC → switch → box (NAT) → routeur de l'opérateur → serveur : adresses
   MAC et IP de chaque trame.
9. **Diagnostic couche par couche** (1 → 2 → 3 → 4 → 7) avec preuve à chaque couche.

**3 procédures illustrées** : choisir l'équipement adapté (5 étapes) ; suivre un paquet du PC à
Internet (6) ; diagnostiquer couche par couche (6).

**5 cas résolus** : atelier en bus coaxial et logiciel NetBEUI ; équiper une PME de A à Z ;
suivre un paquet jusqu'au site web ; un hub qui ralentit tout ; l'intranet ne s'ouvre pas
(diagnostic par couche, port 443 bloqué).

**20 exercices corrigés** (le ticket en demande au moins 18), avec contexte, consignes, barème et
corrigé :
- 3 remises en ordre (chemin d'un paquet, diagnostic par couche, encapsulation) ;
- 5 classements auto-corrigés (topologies, protocole/service/équipement, couche des protocoles,
  rôle des équipements, couche en défaut d'après un relevé) ;
- **6 schémas à compléter** (topologies, OSI/TCP-IP, encapsulation d'une requête DNS, adresses
  MAC/IP de deux trames, domaines de collision et de diffusion, champs d'une trame), affichés en
  SVG dans le cours **et** dans les sessions (`app/static/img/ampcr-pratique/pr19-*.svg`) ; les
  réponses ne figurent ni dans le dessin, ni dans la légende, ni dans les attributs ;
- **5 choix d'équipement ou de topologie** (rôles du catalogue, besoins d'une PME, hub à
  remplacer, deux réseaux IP reliés par erreur par un switch, étoile ou maillage entre agences) ;
- NetBEUI entre deux sites ; ports et pare-feu (port 587 bloqué, refus d'ouvrir 445/3389).

**Mini-examen de 10 questions /20** (2 points chacune, réponses libres, onglet « Examen blanc »,
jamais affiché dans le cours) : bus sans bouchon, site qui ne s'ouvre pas (DNS), taille d'un
accusé TCP (bourrage → 64 octets), MAC de destination locale/distante, domaines d'un bureau,
switch ou routeur pour l'étage, NetBEUI et routeur, port 443 fermé, rapport qui confond
protocole/service/équipement, anneau ou maillage entre six sites.

**10 figures SVG + 6 schémas à compléter**, produits depuis des données testées ; texte
alternatif, légende, mention « schéma non officiel ». **Aucune image générée.**

### Fichiers

- `app/v1/ampcr_pratique_pr19_figures.py` — données et calculs (`isolated_stations`,
  `mesh_links`, `OSI_LAYERS`, `TCPIP_LAYERS`, `encapsulate`, `FRAME_FIELDS`, `PORTS`,
  `DEVICES`, `collision_domains`, `broadcast_domains`, `next_hop`, `lan_frame`, `path_frames`,
  `fault_layer`, `crosses_router`), figures et schémas statiques.
- `app/v1/ampcr_pratique_pr19_bank.py` — 20 exercices et 10 questions d'examen, nombres calculés.
- `app/v1/ampcr_pratique_pr19_course.py` — les 16 blocs.
- `app/v1/ampcr_pratique_bank.py` — déclaration de PR19 et contexte de correction IA propre.
- `app/seed.py` — `_seed_uaa(…, "PR19", …, position 19)`, ajout seul.
- `app/static/img/ampcr-pratique/pr19-*.svg` (6 fichiers).
- `tests/test_ticket220_ampcr_pratique_pr19.py` (33 tests) ; comptages adaptés dans
  `tests/test_admin_content_hierarchy.py` et `tests/test_ticket219_ampcr_pratique_pr18.py`.
- `docs/current_state.md`, `docs/ampcr_pratique_v1.md`, `docs/changelog.md`.

## 2. Liens pour tester

- Cours : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr19
- S'entraîner (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr19/practice
- Examen blanc /20 (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr19/exam
- Accueil du parcours : https://jury-central.lodylands.com/ampcr-pratique
- Matrice : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte :
1. Ouvrir le cours, parcourir les 16 séquences (chapitres, cas résolus, exercices avec les 6 schémas à compléter).
2. « S'entraîner » : 10 exercices tirés des 20 (les schémas à compléter s'affichent dans la question).
3. « Examen blanc » : 10 questions, note sur 20 ; après l'envoi, vérifier corrigé et barème.

## 3. Vérifications effectuées

- **Tests ciblés** `tests/test_ticket220_ampcr_pratique_pr19.py` : **33 passed** — calculs
  recontrôlés indépendamment (liaisons d'un maillage ; effet d'une panne par topologie ; couches
  OSI/TCP-IP et couche des protocoles ; tailles d'encapsulation, bourrage, limite MTU ; champs de
  la trame ; ports ; domaines de collision et de diffusion sur plusieurs réseaux ; adresses des
  trames, envoi local ou vers la passerelle ; couche en défaut de bas en haut ; NetBEUI non
  routable) ; figures (validité, accessibilité, données dessinées) ; schémas à compléter sans leurs
  réponses (dessin, légende, attributs) et fichiers statiques identiques au SVG généré ; exercices
  (format du socle, auto-correction, nombres des corrigés, 6 schémas + 5 choix d'équipement,
  aucune question d'acronyme) ; cours (matière du ticket, 5 cas, 3 procédures, examen absent,
  liens, pas de lien vers PR21/23/25 non publiés, types de cartes) ; seed idempotent et position ;
  réserves séparées ; contexte de correction ; pages (cours, accueil, matrice, MC13/14/21/23) ;
  sessions d'entraînement et d'examen /20 sans génération IA.
- **Suite complète** (une exécution, `seed.py` partagé) : **2 915 passed, 1 failed** —
  `tests/test_ticket55_urgent_ampcr_full.py::test_json_autosave_api_never_reveals_correctness`
  (théorie MC01, question tirée au hasard ; repasse relancé seul ; échec intermittent préexistant,
  déjà signalé au ticket #219, hors périmètre).
- **`ruff check`** sur les fichiers créés et modifiés : All checks passed.
- **Contrôle visuel** (navigateur sans interface) des 16 schémas et de la page du cours rendue par
  l'application ; corrigés pendant la session : libellé du maillage trop long, en-têtes du tableau
  des trames, étiquettes des domaines de diffusion qui chevauchaient une liaison, légendes des
  schémas à compléter qui donnaient des réponses (taille UDP, noms de champs).
- **Installation** : arbre propre sur `develop` ; sauvegarde
  `~/.local/state/jury-central-orch/backups/jury_central-pre-ticket220-20261027-113217.db` ;
  avance rapide `e8d3ca5 → 5050962` ; seed : 1 UAA et 68 blocs créés (16 de PR19 + remplacement
  habituel des 52 blocs FSE) ; deux services actifs ; `/health` local et public OK ; PR19, PR18,
  PR20, accueil, matrice et schéma statique en HTTP 200 ; entraînement et examen en 303 vers la
  connexion (normal sans session) ; 20 cartes d'exercice servies ; « 21 cours publiés sur 30 » ;
  compteurs utilisateurs / sessions / réponses inchangés (18 / 84 / 658).

**Non effectué** : validation pédagogique humaine ; session réelle avec la vraie correction IA.

## 4. Choix techniques faits seul

- **Périmètre** : l'adressage IP, les masques et le format des adresses MAC restent en PR20, le
  dépannage complet en PR24, le bus coaxial en PR16, l'installation en étoile en PR18 (liens). La
  connexion de deux PC (PR21), les partages (PR23) et le Wi-Fi (PR25) sont cités sans lien (non
  publiés).
- **Valeurs normées** : en-têtes **sans option** (IPv4 20, TCP 20, UDP 8 octets), trame Ethernet
  II/802.3 de 64 à 1 518 octets hors préambule, ports IANA ; DNS et DHCP classés à la couche 7
  (protocoles applicatifs sur UDP) ; ARP présenté comme le lien entre couches 2 et 3, jamais
  demandé seul dans un classement (classement ambigu évité) ; modem classé couche 1 (signal),
  passerelle « 3 à 7 ».
- **Modèle de panne** : étoile et étoile étendue jugées par rapport à l'équipement central ;
  anneau simple = tout s'arrête, anneau double = rebouclage ; bus = tout le segment.
- **Comptage des domaines** : chaque liaison d'un switch, pont ou routeur = un domaine de
  collision ; un hub/répéteur réunit ses liaisons ; seul le routeur sépare les diffusions (VLAN
  traité en texte, comme complément).
- Adresses publiques des exemples dans les blocs de documentation RFC 5737 ; MAC, captures et
  entreprises **fictives**. Schémas à compléter servis en fichiers statiques comme PR18/EX01-EX03.
  Pas de nouvelle dépendance.

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Éléments restant à réaliser

- Validation pédagogique et visuelle par le propriétaire.
- Suggestion (hors périmètre, non faite) : le chapitre 2 de PR18 dit « Le détail des topologies
  est l'objet de PR19 » sans lien ; un lien vers `/uaa/ampcr-pratique-pr19` pourrait y être
  ajouté lors d'une prochaine retouche de PR18.
- Suite du parcours : PR21 (#221).
