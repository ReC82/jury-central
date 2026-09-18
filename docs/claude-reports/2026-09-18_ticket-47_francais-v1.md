# Ticket #47 — Français V1 : premier parcours complet

**Date** : 2026-09-18
**Branche** : `feature/47-francais-v1`

---

## 1. Constat initial et recadrage

Le ticket demandait de « réutiliser les contenus Français déjà présents dans le
projet ». Vérification exhaustive du dépôt (code source ET base de données staging) :
**aucun contenu Français n'existait** — aucune Subject « Français », aucun
`SourceDocument`, aucun cours (confirmé par `docs/content_plan_informatique_francais.md`
§ 3.3, écrit le 2026-09-16, et par une recherche de fichiers `*francais*`/`*français*`
dans tout le dépôt). Seule l'infrastructure technique générique existait déjà : le moteur
de session (#55/#57/#58), le modèle `SourceDocument`/`SourceDocumentVersion` (#38), et les
types `document_analysis`/`source_comparison` du registre #40 (déjà « priorité Français »
dans leur commentaire d'origine, jamais branchés).

Face à ce constat, l'utilisateur a validé explicitement (question posée, réponse
confirmée puis précisée) : créer un **premier parcours Français MINIMAL mais
fonctionnel, avec un texte support original de 600-900 mots rédigé spécifiquement pour ce
ticket**, explicitement marqué comme contenu de validation technique — jamais présenté
comme un examen CESS officiel. Le vrai corpus pédagogique remplacera ce texte dès qu'il
sera fourni.

**FRENCH_CONTENT_STATUS=PROVISIONAL_TECHNICAL_SAMPLE** — voir § 10.

---

## 2. Contenu provisoire

`app/v1/francais_content.py` — deux textes originaux (aucun texte protégé copié) :

- **Texte principal** (630 mots) : « Le smartphone au quotidien : outil précieux ou
  distraction permanente ? » — usage à l'école, au travail, dans la vie personnelle ;
  avantages et inconvénients ; conclusion nuancée (usage raisonné). Non polémique,
  niveau CESS.
- **Second texte** (189 mots) : point de vue contrasté (interdiction totale du smartphone
  en classe) — utilisé pour la comparaison de documents (`source_comparison`).

11 questions hand-authored (`app/v1/francais_bank.py`), mélangeant les 10 catégories
demandées par le ticket et les 5 types prioritaires :

| # | Type | Catégorie (ticket) |
|---|---|---|
| 1 | short_answer | compréhension explicite |
| 2 | short_answer | compréhension implicite |
| 3 | vocabulary | vocabulaire en contexte |
| 4 | classification | distinguer fait / opinion |
| 5 | document_analysis | justification avec élément du texte |
| 6 | short_answer | reformulation |
| 7 | short_answer | idée principale / synthèse courte |
| 8 | document_analysis | analyse documentaire (nuance argumentative) |
| 9 | short_answer | réponse argumentée courte |
| 10 | long_answer | réponse longue structurée (plusieurs centaines de mots) |
| 11 | source_comparison | comparaison des deux documents (bonus, hors liste des 10) |

Toutes validées par `app.v1.question_engine.validate_content` (registre #40) avant
stockage — aucune solution privée dans le payload public.

---

## 3. Document source partagé (§ « DOCUMENT SOURCE » du ticket)

`SourceDocument`/`SourceDocumentVersion` (#38) réutilisés tels quels — **aucun nouveau
moteur de contenu**. Le texte principal est référencé par 3 questions (deux
`document_analysis` + le `source_comparison`), le second texte par 1 (`source_comparison`
uniquement) : chaque question ne porte qu'un `source_document_version_id`/`_ids`
(référence entière, jamais le texte), conformément au contrat #40
(`description="Référence toujours une SourceDocumentVersion — jamais de texte dupliqué
dans content_json"`).

---

## 4. Architecture — ce qui a été réutilisé vs étendu

**Réutilisé tel quel** (aucune modification) : `Subject`/`Module`/`UAA`/`LessonBlock`,
`SourceDocument`/`SourceDocumentVersion` (#38), le registre #40 complet, le moteur de
session `start_session`/`save_answer`/`submit_session` (#55), l'écran de résultats
(structure TA RÉPONSE/ATTENDU-CRITÈRES/POINTS FORTS/ERREURS/ÉLÉMENTS
MANQUANTS/EXPLICATION déjà générique), `app.ai.questionnaire.correct_questionnaire`
(#23, seul point d'appel IA).

**Étendu** (jamais un nouveau moteur, des ajouts ciblés à l'existant) :

- `app/v1/ai_bridge.py` : `document_analysis`/`source_comparison` mappés sur le type #23
  `long_answer` pour la CORRECTION (rubric + expected_points) — jamais pour la
  GÉNÉRATION (`BRIDGE_TYPES` inchangé, ces deux types en sont explicitement exclus : le
  contrat #23 n'a pas de notion de document, et générer une question sans document réel
  n'aurait aucun sens). Nouveau `CORRECTABLE_TYPES` (plus large que `BRIDGE_TYPES`) pour
  l'affichage des résultats (`_describe_answer`, qui utilisait par erreur le mauvais
  ensemble avant ce correctif).
- `app/v1/session_service.py` :
  - `_pedagogical_context_for` reconnaît désormais aussi le plan Français (même chaîne de
    résolution qu'AMPCR, juste étendue).
  - `build_question_display` résout et joint les `SourceDocumentVersion` référencées par
    une question, pour le panneau de lecture (nouveau paramètre `db`, un seul appel
    site — `routes_sessions.py::view_session`).
  - `_document_contexts_for` (nouveau) : construit UN contexte pédagogique PAR DOCUMENT
    distinct référencé par la session (jamais par question), injecté dans le batch de
    correction — le texte n'apparaît donc qu'UNE SEULE FOIS dans le prompt envoyé à
    l'IA, quel que soit le nombre de questions qui le citent (§ CORRECTION du ticket).
  - `LONG_SEMANTIC_TYPES` inclut désormais `document_analysis`/`source_comparison` (même
    plafond de 3 réponses longues/sémantiques par session que le reste du ticket #55).
- `app/v1/routes_sessions.py`/`app/main.py` : résolution du plan (AMPCR ou Français) déjà
  générique, étendue par un simple second `if` — aucune route renommée ni dupliquée.
- `app/templates/v1_session_question.html` : accordéon de lecture du document source
  (Bootstrap, déjà utilisé ailleurs dans le projet), affiché uniquement quand la question
  en référence un — reste consultable pendant que l'utilisateur répond, sans revenir en
  arrière (§ UX du ticket).

**Nouveau, minimal** : `app/v1/francais_plan.py` (même schéma qu'`app.v1.ampcr_plan`,
UNE UAA pilote), `app/v1/francais_content.py` (textes), `app/v1/francais_bank.py` (import
idempotent, même principe qu'`app.v1.bank.import_mc01_legacy_to_bank`).

---

## 5. UX

- **Mobile-first** : viewport déjà géré par le template de base ; l'accordéon du document
  source utilise `max-height: 50vh; overflow-y: auto` pour rester utilisable sur petit
  écran sans repousser la question trop bas.
- **Une question à la fois**, autosave silencieux, aucune correction avant soumission —
  comportement hérité tel quel du moteur #55, vérifié spécifiquement pour Français.
- **Réponse longue** : `max_length=6000` pour la question `long_answer` (largement
  au-delà de « plusieurs centaines de mots » — testé avec un texte de plus de 2000
  caractères, jamais tronqué, ni à l'autosave ni à la soumission finale).

---

## 6. Tests

`tests/test_ticket47_francais_v1.py` (20 tests) couvre : import de la banque (2
SourceDocument, 11 questions, idempotent) ; plusieurs questions référencent le même
document sans dupliquer son texte ; page Cours publique avec mention explicite du statut
provisoire ; authentification requise pour practice/exam ; session practice à 10
questions ; aucune correction/solution visible avant soumission (y compris absence des
boutons Corriger/Vérifier) ; autosave d'une réponse longue relue intégralement ; reprise
d'une session en cours ; examen à au moins 10 questions, anti-doublon, immuable après
soumission ; soumission déclenche exactement un appel IA batch ; le contexte de document
n'apparaît qu'une fois par document (jamais par question) ; réponse longue non tronquée
de bout en bout (formulaire → autosave → soumission → relecture) ; résultats détaillés
(structure complète) ; aucune fuite de solution dans les résultats ; panneau de lecture
du document affiché pour les questions qui le référencent ; viewport mobile présent ;
non-régression AMPCR MC01.

`tests/test_admin_content_hierarchy.py::test_seed_is_idempotent` mis à jour (comptages
Subject/Module/UAA/LessonBlock +1 matière/+1 module/+1 UAA/+1 bloc) — conséquence directe
et attendue de l'ajout de contenu, même pattern que les tickets précédents.

Aucun appel OpenAI réel : `FakeAIProvider` (monkeypatch) partout où une génération/
correction IA est exercée.

---

## 7. Résultat pytest (suite complète)

```
910 passed, 2 warnings in 203.99s (0:03:23)
```

(890 avant ce ticket + 20 nouveaux — `tests/test_ticket47_francais_v1.py`). Les 2
warnings sont préexistants (httpx/anyio), sans lien avec ce ticket.

---

## 8. Résultat Ruff

```
Found 36 errors.
```

Identique à la base (`app/admin.py`/`app/main.py`/`app/practice.py` B008 Depends,
`tests/conftest.py` RUF100 — tous préexistants, aucun dans les fichiers de ce ticket).
**0 nouvelle erreur.** (Note : un `ruff check --fix` global a incidemment corrigé deux
fichiers hors périmètre de ce ticket — `tests/conftest.py`, `tests/test_rich_content.py`
— ces corrections ont été délibérément annulées avant commit pour garder le changement
strictement scopé à #47.)

---

## 9. `git diff --check`

```
$ git diff --check origin/develop...HEAD
(aucune sortie, exit code 0)
```

---

## 10. Limites assumées

- **FRENCH_CONTENT_STATUS=PROVISIONAL_TECHNICAL_SAMPLE** — le texte support et les 11
  questions sont un contenu de VALIDATION TECHNIQUE, pas un examen CESS officiel. Le
  contexte pédagogique (`app/v1/francais_plan.py`) l'indique explicitement dans ses
  contraintes. Le remplacement par un vrai corpus pédagogique (validé par l'équipe
  pédagogique/ChatGPT) reste à faire dans un ticket ultérieur, sans changement
  d'architecture attendu (même mécanisme d'import idempotent, même moteur de session).
- **Une seule UAA pilote** (« C01 »), pas les 9-10 cours mentionnés dans le ticket #4
  d'origine (fondations lire/écrire, justification, résumé, opinion écrite/orale,
  œuvre, récit, révision méthodologie) — hors périmètre explicite de ce ticket
  (« créer un premier parcours complet »), à généraliser une fois le premier pilote
  validé.
- **Génération IA non supportée pour `document_analysis`/`source_comparison`** (choix
  architectural documenté § 4) — la banque hand-authored (11 questions) suffit pour les
  deux premières sessions (practice + exam) sans recours à la génération ; un
  élargissement futur nécessiterait un prompt de génération conscient des documents,
  hors périmètre de ce ticket.
- **Pas de plafonnage par catégorie thématique** pour Français (un seul document/sujet
  pour l'instant, la question ne se pose pas encore) — pertinent seulement si plusieurs
  documents/UAA coexistent, comme pour MC38 (#58).

---

## Statut

Implémentation, tests et documentation terminés. `pytest -q` (suite complète) : 909
passed. Ruff : 36 erreurs, 0 nouvelle. `git diff --check` : propre. Aucun appel OpenAI
réel. Aucune modification de `jury_central.db`. Prêt pour commit/push. **Aucun merge,
aucun déploiement.**
