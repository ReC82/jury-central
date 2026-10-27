# Ticket #226 — [AMPCR pratique PR27] Construire et justifier une procédure de diagnostic

- Ticket : https://github.com/ReC82/jury-central/issues/226
- **État réel : Installé — à tester**
- SHA installé : `511b94393575956fc2db617c8b1cc963179fc33f` (fusion de la PR #313 dans `develop`)
- Date : 2026-10-27 (session jcorch autonome)

## 1. Résultat

Le cours **PR27 « Construire et justifier une procédure de diagnostic »** est publié dans le
parcours **Informatique AMPCR → Pratique écrite** (module `AMPCR-PRATIQUE`), séparé de la théorie
MC (cours, banque, examen et progression distincts ; liens seulement vers MC29 et MC30). Il occupe
la position 27, juste après PR26.

**Numérotation vérifiée** : dans le plan installé (`_COURSE_ROWS`, numérotation de #236),
l'emplacement PR27 porte bien le sujet du ticket (« PR27, ticket 226, Construire et justifier une
procédure de diagnostic », exigences **AP-15** « Dépannage sur les dysfonctionnements courants
(hardware ou software) » (officielle, p. 5) et **AP-C01** (complément : rédiger une réponse écrite
de technicien)). Aucun autre cours n'a été touché ni renuméroté.

### Contenu (15 blocs)

**8 chapitres**, chacun avec objectifs, théorie, procédure professionnelle, erreur fréquente,
attendu « à l'écrit », repère rapide et renvoi aux exercices liés :

1. **Cycle de diagnostic** : hypothèse → test discriminant → résultat attendu (écrit avant le
   test) → interprétation → action → validation ; comment écrire un test justifié.
2. **Du moins invasif au plus invasif** : échelle 0 à 5 (observer, lire, manipuler, configurer,
   ouvrir, effacer), précautions exigées à chaque niveau, **mesure d'impact et sécurité**.
3. **Approche par couches** (réseau et poste ; ascendante, descendante, par division) et
   **isolation de variables** (une variable à la fois, recherche par moitiés).
4. **Test croisé** (tableau des 4 conclusions), **test négatif**, **faux positifs** et faux
   négatifs (8 cas commentés).
5. **Contrôle de configuration**, **journaux** Windows et Linux (41/6008 = conséquences, pas la
   cause), **conditions de reproduction** (facteur présent à chaque panne et jamais sans).
6. **Quatre arbres de décision exacts** : matériel (périphérique USB), démarrage, système
   (Windows), réseau.
7. **Conservation de preuves** et **plan de retour arrière** (modèle à recopier).
8. **Alternatives et escalade** (renvoi à l'arbre d'escalade de PR26) et modèle de tableau pour
   rédiger la procédure sur la copie.

**6 dossiers entièrement résolus** (ticket : 6) — démarrage (« No bootable device » après ajout
d'un disque), périphérique (imprimante USB), DHCP (169.254 après déménagement, VLAN du port),
DNS (DNS manuel obsolète), partage (« Accès refusé », groupe manquant), panne intermittente
(câble écrasé, journal de la réceptionniste). Chacun : situation, symptômes, hypothèses, tableau
des tests (niveau, résultat attendu par hypothèse, résultat obtenu, hypothèses écartées), cause,
chemin dans l'arbre, action, impact, retour arrière, preuves, validation, escalade, conclusion.

**23 exercices corrigés** (ticket : ≥ 20) dont **8 procédures à ordonner et justifier** (ticket :
≥ 8 ; 5 remises en ordre auto-corrigées + 3 ordonnancements justifiés rédigés), 7 choix et
interprétations de tests, **2 schémas à compléter** (arbres réseau et démarrage), 2 parcours
d'arbre (système, matériel), 4 rédactions (retour arrière, preuves, mesure d'impact, alternative
et escalade).

**Mini-examen de 10 questions /20** (2 points chacune, réponses libres, onglet « Examen blanc »,
jamais affiché dans le cours).

**Visuels** : 4 procédures, échelle d'invasivité, 2 piles de couches, tableau du test croisé,
4 arbres (12 figures SVG) + 2 arbres à compléter servis en fichiers statiques. **Aucune image
générée** : toutes les informations sont des règles exactes dessinées depuis les données.

### Fichiers

- `app/v1/ampcr_pratique_pr27_figures.py` — règles (`LEVELS`/`precautions`/`order_probes`,
  `cross_test`, `FALSE_RESULTS`, `config_diff`, `common_factors`, `remaining`/`is_discriminant`,
  `TREES`/`walk`), 6 dossiers `CASES`, schémas.
- `app/v1/ampcr_pratique_pr27_bank.py` — 23 exercices et 10 questions d'examen.
- `app/v1/ampcr_pratique_pr27_course.py` — les 15 blocs.
- `app/v1/ampcr_pratique_bank.py` — déclaration de PR27 et contexte de correction IA propre.
- `app/seed.py` — `_seed_uaa(…, "PR27", …, position 27)`, ajout seul.
- `app/static/img/ampcr-pratique/pr27-*.svg` (2 fichiers).
- `tests/test_ticket226_ampcr_pratique_pr27.py` (40 tests) ; comptages adaptés dans
  `tests/test_admin_content_hierarchy.py` et `tests/test_ticket225_ampcr_pratique_pr26.py`.
- `docs/current_state.md`, `docs/ampcr_pratique_v1.md`, `docs/changelog.md`.

## 2. Liens pour tester

- Cours : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr27
- S'entraîner (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr27/practice
- Examen blanc /20 (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr27/exam
- Accueil du parcours : https://jury-central.lodylands.com/ampcr-pratique
- Matrice : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte :
1. Ouvrir le cours, parcourir les 15 séquences (chapitres, 4 arbres, six dossiers, exercices).
2. « S'entraîner » : 10 exercices tirés des 23 (arbres à compléter et documents dans la question).
3. « Examen blanc » : 10 questions, note sur 20 ; après l'envoi, vérifier corrigé et barème.

## 3. Vérifications effectuées

- **Tests ciblés** `tests/test_ticket226_ampcr_pratique_pr27.py` : **40 passed** — échelle et
  précautions, tri des tests, table du test croisé, faux positifs/négatifs, écarts de
  configuration, facteur commun, hypothèses restantes, parcours des 4 arbres (chaque branche) ;
  pour chacun des 6 dossiers : tests triés par invasivité, chaque test discriminant, résultat
  obtenu prévu par une hypothèse vivante, cause unique, chemin d'arbre cohérent ; figures
  (validité, accessibilité, données dessinées), schémas à compléter sans leurs réponses, fichiers
  statiques identiques ; exercices (format du socle, auto-correction, valeurs des corrigés) ;
  matière du ticket, liens, types de cartes, seed idempotent et position, réserves séparées,
  contexte de correction, pages, sessions d'entraînement et d'examen /20 sans génération IA.
- Avec les voisins (PR25, PR26, EX04, #236, #299, #302, #192, hiérarchie admin) : **226 passed**.
- **Suite complète** (une exécution, `seed.py` partagé) : **3 160 passed**, aucun échec (27 min).
- **`ruff check`** sur les fichiers créés et modifiés : All checks passed.
- **Contrôle visuel** (Chromium sans interface) de toutes les figures et de deux dossiers rendus
  sur une base temporaire, en largeur bureau et mobile (390 px). Corrigé pendant la session :
  légende de la pile de couches et en-tête du tableau du test croisé qui débordaient. Sur mobile,
  les tableaux larges défilent horizontalement (même comportement que PR26).
- **Installation** : arbre propre sur `develop` ; sauvegarde
  `~/.local/state/jury-central-orch/backups/jury_central-pre-ticket226-20261027-190631.db` ;
  avance rapide `6b01a7b → 511b943` ; seed : 1 UAA et 67 blocs créés (15 de PR27 + remplacement
  habituel des 52 blocs FSE) ; deux services actifs ; `/health` local et public OK ; PR27, PR26,
  accueil, matrice et les 2 schémas statiques en HTTP 200 ; entraînement en 303 vers la connexion
  (normal sans session) ; 23 cartes d'exercice servies ; « 27 cours publiés sur 30 » ; compteurs
  utilisateurs / sessions / réponses inchangés (18 / 84 / 661).

**Non effectué** : validation pédagogique humaine ; session réelle avec la vraie correction IA.

## 4. Choix techniques faits seul

- **Échelle d'invasivité 0 à 5** et règle « à niveau égal, le plus rapide d'abord » : convention
  du cours, présentée comme telle (« la procédure de l'entreprise fait foi »). Précautions par
  niveau explicites (pas cumulatives à l'aveugle : une réinstallation n'exige pas de bracelet
  antistatique).
- **Faux positif / négatif** définis du point de vue du diagnostic (positif = le test signale une
  panne).
- **Arbres** : questions fermées, « oui » on descend, premier « non » → piste (format de PR06/PR24) ;
  l'arbre démarrage et l'arbre réseau sont cohérents avec ceux de PR06 et PR24 sans les recopier.
- **Dossiers** : seuls des tests discriminants figurent dans le tableau ; les confirmations
  passent dans « action » et « validation ».
- **Exigences citées** : AP-15 et AP-C01 sur chaque item ; AP-C03 (données) et AP-C02 (matériel)
  ajoutées sur les items concernés.
- **Fichiers** : même découpage que PR25/PR26 (figures / bank / course) ; schémas à compléter en
  fichiers statiques.
- **Pas de lien** vers PR28–PR30 (non publiés).

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Éléments restant à réaliser

- Validation visuelle et pédagogique par le propriétaire.
- Suggestions (hors périmètre, non faites) : PR29 (#228) pourra reprendre le tableau de
  procédure et le plan de retour arrière de PR27 pour le rapport d'intervention ; MC29/MC30
  (théorie) pourraient renvoyer vers PR27.
