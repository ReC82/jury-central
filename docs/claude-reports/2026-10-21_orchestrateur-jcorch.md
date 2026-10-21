# 2026-10-21 — Installation de l'orchestrateur Jury Central (`jcorch`)

## 1. Demande et périmètre

Consigne explicite du propriétaire (21 octobre 2026) : reproduire pour Jury Central le
fonctionnement de LQORCH (superviseur des sessions Claude de LodyQuests), sans réinventer de
système et sans modifier LodyQuests. Instance dédiée, file de tickets explicite, un seul ticket
actif, worktrees séparés du dossier servi, reprise après interruption, blocage documenté puis
passage au ticket indépendant suivant.

Autorisation donnée pour les tickets explicitement mis en file : code, contrôles ciblés, commit,
push, fusion vers `develop` et installation sur https://jury-central.lodylands.com sans
confirmation intermédiaire. Pas de preview séparée. Pas de suite complète répétée pour les petites
modifications. Aucune autre modification d'infrastructure n'est autorisée.

Branche : `chore/jcorch-orchestrator` (ce rapport seulement, aucun code applicatif).

## 2. Constat sur LQORCH (lecture seule)

- Service `lodyquests-orch.service` → `/opt/lodyquests-orch/lqorch.py run` (Python, bibliothèque
  standard uniquement), prompt `/opt/lodyquests-orch/session_prompt.md`, commande
  `/usr/local/bin/lqorch`.
- État SQLite (`tasks`, `sessions`, `events`, `control`) dans `~/.local/state/lodyquests-orch/`,
  verrou exclusif `supervisor.lock` (`flock`), journaux de session `sessions/*.jsonl`.
- Une session = `claude -p` sur UN ticket, qui écrit un fichier d'état JSON ; le superviseur
  classe la fin de session (COMPLETED, RATE_LIMIT, TIMEOUT, CRASH…), applique un délai
  progressif, un disjoncteur (pause après N sessions sans rapport) et respecte les limites
  fournisseur (`rate_limit_event`, seuils 5 h / 7 j, plafond de sessions et de coût par jour).
- Reprise : au redémarrage, toute session orpheline est arrêtée et notée INTERRUPTED ; son ticket
  reste RUNNING et passe en premier.
- File : `lqorch add N`. Une file vide déclenche un « tri du backlog » automatique (ticket #0),
  et une session peut ajouter des tickets (`enqueue`).
- Tout est paramétrable par variables `LQ_*` (dépôt, dossiers, prompt, état).

## 3. Ce qui a été installé

| Élément | Emplacement |
|---|---|
| Code | `/opt/jury-central-orch/lqorch.py` — copie de LQORCH (empreinte d'origine `573d74066d25`) |
| Prompt de session | `/opt/jury-central-orch/session_prompt.md` (règles Jury Central) |
| Configuration | `/opt/jury-central-orch/instance.env` |
| Commande | `/usr/local/bin/jcorch` |
| Service | `jury-central-orch.service` (activé, `Restart=on-failure`, 5 relances/h max) |
| État, verrous, journaux | `/home/ubuntu/.local/state/jury-central-orch/` |
| Worktrees | `/srv/jury-central-worktrees/ticket-<n>` |

Différences avec LQORCH, toutes désactivées par défaut (le code reste compatible LodyQuests) :

- `LQ_TRIAGE=0` : pas de tri automatique du backlog — rien n'entre en file sans `jcorch add` ;
- `LQ_SESSION_ENQUEUE=0` : une session ne peut pas ajouter de ticket (simple événement
  `proposed`) ;
- `LQ_SERVICE` : nom du service rappelé par `resume`.

Garde-fous de l'instance (`jcorch config`) : 12 sessions/jour, seuils fournisseur 85 % (5 h) et
75 % (7 j) pour laisser une marge à LodyQuests et à l'usage interactif, qui partagent le même
compte Claude.

Le prompt de session impose notamment : un worktree par ticket ; aucune écriture dans
`/srv/jury-central` hors installation ; installation sous verrou (`install.lock`) après
sauvegarde SQLite (`.backup` vers `~/.local/state/jury-central-orch/backups/`), `merge --ff-only`,
seed idempotent seulement si du contenu a changé, redémarrage des deux services, contrôles
`/health` local et public et compteurs utilisateurs/sessions/réponses ; retour arrière par
`git revert` en cas d'échec ; rapport `docs/claude-reports/` avec SHA installé, liens directs et
« Statut : à tester » ; commentaire sur le ticket laissé ouvert ; statut `WAITING_OWNER`.
Interdits : `main`, `--force`, infrastructure, `.env`, données utilisateurs, LodyQuests.

## 4. Vérifications effectuées

- Aucune instance Jury Central préexistante (service, dossiers, commande, processus).
- Essai à blanc avec une fausse commande `claude` et un état temporaire : session lancée sur le
  bon ticket, prompt entièrement substitué, statut `WAITING_OWNER` appliqué, ticket proposé par
  la session **non** ajouté, aucun ticket #0 créé.
- Deuxième superviseur refusé (« Un autre superviseur tourne déjà »), y compris sur l'instance
  réelle.
- Arrêt brutal (`kill -9`) du superviseur pendant une session : au redémarrage, session orpheline
  arrêtée, notée INTERRUPTED, ticket repris en premier.
- `jcorch stop` : arrêt propre ; le superviseur refuse de redémarrer avant `jcorch resume`.
- Import Python depuis un worktree avec le `.venv` du site : `app` vient bien du worktree.
- Service actif, file vide, `lodyquests-orch`, `jury-central` et
  `jury-central-correction-worker` toujours actifs et inchangés.

Non fait : aucune vraie session Claude n'a encore été lancée (file vide volontairement).

## 5. Rapprochement tickets / livraisons (develop `0e8228a`)

- Livrés sans reste identifié (fermeture à décider par le propriétaire) : #92, #90, #88, #85,
  #84, #82, #80, #79, #74, #73, #71, #70, #69, #68, #64, #62, #58, #55, #47, #44, #43, #42, #41,
  #31, #29, #25, #24, #16, #4.
- Livrés dans le code mais **pas visibles sur le site** : #83 (SMART MC04) et #65 (`> 2 To` MC08) —
  la base live garde l'ancien contenu ; le correctif est la PR #89, ouverte et non fusionnée.
- Travail réel restant : #86 (choix du nombre de questions), #67 (navigation par parcours),
  #94 (FR06→FR20), #129 (FSE : variété et visuels), #75, #48, #46, #45.
- Candidats raisonnables pour la file : #86 et #67 (spécifiés, indépendants), puis #94 par lots
  et #129. #75, #45, #48, #46 demandent des arbitrages produit.
- PR #104 (mise à jour des règles de fusion/déploiement) est toujours ouverte.

Aucun ticket n'a été mis en file : la sélection reste au propriétaire.

## 6. Exploitation

```bash
jcorch status                       # état, session en cours, quotas
jcorch queue                        # file
jcorch log [N]                      # événements (globaux ou d'un ticket)
jcorch sessions                     # dernières sessions
ls -t ~/.local/state/jury-central-orch/sessions/ | head   # journaux bruts
journalctl -u jury-central-orch -f  # journal du service
jcorch add N [--prio P] [--deps 12,34] [--note "…"]       # mettre / remettre un ticket en file
jcorch skip N "raison"              # mettre de côté
jcorch pause | jcorch resume        # suspendre / reprendre
jcorch stop [--now]                 # arrêter (après la session / tout de suite)
jcorch resume && sudo systemctl start jury-central-orch   # relancer après stop
```

## 7. Limites et points ouverts

- Le quota Claude est partagé avec LodyQuests et l'usage interactif ; chaque instance ne voit que
  les valeurs remontées par ses propres sessions.
- La règle permanente § 8 de `docs/PROJECT_RULES.md` (pas de fusion/déploiement sans validation)
  reste inchangée dans le dépôt ; l'exception pour les tickets mis en file est portée par le
  prompt de l'orchestrateur. La PR #104 traite ce sujet et reste une décision du propriétaire.
- Mise à jour du code LQORCH : recopie manuelle plus réapplication des trois options
  (`/opt/jury-central-orch/README.md`).
