# Ticket #202 — [AMPCR pratique PR01] Structure d'un PC et identification des composants

- Ticket : https://github.com/ReC82/jury-central/issues/202
- **État réel : Installé — à tester**
- SHA installé : `dd2058cb6a9aa36ff313494e6d1acf8801fe8270` (fusion de la PR #253 dans `develop`)
- Date : 2026-10-26 (session jcorch autonome)

## 1. Résultat

Le cours **PR01 « Structure d'un PC et identification des composants »** est publié dans le
parcours **Informatique AMPCR → Pratique écrite** (module `AMPCR-PRATIQUE`, distinct de la
théorie MC). C'est le premier cours de l'ordre pédagogique PR01 → PR30 demandé par le
propriétaire le 26/10. L'emplacement PR01 du plan installé (`_COURSE_ROWS`, numérotation
définitive de #236) porte bien le sujet du ticket (« PR01, ticket 202, Structure d'un PC et
identification des composants ») : aucun écart, aucun autre cours touché ni renuméroté.

Contenu (19 blocs) :

- **13 chapitres de théorie**, chacun avec objectifs, théorie, « à l'écrit » (ce qu'on attend
  dans une réponse) et repère rapide :
  1. structure : unité centrale, périphériques, **cheminement des données** (processeur, RAM,
     PCIe x16, M.2, chipset, SATA, USB) ;
  2. boîtier et formats **ATX / microATX / Mini-ITX** (dimensions, emplacements, emboîtement),
     intérieur d'une tour, flux d'air, limites du boîtier ;
  3. carte mère : **plan numéroté de 20 repères** + légende, **socket** (LGA/PGA, AM4, AM5,
     LGA1700, LGA1851), **chipset**, **VRM**, PCIe (mécanique/électrique, débits), M.2 (clé,
     NVMe/SATA, 2280), SATA, connecteurs internes (USB 2.0/3.x, HD_AUDIO, CPU_FAN, façade) ;
  4. processeur et refroidissement (puissance thermique, partie graphique intégrée, ventirad,
     pâte thermique) ;
  5. **RAM, ROM et stockage** (volatile ou non ; la ROM n'est pas du stockage), barrettes
     **DIMM / SO-DIMM**, DDR3/DDR4/DDR5 (contacts, tensions), capacité, double canal, ECC ;
  6. firmware **BIOS/UEFI**, **POST**, **pile CMOS** ;
  7. stockage **HDD, SSD SATA, M.2 SATA, NVMe**, lecture d'un inventaire `lsblk`, Go/Gio ;
  8-9. connecteurs du bloc (**ATX 24, EPS 8, PCIe 6/8, SATA, Molex** — identification ; le détail
     est en PR02) et **carte graphique** ;
  10. ports externes et internes, **USB** (la forme n'est pas le débit), vidéo, réseau, audio ;
  11. périphériques d'entrée/sortie et **rôle d'un pilote** ;
  12. **grille de compatibilité** (arbre de décision + tableau par pièce) ;
  13. démarche écrite : identifier, inventorier, interpréter, **précautions ESD** justifiées.
- **4 cas intégralement résolus** : inventaire d'une unité centrale ; inventaire mémoire (8 Go
  détectés pour 16 installés, relevé PowerShell) ; choix d'une carte mère de remplacement ;
  installation justifiée d'une carte graphique avec précautions.
- **Pièges fréquents**, **fiche mémo + glossaire**, **sources et compléments**.
- **16 exercices corrigés** (cours + « S'entraîner ») : identifications sur description,
  2 classements (mémoires ; périphériques), 1 remise en ordre (trajet d'une photo jusqu'à
  l'écran), inventaire `lsblk`, choix de barrette, de SSD M.2, de processeur, de ventirad, de
  carte graphique, devis complet, format de boîtier, branchements, pilote, questions de client
  sur le firmware, procédure d'ajout de RAM avec ESD. Chacun : contexte, documents, consignes,
  barème analytique, corrigé.
- **Mini-examen 10 questions /20** (2 pts chacune, réponses libres) dans « Examen blanc »,
  jamais affiché dans le cours.
- **8 schémas SVG** construits depuis des données testées : démarche d'identification,
  schéma-bloc des liaisons, formats à l'échelle (1 px = 1 mm), intérieur d'une tour, plan de
  carte mère numéroté, barrettes DIMM/SO-DIMM à l'échelle, panneau arrière, arbre de
  compatibilité. Alt complet, légende, mention « schéma non officiel », responsive.

### Fichiers

- `app/v1/ampcr_pratique_pr01_figures.py` — données normalisées, relevés fictifs calculés, SVG
- `app/v1/ampcr_pratique_pr01_bank.py` — 16 exercices + 10 questions d'examen
- `app/v1/ampcr_pratique_pr01_course.py` — 19 blocs du cours
- `app/v1/ampcr_pratique_bank.py` — déclaration PR01 + contexte de correction IA spécifique
- `app/seed.py` — `_seed_uaa(…, "PR01", …, position 1)` dans le module pratique (additif)
- `tests/test_ticket202_ampcr_pratique_pr01.py` (29 tests) ; comptages adaptés dans
  `tests/test_admin_content_hierarchy.py` et `tests/test_ticket200_ampcr_pratique_pr24.py`
- `docs/current_state.md`, `docs/ampcr_pratique_v1.md`, `docs/changelog.md`

## 2. Liens pour tester

- Cours : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr01
- S'entraîner (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr01/practice
- Examen blanc /20 (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr01/exam
- Accueil du parcours pratique : https://jury-central.lodylands.com/ampcr-pratique
- Matrice : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte : ouvrir le cours, parcourir les séquences (chapitres 1 → 13, cas, exercices) ;
lancer une session « S'entraîner » (10 exercices tirés des 16) puis un « Examen blanc »
(10 questions, note sur 20) ; vérifier la correction et le barème après envoi.

## 3. Vérifications effectuées

- Tests ciblés `tests/test_ticket202_ampcr_pratique_pr01.py` : **29 passed** — valeurs
  normalisées recalculées indépendamment (formats et emboîtement, contacts des barrettes,
  débits PCIe 128b/130b, USB, conversion décimal → binaire de `lsblk`, octets du relevé
  PowerShell), largeur mobile des captures (≤ 56 caractères), schémas (validité, plans numérotés
  = légendes, zones sans chevauchement, formats dessinés à l'échelle, liaisons du schéma-bloc),
  réponses auto-corrigées, absence de question d'acronyme, matière du ticket présente, 4 cas,
  examen absent du cours, seed idempotent, import de la banque et réserves séparées, contexte de
  correction, pages, sessions entraînement/examen, note /20, aucune génération IA.
- Tests des autres cours pratiques, du socle #192, de la numérotation #236 et du seed :
  284 passed. **Suite complète : 2449 passed** (une seule exécution, `seed.py` étant partagé).
- `ruff check` sur les fichiers modifiés : aucune erreur.
- Installation : arbre propre sur `develop`, sauvegarde de la base
  (`~/.local/state/jury-central-orch/backups/jury_central-pre-ticket202-20261026-222202.db`),
  fast-forward `6493003 → dd2058c`, seed idempotent (1 UAA créée ; les 52 blocs FSE
  « recréés » sont le remplacement volontaire et habituel des blocs FSE pilotés par le code,
  `obsolete_titles`, sans doublon), redémarrage des deux services (actifs), `/health` local et
  public OK, pages du cours, de l'accueil, de la matrice et de PR06/PR24 en HTTP 200,
  « 7 cours publiés sur 30 prévus » sur l'accueil, 16 cartes d'exercice servies. Compteurs
  utilisateurs/sessions/réponses inchangés (18 / 81 / 638).
- Contrôle visuel (navigateur sans interface) des schémas et de la page installée en desktop et
  en mobile (390 px) : schémas lisibles ; sur mobile, les tableaux larges défilent
  horizontalement dans leur cadre (`table-responsive`), comme dans les autres cours.

Non effectué : validation pédagogique humaine (au propriétaire) ; passage d'une session réelle
avec la vraie correction IA (les tests utilisent `FakeAIProvider`).

## 4. Choix techniques faits seul

- **Pas d'image générée ni de photographie** : le ticket demande « identifier sur
  photographie/schéma » ; faute de photos libres de droits vérifiées, l'identification se fait
  sur **schémas numérotés** et sur **descriptions écrites** (format utilisable aussi dans les
  sessions, qui n'affichent que des documents texte/tableau). Les images générées auraient risqué
  des détails techniques faux (broches, slots).
- **Fiches produits fictives** (« ne pas inventer de spécifications de produits ») : aucun
  produit réel cité ; les noms de sockets réels (AM4, AM5, LGA1700, LGA1851) et les valeurs de
  normes (JEDEC, PCI-SIG, USB-IF, ATX) sont exacts et cités en sources.
- **Recouvrement avec PR02, PR03, PR05, PR06 limité** : connecteurs d'alimentation,
  montage, stockage et diagnostic restent au niveau de l'identification, avec renvoi au cours
  dédié ; ESD traité au niveau des précautions justifiées (complément AP-C02).
- **Exigences** : celles du plan installé (AP-01, AP-02, AP-05, AP-07, AP-17) + complément
  AP-C02 ; statut « partiel » dans la matrice, jamais « validé » (pas de relecture humaine).
- Mêmes moteur, réserves `practice`/`exam`, format d'exercice et mise en forme que les cours
  pratiques déjà publiés ; pas de nouveau moteur ni de nouvelle dépendance.

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Éléments restant à réaliser

- Validation pédagogique et visuelle par le propriétaire.
- Suite de l'ordre pédagogique : PR02 (#203), PR03 (#204), PR04 (#205), PR05 (#206), puis EX01
  (#230) après PR06.
- Amélioration repérée, non implémentée (hors périmètre) : sur mobile, les tableaux à trois
  colonnes et plus défilent horizontalement ; une présentation en cartes empilées pourrait être
  étudiée pour tous les cours pratiques.
