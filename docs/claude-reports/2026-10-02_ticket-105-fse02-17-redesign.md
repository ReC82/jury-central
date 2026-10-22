# Rapport — Ticket #105 (suite) : refonte pédagogique et visuelle de FSE02-FSE17

Branche : `feature/105-fse-redesign-fse02-17` (depuis `develop`). PR #107 fusionnée dans
`develop`, puis installée sur `jury-central.lodylands.com`.

**SHA installé : `0b98e77`** (merge commit de la PR #107 dans `develop`). Fait suite à la
PR #106 (FSE01, SHA `3c9a815`, voir `docs/claude-reports/2026-10-02_ticket-105-fse01-redesign.md`).

---

## 1. Principe : étendre, pas reproduire mécaniquement (demande § 5)

FSE02-FSE16 partagent tous la même structure en 10 sections numérotées (certains avec une
11e, « Sources officielles vérifiées », tickets #98-#101) — vérifié sur les 15 fichiers
avant d'écrire la moindre ligne de code. Plutôt que de réécrire chaque cours à la main (ce
qui aurait pris un temps disproportionné et risqué des incohérences), un **transformateur
générique et réutilisable** a été écrit : `app/v1/fse_course_sections.py`.

Ce module applique uniquement des transformations **mécaniques et sûres** à la prose déjà
rédigée et validée (aucune notion, nuance ou terme supprimé, aucune reformulation) :

1. **Découpage en blocs titrés** (comme FSE01) : chaque section numérotée devient un bloc
   distinct, dont le titre pilote automatiquement son type de carte.
2. **Correction mécanique du bug de liste** (`fix_list_blank_lines()`) : insère la ligne
   vide manquante avant toute liste Markdown, partout où elle manque — élimine
   systématiquement les paragraphes à tirets littéraux diagnostiqués au ticket #105 § 1.
3. **Conversion en grille de comparaison** (`mauvaises_bonnes_to_comparegrid()`) : chaque
   paire « ❌ Mauvaise réponse / ✅ Bonne réponse » (format strictement identique dans les
   15 cours, vérifié avant d'écrire la fonction) devient une grille `.jc-compare`.
4. **Conversion en citations** (`pieges_to_blockquotes()`) : chaque bloc de pièges devient
   une citation Markdown, convertie automatiquement en WarningCard par le mécanisme déjà
   existant (`wrapBlockquotesAsWarningCards()`).

**Ce qui n'a volontairement PAS été forcé partout** (conformément à la demande explicite de
ne pas reproduire artificiellement le même modèle) :
- Les définitions et les exemples restent des listes/paragraphes corrigés, affichés dans
  leur carte appropriée — pas de grille de définitions automatique : plusieurs cours (ex.
  FSE08) regroupent plusieurs termes dans une seule puce (« Loi : ... Décret : ...
  Ordonnance : ... »), ce qui ne se prête pas à un découpage fiable terme par terme.
- **Aucun schéma SVG n'a été ajouté par défaut.** Seuls deux cours dont la notion centrale
  est un vrai schéma relationnel en ont reçu un, choisi au cas par cas après lecture du
  contenu :
  - **FSE08** (« La Belgique : État et niveaux de pouvoir ») : schéma des niveaux de
    pouvoir (fédéral → Régions/Communautés → provinces/communes), avec une note explicite
    rappelant que Régions et Communautés sont deux découpages différents, pas une
    hiérarchie de commandement entre eux — reprend un piège déjà identifié dans le cours.
  - **FSE15** (« Le circuit économique... ») : schéma du circuit à quatre agents (ménages,
    entreprises, État, reste du monde) avec flux réels (vert) et flux monétaires (bleu)
    clairement distingués par couleur et libellé — exactement la notion que ce cours
    enseigne.
  - Les 13 autres cours (FSE02-07, 09-14, 16) n'ont reçu aucun schéma : leur contenu
    (financement des médias, traces numériques, élections, budget...) ne correspond pas à
    un schéma relationnel à représenter, un tableau ou une liste corrigée suffit.

## 2. FSE17 (structure propre) traité à la main

FSE17 (révision transversale) a une structure entièrement différente (carte des deux
thèmes, tableau de synthèse, lexique, confusions, fiches méthode, répartition du temps,
12 exercices + 12 corrigés séparés, accès aux 3 examens blancs) : le transformateur
générique ne s'applique pas. `fse17_course_sections()` découpe donc ses 9 sections à la
main, en réutilisant les mêmes fonctions mécaniques (`fix_list_blank_lines`,
`pieges_to_blockquotes` pour la section « Confusions fréquentes », qui est déjà par nature
une liste de pièges). Deux titres de section ont été reformulés pour éviter une
classification de carte incorrecte (le mot « exemple » ou « examen » présent dans un titre
déclenche automatiquement ExampleCard/ExamCard) :
- « Tableau notion → ce que je dois savoir faire → exemple » → « Tableau de révision :
  notion et savoir-faire » (évite une ExampleCard pour un tableau de référence).
- « Fiches méthode — verbes d'examen » → « Fiches méthode : les verbes à maîtriser » (évite
  une ExamCard pour une fiche de méthode).

## 3. Migration des données

Même mécanisme que FSE01 (`obsolete_titles=frozenset({"Cours complet"})` sur chaque appel
`_seed_uaa` de FSE02 à FSE17). Vérifié après le seed de production : plus aucun bloc
« Cours complet » dans FSE01-17, 123 nouveaux blocs créés, et aucune donnée de compte/
session affectée (18 utilisateurs, 67 sessions, 536 réponses — identiques avant/après).

---

## 4. Tests exécutés (ciblés, PAS la suite complète de 1 419 tests)

| Lot | Résultat |
|---|---|
| `test_card_kind.py`, `test_admin_content_hierarchy.py`, `test_ticket96_fse01.py`, `test_ticket97_fse02_04.py`, `test_ticket98_fse05_08.py` | 130/130 ✅ |
| `test_ticket99_fse09_12.py`, `test_ticket100_fse13_16.py`, `test_ticket101_fse17.py` (adapté), `test_ticket102_coverage.py` | 156/156 ✅ |

**Total ciblé (cette étape) : 286/286.** Exécutés deux fois : une fois sur la branche avant
fusion, une fois sur le checkout de production après fast-forward, avant le seed.

`tests/test_ticket101_fse17.py::test_fse17_course_page_is_real_content` a dû être adapté :
il vérifiait la présence du libellé EXACT des anciens titres de section (« Carte des deux
thèmes », « Tableau notion »), devenus « Les deux thèmes du programme » / « Tableau de
révision : notion et savoir-faire » après le découpage. L'assertion vérifie désormais la
substance (noms des deux thèmes, en-tête de colonne du tableau) plutôt que le libellé exact
d'un titre de section — plus robuste à une future reformulation.

---

## 5. Vérifications de rendu effectuées (production)

Sur les 16 pages réelles `/uaa/fse-fseNN` (FSE02-FSE17), après installation :

- Statut 200 sur les 16 pages, plusieurs cartes distinctes générées sur chacune.
- **Zéro paragraphe à tirets littéraux** sur les 16 pages (le bug diagnostiqué au § 1 du
  rapport précédent n'est plus présent nulle part dans FSE01-17).
- Aucun `<details open` (corrigés fermés par défaut) sur les 16 pages.
- FSE08 et FSE15 : `<svg>` + `.jc-diagram` confirmés présents ; aucun autre cours FSE02-16
  n'en contient (schéma non forcé artificiellement).
- FSE02 : `.jc-compare` et `<blockquote>` confirmés présents (comparaison + pièges
  convertis).
- FSE17 : carte Méthode et carte Examen confirmées présentes, les 12 exercices et leurs 12
  corrigés tous présents.
- Assets statiques (`design-system.css`) répondent en 200 ; la route `/practice` (fonction
  d'entraînement, non modifiée) répond toujours par une redirection d'authentification
  (303), comportement inchangé.

**Limite explicite, identique au rapport FSE01** : vérifications structurelles (HTML/CSS),
pas de capture d'écran réelle — aucun outil de rendu visuel disponible dans cet
environnement. La vérification visuelle réelle sur ordinateur, téléphone et à l'impression
reste à faire par l'utilisateur.

Sauvegarde de `jury_central.db` effectuée avant ce second seed :
`jury_central.db.bak-pre-ticket105-fse0217-<horodatage>` (conservée dans
`/srv/jury-central`, en plus de la sauvegarde prise avant le seed de FSE01).

---

## 6. Pages/fichiers modifiés

- `app/v1/fse_course_sections.py` — nouveau, transformateur générique.
- `app/v1/fse02_course.py` à `app/v1/fse16_course.py` — ajout de `fseNN_course_sections()`
  (wrapper autour de `fseNN_course_markdown()`, inchangée sauf FSE08/FSE15 qui reçoivent en
  plus la constante du schéma SVG).
- `app/v1/fse17_course.py` — ajout de `fse17_course_sections()` (découpage à la main).
- `app/seed.py` — `FSE02_BLOCKS` à `FSE17_BLOCKS` reconstruits via `_fse_course_blocks()`
  (ticket #105, FSE01) + `fseNN_course_sections()` ; `obsolete_titles` ajouté sur chaque
  appel `_seed_uaa` concerné.
- `tests/test_ticket101_fse17.py` — adapté (voir § 4).

---

## 7. Liens à tester

Les 16 cours (en plus de FSE01, déjà livré) :

- `https://jury-central.lodylands.com/uaa/fse-fse02` … jusqu'à `fse-fse17`

À vérifier en particulier : les schémas de FSE08 (niveaux de pouvoir) et FSE15 (circuit
économique) sur téléphone, les grilles de comparaison bonne/mauvaise réponse sur
n'importe quel cours (ex. FSE02, FSE08), les 12 exercices/corrigés de FSE17, et l'absence de
tout « mur de texte à tirets » sur l'ensemble des 17 cours FSE.

---

## 8. Ticket #105 : terminé

Les deux étapes demandées (pilote FSE01 puis extension FSE02-17) sont livrées et
installées. Ticket #105 clôturé sur GitHub avec un commentaire récapitulatif pointant vers
les deux rapports.
