# Ticket #229 — [AMPCR pratique PR30] Grand laboratoire écrit — installation et dépannage d'un réseau complet

- Ticket : https://github.com/ReC82/jury-central/issues/229
- **État réel : Installé — à tester**
- SHA installé : `9c31501` (fusion de la PR #319 dans `develop`)
- Date : 2026-10-27 (session jcorch autonome)

## 1. Résultat

Le cours **PR30 « Grand laboratoire écrit — installation et dépannage d'un réseau complet »**
est publié dans **Informatique AMPCR → Pratique écrite** (module `AMPCR-PRATIQUE`). Il occupe la
position 30, juste après PR29. Il reste séparé de la théorie MC : cours, banque, examen et
progression sont distincts, avec seulement des liens vers MC15, MC16, MC23, MC25 et MC31.
L'accueil du parcours affiche désormais **« 30 cours publiés sur 30 »**.

**Numérotation vérifiée** : dans le plan installé (`_COURSE_ROWS`, numérotation de #236),
l'emplacement PR30 porte bien le sujet du ticket : « PR30, ticket 229, Grand laboratoire écrit —
installation et dépannage d'un réseau complet ». Ses exigences sont **AP-36** (câblage et
installation physique), **AP-37** (dépannage de l'accès au réseau) et **AP-38** (création d'un
mini réseau). Aucun autre cours n'a été touché ni renuméroté.

### Le dossier de la PME (fictive)

« Géomètres Lambert & Associés » :

- un plateau de 24 m × 10 m avec **deux salles** et un local technique entre les deux ;
- **six postes** : cinq sous Windows 11 Pro, un sous Ubuntu 24.04 LTS ;
- un switch, la box de l'opérateur, un point d'accès Wi-Fi, une imprimante multifonction et un
  **serveur de fichiers** ;
- des contraintes écrites dans la demande : quatre postes de plus dans deux ans, un Wi-Fi pour
  les invités, l'arrêt propre du serveur en cas de coupure, un budget à présenter par postes.

**Toutes les valeurs du dossier sont calculées** par des règles déjà vérifiées dans les cours
précédents, jamais recopiées à la main :

| Valeur | Règle reprise de |
|---|---|
| Longueurs des liens, switch, panneau, baie, câble, PoE, recette des liens et des postes | PR18 |
| Plan IPv4 et erreurs d'un plan | PR20 |
| Groupe de travail ou domaine | PR22 |
| Droits effectifs (partage + NTFS) | PR23 |
| Compatibilité Windows 11 | PR07 |
| Audit Wi-Fi, choix du canal, couverture estimée | PR25 |
| Verdict, décision et rapport en 14 rubriques | PR29 |
| Arbre de décision | PR27 |

### Contenu (16 blocs)

**8 chapitres.** Chacun a ses objectifs, la théorie utile, une procédure professionnelle, une
erreur fréquente, un attendu « à l'écrit », un repère rapide et un renvoi vers les exercices :

1. **Le dossier** : demande, plan, personnel, contraintes, les huit phases du laboratoire.
2. **Inventaire, dimensionnement et budget indicatif.**
   - Switch : 14 ports aujourd'hui, 19 avec l'extension, donc **24 ports**.
   - Panneau de 24 ports, baie de 15 U, une boîte de câble (159 m).
   - Compatibilité Windows 11 de chaque PC.
   - Nomenclature en **quatre postes de dépense, sans aucun prix** : les montants viennent des
     devis.
3. **Câblage** : Cat6 U/UTP en T568B partout, baie, repérage, tableau de longueurs, rapport du
   testeur. Un lien est en défaut (P08, fil 6 ouvert).
4. **Plan IPv4** `192.168.50.0/24` : adresses fixes hors de l'étendue DHCP, DNS par la box,
   réseau invités sur le VLAN 60. Le contrôle par les règles de PR20 donne **0 erreur**.
5. **Groupe de travail aujourd'hui, domaine si des stagiaires tournent** (le « selon scénario »
   du ticket). Comptes, groupes, partages, et une **matrice des droits calculée** qui répond
   exactement aux besoins du client.
6. **Installation des systèmes** : Windows 11 Pro sur la station livrée nue, mise à niveau de
   COMPTA (Windows 10 n'est plus pris en charge depuis le 14/10/2025), Ubuntu sur le PC non
   compatible, raccordement au serveur et à l'imprimante.
7. **Wi-Fi** : deux SSID, WPA2/WPA3, canal 11 calculé depuis les voisins, invités isolés,
   couverture estimée. **Sécurité de l'installation** : liste à cocher, vraies et fausses
   mesures.
8. **Pannes de mise en service, recette et rapport** :
   - panne matérielle : plus d'image après un ajout de mémoire ;
   - panne logicielle : « Accès refusé » à cause d'un identifiant enregistré d'un autre compte ;
   - recette des six postes ; trois échouent, chacun pour une cause différente ;
   - verdict « **validation avec réserve** » (le test de coupure de courant n'a pas pu être
     fait) ;
   - rapport complet en 14 rubriques.

**8 études de cas graduées** (niveau 1 à 4), réparties sur deux blocs « Exemples ». Chacune
donne :

- ses exigences officielles AP-xx, citées en toutes lettres ;
- ses compléments, signalés comme tels ;
- un énoncé et un **corrigé intégral** ;
- les **variantes acceptées si elles sont justifiées**.

Un tableau relie chaque cas aux consignes officielles. Le laboratoire couvre 29 des 38
exigences officielles. Les 9 autres sont nommées dans les sources, avec le cours qui les
traite : AP-03 à AP-07, AP-21, AP-22, AP-28 et AP-35.

**23 exercices transversaux** (le ticket en demande au moins 20) répartis sur les thèmes du
dossier : inventaire et budget, câblage, IPv4 et DHCP, comptes et droits, systèmes, pannes,
Wi-Fi, sécurité, recette, rapport, exigences officielles. Dans le lot :

- 2 schémas à compléter (baie, arbre de recette) ;
- 2 procédures à ordonner et 1 parcours d'arbre ;
- 5 classements et 2 remises en ordre auto-corrigés.

**Mini-examen de 10 questions /20** : 2 points par question, réponses libres. Il est
uniquement dans l'onglet « Examen blanc » et n'apparaît jamais dans le cours.

**Visuels** : 4 procédures et 10 figures SVG, plus 2 schémas à compléter servis en fichiers
statiques. Les figures :

- plan des locaux à l'échelle ;
- baie ;
- fiche T568B ;
- rapport du testeur ;
- schéma logique et adressage ;
- matrice des droits ;
- couverture Wi-Fi ;
- liste de sécurité ;
- arbre de recette ;
- fiche de recette.

Toutes sont **dessinées depuis les données**. **Aucune image générée.**

### Fichiers

- `app/v1/ampcr_pratique_pr30_figures.py` — données de la PME, valeurs calculées (règles
  réutilisées), nomenclature sans prix, études de cas et exigences, procédures, arbre de
  recette, rapport final, schémas.
- `app/v1/ampcr_pratique_pr30_bank.py` — 23 exercices et 10 questions d'examen.
- `app/v1/ampcr_pratique_pr30_course.py` — les 16 blocs.
- `app/v1/ampcr_pratique_bank.py` — déclaration de PR30 et contexte de correction IA propre.
  Ce contexte accepte plusieurs solutions justifiées et refuse explicitement les mauvaises
  pratiques.
- `app/seed.py` — `_seed_uaa(…, "PR30", …, position 30)`, simple ajout.
- `app/static/img/ampcr-pratique/pr30-*.svg` (2 fichiers).
- `tests/test_ticket229_ampcr_pratique_pr30.py` (35 tests) ; comptage adapté dans
  `tests/test_admin_content_hierarchy.py`.
- `docs/current_state.md`, `docs/ampcr_pratique_v1.md`, `docs/changelog.md`.

## 2. Liens pour tester

- Cours : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr30
- S'entraîner (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr30/practice
- Examen blanc /20 (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr30/exam
- Accueil du parcours : https://jury-central.lodylands.com/ampcr-pratique
- Matrice : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte :

1. Ouvrir le cours et parcourir les 16 séquences. Le chapitre 8 et le cas 8 montrent la recette
   et le rapport final.
2. Lire un cas (par exemple le cas 4) : énoncé, corrigé, variantes acceptées.
3. « S'entraîner » : 10 exercices tirés des 23.
4. « Examen blanc » : 10 questions notées sur 20. Après l'envoi, vérifier le corrigé et le
   barème.

## 3. Vérifications effectuées

- **Tests ciblés** `tests/test_ticket229_ampcr_pratique_pr30.py` : **35 passed** (59 avec les tests de hiérarchie et de mise en page des consignes #299). Ils couvrent :
  - le dossier recalculé **indépendamment** : longueurs, ports, baie, câble, absence de prix,
    T568B, plan IPv4 sans erreur, brouillon fautif, matrice comparée à un tableau attendu écrit
    à la main, Windows 11, canal et couverture, clé Wi-Fi en ASCII et jamais dans le rapport,
    recette, verdict ;
  - les 8 cas : niveaux croissants, exigences existantes, AP-36/37/38 couvertes ;
  - les figures : validité, accessibilité, données dessinées ; les schémas à compléter ne
    montrent pas leurs réponses ; fichiers statiques identiques ;
  - les exercices : format du socle, auto-correction, valeurs des corrigés ;
  - le cours, le seed (idempotent, position 30), la banque, le contexte de correction ;
  - les pages, les sessions d'entraînement et d'examen /20, sans génération IA.
- **Tests voisins** (PR29, numérotation #236, socle #192, hiérarchie du contenu) : verts.
- **Suite complète** (une exécution, car `seed.py` est partagé) : **3 268 passed**, aucun échec (28 min 04 s).
- **`ruff check`** sur les fichiers créés et modifiés : All checks passed.
- **Contrôle visuel** (Chromium sans interface, largeur 440 px) des 16 schémas.
  - Défauts trouvés puis corrigés : légende du plan tronquée, box posée sur l'étiquette
    « LT », en-tête « Administration » trop large, lignes de couverture qui débordaient.
  - page en ligne en largeur mobile (390 px) : en-tête, onglets et 16 séquences lisibles.
- **Installation** :
  - arbre propre sur `develop` ; sauvegarde
    `~/.local/state/jury-central-orch/backups/jury_central-pre-ticket229-20261027-214131.db` ;
  - avance rapide `64107ed → 9c31501` ;
  - seed : 1 UAA et 68 blocs créés (16 de PR30 + le remplacement habituel des 52 blocs FSE) ;
  - les deux services sont actifs ; `/health` local et public OK ;
  - en HTTP 200 : PR30, PR29, accueil, matrice et les 2 schémas ; l'entraînement répond 303
    vers la connexion (normal sans session) ;
  - 23 cartes d'exercice servies ; « 30 cours publiés sur 30 » ;
  - compteurs utilisateurs / sessions / réponses inchangés (18 / 84 / 668).

**Non effectué** :

- validation pédagogique humaine ;
- session réelle avec la vraie correction IA ;
- impression papier.

## 4. Choix techniques faits seul

- **Nouvelle PME fictive**, différente du dossier « Archimède » de la fiche mémo 6 (#302). On
  évite ainsi de recopier une copie modèle déjà publiée ; les deux restent cohérents (mêmes
  règles).
- **Valeurs calculées par les règles existantes** (PR07, PR18, PR20, PR22, PR23, PR25, PR27,
  PR29) plutôt que des valeurs écrites à la main : un correcteur peut refaire chaque calcul,
  et les tests le refont.
- **Budget indicatif sans prix** : quantités et justifications par poste de dépense (matériel
  actif, câblage et passif, logiciels et licences, main-d'œuvre). Les prix viennent de devis ;
  aucun montant n'apparaît.
- **Switch dimensionné pour l'extension** (24 ports), puisqu'elle est écrite dans la demande.
  L'exercice E02 montre pourquoi un 16 ports ne suffit pas.
- **Serveur Windows Server en groupe de travail**, avec les licences d'accès client signalées.
  Variante acceptée : un NAS.
- **« Selon scénario »** : groupe de travail aujourd'hui (6 postes stables), domaine si des
  stagiaires tournent (règle de PR22).
- **Wi-Fi invités sur un VLAN** (complément). Variante acceptée : la fonction « invités » du
  point d'accès, à condition d'être vérifiée à la recette.
- **Couverture Wi-Fi** : estimation du modèle de PR25, présentée comme telle, à confirmer par
  une mesure.
- **Verdict « avec réserve »** : le test de coupure de courant (arrêt du serveur par
  l'onduleur) n'est pas faisable pendant les heures de bureau ; il est daté. Cela illustre la
  règle de PR29.
- **Pas de nouveau formulaire imprimable** : ceux de PR29 (rapport, contrôles, journal)
  conviennent. Pas de nouvelle route ni de nouveau gabarit.
- **Pas d'image générée** : il n'y avait aucune photo utile. Tous les visuels sont des schémas
  techniques construits depuis les données.

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Éléments restant à réaliser

- Validation visuelle et pédagogique par le propriétaire.
- Suggestions (hors périmètre, non faites) :
  - ajouter à l'audit final (#235) les liens « approfondi en PR30 » depuis PR06, et
    « approfondi en PR29 » depuis PR11, PR15, PR16, PR20 et PR24 ;
  - l'examen global EX06 (#234) pourra réutiliser le dossier de la PME et ses fonctions pour
    des variantes.
