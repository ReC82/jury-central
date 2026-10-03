# Rapport — Ticket #124 : mise en page de la théorie FSE (colonne étroite, vide à droite)

Installé sur `jury-central.lodylands.com`.

**SHA installé : `3d50a41`** (merge de la PR #125).

---

## 1. Constat et diagnostic

Depuis le ticket #120, `.jc-prose` limitait la largeur de la prose théorique à `70ch`
(~65-75 caractères par ligne) mais ne la centrait pas : le texte restait plaqué à gauche
dans une carte (`.jc-card`, sans largeur maximale propre) beaucoup plus large — toute la
moitié droite restait vide, ce qui se lisait comme une mise en page cassée plutôt que
voulue.

---

## 2. Correctif générique — tous les cours concernés (FSE02, FSE05-FSE16)

Un correctif CSS d'une ligne (`margin: 0 auto` sur `.jc-prose`) centre désormais ce bloc
dans sa carte, sans aucun changement de contenu. Comme ces 13 cours partagent exactement
le même composant `.jc-prose` (ticket #120), ce correctif les corrige TOUS d'un coup —
c'est la réponse apportée à « applique la correction aux autres pages FSE présentant le
même problème », sans leur imposer la restructuration bespoke de FSE04 ni aucune
réécriture de leur matière. Les grilles de définitions (`.jc-definitions`), déjà jugées
satisfaisantes, n'ont pas été touchées.

---

## 3. FSE04 — flagship : théorie bespoke avec vraie mise en page à deux colonnes

Plutôt que de se contenter de centrer un bloc de texte, FSE04 reçoit une restructuration
complète en trois cartes qui utilisent intelligemment la largeur disponible, chacune selon
son contenu :

- **« Valeur, norme, comportement : quelle différence ? »** : comparaison à trois éléments
  (nouvelle variante `.jc-compare--three`, troisième couleur violette) avec définition
  courte + exemple pour chacun, puis un schéma (`.jc-flow`) qui montre leur enchaînement
  sur un exemple cohérent (valeur « respect d'autrui » → norme « ne pas se moquer
  publiquement » → comportement observé, qui peut suivre la norme ou s'en écarter).
- **« Pourquoi suit-on parfois le groupe ? »** : nouvelle mise en page à deux colonnes
  (`.jc-theory-split`) — explication (besoins, groupe d'appartenance, influence sociale,
  socialisation) à gauche, « Situation concrète » (reprenant verbatim l'exemple déjà
  rédigé au ticket #97) dans un encadré à droite. S'effondre en une seule colonne sous
  768px.
- **« Peut-on agir autrement ? »** : ici le contenu est une explication continue sans
  second volet naturel (frustration, limites de l'influence) — reste donc en `.jc-prose`
  centrée, suivie d'un encadré « À retenir » sur la responsabilité individuelle (l'
  « encadré lisible » demandé), puis un lexique repliable qui reprend les 8 définitions
  d'origine, chacune déjà présente dans les explications visibles au-dessus.

Ce choix (deux colonnes seulement là où un exemple distinct existe naturellement, prose
centrée sinon) illustre directement le principe demandé : « la limite de largeur doit être
adaptée au composant, plutôt qu'appliquée uniformément à tous les paragraphes ».

**Bug de position trouvé et corrigé avant installation** (même nature qu'au ticket #120
pour FSE03) : le passage d'un bloc théorique unique à trois cartes décale la position des
blocs suivants (Méthode, Comparer pour ne pas confondre, Fiche mémo) sur tout staging déjà
seedé. `FSE04_REPOSITION_TITLES` les resynchronise — vérifié par un test qui reproduit
l'état pré-ticket avant de confirmer le correctif, et confirmé sur l'installation réelle
(ordre des 9 blocs FSE04 vérifié directement en base après seed : 1 à 9, sans collision).

---

## 4. Contrôles effectués

| Contrôle | Résultat |
|---|---|
| `tests/test_ticket124_fse_theory_layout.py` (nouveau, 12 cas : CSS du correctif, nouveaux composants, FSE04 bespoke, reproduction du bug de position) | ✅ |
| `tests/test_ticket120_fse_theory_generic.py` (mis à jour : FSE04 sorti de la liste générique) | ✅ |
| Suite complète FSE01-17 + card_kind + admin_content_hierarchy + ticket #118/#120 | ✅ (358 passants) |

Exécutés avant fusion, puis à nouveau sur le checkout de production après fast-forward,
avant le seed.

**Vérification de la page réelle en production** : les trois nouveaux titres de section
FSE04 présents, ancien titre fusionné absent, `.jc-theory-split`/`.jc-compare--three`/
`.jc-flow`/`.jc-glossary` tous présents, aucune fuite Markdown, aucune mention
« provisoire », notions d'examen (Karim, responsabilité individuelle...) toujours
présentes ; les 13 autres cours génériques vérifiés eux aussi (`.jc-prose` présent, aucune
fuite). Ordre des 9 blocs FSE04 vérifié directement en base de données après le seed de
production : positions 1 à 9 sans collision.

**Prévisualisation visuelle locale** (HTML réel → PDF → image, WeasyPrint, outil de
développement uniquement, jamais une dépendance du projet) : FSE04 (les trois cartes —
comparaison à trois couleurs avec schéma, mise en page à deux colonnes avec l'encadré
« Situation concrète » bien à droite, prose centrée + lexique replié) et FSE02 (prose
désormais centrée au lieu de plaquée à gauche, grille de définitions inchangée) — rendu
conforme à l'intention dans les deux cas.

**Limite explicite, identique aux rapports précédents** : aucun navigateur réel (Chrome/
Firefox headless, Playwright) disponible dans cet environnement. Les contrôles ci-dessus
sont soit des vérifications HTML/CSS (structure, classes, absence de fuite), soit des
rendus WeasyPrint locaux — jamais un test dans un vrai navigateur. L'empilement réel du
layout à deux colonnes sous 768px (téléphone), le rendu exact des couleurs/espacements, et
le comportement du lexique repliable au clic restent à confirmer par l'utilisateur dans un
navigateur réel et sur un appareil réel.

**Comptes et données vérifiés intacts** après le seed de production : 18 utilisateurs, 67
sessions, 536 réponses — identiques avant/après. Sauvegarde de `jury_central.db` effectuée
avant le seed : `jury_central.db.bak-pre-ticket124-<horodatage>`.

---

## 5. Fichiers modifiés/créés

- `app/static/css/design-system.css` — centrage de `.jc-prose` ; nouveaux composants
  `.jc-theory-split`/`.jc-theory-split-main`/`.jc-theory-split-aside`,
  `.jc-compare--three`/`.jc-compare-item--c`.
- `app/v1/fse04_course.py` — trois sections bespoke (`_section_value_norm_behaviour`,
  `_section_why_follow_the_group`, `_section_can_one_act_differently`) remplaçant
  `build_course_sections` pour la théorie.
- `app/seed.py` — `FSE04_REPOSITION_TITLES` (même mécanisme que `FSE03_REPOSITION_TITLES`,
  ticket #120).
- `docs/components/TheoryProgression.md` — documentation des nouveaux composants et du
  correctif de centrage.
- `tests/test_ticket124_fse_theory_layout.py` (nouveau), `tests/test_ticket120_fse_theory_generic.py`
  (FSE04 retiré de la liste générique).

---

## 6. Liens à vérifier

- FSE04 (flagship, trois cartes + deux colonnes) : **https://jury-central.lodylands.com/uaa/fse-fse04**
- FSE02 (correctif générique, prose désormais centrée) : **https://jury-central.lodylands.com/uaa/fse-fse02**
- FSE05 à FSE16 (même correctif générique) : `https://jury-central.lodylands.com/uaa/fse-fseNN`
- FSE03 (théorie bespoke du ticket #120, également centrée par ce correctif) : **fse-fse03**

À vérifier en particulier dans un vrai navigateur : l'empilement du layout à deux colonnes
de FSE04 sur téléphone, l'équilibre visuel du centrage sur très grand écran, et
l'ouverture/fermeture des lexiques repliables.

---

## 7. Suite

FSE01 et FSE17 n'utilisent pas `.jc-prose` (structure bespoke propre, non affectée par ce
problème) et restent donc non modifiés. Le reste du périmètre FSE (cours génériques
FSE02/FSE05-16) a reçu uniquement le correctif CSS générique, sans restructuration bespoke
comme FSE04 — à la disposition de l'utilisateur si une mise en page à deux colonnes
s'avère pertinente pour l'un d'entre eux après vérification visuelle.
