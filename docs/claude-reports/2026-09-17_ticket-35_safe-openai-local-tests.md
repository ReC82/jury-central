# Ticket #35 — Tests manuels : empêcher le fallback involontaire sur la vraie OPENAI_API_KEY

**Date** : 2026-09-17
**Branche** : `feature/35-safe-openai-local-tests`

---

## 1. Cause exacte

`app/config.py::Settings` est une `pydantic_settings.BaseSettings` configurée avec
`model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), extra="ignore")`.
Pour tout champ (dont `openai_api_key`), pydantic-settings résout la valeur dans cet
ordre de priorité : variable déjà présente dans `os.environ` du process **>** valeur lue
dans le fichier `.env` **>** valeur par défaut de la classe (`""` pour
`openai_api_key`).

Sur ce serveur, `/srv/jury-central/.env` contient la vraie clé OpenAI depuis la
validation réelle du ticket #31. Le service staging réel fonctionne correctement car
l'unité systemd (`EnvironmentFile=/srv/jury-central/.env`) exporte chaque ligne de `.env`
comme une vraie variable d'environnement du process **avant** le démarrage d'uvicorn —
`OPENAI_API_KEY` est donc déjà dans `os.environ` quand `Settings()` s'exécute, et
pydantic-settings n'a jamais besoin de retomber sur la lecture de `.env` lui-même.

**Le risque concerne uniquement un process lancé manuellement/ad hoc**, sans passer par
systemd — typiquement une commande `uvicorn app.main:app ...` tapée directement pour une
vérification manuelle. Si cette commande n'exporte pas explicitement
`OPENAI_API_KEY=""` (ou une valeur), `os.environ` ne contient pas la variable au moment
où `app.config` est importé, et pydantic-settings lit alors silencieusement la vraie
valeur depuis `.env` — sans qu'aucun message ne le signale. C'est exactement ce qui s'est
produit pendant le ticket #29 : une vérification manuelle a surchargé
`DATABASE_URL`/`ADMIN_USERNAME`/`ADMIN_PASSWORD`/`SECRET_KEY` mais pas
`OPENAI_API_KEY`, provoquant un appel OpenAI réel non intentionnel (documenté dans
`docs/claude-reports/2026-09-17_ticket-29_mc01-practice-interactive.md`, § 10 — aucun
secret exposé, aucune donnée corrompue).

---

## 2. Scénario de reproduction (sans jamais lire ni afficher la vraie clé)

Reproduit dans `tests/test_ticket35_safe_openai_config.py::
test_root_cause_reproduced_without_the_guard`, avec un fichier `.env` **temporaire**
contenant une valeur explicitement factice (`sk-fake-test-key-never-real-do-not-use`,
jamais la vraie clé) :

```python
monkeypatch.delenv("OPENAI_API_KEY", raising=False)   # process sans la variable
env_file = _write_fake_env_file(tmp_path)              # .env temporaire, clé FACTICE

settings = Settings(_env_file=env_file)

assert settings.openai_api_key == _FAKE_ENV_FILE_KEY   # fallback silencieux confirmé
```

Ce test démontre le mécanisme exact du risque (repli sur `.env`) sans jamais toucher au
vrai `/srv/jury-central/.env` ni en lire le contenu réel — seul un fichier temporaire
jetable, avec une valeur inventée, est utilisé.

---

## 3. Solution retenue

**Nouveau module `app/safe_local_server.py`**, exposé comme commande installée
`safe-local-server` (`pyproject.toml`, `[project.scripts]`, même mécanisme que
`seed-db`/`reset-db`) :

- Force `os.environ["OPENAI_API_KEY"] = ""` **au niveau module**, donc dès l'import de
  `app.safe_local_server`, donc avant tout import de `app.config`/`app.main` par ce même
  process — reprend explicitement le mécanisme déjà en place et documenté dans
  `tests/conftest.py` (commentaire « Force-cleared (pas setdefault) »), dont l'efficacité
  est éprouvée depuis le ticket #31.
- Lance ensuite `uvicorn.run("app.main:app", ...)` (import de `app.main` différé, réalisé
  par uvicorn lui-même après la garde) sur un port dédié (`8099` par défaut, distinct du
  port staging `8100`), avec une bannière explicite rappelant que le mode est sûr.
- `--reload` reste disponible : le rechargement automatique d'uvicorn relance le process
  applicatif comme sous-process, qui hérite de `os.environ` (donc de la garde) — pas de
  fuite possible via ce mécanisme.

**Aucune modification de `app/config.py`** : la garde agit uniquement sur
`os.environ`, en amont, jamais sur la classe `Settings` elle-même — le comportement de
`Settings` (y compris pour le service staging réel) reste inchangé à l'octet près.

### Alternatives évaluées et écartées

- **`APP_ENV=test` / gate conditionnel dans `Settings`** : `.env.example` contient déjà
  un champ `APP_ENV` (local/dev/staging/prod), mais il n'est lu nulle part dans le code
  (`grep -rn "APP_ENV" app/` : aucun résultat) — c'est un champ mort. Le faire piloter le
  chargement de `OPENAI_API_KEY` déplacerait simplement le problème : `APP_ENV`
  lui-même devrait alors provenir uniquement de `os.environ` (jamais de `.env`) pour ne
  pas réintroduire la même ambiguïté — ce qui revient exactement à exiger qu'une
  variable soit positionnée explicitement dans le process, sans rien apporter de plus
  qu'une variable directement dédiée. Solution écartée : ajoute un niveau d'indirection
  sans bénéfice réel.
- **`AI_ALLOW_REAL_REQUESTS=false`** : nécessiterait un nouveau champ dans `Settings` et
  une vérification supplémentaire dans `app/ai/factory.py::get_ai_provider()` (ou
  `OpenAIProvider`), donc une modification du chemin de code partagé avec le service
  staging réel — risque plus élevé pour un bénéfice identique à « ne pas avoir de clé du
  tout », qui est déjà le comportement testé et sûr de `AINotConfiguredError`. Solution
  écartée au profit de la neutralisation directe, la plus simple possible.

Solution retenue : **neutraliser directement la seule variable réellement sensible
(`OPENAI_API_KEY`), au plus tôt, de façon inconditionnelle**, dans une commande dédiée —
aucune nouvelle option de configuration, aucune branche conditionnelle dans le code
applicatif partagé avec staging.

---

## 4. Pourquoi le staging réel continue de fonctionner sans changement

`jury-central.service` (systemd) définit `EnvironmentFile=/srv/jury-central/.env` (voir
`docs/deployment_staging.md` § 1.2) : chaque ligne de `.env`, dont `OPENAI_API_KEY`,
devient une vraie variable d'environnement du process **avant** que uvicorn ne démarre et
donc avant que `app.config.Settings()` ne s'exécute. `os.environ` contient déjà la vraie
clé à ce moment — pydantic-settings ne lit alors jamais `.env` lui-même pour ce champ
(une variable de process a toujours priorité). Confirmé par
`test_staging_style_explicit_env_var_still_loads_correctly` : avec `OPENAI_API_KEY`
positionnée explicitement dans le process (simulant `EnvironmentFile`), la valeur du
process l'emporte toujours sur celle d'un `.env` différent.

`scripts/deploy_staging.sh` n'a pas été modifié : il ne touche jamais à `.env`, ne lance
jamais `safe-local-server`, et redémarre uniquement `jury-central.service` via systemd —
son fonctionnement est strictement inchangé par ce ticket.

---

## 5. Commande sûre pour les validations manuelles

```bash
safe-local-server                     # http://127.0.0.1:8099
safe-local-server --port 8123 --reload
```

Documentée dans `docs/development.md` (nouvelle section « Serveur de test local sûr »,
remplaçant l'ancienne suggestion « Lancer un second serveur : `uvicorn app.main:app
--port 8001` » qui ne mettait pas en garde contre ce risque) et dans
`docs/ai_exercise_engine.md` (§ Tests).

---

## 6. Tests ajoutés

`tests/test_ticket35_safe_openai_config.py` (8 tests, aucun appel réseau réel, aucune
lecture/écriture de la vraie clé — uniquement des `.env` temporaires à valeur factice) :

1. `test_pytest_never_loads_a_real_key_from_env` — confirme explicitement que la garde
   déjà en place dans `tests/conftest.py` est active pendant toute la suite pytest.
2. `test_root_cause_reproduced_without_the_guard` — reproduit le mécanisme exact du
   risque (voir § 2).
3. `test_safe_local_guard_prevents_fallback_to_env_file` — le mode local sûr empêche
   effectivement ce fallback, même avec une variable déjà positionnée sur une valeur
   factice auparavant et un `.env` temporaire présent.
4. `test_staging_style_explicit_env_var_still_loads_correctly` — confirme que la
   configuration staging normale (variable de process déjà positionnée) continue de
   fonctionner sans changement (voir § 4).
5. `test_safe_local_server_module_import_has_no_side_effect_beyond_the_guard` — importer
   le module ne démarre jamais de serveur ni n'importe `app.main` au niveau module
   (vérifié par inspection du code source, pas seulement par confiance).
6. `test_no_real_network_call_possible_with_empty_key` — avec la garde appliquée, toute
   tentative de correction/génération IA lève `AINotConfiguredError` avant toute I/O
   réseau.
7. `test_not_configured_error_never_contains_a_secret` — le message d'erreur ne contient
   jamais aucune des valeurs factices utilisées dans ces tests, ni le préfixe `sk-`.
8. `test_safe_local_server_cli_entry_point_is_registered` — la commande est bien
   déclarée dans `pyproject.toml`.

Aucun test de ce ticket ne lit, n'affiche ni ne dépend du vrai `/srv/jury-central/.env` —
tous utilisent des fichiers temporaires (`tmp_path`) avec des valeurs explicitement
inventées.

---

## 7. Résultat pytest

```
439 passed, 2 warnings in 18.14s
```

(431 avant ce ticket + 8 nouveaux). Les 2 warnings sont préexistants (dépréciations
`httpx`/`anyio`), sans lien avec ce ticket.

---

## 8. Résultat Ruff

```
Found 36 errors.
```

Identique, fichier par fichier et règle par règle, à la base `develop` (comparé via un
worktree isolé, méthodologie déjà utilisée aux tickets précédents). **0 nouvelle erreur.**
Un ajustement mineur a été nécessaire pendant le développement : les `# noqa: E402`
initialement ajoutés à `app/safe_local_server.py` (par analogie avec
`tests/conftest.py`) ont été retirés — la règle `E402` n'est pas activée dans la
configuration Ruff de ce projet (sélection par défaut), donc ces directives étaient
elles-mêmes signalées comme inutiles (`RUF100`). Ce même signalement existe déjà, de façon
préexistante, sur les `# noqa: E402` de `tests/conftest.py` (4 occurrences, non modifiées
ici — dette historique hors périmètre de ce ticket).

---

## 9. Fichiers modifiés

- `app/safe_local_server.py` (nouveau) — garde + commande `safe-local-server`.
- `pyproject.toml` — nouvel entry point `[project.scripts]`.
- `tests/test_ticket35_safe_openai_config.py` (nouveau) — 8 tests.
- `docs/development.md` — nouvelle section « Serveur de test local sûr », remplace la
  suggestion `uvicorn app.main:app --port 8001` par `safe-local-server`.
- `docs/ai_exercise_engine.md` — référence croisée dans la section Tests.

---

## 10. Limites

- La garde protège spécifiquement `OPENAI_API_KEY`, seule variable dont un repli
  silencieux sur `.env` a un effet observable côté réseau/coût (appel API réel). Les
  autres champs de `Settings` (`admin_username`, `secret_key`, etc.) n'ont pas cette
  propriété — un repli sur `.env` pour ces champs reproduit simplement la configuration
  staging normale, sans appel réseau ni coût, donc sans le même risque.
- `safe-local-server` protège les vérifications manuelles qui l'utilisent ; il ne peut
  pas empêcher une commande `uvicorn app.main:app` tapée directement sans cette garde —
  la protection est désormais disponible et documentée comme la voie recommandée
  (`docs/development.md`), mais reste, comme toute commande, contournable par une
  commande différente. Une garde strictement impossible à contourner nécessiterait de
  modifier `app/config.py` lui-même (écarté, voir § 3, pour ne pas toucher au chemin de
  code partagé avec le service staging réel dans le cadre de ce ticket).

---

## Statut

Implémentation, tests, documentation terminés. `pytest -q` : 439 passed. Ruff : 36
erreurs, 0 nouvelle. Aucun appel OpenAI réel effectué à aucun moment de ce ticket. Prêt
pour commit/push. **Aucun merge, aucun déploiement.**
