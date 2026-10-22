# Ticket #65 — Bug rendu Markdown AMPCR : `> 2 To` transformé en encadré ATTENTION

Ticket : [#65](https://github.com/ReC82/jury-central/issues/65)

## Synthèse (mise à jour du 2026-10-22)

- **État réel : Installé — à tester.**
- **SHA installé :** `17ff0e843e9aa998cab5582c73db86a0192603af` (merge de la PR [#169](https://github.com/ReC82/jury-central/pull/169) sur `develop`).
- **Lien direct pour tester :** https://jury-central.lodylands.com/uaa/ampcr-mc08 — cours « Partitionnement, GPT/MBR et formatage », section « 4. Procédure / méthode ».
- **Procédure :** ouvrir la page, lire la phrase « (2) choisir GPT pour un usage moderne (UEFI, disque > 2 To), MBR seulement… » : elle doit être continue, dans un seul paragraphe, sans encadré « ⚠️ Attention » au milieu. Les vrais encadrés « Piège fréquent » des autres cours (ex. https://jury-central.lodylands.com/uaa/ampcr-mc01) doivent rester inchangés.
- **Décisions demandées au propriétaire :** Aucune décision utilisateur nécessaire.
- **Reste à faire :** rien pour ce ticket (validation visuelle par le propriétaire).

## Session du 2026-10-22 — le correctif n'atteignait pas le site

### Constat (réconciliation)

Le correctif de contenu du 2026-09-19 (section plus bas, livré via la PR #87) était bien dans `develop`, mais **le site servait toujours l'ancien texte** : `seed()` ne modifie jamais un bloc de cours déjà présent (pour ne pas écraser une édition faite depuis l'admin). Vérifié en lecture seule : le bloc « Cours de révision express » de MC08 contenait encore la ligne commençant par `> 2 To)`, et la page `/uaa/ampcr-mc08` rendait un `<blockquote>` (donc l'encadré ATTENTION).

La PR #89 (ouverte depuis le 2026-09-19, jamais fusionnée) visait ce problème mais remplaçait le bloc **entier** et mélangeait la correction MC04/SMART du ticket #83.

### Changements (PR #169)

- `app/seed.py` : nouvelle réparation ponctuelle `repair_mc08_greater_than_line`, appelée par `seed()`. Elle remplace **uniquement le fragment exact** d'avant correctif (4 lignes de la section « 4. Procédure / méthode » de MC08) par le fragment corrigé — mots identiques, seul le retour à la ligne est déplacé avant « disque ». Le reste du bloc n'est jamais touché ; un fragment déjà modifié depuis l'admin n'est pas trouvé, donc pas touché ; idempotent.
- `tests/test_ticket65_markdown_greater_than.py` : 4 tests ajoutés (l'ancien fragment reproduit bien le `<blockquote>` ; le fragment corrigé est celui du cours actuel ; remplacement ciblé qui conserve le reste du bloc et un vrai encadré « Piège fréquent », idempotence ; autre UAA et texte modifié jamais touchés).

### Installation et vérifications

- Sauvegarde de la base avant installation (`jury_central-pre-ticket65-*.db`, hors dépôt), fast-forward `b47f61e` → `17ff0e8`, seed idempotent : « Corrigé (« > 2 To » MC08…) : 1 bloc(s) » ; second seed : 0 bloc (idempotence vérifiée sur le site).
- Services `jury-central` et `jury-central-correction-worker` actifs, `/health` OK en local et en HTTPS.
- `/uaa/ampcr-mc08` : HTTP 200, 0 `<blockquote>` (contre 1 avant), texte « disque &gt; 2 To), MBR seulement… » dans le paragraphe.
- Compteurs utilisateurs / sessions / réponses identiques avant et après (18 / 71 / 584).
- Tests : fichier du ticket 10/10 ; `ruff check` des fichiers touchés : OK ; suite complète : 1917 passed, 1 failed — `test_ticket55_urgent_ampcr_full.py::test_json_autosave_api_never_reveals_correctness`, **instable et préexistant** (échoue 2 fois sur 15 sur `develop` sans ce changement : la première question MC01 est tirée au hasard et une réponse texte envoyée à une question non textuelle renvoie 422).
- Audit du contenu Informatique **réellement servi** (tous les blocs AMPCR de la base) : plus aucune ligne commençant par `>` au milieu d'un paragraphe. Les seules lignes `> nombre` restantes (MC01 « > 3,2 GHz », MC02 « > 16 lanes », « > 12V-2x6 ») font partie de vrais encadrés « Piège fréquent » où chaque ligne commence par `>` : rendu correct, rien à corriger. Aucune comparaison `< nombre` en début de ligne.
- Non effectué : contrôle visuel dans un navigateur (validation par le propriétaire).

### Choix techniques faits seul

- Remplacement du **fragment** plutôt que du bloc entier (contrairement à la PR #89) : préserve toute édition admin ailleurs dans le bloc, et ne peut rien écraser si le fragment a été modifié.
- Correction restée au niveau du contenu, sans toucher `render_markdown` ni `wrapBlockquotesAsWarningCards` : les vrais encadrés ATTENTION gardent exactement leur style (exigence du ticket).
- La partie MC04/SMART de la PR #89 relève du ticket #83 : non reprise ici. La PR #89 reste ouverte (non fermée par cette session) ; le ticket #83 pourra s'en servir ou la remplacer.

### Suites proposées (non implémentées)

- Rendre `test_json_autosave_api_never_reveals_correctness` déterministe (choisir une question textuelle) — instabilité de test signalée.
- Décider du sort de la PR #89 dans le cadre du ticket #83.

---

## Session du 2026-09-19 — correctif de contenu initial

**Branche :** `fix/65-markdown-greater-than`
**Base :** `develop` @ `486f35c4bcabc172e6f172c0250e073b6e03223b` (merge #81)
**Portée :** Informatique uniquement (Français en pause, cf. mission « PRIORITÉ FIABILITÉ AVANT EXAMEN »)

## Symptôme rapporté

Dans le contenu du cours MC08 (« Partitionnement, GPT/MBR et formatage »), la
comparaison numérique `disque > 2 To` se retrouvait affichée comme un encadré
rouge « ⚠️ Attention » séparé, au lieu de rester dans la phrase. Le texte de la
phrase était visuellement coupé en deux.

## Cause racine

Deux mécanismes combinés :

1. **Markdown standard** (bibliothèque `markdown`, utilisée telle quelle dans
   `app/content.py::render_markdown`, sans extension de citation
   personnalisée) : toute ligne commençant par `>` est syntaxiquement une
   citation (blockquote), qu'elle soit voulue ou non.
2. **`wrapBlockquotesAsWarningCards`** (`app/static/js/design_system.js`) :
   transforme *sans condition* chaque `<blockquote>` généré en encadré
   `jc-card--warning` « ⚠️ Attention ». Aucune distinction n'existe entre un
   encadré intentionnel et une ligne qui commence accidentellement par `>`.

Dans `app/v1/ampcr_courses.py` (MC08), la phrase de la section « 4. Procédure /
méthode » était repliée sur plusieurs lignes dans la chaîne Python source, et
le point de repli tombait juste avant `> 2 To` — plaçant ce `>` en tout début
de ligne rendue, donc interprété comme un marqueur de citation.

## Audit réalisé

Un audit systématique a été effectué sur l'ensemble du contenu Informatique
(`app/v1/ampcr_courses.py`, dict `AMPCR_COURSE_MARKDOWN`, tous les MC01–MC38)
et, pour référence de non-régression uniquement (aucune modification, Français
en pause), sur `app/seed.py` :

- **Occurrences de lignes commençant par `>`** : un seul cas trouvé dans tout
  le contenu Informatique — MC08, ligne « `> 2 To), MBR seulement... » — le
  bug rapporté. Aucun autre cas dans `AMPCR_COURSE_MARKDOWN`. Dans
  `app/seed.py` (Français, non modifié), tous les blocs `>` trouvés sont des
  encadrés « Piège fréquent »/« Piège majeur » intentionnels (chaque ligne du
  bloc commence par `>`, convention cohérente sur tout le fichier) — aucun bug
  supplémentaire détecté.
- **Occurrences de lignes commençant par `<`** : toutes des balises HTML brutes
  intentionnelles (`<div>`, `<svg>`, `<ol>`, `<li>`, etc.), aucune comparaison
  numérique du type `< 3 Go` repliée en début de ligne.

Conclusion : **un seul bug réel**, corrigé ci-dessous. Aucun autre encadré
ATTENTION intentionnel n'a été touché.

## Correctif

`app/v1/ampcr_courses.py` (MC08, section « 4. Procédure / méthode`) : reflow
du seul point de repli de ligne concerné, texte strictement identique (aucun
mot changé, aucune reformulation pédagogique — conforme à la règle « Claude ne
redéfinit jamais le contenu pédagogique »), simplement pour que `>` ne se
retrouve plus en début de ligne rendue.

Avant :
```
présente (opération destructive) ; (2) choisir GPT pour un usage moderne (UEFI, disque
> 2 To), MBR seulement pour une compatibilité ancienne spécifique ; (3) choisir le système
```

Après :
```
présente (opération destructive) ; (2) choisir GPT pour un usage moderne (UEFI,
disque > 2 To), MBR seulement pour une compatibilité ancienne spécifique ; (3) choisir
```

Aucune modification du moteur de rendu (`app/content.py`), du CSS
(`design-system.css`) ni du JS (`design_system.js`) : le correctif reste au
niveau du contenu, comme demandé par le ticket, et ne risque donc pas
d'altérer les vrais encadrés ATTENTION ailleurs dans l'application.

## Tests (`tests/test_ticket65_markdown_greater_than.py`, 6 tests)

1. `test_mc08_gpt_mbr_greater_than_comparison_stays_inline` — reproduit le cas
   exact du ticket : `render_markdown(AMPCR_COURSE_MARKDOWN["MC08"])` ne
   contient plus de `<blockquote>` et affiche `disque &gt; 2 To` inline.
2. `test_mc08_procedure_paragraph_is_a_single_unbroken_paragraph` — la phrase
   entière reste un unique `<p>…</p>`, non coupée en deux.
3. `test_no_accidental_blockquote_triggers_in_informatique_course_content` —
   garde de non-régression : scanne tout `AMPCR_COURSE_MARKDOWN` et échoue si
   une future modification de contenu réintroduit une ligne `>` accidentelle
   (aujourd'hui, aucun cours Informatique n'utilise de citation intentionnelle).
4. `test_no_line_start_angle_bracket_outside_known_html_blocks_in_informatique_content`
   — même garde pour `<`.
5. `test_intentional_attention_blockquotes_in_french_content_are_unaffected` —
   vérifie qu'un vrai encadré « Piège fréquent » (contenu Français, non
   modifié) continue à être rendu comme une vraie citation Markdown.
6. `test_no_accidental_blockquote_triggers_in_seed_content` — même audit que
   le test 3, appliqué au fichier `app/seed.py` existant (lecture seule, pas
   de modification) : confirme qu'aucun bug équivalent n'existe côté Français
   à ce jour.

## Décisions documentées / hors scope

- Le correctif est volontairement limité au contenu (pas de changement du
  pipeline de rendu), car (a) la seule occurrence réelle du bug en
  Informatique est corrigée avec un simple reflow, et (b) une modification du
  mécanisme `wrapBlockquotesAsWarningCards` ou de `render_markdown` risquerait
  de casser les vrais encadrés ATTENTION du contenu Français déjà en
  production — hors scope de cette mission (« Ne travaille PAS sur : Français »).
- Aucune modification apportée à `app/seed.py` (Français en pause) : l'audit y
  confirme l'absence de bug, sans y toucher.

## Validation

- `pytest -q` (suite complète) : voir bloc final de mission.
- `ruff check .` : 36 erreurs — identique à la baseline connue de `develop`
  (486f35c). 0 nouvelle dette sur les fichiers modifiés/ajoutés
  (`app/v1/ampcr_courses.py`, `tests/test_ticket65_markdown_greater_than.py`
  : 0 erreur).
- `git diff --check` : aucun problème d'espaces/fin de ligne.

## Fichiers modifiés

- `app/v1/ampcr_courses.py` (contenu MC08, reflow d'une ligne)
- `tests/test_ticket65_markdown_greater_than.py` (nouveau, 6 tests)
- `docs/claude-reports/2026-09-19_ticket-65_markdown-greater-than.md` (ce rapport)
