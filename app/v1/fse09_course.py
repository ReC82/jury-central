"""Contenu de cours — FSE09 « Qui décide de quoi ? » (ticket #99, cahier des charges
détaillé).

Même structure que FSE01-FSE08 : 1. Ce que tu dois savoir faire à l'examen —
2. Théorie progressive — 3. Définitions importantes — 4. Méthode étape par étape —
5. Exemples commentés — 6. Mauvaises réponses comparées aux bonnes — 7. Pièges et erreurs
fréquentes — 8. Exercices guidés (corrigés masqués par défaut) — 9. Corrigés très
expliqués — 10. Fiche mémo — 11. Sources officielles vérifiées.

Premier cours du thème « Le citoyen et l'État » à approfondir la répartition des
compétences déjà introduite en FSE08 (programme p. 61-62) — réutilise son vocabulaire
(fédéral/Régions/Communautés/provinces/communes) sans le ré-enseigner intégralement."""

from app.v1.fse09_content import FSE09_SITUATIONS_TEXT

from app.v1.fse_course_sections import build_course_sections


def fse09_course_markdown() -> str:
    return f"""# FSE09 — Qui décide de quoi ?

## 1. Ce que tu dois savoir faire à l'examen

Tu dois être capable d'associer une situation concrète au niveau de pouvoir compétent \
(fédéral, Région, Communauté, province, commune) et à la matière concernée, en expliquant \
les indices qui te permettent de conclure — et de reconnaître qu'une situation peut, dans \
certains cas, impliquer plusieurs niveaux à la fois.

**Prérequis** : ce cours réutilise directement les cinq niveaux de pouvoir vus en FSE08 \
(fédéral, Régions, Communautés, provinces, communes) et leur logique respective \
(territoire pour les Régions, personnes/langue/culture pour les Communautés).

## 2. Théorie progressive

Chaque niveau de pouvoir vu en FSE08 est compétent pour des **matières précises**. Le \
**niveau fédéral** reste compétent pour ce qui concerne l'ensemble du pays : justice, \
affaires étrangères, défense, sécurité sociale. Les **Régions** sont compétentes pour des \
matières liées au territoire : économie, emploi, environnement, logement, travaux publics. \
Les **Communautés** sont compétentes pour des matières liées aux personnes, à la langue et \
à la culture : enseignement, culture, aide à la jeunesse. Les **provinces** jouent un rôle \
d'appui technique aux communes de leur territoire ; les **communes** gèrent les matières de \
proximité (voirie, propreté publique, état civil).

Certaines situations ne se laissent pas ranger dans un seul niveau : la **santé**, par \
exemple, dépend à la fois du niveau fédéral (l'assurance maladie-invalidité, qui rembourse \
les soins) et des Communautés (certains aspects de la prévention et de l'aide aux \
personnes, dites matières personnalisables). De même, une politique peut nécessiter une \
**coordination entre niveaux** quand elle touche à la fois une compétence fédérale et une \
compétence régionale. Il ne faut jamais forcer une réponse unique quand la situation \
décrit réellement un partage de compétences.

## 3. Définitions importantes

- **Compétence** : matière pour laquelle un niveau de pouvoir précis est habilité à \
décider.
- **Matière personnalisable** : matière liée aux personnes (santé, aide aux personnes), \
gérée en tout ou partie par les Communautés.
- **Coordination entre niveaux** : nécessité, pour certaines politiques, d'un accord entre \
plusieurs niveaux de pouvoir dont les compétences se croisent.

## 4. Méthode étape par étape

Face à une situation, procède dans cet ordre :

1. Identifie la **matière** concernée (justice ? économie ? enseignement ? voirie \
locale ?).
2. Associe cette matière au **niveau de pouvoir compétent**, à l'aide des catégories vues \
en FSE08 (territoire → Région ; personnes/langue/culture → Communauté ; pays entier → \
fédéral ; proximité → commune/province).
3. Vérifie si la situation décrit explicitement un **partage entre plusieurs niveaux** \
(ex. santé, coordination fédéral/régional) — dans ce cas, ne choisis jamais un seul niveau \
par simplification.
4. Justifie ta réponse par la matière elle-même, jamais par une supposition non confirmée \
par l'énoncé.

## 5. Exemples commentés

### Exemple 1 — Situation 1 (procédure pénale)

{FSE09_SITUATIONS_TEXT.splitlines()[2]}

**Analyse commentée :** la procédure pénale concerne l'ensemble du pays : c'est une \
matière du **niveau fédéral**.

### Exemple 2 — Situation 3 (programmes scolaires)

{FSE09_SITUATIONS_TEXT.splitlines()[6]}

**Analyse commentée :** les programmes de cours relèvent de l'enseignement, une matière \
liée aux personnes et à la culture : c'est une compétence de la **Communauté** dont relève \
l'école.

### Exemple 3 — Situation 8 (remboursement de soins)

{FSE09_SITUATIONS_TEXT.splitlines()[16]}

**Analyse commentée :** cette situation implique **plusieurs niveaux** : le remboursement \
par la mutualité relève de l'assurance maladie-invalidité, une matière fédérale, tandis que \
d'autres aspects de la santé (prévention, aide aux personnes) relèvent des Communautés. Il \
ne faut jamais répondre « fédéral » seul ou « Communauté » seule ici.

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse** (situation 6, normes environnementales) : « C'est une compétence \
fédérale, parce que l'environnement concerne tout le monde. » → ignore que l'environnement \
est une matière territoriale, donc régionale.
- ✅ **Bonne réponse** : « Les normes environnementales pour les entreprises d'un territoire \
relèvent de la Région, compétente pour les matières territoriales comme l'environnement. »

- ❌ **Mauvaise réponse** (situation 8, remboursement de soins) : « C'est uniquement une \
compétence fédérale. » → ignore le partage explicite décrit dans l'énoncé.
- ✅ **Bonne réponse** : « Cette situation implique plusieurs niveaux : le remboursement \
par la mutualité (fédéral) et d'autres aspects de la santé gérés par la Communauté. »

## 7. Pièges et erreurs fréquentes

- **Forcer une réponse à un seul niveau** quand l'énoncé décrit explicitement un partage \
de compétences.
- **Confondre « concerne tout le monde » et « compétence fédérale »** : l'environnement ou \
le logement concernent aussi tout le monde, mais restent des matières régionales \
(territoriales).
- **Oublier le rôle d'appui des provinces**, souvent réduit à tort aux seules communes.

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Identifier le niveau compétent (essaie avant de regarder la \
correction)</summary>

Reprends la situation 2 (aides aux entreprises). Quel niveau de pouvoir est compétent, et \
pourquoi ?

<details>
<summary>Voir la correction expliquée</summary>

La Région est compétente : les aides aux entreprises installées sur un territoire précis \
relèvent de l'économie, une matière territoriale.

Ce corrigé fonctionne parce qu'il relie directement la matière (économie, territoriale) au \
niveau compétent (Région), sans supposition supplémentaire.
</details>
</details>

<details>
<summary>Exercice 2 — Reconnaître un partage de compétences (essaie avant de regarder la \
correction)</summary>

Reprends la situation 10 (coordination fédéral/régional). Pourquoi cette situation \
nécessite-t-elle un accord entre deux niveaux plutôt qu'une décision d'un seul niveau ?

<details>
<summary>Voir la correction expliquée</summary>

La politique décrite touche à la fois une compétence fédérale (la fiscalité générale) et \
une compétence régionale (le logement) : aucun des deux niveaux ne peut décider seul sur \
l'ensemble de la politique, d'où la nécessité d'une coordination.

Ce corrigé fonctionne parce qu'il identifie précisément les deux compétences en jeu, plutôt \
que d'affirmer vaguement qu'« il faut que tout le monde soit d'accord ».
</details>
</details>

## 9. Corrigés très expliqués

**Question :** « Pourquoi ne peut-on pas toujours donner une réponse unique à la question \
« qui décide de quoi » ? »

**Corrigé expliqué :** parce que certaines matières, comme la santé, ne sont pas \
entièrement confiées à un seul niveau de pouvoir : le remboursement des soins (assurance \
maladie-invalidité) reste fédéral, mais d'autres aspects de la santé (prévention, aide aux \
personnes) sont des matières personnalisables gérées par les Communautés. Vouloir à tout \
prix une réponse unique reviendrait à simplifier une réalité réellement partagée, ce que ce \
cours demande explicitement d'éviter.

Ce corrigé fonctionne parce qu'il justifie le partage par un exemple précis (la santé) \
plutôt que d'affirmer une règle générale non vérifiable.

## 10. Fiche mémo

- Fédéral = pays entier (justice, affaires étrangères, défense, sécurité sociale).
- Région = territoire (économie, emploi, environnement, logement).
- Communauté = personnes/langue/culture (enseignement, culture, aide à la jeunesse).
- Provinces = appui technique aux communes ; communes = proximité (voirie, état civil).
- Certaines matières (santé) sont partagées entre plusieurs niveaux : ne jamais forcer une \
réponse unique dans ce cas.

## 11. Sources officielles vérifiées

La répartition des compétences décrite ci-dessus est vérifiée auprès de sources belges \
officielles, dans la continuité de FSE08 :

- La Chambre des représentants de Belgique, fiche pédagogique sur le statut de l'État \
fédéral, https://www.lachambre.be/kvvcr/pdf_sections/pri/fiche/en_07_00.pdf — consulté le \
2026-10-01.
- Portail citoyen « Bruxelles-J », « Quelles sont les institutions régionales belges ? », \
https://www.bruxelles-j.be/exercer-ta-citoyennete/quelles-sont-les-institutions-regionales/ \
— consulté le 2026-10-01 (source de vulgarisation citoyenne, recoupée avec la fiche \
officielle ci-dessus pour les grandes catégories de compétences — aucun détail législatif \
précis n'est enseigné ni évalué ici, conformément au périmètre du cours).

En cas de doute sur un cas réel, consulte ces organismes officiels plutôt que ce cours.
"""


def fse09_course_sections() -> list[tuple[str, str]]:
    """Sections (titre, Markdown) du cours FSE09 — refonte pédagogique et visuelle
    (ticket #105), voir `app.v1.fse_course_sections.build_course_sections`."""
    return build_course_sections("FSE09", fse09_course_markdown())
