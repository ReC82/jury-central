# Changelog

Historique des tranches livrées. Format : date, résumé, détail technique bref.

## 2026-09-16 — Socle générique des exercices éditoriaux interactifs (ticket #17)

Suite à l'audit UX/technique du même jour
(`docs/claude-reports/2026-09-16_audit_interactivite.md`), premier chantier
d'interactivité : les exercices éditoriaux (texte Markdown avec correction masquée/
affichée côté client, sans saisie ni vérification serveur) gagnent un socle générique
réutilisable dans toutes les matières, sur le patron déjà éprouvé par `value_table`/
`quiz`/`ai_exercise` (config JSON → route de vérification → widget AJAX).

**Nouveau type de bloc `editorial_exercise`** (`app/models.py::BlockType`, extension
minimale, aucun changement de schéma SQLite). Nouveau module `app/editorial_exercise.py` :
`EditorialExerciseBlockConfig` (`mode: practice|exam`, liste d'items),
`EditorialExerciseItem` (validation stricte à la construction, tolérance au chargement
depuis la base), première tranche de types — `single_choice`, `true_false`,
`short_answer` — à correction locale déterministe uniquement. Nouvelle fonction
`app/answer_checking.py::text_answer_matches` (comparaison textuelle normalisée casse/
espaces/accents, aucun `eval()`).

**Nouvelle route** `POST /practice/api/editorial/{block_id}/verify` — le serveur recharge
toujours la configuration complète depuis `LessonBlock.content` ; `to_public_dict()`
exclut structurellement la solution. Nouveau widget `app/static/js/editorial_exercise.js`
(AJAX, sans rechargement, contrôles `d-print-none`, tailles/contrôles adaptés au mobile).

**Démonstration** `/admin/editorial-exercise-demo` (+ route de vérification associée),
même principe que `/admin/value-table-demo` : un exercice fixe par type, indépendamment
de tout contenu réel.

**MC01 : aucune migration dans ce ticket.** Les 12 exercices existants ont été passés en
revue un par un : 8 nécessitent `long_answer` (réponse rédigée, correction IA — ticket
séparé), 3 nécessitent `classification`, 1 nécessite `ordering` — aucun ne peut être
honnêtement exprimé avec la première tranche de types sans dénaturer son contenu
pédagogique. Conformément au ticket #17 (« ne force pas artificiellement »), MC01 reste
donc intact dans ce ticket ; le détail exercice par exercice est dans
`docs/claude-reports/2026-09-16_ticket-17_editorial-exercises.md`.

**Tests** : +38 tests (`tests/test_editorial_exercise.py` : validation, sérialisation,
absence de fuite, correction ; `tests/test_practice_editorial_routes.py` : route HTTP de
bout en bout, IDs invalides, bloc non publié/mauvais type, absence de fuite dans le HTML
public, démo admin ; `tests/test_ticket17_no_regression.py` : confirme `app/seed.py`
inchangé, MC01/MC02/MC03/Mathématiques strictement intacts). 236 tests au total, tous
verts. `ruff check .` : 36 erreurs, identiques à `develop` (comparé via worktree isolé) —
aucune nouvelle erreur.

**Vérifié manuellement** sur une base SQLite temporaire isolée (jamais `jury_central.db`,
intégrité re-vérifiée par MD5) : MC01/MC02/MC03/Mathématiques inchangés, démo admin
accessible après connexion, réponse correcte/incorrecte/normalisée toutes vérifiées,
aucune fuite de solution dans le HTML brut de la page de démo.

**Documentation** : `docs/editorial_exercise_engine.md` (nouveau),
`docs/EXERCISE_TYPES.md`, `docs/admin.md`, `docs/current_state.md`, `docs/INDEX.md`,
`docs/README.md`,
`docs/claude-reports/2026-09-16_ticket-17_editorial-exercises.md` (rapport de ticket).

## 2026-09-16 — Informatique AMPCR : mini-cours 03 « CPU et mémoire RAM » (ticket #14)

Troisième cours de la série Informatique AMPCR, contenu et périmètre pédagogique fournis
intégralement par ChatGPT dans le ticket #14. Réutilise **strictement** l'architecture des
tickets #10/#12 — aucun nouveau mécanisme, aucun second moteur IA.

**Matière/UAA** : nouvelle UAA `MC03` (« CPU et mémoire RAM ») sous le module `AMPCR`
existant, navigable depuis `/uaa/ampcr-mc03`, juste après MC02.

**Contenu** (`app/seed.py::MC03_BLOCKS`, 25 blocs) : plan, 17 sections de cours — CPU (rôle
et cycle d'exécution, cœurs/threads/SMT, fréquence base/boost, IPC, cache L1/L2/L3,
32/64 bits, socket/génération/compatibilité, TDP/refroidissement/throttling, graphique
intégré) puis RAM (rôle/capacité/latence, DDR3/DDR4/DDR5, DIMM/SO-DIMM/dual-channel,
capacité maximale, XMP/EXPO/ECC, RAM vs VRAM vs stockage) puis performances/diagnostic
(goulot d'étranglement, diagnostic RAM et CPU/thermique, unités et pièges d'examen),
vocabulaire FR/EN — 12 exercices progressifs (3 blocs) à correction masquée à la demande,
un bloc `ai_exercise` réutilisant le moteur du ticket #10, une fiche mémo, et l'examen
final (10 questions/20 points, aucune réponse visible, corrigé dans un bloc séparé
`is_published: False` — même mécanisme exactement qu'aux mini-cours 01/02).

**Nuances explicitement respectées** (exigées par le ticket #14, vérifiées par test) : TDP
présenté comme indicateur de conception thermique et non comme consommation électrique
exacte ; GHz explicitement insuffisant seul pour comparer deux CPU (IPC, cœurs, génération) ;
64 bits jamais assimilé à « deux fois plus rapide » que 32 bits ; DDR5 explicitement
distinguée d'une simple « DDR4 plus rapide » (incompatibilité de génération, pas seulement
une différence de vitesse).

**Contexte IA MC03** : nouvelle entrée
`app/ai/context.py::PEDAGOGICAL_CONTEXTS["ampcr-mc03"]` (notions, compétences 1.1.1–1.1.4/
2.3.2–2.3.3, vocabulaire, contraintes reprenant explicitement les nuances TDP/GHz/64 bits/
DDR5 ci-dessus pour que le moteur IA ne les reproduise pas non plus). Aucune autre
modification du moteur IA (`app/ai/`, routes `/practice/api/ai/*`).

**Examen** : bloc publié avec 10 questions/20 points, aucune réponse ; corrigé complet dans
un second bloc `is_published: False`, jamais servi côté public.

**Tests** : +8 tests (`tests/test_informatique_mc03.py` : navigation, matière obligatoire
(dont les nuances TDP/GHz/64 bits/DDR5), 12 exercices, examen sans correction visible,
corrigé non publié, contexte IA enregistré, génération/correction via le moteur partagé
avec le contexte MC03 spécifiquement vérifié, non-régression MC01/MC02/Mathématiques),
`test_seed_is_idempotent` mis à jour pour les nouveaux effectifs. 198 tests au total, tous
verts. Aucun appel OpenAI réel dans les tests.

`ruff check .` : 36 erreurs, identiques (mêmes fichiers, mêmes règles) à celles de
`develop` — comparé via un worktree isolé, aucune nouvelle erreur.

**Vérifié manuellement** sur une base SQLite temporaire isolée (jamais `jury_central.db`,
intégrité re-vérifiée par MD5) : toutes les routes répondent 200, corrigé absent de la
réponse publique, 12 exercices présents, MC01/MC02/Mathématiques inchangés. Seed additif et
idempotent, aucun reset staging.

**Documentation** : `docs/current_state.md`, `docs/changelog.md`,
`docs/content_plan_informatique_francais.md`.

## 2026-09-16 — Informatique AMPCR : mini-cours 02 « Carte mère, formats et connectiques » (ticket #12)

Deuxième cours de la série Informatique AMPCR, contenu et périmètre pédagogique fournis
intégralement par ChatGPT dans le ticket #12. Réutilise **strictement** l'architecture du
ticket #10 — aucun nouveau mécanisme, aucun second moteur IA.

**Matière/UAA** : nouvelle UAA `MC02` (« Carte mère, formats et connectiques ») sous le
module `AMPCR` existant, navigable depuis `/uaa/ampcr-mc02`, juste après MC01.

**Contenu** (`app/seed.py::MC02_BLOCKS`, 24 blocs) : plan, 16 sections de cours (rôle
détaillé de la carte mère, formats ATX/micro-ATX/Mini-ITX, socket et compatibilité,
chipset, slots RAM/DIMM, PCIe, stockage SATA/M.2, alimentation interne ATX/EPS, connecteurs
internes, connectique arrière, F_PANEL, BIOS/UEFI/POST, méthode de compatibilité,
diagnostic no-POST, sécurité/ESD, vocabulaire FR/EN), 12 exercices progressifs (3 blocs) à
correction masquée à la demande, un bloc `ai_exercise` réutilisant le moteur du ticket #10,
une fiche mémo, et l'examen final.

**Contexte IA MC02** : nouvelle entrée
`app/ai/context.py::PEDAGOGICAL_CONTEXTS["ampcr-mc02"]` (notions, compétences 1.1.1–1.1.4/
1.2.3/2.3.2–2.3.3/3.4.1–3.4.2, vocabulaire, contraintes reportant DDR/dual-channel au
mini-cours 03, SATA/NVMe détaillé au mini-cours 04, alimentation/refroidissement au
mini-cours 05). Aucune autre modification du moteur IA (`app/ai/`, routes
`/practice/api/ai/*`) : le bloc `ai_exercise` de MC02 référence simplement cette nouvelle
clé de contexte.

**Examen** : bloc publié avec 10 questions/20 points, aucune réponse ; corrigé complet dans
un second bloc `is_published: False`, jamais servi côté public — même mécanisme
exactement qu'au mini-cours 01.

**Tests** : +8 tests (`tests/test_informatique_mc02.py` : navigation, matière obligatoire,
12 exercices, examen sans correction visible, corrigé non publié, contexte IA enregistré,
génération/correction via le moteur partagé avec le contexte MC02 — vérifié explicitement
que `FakeAIProvider` reçoit `course_key == "ampcr-mc02"`, pas MC01 ; non-régression MC01 et
Mathématiques), `test_seed_is_idempotent` mis à jour pour les nouveaux effectifs. 190 tests
au total, tous verts. `ruff check .` : 36 erreurs, identiques (mêmes fichiers, mêmes
règles) à celles de `develop` — comparé via un worktree isolé, aucune nouvelle erreur.

**Vérifié** : seed idempotent (second appel = 0 création), MC01 et Mathématiques
inchangés, corrigé de l'examen absent de la réponse HTTP publique.

**Documentation** : `docs/current_state.md`, `docs/content_plan_informatique_francais.md`.

## 2026-09-16 — Moteur générique de génération d'exercices et de correction par IA (complément ticket #10)

ChatGPT a complété le ticket #10 en cours de réalisation : le mini-cours 01 ne doit pas
reposer uniquement sur des exercices figés. Ajout d'un moteur réutilisable de génération
d'exercices à la demande (difficulté facile/moyen/difficile) et de correction par IA (API
OpenAI, côté serveur uniquement), en plus des 12 exercices éditoriaux déjà livrés (conservés
tels quels comme entraînement de référence garanti). Voir
[docs/ai_exercise_engine.md](ai_exercise_engine.md) pour l'architecture complète.

**Nouveau package `app/ai/`** : `schemas.py` (structures JSON typées — jamais de texte libre
non structuré), `context.py` (registre `PEDAGOGICAL_CONTEXTS`, un contexte borné par cours,
rédigé à la main), `prompts.py` (messages + schémas JSON stricts, testable sans réseau),
`provider.py` (interface générique `AIProvider` + hiérarchie d'exceptions),
`openai_provider.py` (implémentation réelle, HTTP via `httpx`, clé API jamais journalisée),
`fake_provider.py` (déterministe, pour les tests), `factory.py` (point d'entrée unique),
`integrity.py` (signature HMAC des exercices générés, réutilise `settings.secret_key`).

**Nouveau type de bloc `ai_exercise`** (`app/models.py::BlockType`, extension minimale et
générique) : `app/ai_exercise_blocks.py::AIExerciseBlockConfig` (JSON `{context_key,
intro}`), rendu par `app/main.py::uaa_detail` + `app/templates/uaa_detail.html`, widget
`app/static/js/ai_exercise.js`. Aucun changement de schéma de base côté SQLite (`type` est
un simple `VARCHAR`, vérifié sur la base staging avant modification).

**Nouvelles routes `app/practice.py`** : `POST /api/ai/generate` (retourne un exercice signé
HMAC) et `POST /api/ai/correct` (vérifie la signature avant tout appel IA — rejette un
énoncé modifié côté client sans jamais interroger le fournisseur). Erreurs claires : 503 si
`OPENAI_API_KEY` absente, 502 en cas d'échec du fournisseur (timeout, réponse invalide), 400
si l'énoncé a été altéré, 404/422 pour les cas invalides — jamais de 500 brut.

**Sécurité** : clé API exclusivement serveur (`.env`, jamais Git, jamais journalisée, jamais
transmise au navigateur) ; réponse candidate toujours traitée comme donnée délimitée à
évaluer, jamais comme instruction (`app/ai/prompts.py`) ; sortie forcée en JSON strict
(`response_format: json_schema`) ; contexte pédagogique borné par cours, jamais l'ensemble
de la base ; aucune écriture automatique dans le contenu éditorial du cours.

**Mini-cours 01** : nouveau bloc « Architecture d'un PC — Génère ton propre exercice (IA) »
(`app/seed.py`), ajouté après les 3 blocs d'exercices éditoriaux et avant la fiche mémo —
les 12 exercices éditoriaux et l'examen final restent inchangés.

**Tests** : +26 tests (`tests/ai/` : prompts, contexte, fournisseur factice, intégrité,
fournisseur réel avec `httpx.post` intercepté — succès, timeout, réponse malformée,
non-fuite de la clé API ; `tests/test_practice_ai_routes.py` : routes de bout en bout avec
`FakeAIProvider`, cas « non configuré » sans aucun mock réseau). 182 tests au total, tous
verts. `ruff check .` : 2 nouvelles occurrences de B008 (`Depends()` en valeur par défaut),
motif déjà présent 4 fois dans le projet avant ce complément — non corrigées, cohérence avec
l'existant plutôt que correction isolée.

**Dépendance** : `httpx` promu de `dev` vers les dépendances principales (`pyproject.toml`)
— nécessaire à `OpenAIProvider` en runtime, déjà présent et vérifié dans le projet (utilisé
jusqu'ici par `TestClient`).

**Vérifié manuellement** : widget affiché sur `/uaa/ampcr-mc01`, `app/static/js/ai_exercise.js`
correctement servi, `POST /practice/api/ai/generate` renvoie 503 avec message clair en
l'absence de clé, 422 sur difficulté invalide, 404 sur bloc inconnu, aucune fuite de
clé/secret dans les réponses. Aucun appel réseau réel effectué (pas de clé API disponible
dans cet environnement) — conforme à l'exigence de tests sans consommation d'API réelle.

## 2026-09-16 — Informatique AMPCR : mini-cours 01 « Architecture générale d'un PC » (ticket #10)

Premier contenu réel pour Informatique AMPCR, cours pilote de la série prévue des 38
mini-cours. Contenu et périmètre pédagogique fournis intégralement par ChatGPT dans le
ticket GitHub #10 (référentiel officiel cité : programme 345/2007/249 AMPCR), implémentés
sans en changer la portée. Aucune régression sur Mathématiques.

**Matière/module/UAA** : `Informatique` (nouvelle matière) → module `AMPCR` → UAA `MC01`
(« Architecture générale d'un PC »), navigable depuis `/subjects`,
`/subjects/informatique`, `/modules/ampcr`, `/uaa/ampcr-mc01`, exactement comme
Mathématiques.

**Architecture (réutilisée, pas réinventée)** :
- `app/seed.py` : `_ensure_subject()`/`_ensure_modules()` extraits du code jusque-là
  spécifique à Mathématiques, pour un seed additif et idempotent **générique**,
  réutilisable par les mini-cours 02–38 et par Français. `seed()` appelle désormais ces
  helpers deux fois (Mathématiques, puis Informatique) au lieu d'un chemin unique câblé en
  dur. Aucun changement de schéma de base de données.
- `app/card_kind.py` : le mot-clé « examen » classe désormais un bloc en carte « exam » (au
  même titre que « mini-test »), pour que « Examen final — ... » réutilise directement
  `ExamCard` sans nouveau type de bloc.
- `app/static/css/design-system.css` : nouveau composant générique `.jc-flow` (schéma de
  flux en étapes reliées par des flèches, responsive, compatible impression) — voir
  `docs/UI_GUIDELINES.md`. Aucun changement JS, aucune nouvelle dépendance.
- Tous les autres mécanismes sont réutilisés tels quels : blocs `markdown`, classification
  de carte par titre, masquage de correction générique
  (`app/static/js/design_system.js::splitExerciseCorrections()`), blocs `is_published`.

**Contenu** : 18 blocs (`MC01_BLOCKS`) — plan, 9 sections de théorie (vue globale, carte
mère, CPU, RAM, stockage, GPU, PSU, périphériques E/S, vocabulaire FR/EN + vocabulaire
ancien du référentiel), 1 scénario d'interaction (ExampleCard), 12 exercices progressifs
répartis en 3 blocs (correction masquée à la demande, mécanisme existant), 1 fiche mémo, et
l'examen final.

**Examen — traçabilité stricte** : le bloc « Examen final... » (publié) contient les 10
questions et le barème (2 pts chacune) mais **aucune réponse**. Le corrigé/barème complet
vit dans un second bloc, « Examen final — Corrigé (réservé formateur, non publié) »,
`is_published: False` — jamais transmis à la route publique
(`app/main.py::uaa_detail` ignore les blocs non publiés), consultable/éditable uniquement
depuis `/admin`. Garantie serveur, pas seulement un masquage CSS/JS côté client.

**Tests** : +14 tests (`tests/test_card_kind.py`, `tests/test_informatique_mc01.py`,
mise à jour de `test_seed_is_idempotent` pour les nouveaux effectifs) — 156 tests au total,
tous verts. `ruff check .` : aucune nouvelle erreur (36 préexistantes, non liées à ce
ticket, déjà signalées avant ce ticket).

**Vérifié manuellement** : serveur démarré sur une base SQLite temporaire isolée (jamais
`jury_central.db`) — `/subjects`, `/subjects/informatique`, `/modules/ampcr`,
`/uaa/ampcr-mc01` répondent 200 ; les 12 exercices et les 5 types de cartes s'affichent
(`jc-card--theory/--example/--exercise/--summary/--exam`) ; le schéma `.jc-flow` est
présent ; le corrigé de l'examen n'apparaît jamais sur la page publique ; l'admin, une fois
connecté, voit bien le bloc corrigé non publié ; Mathématiques (`/uaa/mb32-uaa1`) reste
inchangé.

**Documentation** : `docs/content_workflow.md` (nouvelle section : contenu rédigé depuis un
cahier des charges de ticket, sans fichier `docs/sources_cours/`), `docs/UI_GUIDELINES.md`
(composant `.jc-flow`), `docs/components/ExamCard.md` (mot-clé « examen », variante examen
sans correction révélable), `docs/current_state.md`,
`docs/content_plan_informatique_francais.md` (mise à jour de statut).

## 2026-09-16 — Validation staging réelle du ticket #6 et correction de doc

Première exécution réelle de `scripts/deploy_staging.sh` contre le staging opérationnel,
à la demande explicite de l'utilisateur. Résultat : succès complet, sans interaction
`sudo`, sans échec — voir le rapport de validation transmis en session pour le détail des
vérifications (service, nginx, `/health`, HTTPS public, intégrité de `jury_central.db`).

Cette validation a révélé une inexactitude dans `docs/deployment_staging.md` § 1.1 : le
nom du fichier de configuration nginx documenté (« probablement
`jury-central.lodylands.com` ») ne correspondait pas au fichier réel
(`/etc/nginx/sites-available/jury-central`, sans le domaine dans le nom). Corrigé, avec la
définition systemd également confirmée mot pour mot (§ 1.2, plus besoin de « à
confirmer »). Aucune autre modification : script, comportement de l'application et tests
inchangés.

**Tests** : aucune modification de code applicatif ; suite complète toujours verte
(`pytest -q`).

## 2026-09-16 — Documenter et automatiser le déploiement staging (ticket #6)

Un environnement staging (`https://jury-central.lodylands.com`, installé manuellement sur
AWS) existe désormais. Ce ticket documente son architecture et ajoute un script de
déploiement prudent, sans toucher à l'infrastructure active (nginx, Certbot, systemd) ni
déployer quoi que ce soit.

**Nouveau `scripts/deploy_staging.sh`** : refuse toute branche autre que `develop`, refuse
un working tree sale, synchronise `origin/develop` en fast-forward uniquement (jamais de
force), installe les dépendances dans le `.venv` existant, exécute `pytest -q` (aucun
redémarrage si échec), ne touche jamais `jury_central.db`, redémarre
`jury-central.service` seulement après succès, puis vérifie que le service est `active` et
que `http://127.0.0.1:8100/health` répond. Ne lit, n'affiche ni ne modifie jamais `.env`.
Vérifié avec `bash -n` et `shellcheck` (aucune erreur), non exécuté contre le staging réel
dans ce ticket (interdit par son périmètre).

**Documentation**
- Nouveau `docs/deployment_staging.md` : architecture staging complète (domaine, nginx,
  systemd, port, `.env`, SQLite, logs), fonctionnement détaillé du script, commandes de
  diagnostic, et rappel explicite que `seed-db`/`reset-db` ne font jamais partie d'un
  déploiement.
- `docs/git_workflow.md` : nouvelle section « Après le merge : déploiement staging »,
  renvoyant vers le document ci-dessus.
- `docs/PROJECT_RULES.md` § 16 : ajout explicite de l'interdiction de modifier
  nginx/Certbot/systemd ou de déployer sans instruction explicite.
- `.env.example` : commentaire `DATABASE_URL` corrigé (la variable est bien lue par
  `app/database.py`, contrairement à ce qu'indiquait l'ancien commentaire).
- `docs/INDEX.md`, `docs/README.md` : référencement du nouveau document.

**Tests** : aucune modification de code applicatif ; suite complète toujours verte
(`pytest -q`).

## 2026-09-16 — Cadrage Informatique AMPCR et Français CESS P (ticket #4)

Changement de priorité produit : Informatique (AMPCR) devient la priorité n°1, Français
(CESS Professionnel) la priorité n°2, passant devant la suite des mathématiques (MB32
UAA3, MQ32, MQ34). Ticket de cadrage uniquement — **aucun import de contenu, aucun
changement fonctionnel**.

**Constat de l'inventaire** : ni source officielle ni brouillon ChatGPT pour ces deux
matières ne sont présents dans le dépôt (`docs/sources_cours/` ne contient que
Mathématiques ; `app/seed.py` ne définit que la matière Mathématiques). Les suites de
mini-cours Informatique et de 10 cours Français mentionnées comme déjà préparées avec
ChatGPT existent uniquement hors du dépôt à ce stade.

**Documentation**
- Nouveau `docs/content_plan_informatique_francais.md` : inventaire détaillé, cartographie
  proposée (structure Subject/Module/UAA à confirmer par les référentiels officiels
  manquants) pour Informatique puis Français, écarts/sources manquantes, règle de
  traçabilité officiel/brouillon ChatGPT (champ `source_type` proposé, emplacement dédié
  aux brouillons distinct de `docs/sources_cours/`), et neuf tickets atomiques proposés
  (A à I) avec dépendances explicites.
- `docs/current_state.md` et `docs/ROADMAP.md` : priorité et statuts VS004/VS007 mis à
  jour pour refléter ce nouvel ordre et renvoyer vers le plan.
- `docs/INDEX.md` et `docs/README.md` : référencement du nouveau document de planification.

**Tests** : aucune modification de code applicatif ; suite complète toujours verte
(`pytest -q`).

**Point à clarifier** (signalé, non tranché — voir `docs/PROJECT_RULES.md` § 11) : la
suite Français ChatGPT est décrite comme « 10 cours » mais seuls 9 intitulés sont donnés
dans le ticket #4 ; à vérifier dès que les fichiers seront fournis.

## 2026-09-16 — Assainissement de la gouvernance documentaire (ticket #2)

Un audit de reprise a mis en évidence plusieurs contradictions documentaires (deux
fichiers de règles concurrents, roadmap désynchronisée, nombre de tests obsolète,
fichiers vides). Ce ticket fixe une source unique de vérité et le workflow
ChatGPT (chef de projet, tickets) → GitHub (source de vérité des tâches) → Claude Code
(développement), avant toute nouvelle fonctionnalité. Aucun changement fonctionnel de
l'application.

**Documentation**
- `docs/PROJECT_RULES.md` : source unique des règles du projet. Fusion du contenu
  pertinent et non contradictoire de l'ancien fichier fantôme `(PROJECT_RULES.md`
  (sécurité, UX, vertical slice, interdits explicites) ; § 6 (pilotage) et § 8 (Git)
  réécrits pour le workflow tickets GitHub ; § 7 et § 11 complétés (tests manuels,
  signalement des décisions produit). Numérotation des règles existantes préservée
  (§ 2 notamment, référencée depuis `docs/components/INDEX.md`).
- Suppression du fichier fantôme `./(PROJECT_RULES.md`, tracké à la racine et
  contradictoire avec `docs/PROJECT_RULES.md` (vision produit, stack, workflow Git
  différents). Contenu utile récupéré ci-dessus ; ce qui contredisait le stack réel
  (Python 3.13, Alembic, HTMX) n'a pas été repris — voir points ouverts.
- `docs/git_workflow.md` réécrit : branches `feature/<ticket>-<slug>` /
  `fix/<ticket>-<slug>` depuis `develop`, commit + push autorisés après tests et
  documentation, aucun merge ni déploiement sans validation explicite.
- `docs/ROADMAP.md` : statuts VS002 et VS003 corrigés pour refléter l'état réel du code
  (Design System livré sur les pages UAA, restant sur les listings ; composant
  `value_table` livré, 9 des 10 types de `EXERCISE_TYPES.md` restants ; automatisation de
  l'import de contenu non implémentée, distinguée de VS003).
- `README.md` : retrait du nombre de tests figé (« 87 tests ») au profit d'un renvoi à
  `pytest -q`, pour éviter une référence à maintenir manuellement à chaque évolution.
- Suppression de `TODO.md` et `docs/SEMANTIC_IMPORT_ENGINE.md` : fichiers vides, sans
  fonction actuelle ni référence ailleurs dans le projet (vérifié par recherche globale).

**Tests** : aucune modification de code applicatif ; suite complète toujours verte
(`pytest -q`).

**Points restant à valider** (signalés plutôt que tranchés, voir `docs/PROJECT_RULES.md`
§ 11) :
- Le fichier fantôme mentionnait HTMX et Alembic comme orientations techniques et
  Python 3.13 comme version cible ; non repris car contredits par le stack réellement
  implémenté et documenté (vanilla JS, pas de migrations, Python 3.12+). À confirmer que
  ce n'est pas une intention produit oubliée.
- `docs/README.md` (index du dossier `docs/`) décrit `development.md` comme la
  « roadmap du projet » et n'y mentionne pas `docs/ROADMAP.md` — incohérence préexistante,
  hors périmètre strict de ce ticket, à traiter séparément.

## 2026-07-14 — VS003.1 : renderer de contenu riche unique

Plusieurs écrans affichaient encore du texte brut (question de quiz, énoncé d'exercice
généré, indice, correction) même quand le contenu source contenait un tableau, une liste ou
une formule — par exemple une question de quiz décrivant un tableau en une phrase :
« Le tableau x : -1, 0, 1 → f(x) : 4, 4, 4 correspond à quelle fonction ? ». Cette tranche
fait passer tous ces écrans par le même renderer que les cours
(`app/content.py::render_markdown`), et convertit ce cas concret en un vrai tableau
Markdown.

**Serveur — un champ `*_html` ajouté à chaque endroit qui envoyait du texte brut** :
- `app/quiz.py` : `QuizConfig.to_public_dict()` ajoute `question_html`.
- `app/exercise_blocks.py` : `exercise_to_public_dict()`/`exercise_to_dict()` ajoutent
  `statement_html`, `hint_html`, `solution_steps_html`.
- `app/value_table.py` : nouvelle fonction `value_table_public_dict()` (`question_html`,
  `hint_html` — ne peut pas vivre dans `generators/exercise_types.py`, qui doit rester
  indépendant de FastAPI) ; `ValueTableCorrection.to_dict()` ajoute `explanation_html`.
- `app/practice.py` : `/api/reveal` et `/api/quiz/{id}/verify` renvoient aussi le HTML
  rendu de la correction/explication.
- `app/main.py` : le widget de quiz isolé utilise désormais `QuizConfig.to_public_dict()`
  (déjà utilisé par le parcours groupé) au lieu d'accéder directement au dataclass — même
  représentation partout, une seule méthode de rendu.

**Client — un seul point d'entrée pour insérer du contenu riche** :
- Nouveau `app/static/js/rich_content.js` : `renderRichContent(container, html)` — injecte
  le HTML déjà rendu, ré-applique les mêmes traitements que les cours (tableaux
  responsives, citations → WarningCard, cellules éditables) et relance MathJax scopé au
  conteneur (MathJax ne rescane pas seul le contenu inséré après le chargement initial).
- `app/static/js/design_system.js` : `wrapBlockquotesAsWarningCards`,
  `wrapTablesResponsively`, `makeEmptyCellsEditable` acceptent maintenant un `root` et sont
  regroupées dans `enhanceRichContent(root)`, appelée au chargement de la page **et** par
  `renderRichContent()` — plus de duplication entre le traitement initial et le traitement
  du contenu inséré dynamiquement.
- `quiz.js`, `exercise.js`, `value_table.js` : toute insertion de texte (`textContent`)
  remplacée par `renderRichContent()` avec le champ `*_html` correspondant.

**Contenu** : la question de quiz « Le tableau x : -1, 0, 1 → f(x) : 4, 4, 4 correspond à
quelle fonction ? » (`app/seed.py`, quiz Fonction constante) reformulée en question courte +
tableau Markdown (`| $x$ | -1 | 0 | 1 |` / `| $f(x)$ | 4 | 4 | 4 |`) — mêmes valeurs, même
bonne réponse, même explication, uniquement la présentation change.

**Tests** : 14 nouveaux tests (`tests/test_rich_content.py`) couvrant chaque champ `*_html`
ajouté, le rendu Markdown d'une question de quiz (tableau, liste, texte simple), et — cas
concret demandé — la vérification que cette question précise produit un `<table>` avec
`<td>4</td>` sur la page publique de MB32 UAA1 —, ainsi que les routes `/api/reveal` et
`/api/quiz/{id}/verify`. Un test existant (`test_quiz.py`) mis à jour pour le nouveau champ.
142 tests au total, `ruff check .` sans erreur.

Vérifié manuellement après `reset-db` : la question du quiz Fonction constante s'affiche
comme un vrai tableau (extrait et vérifié depuis le JSON `data-questions` de la page), les
routes `/api/reveal`, `/api/quiz/{id}/verify`, `/admin/value-table-demo/verify` renvoient
toutes leur champ `*_html`, `/admin/generators` bascule toujours correctement entre les deux
rendus, aucune régression sur les autres pages.

## 2026-07-14 — VS003 (suite) : branchement du composant value_table sur la fonction constante

Le composant `value_table` livré précédemment n'était utilisé nulle part (seulement une
démo admin fixe). Cette tranche le branche réellement : les exercices générés de la
fonction constante (MB32 UAA1) affichent désormais un vrai tableau interactif sur la page
publique, au lieu d'un énoncé texte à réponse unique.

**`generators/maths/constant_function.py`** — réécrit : retourne un `InteractiveExercise`
(`value_table`) au lieu d'un `GeneratedExercise`. Les quatre anciens types d'exercice
(image/table/find_p/match) sont unifiés en un seul format « tableau de valeurs de f(x) = p à
compléter » — la logique de difficulté (plage de p, `_random_p`) et le déterminisme par seed
sont inchangés. `find_p`/`match` (trouver p à partir d'un point/graphique) restent couverts
par le quiz et les exemples du cours, déjà présents dans MB32 UAA1.

**`generators/base.py`** — `ExerciseGenerator.__call__` retourne désormais
`GeneratedExercise | InteractiveExercise` : les deux moteurs coexistent, chaque appelant
détecte le type retourné plutôt que d'en supposer un seul. `maths.equations.linear_equation`
n'a pas été modifié.

**Suppression de la duplication** entre les deux moteurs :
- `generate_exercises()` (`app/exercise_blocks.py`) retourne désormais les objets bruts
  (plus de conversion en dict interne) : un seul endroit (la route `uaa_detail`) décide
  comment afficher chaque type, au lieu de dupliquer cette décision.
- `/practice/api/value-table/verify` (nouveau, générique) régénère l'exercice depuis
  `(generator, difficulty, seed)` et vérifie cellule par cellule — même principe que
  `/api/verify` pour l'ancien moteur, réutilise `check_value_table_answers()` déjà écrit
  pour la démo admin.
- `/admin/generators` (outil de debug) détecte le type retourné et affiche soit le composant
  interactif `value_table` (réutilisation totale de `value_table.js`), soit l'ancienne vue
  `<dl>` — un seul outil pour les deux moteurs plutôt que deux outils séparés.
- `app/static/js/value_table.js` : le payload de vérification inclut
  `generator`/`difficulty`/`seed` uniquement quand ces attributs sont présents sur le
  conteneur — un seul renderer sert à la fois la démo fixe et les exercices générés.
- Garde-fous ajoutés sur les routes de l'ancien moteur (`/api/generate`, `/verify`,
  `/reveal`) : erreur claire (400) si un générateur `value_table` y est appelé par erreur,
  plutôt qu'un plantage.

**Tests** : 13 nouveaux tests d'intégration
(`tests/test_practice_value_table.py`) couvrant la page publique de MB32 UAA1 (widget
value_table présent, ancien widget absent, aucune fuite de réponse), l'endpoint générique de
vérification (correct/incorrect), les garde-fous croisés entre les deux moteurs, et la
non-régression complète de `maths.equations.linear_equation` (génération, vérification,
outil admin). Tests existants adaptés : `tests/generators/test_constant_function.py`
(entièrement réécrit pour le nouveau format), `tests/generators/test_architecture.py` (le
test de contrat accepte maintenant les deux types), `tests/test_exercise_blocks.py`
(`generate_exercises()` retourne des objets, plus des dicts). 128 tests au total, `ruff
check .` sans erreur.

Vérifié manuellement après `reset-db` : `/uaa/mb32-uaa1` affiche 3 tableaux interactifs pour
la fonction constante (aucune trace de `exercise-widget` ni de réponse dans le HTML),
vérification cellule par cellule fonctionnelle avec un vrai seed extrait de la page,
`/admin/generators` bascule correctement entre les deux rendus selon le générateur choisi,
`/admin/value-table-demo` toujours fonctionnel, aucune régression sur les autres pages.

## 2026-07-14 — VS003 : premier composant d'exercice interactif officiel (value_table)

Démarrage de VS003 (voir `docs/ROADMAP.md`). Implémente le format officiel décrit dans
`docs/EXERCISE_TYPES.md` : « le générateur ne produit jamais de HTML, uniquement des
données ; le rendu appartient exclusivement au frontend. » Premier type construit :
`value_table` (tableau de valeurs à compléter, vérifié cellule par cellule). Aucun
générateur existant n'a été modifié — uniquement la nouvelle architecture, son renderer et
ses tests.

**`generators/exercise_types.py`** (nouveau) — `InteractiveExercise` : enveloppe générique
`{type, question, data, answer, hint, explanation, difficulty, seed}` commune à tous les
futurs types d'exercices interactifs. `to_public_dict()` exclut toujours `answer` ; seul
`to_full_dict()` (serveur / debug admin) l'inclut.

**`generators/value_table.py`** (nouveau) — `ValueTableRow`, `ValueTableData`
(colonnes + lignes, cellules éditables ou non), `build_value_table_exercise()`. La position
des cellules éditables (`editable_positions()`, ordre lignes puis colonnes) définit l'ordre
attendu de `answer["cells"]` — une liste à plat, conforme à l'exemple officiel du document
(une seule ligne éditable) et généralisée aux tableaux multi-lignes.

**`app/value_table.py`** (nouveau) — `check_value_table_answers()` : vérification cellule
par cellule, réutilise `app/answer_checking.py` (comparaison exacte via `Fraction`, aucun
`eval()`) comme les quiz et exercices générés existants.

**`app/static/js/value_table.js`** (nouveau) — construit entièrement le tableau (aucun HTML
reçu du serveur), champs de saisie sur les cellules éditables, bouton Vérifier, indice
optionnel, coloration verte/rouge cellule par cellule après vérification, correction
détaillée (explication, jamais un simple Correct/Incorrect). Aucune dépendance JS externe.

**`app/static/css/design-system.css`** — `.value-table` réutilise le style des tableaux de
VS002.1 (bordures, padding, en-tête ombré) pour rester homogène ; états `.jc-fill-input
--correct`/`--incorrect` ; règle d'impression dédiée (`@media print`) qui vide visuellement
les cellules de saisie sans afficher texte, couleur ni correction — conforme à
`docs/EXERCISE_TYPES.md` (« Mode impression : zones vides, aucune correction, aucune
interaction »).

**Outil de debug** : `/admin/value-table-demo` (admin uniquement) prévisualise le composant
avec un exercice fixe (`f(x) = 2x + 1`, une ligne donnée + une ligne à compléter), sans être
relié à un générateur — sert à tester l'architecture de bout en bout avant la prochaine
étape (brancher un vrai générateur, hors périmètre de cette tranche).

**Tests** : 28 nouveaux tests (`tests/test_value_table.py`) — structures de données,
validation, ordre des cellules éditables sur tableaux multi-lignes, vérification correcte/
incorrecte/partielle, formats numériques (virgule et point), `to_public_dict()` ne contient
jamais `answer`, protection admin de la démo. 115 tests au total, `ruff check .` sans
erreur. Vérifié manuellement : page de démo (aucune trace de la réponse dans le HTML
généré), vérification cellule par cellule via l'API, aucune régression sur les autres pages.

## 2026-07-14 — VS002.1 : véritables tableaux pédagogiques

Première petite fonctionnalité de la fin de VS002 (voir `docs/ROADMAP.md`). Objectif :
tous les tableaux de Jury Central doivent être lisibles, homogènes et utilisables sur
mobile, sans toucher aux quiz, à la navigation ni à l'impression.

**`app/static/css/design-system.css`**
- Style de tableau propre à Jury Central (bordures, padding `0.55rem 0.75rem`, en-tête
  ombré, lignes zébrées, padding réduit en mobile) plutôt que la classe utilitaire
  `table-sm` de Bootstrap, jugée trop dense pour des tableaux de formules/valeurs.
- Nouvelle classe `.jc-list-alpha` : liste `<ol>` stylée en `a, b, c...`
  (`list-style-type: lower-alpha`) pour les sous-questions numérotées par lettre.

**`app/static/js/design_system.js`**
- `wrapTablesResponsively()` n'ajoute plus `table-bordered`/`table-sm` (remplacés par le
  CSS ci-dessus) ; le défilement horizontal (`table-responsive`) est inchangé.

**`app/seed.py`**
- Trois exercices de MB32 UAA2 (Solides — Exercice « connaître », Solides — Exercice 1,
  Mini-test Question 2) énuméraient leurs sous-questions en `a) ... b) ... c) ...` dans un
  seul paragraphe Markdown (aucun marqueur de liste reconnu par le moteur Markdown). Reformatés
  en `<ol class="jc-list-alpha">` (HTML direct dans le Markdown, même procédé que le
  graphique SVG de la perspective cavalière) : mêmes lettres affichées, vraie liste HTML
  accessible. Texte inchangé, uniquement la structure de présentation.
- Audit du contenu : aucun autre exercice « à compléter » sans tableau réel, aucune autre
  liste lettrée orpheline.

**Tests** : 87 tests inchangés (aucune modification de logique métier), `ruff check .`
sans erreur. Vérifié manuellement après `reset-db` sur `/uaa/mb32-uaa1` et `/uaa/mb32-uaa2` :
les trois listes converties s'affichent en `<ol class="jc-list-alpha"><li>...`, le tableau à
compléter du mini-test garde ses 8 cellules éditables, aucune régression sur les quiz
(`quiz-run` inchangé) ni sur les autres pages.

## 2026-07-14 — Design System réutilisable (cartes, exercices interactifs, tableaux éditables)

Mise en œuvre de `docs/UI_GUIDELINES.md`. Objectif : transformer l'affichage d'une UAA — un
mur de blocs Markdown identiques — en une véritable expérience d'apprentissage, sans toucher
au contenu pédagogique existant (MB32 UAA1 et UAA2), uniquement sa présentation et son
interaction.

**Composants (`app/templates/_cards.html`)**
- Macro générique `card(meta, title)` + alias nommés `TheoryCard`, `ExampleCard`,
  `ExerciseCard`, `QuizCard`, `WarningCard`, `SummaryCard` — icône, libellé et couleur par
  type, conformes au code couleur de `UI_GUIDELINES.md` (bleu=information, vert=réussite,
  orange=méthode/exercice, rouge=attention, or=mémo).
- `app/card_kind.py` : classe un bloc de leçon en type de carte à partir de son **titre
  uniquement** (ex. « Solides — Cours » → théorie, « Solides — Exercices » → exercice,
  « Mini-test final » → exam, « Fiche mémo » → résumé) — aucune lecture ni modification du
  contenu.
- `app/static/css/design-system.css` : styles des cartes, tableaux, citations, champs
  éditables ; responsive (padding réduit en mobile) ; règles d'impression (cartes aplaties
  pour la fiche mémo imprimable existante).

**Interactions (`app/static/js/design_system.js`)**
- Citations Markdown (`> Piège...`) transformées automatiquement en WarningCard.
- Tableaux enveloppés dans `.table-responsive` (défilement horizontal) + classes Bootstrap.
- Cellules de tableau vides rendues éditables (`<input>` injecté) — couvre notamment le
  tableau à compléter du mini-test UAA2, sans marquage spécial dans le contenu.
- Exercices rédigés (blocs classés « exercice » ou « exam ») : la correction (repérée par un
  paragraphe `**Correction :**` ou un titre `## Correction...`) est déplacée dans un conteneur
  masqué, remplacée par un champ de réponse libre et un bouton « Afficher la correction ».
  Fonctionne aussi bien sur le nouveau contenu UAA2 (« Correction : » inline) que sur l'ancien
  contenu UAA1 (« ## Correction détaillée ») sans aucune modification de texte.
- Barre de progression de lecture de la leçon (scroll), sticky en haut du contenu.

**`app/static/js/quiz.js`**
- Le parcours de quiz groupé (`quiz-run`, utilisé par tous les quiz de UAA1 et UAA2)
  n'affichait que « Correct. »/« Incorrect. » après chaque réponse ; il affiche désormais
  systématiquement l'explication retournée par le serveur, comme le fait déjà le widget de
  quiz isolé. Feedback aligné sur `UI_GUIDELINES.md` (✅ Correct / ❌ Incorrect).

**`app/main.py` / `app/templates/uaa_detail.html`**
- Chaque bloc rendu (markdown, exercice généré, quiz, quiz groupé) est désormais enveloppé
  dans le composant carte correspondant, plutôt que dans une simple `<section>` Bootstrap.

**Décisions volontairement limitées à cette tranche**
- Les exercices rédigés restent en auto-évaluation (comparaison libre avec la correction) et
  non en correction automatique : la plupart n'ont pas de réponse unique vérifiable, et
  extraire une réponse par analyse de texte aurait été peu fiable. `answer_checking.py`
  continue d'être utilisé tel quel pour les quiz et exercices générés.
- Le mini-test reste un seul bloc à correction masquée plutôt qu'un parcours paginé
  question par question (Précédent/Suivant/Terminer) — voir `current_state.md`, Points
  ouverts.

**Tests** : 87 tests inchangés (aucune modification de logique métier), `ruff check .` sans
erreur. Vérifié manuellement sur `/uaa/mb32-uaa2` et `/uaa/mb32-uaa1` (aucune régression),
ainsi que `/`, `/subjects`, `/modules/mb32`, `/admin/login`, `/practice/equations`.

## 2026-07-14 — Import complet de MB32 UAA2 (Géométrie)

Import de la première UAA via le nouveau workflow décrit dans `docs/IMPORT_WORKFLOW.md`, à
partir de la source officielle unique
`docs/sources_cours/CESS/P/Mathématiques/MB32/UAA2/cours.html` (non modifiée). Contrairement à
MB32 UAA1 (une seule leçon détaillée, le reste en placeholders non publiés), UAA2 est intégrée
**intégralement** : aucune section du cours source n'est omise, résumée ni reformulée.

**Contenu**
- UAA `mb32-uaa2` (position 2 dans MB32, publiée), 38 blocs de leçon répartis en 6 leçons
  conformes à `docs/content_workflow.md` et `docs/REFERENCE_UAA.md` : Solides, Perspective
  cavalière, Patrons, Vues coordonnées, Aires, Volumes.
- Chaque leçon reprend, quand la source le permet : présentation, cours (vocabulaire, tableaux,
  formules), exemples résolus, exercices rédigés avec correction détaillée, et un court quiz
  auto-corrigé (2 à 3 questions par leçon, regroupées via `QuizConfig.group`) repris directement
  des exercices déjà présents dans le cours plutôt que d'un contenu inventé.
- Le schéma SVG de la perspective cavalière est repris tel quel (le rendu markdown laisse
  passer le HTML brut, comme pour `<div class="jc-graph-constant">` dans UAA1).
- Contenu transversal placé en fin d'UAA (comme dans la source) : mini-test final type examen
  avec sa correction, fiche mémo récapitulative, liste de ressources externes.
- Formules converties en LaTeX (`$...$`) pour un rendu MathJax cohérent avec UAA1 ; le texte du
  cours (théorie, énoncés, corrections) n'est ni résumé ni reformulé.

**Décision technique** : les questions de quiz numériques n'utilisent que des réponses exactes
(ex. `96`, `120`) car `answer_checking.py` compare des `Fraction` exactes sans tolérance ; les
résultats impliquant π (arrondis dans la source, ex. ≈791,7 cm²) sont posés en QCM plutôt qu'en
question numérique, pour éviter un quiz où la valeur exacte attendue diffère de l'arrondi
affiché.

**Code**
- `app/seed.py` : ajout de `UAA2_CODE`/`UAA2_TITLE`/`UAA2_BLOCKS` (même convention que UAA1).
  `seed()` refactorée pour appeler un helper `_seed_uaa()` commun aux deux UAA plutôt que de
  dupliquer la logique de création — reste strictement additif et idempotent.
- `tests/test_admin_content_hierarchy.py` : `test_seed_is_idempotent` mis à jour (2 UAA et
  `len(UAA1_BLOCKS) + len(UAA2_BLOCKS)` blocs désormais attendus après un seed).
- 87 tests au total (inchangé), `ruff check .` sans erreur.
- Vérifié manuellement : `/uaa/mb32-uaa2` (200, 30 sections, tableaux et SVG rendus, MathJax
  actif), `/modules/mb32` (liste UAA1 et UAA2), admin (`/admin/modules/1` liste les deux UAA),
  API `/practice/api/quiz/{id}/verify` (réponses correctes/incorrectes, QCM et numérique).

## 2026-07-14 — Gestion complète de la hiérarchie de contenu depuis l'admin

Objectif : supprimer la dépendance fonctionnelle à `app/seed.py` pour créer du contenu
pédagogique réel. Il est désormais possible de créer MB32 UAA2 (ou toute autre
matière/module/UAA) **entièrement depuis l'administration**, sans modifier de code ni
relancer `seed-db` — vérifié manuellement de bout en bout. Voir `docs/admin.md`, section
"Gérer la hiérarchie de contenu", et `docs/content_workflow.md`.

**Modèles (changement de schéma, nécessite `reset-db` en local)**
- `UAA.position` (entier, ordre d'affichage dans un module) et `UAA.is_published` (bool,
  défaut `False`) — mêmes conventions que sur `LessonBlock`.
- `Module.uaas` trié par `position` (comme `UAA.lesson_blocks` l'est déjà par `position`).

**Admin — nouvelles routes (15), réutilisant entièrement le panneau existant**
- Matières : créer, modifier, supprimer (`/admin/subjects/new`, `/admin/subjects/{id}/edit`,
  `/admin/subjects/{id}/delete`).
- Modules : créer, modifier, supprimer, imbriqués sous une matière.
- UAA : créer, modifier, supprimer, avec position et case "Publiée".
- Validation serveur : champs obligatoires, longueurs alignées sur les colonnes de la base,
  unicité des slugs et des noms vérifiée explicitement avant écriture (message clair plutôt
  qu'une erreur SQL brute), slug vide impossible. Aucun `eval()`.
- Suppression avec confirmation affichant le **nombre exact** d'éléments supprimés en
  cascade (modules/UAA/blocs), calculé côté serveur.
- Une UAA non publiée disparaît de la liste publique de son module et sa page renvoie 404.

**`app/seed.py` — rôle clarifié, plus jamais destructif silencieusement**
- Ne modifie plus le titre d'une UAA existante à chaque exécution (régression corrigée :
  cela aurait écrasé un titre édité depuis l'admin).
- Affiche un résumé clair (créé / conservé / retiré) à chaque exécution.
- Nouvelle commande **distincte et explicite** `reset-db` (supprime la base puis reseed) —
  jamais appelée automatiquement.
- `app/database.py` lit `DATABASE_URL` depuis l'environnement si définie (base de
  développement inchangée par défaut) — permet aux tests de ne jamais toucher
  `jury_central.db`.

**Tests — première suite `TestClient`**
- `tests/conftest.py` : base SQLite temporaire isolée, fixtures `client`/`admin_client`/
  `db_session`.
- `tests/test_admin_content_hierarchy.py` (17 tests) : CRUD des 3 niveaux, rejet de slug
  dupliqué, protections admin (redirection sans session), suppression en cascade,
  publication/dépublication, idempotence du seed, et garantie que le seed ne modifie jamais
  un titre ou un contenu édité manuellement.
- 87 tests au total (+17). `ruff check .` sans erreur.

## 2026-07-13 — Tranche verticale : MB32 UAA1 → Fonction constante

Première expérience étudiante complète de bout en bout (cours, graphique interactif,
exercices générés à l'infini, quiz noté, fiche mémo imprimable), plutôt qu'une UAA entière
esquissée superficiellement. Voir `docs/mb32-uaa1.md` pour le détail complet.

**Contenu pédagogique**
- Section "Fonction constante" de MB32 UAA1 entièrement rédigée : présentation, cours
  (MathJax), graphique interactif (Plotly, curseur sur $p$), 5 exemples résolus, 1 exercice
  guidé avec correction détaillée, exercices générés automatiquement, quiz de 10 questions
  (QCM, vrai/faux, numérique), fiche mémo imprimable.
- Ancien contenu placeholder/démo devenu obsolète supprimé au profit du vrai contenu
  (migration automatique dans `app/seed.py` via `OBSOLETE_DEMO_BLOCK_TITLES`).

**Nouveau générateur**
- `maths.functions.constant_function` : fonction constante $f(x) = p$, 4 formulations, 3
  niveaux, déterministe par seed. Ajout du champ `hint` (indice) sur `GeneratedExercise`,
  rétrocompatible.

**Validation des réponses (changement d'architecture)**
- Les réponses correctes ne sont plus jamais envoyées au navigateur avant que l'étudiant ait
  répondu (exercices générés et quiz). Nouveau module `app/answer_checking.py` (parsing et
  comparaison exacte via `Fraction`, aucun `eval()`). Trois nouvelles routes publiques dans
  `app/practice.py` : `POST /api/verify`, `POST /api/reveal`,
  `POST /api/quiz/{block_id}/verify`. `app/exercise_blocks.py` distingue désormais une
  représentation publique (sans réponse) et une représentation complète (réservée à l'outil
  de debug admin `/admin/generators`).

**Quiz : nouveaux modes**
- `QuizConfig` étendu (rétrocompatible) : `answer_type` (`choice` ou `numeric`),
  `correct_value`, `group`, `order_in_group`. Plusieurs blocs `quiz` partageant un `group`
  sont fusionnés côté public en un seul parcours interactif (une question à la fois, score,
  bouton "Recommencer") — sans changement de schéma de base de données.

**Graphiques interactifs**
- Plotly chargé via CDN, uniquement sur les pages qui en ont besoin. Un contenu Markdown
  active un graphique via un marqueur HTML (`<div class="jc-graph-constant">`), détecté et
  monté par `app/static/js/interactive_graph.js`. Pas de nouveau type de bloc, pas de
  dépendance Python.

**Admin**
- Formulaire de bloc quiz étendu : type de réponse, réponse numérique correcte, groupe et
  ordre dans le groupe.

**Tests**
- 70 tests au total (+41 depuis la dernière tranche) : générateur `constant_function` (10),
  contrat d'architecture étendu automatiquement (2 générateurs), `answer_checking` (11),
  `QuizConfig` étendu (5 nouveaux), séparation public/complet de `exercise_blocks` (2
  nouveaux).

**Décisions volontairement reportées** (voir `docs/mb32-uaa1.md`, limites restantes) : pas
de modèle `Chapter` dédié, pas d'Alembic, progression toujours au niveau de l'UAA entière —
aucune de ces décisions ne bloque le contenu actuel ni n'introduit de dette qui casserait
une évolution future.
