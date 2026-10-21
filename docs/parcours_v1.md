# Parcours et habillage « parcours de jeu » (ticket #136)

Reprend la navigation demandée par #67 (accueil, en-tête, CESS → CESS P → Informatique)
et l'étend à une expérience complète : accueil → choix du parcours → tableau de bord →
matière (chemin de cours) → cours en séquences → entraînement / examen blanc → résultat.

## Modèle

| Notion | Où elle vit | Exemple |
|---|---|---|
| Diplôme | `app/v1/parcours.py::REGISTRY` (`DiplomaDef`) | CESS |
| Forme | `FormDef` | CESS P (professionnel) ; CESS G et TQ affichés « pas encore de contenu » |
| Option (OBG) | `OptionDef` | Assistant/Assistante de maintenance PC-réseaux (AMPCR) |
| Matière du parcours | `SubjectTrack` → relié à un **Module existant par son code** | AMPCR (option), FRANCAIS et FSE (formation commune) |
| Cours / chapitre | UAA publiées en base (jamais déclarées dans le registre) | MC01…MC38, FR01…FR05, FSE01…FSE17 |

Le registre ne crée aucun contenu. `planned_count` sert seulement à afficher « x cours
disponibles sur y prévus ». Les modules présents en base mais non rattachés à l'option
(Mathématiques MB32) sont listés « hors de ce parcours ».

Choix mémorisé : table `v1_user_pathways` (une ligne par compte, créée par `create_all`)
et session signée pour un visiteur ; un choix fait avant connexion est conservé à la
connexion (`login_user`) puis rattaché au compte à la visite de `/mon-parcours`. Changer
de parcours ne modifie aucune session, réponse ni rating.

## Routes

- `/` — accueil : « Choisir mon parcours » ou « Continuer mon parcours » + tuiles.
- `/parcours` (`?diplome=…&forme=…`) — assistant en 3 étapes ; `POST /parcours/choisir` (CSRF).
- `/mon-parcours` — tableau de bord : reprise d'une session en cours, prochaine étape,
  tuiles de matières avec progression réelle, contenus manquants.
- `/subjects`, `/subjects/{slug}`, `/modules/{slug}` — mêmes routes, habillées en tuiles et
  en chemin de cours (accès direct à chaque cours, aucun verrou).
- `/uaa/{slug}` — cours en séquences (`app/static/js/lesson_sequences.js`), cours
  précédent/suivant ; onglets Cours / S'entraîner / Examen blanc (mêmes routes).

## Progression (jamais confondue)

| Libellé | Source | Portée |
|---|---|---|
| Consulté / Lu jusqu'au bout | `progress.js` (localStorage) | cet appareil |
| Entraîné ×n | sessions PRACTICE `COMPLETED` dont toutes les questions viennent du cours | compte |
| Examen blanc réussi (x %) | meilleure session EXAM `COMPLETED`, score ≥ 50 % | compte |
| Session en cours | session `IN_PROGRESS` la plus récente | compte |

Une correction incomplète ne compte jamais comme réussite. Les sessions transversales
(scope MC38 / FSE17) sont attribuées à leur cours de révision. Aucune « maîtrise » n'est
affichée ; la progression est un repère personnel, pas une note officielle.

## Leçon en séquences

`lesson_sequences.js` regroupe l'affichage existant, sans rien retirer : une séquence par
`<h2>` pour un cours en un seul bloc (AMPCR, Français), une séquence par carte pour un cours
en plusieurs cartes (FSE, Mathématiques). Chaque séquence porte une étape Comprendre /
Observer un exemple / Essayer / Retenir déduite de son titre. « Afficher tout le cours sur
une page » restaure la lecture continue ; sans JS et à l'impression, tout est visible.

## Bibliothèques (CDN jsDelivr, versions figées + SRI)

| Bibliothèque | Licence | Usage | Poids |
|---|---|---|---|
| Bootstrap Icons 1.11.3 | MIT | icônes de navigation, états, tuiles | ~86 Ko CSS + police |
| Lexend (Fontsource 5.1.1, 500/700) | SIL OFL 1.1 | titres (police conçue pour la lisibilité) | 2 fichiers woff2 latin |
| canvas-confetti 1.9.3 | ISC | célébration d'un résultat ≥ 70 %, chargée seulement dans ce cas, coupée si animations réduites | ~11 Ko |

Bootstrap 5.3.3 (MIT) reste la base. Aucune bibliothèque spécialisée par matière n'a été
ajoutée à ce stade : voir le rapport du ticket pour les suites proposées.

## Illustrations

`python -m app.v1.parcours_images [--only …] [--force] [--output-dir …]` génère via
l'intégration OpenAI existante (`get_image_provider`) l'illustration d'accueil et une par
matière, en WebP recadré (960×540 / 1200×800) avec un `.json` (prompt, modèle, date).
Jamais appelée au seed, au démarrage ou à la consultation ; une image présente n'est pas
régénérée sans `--force` ; quota insuffisant signalé et série arrêtée. Sans fichier, les
templates affichent une icône (`static_exists`).
