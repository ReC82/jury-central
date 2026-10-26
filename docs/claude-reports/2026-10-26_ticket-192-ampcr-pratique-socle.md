# Ticket #192 — Socle du parcours AMPCR pratique écrite 2026-2027/1 et matrice de couverture officielle

Ticket : [#192 — [P0][AMPCR pratique] Socle du parcours écrit 2026-2027/1 et matrice de couverture officielle](https://github.com/ReC82/jury-central/issues/192)

**État réel : Installé — à tester** (socle livré ; les cours PR01–PR30 et exercices EX01–EX06 relèvent de tickets séparés, comme prévu par le ticket).

**SHA installé : `f9ae4a4` (merge de la PR #210, reprise du 26/10 au soir)** — première livraison : `bc806b3` (PR #195).

## Mise à jour du 2026-10-26 (soir) — exigences pédagogiques et visuelles du propriétaire

Suite au [commentaire du propriétaire](https://github.com/ReC82/jury-central/issues/192#issuecomment-6420068023)
et au corps du ticket complété (directives pédagogiques et visuelles, contrat de fin de
ticket). **État réel : Installé — à tester.**

### Ce qui a changé

1. **Numérotation réalignée sur les tickets déjà rédigés** : le plan livré plaçait le
   diagnostic matériel en PR14 et le RJ45 en PR19, alors que #193 = **PR06**, #194 = **PR11**,
   #197 = **PR15**. Nouveau découpage (`app/v1/ampcr_pratique_plan.py`) : P1 Matériel
   PR01–PR05 ; P2 Intervention et dépannage matériel PR06–PR08 ; P3 Systèmes d'exploitation
   et messages d'erreur PR09–PR14 ; P4 Câbles PR15–PR19 (RJ45, types/débits,
   caractéristiques, fibre, BNC) ; P5 Réseau PR20–PR24 ; P6 Partages et dépannage réseau
   PR25–PR30. Les 38 exigences restent toutes rattachées à un cours et un examen ; matrice
   et `docs/ampcr_pratique_v1.md` régénérées. Les sections ci-dessous qui citent l'ancienne
   numérotation sont remplacées par celle-ci.
2. **Modèle de ticket détaillé pour les 30 cours et 6 examens** :
   [`docs/ampcr_pratique_tickets.md`](https://github.com/ReC82/jury-central/blob/develop/docs/ampcr_pratique_tickets.md)
   — mode d'emploi, gabarit commun, exigences transversales (programme non improvisé,
   compléments signalés, visuels, évaluation, intégration), **contrat de fin de ticket**
   (rapport, email, commentaire), **checklist de validation éditoriale et visuelle**, et
   l'amorce des 36 tickets (titre, module, examen, exigences officielles en texte exact,
   théorie MC à réutiliser, écarts connus, sections « À compléter » pour la matière que vous
   rédigez). Généré depuis le plan (`python -m app.v1.ampcr_pratique_tickets`, ou `… PR07`
   pour un ticket complet prêt à coller) ; un test garantit qu'il reste synchronisé.
3. **Schémas techniques vérifiables** : `app/v1/ampcr_pratique_visuals.py` — figures SVG
   construites depuis des données (codes T568A/T568B testés, démarche en étapes, rangée de
   broches 8P8C avec fils blancs rayés pour le noir et blanc), accessibles (`role="img"`,
   titre, description, légende, mention « schéma non officiel »), fluides sur mobile et non
   coupées à l'impression. `validate_figure` refuse un schéma sans texte alternatif, sans
   légende, sans `viewBox`, avec script, ressource externe ou faux « officiel ».
   Démonstration : `/ampcr-pratique/format-exercice` (document 2 = schémas des deux
   connecteurs de l'exemple, tirés des mêmes données que le tableau ; démarche
   d'intervention en 6 étapes).
4. **Audit des capacités visuelles** (`docs/ampcr_pratique_v1.md` § 7) : génération d'images
   par API déjà en place (#108/#136 : commande manuelle, ≤ 2 essais, fichier statique + JSON
   du prompt, jamais à la consultation) — réservée aux scènes/gestes, jamais aux broches,
   textes ou valeurs ; aucune bibliothèque de diagrammes installée ; Mermaid et Graphviz
   écartés à ce stade (poids JS / binaire système = infrastructure).

### Vérifications

- 39 tests #192 verts (19 existants + 20 nouveaux : numérotation #193/#194/#197, codes
  T568A/B, ordre des broches dessinées, cohérence schéma/tableau/correction de l'exemple,
  garde-fous des figures, page format, synchronisation et contenu des 36 amorces).
- `ruff check` sans erreur sur les fichiers touchés. Suite complète non relancée (aucun
  changement du moteur partagé, modèles, sessions, seed ou `app/main.py`).
- Rendu réel contrôlé en Chromium headless : schémas à 360-390 px de large (lisibles, cadre
  corrigé), page complète en mobile ; impression A4 = 3 pages (fiche, corrigé, démarche),
  aperçu PDF non inspecté visuellement page par page.
- Après installation : services actifs, `/health` OK (local et public), `/ampcr-pratique`,
  `/matrice`, `/format-exercice` en 200 (3 figures servies), `/mon-parcours` 303 (connexion),
  compteurs inchangés 18/79/636, base sauvegardée avant installation.
- Email de la première livraison #192 : envoyé par l'orchestrateur le 2026-10-26 à 15:50:02Z
  avec le rapport joint (journal de notifications consulté en lecture seule).

### Choix faits seul

- Le code et le titre d'un ticket rédigé par le propriétaire font foi ; le plan s'adapte
  (modules de taille inégale plutôt que renuméroter vos tickets).
- PR06 couvre AP-15 (côté matériel), AP-17 et le complément AP-C02 ; PR11 couvre AP-09,
  AP-13 et AP-15 (côté logiciel) ; PR15 couvre AP-18 (paire torsadée), AP-20 et AP-34, comme
  le contenu de #197.
- Pas de nouvelle dépendance : SVG écrit en Python, comme les schémas FSE existants.
- Les blocs transversaux et le contrat ne sont écrits qu'une fois dans le document (§ 2) ;
  chaque amorce y renvoie, la commande produit un ticket complet.
- L'email de fin de ticket reste envoyé par l'orchestrateur (configuration SMTP existante) ;
  les sessions ne touchent pas au SMTP.

### Décisions demandées au propriétaire

1. **Nouveau découpage PR01–PR30** (aligné sur #193/#194/#197) : le valider ? Options : le
   garder ; ou fournir votre propre liste de 30 titres, que la prochaine session reprendra.
   Recommandation : le garder, il respecte vos trois tickets et couvre les 38 exigences.
2. **Examen blanc transversal** en plus des EX01–EX06 ? Recommandation inchangée : trancher
   lors des tickets EX.

### Reste à réaliser

Les tickets de cours et d'examens (rédigés à partir des amorces), dont #193, #194 et #197
déjà ouverts ; la création du module `AMPCR-PRATIQUE` en base revient au premier d'entre eux.

## Liens pour tester

- Accueil du parcours : https://jury-central.lodylands.com/ampcr-pratique
- Matrice de couverture : https://jury-central.lodylands.com/ampcr-pratique/matrice
- Format d'exercice (exemple non officiel, imprimable A4) : https://jury-central.lodylands.com/ampcr-pratique/format-exercice
- Modèles des 36 tickets PR/EX : https://github.com/ReC82/jury-central/blob/develop/docs/ampcr_pratique_tickets.md
- Accès depuis le tableau de bord : https://jury-central.lodylands.com/mon-parcours (tuile « AMPCR — Pratique écrite » sous « Mes matières »)
- Accès depuis la théorie : https://jury-central.lodylands.com/modules/ampcr (bouton « Pratique écrite (Laboratoire + T.P.) »)

Procédure courte : ouvrir `/mon-parcours` (option AMPCR) → tuile Pratique écrite → lire les
consignes du jour, parcourir les 6 modules (tous les emplacements « À venir ») et les liens
« théorie » ; ouvrir la matrice, vérifier les 38 lignes contre les pp. 5-6 du PDF, tester
l'impression (paysage conseillé) ; ouvrir le format d'exercice et imprimer (le corrigé passe
sur une 2ᵉ page). Vérifier sur mobile et desktop. Vérifier que `/modules/ampcr` et les MC
théoriques sont inchangés.

## 1. Source officielle — récupérée et tracée

Le PDF n'était pas dans le dépôt ni sur le serveur. Il a été retrouvé sur la page « Matières
du CESS P » du site des Jurys :

| Document | Version | Pages | SHA-256 |
|---|---|---|---|
| [Consignes pratique 26-27-1](https://jurys.cfwb.be/fileadmin/sites/jurys/secondaire/uploads/BDD_document/Consignes_specifiques/CESS/CESS_P/OBG/AMPCR/26-27-1-CESSP-Consignes-Assistant_Maintenance_PCreseaux-Pratique.pdf) | cycle 2026-2027/1, PDF créé le 2026-07-13 | 6 | `7a93c385…c4df095e1` |
| [Programme 345/2007/249](https://jurys.cfwb.be/fileadmin/sites/jurys/secondaire/uploads/BDD_document/Programmes/CESS/CESS_P/OBG/AMPCR/AMPCR.pdf) (complément) | applicable depuis 2008-2009, PDF modifié le 2015-10-29 | 46 | `95e45949…1a69bf14b` |

Empreintes complètes dans `docs/ampcr_pratique_v1.md` § 1 et sur la page matrice. Le contenu
correspond à la description du ticket (p. 3 écrit uniquement, 10/20 global, exceptions aux
dispenses ; p. 4 matériel, calculatrice non programmable sur instruction ; pp. 5-6 liste ;
p. 2 programme 345/2007/249). Le cycle 2026-2027/2 n'est pas encore publié.

## 2. Réutilisation de l'existant (audit)

- **Parcours** : rattaché à l'option AMPCR existante du registre `app/v1/parcours.py`
  (champ `practical_path` ajouté à `OptionDef`) — pas de nouveau diplôme/option.
- **Progression** : reprend `user_uaa_progress`/`uaa_state` (#136) et `progress.js`
  (« consulté ») dès qu'un cours PR sera publié.
- **Exercices** : aucun nouveau moteur ni type de question ; le format produit une question
  `document_analysis` (avec documents sources `create_source_document`) ou `long_answer`,
  donc sessions, autosave, correction IA batch, historique et impression existants.
- **Garde anti-acronyme** : même principe que `app/v1/course_coverage.py` (#83).
- **Aucune** table, migration, seed ou modification de contenu existant. MC01–MC38 inchangés.

## 3. Changements réalisés

| Fichier | Rôle |
|---|---|
| `app/v1/ampcr_pratique_plan.py` | sources (URL, version, date, SHA-256), consignes du jour (pp. 2-4, texte officiel), 38 exigences AP-01…AP-38 (texte exact pp. 5-6) + 2 compléments AP-C01/AP-C02, 6 modules, PR01–PR30, EX01–EX06, liens théorie, calcul du statut |
| `app/v1/ampcr_pratique_format.py` | format `PracticalExercise` (contexte, documents, consignes, barème, correction justifiée), validation, conversion vers les types existants, exemple non officiel |
| `app/v1/routes_ampcr_pratique.py`, `app/main.py` | routes `/ampcr-pratique`, `/matrice`, `/format-exercice` |
| `app/templates/ampcr_pratique_*.html` | 3 pages (responsive, impression) |
| `app/v1/parcours.py`, `parcours_dashboard.html`, `module_detail.html` | liens d'accès |
| `app/static/css/jc-theme.css` | styles et règles d'impression du parcours |
| `docs/ampcr_pratique_v1.md` | parcours, matrice complète, conventions de production des tickets PR/EX |
| `docs/current_state.md`, `docs/changelog.md`, `docs/INDEX.md` | mise à jour |
| `tests/test_ticket192_ampcr_pratique.py` | 19 tests |

## 4. Matrice — résumé

38 exigences officielles (18 p. 5, 20 p. 6), une ligne chacune, identifiant stable, texte
exact, page, cours prévus, exercice, théorie existante, statut, nature officiel/complément.
**État : 0 validée, 0 partielle, 38 non traitées — couverture non complète** (aucun cours
pratique n'existe encore). Une exigence ne passe « validée » que si tous ses cours PR ET son
exercice EX sont publiés et que son id est ajouté explicitement à `VALIDATED_REQUIREMENT_IDS`.

**Écarts de la théorie actuelle** (notions des pp. 5-6 absentes des MC publiés, contrôle
textuel) : FTP, coaxial/BNC, atténuation, impédance, comparaison fibre/cuivre (fibre seulement
citée en MC14), domaine/groupe de travail, NetBEUI, hub, répéteur Wi-Fi. À combler par les
cours PR correspondants (PR16–PR18, PR20, PR22, PR24–PR26).

## 5. Vérifications

- `tests/test_ticket192_ampcr_pratique.py` : 19 réussis (exhaustivité 38 lignes, ids, chaque
  exigence a un cours et un exercice, statut jamais « validé » sans cours + exercice +
  validation explicite, aucune durée dans les consignes, format → question réellement créée
  en base, refus des exercices interdits, pages 200, non-publiés jamais affichés, liens
  d'accès, doc synchronisée avec le code).
- Tests parcours/accueil/composition existants (#136, #137, #148, #84) : 50 réussis.
- Suite complète : 2167 réussis (16 min 47 s, une seule exécution).
- `ruff check` des fichiers créés/modifiés : aucune nouvelle erreur (4 B008 préexistants dans `app/main.py`).
- Après installation : services `jury-central` et `jury-central-correction-worker` actifs, `/health` OK (local et public), pages `/ampcr-pratique`, `/matrice`, `/format-exercice`, `/modules/ampcr`, `/uaa/ampcr-mc15`, `/parcours`, `/` en HTTP 200 (`/mon-parcours` 303 attendu sans parcours choisi), 40 lignes de matrice servies, compteurs inchangés (18 comptes / 79 sessions / 636 réponses), sauvegarde de la base faite avant installation, aucun seed nécessaire.
- **Non vérifié** : rendu visuel réel sur téléphone et aperçu d'impression navigateur (pas de
  navigateur sur le serveur) — à contrôler par le propriétaire.

## 6. Choix techniques faits seul

1. **Plan en code, sans base** : conforme à la règle du projet (« jamais de cours vide en base
   présenté comme disponible ») ; un emplacement n'apparaît « publié » que si une UAA publiée
   du module `AMPCR-PRATIQUE` porte son code.
2. **Découpage en 6 modules / 30 cours / 6 séries d'exercices** : le ticket fixe les nombres
   mais pas le contenu ; découpage proposé en suivant l'ordre et les blocs des pp. 5-6
   (matériel, systèmes, intervention/dépannage, câbles, réseau, partages/dépannage réseau),
   une série EX par module. Modifiable dans `_COURSE_ROWS` sans migration.
3. **Texte officiel** : recopié depuis l'extraction du PDF, espaces multiples réduits à un seul ;
   les deux puces proches (AP-09 / AP-13) sont conservées car toutes deux présentes.
4. **Compléments** : AP-C01 (rédiger une intervention justifiée — l'épreuve est écrite) et
   AP-C02 (sécurité électrique/ESD — prérequis du montage) marqués « complément pédagogique ».
5. **PDF non versionnés** dans le dépôt (documents officiels) : URL + empreinte suffisent à
   les retrouver et à détecter un changement.
6. **Exemple d'exercice** (câble RJ45 mal serti) affiché uniquement comme exemple de format
   « non officiel », jamais importé dans la banque ; aucune durée indiquée.
7. **Liens théorie** limités aux MC dont le texte mentionne réellement la notion.

## 7. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire pour ce socle. Points à confirmer à l'usage (non
bloquants, recommandation entre parenthèses) :

1. Le découpage proposé des 6 modules et des titres PR01–PR30 convient-il ? (Oui tel quel ;
   ajustable avant le premier ticket de cours.)
2. EX01–EX06 = une série d'exercices par module ; souhaitez-vous en plus un examen blanc
   pratique transversal ? (Le prévoir comme EX06 ou un emplacement à part lors des tickets EX.)

## 8. Reste à réaliser (tickets séparés)

- Cours PR01–PR30 (en commençant par les écarts du § 4) et exercices EX01–EX06 ; création du
  module `AMPCR-PRATIQUE` en base par le premier de ces tickets.
- Relecture du programme 345/2007/249 lors de chaque cours (complément, non transcrit).
- Mise à jour au cycle 2026-2027/2 (nouveau PDF à comparer).
