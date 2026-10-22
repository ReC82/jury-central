"""Contenu de cours — FSE14 « La sécurité sociale : organismes et enjeux » (ticket #100,
cahier des charges détaillé).

Même structure que FSE01-FSE13 : 1. Ce que tu dois savoir faire à l'examen —
2. Théorie progressive — 3. Définitions importantes — 4. Méthode étape par étape —
5. Exemples commentés — 6. Mauvaises réponses comparées aux bonnes — 7. Pièges et erreurs
fréquentes — 8. Exercices guidés (corrigés masqués par défaut) — 9. Corrigés très
expliqués — 10. Fiche mémo — 11. Sources officielles vérifiées.

Périmètre strict (ticket #100, programme p. 61-62) : associer organismes et rôles
(collecteur/gestionnaire/intermédiaire payeur), allocations familiales régionalisées
(FAMIWAL/FAMIRIS), enjeux de vieillissement/emploi/dépenses de santé — SANS mémorisation de
montants, âges de pension ou règles d'accès non vérifiés, conformément au ticket."""

from app.v1.fse_course_sections import build_course_sections


def fse14_course_markdown() -> str:
    return """# FSE14 — La sécurité sociale : organismes et enjeux

## 1. Ce que tu dois savoir faire à l'examen

Tu dois être capable d'associer un organisme de sécurité sociale à son rôle (collecteur, \
gestionnaire ou intermédiaire payeur), de situer les allocations familiales régionalisées \
(FAMIWAL en Wallonie, FAMIRIS/Iriscare à Bruxelles), et d'expliquer deux pressions \
générales sur le financement de la sécurité sociale. **Tu n'as jamais besoin de mémoriser \
un montant, un âge de pension ou une règle d'accès précise.**

**Prérequis** : ce cours réutilise le trajet cotisation→prestation et la distinction \
financement/gestion/versement vus en FSE13.

## 2. Théorie progressive

Plusieurs organismes publics belges se partagent les rôles de **collecteur**, de \
**gestionnaire** et d'**intermédiaire payeur** au sein de la sécurité sociale — trois rôles \
déjà distingués en FSE13 (financement, gestion, versement), ici incarnés par des organismes \
précis. L'**ONSS** joue le rôle de collecteur : il perçoit la quasi-totalité des cotisations \
sociales dues par les employeurs et les travailleurs. Plusieurs organismes jouent ensuite un \
rôle de gestionnaire, chacun pour une branche précise : l'**INAMI** pour l'assurance \
maladie-invalidité, l'**ONEM** pour le chômage, le **SFP** pour les pensions, **FEDRIS** \
pour les accidents du travail et maladies professionnelles, l'**ONVA** pour le pécule de \
vacances des travailleurs manuels, et l'**INASTI** pour la sécurité sociale des travailleurs \
indépendants.

Certains organismes jouent un rôle d'**intermédiaire payeur** : ils ne collectent ni ne \
gèrent le système dans son ensemble, mais versent concrètement une prestation à la personne \
concernée, pour le compte de l'organisme gestionnaire — c'est le cas des **mutualités** pour \
le remboursement des soins de santé.

Les **allocations familiales** ont été **régionalisées** : chaque Région/Communauté \
organise désormais son propre système. En Wallonie, c'est **FAMIWAL** qui verse les \
allocations familiales ; à Bruxelles, c'est **FAMIRIS**, un service d'**Iriscare** (organisme \
bicommunautaire bruxellois).

Le financement de la sécurité sociale fait face à des **enjeux** généraux et documentés, \
sans qu'il soit nécessaire d'en mémoriser les montants précis : le **vieillissement de la \
population** (plus de personnes à la retraite par rapport aux personnes en activité qui \
cotisent) et l'**augmentation des dépenses de santé** (progrès médicaux, vieillissement) \
pèsent tous deux sur l'équilibre financier du système.

## 3. Définitions importantes

- **Collecteur** : organisme qui perçoit les cotisations (ex. ONSS).
- **Gestionnaire** : organisme qui organise et gère une branche précise de la sécurité \
sociale (ex. INAMI, ONEM, SFP, FEDRIS, ONVA, INASTI).
- **Intermédiaire payeur** : organisme qui verse concrètement une prestation, pour le compte \
d'un gestionnaire (ex. mutualité, FAMIWAL, FAMIRIS).
- **Régionalisation** (des allocations familiales) : transfert de l'organisation des \
allocations familiales aux Régions/Communautés, chacune avec son propre organisme payeur.

## 4. Méthode étape par étape

Face à une situation ou un tableau, procède dans cet ordre :

1. Identifie l'**organisme** concerné et la **branche** de sécurité sociale qu'il couvre.
2. Détermine son **rôle** : collecteur, gestionnaire ou intermédiaire payeur.
3. Pour les allocations familiales, identifie la **Région** concernée (FAMIWAL en Wallonie, \
FAMIRIS à Bruxelles).
4. Pour un enjeu de financement, explique le **mécanisme général** (ex. vieillissement → \
plus de dépenses, moins de cotisants), jamais un montant précis non vérifié.

## 5. Exemples commentés

### Exemple 1 — L'ONSS

L'ONSS perçoit la quasi-totalité des cotisations sociales dues par les employeurs et les \
travailleurs.

**Analyse commentée :** l'ONSS joue le rôle de **collecteur** : il réunit l'argent, mais ne \
gère pas lui-même les prestations de chaque branche.

### Exemple 2 — La mutualité

La mutualité verse concrètement certaines prestations (ex. remboursement de soins de santé) \
aux personnes affiliées, pour le compte de l'INAMI.

**Analyse commentée :** la mutualité joue le rôle d'**intermédiaire payeur** : elle ne gère \
pas l'ensemble de la branche maladie-invalidité (c'est le rôle de l'INAMI), mais verse \
concrètement l'argent à la personne.

### Exemple 3 — Allocations familiales régionalisées

Une famille domiciliée en Wallonie reçoit ses allocations familiales via FAMIWAL ; une \
famille domiciliée à Bruxelles les reçoit via FAMIRIS.

**Analyse commentée :** ces deux organismes jouent le même rôle d'**intermédiaire payeur**, \
mais chacun pour sa propre Région, depuis la régionalisation des allocations familiales.

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse** : « L'ONSS gère les pensions. » → confond le rôle de collecteur \
(ONSS) avec le rôle de gestionnaire d'une branche précise (SFP pour les pensions).
- ✅ **Bonne réponse** : « L'ONSS collecte les cotisations ; c'est le SFP qui gère la \
branche pension. »

- ❌ **Mauvaise réponse** : « FAMIWAL verse les allocations familiales partout en \
Belgique. » → ignore la régionalisation.
- ✅ **Bonne réponse** : « FAMIWAL verse les allocations familiales en Wallonie ; FAMIRIS \
les verse à Bruxelles — chaque Région a son propre organisme depuis la régionalisation. »

## 7. Pièges et erreurs fréquentes

- **Confondre collecteur et gestionnaire** : l'ONSS collecte, mais ne gère pas lui-même \
chaque branche.
- **Oublier la régionalisation des allocations familiales** : il n'existe plus un seul \
organisme pour toute la Belgique.
- **Vouloir mémoriser un âge de pension, un montant ou une condition d'accès précise** : \
hors périmètre de ce cours.
- **Réduire les enjeux de financement à un seul facteur** : vieillissement et dépenses de \
santé sont deux pressions distinctes, souvent combinées.

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Associer organisme et rôle (essaie avant de regarder la \
correction)</summary>

Quel est le rôle de FEDRIS, et pour quelle branche de la sécurité sociale ?

<details>
<summary>Voir la correction expliquée</summary>

FEDRIS est **gestionnaire** de la branche accidents du travail et maladies professionnelles \
: il contrôle les assureurs, l'obligation d'assurance des entreprises, et indemnise les \
victimes de ces risques.

Ce corrigé fonctionne parce qu'il précise à la fois le rôle (gestionnaire) et la branche \
précise concernée, plutôt qu'une réponse vague.
</details>
</details>

<details>
<summary>Exercice 2 — Expliquer un enjeu de financement (essaie avant de regarder la \
correction)</summary>

Explique pourquoi le vieillissement de la population pèse sur le financement de la sécurité \
sociale, sans donner de chiffre précis.

<details>
<summary>Voir la correction expliquée</summary>

Le vieillissement de la population signifie qu'un nombre croissant de personnes atteint \
l'âge de la retraite, ce qui augmente les dépenses de pension, pendant que le nombre de \
personnes en activité qui cotisent reste relativement plus restreint. Cela crée une tension \
entre des dépenses croissantes et des recettes de cotisations qui n'augmentent pas dans la \
même proportion.

Ce corrigé fonctionne parce qu'il explique le mécanisme général (plus de bénéficiaires, pas \
nécessairement plus de cotisants) sans avancer de chiffre non vérifié.
</details>
</details>

## 9. Corrigés très expliqués

**Question :** « Pourquoi distingue-t-on collecteur, gestionnaire et intermédiaire payeur, \
alors qu'on pourrait croire qu'un seul organisme suffit pour toute la sécurité sociale ? »

**Corrigé expliqué :** parce que la sécurité sociale belge couvre plusieurs branches très \
différentes (maladie, chômage, pension, accidents du travail, allocations familiales...), \
chacune avec ses propres règles et son propre public. Centraliser la collecte des \
cotisations dans un seul organisme (l'ONSS) tout en confiant la gestion de chaque branche à \
un organisme spécialisé (INAMI, ONEM, SFP, FEDRIS, ONVA, INASTI) permet une organisation \
plus claire ; le versement concret est ensuite parfois délégué à un intermédiaire proche du \
bénéficiaire (mutualité, FAMIWAL, FAMIRIS), pour simplifier les démarches.

Ce corrigé fonctionne parce qu'il justifie la distinction par une raison d'organisation \
concrète, plutôt que de se contenter de lister les trois rôles.

## 10. Fiche mémo

- Collecteur = ONSS (perçoit les cotisations).
- Gestionnaires par branche : INAMI (maladie-invalidité), ONEM (chômage), SFP (pensions), \
FEDRIS (accidents du travail/maladies professionnelles), ONVA (pécule de vacances), INASTI \
(indépendants).
- Intermédiaires payeurs : mutualités (soins de santé), FAMIWAL (allocations familiales, \
Wallonie), FAMIRIS/Iriscare (allocations familiales, Bruxelles).
- Allocations familiales régionalisées : un organisme payeur propre à chaque \
Région/Communauté.
- Enjeux de financement : vieillissement de la population, augmentation des dépenses de \
santé — jamais de montant ni d'âge précis à mémoriser.

## 11. Sources officielles vérifiées

Les noms et rôles des organismes sont vérifiés auprès de sources belges officielles, à la \
date du 2026-10-01 :

- Service public fédéral Sécurité sociale, « Institutions », \
https://www.socialsecurity.be/citizen/fr/a-propos-de-la-securite-sociale/institutions — \
consulté le 2026-10-01 (ONSS, INAMI, ONEM, SFP, FEDRIS, ONVA, INASTI).
- Wallonie.be, « Caisse publique wallonne d'allocations familiales (Famiwal) », \
https://www.wallonie.be/fr/acteurs-et-institutions/wallonie/autres-acteurs-publics-de-la-wallonie/caisse-publique-wallonne-dallocations-familiales-famiwal \
— consulté le 2026-10-01.
- Iriscare, « Caisse d'allocations familiales Famiris », \
https://www.iriscare.brussels/fr/service/iriscare/direction-iriscare/departement-operations/caisse-dallocations-familiales-famiris/ \
— consulté le 2026-10-01.

En cas de doute sur un droit réel, consulte ces organismes officiels plutôt que ce cours.
"""


def fse14_course_sections() -> list[tuple[str, str]]:
    """Sections (titre, Markdown) du cours FSE14 — refonte pédagogique et visuelle
    (ticket #105), voir `app.v1.fse_course_sections.build_course_sections`."""
    return build_course_sections("FSE14", fse14_course_markdown())
