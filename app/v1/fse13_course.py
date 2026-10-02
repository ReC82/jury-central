"""Contenu de cours — FSE13 « La sécurité sociale : rôle et financement » (ticket #100,
cahier des charges détaillé).

Même structure que FSE01-FSE12 : 1. Ce que tu dois savoir faire à l'examen —
2. Théorie progressive — 3. Définitions importantes — 4. Méthode étape par étape —
5. Exemples commentés — 6. Mauvaises réponses comparées aux bonnes — 7. Pièges et erreurs
fréquentes — 8. Exercices guidés (corrigés masqués par défaut) — 9. Corrigés très
expliqués — 10. Fiche mémo — 11. Sources officielles vérifiées.

Périmètre strict (ticket #100, programme p. 61) : solidarité, mutualisation des risques,
assurance sociale, redistribution, financement, risques couverts — sans aucun calcul de
droits (montants, conditions d'accès précises), conformément au ticket."""



def fse13_course_markdown() -> str:
    return """# FSE13 — La sécurité sociale : rôle et financement

## 1. Ce que tu dois savoir faire à l'examen

Tu dois être capable d'expliquer le trajet d'une cotisation à une prestation, d'identifier \
le risque couvert dans une situation donnée, et de distinguer financement, gestion et \
versement. **Tu n'as jamais besoin de calculer un montant de prestation ni une condition \
d'accès précise.**

**Prérequis** : ce cours réutilise la notion de cotisations sociales vue en FSE12 (une \
recette parafiscale de l'État).

## 2. Théorie progressive

La sécurité sociale repose sur le principe de **solidarité** : chacun contribue selon ses \
moyens, et chacun peut bénéficier d'une protection en cas de besoin, indépendamment de ce \
qu'il a personnellement versé. Ce principe s'appuie sur la **mutualisation des risques** : \
plutôt que chaque personne épargne seule pour faire face à un risque (maladie, chômage, \
vieillesse...), l'ensemble des cotisations versées par tous sert à couvrir ceux qui en ont \
besoin au moment où ils en ont besoin. On parle d'**assurance sociale** parce que ce \
système fonctionne un peu comme une assurance collective obligatoire, organisée par \
l'État plutôt que par un assureur privé.

La sécurité sociale a aussi un effet de **redistribution** : les cotisations des personnes \
en activité financent, en partie, les prestations versées à d'autres (malades, chômeurs, \
retraités, familles), ce qui réduit certaines inégalités face aux risques de la vie.

Le financement de la sécurité sociale provient principalement des **cotisations des \
travailleurs et des employeurs**, mais aussi d'un **financement public** (une partie du \
budget de l'État, vu en FSE12) et de **financements alternatifs** complémentaires. Il faut \
distinguer trois rôles différents : le **financement** (qui apporte l'argent : cotisations, \
État), la **gestion** (qui organise et contrôle le système, voir FSE14) et le **versement** \
(qui paie concrètement la prestation à la personne concernée, parfois via un intermédiaire \
comme une mutualité).

Les **risques couverts** par la sécurité sociale incluent la maladie et l'invalidité, le \
chômage, la vieillesse (pension), les accidents du travail et les maladies \
professionnelles, et les charges familiales. Le statut de **salarié** et celui \
d'**indépendant** donnent accès à des systèmes de cotisation différents, sans qu'il soit \
nécessaire ici de calculer les droits précis qui en découlent.

## 3. Définitions importantes

- **Solidarité** : principe selon lequel chacun contribue selon ses moyens et peut \
bénéficier d'une protection selon ses besoins.
- **Mutualisation des risques** : mise en commun des cotisations pour couvrir ceux qui en \
ont besoin.
- **Assurance sociale** : système de protection collective et obligatoire organisé par \
l'État.
- **Redistribution** : effet par lequel les cotisations des uns contribuent aux prestations \
des autres.
- **Financement** : origine de l'argent qui alimente la sécurité sociale (cotisations, \
État).
- **Gestion** : organisation et contrôle du système de sécurité sociale.
- **Versement** : paiement concret de la prestation à la personne concernée.

## 4. Méthode étape par étape

Face à une situation, procède dans cet ordre :

1. Identifie le **risque couvert** (maladie/invalidité, chômage, vieillesse, accident du \
travail/maladie professionnelle, charges familiales).
2. Distingue, si la question le demande, **financement**, **gestion** et **versement**.
3. Relie la situation au principe de **solidarité**/**mutualisation** si on te demande \
d'expliquer le trajet cotisation→prestation.
4. Ne calcule jamais un montant ni une condition d'accès précise : ce cours reste au niveau \
des principes.

## 5. Exemples commentés

### Exemple 1 — Situation 1 (Yasmine, incapacité de travail)

Yasmine est en incapacité de travail pendant plusieurs semaines après une opération \
chirurgicale.

**Analyse commentée :** le risque couvert est la **maladie/invalidité** : l'assurance \
maladie-invalidité verse une prestation de remplacement de revenu pendant l'incapacité.

### Exemple 2 — Situation 5 (Thomas, accident au travail)

Thomas se blesse sur son lieu de travail en manipulant une machine.

**Analyse commentée :** le risque couvert est l'**accident du travail**, une branche \
distincte de l'assurance maladie-invalidité ordinaire.

### Exemple 3 — Situation 6 (indépendant)

Un indépendant, propriétaire de son petit commerce, cotise lui-même pour sa propre \
protection sociale future.

**Analyse commentée :** contrairement à un salarié (dont l'employeur verse une partie des \
cotisations), un indépendant cotise lui-même pour l'ensemble de sa protection sociale — un \
repère utile, sans qu'il soit nécessaire de calculer le montant exact de ses droits.

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse** (situation 2, Marc) : « Marc reçoit de l'argent parce qu'il a \
cotisé exactement ce montant auparavant. » → traite la sécurité sociale comme une épargne \
individuelle, ce qui contredit le principe de mutualisation.
- ✅ **Bonne réponse** : « Marc bénéficie d'une prestation chômage financée par l'ensemble \
des cotisations versées par tous les travailleurs et employeurs, pas seulement les siennes \
: c'est le principe de mutualisation des risques. »

- ❌ **Mauvaise réponse** : « Financement, gestion et versement, c'est la même chose. » → \
confond trois rôles distincts.
- ✅ **Bonne réponse** : « Le financement est l'origine de l'argent (cotisations, État), la \
gestion organise le système, et le versement paie concrètement la personne — ce sont trois \
rôles différents, parfois assurés par des organismes différents. »

## 7. Pièges et erreurs fréquentes

- **Confondre sécurité sociale et épargne personnelle** : la sécurité sociale repose sur la \
mutualisation, pas sur un compte individuel.
- **Confondre financement, gestion et versement.**
- **Chercher à calculer un montant de prestation ou une condition d'accès précise** : hors \
périmètre de ce cours.
- **Oublier la différence de statut salarié/indépendant** comme repère, sans vouloir en \
calculer les conséquences précises.

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Identifier le risque couvert (essaie avant de regarder la \
correction)</summary>

Reprends la situation 4 (Fatima, fin de carrière). Quel risque est couvert ?

<details>
<summary>Voir la correction expliquée</summary>

Le risque couvert est la **vieillesse** : Fatima cesse son activité après une longue \
carrière, ce qui correspond à la branche pension de la sécurité sociale.

Ce corrigé fonctionne parce qu'il associe directement l'élément de la situation (fin de \
carrière après de nombreuses années) au risque correspondant.
</details>
</details>

<details>
<summary>Exercice 2 — Expliquer le trajet cotisation→prestation (essaie avant de regarder \
la correction)</summary>

Explique, à partir de la situation 3 (famille avec deux enfants), comment les cotisations \
versées par l'ensemble des travailleurs et employeurs permettent à cette famille de \
recevoir un soutien financier.

<details>
<summary>Voir la correction expliquée</summary>

Les cotisations versées par l'ensemble des travailleurs et des employeurs sont mutualisées \
: elles ne restent pas propres à chaque cotisant, mais financent collectivement les \
prestations versées à ceux qui en ont besoin, y compris les prestations familiales pour les \
familles avec enfants. C'est le principe de solidarité et de mutualisation des risques, et \
non un remboursement individuel de ce que cette famille aurait elle-même versé.

Ce corrigé fonctionne parce qu'il relie explicitement cotisation, mutualisation et \
prestation, plutôt que de décrire chaque élément séparément.
</details>
</details>

## 9. Corrigés très expliqués

**Question :** « En quoi la sécurité sociale a-t-elle un effet de redistribution ? »

**Corrigé expliqué :** parce que les cotisations versées par les personnes en activité ne \
leur reviennent pas nécessairement à elles-mêmes : elles financent, au même moment, des \
prestations versées à d'autres personnes (malades, chômeurs, retraités, familles). Cet \
effet réduit certaines inégalités face aux risques de la vie : une personne qui traverse \
une période de maladie ou de chômage reçoit une protection financée collectivement, même \
si elle n'a cotisé que peu de temps avant.

Ce corrigé fonctionne parce qu'il explique le mécanisme concret de la redistribution (qui \
finance, qui reçoit, à quel moment), plutôt que de se contenter de répéter le mot.

## 10. Fiche mémo

- Solidarité + mutualisation des risques = principes de base de la sécurité sociale.
- Assurance sociale = protection collective obligatoire organisée par l'État.
- Redistribution = les cotisations des uns financent les prestations des autres.
- Financement (cotisations + État) ≠ gestion (organisation) ≠ versement (paiement concret).
- Risques couverts : maladie/invalidité, chômage, vieillesse, accident du travail/maladie \
professionnelle, charges familiales.
- Jamais de calcul de montant ni de condition d'accès précise dans ce cours.

## 11. Sources officielles vérifiées

Les principes généraux décrits ci-dessus sont vérifiés auprès du portail officiel belge de \
la sécurité sociale :

- Service public fédéral Sécurité sociale, « Structure et organisation », \
https://socialsecurity.belgium.be/fr/propos-de-la-securite-sociale/structure-et-organisation \
— consulté le 2026-10-01.

En cas de doute sur un droit réel, consulte cet organisme officiel plutôt que ce cours, qui \
reste un support pédagogique simplifié et n'enseigne aucun calcul de droit précis.
"""
