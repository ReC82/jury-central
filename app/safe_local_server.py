"""Lance un serveur local jetable pour des vérifications manuelles, sans jamais pouvoir
utiliser la vraie clé OpenAI de `.env`.

Ticket #35 : pendant le développement du ticket #29, un serveur local temporaire lancé
directement via `uvicorn app.main:app` sur ce même serveur (qui héberge aussi staging) a
hérité de la vraie `OPENAI_API_KEY` de `/srv/jury-central/.env`, simplement parce
qu'aucune variable d'environnement `OPENAI_API_KEY` n'était positionnée dans le process :
`app.config.Settings` (pydantic-settings) retombe silencieusement sur la lecture de
`.env` dans ce cas — voir `app.config.Settings.model_config` (`env_file=...`). Un appel
OpenAI réel et non intentionnel en a résulté (aucun secret exposé ; incident documenté
dans `docs/claude-reports/2026-09-17_ticket-29_mc01-practice-interactive.md`).

Ce module force explicitement `OPENAI_API_KEY=""` dans l'environnement du process, dès
son import — donc avant tout import de `app.config`/`app.main` par ce même process —
reprenant exactement le mécanisme déjà utilisé et documenté dans `tests/conftest.py`
(voir son commentaire « Force-cleared (pas setdefault) »). `Settings` n'est instanciée
qu'une seule fois, au chargement de `app.config` (singleton `settings`) : une variable
d'environnement déjà présente dans `os.environ` a toujours priorité sur `.env` en
pydantic-settings — forcer la variable AVANT cet import est donc la seule garantie
efficace, un `os.environ.setdefault(...)` ne suffirait pas si la variable est déjà
positionnée autrement, et ne rien faire laisse `.env` être lu silencieusement dès que la
variable est simplement absente.

Aucune ambiguïté : dans ce mode, `OPENAI_API_KEY` vaut toujours `""`, quel que soit le
contenu de `.env` — la génération/correction IA répond systématiquement « non
configurée » (503, `AINotConfiguredError`), sans jamais pouvoir déclencher un appel
réseau vers OpenAI (voir `app.ai.openai_provider.OpenAIProvider.__init__`, qui lève
l'exception avant toute I/O dès que la clé est vide).

Le service staging réel (lancé par systemd, voir `docs/deployment_staging.md`) n'est
jamais concerné par ce risque et continue de fonctionner normalement sans ce module :
`EnvironmentFile=/srv/jury-central/.env` dans l'unité systemd positionne
`OPENAI_API_KEY` comme une vraie variable d'environnement du process AVANT même le
démarrage d'uvicorn — cette valeur existe donc déjà dans `os.environ` quand
`app.config.Settings()` s'exécute, si bien que pydantic-settings ne retombe jamais sur la
lecture de `.env` pour ce champ dans ce cas. Seul un lancement manuel/ad hoc, sans cette
variable déjà positionnée dans le process, est concerné par le risque que ce module
élimine.

Usage :
    safe-local-server [--host 127.0.0.1] [--port 8099] [--reload]

N'affiche, ne journalise et ne lit jamais la vraie valeur de `OPENAI_API_KEY`.
"""

import os


def force_safe_local_environment() -> None:
    """Empêche tout repli implicite sur la vraie clé OpenAI de `.env`, et sur le vrai
    `APP_ENV` de `.env` (ticket #39 : `.env` porte `APP_ENV=staging` sur ce serveur, ce
    qui active `https_only` sur le cookie de session — un navigateur/outil de test en
    HTTP local ne renverrait alors jamais ce cookie, rendant impossible toute vérification
    manuelle de connexion/session sur ce mode local).

    Doit être appelée avant tout import de `app.config`/`app.main` dans ce process : voir
    la docstring du module pour pourquoi un simple `setdefault` ne suffit pas.
    """
    os.environ["OPENAI_API_KEY"] = ""
    os.environ["APP_ENV"] = "local"


force_safe_local_environment()

import argparse

import uvicorn

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8099


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="safe-local-server",
        description=(
            "Lance app.main:app pour des vérifications manuelles, avec OPENAI_API_KEY "
            "forcée à vide : la génération/correction IA répond systématiquement "
            "'non configurée' (503), sans jamais pouvoir appeler l'API OpenAI réelle, "
            "quel que soit le contenu de .env."
        ),
    )
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"défaut : {DEFAULT_HOST}")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"défaut : {DEFAULT_PORT}")
    parser.add_argument(
        "--reload", action="store_true", help="rechargement automatique (développement)"
    )
    args = parser.parse_args()

    print("=" * 78)
    print("MODE TEST LOCAL SÛR (ticket #35)")
    print("OPENAI_API_KEY forcée à vide pour ce process : aucun appel OpenAI réel n'est")
    print("possible, quel que soit le contenu de .env.")
    print("APP_ENV forcée à 'local' : le cookie de session n'est pas marqué Secure,")
    print("utilisable normalement en HTTP local (ticket #39).")
    print(f"Écoute sur http://{args.host}:{args.port}")
    print("=" * 78)

    uvicorn.run("app.main:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
