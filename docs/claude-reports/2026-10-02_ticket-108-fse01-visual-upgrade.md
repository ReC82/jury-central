# Rapport — Ticket #108 : amélioration visuelle de FSE01 (cartes par notion, documents
réalistes, affiche illustrée, schéma responsive)

Branche : `feature/108-fse01-visual-upgrade` (depuis `develop`). PR #109 fusionnée dans
`develop`, puis installée sur `jury-central.lodylands.com`.

**SHA installé : `8b57101`** (merge commit de la PR #109 dans `develop`).

Périmètre strict FSE01 pour cette étape, conformément à la demande : composants
réutilisables créés et documentés, mais appliqués à FSE01 uniquement — l'extension à
FSE02-17 attend un retour visuel explicite.

---

## 1. Accès OpenAI vérifié et réutilisé

- Intégration existante inspectée (`app/ai/openai_provider.py`, `app/ai/factory.py`,
  `app/config.py`) : appels REST directs via `httpx` (pas de SDK), clé dans
  `OPENAI_API_KEY`, modèle dans `openai_model` (`gpt-5.6-luna` en production — **inchangé**,
  aucun paramètre d'examen touché).
- Documentation officielle OpenAI consultée (2026-10) pour la génération d'images :
  endpoint `POST https://api.openai.com/v1/images/generations`, modèles `gpt-image-2.5-flare`
  (génération rapide — retenu) / `gpt-image-2.5-sunburst` (édition de précision, non
  utilisé ici), réponse déjà en base64 par défaut, authentification identique
  (`Authorization: Bearer`). Une vérification d'organisation est mentionnée comme pouvant
  être exigée par OpenAI avant l'accès aux modèles GPT Image.
- **Accès vérifié par un appel de test réel, à faible coût** (prompt minimal, taille
  1024×1024, qualité `low`) avant toute implémentation : **succès immédiat, aucune
  activation ni accès supplémentaire nécessaire** — la clé déjà configurée pour les examens
  fonctionne aussi pour la génération d'images.
- Nouveau fournisseur séparé (`app/ai/image_provider.py::ImageProvider`) : même clé, mais
  modèle et délai **dédiés** (`openai_image_model` = `gpt-image-2.5-flare`,
  `ai_image_request_timeout_seconds` = 120s, contre 20s pour les examens — une génération
  d'image complexe peut prendre jusqu'à 2 minutes selon la documentation officielle).
  `openai_model`/`ai_request_timeout_seconds` (examens) **n'ont pas été modifiés**.
- La clé n'est jamais journalisée, jamais transmise au navigateur, jamais incluse dans un
  message d'erreur (même garantie que `OpenAIProvider`, vérifiée par test : voir
  `tests/ai/test_image_provider.py::test_generate_image_error_response_never_leaks_key`).

---

## 2. Présentation pédagogique : une carte par notion

Les 8 notions du schéma de communication (émetteur, récepteur, message, code, canal,
contexte, obstacle, rétroaction) sont désormais chacune accompagnées d'une icône cohérente
dans la grille de définitions existante (`.jc-definitions`, déjà en grille sur ordinateur /
empilée sur téléphone depuis le ticket #105) : 🗣️ 👂 💬 🔤 📡 🧭 ⚠️ 🔁. Ajout additif
(`.jc-definition-head`/`.jc-definition-icon`) : les grilles de FSE02-17 qui n'utilisent pas
ce nouvel en-tête restent inchangées visuellement.

Les encadrés distincts déjà en place (définition/exemple/méthode/piège/mémo, ticket #105)
sont conservés — aucune carte imbriquée supplémentaire ajoutée, aucune décoration
superflue. Les corrigés restent fermés au chargement (`<details>` sans `open`, vérifié).

---

## 3. Documents réalistes (texte réel, sélectionnable)

- **Mail** (`docs/components/EmailCard.md`) : vraie mise en page de messagerie — avatar,
  expéditeur/destinataire/objet/date, fil de réponse du service recrutement, message
  interrompu signalé par un encadré rouge pointillé explicite. Toutes les informations
  nécessaires aux questions existantes sont conservées (le texte brut
  `FSE01_MAIL_TEXT`, utilisé par la banque de questions et la correction IA, reste
  byte pour byte identique à avant).
- **Réseau social** (`docs/components/SocialPostCard.md`) : vraie publication — auteur,
  réactions, fil de commentaires (Fatima B., Mourad T., Julien P.), réponse de l'entreprise
  mise en évidence par un badge. Texte brut `FSE01_SOCIAL_TEXT` inchangé.
- **Affiche** (`docs/components/PosterCard.md`) : illustration générée (§ 4) + slogan et
  mentions en HTML/CSS (jamais intégrés à l'image, pour garantir leur exactitude et leur
  lisibilité) ; étiquette renforcée « Reconstitution pédagogique fictive — pas une
  véritable campagne officielle ». Texte brut `FSE01_AFFICHE_TEXT` inchangé.

Les trois analyses (tableaux « Élément du schéma / Ce qu'on observe », ajoutés au ticket
#105) restent strictement à l'extérieur des cartes-documents et n'ont pas été modifiées :
cohérence vérifiée entre documents affichés, analyses et questions de la banque existante.

---

## 4. Génération d'images maîtrisée

- `app/v1/fse01_image.py::generate_and_save_poster_image()` : vérifie d'abord si l'image
  existe déjà (aucun appel API si oui, sauf `--force`) ; sinon, **au maximum deux
  tentatives** (une nouvelle tentative uniquement après un échec technique — réseau,
  timeout, modération, format de réponse — jamais pour une image jugée « ratée », aucun
  jugement automatique de ce type n'étant possible côté serveur).
- **Résultat réel** : succès dès la **première tentative**. Image generée, inspectée
  manuellement (silhouette d'enfant stylisée traversant un passage piéton devant une
  voiture qui ralentit, style plat, palette rouge/blanc/gris, aucun texte ni logo dans
  l'image) et jugée directement utilisable — aucune seconde tentative nécessaire.
- Image enregistrée durablement : `app/static/img/fse01_affiche_securite_routiere.png`
  (1 117 165 octets), **commitée dans le dépôt** (comme `design-system.css`/les scripts
  JS) — aucun appel API à l'ouverture du cours, aucune régénération automatique au seed ou
  au déploiement installé sur production : le fichier a simplement été apporté par `git
  fetch`/`merge --ff-only`, zéro appel OpenAI effectué sur le serveur de production.
- Prompt et modèle conservés durablement dans un fichier de métadonnées sidecar
  (`fse01_affiche_securite_routiere.json`, committé à côté de l'image) : prompt exact,
  modèle (`gpt-image-2.5-flare`), taille (`1024x1536`), qualité (`high`), horodatage.
- Remplacement manuel simple : `generate-fse01-poster-image --force` (nouvelle commande,
  `pyproject.toml`), sans nouvelle interface d'administration.
- Rendu de secours en CSS pur (`_poster_visual_html()`, vérifie l'existence du fichier
  localement — lecture disque, pas un appel réseau) si l'image n'a jamais été générée ou a
  été supprimée : un pictogramme SVG simple remplace alors l'`<img>`, jamais une image
  cassée ni un faux succès. Ce chemin n'a pas été déclenché en production (l'image existe).

---

## 5. Schéma de communication responsive

Deux rendus SVG distincts, permutés par média-requête CSS (`.jc-diagram--desktop`/
`.jc-diagram--mobile`, bascule sous 576px) plutôt qu'un simple redimensionnement du schéma
large — qui aurait rendu le texte minuscule sur téléphone (le texte scale avec le reste du
`viewBox`). Le rendu mobile est en colonne, avec un texte proportionnellement deux fois
plus grand par rapport à la largeur du support que le rendu desktop. Les deux rendus
représentent les mêmes 8 éléments et préservent les mêmes nuances : code et canal restent
deux lignes de texte distinctes (jamais fondues), et la rétroaction précise explicitement
que sa possibilité dépend du canal, pas de la rapidité de la réponse — dans les deux
versions.

Rendu vérifié visuellement (voir § 6) : lisible, bien proportionné, aucune troncature de
texte dans les deux formats.

---

## 6. Vérifications effectuées

**Tests ciblés (pas la suite complète de 1 419 tests)**, exécutés sur la branche puis sur
le checkout de production après fast-forward :

| Lot | Résultat |
|---|---|
| `tests/ai/test_image_provider.py` (nouveau, 6 cas, aucun appel réseau réel) | 6/6 ✅ |
| `tests/test_ticket108_fse01_poster_image.py` (nouveau, 5 cas : succès direct, retry unique, échec sans fichier partiel, `--force`, chemins isolés) | 5/5 ✅ |
| `tests/test_card_kind.py`, `tests/test_admin_content_hierarchy.py`, `tests/test_ticket96_fse01.py` | 56/56 ✅ |
| `tests/ai/test_openai_provider.py`, `tests/test_ticket35_safe_openai_config.py` (non-régression du fournisseur texte/examens) | 60/60 ✅ (total avec ticket96, voir ci-dessus) |
| `tests/test_ticket97_fse02_04.py`, `tests/test_ticket98_fse05_08.py`, `tests/test_ticket102_coverage.py` (non-régression FSE02-17) | 126/126 ✅ |

**Bug corrigé en cours de route** : `_seed_uaa` (`app/seed.py`) utilisait la collection de
relation `uaa.lesson_blocks` pour détecter les blocs déjà existants ; cette collection
pouvait rester périmée juste après une suppression `obsolete_titles` dans le même
process/session (observé par le test d'idempotence, qui appelle `seed()` deux fois de
suite), menant à ignorer à tort comme « déjà existant » un bloc pourtant supprimé — un
bloc attendu n'était alors jamais recréé. Corrigé en interrogeant la base directement
plutôt que la collection en mémoire. Sans impact en production (`seed-db` y est exécuté une
fois par processus), mais nécessaire pour que `FSE01 — Théorie`/`FSE01 — Exemples commentés`
(ajoutés à `obsolete_titles` pour forcer le remplacement de leur contenu déjà seedé par la
version enrichie) soient systématiquement recréés à chaque exécution.

**Vérification structurelle de la page réelle en production** (`/uaa/fse-fse01`, après
installation) : 8 icônes de notion présentes, composants mail/réseau social/affiche
présents avec leurs classes distinctives, réponse de l'entreprise mise en avant, image
statique servie en 200 avec le bon contenu binaire (1 117 165 octets, taille exacte), rendu
de secours absent (l'image existe), les deux rendus SVG du schéma présents, aucun corrigé
ouvert par défaut, aucun paragraphe à tirets littéraux résiduel, CSS des nouveaux
composants chargée en 200.

**Prévisualisation visuelle locale** de chaque nouveau composant, effectuée avec des
outils de développement ad hoc (WeasyPrint + cairosvg, installés temporairement dans
l'environnement de développement uniquement — **jamais ajoutés comme dépendance du
projet**, absents de `pyproject.toml`) : rendu HTML réel → PDF → image, inspecté
directement. Résultat : mail, publication, affiche et les deux schémas (desktop/mobile)
rendus correctement, lisibles, sans défaut de mise en page visible. L'image générée par
OpenAI a également été inspectée directement et jugée pédagogiquement utilisable.

**Limite explicite, demandée à signaler sans ambiguïté** : **aucun outil de capture de
navigateur réel (Chrome/Firefox headless, Playwright, etc.) n'est disponible dans cet
environnement.** La prévisualisation ci-dessus (WeasyPrint) est un moteur de rendu PDF, pas
un navigateur, et ne reproduit pas exactement le comportement de rendu d'un vrai navigateur
(notamment les polices d'emoji, absentes de cet environnement, qui s'affichent comme des
cases vides dans la prévisualisation locale mais s'afficheront normalement dans un vrai
navigateur). **Je n'ai donc pas pu valider visuellement le rendu réel dans un navigateur, ni
sur ordinateur, ni à une largeur de téléphone, ni à l'impression A4** — cette vérification
reste à faire par l'utilisateur. Les vérifications structurelles (HTML/CSS envoyé par le
serveur) et la prévisualisation ad hoc sont des indices de correction, pas une preuve de
rendu visuel final.

**Comptes et données vérifiés intacts** après le seed de production : 18 utilisateurs
(`v1_users`), 67 sessions (`v1_questionnaire_sessions`), 536 réponses
(`v1_session_answers`) — identiques avant/après. Sauvegarde de `jury_central.db` effectuée
avant le seed : `jury_central.db.bak-pre-ticket108-<horodatage>` (conservée dans
`/srv/jury-central`).

---

## 7. Fichiers modifiés/créés

- `app/ai/image_provider.py` (nouveau) — fournisseur de génération d'images.
- `app/ai/factory.py` — `get_image_provider()`.
- `app/config.py` — `openai_image_model`/`ai_image_request_timeout_seconds` (additifs).
- `app/v1/fse01_image.py` (nouveau) — génération/persistance maîtrisée de l'illustration.
- `app/v1/fse01_content.py` — composants mail/réseau social/affiche réalistes, schéma
  responsive à deux rendus (textes bruts inchangés).
- `app/v1/fse01_course.py` — icônes ajoutées à la grille de définitions.
- `app/static/css/design-system.css` — nouvelles règles (`.jc-definition-icon`,
  `.jc-mail-*`, `.jc-social-*`, `.jc-poster-*`, `.jc-diagram--desktop/--mobile`).
- `app/static/img/fse01_affiche_securite_routiere.{png,json}` (nouveaux) — illustration et
  métadonnées.
- `app/seed.py` — `obsolete_titles` étendu pour FSE01 (forcer le remplacement de contenu) +
  correctif `_seed_uaa` (requête fraîche plutôt que collection périmée).
- `docs/components/{EmailCard,SocialPostCard,PosterCard}.md` (nouveaux),
  `docs/components/Diagram.md` (section schéma responsive), `docs/components/INDEX.md`.
- `pyproject.toml` — script `generate-fse01-poster-image`.
- `tests/ai/test_image_provider.py`, `tests/test_ticket108_fse01_poster_image.py`
  (nouveaux).

---

## 8. Lien à tester

- Page de cours FSE01 : **https://jury-central.lodylands.com/uaa/fse-fse01**

À vérifier en particulier (voir § 6, limite explicite) : rendu réel du mail et de la
publication sur téléphone (pas de défilement horizontal), lisibilité du schéma de
communication sur téléphone (les deux rendus, en réduisant la largeur du navigateur),
apparence de l'illustration de l'affiche et contraste du bandeau de slogan, rendu à
l'impression (Ctrl+P / aperçu).

---

## 9. Arrêt avant extension aux autres cours

Conformément à la demande, le travail s'arrête ici : FSE02-17 ne sont pas modifiés par ce
ticket. Les composants EmailCard/SocialPostCard/PosterCard sont documentés et réutilisables,
prêts à être appliqués aux autres cours sur confirmation visuelle explicite.
