"""Contenu de cours — FSE03 « Identités, traces numériques et appartenance » (ticket #97,
cahier des charges détaillé).

Même structure que FSE01/FSE02 : 1. Ce que tu dois savoir faire à l'examen —
2. Théorie progressive — 3. Définitions importantes — 4. Méthode étape par étape —
5. Exemples commentés — 6. Mauvaises réponses comparées aux bonnes — 7. Pièges et erreurs
fréquentes — 8. Exercices guidés (corrigés masqués par défaut) — 9. Corrigés très
expliqués — 10. Fiche mémo.

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
    FSE03_RECOMMENDATION_CARD_HTML,
)

from app.v1.fse_course_sections import build_course_sections


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

## 2. Théorie progressive

Chaque personne a une **identité personnelle** : ce qui la caractérise individuellement \
(son parcours, ses goûts, ses compétences). Elle a aussi une ou plusieurs **identités \
collectives** : son appartenance à un ou plusieurs groupes (une famille, un cercle \
d'amis, une profession, une communauté de loisir).

Lorsque cette identité s'exprime dans un contexte médiatique (réseaux sociaux, forums, \
plateformes en ligne), on parle d'**identité numérique** : ce n'est pas une identité \
différente, mais une application particulière de l'identité personnelle et collective à \
ce contexte précis.

Chaque activité en ligne laisse des **traces numériques**. Une trace est **volontaire** \
quand la personne la publie elle-même en connaissance de cause (une photo, un commentaire, \
un message). Une trace est **involontaire** quand elle est publiée par quelqu'un d'autre \
(une photo où l'on est identifié par un ami, un commentaire d'un tiers nous concernant), \
ou qu'elle résulte d'une action dont la personne ne maîtrise pas la visibilité future \
(un message ancien qui redevient visible des années plus tard).

L'ensemble des traces visibles par autrui construit progressivement une **réputation** : \
l'image qu'une personne donne à voir, telle qu'elle est perçue par les autres. Cette \
image ne correspond pas forcément à l'identité réelle de la personne : une trace ancienne, \
sortie de son contexte d'origine, peut donner une impression très différente de ce que la \
personne est réellement aujourd'hui. C'est pourquoi il faut toujours distinguer \
**l'identité réelle** d'une personne et **l'image qu'elle donne à voir à autrui** à \
travers ses traces numériques, volontaires ou non.

## 3. Définitions importantes

- **Identité personnelle** : ce qui caractérise une personne individuellement.
- **Identité collective** : l'appartenance d'une personne à un ou plusieurs groupes.
- **Identité numérique** : l'identité personnelle et collective telle qu'elle s'exprime \
dans un contexte médiatique (réseaux sociaux, forums, plateformes en ligne).
- **Trace numérique volontaire** : contenu publié par la personne elle-même, en \
connaissance de cause.
- **Trace numérique involontaire** : contenu publié par quelqu'un d'autre concernant la \
personne, ou contenu ancien redevenu visible sans que la personne en maîtrise la \
visibilité.
- **Réputation** : l'image qu'une personne donne à voir à autrui, construite à partir de \
l'ensemble de ses traces visibles.
- **Groupe d'appartenance** : groupe auquel une personne est identifiée comme membre \
(professionnel, familial, de loisir...).

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


def fse03_course_sections() -> list[tuple[str, str]]:
    """Sections (titre, Markdown) du cours FSE03 — refonte pédagogique et visuelle
    (ticket #105), voir `app.v1.fse_course_sections.build_course_sections`."""
    return build_course_sections("FSE03", fse03_course_markdown())
