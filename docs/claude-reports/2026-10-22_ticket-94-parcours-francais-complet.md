# Ticket #94 — URGENT Français : parcours complet 20 mini-cours + entraînements + évaluations

- Ticket : [#94](https://github.com/ReC82/jury-central/issues/94)
- **État réel : Installé — à tester** (les 20 cours FR01→FR20 sont en ligne)
- SHA installé : `bcef613cb446aaa6e31a2a134f6b3c5b54138e4d`
- PR : [#178](https://github.com/ReC82/jury-central/pull/178) (phases B + C), [#179](https://github.com/ReC82/jury-central/pull/179) (phase D)

## Synthèse

Le parcours Français CESS P compte maintenant **20 mini-cours publiés**, chacun avec sa
page de cours, son entraînement et son évaluation, sur le moteur de sessions existant
(génération et correction asynchrones, documents sources visibles pendant la question et
la correction, export, historique). **FR20** est à la fois le cours de méthode de l'épreuve
et l'**examen blanc final** : ses sessions mélangent des questions des cours FR01 à FR19.

| Phase | Cours | État avant cette session | Fait aujourd'hui |
|---|---|---|---|
| A | FR01→FR05 | déjà en ligne (20/09) | inchangé (audits élargis) |
| B | FR06→FR10 | rédigée le 20/09 sur une branche jamais fusionnée | intégrée au `develop` actuel, corrigée, installée |
| C | FR11→FR15 | rien | rédigée et installée |
| D | FR16→FR20 | rien | rédigée et installée, FR20 examen blanc transversal |

## Changements réalisés

### Phase B (FR06→FR10) — reprise
- Branche `feature/94-french-fr06-10` fusionnée avec le `develop` actuel (conflits
  résolus dans `app/v1/session_service.py` et dans les compteurs du test de seed).
- Le correctif de cette branche est conservé : le complément IA d'une session Français
  n'utilise jamais de QCM, d'ordering ni de diagnostic (`FRANCAIS_EXCLUDED_GENERATION_TYPES`).
- Défaut corrigé (règle #151) : dans le mini-test FR09, « Document 3 » était affiché en
  2e position. Les trois documents du mini-test sont maintenant titrés « Document N — Mini-test : … ».
- Deux classifications sans support rattaché (FR07 « extraits des sources », FR10
  « arguments du mini-test ») reçoivent maintenant leurs documents.

### Phase C (FR11→FR15) — nouvelle
Fichiers `app/v1/francais_fr11_15_{content,bank,courses}.py`.
- FR11 Construire un argument développé ; FR12 Rédiger un texte argumentatif ; FR13
  Utiliser un dossier documentaire dans son argumentation ; FR14 Réclamation et
  adaptation au destinataire ; FR15 Défendre une opinion oralement.
- 18 documents originaux (paragraphes modèles, lettre ouverte, dossier « rue scolaire »
  en 3 documents, courriels de réclamation, transcriptions d'interventions orales…),
  41 questions.

### Phase D (FR16→FR20) — nouvelle
Fichiers `app/v1/francais_fr16_20_{content,bank,courses}.py`.
- FR16 Discuter et négocier ; FR17 Comprendre et transformer une œuvre culturelle
  (nouvelles originales) ; FR18 Amplifier, recomposer et transposer ; FR19 Relater une
  expérience culturelle et motiver son appréciation ; FR20 Méthodologie complète de
  l'épreuve et examen final.
- 13 documents originaux pour FR16→FR19, 32 questions ; FR20 contient un sujet complet
  d'entraînement commenté, une grille de relecture et un tableau qui renvoie vers les
  cours FR01→FR19.
- **FR20 examen blanc** : entraînement 10 questions par défaut, évaluation 20 par défaut
  (10 à 40 au choix). Questions tirées uniquement dans les banques FR01→FR19, sans
  génération IA (comme FSE17). Ouvrir FR20 prépare au besoin les banques FR01→FR19.
  Reprise d'une session en cours, historique (« FR20 — Examen blanc final (FR01→FR19) »),
  export (`…fr20-examen-blanc…`) et progression du parcours attribuée à FR20.
- Moteur : la composition FSE17 est passée dans une fonction commune
  `_start_bank_transversal_session` (FSE17 et FR20) et la sélection dans
  `_select_courses_bank_questions` (`app/v1/bank.py`). Le comportement de FSE17 ne change pas.

### Contenu commun aux 20 cours
- Chaque cours suit 10 sections : savoir-faire attendu, théorie progressive, définitions,
  méthode, exemples commentés, mauvaises vs bonnes réponses, pièges, exercices guidés
  (corrigé masqué), corrigés expliqués, fiche mémo (reprise dans « À retenir », #136).
- Types de questions limités au Français : réponse courte, réponse longue, analyse de
  document, comparaison de sources, vocabulaire, classification. Pas de QCM.
- Tout support cité par une question est un vrai document affiché pendant la question et
  la correction, et transmis tel quel au correcteur IA.

## Tester

SHA installé : `bcef613cb446aaa6e31a2a134f6b3c5b54138e4d` — https://jury-central.lodylands.com

1. Liste des 20 cours : https://jury-central.lodylands.com/modules/francais
2. Exemples de cours :
   - https://jury-central.lodylands.com/uaa/francais-fr06 (phase B)
   - https://jury-central.lodylands.com/uaa/francais-fr13 (dossier documentaire)
   - https://jury-central.lodylands.com/uaa/francais-fr15 (oral)
   - https://jury-central.lodylands.com/uaa/francais-fr17 (œuvre culturelle)
   - https://jury-central.lodylands.com/uaa/francais-fr20 (méthode + examen blanc)
3. Entraînement d'un cours : https://jury-central.lodylands.com/uaa/francais-fr13/practice
   → « Commencer » → vérifier les boutons « Voir le texte » / « Ouvrir dans un nouvel
   onglet » sur les questions de dossier → soumettre → correction → « cours à relire ».
4. Examen blanc final : https://jury-central.lodylands.com/uaa/francais-fr20/exam →
   20 questions issues de plusieurs cours → soumettre → résultats, export, historique
   (https://jury-central.lodylands.com/mes-sessions).

## Vérifications effectuées

- Suite complète après fusion de `develop` + phase B : **1977 passed**.
- Suite complète finale (phases B + C + D) : **2004 passed, 1 failed**. L'échec venait d'une assertion de mon test phase C (« FR11→FR15 sont les 5 derniers importeurs »), devenue fausse avec FR16→FR19 ; l'assertion est corrigée et le fichier passe ensuite à 15/15.
- Tests dédiés : `tests/test_ticket94_french_fr06_10.py` (20), `…_fr11_15.py` (15),
  `…_fr16_20.py` (13), plus `tests/test_ticket94_french_20_courses.py` et les tests
  #136/#137/#148/#149/#151/#152/#86/#75/#45/#46/#77/#79/#92 relancés.
- Audits sur les banques FR01→FR19 (153 questions) : 0 renvoi « Document N » non résolu
  (#151), 0 consigne dépendante d'un contexte absent (#152), 0 question qui cite un
  support sans document rattaché.
- Ruff : 0 nouvelle erreur (65 erreurs avant comme après, toutes antérieures).
- Installation : sauvegarde de la base avant chaque installation, seed idempotent, deux
  services `active`, `/health` OK en local et en public, pages FR01→FR20 en HTTP 200,
  entraînement et évaluation redirigent vers la connexion (303), comme pour les autres
  cours. Compteurs utilisateurs/sessions/réponses : 18 / 71 / 584 avant et après chaque installation (jamais en baisse).
- **Non effectué** : aucune session réelle lancée sur le site (cela aurait créé des données
  dans un compte). Le parcours complet est couvert par les tests avec `FakeAIProvider` ;
  la qualité réelle de la correction IA sur ces nouvelles consignes reste à vérifier par
  l'usage.

## Choix techniques faits seul

1. **Reprise de la phase B existante** plutôt qu'une réécriture : contenu déjà rédigé le
   20/09, jamais fusionné. Il a été intégré, contrôlé et corrigé.
2. **Phases B, C et D livrées dans la même session**, en deux installations (B+C puis D),
   pour rendre le parcours complet visible au plus vite, comme le ticket le demande.
3. **FR20 strictement banque**, sans génération IA, comme FSE17. Le contexte « méthode »
   de FR20 produirait des questions méta, le défaut déjà constaté sur MC38, et les
   153 questions de FR01→FR19 suffisent pour 40 questions sans doublon.
4. **C01 exclu de l'examen blanc** : c'est le pilote historique (#47), déjà caché de la
   liste publique.
5. **FR20 garde sa fiche « À retenir »**, contrairement à MC38/FSE17 : c'est un vrai cours
   de méthode avec sa propre fiche mémo.
6. **Factorisation FSE17/FR20** (`_start_bank_transversal_session`) plutôt qu'une copie
   de 60 lignes. FSE17 garde exactement le même comportement (suite complète verte).
7. **Œuvres culturelles fictives** (nouvelles, exposition, concert, pièce) : aucun
   problème de droits, et l'élève a toujours le texte complet sous les yeux.
8. **FR15 (oral)** : l'oral n'est pas enregistré. Les questions portent sur la
   préparation écrite (fiche aide-mémoire, ouverture, réponse à une objection) et sur
   l'analyse de transcriptions.
9. **Organisation officielle de l'épreuve** (durée, barème) non inventée : FR20 la
   présente comme un exemple et renvoie à l'établissement ou au jury.
10. **Nouveau rapport daté** plutôt que la suite des rapports du 20/09 : ces rapports
    (phases A et B) portaient la consigne « NE MERGE RIEN », devenue fausse.
11. **Seed** : en plus des 15 nouveaux cours, le seed a remplacé à l'identique 52 blocs
    FSE. C'est le mécanisme de rafraîchissement existant (même contenu, nouveaux id). Le
    nombre de blocs n'augmente que du nombre de nouveaux cours.

## Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## Éléments restant à réaliser

- Validation pédagogique et visuelle des 15 nouveaux cours par le propriétaire.
- Suites possibles (non faites, hors périmètre) : répartir les questions de l'examen
  blanc FR20 par parties (lecture / réduction / production), comme une épreuve réelle ;
  passer les cours Français au découpage en blocs titrés utilisé par FSE (#105) pour
  profiter des cartes visuelles ; enrichir chaque banque au-delà de 8-9 questions, pour
  limiter le complément IA en entraînement de 20 à 40 questions.
