# Ticket #86 — Sessions : choisir le nombre de questions avant entraînement ou évaluation

- Ticket : #86 — https://github.com/ReC82/jury-central/issues/86
- **État réel : Installé — à tester**
- PR : #176 (fusionnée dans `develop`) — branche `feature/86-session-question-count`
- **SHA installé : `6a904a7e22b7195e9efeed5b6f3de96dc9226682`**

## Résultat

Avant de démarrer un entraînement ou une évaluation, l'écran de démarrage affiche
**« Nombre de questions »** avec les choix **10 · 20 · 30 · 40**, plus **50** pour MC38 et le parcours
global AMPCR. Viennent ensuite la difficulté et le bouton « Commencer l'évaluation » ou
« Commencer l'entraînement ». Une indication non officielle s'affiche : « 10 ≈ révision rapide ·
20 ≈ standard · 30/40 ≈ examen approfondi ». Aucune durée officielle n'est indiquée.

- Couvert : entraînement et évaluation par mini-cours (AMPCR, Français, FSE), entraînement et examen MC38,
  entraînement et examen blanc global AMPCR, et FSE17.
- Valeur présélectionnée : 10 en entraînement, 20 en évaluation (MC, MC38, global).
- **Choix impossibles masqués** : quand la génération IA n'est pas disponible (pas de fournisseur
  configuré, génération du module en pause, ou FSE17 qui fonctionne uniquement sur la banque), seules les longueurs que la banque
  couvre sans doublon sont proposées. La plus courte est toujours proposée. En production la génération est
  active : tous les choix sont proposés et le manque est généré.
- **Persistance** : le choix est enregistré dans la session (`parameters_json.requested_question_count`).
  Le nombre réel reste `question_count`. L'historique (« Mes sessions ») et l'export Markdown
  affichent le choix lorsqu'il diffère du nombre réel, par exemple « 18 (choisi : 20) ».
- **Anti-doublon (#82)** : la garde finale est inchangée. Une session n'est jamais complétée en répétant une
  question. Si la banque et la génération ne suffisent pas, la session est plus courte.
- **Composition (§ C)** : le plafond par catégorie (MC38) ou par mini-cours (global AMPCR, FSE17) vaut
  `ceil(n / k)`, avec k = 3 valeurs distinctes à 10 questions, 4 à 20 et 6 à partir de 30 (Hardware, Systèmes, Réseaux,
  Wi-Fi/Sécurité, Dépannage, Métier). Ce plafond est borné au nombre de valeurs réellement présentes dans le pool.
- **Génération par lots** : au-delà de 20 questions manquantes, la génération est découpée en appels de 20.
  Les énoncés du lot précédent sont transmis comme « à éviter ». Si un lot suivant échoue, les lots déjà
  générés sont conservés. Pour MC38, chaque lot retire de nouveaux contextes MC01→MC37, ce qui élargit la couverture.

Fichiers : `app/v1/session_service.py`, `app/v1/routes_sessions.py`,
`app/templates/v1_session_start.html`, `app/templates/v1_history.html`,
`docs/current_state.md`, `tests/test_ticket86_session_length.py`.

## Tester (connecté)

- Entraînement MC01 : https://jury-central.lodylands.com/uaa/ampcr-mc01/practice
- Évaluation MC01 : https://jury-central.lodylands.com/uaa/ampcr-mc01/exam
- Examen MC38 (10→50) : https://jury-central.lodylands.com/uaa/ampcr-mc38/exam
- Examen blanc global AMPCR : https://jury-central.lodylands.com/modules/ampcr/exam
- Entraînement global AMPCR : https://jury-central.lodylands.com/modules/ampcr/practice
- Historique : https://jury-central.lodylands.com/mes-sessions

Procédure : choisir 30 ou 40, démarrer, attendre la préparation, puis vérifier « Question 1 / 30 »,
l'absence de doublon et la répartition des catégories. Interrompre puis reprendre : la taille est conservée.
Terminer, puis vérifier l'historique et l'export.

Remarque : une session de 40 ou 50 questions sur un mini-cours dont la banque est petite demande 2 ou 3 appels
de génération. Sa préparation est donc plus longue (page d'attente asynchrone #92, pas de 504).

## Vérifications

- `tests/test_ticket86_session_length.py` (16 tests) : options affichées (10–40, et 50 pour MC38/global),
  présélection, masquage des choix quand seule la banque est disponible, création 10/20/30/40 sans doublon, MC38 à 50,
  compteur « Question 1 / N », persistance, rejet des valeurs invalides (400), repli sur le volume historique
  quand le champ est absent, échec d'un lot suivant, historique et export, plafond de diversité selon la longueur.
  Aucun appel OpenAI réel (FakeAIProvider).
- Suite complète : 1955 passed, 1 échec (test #64 sur le plafond de diversité avec seulement 2 mini-cours),
  corrigé ensuite en bornant k au nombre de valeurs présentes. Re-vérification sur les fichiers liés aux
  sessions (#55, #58, #64, #82, #92, #101, #86) : 189 passed. La suite complète n'a pas été relancée après ce
  dernier correctif, limité à la fonction de plafond.
- Ruff : aucune erreur sur les fichiers modifiés.
- Installation : services actifs, `/health` OK en local et en public, pages en 303 (redirection vers la connexion,
  normal sans session), journaux sans erreur, compteurs utilisateurs/sessions/réponses inchangés (18/71/584).
  Sauvegarde de la base faite avant l'installation.
- Non vérifié : rendu visuel connecté et génération réelle de 30 à 50 questions avec l'IA de production
  (validation par le propriétaire).

## Choix techniques faits seul

1. **Formulaire sans le champ** (ancien formulaire en cache, appel direct) : le volume historique est conservé
   (10, ou 20 pour l'examen MC38/C01/FSE17/global). Le défaut « examen MC = 20 » est appliqué par la
   présélection de l'écran, comme le recommande le ticket.
2. **50 questions** seulement pour MC38 et le global AMPCR (§ A). FSE17 et Français C01 s'arrêtent à 40.
3. **Lots de 20** et non de 10 : les sessions de 10 et 20 restent à un seul appel IA, comme avant
   (invariant #55, comportement déjà éprouvé en production). Seules les sessions de 30 à 50 sont découpées.
4. **Plafond de longs sémantiques** (3 par session, #64) inchangé, quelle que soit la longueur.
5. **Valeur hors options** : HTTP 400, sans création de session.

## Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## Reste à faire

Rien dans le périmètre. Suites possibles, non implémentées : proposer 50 questions pour FSE17, et faire
évoluer le plafond de longs sémantiques avec la longueur de la session.
