# Rapport — Ticket #115 : extension de la présentation finalisée de FSE01 à FSE02-FSE17

Branche : `feature/115-fse02-17-visual-extension` (depuis `develop`), deux lots fusionnés
(PR #116, PR #117) et installés par lots successifs sur `jury-central.lodylands.com`,
conformément à la demande (« installe les améliorations par lots »).

**SHA installé (fin du lot 2) : `b0e1e1b`** (merge commit de la PR #117 dans `develop`,
qui inclut le lot 1, PR #116, SHA `9209acf`).

---

## 1. Principe et périmètre réellement couvert

Cette extension s'appuie sur la présentation déjà validée de FSE01 (tickets #108, #110,
#112). Compte tenu de l'ampleur du périmètre (16 cours), le travail a été scindé en deux
niveaux, livrés chacun par lot :

- **Niveau 1 — infrastructure mécanique, appliquée aux 15 cours FSE02-FSE16** (FSE17 a sa
  propre structure, non concernée) : espacement des exemples, titre « Décryptons ce
  document », exercices guidés redesignés en cartes individuelles avec corrigés structurés
  en HTML réel. Ce niveau corrige un bug réel et généralisé (voir § 3).
- **Niveau 2 — forme réaliste des documents, au cas par cas** : traitement complet pour
  FSE02 (spec détaillée de l'utilisateur) et pour les dialogues à plusieurs voix clairement
  identifiés (FSE04, FSE07, FSE16). **Les documents textuels des autres cours (FSE03, 05,
  06, 08, 09, 10, 11, 12, 13, 14, 15) n'ont PAS reçu de maquette visuelle bespoke dans ce
  lot** : ils bénéficient du niveau 1 (structure correcte, listes réparées, exercices en
  cartes) mais restent des paragraphes de texte enrichi plutôt que des pages/documents
  stylés. C'est une limite assumée de ce lot, pas un oubli — voir § 6 pour le détail
  cours par cours et les suites possibles.

---

## 2. Niveau 1 : infrastructure mécanique (15 cours)

Trois transformations génériques ajoutées à `app/v1/fse_course_sections.py`, appliquées à
tous les cours FSE02-FSE16 (texte déjà rédigé et validé, jamais réécrit) :

- `exemple_headers_to_titles()` : chaque `### Exemple N — ...` devient
  `<h3 class="jc-example-title">` (espacement 32px/16px, comme FSE01).
- `analyse_commentee_to_decrypt()` : chaque `**Analyse commentée :**` devient le titre
  « 🔍 Décryptons ce document ».
- `exercises_to_cards()` : les exercices guidés (anciens `<details>` imbriqués) deviennent
  des cartes individuelles (`.jc-exercise-card`) — numéro, titre, consigne toujours
  visible, accordéon « Voir le corrigé » stylé comme un bouton (fermé par défaut, ouvrable
  au clic et au clavier), corrigé structuré en HTML réel. Le « Corrigé très expliqué »
  final devient une 3e carte (« Question flash »).

---

## 3. Bug réel diagnostiqué et corrigé (niveau 1)

Vérification explicitement demandée : « les listes dans les accordéons [...] doivent
réellement être converties en HTML ». Diagnostic confirmé par test direct :
`app.content.render_markdown` ne retraite **jamais** le Markdown situé à l'intérieur d'un
bloc HTML brut (`<details>`), quelle que soit la présence d'une ligne vide — un bug
différent de celui déjà corrigé aux tickets #103/#105 (qui ne concernait que les listes
hors blocs HTML).

Recherche systématique sur les 15 cours : **une occurrence réelle trouvée** — FSE03,
exercice 1, corrigé numéroté (« 1. Photo de profil... 2. Photo d'anniversaire... ») restait
fondu en texte à numéros littéraux. Corrigé par la nouvelle fonction `exercises_to_cards()`,
qui reconstruit chaque corrigé en HTML réel (`<ol>`/`<ul>` quand le texte est une liste,
`<p>` sinon). Vérifié après coup sur les 15 cours installés en production : **zéro
occurrence résiduelle** (recherche explicite de tirets/numéros littéraux à l'intérieur de
chaque `<details>` de chaque page rendue).

---

## 4. Niveau 2 : documents réalistes

### FSE02 — traitement complet (spec détaillée)

Les trois descriptions entre crochets deviennent de vraies pages de média (HTML/CSS),
textes bruts (`FSE02_*_TEXT`, utilisés par la banque de questions) strictement inchangés :

- **L'Hebdo du Littoral** : trois cartes de tarifs (14€/mois, 9€/mois, 2,50€ à l'unité),
  citation mise en avant, encadré « ✉️ Vos lettres ».
- **Le Flash Infos** : titre du média, deux bannières publicitaires **visuellement
  distinctes** (couleurs et bordures différentes), titre d'article, ligne compteur de
  vues/partage/commentaire.
- **Radio Communauté Wallonie** : page « Qui sommes-nous », mission affichée, encadré
  « 📞 Émission du matin » (appels à l'antenne).

### FSE04, FSE07, FSE16 — dialogues à plusieurs voix

Nouveaux composants génériques (`docs/components/DialogueComponents.md`) : `ChatThread`,
`QuoteCard`, et cinq classes de couleur d'intervenant réutilisables
(`.jc-social-avatar--p1` à `--p5`) — la même personne garde la même couleur partout dans un
même document.

- **FSE04** : la publication de groupe (5 membres anonymisés A-E) devient une carte avec
  avatars colorés — rend visible, d'un coup d'œil, que le membre D exprime un désaccord
  explicite au milieu des réactions moqueuses (illustre directement la limite de
  l'influence sociale enseignée dans ce cours). Le témoignage de Karim devient une carte de
  citation.
- **FSE07** : la note de direction devient un mémo signé/daté (réutilise `.jc-doc-meta`),
  le fil de discussion de classe (4 élèves, 7 messages) devient un vrai chat coloré, la
  publication de forum anonyme devient une carte avec ses métadonnées (sujet, pseudonyme) —
  matérialise visuellement les trois niveaux de fiabilité que le cours enseigne à
  distinguer.
- **FSE16** : les trois réactions de parties prenantes (ménage, entreprise de transport,
  association environnementale) sont désormais affichées **en entier** comme « document 3 »
  — l'ancienne version du cours n'affichait qu'un extrait recopié à la main (la réaction de
  l'association), alors que les exercices font déjà référence aux trois réactions. C'est
  une correction de complétude, pas seulement une amélioration visuelle.

---

## 5. Cohérence pédagogique

Vérification systématique (recherche dans les 17 cours) des cinq généralisations citées :

- **Financement exclusif vs mixte** : seul FSE02 traite le financement des médias. Ajouté
  en théorie, dans l'exemple RCW et dans la fiche mémo : « un média public qui combinerait
  dotation ET publicité resterait, lui, partiellement soumis à cette logique d'audience » —
  **vérifié contre une source réelle** (RTBF : ~73% de dotation publique + recettes
  publicitaires plafonnées à 22,5% des recettes totales, selon son rapport financier 2024),
  confirmant que la généralisation ajoutée (beaucoup de médias publics réels sont à
  financement mixte) est fondée.
- **Média public présenté comme exempt de publicité par défaut** : corrigé au même endroit
  — l'indépendance vis-à-vis de l'audience est désormais explicitement rattachée au
  financement *exclusivement* public de RCW, pas généralisée à « tout média public ».
- **Interactivité vs délai vs financement** : seul FSE02 traite l'interactivité comme
  notion. Fiche mémo complétée : « Interactivité, délai de la réponse et mode de
  financement sont trois notions indépendantes ».
- **Compteur de vues ≠ interactivité** : corrigé dans l'exemple Le Flash Infos et la fiche
  mémo — le compteur de vues mesure l'audience, l'interactivité réelle vient du partage et
  des commentaires.
- **QR code consulté ≠ rétroaction vers l'émetteur** : déjà correctement traité dans FSE01
  depuis le ticket #110 (seul cours concerné, vérifié par recherche — aucune autre
  occurrence de « QR code » dans FSE02-17) ; nouvelle vérification de non-régression
  effectuée, aucune reformulation involontaire introduite ailleurs.

Aucune autre généralisation abusive détectée par la recherche systématique dans les 17
cours sur ces cinq points.

---

## 6. État détaillé par cours (pour la validation cours par cours annoncée)

| Cours | Niveau 1 (structure, exercices, listes) | Niveau 2 (documents réalistes) |
|---|---|---|
| FSE02 | ✅ | ✅ complet (3 pages de média) |
| FSE03 | ✅ | Non traité — reste en texte enrichi |
| FSE04 | ✅ | ✅ dialogue coloré (groupe + témoignage) |
| FSE05 | ✅ | Non traité |
| FSE06 | ✅ | Non traité |
| FSE07 | ✅ | ✅ mémo + chat coloré + forum |
| FSE08 | ✅ | Non traité (déjà un tableau + schéma SVG, ticket #105) |
| FSE09 | ✅ | Non traité |
| FSE10 | ✅ | Non traité (tableau déjà présent) |
| FSE11 | ✅ | Non traité |
| FSE12 | ✅ | Non traité (tableau déjà présent) |
| FSE13 | ✅ | Non traité |
| FSE14 | ✅ | Non traité (tableau déjà présent) |
| FSE15 | ✅ | Non traité (déjà un schéma SVG, ticket #105) |
| FSE16 | ✅ | ✅ réactions colorées (document complet) |
| FSE17 | n/a (structure propre, non concernée, déjà conforme) | n/a |

---

## 7. Génération d'images

**Aucune image n'a été générée pour ce lot.** Vérification explicite avant toute décision :
recherche de scènes visuelles nécessitant une illustration (affiche, campagne, scène
réelle) dans les 16 cours — aucune occurrence trouvée (seule FSE01 avait une affiche de
sécurité routière, déjà traitée aux tickets #108/#110). Tous les documents de FSE02-17 sont
des pages web, tableaux, dialogues ou schémas institutionnels, entièrement représentables
en HTML/CSS/SVG. Conforme à la consigne : « pas d'image décorative systématique ni de
quota d'images par cours » — zéro appel à l'API de génération d'images dans ce lot.

---

## 8. Tests exécutés (ciblés, pas la suite complète de 1 419 tests)

| Lot | Résultat |
|---|---|
| Lot 1 : `test_ticket97_fse02_04.py`, `98_fse05_08.py`, `99_fse09_12.py`, `100_fse13_16.py` (adaptés : libellé du bouton de corrigé) | 162/162 ✅ |
| Lot 1 : `test_ticket101_fse17.py`, `test_ticket102_coverage.py` (non-régression) | 68/68 ✅ |
| Lot 2 : `test_ticket97_fse02_04.py`, `98_fse05_08.py`, `100_fse13_16.py`, `102_coverage.py` | 170/170 ✅ |
| `test_admin_content_hierarchy.py` (idempotence du seed, deux `seed()` consécutifs) — exécuté après chaque lot | 18/18 ✅ (×2) |

Exécutés sur la branche avant fusion, puis sur le checkout de production après chaque
fast-forward, avant chaque seed — jamais la suite complète de 1 419 tests.

**Vérification structurelle des pages réelles en production**, après chaque lot : 15 pages
(FSE02-16) avec 3 cartes d'exercice chacune, aucun `<details open>`, titres d'exemple et de
décryptage présents, zéro tiret/numéro littéral résiduel dans les `<details>` (lot 1) ;
cartes de tarifs et bannières distinctes sur FSE02, couleurs d'intervenant et cartes de
citation sur FSE04/16, fil de chat complet sur FSE07, aucune régression sur les 11 autres
cours (lot 2).

**Prévisualisation visuelle locale** (HTML réel → PDF → image, WeasyPrint, outil de
développement uniquement, jamais une dépendance du projet) des pages d'exemples de FSE02,
FSE03 (vérification spécifique du corrigé à liste numérotée), FSE04 et FSE07 — rendu
conforme à la description dans chaque cas.

**Limite explicite, identique aux rapports précédents** : aucun navigateur réel (Chrome/
Firefox headless, Playwright) disponible dans cet environnement. Les vérifications
structurelles (HTML/CSS envoyé par le serveur) et les prévisualisations WeasyPrint sont des
indices de correction, pas une preuve de rendu visuel final sur ordinateur, téléphone et à
l'impression — cette vérification reste à faire par l'utilisateur, cours par cours, comme
annoncé.

**Comptes et données vérifiés intacts** après chaque seed de production : 18 utilisateurs,
67 sessions, 536 réponses — identiques avant/après, aux deux étapes. Sauvegardes de
`jury_central.db` effectuées avant chaque seed
(`jury_central.db.bak-pre-ticket115-batch1-<horodatage>`,
`...-batch2-<horodatage>`).

---

## 9. Fichiers modifiés/créés

- `app/v1/fse_course_sections.py` — trois nouvelles transformations génériques (§ 2).
- `app/v1/fse02_content.py`/`fse02_course.py` — 3 pages de média + nuances pédagogiques.
- `app/v1/fse04_content.py`/`fse04_course.py`, `fse07_content.py`/`fse07_course.py`,
  `fse16_content.py`/`fse16_course.py` — dialogues colorés.
- `app/static/css/design-system.css` — composants `.jc-webpage-*`/`.jc-pricing-*`/
  `.jc-ad-banner*` (FSE02), `.jc-chat-*`/`.jc-quote-*`/`.jc-social-avatar--p1..5`
  (dialogues), `.jc-source-doc-*` (générique, pas encore utilisé).
- `app/seed.py` — `obsolete_titles` étendu pour FSE02-16 (Exemples/Exercices partout,
  Théorie/Fiche mémo en plus pour FSE02).
- `docs/components/DialogueComponents.md` (nouveau), `ExampleTitle.md`, `DecryptTitle.md`,
  `ExerciseStepCard.md`, `INDEX.md` (étendus à FSE02-17).
- `tests/test_ticket97_fse02_04.py`, `98_fse05_08.py`, `99_fse09_12.py`,
  `100_fse13_16.py` (adaptés : libellé du bouton de corrigé).

---

## 10. Liens à tester

- `https://jury-central.lodylands.com/uaa/fse-fse02` — documents réalistes complets
- `https://jury-central.lodylands.com/uaa/fse-fse04` — dialogue coloré
- `https://jury-central.lodylands.com/uaa/fse-fse07` — mémo + chat + forum
- `https://jury-central.lodylands.com/uaa/fse-fse16` — réactions colorées
- `https://jury-central.lodylands.com/uaa/fse-fse03` … `fse-fse15` (hors 04/07) — structure
  et exercices améliorés, documents encore en texte enrichi (niveau 2 non traité, voir § 6)

À vérifier en particulier : les listes désormais réelles dans les corrigés (ex. FSE03,
exercice 1), l'ouverture/fermeture au clic et au clavier des accordéons « Voir le corrigé »
sur plusieurs cours, le rendu des pages de média FSE02 et du chat FSE07 sur téléphone et à
l'impression.

---

## 11. Suite possible (pour la validation cours par cours annoncée)

Les 11 cours restants (FSE03, 05, 06, 08, 09, 10, 11, 12, 13, 14, 15) ont une structure
corrigée et des exercices redesignés, mais leurs documents (situations numérotées, tableaux
déjà présents, notes) n'ont pas reçu de traitement visuel bespoke dans ce lot. Candidats
identifiés pour un prochain lot, selon le retour de l'utilisateur : cartes de situation
numérotées (FSE05/06/09/13, listes de scénarios courts), visuel de bulletin de vote
(FSE10), mémo/dossier pour les documents de type note (FSE03, FSE11, FSE14).
