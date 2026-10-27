# Ticket #234 — [AMPCR pratique EX06] Examen blanc global avancé — dossiers complexes

- Ticket : https://github.com/ReC82/jury-central/issues/234
- **État réel : Installé — à tester**
- SHA installé : `3f4bcc5c5c16c123f0fd92dd779cc70cef5085c6` (fusion de la PR #323 dans `develop`)
- Date : 2026-10-27 (session jcorch autonome)

## 1. Résultat

L'**examen blanc global avancé EX06** du parcours **Informatique AMPCR → Pratique écrite** est
publié, juste après EX05 (fin de parcours). L'emplacement EX06 du plan installé
(`_EXERCISE_ROWS`, numérotation #236 : « EX06, ticket 234 ») porte bien le sujet du ticket :
aucun écart, aucun autre cours ni examen modifié. Module `AMPCR-PRATIQUE` uniquement : Théorie
(MC) et Pratique restent séparées (banques, sessions, progression).

### Ce que voit le candidat

- **Page « Sujet »** (`/uaa/ampcr-pratique-ex06`), version candidat **sans aucun corrigé**,
  13 séquences : présentation (ce qui est évalué, deux variantes, notation /100 avec répartition
  par dossier, barème analytique, corrigé après remise, durée conseillée 4 h donnée comme repère
  et **non comme durée officielle**, version A4, barème global, **couverture comparée avec EX05**,
  exigences évaluées et non évaluées), puis pour chaque variante : documents communs (fiche du
  client, **schéma du réseau**, inventaire) et **dossiers A, B, C, D** avec leurs documents et
  questions ; méthode ; sources et supports fictifs. À l'impression : 12 lignes de réponse par
  question, chaque variante sur une nouvelle page.
- **Examen blanc** (`/uaa/ampcr-pratique-ex06/exam`) : **12 questions**, une par écran, dans
  l'ordre du sujet, avec repère « Variante n », documents, consignes numérotées et points ;
  sauvegarde automatique et reprise ; barème et corrigé invisibles avant la remise ; note /100,
  corrigé détaillé, « Imprimer / PDF ». Le sélecteur « Nombre de questions » propose **12**.
- **Variantes** : chaque session sert une variante entière — Atelier d'architecture Morel
  (Liège, 192.168.50.0/25) la première fois, puis Imprimerie Dufour (Charleroi, 10.20.0.0/24),
  puis la moins faite.

### Les 4 dossiers, 12 situations (8 ou 9 points, 4 critères chacune)

| N° | Dossier | Situation | Pts | Variante 1 | Variante 2 |
|---|---|---|---|---|---|
| 1 | A | Poste qui ne démarre plus : départager les causes | 9 | INACCESSIBLE_BOOT_DEVICE : contrôleur passé en RST par le neveu (faux indice : mise à jour) → remettre AHCI | No bootable device : disque invisible partout, cliquetis → mort ; pile 2,41 V usée (indice secondaire) |
| 2 | A | Stockage : supports et entretien | 8 | HDD 4 To : GPT (MBR perdrait ≈ 1,64 Tio), 3,64 « To » affichés ; clé exFAT (fichier 6,4 Gio) ; pas de défragmentation du SSD | SSD système 2 To : GPT, 1,82 « To » ; clé FAT32 (appareil ancien, 0,35 Gio) |
| 3 | A | Données : 3-2-1, intégrité, opération qui efface | 8 | 3 manques 3-2-1 ; empreinte différente → recopier ; effacement sécurisé avant don | 2 manques ; fichier absent de la copie ; reformatage du disque externe |
| 4 | B | Devis : compatibilité et puissance | 9 | DDR4 sur carte DDR5, ventirad 165/160 mm, bloc 650 W < 750 W (533 W + 30 %) | socket LGA1851/LGA1700, ATX en boîtier microATX, carte 336/320 mm, 1 PCIe 8 broches sur 2 (464 W → 700 W) |
| 5 | B | Windows 11 : blocage et activation | 8 | « aucun lecteur » : pilote VMD (faux indice : SSD défectueux) ; Famille installée sur licence Pro → non activé | disque MBR : sauvegarde D:, mbr2gpt (conseil « mode hérité » refusé) ; licence numérique → activé |
| 6 | B | Double démarrage Linux | 8 | conditions réunies ; swap 4 Go ; image OK ; BootOrder Windows d'abord → efibootmgr -o | copie non relue + accord oral → arrêt ; image FAILED ; swap 8 Go ; aucune entrée ubuntu |
| 7 | C | Cordon RJ45 : lien dégradé | 8 | broche 8 ouverte → 100 Mb/s (faux indice : Cat5e) | paires séparées invisibles au testeur, NEXT en échec, CRC |
| 8 | C | Segment coaxial et câble BNC | 9 | 25 Ω (terminaisons bonnes) ; T en dérivation + 192 m > 185 m | 50 Ω partout → coupure ; tronçon de 22 m ouvert mesuré seul |
| 9 | D | Agrandir le réseau IPv4 | 9 | 180 hôtes → /24 ; étendue de 57 pour 64 appareils (APIPA) ; imprimante fixe dans l'étendue | 400 hôtes → /23 (diffusion 10.20.1.255) ; masque /24, passerelle erronée |
| 10 | D | Wi-Fi : couverture, canal, sécurité, extension | 8 | canal 11 ; WPA/TKIP, WPS, mot de passe d'usine ; point d'accès câblé 72 Mb/s vs répéteur 36 | canal 1 ; WEP, SSID masqué, 40 MHz, 2 DHCP ; 52 vs 26 Mb/s |
| 11 | D | Partage et NTFS : héritage, refus | 8 | héritage désactivé sur Concours → NTFS bloque ; refus explicite G_Stagiaires | partage « Tout le monde : Lecture » limite (fonctionne en local sur le serveur) |
| 12 | D | Rapport de la journée | 8 | 385 min facturables, amplitude 7 h 10, pause 45 min | 405 min, amplitude 7 h 35, pause 50 min |

Répartition : A 25, B 25, C 17, D 33 = 100. Les 13 exigences prévues pour EX06 dans le plan
(AP-03, 10, 15, 16, 17, 25, 27, 30, 33, 34, 35, C01, C03) sont évaluées ; matrice inchangée
(aucune exigence déclarée « validée »).

### Fichiers

- `app/v1/ampcr_pratique_ex06_figures.py` — 2 variantes ; chaque valeur et verdict calculé par
  les fonctions **des cours** (PR02 `check_configuration`/`recommended_psu`, PR05
  `partition_table_choice`/`filesystem_for`/`tb_to_tib`, PR08 `activation_result`, PR09
  `swap_advice`/`checksum_verdict`/`dual_boot_action`/`first_boot_entry`, PR15 `split_pairs`,
  PR16 `bus_errors`/`ohmmeter_reading`, PR20 `smallest_prefix_for`/`plan_errors`, PR23
  `effective_access`, PR25 `received_dbm`/`best_channel_24`/`audit_config`/`repeater_mbps`, PR28
  `check_321`/`compare_copy`/`required_prerequisites`) + `boot_diagnosis` et `negotiated_speed`
  ; schémas SVG (réseau et Wi-Fi).
- `app/v1/ampcr_pratique_ex06_bank.py` — 25 documents numérotés par variante, 12 situations,
  validation, comparaison avec EX05.
- `app/v1/ampcr_pratique_ex06_course.py` — 13 blocs de la page du sujet.
- `app/static/img/ampcr-pratique/ex06-v{1,2}-plan-{reseau,wifi}.svg`.
- `app/v1/ampcr_pratique_bank.py` — EX06 déclaré (contexte de correction propre, variantes) ;
  `exam_variant_length`.
- `app/v1/session_service.py` — `session_length_options` : pour un examen à variantes, une seule
  longueur = celle d'une variante (EX06 : 12 ; EX05 : 10, inchangé).
- `app/seed.py` — `_seed_uaa(…, "EX06", …, position 30)` après EX05 (additif).
- `tests/test_ticket234_ampcr_pratique_ex06.py` (33 tests) ; comptages
  `tests/test_admin_content_hierarchy.py` ; motif « 5 examens blancs » assoupli dans le test EX05.
- `docs/current_state.md`, `docs/ampcr_pratique_v1.md`, `docs/changelog.md`.

## 2. Liens pour tester

- Sujet : https://jury-central.lodylands.com/uaa/ampcr-pratique-ex06
- Examen blanc (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-ex06/exam
- Accueil du parcours : https://jury-central.lodylands.com/ampcr-pratique
- Schémas : https://jury-central.lodylands.com/static/img/ampcr-pratique/ex06-v1-plan-reseau.svg,
  https://jury-central.lodylands.com/static/img/ampcr-pratique/ex06-v1-plan-wifi.svg,
  https://jury-central.lodylands.com/static/img/ampcr-pratique/ex06-v2-plan-reseau.svg,
  https://jury-central.lodylands.com/static/img/ampcr-pratique/ex06-v2-plan-wifi.svg

Procédure courte : parcourir les 13 séquences du sujet ; aperçu avant impression (Ctrl + P) ;
lancer l'examen blanc (12 questions, variante 1), répondre à quelques questions, quitter,
reprendre, remettre ; vérifier note /100, barème et corrigé ; relancer : variante 2.

## 3. Vérifications effectuées

- `tests/test_ticket234_ampcr_pratique_ex06.py` : **33 passed** — valeurs recalculées
  indépendamment (ipaddress pour /24 et /23, Go/Gio et limite MBR, budget de puissance et palier,
  signal Wi-Fi par la formule en dur, 25/50 Ω, durées), causes départagées (contrôleur / disque
  mort), matrices d'accès écrites en dur + correction de la variante 2 vérifiée, captures ≤ 56
  caractères, schémas valides, accessibles, sans verdict ni signal reçu, fichiers statiques
  identiques ; 24 questions, 100 points par variante, structure identique et données
  différentes, **aucune question reprise d'EX05**, documents cités fournis, réponses absentes des
  énoncés ; sujet sans corrigé (24 zones de réponse) ; seed idempotent (EX06 juste après EX05) ;
  réserve `exam` seule ; contexte de correction propre ; longueurs (EX06 12, EX05 10, EX04
  inchangé) ; **sessions : 1ʳᵉ = variante 1 (12 questions dans l'ordre, corrigé masqué, schémas
  réseau et Wi-Fi), note /100 ; 2ᵉ = variante 2**.
- Tests liés (EX01–EX05, PR30, #86, #151, #192, #236, #299, hiérarchie admin) : 320 passed.
- **Suite complète : 3334 passed** (une exécution, 28 min 33 ; moteur de sessions et seed touchés).
- `ruff check` : fichiers créés et modifiés sans nouvelle erreur (une erreur d'ordre d'imports
  préexistante dans `tests/test_ticket201_ampcr_pratique_ex05.py`, lignes non modifiées).
- Visuel (navigateur sans interface) : les 4 schémas contrôlés (un défaut de cadre du plan Wi-Fi
  corrigé avant livraison) ; capture de la page publiée à 1 280 px.
- Installation : arbre propre sur `develop`, sauvegarde
  `~/.local/state/jury-central-orch/backups/jury_central-pre-ticket234-20261027-232323.db`,
  fast-forward `2304e92 → 3f4bcc5`, `pyproject.toml` inchangé, seed idempotent (1 UAA ; 65 blocs
  = 13 blocs EX06 + le remplacement habituel des 52 blocs FSE), redémarrage des deux services
  (actifs), `/health` local et public OK ; sujet, EX05, accueil, matrice, 4 SVG en HTTP 200
  (examen : 303 vers la connexion, normal) ; sujet servi avec 24 questions et aucun corrigé ;
  accueil « 6 examens blancs sur 6 ». Compteurs utilisateurs/sessions/réponses inchangés
  (18 / 84 / 668).

Non effectué : validation pédagogique humaine ; correction réelle par l'IA (tests avec
`FakeAIProvider`) ; contrôle de l'impression PDF page par page.

## 4. Choix techniques faits seul

- **12 questions** (fourchette 12–16 du ticket) sur **4 dossiers** (fourchette 3–4), de 8 ou
  9 points pour totaliser 100 ; un seul client par variante (journée de maintenance) pour que les
  documents communs (fiche, schéma, inventaire) servent à tous les dossiers.
- **Mêmes mécanismes qu'EX05** (variante entière par session, ordre du sujet). Seul ajout au
  moteur : la longueur proposée au démarrage est celle de la variante (sinon l'écran annonçait
  « 10 » pour 12 questions servies) ; EX05 et les autres parcours sont inchangés (suite complète).
- **Faux indices** toujours réfutables par une donnée fournie (SMART bon, SSD listé, lien
  certifié, terminateurs mesurés seuls…), jamais trompeurs.
- **Pas d'image générée** : schémas et valeurs exacts construits sur des données testées.
  Adresses privées RFC 1918 et publiques de documentation RFC 5737.
- **Durée conseillée 4 h** : repère personnel, pas la durée officielle.

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Éléments restant à réaliser

- Validation pédagogique et visuelle par le propriétaire (sujet, impression, correction réelle).
- Suite de la file : audit final de couverture et qualité (#235), maintenant que les 30 cours et
  les 6 examens blancs sont publiés.

## Notification

L'email de livraison est envoyé par le superviseur jcorch à la fin de la session, avec ce rapport
en pièce jointe (copie dans `~/.local/state/jury-central-orch/reports/`).
