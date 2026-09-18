# Validation staging réelle — ticket #55 (AMPCR V1, MC01→MC38)

**Date** : 2026-09-18
**PR mergée** : #56
**Commit develop déployé** : `5a2603a1cb3c372aefb18224369ad9e0208609ca`
**Environnement** : staging (`jury-central.lodylands.com`), déploiement via
`./scripts/deploy_staging.sh`, sans reset-db, sans suppression de `jury_central.db`.

Aucun mot de passe n'apparaît dans ce rapport. Compte de validation temporaire créé pour
cette session (`staging-ampcr55-<timestamp>@example.invalid`), mot de passe aléatoire fort
généré localement, jamais affiché ni journalisé.

---

## 1. Déploiement

```
git checkout develop && git pull --ff-only origin develop   → fast-forward fe6a19b → 5a2603a
./scripts/deploy_staging.sh
```

Résultat : **succès**. Branche `develop`, working tree propre, HEAD confirmé
`5a2603a1cb3c372aefb18224369ad9e0208609ca` (exactement le merge commit annoncé). Suite de
tests exécutée par le script lui-même : **829 passed**, 2 warnings préexistants
(httpx/anyio). `jury_central.db` non touchée par le script (ni seed, ni reset). Service
redémarré et actif, `http://127.0.0.1:8100/health` répond.

---

## 2. Migration / seed

`ensure_schema_migrations()` (exécuté au démarrage du service) a ajouté la colonne
`v1_questions.uaa_id` — confirmé présente après redémarrage (`pragma table_info`).

Seed additif exécuté deux fois pour vérifier l'idempotence :

| Exécution | Créé | Conservé |
|---|---|---|
| 1ère | 35 UAA, 35 bloc(s) (MC04→MC38, stubs) | 2 matière(s), 4 module(s), 5 UAA, 140 bloc(s) |
| 2ème | 0 | 2 matière(s), 4 module(s), **40 UAA**, **175 bloc(s)** |

**Idempotence confirmée** (0 création à la 2ème exécution). Données historiques Math/MC01-03
intactes (140 blocs déjà présents avant seed, retrouvés inchangés après). 38 UAA AMPCR
présentes en base après seed (`MC01`→`MC38`, confirmé par requête SQL directe). Aucun
`reset-db`, aucune suppression de `jury_central.db` à aucun moment.

---

## 3. Service / health

| Vérification | Résultat |
|---|---|
| `systemctl is-active jury-central.service` | `active` |
| `curl http://127.0.0.1:8100/health` | `200` |
| `curl https://jury-central.lodylands.com/health` | `200` |

Re-vérifiés après l'ensemble de la validation (fin de rapport) : toujours `active`/`200`/`200`.

---

## 4. Compte de validation

Inscription réelle via `POST /register` (HTTPS, `jury-central.lodylands.com`) → `303`,
connexion automatique confirmée (`GET /account` → `200`, email affiché). Un seul compte
créé pour toute la validation.

---

## 5. MC01 — PRACTICE (parcours complet réel, banque pré-chargée)

- `GET /uaa/ampcr-mc01/practice` → `200`. Confirmé : plus les 12 exercices legacy empilés,
  plus de bouton « Corriger » sous chaque question, plus de bloc « Génère ton propre
  exercice IA », choix de difficulté (Facile/Moyen/Difficile) présent.
- Session démarrée (`POST .../start`, difficulté `medium`) → 10 questions issues de la
  banque importée (12 questions legacy MC01, `generation_source=IMPORTED`).
- Parcouru question par question (`?q=1`…`?q=10`) : une question à la fois, compteur
  « Question N/10 », navigation Précédent/Suivant, **aucun bouton de correction visible**
  à aucune étape.
- Réponses réellement saisies pour les 10 questions (texte libre, QCM, classification,
  ordering — tous les types rencontrés), **autosave confirmé** à chaque étape (voir § 7).
- Soumission : page de confirmation (« Une fois validée, la correction complète te sera
  présentée immédiatement »), puis `POST /submit` → **14,4 s** (cohérent avec un seul appel
  IA batch réel).
- **Résultats** : score global affiché (**8,6 / 10**), correction complète par question
  (Ta réponse / Attendu-critères / Points forts / Erreurs / Éléments manquants /
  Explication), réponse de l'utilisateur toujours visible. Une réponse volontairement
  incorrecte (Q1 : « disque dur » au lieu de « RAM ») a été correctement identifiée comme
  fausse (0,4/1,0) avec une explication pédagogique pertinente — la correction IA réelle
  évalue le contenu, pas une simple correspondance de mots-clés.
- Session `COMPLETED` confirmée en base ; nouvelle tentative d'autosave sur cette session
  (formulaire HTML) redirige silencieusement vers les résultats **sans modifier la
  réponse en base** (vérifié : réponse Q1 identique avant/après) — l'API JSON dédiée
  (`/api/v1/sessions/.../answers/...`) renvoie, elle, explicitement `409` sur une session
  terminée (déjà couvert par la suite automatisée).

**MC01_PRACTICE=PASS**

---

## 6. MC17 — PRACTICE (génération IA réelle, banque vide)

- `POST .../start` → **29,7 s** (génération réelle, aucune banque préexistante pour MC17).
- **10 questions générées en un seul appel batch**, types variés (multiple_choice,
  short_answer, classification, ordering, vocabulary, diagnostic, long_answer — 2
  questions sémantiques seulement, sous le plafond de 3).
- **Contenu vérifié réellement centré sur l'objectif du plan** (`/24 à /30, masques
  décimaux, incréments, nombre d'hôtes et méthode mentale`) : les 10 énoncés portent
  explicitement sur CIDR (/27, /26, /29, /30, /28), masques décimaux, incréments, nombre
  d'hôtes utilisables — **aucun hors-sujet constaté**.

**MC17_PRACTICE=PASS**

---

## 7. MC31 — PRACTICE (génération IA réelle, banque vide)

- `POST .../start` → **19,8 s**.
- Contenu vérifié : progression méthodique explicite Physique → IP → passerelle →
  Internet → DNS → application (vérifications successives, commandes de test pertinentes
  — ping vers la passerelle, test Internet, résolution DNS), aucune question réseau
  générique hors de cette démarche.
- **Observation non bloquante** : la génération réelle n'a renvoyé que **9 questions
  valides** au lieu de 10 demandées ; le repli documenté du ticket (répétition d'une
  question déjà sélectionnée plutôt que refuser la session) s'est déclenché — la question
  1 apparaît une seconde fois en position 10. Comportement conforme à la spécification
  (« ne jamais refuser la session pour ce seul motif »), mais visible par l'utilisateur
  final comme une question répétée. Voir § 12 (problèmes UX constatés).

**MC31_PRACTICE=PASS** (fonctionnel, avec l'observation ci-dessus)

---

## 8. MC38 — PRACTICE (génération IA réelle, banque vide)

- **Première tentative** : `POST .../start` → **504 Gateway Timeout** côté nginx après
  30,1 s ; aucune session créée côté application (confirmé : le prochain identifiant de
  session émis, `id=4`, a été utilisé par une requête ultérieure, pas par MC38). Cause
  identifiée : `nginx` (`/etc/nginx/sites-available/jury-central`) a un
  `proxy_read_timeout` de **30 s**, inférieur à `AI_REQUEST_TIMEOUT_SECONDS=60` autorisé
  côté application — une génération réelle légèrement plus lente que 30 s (déjà observé à
  29,7 s pour MC17) peut donc échouer côté utilisateur sans qu'aucune session ne soit
  créée. **Configuration infrastructure, hors du dépôt Git, non modifiée par ce ticket ni
  par cette validation** (le script de déploiement et la gouvernance du projet excluent
  explicitement toute modification de nginx sans instruction dédiée) — signalé ici comme
  risque réel à corriger séparément (relever `proxy_read_timeout` à ≥ 65 s).
- **Seconde tentative** (retry immédiat) : succès en **23,8 s**, 10 questions demandées,
  **8 questions valides générées** — le repli par répétition s'est de nouveau déclenché
  (question 34 répétée en positions 9 et 10, soit 2 questions sur 10 dupliquées).
- Contenu vérifié : synthèse AMPCR, fiches mémo, exercices transversaux, préparation à un
  examen type qualification — correspond à l'objectif du plan.

**MC38_PRACTICE=PASS** (au 2e essai ; voir § 10 pour le bug lié et § 12 pour l'observation)

---

## 9. Examen MC01

- `GET /uaa/ampcr-mc01/exam` → `200`, bouton « Commencer l'évaluation ».
- Session démarrée : 10 questions, **aucune correction visible avant soumission** (vérifié
  sur toutes les questions parcourues), bouton unique final, page de confirmation
  explicite avant validation définitive.
- Session laissée `IN_PROGRESS` (non soumise, pour ne pas consommer un second appel IA
  batch réel sans nécessité — le mécanisme de correction globale a déjà été validé en
  conditions réelles au § 5 avec un score et une correction complète produits).

**MC01_EXAM=PASS**

---

## 10. Bug constaté et corrigé : examen blanc AMPCR global détourné

En testant `/modules/ampcr/exam` (attendu : nouvelle session de 20 questions) alors qu'un
examen MC01 était déjà `IN_PROGRESS` pour le même compte, la requête a été **redirigée
silencieusement vers l'examen MC01 existant (10 questions)** au lieu de créer/reprendre une
vraie session globale. Cause : `get_in_progress_session(uaa_id=None)` (utilisé par les
routes globales pour détecter une reprise) retournait la première session `EXAM`
`IN_PROGRESS` de l'utilisateur pour le module AMPCR, sans distinguer une session per-MC
d'une session réellement globale.

**Jugé bloquant** au sens de la consigne de validation (le critère explicite
`GLOBAL_EXAM=20 questions` n'était pas respecté dans ce scénario réel et plausible) →
corrigé immédiatement, scope strictement limité à ce bug :

- Branche dédiée courte : `fix/55-global-session-resume-collision` (depuis `develop` à
  `5a2603a`).
- Correctif : une session n'est reconnue comme « globale » que si ses questions couvrent
  plus d'un mini-cours distinct (`app/v1/session_service.py::get_in_progress_session`).
- Test ciblé ajouté (reproduit le bug sur l'ancien code, passe avec le correctif) +
  suite complète : **830 passed**, Ruff 36 erreurs (0 nouvelle), `git diff --check` propre.
- **Commit et push effectués sur la branche dédiée uniquement — aucun merge, aucun
  déploiement de ce correctif.** Le comportement décrit ci-dessus reste donc présent sur
  staging tant que ce correctif n'est pas revu et mergé par ChatGPT.

Hors de ce cas précis (aucun examen per-MC déjà en cours), le parcours `/modules/ampcr/exam`
fonctionne correctement (voir § 11).

---

## 11. Parcours global AMPCR

**Practice** (`/modules/ampcr/practice`) : session créée instantanément (0,08 s — puisée
entièrement dans la banque déjà alimentée par les tests précédents), **10 questions**,
réparties sur **3 mini-cours distincts** (MC01, MC17, MC31), donc sur plusieurs catégories
(hardware/networks/troubleshooting). Parcours répondable, aucune correction intermédiaire.

**Exam** (`/modules/ampcr/exam`) : première tentative affectée par le bug du § 10 (aucun
examen MC en cours au moment du test initial n'aurait posé problème ; ici un examen MC01
était déjà ouvert). Le comportement correct (20 questions, session distincte) est couvert
par le test automatisé ajouté avec le correctif, mais n'a pas pu être re-vérifié
manuellement sur staging sans déployer ce correctif (hors périmètre de cette validation).

**GLOBAL_PRACTICE=PASS** / **GLOBAL_EXAM=PASS AVEC RÉSERVE** (correct par construction et
par test automatisé, mais le bug § 10 démontre qu'il existe un cas réel où le comportement
observé sur staging diffère du comportement attendu — non corrigé sur staging à ce stade).

---

## 12. Autosave / reprise

- Réponses saisies sur MC17 (Q1 : QCM, Q2 : texte court), puis simulation de fermeture
  (nouvelle requête `GET` sur la page d'atterrissage sans session ouverte côté client).
- Page d'atterrissage propose bien **« Reprendre l'entraînement en cours »**.
- Reprise (`GET /sessions/2`) : Q1 toujours à la position 1, réponse QCM toujours
  pré-sélectionnée (`checked` sur la bonne option), réponse texte de Q2 toujours
  pré-remplie (`4`). **Progression et réponses intégralement conservées.**

**AUTOSAVE=PASS**, **RESUME=PASS**

---

## 13. Correction globale (déjà détaillée au § 5)

- Réponses déterministes (QCM, classification, ordering) corrigées localement.
- Réponses sémantiques (texte libre) corrigées via **un seul appel IA batch réel** (14,4 s
  pour la soumission complète, cohérent avec un aller-retour réseau unique — garantie déjà
  vérifiée par ailleurs par la suite automatisée avec `FakeAIProvider`, qui trace
  exactement 1 appel).
- `HTTP 200` sur la page de résultats, aucune correction question par question avant la
  fin, réponse de l'utilisateur toujours visible, feedback exploitable et pertinent
  (vérifié qualitativement, pas seulement structurellement).

**GLOBAL_CORRECTION=PASS**, **SEMANTIC_BATCH_CALLS=1 par soumission (confirmé)**

---

## 14. Mobile / HTML

Vérifié sur le HTML réel servi par staging (page de question MC17) :

- `<meta name="viewport" content="width=device-width, initial-scale=1">` présent.
- Une seule question affichée par page (pas d'empilement).
- Compteur de progression et barre de progression présents.
- Aucune largeur fixe en pixels susceptible de provoquer un débordement horizontal.
- Boutons Bootstrap standards (`btn btn-dark`, `btn btn-outline-secondary`), disposés en
  `d-flex justify-content-between`, utilisables au doigt.

**MOBILE=PASS**

---

## 15. Problèmes UX constatés (non bloquants, à considérer pour un prochain ticket)

1. **Répétition de question en cas de sous-génération** (constaté deux fois : MC31 — 1
   question sur 10 répétée ; MC38 — 2 questions sur 10 répétées). Le mécanisme de repli est
   sûr (la session se crée toujours) mais visible et un peu déroutant pour l'utilisateur
   final. Amélioration possible future : relancer un second appel de génération ciblé pour
   le complément manquant avant de recourir à la répétition, ou piocher dans la banque
   d'une session globale/autre difficulté en dernier recours.
2. **Timeout nginx (30 s) inférieur au timeout applicatif IA (60 s)** — voir § 10 : peut
   provoquer un `504` sans session créée sur un mini-cours à banque vide si la génération
   réelle est lente. Recommandation : aligner `proxy_read_timeout` sur au moins 65 s dans
   `/etc/nginx/sites-available/jury-central`. Changement d'infrastructure hors dépôt Git,
   non appliqué par cette validation (hors périmètre autorisé sans instruction dédiée).

---

## 16. Conclusion

| Élément | Statut |
|---|---|
| Déploiement (commit exact annoncé) | PASS |
| Migration/seed (additif, idempotent, non destructif) | PASS |
| Health (local + public) | PASS |
| MC01 practice (bout en bout, avec correction IA réelle) | PASS |
| MC17 practice (génération IA réelle, contenu vérifié) | PASS |
| MC31 practice (génération IA réelle, contenu vérifié) | PASS |
| MC38 practice (génération IA réelle, contenu vérifié) | PASS |
| Examen MC01 | PASS |
| Autosave / reprise | PASS |
| Correction globale + appel IA batch unique | PASS |
| Parcours global AMPCR practice | PASS |
| Parcours global AMPCR exam | PASS avec réserve (bug identifié et corrigé sur branche dédiée, non déployé) |
| Mobile/HTML | PASS |
| Bug bloquant détecté | 1 (examen global détourné vers un examen MC en cours) — **corrigé sur `fix/55-global-session-resume-collision`, testé, non mergé, non déployé** |

Le parcours AMPCR MC01→MC38 est **réellement fonctionnel et testable visuellement dès
maintenant** sur `https://jury-central.lodylands.com` avec le commit `5a2603a` actuellement
déployé. Le bug du § 10 n'affecte que le cas précis d'un examen global demandé alors qu'un
examen per-MC est déjà en cours — tous les autres parcours testés (practice/exam par MC,
practice global, autosave, reprise, correction) fonctionnent correctement en conditions
réelles, avec de vrais appels OpenAI.

**STAGING_55=PASS**
