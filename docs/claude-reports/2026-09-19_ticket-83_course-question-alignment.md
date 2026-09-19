# Ticket #83 — Alignement pédagogique cours ↔ questions

**Portée :** intégré directement dans `integration/informatique-6-tickets` (puis `develop`).

## Problème réel

« Que signifie l'acronyme SMART ? » a été posée alors que MC04 utilisait SMART comme
indicateur de santé du disque sans jamais donner son développé (*Self-Monitoring,
Analysis and Reporting Technology*). Règle produit : une question ne peut demander une
connaissance que si elle est enseignée dans le cours du MC, ou dans une ressource
transverse autorisée (lexique AMPCR, #84).

## § 83.A — Audit MC01→MC38

**Méthode** (structurelle, pas de NLP — cf. § 83.B du ticket) : les questions
Informatique sont générées par IA à l'exécution, sans banque statique à auditer
directement (confirmé lors de l'audit qualité Phase 7 du cycle précédent). L'audit porte
donc sur l'écart entre (a) les acronymes/termes mentionnés dans l'**objectif exact** de
chaque MC (`app/v1/ampcr_plan.py::_OBJECTIVES_BY_CODE`, transmis verbatim par le chef de
projet) et (b) les acronymes/termes **réellement expliqués** dans le texte du cours
correspondant (`app/v1/ampcr_courses.py`), détectés par un motif structurel (`**X**
(développé)` ou `**X** : définition` — la convention d'écriture observée sur tout le
corpus).

**Rapport** (QUESTION illustrative → NOTION → MC → COVERED_BY_COURSE → COVERED_BY_LEXICON → GAP) :

| QUESTION (illustrative) | NOTION | MC | COVERED_BY_COURSE | COVERED_BY_LEXICON | GAP |
|---|---|---|---|---|---|
| Que signifie l'acronyme SMART ? | SMART | MC04 | ~~NON~~ → **OUI (corrigé § 83.C)** | OUI (#84) | Résolu |
| Que signifie l'acronyme CPU ? | CPU | MC01 | NON (jamais développé dans le corpus) | OUI (#84) | Couvert par le lexique |
| Que signifie l'acronyme GPU ? | GPU | MC01, MC29 | NON | OUI (#84) | Couvert par le lexique |
| Que signifie l'acronyme DDR3 ? | DDR3 | MC03 | NON | NON | **GAP résiduel** |
| Que signifie l'acronyme ITX ? | ITX (Mini-ITX) | MC02 | NON (utilisé comme nom de format, jamais développé) | NON | **GAP résiduel** (mineur — fonctionne comme un nom propre de facto) |
| Que signifie RFC1918 ? | RFC1918 | MC16 | NON (le concept — plages privées — est enseigné, le terme littéral « RFC1918 » ne l'est pas) | NON | **GAP résiduel** |
| Que signifie l'acronyme RDP ? | RDP | MC21 | Partiel (présent dans un tableau de ports, jamais développé en toutes lettres) | OUI (#84) | Couvert par le lexique |
| Que signifie l'acronyme SSH ? | SSH | MC21 | Partiel (idem RDP) | OUI (#84) | Couvert par le lexique |
| Que signifie l'acronyme RJ45 ? | RJ45 | MC37 | NON (utilisé comme nom de connecteur, jamais développé) | NON | **GAP résiduel** (mineur — nom propre de facto) |

**Notions vérifiées comme réellement couvertes** (faux positifs d'un premier passage
d'audit moins précis, corrigés avant ce rapport final) : SATA, ATX, EPS, RJ45→ voir
ci-dessus, OSI, M.2, WEP/WPA/WPA2/WPA3, CMD, FAT32, EFI, DISM, DORA, RJ45(connecteur),
MAC, DNS, DHCP — toutes expliquées dans leur cours respectif, simplement via des
formulations variées (définition en deux-points, description en prose) que le premier
passage d'audit (regex trop strict) ne détectait pas.

**Décision produit documentée (non bloquante, § « Ne fais PAS du NLP complexe »)** :
seul SMART/MC04 a été explicitement demandé pour un correctif de contenu (§ 83.C,
appliqué). Les gaps résiduels (CPU, GPU, DDR3, ITX, RFC1918, RJ45) ne sont **pas**
réécrits ici sans mandat explicite (« Claude ne redéfinit jamais le contenu
pédagogique ») — ils sont (a) documentés dans ce rapport pour le chef de projet, et (b)
déjà neutralisés opérationnellement par la garde § 83.B ci-dessous : toute question qui
demanderait leur développé est rejetée avant persistance, qu'un contenu de cours les
couvre ou non. CPU/GPU/RDP/SSH sont en outre déjà couverts par le lexique AMPCR livré en
§ 84.

## § 83.B — Garde serveur (`app/v1/course_coverage.py`)

Nouveau module, même registre extensible que `app.v1.domain_validation` /
`app.v1.quality_validation` :

- `_extract_defined_notions(markdown) -> frozenset[str]` : extraction structurelle
  (regex, aucune compréhension sémantique) des acronymes/termes expliqués dans un texte
  de cours.
- `defined_notions_for_code(code) -> frozenset[str]` : notions autorisées pour un MC —
  celles de son propre cours **+ celles du lexique AMPCR transverse** (#84 § F, import
  différé pour éviter toute dépendance d'ordre de chargement).
- `check_course_coverage_gap(module, uaa, question_type, content_json) -> list[str]` :
  détecte un motif de question typique (« que signifie X », « que veut dire X », « que
  représente l'acronyme X »...) et rejette (`COURSE_COVERAGE_GAP`) si l'acronyme visé
  n'est ni dans le cours du MC ni dans le lexique. Enregistrée dans
  `QUALITY_VALIDATORS` (`app/v1/quality_validation.py`) — donc appliquée par le même
  rejet dur déjà en place dans `app/v1/bank.py:392` pour toute question générée,
  **sans restriction de type** (contrairement aux règles § 69, une question
  `vocabulary`/`true_false`/`short_answer` peut tout autant demander un développé
  d'acronyme qu'un QCM).

**Prompt renforcé** (`app/v1/ampcr_plan.py::_detailed_context`) : `vocabulary` (jusque là
toujours `[]` pour MC04-38) porte désormais la liste réelle des notions expliquées dans
le cours du MC — le générateur dispose ainsi d'une liste positive explicite de ce qu'il
peut développer, en plus de l'instruction ajoutée à `constraints` : « ne demande JAMAIS
la signification/le développé d'un acronyme... qui n'apparaît pas dans le Vocabulaire
attendu ». Défense en profondeur : prompt (préventif) + garde serveur (rejet dur,
indépendant de ce que produit réellement le modèle).

## § 83.C — MC04 enrichi

`app/v1/ampcr_courses.py`, MC04 § 2 « Définitions essentielles » : SMART développé en
« Self-Monitoring, Analysis and Reporting Technology », définition simple (technologie de
surveillance de l'état du stockage), explique température/secteurs-erreurs/heures de
fonctionnement/indicateurs de santé/utilité diagnostic, précise qu'elle ne garantit pas
de prédire toutes les pannes et ne remplace jamais une sauvegarde — reprise également
dans le tableau Vocabulaire FR/EN (§ 7) et le résumé d'examen (§ 8).

## Tests (`tests/test_ticket83_course_question_alignment.py`, 16 tests)

Extraction structurelle (patterns parenthèse et deux-points), non-crash sur code
inconnu/absent, rejet effectif de l'acronyme fictif ZXQW sur MC04, acceptation de SMART
désormais enseigné, reproduction du vrai gap résiduel CPU/MC01 (preuve que la garde
généralise au-delà du seul cas SMART), insensibilité au type de question, comportement
sans UAA, liste blanche minimale (PC), câblage dans `QUALITY_VALIDATORS` et
`validate_question_quality`, enrichissement de `vocabulary`/`constraints` dans
`_detailed_context`.

## Fichiers

- `app/v1/course_coverage.py` (nouveau)
- `app/v1/quality_validation.py` (câblage du nouveau validateur)
- `app/v1/ampcr_plan.py` (`vocabulary`/`constraints` enrichis dans `_detailed_context`)
- `app/v1/ampcr_courses.py` (MC04 § 83.C)
- `tests/test_ticket83_course_question_alignment.py` (nouveau, 16 tests)
- `docs/claude-reports/2026-09-19_ticket-83_course-question-alignment.md` (ce rapport)
