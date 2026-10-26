# Ticket #204 — [AMPCR pratique PR03] Montage et démontage d'un PC — procédure écrite

- Ticket : https://github.com/ReC82/jury-central/issues/204
- **État réel : Installé — à tester**
- SHA installé : `9eb17a6d632af8972e8249123bb3f98415cc73da` (fusion de la PR #257 dans `develop`)
- Date : 2026-10-26 (session jcorch autonome)

## 1. Résultat

Le cours **PR03 « Montage et démontage d'un PC — procédure écrite »** est publié dans le
parcours **Informatique AMPCR → Pratique écrite** (module `AMPCR-PRATIQUE`, distinct de la
théorie MC : cours, banque, examen et progression séparés ; liens croisés vers MC05 et MC06
seulement). C'est le troisième cours de l'ordre pédagogique PR01 → PR30. L'emplacement PR03 du
plan installé (`_COURSE_ROWS`, numérotation définitive de #236) porte bien le sujet du ticket
(« PR03, ticket 204, Montage et démontage d'un PC — procédure écrite », exigences AP-14 et
AP-C02) : aucun écart de numérotation, aucun autre cours touché ni renuméroté.

Contenu (20 blocs) :

- **13 chapitres de théorie**, chacun avec objectifs, théorie, **procédure professionnelle à
  rédiger**, **erreur fréquente**, « à l'écrit », repère rapide et renvoi aux exercices liés :
  1. préparer le poste : outillage (PH1/PH2, bac à vis…), **ESD** (bracelet, tapis, sachets),
     inventaire, photos ;
  2. avant d'ouvrir : **sauvegarde** vérifiée ou refus écrit, **autorisation**, état initial,
     fiche d'intervention ;
  3. **compatibilité** vérifiée sur les fiches avant le montage (grille), « ne jamais forcer » ;
  4. **ordre de montage** recommandé et sa justification, cas où la notice l'adapte ;
  5. carte équipée hors boîtier : **processeur LGA/PGA** (triangle, capot), **pâte thermique**
     (quantité, film du ventirad, serrage en croix, renouvellement), **ventirad**, CPU_FAN,
     **mémoire** (emplacements du manuel), **SSD M.2** (entretoise, 30°, vis) ;
  6. boîtier : **entretoises** (une sous chaque trou, aucune ailleurs), plaque d'E/S, carte
     mère, **bloc**, disques, **carte graphique** ; tableau de **visserie** ;
  7. **câblage** : ATX 24, EPS, PCIe, SATA, **connecteurs de façade** (brochage, LED
     polarisées, boutons non), USB/audio internes, ventilateurs ;
  8. **contrôle visuel** PC débranché (grille à cocher) ;
  9. **premier démarrage** : POST, entraînement de la mémoire, LED de diagnostic, **UEFI
     comparé au bon de montage**, XMP/EXPO, **tests mémoire, températures, SMART**, ports ;
  10. **gestion des câbles et flux d'air** ;
  11. **démontage** inverse documenté : photos, étiquettes, vis triées, loquets, clip PCIe,
      **dissipateur collé** (rotation, risque d'arrachement d'un processeur PGA), capot LGA ;
  12. **remplacement d'un composant et remontage** (démarche + tableau des cas fréquents) ;
  13. **pannes au premier démarrage** (arbre de décision + tableau symptômes/causes de montage,
      règles de sécurité du diagnostic).
- **5 procédures illustrées** (schémas en étapes) : préparer le poste et l'intervention ;
  monter un PC complet ; installer processeur, pâte et ventirad ; démonter en documentant ;
  premier démarrage et tests.
- **4 cas intégralement résolus** : procédure complète de montage (avec adaptation de l'ordre
  pour un ventirad à plaque arrière) ; démontage/remplacement d'un ventirad sur AM4 ; premier
  démarrage incomplet (écran UEFI fictif : mémoire, disque SATA, CPU_FAN) ; surchauffe après
  montage (film du ventirad, relevés avant/après).
- **Pièges fréquents**, **fiche mémo + glossaire**, **sources et compléments**.
- **16 exercices corrigés** (cours + « S'entraîner ») : **4 remises en ordre** (préparation,
  montage, processeur/ventirad, remplacement d'une carte graphique), **2 classements** (bonnes
  pratiques/erreurs ; moment de chaque vérification), **repérage d'erreurs** (entretoises,
  câblage de façade, contrôle visuel), **premier démarrage** (UEFI, écran noir DDR5,
  températures), **justifications** (ordre de montage, ventirad collé, visserie) et une fiche
  avant démontage. Chacun : contexte complet, documents, consignes, barème analytique, corrigé.
- **Mini-examen 10 questions /20** (2 pts chacune, réponses libres) dans « Examen blanc »,
  jamais affiché dans le cours.
- **9 schémas SVG** produits depuis des données testées : 5 procédures, plan des entretoises,
  connecteur de façade, écran UEFI fictif, arbre des pannes au premier démarrage. Alt complet,
  légende, mention « schéma non officiel », responsive. **Aucune image générée.**
- Aucune manipulation sous tension ni ouverture de bloc d'alimentation n'est demandée ; le cours
  le rappelle explicitement.

### Fichiers

- `app/v1/ampcr_pratique_pr03_figures.py` — procédures, brochage de façade, entretoises
  (contrôle `standoff_status`), visserie, grille de contrôle, arbre des pannes, inventaire
  détecté (`inventory_gaps`), seuil de température, SVG
- `app/v1/ampcr_pratique_pr03_bank.py` — 16 exercices + 10 questions d'examen
- `app/v1/ampcr_pratique_pr03_course.py` — 20 blocs du cours
- `app/v1/ampcr_pratique_bank.py` — déclaration PR03 + contexte de correction IA spécifique
- `app/seed.py` — `_seed_uaa(…, "PR03", …, position 3)` dans le module pratique (additif)
- `tests/test_ticket204_ampcr_pratique_pr03.py` (25 tests) ; comptages adaptés dans
  `tests/test_admin_content_hierarchy.py` et `tests/test_ticket203_ampcr_pratique_pr02.py`
- `docs/current_state.md`, `docs/ampcr_pratique_v1.md`, `docs/changelog.md`

## 2. Liens pour tester

- Cours : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr03
- S'entraîner (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr03/practice
- Examen blanc /20 (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr03/exam
- Accueil du parcours pratique : https://jury-central.lodylands.com/ampcr-pratique
- Matrice : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte : ouvrir le cours, parcourir les séquences (chapitres 1 → 13, cas,
exercices) ; lancer une session « S'entraîner » (10 exercices tirés des 16, dont des remises
en ordre et des classements auto-corrigés) puis un « Examen blanc » (10 questions, note sur
20) ; vérifier la correction et le barème après envoi.

## 3. Vérifications effectuées

- Tests ciblés `tests/test_ticket204_ampcr_pratique_pr03.py` : **25 passed** — brochage de
  façade (disposition Intel, LED polarisées, boutons non), entretoises (verdict par
  emplacement, en trop / manquante), visserie, grille de contrôle, 5 procédures (ordre et
  contenu), écarts d'inventaire, seuils de température, schémas (validité, accessibilité,
  broches/emplacements/étapes = données), remises en ordre et classements auto-corrigés,
  absence de question d'acronyme et d'affirmation fausse, matière du ticket présente, 5
  procédures et 4 cas, examen absent du cours, seed idempotent, réserves séparées, contexte de
  correction, pages, sessions entraînement/examen, note /20, aucune génération IA.
- **Suite complète : 2500 passed** (une seule exécution, `seed.py` étant partagé).
- `ruff check` sur les fichiers modifiés : aucune erreur.
- Contrôle visuel (navigateur sans interface) des 9 schémas à 420 px de large (lisibilité
  mobile ; connecteur de façade et plan des entretoises corrigés après ce contrôle) et de la page
  installée en desktop.
- Installation : arbre propre sur `develop`, sauvegarde de la base
  (`~/.local/state/jury-central-orch/backups/jury_central-pre-ticket204-20261026-233918.db`),
  fast-forward `4059cd1 → 9eb17a6`, seed idempotent (1 UAA créée ; les 72 blocs « créés » =
  20 blocs PR03 + le remplacement habituel des 52 blocs FSE pilotés par le code, sans doublon),
  redémarrage des deux services (actifs), `/health` local et public OK, pages du cours, de
  l'accueil, de la matrice, de PR01, PR02 et PR06 en HTTP 200 (entraînement/examen : 303 vers la
  connexion, normal sans session), « 9 cours publiés » sur l'accueil, 16 cartes d'exercice et
  9 figures servies. Compteurs utilisateurs/sessions/réponses inchangés (18 / 81 / 638).

Non effectué : validation pédagogique humaine (au propriétaire) ; passage d'une session réelle
avec la vraie correction IA (les tests utilisent `FakeAIProvider`) ; capture pleine page mobile
du cours installé (même composant de page que les cours déjà publiés).

## 4. Choix techniques faits seul

- **Pas d'image générée ni de photographie** : brochage de façade, entretoises, procédures et
  écran du firmware sont dessinés en SVG depuis des données vérifiées (une image générée
  risquerait des broches ou des positions fausses).
- **Connecteur de façade** : disposition 2 × 5 du guide Intel (*Front Panel I/O Connectivity
  Design Guide*), la plus répandue ; le cours, la légende et les corrigés rappellent que le
  manuel de la carte fait foi (certaines cartes diffèrent).
- **Ordre de montage** : ordre « carte équipée hors du boîtier » le plus enseigné, présenté
  comme recommandé et justifié, avec les cas où la notice l'adapte (plaque arrière, AIO,
  boîtier compact). Les remises en ordre précisent « l'ordre recommandé par la procédure du
  cours » pour éviter l'ambiguïté.
- **Visserie** : valeurs « les plus courantes » (6-32, M3, M2), formulées avec prudence
  (carte mère : 6-32 le plus souvent, parfois M3 ; vis livrées avec le boîtier).
- **Seuil de température** : convention du cours « à surveiller à moins de 10 °C de la limite
  de la fiche, anormal à la limite » (pas une norme), explicitée dans le chapitre 9.
- **Renvois aux exercices en texte** (et non en liens d'ancre) : la page affiche une séquence à
  la fois et un clic sur une ancre d'une autre séquence ne la ferait pas apparaître (le script
  ne gère l'ancre qu'au chargement).
- **Recouvrement limité** : reconditionnement et effacement des données renvoyés à PR04,
  connecteurs d'alimentation et compatibilité détaillée à PR02, identification à PR01,
  diagnostic complet à PR06. Exigences : celles du plan installé (AP-14 + complément AP-C02) ;
  statut « partiel » dans la matrice, jamais « validé ».
- Mêmes moteur, réserves `practice`/`exam`, format d'exercice et mise en forme que les cours
  pratiques déjà publiés ; pas de nouvelle dépendance.

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Éléments restant à réaliser

- Validation pédagogique et visuelle par le propriétaire.
- Suite de l'ordre pédagogique : PR04 (#205), PR05 (#206), puis EX01 (#230) après PR06.
- Améliorations repérées, non implémentées (hors périmètre) : (1) `lesson_sequences.js` ne
  réagit à une ancre qu'au chargement de la page : un lien interne vers une autre séquence ne
  l'affiche pas (un écouteur `hashchange` le permettrait, pour tous les cours) ; (2) dans
  l'arbre de décision partagé (`decision_tree_svg`), l'étiquette « NON » chevauche la flèche
  sur mobile (déjà présent sur PR02/PR06).
