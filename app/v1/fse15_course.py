"""Contenu de cours — FSE15 « Le circuit économique et les interventions de l'État »
(ticket #100, cahier des charges détaillé).

Même structure que FSE01-FSE14 : 1. Ce que tu dois savoir faire à l'examen —
2. Théorie progressive — 3. Définitions importantes — 4. Méthode étape par étape —
5. Exemples commentés — 6. Mauvaises réponses comparées aux bonnes — 7. Pièges et erreurs
fréquentes — 8. Exercices guidés (corrigés masqués par défaut) — 9. Corrigés très
expliqués — 10. Fiche mémo.

Périmètre strict (ticket #100, programme p. 43, 61-63) : agents, flux réels/monétaires,
politiques de redistribution/régulation/production de biens collectifs — purement
conceptuel. Le volet législation reste hors évaluation sommative (note 90 du programme) :
aucune question de ce cours ne porte sur un texte de loi précis."""

from app.v1.fse15_content import FSE15_AID_TEXT


def fse15_course_markdown() -> str:
    return f"""# FSE15 — Le circuit économique et les interventions de l'État

## 1. Ce que tu dois savoir faire à l'examen

Tu dois être capable de compléter un circuit économique à quatre agents (ménages, \
entreprises, État, reste du monde), de distinguer flux réels et flux monétaires, et \
d'expliquer l'effet d'une intervention publique (aide, service public) sur ce circuit.

**Prérequis** : ce cours réutilise la notion de financement d'un média (FSE02) comme \
exemple d'aide publique, et les notions de recettes/dépenses de l'État (FSE12).

## 2. Théorie progressive

Le **circuit économique** représente les échanges entre quatre types d'**agents** : les \
**ménages** (les personnes et familles), les **entreprises** (qui produisent des biens et \
services), l'**État** (qui prélève des impôts/cotisations et effectue des dépenses), et le \
**reste du monde** (les échanges avec l'étranger).

On distingue deux types de **flux** entre ces agents. Un **flux réel** correspond à un \
échange de biens, de services ou de travail (ex. un ménage fournit son travail à une \
entreprise ; une entreprise livre un bien à un ménage). Un **flux monétaire** correspond à \
un paiement en argent, généralement en contrepartie d'un flux réel (ex. une entreprise verse \
un salaire en échange du travail reçu).

Les ménages fournissent leur **travail** aux entreprises et reçoivent un **salaire** en \
échange ; ils utilisent ce revenu pour **consommer** des biens/services et payer des \
**impôts/cotisations**. Les entreprises **produisent** des biens/services, qu'elles vendent \
aux ménages, à l'État, ou exportent vers le reste du monde. L'État perçoit des **impôts et \
cotisations** (vu en FSE12-13) et les utilise pour financer des **services publics** \
(utilisés par les ménages et les entreprises) et des **prestations sociales** (versées aux \
ménages). Le reste du monde achète des biens/services du pays (**exportations**) et lui en \
vend (**importations**).

L'État intervient dans ce circuit par plusieurs types de politiques : la \
**redistribution** (déjà vue en FSE13, les cotisations/impôts des uns financent des \
prestations pour d'autres), la **régulation** (fixer des règles pour encadrer les échanges \
économiques) et la **production de biens et services collectifs** (ex. infrastructures, \
enseignement public) que le marché privé ne produirait pas nécessairement seul, ou pas pour \
tous.

## 3. Définitions importantes

- **Agent économique** : acteur qui participe aux échanges du circuit (ménage, entreprise, \
État, reste du monde).
- **Flux réel** : échange de biens, de services ou de travail entre agents.
- **Flux monétaire** : paiement en argent, généralement en contrepartie d'un flux réel.
- **Redistribution** : effet par lequel les contributions des uns financent des prestations \
pour d'autres (déjà vu en FSE13).
- **Régulation** : fixation de règles par l'État pour encadrer les échanges économiques.
- **Bien/service collectif** : bien ou service que l'État produit ou finance pour \
l'ensemble de la population.

## 4. Méthode étape par étape

Face à un circuit à compléter ou à analyser, procède dans cet ordre :

1. Identifie les **agents** concernés par la situation (ménages ? entreprises ? État ? \
reste du monde ?).
2. Pour chaque échange, identifie s'il s'agit d'un **flux réel** (bien, service, travail) \
ou d'un **flux monétaire** (paiement).
3. Si une intervention de l'État est décrite, identifie s'il s'agit de \
**redistribution**, de **régulation** ou de **production de biens collectifs**.
4. Trace, si demandé, l'effet d'une intervention sur plusieurs agents successifs (ex. une \
aide à une entreprise peut ensuite se traduire en salaires versés à des ménages).

## 5. Exemples commentés

### Exemple 1 — Travail et salaire

Un ménage fournit son travail à une entreprise, qui lui verse un salaire en échange.

**Analyse commentée :** le travail fourni par le ménage est un **flux réel** ; le salaire \
versé par l'entreprise est le **flux monétaire** correspondant.

### Exemple 2 — Exportations

Une entreprise du pays vend des biens à des clients situés à l'étranger.

**Analyse commentée :** la livraison des biens est un **flux réel** allant de l'entreprise \
vers le reste du monde ; le paiement reçu en retour est le **flux monétaire** correspondant.

### Exemple 3 — Effet d'une aide publique sur le circuit

{FSE15_AID_TEXT}

**Analyse commentée :** cet exemple montre comment un flux unique (l'aide de l'État) se \
propage à travers plusieurs agents successifs : État → entreprise (média) → ménages \
(salaires) → entreprises (consommation) → État (impôts/cotisations). C'est une illustration \
concrète de la circulation de l'argent dans le circuit économique.

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse** : « Le salaire est un flux réel, puisqu'il permet d'acheter des \
biens réels. » → confond la nature du flux (de l'argent = monétaire) avec son usage \
ultérieur.
- ✅ **Bonne réponse** : « Le salaire est un flux monétaire : c'est un paiement en argent, \
en contrepartie du travail (flux réel) fourni par le ménage. »

- ❌ **Mauvaise réponse** : « L'aide publique à un média n'a d'effet que sur ce média. » → \
ignore la propagation de l'argent à travers plusieurs agents successifs (salaires, \
consommation, impôts).
- ✅ **Bonne réponse** : « L'aide publique se propage : le média l'utilise pour verser des \
salaires, que les ménages utilisent ensuite pour consommer et payer des impôts, qui \
reviennent en partie à l'État. »

## 7. Pièges et erreurs fréquentes

- **Confondre flux réel et flux monétaire** : un flux réel porte sur un bien/service/travail \
; un flux monétaire porte sur de l'argent.
- **Oublier le reste du monde** comme quatrième agent, en se limitant à ménages/entreprises/ \
État.
- **Limiter l'effet d'une intervention publique au premier agent concerné**, sans tracer sa \
propagation ultérieure.
- **Mémoriser un texte de loi précis sur les interventions de l'État** : ce cours reste au \
niveau du mécanisme économique, jamais de la législation détaillée.

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Identifier flux réel et flux monétaire (essaie avant de regarder la \
correction)</summary>

Un ménage achète un bien produit par une entreprise. Identifie le flux réel et le flux \
monétaire de cet échange.

<details>
<summary>Voir la correction expliquée</summary>

Flux réel : le bien livré par l'entreprise au ménage. Flux monétaire : le paiement effectué \
par le ménage à l'entreprise en contrepartie de ce bien.

Ce corrigé fonctionne parce qu'il identifie séparément les deux sens de l'échange (bien vs \
paiement), plutôt que de les confondre en un seul flux.
</details>
</details>

<details>
<summary>Exercice 2 — Tracer la propagation d'une aide (essaie avant de regarder la \
correction)</summary>

Reprends l'exemple de l'aide publique au média (exemple 3). Trace, étape par étape, les \
agents successifs touchés par cet argent, du versement initial jusqu'au retour partiel vers \
l'État.

<details>
<summary>Voir la correction expliquée</summary>

1. L'État verse l'aide au média (une entreprise). 2. Le média verse une partie de cette aide \
en salaires à ses employés (des ménages). 3. Ces ménages utilisent leur revenu pour consommer \
auprès d'autres entreprises. 4. Ces mêmes ménages et entreprises paient des impôts/ \
cotisations, qui retournent en partie vers l'État.

Ce corrigé fonctionne parce qu'il trace la circulation complète de l'argent à travers quatre \
étapes successives, plutôt que de s'arrêter au premier agent touché.
</details>
</details>

## 9. Corrigés très expliqués

**Question :** « En quoi la production de biens collectifs par l'État est-elle différente \
d'un bien produit par une entreprise privée ? »

**Corrigé expliqué :** un bien collectif (ex. une infrastructure publique, l'enseignement \
public) est produit ou financé par l'État pour l'ensemble de la population, souvent sans \
paiement direct proportionnel à l'usage individuel qu'en fait chaque personne — il est \
financé collectivement via les impôts et cotisations (circuit vu en FSE12-13), puis mis à \
disposition de tous. Un bien produit par une entreprise privée, au contraire, est en général \
vendu directement à celui qui l'achète, au prix fixé par l'entreprise.

Ce corrigé fonctionne parce qu'il compare explicitement le mode de financement (collectif vs \
individuel) et d'accès (pour tous vs pour l'acheteur), plutôt que de se limiter à répéter la \
définition.

## 10. Fiche mémo

- Quatre agents : ménages, entreprises, État, reste du monde.
- Flux réel = bien/service/travail ; flux monétaire = paiement en argent, généralement en \
contrepartie d'un flux réel.
- L'État intervient par redistribution, régulation, ou production de biens/services \
collectifs.
- Une intervention publique peut se propager à travers plusieurs agents successifs : ne \
jamais s'arrêter au premier agent concerné.
- Le volet législation reste hors évaluation : seul le mécanisme économique compte ici.
"""
