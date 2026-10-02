"""Contenu de cours — FSE07 « Analyser un dossier médiatique » (ticket #98, cahier des charges
détaillé).

Même structure que FSE01-FSE06 : 1. Ce que tu dois savoir faire à l'examen —
2. Théorie progressive — 3. Définitions importantes — 4. Méthode étape par étape —
5. Exemples commentés — 6. Mauvaises réponses comparées aux bonnes — 7. Pièges et erreurs
fréquentes — 8. Exercices guidés (corrigés masqués par défaut) — 9. Corrigés très
expliqués — 10. Fiche mémo.

Périmètre strict (ticket #98, programme p. 41-47) : méthode de recueil/traitement/analyse/
synthèse de l'information et distinction faits/interprétations/opinions, appliquée à un dossier
complet. Ce cours ne réapprend pas le droit à l'image (FSE05) ni les comportements en ligne
(FSE06) ni les normes/valeurs (FSE04) : il les RÉUTILISE comme enjeux à repérer dans un dossier,
sans les ré-enseigner (« ne pas étendre à un cours complet de journalisme », ticket #98)."""

from app.v1.fse07_content import (
    FSE07_CHAT_TEXT,
    FSE07_CHAT_TITLE,
    FSE07_FORUM_TEXT,
    FSE07_FORUM_TITLE,
    FSE07_SCHOOL_TEXT,
    FSE07_SCHOOL_TITLE,
)


def fse07_course_markdown() -> str:
    return f"""# FSE07 — Analyser un dossier médiatique

## 1. Ce que tu dois savoir faire à l'examen

Tu dois être capable de recueillir, traiter, analyser et synthétiser les informations d'un \
dossier composé de plusieurs documents, de distinguer un fait, une interprétation et une \
opinion, de vérifier la fiabilité d'un document (auteur, date, contexte, preuves), \
d'identifier les enjeux juridiques et sociologiques présents, et de rédiger une conclusion \
argumentée.

**Prérequis** : ce cours réutilise le schéma de communication (FSE01), les normes et \
l'influence sociale (FSE04), le droit à l'image (FSE05) et les comportements en ligne (FSE06) \
— ces notions sont rappelées brièvement quand elles sont utiles, jamais ré-enseignées en \
détail ici.

## 2. Théorie progressive

Analyser un dossier médiatique suppose d'abord de distinguer trois types d'énoncés. Un **fait** \
est un élément vérifiable, que plusieurs personnes indépendantes pourraient constater de la même \
façon (« la vidéo a été partagée le 12 mars »). Une **interprétation** est une explication \
proposée à partir d'un ou plusieurs faits, qui reste discutable (« il a probablement filmé la \
scène sans réfléchir aux conséquences »). Une **opinion** est un jugement personnel, qui ne \
prétend pas décrire la réalité mais exprimer un point de vue (« je trouve ça inadmissible »).

Avant d'utiliser un document dans une analyse, il faut le **vérifier** : qui est l'**auteur** \
(identifié ou anonyme) ? à quelle **date** a-t-il été produit ? dans quel **contexte** (lieu, \
circonstance) ? quelles **preuves** concrètes appuient ce qui est affirmé ? Un document signé, \
daté et appuyé sur des éléments vérifiables (comme une note officielle) a une fiabilité \
différente d'un document anonyme, non daté, qui relaie des informations de seconde main sans \
preuve.

Un dossier médiatique soulève souvent plusieurs **enjeux**. Un **enjeu juridique** concerne par \
exemple le droit à l'image (filmer/diffuser sans consentement, vu en FSE05) ou un comportement \
en ligne problématique (vu en FSE06). Un **enjeu sociologique** concerne par exemple les normes \
et l'influence sociale au sein d'un groupe (vu en FSE04) : pourquoi un comportement se répand-il \
dans un groupe, et quelles limites cette explication rencontre-t-elle ?

Enfin, une **conclusion argumentée** s'appuie explicitement sur les faits et les enjeux \
identifiés dans le dossier, jamais sur une impression générale ou sur le document le moins \
fiable du dossier.

## 3. Définitions importantes

- **Fait** : élément vérifiable, constatable de façon similaire par plusieurs personnes \
indépendantes.
- **Interprétation** : explication proposée à partir d'un ou plusieurs faits, qui reste \
discutable.
- **Opinion** : jugement personnel, qui exprime un point de vue plutôt qu'un fait.
- **Fiabilité d'un document** : évaluée à partir de son auteur, sa date, son contexte et les \
preuves qu'il fournit.
- **Enjeu juridique** : question de droit soulevée par une situation (ex. droit à l'image, \
comportement en ligne).
- **Enjeu sociologique** : question liée aux normes, valeurs ou à l'influence sociale dans un \
groupe.
- **Conclusion argumentée** : synthèse qui s'appuie explicitement sur les faits et enjeux \
identifiés, pas seulement sur une opinion personnelle.

## 4. Méthode étape par étape

Face à un dossier de plusieurs documents, procède dans cet ordre :

1. Pour chaque document, identifie l'**auteur**, la **date** et le **contexte** ; note si des \
**preuves** concrètes appuient ce qui y est affirmé.
2. Classe les affirmations importantes de chaque document en **faits**, **interprétations** ou \
**opinions**.
3. Compare les documents entre eux : se contredisent-ils sur des faits ? Un document peu fiable \
affirme-t-il quelque chose qu'aucun document fiable ne confirme ?
4. Identifie les **enjeux juridiques** et **sociologiques** présents, en t'appuyant sur les \
notions déjà vues (FSE04, FSE05, FSE06).
5. Rédige une **conclusion argumentée**, qui s'appuie explicitement sur les faits et enjeux \
identifiés — jamais sur le document le moins fiable du dossier.

## 5. Exemples commentés

### Exemple 1 — {FSE07_SCHOOL_TITLE}

{FSE07_SCHOOL_TEXT}

**Analyse commentée :** ce document est **signé** (M. Devos, directeur adjoint), **daté** (14 \
mars 2026) et décrit des faits précis et vérifiables (date de l'incident, nombre d'élèves dans \
le groupe, mesure prise). C'est le document le plus fiable du dossier.

### Exemple 2 — {FSE07_CHAT_TITLE}

{FSE07_CHAT_TEXT}

**Analyse commentée :** ce document mélange des **faits** (« il tombe dans la cour »), des \
**opinions** (« trop drôle » / « ça craint ») et une **interprétation** (« tout le monde filme \
tout le temps, c'est normal maintenant », qui généralise au-delà de ce que montre réellement le \
document). Il illustre aussi un enjeu sociologique : Yasmine et Thibault semblent suivre une \
norme de groupe qui banalise le fait de filmer, tandis que Karim et Elena s'en écartent \
explicitement — comme vu en FSE04, cette diversité de réactions montre que l'influence du \
groupe n'efface pas les positions individuelles.

### Exemple 3 — {FSE07_FORUM_TITLE}

{FSE07_FORUM_TEXT}

**Analyse commentée :** ce document est **anonyme**, **non daté**, et affirme des faits non \
confirmés par les deux autres documents (« humilié devant toute l'école », alors que la note de \
direction ne mentionne qu'un groupe de 24 élèves ; « la direction n'a strictement rien fait », \
alors que la note de direction décrit une mesure prise). C'est le document le moins fiable du \
dossier : il doit être traité avec prudence, jamais comme une source de faits établis.

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse** : « Le forum dit que la direction n'a rien fait, donc c'est ce qui \
s'est passé. » → utilise comme fait établi une affirmation anonyme et non datée, contredite par \
un document plus fiable.
- ✅ **Bonne réponse** : « La note de direction, signée et datée, décrit une mesure prise (la \
vidéo supprimée à la demande de la direction) ; l'affirmation anonyme du forum, non datée et non \
vérifiable, la contredit sans preuve : elle doit être traitée avec prudence. »

- ❌ **Mauvaise réponse** : « Yasmine trouve ça drôle, donc filmer sans consentement n'est pas \
vraiment un problème de droit à l'image. » → confond une opinion exprimée dans le dossier et la \
réalité de l'enjeu juridique.
- ✅ **Bonne réponse** : « Indépendamment de l'opinion de Yasmine, filmer un camarade sans son \
consentement et diffuser la vidéo dans un groupe pose un enjeu de droit à l'image (FSE05), que \
les réactions des élèves trouvent cela drôle ou non. »

## 7. Pièges et erreurs fréquentes

- **Confondre interprétation et fait** : une explication plausible n'est pas un fait tant \
qu'elle n'est pas vérifiée.
- **Traiter un document anonyme et non daté comme une source fiable** : toujours vérifier \
auteur/date/contexte/preuves avant de l'utiliser.
- **Fonder une conclusion sur une opinion exprimée dans le dossier** plutôt que sur les faits et \
enjeux identifiés.
- **Réduire l'analyse à un seul document** alors que la fiabilité se juge aussi par comparaison \
entre les documents du dossier.

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Fait, interprétation ou opinion ? (essaie avant de regarder la \
correction)</summary>

Classe ces trois phrases tirées du dossier : (a) « La vidéo a été partagée le jour même dans le \
groupe » ; (b) « Je trouve que ça craint » ; (c) « De toute façon tout le monde filme tout le \
temps, c'est normal maintenant ».

<details>
<summary>Voir la correction expliquée</summary>

(a) est un **fait** : élément daté et vérifiable, tiré de la note de direction. (b) est une \
**opinion** : jugement personnel d'Elena. (c) est une **interprétation** : généralisation \
proposée par Thibault à partir de l'incident, qui dépasse ce que les documents permettent de \
vérifier (ils ne montrent qu'un seul cas, pas une pratique générale).

Ce corrigé fonctionne parce qu'il applique la définition de chaque catégorie plutôt que de \
classer les phrases au ton qu'elles emploient.
</details>
</details>

<details>
<summary>Exercice 2 — Comparer la fiabilité de deux documents (essaie avant de regarder la \
correction)</summary>

Le forum anonyme affirme que Lucas a été « humilié devant toute l'école ». La note de direction \
mentionne un groupe de 24 élèves dans une classe. Lequel de ces deux éléments retiens-tu comme \
fait établi, et pourquoi ?

<details>
<summary>Voir la correction expliquée</summary>

Le fait établi est celui de la note de direction (un groupe de 24 élèves, document signé et \
daté). L'affirmation du forum (« devant toute l'école ») n'est confirmée par aucun autre \
document du dossier, provient d'une source anonyme et non datée, et ne doit donc pas être \
retenue comme un fait vérifié, mais au mieux signalée comme une affirmation non confirmée.

Ce corrigé fonctionne parce qu'il compare explicitement la fiabilité des deux sources avant de \
choisir laquelle retenir, plutôt que de prendre l'affirmation la plus dramatique au premier \
degré.
</details>
</details>

## 9. Corrigés très expliqués

**Question :** « Quels enjeux juridique et sociologique peux-tu identifier dans ce dossier, et \
sur quels éléments précis t'appuies-tu ? »

**Corrigé expliqué :** enjeu juridique : filmer un camarade sans son consentement puis diffuser \
la vidéo dans un groupe de 24 élèves pose un problème de droit à l'image (FSE05), \
indépendamment du fait que cela ait fait rire certains élèves. Enjeu sociologique : les messages \
du groupe-classe montrent une norme implicite qui banalise le fait de filmer et de partager \
(Yasmine, Thibault), mais aussi des membres du même groupe qui s'en écartent explicitement \
(Karim, Elena) — comme vu en FSE04, cela montre que l'influence du groupe n'efface jamais les \
positions individuelles. Ces deux enjeux sont distincts : l'un porte sur le droit, l'autre sur \
le fonctionnement social du groupe, et une bonne analyse les traite séparément avant de conclure.

Ce corrigé fonctionne parce qu'il nomme chaque enjeu séparément et l'appuie sur un élément \
précis du dossier, plutôt que de les mélanger dans une impression générale.

## 10. Fiche mémo

- Fait = vérifiable ; interprétation = explication discutable à partir d'un fait ; opinion = \
jugement personnel.
- Avant d'utiliser un document : vérifier auteur, date, contexte, preuves.
- Un document anonyme, non daté et sans preuve est moins fiable qu'un document signé et daté — \
en cas de contradiction, préférer le document le plus fiable.
- Un dossier peut soulever un enjeu juridique (ex. droit à l'image, comportement en ligne) et un \
enjeu sociologique (ex. normes, influence sociale) en même temps : les identifier séparément.
- Une conclusion argumentée s'appuie sur les faits et enjeux identifiés, jamais sur une opinion \
du dossier ni sur son document le moins fiable.
"""
