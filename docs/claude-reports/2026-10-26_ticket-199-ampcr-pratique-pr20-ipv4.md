# Ticket #199 — [P0][AMPCR pratique PR20] IPv4, MAC, masques et passerelles — configuration et diagnostics écrits

Ticket : [#199](https://github.com/ReC82/jury-central/issues/199) · branche `feature/199-pr20-ipv4` · PR [#249](https://github.com/ReC82/jury-central/pull/249)

**État réel : Installé — à tester.**

**SHA installé : `5534db5`** (merge de la PR [#249](https://github.com/ReC82/jury-central/pull/249) sur `develop`, 26/10/2026).

## Liens pour tester

- Cours : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr20
- S'entraîner (20 exercices, 10 tirés par session, correction après envoi) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr20/practice
- Examen blanc (mini-examen 10 questions, note /20) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr20/exam
- Accueil du parcours (« 5 cours publiés ») : https://jury-central.lodylands.com/ampcr-pratique
- Matrice (AP-30 passe « partiel ») : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte : se connecter ; ouvrir le cours sur téléphone puis sur PC (séquences ou
« Afficher tout le cours sur une page ») ; vérifier le schéma du réseau de référence (4 postes,
switch, routeur, serveur DHCP/DNS, adresses et MAC), la structure de la MAC, les trois
décompositions en bits (/24, /26, /27), l'échange DORA, les captures fictives `ipconfig /all`,
`ip addr`/`ip route` et la fenêtre « Protocole Internet version 4 », la démarche de ping et les
**trois arbres** (« ping IP OK, nom KO », « APIPA », « deux machines ne communiquent pas ») ;
lire les **cinq cas résolus** ; ouvrir quelques corrigés ; lancer « S'entraîner » (3 classements
et une remise en ordre corrigés automatiquement), puis « Examen blanc » (10 questions absentes du
cours, aucune correction pendant la passation), envoyer et lire « x / 20 ». Vérifier que PR06,
PR11, PR15, PR16 et la théorie `/modules/ampcr` sont inchangés.

## 1. Réconciliation et prérequis

- Aucune branche, PR, rapport ni contenu PR20 avant cette session (worktree créé depuis
  `origin/develop` = `b2d5369`).
- **Numérotation** : la note du superviseur et le premier tableau de la spec signalaient un
  écart (« PR20 installé = câble BNC »). Ce tableau est **périmé** : l'audit #236 a réaligné le
  plan sur les tickets GitHub. Contrôle fait sur `origin/develop` : `_COURSE_ROWS` porte bien
  **PR20 = « IPv4, MAC, masques et passerelles — configuration et diagnostics écrits »**
  (ticket 199, module P4, exigence AP-30) ; le BNC est en PR16 (#198). Aucune autre unité
  touchée, aucune renumérotation.
- **PDF officiel** : versionné par #192 (`docs/references-officielles/ampcr/2026-2027-1/`).
  Exigence utilisée, texte exact p. 6 : **AP-30** « L’adressage IP, les adresses MAC,
  l’identification d’une adresse MAC et d’une adresse IP. » Liens secondaires cités dans les
  exercices : AP-28 (connexion directe), AP-31 (passerelle/routeur), AP-32 (panne Internet),
  AP-37 (dépannage d'accès), AP-38 (mini-réseau), AP-11 (commandes), AP-25 (partage
  d'imprimante) ; complément AP-C01.
- Modèle d'intégration repris de PR06/PR11/PR15/PR16 (aucun moteur concurrent).

## 2. Ce qui a été livré

### Cours (`/uaa/ampcr-pratique-pr20`, 16 blocs, toute la matière 1 → 15 du ticket)

| Bloc | Contenu |
|---|---|
| Objectifs et place dans l'épreuve | 6 objectifs ; AP-30 (texte exact) ; AP-C01 ; liens vers la théorie MC16–MC20 |
| 1. Réseau local | carte/interface, liaison Ethernet/Wi-Fi, switch, routeur, passerelle, DHCP, DNS, box ; **physique vs logique** ; schéma de référence |
| 2. MAC | 48 bits, hexadécimal, OUI, unicité administrative, MAC aléatoires/virtuelles (bit U/L), relevé (ipconfig /all, getmac, ip link, arp -a, ip neigh) et limites ; MAC ≠ IP, MAC ≠ identité |
| 3. IPv4 | 32 bits, 4 octets 0-255, décimale pointée, réseau/hôte, unicast, réseau, diffusion, RFC 1918, 127.0.0.1, 169.254/16 APIPA, 0.0.0.0 ; classement calculé de 8 adresses dont les pièges 172.32 et 192.169 |
| 4-5. Masque et CIDR | masque contigu, ET logique, diffusion, plage, total vs hôtes usuels ; /24 /25 /26 /27 /28 /30 + compléments /31 /32 ; figures /24 /26 /27 ; conversion masque ↔ préfixe ; comparaison de deux postes |
| 6-8. Passerelle, DNS, DHCP | route locale vs par défaut, passerelle dans le réseau, passerelle ≠ DNS ; tests par nom vs IP ; DORA (figure), bail, options, statique/dynamique, réservation, APIPA comme symptôme |
| 9-10. Commandes | Windows : ipconfig, /all, /release, /renew, /flushdns, ping, tracert, nslookup, arp -a, route print (lecture vs modification) ; capture fictive de la fenêtre IPv4 ; Linux : ip addr, ip route, ip neigh, ping -c, resolvectl si présent, temporaire vs persistant (NetworkManager, Netplan), pas de commande universelle |
| 11-12. Plan et connexion directe | démarche en 5 étapes, plan de référence contrôlé ; deux PC en direct, Auto MDI-X, pas de passerelle, pare-feu |
| 13-14. Diagnostic | démarche lien → relevé → 127.0.0.1 → propre IP → passerelle → IP distante → nom ; ICMP filtré ; constat/hypothèse/test/résultat/action ; 3 arbres ; 11 cas d'erreur du ticket |
| 15. Compte rendu | contexte, avant/après, commandes et observations, hypothèses, corrections, validation, risques |
| Exemples (5 cas) | sous-réseaux différents ; APIPA ; DNS erroné ; masque incorrect ; doublon IP |
| Pièges (13), Exercices (20), Mini-examen /20, Fiche mémo + glossaire, Sources et compléments | encadrés « À retenir », « Piège fréquent », « Méthode examen » dans les blocs |

### Visuels (13 figures SVG, aucune image générée)

Réseau de référence (4 postes, switch, routeur, serveur DHCP/DNS, adresses et MAC) ; structure
de la MAC (bits I/G et U/L calculés) ; décompositions en bits de 192.168.10.77 en /24, /26 et
/27 (adresse, masque, ET = réseau, diffusion) ; DORA ; captures fictives `ipconfig /all`,
`ip addr` + `ip route` et fenêtre « Protocole Internet version 4 » ; démarche de ping ; arbres
« ping IP OK, nom KO », « APIPA », « deux machines ne communiquent pas ». **Tout est produit par
un modèle de données** (`Host`, `AddressPlan`) et le module standard `ipaddress` : les adresses
du schéma, les bits, les sorties de commandes, les corrigés et les réponses auto-corrigées
viennent des mêmes fonctions. Largeur 380 px, texte alternatif complet, légende, « schéma non
officiel », information jamais portée par la seule couleur.

### Exercices et mini-examen

- 20 exercices (ticket : ≥ 18) : **7 calculs** (≥ 6 : masques ↔ préfixes, réseau/diffusion/plage
  de 4 postes, types d'adresses, même réseau ou routeur, masques différents, taille des
  sous-réseaux, ET logique en binaire), **5 diagnostics sur relevés** (≥ 5 : APIPA, DNS erroné,
  Linux sans route par défaut, mauvaise passerelle, doublon IP), **4 configurations** (≥ 4 : plan
  d'un cabinet, plan erroné à relire, connexion directe, adresse fixe Windows/Linux), **4
  comptes rendus ou procédures** (≥ 3 : démarche à remettre en ordre, compte rendu d'une erreur
  de masque, adresse stable d'une imprimante, identification MAC et limites). 3 classements et 1
  remise en ordre corrigés localement ; les autres avec barème analytique, réponses
  équivalentes acceptées.
- Mini-examen : 10 questions à réponse libre (2 pts, /20), barème analytique, absentes du cours,
  variées (calculs, relevés Linux/Windows, plan, connexion directe, compte rendu), aucune
  question de développé de sigle.

### Intégration (moteur existant, aucune table, aucune migration)

`app/v1/ampcr_pratique_pr20_{figures,bank,course}.py` ; PR20 ajouté à `PRACTICAL_COURSES` avec
son contexte de correction (refus de « 172.32.x.x est privée », « APIPA = DHCP en panne », « nom
KO = Internet en panne », filtrage MAC comme sécurité, commande Linux universelle…) ; seed
idempotent `_seed_uaa(…, "PR20", …)`. Docs : `current_state.md`, `ampcr_pratique_v1.md`,
`changelog.md`.

## 3. Vérifications

- `tests/test_ticket199_ampcr_pratique_pr20.py` : 41 tests — **calculs IPv4 recalculés
  indépendamment** (arithmétique entière, sans `ipaddress`) et comparés à 9 cas écrits à la main
  (/24, /25, /26, /27, /28, /30) ; masques ↔ préfixes et masques non contigus refusés ; /31 et /32 ;
  types d'adresses (dont 172.32, 172.15, 192.169) ; même sous-réseau ; taille des blocs ; bits
  I/G et U/L ; plan de référence sans erreur ; chaque faute de plan détectée (réseau, diffusion,
  doublon, adresse fixe dans l'étendue, masque, passerelle hors réseau) ; sorties `ipconfig`,
  `ip addr`, `ip route` cohérentes avec la configuration et lisibles (≤ 56 caractères) ; figures
  calculées (réseau, bits, captures, arbres), valides et accessibles ; **toutes les adresses
  IPv4 écrites dans le cours et la banque sont valides** (sauf le contre-exemple volontaire
  192.168.10.256) ; nombres d'exercices par type ; réponses auto-corrigées justes ; 5 cas ;
  examen absent du cours ; matière 1-15 ; types de cartes ; seed idempotent ; import et
  réserves ; contexte de correction ; page ; accueil « 5 cours publiés » ; sessions
  practice/exam sans génération ; note /20 ; deux sessions d'entraînement soumises.
- Tests adaptés : PR16 (« cours publiés » sans nombre figé), comptage du seed (+1 UAA, +16 blocs).
- Tests ciblés AMPCR pratique (#192, #193, #194, #197, #198, #199, #236, hiérarchie) : 259 réussis.
  **Suite complète : 2389 réussis, 0 échec** (19 min 36). `ruff check` propre sur les fichiers touchés.
- Installation (sous verrou) : sauvegarde `jury_central-pre-ticket199-20261026-205224.db` ;
  `b2d5369` → `5534db5` ; `pyproject.toml` inchangé ; seed (1 UAA + 16 blocs ; les 52 blocs FSE
  recréés à l'identique, comportement existant) ; services actifs ; `/health` OK local et
  public ; PR20, PR16, PR15, PR11, PR06, `/ampcr-pratique` (« 5 cours publiés sur 30 prévus »),
  matrice, `/modules/ampcr`, `/` en 200 (practice/exam : 303 vers la connexion, attendu) ;
  compteurs 18 comptes / 81 sessions / 638 réponses inchangés.
- **Rendu réel** (Chromium sur la page servie, toutes les séquences dépliées) : aucun
  débordement de page à 390 px ni à 1280 px ; figures relues en capture (réseau, MAC, bits,
  DORA, captures, arbres).
- **Non vérifié** : qualité réelle de la correction IA (tests avec `FakeAIProvider`) ; vrai
  téléphone ; impression A4 non générée (mêmes styles que les cours précédents).
- **Limites connues** : le tableau du plan d'adressage de E14 (6 colonnes) défile dans son cadre
  à 390 px (style partagé des documents d'exercice) ; les encadrés « > » (« À retenir »,
  « Piège fréquent », « Méthode examen ») prennent l'habillage commun des citations du site
  (étiquette « Attention »), comme en PR16.

## 4. Choix techniques faits seul

1. **Calculs par le module standard `ipaddress`** (pas le validateur #68, conçu pour des
   questions générées) : un modèle `Host`/`AddressPlan` produit valeurs, schémas, captures,
   corrigés et réponses auto-corrigées ; les tests recalculent tout **indépendamment** (arithmétique
   entière) et contre des valeurs écrites à la main.
2. **Réseau de référence unique** (192.168.10.0/24, passerelle .1, DHCP/DNS .5, étendue
   .100–.199) réutilisé par le schéma, les captures, les cas et plusieurs exercices ; adresse
   publique fictive prise dans la plage de documentation RFC 5737 (203.0.113.45).
3. **Captures simplifiées** (points de suite raccourcis, lignes ≤ 56 caractères pour rester
   lisibles à 390 px), signalées « capture fictive — présentation simplifiée ».
4. **Linux persistant** : NetworkManager (`nmcli`) donné en exemple, Netplan cité, avec la règle
   « pas de commande universelle » (exigence du ticket).
5. **/31 et /32** traités en compléments ; DHCP, DNS, commandes et bits I/G-U/L signalés comme
   compléments utiles à AP-30.
6. **Aucune image générée par API** (coût 0) et aucune nouvelle bibliothèque.
7. Matrice : AP-30 passe « partiel » ; `VALIDATED_REQUIREMENT_IDS` reste vide (validation par
   le propriétaire).

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Reste à réaliser / suites proposées

- Validation pédagogique et visuelle par le propriétaire.
- PR21 (#221, connexion directe et mini-réseau) et PR24 (#200, dépannage réseau et Internet)
  peuvent réutiliser `Host`, `AddressPlan`, `plan_errors`, `ipconfig_all_lines`,
  `ip_addr_lines`, `ip_route_lines` et les arbres de diagnostic sans dupliquer les sections
  3-8 ; EX04 (#233) peut tirer ses calculs du même modèle.
- Limite connue (déjà signalée en PR15/PR16, hors périmètre) : les tableaux de documents
  d'exercice larges (plan d'adressage à 6 colonnes de E14) défilent dans leur cadre à 390 px ;
  une mise en page empilée de `_table_html` profiterait à tous les cours pratiques.
