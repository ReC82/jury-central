"""Contenu de cours — FSE04 « Normes, valeurs et influence sociale » (ticket #97, cahier
des charges détaillé).

Même structure que FSE01/FSE02/FSE03 : 1. Ce que tu dois savoir faire à l'examen —
2. Théorie progressive — 3. Définitions importantes — 4. Méthode étape par étape —
5. Exemples commentés — 6. Mauvaises réponses comparées aux bonnes — 7. Pièges et erreurs
fréquentes — 8. Exercices guidés (corrigés masqués par défaut) — 9. Corrigés très
expliqués — 10. Fiche mémo.

Périmètre strict (ticket #97, programme p. 44-46) : UNIQUEMENT les ressources remobilisées
dans cette UAA — norme, valeur, besoin, comportement, frustration, groupe d'appartenance,
influence sociale, socialisation — et leurs limites explicatives. N'importe PAS
l'intégralité de l'UAA « Normes et Société » : reste strictement borné à ces notions.

Traitement du scénario (membre public encourageant la diffusion d'une vidéo humiliante,
`app.v1.fse04_content`) : volontairement sobre, aucune scène décrite en détail, objectif
pédagogique exclusivement centré sur l'analyse norme/valeur/comportement et sur les
limites de l'explication par la seule influence du groupe (jamais une banalisation du
cyberharcèlement — au contraire, le cours souligne explicitement la responsabilité
individuelle qui subsiste malgré la pression de groupe)."""

from app.v1.fse04_content import (
    FSE04_GROUP_CARD_HTML,
    FSE04_GROUP_TITLE,
    FSE04_TESTIMONY_CARD_HTML,
    FSE04_TESTIMONY_TITLE,
)

from app.v1.fse_course_sections import build_course_sections


def fse04_course_markdown() -> str:
    return f"""# FSE04 — Normes, valeurs et influence sociale

## 1. Ce que tu dois savoir faire à l'examen

Tu dois être capable de distinguer une norme, une valeur et un comportement dans une \
situation donnée, d'expliquer comment la pression d'un groupe peut influencer un \
comportement individuel, et de reconnaître les limites de cette explication : la pression \
du groupe n'efface jamais la responsabilité individuelle.

**Prérequis** : ce cours réutilise le groupe d'appartenance vu dans FSE03 (une personne \
peut appartenir à plusieurs groupes, chacun avec ses propres règles implicites).

## 2. Théorie progressive

Une **valeur** est ce qu'un groupe ou une société considère comme important ou \
souhaitable (le respect, l'humour, la solidarité...). Une **norme** est une règle de \
comportement concrète, attendue dans un groupe ou une société, qui découle souvent d'une \
valeur (par exemple, la valeur « respect d'autrui » peut donner la norme « ne pas se \
moquer publiquement de quelqu'un »). Un **comportement** est une action réellement \
observée chez une personne : il peut respecter une norme, ou s'en écarter.

Chaque personne a des **besoins** (être acceptée, appartenir à un groupe, se sentir en \
sécurité). Quand une norme de groupe entre en tension avec un besoin ou une valeur \
personnelle, cela peut créer de la **frustration** : par exemple, vouloir être accepté·e \
par un groupe tout en étant mal à l'aise avec ce que ce groupe encourage.

Un **groupe d'appartenance** (vu dans FSE03) développe souvent ses propres normes \
implicites. L'**influence sociale** désigne la façon dont les normes et comportements \
d'un groupe orientent le comportement d'une personne, même sans règle écrite ni \
obligation formelle : voir le reste du groupe rire d'une situation, ou partager un \
contenu massivement, pousse certaines personnes à faire de même, par désir de s'intégrer \
ou de ne pas se démarquer. Ce processus progressif par lequel une personne intègre les \
normes et valeurs d'un ou plusieurs groupes s'appelle la **socialisation**.

Cette influence a cependant des **limites** : elle explique une tendance statistique \
(« beaucoup de membres d'un groupe agissent dans le même sens »), jamais une fatalité \
individuelle. Face à une même pression de groupe, les personnes ne réagissent pas toutes \
de la même façon — certaines suivent le mouvement, d'autres s'en écartent. L'influence \
sociale explique pourquoi un comportement est FRÉQUENT dans un groupe donné ; elle \
n'efface jamais la responsabilité de la personne qui choisit, individuellement, d'agir \
d'une façon ou d'une autre.

## 3. Définitions importantes

- **Valeur** : ce qu'un groupe ou une société considère comme important ou souhaitable.
- **Norme** : règle de comportement concrète, attendue dans un groupe ou une société, \
qui découle souvent d'une valeur.
- **Comportement** : action réellement observée chez une personne — peut respecter une \
norme ou s'en écarter.
- **Besoin** : ce dont une personne a besoin (être acceptée, appartenir, se sentir en \
sécurité...).
- **Frustration** : tension ressentie quand un besoin n'est pas satisfait, ou qu'une \
norme de groupe entre en conflit avec une valeur personnelle.
- **Groupe d'appartenance** : groupe auquel une personne est identifiée comme membre.
- **Influence sociale** : façon dont les normes et comportements d'un groupe orientent le \
comportement d'une personne, même sans obligation formelle.
- **Socialisation** : processus progressif par lequel une personne intègre les normes et \
valeurs d'un ou plusieurs groupes.

## 4. Méthode étape par étape

Face à une situation de groupe, procède dans cet ordre :

1. Identifie la **valeur** implicite en jeu dans la situation (ex. le respect d'autrui, \
l'humour, l'appartenance au groupe).
2. Identifie la **norme** concrète que le groupe semble suivre ou encourager (ex. \
« partager ce type de contenu est valorisé dans ce groupe »).
3. Observe les **comportements** réellement décrits dans le document : respectent-ils \
cette norme, ou certains s'en écartent-ils ?
4. Explique en quoi l'**influence sociale** peut expliquer la fréquence d'un comportement \
dans le groupe (pression, désir d'intégration).
5. Rappelle la **limite** de cette explication : elle ne dispense jamais une personne de \
sa responsabilité individuelle — d'autres membres du même groupe peuvent agir \
différemment.

## 5. Exemples commentés

### Exemple 1 — {FSE04_GROUP_TITLE}

{FSE04_GROUP_CARD_HTML}

**Analyse commentée :**
- Valeur implicite dans ce groupe : l'humour et le divertissement priment sur le respect \
de la personne filmée.
- Norme observée : dans ce groupe, partager et commenter ce type de vidéo de façon \
moqueuse est valorisé — la publication a été partagée 340 fois, et plusieurs commentaires \
(A, B, C) suivent ce ton moqueur.
- Comportements : la plupart des commentaires visibles suivent la norme du groupe \
(moquerie, partage), mais pas tous — le membre D exprime explicitement un désaccord \
(« c'est méchant de se moquer comme ça »).
- Influence sociale : le nombre élevé de partages et de commentaires moqueurs peut inciter \
d'autres membres à faire de même, par désir de s'intégrer à la dynamique du groupe.
- Limite : le commentaire du membre D montre que l'influence du groupe n'empêche pas \
certains membres d'exprimer une position différente — elle n'efface donc pas leur \
responsabilité individuelle.

### Exemple 2 — {FSE04_TESTIMONY_TITLE}

{FSE04_TESTIMONY_CARD_HTML}

**Analyse commentée :** ce témoignage illustre directement la limite de l'influence \
sociale comme explication. Karim décrit ressentir la pression du groupe (« un réflexe de \
sourire parce que tout le monde autour de moi trouvait ça drôle »), ce qui montre bien \
que l'influence sociale existe réellement. Mais il choisit, individuellement, de ne pas \
partager ni commenter moqueusement : « Ce n'est pas parce qu'un groupe entier semble \
pousser dans une direction que chaque personne qui en fait partie agit forcément de la \
même façon. » Ce témoignage prouve que l'appartenance à un groupe qui encourage un \
comportement donné n'oblige jamais une personne à adopter ce comportement.

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse** (question : « Pourquoi autant de membres ont-ils partagé la \
vidéo ? ») : « Parce que le groupe les y a obligés. » → présente l'influence sociale \
comme une contrainte absolue, ce qui n'est jamais le cas.
- ✅ **Bonne réponse** : « La norme du groupe, qui valorise ce type de contenu moqueur, a \
influencé le comportement de nombreux membres — sans pour autant les y obliger : le \
membre D, dans le même groupe, exprime un désaccord explicite. »

- ❌ **Mauvaise réponse** (question : « Karim n'a-t-il subi aucune influence du groupe ? \
») : « Non, il a agi complètement indépendamment du groupe. » → ignore ce que Karim \
décrit lui-même (le réflexe de sourire, la pression ressentie).
- ✅ **Bonne réponse** : « Si, Karim décrit bien avoir ressenti la pression du groupe (un \
réflexe de sourire partagé par les autres) — mais cette influence ne l'a pas empêché de \
choisir, individuellement, de ne pas participer au partage moqueur. »

## 7. Pièges et erreurs fréquentes

- **Confondre valeur et norme** : la valeur est l'idée générale (le respect, l'humour) ; \
la norme est la règle concrète de comportement qui en découle dans un groupe précis.
- **Présenter l'influence sociale comme une excuse absolue** : elle explique une \
tendance, jamais une obligation — un comportement individuel reste toujours un choix.
- **Réduire tout comportement de groupe à l'influence sociale** : dans un même groupe, \
plusieurs comportements différents (voire opposés) peuvent coexister, comme le montre le \
commentaire du membre D ou le témoignage de Karim.
- **Confondre frustration et influence sociale** : la frustration naît d'une tension \
entre un besoin/une valeur personnelle et une norme de groupe ; l'influence sociale est \
le processus par lequel la norme du groupe oriente malgré tout le comportement.

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Identifier valeur, norme et comportement (essaie avant de regarder \
la correction)</summary>

Reprends la publication du groupe « Fous rires du quotidien » (exemple 1). Identifie la \
valeur implicite, la norme qui en découle dans ce groupe, et donne un exemple de \
comportement qui suit cette norme ET un exemple de comportement qui s'en écarte.

<details>
<summary>Voir la correction expliquée</summary>

Valeur implicite : l'humour et le divertissement priment sur le respect de la personne \
filmée. Norme dans ce groupe : partager et commenter ce type de vidéo de façon moqueuse \
est valorisé. Comportement qui suit la norme : le membre C, qui partage la vidéo à ses \
propres amis en la trouvant « trop drôle ». Comportement qui s'en écarte : le membre D, \
qui exprime désapprouver ce type de moquerie.

Ce corrigé fonctionne parce qu'il traite les trois notions séparément (valeur, norme, \
comportement) et illustre qu'un même groupe peut contenir des comportements différents \
vis-à-vis d'une même norme.
</details>
</details>

<details>
<summary>Exercice 2 — Expliquer sans réduire au groupe (essaie avant de regarder la \
correction)</summary>

À partir du témoignage de Karim (exemple 2), explique pourquoi on ne peut pas dire que \
« tous les membres du groupe ont le même comportement face à ce type de contenu ».

<details>
<summary>Voir la correction expliquée</summary>

Karim décrit avoir ressenti la pression du groupe, comme probablement d'autres membres, \
mais il a choisi de ne pas partager ni commenter moqueusement la vidéo. Il précise même \
que d'autres membres du groupe ont fait le même choix que lui, sans le dire publiquement. \
Cela montre que, même au sein d'un groupe où une norme moqueuse semble dominante \
(340 partages), les comportements individuels restent variés : l'appartenance à un \
groupe et la pression qu'il exerce n'effacent jamais les choix individuels de chacun de \
ses membres.

Ce corrigé fonctionne parce qu'il s'appuie sur un élément précis du témoignage (d'autres \
membres silencieux ont fait le même choix) plutôt que sur une affirmation générale non \
vérifiable.
</details>
</details>

## 9. Corrigés très expliqués

**Question :** « Le membre D, qui désapprouve la moquerie dans ses commentaires, \
subit-il quand même une forme d'influence sociale ? »

**Corrigé expliqué :** oui, d'une certaine façon : le fait même que le membre D ressente \
le besoin d'exprimer explicitement son désaccord (« Franchement, c'est méchant... ») \
montre qu'il perçoit bien la norme dominante du groupe (la moquerie valorisée) et qu'il \
réagit à elle, même en s'y opposant. L'influence sociale ne se limite pas à « suivre le \
groupe » : elle peut aussi se manifester par le besoin de se positionner FACE à une norme \
perçue, y compris pour la contester. Cela ne change rien au fait que son comportement \
final (exprimer un désaccord plutôt que se moquer) reste un choix individuel, différent \
de celui de la majorité des commentaires visibles.

Ce corrigé fonctionne parce qu'il ne réduit pas l'influence sociale à un simple \
alignement sur le groupe : il montre qu'elle peut aussi se manifester dans la façon dont \
une personne réagit à une norme, même en s'y opposant, sans jamais nier la responsabilité \
individuelle de son choix final.

## 10. Fiche mémo

- Valeur = idée générale importante pour un groupe ; norme = règle concrète de \
comportement qui en découle ; comportement = action réellement observée.
- Un besoin non satisfait, ou en tension avec une norme de groupe, peut créer de la \
frustration.
- L'influence sociale explique une TENDANCE dans un groupe, jamais une obligation \
individuelle absolue.
- Dans un même groupe, plusieurs comportements différents (voire opposés) à une même \
norme peuvent toujours coexister.
- La pression du groupe n'efface jamais la responsabilité individuelle du comportement \
choisi.
"""


def fse04_course_sections() -> list[tuple[str, str]]:
    """Sections (titre, Markdown) du cours FSE04 — refonte pédagogique et visuelle
    (ticket #105), voir `app.v1.fse_course_sections.build_course_sections`."""
    return build_course_sections("FSE04", fse04_course_markdown())
