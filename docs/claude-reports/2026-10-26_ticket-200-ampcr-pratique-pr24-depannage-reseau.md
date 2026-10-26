# Ticket #200 — [P0][AMPCR pratique PR24] Dépannage réseau et Internet — dossiers d'intervention écrits

Ticket : [#200](https://github.com/ReC82/jury-central/issues/200) · branche `feature/200-pr24-depannage-reseau` · PR [#251](https://github.com/ReC82/jury-central/pull/251)

**État réel : Installé — à tester.**

**SHA installé : `8cd5126`** (merge de la PR [#251](https://github.com/ReC82/jury-central/pull/251) sur `develop`, 26/10/2026).

## Liens pour tester

- Cours : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr24
- S'entraîner (20 exercices, 10 tirés par session, correction après envoi) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr24/practice
- Examen blanc (mini-examen 10 questions, note /20) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr24/exam
- Accueil du parcours (« 6 cours publiés ») : https://jury-central.lodylands.com/ampcr-pratique
- Matrice (AP-32 et AP-37 passent « partiel ») : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte : se connecter ; ouvrir le cours sur téléphone puis sur PC ; vérifier le schéma
du réseau de référence « l'atelier » (box, switch, serveur DHCP/DNS, NAS, imprimante, point
d'accès PoE, portable Wi-Fi), la page des ports du switch, la procédure en couches, les **trois
arbres** (général, Wi-Fi, partage) et les **sept documents de diagnostic** (APIPA, ping, tracert,
nslookup, journal DHCP, état Wi-Fi, Linux sans lien) ; lire les **six tableaux symptôme → test
discriminant → action** et les **six cas résolus** ; ouvrir quelques corrigés ; lancer
« S'entraîner » (un classement et une remise en ordre corrigés automatiquement, le reste en
réponses rédigées), puis « Examen blanc » (10 scénarios absents du cours, aucune correction
pendant la passation), envoyer et lire « x / 20 ». Vérifier que PR06, PR11, PR15, PR16, PR20 et
la théorie `/modules/ampcr` sont inchangés.

## 1. Réconciliation et prérequis

- Aucune branche, PR, rapport ni contenu PR24 avant cette session (worktree créé depuis
  `origin/develop` = `d4e4b9f`, SHA alors installé).
- **Numérotation** : la note du superviseur signalait un écart (« l'emplacement installé PR24
  est Hub, switch… »). Ce constat est **périmé** : l'audit #236 a réaligné le plan sur les
  tickets GitHub. Contrôle fait sur `origin/develop` : `_COURSE_ROWS` porte bien **PR24 =
  « Dépannage réseau et Internet — dossiers d'intervention écrits »** (ticket 200, module P4,
  exigences AP-32 et AP-37). Aucune autre unité touchée, aucune renumérotation.
- **Dépendances** #192 (socle, matrice, références officielles) et #236 (numérotation) :
  livrées et installées (statut « à tester »), suffisantes pour ce cours.
- **PDF officiel** : versionné par #192 (`docs/references-officielles/ampcr/2026-2027-1/`).
  Exigences utilisées, texte exact p. 6 : **AP-32** « Connexions et interventions en cas de
  panne internet. » et **AP-37** « Dépannage de problèmes simples d’accès au réseau. » Liens
  secondaires cités dans les exercices : AP-19 (débits/câbles), AP-25 et AP-27 (partages,
  permissions), AP-30 (adressage), AP-33 (Wi-Fi) ; compléments AP-C01 (rédaction) et AP-C03
  (protection des données).
- Séparation Théorie / Pratique écrite respectée : UAA PR24 dans le module `AMPCR-PRATIQUE`,
  banque et réserves `ampcr-pratique-pr24:practice` / `:exam` propres ; la théorie (module
  `AMPCR`, MC01–MC38) n'est pas modifiée, seulement citée par liens.

## 2. Ce qui a été livré

### Cours (`/uaa/ampcr-pratique-pr24`, 18 blocs, toute la matière 1 → 15 du ticket)

| Bloc | Contenu |
|---|---|
| Objectifs et place dans l'épreuve | 6 objectifs ; AP-32, AP-37 (texte exact) ; AP-C01, AP-C03 ; liens MC13, MC14, MC19, MC20, MC22, MC24, MC25, MC26, MC31, MC33 et PR15/PR20 ; réseau de référence |
| 1. Démarche en couches | symptôme exact, périmètre (un poste/tous, filaire/Wi-Fi, local/Internet), chronologie, changements récents, topologie ; ordre des couches ; hypothèse, tests non destructifs, preuve ; **corrélation ≠ preuve** |
| 2. Physique et liaison | cuivre/fibre, RJ45, voyants, port désactivé, prise brassée, carte activée, « Média déconnecté »/`NO-CARRIER`, alimentation, **PoE** (802.3af/at), vitesse/duplex, désaccord de duplex, **erreurs CRC**, blindage, 100 m, Auto MDI-X, radio ; « pas de lien = pas de diagnostic IP » ; page des ports du switch |
| 3-4. IP et DHCP | adresse, masque/CIDR, passerelle, table de routage, MAC, même sous-réseau, doublon, **APIPA** (indice, pas preuve), statique/réservation ; **DORA**, bail, options 3 et 6, absence de bail, étendue épuisée, mauvais pool, serveur arrêté, **relais**, second serveur, mauvaise option ; `ipconfig /all`, `/renew`, avertissement sur `/release` |
| 5. DNS | IP vs nom, nslookup/dig/resolvectl, réponse/NXDOMAIN/délai dépassé, **DNS interne vs public**, cache (`/displaydns`, `/flushdns`, `resolvectl flush-caches`), nslookup contourne cache et hosts |
| 6-7. Passerelle, routage, switch, VLAN | local → passerelle → distant ; tracert (étoiles intermédiaires non bloquantes) ; route par défaut ; mauvais masque ; routage inter-sous-réseaux ; NAT ; pare-feu, ACL, **ICMP filtré** ; table MAC, ports désactivés, mauvais VLAN, access/trunk en complément, « pas de VLAN supposé sans indice » |
| 8. Wi-Fi | SSID/BSSID, association, authentification WPA2/WPA3, clé, DHCP après association ; 2,4/5 GHz, canaux, interférences, répéteur ; **radio ≠ authentification ≠ IP** ; arbre Wi-Fi |
| 9. Partages et imprimantes | découverte du réseau, chemin UNC, 0x80070035, partage + NTFS (le plus restrictif), compte domaine/groupe de travail, identifiants mémorisés, SMB 445, `Test-NetConnection` ; file d'impression, port, spouleur ; arbre partage |
| 10-11. Outils | Windows : ipconfig, ping, tracert, nslookup, arp, route print, netstat/Get-NetTCPConnection, Test-NetConnection, netsh wlan — **lecture vs modification**, limites de ping ; Linux : ip addr/link/route/neigh, ping, traceroute/tracepath, dig, ss, journalctl, nmcli, resolvectl — **outils pas toujours présents** |
| 12. Procédure ordonnée | état physique → IP/masque → passerelle → IP distante → DNS → service, résultat attendu et branches ; **arbre général** (6 questions) ; relevé Linux sans lien |
| 13. Pannes combinées | 6 cartes **symptôme → causes possibles → test discriminant → résultat → action** (dont plusieurs à causes multiples) ; câble + DNS, masque + passerelle, DHCP intermittent, LAN OK/Internet KO, Internet OK/partage KO, Wi-Fi associé sans IP, lenteur intermittente |
| 14-15. Sécurité et rapport | autorisation, état initial, retour arrière, une modification à la fois, prévenir des coupures, **pas de scan non autorisé**, confidentialité des journaux ; rapport en 10 points (cause confirmée ou incertaine) |
| Exemples | **6 cas résolus** (constat, relevés, raisonnement, correction, validation, compte rendu) : APIPA (serveur qui ignore une carte non enregistrée) ; ping IP OK / nom interne KO (DNS du fournisseur) ; mauvais masque (/26, passerelle hors réseau, calculé) ; Wi-Fi connecté sans Internet (carte Wi-Fi en adresse fixe d'un autre réseau) ; LAN OK / Internet KO (ligne non synchronisée) ; imprimante inaccessible malgré le ping (spouleur arrêté) |
| Pièges | 13 erreurs fréquentes |
| Exercices corrigés (20) | cartes d'exercice avec documents, barème et corrigé replié |
| Mini-examen | mode d'emploi (10 × 2 pts, barème analytique, correction après envoi, nature IA de la proposition de correction) |
| Fiche mémo et glossaire | synthèse et 13 termes |
| Sources et compléments | consignes officielles, RFC 2131/2132/1542/3927/5737/3022/1918, IEEE 802.3/802.11/802.1Q, docs Microsoft et pages de manuel ; compléments signalés ; supports fictifs |

### Schémas et documents (13 figures SVG, `app/v1/ampcr_pratique_pr24_figures.py`)

Réseau de référence (`192.168.20.0/24` : box 192.168.20.1 avec NAT vers 203.0.113.45, switch
SW-01, SRV-01 DHCP+DNS 192.168.20.5, NAS 192.168.20.10, imprimante 192.168.20.20, AP PoE
192.168.20.30, postes DHCP de l'étendue 192.168.20.100–199) ; état des 10 ports du switch ;
procédure en couches ; arbres **général**, **Wi-Fi** et **partage** ; 7 documents fictifs :
`ipconfig /all` en APIPA, ping passerelle OK / IP distante KO, tracert arrêté après la box,
nslookup DNS du fournisseur vs DNS interne, journal dnsmasq (renouvellement accepté, carte
ignorée), `netsh wlan show interfaces` signal faible, `ip link`/`ip route` sans lien.

**Tous les relevés sont produits par code** à partir du réseau de référence (statistiques de
ping calculées, premier saut de tracert = passerelle, réponses DNS selon le statut, journaux
DHCP depuis les MAC des équipements, ARP, routes) ; les adresses publiques viennent des plages
de documentation RFC 5737 ; aucun schéma ne vient d'une image générée (pas d'appel à l'API
d'images : coût nul).

### Exercices et mini-examen (`app/v1/ampcr_pratique_pr24_bank.py`)

- **20 exercices corrigés** (affichés dans le cours, proposés dans « S'entraîner ») :
  **8 analyses de relevés** (VLAN invités, tracert avec étoiles, nslookup et faute de frappe,
  étendue DHCP épuisée, Wi-Fi faible, Linux NO-CARRIER, désaccord de duplex, doublon d'adresse
  de l'imprimante), **5 arbres ou procédures** (remise en ordre de la procédure, classement de
  8 observations par couche, arbre Wi-Fi à écrire, modification DHCP en production, tableau de
  diagnostic d'un partage), **4 dossiers multi-postes** (4 configurations à contrôler, 3
  utilisateurs et 3 refus d'accès, panne combinée câble + DNS, second serveur DHCP) et **3
  rapports** (intervention réussie, panne intermittente non reproduite, rapport bâclé à
  corriger). Chaque exercice : contexte complet, documents, consignes, barème analytique,
  corrigé justifié.
- **Mini-examen 10 questions /20** (2 points chacune, réponses libres, 5 avec documents) : port
  en VLAN « parking », PPP en échec après réinitialisation de la box, DNS injoignable, masque
  /28 (calculé), WPA3 seul et ancien portable, file d'impression sur l'ancienne adresse, Linux
  sans route par défaut, port 445 fermé sur le NAS, propositions dangereuses d'un collègue,
  compte rendu d'une étendue épuisée. Questions absentes du cours ; correction après envoi.
- Contexte de correction IA propre à PR24 (`_PR24_CONTEXT`) : notions autorisées, acceptation
  des démarches alternatives, erreurs toujours sanctionnées (APIPA ≠ preuve, ping par nom KO ≠
  panne Internet, ping sans réponse ≠ machine éteinte, VLAN sans indice, modification de
  production sans autorisation, réinitialisation de box, scan non autorisé…).

### Intégration (aucun nouveau moteur)

- `app/seed.py` : UAA PR24 (position 24) dans le module `AMPCR-PRATIQUE`, seed idempotent.
- `app/v1/ampcr_pratique_bank.py` : cours ajouté à `PRACTICAL_COURSES` (importeur de banque,
  réserves practice/exam, pas de génération IA, contexte de correction).
- Tests : `tests/test_ticket200_ampcr_pratique_pr24.py` (31 tests) ; comptage du seed
  (`test_admin_content_hierarchy.py`) et accueil PR20 (« cours publiés ») adaptés.
- Documentation : `docs/current_state.md`, `docs/ampcr_pratique_v1.md`, `docs/changelog.md`.

## 3. Vérifications effectuées

- `tests/test_ticket200_ampcr_pratique_pr24.py` : **31 passed** — réseau de référence sans
  erreur de plan (fixes hors étendue, étendue de 100 adresses), statistiques de ping relues,
  premier saut = passerelle, réponses DNS, journal DHCP, largeur ≤ 56 caractères de **toutes**
  les captures (figures et documents d'exercice), toute adresse IPv4 écrite valide et toute
  adresse publique dans les plages de documentation, calculs /26 et /28 recalculés
  indépendamment, figures accessibles (`role="img"`, titre, description, mention « schéma non
  officiel »), réponses auto-corrigées (classement, remise en ordre), absence d'affirmations
  fausses, matière 1-15 présente, 6 cas, tableaux complets, types de cartes des blocs, seed
  idempotent, banque et réserves, contexte de correction, page du cours, accueil « 6 cours
  publiés », matrice, sessions practice/exam sans génération IA, note sur 20.
- Tests du parcours pratique existants (#192 ×3, #193, #194, #197, #198, #199, #236) et
  `test_admin_content_hierarchy.py` : **verts**.
- **Suite complète** (le seed global est touché) : **2420 réussis, 0 échec** (18 min 47).
- `ruff check` sur tous les fichiers modifiés : aucune erreur.
- **Rendu réel** (Chromium headless sur la page servie par l'application de test) : aucun
  débordement horizontal à 390 px ni à 1280 px (le tableau des outils Windows débordait à
  390 px : converti en listes avant livraison) ; les 13 figures ont été relues en capture
  (deux libellés trop longs du schéma réseau raccourcis, ligne « port 1 » rattachée au switch).
- Installation : santé locale et publique, pages du cours / entraînement / examen / accueil /
  matrice en HTTP 200, compteurs utilisateurs/sessions/réponses non diminués (détail en
  section 7).

Non vérifié : correction IA réelle des réponses rédigées (les tests utilisent
`FakeAIProvider`) ; validation pédagogique par le propriétaire.

## 4. Choix techniques faits seul

1. **Emplacement PR24 conservé** : la numérotation définitive de #236 correspond au sujet du
   ticket ; la note « PR24 = Hub, switch… » est antérieure à #236.
2. **Un réseau de référence propre au cours** (« l'atelier », 192.168.20.0/24) plutôt que celui
   de PR20 : il faut un switch administrable (ports, VLAN, PoE), un NAS, une imprimante, un point
   d'accès et un réseau invités, absents de PR20. Le modèle `Host`/`AddressPlan` de PR20 est
   réutilisé pour les calculs et les contrôles de plan.
3. **Relevés générés par code**, au format réel des commandes (Windows en français, Linux en
   anglais) mais **simplifiés** (lignes ≤ 56 caractères, journaux sur deux lignes, tracert
   limité aux sauts utiles) et toujours étiquetés « capture fictive ».
4. **Adresses publiques fictives** prises dans les plages de documentation RFC 5737
   (203.0.113.45, 198.51.100.20, 198.51.100.53), jamais des adresses réelles.
5. **Serveur DHCP/DNS sous Linux (dnsmasq)** pour pouvoir montrer de vrais messages de journal
   (`no address available`, `ignored`) ; baux de 8 jours, ce qui explique dans les cas que les
   postes déjà configurés continuent de fonctionner.
6. **Six cas résolus distincts des exercices et de l'examen** (causes différentes pour chaque
   symptôme imposé : APIPA par carte ignorée, nom interne via DNS du fournisseur, masque /26,
   carte Wi-Fi en adresse fixe, ligne non synchronisée, spouleur) ; les mêmes symptômes
   reviennent dans les exercices avec d'autres causes (VLAN, étendue pleine, second DHCP,
   PPP…), pour entraîner le test discriminant plutôt que la mémorisation.
7. **Tableaux symptôme → action en cartes** (liste par symptôme) et outils en listes : un
   tableau à 5 colonnes est illisible à 390 px (même choix que la correction de PR16).
8. **Désaccord de duplex** : compteur d'erreurs générique dans la page des ports (collisions
   tardives côté half duplex, CRC côté full duplex) ; câble écrasé modélisé en 100 Mb/s full
   avec erreurs CRC (repli de vitesse), pas en half duplex.
9. **Pas de génération d'image par API** : les supports utiles ici sont des schémas et des
   relevés exacts, que l'API ne doit pas produire (consigne #192) ; aucune mise en situation
   illustrée n'apportait de valeur suffisante.
10. **VLAN, trunk/access, relais DHCP, protection DHCP du switch** présentés comme
    **compléments** (non exigés explicitement par la liste officielle), conformément au ticket.

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Éléments restant à réaliser

- Validation pédagogique et visuelle par le propriétaire (statut matrice AP-32 / AP-37 :
  « partiel » jusqu'à validation explicite).
- Suites prévues par la file (non traitées ici) : PR25 Wi-Fi (#224) approfondira le Wi-Fi,
  PR23 (#223) les partages et permissions, PR29 (#228) le rapport d'intervention, EX04/EX05
  (#233, #201) pourront réutiliser le réseau de référence et les générateurs de relevés de PR24.
- Amélioration repérée, non implémentée (hors périmètre) : dans l'arbre de décision partagé
  (`decision_tree_svg`, utilisé aussi par PR06/PR11/PR20), l'étiquette « NON » chevauche
  légèrement la pointe de la flèche ; lisible, mais pourrait être décalée dans un ticket de
  finition graphique.

## 7. Installation

Sous verrou : sauvegarde `jury_central-pre-ticket200-20261026-214054.db` (état de
production intact : copie de travail propre, branche `develop`) ; `d4e4b9f` → `8cd5126` ;
`pyproject.toml` inchangé ; seed idempotent (1 UAA PR24 + 18 blocs ; les 52 blocs FSE recréés à
l'identique, comportement existant déjà signalé au ticket #199) ; services `jury-central` et
`jury-central-correction-worker` actifs ; `/health` OK en local et en public ; cours PR24,
`/ampcr-pratique` (« 6 cours publiés »), matrice, PR20 et `/modules/ampcr` en 200
(practice/exam : 303 vers la connexion, attendu) ; 13 figures présentes sur la page servie ;
compteurs 18 comptes / 81 sessions / 638 réponses inchangés.
