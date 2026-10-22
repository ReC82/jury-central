"""Contenu de cours — Français FR06→FR10 (ticket #94, PHASE B).

Même structure imposée que PHASE A (#94, `app.v1.francais_fr01_05_courses`, docstring) :
1. Ce que je dois savoir faire à l'examen — 2. Théorie progressive — 3. Définitions —
4. Méthode étape par étape — 5. Exemples commentés — 6. Mauvaises réponses vs bonnes —
7. Pièges — 8. Exercices guidés — 9. Corrigés expliqués — 10. Fiche mémo. (11. S'entraîner
/ 12. S'évaluer déjà fournis génériquement par `_uaa_space_nav.html`, ticket #22.)

Leçon du review PHASE A appliquée dès le départ ici : AUCUNE mention "validation
technique provisoire"/statut prototype sur ces pages — ce sont de vrais cours."""

from app.v1.francais_fr06_10_content import (
    FR06_ARTICLE_TEXT,
    FR06_ARTICLE_TITLE,
    FR06_MULTIMEDIA_TEXT,
    FR06_MULTIMEDIA_TITLE,
    FR06_SITE_TEXT,
    FR06_SITE_TITLE,
    FR06_TOC_TEXT,
    FR06_TOC_TITLE,
    FR07_SOURCE_A_TEXT,
    FR07_SOURCE_A_TITLE,
    FR07_SOURCE_B_TEXT,
    FR07_SOURCE_B_TITLE,
    FR08_SOURCE1_TEXT,
    FR08_SOURCE1_TITLE,
    FR09_DOC1_TEXT,
    FR09_DOC1_TITLE,
    FR09_DOC2_TEXT,
    FR09_DOC2_TITLE,
    FR10_TEXT1_TEXT,
    FR10_TEXT1_TITLE,
)


def fr06_course_markdown() -> str:
    return f"""# Rechercher et sélectionner l'information

## 1. Ce que tu dois savoir faire à l'examen

Tu dois pouvoir, face à un sujet donné, chercher efficacement une information dans \
différents types de sources (sommaire, index, dictionnaire, encyclopédie, article, site, \
ressource multimédia), en évaluant leur pertinence AVANT de les lire en entier.

## 2. Théorie progressive

Rechercher une information commence par transformer un sujet en questions de recherche \
précises, puis en mots-clés et synonymes à utiliser dans un sommaire, un index ou un \
moteur de recherche. Une fois une source identifiée, un **survol** rapide (titre, \
sommaire, intertitres) permet de juger sa pertinence avant une lecture plus poussée. Le \
**repérage** consiste à localiser rapidement où se trouve l'information recherchée \
(numéro de page, chapitre, minutage d'une vidéo), pour ensuite pratiquer une **lecture \
sélective** (seulement les passages utiles) plutôt qu'une lecture intégrale.

Toute recherche sérieuse se conclut par une prise de notes organisée, idéalement sous \
forme de **fiche-source** (titre, auteur/origine si connu, date, contenu utile retenu), \
qui constitue une trace exploitable ensuite (portefeuille de recherche).

## 3. Définitions importantes

- **Sommaire** : liste des chapitres d'un document, avec leur numéro de page.
- **Index** : liste alphabétique de mots-clés avec leur(s) page(s) de référence.
- **Survol** : lecture rapide et globale pour juger la pertinence d'un document.
- **Repérage** : action de localiser précisément une information dans un document.
- **Lecture sélective** : lecture ciblée uniquement des passages utiles, par opposition à \
la lecture intégrale (tout le document).
- **Pertinence** : qualité d'une source qui répond réellement à la question posée.
- **Fiche-source** : note structurée (titre, origine, contenu retenu) qui garde une trace \
d'une recherche.

## 4. Méthode étape par étape

1. Transforme ton sujet en une ou plusieurs questions de recherche précises.
2. Identifie des mots-clés et leurs synonymes pour chaque question.
3. Choisis un type de source adapté (dictionnaire pour un mot, encyclopédie pour un \
sujet général, article pour une actualité, site pour un service pratique).
4. Survole la source (sommaire, index, titres) pour juger sa pertinence avant de la lire \
en entier.
5. Repère précisément où se trouve l'information utile (page, chapitre, minutage).
6. Pratique une lecture sélective des seuls passages utiles.
7. Note l'information retenue dans une fiche-source, avec son origine.

## 5. Exemples commentés

### {FR06_TOC_TITLE}

{FR06_TOC_TEXT}

**Question d'exemple :** je cherche des informations sur mes droits en cas d'absence. Où \
dois-je regarder ?

**Analyse commentée :** l'index indique « congés (p. 27) » — un repérage rapide via \
l'index évite de parcourir tout le guide. Le sommaire confirme : Chapitre 4.2, page 27.

### {FR06_ARTICLE_TITLE}

{FR06_ARTICLE_TEXT}

**Analyse commentée :** un survol du titre et du premier paragraphe suffit à juger que \
cet article est pertinent pour une recherche sur « horaires des bibliothèques », sans \
devoir lire les détails sur le recrutement d'agents si ce n'est pas la question posée.

### {FR06_SITE_TITLE}

{FR06_SITE_TEXT}

### {FR06_MULTIMEDIA_TITLE}

{FR06_MULTIMEDIA_TEXT}

**Analyse commentée :** les chapitres horodatés permettent un repérage direct — pour une \
question sur les erreurs fréquentes, il n'est pas nécessaire de regarder la vidéo en \
entier : le chapitre 2 (03:40) suffit.

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse** (face à un dossier de plusieurs sources) : lire chaque document \
en entier avant de savoir lequel est utile, en perdant un temps considérable.
- ✅ **Bonne réponse** : survoler chaque source pour juger sa pertinence par rapport à la \
question posée, puis ne lire en détail que les sources réellement pertinentes.

## 7. Pièges et erreurs fréquentes

- Lire un document en entier alors qu'un survol aurait suffi à juger sa pertinence.
- Confondre sommaire (chapitres/pages) et index (mots-clés alphabétiques).
- Chercher un mot-clé trop général, qui ne mène à aucun résultat précis.
- Oublier de noter l'origine d'une information retenue (fiche-source incomplète).

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Essaie avant de regarder la correction</summary>

Tu cherches à savoir comment gérer le stress des premières semaines dans un nouvel \
emploi. En utilisant le sommaire du guide, à quelle page devrais-tu aller directement ?

<details>
<summary>Voir la correction expliquée</summary>

Le sommaire indique « 2.3 Gérer le stress des premières semaines » à la page 15 — un \
repérage direct via le sommaire, sans avoir à parcourir tout le Chapitre 2.
</details>
</details>

<details>
<summary>Exercice 2 — Essaie avant de regarder la correction</summary>

Pour connaître les horaires d'ouverture précis de la bibliothèque, l'article ou la \
description du site « Ma Commune Pratique » est-il la source la plus directement \
pertinente ? Justifie.

<details>
<summary>Voir la correction expliquée</summary>

L'article donne l'information demandée directement (horaires élargis, jours précis). Le \
site décrit ne mentionne pas les bibliothèques dans sa description — il n'est donc pas \
pertinent pour cette question précise, même s'il pourrait l'être pour une autre question \
(ex. trouver un numéro de contact général).
</details>
</details>

## 9. Corrigés très expliqués

**Question :** dans quelle rubrique du site « Ma Commune Pratique » trouverais-tu une \
formation financée ?

**Corrigé expliqué :** la rubrique « Emploi et formation » contient l'entrée \
« Formations financées » d'après la description du site. Un repérage direct dans le \
sous-menu décrit permet de répondre sans avoir à « visiter » tout le site imaginé.

## 10. Fiche mémo

- Sommaire = chapitres/pages ; Index = mots-clés alphabétiques.
- Toujours survoler avant de lire en entier.
- Repérage = trouver où ; lecture sélective = lire seulement ce qui est utile.
- Une fiche-source garde toujours une trace de l'origine de l'information.
"""


def fr07_course_markdown() -> str:
    return f"""# Évaluer une source et sa fiabilité

## 1. Ce que tu dois savoir faire à l'examen

Tu dois pouvoir évaluer si une source est fiable en observant qui l'a écrite, dans quel \
but, avec quelle méthode — et distinguer la PERTINENCE d'une source (répond-elle à ma \
question ?) de sa FIABILITÉ (peut-on lui faire confiance ?), deux qualités différentes.

## 2. Théorie progressive

Une source fiable se reconnaît à plusieurs critères convergents : qui est l'**auteur ou \
l'organisme** (a-t-il une expertise réelle sur le sujet ?), quel est l'**éditeur/site** \
(institution reconnue, entreprise commerciale, forum ouvert...), quelle est la **date** \
(une information peut devenir obsolète), et quel est l'**objectif** déclaré ET réel de la \
source (informer, vendre, convaincre, témoigner...).

Il faut aussi savoir distinguer, dans un même texte, ce qui relève du **fait** \
(vérifiable), de l'**opinion** (jugement personnel), du **témoignage** (expérience \
individuelle), de la **publicité** (vise à vendre) ou de l'**argument** (soutient une \
thèse). Une source biaisée n'est pas forcément fausse, mais elle mérite d'être \
**recoupée** avec d'autres sources indépendantes avant d'être considérée comme fiable.

## 3. Définitions importantes

- **Expertise** : compétence reconnue d'un auteur/organisme sur le sujet traité.
- **Biais** : orientation qui favorise un point de vue, souvent liée à un intérêt \
(commercial, idéologique).
- **Recoupement** : vérification d'une information en la comparant à d'autres sources \
indépendantes.
- **Pertinence** : la source répond-elle à la question posée ?
- **Fiabilité** : peut-on faire confiance au contenu de la source ?

## 4. Méthode étape par étape

1. Identifie l'auteur/organisme : a-t-il une expertise reconnue sur ce sujet précis ?
2. Vérifie l'éditeur/site : institution reconnue, entreprise, forum, réseau social ?
3. Regarde la date : l'information est-elle encore d'actualité ?
4. Identifie l'objectif déclaré ET l'objectif réel (parfois différents, ex. publicité \
déguisée en information).
5. Distingue, dans le contenu, ce qui est fait, opinion, témoignage, publicité ou \
argument.
6. Recoupe l'information avec au moins une autre source indépendante si possible.
7. Conclus : la source est-elle pertinente pour ta question ? Est-elle fiable ? Les deux \
réponses peuvent être différentes.

## 5. Exemples commentés

### {FR07_SOURCE_A_TITLE}

{FR07_SOURCE_A_TEXT}

**Analyse commentée :** organisme public de recherche, méthode détaillée, comparaison à \
d'autres études, et surtout une PRUDENCE explicite (« ne permet pas d'établir un lien de \
cause à effet ») — plusieurs signes de fiabilité forte.

### {FR07_SOURCE_B_TITLE}

{FR07_SOURCE_B_TEXT}

**Analyse commentée :** l'objectif déclaré (« sensibiliser ») ne correspond pas à \
l'objectif réel (vendre un logiciel) — un décalage typique d'une source biaisée, à \
recouper impérativement avant d'être utilisée comme preuve.

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse** : « La Source C n'est pas fiable donc elle ne sert à rien. » → \
confond fiabilité (faible pour établir un fait général) et utilité (un témoignage reste \
utile pour comprendre un ressenti individuel).
- ✅ **Bonne réponse** : « La Source C est utile pour connaître un vécu personnel, mais \
insuffisante pour établir un fait général, faute de méthode et de recoupement. »

## 7. Pièges et erreurs fréquentes

- Confondre pertinence (répond au sujet) et fiabilité (digne de confiance).
- Rejeter une source uniquement parce qu'elle est commerciale, sans analyser son contenu.
- Faire confiance à une source uniquement parce qu'elle semble « scientifique » dans le \
ton, sans vérifier la méthode réelle.
- Ne jamais recouper une information choquante ou trop belle pour être vraie.

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Essaie avant de regarder la correction</summary>

La Source D est un article de vulgarisation scientifique qui cite quatre études \
nommément. Est-elle plus ou moins fiable qu'un article scientifique original comme la \
Source A ? Justifie.

<details>
<summary>Voir la correction expliquée</summary>

La Source D reste fiable (elle cite ses sources et nuance ses propos), mais elle est une \
SYNTHÈSE de plusieurs études, pas l'étude elle-même. Elle est utile pour une vue \
d'ensemble, tandis que la Source A donne accès à la méthode précise d'UNE étude — les \
deux ont leur utilité, à des niveaux différents.
</details>
</details>

<details>
<summary>Exercice 2 — Essaie avant de regarder la correction</summary>

Dans la Source B, relève un élément du TEXTE (pas de la présentation) qui révèle son \
objectif commercial réel.

<details>
<summary>Voir la correction expliquée</summary>

La phrase « découvrez comment FamilySafe peut vous aider dès aujourd'hui » est un appel \
direct à l'action commerciale, typique d'un contenu publicitaire déguisé en article de \
sensibilisation.
</details>
</details>

## 9. Corrigés très expliqués

**Question :** pourquoi la Source A est-elle plus fiable que la Source B pour évaluer les \
effets des écrans sur le sommeil des adolescents ?

**Corrigé expliqué :** la Source A provient d'un organisme public de recherche, sans \
intérêt commercial déclaré, avec une méthode précise (questionnaire validé, comparaison à \
d'autres études) et une prudence explicite sur les limites de ses résultats. La Source B \
provient d'une entreprise vendant un produit lié au sujet traité, sans méthode ni \
référence précise, et oriente son contenu vers l'achat de ce produit — un biais commercial \
clair qui réduit fortement sa fiabilité en tant que source d'information neutre.

## 10. Fiche mémo

- Pertinence ≠ fiabilité : une source peut être l'une sans l'autre.
- Vérifie toujours : auteur, éditeur, date, objectif déclaré ET réel.
- Distingue fait, opinion, témoignage, publicité, argument dans un même texte.
- Recoupe toujours une information importante avec une autre source indépendante.
"""


def fr08_course_markdown() -> str:
    return f"""# Réduire et résumer un texte

## 1. Ce que tu dois savoir faire à l'examen

Tu dois pouvoir réduire un texte à l'essentiel — d'abord une phrase, puis un paragraphe, \
puis un texte complet — en respectant fidèlement le sujet, l'intention et l'idée \
principale du texte source, sans jamais y ajouter ton avis personnel.

## 2. Théorie progressive

Résumer, c'est **hiérarchiser** l'information d'un texte : distinguer l'**idée \
principale** (ce qui doit absolument rester) des **idées secondaires** (à garder \
seulement si la longueur imposée le permet) et des détails à **supprimer**. Cette \
**condensation** doit se faire par **reformulation** (dire la même chose avec moins de \
mots et d'autres mots), jamais par un simple collage de phrases copiées-collées.

Un bon résumé reste **fidèle** (ne trahit pas le sens du texte source) et **neutre** (pas \
d'avis personnel de celui qui résume) — à ne pas confondre avec un **commentaire**, qui \
ajoute une analyse ou un point de vue. La **paraphrase**, elle, reformule sans forcément \
réduire la longueur.

## 3. Définitions importantes

- **Réduction/condensation** : action de rendre un texte plus court en gardant l'essentiel.
- **Hiérarchisation** : distinction entre idée principale, idées secondaires, détails.
- **Fidélité** : un résumé fidèle ne déforme jamais le sens du texte source.
- **Neutralité** : un résumé neutre n'ajoute aucune opinion personnelle.
- **Paraphrase** : reformulation d'un texte, sans réduction de longueur nécessaire.

## 4. Méthode étape par étape

1. Lis le texte en entier pour en comprendre le sujet et l'intention globale.
2. Identifie l'idée principale en une phrase.
3. Repère les idées secondaires qui la complètent (2 à 4 en général).
4. Supprime les exemples, détails et répétitions non essentiels.
5. Reformule chaque idée gardée avec tes propres mots, sans copier de phrases entières.
6. Vérifie la longueur imposée et ajuste si besoin.
7. Relis en te demandant : « Ai-je trahi le sens du texte, ou ajouté mon avis ? »

## 5. Exemples commentés

### {FR08_SOURCE1_TITLE}

{FR08_SOURCE1_TEXT}

**Résumé en une phrase :** « Des villes installent des composteurs collectifs pour \
permettre aux habitants sans jardin de valoriser leurs déchets alimentaires. »

**Résumé en un paragraphe (progression phrase → paragraphe) :** « Des villes installent \
des composteurs collectifs pour permettre aux habitants sans jardin de valoriser leurs \
déchets alimentaires. Ce dispositif réduit le poids des poubelles classiques, produit un \
compost redistribué gratuitement, et crée du lien entre voisins. Il demande cependant un \
entretien régulier et un référent motivé pour bien fonctionner. »

**Analyse commentée :** le résumé en paragraphe reprend l'idée principale de la phrase, \
puis ajoute les idées secondaires essentielles (avantages, puis difficulté), sans copier \
aucune phrase du texte source mot pour mot.

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse** : copier-coller la première et la dernière phrase du texte \
source, sans reformulation ni hiérarchisation réelle.
- ✅ **Bonne réponse** : reformuler l'idée principale et les idées secondaires avec ses \
propres mots, dans l'ordre logique du texte source, sans copie.

## 7. Pièges et erreurs fréquentes

- Copier des phrases entières du texte source au lieu de reformuler.
- Oublier une idée secondaire essentielle, ou au contraire garder un détail inutile.
- Ajouter son avis personnel (« ce qui est une excellente initiative... ») — jamais dans \
un résumé neutre.
- Dépasser la longueur imposée sans chercher à condenser davantage.

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Essaie avant de regarder la correction</summary>

Résume en une phrase le texte sur le covoiturage courte distance.

<details>
<summary>Voir la correction expliquée</summary>

Exemple de bonne réponse : « Le covoiturage se développe pour les trajets courts du \
quotidien, porté par la hausse des prix du carburant, la saturation des parkings et des \
préoccupations écologiques, mais reste freiné par la difficulté à synchroniser les \
horaires. » Une phrase qui couvre le sujet ET l'idée principale (développement + frein \
principal), sans détail secondaire inutile.
</details>
</details>

<details>
<summary>Exercice 2 — Essaie avant de regarder la correction</summary>

Le texte source dit : « Ce développement s'explique par plusieurs facteurs convergents. \
La hausse du prix des carburants a rendu le partage des frais plus attractif \
financièrement. » Comment reformuler cette idée sans la copier ?

<details>
<summary>Voir la correction expliquée</summary>

Exemple de reformulation : « Le prix élevé du carburant pousse à partager les frais de \
trajet. » — même idée, mots différents, plus court.
</details>
</details>

## 9. Corrigés très expliqués

**Consigne :** résume en 3 phrases maximum le texte sur le compostage collectif.

**Corrigé expliqué :** « Des villes installent des composteurs collectifs pour les \
habitants sans jardin. Ce dispositif réduit les déchets, produit du compost et crée du \
lien social, mais demande un entretien régulier. La réussite dépend surtout d'un référent \
motivé sur la durée. » Ce corrigé fonctionne car il hiérarchise (idée principale, \
avantages, condition de réussite) en 3 phrases reformulées, sans copie ni opinion \
ajoutée.

## 10. Fiche mémo

- Idée principale d'abord, idées secondaires ensuite, détails supprimés en dernier.
- Reformuler toujours, jamais copier-coller.
- Rester fidèle et neutre : ne jamais ajouter son avis dans un résumé.
- Respecter la longueur imposée, quitte à condenser davantage.
"""


def fr09_course_markdown() -> str:
    return f"""# Synthétiser plusieurs documents

## 1. Ce que tu dois savoir faire à l'examen

Tu dois pouvoir confronter PLUSIEURS documents sur un même sujet pour en dégager les \
points communs, les compléments, les divergences et les nuances, puis organiser ces \
éléments selon un plan THÉMATIQUE personnel — jamais un simple résumé de chaque document \
l'un après l'autre.

## 2. Théorie progressive

La synthèse se distingue fondamentalement du résumé : un résumé condense UN texte selon \
SON plan, alors qu'une synthèse organise les idées de PLUSIEURS documents selon un plan \
PERSONNEL, construit autour de thèmes qui traversent les documents. Le point de départ \
est souvent un **tableau de confrontation** (informel ou mental) : pour chaque idée \
importante, quels documents en parlent, sont-ils d'accord (**commun**), l'un \
ajoute-t-il une information que l'autre n'a pas (**complément**), se \
contredisent-ils (**divergence**), ou l'un vient-il **nuancer** l'autre sans le \
contredire totalement ?

Une fois ces relations identifiées, il faut construire un **plan personnel** thématique \
(par exemple : effets positifs / effets négatifs / conditions de réussite), et rédiger en \
**reformulant**, de façon **neutre**, dans la longueur demandée.

## 3. Définitions importantes

- **Synthèse** : mise en relation organisée de plusieurs documents sur un même sujet, \
selon un plan personnel thématique.
- **Point commun** : idée partagée par au moins deux documents.
- **Complément** : information apportée par un document que les autres n'ont pas.
- **Divergence** : contradiction réelle entre deux documents.
- **Nuance** : différence de degré ou d'angle, sans contradiction totale.
- **Patchwork** (à éviter) : juxtaposition de résumés de chaque document, sans les \
confronter ni les organiser par thème.
- **Plan D1/D2/D3** (à éviter) : organiser sa synthèse document par document, plutôt que \
par thème — l'erreur la plus fréquente et la plus pénalisée.

## 4. Méthode étape par étape

1. Lis chaque document en identifiant son idée principale et sa position sur le sujet.
2. Repère, entre les documents, les points communs, compléments, divergences et nuances.
3. Construis un plan PERSONNEL organisé par thème (jamais un plan par document).
4. Pour chaque thème, mobilise les documents pertinents, en les nommant (Document 1, 2, \
3) mais sans les traiter un par un séparément.
5. Reformule toujours, ne cite jamais de longs passages entiers.
6. Reste neutre : la synthèse rapporte des points de vue, elle n'exprime pas le tien.
7. Vérifie la longueur imposée et l'absence de tout plan D1/D2/D3.

## 5. Exemples commentés

### {FR09_DOC1_TITLE}

{FR09_DOC1_TEXT}

### {FR09_DOC2_TITLE}

{FR09_DOC2_TEXT}

**Analyse commentée :** ces deux documents partagent un POINT COMMUN implicite : tous \
deux évoquent une difficulté liée au travail collectif à distance (délais allongés pour \
le Document 1, isolement des nouveaux salariés pour le Document 2) — une vraie mise en \
relation thématique, pas une simple juxtaposition « le Document 1 dit que... le Document \
2 dit que... ».

**Exemple de plan THÉMATIQUE (jamais par document) :** 1. Effets sur la productivité \
individuelle et collective — 2. Effets sur l'intégration et le lien social — 3. \
Conditions de réussite selon les sources.

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse** (plan D1/D2/D3, à proscrire absolument) : « Le Document 1 dit \
que... Le Document 2 dit que... Le Document 3 dit que... » — aucune vraie mise en \
relation, juste un résumé de chaque document l'un après l'autre.
- ✅ **Bonne réponse** (plan thématique) : « Sur le plan de la productivité, le Document 1 \
montre un gain individuel mais une perte collective, ce que confirme indirectement le \
Document 2 en évoquant des échanges moins spontanés. »

## 7. Pièges et erreurs fréquentes

- Le plan D1/D2/D3 — l'erreur la plus fréquente et la plus pénalisée à l'examen.
- Le patchwork : citer un extrait de chaque document sans les relier entre eux.
- Ajouter son avis personnel au lieu de rester neutre.
- Ignorer un document parce qu'il semble moins important, plutôt que de l'intégrer au \
plan thématique.

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Essaie avant de regarder la correction</summary>

Le Document 3 (médecine du travail) apporte-t-il un complément ou une divergence par \
rapport aux Documents 1 et 2 ?

<details>
<summary>Voir la correction expliquée</summary>

Un COMPLÉMENT : le Document 3 aborde un angle nouveau (la santé physique, troubles \
musculo-squelettiques) que ne traitent ni le Document 1 (économique) ni le Document 2 \
(intégration sociale) — il ne les contredit pas, il élargit le sujet.
</details>
</details>

<details>
<summary>Exercice 2 — Essaie avant de regarder la correction</summary>

Propose un plan thématique en trois parties pour synthétiser les trois documents sur le \
télétravail.

<details>
<summary>Voir la correction expliquée</summary>

Exemple : 1. Effets sur la productivité (individuelle vs collective) — 2. Effets sur \
l'intégration et le lien social — 3. Effets sur la santé physique. Un plan par thème, \
jamais « Document 1 / Document 2 / Document 3 ».
</details>
</details>

## 9. Corrigés très expliqués

**Consigne :** en une phrase, identifie un point de VIGILANCE commun aux trois documents \
sur le télétravail (au-delà de leurs différences d'angle).

**Corrigé expliqué :** « Les trois documents s'accordent sur le fait que le télétravail \
demande un encadrement spécifique — que ce soit pour préserver le travail d'équipe \
(Document 1), accompagner les nouveaux arrivants (Document 2), ou garantir de bonnes \
conditions matérielles (Document 3) — plutôt qu'être laissé sans aucun cadre. » Ce corrigé \
fonctionne car il dégage un point commun THÉMATIQUE réel, au-delà du simple constat que \
« les trois documents parlent du télétravail ».

## 10. Fiche mémo

- Synthèse ≠ résumé : plusieurs documents, plan personnel thématique.
- Jamais de plan D1/D2/D3 : c'est l'erreur la plus pénalisée.
- Cherche systématiquement : points communs, compléments, divergences, nuances.
- Reste neutre, reformule toujours, ne cite jamais de longs passages entiers.
"""


def fr10_course_markdown() -> str:
    return f"""# Comprendre thèse, arguments et preuves

## 1. Ce que tu dois savoir faire à l'examen

Tu dois pouvoir identifier, dans un texte argumentatif, la thèse défendue (explicite ou \
implicite), les arguments qui la soutiennent, les exemples et preuves qui les illustrent, \
ainsi que les éventuels contre-arguments — et distinguer un argument solide d'un argument \
faible (impression non prouvée, généralisation hâtive, attaque personnelle simple).

## 2. Théorie progressive

Un texte argumentatif défend une **thèse** sur un **thème** donné — parfois énoncée \
clairement (thèse explicite), parfois seulement suggérée par l'ensemble du texte (thèse \
implicite). Cette thèse s'appuie sur des **arguments**, des idées générales qui la \
justifient, eux-mêmes illustrés par des **exemples** concrets ou appuyés par des \
**preuves/données** vérifiables. Un texte peut aussi anticiper un **contre-argument** \
pour mieux le réfuter, avant d'aboutir à une **conclusion**.

Tous les arguments ne se valent pas : un argument appuyé sur une **donnée précise** \
(chiffre, étude, source identifiée) est plus solide qu'un argument reposant sur une \
simple impression, une **généralisation hâtive** (tirer une règle générale d'un seul cas), \
des **arguments répétitifs** (répéter la même idée sous une autre forme sans rien \
ajouter), ou une **attaque personnelle simple** (juger la personne plutôt que son idée).

## 3. Définitions importantes

- **Thèse** : position défendue par l'auteur sur un sujet donné.
- **Argument** : idée générale qui soutient la thèse.
- **Exemple** : cas concret qui illustre un argument.
- **Preuve/donnée** : élément vérifiable (chiffre, étude, fait) qui appuie un argument.
- **Contre-argument** : objection anticipée et traitée par l'auteur.
- **Généralisation hâtive** : tirer une conclusion générale à partir d'un cas trop limité.
- **Attaque personnelle simple** : critiquer la personne plutôt que son idée, sans preuve.

## 4. Méthode étape par étape

1. Identifie le thème général du texte.
2. Cherche la thèse : est-elle énoncée clairement, ou dois-tu la déduire de l'ensemble du \
texte (thèse implicite) ?
3. Repère chaque argument avancé pour soutenir cette thèse.
4. Pour chaque argument, identifie l'exemple ou la preuve qui l'illustre — s'il y en a un.
5. Repère un éventuel contre-argument et la façon dont l'auteur y répond.
6. Évalue la solidité de chaque argument : s'appuie-t-il sur une donnée précise, ou \
seulement sur une impression/généralisation/attaque personnelle ?
7. Formule la conclusion du texte, en lien avec la thèse de départ.

## 5. Exemples commentés

### {FR10_TEXT1_TITLE}

{FR10_TEXT1_TEXT}

**Analyse commentée :** thèse explicite (dès la première phrase : « mérite d'être \
encouragée plus largement »). Trois arguments identifiables : productivité maintenue \
(preuve : +4% mesuré), effet santé positif (preuve : -30% d'arrêts maladie), effet social \
(argument plus qualitatif, moins chiffré). Un contre-argument est anticipé et limité \
(« ne convient pas à tous les métiers »).

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse** : « L'argument sur la santé est solide parce que l'auteur \
semble convaincu. » → confond la conviction de l'auteur avec la solidité réelle de \
l'argument (ici, la donnée chiffrée -30% est la vraie preuve de solidité, pas le ton).
- ✅ **Bonne réponse** : « L'argument sur la santé est solide car il s'appuie sur une \
donnée chiffrée précise (-30% d'arrêts maladie) issue d'une étude interne nommée, pas \
seulement sur une impression. »

## 7. Pièges et erreurs fréquentes

- Confondre argument (idée générale) et exemple (cas particulier qui l'illustre).
- Accepter un argument comme solide simplement parce qu'il est affirmé avec assurance.
- Ne pas repérer une thèse implicite, en cherchant une phrase qui l'énoncerait \
explicitement alors qu'elle se déduit de l'ensemble du texte.
- Ignorer les arguments répétitifs (la même idée reformulée plusieurs fois n'ajoute pas \
de preuve supplémentaire).

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Essaie avant de regarder la correction</summary>

Le deuxième texte (contre la généralisation hâtive) reproche au premier texte un défaut \
précis dans son raisonnement. Lequel ?

<details>
<summary>Voir la correction expliquée</summary>

Le deuxième texte reproche au premier de généraliser des résultats obtenus dans des \
entreprises déjà favorables et volontaires à l'ensemble des entreprises — une \
généralisation hâtive, puisque rien ne garantit que ces résultats se reproduiraient \
ailleurs.
</details>
</details>

<details>
<summary>Exercice 2 — Essaie avant de regarder la correction</summary>

Dans le premier texte, l'argument social (temps pour la famille, le bénévolat, la \
formation) est-il appuyé par une preuve chiffrée comme les deux premiers arguments ?

<details>
<summary>Voir la correction expliquée</summary>

Non — contrairement aux deux premiers arguments (chiffres précis à l'appui), l'argument \
social reste plus qualitatif, sans donnée chiffrée équivalente. Il est donc, à ce stade \
du texte, moins solidement prouvé que les deux précédents, même s'il reste pertinent.
</details>
</details>

## 9. Corrigés très expliqués

**Question :** le texte mini-test présente trois arguments contre l'usage du téléphone au \
travail. Explique pourquoi l'argument sécuritaire est le plus solide des trois.

**Corrigé expliqué :** l'argument sécuritaire s'appuie sur « plusieurs accidents du \
travail recensés par un organisme de prévention », une donnée précise et vérifiable, \
émanant d'une source identifiée. Les deux autres arguments (productivité, comparaison au \
passé) reposent sur des impressions non chiffrées (« tout le monde perd un temps fou ») \
ou un jugement moral sans preuve (« n'ont qu'à se déconnecter »). La différence de \
solidité tient donc précisément à la présence ou l'absence d'une preuve vérifiable \
derrière chaque argument.

## 10. Fiche mémo

- Thèse = position défendue ; peut être explicite ou implicite.
- Argument = idée générale ; exemple/preuve = ce qui l'illustre ou le prouve.
- Un argument chiffré et sourcé est plus solide qu'une impression ou un jugement moral.
- Repère toujours : généralisation hâtive, répétition sans preuve, attaque personnelle.
"""
