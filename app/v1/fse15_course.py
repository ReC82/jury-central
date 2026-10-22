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

from app.v1.fse_course_sections import build_course_sections

FSE15_CIRCUIT_DIAGRAM_SVG = """<div class="jc-diagram" role="img" aria-label="Schéma du circuit économique à quatre agents : ménages et entreprises échangent travail (flux réel) contre salaire (flux monétaire) ; chacun verse des impôts et cotisations à l'État (flux monétaire) et reçoit en retour des prestations sociales et des services publics (flux réel et monétaire) ; les entreprises échangent des biens et services (flux réel) contre paiement (flux monétaire) avec le reste du monde.">
<svg viewBox="0 0 900 460" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="fse15-arrow-blue" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 Z" fill="#1565c0" />
    </marker>
    <marker id="fse15-arrow-green" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 Z" fill="#1e7e45" />
    </marker>
  </defs>

  <rect x="30" y="30" width="230" height="80" rx="10" fill="#e8f1fc" stroke="#1565c0" stroke-width="2" />
  <text x="145" y="64" text-anchor="middle" font-size="16" font-weight="600" fill="#0d3b66">Ménages</text>
  <text x="145" y="84" text-anchor="middle" font-size="11.5" fill="#55606b">personnes et familles</text>

  <rect x="640" y="30" width="230" height="80" rx="10" fill="#e8f1fc" stroke="#1565c0" stroke-width="2" />
  <text x="755" y="64" text-anchor="middle" font-size="16" font-weight="600" fill="#0d3b66">Entreprises</text>
  <text x="755" y="84" text-anchor="middle" font-size="11.5" fill="#55606b">produisent biens et services</text>

  <line x1="260" y1="55" x2="640" y2="55" stroke="#1e7e45" stroke-width="2" marker-end="url(#fse15-arrow-green)" />
  <text x="450" y="45" text-anchor="middle" font-size="11.5" fill="#15532d">travail (flux réel)</text>
  <line x1="640" y1="85" x2="260" y2="85" stroke="#1565c0" stroke-width="2" marker-end="url(#fse15-arrow-blue)" />
  <text x="450" y="104" text-anchor="middle" font-size="11.5" fill="#0d3b66">salaire (flux monétaire)</text>

  <rect x="335" y="195" width="230" height="80" rx="10" fill="#fdf2e3" stroke="#b5600a" stroke-width="2" />
  <text x="450" y="229" text-anchor="middle" font-size="16" font-weight="600" fill="#7a4306">État</text>
  <text x="450" y="249" text-anchor="middle" font-size="11.5" fill="#55606b">impôts, cotisations, dépenses publiques</text>

  <line x1="180" y1="112" x2="368" y2="193" stroke="#1565c0" stroke-width="2" marker-end="url(#fse15-arrow-blue)" />
  <text x="215" y="148" text-anchor="middle" font-size="11" fill="#0d3b66">impôts /</text>
  <text x="215" y="161" text-anchor="middle" font-size="11" fill="#0d3b66">cotisations</text>
  <line x1="400" y1="197" x2="212" y2="116" stroke="#1e7e45" stroke-width="2" marker-end="url(#fse15-arrow-green)" />
  <text x="150" y="150" text-anchor="middle" font-size="11" fill="#15532d">prestations</text>
  <text x="150" y="163" text-anchor="middle" font-size="11" fill="#15532d">sociales</text>

  <line x1="720" y1="112" x2="532" y2="193" stroke="#1565c0" stroke-width="2" marker-end="url(#fse15-arrow-blue)" />
  <text x="685" y="148" text-anchor="middle" font-size="11" fill="#0d3b66">impôts /</text>
  <text x="685" y="161" text-anchor="middle" font-size="11" fill="#0d3b66">cotisations</text>
  <line x1="500" y1="197" x2="688" y2="116" stroke="#1e7e45" stroke-width="2" marker-end="url(#fse15-arrow-green)" />
  <text x="760" y="150" text-anchor="middle" font-size="11" fill="#15532d">services</text>
  <text x="760" y="163" text-anchor="middle" font-size="11" fill="#15532d">publics</text>

  <rect x="640" y="350" width="230" height="80" rx="10" fill="#f1f3f5" stroke="#55606b" stroke-width="2" />
  <text x="755" y="384" text-anchor="middle" font-size="16" font-weight="600" fill="#2b3440">Reste du monde</text>
  <text x="755" y="404" text-anchor="middle" font-size="11.5" fill="#55606b">échanges avec l'étranger</text>

  <line x1="735" y1="110" x2="735" y2="350" stroke="#1e7e45" stroke-width="2" marker-end="url(#fse15-arrow-green)" />
  <text x="695" y="230" text-anchor="middle" font-size="11" fill="#15532d">exportations</text>
  <line x1="775" y1="350" x2="775" y2="110" stroke="#1565c0" stroke-width="2" marker-end="url(#fse15-arrow-blue)" />
  <text x="815" y="230" text-anchor="middle" font-size="11" fill="#0d3b66">paiement</text>
</svg>
</div>"""


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

{FSE15_CIRCUIT_DIAGRAM_SVG}

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


def fse15_course_sections() -> list[tuple[str, str]]:
    """Sections (titre, Markdown) du cours FSE15 — refonte pédagogique et visuelle
    (ticket #105), voir `app.v1.fse_course_sections.build_course_sections`."""
    return build_course_sections("FSE15", fse15_course_markdown())
