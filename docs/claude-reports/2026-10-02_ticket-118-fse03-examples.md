# Rapport — Ticket #118 : exemples réalistes de FSE03 (Sophie Lambert)

Branche : `feature/118-fse03-examples` (depuis `develop`). PR #119 fusionnée dans
`develop`, puis installée sur `jury-central.lodylands.com`.

**SHA installé : `abee3e2`** (merge commit de la PR #119). Correction ciblée intégrée au
travail d'extension FSE02-17 déjà en cours (ticket #115) — aucun cours déjà terminé n'a été
repris depuis le début, conformément à la demande.

---

## 1. Les cinq traces de Sophie Lambert, devenues des documents visibles

L'ancienne liste numérotée ( « 1. Une photo de profil... 2. Une photo prise lors d'un
anniversaire... » ) devient cinq documents distincts, chacun avec sa propre carte :

1. **Profil professionnel** (`.jc-profile-head`/`.jc-profile-portrait`, nouveau) : portrait
   illustré généré, nom, fonction, résumé de parcours — carte de réseau professionnel.
2. **Publication d'anniversaire** (réutilise `SocialPostCard`) : illustration générée
   (Sophie avec deux amies, soirée extérieure, gâteau), publiée par « Une amie de Sophie »,
   horodatage « il y a deux ans », mention neutre « Sophie Lambert identifiée sur la
   photo ».
3. **Ancien commentaire** : vraie carte de forum de jeu vidéo (`.jc-doc-meta`), auteur
   « Sophie Lambert », « il y a cinq ans », un commentaire représentatif du ton décrit dans
   le texte source (familier, rude envers d'autres joueurs, sans langage explicitement
   injurieux — resté approprié pour une plateforme pédagogique).
4. **Recommandation** (réutilise `QuoteCard`) : citation attribuée à « Un ancien collègue de
   Sophie ».
5. **Groupes** (`.jc-group-cards`/`.jc-group-card`, nouveau) : deux cartes distinctes avec
   icônes (🥾 randonneurs, 📦 gestionnaires de stock).

**Vérification explicite demandée et effectuée** : aucune classification pédagogique
(volontaire/involontaire) n'apparaît sur les documents eux-mêmes — un test automatisé
dédié confirme qu'aucune occurrence du mot « volontaire » n'apparaît entre les cinq
documents et le titre « 🔍 Décryptons ce document » qui introduit l'analyse. Les
classifications restent exclusivement dans cette analyse, inchangée dans son contenu.

---

## 2. Note RH devenue un e-mail interne crédible

Réutilisation du composant `EmailCard` (déjà existant depuis FSE01) : expéditeur fictif
(Julie Petit, service recrutement) et destinataire fictif (Marc Dubois, responsable
recrutement), objet « Préparation de l'entretien — Sophie Lambert », date cohérente (9
avril 2026, veille de l'entretien mentionné dans le texte), contenu identique au texte
d'origine mais aéré en paragraphes, signature professionnelle. Document et analyse
« Décryptons ce document » restent clairement séparés. Mention « Document pédagogique
fictif » explicite dans l'étiquette d'en-tête (remplace le simple « Fictif » générique pour
ce document).

---

## 3. Illustrations générées — accès vérifié, cohérence du personnage

### Accès et vérification technique préalable

Avant toute génération réelle pour ce ticket, vérification empirique de la fonctionnalité
d'édition d'image avec référence (`POST /v1/images/edits`) : un test à faible coût (cercle
rouge + ajout d'un carré bleu) a confirmé que l'API conserve bien l'élément de référence et
compose une nouvelle scène autour, avant tout usage sur le contenu réel.

### Deux images générées, un seul personnage

- **Portrait professionnel** : `POST /v1/images/generations`, réussi à la première
  tentative.
- **Scène d'anniversaire** : `POST /v1/images/edits`, en utilisant le portrait **comme
  image de référence** (nouvelle méthode `ImageProvider.edit_image`, ticket #118) — c'est
  ce qui garantit visuellement la même personne dans les deux images (même visage, mêmes
  cheveux, même tenue), plutôt que deux générations indépendantes à partir du seul texte,
  qui auraient presque certainement produit deux apparences différentes.

Un paramètre `input_fidelity` (censé renforcer la fidélité au personnage de référence,
documenté par OpenAI) a été testé mais **rejeté par les deux modèles disponibles sur ce
compte à ce jour** (`gpt-image-2.5-flare` et `gpt-image-2.5-sunburst`, erreur
`invalid_input_fidelity_model`) — un écart entre la documentation et le comportement réel
de l'API, constaté et contourné proprement (paramètre omis, code adapté pour le rendre
optionnel). La cohérence du personnage repose donc sur l'image de référence transmise à
`/v1/images/edits` (confirmée suffisante par le résultat obtenu, voir ci-dessous) et sur la
description textuelle détaillée du personnage, répétée dans les deux prompts.

**Résultat obtenu, inspecté visuellement** : la scène d'anniversaire montre bien la même
femme que le portrait (mêmes cheveux bruns mi-longs, même visage, même blazer bleu
canard), entourée de deux amies, avec gâteau et guirlande lumineuse — succès dès la
première tentative de génération de contenu réelle (deux appels ont été nécessaires en
tout, mais le premier a échoué pour un problème de paramètre technique avant toute
génération, pas pour une image jugée inutilisable — conforme à l'esprit de la règle « une
seconde tentative seulement si nécessaire », qui vise les échecs de génération, pas les
erreurs de requête corrigées en cours de développement).

### Conservation et contrôle d'appels

- **Aucun appel API à l'ouverture du cours ni au seed/déploiement** : les deux images sont
  des fichiers statiques (`app/static/img/fse03_sophie_portrait.png`,
  `fse03_sophie_birthday.png`), commitées dans le dépôt — apportées sur le serveur de
  production par un simple `git fetch`/`merge --ff-only`, zéro appel OpenAI effectué sur le
  serveur.
- **Métadonnées conservées** : fichiers sidecar JSON par image (prompt exact, modèle,
  taille, qualité, horodatage ; la scène d'anniversaire précise en plus l'image de
  référence utilisée et le statut du paramètre `input_fidelity`).
- **Remplacement manuel** : nouvelle commande `generate-fse03-sophie-images --force`.
- **Rendu de secours** : un SVG générique (silhouette) remplace chaque image en cas
  d'absence du fichier — non déclenché ici, les deux images existent et sont servies.

---

## 4. Dimensions et adaptation

- Portrait : cercle de 4,5rem (72px), accompagne la carte sans la dominer.
- Illustration d'anniversaire : largeur maximale 320px (`jc-doc-scene-image`), centrée,
  réduite à 220px à l'impression (`@media print`).
- Les deux images sont agrandissables au clic (réutilisation du mécanisme `.jc-zoomable`
  déjà existant depuis le ticket #110) pour l'illustration d'anniversaire.
- Cartes de groupe et carte de profil utilisent les grilles déjà responsives du Design
  System (`repeat(auto-fit, minmax(...))`), qui s'empilent naturellement sur téléphone.

---

## 5. Tests exécutés (ciblés, pas la suite complète de 1 419 tests)

| Lot | Résultat |
|---|---|
| `tests/test_ticket97_fse02_04.py`, `test_card_kind.py`, `test_admin_content_hierarchy.py` | 58/58 ✅ |
| `tests/test_ticket102_coverage.py` | 52/52 ✅ |
| `tests/ai/test_image_provider.py` (6 nouveaux cas pour `edit_image`, aucun appel réseau réel) | 9/9 ✅ |
| `tests/test_ticket118_fse03_sophie_images.py` (nouveau, 6 cas : génération + réutilisation du portrait comme référence, échec sans fichier partiel, retry unique, `--force`, isolation `tmp_path`) | 6/6 ✅ |
| `tests/test_ticket108_fse01_poster_image.py` (non-régression du mécanisme sœur, FSE01) | 5/5 ✅ |

Exécutés sur la branche avant fusion, puis sur le checkout de production après
fast-forward, avant le seed.

**Vérification structurelle de la page réelle en production** (`/uaa/fse-fse03`) : les 6
documents présents avec leurs identifiants d'ancre, portrait et illustration d'anniversaire
servis en 200 avec le contenu binaire exact (926 671 et 1 160 133 octets), mention
« Document pédagogique fictif » présente, aucun rendu de secours déclenché, aucune liste
Markdown cassée.

**Prévisualisation visuelle locale** (HTML réel → PDF → image, WeasyPrint, outil de
développement uniquement, jamais une dépendance du projet) des six documents et de
l'e-mail — rendu conforme à la description, portrait et scène correctement dimensionnés,
e-mail aéré et lisible.

**Limite explicite, identique aux rapports précédents** : aucun navigateur réel (Chrome/
Firefox headless, Playwright) disponible dans cet environnement — l'agrandissement au clic
de l'illustration d'anniversaire n'a pas pu être testé en conditions réelles (seule la
logique CSS/JS, déjà utilisée et vérifiée pour l'affiche FSE01, a été relue). La
vérification visuelle finale sur ordinateur, téléphone et à l'impression reste à faire par
l'utilisateur.

**Comptes et données vérifiés intacts** après le seed de production : 18 utilisateurs, 67
sessions, 536 réponses — identiques avant/après. Sauvegarde de `jury_central.db` effectuée
avant le seed : `jury_central.db.bak-pre-ticket118-<horodatage>`.

---

## 6. Fichiers modifiés/créés

- `app/ai/image_provider.py` — nouvelle méthode `edit_image()` (`POST /v1/images/edits`,
  jusqu'à 16 images de référence, ici une seule).
- `app/v1/fse03_image.py` (nouveau) — génération et persistance des deux illustrations.
- `app/v1/fse03_content.py` — cinq documents + e-mail RH (textes bruts inchangés).
- `app/v1/fse03_course.py` — intégration des nouveaux documents dans les exemples.
- `app/static/css/design-system.css` — `.jc-profile-*`, `.jc-doc-scene-image`,
  `.jc-doc-tag`, `.jc-group-cards`/`.jc-group-card`.
- `app/static/img/fse03_sophie_{portrait,birthday}.{png,json}` (nouveaux).
- `docs/components/ProfileAndGroupCards.md` (nouveau), `INDEX.md` mis à jour.
- `pyproject.toml` — script `generate-fse03-sophie-images`.
- `tests/ai/test_image_provider.py`, `tests/test_ticket118_fse03_sophie_images.py`
  (nouveaux).

---

## 7. Lien à tester

- Page de cours FSE03 : **https://jury-central.lodylands.com/uaa/fse-fse03**

À vérifier en particulier : apparence du portrait et de l'illustration d'anniversaire
(cohérence du personnage), agrandissement au clic de l'illustration, lisibilité de l'e-mail
RH sur téléphone, rendu à l'impression des six documents.

---

## 8. Suite

Le ticket #115 (extension FSE02-17) reprend là où il en était — FSE02, FSE04, FSE07 et
FSE16 restent inchangés par ce correctif, FSE03 est maintenant au niveau de qualité visé
pour les deux niveaux (structure ET documents réalistes).
