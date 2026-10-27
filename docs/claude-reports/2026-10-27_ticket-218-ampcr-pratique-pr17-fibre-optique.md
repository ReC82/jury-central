# Ticket #218 — [AMPCR pratique PR17] Fibre optique — choix, raccordement et diagnostic

- Ticket : https://github.com/ReC82/jury-central/issues/218
- **État réel : Installé — à tester**
- SHA installé : `f060fa2cc13f24b9d6e17b64e9625a1dca42fd62` (fusion de la PR #281 dans `develop`)
- Date : 2026-10-27 (session jcorch autonome)

## 1. Résultat

Le cours **PR17 « Fibre optique — choix, raccordement et diagnostic »** est publié dans le
parcours **Informatique AMPCR → Pratique écrite** (module `AMPCR-PRATIQUE`). Il est séparé de la
théorie MC : son cours, sa banque, son examen et sa progression sont distincts. Le seul lien vers
la théorie renvoie à MC15. PR17 occupe la position 17 de l'ordre pédagogique : après PR16, avant
PR20 (PR18 et PR19 ne sont pas encore publiés).

**Numérotation vérifiée** : dans le plan installé (`_COURSE_ROWS`, numérotation définitive de
#236), l'emplacement PR17 porte bien le sujet du ticket (« PR17, ticket 218, Fibre optique —
choix, raccordement et diagnostic », exigences officielles AP-21 et AP-22). Aucun écart, aucun
autre cours touché ni renuméroté.

### Contenu (18 blocs)

**11 chapitres de théorie**, chacun avec objectifs, théorie, procédure professionnelle à rédiger,
erreur fréquente, attendu « à l'écrit », repère rapide et renvoi aux exercices liés :

1. **Principe** : cœur et gaine (125 µm), indice plus faible de la gaine, réflexion totale ;
   revêtement 250 µm, aramide ; lumière infrarouge invisible ; aucun courant (parasites,
   isolation électrique).
2. **Monomode ou multimode** : cœurs 9 / 50 / 62,5 µm, dispersion modale ; tableau OM1–OM4 et
   OS2 (longueurs d'onde, couleur habituelle de gaine et de connecteur, le marquage fait foi) ;
   **portée selon le module et la fibre** (1000BASE-SX/LX, 10GBASE-SR/LR, valeurs de PR14).
3. **Connecteurs** LC (1,25 mm), SC et ST (2,5 mm) ; polissage UPC / APC 8° (jamais APC sur
   UPC) ; choix des jarretières.
4. **Modules SFP (1 Gb/s) et SFP+ (10 Gb/s)** ; mêmes modules aux deux bouts, famille de la
   fibre, module reconnu ; **TX/RX, duplex, polarité** et correction d'une inversion (croiser à
   une seule extrémité).
5. **Pertes et puissance reçue** : calcul de PR14 ; reçue = émise − perte ; perte d'un sens ;
   plage de la fiche (sensibilité, maximum), LOS, saturation.
6. **Raccordement** : épissure par fusion (≤ 0,3 dB), épissure mécanique (complément), pigtail,
   tiroir, cassettes, traversées, brassage ; chaîne complète chiffrée.
7. **Pose** : rayon de courbure (10 × Ø au repos, 20 × au tirage, convention du cours), traction
   par l'aramide, attaches non serrées, love, étiquettes ; procédure de pose et de contrôle.
8. **Fibre, cuivre ou coaxial** : tableau comparatif (débit, longueur, parasites, isolation,
   PoE, raccordement, coût, fragilité) et règles de choix.
9. **Contrôle** : inspecter-nettoyer-inspecter ; photométrie (référence, perte = référence −
   lecture) ; réflectométrie OTDR au niveau technicien (bobine amorce, pente, connecteur,
   épissure, courbure plus forte à 1 550 nm, fin ou cassure ; distance) ; stylo laser rouge.
10. **Sécurité** : lumière laser invisible (ne jamais regarder, photomètre, capuchons, sonde
    d'inspection fibre déconnectée) ; éclats de fibre (tapis sombre, lunettes, récipient fermé,
    ruban adhésif, ni manger ni boire).
11. **Diagnostic** : tableau des cinq causes (symptômes, correction) et démarche.

**3 procédures illustrées** : inspecter, nettoyer, inspecter un connecteur ; poser et contrôler
une liaison optique ; diagnostiquer une liaison optique sans lien.

**5 cas résolus** (demandés par le ticket) : **lien inversé** (LOS des deux côtés, fibres bonnes
à 1,9 et 2,0 dB ≤ 2,42 dB → polarité) ; **connecteur sale** (7,7 dB de trop, sous la
sensibilité → nettoyage) ; **mauvais module** (SR face à LR sur OS2 : deux erreurs) ; **distance**
(1000BASE-SX sur 420 m d'OM1 : perte 2,97 dB correcte mais portée de 275 m dépassée) ; **casse**
(trace OTDR qui s'arrête à 562 m avec 150 m d'amorce → cassure à 412 m, budget après réparation
2,96 dB).

Puis **pièges**, **fiche mémo et glossaire**, **sources et compléments**.

**18 exercices corrigés** (le ticket en demande au moins 16), chacun avec contexte, consignes,
barème et corrigé :
- **3 remises en ordre** : nettoyage d'un connecteur, pose et contrôle, diagnostic ;
- **5 classements auto-corrigés** : puissance reçue face à la fiche (8 relevés), événements OTDR
  (7), compatibilité module / fibre / distance (8), famille de fibre d'après gaine et marquage
  (8), cause probable d'une panne (7) ;
- **6 analyses de documents** : rapport de photométrie de 4 fibres, trace OTDR (cassure),
  puissances des modules (un sens perd trop), choix d'un module et bilan, commande de
  jarretières (OM4, SC/APC – LC/UPC), rapport de chantier (rayons de courbure) ;
- **4 rédactions** : sécurité laser, éclats de fibre, fibre ou cuivre pour un atelier de
  soudure, pigtail et épissure expliqués au client.

**Mini-examen de 10 questions /20** (2 points chacune, réponses libres, onglet « Examen blanc »,
jamais affiché dans le cours) : lien neuf sans lien (polarité), erreurs sur liaison courte
(connecteur sale), lien coupé après échange de switch (mauvais module), 10 Gb/s sur OM2
(distance), localiser une cassure, recette au photomètre, rangement d'un câble (rayon), règles de
sécurité, imagerie d'un hôpital (fibre ou cuivre), module longue portée sur liaison courte
(saturation, atténuateur).

**9 schémas SVG** produits depuis des données testées : coupe à l'échelle (OM1, OM3, OS2) et
trajet de la lumière ; connecteurs (férules à l'échelle relative, faces UPC/APC) ; polarité duplex
correcte et inversée ; puissance reçue et zones de la fiche ; chaîne de raccordement chiffrée
(2,42 dB) ; trace OTDR annotée ; 3 procédures. Texte alternatif complet, légende, mention « schéma
non officiel ». **Aucune image générée, aucune photographie.**

### Fichiers

- `app/v1/ampcr_pratique_pr17_figures.py` — données, calculs et figures (`FIBRE_KINDS`,
  `fibre_family`, `CONNECTORS`, `POLISHES`, `MODULES`, `module_errors`/`module_verdict`,
  `polarity_ok`, `rx_power_dbm`, `RxSpec`/`rx_status`, `measured_loss_db`, `photometry_verdict`,
  `max_link_loss_db`, `otdr_distance_m`, `OtdrEvent`/`otdr_event_kind`, `trace_points`,
  `break_position_m`, `min_bend_radius_mm`, `COMPARISON`) ; affaiblissements et portées importés
  de PR14 (une seule source de vérité).
- `app/v1/ampcr_pratique_pr17_bank.py` — 18 exercices et 10 questions d'examen ; tous les
  nombres des énoncés, barèmes et corrigés sont calculés par ces fonctions.
- `app/v1/ampcr_pratique_pr17_course.py` — les 18 blocs du cours.
- `app/v1/ampcr_pratique_bank.py` — déclaration de PR17 et contexte de correction IA propre.
- `app/seed.py` — `_seed_uaa(…, "PR17", …, position 17)`, ajout seul.
- `tests/test_ticket218_ampcr_pratique_pr17.py` (27 tests).
- Comptages adaptés : `tests/test_admin_content_hierarchy.py`, `tests/test_ticket217_ampcr_pratique_pr14.py`.
- `docs/current_state.md`, `docs/ampcr_pratique_v1.md`, `docs/changelog.md`.

## 2. Liens pour tester

- Cours : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr17
- S'entraîner (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr17/practice
- Examen blanc /20 (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr17/exam
- Accueil du parcours pratique : https://jury-central.lodylands.com/ampcr-pratique
- Matrice : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte :
1. Ouvrir le cours et parcourir les 18 séquences (chapitres 1 à 11, cas résolus, exercices).
2. Lancer « S'entraîner » : 10 exercices tirés des 18.
3. Lancer « Examen blanc » : 10 questions, note sur 20 ; après l'envoi, vérifier correction et barème.

Dans l'accueil du parcours, PR17 apparaît après PR16 (« 19 cours publiés sur 30 prévus »).

## 3. Vérifications effectuées

- **Tests ciblés** `tests/test_ticket218_ampcr_pratique_pr17.py` : **27 passed** — calculs
  recontrôlés indépendamment (types et familles de fibre, polissage, compatibilité module / fibre
  / portée et refus d'une portée non tabulée, polarité, pertes et chaîne à 2,42 dB, puissance
  reçue et bornes de la plage, photométrie, distance OTDR depuis le temps, nature des événements,
  pente de la trace, rayons de courbure) ; schémas (validité, accessibilité, valeurs dessinées) ;
  exercices (format du socle, réponses des classements et remises en ordre, classements non
  triviaux, nombres présents dans les corrigés, aucune question d'acronyme, affirmations justes
  exigées / fausses interdites) ; cours (matière du ticket point par point, 5 cas, 3 procédures,
  examen absent du cours, liens) ; seed idempotent, position, réserves séparées, contexte de
  correction, pages, sessions d'entraînement et d'examen /20 sans génération IA.
- **Tests liés** (PR13, PR14, PR15, PR16, socle #192, numérotation #236, hiérarchie admin) :
  **224 passed** (PR17 compris).
- **Suite complète** (une exécution, `seed.py` partagé) : **2 824 passed** en 23 min.
- **`ruff check`** sur les fichiers créés et modifiés : All checks passed.
- **Contrôle visuel** (navigateur sans interface) des 9 schémas à 440 px et de la page à
  1 280 px (séquence 1, vue complète). Corrigés pendant la session : légendes qui chevauchaient
  le titre suivant (coupe, polarité), trace OTDR trop écrasée, signe moins typographique des dBm.
- **Installation** : arbre propre sur `develop` ; sauvegarde
  `~/.local/state/jury-central-orch/backups/jury_central-pre-ticket218-20261027-082532.db` ;
  avance rapide `1b19356 → f060fa2` ; seed : 1 UAA et 70 blocs « créés » (18 blocs de PR17 +
  remplacement habituel des 52 blocs FSE pilotés par le code) ; deux services actifs ; `/health`
  local et public OK ; cours PR17, PR16, PR14, accueil, matrice en HTTP 200 ; entraînement et
  examen en 303 vers la connexion (normal sans session) ; 18 cartes d'exercice servies ;
  « 19 cours publiés sur 30 prévus » ; compteurs utilisateurs / sessions / réponses inchangés
  (18 / 82 / 646).

**Non effectué** : validation pédagogique humaine ; session réelle avec la vraie correction IA
(tests avec `FakeAIProvider`) ; vérification sur le texte payant des normes (valeurs tirées de
sources publiques, présentées avec « la fiche du fabricant et les normes en vigueur font foi »).

## 4. Choix techniques faits seul

- **Périmètre** : les calculs de bilan détaillés restent dans PR14 (repris par import, lien) ;
  PR17 traite le **choix**, le **raccordement**, le **contrôle**, la **sécurité** et le
  **diagnostic**. Le matériel cuivre reste dans PR13/PR15, le coaxial dans PR16 (liens).
- **Valeurs** : affaiblissements (3,5 / 0,4 dB/km, 0,75 dB par connecteur, 0,3 dB par épissure)
  et portées IEEE 802.3 importés de PR14 ; géométrie 125/250/900 µm ; férules LC 1,25 mm, SC/ST
  2,5 mm ; APC 8° ; indice de groupe 1,468.
- **Conventions du cours**, signalées : rayon de courbure 10 × / 20 × le diamètre (la fiche du
  câble fait foi) ; seuil « aucune lumière » à −30 dBm (affichage LOS) ; fiches de modules
  (plages de réception, budget 6,2 dB, module « longue portée ») **fictives** et signalées ; code
  couleur TIA-598 présenté comme un usage, le marquage imprimé faisant foi.
- **Pas d'invention** : la fonction de compatibilité refuse une portée non tabulée (ex.
  1000BASE-SX sur OM3) plutôt que d'en deviner une ; aucun exercice ne l'utilise.
- **Classements** : éléments réordonnés pour qu'aucun ne commence par la suite des catégories
  dans l'ordre (cohérent avec #150) ; toutes les catégories sont utilisées.
- **Pas de nouvelle dépendance** ; nouveaux dessins SVG locaux et `step_flow_svg` existant.

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Éléments restant à réaliser

- Validation pédagogique et visuelle par le propriétaire.
- Suite de l'ordre pédagogique : PR18 « Installation physique d'un mini-réseau » (#219), puis
  EX03 (#232), qui couvre PR13–PR17.
- Point signalé (hors périmètre, non modifié) : PR13 et PR14 mentionnent encore PR17 « à venir »
  en texte ; maintenant que PR17 est publié, ces renvois pourraient devenir des liens (ticket de
  maintenance ou EX03).
