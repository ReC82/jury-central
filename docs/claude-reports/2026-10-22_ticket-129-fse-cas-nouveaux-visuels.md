# Ticket #129 — FSE : varier les questions et afficher de vrais supports visuels

- **Ticket** : [#129 — FSE — varier les questions et afficher de vrais supports visuels en entraînement et examen blanc](https://github.com/ReC82/jury-central/issues/129)
- **État réel** : **Partiel — installé, reste à faire** (mécanisme commun + cas nouveaux FSE01 à FSE12 ; FSE13 à FSE16 restent à enrichir)
- **Branche** : `feature/129-fse-variantes-visuels`
- **SHA installé** : `73f175cef43395a7bb80fed5c6a49b37c41aadfb` (PR #185, lot 3 FSE09→FSE12 ; lot 2 : PR #183 ; lot 1 : PR #181)
- **Date** : 2026-10-22

## 1. Diagnostic

- Les banques FSE01–FSE16 (14 questions par cours en moyenne) sont écrites sur les
  **exemples commentés du cours** : en FSE01, 8 questions sur 14 portent sur le mail de
  Karim Haddad, l'affiche de sécurité routière ou l'offre d'emploi de Techno Services, que
  le cours analyse déjà en détail. L'entraînement et l'examen blanc réinterrogeaient donc
  l'élève sur des cas déjà corrigés devant lui.
- La sélection tirait au hasard dans cette banque (après la difficulté et l'anti-répétition
  par question) : rien ne faisait passer un cas neuf avant un exemple du cours, et une
  question différente sur un document déjà vu comptait comme « nouvelle ».
- L'affiche de FSE01 en session était celle du cours, accompagnée d'une légende descriptive
  (« Image : silhouette noire… », « logo du SPW… ») ; l'illustration réelle ne correspond
  pas à cette description (lettres et enfant en rouge, voir #149 question 2), et la
  situation est incohérente (enfant qui traverse au bord d'une autoroute).
- **Génération d'images par API impossible actuellement** : la clé OpenAI du serveur est
  refusée (`401 invalid_api_key` dans les journaux du worker, dernier essai le 21/10 à
  16 h 31 ; fichier de configuration inchangé depuis le 17/09 ; aucune correction IA réussie
  depuis le 03/10). Je n'ai pas lu la configuration.

## 2. Ce qui est livré

### Mécanisme commun (sans second moteur)

- `app/v1/fse_cases.py` : un **cas** = un document structuré (`SourceDocument` + version,
  texte exact + `content_json["layout"]`, mêmes composants que #149) et ses questions.
  Import idempotent (un cas déjà présent, reconnu au titre exact de son document, n'est ni
  recréé ni modifié), questions `MANUAL` (ne bloque pas l'import historique `IMPORTED`),
  difficulté déclarée sur chaque question. Appelé par l'amorçage paresseux existant
  (`_ensure_bank_seeded`) ; l'ouverture de FSE17 amorce les banques et les cas de
  FSE01→FSE16 (même principe que FR20). Aucune question ni aucun document existant n'est
  modifié : les anciennes sessions gardent leurs versions.
- **Ordre de sélection** (`case_ranker`, utilisé par `compose_selection`) : la difficulté
  demandée reste prioritaire ; à l'intérieur de chaque difficulté : (0) cas nouveaux jamais
  vus par l'élève (ou questions sans document), (1) cas nouveaux dont l'élève a déjà vu le
  document — en entraînement OU en examen —, (2) exemples commentés du cours. Ce n'est
  jamais un filtre : une session n'est jamais raccourcie. FSE17 garde sa répartition par
  cours et applique le même ordre dans chaque cours. No-op strict pour les matières sans
  exemples déclarés (Informatique, Français).
- **Vrai visuel ou rien** : une illustration est un `Asset` (fichier livré, empreinte
  SHA-256, méthode de production, prompt, modèle) rattaché à la version du document
  (`SourceDocumentVersion.asset_id`). Fichier absent → le cas n'est pas importé ; asset
  invalidé par l'admin ou fichier disparu → ses questions ne sont plus servies
  (`unusable_document_question_ids`, appliqué aussi à FSE17). Aucune génération d'image à
  l'affichage, à la reprise, au seed ou au déploiement.
- **Composant `poster_sheet`** (`_document_layouts.html` + CSS) : affiche réellement
  composée — émetteur, bandeau, titre, illustration, slogan, informations pratiques,
  mention en bas — texte exact en HTML ; clic = agrandissement ; « Ouvrir en grand » =
  page imprimable ; texte alternatif complet. Le contexte non visible sur le support (lieu
  d'installation, public) est affiché à part, dans un encadré « situation » au-dessus du
  document (tous composants). Statut « lu par… » ajouté au composant conversation.

### Contenu

| Cours | Cas nouveaux (supports) | Questions | Facile / moyen / difficile |
|---|---|---|---|
| FSE01 | Affiche d'un atelier de réparation de quartier (dessin + texte) ; conversation d'une équipe de futsal (consigne ambiguë, rétroaction, « lu par 8 des 12 ») ; note de service jargonneuse d'un supermarché (obstacle de code) ; 3 mini-situations (SMS « ne pas répondre », appel vidéo figé, panneau lumineux) | 17 | 5 / 7 / 5 |
| FSE02 | Page « Qui finance votre radio ? » d'une radio locale à financement mixte (publicité 65 %, subvention 35 %, prix du spot selon l'audience, émission où l'on appelle le studio) ; couverture d'un magazine sans publicité (vente au numéro + abonnement) ; publication d'un site gratuit qui devient payant et réactions des lecteurs ; 2 mini-situations (publicité avant une vidéo en ligne, télévision publique sans publicité pour les enfants) | 13 | 5 / 5 / 3 |
| FSE03 | Cinq résultats d'une recherche en ligne sur un candidat apprenti électricien (profil, vidéo publiée par son club, palmarès scolaire, avis laissé sur une pizzeria, adresse déduite par un réseau) ; 2 mini-situations (vidéo de mariage publiée par un invité, profil qui ne montre que des voyages) | 8 | 3 / 3 / 2 |
| FSE04 | Conversation de l'équipe d'un garage quand un apprenti part sans ranger son poste (norme, valeur, besoin, frustration, socialisation, limites de l'influence) ; affiche du règlement d'une maison de jeunes (normes écrites / valeur affichée) ; 2 mini-situations (tri des déchets appris en famille, refus de suivre le groupe) | 9 | 3 / 4 / 2 |

Total : 47 questions nouvelles, 10 nouveaux documents. Exemples du cours déclarés
(titres + noms propres) : FSE01 (Karim Haddad, affiche routière, Techno Services), FSE02
(Hebdo du Littoral, Flash Infos, RCW), FSE03 (Sophie Lambert), FSE04 (« Fous rires du
quotidien », Karim).

FSE01 passe de 14 à 31 questions, dont 23 hors exemples du cours (deux entraînements de 10 sans aucun exemple du cours). Le nouveau cas d'affiche
évite la situation incohérente : affiche collée sur la porte d'une boulangerie de
quartier, public de passants, rétroaction possible seulement par un autre canal (mail ou
sur place) — cohérent avec le cours (« une affiche ne permet pas de rétroaction directe »).

### Illustration

`app/static/img/fse/cases/fse01_atelier_reparation.svg` : dessin vectoriel original (deux
bénévoles réparent un vélo sur un pied d'atelier, outils au mur), sans texte ni visage
détaillé. La description transmise à la correction (« deux bénévoles réparent un vélo
installé sur un pied d'atelier ; des outils sont accrochés au mur derrière eux ») correspond
exactement au dessin, et est aussi affichée sous l'affiche.

## 3. Tester

Connecte-toi d'abord sur le site.

- Entraînement FSE01 : https://jury-central.lodylands.com/uaa/fse-fse01/practice
- Entraînements FSE02 / FSE03 / FSE04 : https://jury-central.lodylands.com/uaa/fse-fse02/practice — https://jury-central.lodylands.com/uaa/fse-fse03/practice — https://jury-central.lodylands.com/uaa/fse-fse04/practice
- Examen FSE01 : https://jury-central.lodylands.com/uaa/fse-fse01/exam
- Examen blanc FSE17 : https://jury-central.lodylands.com/uaa/fse-fse17/exam

Procédure courte : démarrer un entraînement FSE01 (10 questions) ; vérifier que les
questions portent sur l'atelier de réparation, le groupe de futsal, la note du magasin ou
des mini-situations, et plus sur le mail de Karim/l'affiche routière/Techno Services ;
cliquer sur l'affiche (agrandissement) et sur « Ouvrir en grand » (page imprimable) ;
quitter puis reprendre la session (mêmes questions, même affiche) ; terminer et regarder
« Revoir le document » dans les résultats ; démarrer un deuxième entraînement : aucune
question répétée, encore des cas nouveaux ; sur téléphone, vérifier l'affiche en une
colonne.

## 4. Vérifications

- Tests ciblés `tests/test_ticket129_fse_cases.py` (43, dont vérification mot pour mot de chaque document et absence des exemples du cours pour chaque cas) : import additif/idempotent, texte
  affiché = extraits exacts du document et couverture de son contenu, affiche rendue avec
  l'illustration et sans crochets, page de session et page document (HTTP), détection des
  exemples du cours, deux puis trois sessions successives (0, 0 puis 7 exemples, aucune
  répétition), cas déjà vu classé après un cas jamais vu, difficulté prioritaire, no-op
  strict sans rangs, autres cours inchangés, illustration absente → cas non importé, asset
  invalide → questions non servies, reprise identique sans appel de génération, FSE17
  (cas nouveaux amorcés, plusieurs cours couverts, pas d'exemples FSE01 en tête).
- Suite complète (moteur de sélection partagé modifié) : 2047 passed, 1 échec attendu
  corrigé (`test_ticket96…persists_through_resume` comptait 3 questions difficiles en
  FSE01 ; il y en a désormais 5). Un premier passage avait aussi montré un échec AMPCR
  intermittent préexistant (`test_ticket55…json_autosave_api…` : le type de la première
  question est aléatoire, une remise en ordre refuse une réponse texte), qui passe à
  nouveau et ne touche pas FSE — signalé, non corrigé ici.
- Essai à blanc sur une **copie** de la base réelle (sauvegarde d'avant installation,
  fichier temporaire supprimé ensuite) : l'ouverture de FSE17 importe les 47 questions et
  10 documents, un second passage n'ajoute rien ; un entraînement FSE01 « moyen » se compose
  normalement.
- `ruff check` des fichiers modifiés : aucune erreur.
- Rendu visuel : captures headless Chromium des dix nouveaux documents avec les vraies
  feuilles de style (desktop 1100 px, mobile 390 px), examinées. La page complète du site
  reste à valider par toi.
- Non vérifié : qualité réelle de la correction IA sur ces nouvelles questions (la clé IA
  est refusée ; les tests utilisent le fournisseur simulé).

## 5. Choix techniques faits seul

1. **Illustration en SVG dessiné plutôt que générée par API** : la clé est refusée (401) ;
   le ticket admet le SVG/HTML et demande des dessins plutôt que des photos. Le prompt
   équivalent est conservé dans les métadonnées de l'asset pour une éventuelle génération.
2. **Exemples du cours dépriorisés, pas archivés** : aucune question existante n'est
   modifiée ni retirée ; les exemples ne servent plus qu'en complément quand les cas
   nouveaux d'une difficulté sont épuisés.
3. **Un même support sert plusieurs questions complémentaires** (4 à 5 par document), comme
   le demande le ticket ; un cas déjà vu passe après un cas jamais vu.
4. **Questions à choix multiple sur mini-situations** : le registre des types n'autorise pas
   de document pour `multiple_choice` ; la situation tient dans l'énoncé.
5. **Questions `MANUAL`** pour ne pas perturber l'import historique (`IMPORTED`).
6. **Pas d'import au seed** : les cas s'importent à l'ouverture du cours (ou de FSE17),
   comme les banques existantes.

## 6. Décisions demandées au propriétaire

1. **Clé API OpenAI refusée (401)**. Elle bloque la génération d'illustrations ET la
   correction IA des réponses ouvertes. Options : (a) remplacer la clé dans la
   configuration du serveur ; (b) continuer en dessins SVG uniquement. **Recommandation :
   (a)** ; les dessins SVG livrés restent valables.
2. **Ancienne affiche FSE01 (autoroute + enfant qui traverse)**, incohérente et non conforme
   à sa légende. Elle n'est plus servie qu'en dernier recours. Options : (a) l'archiver dans
   la banque (anciennes sessions intactes) ; (b) la garder en dernier recours.
   **Recommandation : (a)**, à faire avec la correction du cours lui-même (hors périmètre).

## 7. Restant à réaliser

- Cas nouveaux pour FSE13 à FSE16 (dernier lot), même mécanisme.
- Génération d'illustrations raster via l'API quand la clé sera valide (si souhaité).

## 8. Installation (2026-10-22)

- PR #181 fusionnée dans `develop`, installée en avance rapide : `3de3aec` → `1b15c71`.
- Sauvegarde de la base avant installation (dossier de l'orchestrateur). Pas de seed : les
  cas s'importent à la première ouverture d'un cours FSE ou de l'examen blanc FSE17. Aucune
  dépendance ajoutée.
- Services `jury-central` et `jury-central-correction-worker` redémarrés : actifs ;
  `/health` local et public : `ok` ; pages FSE01/FSE17 : 303 (connexion requise, normal) ;
  illustration et feuille de style servies (200).
- Compteurs utilisateurs/sessions/réponses : 18 / 71 / 584 avant et après.

## 9. Lot 2 — FSE05 à FSE08 (2026-10-22)

### Livré

| Cours | Cas nouveaux (supports) | Questions | Facile / moyen / difficile |
|---|---|---|---|
| FSE05 | Conversation du groupe des parents d'une équipe U11 après un tournoi (photos et vidéo à publier, autorisation signée pour le seul trombinoscope du vestiaire, enfant de 10 ans qui refuse, « terrain public donc tout est permis ») ; fiche d'inscription en ligne d'une salle d'escalade (but annoncé, données excessives, case pré-cochée pour des partenaires, inscrit de 16 ans) ; 2 mini-situations (vidéo de vacances envoyée aux seuls grands-parents, passante photographiée pour une publicité) | 12 | 4 / 5 / 3 |
| FSE06 | Publication d'une maison de quartier qui change ses horaires et ses 7 commentaires (critique argumentée, injure, accusation sans preuve, menace, discrimination, faux compte « officiel » démenti par l'animateur) ; fiche de signalement d'une stagiaire (compte piraté, photos privées publiées « pour qu'elle ait honte », messages moqueurs répétés) ; 2 mini-situations (application qui copie les contacts, critique d'une vidéo) | 11 | 3 / 5 / 3 |
| FSE07 | Dossier en trois documents sur la vidéo d'un chauffeur de bus : communiqué signé et daté de la société de transport, publication virale mêlant faits, interprétation et opinion, message transféré anonyme et non daté (et contredit) ; 2 mini-situations (capture d'écran sans source, interprétation dans un article) | 8 | 3 / 3 / 2 |
| FSE08 | Huit brèves d'actualité « qui a décidé ? » (Parlement wallon, Parlement bruxellois, Parlement de la Communauté française, Chambre, conseil communal, tribunal, gouvernement wallon, signature du Roi) ; 1 mini-situation (carte d'identité à la commune) | 7 | 2 / 3 / 2 |

Total lot 2 : 38 questions, 5 documents. Cumul FSE01→FSE08 : 85 questions nouvelles,
15 documents. Exemples du cours déclarés (dépriorisés) : FSE05 (six situations, Nabil,
Chloé…), FSE06 (dix scénarios, Sarah…), FSE07 (Athénée du Parc, 5e B, forum anonyme),
FSE08 (tableau des niveaux de pouvoir et ses affirmations).

Les trois documents du dossier FSE07 sont réunis dans un seul support à trois fiches
numérotées : les questions qui les comparent s'appuient exactement sur le document que voit
l'élève et que reçoit la correction (aucun « document 3 » introuvable, cf. #151).

Aucune illustration nouvelle dans ce lot : les notions de FSE05→FSE08 se travaillent sur
des conversations, formulaires, publications, dossiers et brèves (HTML/CSS), pas sur des
affiches. Je n'ai volontairement pas mis de « photo » décrite en texte.

### Tester (lot 2)

- Entraînement FSE05 : https://jury-central.lodylands.com/uaa/fse-fse05/practice
- Entraînement FSE06 : https://jury-central.lodylands.com/uaa/fse-fse06/practice
- Entraînement FSE07 : https://jury-central.lodylands.com/uaa/fse-fse07/practice
- Entraînement FSE08 : https://jury-central.lodylands.com/uaa/fse-fse08/practice
- Examens : remplacer `practice` par `exam` ; examen blanc : https://jury-central.lodylands.com/uaa/fse-fse17/exam

Procédure : démarrer un entraînement de 10 questions dans chaque cours ; vérifier que les
documents sont les nouveaux supports (parents des Aiglons, salle d'escalade, maison de
quartier « Le Préau », fiche d'Amina, dossier de la ligne 12, brèves) et non plus les
exemples du cours ; regarder le rendu sur téléphone ; démarrer un deuxième entraînement
(aucune question répétée).

### Vérifications (lot 2)

- `tests/test_ticket129_fse_cases.py` : 72 passed (nouveaux : import réel par cours
  FSE05→FSE08, idempotence, cas nouveaux classés « jamais vus », exemples du cours
  reconnus, première session de 10 sans aucun exemple du cours, rendu HTML de chaque
  nouveau document contenant tout son texte exact et aucune description entre crochets ;
  texte mot pour mot et couverture du document ; difficultés réparties dans chaque cours).
  Le test « matière sans exemples déclarés » utilise désormais FSE09 (FSE05 en a).
- Tests FSE liés : `test_ticket98_fse05_08`, `test_ticket101_fse17`,
  `test_ticket149_document_layouts`, `test_ticket131…`, `test_ticket133…`,
  `test_ticket97…` : 177 passed. Pas de suite complète (aucun moteur partagé modifié dans
  ce lot : contenu + registre).
- `ruff check` des fichiers modifiés : aucune erreur.
- Essai à blanc sur une copie de la base réelle (fichier temporaire supprimé) : 12 / 11 / 8
  / 7 questions importées, second passage 0.
- Captures headless (desktop 1100 px, mobile 390 px) des 5 nouveaux documents avec les
  vraies feuilles de style, examinées. Validation sur le site réel : à faire par toi.
- Installation : `6edfc11` → `8f651d5` (avance rapide), sauvegarde de la base avant
  installation, services redémarrés et actifs, `/health` local et public `ok`, pages FSE05,
  FSE08, FSE17 : 303 (connexion requise, normal), compteurs 18 / 71 / 584 avant et après.
  Pas de seed (import à l'ouverture du cours ou de FSE17).

### Choix faits seul (lot 2)

1. **Pas d'affiche ni d'image dans ce lot** : aucune notion de FSE05→FSE08 ne demande
   d'analyser une affiche ; une photo décrite en texte serait justement ce que le ticket
   interdit. Supports HTML/CSS (conversation, formulaire, publication, fiche, brèves).
2. **Dossier FSE07 en un seul document à trois fiches**, pour que comparaison, élève et
   correcteur partagent exactement le même support.
3. **FSE08 : brèves fictives** décrivant des décisions plausibles, limitées aux
   compétences du cours (défense, logement, environnement, enseignement, proximité) et
   aux trois noms de normes ; rien sur des textes réellement votés.
4. **Nom de la maison de quartier FSE06 (« Le Préau »)** différent de celui de l'affiche
   FSE01 (« des Tilleuls ») pour éviter toute confusion entre cours.

## 10. Lot 3 — FSE09 à FSE12 (2026-10-22)

### Livré

| Cours | Cas nouveaux (supports) | Questions | Facile / moyen / difficile |
|---|---|---|---|
| FSE09 | Neuf demandes notées par une permanence « Qui contacter ? » (rénovation de logement, changement d'école, trottoir abîmé, allocations de chômage, recherche d'emploi, maison de jeunes, conflit devant un tribunal, diabète — matière partagée —, appui technique à une commune) ; conversation de voisins qui se trompent d'interlocuteur (« le fédéral décide de tout ») ; 1 mini-situation (aide à l'installation d'une boulangerie) | 11 | 3 / 5 / 3 |
| FSE10 | Feuille de résultats d'un scrutin communal fictif (27 sièges, aucune liste majoritaire, coalitions à chiffrer, bulletins blancs et nuls) ; conversation de jeunes électeurs liégeois la veille du vote (procuration, abstention ≠ vote blanc, règle flamande généralisée à tort, témoin du dépouillement, pétition, consultation populaire) ; 1 mini-situation (bulletin « Tous pareils ! ») | 11 | 3 / 6 / 2 |
| FSE11 | Quatre tracts de listes imaginaires (noms d'arbres) à rattacher aux familles socialiste, libérale, écologiste, centriste/humaniste ; trois réponses d'élèves à une consigne de comparaison (neutre, opinion, incomplète) | 7 | 2 / 3 / 2 |
| FSE12 | Budget d'un État imaginaire en **excédent** (autres recettes et dépenses, totaux à calculer absents du document) ; quatre mesures annoncées qui font basculer un autre budget en déficit ; 1 mini-situation (billets d'un musée public) | 8 | 2 / 4 / 2 |

Total lot 3 : 37 questions, 8 documents (cartes, conversations, tableau de résultats,
citations, budget — tous en HTML/CSS). Cumul FSE01→FSE12 : 122 questions nouvelles,
23 documents. Exemples du cours déclarés (dépriorisés) : FSE09 (dix situations), FSE10
(tableau daté des scrutins, bulletins A à D), FSE11 (six extraits sur les partis réels,
propositions Alpha/Beta), FSE12 (tableau fictif du cours).

Variations réelles : nouveaux supports et nouveaux modes de questionnement (orienter une
personne, corriger des affirmations erronées dans une conversation, chiffrer des
coalitions, critiquer un titre de presse, juger la neutralité d'une réponse d'élève,
vérifier l'affirmation d'un ministre par le calcul), pas seulement de nouveaux noms.

### Tester (lot 3)

- Entraînement FSE09 : https://jury-central.lodylands.com/uaa/fse-fse09/practice
- Entraînement FSE10 : https://jury-central.lodylands.com/uaa/fse-fse10/practice
- Entraînement FSE11 : https://jury-central.lodylands.com/uaa/fse-fse11/practice
- Entraînement FSE12 : https://jury-central.lodylands.com/uaa/fse-fse12/practice
- Examens : remplacer `practice` par `exam` ; examen blanc : https://jury-central.lodylands.com/uaa/fse-fse17/exam

Procédure : démarrer un entraînement de 10 questions dans chaque cours ; vérifier que les
documents sont les nouveaux supports (permanence « Qui contacter ? », voisins de la rue des
Glycines, résultats de Valbrise, groupe « Premiers votes — Liège », tracts Saule/Chêne/
Érable/Bouleau, réponses d'Élise/Hamza/Lina, budget de Valmerie, mesures d'Ostrelande) et
non plus les exemples du cours ; regarder le rendu sur téléphone (tableau et budget) ;
démarrer un deuxième entraînement (aucune question répétée).

### Vérifications (lot 3)

- `tests/test_ticket129_fse_cases.py` : 103 passed (import réel, idempotence, rang « jamais
  vu », exemples reconnus et première session sans exemple du cours pour FSE09→FSE12 ;
  rendu HTML de chaque nouveau document avec tout son texte exact et sans crochets ; texte
  mot pour mot et couverture ; difficultés réparties dans les 12 cours). Le test « matière
  sans exemples déclarés » utilise désormais FSE13.
- Tests FSE liés (`test_ticket97…`, `98…`, `99_fse09_12`, `101_fse17`, `131…`, `133…`,
  `149…`, `152…`) : 234 passed. Pas de suite complète (contenu + registre seulement).
- Contrôle des marqueurs d'exemples sur la banque réelle : les questions historiques sur
  les documents du cours sont bien dépriorisées ; aucune question générale sans document
  n'est prise à tort pour un exemple (un marqueur trop large, « du tableau », a été écarté
  pour FSE12).
- `ruff check` des fichiers modifiés : aucune erreur.
- Essai à blanc sur une copie de la base réelle (fichier temporaire supprimé) : 11 / 11 /
  7 / 8 questions importées, second passage 0.
- Captures headless (desktop 1100 px, mobile 390 px) des 8 nouveaux documents avec les
  vraies feuilles de style, examinées. Validation sur le site réel : à faire par toi.
- Installation : `06c82a4` → `73f175c` (avance rapide), sauvegarde de la base avant
  installation, services redémarrés et actifs, `/health` local et public `ok`, pages
  FSE09→FSE12 et FSE17 : 303 (connexion requise, normal), compteurs 18 / 71 / 584 avant et
  après. Pas de seed (import à l'ouverture du cours ou de FSE17).

### Choix faits seul (lot 3)

1. **Aucune image dans ce lot** : les notions de FSE09→FSE12 se travaillent sur des
   demandes, conversations, résultats chiffrés, tracts et budgets ; HTML/CSS suffit et
   garantit des chiffres exacts.
2. **FSE10 : aucune condition d'âge mobilisée** ; la seule règle régionale citée (vote
   communal plus obligatoire en Flandre depuis le 13 octobre 2024, toujours obligatoire en
   Wallonie) est celle du tableau daté du cours. Les sièges de Valbrise correspondent à une
   répartition proportionnelle (vérifiée avec la méthode D'Hondt), méthode ni enseignée ni
   demandée.
3. **FSE11 : listes imaginaires uniquement** (noms d'arbres neutres), pour ne jamais
   décrire ni évaluer un parti réel ; aucune question ne demande d'opinion.
4. **FSE12 : un budget en excédent**, à l'inverse de l'exemple du cours (déficit), pour que
   le calcul et le vocabulaire ne se mémorisent pas ; totaux absents des documents.
5. **Noms distincts des autres cours** (« Horizon », « rue des Glycines ») pour éviter la
   confusion avec la maison de quartier « des Tilleuls » de FSE01.
