# Ticket #136 — Refonte ludique et visuelle : Jury Central comme un parcours de jeu accessible

- Ticket : https://github.com/ReC82/jury-central/issues/136 (P0)
- Branche : `feature/136-parcours-ludique` — PR #140 (fusionnée dans `develop`)
- **État réel : Partiel — installé, reste à faire** (tranche 1 livrée, à tester)
- **SHA installé** : `f93c3d7ab7df0132e3d3de49c871552e8b38ba85` (+ commit de rapport/doc, sans redémarrage)

## 1. Synthèse

Première tranche verticale installée et reliée aux vraies données :
**accueil → choix du parcours → Mon parcours → matière (chemin de cours) → cours en
séquences → entraînement / examen blanc → résultat**. Le volet A de #67 (en-tête) est
repris ici sans être dupliqué.

**Illustrations IA non générées** : la clé API OpenAI configurée sur le serveur est refusée
par OpenAI (HTTP 401 `invalid_api_key`). Le générateur est livré et testé ; les pages
affichent en attendant un repli propre (grande icône sur fond coloré), jamais une image
cassée. Voir la décision n° 1.

## 2. Ce qui change à l'écran

- **En-tête** (toutes les pages) : fond clair, logo, icônes ; Accueil · Mon parcours ·
  Matières · Mes entraînements · compte · bouton « Déconnexion » discret. Le lien
  « S'entraîner » (`/practice/equations`) est retiré de l'en-tête (#67 § A) ; la route reste
  servie.
- **Accueil `/`** : bloc d'accueil avec « Choisir mon parcours » (ou « Continuer mon
  parcours » + tuiles des matières si un parcours est mémorisé), trois points clés, accès
  direct aux cours publics.
- **Assistant `/parcours`** : 3 étapes (Diplôme → Forme → Option) avec fil d'étapes.
  CESS → CESS P → « Assistant/Assistante de maintenance PC-réseaux ». CESS G, CESS TQ et
  les autres diplômes sont affichés « pas encore de contenu », non cliquables.
- **Mon parcours `/mon-parcours`** : bandeau « À reprendre » (session en cours) ou
  « Prochaine étape » (premier cours non encore entraîné), tuiles Option / Formation
  commune (Informatique AMPCR, Français, FSE) avec « x cours disponibles sur y prévus »,
  barre « Entraînés x/y » et nombre d'examens blancs réussis, encadré honnête sur ce que
  mesure la progression et sur les contenus manquants (Français : 5 publiés sur 20 prévus),
  Mathématiques signalées « hors de ce parcours ». « Changer de parcours » à tout moment.
- **Matières `/subjects`, `/subjects/{slug}`** : tuiles.
- **Module `/modules/{slug}`** : chemin de cours (jalons numérotés reliés), chaque cours
  avec accès direct Cours / S'entraîner / Examen blanc (seulement si l'espace existe
  réellement : rien pour MB32 qui n'a pas d'entraînement V1), états « Entraîné ×n »,
  « Examen blanc réussi (x %) » / « à retenter », « Session en cours ». MC38/FSE17 mis en
  avant comme jalons de révision. Aucun verrou.
- **Cours `/uaa/{slug}`** : en-tête de matière, onglets Cours / S'entraîner / Examen blanc
  (icônes au lieu d'emojis ; « S'évaluer » devient « Examen blanc », même route), **cours
  découpé en séquences** (une par titre de section pour AMPCR/Français, une par carte pour
  FSE/Maths) avec les étapes Comprendre / Observer un exemple / Essayer / Retenir, pastilles
  numérotées, Précédent / Suivant, « Passer à l'entraînement » à la fin, et « Afficher tout
  le cours sur une page ». Cours précédent / suivant / Tous les cours en bas. Contenu
  intégral conservé (aucun texte retiré ni réécrit) ; sans JS et à l'impression tout
  s'affiche.
- **Résultats** : message de réussite (≥ 50 %) lié au résultat réellement corrigé, petite
  animation de confettis à partir de 70 % (coupée si l'appareil demande moins
  d'animations), message encourageant sous 50 %. Jamais sur une correction incomplète.
- Badges de lecture renommés pour ne pas confondre : « Pas encore ouvert / Consulté / Lu
  jusqu'au bout » (cet appareil) ; « Entraîné » et « Examen blanc réussi » viennent du
  serveur. Bouton « J'ai lu ce cours jusqu'au bout ». Pied de page : la progression est
  indicative, pas une note officielle.

## 3. Liens directs pour tester

1. https://jury-central.lodylands.com/ → « Choisir mon parcours »
2. https://jury-central.lodylands.com/parcours → CESS → CESS P → AMPCR
3. https://jury-central.lodylands.com/mon-parcours (connecté : progression et reprise)
4. https://jury-central.lodylands.com/modules/ampcr (chemin de cours ; aussi `/modules/fse`, `/modules/francais`)
5. https://jury-central.lodylands.com/uaa/ampcr-mc05 (séquences, cours en un bloc)
6. https://jury-central.lodylands.com/uaa/fse-fse04 (séquences par carte, cours FSE)
7. https://jury-central.lodylands.com/subjects
8. Un résultat d'entraînement/examen blanc depuis « Mes entraînements » (message de réussite)

Procédure courte : sans compte, choisir le parcours → le site s'en souvient. Se connecter
→ le choix est rattaché au compte. Ouvrir un cours, parcourir 2-3 séquences, basculer
« Afficher tout le cours », imprimer (aperçu) pour vérifier que tout apparaît. Tester sur
téléphone (menu hamburger, tuiles, chemin).

## 4. Vérifications

- Tests nouveaux `tests/test_ticket136_parcours.py` (16) : registre, assistant, CSRF,
  mémorisation visiteur/compte, rattachement après connexion, changement sans perte,
  progression (entraîné / examen ≥ 50 % / correction incomplète jamais comptée / session en
  cours / scope MC38), espaces proposés seulement s'ils existent, générateur d'images
  (recadrage WebP, pas de régénération, arrêt immédiat sur quota ou clé refusée) — sans
  réseau.
- **Suite complète** (modèles et `app/main.py` touchés) : **1735 passed** avant fusion.
  Deux assertions d'anciens tests mises à jour pour les nouveaux libellés (#22, #47).
- Ruff : aucune nouvelle erreur (les B008 de `app/main.py` préexistent).
- Installation : sauvegarde de la base, fast-forward, redémarrage des 2 services (actifs),
  `/health` local et public OK, 15 pages publiques en HTTP 200, `/mes-sessions` 303 sans
  connexion (normal). Compteurs utilisateurs/sessions/réponses : 18/69/566 avant et après.
- Captures navigateur (Chromium headless, ordinateur 1280 px et téléphone 390 px) des
  pages publiques : accueil, assistant, chemin AMPCR, cours MC05 en séquences, cours FSE04.
  Ces captures montrent la mise en page, pas une validation esthétique : **la validation
  visuelle reste la tienne**. Pages connectées non capturées (pas de session de test sur le
  site réel).

## 5. Choix techniques faits seul

1. **Registre de parcours en code** (`app/v1/parcours.py`), relié aux modules existants par
   leur code (AMPCR, FRANCAIS, FSE) : pas de nouvelle hiérarchie en base (cohérent avec
   l'architecture Subject → Module → UAA). Seule nouvelle table : `v1_user_pathways` (choix
   du compte), créée automatiquement, aucune migration de données.
2. **Composition du parcours CESS P AMPCR** = option + Français + FSE (matières déjà
   présentées comme « CESS P » dans le projet, FSE d'après les consignes 2026-2027/1).
   Les consignes officielles n'ont pas pu être relues : le site des Jurys
   (jurys.cfwb.be) redirigeait vers une page de maintenance ETNIC le 21/10. Voir décision 2.
3. **Progression** calculée uniquement à partir des sessions corrigées ; « réussi » = examen
   blanc ≥ 50 % (seuil CESS P documenté) ; aucune « maîtrise » affichée.
4. **Séquences** : découpage d'affichage côté navigateur, sans toucher au contenu ni aux
   seeds ; étape déduite du titre de section.
5. **Bibliothèques** (CDN jsDelivr, versions figées + SRI, comme Bootstrap) :
   Bootstrap Icons 1.11.3 (MIT), police Lexend via Fontsource 5.1.1 (SIL OFL), canvas-confetti
   1.9.3 (ISC, chargé seulement sur un résultat ≥ 70 %). Aucune bibliothèque spécialisée par
   matière dans cette tranche (chimie/physique n'ont pas de contenu ; voir § 8).
6. **Illustrations** : générateur manuel `python -m app.v1.parcours_images` (accueil + 3
   matières), WebP recadré 960×540 / 1200×800, prompt et modèle conservés en `.json`,
   jamais appelé à la consultation ni au seed, arrêt immédiat si quota/clé refusés.
7. Le libellé « S'évaluer » devient « Examen blanc » (demande du ticket), routes inchangées.

## 6. Décisions demandées au propriétaire

1. **Clé API OpenAI refusée (401 invalid_api_key).** Le générateur d'illustrations n'a pu
   produire aucune image. La même clé sert aussi à la génération/correction IA des
   questions : vérifie qu'elles fonctionnent encore. Options : (a) remplacer la clé dans
   `.env` du serveur (je n'y touche pas), puis la prochaine session relance
   `python -m app.v1.parcours_images` et commite les 4 images ; (b) garder le repli icône.
   **Recommandation : (a).**
2. **Composition officielle de la formation commune CESS P (cycle 2026-2027/1).** Le parcours
   contient Informatique AMPCR + Français + FSE. Faut-il ajouter d'autres épreuves (ex.
   mathématiques MB32 déjà présentes, sciences…) ? Options : (a) confirmer la liste
   actuelle ; (b) me donner la liste exacte (ou le PDF des consignes) ; (c) laisser comme
   ça en attendant. **Recommandation : (b)** — il suffit ensuite d'ajouter une ligne au
   registre ; les matières sans contenu seraient affichées « à venir », jamais comme
   disponibles.

## 7. Restant à réaliser (tranches suivantes de #136)

- Illustrations réelles (dès que la clé fonctionne) et éventuels visuels d'étapes.
- Habillage des pages de session (démarrage, question, attente, confirmation),
  historique, compte, connexion/inscription et lexique avec le même langage visuel.
- Intégration de l'espace Quiz quand #137 existera (aucun bouton tant qu'il n'existe pas).
- Visualisations spécialisées utiles au contenu existant, ex. schémas réseau/topologies
  interactifs pour AMPCR (bibliothèque type Cytoscape.js, MIT) — à évaluer cours par cours.
- Ajustements après ta validation visuelle (couleurs, densité, textes).
