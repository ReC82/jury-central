"""Contenu de cours — FSE03 « Identités, traces numériques et appartenance » (ticket #97,
cahier des charges détaillé).

Même structure générale que FSE01/FSE02 : 1. Ce que tu dois savoir faire à l'examen —
2. Théorie progressive — 3. Définitions importantes — 4. Méthode étape par étape —
5. Exemples commentés — 6. Mauvaises réponses comparées aux bonnes — 7. Pièges et erreurs
fréquentes — 8. Exercices guidés (corrigés masqués par défaut) — 9. Corrigés très
expliqués — 10. Fiche mémo.

Refonte ticket #120 : les sections 2 et 3 (« Théorie progressive » + « Définitions
importantes »), auparavant fusionnées par `app.v1.fse_course_sections.build_course_sections`
en un seul grand bloc « Théorie : notions et définitions », sont remplacées par TROIS
cartes théoriques progressives, bespoke (comme FSE01, voir `app.v1.fse01_course`) : « Qui
suis-je ? » (identité personnelle/collective, groupe d'appartenance, identité numérique),
« Quelles traces je laisse ? » (trace volontaire/involontaire, nuance ancienne publication
volontaire ≠ devenue involontaire), « Quelle image les autres voient-ils ? » (schéma
traces → perception → réputation, identité réelle vs image perçue). La liste de
définitions, désormais répétée par les explications visibles, devient un lexique repliable
(`.jc-glossary`, disponible à l'impression même fermé) à la fin de la troisième carte —
voir `docs/components/TheoryProgression.md`. Les sections 1, 4-10 ne sont pas modifiées
dans leur matière : seule la section 2+3 change de forme, aucune notion n'est retirée.

Périmètre strict (ticket #97, programme p. 44-45) : identité personnelle/collective,
identité numérique, traces volontaires/involontaires, réputation, groupe d'appartenance,
distinction identité/image donnée à autrui. Aucune autre notion (ex. droit à l'oubli,
protection des données personnelles au sens juridique) n'est introduite ici : elle relève
d'un autre mini-cours (FSE05, voir `docs/content_plan_fse.md`)."""

from app.v1.fse03_content import (
    FSE03_BIRTHDAY_CARD_HTML,
    FSE03_FORUM_CARD_HTML,
    FSE03_GROUPS_CARD_HTML,
    FSE03_HR_NOTE_CARD_HTML,
    FSE03_HR_NOTE_TITLE,
    FSE03_PROFILE_CARD_HTML,
    FSE03_PROFILE_TITLE,
    FSE03_RECENT_POST_CARD_HTML,
    FSE03_RECENT_POST_TITLE,
    FSE03_RECOMMENDATION_CARD_HTML,
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


def fse03_course_markdown() -> str:
    return f"""# FSE03 — Identités, traces numériques et appartenance

## 1. Ce que tu dois savoir faire à l'examen

Tu dois être capable de distinguer une trace numérique volontaire d'une trace \
involontaire, d'expliquer la différence entre l'identité réelle d'une personne et l'image \
qu'elle donne à voir à autrui, et d'expliquer les conséquences concrètes d'anciennes \
publications sur une candidature ou une réputation.

**Prérequis** : ce cours réutilise le canal et le message vus dans FSE01 — une \
publication en ligne est un message transmis via un canal (réseau social, forum) qui \
laisse une trace durable, contrairement à une conversation orale.

## 4. Méthode étape par étape

Face à un ensemble de traces numériques concernant une personne, procède dans cet ordre :

1. Pour chaque trace, détermine si elle est **volontaire** (publiée par la personne \
elle-même) ou **involontaire** (publiée par un tiers, ou ancienne et redevenue visible).
2. Identifie les **groupes d'appartenance** visibles à travers ces traces.
3. Distingue ce que ces traces révèlent de l'**identité réelle** de la personne \
aujourd'hui, de ce qu'elles donnent comme **image** à un observateur extérieur qui ne \
connaît pas le contexte.
4. Si la situation l'exige, explique la **conséquence concrète** d'une trace précise sur \
une situation réelle (une candidature, une relation), en te basant uniquement sur ce que \
le document donne à voir.

## 5. Exemples commentés

### Exemple 1 — {FSE03_PROFILE_TITLE}

{FSE03_PROFILE_CARD_HTML}

{FSE03_BIRTHDAY_CARD_HTML}

{FSE03_FORUM_CARD_HTML}

{FSE03_RECOMMENDATION_CARD_HTML}

{FSE03_GROUPS_CARD_HTML}

**Analyse commentée :**
- Trace 1 (photo de profil professionnelle) : **volontaire** — publiée par Sophie \
elle-même, dans un contexte professionnel assumé.
- Trace 2 (photo d'anniversaire identifiée par une amie) : **involontaire** — Sophie ne \
l'a pas publiée elle-même et n'a pas choisi son identification.
- Trace 3 (commentaire sur un forum de jeux vidéo) : **volontaire** au moment de sa \
publication, mais ancienne — Sophie l'a bien écrit elle-même, même si elle ne le \
publierait probablement plus aujourd'hui.
- Trace 4 (recommandation d'un collègue) : **involontaire** — rédigée par quelqu'un \
d'autre à son sujet.
- Groupes d'appartenance visibles : un groupe de loisir (randonneurs amateurs) et un \
groupe professionnel (gestionnaires de stock).

### Exemple 2 — {FSE03_HR_NOTE_TITLE}

{FSE03_HR_NOTE_CARD_HTML}

**Analyse commentée :** ce document montre concrètement comment des traces numériques \
influencent une situation réelle. La recommandation professionnelle (trace involontaire, \
positive) renforce l'image de Sophie comme candidate sérieuse. Le commentaire ancien sur \
le forum (trace volontaire, mais vieille de cinq ans et hors contexte professionnel) crée \
une impression négative chez le recruteur, même si le document précise explicitement que \
ce commentaire date d'avant le début de sa carrière et ne reflète pas ses compétences \
réelles. On voit ici la différence entre l'identité réelle de Sophie (une professionnelle \
rigoureuse, selon son ancien collègue) et l'image que certaines traces anciennes peuvent \
donner à un observateur qui ne connaît pas le contexte.

### Exemple 3 — {FSE03_RECENT_POST_TITLE}

{FSE03_RECENT_POST_CARD_HTML}

**Analyse commentée :** cette publication est, comme la photo de profil (exemple 1), une \
trace **volontaire** : Sophie l'a écrite et publiée elle-même. Elle est aussi **récente** \
et directement liée à son contexte professionnel actuel — à l'inverse du commentaire \
ancien vu dans l'exemple 1, qui datait d'avant le début de sa carrière. Elle illustre un \
cas où l'image donnée à voir correspond bien à l'identité réelle de Sophie aujourd'hui : \
une professionnelle investie dans son métier. Toutes les traces ne créent donc pas un \
écart entre identité réelle et image perçue : ce sont surtout les traces anciennes, hors \
contexte, ou publiées par d'autres qui risquent de produire cet écart — pas une trace \
récente et volontaire qui reste fidèle à la situation actuelle de la personne.

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse** (question : « La photo d'anniversaire est-elle une trace \
volontaire ? ») : « Oui, puisqu'elle apparaît sur la photo. » → confond le fait \
d'apparaître sur une trace avec le fait de l'avoir publiée soi-même.
- ✅ **Bonne réponse** : « Non : la photo a été publiée par une amie, pas par Sophie \
elle-même — c'est une trace involontaire, même si Sophie y apparaît. »

- ❌ **Mauvaise réponse** (question : « Le commentaire sur le forum révèle-t-il qui est \
réellement Sophie aujourd'hui ? ») : « Oui, puisqu'elle l'a écrit elle-même. » → confond \
une trace volontaire ancienne avec un reflet fidèle de l'identité actuelle de la personne.
- ✅ **Bonne réponse** : « Pas nécessairement : ce commentaire date de cinq ans, dans un \
contexte de loisir précis. Il donne une IMAGE négative à qui le découvre hors contexte, \
mais ne dit rien de certain sur les compétences professionnelles de Sophie aujourd'hui. »

## 7. Pièges et erreurs fréquentes

- **Confondre apparaître sur une trace et l'avoir publiée** : être identifié·e sur une \
photo par quelqu'un d'autre ne fait pas de cette photo une trace volontaire.
- **Croire qu'une trace ancienne a disparu** : une trace volontaire publiée il y a \
longtemps peut rester visible et redevenir une trace qui échappe au contrôle de la \
personne, même si elle l'a bien publiée elle-même à l'origine.
- **Confondre identité réelle et image donnée à voir** : une personne peut être perçue \
très différemment de ce qu'elle est réellement, à cause d'une trace ancienne ou sortie de \
son contexte.
- **Mélanger plusieurs groupes d'appartenance** : une personne peut appartenir à \
plusieurs groupes en même temps (professionnel, loisir...) sans contradiction.

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Classer les traces de Sophie Lambert (essaie avant de regarder la \
correction)</summary>

Reprends les cinq éléments de l'exemple 1. Pour chacun, indique s'il s'agit d'une trace \
volontaire ou involontaire, en justifiant en une phrase.

<details>
<summary>Voir la correction expliquée</summary>

1. Photo de profil professionnelle : volontaire — publiée par Sophie elle-même.
2. Photo d'anniversaire identifiée par une amie : involontaire — publiée et identifiée \
par quelqu'un d'autre.
3. Commentaire sur le forum de jeux vidéo : volontaire — écrit par Sophie elle-même, même \
s'il est ancien.
4. Recommandation professionnelle d'un collègue : involontaire — rédigée par quelqu'un \
d'autre à son sujet.
5. Appartenance aux deux groupes en ligne : ce ne sont pas des traces à classer \
volontaire/involontaire au sens strict, mais des indices visibles d'appartenance à des \
groupes, qui peuvent résulter de choix volontaires (s'inscrire à un groupe).

Ce corrigé fonctionne parce qu'il justifie chaque classement par QUI a publié la trace, \
jamais seulement par le fait que la personne y apparaisse ou non.
</details>
</details>

<details>
<summary>Exercice 2 — Expliquer une conséquence concrète (essaie avant de regarder la \
correction)</summary>

Reprends la note du service recrutement (exemple 2). Explique pourquoi le commentaire \
ancien sur le forum influence l'impression du recruteur, alors même que le document \
précise qu'il ne reflète pas les compétences professionnelles de Sophie.

<details>
<summary>Voir la correction expliquée</summary>

Même si ce commentaire date d'avant le début de la carrière de Sophie et concerne un \
contexte de loisir sans lien avec le poste, il reste visible publiquement sous son vrai \
nom. Un recruteur qui le découvre sans connaître ce contexte peut en tirer une impression \
négative, car il juge sur la base d'une IMAGE isolée, pas sur l'ensemble de l'identité \
réelle de la personne. Le document montre bien cette tension : le recruteur reconnaît \
lui-même que ce commentaire « ne reflète pas ses compétences réelles », mais admet \
qu'il « pourrait donner une impression négative à qui tombe dessus sans contexte ».

Ce corrigé fonctionne parce qu'il distingue explicitement l'effet sur l'IMAGE perçue \
(négatif, à cause du manque de contexte) de ce que le document dit réellement sur \
l'identité professionnelle de Sophie (positive, confirmée par la recommandation).
</details>
</details>

## 9. Corrigés très expliqués

**Question :** « Sophie est-elle responsable du fait que la photo d'anniversaire soit \
visible publiquement ? »

**Corrigé expliqué :** pas directement. La photo a été publiée par une amie, qui y a \
identifié Sophie par son nom — c'est donc une trace involontaire du point de vue de \
Sophie : elle n'a pas choisi de la publier, ni de s'y faire identifier. Le document \
précise cependant que Sophie n'a pas demandé son retrait, ce qui signifie qu'elle a \
connaissance de son existence sans pour autant en être l'autrice. La responsabilité de la \
PUBLICATION initiale revient à l'amie ; la question de son maintien en ligne, elle, \
dépend désormais aussi de Sophie.

Ce corrigé fonctionne parce qu'il distingue deux moments différents (la publication \
initiale, involontaire pour Sophie, et son maintien en ligne, qu'elle pourrait \
potentiellement faire retirer) plutôt que de répondre par un simple oui ou non.

## 10. Fiche mémo

- Identité numérique = identité personnelle et collective, appliquée au contexte \
médiatique — pas une identité à part.
- Trace volontaire = publiée par la personne elle-même ; trace involontaire = publiée par \
quelqu'un d'autre, ou ancienne et redevenue visible.
- Apparaître sur une trace ≠ l'avoir publiée soi-même.
- La réputation (image donnée à voir) peut différer de l'identité réelle, surtout à cause \
de traces anciennes ou sorties de leur contexte.
- Une ancienne publication peut avoir des conséquences réelles des années plus tard (ex. \
une candidature), même sans lien avec le sujet concerné.
"""


def _section_identity() -> str:
    """« Qui suis-je ? » — identité personnelle/collective, groupe d'appartenance,
    identité numérique (ticket #120). Tout le contenu à l'intérieur d'un `<div>`/`<details>`
    est écrit en HTML littéral (`<strong>`, jamais `**gras**`) : `app.content.render_markdown`
    ne retraite jamais le Markdown situé à l'intérieur d'un bloc HTML brut (diagnostic
    ticket #112)."""
    return """<div class="jc-prose">
<p>Chaque personne peut se décrire de deux manières complémentaires : par ce qui la rend \
unique, et par les groupes auxquels elle appartient.</p>
</div>

<div class="jc-compare">
<div class="jc-compare-item jc-compare-item--a">
<span class="jc-compare-label">Identité personnelle</span>
<p>Ce qui caractérise une personne individuellement : son parcours, ses goûts, ses \
compétences.</p>
<p><strong>Exemple :</strong> Sophie Lambert aime la randonnée et travaille comme \
gestionnaire de stock.</p>
</div>
<div class="jc-compare-item jc-compare-item--b">
<span class="jc-compare-label">Identité collective</span>
<p>L'appartenance d'une personne à un ou plusieurs groupes : une famille, un cercle \
d'amis, une profession, une communauté de loisir.</p>
<p><strong>Exemple :</strong> Sophie appartient à un groupe de randonneurs et à un groupe \
de gestionnaires de stock — deux <strong>groupes d'appartenance</strong> différents, sans \
aucune contradiction entre eux.</p>
</div>
</div>

<div class="jc-prose">
<p>Une personne peut appartenir à plusieurs groupes à la fois (professionnel, familial, de \
loisir...) : ce n'est jamais contradictoire.</p>
<p>Lorsque cette double identité — personnelle et collective — s'exprime dans un contexte \
médiatique (réseaux sociaux, forums, plateformes en ligne), on parle d'<strong>identité \
numérique</strong>. Ce n'est pas une identité différente : c'est l'application de \
l'identité personnelle et collective à ce contexte précis.</p>
</div>

<div class="jc-takeaway">
<span class="jc-takeaway-label">📌 À retenir</span>
<p>L'identité numérique n'ajoute rien de nouveau à une personne : c'est la manière dont \
son identité personnelle et collective s'exprime en ligne.</p>
</div>"""


def _section_traces() -> str:
    """« Quelles traces je laisse ? » — trace volontaire/involontaire, nuance ancienne
    publication volontaire ≠ devenue involontaire (ticket #120)."""
    return """<div class="jc-prose">
<p>Chaque activité en ligne laisse une trace numérique. Toutes les traces ne se \
ressemblent pas : certaines sont publiées par la personne elle-même, d'autres par \
quelqu'un d'autre à son sujet.</p>
</div>

<div class="jc-compare">
<div class="jc-compare-item jc-compare-item--a">
<span class="jc-compare-label">Trace volontaire</span>
<p>Publiée par la personne elle-même, en connaissance de cause.</p>
<p><strong>Exemple :</strong> Sophie publie elle-même une photo sur son profil \
professionnel.</p>
</div>
<div class="jc-compare-item jc-compare-item--b">
<span class="jc-compare-label">Trace involontaire</span>
<p>Publiée par quelqu'un d'autre, ou résultant d'une action dont la personne ne maîtrise \
plus la visibilité.</p>
<p><strong>Exemple :</strong> une amie publie une photo où Sophie est identifiée, sans que \
Sophie l'ait décidé.</p>
</div>
</div>

<blockquote>
<p>Une ancienne publication volontaire ne devient pas automatiquement une trace \
involontaire. Si Sophie a bien écrit elle-même un commentaire il y a cinq ans, cela reste \
un acte volontaire au moment où elle l'a publié. Ce qui échappe à son contrôle aujourd'hui, \
c'est sa <strong>visibilité ultérieure</strong> : un message ancien peut redevenir visible \
des années plus tard, sans qu'elle l'ait recherché — ce n'est pas la même chose que si \
quelqu'un d'autre l'avait publié à sa place.</p>
</blockquote>

<div class="jc-takeaway">
<span class="jc-takeaway-label">📌 À retenir</span>
<p>Pour classer une trace, demande-toi toujours QUI l'a publiée — jamais seulement si la \
personne y apparaît.</p>
</div>"""


def _section_image() -> str:
    """« Quelle image les autres voient-ils ? » — ticket #126 (correction de composition
    après retour visuel réel sur le site, le ticket #124 n'ayant pas suffi) : introduction
    courte (pleine largeur, pas de `.jc-prose` isolé) → schéma traces → perception →
    réputation → trois limites en cartes de largeur égale
    (`.jc-theory-cards.jc-theory-cards--three`) → rangée à deux colonnes identité réelle/
    image perçue + exemple concret (`.jc-theory-split`) → encadré « À retenir » compact →
    lexique repliable des 7 définitions, inchangé. Aucune nuance retirée : les trois
    limites (partielle/ancienne/hors contexte) et la distinction identité réelle/image
    perçue restent intégralement expliquées, seule la phrase de l'encadré est une synthèse
    volontairement courte."""
    return """<p>L'ensemble des traces visibles par autrui construit progressivement une \
image de la personne, telle qu'elle est perçue par les autres.</p>

<div class="jc-flow">
<div class="jc-flow-step">Traces visibles<small>ce que l'on peut voir en ligne</small></div>
<div class="jc-flow-arrow" aria-hidden="true">→</div>
<div class="jc-flow-step">Perception des autres<small>l'interprétation qu'on en fait</small></div>
<div class="jc-flow-arrow" aria-hidden="true">→</div>
<div class="jc-flow-step">Réputation<small>l'image qui en résulte</small></div>
</div>

<div class="jc-theory-cards jc-theory-cards--three">
<div class="jc-theory-card">
<span class="jc-theory-card-icon" aria-hidden="true">🧩</span>
<span class="jc-theory-card-title">Une image partielle</span>
<p>Les traces visibles ne montrent qu'une partie de la personne — jamais la personne tout \
entière.</p>
</div>
<div class="jc-theory-card">
<span class="jc-theory-card-icon" aria-hidden="true">🕰️</span>
<span class="jc-theory-card-title">Une trace ancienne</span>
<p>Une trace vieille de plusieurs années ne dit rien de certain sur qui est la personne \
aujourd'hui.</p>
</div>
<div class="jc-theory-card">
<span class="jc-theory-card-icon" aria-hidden="true">🖼️</span>
<span class="jc-theory-card-title">Un contexte manquant</span>
<p>Un message écrit dans une situation précise peut être interprété très différemment une \
fois détaché de ce contexte.</p>
</div>
</div>

<div class="jc-theory-split">
<div class="jc-theory-split-main">
<span class="jc-theory-split-main-title">Identité réelle et image perçue</span>
<p>Il faut toujours distinguer <strong>l'identité réelle</strong> d'une personne — qui \
elle est réellement, aujourd'hui — de <strong>l'image qu'elle donne à voir à autrui</strong> \
à travers ses traces, volontaires ou non. L'une n'efface jamais l'autre : une image \
publique partielle, ancienne ou hors contexte ne devient pas l'identité réelle de la \
personne, elle reste une perception construite par d'autres.</p>
</div>
<div class="jc-theory-split-aside">
<span class="jc-theory-split-aside-label">Exemple concret</span>
<p>Un recruteur qui découvre un commentaire vieux de cinq ans, sans connaître son \
contexte, peut s'en faire une image différente de qui la personne est réellement \
aujourd'hui.</p>
</div>
</div>

<div class="jc-takeaway">
<span class="jc-takeaway-label">📌 À retenir</span>
<p>La réputation est une image perçue : elle ne résume pas qui est réellement une \
personne.</p>
</div>

<details class="jc-glossary">
<summary>📖 Retrouver les définitions</summary>
<div class="jc-definitions">
<div class="jc-definition">
<span class="jc-definition-term">Identité personnelle</span>
<p class="jc-definition-body">Ce qui caractérise une personne individuellement.</p>
</div>
<div class="jc-definition">
<span class="jc-definition-term">Identité collective</span>
<p class="jc-definition-body">L'appartenance d'une personne à un ou plusieurs groupes.</p>
</div>
<div class="jc-definition">
<span class="jc-definition-term">Groupe d'appartenance</span>
<p class="jc-definition-body">Groupe auquel une personne est identifiée comme membre \
(professionnel, familial, de loisir...).</p>
</div>
<div class="jc-definition">
<span class="jc-definition-term">Identité numérique</span>
<p class="jc-definition-body">L'identité personnelle et collective telle qu'elle \
s'exprime dans un contexte médiatique.</p>
</div>
<div class="jc-definition">
<span class="jc-definition-term">Trace numérique volontaire</span>
<p class="jc-definition-body">Contenu publié par la personne elle-même, en connaissance de \
cause.</p>
</div>
<div class="jc-definition">
<span class="jc-definition-term">Trace numérique involontaire</span>
<p class="jc-definition-body">Contenu publié par quelqu'un d'autre, ou contenu ancien \
redevenu visible sans que la personne en maîtrise la visibilité.</p>
</div>
<div class="jc-definition">
<span class="jc-definition-term">Réputation</span>
<p class="jc-definition-body">L'image qu'une personne donne à voir à autrui, construite à \
partir de l'ensemble de ses traces visibles.</p>
</div>
</div>
</details>"""


def fse03_course_sections() -> list[tuple[str, str]]:
    """Sections (titre, Markdown/HTML) du cours FSE03 — refonte pédagogique et visuelle
    (ticket #105), théorie restructurée en trois cartes progressives (ticket #120, voir
    docstring du module). Les sections 1, 4-10 réutilisent les mêmes transformations
    mécaniques que `app.v1.fse_course_sections.build_course_sections` (FSE02-FSE16),
    seule la théorie (sections 2+3 d'origine) devient bespoke, comme FSE01."""
    sections = parse_numbered_sections(fse03_course_markdown())
    return [
        ("FSE03 — Présentation et objectifs", fix_list_blank_lines(sections[1])),
        ("FSE03 — Qui suis-je ?", _section_identity()),
        ("FSE03 — Quelles traces je laisse ?", _section_traces()),
        ("FSE03 — Quelle image les autres voient-ils ?", _section_image()),
        ("FSE03 — Méthode", fix_list_blank_lines(sections[4])),
        (
            "FSE03 — Exemples commentés",
            analyse_commentee_to_decrypt(
                exemple_headers_to_titles(fix_list_blank_lines(sections[5]))
            ),
        ),
        (
            "FSE03 — Comparer pour ne pas confondre",
            mauvaises_bonnes_to_comparegrid(sections[6])
            + "\n\n"
            + pieges_to_blockquotes(sections[7]),
        ),
        (
            "FSE03 — Exercices guidés",
            exercises_to_cards(sections[8] + "\n\n" + sections[9]),
        ),
        ("FSE03 — Fiche mémo", fix_list_blank_lines(sections[10])),
    ]
