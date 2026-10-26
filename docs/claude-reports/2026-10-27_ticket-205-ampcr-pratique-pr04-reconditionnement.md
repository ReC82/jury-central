# Ticket #205 — [AMPCR pratique PR04] Reconditionnement, entretien et contrôles après intervention

- Ticket : https://github.com/ReC82/jury-central/issues/205
- **État réel : Installé — à tester**
- SHA installé : `965b29bf7aaec1161453a1a13f19139cc230156c` (fusion de la PR #259 dans `develop`)
- Date : 2026-10-27 (session jcorch autonome)

## 1. Résultat

Le cours **PR04 « Reconditionnement, entretien et contrôles après intervention »** est publié
dans le parcours **Informatique AMPCR → Pratique écrite** (module `AMPCR-PRATIQUE`, distinct de
la théorie MC : cours, banque, examen et progression séparés ; liens croisés vers MC06 et MC32
seulement). C'est le quatrième cours de l'ordre pédagogique PR01 → PR30. L'emplacement PR04 du
plan installé (`_COURSE_ROWS`, numérotation définitive de #236) porte bien le sujet du ticket
(« PR04, ticket 205, Reconditionnement, entretien et contrôles après intervention », exigences
AP-14 et AP-C03) : aucun écart de numérotation, aucun autre cours touché ni renuméroté.

Contenu (20 blocs) :

- **13 chapitres de théorie**, chacun avec objectifs, théorie, **procédure professionnelle à
  rédiger**, **erreur fréquente**, « à l'écrit », repère rapide et renvoi aux exercices liés :
  1. **réparation / reconditionnement / remise à zéro / effacement sécurisé** (tableau : but,
     sort des données, destinataire, trace) et procédure complète de reconditionnement ;
  2. **réception** : fiche de réception (formulaire), inventaire, **numéros de série**,
     accessoires, état initial et photos ;
  3. **diagnostic avant intervention** (UEFI, SMART, mémoire, batterie, ports) ;
  4. **protection des données** : seul le propriétaire décide, par écrit ; sauvegarde vérifiée
     ou refus signé ; confidentialité ; arbre de décision ;
  5. **effacement sécurisé HDD / SSD SATA / SSD NVMe** : formatage rapide ≠ effacement,
     niveaux NIST SP 800-88, écrasement complet (HDD), commande d'effacement sécurisé /
     Sanitize / NVMe Format ou effacement cryptographique (SSD), destruction, **certificat** ;
  6. **nettoyage non destructif** (vue annotée des points de poussière, procédure) ;
  7. **poussière, refroidissement et températures** (mesures avant/après, pâte neuve) ;
  8. **remplacement de pièces** et contrôle de compatibilité (SSD, mémoire, ventilateur,
     batterie, pile CR2032, bloc) ;
  9. **mises à jour firmware, système et pilotes** avec précautions (modèle exact, notes,
     secteur stable, **BitLocker suspendu**, ne jamais couper) ;
  10. **tests après intervention** : RAM, **SMART** (lire les attributs, pas « PASSED »),
      températures, ports, stabilité, **rapport de batterie** (`powercfg /batteryreport`) ;
  11. **check-list de réception et de remise** (formulaire de remise) ;
  12. **déchets** : DEEE (directive 2012/19/UE, Recupel), piles et batteries (Bebat), batterie
      lithium gonflée ;
  13. **rapport et traçabilité** (rubriques, étiquette, registre).
- **5 procédures illustrées** : reconditionner un PC ; nettoyer une tour ; mettre à jour le
  firmware ; effacer un support ; contrôler après l'intervention.
- **4 cas intégralement résolus** : lot de PC pour une école ; disque « PASSED » à remplacer
  (relevé SMART) ; batterie d'un portable de prêt (68 % → à remplacer) ; portable qui chauffe
  (températures avant/après nettoyage).
- **Pièges fréquents**, **fiche mémo + glossaire**, **sources et compléments**.
- **16 exercices corrigés** (cours + « S'entraîner ») : **3 remises en ordre**
  (reconditionnement, nettoyage, firmware), **4 classements** auto-corrigés (opérations,
  **sort des données en 6 situations**, technique d'effacement adaptée au support, tri des
  déchets), **décisions de protection des données** (demande d'un tiers, SSD par passes),
  lecture de relevés (2 relevés SMART, températures, batterie, pile de la carte mère),
  formulaires (fiche de réception à compléter, check-list de remise) et rapport à corriger.
  Chacun : contexte complet, documents, consignes, barème analytique, corrigé.
- **Mini-examen 10 questions /20** (2 pts chacune, réponses libres) dans « Examen blanc »,
  jamais affiché dans le cours.
- **9 schémas SVG** produits depuis des données testées : 5 procédures, **vue annotée** d'une
  tour (7 repères numérotés), arbre de décision des données, relevé SMART fictif, courbe de
  températures. Alt complet, légende, mention « schéma non officiel », responsive. **Aucune
  image générée ni photographie** (voir choix techniques).

### Fichiers

- `app/v1/ampcr_pratique_pr04_figures.py` — procédures, opérations, `data_decision`,
  techniques d'effacement par support (`erase_method_ok`), `smart_verdict`, batterie,
  points de nettoyage, formulaires, filières de déchets, SVG
- `app/v1/ampcr_pratique_pr04_bank.py` — 16 exercices + 10 questions d'examen
- `app/v1/ampcr_pratique_pr04_course.py` — 20 blocs du cours
- `app/v1/ampcr_pratique_bank.py` — déclaration PR04 + contexte de correction IA spécifique
- `app/seed.py` — `_seed_uaa(…, "PR04", …, position 4)` dans le module pratique (additif)
- `tests/test_ticket205_ampcr_pratique_pr04.py` (25 tests) ; comptages adaptés dans
  `tests/test_admin_content_hierarchy.py` et `tests/test_ticket204_ampcr_pratique_pr03.py`
- `docs/current_state.md`, `docs/ampcr_pratique_v1.md`, `docs/changelog.md`

## 2. Liens pour tester

- Cours : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr04
- S'entraîner (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr04/practice
- Examen blanc /20 (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr04/exam
- Accueil du parcours pratique : https://jury-central.lodylands.com/ampcr-pratique
- Matrice : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte : ouvrir le cours, parcourir les séquences (chapitres 1 → 13, cas,
exercices) ; lancer une session « S'entraîner » (10 exercices tirés des 16, dont des remises
en ordre et des classements auto-corrigés) puis un « Examen blanc » (10 questions, note sur
20) ; vérifier la correction et le barème après envoi.

## 3. Vérifications effectuées

- Tests ciblés `tests/test_ticket205_ampcr_pratique_pr04.py` : **25 passed** — décision sur
  les données (jamais d'effacement sans accord écrit, sauvegarde d'abord), techniques
  d'effacement par support (formatage rapide, passes sur SSD et défragmentation refusés),
  verdicts SMART / batterie / températures, opérations, procédures (ordre), tri des déchets,
  schémas (validité, accessibilité, repères et étapes = données), remises en ordre et
  classements auto-corrigés, absence de question d'acronyme et d'affirmation fausse, matière du
  ticket présente, 5 procédures et 4 cas, examen absent du cours, seed idempotent, réserves
  séparées, contexte de correction, pages, sessions entraînement/examen, note /20, aucune
  génération IA.
- **Suite complète : 2525 passed** (une seule exécution, `seed.py` étant partagé).
- `ruff check` sur les fichiers modifiés : aucune erreur.
- Contrôle visuel (navigateur sans interface, 420 px de large) des 9 schémas ; la vue annotée a
  été corrigée après ce contrôle (repères qui chevauchaient les libellés).
- Installation : arbre propre sur `develop`, sauvegarde de la base
  (`~/.local/state/jury-central-orch/backups/jury_central-pre-ticket205-20261027-001638.db`),
  fast-forward `61728c6 → 965b29b`, seed idempotent (1 UAA créée ; les 72 blocs « créés » =
  20 blocs PR04 + le remplacement habituel des 52 blocs FSE pilotés par le code, sans doublon),
  redémarrage des deux services (actifs), `/health` local et public OK, pages du cours, de
  l'accueil, de la matrice, de PR03 et PR06 en HTTP 200 (entraînement/examen : 303 vers la
  connexion, normal sans session), « 10 cours publiés » sur l'accueil, 16 cartes d'exercice et
  9 figures servies. Compteurs utilisateurs/sessions/réponses inchangés (18 / 81 / 638).

Non effectué : validation pédagogique humaine (au propriétaire) ; passage d'une session réelle
avec la vraie correction IA (les tests utilisent `FakeAIProvider`) ; capture pleine page mobile
du cours installé (même composant de page que les cours déjà publiés).

## 4. Choix techniques faits seul

- **Pas de photographie ni d'image générée** : le ticket demande des « photos annotées » ; elles
  sont remplacées par une **vue annotée schématique** (SVG, repères numérotés = données testées),
  comme pour PR01-PR03 : une image générée risquerait de montrer des composants faux, et aucune
  photo libre de droits vérifiée n'est disponible sur le serveur. Les **formulaires** demandés
  sont la fiche de réception, la check-list de remise, le certificat d'effacement et le plan du
  rapport (tableaux imprimables).
- **Effacement** : principes de NIST SP 800-88 (effacer / purger / détruire), formulés sans
  citer de logiciel commercial ; « une passe suffit sur un disque dur récent » ; sur SSD,
  commande intégrée (effacement sécurisé / Sanitize / NVMe Format) ou effacement cryptographique.
- **Seuils signalés comme conventions du cours, pas des normes** : SMART (HDD : secteurs en
  attente/illisibles > 0 → à remplacer, réalloués > 0 → à surveiller ; NVMe : usure ≥ 100 %,
  erreurs ou réserve sous le seuil → à remplacer, ≥ 80 % → à surveiller), batterie à remplacer
  sous 80 % de la capacité d'origine, température « à surveiller » à moins de 10 °C de la limite
  (seuil repris de PR03).
- **Déchets** : filières belges (Recupel, Bebat, recyparcs) puisque le Jury est en Fédération
  Wallonie-Bruxelles.
- **Décision sur les données codée** (`data_decision`) et utilisée pour calculer les réponses
  du classement E05 : l'énoncé, l'arbre et le corrigé ne peuvent pas diverger.
- **Recouvrement limité** : montage/démontage renvoyés à PR03, connecteurs et sécurité
  électrique à PR02, diagnostic complet à PR06, stockage (partitions, formatage) à PR05 (renvoi
  en texte, PR05 n'étant pas encore publié), installation des systèmes à PR08/PR09.
  Exigences : celles du plan installé (AP-14 + complément AP-C03) ; statut « partiel » dans la
  matrice, jamais « validé ».
- Mêmes moteur, réserves `practice`/`exam`, format d'exercice et mise en forme que les cours
  pratiques déjà publiés ; pas de nouvelle dépendance.

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Éléments restant à réaliser

- Validation pédagogique et visuelle par le propriétaire.
- Suite de l'ordre pédagogique : PR05 (#206), puis EX01 (#230) après PR06.
- Améliorations repérées, non implémentées (hors périmètre) : (1) le cours PR03 cite PR04 en
  texte ; un lien vers `/uaa/ampcr-pratique-pr04` pourrait maintenant être ajouté ; (2) dans
  l'arbre de décision partagé (`decision_tree_svg`), l'étiquette « NON » chevauche la flèche
  sur mobile (déjà signalé pour PR02/PR03/PR06).
