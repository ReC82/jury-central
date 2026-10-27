# Ticket #227 — [AMPCR pratique PR28] Outillage, sécurité et protection des données

- Ticket : https://github.com/ReC82/jury-central/issues/227
- **État réel : Installé — à tester**
- SHA installé : `433f8c37ac18f5dc79d68edc9978bf8b6d395a54` (fusion de la PR #315 dans `develop`)
- Date : 2026-10-27 (session jcorch autonome)

## 1. Résultat

Le cours **PR28 « Outillage, sécurité et protection des données »** est publié dans le parcours
**Informatique AMPCR → Pratique écrite** (module `AMPCR-PRATIQUE`), séparé de la théorie MC
(cours, banque, examen et progression distincts ; liens seulement vers MC05, MC06 et MC32). Il
occupe la position 28, juste après PR27.

**Numérotation vérifiée** : dans le plan installé (`_COURSE_ROWS`, numérotation de #236),
l'emplacement PR28 porte bien le sujet du ticket (« PR28, ticket 227, Outillage, sécurité et
protection des données », compléments **AP-C02** « Sécurité électrique et protection ESD » et
**AP-C03** « Protéger les données du client »). Le cours s'appuie aussi sur les exigences
officielles **AP-14** (montage, démontage) et **AP-20** (précautions d'utilisation des câbles,
connecteurs), et AP-21 pour la fibre. Aucun autre cours n'a été touché ni renuméroté.

### Contenu (15 blocs)

**8 chapitres**, chacun avec objectifs, théorie, procédure professionnelle, erreur fréquente,
attendu « à l'écrit », repère rapide et renvoi aux exercices liés :

1. **Outillage PC** : tournevis, pinces, bracelet et tapis ESD *selon la procédure*, testeur
   d'alimentation (outil autorisé, ne prouve pas la tenue en charge), multimètre avec ses
   précautions (procédure en 5 points, pile CMOS 3 V), pâte thermique, outils de nettoyage ;
   rappel des tolérances ATX de PR02.
2. **Outillage réseau** : dénudeur, sertisseuse 8P8C, outil d'insertion 110/LSA, testeur
   wiremap (jamais sur un port PoE actif), outils BNC, kit de nettoyage fibre, localisateur
   visuel ; **sécurité laser et éclats de fibre**.
3. **Électricité, bloc d'alimentation (jamais ouvert), débranchement, ESD** (poste antistatique
   numéroté).
4. **Batteries endommagées, ventilation, risques mécaniques, poste de travail**, dépoussiérage
   et pâte thermique (à faire / interdit).
5. **Données du client** : confidentialité, mot de passe d'autrui, intégrité par empreintes
   SHA-256, chiffrement (BitLocker, clé de récupération de 48 chiffres, suspension avant mise à
   jour du firmware), droits ; RGPD (le client reste responsable de ses données).
6. **Sauvegarde 3-2-1 (présentée comme complément)** et **autorisation avant effacement ou
   réinstallation** (tableau des prérequis par opération).
7. **Fin de vie** : DEEE, piles et batteries, supports de données (effacement certifié ou
   destruction), cartouches.
8. **Fiche sécurité** (modèle rempli), **choix d'outil selon l'intervention** (tableau des
   kits), **liste de contrôle** avant / pendant / après, **gestion d'incident** (procédure +
   arbre).

**5 interventions entièrement résolues** (ticket : 5) — dépoussiérage et pâte thermique,
batterie gonflée, réinstallation du PC d'un comptable (3-2-1, empreintes, prérequis), prise
murale + jarretière optique, vidage d'une réserve (effacement et filières). Chacune : risques,
outils, avant / pendant / après, données, incident, conclusion rédigée.

**22 exercices corrigés** (ticket : ≥ 18) : 4 choix d'outil, 3 risques et sécurité, 4
procédures à ordonner (auto-corrigées), 5 protection des données, 1 fin de vie, **2 schémas à
compléter** (poste antistatique, arbre d'incident), 1 parcours d'arbre, 2 rédactions (fiche
sécurité, incident de données).

**Mini-examen de 10 questions /20** (2 points chacune, réponses libres, onglet « Examen blanc »,
jamais affiché dans le cours) : kit pour un bloc, mesures du testeur, smartphone qui gonfle,
erreurs d'une procédure de dépoussiérage, plan de sauvegarde, copie à vérifier, réinstallation
d'un portable chiffré, connecteur optique, matériel usagé, fumée pendant un test.

**Visuels (« illustrations sûres »)** : 14 figures SVG (2 inventaires d'outils, 5 procédures,
poste antistatique, sécurité fibre, nettoyage, règle 3-2-1, filières, liste de contrôle, arbre
d'incident) + 2 schémas à compléter en fichiers statiques. **Aucune image générée, aucun geste
dangereux montré** : tout est dessiné depuis les données du cours.

### Fichiers

- `app/v1/ampcr_pratique_pr28_figures.py` — règles (`TOOLS`/`TASKS`/`INTERVENTIONS`/`kit`,
  `RISKS`, procédures, `check_321`, `fingerprint`/`compare_copy`, `required_prerequisites`/
  `missing_prerequisites`, `waste_route`, `INCIDENT_TREE`), 5 interventions `CASES`, schémas ;
  réutilise les tolérances de PR02, la décision et les techniques d'effacement de PR04, le
  format d'arbre de PR27.
- `app/v1/ampcr_pratique_pr28_bank.py` — 22 exercices et 10 questions d'examen.
- `app/v1/ampcr_pratique_pr28_course.py` — les 15 blocs.
- `app/v1/ampcr_pratique_bank.py` — déclaration de PR28 et contexte de correction IA propre.
- `app/seed.py` — `_seed_uaa(…, "PR28", …, position 28)`, ajout seul.
- `app/static/img/ampcr-pratique/pr28-*.svg` (2 fichiers).
- `tests/test_ticket227_ampcr_pratique_pr28.py` (36 tests) ; comptage adapté dans
  `tests/test_admin_content_hierarchy.py`.
- `docs/current_state.md`, `docs/ampcr_pratique_v1.md`, `docs/changelog.md`.

## 2. Liens pour tester

- Cours : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr28
- S'entraîner (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr28/practice
- Examen blanc /20 (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr28/exam
- Accueil du parcours : https://jury-central.lodylands.com/ampcr-pratique
- Matrice : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte :
1. Ouvrir le cours, parcourir les 15 séquences (chapitres, cinq interventions, exercices).
2. « S'entraîner » : 10 exercices tirés des 22 (schémas à compléter et documents dans la
   question).
3. « Examen blanc » : 10 questions, note sur 20 ; après l'envoi, vérifier corrigé et barème.

## 3. Vérifications effectuées

- **Tests ciblés** `tests/test_ticket227_ampcr_pratique_pr28.py` : **36 passed** — inventaire
  (un outil par tâche, précautions clés), kits (chaque outil utilisé), risques, ordre du
  débranchement, tolérances recontrôlées, règle 3-2-1 (cas limites), empreintes SHA-256
  (valeur de référence de `sha256("abc")`), intégrité d'une copie, prérequis avant effacement,
  filières, arbre d'incident ; cinq interventions et leurs valeurs calculées ; figures
  (validité, accessibilité, données dessinées), schémas à compléter sans leurs réponses,
  fichiers statiques identiques ; exercices (format du socle, auto-correction, valeurs des
  corrigés) ; matière du ticket, liens, types de cartes, seed idempotent et position, réserves
  séparées, contexte de correction, pages, sessions d'entraînement et d'examen /20 sans
  génération IA.
- Avec les voisins (PR26, PR27, #236, #299, #302, #192, PR12, hiérarchie admin) : **251 passed**.
- **Suite complète** (une exécution, `seed.py` partagé) : **3 196 passed**, aucun échec (27 min).
- **`ruff check`** sur les fichiers créés et modifiés : All checks passed.
- **Contrôle visuel** (Chromium sans interface) de toutes les figures, puis des séquences
  rendues par l'application sur une base de test temporaire, en largeur bureau et mobile
  (390 px). Corrigé pendant la session : listes « à faire / interdit » qui se chevauchaient
  (nouveau schéma pleine largeur), repères écrits retirés du schéma à compléter (ils donnaient
  la réponse), majuscules perdues dans les filières, nombre de disques incohérent dans
  l'intervention 5, renvoi « document 1 » d'un exercice à deux documents. Sur mobile, les
  tableaux larges défilent horizontalement (comme PR26/PR27).
- **Installation** : arbre propre sur `develop` ; sauvegarde `~/.local/state/jury-central-orch/backups/jury_central-pre-ticket227-20261027-195803.db` ; avance rapide `7fd4d2b → 433f8c3` ; seed : 1 UAA et 67 blocs créés (15 de PR28 + remplacement habituel des 52 blocs FSE) ; deux services actifs ; `/health` local et public OK ; PR28, PR27, accueil, matrice et les 2 schémas statiques en HTTP 200 ; entraînement en 303 vers la connexion (normal sans session) ; 22 cartes d'exercice servies ; « 28 cours publiés sur 30 » ; compteurs utilisateurs / sessions / réponses inchangés (18 / 84 / 661).

**Non effectué** : validation pédagogique humaine ; session réelle avec la vraie correction IA.

## 4. Choix techniques faits seul

- **Consignes de sécurité = règles générales de prudence** ; le cours dit explicitement que la
  procédure de l'atelier, le manuel du fabricant et les consignes du site font foi (le ticket
  demande « bracelet/tapis ESD selon procédure », « testeur PSU autorisé »).
- **Règle 3-2-1** : présentée comme **complément** (ticket) ; 3 copies *original compris* ;
  convention prudente du cours pour le « 2 » : disque interne, disque externe et NAS comptent
  comme **un seul type** (disque), l'en-ligne et la mémoire flash comme d'autres types. Écrit
  dans le cours et dans les énoncés concernés.
- **Prérequis avant une opération qui efface** : accord écrit + personne habilitée toujours ;
  sauvegarde vérifiée si des données sont à garder ; clé de récupération si le disque est
  chiffré et le poste remis en service ; licences notées si le poste resservira.
- **Empreintes** : vraies empreintes SHA-256 de contenus fictifs, tronquées à 16 caractères
  (indiqué dans les énoncés).
- **Filières belges** citées comme exemples (« en Belgique : Recupel, Bebat ») ; RGPD art. 33
  (72 h, notification par le client, responsable de ses données) sans détailler de procédure
  juridique.
- **Exigences citées** : AP-C02 et/ou AP-C03 sur chaque item, AP-C01 (réponse de technicien),
  AP-14 pour les interventions dans le matériel, AP-20 pour l'outillage de câblage, AP-21 pour
  la fibre.
- **Réutilisation** plutôt que duplication : tolérances (PR02), décision et techniques
  d'effacement (PR04), format et parcours d'arbre (PR27) ; les cours PR02–PR05, PR12, PR15–PR18,
  PR22, PR23, PR26, PR27 sont liés, pas recopiés.
- **Pas de lien** vers PR29–PR30 (non publiés).

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Éléments restant à réaliser

- Validation visuelle et pédagogique par le propriétaire.
- Suggestions (hors périmètre, non faites) : PR29 (#228) pourra reprendre la liste de contrôle
  « après » et la fiche d'incident de PR28 dans le rapport d'intervention ; le tableau statique
  de `docs/ampcr_pratique_v1.md` affiche encore AP-C02 / AP-C03 « non traité » (la page
  `/ampcr-pratique/matrice` calcule l'état en direct) : à réaligner à l'audit final (#235) ;
  MC05 et MC32 (théorie) pourraient renvoyer vers PR28.
