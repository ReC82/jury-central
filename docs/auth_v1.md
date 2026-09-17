# Jury Central — Authentification V1 (ticket #39)

Ce document décrit l'authentification utilisateur V1 : inscription, connexion,
déconnexion, session web, CSRF, rôles, et les routes désormais protégées. Il complète
`docs/architecture_v1_data_model.md` (modèle `User`, ticket #38) sans le remplacer.

---

# 1. Objectif et périmètre

Décision produit (ticket #39) : les cours restent consultables sans compte ;
S'entraîner et S'évaluer nécessitent désormais un compte. Ce ticket ajoute
l'authentification nécessaire à cette règle, **sans** :

- remplacer l'admin HTTP-session existant (`app/auth.py`, `app/admin.py`) — toujours en
  place, inchangé, testé non régressé (voir § 9) ;
- construire la vérification d'email ou la réinitialisation de mot de passe ;
- construire d'interface spécifique par rôle (teacher/admin/author sont reconnus par le
  modèle et les helpers, sans écran dédié — student reste la seule expérience utilisateur
  construite ici).

---

# 2. Audit préalable (résumé — détail dans le rapport de ticket)

- `app/auth.py` : `require_admin` compare des identifiants HTTP-form via
  `hmac.compare_digest` et pose `request.session["is_admin"]`. Session déjà gérée par
  `starlette.middleware.sessions.SessionMiddleware` (cookie signé, `itsdangerous`, déjà
  une dépendance du projet) — **réutilisée telle quelle** pour la session V1, jamais un
  second mécanisme de session.
- Aucun mécanisme CSRF n'existe nulle part dans le projet avant ce ticket (vérifié :
  aucune occurrence de « csrf » dans `app/`) — ce ticket introduit donc le **premier**
  mécanisme CSRF du projet, pas un second système concurrent (voir § 5).
- Aucune bibliothèque de hachage de mot de passe n'était installée — `argon2-cffi`
  ajoutée (voir § 4).
- `app/database.py::ensure_schema_migrations` gère déjà l'ajout additif de colonnes sur
  une table SQLite existante (pattern du ticket #22) — étendu ici pour `v1_users` (voir
  § 6).
- `app/v1/models.py::User` (ticket #38) portait déjà `email`/`display_name`/`role`/
  `plan`/`is_active` — complété par `password_hash`/`last_login_at` (§ 3).
- `app/templating.py` n'avait pas de `context_processors` — ajouté pour exposer
  `current_user`/`csrf_token` à toutes les pages sans modifier chaque route (§ 7).

---

# 3. Modèle (`app/v1/models.py::User`)

Deux colonnes ajoutées (migration additive, § 6) :

- `password_hash: str | None` — nullable au niveau base (permet la migration sans valeur
  factice), toujours renseigné par `register_user` (jamais un autre point d'entrée).
- `last_login_at: datetime | None` — mis à jour à chaque connexion réussie
  (`record_login`).

**Pas de colonne `email_normalized`** : `email` est stocké déjà normalisé
(minuscules, espaces retirés — `app.v1.auth.normalize_email`), donc une colonne séparée
aurait été redondante avec l'unique champ `email` déjà `unique=True`.

---

# 4. Mots de passe

`argon2-cffi` (nouvelle dépendance, `pyproject.toml`) — Argon2id, recommandation OWASP
actuelle pour le hachage de mot de passe, déjà utilisé par des frameworks matures
(Django la propose comme hasher recommandé). Aucun algorithme réimplémenté ici :
`app.v1.auth.hash_password`/`verify_password` délèguent entièrement à
`argon2.PasswordHasher`.

- Le sel est généré et encodé PAR la bibliothèque dans la chaîne de hachage retournée
  (`$argon2id$v=19$m=...,t=...,p=...$<sel>$<hash>`) — aucune colonne de sel séparée
  nécessaire.
- La vérification (`verify_password`) utilise la comparaison en temps constant intégrée
  à `argon2-cffi` — jamais un `==` sur des chaînes de hachage.
- `authenticate_user` applique un hachage factice (« défense de timing ») quand l'email
  n'existe pas ou que le compte n'a pas de mot de passe, pour que le temps de réponse ne
  distingue pas trivialement « email inconnu » de « mauvais mot de passe ».
- Longueur minimale : 8 caractères (`MIN_PASSWORD_LENGTH`) — aucune autre règle de
  complexité imposée (non demandée par le ticket, évite une politique arbitraire).

---

# 5. CSRF

Premier mécanisme CSRF du projet (voir § 2). Synchronizer token pattern classique,
appuyé sur la session déjà signée par `SessionMiddleware` :

- `get_or_create_csrf_token(request)` : lit `request.session["v1_csrf_token"]`, en crée
  un (`secrets.token_urlsafe(32)`) s'il est absent, toujours stocké côté serveur (dans la
  session signée) — jamais dérivable du cookie seul par un tiers.
- `validate_csrf_token(request, submitted_token)` : comparaison en temps constant
  (`secrets.compare_digest`).
- Exposé à **toutes** les pages via le context processor de `app/templating.py`
  (`csrf_token`), donc disponible pour le formulaire de déconnexion du nav (`base.html`)
  sans que chaque route ait à le poser explicitement.
- Appliqué à `/register`, `/login`, `/logout` (POST) : jeton invalide ou absent → 400 sur
  inscription/connexion (formulaire réaffiché avec message générique « Session expirée,
  réessaie. ») ; sur `/logout`, un jeton invalide fait échouer silencieusement la
  déconnexion (redirection identique, session conservée) plutôt que d'afficher une page
  d'erreur — choix délibéré : le pire cas (CSRF invalide sur logout) reste « rien ne se
  passe », jamais « l'utilisateur est déconnecté par une page tierce », qui est
  précisément le risque que la protection doit couvrir.
- **Non rétrofité** sur l'admin existant (`/admin/login`, `/admin/logout`) : hors
  périmètre de ce ticket (« ne remplace pas l'admin existant si ce n'est pas
  nécessaire ») — signalé comme limite (§ 11).

---

# 6. Session web

**Choix retenu : session signée côté cookie (option A), pas de persistance en base.**

Réutilise l'unique `SessionMiddleware` déjà enregistré dans `app/main.py` (cookie
`session`, signé HMAC via `itsdangerous`, `secret_key` déjà existant). Justification :

- L'admin l'utilise déjà avec succès depuis le début du projet — introduire une session
  persistée en base pour V1 aurait créé DEUX mécanismes de session concurrents dans la
  même application, exactement ce que le ticket demande d'éviter.
- V1 ne stocke qu'un entier (`v1_user_id`) et un jeton CSRF dans la session — pas de
  données volumineuses, pas de besoin d'invalidation centralisée (pas de fonctionnalité
  « déconnecter tous mes appareils » demandée par ce ticket).
- `QuestionnaireSession` (`app/v1/models.py`, ticket #38) est un concept métier
  totalement différent (progression dans un questionnaire) — jamais mélangé avec la
  session web, ni dans le nom, ni dans le stockage.

Protections effectives du cookie (`app/main.py`, `SessionMiddleware`) :

- **HttpOnly** : toujours actif (comportement par défaut de `SessionMiddleware`,
  jamais désactivé).
- **SameSite=Lax** : valeur par défaut de `SessionMiddleware`, conservée.
- **Secure** (HTTPS uniquement) : activé via `https_only=settings.app_env in
  ("staging", "prod")` — voir § 6.1.
- **Expiration** : 14 jours (`max_age` par défaut de `SessionMiddleware`, jamais changé
  par ce ticket — durée jugée raisonnable pour un compte élève, pas de exigence
  explicite du ticket demandant une valeur différente).
- **Régénération à la connexion** (`login_user`) : `request.session.clear()` avant de
  poser `v1_user_id` — limite la fixation de session (un jeton obtenu avant
  authentification, y compris son propre CSRF, ne reste pas valide après connexion).

## 6.1 `APP_ENV` et le drapeau `Secure`

Nouveau champ `Settings.app_env` (`app/config.py`), lu depuis `.env`/l'environnement,
défaut `"local"` (déjà le défaut documenté dans `.env.example` depuis l'origine du
projet, jusqu'ici jamais lu par le code). `app/main.py` calcule
`https_only=settings.app_env in ("staging", "prod")` pour l'unique `SessionMiddleware`
(partagé admin + V1).

**Incident détecté et corrigé pendant ce ticket** : le vrai `.env` de ce serveur porte
déjà `APP_ENV=staging` (réglage légitime pour le déploiement réel, indépendant de ce
ticket). `tests/conftest.py` ne forçait jusqu'ici que `OPENAI_API_KEY=""` — sans
protection équivalente pour `APP_ENV`, la suite de tests entière lisait silencieusement
cette valeur `staging` depuis le vrai `.env`, activant `https_only=True` : `TestClient`
n'utilisant jamais HTTPS, le cookie `Secure` posé après une première réponse n'était
alors plus jamais renvoyé par le client sur la requête suivante, cassant silencieusement
**toute** connexion (admin ET V1) dès le deuxième appel HTTP d'un test. Corrigé en
ajoutant `os.environ["APP_ENV"] = "local"` dans `tests/conftest.py`, même discipline que
`OPENAI_API_KEY` (voir son commentaire « Force-cleared »). `app/safe_local_server.py`
(ticket #35) a reçu la même protection pour les vérifications manuelles locales.

---

# 7. `current_user` / `require_user` / `require_role`

`app/v1/auth.py` :

- `get_current_user(request, db) -> User | None` : lit `request.session["v1_user_id"]`,
  recharge l'utilisateur, `None` si absent/inconnu/inactif.
- `current_user_dependency` : version FastAPI de `get_current_user`, pour une route qui
  s'adapte sans exiger de compte (utilisée par `/register`, `/login` pour rediriger un
  utilisateur déjà connecté).
- `require_user` : dépendance FastAPI pour une **page HTML** — redirige (303) vers
  `/login?next=<chemin demandé>` si personne n'est connecté (même schéma que
  `app.auth.require_admin`). `next` est construit depuis la requête elle-même, jamais une
  entrée utilisateur à ce stade — sûr par construction.
- `require_user_api` : équivalent pour une **route API JSON**
  (`/practice/api/ai/generate`, `/practice/api/ai/correct`,
  `/practice/api/editorial/{block_id}/verify`) — lève un 401 JSON plutôt qu'une
  redirection HTML, qu'un appel `fetch()` suivrait silencieusement et interpréterait à
  tort comme une réponse JSON.
- `require_role(*roles)` : fabrique une dépendance exigeant un rôle précis. Aucune route
  ne l'utilise encore (aucune interface teacher/admin/author construite par ce ticket) —
  couverte par des tests directs (`tests/test_ticket39_v1_auth.py`) appelant la
  dépendance sans passer par une route HTTP.

`current_user` est également exposé à **tous** les templates via un context processor
(`app/templating.py::_inject_current_user`) — `base.html` adapte sa navigation
(Connexion/Créer un compte vs display_name/Mon compte/Déconnexion) sans qu'aucune route
existante n'ait eu besoin d'être modifiée pour passer ce contexte.

---

# 8. Rôles et plans

`UserRole` (student/teacher/admin/author) et `UserPlan` (free/premium/internal) restent
des enums Python (`app/v1/models.py`, ticket #38, inchangés par ce ticket) — voir
`docs/architecture_v1_data_model.md`, § 9, pour la justification de ce choix plutôt que
des tables de référence séparées.

`current_user.plan` est déjà exposé au backend partout où `current_user`/`require_user`
sont utilisés — aucun mécanisme de quota réel n'est construit ici (ticket #43/#46), mais
la donnée est disponible dès maintenant pour ces tickets, sans travail supplémentaire.

---

# 9. Routes

## Nouvelles (`app/v1/routes.py`, montées sans préfixe dans `app/main.py`)

| Route | Méthode | Rôle |
|---|---|---|
| `/register` | GET/POST | Inscription (email, mot de passe, confirmation, display_name optionnel). Valeurs automatiques : role=student, plan=free, is_active=true. Connecte automatiquement après succès. |
| `/login` | GET/POST | Connexion. `next` (query en GET, champ caché en POST) validé par `safe_next_path` — jamais de redirection externe. Message générique en cas d'échec (mauvais mot de passe, email inconnu, ou compte inactif : même réponse). |
| `/logout` | POST | Déconnexion (CSRF requis). Pas de variante GET (évite d'affaiblir la protection CSRF avec une action déclenchable par un simple lien/image). |
| `/account` | GET | Optionnel (construit) : affiche email/display_name/rôle/plan, bouton de déconnexion. Protégée par `require_user`. |

## Existantes, désormais protégées (ticket #39)

| Route | Dépendance ajoutée | Pourquoi |
|---|---|---|
| `GET /uaa/{slug}/practice` | `require_user` | Route générique (toutes matières) de l'espace S'entraîner. |
| `GET /uaa/{slug}/exam` | `require_user` | Route générique de l'espace S'évaluer. |
| `POST /practice/api/ai/generate` | `require_user_api` | Génère un exercice dans l'espace PRACTICE. |
| `POST /practice/api/ai/correct` | `require_user_api` | Corrige une réponse IA dans l'espace PRACTICE. |
| `POST /practice/api/editorial/{block_id}/verify` | `require_user_api` | Corrige une réponse à un bloc `editorial_exercise` — tous les blocs actuellement seedés (MC01/MC02/MC03) sont en espace PRACTICE (audit du ticket, voir rapport). |

`GET /uaa/{slug}` (espace COURS) reste **public**, inchangé — vérifie la structure
générique (`app/main.py::_space_blocks`, filtrage par `BlockSpace`), pas une route
spécifique à un cours.

## Explicitement NON protégées (legacy/démo, hors expérience V1)

`/practice/equations`, `/practice/api/generate`, `/practice/api/verify`,
`/practice/api/reveal`, `/practice/api/value-table/verify`,
`/practice/api/quiz/{block_id}/verify` — aucun bloc PRACTICE/EXAM actuellement seedé
n'utilise ces mécanismes (audit exhaustif de `app/seed.py`, voir rapport de ticket) : ce
sont des démonstrations/fonctionnalités legacy indépendantes de la hiérarchie
Subject/Module/UAA/LessonBlock, hors périmètre de « l'expérience S'entraîner/S'évaluer »
que ce ticket protège. Les routes admin (`/admin/*`) restent protégées par leur propre
mécanisme (`require_admin`), inchangé.

---

# 10. Migration (`app/database.py::ensure_schema_migrations`)

`v1_users` peut déjà exister (créée par le ticket #38, sans `password_hash` ni
`last_login_at`). Étend le même mécanisme déjà utilisé pour `lesson_blocks.space`
(ticket #22) : `PRAGMA table_info` vérifie la présence de chaque colonne avant un
`ALTER TABLE ... ADD COLUMN` — idempotent, strictement additif, aucun `reset-db`.
Refactorisé en un helper générique `_add_column_if_missing(table, column, ddl_type)`,
réutilisé pour les 3 colonnes actuellement gérées (`lesson_blocks.space`,
`v1_users.password_hash`, `v1_users.last_login_at`).

---

# 11. Limites V1

- Pas de vérification d'email, pas de réinitialisation de mot de passe (ticket suivant
  si nécessaire).
- Pas de connexion sociale (Google, etc.).
- CSRF non rétrofité sur l'admin existant (`/admin/login`, `/admin/logout`) — reste sans
  protection CSRF, comme avant ce ticket ; seules les nouvelles routes V1 en bénéficient.
- Session cookie signée uniquement — pas de table de sessions actives, donc pas de
  fonctionnalité « déconnecter tous mes appareils » ni de révocation immédiate d'une
  session déjà émise (la seule façon de révoquer est de changer `secret_key`, ce qui
  invaliderait TOUTES les sessions, admin comprise).
- Pas d'interface teacher/admin/author : rôles reconnus par le modèle et par
  `require_role`, aucun écran ne les utilise encore.
- Pas de quota réel associé au `plan` (ticket #43/#46).
- `https_only` reste un réglage global (`APP_ENV`), pas par requête — cohérent puisque
  ce serveur est systématiquement servi en HTTPS en dehors du développement local.
