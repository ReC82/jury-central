"""Contenu de cours — FSE05 « Image, vie privée et données personnelles » (ticket #98,
cahier des charges détaillé).

Même structure que FSE01-FSE04 : 1. Ce que tu dois savoir faire à l'examen —
2. Théorie progressive — 3. Définitions importantes — 4. Méthode étape par étape —
5. Exemples commentés — 6. Mauvaises réponses comparées aux bonnes — 7. Pièges et erreurs
fréquentes — 8. Exercices guidés (corrigés masqués par défaut) — 9. Corrigés très
expliqués — 10. Fiche mémo — 11. Sources officielles vérifiées (nouveau, ticket #98 :
« vérifie les affirmations juridiques... auprès des sources officielles et référence-les
dans la documentation »).

Périmètre strict (ticket #98, programme p. 45) : UNIQUEMENT droit à l'image, vie privée,
données personnelles et consentement, tels qu'ils s'appliquent aux médias/réseaux sociaux.
Aucune notion de responsabilité civile détaillée, de procédure judiciaire ni de montant de
dommages et intérêts (hors périmètre). Les principes énoncés sont vérifiés auprès de
l'Autorité de protection des données (APD), autorité belge officielle compétente — voir
section 11 ci-dessous pour les URL et la date de vérification exactes."""

from app.v1.fse05_content import FSE05_SITUATIONS_TEXT

from app.v1.fse_course_sections import build_course_sections


def fse05_course_markdown() -> str:
    return f"""# FSE05 — Image, vie privée et données personnelles

## 1. Ce que tu dois savoir faire à l'examen

Tu dois être capable de distinguer, dans une situation donnée, la prise de vue (photographier/\
filmer) et la diffusion (publier/partager), de déterminer si une personne apparaît comme \
sujet principal ou comme personne accessoire sur une image, et d'expliquer la conséquence sur \
le consentement nécessaire. Tu dois aussi reconnaître une utilisation de données personnelles \
qui dépasse la finalité annoncée.

**Prérequis** : ce cours réutilise la notion d'identité numérique vue en FSE03 (ce que \
quelqu'un montre de lui-même ou que d'autres montrent de lui en ligne).

## 2. Théorie progressive

Le **droit à l'image** est le droit, pour toute personne, de décider si elle peut être \
photographiée ou filmée, et si cette image peut ensuite être utilisée ou diffusée. Il faut \
distinguer deux moments bien séparés : la **prise de vue** (le fait de photographier ou de \
filmer quelqu'un) et la **diffusion** (le fait de publier, partager ou transmettre cette image \
à d'autres personnes). Un accord donné pour l'un de ces deux moments n'autorise pas \
automatiquement l'autre : on peut accepter d'être photographié sans accepter que la photo soit \
publiée sur un compte public.

Le **consentement** nécessaire dépend aussi de la façon dont une personne apparaît sur l'image. \
Une personne est **sujet principal** quand elle est mise en avant, reconnaissable et au centre \
de l'image : son consentement reste en principe nécessaire, y compris dans un lieu public. Une \
personne est **personne accessoire** quand elle se trouve par hasard sur une image (une foule, \
un arrière-plan), sans être individualisée ni mise en évidence : dans ce cas précis, un accord \
n'est en principe pas nécessaire. **Il n'existe cependant aucune règle absolue selon laquelle \
« se trouver dans un lieu public » suffirait à autoriser toute diffusion** : tout dépend de si \
la personne est reconnaissable et mise en avant, ou simplement accessoire dans la scène.

Une exception existe pour une **activité strictement personnelle ou domestique** : partager une \
photo dans un cercle très restreint (famille proche, par exemple) est traité différemment d'une \
diffusion à un large public. Mais dès qu'une image quitte ce cercle restreint pour être publiée \
plus largement (un groupe de centaines de membres, un compte public), un nouvel accord, \
spécifique à cette diffusion-là, est en principe nécessaire.

Le droit à l'image s'accompagne du droit plus général au respect de la **vie privée**. Une \
**donnée personnelle** est toute information qui permet d'identifier une personne (nom, numéro \
de téléphone, adresse, photo...). Un principe central est celui de la **finalité** : une donnée \
personnelle ne devrait être collectée et utilisée que pour un but précis, annoncé à la personne \
concernée — l'utiliser ensuite pour un autre usage, non annoncé, pose problème.

Les **mineurs** bénéficient d'une protection renforcée : plus un enfant est jeune, plus l'accord \
d'un parent est nécessaire en plus du sien ; en grandissant, l'enfant lui-même doit de plus en \
plus être associé à la décision de diffuser ou non une image de lui.

## 3. Définitions importantes

- **Droit à l'image** : droit de décider si l'on peut être photographié/filmé, et si cette \
image peut être utilisée ou diffusée.
- **Prise de vue** : le fait de photographier ou de filmer une personne.
- **Diffusion** : le fait de publier, partager ou transmettre une image à d'autres personnes.
- **Sujet principal** : personne mise en avant, reconnaissable et au centre d'une image — son \
consentement reste en principe nécessaire.
- **Personne accessoire** : personne présente par hasard sur une image (foule, arrière-plan), \
non individualisée ni mise en évidence — un accord n'est en principe pas nécessaire.
- **Activité strictement personnelle ou domestique** : partage dans un cercle très restreint \
(ex. famille proche), traité différemment d'une diffusion large.
- **Vie privée** : droit au respect de sa sphère personnelle, y compris en ligne.
- **Donnée personnelle** : toute information qui permet d'identifier une personne.
- **Finalité** : but précis pour lequel une donnée personnelle est collectée et utilisée.

## 4. Méthode étape par étape

Face à une situation impliquant une image ou une donnée personnelle, procède dans cet ordre :

1. Identifie s'il s'agit d'une question de **prise de vue**, de **diffusion**, ou des deux — \
réponds séparément pour chacune.
2. Si une image est en cause, détermine si la personne concernée est **sujet principal** ou \
**personne accessoire**.
3. Vérifie si le contexte correspond à une **activité strictement personnelle ou domestique**, \
ou si l'image/la donnée est destinée à un public plus large.
4. Si une donnée personnelle est collectée, vérifie si une **finalité précise** est annoncée.
5. Conclus en expliquant pourquoi un consentement est (ou n'est pas) en principe nécessaire, \
sans jamais invoquer la seule présence dans un lieu public comme règle absolue.

## 5. Exemples commentés

### Exemple 1 — Situation 1 (monument touristique)

{FSE05_SITUATIONS_TEXT.splitlines()[2]}

**Analyse commentée :** les passants apparaissent par hasard, en arrière-plan d'une photo de \
monument : ce sont des personnes accessoires, non individualisées. Prise de vue et diffusion de \
cette photo ne nécessitent en principe pas leur accord — mais cela tient au caractère accessoire \
de leur présence, pas au seul fait que la scène se déroule dans un lieu public.

### Exemple 2 — Situation 2 (anniversaire, Nabil)

Thomas prend une photo nette de Nabil, reconnaissable au premier plan en train de souffler ses \
bougies, puis la publie sur son compte public sans lui en parler.

**Analyse commentée :** Nabil est ici **sujet principal** : il est mis en avant et parfaitement \
identifiable. La prise de vue a pu se faire dans un cadre amical, mais la **diffusion** sur un \
compte public (1 200 abonnés) est un acte distinct, qui nécessite en principe l'accord spécifique \
de Nabil — un accord implicite pour être photographié ne vaut pas accord pour une diffusion \
publique.

### Exemple 3 — Situation 6 (formulaire concours)

Un site demande nom, téléphone et établissement scolaire « pour participer à un concours », sans \
préciser l'usage ultérieur de ces informations.

**Analyse commentée :** ce sont des **données personnelles** (elles permettent d'identifier une \
personne précise). Le problème ici n'est pas la collecte elle-même, mais l'absence de **finalité \
précisée** : les visiteurs ne savent pas à quel usage précis ces données seront destinées au-delà \
du concours annoncé.

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse** (situation 3, manifestation filmée) : « C'est un lieu public, donc tout \
le monde peut être filmé et diffusé librement. » → applique une règle absolue qui n'existe pas.
- ✅ **Bonne réponse** : « Le reportage montre la foule sans isoler un visage en particulier : \
les participants apparaissent comme personnes accessoires dans ce contexte précis, ce qui change \
la réponse — pas le seul fait que la scène se passe dans la rue. »

- ❌ **Mauvaise réponse** (situation 4, photo transmise puis publiée par Chloé) : « Puisque la \
photo lui a été envoyée, Chloé peut la publier où elle veut. » → confond prise de vue/réception \
d'une image et diffusion à un nouveau public.
- ✅ **Bonne réponse** : « La photo a été prise et partagée dans un cadre personnel restreint ; \
la publier dans un groupe de 500 membres est une diffusion nouvelle et plus large, qui \
nécessiterait en principe l'accord des personnes présentes sur la photo. »

## 7. Pièges et erreurs fréquentes

- **Confondre prise de vue et diffusion** : ce sont deux actes distincts, chacun pouvant \
nécessiter un accord propre.
- **Croire que « lieu public » autorise automatiquement toute diffusion** : seule l'absence de \
mise en avant individuelle (personne accessoire) change la réponse, pas le lieu en lui-même.
- **Oublier la distinction sujet principal/personne accessoire** : une personne reconnaissable \
et mise en avant reste protégée, même en public.
- **Ignorer que recevoir une donnée ou une image dans un cadre restreint n'autorise pas sa \
diffusion à un public plus large.**

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Prise de vue et diffusion séparément (essaie avant de regarder la \
correction)</summary>

Reprends la situation 2 (Thomas et Nabil). Réponds séparément : la prise de vue de la photo \
pose-t-elle problème ? La diffusion sur le compte public pose-t-elle problème ? Justifie chaque \
réponse.

<details>
<summary>Voir la correction expliquée</summary>

Prise de vue : prendre la photo lors d'un anniversaire entre amis correspond à un cadre \
personnel/amical ; ce moment seul ne pose pas nécessairement problème. Diffusion : publier \
ensuite cette photo sur un compte public (1 200 abonnés), sans en parler à Nabil, est un acte \
distinct — Nabil est sujet principal, reconnaissable et mis en avant, et son accord serait en \
principe nécessaire pour cette diffusion précise.

Ce corrigé fonctionne parce qu'il traite les deux actes séparément, comme l'exige la méthode, au \
lieu de répondre globalement « oui » ou « non » pour toute la situation.
</details>
</details>

<details>
<summary>Exercice 2 — Personne principale ou accessoire (essaie avant de regarder la \
correction)</summary>

Compare la situation 1 (monument touristique) et la situation 5 (parent publiant une photo de \
son enfant). Dans laquelle la personne concernée est-elle clairement sujet principal, et \
pourquoi cela change-t-il la réponse par rapport à l'autre situation ?

<details>
<summary>Voir la correction expliquée</summary>

Dans la situation 5, l'enfant est sujet principal : il est identifiable, mis en avant et seul \
visé par la photo — son accord (et celui d'un parent, vu son âge) est en principe nécessaire \
avant diffusion à 800 contacts. Dans la situation 1, les passants sont accessoires, présents par \
hasard en arrière-plan d'une photo de monument, sans être individualisés : la réponse est donc \
différente, non pas parce que l'un est un enfant et l'autre un adulte, mais parce que l'un est \
mis en avant et l'autre non.

Ce corrigé fonctionne parce qu'il isole le critère pertinent (principal/accessoire) plutôt que \
de s'appuyer sur un élément non pertinent comme l'âge ou le lieu.
</details>
</details>

## 9. Corrigés très expliqués

**Question :** « Le site de la situation 6 peut-il tout de même collecter nom, téléphone et \
école des visiteurs ? »

**Corrigé expliqué :** la collecte de données personnelles n'est pas interdite en soi, mais elle \
devrait s'accompagner d'une **finalité précise**, annoncée aux personnes concernées (par exemple \
: « ces informations serviront uniquement à vous contacter en cas de victoire, et seront \
supprimées après le concours »). Dans la situation décrite, aucune finalité n'est précisée : les \
visiteurs ne peuvent donc pas savoir si leurs informations seront réutilisées à d'autres fins. \
C'est cette absence de finalité annoncée qui pose problème, pas la collecte de données en \
elle-même.

Ce corrigé fonctionne parce qu'il distingue clairement le principe général (la collecte est \
possible) de la condition manquante dans ce cas précis (l'absence de finalité annoncée).

## 10. Fiche mémo

- Prise de vue (photographier/filmer) et diffusion (publier/partager) sont deux actes distincts \
: un accord pour l'un ne vaut pas accord pour l'autre.
- Sujet principal (mis en avant, reconnaissable) : consentement en principe nécessaire, y \
compris en public. Personne accessoire (foule, arrière-plan, non individualisée) : en principe \
pas d'accord nécessaire.
- Aucune règle absolue « lieu public = diffusion libre ».
- Une activité strictement personnelle ou domestique est traitée différemment d'une diffusion \
large — mais quitter ce cercle restreint change la réponse.
- Donnée personnelle = toute information qui identifie une personne ; elle devrait toujours \
être associée à une finalité précise et annoncée.
- Les mineurs bénéficient d'une protection renforcée (accord parental, puis association \
croissante de l'enfant avec l'âge).

## 11. Sources officielles vérifiées

Les principes énoncés ci-dessus (distinction prise de vue/diffusion, sujet principal/personne \
accessoire, exception de l'activité personnelle ou domestique, consentement par finalité, \
protection renforcée des mineurs) sont vérifiés auprès de l'**Autorité de protection des \
données** (APD), autorité belge officielle compétente en matière de vie privée et de droit à \
l'image :

- Autorité de protection des données, « Droit à l'image », \
https://www.autoriteprotectiondonnees.be/citoyen/droit-a-l-image — consulté le 2026-10-01.
- Autorité de protection des données, « Principe du consentement », \
https://www.autoriteprotectiondonnees.be/citoyen/themes/le-droit-a-l-image/loi-du-30-juillet-2018/principe-du-consentement \
— consulté le 2026-10-01.

Ces règles évoluent : en cas de doute sur un cas réel, consulte systématiquement le site de \
l'Autorité de protection des données plutôt que ce cours, qui reste un support pédagogique \
simplifié.
"""


def fse05_course_sections() -> list[tuple[str, str]]:
    """Sections (titre, Markdown) du cours FSE05 — refonte pédagogique et visuelle
    (ticket #105), voir `app.v1.fse_course_sections.build_course_sections`."""
    return build_course_sections("FSE05", fse05_course_markdown())
