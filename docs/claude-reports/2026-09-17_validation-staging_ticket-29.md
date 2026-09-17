# Validation staging — ticket #29 (S'entraîner MC01 interactif)

**Date** : 2026-09-17
**PR mergée** : #34
**Commit develop déployé** : `1a40034ca55fbd07dda0f7cf9e8fc6c830ab55b6`
**Environnement** : staging (`jury-central.lodylands.com`), déploiement via
`./scripts/deploy_staging.sh`, sans reset-db, sans suppression de `jury_central.db`.

---

## 1. Déploiement

```
git checkout develop
git pull --ff-only origin develop   → déjà à jour localement, fast-forward vers 1a40034
./scripts/deploy_staging.sh
```

Résultat : **succès**.
- branche vérifiée : `develop`
- working tree propre avant déploiement
- fast-forward `615a6f9 → 1a40034` (aucune divergence)
- `.venv` existant réutilisé, dépendances mises à jour
- suite de tests exécutée par le script lui-même : **431 passed**, 2 warnings préexistants
  (httpx/anyio, sans lien avec #29)
- `jury_central.db` non touchée par le script (ni seed, ni reset — rappel explicite du
  script lui-même)
- `jury-central.service` redémarré et actif
- `http://127.0.0.1:8100/health` répond après redémarrage

**Le script de déploiement n'a modifié ni nginx, ni Certbot, ni la définition du service
systemd** — il ne fait que `git fetch/merge --ff-only`, `pip install`, `pytest`,
`systemctl restart jury-central.service`.

---

## 2. Seed additif (contenu du ticket #29)

Le ticket #29 modifie le contenu seedé (migration des 8 derniers exercices Markdown MC01
vers `editorial_exercise`). Exécution du seed officiel, additif/idempotent, **sans
reset-db, sans suppression de `jury_central.db`** :

### Premier `seed-db`

```
Seed terminé : Mathématiques (MB32, MQ32, MQ34), Informatique (AMPCR)
  Créé   : 0 matière(s), 0 module(s), 0 UAA, 8 bloc(s)
  Conservé (déjà présent, non modifié) : 2 matière(s), 4 module(s), 5 UAA, 132 bloc(s)
  Retiré : 3 bloc(s) de démonstration obsolète(s)
```

8 blocs créés (les 8 nouveaux exercices structurés Ex3/4/5/6/7/8/10/12), 3 blocs retirés
(les 3 anciens blocs Markdown regroupant ces exercices sous leur ancien titre) — conforme
au mécanisme de migration par `MC01_OBSOLETE_TITLES` documenté dans le rapport de
développement du ticket.

### Second `seed-db` (preuve d'idempotence)

```
Seed terminé : Mathématiques (MB32, MQ32, MQ34), Informatique (AMPCR)
  Créé   : 0 matière(s), 0 module(s), 0 UAA, 0 bloc(s)
  Conservé (déjà présent, non modifié) : 2 matière(s), 4 module(s), 5 UAA, 140 bloc(s)
```

**0 création, 0 suppression, 140 blocs conservés à l'identique.** Aucun doublon généré
par un second passage. Idempotence confirmée.

---

## 3. État service / health

| Vérification | Résultat |
|---|---|
| `systemctl is-active jury-central.service` | `active` |
| `systemctl is-active nginx` | `active` |
| `curl http://127.0.0.1:8100/health` | `200` |
| `curl https://jury-central.lodylands.com/health` | `200` |
| `https://jury-central.lodylands.com` répond | Oui (page MC01 testée directement, voir §5) |

Aucune modification apportée à nginx, Certbot ou à la définition systemd — seul
`systemctl restart jury-central.service` (déjà autorisé par le script officiel) a été
exécuté.

---

## 4. Audit base — les 12 exercices MC01

Requête directe sur `jury_central.db` (table `lesson_blocks`, filtrée sur l'UAA
`ampcr-mc01`) après le seed additif :

| Titre | type | space |
|---|---|---|
| Exercice 1 — Matériel ou logiciel (classification) | EDITORIAL_EXERCISE | PRACTICE |
| Exercice 2 — Unité centrale ou périphérique (classification) | EDITORIAL_EXERCISE | PRACTICE |
| Exercice 3 — Compatibilité CPU/carte mère (réponse rédigée) | EDITORIAL_EXERCISE | PRACTICE |
| Exercice 4 — Diagnostic : rien ne s'affiche (diagnostic) | EDITORIAL_EXERCISE | PRACTICE |
| Exercice 5 — RAM et stockage (réponse rédigée) | EDITORIAL_EXERCISE | PRACTICE |
| Exercice 6 — Ambiguïté des Go (réponse rédigée) | EDITORIAL_EXERCISE | PRACTICE |
| Exercice 7 — GPU intégré ou dédié (réponse rédigée) | EDITORIAL_EXERCISE | PRACTICE |
| Exercice 8 — Puissance de l'alimentation (réponse rédigée) | EDITORIAL_EXERCISE | PRACTICE |
| Exercice 9 — Lancement d'un programme (ordering) | EDITORIAL_EXERCISE | PRACTICE |
| Exercice 10 — Diagnostic : le PC ralentit (diagnostic) | EDITORIAL_EXERCISE | PRACTICE |
| Exercice 11 — Entrée, sortie ou mixte (classification) | EDITORIAL_EXERCISE | PRACTICE |
| Exercice 12 — Vocabulaire FR/EN (vocabulaire) | EDITORIAL_EXERCISE | PRACTICE |

- **12/12 EDITORIAL_EXERCISE**, **12/12 space=PRACTICE**.
- **0** bloc `MARKDOWN` dont le titre contient « Exercice » restant dans MC01 (les 3
  anciens blocs regroupant les exercices 3–8, 10, 12 ont bien été retirés par le seed).
- **0 doublon** de titre parmi les 28 blocs de l'UAA `ampcr-mc01`.
- Le bloc `AI_EXERCISE` (« Architecture d'un PC — Génère ton propre exercice (IA) »,
  ticket #10) est distinct des 12 exercices pédagogiques et reste présent, en PRACTICE,
  sans changement.

---

## 5. Validation HTTP/HTML de la page publique

`GET https://jury-central.lodylands.com/uaa/ampcr-mc01/practice` → **200**.

- **12** blocs `.editorial-exercise-block` présents dans la page.
- **0** occurrence de « Correction : » dans le HTML brut.
- Les items sont transmis au JS via l'attribut `data-items` (JSON), inspectés
  directement : **aucune fuite** de `accepted_answers`, `correct_index`,
  `correct_categories`, `correct_order`, `explanation` ou `rubric` dans ce JSON — la
  correction (locale ou IA) n'est obtenue qu'à l'appel de la route `verify`, jamais au
  chargement de page.
- `requires_ai` correctement `false` pour les exercices 1, 2, 9, 11 (classification/
  ordering) et `true` pour les exercices 3, 4, 5, 6, 7, 8, 10, 12
  (long_answer/diagnostic/vocabulary).
- Bouton présent (« Corriger ma réponse » / « Vérifier », construits côté client par
  `editorial_exercise.js` en fonction de `requires_ai` — non visibles dans le HTML brut
  car construits en JS, comme le sont les contrôles textarea et les boutons de
  classification/ordering ; confirmé fonctionnellement via les tests §6).
- **0 doublon Markdown** : aucun ancien bloc statique des exercices 3–8, 10, 12 ne
  subsiste sur la page.

### ⚠️ Problème constaté (non corrigé, remonté tel quel)

**L'ordre d'affichage des 12 exercices sur la page n'est pas strictement 1→12.** Ordre
réel observé sur la page publique :

```
1, 2, 3, 4, 9, 5, 11, 6, 7, 8, 10, 12
```

Les exercices 9 et 11 (déjà migrés en #21, non retouchés par #29) s'intercalent entre 4
et 5, puis entre 5 et 6, au lieu d'apparaître en position 9 et 11. Cause probable : les
positions (`LessonBlock.position`) de plusieurs blocs de `MC01_BLOCKS` sont dupliquées
(confirmé en base : plusieurs blocs partagent la même valeur de `position`, ex. 16, 17,
18), et l'ordre d'affichage départage alors les égalités par un critère qui ne correspond
pas à l'ordre pédagogique voulu 1→12. Tous les exercices restent présents, tous
répondables, aucune correction n'est exposée — il s'agit d'un problème d'ordre
d'affichage uniquement, pas d'un problème de contenu ou de sécurité.

**Conformément à l'instruction reçue, le code n'a pas été modifié** — ce problème est
rapporté pour arbitrage par ChatGPT avant toute correction.

---

## 6. Tests fonctionnels réels sur staging

Effectués **exclusivement contre le service staging déjà déployé** (aucun serveur local
parallèle lancé), conformément à la consigne visant à éviter l'incident documenté dans le
rapport du ticket précédent.

### A. Correction locale — Exercice 1 (classification)

Requête `POST /practice/api/editorial/132/verify` avec une réponse volontairement
correcte (`[0,1,0,1,0]`, soit Matériel/Logiciel/Matériel/Logiciel/Matériel pour carte
graphique/navigateur/RAM/antivirus/SSD) :

- **HTTP 200**
- `"correct": true`
- Feedback complet retourné (`correct_answer`, `explanation`) — normal puisqu'il s'agit
  de la réponse envoyée *après* validation, jamais avant.

### B. Correction IA — Exercice 3 (long_answer)

Requête `POST /practice/api/editorial/137/verify` avec une réponse volontairement
imparfaite mais pertinente (« Parce que le processeur doit avoir le bon socket, sinon ça
marche pas. ») :

- **HTTP 200**
- Temps de réponse : **~7 secondes**, aucun timeout, aucun 502.
- Feedback exploitable et cohérent avec l'imperfection de la réponse envoyée :
  `points_awarded: 0.7`, `points_max: 1.0`, `strengths` (2 éléments : socket bien
  identifié), `missing` (2 éléments : absence de mention du chipset) — la correction IA
  fonctionne réellement en conditions staging, avec la vraie clé configurée en #31.
- Cette correction n'apparaît qu'en réponse à la requête explicite (aucun contenu de ce
  type n'était présent dans la page avant l'appel — confirmé §5).

Aucune valeur de `OPENAI_API_KEY` n'a été affichée, journalisée ou incluse dans ce
rapport à aucun moment.

---

## 7. Problèmes constatés

- **Ordre d'affichage des exercices 9 et 11 incorrect sur la page S'entraîner MC01**
  (voir détail §5). Fonctionnel mais gênant pédagogiquement (l'élève voit « Exercice 9 »
  puis « Exercice 5 »). À arbitrer par ChatGPT — aucune correction appliquée dans le
  cadre de cette validation.
- Aucun autre problème visuel, fonctionnel ou de sécurité constaté.

---

## 8. Conclusion

- Déploiement : OK, commit `1a40034` actif.
- Seed additif : OK, 8 blocs créés au premier passage, 0 régression.
- Idempotence du second seed : confirmée (0 création, 0 doublon).
- Service et santé (local + public) : OK.
- Base : 12/12 exercices MC01 structurés, 12/12 en PRACTICE, 0 ancien bloc Markdown
  d'exercice restant, 0 doublon.
- Page publique : 200, contenu conforme, 0 correction visible avant validation.
- Correction locale : fonctionnelle (HTTP 200, résultat correct).
- Correction IA : fonctionnelle en conditions réelles (HTTP 200, ~7 s, feedback
  exploitable, aucun timeout, aucun 502).
- Problème non bloquant identifié et rapporté sans être corrigé : ordre d'affichage des
  exercices 9 et 11.

**STAGING_29=PASS**

(Le contenu est fonctionnellement complet et conforme au ticket #29 ; le problème
d'ordre d'affichage est un défaut d'UX mineur n'empêchant ni la réponse ni la correction
d'aucun exercice, et n'a volontairement pas été corrigé dans le cadre de cette
validation, en attente d'arbitrage de ChatGPT.)
