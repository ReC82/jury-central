# Ticket #233 — [AMPCR pratique EX04] Examen blanc écrit — réseau, configuration et dépannage

- Ticket : https://github.com/ReC82/jury-central/issues/233
- **État réel : Installé — à tester**
- SHA installé : `042407f5de437a22f2533d5170f6b66168c8fc8a` (fusion de la PR #297 dans `develop`)
- Date : 2026-10-27 (session jcorch autonome)

## 1. Résultat

Le **quatrième examen blanc** du parcours **Informatique AMPCR → Pratique écrite** est publié :
**EX04 « Examen blanc écrit — réseau, configuration et dépannage »**, épreuve autonome **/100** du
module 4 du plan (cours PR18 → PR25, tous publiés avant cette session). Il est placé juste après
PR25 dans la navigation. L'emplacement EX04 du plan installé (`_EXERCISE_ROWS`, numérotation
définitive de #236 : « EX04, ticket 233 ») porte bien le sujet du ticket : aucun écart, aucun autre
cours ni examen touché. Module `AMPCR-PRATIQUE` uniquement : Théorie (MC) et Pratique restent
séparées (banques, sessions, progression). Même modèle d'intégration que EX01, EX02 et EX03.

### Ce que voit le candidat

- **Page « Sujet »** (`/uaa/ampcr-pratique-ex04`, onglets « Sujet » et « Examen blanc ») — version
  candidat **sans aucun corrigé**, 7 séquences : présentation, organisation et notation (10 × 10
  points, barème analytique, corrigé après remise, durée conseillée 2 h 30 donnée comme repère
  personnel **et non comme durée officielle**, calculatrice utile), barème global, 12 exigences
  officielles évaluées ; partie 1 ; dossiers A, B, C ; méthode ; sources et supports fictifs. À
  l'impression (A4) : 12 lignes de réponse par question, chaque dossier sur une nouvelle page.
- **Examen blanc** (`/uaa/ampcr-pratique-ex04/exam`) : 10 questions, une par écran, avec les
  documents de leur dossier (tableaux, captures de commandes en police fixe, 3 schémas avec leur
  description écrite) ; sauvegarde automatique et reprise ; barème et corrigé invisibles avant la
  remise ; note /100 (et repère /20) puis corrigé détaillé. `/practice` redirige vers l'examen.

### Les 10 questions (10 points chacune, barème en 3 ou 4 critères, corrigé détaillé)

| N° | Partie | Question | Exigences |
|---|---|---|---|
| 1 | Partie 1 | Plan de réseau (schéma) : étoile étendue et hub, panne de SW1, couches OSI/TCP-IP de R1/SW1/hub, **7 domaines de collision, 2 de diffusion**, MAC/IP de destination des trames PC3→PC6 (MAC de la passerelle) et PC3→PC4, NetBEUI non routable | AP-23, AP-29, AP-31 |
| 2 | Partie 1 | Calculs IPv4 : /26, /21, masque 255.255.255.192, /27 → réseau, diffusion, plage, hôtes (62, 2 046, 62, 30) ; deux postes /26 dans des réseaux différents ; bloc pour 50 postes (/26) ; identifier MAC/IP : bits I/G et U/L, APIPA, bouclage, 172.31 privée / 172.32 publique | AP-30 |
| 3 | Dossier A | Connexion directe : Auto MDI-X (droit suffit ; croisé sinon), relevé « Défaillance générale » (autre réseau, pas de passerelle), configuration du portable, relevé « délai dépassé » = pare-feu ICMP, accès `\\192.168.10.1\Agenda` | AP-28, AP-30 |
| 4 | Dossier A | Mini-réseau 5 postes + imprimante (schéma) : rôles box/switch, ports, **4 erreurs** (passerelle = un poste, masque /16, adresse fixe dans l'étendue DHCP, doublon IP), plan corrigé, procédure de validation | AP-38, AP-30, AP-31 |
| 5 | Dossier B | Poste « sans Internet » : ping box OK, ping IP Internet OK, ping du nom KO, nslookup vers l'ancien DNS en délai, vers SRV-01 OK → **panne DNS, connectivité IP intacte** ; correction et vérification | AP-32, AP-37 |
| 6 | Dossier B | Linux sans route par défaut (`ip route`, « Network is unreachable ») ; portable en APIPA, journal DHCP « no address available », étendue de 20 adresses pleine → agrandir (100 adresses) / baux plus courts | AP-37, AP-30, AP-32 |
| 7 | Dossier B | Panne Internet de toute l'agence : box joignable, IP Internet injoignable, tracert arrêté à la box, VDSL non synchronisée → liaison du fournisseur ; actions ordonnées ; **rapport d'intervention** | AP-32, AP-37 |
| 8 | Dossier C | Wi-Fi : fiche du point d'accès (9 réglages à corriger : WPA/TKIP, clé, WPS, admin, micrologiciel, canal 3, 40 MHz, SSID masqué, invités), canal depuis un relevé en % (→ dBm, canal 11), répéteur : 13 Mb/s en R1 contre 26 sans répéteur et 36 en R2 (schéma) | AP-33 |
| 9 | Dossier C | Accès effectifs partage + NTFS de 3 comptes sur 3 dossiers, besoin non satisfait (partage « Tout le monde : Lecture » limite la comptable), session locale = NTFS seul, mise à disposition d'un dossier Modèles (lecteur réseau) | AP-25, AP-26, AP-27 |
| 10 | Dossier C | Après changement de box : traceur passé de .120 à .131 par DHCP (adresse fixe hors étendue ou imprimante partagée par le serveur) ; lecteur P: erreur 53, ping OK, port 445 fermé → SMB bloqué, pas les droits | AP-25, AP-26, AP-37 |

Les 12 exigences de l'emplacement EX04 (AP-23, 25, 26, 27, 28, 29, 30, 31, 32, 33, 37, 38) sont
toutes évaluées ; aucune n'est déclarée « validée » (matrice inchangée). Les 8 cours du module
sont cités dans les liens « À revoir ».

### Fichiers

- `app/v1/ampcr_pratique_ex04_figures.py` — données des dossiers et 3 schémas ; chaque valeur vient
  de la règle **du cours** : `Lan`, `collision_domains`, `broadcast_domains`, `next_hop`,
  `crosses_router`, `domains_svg` (PR19) ; `subnet_facts`, `mask_to_prefix`, `same_subnet`,
  `smallest_prefix_for`, `address_kind`, bits MAC, `plan_errors`, `ipconfig_all_lines`,
  `ip_addr_lines`, `ip_route_lines` (PR20) ; `cable_needed`, `ping_outcome`, `ping_lines` (PR21) ;
  `effective_access`, `limiting_layer`, `net_use_lines`, `port_test_lines` (PR23) ;
  `win_ping_lines`, `nslookup_lines`, `tracert_lines`, `dnsmasq_lines`, `pool_size`, `in_pool`
  (PR24) ; `audit_config`, `best_channel_24`, `networks_lines`, `received_dbm`, `link_rate`,
  `repeater_mbps` (PR25).
- `app/v1/ampcr_pratique_ex04_bank.py` — 10 questions, documents des dossiers, validation.
- `app/v1/ampcr_pratique_ex04_course.py` — 7 blocs de la page du sujet.
- `app/static/img/ampcr-pratique/ex04-plan-reseau.svg`, `ex04-cabinet-mini-reseau.svg`,
  `ex04-wifi-repeteur.svg` (identiques au SVG du code, vérifié par test).
- `app/v1/ampcr_pratique_bank.py` — EX04 déclaré, contexte de correction propre (notions du
  module ; pénalités : calcul d'adresse faux, confusion connectivité IP / DNS, adresse fixe dans
  l'étendue, correction qui casse autre chose, Wi-Fi en WEP/WPA-TKIP, confusion partage/NTFS).
- `app/seed.py` — `_seed_uaa(…, "EX04", …, position 25)` (additif).
- `tests/test_ticket233_ampcr_pratique_ex04.py` (31 tests) ; comptage adapté dans
  `tests/test_admin_content_hierarchy.py` ; motif « 3 examens blancs » assoupli dans
  `tests/test_ticket232_ampcr_pratique_ex03.py`.
- `docs/current_state.md`, `docs/ampcr_pratique_v1.md`, `docs/changelog.md`.

## 2. Liens pour tester

- Sujet (public) : https://jury-central.lodylands.com/uaa/ampcr-pratique-ex04
- Examen blanc (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-ex04/exam
- Accueil du parcours : https://jury-central.lodylands.com/ampcr-pratique
- Schémas : https://jury-central.lodylands.com/static/img/ampcr-pratique/ex04-plan-reseau.svg,
  https://jury-central.lodylands.com/static/img/ampcr-pratique/ex04-cabinet-mini-reseau.svg,
  https://jury-central.lodylands.com/static/img/ampcr-pratique/ex04-wifi-repeteur.svg

Procédure courte : ouvrir le sujet, parcourir les 7 séquences ; aperçu avant impression
(Ctrl + P) ; lancer l'examen blanc, répondre à quelques questions, quitter et reprendre, remettre,
vérifier la note /100, le barème et le corrigé.

## 3. Vérifications effectuées

- Tests ciblés `tests/test_ticket233_ampcr_pratique_ex04.py` : **31 passed** — recalculs
  indépendants avec le module standard `ipaddress` (réseaux, diffusions, plages, hôtes, /26 pour
  50 postes, 172.31/172.32) ; bits I/G et U/L ; domaines recomptés et panne de SW1 recalculée sur
  le graphe ; trame vers la MAC de la passerelle ; pings de la connexion directe ; 4 erreurs du
  plan du cabinet et plan corrigé sans doublon ni adresse fixe dans l'étendue ; DNS (IP OK, nom
  KO) ; absence de route par défaut ; étendue de 20 adresses = 20 baux ; tracert arrêté à la box ;
  conversion % → dBm et canal 11 ; débits 13 / 26 / 36 Mb/s recalculés ; matrice des accès
  effectifs écrite en dur ; adresses du traceur dans l'étendue ; captures ≤ 56 caractères ; 3
  schémas valides, accessibles, **sans verdict**, fichiers statiques identiques ; 10 × 10 = 100,
  matière du ticket, 12 exigences couvertes, réponses absentes des énoncés ; sujet sans corrigé ;
  seed idempotent, EX04 juste après PR25 (EX01–EX03 inchangés) ; réserve `exam` seule ; contexte
  de correction propre ; navigation, accueil « 4 examens blancs sur 6 » ; session d'examen :
  corrigé masqué avant remise, 3 schémas dans leurs questions, note /100.
- **Suite complète : 3080 passed** (une exécution ; seed et banque partagée touchés).
- `ruff check` : fichiers créés et modifiés sans erreur.
- Contrôle visuel (navigateur sans interface) : les 3 schémas à 400 px (corrigé pendant la session :
  ligne des distances du plan Wi-Fi) ; page du sujet rendue par l'app à 1 280 px ; une question à
  400 px (tableaux et captures lisibles, défilement horizontal des captures comme dans les cours).
- Installation : arbre propre sur `develop`, sauvegarde
  (`~/.local/state/jury-central-orch/backups/jury_central-pre-ticket233-20261027-162426.db`),
  fast-forward `f4f358d → 042407f`, seed idempotent (1 UAA créée ; 59 blocs « créés » = 7 blocs
  EX04 + le remplacement habituel des 52 blocs FSE pilotés par le code), redémarrage des deux
  services (actifs), `/health` local et public OK ; sujet, accueil, matrice, PR25, EX03 et les 3
  SVG en HTTP 200 (examen : 303 vers la connexion sans session, normal) ; sujet servi avec 10
  questions et aucun « Corrigé de référence » ; accueil « 4 examens blancs sur 6 ». Compteurs
  utilisateurs/sessions/réponses inchangés (18 / 84 / 659).

Non effectué : validation pédagogique humaine (au propriétaire) ; correction réelle par l'IA
(tests avec `FakeAIProvider`) ; contrôle de l'impression PDF page par page ; session d'examen
parcourue en vrai sur le site.

## 4. Choix techniques faits seul

- **Périmètre du module** : le plan installé rattache PR18 → PR25 au module 4 (la note de la file
  cite PR19–PR25) ; PR18 (installation physique d'un mini-réseau) est donc aussi couvert (question
  4, exigence AP-38).
- **10 questions de 10 points** (le ticket demande 10 à 14) : même choix que EX01–EX03 ; les 12
  exigences tiennent dans 10 questions.
- **Schémas sans verdict** : le plan du réseau n'affiche ni numéros de domaines ni zones (dessin du
  cours PR19 avec ces options coupées) ; le schéma du cabinet est dessiné pour EX04 sans la note
  « adresses fixes hors de l'étendue » du dessin de PR21 (elle soufflait une erreur) ; le plan Wi-Fi
  donne les dBm mesurés sans appréciation.
- **Captures de commandes** en documents « console » (pas d'image) : format réel simplifié, lignes
  de 56 caractères au plus ; lignes `ping` Linux raccourcies (sans `time=`).
- **Relevé Wi-Fi en pourcentages** (comme `netsh wlan show networks`) : le candidat convertit en
  dBm (règle du cours PR25) ; l'énoncé le lui rappelle.
- **Question 10, lecteur P:** : les relevés prouvent que le port 445 est fermé depuis ce portable
  sans désigner une cause unique ; le barème accepte pare-feu/profil réseau du portable ou règle du
  serveur (méthodes alternatives valides, comme le demande le ticket).
- **Pas d'image générée** : valeurs et plans exacts mieux servis par un dessin construit sur des
  données testées. Adresses publiques des plages de documentation (RFC 5737) ; seule l'adresse
  172.32.4.9 sert d'exemple de classement « publique », sans désigner de service.

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Éléments restant à réaliser

- Validation pédagogique et visuelle par le propriétaire (sujet, impression, correction réelle).
- Suite de la file : EX05 (#201), EX06 (#234), PR26–PR30, puis audit final (#235).
- Suggestions déjà notées (hors périmètre) : fixer l'ordre des questions d'un examen blanc dans le
  moteur de sessions (la session les présente mélangées, les numéros du sujet ne correspondent donc
  pas aux positions de la session) ; bouton de fin de séquence « Passer à l'examen » sur la page
  d'un EX.

## Notification

L'email de livraison est envoyé par le superviseur jcorch à la fin de la session, avec ce rapport
en pièce jointe (copie dans `~/.local/state/jury-central-orch/reports/`).
