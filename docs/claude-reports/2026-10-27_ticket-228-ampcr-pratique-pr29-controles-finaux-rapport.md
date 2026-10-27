# Ticket #228 — [AMPCR pratique PR29] Contrôles finaux et rapport professionnel d'intervention

- Ticket : https://github.com/ReC82/jury-central/issues/228
- **État réel : Installé — à tester**
- SHA installé : `412d15408bf7f8655e5cf2453f8963a8dd3cfcfb` (fusion de la PR #317 dans `develop`)
- Date : 2026-10-27 (session jcorch autonome)

## 1. Résultat

Le cours **PR29 « Contrôles finaux et rapport professionnel d'intervention »** est publié dans le
parcours **Informatique AMPCR → Pratique écrite** (module `AMPCR-PRATIQUE`). Il est séparé de la
théorie MC : cours, banque, examen et progression sont distincts, avec seulement des liens vers
MC29, MC30 et MC36. Il occupe la position 29, juste après PR28. L'accueil du parcours affiche
désormais « 29 cours publiés sur 30 ».

**Numérotation vérifiée** : dans le plan installé (`_COURSE_ROWS`, numérotation de #236),
l'emplacement PR29 porte bien le sujet du ticket : « PR29, ticket 228, Contrôles finaux et rapport
professionnel d'intervention ». Exigences : **AP-16** « Vocabulaire technique » (officielle, p. 5)
et **AP-C01** (complément : réponse écrite de technicien). Le cours s'appuie aussi sur **AP-15**
(dépannage) et rappelle AP-C03 (confidentialité). Aucun autre cours n'a été touché ni renuméroté.

### Contenu (15 blocs)

**8 chapitres.** Chacun a ses objectifs, la théorie, une procédure professionnelle, une erreur
fréquente, un attendu « à l'écrit », un repère rapide et un renvoi vers les exercices liés :

1. **Critères d'acceptation** : un critère se mesure. Il se compare avant / après, dans les mêmes
   conditions. Chaque critère est atteint, non atteint (même si c'est mieux qu'avant) ou **non
   concluant**. Le verdict suit une règle : un seul « non atteint » invalide tout ; sinon un
   « non concluant » impose une réserve ; sinon tout est validé.
2. **Six familles de contrôles finaux** : test fonctionnel, stabilité, performance, réseau local
   et Internet, sécurité, pilote et périphérique. Un tableau donne les contrôles exigés pour
   chacun des 6 types d'intervention. Le test fonctionnel et la sécurité sont toujours exigés.
3. **Journal des opérations** (ordre des heures, une modification à la fois, jamais « OK » comme
   résultat) et **tests reproductibles** (6 rubriques).
4. **Retour arrière, restauration et résultats non concluants** : l'arbre de clôture mène à l'une
   de quatre issues : signer, retour arrière, escalade ou réserve. Le chapitre traite aussi la
   régression et les limites du résultat.
5. **Compte rendu structuré** en 6 parties et 14 rubriques : identité non sensible de
   l'équipement, demande, symptômes, hypothèses, relevés, tests, résultats, action, pièces,
   validation, risques résiduels, recommandation, signature et accord.
6. **Rédaction** : séparer faits et hypothèses, tableau du vocabulaire technique (AP-16),
   confidentialité (ce qu'on n'écrit jamais), grille d'évaluation d'un rapport sur 20.
7. **Restitution au client** sans jargon, **escalade** (contrôles de PR26 réutilisés),
   **documentation** (rapport, journal, base de connaissances, inventaire du parc).
8. **Formulaires imprimables** et liste de contrôle de clôture.

**5 rapports modèles complets** (le ticket en demande 5), un par thème : PC (bloc d'alimentation),
système (réinstallation, avec un retour arrière noté au journal), RJ45 (prise refaite), réseau
(VLAN, **validation avec réserve**) et partage (groupes et droits). Chacun contient les 14
rubriques, les critères avant / après, le verdict, la décision, le journal et le message au client.

**22 exercices corrigés** (le ticket en demande au moins 18) :

- 2 contrôles finaux ;
- 2 critères avant / après ;
- 2 journal et tests reproductibles ;
- 4 corrections de rapports : données sensibles, rubriques manquantes, validation abusive, note
  sur la grille ;
- 2 communication au client ;
- 2 procédures à remettre en ordre ;
- 3 décisions, escalade et documentation ;
- 2 schémas à compléter : arbre de clôture, structure du rapport ;
- 1 parcours d'arbre ;
- 2 rédactions : rapport complet à partir de notes, réserve et limites.

**Mini-examen de 10 questions /20** : 2 points par question, réponses libres, dans l'onglet
« Examen blanc » uniquement, jamais affiché dans le cours.

**Visuels** : 4 procédures, 11 figures SVG et 2 schémas à compléter (fichiers statiques). Tout est
dessiné depuis les données du cours. **Aucune image générée.**

**Formulaires imprimables (A4)**, autonomes, sans script ni ressource externe :

- rapport d'intervention vierge ;
- fiche de contrôles finaux (familles, tableau avant / après, verdict) ;
- journal des opérations, avec un test reproductible et le retour arrière.

### Fichiers

- `app/v1/ampcr_pratique_pr29_figures.py` — règles du cours, 5 rapports `REPORTS`, schémas et
  formulaires. Les règles : `CHECK_FAMILIES` / `required_checks` / `missing_checks`,
  `Criterion` / `assess` / `verdict` / `decision`, `DECISION_TREE`, `journal_issues`,
  `repro_missing`, `REPORT_FIELDS` / `missing_report_fields` / `sensitive_lines`,
  `report_score`, `MESSAGES`, `DOC_ITEMS`. Réutilise le format d'arbre de PR27 et les schémas de
  listes de PR28.
- `app/v1/ampcr_pratique_pr29_bank.py` — 22 exercices et 10 questions d'examen.
- `app/v1/ampcr_pratique_pr29_course.py` — les 15 blocs.
- `app/v1/ampcr_pratique_bank.py` — déclaration de PR29 et contexte de correction IA propre.
- `app/seed.py` — `_seed_uaa(…, "PR29", …, position 29)`, simple ajout.
- `app/static/img/ampcr-pratique/pr29-*.svg` (2 fichiers) ;
  `app/static/print/ampcr-pratique/pr29-formulaire-*.html` (3 fichiers).
- `tests/test_ticket228_ampcr_pratique_pr29.py` (37 tests) ; comptage adapté dans
  `tests/test_admin_content_hierarchy.py`.
- `docs/current_state.md`, `docs/ampcr_pratique_v1.md`, `docs/changelog.md`.

## 2. Liens pour tester

- Cours : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr29
- S'entraîner (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr29/practice
- Examen blanc /20 (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr29/exam
- Formulaires A4 :
  - https://jury-central.lodylands.com/static/print/ampcr-pratique/pr29-formulaire-rapport.html
  - https://jury-central.lodylands.com/static/print/ampcr-pratique/pr29-formulaire-controles.html
  - https://jury-central.lodylands.com/static/print/ampcr-pratique/pr29-formulaire-journal.html
- Accueil du parcours : https://jury-central.lodylands.com/ampcr-pratique
- Matrice : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte :

1. Ouvrir le cours et parcourir les 15 séquences. Le rapport modèle 4 montre la réserve, le
   rapport 2 le retour arrière.
2. Ouvrir un formulaire et l'imprimer en A4 (Ctrl+P).
3. « S'entraîner » : 10 exercices tirés des 22.
4. « Examen blanc » : 10 questions notées sur 20. Après l'envoi, vérifier le corrigé et le barème.

## 3. Vérifications effectuées

- **Tests ciblés** `tests/test_ticket228_ampcr_pratique_pr29.py` : **37 passed**. Ils couvrent :
  - les règles du cours, recontrôlées indépendamment : familles de contrôles, contrôles exigés,
    `assess` / `verdict` / `decision`, arbre de clôture, journal, test reproductible, 14
    rubriques, détection des données sensibles, grille sur 20 ;
  - les 5 rapports modèles : rubriques complètes, aucun contrôle manquant, aucune donnée
    sensible, journal sans défaut, verdicts attendus ;
  - les figures : validité, accessibilité, contenu dessiné depuis les données ; les schémas à
    compléter ne montrent pas leurs réponses ;
  - les fichiers statiques et les formulaires : identiques au contenu généré, A4, sans script ;
  - les exercices : auto-correction, valeurs des corrigés, renvois aux documents, types de
    questions ;
  - le cours, le seed (idempotent, position), les réserves de questions séparées, le contexte
    de correction ;
  - les pages, les sessions d'entraînement et d'examen /20, sans génération IA.
- **Suite complète** (une exécution, car `seed.py` est partagé) : **3 233 passed**, aucun échec
  (27 min 38 s).
- **`ruff check`** sur les fichiers créés et modifiés : All checks passed.
- **Contrôle visuel** (Chromium sans interface) :
  - les 13 figures : textes lisibles, rien ne se chevauche ;
  - un formulaire A4 ;
  - la page en ligne en largeur mobile (390 px) ;
  - le rapport modèle 1 rendu avec le style du site, en largeur bureau.
- **Installation** :
  - arbre propre sur `develop` ;
  - sauvegarde `~/.local/state/jury-central-orch/backups/jury_central-pre-ticket228-20261027-204745.db` ;
  - avance rapide `10c1772 → 412d154` ;
  - seed : 1 UAA et 67 blocs créés (15 de PR29 + le remplacement habituel des 52 blocs FSE) ;
  - les deux services sont actifs ; `/health` local et public OK ;
  - en HTTP 200 : PR29, PR28, accueil, matrice, les 2 schémas et les 3 formulaires ;
  - l'entraînement répond 303 vers la connexion (normal sans session) ;
  - 22 cartes d'exercice servies ; « 29 cours publiés sur 30 » ;
  - compteurs utilisateurs / sessions / réponses inchangés (18 / 84 / 668).

**Non effectué** :

- validation pédagogique humaine ;
- session réelle avec la vraie correction IA ;
- impression papier réelle.

## 4. Choix techniques faits seul

- **Contrôles exigés par type d'intervention** : c'est une **convention du cours**, signalée
  comme telle. Le test fonctionnel et la sécurité sont toujours exigés ; pour le reste, chaque
  entreprise a ses règles, qui font foi.
- **« Non concluant »** : la mesure est absente ou impossible. Le résultat n'est ni réussi ni
  raté. Il conduit à une **validation avec réserve**, sauf si un autre critère n'est pas atteint
  (dans ce cas, non validé).
- **« Mieux qu'avant » ≠ atteint** : le critère se compare à la cible écrite, pas à l'état
  avant l'intervention.
- **Décision** : le retour arrière n'est possible que s'il a été préparé. Sinon, ou si l'action
  est hors de ses droits, on escalade. On reprend les contrôles d'escalade de PR26 sans les
  recopier.
- **Modèle de rapport** : 14 rubriques, celles listées par le ticket, plus « référence ». C'est
  un complément AP-C01. La grille sur 20 est une convention du cours.
- **Formulaires imprimables** : fichiers HTML statiques sous `/static/print/ampcr-pratique/`.
  Ils ne contiennent aucun script ; on imprime avec Ctrl+P. Ce choix évite de toucher aux
  gabarits et aux routes.
- **Pas d'image générée** : tous les visuels sont des schémas de texte et de structure
  construits depuis les données. Il n'y avait rien de technique à illustrer par photo.
- **Pas de lien vers PR30** (non publié).

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Éléments restant à réaliser

- Validation visuelle et pédagogique par le propriétaire.
- **Détails typographiques connus**, non corrigés en ligne :
  - dans la rubrique « Validation » des rapports modèles, les critères sont séparés par « ; »
    sans espace avant ;
  - les valeurs avant / après des tableaux n'ont pas d'unité (l'unité figure dans le libellé du
    critère).

  Le seed ne réécrit jamais un bloc déjà publié. Une correction demande donc soit une édition
  depuis l'admin, soit un ticket de mise à jour des blocs. Je ne l'ai pas faite ici pour rester
  dans le périmètre.
- Suggestions (hors périmètre, non faites) :
  - PR30 (#229) pourra réutiliser `REPORT_FIELDS`, la fiche de contrôles et `verdict` pour le
    rapport du grand laboratoire ;
  - les cours PR11, PR15, PR16, PR20 et PR24 annoncent « approfondi en PR29 » sans lien : on
    pourra ajouter ces liens à l'audit final (#235).
