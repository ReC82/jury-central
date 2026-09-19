# Ticket #84 — Lexique AMPCR : acronymes, abréviations et vocabulaire FR/EN

**Portée :** intégré directement dans `integration/informatique-6-tickets` (puis `develop`).

## Objectif

Ressource pédagogique accessible depuis Informatique → AMPCR → Lexique / Acronymes FR-EN
(`/modules/ampcr/lexicon`, connexion requise — mêmes règles d'accès qu'une page de cours),
utilisable comme fiche de révision, et intégrée comme source pédagogique autorisée pour la
garde § 83.B (ticket #83, ce même cycle).

## § 84.A — Structure par thèmes

`app/v1/lexicon.py::LEXICON_THEMES` — les 11 thèmes exacts du ticket, dans l'ordre. Deux
thèmes (« Dépannage », « Sauvegarde / données ») restent structurellement présents mais
vides : aucun acronyme de la liste minimale du ticket ne s'y rattache naturellement sans
inventer une entrée artificiellement (cohérent avec § 84.C, voir plus bas).

## § 84.B — Champs d'une entrée

`LexiconEntry` : `acronym`, `english`, `french_term`, `definition`, `context`,
`confusion`, `mc_codes`. Chaque définition/contexte/piège est une reformulation FIDÈLE et
courte du texte déjà présent dans `app.v1.ampcr_courses.AMPCR_COURSE_MARKDOWN` — jamais un
contenu inventé (règle du projet : « Claude ne redéfinit jamais le contenu pédagogique »).
Chaque entrée cite le(s) MC d'origine.

## § 84.C — Entrées minimales : audit d'exhaustivité

Recherche exhaustive (regex, mot entier, insensible à la casse) des 45 acronymes de la
liste minimale du ticket dans tout `AMPCR_COURSE_MARKDOWN` + tous les objectifs de MC
(`_OBJECTIVES_BY_CODE`) :

| Absent du programme AMPCR actuel | Décision |
|---|---|
| ROM | Non inclus |
| WLAN | Non inclus (le programme dit « Wi-Fi », jamais littéralement « WLAN ») |
| IPv6 | Non inclus (programme IPv4 uniquement — MC16-18) |
| FTP | Non inclus |
| CLI | Non inclus (le programme dit « ligne de commande », jamais littéralement « CLI ») |
| GUI | Non inclus (le programme dit « interface graphique », jamais littéralement « GUI ») |

Ces 6 acronymes sont **volontairement absents** du lexique, conformément à la règle
explicite du ticket : « Ne pas ajouter une entrée uniquement parce qu'elle est connue en
informatique. Elle doit être présente dans : les cours ; le programme ; ou les questions
réellement autorisées. » Les 39 acronymes restants de la liste minimale ont chacun été
vérifiés présents et sont tous inclus, avec au moins un MC de rattachement réel — total
**40 entrées** (« exFAT » compte pour le 40e).

## § 84.D — Recherche

Champ `<input type="search">` avec filtrage JS instantané côté client (`input` event,
correspondance sous-chaîne insensible à la casse sur acronyme + anglais + français +
définition + contexte). Aucune dépendance externe, aucun appel réseau — cohérent avec
« si simple ».

## § 84.E — Impression / mobile

CSS `@media print` dédié (masque la barre de recherche, évite les coupures de thème entre
deux pages, format A4). Bouton « Imprimer / PDF » explicite (`window.print()`, même
convention que `v1_session_results.html`). Mise en page en grille Bootstrap
(`col-12 col-md-6`), donc lisible sur téléphone (une colonne) comme sur desktop (deux
colonnes) sans CSS supplémentaire.

## § 84.F — Intégration avec #83

`app/v1/lexicon.py::lexicon_defined_notions()` — retourne l'ensemble des 40 acronymes du
lexique. `app/v1/course_coverage.py::defined_notions_for_code` l'inclut désormais
systématiquement (import différé pour éviter toute dépendance d'ordre de chargement entre
les deux modules) : une question qui demande le développé d'un acronyme listé dans le
lexique n'est plus jamais rejetée par la garde § 83.B, même si le cours du MC concerné ne
l'explique pas en détail lui-même.

**Preuve concrète** : l'audit § 83.A avait trouvé que « CPU » n'est expliqué nulle part
dans le cours MC01, un gap resté non corrigé (aucun mandat explicite pour réécrire MC01).
Depuis l'intégration du lexique, `check_course_coverage_gap` accepte désormais
« Que signifie l'acronyme CPU ? » sur MC01 — le lexique ferme ce gap sans qu'aucun
contenu de cours n'ait dû être réécrit (test dédié :
`test_lexicon_closes_the_cpu_gap_found_in_ticket_83_audit`).

## Navigation

`app/templates/module_detail.html` : bouton « 📖 Lexique / Acronymes FR-EN » affiché
uniquement quand `module.code == "AMPCR"` (jamais sur Mathématiques/Français).

## Tests (`tests/test_ticket84_ampcr_lexicon.py`, 18 tests)

Structure des 11 thèmes, unicité des acronymes, champs obligatoires par entrée, fidélité
de l'entrée SMART au cours, exclusion vérifiée des 6 acronymes absents du programme,
sous-ensemble strict de la liste minimale du ticket, intégration avec la garde § 83.B
(notions disponibles même hors du MC d'origine, fermeture du gap CPU), route HTTP
(connexion requise, rendu correct, champ de recherche, bouton impression, codes MC
affichés), lien de navigation conditionnel depuis `module_detail.html`.

## Fichiers

- `app/v1/lexicon.py` (nouveau, 40 entrées / 11 thèmes)
- `app/v1/routes_lexicon.py` (nouveau, route `/modules/ampcr/lexicon`)
- `app/templates/v1_lexicon.html` (nouveau)
- `app/templates/module_detail.html` (lien conditionnel AMPCR)
- `app/main.py` (câblage du routeur)
- `app/v1/course_coverage.py` (déjà câblé pour consommer le lexique, voir #83)
- `tests/test_ticket84_ampcr_lexicon.py` (nouveau, 18 tests)
- `docs/claude-reports/2026-09-19_ticket-84_lexique-ampcr.md` (ce rapport)
