# Ticket #67 — UX navigation : accueil par parcours CESS → CESS P → Informatique

**Date** : 2026-09-18
**Branche** : `feature/67-home-navigation`

---

## 1. Contexte

Le moteur Informatique (AMPCR, tickets #55→#66) est désormais fonctionnel et validé en
staging. Ce ticket est une passe UX COURTE, strictement limitée à la navigation/accueil :
**aucune modification** de génération, correction, banque, rating, admin ou paiement.

---

## 2. Header (§ 1/2)

`app/templates/base.html` :

- Lien global **« S'entraîner »** (`/practice/equations`) **supprimé** du header — la
  route elle-même n'est PAS supprimée (`app/templates/practice_equations.html` inchangé,
  toujours servie), seulement retirée de la navigation globale, conformément à « l'entraînement
  doit se lancer depuis une matière/cours, pas depuis le menu global ».
- Menu résultant, dans l'ordre demandé : Accueil, Matières, (si connecté) Mes
  entraînements, compte utilisateur, Déconnexion.
- **Déconnexion** restylée : `btn btn-sm jc-nav-logout` (nouvelle classe, `app/static/css/
  design-system.css`) — pilule discrète alignée avec le reste du header, bordure/texte
  semi-transparents au repos, contraste plein au survol/focus (`:hover`/`:focus-visible`),
  `outline` explicite au focus clavier. Toujours un `<button type="submit">` dans le même
  `<form>` CSRF qu'avant (aucun changement de mécanique, seulement de rendu) — jamais un
  bouton d'action primaire (`btn-primary`).

---

## 3. Page d'accueil et parcours par tuiles (§ 3/4/5)

Nouveau module **`app/programs.py`** : arborescence CESS → filière → matière, **statique**
(dataclasses figées, aucune nouvelle table SQL) — réutilise la hiérarchie déjà existante
(`app.models.Subject`) pour tout ce qui a un contenu réel, plutôt que de la dupliquer.
Seules la filière **P** et la matière **Informatique** sont `available=True` aujourd'hui ;
G/TTR/TQ et Français/Maths/Sciences existent dans la structure (§ 5 : « prévoir sans
implémenter ») mais ne sont jamais des liens cliquables côté template — un badge « Bientôt
disponible » les affiche sans jamais mener à un lien mort.

Nouvelles routes (`app/main.py`) :

- `GET /` — accueil, une seule tuile **CESS** (remplace le message « application en cours
  de construction »).
- `GET /cess` — tuiles filières (P cliquable → `/cess/p`, G/TTR/TQ non cliquables).
- `GET /cess/{filiere_slug}` — 404 si la filière est inconnue ; matières de la filière
  sinon (tuiles, seule celle avec `available=True` est cliquable).
- `GET /cess/{filiere_slug}/{subject_slug}` — 404 si filière OU matière inconnue de
  `app.programs` ; pour la matière **disponible** (informatique), rend la page AMPCR
  (§ 4 ci-dessous) ; pour une matière **annoncée mais non câblée** (français/maths/
  sciences), une page d'attente explicite (200, jamais un 404 brut).

Parcours exact demandé : Accueil → CESS → CESS P → Informatique → AMPCR (existant).

---

## 4. Page Informatique (§ 9)

`app/templates/cess_informatique.html` affiche clairement **« Assistant/Assistante de
maintenance PC-réseaux (AMPCR) »** avec trois actions vers les routes **déjà existantes**
(ticket #55, aucune nouvelle logique de session) :

- **Cours** → `/modules/ampcr` (liste des 38 mini-cours, inchangé)
- **S'entraîner** → `/modules/ampcr/practice` (examen blanc global, inchangé)
- **S'évaluer** → `/modules/ampcr/exam` (examen blanc global, inchangé)

**Aucun second moteur de navigation** : cette page ne fait que rendre ces routes plus
faciles à découvrir depuis l'accueil, elle ne réimplémente ni ne contourne la sélection/
composition de session (`app.v1.session_service`, non touché par ce ticket).

---

## 5. Breadcrumb (§ 7)

`CESS > CESS P > Informatique` sur les 3 nouvelles pages (`cess_filiere.html`,
`cess_informatique.html`, `cess_subject_soon.html`). Les breadcrumbs déjà existants sur
les pages de cours (`uaa_detail.html`, `module_detail.html`, `subject_detail.html`)
restent **strictement inchangés** — aucun de ces gabarits n'a été modifié par ce ticket.

---

## 6. Design (§ 6)

Nouvelles classes dans `app/static/css/design-system.css` (section « Tuiles de parcours
CESS ») : `.jc-tile-grid` (grille CSS, **une colonne par défaut**, deux colonnes à partir
de 576px — mobile-first), `.jc-tile` (grande tuile simple, peu de texte, `min-height`
généreux pour un tap-target confortable), `.jc-tile-soon` (variante grisée non cliquable).
Réutilise les tokens de couleur déjà définis (`--jc-blue`, `--jc-gray`, `--jc-gray-bg`) et
le composant `.jc-card`/`.jc-card--theory` déjà existant pour la carte AMPCR — **aucune
nouvelle librairie**, Bootstrap 5.3.3 (CDN déjà en place) inchangé. Le reste du design
(cartes de leçon, navigation d'espace Cours/S'entraîner/S'évaluer par UAA, etc.) n'est pas
retouché.

---

## 7. Routes — audit et compatibilité (§ 8)

Routes existantes auditées avant d'ajouter quoi que ce soit : `/`, `/subjects`,
`/subjects/{slug}`, `/modules/{slug}`, `/uaa/{slug}`, `/uaa/{slug}/practice`,
`/uaa/{slug}/exam`, `/modules/ampcr/practice`, `/modules/ampcr/exam`, `/mes-sessions`,
`/sessions/{id}/...` (toutes dans `app/main.py`/`app/v1/routes_sessions.py`). **Aucune
route existante renommée, supprimée ou redirigée** — les nouvelles routes `/cess`,
`/cess/{filiere}`, `/cess/{filiere}/{matiere}` s'ajoutent, elles ne remplacent rien.
`/practice/equations` reste servie (seulement retirée du header, § 2).

---

## 8. Tests

Nouveau fichier **`tests/test_ticket67_home_navigation.py`** (31 tests) :

- Parcours CESS → CESS P → Informatique → AMPCR (tuiles cliquables/non-cliquables,
  contenu de la page Informatique, breadcrumb).
- 404 pour filière/matière réellement inconnue ; page d'attente (200) pour une matière
  annoncée mais non câblée, ou une filière annoncée mais non disponible — jamais de 404
  sur une entrée réelle de `app.programs`.
- Header : lien « S'entraîner » absent partout, route `/practice/equations` elle-même
  toujours servie ; « Mes entraînements »/Déconnexion présents seulement connecté,
  Connexion/Créer un compte sinon ; classe `jc-nav-logout` présente, jamais `btn-primary`.
- Non-régression : `/subjects`, `/subjects/informatique`, `/modules/ampcr` toujours 200 ;
  cours UAA publics sans connexion ; practice/exam (par UAA et global AMPCR) toujours
  redirigés vers `/login` sans session ; cycle inscription → session active → déconnexion
  → routes protégées de nouveau refusées.
- Mobile : balise viewport présente sur les 4 nouvelles pages ; absence de largeur fixe
  imposée susceptible de provoquer un débordement horizontal ; grille CSS `.jc-tile-grid`
  vérifiée à une colonne par défaut.
- `app.programs` : unitaire pur (quelles entrées sont `available`, helpers
  `get_filiere`/`get_subject_link`).

`pytest -q` (suite complète) : **984 passed** (953 baseline ticket #64 + 31 nouveaux),
`0 failed`. Ruff : **36 erreurs, 0 nouvelle** (baseline inchangée — une nouvelle route
suit le même style `Depends(get_db)` déjà utilisé sans suppression ailleurs dans
`app/main.py`, donc marquée `# noqa: B008` comme les routes équivalentes de
`app/v1/routes_sessions.py`, pour ne pas ajouter de dette). `git diff --check` : propre.

---

## 9. Limites assumées

- **Aucune vérification automatisée du rendu visuel réel** (pas de navigateur/capture
  d'écran dans cette validation) — la conformité mobile est vérifiée structurellement
  (viewport, absence de largeurs fixes, grille CSS responsive documentée), pas visuellement ;
  une vérification manuelle sur staging reste recommandée avant diffusion large, comme pour
  tout le reste de l'UI du projet.
- **Français/Maths/Sciences et CESS G/TTR/TQ** : structure prête (`app.programs`), aucun
  contenu ni câblage — conforme à la demande explicite « prévoir sans implémenter ».
- **Mathématiques (legacy)** : le contenu existant (`/subjects/mathematiques`, MB32/MQ32/
  MQ34) reste accessible via l'ancienne route, mais n'est PAS encore rattaché à la tuile
  « Mathématiques » de CESS P (marquée `available=False`) — le ticket ne demandait que
  l'activation d'Informatique ; rattacher Mathématiques à ce nouvel arbre est une décision
  pédagogique/produit hors périmètre de cette passe UX, laissée à un futur ticket explicite.

---

## Statut

Implémentation, tests et documentation terminés. `pytest -q` (suite complète) : 984
passed. Ruff : 36 erreurs, 0 nouvelle. `git diff --check` : propre. Prêt pour commit/push.
**Aucun merge, aucun déploiement.** Génération/correction/banque/rating/admin/paiement
non touchés ; le Français (`feature/47-francais-v1`) n'a pas été touché.
