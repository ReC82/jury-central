# Ticket #18 — Bug mobile : menu hamburger ne s'ouvre pas

**Date** : 2026-09-16
**Branche** : `fix/18-mobile-menu-hamburger`
**Ticket GitHub** : #18 « Bug mobile — menu hamburger ne s'ouvre pas »
**Constat initial** : bouton hamburger visible sur staging (Chrome Android) mais inerte au toucher.

---

## 1. Résumé

Le bug n'était **pas** dans le markup de la navbar (déjà syntaxiquement correct) ni dans
le JavaScript du projet (aucun conflit, aucun gestionnaire interceptant le clic). La cause
était un attribut `integrity` (Subresource Integrity) **incorrect** sur le `<script>` qui
charge le bundle JS Bootstrap depuis le CDN, dans `app/templates/base.html`. Correction :
une seule ligne modifiée (la valeur du hash), aucun second menu mobile, aucune dépendance
ajoutée.

---

## 2. Démarche de diagnostic

Éléments explicitement demandés par le ticket, inspectés dans l'ordre :

1. **Template navbar/collapse** (`app/templates/base.html`) : markup relu intégralement.
   `data-bs-toggle="collapse"`, `data-bs-target="#navbarNav"`, `aria-controls="navbarNav"`,
   `id="navbarNav"` sur le `.collapse.navbar-collapse` — tout est cohérent et syntaxiquement
   conforme à Bootstrap 5.3.3. **Rien d'anormal ici.**
2. **Bootstrap CSS réellement chargé** : `<link>` CDN avec `integrity` — vérifié par
   recalcul du hash réel du fichier (voir § 3) : **correct**.
3. **Bootstrap JS réellement chargé (bundle)** : `<script>` CDN avec `integrity` — vérifié
   par recalcul du hash réel du fichier (voir § 3) : **incorrect**. C'est la cause.
4. **Ordre de chargement JS** : le bundle Bootstrap est chargé en fin de `<body>`, sans
   `defer` ni `async` — ordre correct, aurait fonctionné si le hash avait été bon.
5. **Conflits avec le JS Jury Central** : recherche exhaustive de
   `stopPropagation`/`preventDefault`/`stopImmediatePropagation` dans tous les fichiers
   `app/static/js/*.js` — **aucune occurrence**. Aucun gestionnaire de clic générique ne
   pouvait intercepter le clic sur le hamburger.
6. **CSS pouvant intercepter les clics/touch (z-index, pointer-events)** : recherche de
   `z-index`, `position: fixed/sticky`, `pointer-events` dans `design-system.css` et
   `style.css` — une seule occurrence (`.jc-lesson-progress`, barre de progression de
   lecture, `position: sticky; z-index: 5`), interne à `<main>`, sans recouvrement possible
   avec la navbar en haut de page. **Aucune interférence.**
7. **Erreurs JavaScript** : aucun outil de console disponible dans cet environnement
   serveur (voir § 6, limites) ; le raisonnement s'est donc appuyé sur la vérification
   directe du mécanisme SRI plutôt que sur l'observation d'une erreur console.

---

## 3. Cause exacte

L'attribut `integrity` du `<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js">`
dans `app/templates/base.html` ne correspondait pas au contenu réel du fichier.

Vérification reproduite par téléchargement direct du fichier exact (URL versionnée,
immuable) et calcul du hash SHA-384 réel :

```bash
curl -sL -o bootstrap.bundle.min.js \
  https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js
openssl dgst -sha384 -binary bootstrap.bundle.min.js | openssl base64 -A
```

| | Valeur |
|---|---|
| Hash attendu (template, avant correction) | `YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDwLef6MjxeMkbA0OCA34IdgeH+` |
| Hash réel du fichier (recalculé) | `YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz` |

Les deux valeurs partagent un préfixe identique (`YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55ND`)
puis divergent totalement — cohérent avec une erreur de transcription du hash à un moment
de l'historique du projet, pas une compromission de la CDN (le hash CSS, vérifié par la
même méthode sur la même CDN au même moment, était lui exact). Re-téléchargement effectué
deux fois pour confirmer la stabilité/reproductibilité du hash réel (fichier immuable,
identique à chaque requête).

**Mécanisme du bug** : quand `integrity` ne correspond pas au fichier téléchargé, le
navigateur **bloque silencieusement l'exécution du script** (Subresource Integrity), sans
alerte visible pour l'utilisateur — seule la console développeur affiche une erreur. Le
CSS Bootstrap (chargé séparément, intégrité correcte) continue d'afficher normalement le
bouton hamburger stylé ; mais le JavaScript Bootstrap (composant Collapse, qui écoute les
clics sur `[data-bs-toggle="collapse"]`) n'est jamais exécuté : le bouton est visuellement
présent mais fonctionnellement mort. Cela explique aussi pourquoi rien d'autre sur le
site n'était visiblement cassé : Jury Central n'utilise aucun autre composant JS Bootstrap
(pas de modal, tooltip, carousel...) — seul le hamburger dépend de ce script.

---

## 4. Correction

Une seule ligne modifiée, `app/templates/base.html` :

```diff
- integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDwLef6MjxeMkbA0OCA34IdgeH+"
+ integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz"
```

Aucune autre modification : le markup navbar/collapse était déjà correct et n'a pas été
touché ; aucun second menu mobile parallèle n'a été introduit (conforme à la consigne
explicite du ticket) ; le hamburger continue d'utiliser exactement le système de
navigation Bootstrap existant.

---

## 5. Fichiers

- `app/templates/base.html` — correction du hash `integrity`.
- `tests/test_navbar_mobile_menu.py` — nouveau, 5 tests de non-régression.
- `docs/changelog.md` — entrée de ticket.
- `docs/claude-reports/2026-09-16_ticket-18_mobile-menu.md` — ce rapport.

---

## 6. Tests automatiques

`tests/test_navbar_mobile_menu.py` (5 tests, tous parsent `app/templates/base.html`
directement, sans dépendance réseau) :

1. `test_bootstrap_bundle_script_tag_has_the_correct_integrity_hash` — régression
   directe sur la cause exacte : le hash figé dans le test (recalculé le 2026-09-16 depuis
   le fichier réel, méthode documentée dans le test) doit correspondre exactement à celui
   du template.
2. `test_bootstrap_bundle_script_is_not_deferred_or_async` — le script doit s'exécuter dès
   son chargement, avant tout clic possible.
3. `test_navbar_toggler_markup_matches_the_collapse_target` — cohérence
   `data-bs-toggle`/`data-bs-target`/`aria-controls`/id du `.collapse` ciblé.
4. `test_only_one_navbar_toggler_and_one_collapse_target_exist` — garde-fou explicite
   contre un contournement par un second menu mobile parallèle.
5. `test_navbar_uses_responsive_expand_breakpoint_for_mobile_widths` — `navbar-expand-md`
   confirmé (hamburger sous 768px, couvre les trois largeurs mobiles demandées par le
   ticket).

**Résultat** : `pytest -q` → **241 passed** (236 avant ce ticket + 5 nouveaux), 2 warnings
préexistants.

**Ruff** : `ruff check .` → **36 erreurs**, strictement identiques (mêmes fichiers, mêmes
règles) à celles de `develop` — comparé via un worktree isolé. **0 nouvelle erreur.**

---

## 7. Tests mobile

**Vérifié** (sans navigateur, au niveau HTML/CSS servi par le serveur réel, sur une base
SQLite temporaire isolée — jamais `jury_central.db`) :
- Le HTML servi par `/`, `/uaa/ampcr-mc01` etc. contient désormais le hash `integrity`
  corrigé (vérifié par `curl` sur le serveur de développement réellement démarré).
- Le markup hamburger reste exactement celui attendu :
  `data-bs-target="#navbarNav"` = `aria-controls="navbarNav"` = `id="navbarNav"`.
- `navbar-expand-md` (breakpoint 768px) confirmé dans le markup — couvre nativement les
  trois largeurs mobiles demandées (~360px, ~390px, ~430px), toutes inférieures à 768px :
  le hamburger y est affiché par le CSS Bootstrap (déjà vérifié intègre), sans code
  spécifique par largeur à maintenir.
- Aucune modification de CSS ou de layout : aucun risque de débordement horizontal
  introduit par ce correctif (une seule chaîne de caractères modifiée).

**Non vérifié — limite explicite** (voir § 8) : le clic/toucher réel du bouton et
l'ouverture/fermeture visuelle du menu sur un vrai moteur de rendu, aux largeurs exactes
360/390/430px, n'ont pas pu être exécutés dans cet environnement (aucun navigateur ni
outil d'automatisation disponible ici — voir § 8).

---

## 8. Tests desktop

**Vérifié** : `navbar-expand-md` signifie que dès 768px et au-delà, Bootstrap affiche la
navigation complète (`.navbar-collapse` visible en permanence) et masque le bouton
`.navbar-toggler` via son propre CSS (déjà vérifié intègre, non modifié par ce ticket).
Aucune régression possible côté desktop : ce comportement est entièrement géré par le CSS
Bootstrap standard, dont seule l'intégrité a été revérifiée (correcte, inchangée par ce
correctif). Le fix ne touche que le hash du **JS**, jamais le CSS ni le markup.

**Non vérifié visuellement** — même limite qu'au § 7.

---

## 9. Limites

- **Aucun navigateur ni outil d'automatisation (Playwright/Selenium/Chromium headless)
  n'est installé dans cet environnement serveur.** Installer un tel outil pour cette seule
  vérification aurait introduit une dépendance lourde, contraire aux conventions du projet
  (« vanilla JS, aucune dépendance npm », `docs/PROJECT_RULES.md`). Le diagnostic et la
  correction s'appuient donc sur la vérification **directe et rigoureuse** du mécanisme
  exact qu'un navigateur utilise pour décider d'exécuter ou non le script (comparaison
  SHA-384 octet pour octet), ce qui est plus précis qu'une simple observation visuelle —
  mais ne remplace pas un clic réel.
- **Recommandation explicite** : ChatGPT ou l'utilisateur doit valider visuellement
  l'ouverture/fermeture du menu sur un vrai téléphone (ou DevTools responsive) après
  déploiement sur staging, aux largeurs 360/390/430px, avant de considérer le ticket
  entièrement clos côté UX — la correction technique est certaine (cause confirmée par
  calcul de hash), la confirmation visuelle finale reste à faire.
- Si la version de Bootstrap est mise à jour à l'avenir, le hash `integrity` (CSS **et**
  JS) devra être recalculé par la même méthode (`openssl dgst -sha384`) et le test
  `test_bootstrap_bundle_script_tag_has_the_correct_integrity_hash` mis à jour en
  conséquence — documenté dans le docstring du fichier de test.

---

## Statut

Correction terminée jusqu'au commit + push. Aucun merge, aucun déploiement. En attente de
validation visuelle par ChatGPT/l'utilisateur sur staging (voir § 9).
