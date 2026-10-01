"""Contenu de cours — FSE06 « Droits et comportements illicites en ligne » (ticket #98,
cahier des charges détaillé).

Même structure que FSE01-FSE05 : 1. Ce que tu dois savoir faire à l'examen —
2. Théorie progressive — 3. Définitions importantes — 4. Méthode étape par étape —
5. Exemples commentés — 6. Mauvaises réponses comparées aux bonnes — 7. Pièges et erreurs
fréquentes — 8. Exercices guidés (corrigés masqués par défaut) — 9. Corrigés très
expliqués — 10. Fiche mémo — 11. Sources officielles vérifiées.

Périmètre strict (ticket #98, programme p. 45) : reconnaître des comportements à partir
d'indices dans un scénario, JAMAIS de qualification pénale précise ni de peine (conformément
au ticket : « utiliser les termes de l'ancien exemple comme vocabulaire pédagogique
historique, sans figer les qualifications pénales ni les peines »). Les catégories
pédagogiques utilisées sont vérifiées auprès du Centre for Cybersecurity Belgium (Safeonweb)
et de la Police fédérale belge — voir section 11."""

from app.v1.fse06_content import FSE06_SCENARIOS_TEXT


def fse06_course_markdown() -> str:
    return f"""# FSE06 — Droits et comportements illicites en ligne

## 1. Ce que tu dois savoir faire à l'examen

Tu dois être capable de reconnaître, dans un scénario décrit, le ou les comportements en ligne \
qui posent problème (cyberharcèlement, injure, accusation non étayée/calomnie, menace, \
racisme/discrimination, usurpation d'identité, intrusion informatique, diffusion malveillante, \
traitement de données sans base valable), d'expliquer les indices qui te permettent de les \
identifier, et de distinguer ces comportements d'une critique couverte par la liberté \
d'expression. **Tu n'as jamais besoin de citer un numéro d'article de loi ni une peine** : \
seuls les indices du scénario comptent.

**Prérequis** : ce cours réutilise la notion de donnée personnelle vue en FSE05 (information \
qui permet d'identifier une personne).

## 2. Théorie progressive

La **liberté d'expression** permet à chacun de donner son avis, y compris de façon critique ou \
négative, sur une personne, un service ou une situation. Mais cette liberté a des **limites** : \
certains comportements en ligne dépassent la simple expression d'une opinion et peuvent nuire \
gravement à une personne.

Le **cyberharcèlement** désigne des propos ou actes hostiles, **répétés dans le temps**, visant \
une même personne en ligne, surtout lorsque cette personne a demandé que cela cesse. Une \
**injure** est un propos insultant visant une personne, sans affirmer de fait précis à son \
sujet (« tu es nul »). Une **accusation non étayée** (ou calomnie) affirme au contraire un fait \
précis et négatif sur une personne, sans preuve pour l'appuyer (« il vole ses clients »). Une \
**menace** annonce un mal futur dans le but de faire peur ou de contraindre quelqu'un. Un \
comportement **raciste ou discriminatoire** traite une personne défavorablement en raison de \
son origine, de sa couleur de peau, de sa religion ou d'une autre caractéristique protégée.

L'**usurpation d'identité** consiste à se faire passer pour quelqu'un d'autre en ligne (faux \
compte, utilisation de sa photo ou de son nom) sans son accord. Une **intrusion informatique** \
consiste à accéder, sans autorisation, à un compte, un appareil ou des données appartenant à \
autrui. La **diffusion malveillante** consiste à partager une information, une image ou une \
vidéo dans le but explicite de nuire à la personne concernée. Enfin, un **traitement de données \
sans base valable** consiste à collecter, utiliser ou transmettre des données personnelles sans \
justification acceptable ni information des personnes concernées (notion déjà vue, appliquée \
ici à un contexte de comportement en ligne).

Pour reconnaître ces comportements, il faut toujours s'appuyer sur des **indices concrets** du \
scénario : répétition, absence de preuve, présence d'une menace explicite, usage du nom/de la \
photo d'autrui, accès non autorisé, intention de nuire, absence d'information sur l'usage d'une \
donnée. L'**absence de ces indices**, à l'inverse, signale une critique couverte par la liberté \
d'expression.

## 3. Définitions importantes

- **Liberté d'expression** : droit de donner son avis, y compris de façon critique, dans les \
limites qui protègent autrui.
- **Cyberharcèlement** : propos ou actes hostiles répétés en ligne, visant une même personne.
- **Injure** : propos insultant visant une personne, sans fait précis affirmé.
- **Accusation non étayée / calomnie** : affirmation d'un fait précis et négatif, non prouvé, \
qui nuit à la réputation d'une personne.
- **Menace** : annonce d'un mal futur, dans le but de faire peur ou de contraindre.
- **Racisme / discrimination** : traitement défavorable fondé sur une origine, une couleur de \
peau, une religion ou une autre caractéristique protégée.
- **Usurpation d'identité** : se faire passer pour quelqu'un d'autre en ligne, sans son accord.
- **Intrusion informatique** : accès non autorisé à un compte, un appareil ou des données \
d'autrui.
- **Diffusion malveillante** : partage d'une information, d'une image ou d'une vidéo dans le \
but explicite de nuire.
- **Traitement de données sans base valable** : collecte ou usage de données personnelles sans \
justification acceptable ni information des personnes concernées.

## 4. Méthode étape par étape

Face à un scénario, procède dans cet ordre :

1. Repère les **indices concrets** décrits (répétition, preuve absente, menace, usage du \
nom/photo d'autrui, accès non autorisé, intention de nuire, absence d'information).
2. Associe ces indices à **une ou plusieurs catégories** vues ci-dessus.
3. Vérifie qu'il ne s'agit pas d'une simple **critique ou opinion**, sans insulte ni accusation \
non prouvée.
4. Explique ta réponse en citant les indices précis du scénario — jamais un article de loi ou \
une peine.

## 5. Exemples commentés

### Exemple 1 — Scénario 1 (Sarah)

{FSE06_SCENARIOS_TEXT.splitlines()[2]}

**Analyse commentée :** l'indice clé est la **répétition dans le temps** (« depuis plusieurs \
semaines », « chaque jour ») et le fait que Sarah ait demandé que cela cesse sans effet. Cela \
correspond au cyberharcèlement.

### Exemple 2 — Scénario 3 (commerçant accusé)

{FSE06_SCENARIOS_TEXT.splitlines()[6]}

**Analyse commentée :** l'indice clé est l'**affirmation d'un fait précis et négatif** \
(« vole systématiquement ») **sans aucune preuve fournie**. Cela correspond à une accusation \
non étayée (calomnie), à distinguer d'une simple insulte (qui n'affirme pas de fait précis).

### Exemple 3 — Scénario 10 (critique du restaurant)

{FSE06_SCENARIOS_TEXT.splitlines()[20]}

**Analyse commentée :** ce scénario ne contient **aucun des indices** vus ci-dessus : pas de \
répétition ciblée, pas d'insulte, pas d'accusation non prouvée (l'avis porte sur une expérience \
vécue, pas sur un fait extérieur invérifiable), pas de menace. C'est une critique couverte par \
la liberté d'expression.

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse** (scénario 2, injure) : « Ce n'est rien, c'est juste une opinion sur la \
vidéo. » → confond une opinion sur un contenu et une insulte directement adressée à une \
personne.
- ✅ **Bonne réponse** : « Le message s'adresse directement à l'auteur avec des mots insultants \
(« idiot fini »), sans affirmer de fait précis à son sujet : c'est une injure. »

- ❌ **Mauvaise réponse** (scénario 10, critique du restaurant) : « Critiquer un restaurant en \
ligne est forcément un comportement illicite puisque ça peut lui faire perdre des clients. » → \
confond conséquence économique possible et comportement illicite ; aucune insulte ni accusation \
non prouvée n'est présente ici.
- ✅ **Bonne réponse** : « Ce commentaire critique un service vécu, sans insulte ni accusation \
non prouvée : il relève de la liberté d'expression, même s'il est sévère. »

## 7. Pièges et erreurs fréquentes

- **Confondre injure et accusation non étayée** : l'injure n'affirme aucun fait précis ; \
l'accusation non étayée affirme un fait précis, non prouvé.
- **Croire que toute critique négative est un comportement illicite** : seule la présence \
d'indices précis (répétition, absence de preuve, menace, etc.) permet de conclure.
- **Oublier qu'un comportement peut combiner plusieurs catégories** (ex. usurpation d'identité \
ET diffusion malveillante dans un même scénario).
- **Citer un article de loi ou une peine** : ce cours ne les enseigne jamais — seuls les \
indices comptent à l'examen.

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Identifier les indices (essaie avant de regarder la correction)</summary>

Reprends le scénario 6 (faux profil). Quels indices précis permettent de l'associer à \
l'usurpation d'identité ?

<details>
<summary>Voir la correction expliquée</summary>

Les indices sont : la création d'un profil **au nom** d'une autre personne, l'utilisation de \
**sa photo**, et le fait de **publier des messages en se faisant passer pour elle** auprès \
d'autres personnes — sans son accord. Ces trois éléments réunis (nom, photo, messages envoyés \
« en son nom ») caractérisent l'usurpation d'identité.

Ce corrigé fonctionne parce qu'il énumère les indices un par un, plutôt que de se contenter \
d'affirmer la catégorie sans preuve.
</details>
</details>

<details>
<summary>Exercice 2 — Distinguer un scénario illicite d'une critique légitime (essaie avant de \
regarder la correction)</summary>

Compare le scénario 3 (commerçant accusé) et le scénario 10 (critique du restaurant). Pourquoi \
l'un pose-t-il problème et pas l'autre, alors que les deux sont des avis négatifs publiés en \
ligne ?

<details>
<summary>Voir la correction expliquée</summary>

Le scénario 3 affirme un **fait précis et négatif** (« vole systématiquement ses clients ») \
**sans aucune preuve**, ce qui correspond à une accusation non étayée. Le scénario 10 critique \
une expérience **vécue par l'auteur lui-même** (la qualité du service), sans affirmer de fait \
extérieur invérifiable ni insulter personne : c'est une opinion couverte par la liberté \
d'expression. La différence ne tient donc pas à la sévérité du ton, mais à la présence ou non \
d'un fait précis affirmé sans preuve.

Ce corrigé fonctionne parce qu'il isole le critère pertinent (fait précis non prouvé) plutôt que \
de comparer seulement le ton des deux messages.
</details>
</details>

## 9. Corrigés très expliqués

**Question :** « Le scénario 9 (association qui revend des adresses e-mail) implique-t-il un \
comportement en ligne comme le cyberharcèlement ou la menace ? »

**Corrigé expliqué :** non. Ce scénario ne contient aucun indice de répétition hostile, \
d'insulte, de menace ou d'accusation non prouvée visant une personne précise. En revanche, il \
illustre un **traitement de données sans base valable** : les adresses e-mail (données \
personnelles) sont transmises à une entreprise de publicité **sans que les participants en aient \
été informés**, ce qui constitue l'indice central de cette catégorie, distincte des \
comportements qui visent directement à nuire à une personne identifiée.

Ce corrigé fonctionne parce qu'il élimine d'abord les catégories non pertinentes avant \
d'identifier la bonne, plutôt que de choisir une catégorie au hasard parmi celles déjà vues.

## 10. Fiche mémo

- Liberté d'expression : permet la critique, même sévère, tant qu'elle ne dépasse pas les \
limites ci-dessous.
- Cyberharcèlement = répétition hostile ciblée. Injure = insulte sans fait précis. Accusation \
non étayée = fait précis négatif sans preuve. Menace = annonce d'un mal futur.
- Racisme/discrimination = traitement défavorable fondé sur une caractéristique protégée.
- Usurpation d'identité = se faire passer pour autrui en ligne. Intrusion informatique = accès \
non autorisé à un compte/appareil/des données.
- Diffusion malveillante = partage dans le but explicite de nuire. Traitement de données sans \
base valable = collecte/usage de données personnelles sans justification ni information.
- Jamais de numéro d'article de loi ni de peine à citer : seuls les indices du scénario comptent.

## 11. Sources officielles vérifiées

Les catégories pédagogiques utilisées ci-dessus sont vérifiées auprès de sources belges \
officielles, à un niveau général (vocabulaire de sensibilisation, sans qualification pénale \
précise ni peine, conformément au périmètre de ce cours) :

- Centre for Cybersecurity Belgium (Safeonweb, service public fédéral), « I am a victim of \
cyberbullying », https://safeonweb.be/en/i-am-victim-cyberbullying — consulté le 2026-10-01.
- Police fédérale belge, « Usurpation d'identité », \
https://www.police.be/5344/fr/questions/cybercriminalite/usurpation-didentite — consulté le \
2026-10-01.

En cas de situation réelle, consulte ces organismes officiels plutôt que ce cours, qui reste un \
support pédagogique simplifié et ne fige aucune qualification pénale.
"""
