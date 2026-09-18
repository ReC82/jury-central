# Ticket #62 — Correction pédagogique IA, historique, impression et export

**Date** : 2026-09-18
**Branche** : `feature/62-training-feedback-history-export`

---

## 1. Contexte

Après validation staging du moteur AMPCR (#55/#57/#58), plusieurs problèmes UX/
pédagogiques bloquants ont été observés : une erreur objective (ordering, classification,
QCM...) ne renvoyait qu'un message générique — « Correction automatique déterministe (pas
d'appel IA nécessaire). » — sans expliquer NI le raisonnement attendu NI la notion à
revoir. Aucune sévérité de correction réglable, aucun historique des sessions, aucune
impression/export des résultats.

Ce ticket ne touche pas au moteur de session (#55/#57/#58, inchangé) ni au Français
(`feature/47-francais-v1`, non rebasé sur cette branche — construite depuis `develop`
seul, comme demandé).

---

## 2. Architecture — correction hybride (§ 2/3/15/16 du ticket)

`app/v1/hybrid_correction.py` (nouveau) : `correct_session_hybrid()` remplace l'appel à
`app.ai.questionnaire.correct_questionnaire()` dans `submit_session()`, en UN SEUL appel
IA batch maximum, qui regroupe :

- **(A) questions sémantiques** nécessitant une notation IA — comportement strictement
  identique à avant (via `validate_semantic_correction`, réutilisé tel quel).
- **(B) questions déterministes INCORRECTES** — score déjà calculé par `correct_locally`
  (inchangé, aucun appel réseau), envoyées dans le MÊME lot IA avec un `rubric` augmenté
  d'une instruction explicite (« ce score est déjà fixé, n'explique que le
  raisonnement ») pour obtenir une VRAIE explication pédagogique. Une question
  déterministe CORRECTE n'est jamais envoyée à l'IA (§ 3 : pas besoin d'explication sur
  une bonne réponse).

**Aucune modification du contrat #23** (`app.ai.questionnaire`/`app.ai.schemas`/
`app.ai.prompts`, hors extension de l'échelle de sévérité, § 3 ci-dessous) : une question
déterministe est envoyée à `provider.correct_semantic_batch` comme n'importe quelle
question du lot — le format de requête/réponse ne change pas, donc
`app/editorial_ai_correction.py` (seul autre appelant de `correct_semantic_batch`) n'est
affecté en rien.

**Verrouillage du score (§ 3, SERVER_SCORE_LOCKED)** : après réponse de l'IA, pour les
questions déterministes, seuls les champs textuels (`strengths`/`errors`/`missing`/
`feedback`) sont retenus — `points_awarded`/`points_max`/`correct`/`expected_answer`
restent strictement ceux de `correct_locally`, quoi que l'IA renvoie. Testé avec un
fournisseur volontairement malveillant (`points_awarded=999` renvoyé) : le score reste
`0/1`, inchangé.

**Réponse humainement lisible pour l'IA** (§ batch) : la représentation interne d'une
réponse déterministe (ex. une liste d'index pour `ordering`) est remplacée, uniquement
dans le batch d'explication, par sa description lisible (`app.v1.ai_bridge.
describe_submitted_answer`, déjà utilisée par l'écran de résultats — ex.
« SSD → RAM → écran → CPU ») : l'IA reçoit une vraie réponse à commenter, pas des indices
opaques.

---

## 3. Sévérité 1-5 (§ 5/6/7 du ticket)

`app.ai.schemas.SEVERITY_LEVELS` étendu de 3 à 5 valeurs internes (`very_lenient`,
`lenient`, `standard`, `strict`, `very_strict`) — les 3 valeurs déjà testées
(`lenient`/`standard`/`strict`) gardent leur comportement/texte inchangés (voir
`tests/ai/test_questionnaire.py::test_correct_questionnaire_severity_changes_points_not_facts`,
toujours vert), les 2 nouvelles étendent l'échelle aux deux extrêmes.

`app/v1/session_service.py` : `SEVERITY_UI_LEVELS = (1,2,3,4,5)`, `SEVERITY_UI_DEFAULT = 3`,
`SEVERITY_UI_LABELS` (libellés français exacts du ticket), mappés vers les 5 valeurs
internes. Choisie sur l'écran de confirmation (`v1_session_submit_confirm.html`, avant
« Terminer et corriger »/« Terminer l'évaluation »), zone de sélection large (padding +
séparateurs) pour rester utilisable au doigt sur mobile.

**N'influence que le sémantique** : testé explicitement (`test_severity_does_not_change_
deterministic_outcome`) — un ordering faux reste à 0 point en very_lenient ET
very_strict ; et (`test_severity_changes_semantic_points_awarded`) — une réponse longue
identique obtient plus de points en lenient qu'en very_strict.

---

## 4. Persistance de la sévérité (§ 7)

`QuestionnaireSession.parameters_json` (colonne JSON déjà présente, ticket #58) — fusion
sans écraser d'éventuelles autres clés (ex. `{"scope": "mc38"}`) :
`parameters_json["severity"] = severity_ui`. Aucune migration de schéma. Une session
`COMPLETED` conserve définitivement sévérité/score/réponses/feedback (immuable, inchangé
depuis #55).

---

## 5. Historique utilisateur (§ 8/9)

`GET /mes-sessions` (nouveau, `app/v1/session_service.py::list_user_sessions`/
`describe_session_scope`) : liste les sessions du user connecté uniquement (isolation
stricte testée), les plus récentes d'abord. Par session : date/heure, matière, module/
mini-cours (dérivé de l'UAA des questions, ou marqueur `scope` MC38, ou « Parcours
global » si plusieurs UAA — aucune nouvelle colonne), PRACTICE/EXAM, score, nombre de
questions, sévérité si terminée, statut (badge En cours/Terminé), action (Reprendre/Voir
les résultats). Lien ajouté à la navigation (`base.html`, visible uniquement connecté).

**Reconnexion testée explicitement** (§ 9) : terminer un entraînement → logout → login →
historique → session terminée retrouvée → résultats ouverts avec succès ; même chose pour
une session `IN_PROGRESS`, reprise avec succès.

---

## 6. Résultats — accordéons multiples, tout déplier/replier (§ 10/11)

`data-bs-parent="#results-accordion"` retiré de chaque `.accordion-collapse` — chaque
panneau devient indépendant, plusieurs questions peuvent rester ouvertes simultanément
(vérifié : aucun `data-bs-parent` dans le HTML rendu). Deux boutons (« Tout déplier »/
« Tout replier ») pilotent tous les panneaux via l'API JS `bootstrap.Collapse` (script
inline minimal, réutilise le bundle Bootstrap déjà chargé par `base.html`, aucune
dépendance ajoutée) — fonctionnent identiquement desktop/mobile (boutons Bootstrap
standards, pas de media query spécifique nécessaire).

---

## 7. Impression / PDF (§ 12)

Bouton « Imprimer / PDF » → `window.print()` (mécanisme navigateur, aucune dépendance
lourde, conforme à la consigne). CSS `@media print` dédiée :
- `.accordion-collapse { display: block !important; }` — force TOUTES les questions
  visibles à l'impression, y compris celles repliées à l'écran (testé : les 10 titres
  `Question N —` sont présents dans le HTML source, jamais générés dynamiquement).
- `.accordion-item { break-inside: avoid; }` — évite qu'une question soit coupée entre
  deux pages autant que possible.
- `@page { size: A4; margin: 1.5cm; }`.
- Navigation/pied de page déjà masqués par `.d-print-none` (utilitaire Bootstrap déjà
  utilisé ailleurs dans le projet) ; boutons d'action (déplier/replier/imprimer/export/
  retour accueil) explicitement masqués à l'impression via la même classe.
- Titre, matière/module, date, score et sévérité affichés en tête de page (déjà dans le
  flux normal, donc imprimés).

Le choix Imprimer vs Enregistrer en PDF appartient à la boîte de dialogue d'impression du
navigateur (comportement standard de `window.print()`), conforme à la consigne.

---

## 8. Export Markdown (§ 13)

`GET /sessions/{id}/export.md` (nouveau) : vérifie la propriété de la session (404 pour
un autre utilisateur — testé), exige `COMPLETED` (409 sinon — testé), construit un
Markdown structuré exactement comme demandé (Métadonnées puis une section par question :
énoncé, Ma réponse, Attendu/critères, Points, Points forts, Erreurs, Éléments manquants,
Explication), servi en téléchargement (`Content-Disposition: attachment`,
`text/markdown`). Nom de fichier : `jury-central_{scope}_{mode}_{date}.md` (ex.
`jury-central_mc01_practice_2026-09-18.md`, conforme à l'exemple du ticket). Le
constructeur de lignes de résultat (`_build_results_rows`) est factorisé entre l'écran
HTML et l'export — jamais deux implémentations divergentes.

---

## 9. Fichiers

**Nouveaux** :
- `app/v1/hybrid_correction.py`
- `app/templates/v1_history.html`
- `tests/test_ticket62_hybrid_correction_history_export.py` (31 tests)
- `docs/claude-reports/2026-09-18_ticket-62_training-feedback-history-export.md` (ce
  rapport)

**Modifiés** :
- `app/ai/schemas.py` (`SEVERITY_LEVELS` étendu à 5 valeurs)
- `app/ai/prompts.py` (`SEVERITY_INSTRUCTIONS` : 2 nouvelles entrées, 3 existantes
  inchangées)
- `app/ai/fake_provider.py` (facteur de sévérité étendu, 3 valeurs historiques
  inchangées)
- `app/v1/session_service.py` (`submit_session` hybride + sévérité, `describe_session_
  scope`, `list_user_sessions`, constantes `SEVERITY_UI_*`)
- `app/v1/routes_sessions.py` (route `/mes-sessions`, route export, sévérité sur
  `/submit`, `_build_results_rows` factorisé)
- `app/templates/v1_session_submit_confirm.html` (sélecteur de sévérité)
- `app/templates/v1_session_results.html` (multi-expand, tout déplier/replier, CSS print,
  boutons imprimer/export)
- `app/templates/base.html` (lien navigation « Mes entraînements »)

---

## 10. Tests

`tests/test_ticket62_hybrid_correction_history_export.py` (31 tests) — deux niveaux :

**Unitaire** (`app.v1.hybrid_correction`, sans DB/HTTP) : score déterministe identique
avec/sans passage par le lot IA ; IA ne peut pas modifier le score déterministe (fournisseur
malveillant simulé) ; ordering/classification faux reçoivent une explication IA réelle
(plus le message générique) ; réponse déterministe correcte jamais envoyée à l'IA ; un
seul appel batch mélangeant sémantique + explication ; les 5 niveaux de sévérité internes
acceptés ; sévérité sans effet sur le résultat déterministe ; sévérité modifie bien les
points sémantiques attribués.

**HTTP de bout en bout** : sélecteur de sévérité par défaut = 3 ; sévérité persistée dans
`parameters_json` ; aucune fuite de solution avant soumission ; historique affiche
sessions terminées ET en cours avec les bons libellés/actions ; reconnexion (logout/login)
retrouve une session terminée dans l'historique et permet d'ouvrir ses résultats ; même
chose pour une session en cours (reprise) ; plusieurs panneaux de résultats ouvrables
simultanément (`data-bs-parent` absent) ; boutons Tout déplier/Tout replier présents et
fonctionnels (JS) ; bouton Imprimer + CSS `@media print` forçant l'affichage de toutes les
questions ; export contient les 10 questions avec toutes les sections demandées ; export
refusé (404) pour un autre utilisateur, refusé (409) avant soumission ; historique
strictement isolé entre deux utilisateurs ; soumission ne plante jamais sans clé OpenAI
configurée (repli local) ; non-régression MC01/MC17/MC31/MC38 (practice + résultats).

Aucun appel OpenAI réel : `FakeAIProvider` partout où une correction IA est exercée.

---

## 11. Résultat pytest (suite complète)

```
921 passed, 2 warnings in 202.48s (0:03:22)
```

(890 avant ce ticket + 31 nouveaux). Les 2 warnings sont préexistants (httpx/anyio), sans
lien avec ce ticket.

---

## 12. Résultat Ruff

```
Found 36 errors.
```

Identique à la base (`app/admin.py`/`app/main.py`/`app/practice.py` B008 Depends,
`tests/conftest.py` RUF100 — tous préexistants). **0 nouvelle erreur.**

---

## 13. `git diff --check`

```
$ git diff --check origin/develop...HEAD
(aucune sortie, exit code 0)
```

---

## 14. Non-régression

MC01/MC17/MC31/MC38 : practice + résultats re-testés explicitement (paramétré), tous
verts. Aucune route renommée/supprimée. `correct_questionnaire()` (#23) reste inchangé et
continue de fonctionner pour `app/editorial_ai_correction.py` (non touché par ce ticket).

---

## 15. Limites assumées

- **Qualité pédagogique réelle des explications** non vérifiable en pytest (`FakeAIProvider`
  déterministe, jamais un vrai texte pédagogique) — seule la PLOMBERIE (verrouillage du
  score, inclusion dans le même lot, remplacement du message générique) est testée
  automatiquement ; la qualité réelle du texte généré nécessite une validation manuelle
  sur staging avec un vrai fournisseur, comme pour tout le reste du moteur IA.
- **Export uniquement Markdown** (pas de PDF serveur) — conforme au choix MVP recommandé
  par le ticket ; l'impression navigateur (`window.print()`) couvre le besoin PDF sans
  dépendance lourde côté serveur.
- **Historique sans pagination** — acceptable au volume actuel (un seul pilote
  utilisateur avant l'examen) ; à revisiter si le nombre de sessions par utilisateur
  devient important.
- **Retry IA après échec non implémenté** (§ 16 : « permettre éventuellement de relancer
  l'enrichissement IA plus tard si simple, sinon documenter la limite ») — une session
  dont la correction IA a échoué reste `COMPLETED` avec repli local (score déterministe
  correct, explications génériques) ; relancer l'enrichissement a posteriori
  nécessiterait de rouvrir une session `COMPLETED` (violerait son immutabilité, #55) —
  hors périmètre de ce ticket, documenté ici comme limite assumée plutôt qu'implémenté à
  la hâte.

---

## Statut

Implémentation, tests et documentation terminés. `pytest -q` (suite complète) : 921
passed. Ruff : 36 erreurs, 0 nouvelle. `git diff --check` : propre. Aucun appel OpenAI
réel. Aucune modification de `jury_central.db`. Prêt pour commit/push. **Aucun merge,
aucun déploiement.** Le Français (`feature/47-francais-v1`) et #45/#46/#48 n'ont pas été
touchés.
