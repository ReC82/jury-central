"""Contenu de cours — FSE16 « Analyser une décision publique » (ticket #100, cahier des
charges détaillé).

Même structure que FSE01-FSE15 : 1. Ce que tu dois savoir faire à l'examen —
2. Théorie progressive — 3. Définitions importantes — 4. Méthode étape par étape —
5. Exemples commentés — 6. Mauvaises réponses comparées aux bonnes — 7. Pièges et erreurs
fréquentes — 8. Exercices guidés (corrigés masqués par défaut) — 9. Corrigés très
expliqués — 10. Fiche mémo.

Dernier cours avant la synthèse FSE17 : réutilise explicitement budget (FSE12), sécurité
sociale (FSE13-14), circuit économique (FSE15) et niveaux de pouvoir (FSE08-09) comme
outils d'analyse d'une décision publique complète, sans les ré-enseigner."""

from app.v1.fse16_content import (
    FSE16_BUDGET_NOTE_TEXT,
    FSE16_BUDGET_NOTE_TITLE,
    FSE16_PROPOSAL_TEXT,
    FSE16_PROPOSAL_TITLE,
)

from app.v1.fse_course_sections import build_course_sections


def fse16_course_markdown() -> str:
    return f"""# FSE16 — Analyser une décision publique

## 1. Ce que tu dois savoir faire à l'examen

Tu dois être capable d'analyser une décision publique en identifiant la décision elle-même, \
le niveau de pouvoir compétent, ses objectifs, les agents concernés, les flux qu'elle \
engendre, ses effets attendus, ses limites et ses conséquences indirectes, en distinguant \
court et long terme — puis de rédiger une conclusion fondée sur les documents fournis.

**Prérequis** : ce cours réutilise les niveaux de pouvoir (FSE08-09), le budget (FSE12), la \
sécurité sociale (FSE13-14) et le circuit économique (FSE15), sans les ré-enseigner.

## 2. Théorie progressive

Analyser une **décision publique** suppose de répondre, dans l'ordre, à plusieurs questions. \
D'abord, quelle est la **décision** précise, et quel **niveau de pouvoir** est compétent \
pour la prendre (vu en FSE08-09) ? Ensuite, quels sont ses **objectifs** affichés ? Quels \
**agents** (ménages, entreprises, État, reste du monde — vus en FSE15) sont concernés, et \
par quels **flux** (réels et monétaires) ?

Il faut ensuite évaluer les **effets attendus** de la décision : à qui profite-t-elle \
directement ? Mais aussi ses **limites** : quelles conditions doivent être réunies pour que \
l'effet attendu se réalise réellement (ex. une capacité suffisante du réseau de transport) ? \
Et ses **conséquences indirectes** : quels effets, non visés au départ, pourraient aussi se \
produire (ex. une recette fiscale supplémentaire liée à un emploi facilité) ?

Une distinction essentielle est celle entre le **court terme** (l'effet immédiat, souvent \
une dépense ou un coût) et le **long terme** (des effets qui ne se concrétisent, le cas \
échéant, qu'après un certain délai, et qui restent parfois incertains). Une bonne analyse \
ne confond jamais un effet attendu avec un effet garanti.

Enfin, une **conclusion fondée sur les documents** s'appuie explicitement sur les éléments \
réellement présents dans le dossier (chiffres, citations, réactions des agents concernés), \
jamais sur une impression générale non appuyée sur le texte.

## 3. Définitions importantes

- **Décision publique** : choix pris par un niveau de pouvoir compétent, avec des objectifs \
affichés.
- **Effet attendu** : conséquence visée par une décision publique.
- **Limite** : condition nécessaire pour qu'un effet attendu se réalise réellement.
- **Conséquence indirecte** : effet non visé au départ, qui peut néanmoins se produire.
- **Court terme / long terme** : distinction entre un effet immédiat et un effet qui ne se \
concrétise, le cas échéant, qu'après un certain délai.

## 4. Méthode étape par étape

Face à un dossier sur une décision publique, procède dans cet ordre :

1. Identifie la **décision**, le **niveau de pouvoir** compétent et ses **objectifs** \
affichés.
2. Identifie les **agents concernés** et les **flux** (réels et monétaires) qu'elle \
engendre.
3. Distingue les **effets attendus à court terme** des **effets possibles à plus long \
terme**, en soulignant leurs **limites** (conditions nécessaires) et leurs **conséquences \
indirectes**.
4. Rédige une **conclusion fondée sur les documents**, en citant les éléments précis du \
dossier qui l'appuient.

## 5. Exemples commentés

### Exemple 1 — {FSE16_PROPOSAL_TITLE}

{FSE16_PROPOSAL_TEXT}

**Analyse commentée :** la décision relève d'un niveau **régional** (compétence \
territoriale, transport). Les objectifs affichés sont doubles : faciliter l'accès à \
l'emploi et réduire l'usage de la voiture individuelle. Les agents concernés sont les \
ménages (bénéficiaires directs), les entreprises de transport (fournisseurs du service) et \
l'État régional (financeur).

### Exemple 2 — {FSE16_BUDGET_NOTE_TITLE}

{FSE16_BUDGET_NOTE_TEXT}

**Analyse commentée :** cette note distingue clairement un **effet à court terme** (la \
dépense régionale augmente immédiatement) d'un **effet possible à plus long terme** (une \
compensation partielle par de nouvelles recettes), explicitement présenté comme une \
**hypothèse incertaine**, pas un résultat garanti.

### Exemple 3 — Réaction de l'association environnementale

« Nous saluons l'effet attendu de réduction de l'usage de la voiture individuelle, mais \
rappelons que cet effet dépendra de la capacité réelle du réseau à absorber la demande \
supplémentaire — un effet incertain à court terme, qui pourrait ne se concrétiser qu'à plus \
long terme si le réseau est renforcé en conséquence. »

**Analyse commentée :** cette réaction illustre une **limite** explicite de l'effet attendu \
(réduction de l'usage de la voiture) : cet effet dépend de la **capacité réelle du réseau** \
à absorber la demande supplémentaire — sans cette condition, l'effet pourrait ne pas se \
réaliser, ou seulement à plus long terme.

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse** : « Cette aide réduira certainement l'usage de la voiture \
individuelle. » → présente un effet attendu comme un résultat garanti, en ignorant la limite \
explicitement mentionnée (capacité du réseau).
- ✅ **Bonne réponse** : « Cette aide vise à réduire l'usage de la voiture individuelle, mais \
cet effet reste conditionné à la capacité du réseau à absorber la demande supplémentaire, \
comme le souligne l'association environnementale. »

- ❌ **Mauvaise réponse** : « Cette décision ne coûte rien à l'État, puisqu'elle facilite \
l'emploi. » → ignore la dépense immédiate (court terme) au profit d'un effet hypothétique \
(long terme, incertain).
- ✅ **Bonne réponse** : « À court terme, la dépense régionale augmente ; une compensation \
partielle par de nouvelles recettes n'est qu'une hypothèse à plus long terme, non garantie. »

## 7. Pièges et erreurs fréquentes

- **Confondre effet attendu et effet garanti** : toujours vérifier les limites mentionnées \
dans les documents.
- **Ignorer les conséquences indirectes** (ex. recettes fiscales supplémentaires liées à un \
emploi facilité).
- **Confondre court terme et long terme** : une dépense immédiate n'est pas annulée par un \
effet hypothétique à plus long terme.
- **Conclure sans s'appuyer sur les documents** : toute conclusion doit citer un élément \
précis du dossier.

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Identifier les agents et les flux (essaie avant de regarder la \
correction)</summary>

Reprends la proposition (document 1). Liste les agents concernés et, pour chacun, un flux \
(réel ou monétaire) qui le relie à cette décision.

<details>
<summary>Voir la correction expliquée</summary>

Ménages : reçoivent une subvention (flux monétaire) qui réduit leur dépense de transport. \
Entreprises de transport collectif : reçoivent davantage de clients (flux réel, \
fréquentation) et des ressources supplémentaires pour développer leur capacité. État \
régional : verse la subvention (flux monétaire sortant), financée par son budget existant \
(vu en FSE12).

Ce corrigé fonctionne parce qu'il associe un flux concret à chaque agent, plutôt que de se \
limiter à les citer.
</details>
</details>

<details>
<summary>Exercice 2 — Distinguer effet attendu et limite (essaie avant de regarder la \
correction)</summary>

À partir de la réaction de l'entreprise de transport (document 3), identifie un effet \
attendu de la proposition ET une limite ou un coût qu'elle soulève.

<details>
<summary>Voir la correction expliquée</summary>

Effet attendu : une hausse de la fréquentation des lignes de transport collectif. Limite/ \
coût soulevé : des coûts supplémentaires pour augmenter la capacité des lignes les plus \
demandées, qui ne sont pas financés automatiquement par la seule subvention aux usagers.

Ce corrigé fonctionne parce qu'il distingue l'effet positif annoncé et la limite/le coût \
qu'il entraîne, plutôt que de ne retenir que l'un des deux.
</details>
</details>

## 9. Corrigés très expliqués

**Question :** « Rédige une conclusion argumentée sur cette proposition, fondée sur les \
trois documents. »

**Corrigé expliqué :** la proposition vise, par une subvention régionale (document 1), à \
faciliter l'accès à l'emploi des travailleurs à revenus modestes et à réduire l'usage de la \
voiture individuelle. Elle engendre une dépense immédiate pour la Région, compensée \
peut-être en partie, mais seulement à plus long terme et de façon incertaine, par de \
nouvelles recettes liées à l'emploi facilité (document 2). Ses effets positifs dépendent \
toutefois de conditions réelles, notamment la capacité du réseau de transport à absorber la \
demande supplémentaire, comme le souligne l'association environnementale, et des coûts \
d'adaptation du réseau, comme le souligne l'entreprise de transport (document 3). Une \
évaluation complète de cette décision devrait donc attendre de vérifier si ces conditions \
sont effectivement réunies, plutôt que de considérer ses effets positifs comme acquis.

Ce corrigé fonctionne parce qu'il s'appuie successivement sur les trois documents, distingue \
court et long terme, et conclut sur une réserve justifiée plutôt que sur une affirmation non \
nuancée.

## 10. Fiche mémo

- Méthode : décision + niveau compétent + objectifs → agents + flux → effets attendus + \
limites + conséquences indirectes (court/long terme) → conclusion fondée sur les documents.
- Un effet attendu n'est jamais un effet garanti : vérifier les limites mentionnées.
- Les conséquences indirectes (ex. recettes fiscales supplémentaires) sont à distinguer de \
l'effet principal visé.
- Une conclusion doit toujours s'appuyer sur des éléments précis du dossier, jamais sur une \
impression générale.
"""


def fse16_course_sections() -> list[tuple[str, str]]:
    """Sections (titre, Markdown) du cours FSE16 — refonte pédagogique et visuelle
    (ticket #105), voir `app.v1.fse_course_sections.build_course_sections`."""
    return build_course_sections("FSE16", fse16_course_markdown())
