# Ticket #203 — [AMPCR pratique PR02] Alimentation, connectique, compatibilité et sécurité

- Ticket : https://github.com/ReC82/jury-central/issues/203
- **État réel : Installé — à tester**
- SHA installé : `57aebb3e27b0b196f9fd8eaf5bc89c1410315bfb` (fusion de la PR #255 dans `develop`)
- Date : 2026-10-26 (session jcorch autonome)

## 1. Résultat

Le cours **PR02 « Alimentation, connectique, compatibilité et sécurité »** est publié dans le
parcours **Informatique AMPCR → Pratique écrite** (module `AMPCR-PRATIQUE`, distinct de la
théorie MC). C'est le deuxième cours de l'ordre pédagogique PR01 → PR30. L'emplacement PR02 du
plan installé (`_COURSE_ROWS`, numérotation définitive de #236) porte bien le sujet du ticket
(« PR02, ticket 203, Alimentation, connectique, compatibilité et sécurité ») : aucun écart,
aucun autre cours touché ni renuméroté.

Contenu (19 blocs) :

- **12 chapitres de théorie**, chacun avec objectifs, théorie, « à l'écrit » et repère rapide :
  1. courant **alternatif / continu**, rôle du bloc, tensions +12 V, +5 V, +3,3 V, −12 V,
     **+5 VSB** (« éteint n'est pas hors tension »), PS_ON#, PWR_OK, **tolérances ATX** calculées ;
  2. caractéristiques d'un bloc : puissance nominale, **+12 V = 12 × I**, puissance combinée,
     mono/multi-rails, **rendement** et seuils **80 PLUS**, formats ATX/SFX, câbles modulaires,
     ATX 3.x ;
  3. connecteurs **ATX 24 (20+4), EPS 8 (4+4), ATX12V 4, PCIe 6/8 (75/150 W + 75 W par
     l'emplacement), 12V-2x6 (≤ 600 W), SATA 15, Molex 4**, brochages, échanges interdits ;
  4. **budget de puissance** : total, marge 20-30 %, palier, recommandation GPU, +12 V,
     connecteurs ;
  5. **ventilateurs** (3 broches DC / 4 broches PWM, CPU_FAN, SYS_FAN, AIO_PUMP), flux d'air,
     ventirad, ventilateur de bloc semi-passif ;
  6. **protections** OVP/UVP/OCP/OPP/SCP/OTP, terre, différentiel, parafoudre, **onduleur** ;
  7. **sécurité électrique** : interdiction d'ouvrir un bloc, mise hors tension, **ESD**,
     **batteries gonflées**, tableau des **outils** ;
  8. **USB** (versions, la forme n'est pas la vitesse, puissance fournie, PD), **HDMI** et
     **DisplayPort** (débits, câbles, adaptateurs) ;
  9. **SATA** données/alimentation, **PCIe**, **M.2** (longueur, clé, interface NVMe/SATA,
     ports partagés) ;
  10. **compatibilité** : génération **DDR**, **socket** (AM4, AM5, LGA1700, LGA1851), formats,
      grille complète ;
  11. **évaluer des symptômes d'alimentation** (tableau, arbre de décision, mesures) ;
  12. **procédure écrite de remplacement sûr** d'un bloc.
- **4 cas intégralement résolus** : compatibilité d'un devis (grille calculée, 4 points non
  conformes) ; dimensionnement d'un bloc ; mauvais branchement ; symptômes d'alimentation
  (relevé à vide / en charge) et remplacement sûr.
- **Pièges fréquents**, **fiche mémo + glossaire**, **sources et compléments**.
- **16 exercices corrigés** (cours + « S'entraîner ») : identification de câbles, classement
  des connecteurs, remise en ordre du remplacement d'un bloc, rendement, budget, étiquette et
  +12 V, tolérances au testeur, devis à valider, M.2 SATA/NVMe, liaison vidéo 4K 120 Hz, ports
  USB, mauvais branchements, tri des pratiques sûres/dangereuses, batterie gonflée, arrêts en
  jeu, ventilation. Chacun : contexte, documents, consignes, barème analytique, corrigé.
- **Mini-examen 10 questions /20** (2 pts chacune, réponses libres) dans « Examen blanc »,
  jamais affiché dans le cours (connecteurs, rendement, budget, tolérances, mémoire/socket,
  M.2, HDMI, EPS sur la carte graphique, mise hors tension, onduleur).
- **8 schémas SVG** produits depuis des données testées : chaîne d'alimentation, brochage
  ATX 24, EPS 8, SATA 15 + Molex, budget de puissance, flux d'air, arbre des symptômes,
  procédure sûre. Alt complet, légende, mention « schéma non officiel », responsive.

### Fichiers

- `app/v1/ampcr_pratique_pr02_figures.py` — données normalisées, calculs (tolérances,
  rendement, budget, +12 V, grille de compatibilité), relevés fictifs, SVG
- `app/v1/ampcr_pratique_pr02_bank.py` — 16 exercices + 10 questions d'examen
- `app/v1/ampcr_pratique_pr02_course.py` — 19 blocs du cours
- `app/v1/ampcr_pratique_bank.py` — déclaration PR02 + contexte de correction IA spécifique
- `app/seed.py` — `_seed_uaa(…, "PR02", …, position 2)` dans le module pratique (additif)
- `tests/test_ticket203_ampcr_pratique_pr02.py` (26 tests) ; comptages adaptés dans
  `tests/test_admin_content_hierarchy.py` et `tests/test_ticket202_ampcr_pratique_pr01.py`
- `docs/current_state.md`, `docs/ampcr_pratique_v1.md`, `docs/changelog.md`

## 2. Liens pour tester

- Cours : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr02
- S'entraîner (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr02/practice
- Examen blanc /20 (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr02/exam
- Accueil du parcours pratique : https://jury-central.lodylands.com/ampcr-pratique
- Matrice : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte : ouvrir le cours, parcourir les séquences (chapitres 1 → 12, cas, exercices) ;
lancer une session « S'entraîner » (10 exercices tirés des 16) puis un « Examen blanc »
(10 questions, note sur 20) ; vérifier la correction et le barème après envoi.

## 3. Vérifications effectuées

- Tests ciblés `tests/test_ticket203_ampcr_pratique_pr02.py` : **26 passed** — valeurs
  recalculées indépendamment (tolérances ATX, couleurs de fil, brochages ATX 24/EPS/SATA/Molex,
  puissances PCIe, seuils 80 PLUS, puissance absorbée, budgets et paliers, +12 V, grille de
  compatibilité des devis, relevés hors tolérance, débits vidéo), schémas (validité, broches et
  barres = données, flux d'air), réponses auto-corrigées, absence de question d'acronyme et
  d'affirmation fausse, matière du ticket présente, 4 cas, examen absent du cours, seed
  idempotent, réserves séparées, contexte de correction, pages, sessions entraînement/examen,
  note /20, aucune génération IA.
- **Suite complète : 2475 passed** (une seule exécution, `seed.py` étant partagé).
- `ruff check` sur les fichiers modifiés : aucune erreur.
- Installation : arbre propre sur `develop`, sauvegarde de la base
  (`~/.local/state/jury-central-orch/backups/jury_central-pre-ticket203-20261026-230110.db`),
  fast-forward `e4a4cb0 → 57aebb3`, seed idempotent (1 UAA créée ; les 52 blocs FSE
  « recréés » sont le remplacement habituel des blocs FSE pilotés par le code, sans doublon),
  redémarrage des deux services (actifs), `/health` local et public OK, pages du cours, de
  l'accueil, de la matrice, de PR01 et PR06 en HTTP 200 (entraînement/examen : 303 vers la
  connexion, normal sans session), « 8 cours publiés sur 30 prévus » sur l'accueil, 16 cartes
  d'exercice et 8 figures servies. Compteurs utilisateurs/sessions/réponses inchangés
  (18 / 81 / 638).
- Contrôle visuel (navigateur sans interface) des 8 schémas à 420 px de large (lisibilité
  mobile, deux schémas corrigés après ce contrôle) et de la page installée en desktop.

Non effectué : validation pédagogique humaine (au propriétaire) ; passage d'une session réelle
avec la vraie correction IA (les tests utilisent `FakeAIProvider`) ; capture pleine page mobile
du cours installé (même composant de page que les cours déjà publiés).

## 4. Choix techniques faits seul

- **Pas d'image générée ni de photographie** : brochages, tensions et valeurs sont dessinés en
  SVG depuis des données vérifiées (une image générée risquerait des broches ou des couleurs
  fausses). Les brochages ATX 24 et EPS 8 réutilisent les données déjà testées du cours PR06.
- **Brochage PCIe 8 broches non dessiné** : décrit en texte (3 × +12 V, 5 masses) pour éviter
  une ambiguïté d'orientation ; le message clé (EPS ≠ PCIe, ne jamais forcer) est enseigné.
- **Seuils 80 PLUS « 115 V usage interne »** : ce sont les seuils de référence publiés le plus
  souvent sur les fiches ; signalé dans le cours.
- **Marge de budget 30 %** (plage enseignée 20-30 %) et paliers de 50 W : convention de calcul
  explicite, toujours plafonnée par la recommandation du fabricant de la carte graphique.
- **Fiches produits fictives** ; seules les valeurs de normes (ATX12V, PCIe CEM, SATA, USB-IF,
  HDMI, VESA, 80 PLUS) et les noms de sockets réels sont cités.
- **Recouvrement limité** : diagnostic complet renvoyé à PR06, identification à PR01, montage
  pas à pas à PR03 ; ESD et outils traités ici au niveau requis (complément AP-C02).
- **Exigences** : celles du plan installé (AP-04, AP-06, AP-17 + complément AP-C02) ; statut
  « partiel » dans la matrice, jamais « validé ».
- Mêmes moteur, réserves `practice`/`exam`, format d'exercice et mise en forme que les cours
  pratiques déjà publiés ; pas de nouvelle dépendance.

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Éléments restant à réaliser

- Validation pédagogique et visuelle par le propriétaire.
- Suite de l'ordre pédagogique : PR03 (#204), PR04 (#205), PR05 (#206), puis EX01 (#230) après
  PR06.
- Amélioration repérée, non implémentée (hors périmètre) : la page du cours affiche les
  séquences une à une ; une capture « tout le cours » pour l'impression A4 pourrait être
  vérifiée sur l'ensemble des cours pratiques.
