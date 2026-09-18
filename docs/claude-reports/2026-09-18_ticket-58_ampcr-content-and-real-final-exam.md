# Ticket #58 — Cours AMPCR MC04→MC37 + MC38 réellement transversal

**Date** : 2026-09-18
**Branche** : `feature/58-ampcr-content-real-final-exam`

---

## 1. Contexte et problèmes corrigés

Après mise en ligne du ticket #55/PR #57, deux problèmes pédagogiques bloquaient
l'utilité réelle du site avant l'examen :

1. **MC04→MC37** affichaient encore un stub minimal (« contenu de cours détaillé pas
   encore rédigé »).
2. **MC38** générait des questions MÉTA sur le processus de révision lui-même
   (« Quel est l'objectif principal d'une révision finale AMPCR ? »,
   « Que faut-il faire après avoir corrigé un exercice transversal ou un examen blanc ? »,
   « Fiches mémo → Révision et mémorisation ») au lieu de vraies questions d'informatique
   AMPCR — cause : la génération utilisait le propre contexte pédagogique de MC38 (objectif
   du plan : « synthèse, fiches mémo, pièges, exercices transversaux et examen type
   qualification »), qui invite naturellement l'IA à parler DU processus de révision
   plutôt qu'À PARTIR du contenu technique réel.

---

## 2. MC04→MC37 : cours de révision express

`app/v1/ampcr_courses.py` (nouveau) contient `AMPCR_COURSE_MARKDOWN`, un cours par MC04
à MC37 (34 entrées), structuré en 8 sections fixes imposées par le ticket : Ce qu'il faut
savoir / Définitions essentielles / Notions principales / Procédure-méthode / Exemple
concret / Pièges fréquents / Vocabulaire FR-EN / À retenir pour l'examen. Court, dense,
orienté examen — pas une encyclopédie.

**Périmètre** : chaque cours reste strictement borné à l'objectif déjà validé du plan
AMPCR pour ce MC (`app.v1.ampcr_plan._OBJECTIVES_BY_CODE`, transmis verbatim par ChatGPT
aux tickets #55/#56). Les notions techniques standard nécessaires pour expliquer cet
objectif sont utilisées (autorisé explicitement par le ticket, § 10) — par exemple pour
MC17, la table masque/incrément/hôtes pour /24 à /30 et la méthode mentale associée ;
pour MC31, la démarche Physique → IP → passerelle → Internet → DNS → application avec des
commandes de test réelles (`ping`, `ipconfig`/`ip a`, `nslookup`). Aucun chapitre hors
programme n'a été ajouté.

**Intégration au système de contenu existant** (`app/seed.py`) : le bloc COURS stub
(titre « Plan du mini-cours », ticket #55) est retiré par son ancien titre
(`AMPCR_STUB_OBSOLETE_TITLES`, même mécanisme déjà utilisé pour les blocs de démonstration
et pour MC01 au ticket #21) et remplacé par un nouveau bloc (« Cours de révision
express ») contenant le vrai cours — purement additif au niveau Module/UAA, **aucun
reset-db**, vérifié par un test manuel de migration (stub existant → réel cours après
un second `seed-db`) avant intégration.

MC38 a son propre contenu distinct (`MC38_COURSE_MARKDOWN`) : il explique le principe de
la révision finale transversale (S'entraîner/S'évaluer tirent dans MC01→MC37) — contenu
de COURS légitime et informatif, jamais confondu avec les questions de quiz (voir § 3).

---

## 3. MC38 : practice/exam réellement transversaux

Nouveau module `app/v1/mc38_transversal.py` :

- `mc01_to_mc37_codes()` : le périmètre réel de MC38 (37 codes, jamais MC38 lui-même).
- `pick_transversal_contexts()` : échantillon de contextes MC01→MC37 diversifié par
  catégorie (round-robin), transmis à `generate_questionnaire` (qui accepte déjà
  plusieurs contextes simultanés, ticket #23, `QuestionnaireRequest.contexts` est un
  tuple) — **jamais le contexte MC38 lui-même**.
- `is_meta_revision_question()` : garde de contenu ciblant le SENS méta (réviser,
  mémoriser, fiche mémo, après correction, organisation de l'étude, fonctionnement du
  site...), pas une liste noire naïve de mots isolés — ne bloque jamais le mot « examen »
  ou « piège » seul, qui apparaissent légitimement dans de vraies questions techniques
  (§ 8 du ticket, vérifié par des tests dédiés avec des contre-exemples).

`app/v1/bank.py::select_transversal_bank_questions` : puise dans les mini-cours réels
MC01→MC37 ET dans le bucket propre de MC38 (où sont stockées les questions déjà générées
par une session MC38 précédente — la banque grandit organiquement, comme pour tout autre
mini-cours), en excluant par sécurité toute question qui ressemblerait à du contenu méta
(défense en profondeur, y compris contre d'éventuelles questions déjà en banque avant ce
ticket).

`app/v1/session_service.py::_start_mc38_transversal_session` (dispatché automatiquement
depuis `start_session` quand `uaa_code == "MC38"`, sans changement de route) :
sélectionne dans ce pool transversal, complète par génération (UN appel, contextes
diversifiés MC01→MC37) si nécessaire, filtre les questions méta AVANT persistance, et se
rabat sur la répétition plutôt que d'échouer — même philosophie de repli que le reste du
ticket #55.

**Diversité de catégories** (§ 6 du ticket) : `_category_balanced_oversample` plafonne la
représentation d'une seule catégorie AMPCR à environ la moitié de la taille de session
demandée, tant que d'autres catégories ont du contenu disponible — sans garantir de
proportions exactes si la banque ne le permet pas encore (explicitement toléré par le
ticket). **Point technique important** : `compose_selection` (ticket #55) regroupe son
entrée par TYPE de question sans tenir compte de l'ordre — un simple réordonnancement du
pool par catégorie n'aurait donc eu AUCUN effet sur le résultat final ; la fonction
retire réellement l'excédent d'une catégorie dominante plutôt que de le réordonner
(vérifié par un test dédié : bank artificiellement dominée à 20 questions MC17 contre 3
MC31 → résultat final avec les deux catégories représentées, jamais uniquement MC17).

**Examen MC38** : 20 questions (comme l'examen blanc global), au lieu des 10 par défaut
des autres examens per-MC — `app/v1/routes_sessions.py::_start_session_for_uaa` détecte
`uaa_code == "MC38" and mode == EXAM`.

**Reprise / anti-doublon (bug évité avant qu'il n'arrive)** : en implémentant MC38, il est
apparu qu'une session MC38 (dont les questions appartiennent à MC01-37, jamais à MC38
lui-même) ne pouvait pas être repérée par `uaa_id` — exactement la même classe de bug que
celui corrigé au ticket précédent (#57, examen global détourné vers un examen per-MC) se
serait reproduite entre MC38 et le parcours global `/modules/ampcr/...` (les deux
partagent la caractéristique « plusieurs mini-cours »). Corrigé en amont : les sessions
MC38 portent un marqueur explicite (`QuestionnaireSession.parameters_json =
{"scope": "mc38"}`, colonne JSON déjà présente dans le modèle, jamais utilisée avant ce
ticket — **aucune migration de schéma nécessaire**), et la détection du parcours global
exclut désormais explicitement les sessions ainsi marquées. Testé : démarrer un examen
MC38 puis l'examen blanc global produit bien deux sessions distinctes ; redémarrer
l'examen MC38 reprend la même session (jamais de doublon).

---

## 4. Fichiers

**Nouveaux** :
- `app/v1/ampcr_courses.py` (cours MC04-37 + MC38)
- `app/v1/mc38_transversal.py` (contextes transversaux, garde anti-méta)
- `tests/test_ticket58_ampcr_content_and_mc38.py` (59 tests)
- `docs/claude-reports/2026-09-18_ticket-58_ampcr-content-and-real-final-exam.md` (ce
  rapport)

**Modifiés** :
- `app/seed.py` : bloc COURS réel pour MC04-37/MC38 (retrait de l'ancien stub par titre)
- `app/v1/bank.py` : `select_transversal_bank_questions`
- `app/v1/session_service.py` : dispatch MC38, `_finalize_session` factorisé,
  `_category_balanced_oversample`, `get_in_progress_session(scope=...)`
- `app/v1/routes_sessions.py` : `_resumable_session_for_uaa` (MC38 vs per-MC), 20
  questions pour l'examen MC38
- `docs/ampcr_v1_functional.md` : § 2bis (cours), § 4bis (mécanisme MC38), § 6 mis à jour

---

## 5. Tests

`tests/test_ticket58_ampcr_content_and_mc38.py` (59 tests) couvre : les 34 entrées de
`AMPCR_COURSE_MARKDOWN` (MC04-37 sans trou) ; MC04 n'est plus un stub et respecte la
structure à 8 sections ; MC17 contient CIDR/masques/hôtes/incrément ; MC24 contient
VLAN/trunk/802.1Q ; MC31 contient IP/passerelle/DNS ; MC37 est bien intégrateur
(montage/RJ45/partage/Wi-Fi/sécurité) ; chacun des 34 MC sert réellement son cours réel
(paramétré) ; le cours MC38 explique la révision transversale sans être un sujet de
question ; la garde anti-méta rejette exactement les 3 exemples interdits du ticket et
n'importe jamais le mot « examen »/« piège » seul (4 contre-exemples) ; une génération
simulée mixant questions méta et réelles ne laisse passer que les réelles ; MC38
practice/exam tirent bien dans MC01-37 (jamais dans un MC hors programme) ; l'examen MC38
a 20 questions ; la génération MC38 utilise des contextes transversaux (≥2, jamais
`ampcr-mc38`) ; plusieurs catégories sont représentées quand la banque le permet (test à
bank artificiellement déséquilibrée) ; `select_transversal_bank_questions` ne renvoie
jamais de question méta ; aucune fuite de solution dans une session MC38 ; non-régression
MC01 practice/exam et parcours global AMPCR.

Aucun appel OpenAI réel : `FakeAIProvider` ou un `Questionnaire` construit à la main
(monkeypatch de `generate_questionnaire`) partout où une génération est exercée.

---

## 6. Résultat pytest (suite complète)

```
889 passed, 2 warnings in 197.09s (0:03:17)
```

(830 avant ce ticket + 59 nouveaux — `tests/test_ticket58_ampcr_content_and_mc38.py`). Les
2 warnings sont préexistants (httpx/anyio), sans lien avec ce ticket.

---

## 7. Résultat Ruff

```
Found 36 errors.
```

Identique à la base (`app/admin.py`/`app/main.py` B008 Depends, `tests/conftest.py`
RUF100, `tests/test_rich_content.py` I001 — tous préexistants, aucun dans les fichiers de
ce ticket). **0 nouvelle erreur.**

---

## 8. `git diff --check`

```
$ git diff --check origin/develop...HEAD
(aucune sortie, exit code 0)
```

---

## 9. Non-régression

- MC01/MC02/MC03 : cours et contexte pédagogique inchangés (aucune modification).
- MC01 practice/exam, parcours global AMPCR practice/exam : re-testés, fonctionnels.
- Aucune route existante renommée ni supprimée — le dispatch MC38 est interne à
  `start_session()`, invisible depuis les routes HTTP (`/uaa/ampcr-mc38/practice`,
  `/uaa/ampcr-mc38/exam` inchangées).
- Aucune migration de schéma (réutilisation de `parameters_json`, colonne déjà présente).

---

## 10. Limites assumées

- Les cours MC04-37 restent des révisions EXPRESS (8 sections courtes et denses), pas un
  cahier des charges complet comme MC01-03 — un enrichissement éditorial ultérieur reste
  possible mais non urgent (le cours actuel est déjà réellement utilisable pour réviser).
- La diversité de catégories pour MC38 reste best-effort (plafond ~50%, pas de
  proportions exactes garanties) — explicitement toléré par le ticket § 6.
- Le parcours GLOBAL `/modules/ampcr/...` (distinct de MC38) n'a PAS reçu le même
  plafonnage par catégorie — hors périmètre de ce ticket, déjà noté comme limite connue
  depuis le ticket #55 (`docs/ampcr_v1_functional.md` § 6).
- Les questions déjà en banque MC38 depuis les validations staging précédentes (avant ce
  ticket, potentiellement méta) ne sont pas supprimées de la base (aucun reset-db) — la
  garde anti-méta les exclut désormais systématiquement de toute future sélection, sans
  qu'une suppression de données soit nécessaire.

---

## Statut

Implémentation, tests et documentation terminés. `pytest -q` (suite complète) : 889
passed. Ruff : 36 erreurs, 0 nouvelle. `git diff --check` : propre. Aucun appel OpenAI
réel. Aucune modification de `jury_central.db` (uniquement des bases SQLite temporaires
isolées pour la vérification manuelle). Prêt pour commit/push. **Aucun merge, aucun
déploiement.** Le Français, #45, #46 et #48 n'ont pas été démarrés.
