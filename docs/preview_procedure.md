# Jury Central — Procédure de prévisualisation isolée

Complète `docs/PROJECT_RULES.md` § 18. Décrit comment mettre en place un accès de
prévisualisation fonctionnel (PC et téléphone) pour une branche de ticket, sans jamais
modifier le site public (`jury-central.service`, `/etc/nginx/sites-available/jury-central`,
`jury_central.db`).

---

# 1. Principe

Trois ingrédients, toujours séparés du site public :

1. **Code** : exécuté depuis un `git worktree` dédié (jamais `/srv/jury-central`, dont le
   `WorkingDirectory` est partagé avec le service live — voir
   `docs/claude-reports/2026-10-01_incident-502.md` § 7 pour le risque concret que cela a
   représenté une fois). `git worktree add <chemin> <branche-du-ticket>` depuis
   `/srv/jury-central`, après avoir remis ce dernier sur `develop`.
2. **Base de données** : fichier SQLite dédié, jamais nommé comme la base réelle, jamais
   partagé avec les tests automatisés. `seed()` uniquement — aucune donnée réelle.
3. **Processus** : un `uvicorn` et, si la fonctionnalité en a besoin (sessions
   V1/correction asynchrone), un `python -m app.v1.correction_worker` séparés, lancés avec
   les mêmes variables d'environnement explicites (`DATABASE_URL`, `APP_ENV=local`,
   `OPENAI_API_KEY`, `ADMIN_USERNAME`/`ADMIN_PASSWORD`, `SECRET_KEY`) pointant vers la base
   de démonstration — jamais les processus `jury-central.service`/
   `jury-central-correction-worker.service` existants.

---

# 2. Accès réseau — options, de la plus simple à la plus robuste

Le code applicatif écoute toujours en local (`127.0.0.1:<port>`), jamais exposé
directement. L'exposition passe par nginx, qui est déjà le reverse proxy de tous les sites
de ce serveur.

## Option A — port TLS dédié sur un nom de domaine déjà certifié (rapide, mais dépend du pare-feu cloud)

Ajouter un **nouveau fichier** `/etc/nginx/sites-available/<nom>-preview` (jamais modifier
le fichier du site existant), qui réutilise le certificat Let's Encrypt déjà valide du
domaine concerné sur un **nouveau port** :

```nginx
server {
    listen 8443 ssl;
    listen [::]:8443 ssl;
    server_name jury-central.lodylands.com;

    ssl_certificate     /etc/letsencrypt/live/jury-central.lodylands.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/jury-central.lodylands.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    auth_basic "Aperçu privé";
    auth_basic_user_file /etc/nginx/.htpasswd-<nom>-preview;

    location / {
        proxy_pass http://127.0.0.1:<port-backend>;
        proxy_http_version 1.1;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -sf /etc/nginx/sites-available/<nom>-preview /etc/nginx/sites-enabled/<nom>-preview
sudo nginx -t && sudo systemctl reload nginx   # reload, jamais restart — aucun impact sur le site public
```

`auth_basic` (même pattern que `kestrel.lodylands.com`, voir sa configuration) rend l'accès
privé — identifiants générés via `sudo htpasswd -bc /etc/nginx/.htpasswd-<nom>-preview <user> <pass>`.

**Jamais de préfixe de chemin** (`location /preview/`) sur le site public existant pour ce
besoin : cette application construit ses redirections et ses liens avec des chemins
absolus (`/sessions/{id}`, `/static/...`) sans tenir compte d'un préfixe — un chemin
préfixé casse la navigation dès la première redirection. Un port ou un sous-domaine dédiés
évitent ce problème par construction.

**Limite connue** : un nouveau port doit être ouvert en entrée au niveau du pare-feu/groupe
de sécurité cloud (ex. AWS Security Group) — une configuration hors de portée depuis
l'intérieur de la machine, et que Claude Code ne doit jamais tenter de modifier lui-même
(risque de sortie de bac à sable / modification d'infrastructure sensible sans
autorisation). Si le port reste injoignable depuis l'extérieur après vérification (`nginx`
l'écoute bien localement, voir § 3), le signaler et demander à l'utilisateur d'ouvrir ce
port précis, ou de choisir l'option B.

## Option B — sous-domaine dédié (plus robuste, même convention que les sites existants)

Si un nouveau nom de sous-domaine peut être pointé vers l'IP publique du serveur (DNS,
hors de portée depuis la machine elle-même) : créer un nouveau fichier
`/etc/nginx/sites-available/<sous-domaine>` sur le modèle exact de
`/etc/nginx/sites-available/kestrel` (reverse proxy + `auth_basic`), puis
`sudo certbot --nginx -d <sous-domaine>` pour obtenir un certificat dédié. Aucune
dépendance à un port non standard ni à un groupe de sécurité particulier (le port 443 est
déjà ouvert pour tous les sites existants).

---

# 3. Vérifications avant de transmettre le lien

```bash
# Le vhost de prévisualisation écoute-t-il bien localement ?
sudo ss -tlnp | grep <port-nginx>
curl -sk -H "Host: <domaine>" https://127.0.0.1:<port-nginx>/ -o /dev/null -w "%{http_code}\n"

# Le site PUBLIC reste-t-il inchangé après le reload nginx ?
curl -s -o /dev/null -w "%{http_code}\n" https://<domaine-public>/

# L'accès est-il joignable depuis l'EXTÉRIEUR (pas seulement localhost) ?
curl -4 -s --connect-timeout 5 -o /dev/null -w "%{http_code}\n" https://<domaine>:<port>/
# "000" + timeout (pas "connection refused") = bloqué en amont (pare-feu cloud), pas une
# erreur de configuration nginx — ne pas tenter de contourner, signaler et demander
# l'ouverture du port ou choisir l'option B.
```

Parcours fonctionnel court à exécuter avant de transmettre le lien (adapter selon la
fonctionnalité prévisualisée) : inscription d'un compte de démonstration, page de cours,
démarrage d'un entraînement avec un réglage de difficulté, réponse à quelques questions,
démarrage d'un examen avec réglage de difficulté ET de sévérité, soumission, vérification
de la page de résultats (ou du comportement « correction incomplète » si aucun fournisseur
IA n'est configuré — jamais un faux score), reprise d'une session en cours.

---

# 4. Nettoyage après la prévisualisation

Une fois la validation obtenue (ou le ticket terminé) :

```bash
# Arrêter les processus par PID exact (jamais un pkill par motif large — voir
# docs/claude-reports/2026-10-01_incident-502.md § 2.2 pour le risque réel que cela a
# représenté une fois sur ce serveur).
kill -TERM <pid-uvicorn-preview> <pid-worker-preview>

sudo rm -f /etc/nginx/sites-enabled/<nom>-preview
sudo nginx -t && sudo systemctl reload nginx

rm -f <base-de-demonstration>.db
```

Le site public et `jury-central.service` ne sont à aucun moment arrêtés, redémarrés ni
reconfigurés par cette procédure.
