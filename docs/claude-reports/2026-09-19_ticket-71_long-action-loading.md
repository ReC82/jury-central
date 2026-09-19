# Ticket #71 — UX actions longues / double-clic

**Branche** : `feature/71-long-action-loading`, base `develop` (486f35c, PR #81 mergée).
Aucun merge, aucun déploiement effectué.

---

# 1. Protection cliente (UI) — meilleur effort, jamais la seule ligne de défense

`app/templates/v1_session_start.html` (practice ET exam, même gabarit) et
`app/templates/v1_session_submit_confirm.html` : au `submit` du formulaire, le bouton est
désactivé immédiatement, remplacé par un spinner Bootstrap + le texte demandé
(« Préparation de l'entraînement… » / « Préparation de l'évaluation… » /
« Correction en cours… »), et un message d'attente s'affiche (« Génération des questions
en cours. Merci de patienter quelques secondes. » / « Correction en cours. Merci de
patienter quelques secondes. »). Un second `submit` sur la même page (ex. touche Entrée
répétée) est ignoré (`event.preventDefault()` si déjà en cours d'envoi).

Réactivation explicite si la page est restaurée depuis le cache navigateur
(`pageshow` avec `event.persisted`, ex. retour arrière après une erreur serveur) — le
bouton ne reste jamais bloqué durablement côté client.

Cette protection reste contournable par construction (JS désactivé, requête rejouée
directement hors navigateur) — jamais la garantie réelle, voir § 2.

---

# 2. Protection serveur — la vraie garantie

## 2.1 Double POST sur « Commencer » (practice) — n'existait pas avant #71

L'examen était déjà protégé (§ 12 du ticket #55 : un examen `IN_PROGRESS` est toujours
repris, jamais dupliqué). **Practice ne l'était PAS** : le formulaire de démarrage
n'envoie jamais `resume=1`, donc un double POST (double-clic, requête rejouée) créait
deux `QuestionnaireSession` practice distinctes — potentiellement deux appels de
génération IA pour un seul clic utilisateur.

Nouvelle fonction `_is_unstarted(session)` (`app/v1/routes_sessions.py`) : vrai si une
session `IN_PROGRESS` existe pour cet utilisateur/UAA/mode et n'a **aucune réponse
enregistrée**. Appliquée dans `start_practice_session` et `start_ampcr_global_practice`,
avant toute création : si une session vierge existe déjà, on y redirige au lieu d'en
créer une nouvelle.

**Ne change pas la politique produit existante** (§ 12 du ticket #55 : « plusieurs
sessions practice simultanées autorisées ») — seule la répétition EXACTE et IMMÉDIATE
(aucune réponse entre les deux clics) est traitée comme un doublon accidentel. Une
deuxième tentative réellement voulue, après avoir commencé à répondre à la première
session, crée toujours une vraie deuxième session (vérifié par test explicite).

## 2.2 Double POST sur « Terminer et corriger » — réclamation atomique

Bug plus sérieux : `submit_session` (`app/v1/session_service.py`) ne marquait la session
`COMPLETED` qu'à la toute fin, APRÈS l'appel IA (potentiellement long de plusieurs
secondes — la fenêtre de la course). Un double POST pendant cette fenêtre lisait deux
fois `status == IN_PROGRESS` et déclenchait deux corrections IA complètes.

Fix : un `UPDATE ... WHERE status = 'in_progress'` atomique réclame la session AVANT
l'appel IA (`rowcount == 0` signale qu'une autre requête a déjà réclamé la session — on
s'arrête immédiatement, jamais un second appel). Le corps de la correction est extrait
dans `_correct_and_finalize_claimed_session`, appelé sous un filet de sécurité : toute
exception inattendue (hors `AIProviderError`, déjà gérée par le repli local existant)
remet `status = IN_PROGRESS` avant de se propager — jamais une session bloquée
`COMPLETED` sans résultat réel si quelque chose d'imprévu échoue.

---

# 3. Tests

Nouveau fichier `tests/test_ticket71_long_action_loading.py` (9 tests, aucun appel
OpenAI réel) :

1. **UI** : markup de chargement présent sur les pages start practice/exam et
   submit-confirm (bouton, spinner, textes exacts demandés).
2. **Double POST réel (même jeton CSRF, deux POST consécutifs)** : practice (nouveau —
   aurait échoué avant #71), exam (non-régression), practice globale AMPCR — toujours
   UNE seule session créée, jamais deux.
3. **Non-régression explicite** : une vraie deuxième tentative après avoir répondu à une
   question crée bien une session distincte — la politique multi-sessions n'est pas
   cassée.
4. **Double POST sur submit (HTTP réel)** : un seul appel `correct_semantic_batch`
   (`FakeAIProvider.semantic_calls`), session `COMPLETED`, score cohérent après les deux
   POST.
5. **Réclamation atomique au niveau service** : deux appels Python consécutifs à
   `submit_session` sur le même objet session — un seul appel IA, même résultat renvoyé
   par les deux appels.

Suite complète du dépôt : **1103 passed**. Ruff : **0 nouvelle erreur** (36
pré-existantes, hors fichiers touchés, confirmé par comparaison directe avec `develop`).

---

# 4. Fichiers modifiés

- `app/v1/routes_sessions.py` — `_is_unstarted`, appliquée dans
  `start_practice_session`/`start_ampcr_global_practice`.
- `app/v1/session_service.py` — réclamation atomique dans `submit_session`,
  `_correct_and_finalize_claimed_session` (corps extrait, filet de sécurité).
- `app/templates/v1_session_start.html` — état de chargement (practice + exam).
- `app/templates/v1_session_submit_confirm.html` — état de chargement (correction).
- `tests/test_ticket71_long_action_loading.py` — nouveau, 9 tests.
