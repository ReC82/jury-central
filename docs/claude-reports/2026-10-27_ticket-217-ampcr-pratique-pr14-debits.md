# Ticket #217 — [AMPCR pratique PR14] Débits, distances, atténuation et impédance

- Ticket : https://github.com/ReC82/jury-central/issues/217
- **État réel : Installé — à tester**
- SHA installé : `c2ee9980c1a832b42709b3b3a8e9145351be3a34` (fusion de la PR #279 dans `develop`)
- Date : 2026-10-27 (session jcorch autonome)

## 1. Résultat

Le cours **PR14 « Débits, distances, atténuation et impédance »** est publié dans le parcours
**Informatique AMPCR → Pratique écrite** (module `AMPCR-PRATIQUE`). Il est séparé de la théorie
MC : son cours, sa banque, son examen et sa progression sont distincts. Le seul lien vers la
théorie renvoie à MC15. PR14 occupe la position 14 de l'ordre pédagogique : après PR13, avant
PR15.

**Numérotation vérifiée** : dans le plan installé (`_COURSE_ROWS`, numérotation définitive de
#236), l'emplacement PR14 porte bien le sujet du ticket (« PR14, ticket 217, Débits, distances,
atténuation et impédance », exigences officielles AP-19 et AP-20). Aucun écart, aucun autre
cours touché ni renuméroté.

### Contenu (16 blocs)

**9 chapitres de théorie**, chacun avec objectifs, théorie, procédure professionnelle à rédiger,
erreur fréquente, attendu « à l'écrit », repère rapide et renvoi aux exercices liés :

1. **Bits, octets, b/s et multiples** : b et o (B), préfixes décimaux (k, M, G, T) et binaires
   (Ki, Mi, Gi ; Windows écrit « Go » pour des Gio), conversions × 8 / ÷ 8.
2. **Durée d'une copie, débit nominal et utile** : durée = bits / débit utile ; rendement
   maximal d'une copie TCP sur Ethernet calculé depuis les en-têtes (1460 / 1538 ≈ 94,9 %) ;
   causes d'un débit utile plus bas.
3. **Ethernet 10/100/1000/10G et coaxial** : tableau des normes (débit, câble, paires) ; canal
   100 m = lien permanent 90 m + cordons 10 m ; Cat5e 1 Gb/s sur 100 m, Cat6A 10 Gb/s sur
   100 m, Cat6 à 10 Gb/s sur distance conditionnelle (55 m au plus, 37 m au pire, à certifier) ;
   10BASE2 185 m, 10BASE5 500 m, longueurs fixées par la limite de 8,5 dB à 10 MHz.
4. **Atténuation et décibels** : formule, 3 dB ≈ ÷ 2, 10 dB = ÷ 10, addition des dB, dBm ;
   affaiblissement maximal du câble seul à 100 MHz (Cat5e 22,0 / Cat6 19,8 / Cat6A 19,1 dB pour
   100 m).
5. **Bruit, diaphonie NEXT et blindage** : rapport signal/bruit, NEXT et FEXT (grand NEXT = bon),
   ACR, diaphonie exogène, rôle de l'écran (renvoi PR13).
6. **Impédance et réflexions** : 100 Ω ± 15 Ω, 50 Ω, 75 Ω (et 150 Ω historique) ; Γ, puissance
   réfléchie, affaiblissement de réflexion ; tableau calculé ; renvoi PR16 (réflectométrie).
7. **Fibre monomode ou multimode** : types OM1–OM4, OS1/OS2 ; pertes (3,5 / 1,5 dB/km
   multimode, 0,4 dB/km OS2, 0,75 dB par connecteur, 0,3 dB par épissure) ; **portée selon le
   module et la fibre** (1000BASE-SX/LX, 10GBASE-SR/LR) ; budget et marge.
8. **Duplex, auto-négociation et collisions** : half/full, hubs et CSMA/CD, auto-négociation,
   désaccord de duplex (tableau calculé).
9. **Diagnostic d'une liaison à 100 Mb/s au lieu de 1 Gb/s** : trois familles de causes,
   lecture `ethtool` / `Get-NetAdapter` / port du switch.

**3 procédures illustrées** : calculer la durée d'une copie ; diagnostiquer une liaison à
100 Mb/s ; faire le bilan d'une liaison optique.

**5 cas chiffrés résolus** : sauvegarde de 50 Go (7 min 6 s à 1 Gb/s, 1 h 10 min 55 s à
100 Mb/s) ; 10 Gb/s sur Cat6 de 48 m (sous conditions) ; affaiblissement d'un Cat6 de 60 m
(11,88 dB, 6,5 % restants) ; bilan OM3 de 220 m (2,27 dB, marge 0,33 dB) ; PC à 100 Mb/s par
paire 7-8 ouverte.

Puis **pièges**, **fiche mémo et glossaire**, **sources et compléments**.

**19 exercices corrigés** (le ticket en demande au moins 18), chacun avec contexte, consignes,
barème et corrigé :
- **3 remises en ordre** : calcul d'une durée, diagnostic 100 Mb/s, bilan optique ;
- **5 classements auto-corrigés** : norme/catégorie/longueur (8 liaisons), décibels → part
  restante, auto-négociation (7 liaisons), support et module à 10 Gb/s (7 liaisons), type de
  réflexion (7 montages) ;
- **6 analyses de documents chiffrés** : durée d'une image disque, débit mesuré (Gio/Go), sortie
  `ethtool` + testeur, rapport de testeur (affaiblissement, NEXT, ACR), bilan monomode avec marge
  exigée, segments coaxiaux ;
- **5 rédactions** : 1 Gb/s ≠ 1 Go/s, désaccord de duplex, Cat6 à 10 Gb/s, idée fausse sur le
  NEXT, collisions d'un hub.

**Mini-examen de 10 questions /20** (2 points chacune, réponses libres, onglet « Examen blanc »,
jamais affiché dans le cours) : durée de sauvegarde, abonnement 500 Mb/s, 10 Gb/s sur Cat6 de
75 m, bus 10BASE2 de 230 m, puissance après 13 dB, bilan monomode, poste bloqué à 100 Mb/s,
collisions tardives, caméra 75 Ω sur RG-58, lien refusé pour le NEXT.

**9 schémas SVG** produits depuis des données testées : octet et préfixes ; portées (échelle
logarithmique) ; puissance restante en dB ; diaphonie NEXT/FEXT ; réflexions (Γ calculés) ;
bilan optique empilé ; 3 procédures. Texte alternatif complet, légende, mention « schéma non
officiel ». **Aucune image générée, aucune photographie.**

### Fichiers

- `app/v1/ampcr_pratique_pr14_figures.py` — données, calculs et figures (`to_bits`, `rate_bps`,
  `transfer_time_s`, `duration_fr`, `TCP_EFFICIENCY`, `COPPER_STANDARDS`/`copper_verdict`,
  `loss_db`/`fraction_after`/`dbm`/`cable_loss_db`, `acr_db`, `reflected_power_pct`,
  `return_loss_db`, `FIBRE_REACH`/`FibreLink`/`fibre_errors`/`choose_10g`, `Port`/`negotiate`).
- `app/v1/ampcr_pratique_pr14_bank.py` — 19 exercices et 10 questions d'examen ; tous les
  nombres des énoncés, barèmes et corrigés sont calculés par ces fonctions.
- `app/v1/ampcr_pratique_pr14_course.py` — les 16 blocs du cours.
- `app/v1/ampcr_pratique_bank.py` — déclaration de PR14 et contexte de correction IA propre.
- `app/seed.py` — `_seed_uaa(…, "PR14", …, position 14)`, ajout seul.
- `tests/test_ticket217_ampcr_pratique_pr14.py` (29 tests).
- Comptages adaptés : `tests/test_admin_content_hierarchy.py`, `tests/test_ticket216_ampcr_pratique_pr13.py`.
- `docs/current_state.md`, `docs/ampcr_pratique_v1.md`, `docs/changelog.md`.

## 2. Liens pour tester

- Cours : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr14
- S'entraîner (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr14/practice
- Examen blanc /20 (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr14/exam
- Accueil du parcours pratique : https://jury-central.lodylands.com/ampcr-pratique
- Matrice : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte :
1. Ouvrir le cours et parcourir les 16 séquences (chapitres 1 à 9, cas résolus, exercices).
2. Lancer « S'entraîner » : 10 exercices tirés des 19.
3. Lancer « Examen blanc » : 10 questions, note sur 20 ; après l'envoi, vérifier correction et barème.

Dans l'accueil du parcours, PR14 apparaît après PR13 (« 18 cours publiés sur 30 prévus »).

## 3. Vérifications effectuées

- **Tests ciblés** `tests/test_ticket217_ampcr_pratique_pr14.py` : **29 passed** — calculs
  recontrôlés indépendamment (unités, durées, rendement TCP, verdicts cuivre, 8,5 dB coaxial,
  dB/dBm, ACR, Γ et affaiblissement de réflexion, bilans et portées optiques, négociation et
  duplex) ; schémas (validité, accessibilité, valeurs dessinées) ; exercices (format du socle,
  réponses des classements et remises en ordre, nombres présents dans les corrigés, aucune
  question d'acronyme, liste d'affirmations justes exigées / fausses interdites) ; cours
  (matière du ticket point par point, 5 cas, 3 procédures, examen absent du cours, liens) ;
  seed idempotent, position, réserves séparées, contexte de correction, pages, sessions
  d'entraînement et d'examen /20 sans génération IA.
- **Tests liés** (PR13, socle #192, numérotation #236, PR15, PR16, EX02, PR12, hiérarchie admin) :
  **254 passed**.
- **Suite complète** (une exécution, `seed.py` partagé) : **2 797 passed** en 23 min.
- **`ruff check`** sur les fichiers créés et modifiés : All checks passed.
- **Contrôle visuel** (navigateur sans interface) des 9 schémas à 440 px et de la page à
  1 280 px. Corrigés pendant la session : libellés tronqués dans le schéma des réflexions et
  dans l'octet ; pourcentages mal formatés (« 1 % » pour 100 %) dus à `fr(x, 0)` de PR16 — PR14
  utilise sa propre fonction `fr`, qui arrondit correctement à l'unité.
- **Installation** : arbre propre sur `develop` ; sauvegarde
  `~/.local/state/jury-central-orch/backups/jury_central-pre-ticket217-20261027-073832.db` ;
  avance rapide `24e2af8 → c2ee998` ; seed : 1 UAA et 68 blocs « créés » (16 blocs de PR14 +
  remplacement habituel des 52 blocs FSE pilotés par le code) ; deux services actifs ; `/health`
  local et public OK ; cours, PR13, PR15, accueil, matrice en HTTP 200 ; entraînement et examen
  en 303 vers la connexion (normal sans session) ; 19 cartes d'exercice servies ; « 18 cours
  publiés sur 30 prévus » ; compteurs utilisateurs / sessions / réponses inchangés (18 / 81 / 638).

**Non effectué** : validation pédagogique humaine ; session réelle avec la vraie correction IA
(tests avec `FakeAIProvider`) ; vérification sur le texte payant des normes (valeurs tirées de
sources publiques, présentées avec « la fiche du fabricant et les normes en vigueur font foi »).

## 4. Choix techniques faits seul

- **Périmètre** : choix et pose des câbles → PR13 ; brochage, testeurs → PR15 ; coaxial BNC et
  réflectométrie → PR16 (liens) ; pose et raccordement de la fibre → PR17 (non publié, cité en
  texte). PR14 traite les **valeurs chiffrées** et le **diagnostic par les valeurs**. Les items
  sur la fibre citent aussi AP-21 (exigence de PR17) en complément ; la matrice reste AP-19/AP-20
  pour PR14, statut « partiel ».
- **Rendement** : calculé depuis les tailles de trame (sans option TCP) ; les exercices donnent
  le rendement mesuré quand il intervient, pour éviter toute ambiguïté.
- **Valeurs normatives retenues** : celles listées au § 1 (IEEE 802.3, TIA-568, TSB-155,
  ISO/IEC 11801). Les limites des rapports de testeur (31,1 dB / 35,3 dB à 250 MHz) et les budgets
  de modules (2,6 dB, 6,2 dB) sont présentés comme « limites du testeur » ou « fiche du module »
  dans des supports fictifs.
- **Conventions du cours**, signalées : 1000BASE-T sur Cat5e minimum (un ancien Cat5 est « à
  certifier ») ; choix d'un support à 10 Gb/s (cuivre ≤ 100 m dans un bâtiment, puis OM3, OM4,
  OS2) ; rétrogradation à 100 Mb/s quand une paire manque (comportement courant des cartes).
- **Pas de nouvelle dépendance** ; quatre nouveaux dessins SVG locaux (octet, portées
  logarithmiques, dB, diaphonie, réflexions, bilan) et `step_flow_svg` existant. L'arbre de
  décision partagé n'est pas utilisé (défaut d'étiquette « NON » déjà signalé).

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Éléments restant à réaliser

- Validation pédagogique et visuelle par le propriétaire.
- Suite de l'ordre pédagogique : PR17 « Fibre optique » (#218). Une fois PR14 publié, les
  renvois en texte de PR13 vers PR14 pourraient devenir des liens (hors périmètre ici, à faire
  dans un ticket de maintenance ou lors de PR17).
- Point signalé (pas de défaut visible aujourd'hui) : `fr(x, 0)` de `ampcr_pratique_pr16_figures`
  retirerait les zéros des entiers (120 → « 12 ») ; aucun autre cours ne l'appelle avec 0 décimale
  (recherche faite), PR14 utilise sa propre fonction.
