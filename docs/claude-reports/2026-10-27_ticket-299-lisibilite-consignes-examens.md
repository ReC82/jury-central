# Ticket #299 — Lisibilité des consignes d'examen AMPCR pratique

- Ticket : [#299 — [P0][AMPCR pratique] Lisibilité des consignes d'examen : contexte, documents, données, questions numérotées](https://github.com/ReC82/jury-central/issues/299)
- **État réel : Installé — à tester**
- **SHA installé : `f9dc5957472db223404271cabcc84763d527fcf9`** (PR #311)
- Date : 2026-10-27

## Résultat

Les consignes des exercices pratiques AMPCR ne s'affichent plus en un seul bloc
« contexte… À faire : 1) … 2) … ». En entraînement, en examen blanc et sur la page de
résultats, chaque question pratique est présentée ainsi :

1. **Contexte** — la situation professionnelle (avec un repère « Partie n » pour les examens blancs) ;
2. **Documents à consulter** — liste des documents de la question, chaque entrée est un lien vers le document affiché juste en dessous ;
3. les documents eux-mêmes (rendu existant du ticket #149, inchangé) ;
4. **Données et règles** — encadré jaune pour les contraintes, conventions d'atelier et règles de calcul, lorsqu'elles sont identifiées ;
5. **Questions** — liste numérotée (une tâche par numéro), avec **sous-questions** en puces pour les consignes qui énumèrent plusieurs éléments (EX01 X01, EX04 X02 consignes 1 et 4) ; « À faire » quand il n'y a qu'une tâche.

Périmètre couvert : **les 757 exercices** des cours PR01–PR26 et des examens blancs EX01–EX04
(EX05, EX06 et PR27–PR30 ne sont pas encore publiés ; ils utiliseront automatiquement le même
composant s'ils sont rédigés avec le même format `context` / `instructions`).

Inchangé : texte de la consigne enregistrée en base, barème, critères, corrigé, contenu envoyé
au correcteur IA, notation. Aucun indice ni réponse ajouté, aucune question transformée en QCM.
Les autres matières (Français, FSE, AMPCR théorique) gardent l'affichage d'origine.

## Changements

- `app/v1/prompt_layout.py` (nouveau) : construit la présentation à partir des champs
  `context` et `instructions` de l'exercice, retrouvé par le **texte exact** de la consigne
  enregistrée. `ANNOTATIONS` : quelques extraits mot pour mot déplacés dans « Données et
  règles » ou découpés en sous-questions (EX01–EX04) ; `validate_annotations()` vérifie qu'ils
  existent et que rien n'est perdu.
- `app/templates/_prompt_layout.html` (nouveau) : composant commun (macros `situation`, `questions`).
- `app/templates/v1_session_question.html`, `app/templates/v1_session_results.html` : utilisation du composant, repli sur l'affichage d'origine.
- `app/templating.py` : enregistrement de `prompt_layout`.
- `app/static/css/design-system.css` : styles `.jc-pl-*` (écran, téléphone ≤ 576 px, impression A4 sans coupure à l'intérieur d'un bloc).
- `tests/test_ticket299_prompt_layout.py`, `docs/current_state.md`.

## Liens pour tester

- Examen blanc EX04 (calculs IPv4, plusieurs documents, sous-questions) : https://jury-central.lodylands.com/uaa/ampcr-pratique-ex04/exam
- Examen blanc EX01 (données et règles : puissance du bloc, températures, SMART) : https://jury-central.lodylands.com/uaa/ampcr-pratique-ex01/exam
- Examens blancs EX02 / EX03 : https://jury-central.lodylands.com/uaa/ampcr-pratique-ex02/exam — https://jury-central.lodylands.com/uaa/ampcr-pratique-ex03/exam
- Entraînement d'un cours (ex. PR20) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr20/practice
- Parcours : https://jury-central.lodylands.com/ampcr-pratique

Procédure : démarrer un examen blanc, parcourir les questions (ordinateur et téléphone),
cliquer un lien de « Documents à consulter », imprimer une page (Ctrl+P, A4), terminer
l'examen et ouvrir les résultats. Une session déjà commencée s'affiche aussi avec la
nouvelle présentation, réponses conservées.

## Vérifications effectuées

- Les 757 consignes ont une présentation ; pour chacune, contexte affiché + données et règles
  = contexte d'origine **mot pour mot**, questions = consignes d'origine, sous-questions sans
  perte (test automatique).
- Session d'examen EX04 complète (10 questions) : ordre contexte → documents → données →
  questions, liens vers des documents présents sur la page, pas de corrigé ni de barème,
  plus de bloc « À faire : » ; soumission, correction (fournisseur simulé) et résultats OK.
- Question de Français : affichage d'origine conservé.
- Tests : `test_ticket299` (6) + documents #149/#79, EX01–EX04, PR06, quiz : 245 passés ;
  29 autres fichiers AMPCR pratique et résultats : 826 passés. `ruff` propre sur les fichiers modifiés.
- Base en lecture seule : les 58 versions de questions pratiques déjà importées (dont 30
  utilisées dans des sessions) correspondent toutes à une présentation — aucune session
  ni copie invalidée, aucune donnée modifiée. Compteurs utilisateurs/sessions/réponses
  identiques avant/après (18 / 84 / 661). Sauvegarde de la base prise avant installation.
- Après installation : deux services actifs, `/health` local et public OK, pages EX01, EX04,
  PR20 et parcours en HTTP 200, nouvelle feuille de style servie.

Non effectué : contrôle visuel réel (navigateur, téléphone, impression) — à faire par le
propriétaire ; pas de suite de tests complète (moteur partagé non modifié).

## Choix techniques faits seul

- **Structure explicite, pas de découpage automatique** : les exercices pratiques ont déjà
  contexte et consignes séparés dans le code ; on retrouve l'exercice par le texte exact de
  la consigne enregistrée. Si le texte ne correspond pas (ancienne version, autre matière),
  l'affichage d'origine est conservé plutôt qu'un découpage approximatif.
- **Aucune migration de données** : seule la présentation change ; ainsi aucune session en
  cours ni copie rendue n'est touchée, et le correcteur reçoit exactement le même texte.
- « Données et règles » n'est rempli que pour les phrases clairement normatives (règles
  d'atelier, conventions, contraintes) des examens blancs ; ailleurs, le contexte reste un
  paragraphe unique plutôt que d'inventer une séparation.
- Les documents restent affichés à leur place (au-dessus de la carte réponse) ; la liste
  « Documents à consulter » ne fait que les nommer et y renvoyer.

## Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## Reste à réaliser

- Validation visuelle par le propriétaire (ordinateur, téléphone, impression A4).
- Si certains contextes d'entraînement PR01–PR26 vous paraissent encore denses, indiquez les
  exercices : on peut ajouter des extraits « Données et règles » ciblés (même mécanisme vérifié).
- EX05, EX06 et PR27–PR30 bénéficieront du composant à leur publication.
