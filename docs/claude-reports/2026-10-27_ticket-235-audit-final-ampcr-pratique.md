# Ticket #235 — [P2][AMPCR pratique] Audit final de couverture officielle et qualité

- Ticket : #235 — https://github.com/ReC82/jury-central/issues/235
- Date : 2026-10-27 (session autonome jcorch)
- **État réel : Installé — à tester** (audit livré ; validation pédagogique finale par le propriétaire)
- Branche : `feature/235-audit-final-ampcr-pratique` — PR : #325 (fusionnée, merge `7ffd03e`)
- **SHA installé : `7ffd03eaf9bf44cf12ffa135efc868c35ba5d0f7`** (installé le 27/10/2026, services redémarrés, santé OK, compteurs utilisateurs/sessions/réponses inchangés 18/84/668, sauvegarde de la base prise avant)

## 1. Synthèse

- **36/36 unités publiées** sous *Informatique (AMPCR) → Pratique écrite* : PR01–PR30 et
  EX01–EX06, toutes `is_published` dans le module `AMPCR-PRATIQUE`, **contenu en production
  identique au code** (comparaison bloc par bloc des 566 blocs de cours de la base réelle, en
  lecture seule).
- **38/38 exigences officielles (pp. 5-6 des consignes 2026-2027/1) + 3/3 compléments
  pédagogiques prouvés** : pour chacune, cours liés rédigés, notion présente dans le texte du
  cours (termes-témoins), au moins un exercice corrigé ET au moins une question d'examen blanc
  EX01–EX06. La matrice https://jury-central.lodylands.com/ampcr-pratique/matrice affiche
  désormais **38 validée(s), 0 partielle, 0 non traitée** avec une colonne « Preuves (audit) ».
  « Validé » = validation technique de couverture ; la validation pédagogique reste au
  propriétaire (écrit sur la page).
- **931 questions** rédigées : 547 exercices corrigés, 300 questions de mini-examens (30 × 10,
  chacun /20), 84 questions d'examens blancs (EX01–EX04 /100 ; EX05 et EX06 : 2 variantes /100).
- **Aucune erreur technique trouvée** dans les contrôles automatiques : 4 158 adresses IPv4
  (octets, préfixes, masques), 25 séquences T568A/B écrites en toutes lettres, valeurs du
  coaxial (10BASE2 50 Ω, RG-58, 185 m), 376 schémas SVG accessibles (role="img" + titre),
  55 images de documents d'examen présentes et servies (HTTP 200).
- **121 pages du parcours parcourues sur le site réel : 121 × HTTP 200** (accueil, matrice,
  format d'exercice, 6 fiches + téléchargements, 36 pages de cours/examens, 36 pages
  « Examen blanc », 30 pages « S'entraîner »).
- Empreintes SHA-256 des deux PDF officiels re-téléchargées le 27/10 : **identiques** à celles
  enregistrées par #192 (consignes `7a93c385…95e1`, programme 345/2007/249 `95e45949…f14b`) —
  aucune nouvelle version publiée.
- Écarts : **aucun écart bloquant** ; 4 écarts mineurs listés au § 5 (aucun ticket correctif
  indispensable, propositions au § 9).

## 2. Changements réalisés

| Fichier | Changement |
|---|---|
| `app/v1/ampcr_pratique_audit.py` (nouveau) | Moteur d'audit : `REQUIREMENT_TERMS` (termes-témoins par exigence, tirés du libellé officiel), `course_text` (texte rendu d'un cours publié), `requirement_evidence` / `audit_rows` / `proven_requirement_ids` (preuves par exigence). Aucune écriture en base. |
| `app/v1/ampcr_pratique_plan.py` | `VALIDATED_REQUIREMENT_IDS` = les 41 exigences prouvées (était vide depuis #192) ; docstring mise à jour. Le statut « validé » exige toujours en plus que cours ET examens liés soient publiés en base. |
| `app/v1/routes_ampcr_pratique.py`, `app/templates/ampcr_pratique_matrix.html` | Matrice : colonne « Preuves (audit) » (nb d'exercices corrigés, de questions de mini-examen, de questions d'examen blanc ; alerte rouge si une notion manque), définition honnête de « validé ». |
| `app/templates/ampcr_pratique_home.html`, `app/v1/ampcr_pratique_tickets.py`, `docs/ampcr_pratique_tickets.md` (régénéré) | Libellé : « validé » = publié + preuves de l'audit #235. |
| `tests/test_ticket235_ampcr_pratique_audit.py` (nouveau, 58 tests) | Garde-fous transversaux (§ 4). |
| 26 tests de cours (#193…#225) + `tests/test_ticket192_ampcr_pratique.py` | L'assertion « `VALIDATED_REQUIREMENT_IDS` vide » (règle : un ticket de cours ne valide jamais) devient « égal à l'ensemble prouvé par l'audit #235 ». |
| `docs/ampcr_pratique_v1.md` § 9, `docs/current_state.md` | Documentation de l'audit. |

Aucun contenu de cours ou d'examen modifié, aucune donnée utilisateur touchée, pas de seed
nécessaire (le contenu seedé n'a pas changé).

## 3. Liens directs pour tester (procédure courte)

1. Matrice : https://jury-central.lodylands.com/ampcr-pratique/matrice — en-tête « 38 exigences
   officielles — 38 validée(s), 0 partielle(s), 0 non traitée(s). Couverture complète. » ; colonne
   « Preuves (audit) » remplie pour chaque ligne, aucune alerte rouge « Notion absente du cours ».
2. Accueil du parcours : https://jury-central.lodylands.com/ampcr-pratique — « 30 cours publiés sur
   30 prévus », 6 examens, encart de couverture « 38 exigence(s) validée(s) sur 38 ».
3. Contrôle par sondage (recommandé) : choisir 3 exigences dans la matrice (ex. AP-22 comparaison
   fibre/cuivre → https://jury-central.lodylands.com/uaa/ampcr-pratique-pr17 ; AP-35 BNC →
   https://jury-central.lodylands.com/uaa/ampcr-pratique-pr16 ; AP-24 domaine →
   https://jury-central.lodylands.com/uaa/ampcr-pratique-pr22), vérifier que la notion est
   enseignée, qu'un exercice corrigé et une question d'examen blanc la travaillent.
4. Théorie intacte : https://jury-central.lodylands.com/mon-parcours → Informatique AMPCR →
   Théorie (MC01–MC38) inchangée, sans cours PR/EX.

## 4. Vérifications effectuées

| Contrôle | Méthode | Résultat |
|---|---|---|
| Publication réelle | Base réelle en lecture seule (`sqlite3 -readonly`) : 36 UAA PR/EX publiées dans `AMPCR-PRATIQUE` ; blocs comparés au rendu du code | 36/36 identiques (566 blocs) |
| Couverture AP-01…AP-38 + compléments | `ampcr_pratique_audit` (preuves textuelles + questions étiquetées) | 41/41 prouvées (tableau § 6) |
| Correspondance plan ↔ banques | Chaque exigence d'un emplacement PR/EX est portée par au moins une de ses questions ; toute question porte des exigences connues | OK (36/36) |
| Barèmes | Critères > 0 avec réponse attendue, corrigé présent, types corrigeables ; mini-examen 10 questions = 20 pts ; EX01–EX04 = 100 ; EX05/EX06 = 100 par variante | OK |
| Structure des cours | Objectifs, Exemples résolus, Pièges, Exercices corrigés, Mini-examen /20, Fiche mémo, Sources : présents dans les 30 cours | OK |
| IPv4 | 4 158 occurrences : octets ≤ 255, préfixes ≤ 32, masques contigus (4 contre-exemples volontaires de PR20 présentés comme invalides) | OK |
| RJ45 | 25 séquences T568A/B écrites en ligne comparées à la norme ; données `T568A`/`T568B` des schémas | OK |
| Coaxial / BNC | 10BASE2 = 50 Ω, RG-58, 185 m, 75 Ω (vidéo) présents dans PR16 | OK |
| Accessibilité | 376 SVG des 36 pages : tous `role="img"` + `aria-labelledby` ; 0 `<img>` sans `alt` ; tableaux avec `scope` | OK |
| Images d'examen | 55 fichiers référencés par les documents de questions : présents et servis (HTTP 200) | OK |
| Liens / navigation | Robot sur le site réel depuis `/ampcr-pratique` (liens internes du parcours) | 121 pages, 0 erreur |
| Séparation Théorie / Pratique | Test : module `AMPCR` ne contient que des MC, module `AMPCR-PRATIQUE` que des PR/EX ; une session pratique est rattachée au module pratique | OK |
| Autosave, reprise, corrigé caché | Test bout-en-bout PR15 : sauvegarde API, réponse réaffichée, ni « Corrigé de référence » ni « Barème » avant remise, « Reprendre l'entraînement en cours » | OK |
| Sources officielles | PDF consignes et programme re-téléchargés : SHA-256 identiques aux empreintes de #192 | OK |
| Tests automatisés | `tests/test_ticket235_ampcr_pratique_audit.py` (58) + régression des 43 fichiers AMPCR pratique / #299 / #302 | 1 244 passed (8 min 09 s), 0 échec ; contrôle post-installation sur le site public : matrice 38/38, 121 pages HTTP 200 |
| Ruff | fichiers modifiés | aucune erreur |

**Non effectué / limites** : pas de relecture humaine intégrale des 931 questions (l'audit vérifie
la présence et la cohérence, pas la qualité rédactionnelle de chaque corrigé) ; pas de test visuel
automatisé sur téléphone ni d'impression A4 réelle (les règles d'impression `@media print` et la
largeur fluide existent et ont été testées par les tickets de cours, non re-mesurées ici) ; les
banques ne sont importées en base qu'au premier démarrage d'une session (comportement voulu
depuis #193 : 3 unités importées à ce jour), elles sont donc vérifiées depuis le code ; la
correction IA réelle n'est pas exercée (tests avec `FakeAIProvider`).

## 5. Tableau des écarts

| # | Gravité | Constat | Preuve | Suite proposée |
|---|---|---|---|---|
| E1 | Mineur | AP-22 « Comparaison entre la fibre optique et les autres types de câbles » est la moins entraînée : 2 exercices corrigés, 1 question de mini-examen, 3 questions d'examen blanc (EX03) | Colonne « Preuves » de la matrice | Facultatif : 2-3 exercices comparatifs supplémentaires dans PR17 (ticket de contenu si le propriétaire le souhaite) |
| E2 | Mineur | Huit exigences ne sont évaluées que par **une seule question d'examen blanc** EX01–EX06 : AP-04, AP-05, AP-07, AP-08, AP-23, AP-24, AP-29, AP-38 (elles ont par ailleurs 4 à 12 questions de mini-examen chacune) | § 6 | Facultatif : les examens globaux EX05/EX06 pourraient en reprendre une au prochain enrichissement ; couverture déjà assurée par cours + mini-examens |
| E3 | Mineur (formulation) | PR19 écrit « le réseau 192.168.1.23/24 » (notation d'interface) pour désigner le réseau du poste ; formulation correcte mais moins rigoureuse que « le réseau 192.168.1.0/24 » (exercice E12, mini-examen X04) | Contrôle d'alignement réseau/préfixe | À corriger lors d'une prochaine retouche de PR19 (non bloquant, pas de faux technique) |
| E4 | Information | Programme 345/2007/249 : deux activités ne sont traitées que par citation — 7.1.4 « règles ergonomiques de manipulation » (absent) et 6.2 « logiciels clients des services Internet » (messagerie/navigateur cités, pas de configuration d'un client) | Comparaison § 7 | Hors consignes pp. 5-6 de l'épreuve pratique 2026-2027/1 ; voir question 1 |

Aucun écart bloquant ; aucun ticket correctif créé (une session ne crée pas de ticket : propositions au § 9).

## 6. Couverture chiffrée, exigence par exigence (contenu publié au 27/10/2026)

Exercices corrigés = réserve « S'entraîner » des cours ; mini-examens = réserve « Examen blanc »
des cours PRxx ; examens blancs = EX01–EX06. Toutes les exigences sont aussi reliées aux
mini-cours théoriques MC existants dans la matrice (liens de lecture, non comptés).

| Id | Exigence (abrégée) | Cours liés | Exercices corrigés | Questions mini-examens | Questions examens blancs (EX) | Statut |
|---|---|---|---|---|---|---|
| AP-01 | La structure d’un ordinateur, ses composants et ses périphériques. | PR01 | 8 | 4 | 5 (EX01, EX05) | validé (preuves) |
| AP-02 | Les différents éléments qui peuvent constituer un ordinateur (Proce… | PR01 | 15 | 6 | 2 (EX01) | validé (preuves) |
| AP-03 | Les différents types de disque dur et unités de stockage, le format… | PR05 | 16 | 10 | 7 (EX01, EX02, EX06) | validé (preuves) |
| AP-04 | Les caractéristiques d’une alimentation PC. | PR02 | 13 | 7 | 1 (EX01) | validé (preuves) |
| AP-05 | Les périphériques d’entrée et de sortie et le rôle d'un pilote. | PR01, PR10 | 12 | 8 | 1 (EX02) | validé (preuves) |
| AP-06 | Branchements, interfaces et connexions. | PR02 | 9 | 6 | 5 (EX01) | validé (preuves) |
| AP-07 | La carte mère et ses éléments constitutifs. | PR01 | 8 | 4 | 1 (EX01) | validé (preuves) |
| AP-08 | Les différents systèmes d’exploitation actuellement sur le marché. | PR07 | 17 | 11 | 1 (EX02) | validé (preuves) |
| AP-09 | Les principaux messages d’erreurs, l’interprétation et les démarche… | PR11 | 14 | 10 | 2 (EX02) | validé (preuves) |
| AP-10 | Installation complète des différents systèmes d’exploitation couran… | PR08, PR09 | 46 | 26 | 11 (EX02, EX05, EX06) | validé (preuves) |
| AP-11 | Paramètres et commandes de base des systèmes d'exploitation courants. | PR10 | 23 | 14 | 4 (EX02) | validé (preuves) |
| AP-12 | Interface graphique et interface de ligne de commande. | PR07, PR10 | 13 | 9 | 3 (EX02) | validé (preuves) |
| AP-13 | Connaître les principaux messages d’erreurs, comment interpréter ce… | PR11 | 15 | 9 | 2 (EX02) | validé (preuves) |
| AP-14 | Montage, démontage et reconditionnement d’un PC. | PR03, PR04 | 40 | 23 | 4 (EX01) | validé (preuves) |
| AP-15 | Dépannage sur les dysfonctionnements courants (hardware ou software). | PR06, PR11, PR12, PR27 | 87 | 41 | 22 (EX01, EX02, EX05, EX06) | validé (preuves) |
| AP-16 | Vocabulaire technique. | PR26, PR29 | 30 | 16 | 8 (EX05, EX06) | validé (preuves) |
| AP-17 | Notion de compatibilité. | PR01, PR02, PR06 | 24 | 10 | 4 (EX01, EX06) | validé (preuves) |
| AP-18 | Les différents types de câbles : UTP, FTP, STP, Coax. | PR13, PR15, PR16 | 17 | 9 | 5 (EX03) | validé (preuves) |
| AP-19 | Les débits binaires des câbles. | PR14 | 17 | 8 | 5 (EX03) | validé (preuves) |
| AP-20 | Les caractéristiques des câbles : atténuation, notion d’impédance, … | PR13, PR14, PR15, PR16 | 40 | 26 | 8 (EX03) | validé (preuves) |
| AP-21 | La fibre optique et ses caractéristiques : support d’information, d… | PR17 | 22 | 12 | 3 (EX03) | validé (preuves) |
| AP-22 | Comparaison entre la fibre optique et les autres types de câbles. | PR17 | 2 | 1 | 3 (EX03) | validé (preuves) |
| AP-23 | Topologies de réseaux. | PR19 | 8 | 4 | 1 (EX04) | validé (preuves) |
| AP-24 | Notions de domaine, groupe de travail, comptes utilisateurs et grou… | PR22 | 22 | 12 | 1 (EX02) | validé (preuves) |
| AP-25 | Partage de ressources (imprimantes, disques, répertoires…). | PR23 | 16 | 8 | 6 (EX04, EX05, EX06) | validé (preuves) |
| AP-26 | Mise en partage sur un réseau informatique de documents et applicat… | PR23 | 6 | 5 | 2 (EX04) | validé (preuves) |
| AP-27 | Les notions de droit et de permission. | PR23 | 19 | 8 | 5 (EX02, EX04, EX06) | validé (preuves) |
| AP-28 | Connexion de deux machines en direct. | PR21 | 15 | 9 | 1 (EX04) | validé (preuves) |
| AP-29 | Notions de base sur les protocoles (TCP/IP, OSI, NETBEUI…). | PR19 | 14 | 6 | 1 (EX04) | validé (preuves) |
| AP-30 | L’adressage IP, les adresses MAC, l’identification d’une adresse MA… | PR20 | 27 | 14 | 10 (EX04, EX05, EX06) | validé (preuves) |
| AP-31 | Hub, switch, passerelle, routeur, modem. | PR19 | 14 | 7 | 2 (EX04) | validé (preuves) |
| AP-32 | Connexions et interventions en cas de panne internet. | PR24 | 22 | 12 | 3 (EX04) | validé (preuves) |
| AP-33 | WIFI : principe, sécurisation, cryptage, répéteur. | PR25 | 26 | 12 | 3 (EX04, EX06) | validé (preuves) |
| AP-34 | Description de la réalisation d’un câble avec connecteurs RJ45 (cod… | PR15 | 16 | 10 | 8 (EX03, EX05, EX06) | validé (preuves) |
| AP-35 | Description de la réalisation d’un câble avec connecteurs BNC. | PR16 | 16 | 9 | 6 (EX03, EX05, EX06) | validé (preuves) |
| AP-36 | Câblage et installation physique d’un réseau informatique. | PR18, PR30 | 31 | 15 | 4 (EX05) | validé (preuves) |
| AP-37 | Dépannage de problèmes simples d’accès au réseau. | PR24, PR30 | 53 | 25 | 6 (EX04, EX05) | validé (preuves) |
| AP-38 | Création d’un mini réseau entre plusieurs machines. | PR18, PR21, PR30 | 42 | 17 | 1 (EX04) | validé (preuves) |
| AP-C01 | Rédiger une réponse écrite de technicien : décrire une intervention… | PR26, PR27, PR29 | 109 | 49 | 5 (EX01, EX05, EX06) | validé (preuves) |
| AP-C02 | Sécurité électrique et protection ESD lors d'une intervention sur u… | PR02, PR03, PR06, PR28 | 31 | 14 | 3 (EX01) | validé (preuves) |
| AP-C03 | Protéger les données du client : sauvegarde préalable, confidential… | PR04, PR12, PR28 | 73 | 31 | 8 (EX01, EX02, EX06) | validé (preuves) |


## 7. Comparaison avec le programme 345/2007/249 (indicative)

Le programme (46 pages, empreinte vérifiée) décrit 8 fonctions et 22 activités. Les consignes de
l'épreuve pratique 2026-2027/1 (pp. 5-6) restent la référence de l'examen ; ce tableau sert
seulement à repérer des notions du programme absentes du parcours. Correspondance établie par
recherche textuelle dans les cours publiés — **non officielle**.

| Activité du programme | Cours du parcours |
|---|---|
| 1.1-1.2 Réunir, placer et connecter les composants | PR01, PR02, PR03 |
| 2.1-2.4 Démonter, trier, reconditionner, mettre à niveau | PR03, PR04 |
| 3.1 Préparer l'ordinateur et le disque (BIOS, partitions, formatage) | PR05, PR07, PR08, PR09 |
| 3.2-3.3 Installer et configurer un système d'exploitation | PR07, PR08, PR09, PR10 |
| 3.4-3.5 Connecter un périphérique, pilotes | PR01, PR10, PR11 |
| 3.6 Installer / désinstaller un logiciel | PR10, PR12 (désinstallation citée dans 9 cours) |
| 4.1-4.2 Réaliser, poser et tester le câblage | PR13–PR18 |
| 4.3 Intégrer des postes à un réseau, connexion Internet, protection du poste | PR19–PR25, PR30 |
| 5.1-5.2 Repérer et remédier aux dysfonctionnements simples | PR06, PR11, PR12, PR24, PR26, PR27 |
| 6.1 Fonctionnalités de base du système et des utilitaires (commandes, arborescence) | PR10, PR11, PR12 |
| 6.2 Logiciels clients des services Internet | **cités seulement** (messagerie dans 7 cours, navigateur dans 11) |
| 6.3 Mise à jour et mise à niveau | PR04, PR07–PR10, PR12 |
| 7.1 Ergonomie, sécurité, prévention (dont 7.1.4 ergonomie de manipulation) | sécurité : PR02, PR03, PR28 ; **ergonomie absente** |
| 7.2 Dispositions légales (licences, déchets DEEE) | PR04, PR07, PR08, PR28 |
| 7.3 Confidentialité | PR04, PR26, PR28 (AP-C03) |
| 8.1 Communiquer avec la hiérarchie, les clients | PR26, PR29 |
| 8.2 Dispositions socio-professionnelles | non traité (non évaluable dans une épreuve écrite technique) |

## 8. Choix techniques faits seul

1. **Définition de « validé »** : le ticket demande de classer manque/partiel/validé « avec preuves »
   et de ne jamais valider sans cours ET exercice publiés. J'ai défini des preuves vérifiables par
   machine (cours rédigés + termes-témoins dans leur texte + exercice corrigé + question d'examen
   blanc) et aligné `VALIDATED_REQUIREMENT_IDS` sur elles par test. La page dit explicitement que
   c'est une validation technique, la validation pédagogique restant au propriétaire.
2. **Termes-témoins** tirés du libellé officiel de chaque exigence (2 à 5 par exigence) : un contrôle
   simple, lisible et reproductible, plutôt qu'un jugement automatique de qualité.
3. **Aucune modification de contenu** de cours ou d'examen : l'audit n'a trouvé aucun faux
   technique ; les écarts mineurs sont signalés (règle « une amélioration repérée est signalée »).
4. **Tests de cours existants** : l'assertion « aucune exigence validée » (vraie avant l'audit)
   est remplacée par « ensemble validé = ensemble prouvé par l'audit », qui garde la même intention.
5. **Pas de nouvelle dépendance** : la lecture du programme PDF a été faite avec une bibliothèque
   installée dans un environnement temporaire hors dépôt, uniquement pour cet audit.
6. Pas de seed ni de migration : le contenu seedé est inchangé ; seul le code de l'application
   (plan, matrice) change, d'où un simple redémarrage.

## 9. Décisions demandées au propriétaire

1. **Compléments hors consignes (programme 7.1.4 ergonomie, 6.2 clients Internet)** — ils figurent
   au programme 345/2007/249 mais pas dans la liste des pp. 5-6 des consignes de l'épreuve pratique.
   Options : (a) ne rien ajouter ; (b) un encadré court dans PR28 (ergonomie) et PR10 (client de
   messagerie). **Recommandation : (a)**, l'épreuve suit les consignes 2026-2027/1 ; (b) seulement si
   tu veux couvrir tout le programme.
2. **Renforcer AP-22 et les huit exigences à une seule question d'examen blanc (E1, E2)** — options :
   (a) laisser en l'état (déjà couvertes par cours + mini-examens) ; (b) ticket de contenu pour
   ajouter quelques questions. **Recommandation : (a)** pour l'examen du 28/10, (b) éventuellement
   ensuite.

Aucune de ces questions ne bloque la livraison.

## 10. Protocole de recette utilisateur (≈ 30 min)

1. Ouvrir la matrice (lien § 3) : 38/38, colonne Preuves, aucune alerte rouge ; imprimer en A4
   paysage (bouton « Imprimer ») et vérifier que le tableau tient.
2. Depuis l'accueil Pratique écrite, ouvrir un cours par module (PR01, PR08, PR15, PR20, PR27,
   PR30) sur ordinateur puis sur téléphone : schémas lisibles, tableaux défilables, retour au parcours.
3. Lancer « S'entraîner » sur PR15, écrire une réponse, quitter, revenir : bouton « Reprendre » et
   réponse conservée ; aucun corrigé avant remise ; remettre et lire la correction.
4. Lancer EX05 puis EX06 (« Examen blanc ») : variante entière, documents à côté de chaque question,
   note /100 après correction.
5. Vérifier qu'aucun cours PR/EX n'apparaît dans la Théorie (MC01–MC38) et que la progression
   théorique n'a pas bougé.
6. Signaler tout défaut dans le ticket du cours concerné (il sera repris en priorité).

## 11. Synthèse de mise en production

- Parcours Pratique écrite complet en production : 30 cours, 6 examens blancs, 6 fiches mémo
  (#302), matrice 38/38 prouvée, format d'exercice, consignes structurées (#299).
- Risques résiduels : qualité rédactionnelle non relue humainement question par question ;
  correction IA réelle des réponses longues dépendante du fournisseur (moteur asynchrone, échec
  jamais transformé en 0, #88/#90) ; banques importées au premier usage (premier démarrage de
  chaque cours légèrement plus long).
- Retour arrière : `git revert -m 1 <merge>` de la PR de ce ticket rend la matrice à « partiel » sans
  toucher au contenu ni aux données.

## 12. Éléments restant à réaliser

- Validation pédagogique et visuelle par le propriétaire (protocole § 10).
- Facultatif selon les réponses au § 9 : compléments programme, questions supplémentaires AP-22 /
  examens blancs, reformulation E3 dans PR19.
