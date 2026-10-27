# Ticket #224 — [AMPCR pratique PR25] Wi-Fi : configuration, couverture, sécurité et diagnostic

- Ticket : https://github.com/ReC82/jury-central/issues/224
- **État réel : Installé — à tester**
- SHA installé : `6b3d698c672702075c8f44428aa3bb6b599c424e` (fusion de la PR #295 dans `develop`)
- Date : 2026-10-27 (session jcorch autonome)

## 1. Résultat

Le cours **PR25 « Wi-Fi : configuration, couverture, sécurité et diagnostic »** est publié dans le
parcours **Informatique AMPCR → Pratique écrite** (module `AMPCR-PRATIQUE`), séparé de la théorie
MC (cours, banque, examen et progression distincts ; liens seulement vers MC25 et MC26). Il occupe
la position 25 de l'ordre pédagogique, après PR24.

**Numérotation vérifiée** : dans le plan installé (`_COURSE_ROWS`, numérotation de #236),
l'emplacement PR25 porte bien le sujet du ticket (« PR25, ticket 224, Wi-Fi : configuration,
couverture, sécurité et diagnostic », exigence officielle p. 6 **AP-33** « WIFI : principe,
sécurisation, cryptage, répéteur »). Aucun autre cours n'a été touché ni renuméroté.

### Contenu (16 blocs)

**9 chapitres**, chacun avec objectifs, théorie, procédure professionnelle à rédiger, erreur
fréquente, attendu « à l'écrit », repère rapide et renvoi aux exercices liés :

1. **Architecture** : client, point d'accès, routeur (box), serveur DHCP, répéteur, mesh ; SSID et
   BSSID ; comparaison point d'accès câblé / mesh / répéteur.
2. **Normes 802.11 et bandes** : b/a/g/n/ac/ax/be (Wi-Fi 4 à 7, débits théoriques) ; 2,4 / 5 /
   6 GHz (canaux autorisés en Europe, DFS, WPA3 obligatoire en 6 GHz, compatibilité des appareils).
3. **Canaux, largeur, interférences** : fréquences 2407 + 5n, chevauchement, 1/6/11, conversion
   % → dBm, choix du canal le moins gêné, canaux 5 et 6 GHz par largeur (20 à 160 MHz),
   micro-ondes et Bluetooth.
4. **Portée, obstacles, débit réel, répéteur, roaming** : dBm et seuils, affaiblissement en
   espace libre + obstacles, plan de couverture estimé, débit utile, répéteur à une radio,
   roaming (même SSID / sécurité / clé, canaux différents, 802.11k/v/r).
5. **Connexion d'un client** : découverte, association (SAE), échange en 4 temps / 802.1X-RADIUS,
   DHCP, DNS ; lecture de `netsh wlan show interfaces`.
6. **Sécurité** : ouvert/WEP/WPA-TKIP à refuser, WPA2 AES-CCMP, transition WPA2/WPA3, WPA3 SAE,
   Entreprise 802.1X/RADIUS ; WPS, mot de passe fort, mot de passe d'administration, réseau
   invités (VLAN, isolation), fausses protections (SSID masqué, filtrage MAC).
7. **Configurer un point d'accès** : arborescence d'administration, SSID, bande, canal,
   sécurité, clé, une seule source DHCP, micrologiciel et sauvegarde, invités, test et fiche.
8. **Diagnostiquer la connexion** : réseau invisible, mauvaise clé, mauvaise IP (169.254, second
   DHCP), connecté sans Internet (passerelle, Internet, DNS).
9. **Diagnostiquer la qualité** : signal faible, interférence, répéteur mal placé.

**3 procédures illustrées** : configurer un point d'accès (8 étapes), étendre la couverture (7),
dépanner un poste Wi-Fi (8).

**5 cas résolus** : mise en service d'un cabinet ; stock et étage mal couverts ; « pas
d'Internet » après un orage ; lenteurs dues au canal ; WPA3 seul et vieux portable.

**20 exercices corrigés** (ticket : ≥ 18) avec contexte, consignes, barème et corrigé :
3 remises en ordre ; 4 classements auto-corrigés (sécurité, piste d'une panne, bande, clés) ;
**4 schémas à compléter** (architecture, canaux 2,4 GHz, couverture, répéteur) ; **7 exercices
sur relevés** (`netsh wlan show networks/interfaces/drivers/profiles`, `ipconfig /all`, `ping`,
`nslookup`) — ticket : ≥ 5 ; **7 diagnostics** — ticket : ≥ 5 ; **6 choix de configuration** —
ticket : ≥ 4.

**Mini-examen de 10 questions /20** (2 points chacune, réponses libres, onglet « Examen blanc »,
jamais affiché dans le cours), dont un relevé Linux `nmcli`.

**13 figures SVG + 4 schémas à compléter** produits depuis des données testées, avec texte
alternatif, légende et mention « schéma non officiel ». **Aucune image générée.**

### Fichiers

- `app/v1/ampcr_pratique_pr25_figures.py` — données et calculs (canaux, `best_channel_24`,
  `blocks_5`/`blocks_6`, `fspl_db`, `received_dbm`, `quality_pct`, `link_rate`, `repeater_mbps`,
  `SECURITY_MODES`, `passphrase_issues`, `audit_config`, `wifi_checks`/`wifi_diagnosis`), relevés,
  figures.
- `app/v1/ampcr_pratique_pr25_bank.py` — 20 exercices et 10 questions d'examen.
- `app/v1/ampcr_pratique_pr25_course.py` — les 16 blocs.
- `app/v1/ampcr_pratique_bank.py` — déclaration de PR25 et contexte de correction IA propre.
- `app/seed.py` — `_seed_uaa(…, "PR25", …, position 25)`, ajout seul.
- `app/static/img/ampcr-pratique/pr25-*.svg` (4 fichiers).
- `tests/test_ticket224_ampcr_pratique_pr25.py` (34 tests) ; comptages adaptés dans
  `tests/test_admin_content_hierarchy.py` et `tests/test_ticket223_ampcr_pratique_pr23.py`.
- `docs/current_state.md`, `docs/ampcr_pratique_v1.md`, `docs/changelog.md`.

## 2. Liens pour tester

- Cours : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr25
- S'entraîner (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr25/practice
- Examen blanc /20 (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr25/exam
- Accueil du parcours : https://jury-central.lodylands.com/ampcr-pratique
- Matrice : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte :
1. Ouvrir le cours, parcourir les 16 séquences (chapitres et schémas, cas résolus, exercices avec
   les 4 schémas à compléter).
2. « S'entraîner » : 10 exercices tirés des 20 (schémas et relevés affichés dans la question).
3. « Examen blanc » : 10 questions, note sur 20 ; après l'envoi, vérifier corrigé et barème.

## 3. Vérifications effectuées

- **Tests ciblés** `tests/test_ticket224_ampcr_pratique_pr25.py` : **34 passed** — fréquences et
  chevauchement recalculés (centres à moins de 22 MHz), canal conseillé recalculé à la main pour
  chaque relevé, canaux 5 GHz (19/9/4/2) et 6 GHz (24/12/6/3) par largeur, formule d'espace libre
  et obstacles recalculée point par point, conversion % ↔ dBm, débit derrière un répéteur, modes
  de sécurité, clés, audit de configuration, ordre du diagnostic ; largeur (≤ 56 caractères) de
  toutes les captures ; figures (validité, accessibilité, données dessinées) ; schémas à compléter
  sans leurs réponses ; fichiers statiques identiques au SVG généré ; exercices (format du socle,
  auto-correction, valeurs des corrigés, aucune affirmation fausse type « masquer le SSID
  protège ») ; cours (matière du ticket, 5 cas, 3 procédures, examen absent, liens, aucun lien
  vers un cours non publié) ; types de cartes ; seed idempotent et position ; réserves séparées ;
  contexte de correction ; pages ; sessions d'entraînement et d'examen /20 sans génération IA.
- Tests PR22, PR23 et hiérarchie de contenu relancés : OK (119 passed avec ceux de PR25).
- **Suite complète** (une exécution, `seed.py` partagé) : **3 049 passed**, aucun échec (26 min).
- **`ruff check`** sur les fichiers créés et modifiés : All checks passed.
- **Contrôle visuel** (Chromium sans interface) des schémas ; corrigés pendant la session :
  chevauchements de boîtes dans l'architecture, arcs de canaux coupés au bord, numéros de canaux
  5 GHz superposés, textes du répéteur superposés, libellé « WPA (TKIP) (TKIP) ».
- **Installation** : arbre propre sur `develop` ; sauvegarde
  `~/.local/state/jury-central-orch/backups/jury_central-pre-ticket224-20261027-153714.db` ;
  avance rapide `585f304 → 6b3d698` ; seed : 1 UAA et 68 blocs créés (16 de PR25 + remplacement
  habituel des 52 blocs FSE) ; deux services actifs ; `/health` local et public OK ; PR25, PR24,
  accueil, matrice et schéma statique en HTTP 200 ; entraînement en 303 vers la connexion (normal
  sans session) ; 20 cartes d'exercice servies ; « 25 cours publiés sur 30 » ; compteurs
  utilisateurs / sessions / réponses inchangés (18 / 84 / 658).

**Non effectué** : validation pédagogique humaine ; session réelle avec la vraie correction IA ;
mesure Wi-Fi réelle (les valeurs du cours sont des estimations signalées comme telles).

## 4. Choix techniques faits seul

- **Réseau de référence** : l'atelier Durant de PR24 (192.168.20.0/24, box .1, SRV-01 DHCP/DNS .5,
  AP-01 .30, SSID ATELIER-PRO, invités en VLAN 30), complété d'AP-02 (.31) et d'un répéteur.
- **Couverture** : estimation simplifiée « 20 dBm − espace libre − obstacles » avec des
  affaiblissements d'obstacles en ordres de grandeur (2,4 / 5 GHz) ; présentée partout comme
  estimation, « la mesure sur place fait foi ».
- **Conventions signalées** : seuils −60 / −67 / −75 dBm ; voisin gênant à −80 dBm ou plus sur un
  canal à moins de 5 numéros ; débit de liaison selon le signal (802.11n 2×2, 20 MHz) ; débit
  utile = moitié, partagé ; répéteur à une radio = ÷ 2 ; règle des clés (12+ caractères de trois
  types ou phrase de 20+).
- **Canaux européens** : 5 GHz limité à 36–64 et 100–140 (canal 144 et 149+ non utilisés) ;
  6 GHz 5945–6425 MHz ; le texte rappelle que le pays réglé et la réglementation font foi.
- **Captures Windows** en français, simplifiées, 56 caractères par ligne au plus ;
  `netsh wlan show drivers` présenté en extrait simplifié.
- **Répéteur** traité en détail (exigence AP-33, absent de la théorie MC actuelle) ; mesh, roaming
  et 6 GHz signalés comme compléments.
- Schémas à compléter servis en fichiers statiques, comme PR18 à PR23.

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Éléments restant à réaliser

- Validation visuelle et pédagogique par le propriétaire.
- Suggestions (hors périmètre, non faites) : PR19 et PR24 citent « PR25 » sans lien (il n'était
  pas publié) ; un lien vers `/uaa/ampcr-pratique-pr25` pourrait y être ajouté. EX04 (#233), qui
  dépend de PR19–PR25, peut maintenant s'appuyer sur ce cours publié.
