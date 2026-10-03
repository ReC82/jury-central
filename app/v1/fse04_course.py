"""Contenu de cours — FSE04 « Normes, valeurs et influence sociale » (ticket #97, cahier
des charges détaillé).

Même structure générale que FSE01/FSE02/FSE03 : 1. Ce que tu dois savoir faire à l'examen —
2. Théorie progressive — 3. Définitions importantes — 4. Méthode étape par étape —
5. Exemples commentés — 6. Mauvaises réponses comparées aux bonnes — 7. Pièges et erreurs
fréquentes — 8. Exercices guidés (corrigés masqués par défaut) — 9. Corrigés très
expliqués — 10. Fiche mémo.

Refonte ticket #124 (mise en page) : les sections 2+3, auparavant fusionnées en un bloc
théorique unique par `theory_and_definitions_to_cards` (ticket #120), sont remplacées par
TROIS cartes bespoke (comme FSE03, ticket #120) : « Valeur, norme, comportement : quelle
différence ? » (comparaison à trois, `.jc-compare--three`, puis schéma `.jc-flow` montrant
leur enchaînement), « Pourquoi suit-on parfois le groupe ? » (mise en page à deux colonnes
`.jc-theory-split` : explication à gauche, situation concrète à droite — cas réel de
contenu qui se prête à ce layout, contrairement à une prose purement linéaire) et « Peut-on
agir autrement ? » (prose centrée `.jc-prose` + encadré « À retenir » sur la responsabilité
individuelle). Lexique repliable en fin de troisième carte (7 définitions d'origine,
chacune déjà présente dans les explications visibles). Voir
`docs/components/TheoryProgression.md`. Les sections 1, 4-10 ne sont pas modifiées dans
leur matière : seule la forme de la théorie change.

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

from app.v1.fse_course_sections import (
    analyse_commentee_to_decrypt,
    exemple_headers_to_titles,
    exercises_to_cards,
    fix_list_blank_lines,
    mauvaises_bonnes_to_comparegrid,
    parse_numbered_sections,
    pieges_to_blockquotes,
)


def fse04_course_markdown() -> str:
    return f"""# FSE04 — Normes, valeurs et influence sociale

## 1. Ce que tu dois savoir faire à l'examen

Tu dois être capable de distinguer une norme, une valeur et un comportement dans une \
situation donnée, d'expliquer comment la pression d'un groupe peut influencer un \
comportement individuel, et de reconnaître les limites de cette explication : la pression \
du groupe n'efface jamais la responsabilité individuelle.

**Prérequis** : ce cours réutilise le groupe d'appartenance vu dans FSE03 (une personne \
peut appartenir à plusieurs groupes, chacun avec ses propres règles implicites).

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


def _section_value_norm_behaviour() -> str:
    """« Valeur, norme, comportement : quelle différence ? » — comparaison à trois
    (`.jc-compare--three`), puis schéma `.jc-flow` montrant l'enchaînement sur un exemple
    cohérent (ticket #124). HTML littéral (`<strong>`, jamais `**gras**`) : voir
    diagnostic ticket #112."""
    return """<div class="jc-prose">
<p>Trois notions se suivent et s'enchaînent, mais ne désignent jamais la même chose.</p>
</div>

<div class="jc-compare jc-compare--three">
<div class="jc-compare-item jc-compare-item--a">
<span class="jc-compare-label">Valeur</span>
<p>Ce qu'un groupe ou une société considère comme important ou souhaitable.</p>
<p><strong>Exemple :</strong> le respect d'autrui.</p>
</div>
<div class="jc-compare-item jc-compare-item--b">
<span class="jc-compare-label">Norme</span>
<p>Règle de comportement concrète, attendue dans un groupe, qui découle souvent d'une \
valeur.</p>
<p><strong>Exemple :</strong> ne pas se moquer publiquement de quelqu'un.</p>
</div>
<div class="jc-compare-item jc-compare-item--c">
<span class="jc-compare-label">Comportement</span>
<p>Action réellement observée chez une personne : elle peut respecter une norme, ou s'en \
écarter.</p>
<p><strong>Exemple :</strong> une personne se tait pendant qu'un camarade est moqué — un \
comportement qui s'écarte de la norme.</p>
</div>
</div>

<div class="jc-flow">
<div class="jc-flow-step">Valeur<small>respect d'autrui</small></div>
<div class="jc-flow-arrow" aria-hidden="true">→</div>
<div class="jc-flow-step">Norme<small>ne pas se moquer publiquement</small></div>
<div class="jc-flow-arrow" aria-hidden="true">→</div>
<div class="jc-flow-step">Comportement observé<small>suit la norme, ou s'en écarte</small></div>
</div>

<div class="jc-takeaway">
<span class="jc-takeaway-label">📌 À retenir</span>
<p>Une norme découle souvent d'une valeur, mais le comportement réellement observé peut \
toujours s'en écarter — les trois notions ne se confondent jamais.</p>
</div>"""


def _section_why_follow_the_group() -> str:
    """« Pourquoi suit-on parfois le groupe ? » — mise en page à deux colonnes
    (`.jc-theory-split`) : explication à gauche, situation concrète à droite (ticket
    #124)."""
    return """<div class="jc-theory-split">
<div class="jc-theory-split-main">
<p>Chaque personne a des <strong>besoins</strong> : être acceptée, appartenir à un \
groupe, se sentir en sécurité.</p>
<p>Un <strong>groupe d'appartenance</strong> (vu dans FSE03) développe souvent ses \
propres normes implicites. L'<strong>influence sociale</strong> désigne la façon dont les \
normes et comportements d'un groupe orientent le comportement d'une personne, même sans \
règle écrite ni obligation formelle. Ce processus progressif par lequel une personne \
intègre les normes et valeurs d'un ou plusieurs groupes s'appelle la \
<strong>socialisation</strong>.</p>
</div>
<div class="jc-theory-split-aside">
<span class="jc-theory-split-aside-label">Situation concrète</span>
<p>Voir le reste du groupe rire d'une situation, ou partager un contenu massivement, \
pousse certaines personnes à faire de même, par désir de s'intégrer ou de ne pas se \
démarquer — même sans règle écrite ni obligation formelle.</p>
</div>
</div>"""


def _section_can_one_act_differently() -> str:
    """« Peut-on agir autrement ? » — prose centrée (`.jc-prose`) + encadré « À retenir »
    sur la responsabilité individuelle, puis lexique repliable des 7 définitions d'origine
    (ticket #124)."""
    return """<div class="jc-prose">
<p>Quand une norme de groupe entre en tension avec un besoin ou une valeur personnelle, \
cela peut créer de la <strong>frustration</strong> : par exemple, vouloir être accepté·e \
par un groupe tout en étant mal à l'aise avec ce que ce groupe encourage.</p>
<p>Cette influence a cependant des <strong>limites</strong> : elle explique une tendance \
statistique (« beaucoup de membres d'un groupe agissent dans le même sens »), jamais une \
fatalité individuelle. Face à une même pression de groupe, les personnes ne réagissent \
pas toutes de la même façon — certaines suivent le mouvement, d'autres s'en écartent.</p>
</div>

<div class="jc-takeaway">
<span class="jc-takeaway-label">📌 À retenir</span>
<p>L'influence sociale explique pourquoi un comportement est FRÉQUENT dans un groupe \
donné ; elle n'efface jamais la responsabilité de la personne qui choisit, \
individuellement, d'agir d'une façon ou d'une autre.</p>
</div>

<details class="jc-glossary">
<summary>📖 Retrouver les définitions</summary>
<div class="jc-definitions">
<div class="jc-definition">
<span class="jc-definition-term">Valeur</span>
<p class="jc-definition-body">Ce qu'un groupe ou une société considère comme important \
ou souhaitable.</p>
</div>
<div class="jc-definition">
<span class="jc-definition-term">Norme</span>
<p class="jc-definition-body">Règle de comportement concrète, attendue dans un groupe ou \
une société, qui découle souvent d'une valeur.</p>
</div>
<div class="jc-definition">
<span class="jc-definition-term">Comportement</span>
<p class="jc-definition-body">Action réellement observée chez une personne — peut \
respecter une norme ou s'en écarter.</p>
</div>
<div class="jc-definition">
<span class="jc-definition-term">Besoin</span>
<p class="jc-definition-body">Ce dont une personne a besoin (être acceptée, appartenir, \
se sentir en sécurité...).</p>
</div>
<div class="jc-definition">
<span class="jc-definition-term">Frustration</span>
<p class="jc-definition-body">Tension ressentie quand un besoin n'est pas satisfait, ou \
qu'une norme de groupe entre en conflit avec une valeur personnelle.</p>
</div>
<div class="jc-definition">
<span class="jc-definition-term">Groupe d'appartenance</span>
<p class="jc-definition-body">Groupe auquel une personne est identifiée comme membre.</p>
</div>
<div class="jc-definition">
<span class="jc-definition-term">Influence sociale</span>
<p class="jc-definition-body">Façon dont les normes et comportements d'un groupe \
orientent le comportement d'une personne, même sans obligation formelle.</p>
</div>
<div class="jc-definition">
<span class="jc-definition-term">Socialisation</span>
<p class="jc-definition-body">Processus progressif par lequel une personne intègre les \
normes et valeurs d'un ou plusieurs groupes.</p>
</div>
</div>
</details>"""


def fse04_course_sections() -> list[tuple[str, str]]:
    """Sections (titre, Markdown/HTML) du cours FSE04 — théorie restructurée en trois
    cartes progressives avec mise en page à deux colonnes (ticket #124, voir docstring du
    module). Les sections 1, 4-10 réutilisent les mêmes transformations mécaniques que
    `app.v1.fse_course_sections.build_course_sections` ; seule la théorie devient bespoke,
    comme FSE01/FSE03."""
    sections = parse_numbered_sections(fse04_course_markdown())
    return [
        ("FSE04 — Présentation et objectifs", fix_list_blank_lines(sections[1])),
        ("FSE04 — Valeur, norme, comportement : quelle différence ?", _section_value_norm_behaviour()),
        ("FSE04 — Pourquoi suit-on parfois le groupe ?", _section_why_follow_the_group()),
        ("FSE04 — Peut-on agir autrement ?", _section_can_one_act_differently()),
        ("FSE04 — Méthode", fix_list_blank_lines(sections[4])),
        (
            "FSE04 — Exemples commentés",
            analyse_commentee_to_decrypt(
                exemple_headers_to_titles(fix_list_blank_lines(sections[5]))
            ),
        ),
        (
            "FSE04 — Comparer pour ne pas confondre",
            mauvaises_bonnes_to_comparegrid(sections[6])
            + "\n\n"
            + pieges_to_blockquotes(sections[7]),
        ),
        (
            "FSE04 — Exercices guidés",
            exercises_to_cards(sections[8] + "\n\n" + sections[9]),
        ),
        ("FSE04 — Fiche mémo", fix_list_blank_lines(sections[10])),
    ]
