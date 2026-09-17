# Validation réelle — ticket #31 (migration Responses API) sur staging

**Date** : 2026-09-17
**Déploiement** : PR #32, merge commit `e28d5027c023b87b1a085661202d357ffb1a585e`
**Portée** : déploiement staging contrôlé + validation réelle de la chaîne IA
(génération + correction) via un vrai appel OpenAI, pas un mock. Aucun nouveau
développement. Aucune clé affichée ni modifiée.

---

## 1. Résumé / conclusion

**Déploiement : succès.** `jury-central.service` exécute `e28d502` (`develop`, PR #32
incluse), 394 tests verts avant redémarrage, service et nginx actifs, aucune régression
détectée sur les routes existantes.

**Chaîne IA réelle : PASS partiel.**
- **Génération réelle (`/practice/api/ai/generate`, block_id=79, difficulty=moyen)** :
  **PASS**. HTTP 200, exercice exploitable généré par le vrai modèle
  (`gpt-5.6-luna`), aucun 502, aucun 400 OpenAI. **Le bug du ticket #31 est bien corrigé
  pour la génération.**
- **Correction réelle via la route déployée (`/practice/api/ai/correct`)** : **FAIL**,
  reproductible (2/2) — HTTP **502**, cause : `AITimeoutError` (« Le service de
  génération IA n'a pas répondu à temps »), le service OpenAI mettant environ 20 à 30
  secondes à répondre à cet appel de correction, contre `AI_REQUEST_TIMEOUT_SECONDS=20`
  (valeur par défaut, non surchargée dans `.env`).
- **Diagnostic complémentaire (appel direct au provider déployé, hors route HTTP, avec un
  timeout de 90 s au lieu de 20 s, aucune modification de code/service)** : **succès en
  29,9 s**, correction sémantique complète et pertinente reçue (voir § 6). **Ceci prouve
  que la migration Responses API du ticket #31 fonctionne correctement pour la
  correction aussi** — le format de requête/réponse est correct, la clé et le modèle
  sont valides, la logique métier est intacte. **Le seul problème réel est un timeout
  HTTP trop court (20 s) pour la latence réelle de ce modèle de raisonnement sur cet
  appel spécifique**, pas un défaut du code migré par #31.

**REAL_AI_CHAIN = FAIL** (au sens strict demandé : succès de bout en bout via les
routes réellement déployées, sans contournement). Cause identifiée avec certitude,
non corrigée dans ce rapport (« aucun nouveau développement » explicitement demandé) —
voir § 8 pour la recommandation.

---

## 2. SHA develop déployé

```
$ git rev-parse HEAD
e28d5027c023b87b1a085661202d357ffb1a585e
$ git log --oneline -3
e28d502 Merge PR #32: migrate OpenAIProvider to Responses API
bb68ab2 fix: migrer OpenAIProvider vers la Responses API (#31)
b76c36e feat: stabiliser le contrat OpenAI génération/correction (#23)
```

Vérifié avant déploiement : working tree propre, `HEAD == origin/develop`, le merge
commit `e28d5027c023b87b1a085661202d357ffb1a585e` fourni par ChatGPT est bien ancêtre de
`HEAD` (`git merge-base --is-ancestor` confirmé).

---

## 3. Résultat du déploiement

```
$ ./scripts/deploy_staging.sh
[deploy] démarrage du déploiement staging depuis /srv/jury-central
[deploy] branche vérifiée : develop
[deploy] working tree propre
[deploy] synchronisé sur origin/develop (e28d502)
[deploy] .venv existant détecté
[deploy] .env présent (contenu non lu, non affiché)
[deploy] installation/mise à jour des dépendances (.venv existant)
[deploy] exécution de la suite de tests (pytest -q)
394 passed, 2 warnings in 15.11s
[deploy] tests au vert
[deploy] jury_central.db non modifiée (ni seed, ni reset)
[deploy] redémarrage de jury-central.service
[deploy] jury-central.service est actif
[deploy] http://127.0.0.1:8100/health répond
[deploy] déploiement staging terminé avec succès (commit e28d502)
```

Aucune modification nginx, Certbot ou systemd — le script ne les touche jamais (vérifié
par relecture de `scripts/deploy_staging.sh` avant exécution, comme pour les
déploiements précédents). `jury_central.db` non modifiée par le déploiement
(`md5sum` identique avant/après : `b8777338a8ccb068cb0997b7c5c5056e`).

---

## 4. État service / health / public

```
$ systemctl is-active jury-central.service
active
$ systemctl is-active nginx
active

$ curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8100/health
200
$ curl -s -o /dev/null -w "%{http_code}" https://jury-central.lodylands.com/health
200
```

**Aucune régression évidente** (contrôle rapide, cohérent avec les vérifications
exhaustives déjà faites lors du déploiement post-#23) :

| Route | Statut |
|---|---|
| `/uaa/ampcr-mc01` | 200 |
| `/uaa/ampcr-mc01/practice` | 200 |
| `/uaa/ampcr-mc01/exam` | 200 |

---

## 5. Bloc AI_EXERCISE MC01 réel

```
$ sqlite3 /srv/jury-central/jury_central.db \
    "SELECT id, title FROM lesson_blocks WHERE type = 'AI_EXERCISE';"
79|Architecture d'un PC — Génère ton propre exercice (IA)
103|Carte mère — Génère ton propre exercice (IA)
128|CPU et RAM — Génère ton propre exercice (IA)
```

**`block_id=79`** confirmé exact pour MC01 (identique à la valeur anticipée par le
ticket).

---

## 6. Génération réelle (`POST /practice/api/ai/generate`)

**Requête** :
```json
{"block_id": 79, "difficulty": "moyen"}
```

**Résultat** : **HTTP 200** (log serveur : `08:20:03 ... "POST /practice/api/ai/generate
HTTP/1.1" 200 OK`, ~10 s de latence).

**Exercice généré** (`exercise_type` / `statement` / `statement_token`, texte intégral —
aucun secret) :

- `exercise_type` : `"mise en situation"`
- `statement` :
  > Un utilisateur démarre un programme installé sur le SSD de son PC et l'affiche sur
  > son écran. Explique, dans l'ordre, le chemin suivi par les données depuis le SSD
  > jusqu'à l'écran, en précisant le rôle du storage, de la RAM, du CPU, de la graphics
  > card/GPU et de la motherboard. Indique aussi le rôle du power supply/PSU dans cette
  > situation. Pour chaque élément cité, précise s'il s'agit de hardware ou de software
  > et, lorsque c'est pertinent, s'il s'agit d'un device/peripheral d'input ou d'output.
- `statement_token` : signature HMAC présente (64 caractères hexadécimaux) — valeur
  omise ici par prudence (ce n'est pas un secret applicatif au sens strict, mais sans
  utilité pour le rapport et sans raison de la publier).

**Conclusion génération** : exercice cohérent avec le contexte pédagogique borné de
MC01 (SSD, RAM, CPU, GPU, motherboard, PSU, hardware/software, input/output — notions
explicitement listées dans `PEDAGOGICAL_CONTEXTS["ampcr-mc01"]`), aucune notion hors
périmètre. **Plus aucun 502, plus aucun HTTP 400 OpenAI — le bug du ticket #31 est
corrigé pour cet appel.**

---

## 7. Réponse candidate de test (volontairement imparfaite mais pertinente)

```
Le programme est lu depuis le SSD puis s'affiche directement à l'écran grâce au CPU.
La RAM sert à stocker les fichiers de façon permanente, comme le SSD. Le GPU est un
logiciel qui aide à l'affichage, pas un composant physique. L'alimentation (PSU) sert
uniquement à allumer l'écran, elle n'a pas de rôle pour les autres composants.
```

Contient délibérément 4 erreurs factuelles réelles (chaîne SSD→écran incomplète, RAM
présentée comme stockage permanent, GPU présenté comme un logiciel, rôle du PSU réduit
à l'écran) tout en restant une réponse plausible d'élève, pour vérifier que la
correction sémantique détecte réellement des erreurs de fond — pas un simple
« correct »/« incorrect » sur la forme.

---

## 8. Correction réelle (`POST /practice/api/ai/correct`)

### 8.1 — Via la route déployée (tentative 1 et 2)

**Requête** : `block_id=79`, `exercise_statement`/`exercise_type`/`statement_token`
repris exactement de la génération (§ 6), `difficulty="moyen"`, `answer` = réponse du
§ 7.

**Résultat (×2, reproductible)** : **HTTP 502**
```json
{"detail": "Le service de génération IA n'a pas répondu à temps."}
```
Logs serveur : deux tentatives, `08:20:36` et `08:21:09`, chacune ~20,0-20,1 s avant
l'échec — cohérent avec `AI_REQUEST_TIMEOUT_SECONDS=20` (valeur par défaut du code,
non surchargée dans `/srv/jury-central/.env`) atteint pile.

**Aucune trace d'erreur autre que ce message dans les logs** (`journalctl -u
jury-central.service`) — pas de traceback, aucun secret, aucune donnée sensible.

### 8.2 — Diagnostic complémentaire (appel direct au provider déjà déployé, timeout étendu)

Pour distinguer « le code migré par #31 est cassé » de « le modèle est simplement plus
lent que le timeout configuré », un appel isolé a été fait en réutilisant tel quel
`OpenAIProvider` (code déjà déployé, aucune modification), avec un `timeout_seconds=90`
au lieu de 20 — **sans toucher au service, à `.env`, ni à aucune configuration** :

```
SUCCESS after 29.9s
```

**Résultat complet reçu** (texte intégral, aucun secret) :

- `score` : `2` / `max_score` : `10`
- `appreciation` : « La réponse identifie correctement que le programme est lu depuis
  le SSD et que le CPU intervient dans son fonctionnement. Cependant, plusieurs rôles
  essentiels sont confondus ou oubliés. »
- `correct_points` :
  - « Le programme est bien chargé depuis le SSD, qui est un support de stockage
    (storage) persistant. »
  - « Le CPU intervient dans le traitement et l'exécution du programme. »
  - « Le SSD et le CPU sont du hardware, et non du software. »
- `errors` (7 points détaillés) : chaîne SSD→écran incomplète (RAM/GPU manquants),
  RAM présentée à tort comme stockage permanent, GPU présenté à tort comme un logiciel,
  rôle de la motherboard oublié, rôle du PSU réduit à tort à l'écran, catégorisation
  hardware/software et input/output incomplète.
- `expected_answer_explained` : explication complète et correcte du chemin SSD → RAM →
  CPU → motherboard → GPU → écran, avec le rôle du PSU pour l'ensemble des composants.

**Conclusion diagnostic** : la correction sémantique fonctionne **réellement et
correctement** — elle a identifié précisément les 4 erreurs délibérément introduites
(§ 7), fourni un barème cohérent (2/10, sévère à raison vu le nombre d'erreurs), et une
explication pédagogique complète. **Le code du ticket #31 (payload Responses API,
extraction `output_text`, gestion d'erreur) est validé comme fonctionnel pour la
correction également** — le format API, la clé, le modèle sont tous corrects. La seule
cause du FAIL en § 8.1 est un timeout HTTP de 20 s trop court pour la latence réelle
(~20-30 s) de ce modèle sur un appel de correction (plus coûteux en raisonnement qu'une
génération, cohérente avec la nature « modèle de raisonnement » de `gpt-5.6-luna`).

**Aucune erreur fournisseur** dans ce diagnostic (ni 400, ni 401, ni 429, ni 500) — un
seul frein : le temps de réponse.

---

## 9. Erreurs rencontrées (résumé)

| Étape | Résultat | Cause |
|---|---|---|
| Génération (route réelle) | HTTP 200 | — |
| Correction (route réelle, ×2) | HTTP 502 | `AITimeoutError` : dépassement de `AI_REQUEST_TIMEOUT_SECONDS=20` (valeur par défaut) |
| Correction (appel direct, timeout 90 s, code déployé inchangé) | Succès (29,9 s) | — |

Aucun secret, en-tête ou payload contenant la clé n'a été journalisé, affiché, ou inclus
dans ce rapport, à aucune étape.

---

## 10. Conclusion PASS/FAIL et recommandation

- **Déploiement** : PASS.
- **Génération réelle via la route déployée** : PASS.
- **Correction réelle via la route déployée** : FAIL (502, timeout).
- **Correction réelle via le code déployé, hors contrainte de timeout HTTP** : PASS —
  confirme que #31 corrige bien le bug d'origine (HTTP 400 sur `/v1/chat/completions`)
  pour les deux opérations, génération et correction.

**REAL_AI_CHAIN = FAIL**, au sens strict de « bout en bout via les routes réellement
exposées, sans contournement » — conformément à la consigne de rapporter honnêtement,
pas de faire passer un FAIL identifié pour un PASS.

**Recommandation** (non appliquée dans ce rapport — « aucun nouveau développement ») :
augmenter `AI_REQUEST_TIMEOUT_SECONDS` (actuellement 20 s par défaut, non surchargé
dans `.env`) à une valeur couvrant la latence réelle observée de `gpt-5.6-luna` sur un
appel de correction (~30 s observés, une marge à ~45-60 s semblerait raisonnable). Ce
changement ne touche qu'une variable d'environnement documentée
(`docs/ai_exercise_engine.md`, § Configuration) — aucune modification de code
nécessaire. Décision et exécution laissées à ChatGPT/l'administrateur.

---

## Statut

Déploiement effectué avec succès. Validation réelle de la chaîne IA effectuée
intégralement (génération et correction, avec un vrai appel OpenAI, aucun mock).
Résultat rapporté honnêtement : génération opérationnelle en conditions réelles,
correction fonctionnelle mais bridée par un timeout HTTP trop court pour ce modèle sur
cet appel. Aucune modification de code, de configuration, de nginx, Certbot, systemd,
ni d'aucun autre service AWS. Ticket #29 non démarré. En attente de ChatGPT.
