# Rapport — ticket #148 : composition desktop des cours (prose étroite, grandes zones vides)

- **Ticket** : #148 — « P0 — Corriger la composition desktop des cours : prose étroite et
  grandes zones vides » — https://github.com/ReC82/jury-central/issues/148
- **État réel** : Installé — à tester
- **SHA installé** : `757efb4` (merge de la PR #156)
- **Date** : 21/10/2026

---

## 1. Cause trouvée (DOM et styles calculés sur le site installé)

Mesure faite dans Chromium (1366 px de large) sur https://jury-central.lodylands.com/uaa/fse-fse02,
toutes séquences affichées :

| Élément | Largeur réelle | `max-width` calculée |
|---|---|---|
| `main.container` | 1140 px | 1140 px |
| `.jc-card.jc-card--theory` | 1116 px | aucune |
| `.jc-card-body` / `.content-markdown` | 1062 px | aucune |
| **`.jc-prose`** | **713 px** | **712,6 px (= `70ch`)** |

La règle `.jc-prose { max-width: 70ch; }` (ticket #120, gardée alignée à gauche au #126)
plafonnait le texte à ~710 px dans une carte de 1062 px : **~350 px de vide à droite** sur
toute la hauteur de la théorie (1257 px de haut pour FSE02). Aucune grille ni héritage en
cause : c'est le plafond porté par le texte lui-même.

Relevé sur les 63 cours publiés (même outil) : le défaut touchait **FSE02, FSE05 à FSE16**
(prose de 400 à 1250 px de haut, toujours à 713 px de large) et, en plus petit, **FSE03**
(« Qui suis-je ? », 174 px). AMPCR, Français, FSE01, FSE04, FSE17 et Mathématiques n'utilisent
pas ce composant de cette façon : aucun bloc étroit et haut détecté.

## 2. Correction (la cause, pas une surcharge de plus)

1. **`.jc-prose` ne porte plus de largeur** (`max-width: none`, aucune marge automatique). La
   largeur de lecture vient désormais de la composition qui contient le texte.
2. **Théorie FSE05 → FSE16 : explication + « Les mots clés » côte à côte.** La prose occupe la
   colonne principale (~640 px, soit la largeur de sa cellule), les cartes de définitions
   forment une colonne à droite. Si les définitions sont nombreuses face à une prose courte
   (FSE06, FSE12), la colonne des mots clés s'élargit et range ses cartes sur deux colonnes,
   pour éviter une colonne deux fois plus haute que le texte. Les schémas (FSE08 niveaux de
   pouvoir, FSE15 circuit économique) restent en pleine largeur, sous cette composition.
   Empilé sous 992 px (tablette, téléphone) et à l'impression.
3. **FSE02 recomposé en groupes pédagogiques** (séquence 2 « Théorie : notions et définitions ») :
   - *Média et offre médiatique* : explication + exemple, mots clés Média / Offre médiatique ;
   - *L'interactivité* : explication + mot clé, puis deux cartes « Réagir directement » /
     « En différé, ou pas du tout » (courrier des lecteurs publié la semaine suivante ; journal
     papier, radio sans ligne ouverte) ;
   - *Quatre modes de financement* : quatre cartes Vente / Abonnement / Publicité / Fonds
     publics (définition, « Qui paie ? », exemple), avec le rappel « souvent combinés » ;
   - *Le financement influence le média* : trois cartes (publicité → recherche d'audience,
     fonds publics exclusifs, payant → fidélité), puis l'encadré « Attention : le financement
     mixte » (nuance RCW conservée mot pour mot) à côté du mot clé Audience ;
   - *Un flux économique entre agents* : explication + encadré « Qui verse à qui ? »
     (ménage, entreprise, État).
   Aucune notion ajoutée ; les 8 définitions d'origine restent présentes et la séquence
   « À retenir » (#136) les relit toujours.
4. **FSE03 « Qui suis-je ? »** : le second paragraphe étroit devient explication (identité
   numérique) + repère (« plusieurs groupes à la fois, jamais contradictoire »).
5. **Cartes de texte seul** (présentation et objectifs, méthode, sources…) : au lieu d'étirer
   les lignes sur ~1060 px (~140 caractères), la **carte entière** (bandeau, titre, texte) prend
   une largeur de lecture de 50 rem (~800 px), centrée dans la colonne du cours. Détection côté
   serveur : le HTML rendu ne contient que paragraphes, listes et mises en évidence (pas de
   tableau, image, schéma, grille ni titre de section `<h2>`). Les cours AMPCR et Français en
   un seul bloc (avec titres `<h2>`, tableaux) ne sont donc pas modifiés.
6. **Actualisation du contenu déjà seedé** : les blocs « FSE0x — Théorie : notions et
   définitions » (FSE02, FSE05-16) étaient déjà remplacés à chaque seed ; « FSE03 — Qui
   suis-je ? » a été ajouté à cette liste. Le seed idempotent a été exécuté à l'installation.

### Fichiers modifiés

- `app/static/css/design-system.css` — `.jc-prose` sans plafond ; `.jc-theory-layout`
  (+ variante `--wide-aside`) ; `.jc-theory-group-title` ; cartes `.jc-fund-card` ;
  `.jc-card--reading`.
- `app/v1/fse_course_sections.py` — `theory_and_definitions_to_cards()` compose prose + mots clés.
- `app/v1/fse02_course.py` — `fse02_theory_html()` (groupes pédagogiques).
- `app/v1/fse03_course.py` — « Qui suis-je ? » : explication + repère.
- `app/content.py` — `is_text_only_html()` ; `app/main.py` — marque les blocs texte seul ;
  `app/templates/_lesson_blocks.html` — classe `jc-card--reading`.
- `app/seed.py` — « FSE03 — Qui suis-je ? » rafraîchi au seed.
- Tests : `tests/test_ticket148_composition_desktop.py` (10 tests) ; deux assertions
  devenues obsolètes mises à jour (`test_ticket124…` : plus de `70ch` ; `test_ticket120…` :
  la page porte `jc-theory-layout`).
- `docs/current_state.md`.

## 3. Liens pour tester

- FSE02, séquence 2 : https://jury-central.lodylands.com/uaa/fse-fse02 (bouton « 2 »)
- FSE05 (mise en page générique) : https://jury-central.lodylands.com/uaa/fse-fse05
- FSE12 (beaucoup de définitions) : https://jury-central.lodylands.com/uaa/fse-fse12
- FSE08 (schéma pleine largeur) : https://jury-central.lodylands.com/uaa/fse-fse08
- FSE03 « Qui suis-je ? » : https://jury-central.lodylands.com/uaa/fse-fse03
- Carte de texte seul : séquence 1 de n'importe quel cours FSE (ex. FSE02 ci-dessus)

Procédure courte : sur ordinateur, ouvrir FSE02, séquence 2 → vérifier qu'il n'y a plus de
colonne de texte étroite avec un vide à droite ; cliquer « Afficher tout le cours sur une
page » ; réduire la fenêtre (ou téléphone) → tout s'empile ; Ctrl+P → aperçu d'impression.

## 4. Vérifications

- **Navigateur réel (Chromium headless, Playwright hors dépendances du projet)**, sur une copie
  locale seedée en base temporaire : FSE02 (séquences 1 et 2, 1366 px ; 390 px ; rendu
  impression), FSE03, FSE05, FSE08, FSE12. Captures examinées une par une ; trois déséquilibres
  repérés et corrigés avant livraison (colonne de mots clés trop haute pour FSE06/FSE12, encadré
  « financement mixte » trop haut dans la colonne de droite, mot clé seul à côté de deux cartes).
- Mesure automatique sur les 15 cours FSE02-16 : plus aucun bloc de prose étroit et haut ;
  hauteurs explication / mots clés équilibrées (écart maximal ~1,25 pour FSE08/FSE10).
- Après installation : mêmes contrôles sur le site réel — voir § 7.
- Tests : `tests/test_ticket148_composition_desktop.py` (10) + tests FSE/À retenir liés ;
  suite complète : **1795 passed** (une seule exécution, main.py et seed touchés).
- Ruff : aucune nouvelle erreur sur les fichiers modifiés.
- **Non vérifié** : vrai appareil physique, lecteur d'écran, impression papier réelle (seul
  l'aperçu « print » de Chromium a été contrôlé).

## 5. Choix techniques faits seul

- **Largeur portée par la composition, pas par le texte** : c'est ce que demandait le ticket
  (« dans une cellule, prose à largeur de cellule ; pour texte seul, adapter ensemble
  contenant/titre/synthèse »). Aucun `margin: auto` sur la prose.
- **Définitions en colonne « Les mots clés »** plutôt qu'en grille pleine largeur sous la
  prose : elles remplissent la zone qui était vide et restent visibles sans clic.
- **Carte de texte seul centrée à 50 rem** : la carte, son bandeau et son titre se réduisent
  ensemble ; centrée pour ne pas recréer un vide d'un seul côté. Désactivé à l'impression.
- **Seuil d'élargissement de la colonne des mots clés** calculé sur la longueur des
  définitions (+ coût fixe par carte) face à la prose ; s'applique aujourd'hui à FSE06 et FSE12.
- FSE02 garde **un seul bloc de théorie** (même séquence 2/7) : pas de changement de
  numérotation des séquences ni de progression mémorisée.
- Hors du composant fautif, **les cartes d'exemples, de comparaison et d'exercices n'ont pas
  été retouchées** (pas de colonne étroite, déjà jugées satisfaisantes au #126).

## 6. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 7. Installation

- `develop` à `30fa217` → `757efb4` (fast-forward), sauvegarde de la base avant installation
  (dossier de sauvegardes de l'orchestrateur, `jury_central-pre-ticket148-20261021-231543.db`).
- Seed idempotent : 52 blocs recréés (blocs de théorie FSE rafraîchis), aucun compte ni
  progression touchés ; compteurs utilisateurs/sessions/réponses **18 / 71 / 584** avant et
  après (inchangés).
- Services `jury-central` et `jury-central-correction-worker` actifs ; `/health` local et
  public OK ; 8 pages de cours (FSE02, 03, 05, 08, 12, AMPCR MC05, Français FR02, Maths) en 200.
- Contrôle navigateur sur le site réel : FSE02 séquence 2 conforme aux captures locales ;
  mesure automatique sur FSE01-FSE17 : plus aucun bloc de prose étroit et haut (17/17).

## 8. Reste à faire / signalé

- Validation visuelle par le propriétaire (ordinateur, téléphone, impression).
- Signalé, hors périmètre : dans les cours AMPCR et Français (un seul grand bloc avec titres
  et tableaux), les paragraphes occupent toujours toute la largeur de la carte (~140 caractères
  par ligne sur grand écran). Ils n'ont pas de vide à droite mais des lignes longues ; une
  composition propre demanderait de traiter ces cours section par section (ticket dédié
  possible).
- Signalé : dans les cartes d'exemples FSE, l'analyse « Décryptons ce document » s'étend aussi
  sur toute la largeur ; une mise en page document + analyse côte à côte relèverait plutôt
  de #149 (documents lisibles).
