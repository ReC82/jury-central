# Jury Central — Formation sociale et économique V1 : état fonctionnel de FSE01 (ticket #96)

Première matière « Formation sociale et économique » (CESS Professionnel) du dépôt —
aucun contenu FSE n'existait avant ce ticket (voir `app.v1.fse_plan`, docstring, et
`docs/content_plan_fse.md`). Réutilise intégralement le moteur V1 générique déjà validé
par Informatique AMPCR et Français (`docs/ampcr_v1_functional.md`,
`docs/francais_v1_functional.md`) — aucune nouvelle architecture, aucun second moteur de
sessions/correction/génération.

---

# 1. Ce qui fonctionne pour l'utilisateur

`/subjects/formation-sociale-et-economique` → `/modules/fse` → `/uaa/fse-fse01` (Cours),
`/uaa/fse-fse01/practice` (S'entraîner), `/uaa/fse-fse01/exam` (S'évaluer) offrent
exactement le même parcours que les mini-cours AMPCR/Français, via le moteur générique
partagé :

1. navigation à 3 onglets Cours/S'entraîner/S'évaluer (`_uaa_space_nav.html`, ticket #22) ;
2. **théorie complète** : schéma de communication (émetteur, récepteur, message, code,
   canal, contexte, obstacle, rétroaction) appliqué à trois situations originales — un
   mail de candidature interrompu par une coupure de connexion, une affiche de sécurité
   routière, une publication sur un réseau social — avec définitions, méthode, exemples
   commentés, exercices guidés corrigés (masqués par défaut) et fiche mémo ;
3. **S'entraîner** : choix de difficulté (facile/moyen/difficile), mêmes libellés que
   les autres matières (`_DIFFICULTY_LABELS`, `app/v1/routes_sessions.py`) ;
4. **S'évaluer** : choix de difficulté ET choix de sévérité de cotation (1 à 5), deux
   paramètres distincts — la difficulté sélectionne/dimensionne la session
   (`SessionDifficultyRequest`, persistée dans `QuestionnaireSession.difficulty_requested`
   dès la création, inchangée par la suite), la sévérité ne s'applique qu'à la notation
   sémantique au moment de la soumission (`parameters_json["severity"]`) — jamais
   confondues, vérifié par
   `tests/test_ticket96_fse01.py::test_fse01_difficulty_and_severity_are_distinct_and_applied_server_side` ;
5. autosave à chaque réponse, reprise d'une session en cours (la difficulté choisie au
   départ reste strictement inchangée lors d'une reprise, vérifié par
   `test_fse01_settings_persist_across_resume`) ;
6. aucune correction visible avant la fin ; un seul appel IA batch à la soumission
   (`FakeAIProvider` dans tous les tests, aucun appel OpenAI réel) ;
7. résultats détaillés par question, score global, lien de retour vers le cours, export/
   historique (`/mes-sessions`) — tous réutilisés tels quels, sans modification.

---

# 2. Corpus — 3 documents, 14 questions

Trois `SourceDocument` originaux, rédigés pour ce cours (jamais une modification d'une
source officielle — `docs/content_workflow.md`), chacun correspondant à une application
explicitement demandée par le cahier des charges du ticket #97 :

| Document | Application |
|---|---|
| Candidature par mail — coupure de connexion | obstacle technique, rétroaction rapide |
| Affiche de sécurité routière | canal sans rétroaction directe |
| Publication sur réseau social | obstacle informationnel, rétroaction publique |

14 questions (`app.v1.fse_bank.import_fse01_to_bank`), réparties par type :

| Type | Nombre |
|---|---|
| `short_answer` | 3 |
| `multiple_choice` | 3 |
| `classification` | 2 |
| `vocabulary` | 2 |
| `ordering` | 1 |
| `document_analysis` | 2 |
| `long_answer` | 1 |

Chaque question qui porte `source_document_version_id` référence un document réellement
persisté (même garantie que Français #94 § 8 — aucun « D'après le texte » orphelin,
vérifié par `test_no_orphan_document_dependent_questions_in_fse01`). `multiple_choice`/
`ordering` n'ont pas ce champ dans le registre #40 (`app.v1.question_types`) : ces
questions restent volontairement conceptuelles (définitions, méthode), jamais un résumé
dupliqué d'un document.

Isolation : les 14 questions appartiennent exclusivement à l'`uaa_id` de FSE01, aucun
mélange avec Informatique/Français/Mathématiques (`test_fse01_questions_isolated_to_its_own_uaa`).

---

# 3. Points d'intégration au moteur générique partagé

Même principe que pour l'ajout de Français (`app.v1.francais_plan`) après AMPCR — un
registre dédié `app.v1.fse_plan` (code → titre → contexte pédagogique borné), branché aux
mêmes points d'extension déjà prévus par le moteur, sans modifier son comportement pour
les matières existantes (non-régression vérifiée par
`test_ampcr_and_francais_unaffected_by_fse`) :

- `app/main.py` (`uaa_practice`/`uaa_exam`) : `get_fse_plan_by_slug` ajouté à la condition
  qui bascule une UAA vers le parcours de session V1 générique plutôt que le rendu legacy.
- `app/v1/routes_sessions.py` (`_ensure_bank_seeded`, `_enqueue_build_for_uaa`) :
  `_FSE_BANK_IMPORTERS` (même forme que `_FRANCAIS_BANK_IMPORTERS`) pour l'amorçage
  paresseux de la banque, et résolution de `uaa_code` pour FSE01.
- `app/v1/session_service.py` (`_pedagogical_context_for`) : `FSE_PLAN_BY_CODE`/
  `get_fse_context` ajoutés à la chaîne de résolution du contexte pédagogique transmis à
  la correction sémantique — garantit que la grille de correction/sévérité pour FSE01 ne
  reçoit jamais le contexte AMPCR/Français par défaut.
- `app/seed.py` : matière/module/UAA créés de façon purement additive et idempotente
  (`_ensure_subject`/`_ensure_modules`/`_seed_uaa`, mécanisme déjà existant, aucune
  modification).

---

# 4. Limites assumées (hors périmètre de ce ticket)

- FSE02 à FSE17 ne sont ni seedés ni accessibles — voir `docs/content_plan_fse.md` pour le
  plan complet et la prochaine étape (ticket #97, FSE02-04).
- Comme pour AMPCR/Français, `QuestionnaireSession.question_count` nominal est 10 (practice
  et exam) : avec 14 questions en banque, une session peut recevoir moins de 10 questions
  distinctes selon l'historique déjà vu par l'élève (repli existant du moteur, pas une
  particularité FSE — voir `app.v1.session_service.start_session`).

---

# 5. Fichiers clés

- `app/v1/fse_plan.py` — `FSE_SUBJECT_NAME`, `FSE_MODULE_CODE`, `FSE_PLAN`, contexte IA.
- `app/v1/fse01_content.py` — les trois documents source.
- `app/v1/fse01_course.py` — `fse01_course_markdown()`.
- `app/v1/fse_bank.py` — `import_fse01_to_bank`, les 14 questions.
- `app/seed.py` — section « Formation sociale et économique (FSE) ».
- `tests/test_ticket96_fse01.py` — 18 tests, aucun appel OpenAI réel.
