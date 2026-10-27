# Ticket #219 — [AMPCR pratique PR18] Installation physique d'un mini-réseau

- Ticket : https://github.com/ReC82/jury-central/issues/219
- **État réel : Installé — à tester**
- SHA installé : `6a8a2a3cd891fc270f860aa9539adafefa2b7000` (fusion de la PR #285 dans `develop`)
- Date : 2026-10-27 (session jcorch autonome)

## 1. Résultat

Le cours **PR18 « Installation physique d'un mini-réseau »** est publié dans le parcours
**Informatique AMPCR → Pratique écrite** (module `AMPCR-PRATIQUE`), séparé de la théorie MC
(cours, banque, examen et progression distincts ; liens seulement vers MC14 et MC15). Il occupe
la position 18 de l'ordre pédagogique : après PR17 et l'examen blanc EX03, avant PR20.

**Numérotation vérifiée** : dans le plan installé (`_COURSE_ROWS`, numérotation définitive de
#236), l'emplacement PR18 porte bien le sujet du ticket (« PR18, ticket 219, Installation physique
d'un mini-réseau », exigences officielles AP-36 et AP-38). Aucun autre cours touché ni renuméroté.

### Contenu (18 blocs)

**11 chapitres**, chacun avec objectifs, théorie, procédure professionnelle à rédiger, erreur
fréquente, attendu « à l'écrit », repère rapide et renvoi aux exercices liés :

1. **Besoin et plan des locaux** : questions à poser, relevé du plan (cotes, arrivée de
   l'opérateur, local, chemins, câbles électriques, perturbations).
2. **Topologie en étoile et implantation** : switch au centre, box à l'arrivée de l'opérateur,
   point d'accès en hauteur au centre de la zone, prises (deux par poste), baie, chemins.
3. **Choix du support** : cuivre ≤ 100 m (U/UTP, F/UTP si terre assurée), fibre au-delà ou entre
   bâtiments, coaxial 75 Ω pour vidéo et TV (règle de PR13 réutilisée).
4. **Longueurs, cheminement, repérage** : longueur = parcours le long des murs + 3 m + 2 m,
   lien permanent ≤ 90 m, boîtes de 305 m sans raboutage, repère B1-P1-07 aux deux bouts.
5. **Sécurité et séparation du courant fort** : EN 50174-2 (classes a 300, b 100, c 50, d 10 mm ;
   inconnue 300 mm), cloison, angle droit, détecteur avant de percer, coupe-feu.
6. **Baie, panneau de brassage, keystones** : 2 keystones par lien (panneau vide), une seule norme,
   ordre dans la baie, unités (1 U = 44,45 mm), réserve 25 %.
7. **PoE** : 802.3af/at/bt, puissance réservée par classe, budget total du switch.
8. **Plan de câblage, nomenclature, devis** : plan de brassage, liste du matériel, devis HT,
   TVA 21 %, TTC.
9. **Tests de continuité et certification** : testeur, qualificateur, certificateur ; lecture
   câblage → longueur → performances.
10. **Configuration de base et validation** : box, switch, postes ; contrôles dans l'ordre lien →
    adresse → passerelle → autre poste → Internet → partage.
11. **Documentation et réception** : dossier de recette, PV signé, réserves.

**3 procédures illustrées** : installer un mini-réseau de l'étude à la réception (8 étapes) ;
tester et certifier le câblage (6) ; valider le réseau dans l'ordre (7).

**5 cas résolus de plans de salles et choix du matériel** : cabinet comptable (plan, baie 9 U,
switch 24 ports, devis 1 443,00 € HT / 1 746,03 € TTC) ; salle de classe de 12 PC (16 liens,
switch 24 ports) ; bureaux et atelier (F/UTP, séparation 300 mm) ; agence en PoE (133,6 W :
switchs de 65 et 130 W dépassés, 370 W retenu) ; deux bâtiments (fibre, recette, validation).

**20 exercices corrigés** (le ticket en demande au moins 18), avec contexte, consignes, barème
et corrigé :
- 3 remises en ordre (installation, validation, tests) ;
- 4 classements auto-corrigés (implantation, support, rapport de recette, premier contrôle en échec) ;
- **5 schémas à compléter** (plan des locaux, baie 12 U, chaîne d'un lien, étoile avec second
  bâtiment, plan de brassage), affichés en SVG dans le cours **et** dans les sessions (fichiers
  `app/static/img/ampcr-pratique/pr18-*.svg`) ; les réponses ne figurent ni dans le dessin ni
  dans ses attributs ;
- **4 devis/nomenclatures** (nomenclature d'un plan, devis à vérifier avec trois erreurs, choix
  d'un switch ports + PoE, hauteur de baie) ; plus longueurs et commande de câble, sécurité
  courant fort, analyse du besoin, dossier de recette.

**Mini-examen de 10 questions /20** (2 points chacune, réponses libres, onglet « Examen blanc »,
jamais affiché dans le cours) : emplacement de la baie, second bâtiment, nomenclature, devis,
budget PoE, rapport de test, poste en 169.254, courant fort, repère B1-P2-05, baie 9 U.

**8 figures SVG + 5 schémas à compléter**, produits depuis des données testées ; texte
alternatif, légende, mention « schéma non officiel ». **Aucune image générée.**

### Fichiers

- `app/v1/ampcr_pratique_pr18_figures.py` — plan d'exemple, calculs (`run_length_m`,
  `switch_ports_needed`/`choose_switch`, `panels_needed`, `rack_units`/`choose_rack`,
  `boxes_needed`, `poe_budget_w`/`poe_verdict`, `quote_totals`/`euro`, `link_verdict`,
  `validation_diagnosis`), figures et schémas statiques ; règles de PR13 (choix, séparation,
  repère) et longueurs de PR15 importées.
- `app/v1/ampcr_pratique_pr18_bank.py` — 20 exercices et 10 questions d'examen, nombres calculés.
- `app/v1/ampcr_pratique_pr18_course.py` — les 18 blocs.
- `app/v1/ampcr_pratique_bank.py` — déclaration de PR18 et contexte de correction IA propre.
- `app/seed.py` — `_seed_uaa(…, "PR18", …, position 18)`, ajout seul.
- `app/static/img/ampcr-pratique/pr18-*.svg` (5 fichiers).
- `tests/test_ticket219_ampcr_pratique_pr18.py` (30 tests) ; comptages adaptés dans
  `tests/test_admin_content_hierarchy.py` et `tests/test_ticket218_ampcr_pratique_pr17.py`.
- `docs/current_state.md`, `docs/ampcr_pratique_v1.md`, `docs/changelog.md`.

## 2. Liens pour tester

- Cours : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr18
- S'entraîner (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr18/practice
- Examen blanc /20 (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr18/exam
- Accueil du parcours : https://jury-central.lodylands.com/ampcr-pratique
- Matrice : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte :
1. Ouvrir le cours, parcourir les 18 séquences (chapitres, cas résolus, exercices avec les 5 schémas à compléter).
2. « S'entraîner » : 10 exercices tirés des 20 (les schémas à compléter s'affichent dans la question).
3. « Examen blanc » : 10 questions, note sur 20 ; après l'envoi, vérifier corrigé et barème.

## 3. Vérifications effectuées

- **Tests ciblés** `tests/test_ticket219_ampcr_pratique_pr18.py` : **30 passed** — calculs
  recontrôlés indépendamment (longueurs depuis le plan, jamais en diagonale ; ports, panneaux,
  baie, boîtes sans raboutage ; PoE ; devis, TVA, format des montants ; verdicts de recette ;
  ordre de validation) ; figures (validité, accessibilité, données dessinées) ; schémas à
  compléter sans leurs réponses et fichiers statiques identiques au SVG généré ; exercices
  (format du socle, auto-correction, nombres des corrigés, 5 schémas + 4 devis) ; cours
  (matière du ticket, 5 cas, 3 procédures, examen absent, liens, pas de lien vers PR19/21/23
  non publiés) ; seed idempotent et position ; réserves séparées ; contexte de correction ;
  pages ; sessions d'entraînement et d'examen /20 sans génération IA.
- **Tests liés** (PR13, PR14, PR17, EX03, socle #192, numérotation #236, hiérarchie admin) : **192 passed**.
- **Suite complète** (une exécution, `seed.py` partagé) : **2 882 passed, 1 failed** —
  `tests/test_ticket55_urgent_ampcr_full.py::test_json_autosave_api_never_reveals_correctness`
  (théorie MC01, question tirée au hasard ; repasse relancé seul : hors périmètre, préexistant).
- **`ruff check`** sur les fichiers créés et modifiés : All checks passed.
- **Contrôle visuel** (navigateur sans interface) des 13 schémas et de deux cartes d'exercice
  avec leur schéma ; corrigés pendant la session : chevauchements (titre du plan, libellés des
  petites pièces, nœuds de l'étoile, barres du budget PoE, accolade « canal »).
- **Installation** : arbre propre sur `develop` ; sauvegarde
  `~/.local/state/jury-central-orch/backups/jury_central-pre-ticket219-20261027-104312.db` ;
  avance rapide `48f9240 → 6a8a2a3` ; seed : 1 UAA et 70 blocs créés (18 de PR18 + remplacement
  habituel des 52 blocs FSE) ; deux services actifs ; `/health` local et public OK ; PR18, PR17,
  accueil, matrice et schéma statique en HTTP 200 ; entraînement et examen en 303 vers la
  connexion (normal sans session) ; 20 cartes d'exercice servies ; « 20 cours publiés sur 30 » ;
  compteurs utilisateurs / sessions / réponses inchangés (18 / 83 / 658).

**Non effectué** : validation pédagogique humaine ; session réelle avec la vraie correction IA.

## 4. Choix techniques faits seul

- **Périmètre** : le choix détaillé des câbles reste dans PR13 (règle importée), le brochage et
  le testeur dans PR15, la fibre dans PR17, l'adressage dans PR20, le dépannage dans PR24 ; PR18
  traite l'installation complète au niveau « chantier ». Topologies (PR19), connexion de deux PC
  (PR21) et partages (PR23) sont cités sans lien (non publiés).
- **Conventions du cours**, signalées dans le texte : longueur = parcours horizontal (x + y) +
  3 m + 2 m ; 20 % de ports de réserve + 1 port pour la box ; 25 % d'unités libres ; deux prises
  par poste ; repère B1-P1-07 ; ordre dans la baie ; port n du panneau → port n du switch.
- **Valeurs normées** : 90/100 m (TIA-568, données PR15), EN 50174-2 (données PR13), puissances
  PoE par classe (IEEE 802.3af/at/bt), boîte de 305 m, 1 U = 44,45 mm, TVA belge 21 %.
- **Schémas à compléter** servis en fichiers statiques comme EX01–EX03 (mécanisme existant
  `ExerciseDocument.image`) ; dans le cours, la carte d'exercice de PR06 est réutilisée et le
  SVG inséré avant la description textuelle.
- Prix, plans, appareils et relevés **fictifs**. Pas de nouvelle dépendance.

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Éléments restant à réaliser

- Validation pédagogique et visuelle par le propriétaire.
- Suite de l'ordre pédagogique : PR19 « Topologies, OSI, TCP/IP, NetBEUI et équipements » (#220).
- Signalé (hors périmètre) : le test aléatoire `test_json_autosave_api_never_reveals_correctness`
  (#55) échoue parfois selon la question tirée ; à stabiliser dans un ticket de maintenance.
