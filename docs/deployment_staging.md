# Jury Central - Déploiement staging

Ce document décrit l'environnement staging existant et la procédure de mise à jour
contrôlée à partir de `develop`. Il complète `docs/git_workflow.md` (qui s'arrête au push
de la branche) pour la partie qui suit la review/merge par ChatGPT.

Workflow complet (voir `docs/PROJECT_RULES.md` § 6 et § 8) :

```
ticket GitHub
→ branche depuis develop
→ développement Claude (commit + push)
→ review / PR par ChatGPT
→ merge dans develop par ChatGPT
→ déploiement staging
→ validation visuelle/fonctionnelle
→ ticket fermé
```

**Claude ne déclenche jamais lui-même une mise à jour de staging.** Le script décrit
ci-dessous est prévu pour être exécuté manuellement (ou par une automatisation future),
après merge, sur demande explicite.

---

# 1. Architecture staging actuelle

| Élément | Valeur |
|---|---|
| URL publique | `https://jury-central.lodylands.com` |
| Serveur | instance AWS partagée |
| Dépôt déployé | `/srv/jury-central` |
| Branche déployée | `develop` (validée par ChatGPT) |
| Application | FastAPI, servie par Uvicorn |
| Écoute locale de l'application | `127.0.0.1:8100` |
| Reverse proxy | nginx (config dédiée à ce domaine, hors dépôt) |
| HTTPS | Let's Encrypt via Certbot (renouvellement géré au niveau serveur, hors dépôt) |
| Service | `jury-central.service` (systemd) |
| Environnement | `/srv/jury-central/.env` — **jamais dans Git** |
| Base de données | `/srv/jury-central/jury_central.db` (SQLite) — **jamais dans Git** |
| Environnement virtuel | `/srv/jury-central/.venv` — créé une fois manuellement, réutilisé ensuite |

L'installation initiale (utilisateur système, unité systemd, virtualhost nginx, certificat
Certbot) a été faite manuellement et n'est pas reproduite par ce dépôt. Ce document décrit
l'état existant pour le diagnostic et la mise à jour ; il ne fournit **pas** de script
d'installation initiale.

## 1.1 nginx (config active, hors dépôt)

La configuration nginx active vit dans `/etc/nginx/` sur le serveur (probablement
`/etc/nginx/sites-available/jury-central.lodylands.com` ou équivalent, activée dans
`sites-enabled/`) et n'est **pas** versionnée dans ce dépôt — voir § 5 pour la raison.
Rôle : terminer le TLS (certificat Let's Encrypt) et transmettre les requêtes en HTTP vers
`127.0.0.1:8100`.

## 1.2 systemd (unité active, hors dépôt)

`jury-central.service` est défini sur le serveur (probablement
`/etc/systemd/system/jury-central.service`), pas dans ce dépôt. Il lance vraisemblablement
`uvicorn app.main:app --host 127.0.0.1 --port 8100` avec `WorkingDirectory=/srv/jury-central`
et l'environnement chargé depuis `/srv/jury-central/.env` (à confirmer sur le serveur, voir
§ 4 pour la commande d'inspection).

## 1.3 Certbot

Le renouvellement du certificat Let's Encrypt est géré par Certbot au niveau du serveur
(généralement via un timer systemd `certbot.timer`, indépendant de ce dépôt). Ce ticket ne
touche pas à Certbot.

---

# 2. Ce que le déploiement staging fait — et ne fait jamais

## Fait (voir § 3, script `scripts/deploy_staging.sh`)

- Vérifie que la branche locale est bien `develop`.
- Vérifie que le working tree est propre.
- Synchronise avec `origin/develop` en fast-forward uniquement (jamais de reset forcé).
- Installe/mets à jour les dépendances dans le `.venv` existant.
- Exécute `pytest -q` et s'arrête si un test échoue.
- Redémarre `jury-central.service` seulement après succès des étapes précédentes.
- Vérifie que le service est `active` et que `http://127.0.0.1:8100/health` répond.

## Ne fait jamais

- Ne recrée, ne réinitialise et ne seed **jamais** `jury_central.db` (`seed-db`/`reset-db`
  ne font pas partie d'un déploiement — voir § 6).
- Ne modifie ni n'installe la configuration nginx, l'unité systemd, ou Certbot.
- Ne lit, n'affiche, ne modifie ni ne commit le contenu de `.env`.
- Ne force jamais un merge/reset en cas de divergence avec `origin/develop` — il échoue et
  demande une résolution manuelle.
- Ne déploie jamais une branche autre que `develop`.

---

# 3. Script de déploiement — `scripts/deploy_staging.sh`

## 3.1 Fonctionnement exact

Le script s'exécute depuis la racine du dépôt de déploiement (`/srv/jury-central`) et
avance étape par étape, chaque étape devant réussir avant de passer à la suivante ; le
moindre échec arrête immédiatement le script (`set -euo pipefail` + vérifications
explicites) sans redémarrer le service :

1. Vérifie que `/srv/jury-central` est bien un dépôt git.
2. Vérifie que la branche courante est `develop` — sinon, arrêt immédiat, aucune
   modification.
3. Vérifie que `git status --porcelain` est vide — sinon, arrêt immédiat (working tree
   sale : commit, stash ou nettoyage manuel requis avant de relancer).
4. `git fetch origin develop` puis `git merge --ff-only origin/develop` — en cas
   d'historique divergent (fast-forward impossible), le script échoue plutôt que de forcer
   quoi que ce soit.
5. Vérifie que `.venv/bin/python` existe (le `.venv` n'est jamais créé automatiquement par
   ce script).
6. Vérifie que `.env` existe **sans jamais lire ni afficher son contenu**.
7. `.venv/bin/pip install -e ".[dev]"` pour mettre à jour les dépendances dans le `.venv`
   existant.
8. `.venv/bin/python -m pytest -q` — si la suite échoue, arrêt immédiat, **le service
   n'est pas redémarré**.
9. Rappelle explicitement (log) que `jury_central.db` n'est pas touchée.
10. `sudo systemctl restart jury-central.service`.
11. Vérifie, avec plusieurs tentatives espacées de 2 secondes (jusqu'à 10), que le service
    est bien `active` (`systemctl is-active`).
12. Vérifie, avec la même logique de tentatives, que `http://127.0.0.1:8100/health` répond
    (`curl --fail`).
13. En cas de succès complet, affiche le SHA court du commit déployé.

Chaque échec affiche un message explicite sur stderr et indique la commande de diagnostic
pertinente (`journalctl -u jury-central.service -n 50 --no-pager`), puis quitte avec un
code de sortie non nul.

## 3.2 Usage

```bash
cd /srv/jury-central
scripts/deploy_staging.sh
```

Prérequis sur le serveur, à mettre en place une seule fois manuellement (hors périmètre de
ce script) :
- `.venv` déjà créé (`python -m venv .venv && .venv/bin/pip install -e ".[dev]"`) ;
- `.env` déjà déployé, hors Git, avec les bonnes valeurs ;
- le compte qui exécute le script autorisé à faire
  `sudo systemctl restart jury-central.service` sans mot de passe (ou exécution du script
  par un compte déjà privilégié) ;
- `jury_central.db` déjà présent (ou absent volontairement — l'application crée le schéma
  au démarrage via `Base.metadata.create_all`, sans insérer aucune donnée ; voir § 6).

## 3.3 Ce que le script ne fait pas encore (hors périmètre de ce ticket)

- Pas de rollback automatique en cas d'échec après redémarrage (le service reste dans
  l'état où il était avant le script tant que le redémarrage n'a pas eu lieu ; un échec
  après redémarrage nécessite une intervention manuelle).
- Pas d'installation initiale de l'environnement (venv, `.env`, nginx, systemd, Certbot) :
  ce script suppose un staging déjà opérationnel, conformément à l'énoncé du ticket #6.
- Pas d'exécution automatique par une CI/CD : il est prévu pour un lancement manuel après
  validation par ChatGPT, jusqu'à nouvelle décision produit.

---

# 4. Commandes de diagnostic

```bash
# État du service
sudo systemctl status jury-central.service

# Derniers logs de l'application
sudo journalctl -u jury-central.service -n 100 --no-pager

# Suivre les logs en direct
sudo journalctl -u jury-central.service -f

# Vérifier que l'application répond en local (contourne nginx)
curl -i http://127.0.0.1:8100/health

# Vérifier la définition active du service (lecture seule, ne pas éditer sans ticket dédié)
systemctl cat jury-central.service

# Vérifier la configuration nginx active (lecture seule)
sudo nginx -T | less

# État des certificats Let's Encrypt
sudo certbot certificates
```

Ces commandes sont fournies pour le diagnostic. **Modifier nginx, Certbot ou l'unité
systemd nécessite un ticket dédié et une instruction explicite** (voir
`docs/PROJECT_RULES.md` § 8 et § 16).

---

# 5. Pourquoi nginx/systemd/Certbot ne sont pas versionnés ici

Le ticket #6 demande explicitement de ne pas versionner la configuration nginx active de
`/etc`, ni le fichier systemd actif, comme s'ils étaient automatiquement installés par ce
dépôt — pour éviter qu'une future automatisation écrase silencieusement une configuration
serveur modifiée manuellement, en dehors de tout ticket. Si une installation reproductible
(fichiers d'exemple pour nginx/systemd) devient nécessaire, elle fera l'objet d'un ticket
dédié et explicite plutôt que d'un ajout silencieux ici.

---

# 6. `seed-db` / `reset-db` ne font jamais partie d'un déploiement

`scripts/deploy_staging.sh` ne seed ni ne reset jamais `jury_central.db`, et ne l'appelle à
aucun moment. Rappel (voir aussi `docs/development.md`) :

- `seed-db` (`python -m app.seed` / commande `seed-db`) insère des données de
  démonstration/réelles de façon additive — il ne supprime jamais de contenu existant.
- `reset-db` (commande `reset-db`) **supprime le fichier `jury_central.db`** avant de
  relancer `seed-db` — action destructive.

Sur staging, l'exécution de l'une ou l'autre commande est une **décision explicite et
séparée**, jamais un effet de bord d'un déploiement de code. Le schéma des tables est créé
automatiquement au démarrage de l'application (`Base.metadata.create_all`, voir
`app/main.py`) si les tables n'existent pas encore — cela ne touche pas aux données déjà
présentes.

---

# 7. Sécurité — `.env` et secrets

- `.env` ne doit **jamais** être commité (déjà exclu via `.gitignore`).
- `scripts/deploy_staging.sh` vérifie uniquement que `.env` **existe** ; il n'en lit, n'en
  affiche et n'en modifie jamais le contenu.
- Aucun certificat Let's Encrypt, aucune clé, aucun identifiant ne doit être ajouté à ce
  dépôt à quelque étape que ce soit.
