"""Contenu de cours — FSE11 « Partis politiques et choix argumenté » (ticket #99, cahier
des charges détaillé).

Même structure que FSE01-FSE10 : 1. Ce que tu dois savoir faire à l'examen —
2. Théorie progressive — 3. Définitions importantes — 4. Méthode étape par étape —
5. Exemples commentés — 6. Mauvaises réponses comparées aux bonnes — 7. Pièges et erreurs
fréquentes — 8. Exercices guidés (corrigés masqués par défaut) — 9. Corrigés très
expliqués — 10. Fiche mémo — 11. Sources officielles vérifiées.

Traitement volontairement neutre (ticket #99 : « comparer... de manière neutre » et
« sans noter l'opinion personnelle de l'élève ») : ce cours enseigne à IDENTIFIER une
famille politique et à COMPARER des propositions par valeurs/priorités/effets, jamais à
recommander un vote ni à évaluer la qualité d'un parti. Les six partis cités (programme
p. 61-62, exemple 2024) sont identifiés par leur famille à partir d'une source de presse
neutre et datée (§ 11) ; les propositions comparées dans les exercices sont fictives,
jamais attribuées à un parti réel, pour ne jamais figer une position actuelle comme une
vérité intemporelle."""

from app.v1.fse11_content import (
    FSE11_PARTIES_TEXT,
    FSE11_PROPOSALS_TEXT,
)


def fse11_course_markdown() -> str:
    return f"""# FSE11 — Partis politiques et choix argumenté

## 1. Ce que tu dois savoir faire à l'examen

Tu dois être capable d'associer un extrait sourcé à une famille politique (socialiste, \
libérale, écologiste, centriste/humaniste, ou position radicale), d'utiliser l'axe \
gauche-centre-droite comme repère simplifié sans le traiter comme une vérité absolue, et de \
comparer deux propositions à partir de leurs valeurs, priorités et effets, **sans jamais \
exprimer ton opinion personnelle**.

**Prérequis** : aucun prérequis spécifique des cours précédents n'est nécessaire ici.

## 2. Théorie progressive

Une **famille politique** regroupe des partis qui partagent des valeurs et priorités \
générales proches, au-delà de leurs différences nationales. La famille **socialiste** met \
en avant la justice sociale et le rôle de la solidarité collective. La famille **libérale** \
met en avant l'initiative individuelle et une intervention publique plus limitée. La \
famille **écologiste** met en avant la transition environnementale. La famille \
**centriste/humaniste** se situe entre ces tendances, souvent issue d'une tradition \
démocrate-chrétienne. Des **positions radicales** existent aussi aux extrêmes de \
l'échiquier politique, à gauche comme à droite.

Six partis belges, cités en exemple à partir du programme (p. 61-62, référence 2024, \
noms vérifiés et sourcés § 11), illustrent ces familles : **PS** (socialiste), **MR** \
(libérale), **Ecolo** (écologiste), **Les Engagés** (centriste/humaniste), **PTB** \
(position radicale, extrême gauche) et **Vlaams Belang** (position radicale, extrême \
droite).

L'**axe gauche-centre-droite** est un repère simplifié qui situe approximativement les \
familles politiques les unes par rapport aux autres (la gauche insistant davantage sur \
l'égalité et l'intervention collective, la droite davantage sur la liberté individuelle et \
l'initiative privée). **Ce repère reste une simplification pédagogique, pas une vérité \
absolue** : un même parti peut combiner des positions qui ne se laissent pas toutes ranger \
clairement sur un seul axe, et deux partis de la même famille peuvent avoir des priorités \
différentes selon le pays ou la période.

Pour **comparer deux propositions** de façon argumentée, il faut identifier, pour chacune, \
la **valeur** mise en avant (égalité, liberté, durabilité...), la **priorité** affichée \
(ex. réduire les inégalités, développer l'emploi) et les **effets attendus** (qui en \
bénéficie, qui contribue). Cette comparaison reste **neutre** : elle décrit les choix faits \
par chaque proposition, sans jamais conclure laquelle serait « la meilleure » — ce jugement \
reste personnel et n'a pas sa place dans une réponse d'examen.

## 3. Définitions importantes

- **Famille politique** : ensemble de partis partageant des valeurs et priorités générales \
proches.
- **Axe gauche-centre-droite** : repère simplifié situant les familles politiques les unes \
par rapport aux autres — jamais une vérité absolue.
- **Valeur** (en politique) : ce qu'une proposition considère comme important (égalité, \
liberté, durabilité...).
- **Priorité** : objectif mis en avant par une proposition.
- **Effet attendu** : conséquence concrète annoncée d'une proposition, pour qui elle \
bénéficie ou contribue.

## 4. Méthode étape par étape

Face à un extrait ou une proposition, procède dans cet ordre :

1. Identifie la **valeur** mise en avant dans le texte.
2. Identifie la **priorité** affichée (quel objectif concret est visé).
3. Si plusieurs propositions sont comparées, identifie les **effets attendus** de chacune \
(qui bénéficie, qui contribue).
4. Associe, si demandé, ces éléments à une **famille politique**, en te limitant au repère \
gauche-centre-droite comme simplification, jamais comme vérité absolue.
5. Ne formule jamais de jugement personnel sur la proposition la plus souhaitable.

## 5. Exemples commentés

### Exemple 1 — Extrait 1 (PS)

{FSE11_PARTIES_TEXT.splitlines()[2]}

**Analyse commentée :** la justice sociale et la santé/éducation publiques sont des valeurs \
typiques de la famille **socialiste**.

### Exemple 2 — Extrait 2 (MR)

{FSE11_PARTIES_TEXT.splitlines()[4]}

**Analyse commentée :** l'initiative privée et une intervention publique plus limitée sont \
des valeurs typiques de la famille **libérale**.

### Exemple 3 — Comparaison des deux propositions fictives

{FSE11_PROPOSALS_TEXT}

**Analyse commentée :** la proposition A met en avant la valeur d'**égalité** (réduction des \
inégalités), avec pour effet attendu que les plus hauts revenus contribuent davantage au \
financement de services collectifs. La proposition B met en avant la valeur de **liberté \
économique**, avec pour effet attendu une activité privée facilitée et potentiellement plus \
d'emplois. Cette comparaison décrit les choix de chaque proposition sans indiquer laquelle \
serait préférable : ce choix reste personnel.

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse** : « La proposition A est la meilleure parce qu'elle aide les plus \
pauvres. » → exprime une opinion personnelle, non demandée dans ce cours.
- ✅ **Bonne réponse** : « La proposition A met en avant l'égalité, avec une contribution \
accrue des plus hauts revenus ; la proposition B met en avant la liberté économique, avec \
une contribution réduite des entreprises. »

- ❌ **Mauvaise réponse** : « L'axe gauche-droite permet de classer n'importe quel parti \
avec certitude. » → traite une simplification pédagogique comme une vérité absolue.
- ✅ **Bonne réponse** : « L'axe gauche-centre-droite est un repère simplifié ; un parti \
peut combiner des positions qui ne s'y laissent pas toutes ranger clairement. »

## 7. Pièges et erreurs fréquentes

- **Exprimer une préférence personnelle** : ce cours demande de décrire et comparer, jamais \
de juger ou de recommander.
- **Traiter l'axe gauche-droite comme une classification exacte et universelle.**
- **Confondre famille politique et parti précis** : plusieurs partis peuvent appartenir à la \
même famille tout en ayant des priorités différentes.
- **Présenter une position actuelle comme immuable** : les positions des partis évoluent ; \
seule la famille politique générale, sourcée et datée, est enseignée ici.

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Associer un extrait à une famille (essaie avant de regarder la \
correction)</summary>

Reprends l'extrait 5 (PTB). À quelle famille politique appartient ce parti, et sur quel \
élément du texte t'appuies-tu ?

<details>
<summary>Voir la correction expliquée</summary>

Le PTB appartient à l'extrême gauche de l'échiquier politique belge : l'extrait précise \
explicitement qu'il se revendique d'une tradition marxiste et se situe à l'extrême gauche.

Ce corrigé fonctionne parce qu'il s'appuie sur une information explicitement donnée dans \
l'extrait, plutôt que sur une supposition.
</details>
</details>

<details>
<summary>Exercice 2 — Comparer sans juger (essaie avant de regarder la correction)</summary>

Compare les propositions fictives A et B à partir de leur valeur et de leur priorité, sans \
indiquer laquelle te semble préférable.

<details>
<summary>Voir la correction expliquée</summary>

Proposition A : valeur = égalité ; priorité = réduire les inégalités, via une contribution \
accrue des plus hauts revenus. Proposition B : valeur = liberté économique ; priorité = \
développer l'activité économique et l'emploi privé, via une réduction des contraintes et de \
certaines contributions. Aucune des deux n'est présentée ici comme supérieure à l'autre.

Ce corrigé fonctionne parce qu'il décrit chaque proposition selon les mêmes critères \
(valeur, priorité) sans ajouter de jugement personnel.
</details>
</details>

## 9. Corrigés très expliqués

**Question :** « Pourquoi ce cours insiste-t-il sur le fait que l'axe gauche-centre-droite \
n'est pas une vérité absolue ? »

**Corrigé expliqué :** parce qu'un parti réel combine souvent plusieurs positions qui ne se \
laissent pas toutes ranger clairement sur un seul axe (par exemple, une position peut \
sembler plutôt de gauche sur un sujet et plutôt de droite sur un autre), et parce que la \
même famille politique peut avoir des priorités différentes selon le pays ou la période. \
Présenter cet axe comme une vérité absolue risquerait de réduire une réalité politique \
complexe à une seule ligne, ce que ce cours évite explicitement.

Ce corrigé fonctionne parce qu'il justifie la limite par un raisonnement (complexité réelle \
des positions), pas seulement en répétant l'affirmation du cours.

## 10. Fiche mémo

- Famille politique = ensemble de partis aux valeurs et priorités générales proches \
(socialiste, libérale, écologiste, centriste/humaniste, positions radicales).
- Axe gauche-centre-droite = repère simplifié, jamais une vérité absolue.
- Comparer une proposition : identifier sa valeur, sa priorité et ses effets attendus.
- Ne jamais exprimer d'opinion personnelle ni recommander un choix dans une réponse \
d'examen sur ce sujet.
- Les positions réelles des partis évoluent : seule la famille politique générale, sourcée \
et datée, est enseignée ici.

## 11. Sources officielles vérifiées

Les familles politiques des six partis cités sont identifiées à partir d'une source de \
presse neutre et datée :

- The Brussels Times, « A beginner's guide to Belgium's political parties », \
https://www.brusselstimes.com/312358/a-beginners-guide-to-belgiums-political-parties — \
consulté le 2026-10-01. Cette source décrit chaque parti par sa famille politique générale \
(socialiste, libéral, écologiste, centriste/humaniste, extrême gauche, extrême droite), sans \
détailler un programme actuel précis — exactement le niveau d'information utilisé dans ce \
cours.

En cas de doute sur une position actuelle précise d'un parti, consulte son site officiel ou \
une source de presse datée plutôt que ce cours, qui ne vise que l'identification de la \
famille politique générale.
"""
