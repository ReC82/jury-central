"""Contenu de cours — Français FR16→FR20 (ticket #94, PHASE D).

Même structure imposée que les phases A/B/C (`app.v1.francais_fr01_05_courses`,
docstring) : 1. Ce que tu dois savoir faire à l'examen — 2. Théorie progressive —
3. Définitions — 4. Méthode étape par étape — 5. Exemples commentés — 6. Mauvaises réponses
vs bonnes — 7. Pièges — 8. Exercices guidés — 9. Corrigés expliqués — 10. Fiche mémo (reprise
dans « À retenir », ticket #136).

FR20 est le cours de méthode de l'épreuve ET l'examen blanc final : son entraînement et son
évaluation tirent dans les banques FR01→FR19 (voir
`app.v1.session_service._start_francais_transversal_session`), comme MC38 / FSE17. Chaque
notion interrogée par la banque FR16→FR19 (`app.v1.francais_fr16_20_bank`) est enseignée
ici (ticket #83)."""

from app.v1.francais_fr16_20_content import (
    FR16_BAD_TEXT,
    FR16_BAD_TITLE,
    FR16_GOOD_TEXT,
    FR16_GOOD_TITLE,
    FR17_STORY_TEXT,
    FR17_STORY_TITLE,
    FR18_AMPLIFIED_TEXT,
    FR18_AMPLIFIED_TITLE,
    FR18_SCENE_TEXT,
    FR18_SCENE_TITLE,
    FR18_SOURCE_TEXT,
    FR18_SOURCE_TITLE,
    FR19_MODEL_TEXT,
    FR19_MODEL_TITLE,
    FR19_WEAK_TEXT,
    FR19_WEAK_TITLE,
    FR20_CHECKLIST_TEXT,
    FR20_CHECKLIST_TITLE,
    FR20_SUBJECT_TEXT,
    FR20_SUBJECT_TITLE,
)


def fr16_course_markdown() -> str:
    return f"""# Discuter et négocier

## 1. Ce que tu dois savoir faire à l'examen

Tu dois pouvoir participer à une **discussion** ou à une **négociation** (au travail, à \
l'école, dans la vie quotidienne) en écoutant vraiment l'autre, en exprimant clairement \
ce dont tu as besoin, et en cherchant un **accord** acceptable pour les deux parties. À \
l'écrit, on peut te demander d'analyser la transcription d'un échange ou de proposer une \
solution de compromis.

## 2. Théorie progressive

**Étape 1 — Discuter n'est pas se disputer.** Dans une **discussion**, chacun donne son \
avis et écoute celui des autres. Dans une **négociation**, les personnes ont des intérêts \
différents et doivent arriver à une **décision commune**. Dans les deux cas, le but n'est \
pas d'« écraser » l'autre, mais de trouver une issue qui permette de continuer à vivre ou \
à travailler ensemble.

**Étape 2 — Position et besoin.** La **position**, c'est ce que la personne réclame \
(« je veux trois semaines en juillet »). Le **besoin** (ou l'**intérêt**), c'est la raison \
profonde de cette demande (« je dois être en vacances la semaine où ma sœur garde mes \
enfants »). Deux positions peuvent sembler incompatibles alors que les besoins, eux, \
peuvent être satisfaits ensemble. Chercher le besoin caché derrière la position est la \
clé d'une négociation réussie.

**Étape 3 — Les outils de l'échange.**

- L'**écoute active** : laisser l'autre finir, montrer qu'on suit, ne pas préparer sa \
réponse pendant qu'il parle.
- La **reformulation** : redire avec ses mots ce que l'autre a dit (« Si je comprends \
bien, le problème c'est… ») pour vérifier qu'on a compris et montrer qu'on l'écoute.
- La **question ouverte** : une question qui invite à expliquer (« Qu'est-ce qui vous \
gêne exactement ? »), au lieu d'une question fermée qui appelle oui/non.
- Le **message en « je »** : parler de ce qu'on ressent ou de ce dont on a besoin (« J'ai \
du mal à me concentrer avec la musique ») plutôt que d'accuser (« Tu le fais exprès »).

**Étape 4 — Vers l'accord.** On avance par **propositions**, souvent **conditionnelles** \
(« Si je prends du 14 juillet au 3 août, alors je suis présente quand… »). Chacun peut \
faire une **concession** (renoncer à une partie de sa demande). Le **compromis** est un \
accord où chacun cède un peu ; la solution **gagnant-gagnant** satisfait les besoins \
essentiels des deux parties. Enfin, on **récapitule** l'accord pour éviter les malentendus \
(« Donc on note : … »).

**Étape 5 — Ce qui bloque un échange.** Interrompre, généraliser (« vous les jeunes », \
« tout le monde »), attaquer la personne, menacer, ou quitter la discussion sans \
proposition : l'échange se ferme et le problème reste entier.

## 3. Définitions importantes

- **Discussion** : échange d'avis entre plusieurs personnes.
- **Négociation** : échange qui vise une décision commune entre des intérêts différents.
- **Position** : ce que la personne demande ou réclame.
- **Besoin (intérêt)** : la raison profonde qui explique la position.
- **Écoute active** : écouter sans interrompre en montrant qu'on suit et qu'on comprend.
- **Reformulation** : redire avec ses mots ce que l'autre a dit, pour vérifier la \
compréhension.
- **Question ouverte** : question qui invite à expliquer (« pourquoi ? », « comment ? », \
« qu'est-ce que… ? »).
- **Message en « je »** : exprimer son ressenti ou son besoin sans accuser l'autre.
- **Proposition conditionnelle** : offre du type « si…, alors… ».
- **Concession** : renoncement volontaire à une partie de sa demande.
- **Compromis** : accord où chaque partie cède une partie de sa demande.
- **Solution gagnant-gagnant** : accord qui satisfait les besoins essentiels des deux \
parties.

## 4. Méthode étape par étape

1. Prépare-toi : quelle est ta position ? quel est ton besoin réel ? sur quoi peux-tu céder ?
2. Ouvre l'échange calmement, au bon moment (« Vous avez cinq minutes ? »).
3. Expose ta demande clairement, en « je ».
4. Écoute la réponse jusqu'au bout et reformule-la.
5. Pose des questions ouvertes pour découvrir le besoin de l'autre.
6. Fais une proposition qui tient compte des deux besoins (« si…, alors… »).
7. Accepte une concession si elle ne touche pas ton besoin essentiel.
8. Récapitule l'accord et prévois la suite (écrit, date, responsable).

## 5. Exemples commentés

### {FR16_GOOD_TITLE}

{FR16_GOOD_TEXT}

**Analyse commentée :** Amira choisit un moment adapté et expose sa **position** (trois \
semaines en juillet). Face au refus, elle **reformule** le problème de M. Lenoir (« Si je \
comprends bien… ») au lieu d'insister. Elle révèle ensuite son **besoin** réel (la semaine \
du 14 juillet), ce qui ouvre une solution. Sa **proposition conditionnelle** (« Si je \
prends du 14 juillet au 3 août… ») et sa **concession** (deux dimanches en juin) \
satisfont le besoin de M. Lenoir (quatre personnes présentes) : c'est une solution \
**gagnant-gagnant**. Elle termine en **récapitulant** l'accord et en prévoyant un écrit.

### {FR16_BAD_TITLE}

{FR16_BAD_TEXT}

**Analyse commentée :** Bruno ouvre par une **accusation** (« Tu le fais exprès ») au lieu \
d'un message en « je ». Dylan répond par une **généralisation** (« Tout le monde aime \
bien »). Les deux passent aux **attaques personnelles** (« les jeunes… vous ne respectez \
rien », « personne ne mange avec toi »), puis Bruno **menace** d'aller voir le patron. \
Personne ne reformule, personne ne pose de question, aucune proposition n'est faite : le \
problème n'est pas réglé et la relation est abîmée.

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse** : « Ta musique est insupportable, arrête-la. »
- ✅ **Bonne réponse** : « J'ai du mal à me reposer avec la musique pendant le temps de \
midi. Est-ce que tu accepterais de mettre des écouteurs, ou de la mettre plus bas la \
première demi-heure ? »

La bonne réponse exprime un besoin en « je », n'accuse pas et fait une proposition \
concrète que l'autre peut accepter.

## 7. Pièges et erreurs fréquentes

- Confondre la position (ce que l'on réclame) et le besoin (pourquoi on le réclame).
- Répondre avant que l'autre ait terminé.
- Accuser (« tu ») au lieu d'exprimer son besoin (« je »).
- Généraliser (« tout le monde », « vous les jeunes ») ou attaquer la personne.
- Céder sur l'essentiel pour « avoir la paix » : l'accord ne tiendra pas.
- Oublier de récapituler l'accord : chacun repart avec une version différente.

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Essaie avant de regarder la correction</summary>

Dans la négociation des congés, quelle est la position d'Amira au début, et quel est son \
besoin réel ?

<details>
<summary>Voir la correction expliquée</summary>

**Position** : trois semaines de congé du 1er au 21 juillet. **Besoin réel** : être en \
vacances pendant la semaine du 14 juillet, la seule où sa sœur peut garder ses enfants en \
Espagne. Une fois le besoin connu, d'autres dates deviennent possibles : la négociation se \
débloque.
</details>
</details>

<details>
<summary>Exercice 2 — Essaie avant de regarder la correction</summary>

Réécris la première réplique de Bruno (« Ta musique, là, c'est insupportable. Tu le fais \
exprès ou quoi ? ») pour ouvrir une vraie discussion.

<details>
<summary>Voir la correction expliquée</summary>

Exemple : « Dylan, je peux te parler de la salle de pause ? Pendant le temps de midi, j'ai \
besoin de calme pour me reposer, et la musique me gêne. Comment on pourrait faire pour que \
ça aille à tous les deux ? » Bruno choisit le moment, parle de son besoin en « je » et \
termine par une question ouverte qui invite Dylan à proposer une solution.
</details>
</details>

## 9. Corrigés très expliqués

**Question :** pourquoi l'accord entre Amira et M. Lenoir est-il une solution \
gagnant-gagnant et pas seulement un compromis ?

**Corrigé expliqué :** dans un simple compromis, chacun perd un peu : par exemple, Amira \
aurait pu accepter deux semaines au lieu de trois. Ici, les **besoins essentiels** des deux \
parties sont entièrement satisfaits : Amira est en vacances la semaine du 14 juillet et \
garde trois semaines de congé ; M. Lenoir garde au moins quatre personnes tout l'été et \
gagne même deux dimanches de présence en juin. Ce résultat a été possible parce que la \
discussion est passée des **positions** (des dates précises) aux **besoins** (pourquoi ces \
dates).

## 10. Fiche mémo

- Négocier = trouver une décision commune entre des intérêts différents.
- Position (ce qu'on demande) ≠ besoin (pourquoi on le demande) : cherche le besoin.
- Écoute active, reformulation (« si je comprends bien… »), questions ouvertes, message \
en « je ».
- Propositions conditionnelles (« si…, alors… »), concessions, compromis, gagnant-gagnant.
- À éviter : interrompre, accuser, généraliser, attaquer, menacer.
- Toujours récapituler l'accord.
"""


def fr17_course_markdown() -> str:
    return f"""# Comprendre et transformer une œuvre culturelle

## 1. Ce que tu dois savoir faire à l'examen

Face à un récit (nouvelle, extrait de roman, conte), tu dois pouvoir en **comprendre la \
construction** — qui raconte, qui sont les personnages, où et quand se passe l'histoire, \
comment elle progresse — puis le **transformer** de manière cohérente : changer de point \
de vue, écrire une suite, insérer un dialogue, tout en respectant ce que le texte de \
départ a établi.

## 2. Théorie progressive

**Étape 1 — Auteur et narrateur.** L'**auteur** est la personne réelle qui a écrit le \
texte. Le **narrateur** est la voix qui raconte l'histoire. Quand le narrateur est un \
personnage de l'histoire et dit « je », c'est un **narrateur interne** (récit à la \
première personne). Quand il n'est pas un personnage et raconte « il » ou « elle », c'est \
un **narrateur externe** (récit à la troisième personne).

**Étape 2 — Le point de vue.** C'est ce que le narrateur nous laisse voir et savoir :

- **point de vue interne** : on voit l'histoire à travers les yeux et les pensées d'un \
seul personnage (« Son cœur se mit à battre très fort ») ;
- **point de vue externe** : on voit les personnages de l'extérieur, comme une caméra, \
sans connaître leurs pensées ;
- **point de vue omniscient** : le narrateur sait tout, y compris les pensées de \
plusieurs personnages et ce qui se passe ailleurs.

**Étape 3 — Personnages et cadre.** Le **personnage principal** est celui autour duquel \
l'histoire est construite ; les **personnages secondaires** l'aident, le gênent ou \
l'accompagnent. Le **cadre spatio-temporel** est l'ensemble des indications de **lieu** et \
de **temps** (époque, saison, heure).

**Étape 4 — Le schéma narratif.** La plupart des récits suivent cinq étapes :

1. **situation initiale** : présentation des personnages et du cadre, état d'équilibre ;
2. **élément perturbateur** : l'événement qui rompt l'équilibre et lance l'histoire ;
3. **péripéties** : les actions et obstacles qui suivent ;
4. **élément de résolution** (dénouement) : l'événement qui règle le problème ;
5. **situation finale** : le nouvel équilibre, souvent différent du premier.

**Étape 5 — Transformer un récit.** Transformer, c'est **réécrire** une partie du récit en \
changeant un élément précis : le **point de vue** (raconter la même scène par un autre \
personnage), la **suite** (imaginer ce qui se passe après), la **forme** (transformer un \
passage raconté en dialogue). Une transformation réussie respecte la **cohérence** avec \
l'original : mêmes personnages et mêmes caractères, même cadre, mêmes faits déjà \
racontés, même temps de narration (passé simple et imparfait si l'original les utilise).

## 3. Définitions importantes

- **Auteur** : personne réelle qui a écrit le texte.
- **Narrateur** : voix qui raconte l'histoire.
- **Narrateur interne** : narrateur qui est un personnage de l'histoire (« je »).
- **Narrateur externe** : narrateur absent de l'histoire (« il », « elle »).
- **Point de vue interne / externe / omniscient** : ce que le narrateur laisse voir (les \
pensées d'un personnage / seulement l'extérieur / tout).
- **Personnage principal / secondaire** : personnage central / personnage qui l'entoure.
- **Cadre spatio-temporel** : indications de lieu et de temps du récit.
- **Schéma narratif** : situation initiale, élément perturbateur, péripéties, élément de \
résolution, situation finale.
- **Cohérence** : accord de la réécriture avec ce que le texte d'origine a établi.

## 4. Méthode étape par étape

1. Lis le récit une première fois en entier, pour l'histoire.
2. Relève le narrateur (« je » ou « il/elle ») et le point de vue.
3. Note les personnages (principal, secondaires) et un trait de caractère pour chacun.
4. Relève le cadre : lieux, moments, saison, heure.
5. Découpe le récit selon le schéma narratif en cinq étapes.
6. Pour une transformation : souligne dans la consigne ce qui change (point de vue, \
suite, dialogue) et ce qui doit rester (personnages, cadre, faits).
7. Réécris en gardant les temps du récit et la cohérence.
8. Relis en vérifiant qu'aucun fait de l'original n'est contredit.

## 5. Exemples commentés

### {FR17_STORY_TITLE}

{FR17_STORY_TEXT}

**Analyse commentée :** le récit est raconté par un **narrateur externe** (« Maëlle… \
elle ») en **point de vue interne** : on connaît les sensations de Maëlle (« la gorge \
serrée », « Son cœur se mit à battre très fort »), jamais les pensées de Monsieur Ferreira. \
**Personnage principal** : Maëlle ; **secondaires** : Monsieur Ferreira, la mère. **Cadre** : \
Charleroi, un soir pluvieux de novembre, vers 21 h 40, puis la route des entrepôts. \
**Schéma narratif** : situation initiale (Maëlle sort du basket, compte prendre le bus) ; \
élément perturbateur (elle rate le dernier bus et son téléphone s'éteint) ; péripéties \
(elle marche, une camionnette ralentit, elle hésite, fait appeler sa mère) ; élément de \
résolution (sa mère accepte, Monsieur Ferreira la ramène) ; situation finale (retrouvailles, \
biscuits offerts, batterie de secours).

## 6. Mauvaises réponses comparées aux bonnes

Consigne : « Raconte la scène de la camionnette du point de vue de Monsieur Ferreira. »

- ❌ **Mauvaise réponse** : « Je m'appelle Maëlle, j'ai eu très peur quand la camionnette \
s'est arrêtée. » → c'est encore le point de vue de Maëlle.
- ❌ **Mauvaise réponse** : « Monsieur Ferreira roulait en moto quand il vit Maëlle en plein \
jour. » → incohérent : c'est une camionnette blanche, et il fait nuit.
- ✅ **Bonne réponse** : « En rentrant de sa livraison, Monsieur Ferreira aperçut, dans la \
lumière des phares, une silhouette trempée qui marchait le long des entrepôts. Il ralentit : \
il connaissait ce sac de basket. "La petite Maëlle, toute seule ici à cette heure ?" \
pensa-t-il, inquiet. »

## 7. Pièges et erreurs fréquentes

- Confondre l'auteur et le narrateur.
- Croire qu'un récit en « il » ne peut pas avoir de point de vue interne.
- Oublier l'élément perturbateur, ou le confondre avec la première péripétie.
- Changer le caractère d'un personnage dans une suite (un personnage prudent devient \
imprudent sans raison).
- Changer de temps en cours de réécriture (passer du passé simple au présent).
- Contredire un fait du texte d'origine (lieu, heure, objet, relation entre personnages).

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Essaie avant de regarder la correction</summary>

Dans « Le dernier bus », quel est l'élément perturbateur ? Justifie.

<details>
<summary>Voir la correction expliquée</summary>

L'élément perturbateur est le moment où Maëlle **rate le dernier bus** (et où son \
téléphone s'éteint). C'est lui qui rompt l'équilibre de départ (elle comptait rentrer en \
bus, comme tous les mardis) et qui déclenche toute la suite : la marche sous la pluie, la \
rencontre, le trajet.
</details>
</details>

<details>
<summary>Exercice 2 — Essaie avant de regarder la correction</summary>

Transforme en dialogue de quatre répliques le passage où Monsieur Ferreira raconte son \
dernier train raté à Porto.

<details>
<summary>Voir la correction expliquée</summary>

Exemple :
— Tu sais, à ton âge, moi aussi j'ai raté un dernier train, dit Monsieur Ferreira.
— Ah bon ? Où ça ? demanda Maëlle.
— À Porto. J'ai dormi sur un banc de la gare, avec mon sac comme oreiller !
— Sérieusement ? répondit Maëlle en éclatant de rire.

Le dialogue garde les faits (Porto, banc de la gare), le caractère bienveillant du boulanger \
et la conséquence du récit (Maëlle rit pour la première fois de la soirée).
</details>
</details>

## 9. Corrigés très expliqués

**Question :** pourquoi peut-on dire que « Le dernier bus » est raconté en point de vue \
interne alors que le narrateur dit « elle » ?

**Corrigé expliqué :** le pronom indique seulement que le narrateur est **externe** (il \
n'est pas un personnage). Le **point de vue**, lui, dépend de ce que le texte nous laisse \
savoir. Ici, nous connaissons les sensations et les émotions de Maëlle (« la gorge \
serrée », son cœur qui bat, son hésitation à monter), mais jamais ce que pensent Monsieur \
Ferreira ou la mère : nous vivons la scène à travers Maëlle. C'est donc un narrateur externe \
qui adopte le point de vue interne de Maëlle.

## 10. Fiche mémo

- Auteur (personne réelle) ≠ narrateur (voix qui raconte) : interne « je » / externe « il ».
- Point de vue : interne (un personnage), externe (caméra), omniscient (tout).
- Personnages principal et secondaires ; cadre = lieu + temps.
- Schéma narratif : situation initiale → élément perturbateur → péripéties → résolution → \
situation finale.
- Transformer = changer UN élément (point de vue, suite, forme) en gardant la cohérence.
"""


def fr18_course_markdown() -> str:
    return f"""# Amplifier, recomposer et transposer

## 1. Ce que tu dois savoir faire à l'examen

À partir d'un texte court, tu dois pouvoir le **réécrire** selon une technique précise : \
l'**amplifier** (le développer), le **recomposer** (changer l'ordre du récit) ou le \
**transposer** (changer de genre, de point de vue, d'époque ou de registre), en gardant \
toujours les **éléments essentiels** du texte de départ.

## 2. Théorie progressive

**Étape 1 — Repérer les éléments essentiels.** Avant toute réécriture, on relève ce qui \
ne doit pas changer : les personnages, l'événement principal, le lieu, le moment, la fin. \
Pour un fait divers, on peut s'aider des questions **qui ? quoi ? où ? quand ? comment ? \
pourquoi ?**

**Étape 2 — Amplifier.** Amplifier, c'est **développer** un texte sans changer son \
histoire, en ajoutant :

- des **descriptions** (lieu, objets, atmosphère) ;
- un **portrait** (aspect physique, caractère d'un personnage) ;
- des **paroles rapportées** (dialogue, discours direct) ;
- des **pensées et émotions** des personnages ;
- des **précisions** grâce aux adjectifs, compléments et comparaisons.

Les ajouts doivent rester **vraisemblables** et **cohérents** avec le texte source.

**Étape 3 — Recomposer.** Recomposer, c'est **changer l'ordre** dans lequel les \
événements sont racontés, sans changer les événements eux-mêmes :

- commencer **au milieu de l'action** (*in medias res*) ;
- commencer par la **fin**, puis revenir en arrière ;
- insérer un **retour en arrière** (souvenir d'un événement passé, aussi appelé \
*analepse*).

Les indicateurs de temps (« trois jours plus tôt », « ce matin-là ») et les temps des \
verbes (plus-que-parfait pour le passé du passé) guident le lecteur.

**Étape 4 — Transposer.** Transposer, c'est **faire passer** un texte dans un autre \
cadre ou une autre forme :

- changer de **genre** : récit → scène de théâtre (répliques précédées du nom du \
personnage, **didascalies** en italique ou entre parenthèses qui indiquent le décor, les \
gestes et le ton) ; récit → article de presse (titre, **chapeau** qui répond à qui / quoi / \
où / quand, ton neutre, troisième personne) ;
- changer de **point de vue** (un autre personnage raconte) ;
- changer d'**époque** ou de **lieu** (la même histoire au Moyen Âge, dans le futur) ;
- changer de **registre** (version humoristique, dramatique).

## 3. Définitions importantes

- **Réécriture** : nouveau texte produit à partir d'un texte source selon une consigne.
- **Éléments essentiels** : personnages, événement principal, lieu, moment et fin qui \
doivent être conservés.
- **Amplification** : développement d'un texte par ajouts (description, portrait, \
dialogue, pensées, précisions).
- **Recomposition** : modification de l'ordre de la narration.
- ***In medias res*** : début du récit au milieu de l'action.
- **Retour en arrière (analepse)** : évocation d'un événement antérieur au moment raconté.
- **Transposition** : passage d'un texte dans un autre genre, point de vue, époque, lieu \
ou registre.
- **Didascalie** : indication de mise en scène dans un texte de théâtre (décor, gestes, ton).
- **Réplique** : partie de dialogue prononcée par un personnage de théâtre.
- **Chapeau** : court paragraphe sous le titre d'un article qui résume l'essentiel.

## 4. Méthode étape par étape

1. Lis la consigne : quelle technique (amplifier, recomposer, transposer) ? quelle \
longueur ?
2. Relève les éléments essentiels du texte source (qui, quoi, où, quand, comment).
3. Prépare au brouillon ce que tu vas ajouter, déplacer ou transformer.
4. Choisis les codes du genre visé (répliques et didascalies, titre et chapeau…).
5. Rédige en gardant un temps de narration cohérent.
6. Relis en vérifiant que tous les éléments essentiels sont présents et qu'aucun ajout ne \
contredit le texte source.

## 5. Exemples commentés

### {FR18_SOURCE_TITLE}

{FR18_SOURCE_TEXT}

**Éléments essentiels :** qui (Pilou, Arnaud Collard, 68 ans, des bénévoles) ; quoi (le \
chien perdu revient seul) ; où (Durbuy, la maison du maître, la forêt) ; quand (lundi, \
après trois jours) ; état (épuisé, en bonne santé).

### {FR18_AMPLIFIED_TITLE}

{FR18_AMPLIFIED_TEXT}

**Analyse commentée :** l'histoire est la même, mais le texte est **amplifié** par des \
**pensées** (« Je n'aurais jamais dû le lâcher… »), une **description** (le chien couvert \
de boue, les pattes en sang), des **paroles** (« Pilou ! »), des émotions (la voix cassée) \
et une suite vraisemblable (la tarte avec les bénévoles). Tous les éléments essentiels \
sont conservés.

### {FR18_SCENE_TITLE}

{FR18_SCENE_TEXT}

**Analyse commentée :** le récit est **transposé** en scène de théâtre : le décor et les \
gestes passent dans les **didascalies** (« La cuisine d'Arnaud… », « s'agenouillant, la voix \
tremblante »), l'histoire avance uniquement par les **répliques** et les bruits (le \
grattement). Le narrateur a disparu, comme dans tout texte de théâtre.

## 6. Mauvaises réponses comparées aux bonnes

Consigne : « Recompose le fait divers en commençant par la fin. »

- ❌ **Mauvaise réponse** : « Lundi, à Durbuy, un chien nommé Pilou s'est perdu en forêt… » \
→ l'ordre est inchangé.
- ❌ **Mauvaise réponse** : « Pilou est mort de fatigue sur le paillasson. » → change \
l'événement essentiel (le chien est en bonne santé).
- ✅ **Bonne réponse** : « Ce lundi matin, Arnaud Collard a ouvert sa porte sur un chien \
épuisé et couvert de boue : son Pilou, enfin rentré. Trois jours plus tôt, l'animal avait \
disparu pendant une promenade dans la forêt de Durbuy… »

## 7. Pièges et erreurs fréquentes

- Changer l'histoire au lieu de la réécrire (nouvelle fin, nouveaux personnages sans \
raison).
- Amplifier par des ajouts invraisemblables ou contradictoires.
- Recomposer sans indicateurs de temps : le lecteur se perd.
- Transposer en théâtre en gardant un narrateur (« Arnaud pensa que… ») au lieu de \
didascalies et de répliques.
- Transposer en article de presse en gardant des pensées intimes et des émotions \
inventées : un article reste factuel.
- Oublier un élément essentiel du texte source.

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Essaie avant de regarder la correction</summary>

Quels éléments ajoutés dans la version amplifiée du retour de Pilou relèvent des pensées \
ou des émotions d'un personnage ?

<details>
<summary>Voir la correction expliquée</summary>

« Arnaud buvait son café sans appétit », « n'osait plus la regarder », « "Je n'aurais \
jamais dû le lâcher dans la forêt", se répétait-il », « d'une voix cassée ». Ces ajouts \
font vivre la tristesse puis la joie du maître sans changer aucun fait du texte source.
</details>
</details>

<details>
<summary>Exercice 2 — Essaie avant de regarder la correction</summary>

Rédige un titre et un chapeau pour transposer le texte amplifié en article de presse.

<details>
<summary>Voir la correction expliquée</summary>

Exemple : **Titre** : « Durbuy : perdu depuis trois jours, Pilou retrouve seul sa maison ». \
**Chapeau** : « Lundi matin, le chien d'Arnaud Collard, 68 ans, disparu pendant une \
promenade en forêt, est rentré seul chez son maître. Épuisé mais en bonne santé, il avait \
été cherché tout le week-end par des bénévoles. » Le chapeau répond à qui, quoi, où, quand, \
sur un ton neutre, sans les pensées d'Arnaud.
</details>
</details>

## 9. Corrigés très expliqués

**Question :** quelle différence y a-t-il entre amplifier et transposer le fait divers de \
Pilou ?

**Corrigé expliqué :** **amplifier**, c'est garder le même genre (un récit) et le même \
ordre, mais **développer** le texte avec des descriptions, des paroles, des pensées : il \
devient plus long et plus vivant. **Transposer**, c'est **changer de cadre ou de forme** : \
par exemple faire du récit une scène de théâtre, où tout passe par les répliques et les \
didascalies. Dans les deux cas, les éléments essentiels (Pilou, Arnaud, Durbuy, lundi, le \
retour après trois jours, le chien en bonne santé) sont conservés.

## 10. Fiche mémo

- Toujours relever d'abord les éléments essentiels (qui, quoi, où, quand, comment).
- Amplifier = ajouter description, portrait, dialogue, pensées, précisions.
- Recomposer = changer l'ordre (*in medias res*, fin d'abord, retour en arrière) avec des \
indicateurs de temps.
- Transposer = changer de genre (théâtre : répliques + didascalies ; presse : titre + \
chapeau, ton neutre), de point de vue, d'époque, de lieu ou de registre.
- Ne jamais contredire le texte source.
"""


def fr19_course_markdown() -> str:
    return f"""# Relater une expérience culturelle et motiver son appréciation

## 1. Ce que tu dois savoir faire à l'examen

Tu dois pouvoir **relater** une expérience culturelle (une exposition, un film, un \
concert, une pièce de théâtre, un livre) de façon claire et précise, puis donner une \
**appréciation motivée** : dire ce que tu en penses en le **justifiant** par des critères \
et des exemples précis, sans te contenter de « j'ai aimé » ou « c'était nul ».

## 2. Théorie progressive

**Étape 1 — Relater.** Relater, c'est **raconter** l'expérience pour quelqu'un qui n'y \
était pas. On commence par la **situation** : *quoi* (titre, genre, artiste ou \
compagnie), *où*, *quand*, *avec qui*. On présente ensuite le **contenu** (l'histoire en \
quelques phrases, les thèmes, le déroulement de la visite) sans tout dévoiler.

**Étape 2 — Distinguer goût personnel et appréciation motivée.** « J'aime » ou « je \
n'aime pas » exprime un **goût personnel** : on ne peut pas le discuter, mais il ne \
convainc personne. Une **appréciation motivée** s'appuie sur des **critères** et des \
**exemples précis** que le lecteur peut vérifier.

**Étape 3 — Les critères d'appréciation.** Selon l'œuvre :

- l'**histoire** ou le **thème** (originalité, intérêt, message) ;
- l'**interprétation** (jeu des acteurs, voix du chanteur) ;
- la **mise en scène** ou la **scénographie** (décor, lumière, musique, organisation \
d'une exposition) ;
- l'**émotion** ressentie (rire, émotion, réflexion) et ce qui la provoque ;
- l'**accessibilité** (durée, clarté, public visé).

Chaque critère est illustré par un **exemple précis** (une scène, un objet, un moment).

**Étape 4 — Nuancer.** Une appréciation crédible reconnaît les points forts **et** les \
limites. On utilise un **vocabulaire appréciatif** précis : **mélioratif** (« émouvant », \
« original », « maîtrisé ») ou **péjoratif** (« lent », « confus », « répétitif »), et des \
**modalisateurs** qui nuancent (« un peu », « assez », « particulièrement », « malgré »). On \
évite les superlatifs vides (« le meilleur de ma vie », « trop bien »).

**Étape 5 — Conclure par une recommandation.** On termine par un **bilan** et une \
**recommandation** adaptée au destinataire : à qui conseiller cette œuvre, et pourquoi.

## 3. Définitions importantes

- **Relater** : raconter une expérience avec précision pour quelqu'un qui ne l'a pas vécue.
- **Compte rendu** : texte qui relate une expérience et en donne une appréciation.
- **Goût personnel** : préférence subjective (« j'aime »), non justifiée.
- **Appréciation motivée** : jugement justifié par des critères et des exemples précis.
- **Critère** : point de vue à partir duquel on juge (histoire, interprétation, mise en \
scène, émotion, accessibilité).
- **Vocabulaire mélioratif / péjoratif** : mots qui présentent quelque chose de façon \
positive / négative.
- **Modalisateur** : mot qui nuance un jugement (« assez », « un peu », « particulièrement »).
- **Recommandation** : conseil adressé au lecteur, avec le public visé.

## 4. Méthode étape par étape

1. Note la situation : quoi, où, quand, avec qui.
2. Résume le contenu en trois ou quatre phrases (sans dévoiler la fin d'une histoire).
3. Choisis deux ou trois critères adaptés à l'œuvre.
4. Pour chaque critère : un jugement précis + un exemple concret.
5. Ajoute au moins une limite, formulée avec nuance.
6. Termine par un bilan et une recommandation (à qui ? pourquoi ?).
7. Relis : remplace les mots vagues (« bien », « nul », « trop ») par du vocabulaire précis.

## 5. Exemples commentés

### {FR19_MODEL_TITLE}

{FR19_MODEL_TEXT}

**Analyse commentée :** le premier paragraphe **relate la situation** (samedi dernier, avec \
la classe, au musée de la Vie wallonne, à Liège) et le deuxième le **déroulement** de la \
visite. L'**appréciation** est annoncée (« pour trois raisons ») et organisée par \
**critères** : l'interactivité (exemple : raboter une planche), le lien passé-présent \
(exemple : le forgeron à côté du réparateur de smartphones), la rencontre avec l'artisan \
(exemple : son changement de métier à 35 ans). Une **limite** est formulée avec nuance \
(« Je regrette seulement… Malgré ce défaut »). La fin est une **recommandation** ciblée \
(« à tous ceux qui hésitent sur leur orientation »).

### {FR19_WEAK_TITLE}

{FR19_WEAK_TEXT}

**Analyse commentée :** rien n'est **relaté** (où ? quand ? quel style de musique ?). Le \
jugement n'exprime qu'un **goût personnel** avec des superlatifs vides (« le meilleur \
concert de ma vie », « tout était parfait »), sans aucun critère ni exemple. La phrase \
« Ceux qui n'aiment pas sont nuls » attaque les lecteurs au lieu de les convaincre.

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse** : « Les acteurs jouaient trop bien. »
- ✅ **Bonne réponse** : « L'actrice qui joue l'infirmière est particulièrement juste : on \
sent sa fatigue dans sa voix lente et ses gestes lourds dès la première scène. »

La bonne réponse précise le critère (le jeu d'une actrice), formule un jugement nuancé \
(« particulièrement juste ») et donne un exemple vérifiable.

## 7. Pièges et erreurs fréquentes

- Raconter toute l'histoire, y compris la fin, sans donner d'avis.
- Donner un avis sans rien relater : le lecteur ne sait pas de quoi on parle.
- Confondre goût personnel (« j'adore ») et appréciation motivée.
- Utiliser des mots vagues ou des superlatifs (« trop bien », « nul », « parfait »).
- Ne citer aucun exemple précis.
- Oublier les limites : un avis totalement positif ou négatif paraît peu crédible.
- Oublier la recommandation finale.

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Essaie avant de regarder la correction</summary>

Dans le compte rendu de l'exposition « Mains d'artisans », relève la limite mentionnée et \
le mot qui introduit la nuance.

<details>
<summary>Voir la correction expliquée</summary>

La limite : les textes des panneaux sont écrits en très petits caractères et parfois trop \
longs. La nuance est introduite par « Je regrette **seulement** » puis « **Malgré** ce \
défaut » : l'auteur montre que ce défaut est réel mais secondaire par rapport aux qualités \
de l'exposition.
</details>
</details>

<details>
<summary>Exercice 2 — Essaie avant de regarder la correction</summary>

Transforme « Tout était parfait » (avis sur le concert de Nova Lys) en une appréciation \
motivée d'une ou deux phrases. Tu peux inventer un détail vraisemblable du concert.

<details>
<summary>Voir la correction expliquée</summary>

Exemple : « La chanteuse a une voix puissante mais capable de devenir très douce : lors de \
la ballade chantée seule au piano, toute la salle s'est tue. » Le critère (la voix), le \
jugement nuancé et l'exemple précis remplacent le superlatif vide.
</details>
</details>

## 9. Corrigés très expliqués

**Question :** pourquoi « J'ai adoré, c'était le meilleur concert de ma vie » ne suffit-il \
pas comme appréciation dans un compte rendu ?

**Corrigé expliqué :** cette phrase exprime seulement un **goût personnel** : elle dit ce \
que l'auteur a ressenti, mais pas **pourquoi**. Le lecteur ne peut ni vérifier ni partager \
ce jugement, car aucun **critère** (voix, musiciens, ambiance, mise en scène) et aucun \
**exemple** précis ne sont donnés. Le superlatif « le meilleur de ma vie » ne renseigne \
pas sur le concert lui-même. Pour devenir une appréciation motivée, l'avis doit choisir des \
critères, donner un exemple pour chacun et nuancer.

## 10. Fiche mémo

- Relater : quoi, où, quand, avec qui, puis le contenu (sans tout dévoiler).
- Goût personnel (« j'aime ») ≠ appréciation motivée (critère + exemple précis).
- Critères : histoire/thème, interprétation, mise en scène, émotion, accessibilité.
- Nuancer : vocabulaire mélioratif/péjoratif précis, modalisateurs, au moins une limite.
- Conclure par un bilan et une recommandation adaptée au destinataire.
"""


def fr20_course_markdown() -> str:
    return f"""# Méthodologie complète de l'épreuve et examen final

## 1. Ce que tu dois savoir faire à l'examen

Tu dois pouvoir aborder une épreuve complète de français avec **méthode** : comprendre ce \
que chaque tâche demande, **répartir ton temps**, utiliser un **brouillon** efficace, \
mobiliser la bonne méthode pour chaque type de tâche (compréhension, réduction, synthèse, \
argumentation, réécriture) et **relire** avec une grille. Ce cours rassemble les méthodes \
des cours FR01 à FR19 ; l'entraînement et l'évaluation de ce cours sont un **examen blanc** \
qui mélange des questions de tous ces cours.

L'organisation exacte de ton épreuve (durée, nombre de documents, barème, partie orale \
éventuelle) t'est communiquée par ton établissement ou ton jury : vérifie-la toujours avant \
le jour J.

## 2. Théorie progressive

**Étape 1 — Lire tout le sujet avant de commencer.** On lit d'abord **toutes les tâches** \
et le **barème** : on sait ainsi ce qui rapporte le plus de points et quels documents \
serviront à quoi. On souligne les **verbes de consigne** (relève, explique, justifie, \
résume, compare, rédige — voir « Comprendre une consigne d'examen ») et les **contraintes** \
(nombre de mots, destinataire, genre).

**Étape 2 — Répartir son temps selon les points.** Le temps se répartit à peu près selon \
le barème, en gardant une réserve pour la relecture. Pour une épreuve de trois heures \
notée sur 20, par exemple : 15 minutes de lecture du sujet et des documents, un temps par \
tâche proportionnel à ses points, et 15 minutes de relecture finale. On note les heures de \
fin prévues dans la marge et on s'y tient : une tâche non commencée rapporte zéro.

**Étape 3 — Le brouillon utile.** Le brouillon sert à **préparer**, pas à tout recopier : \
mots-clés, tableau de tri des documents (pour / contre / nuance), plan du texte \
argumentatif, idées principales d'un résumé. Seul le texte argumentatif peut justifier une \
rédaction partielle au brouillon (introduction et conclusion), si le temps le permet.

**Étape 4 — Une méthode par type de tâche.**

| Tâche | Méthode à mobiliser | Cours |
|---|---|---|
| Comprendre une consigne | verbe + objet + contraintes | FR01 |
| Comprendre un document, inférer | idée principale, indices, justification par le texte | FR02, FR03 |
| Écrire et corriger | phrase correcte, organisation, relecture ciblée | FR04, FR05 |
| Rechercher, évaluer une source | pertinence, fiabilité, recoupement | FR06, FR07 |
| Réduire, résumer, synthétiser | reformuler, hiérarchiser, plan thématique | FR08, FR09 |
| Argumenter | thèse, argument développé, texte structuré, dossier | FR10 à FR13 |
| Écrits fonctionnels et oral | réclamation, oral, négociation | FR14 à FR16 |
| Œuvres culturelles | comprendre, transformer, réécrire, apprécier | FR17 à FR19 |

**Étape 5 — Relire avec une grille.** La relecture finale se fait **en plusieurs passages \
ciblés** (consigne, contenu, langue, présentation) plutôt qu'en une lecture rapide : on \
repère beaucoup plus d'erreurs en cherchant une seule chose à la fois.

**Étape 6 — Gérer le stress et l'imprévu.** Si une question bloque, on note le numéro, on \
passe à la suivante et on y revient à la fin. Une réponse partielle mais juste rapporte \
souvent des points ; une page blanche n'en rapporte jamais.

## 3. Définitions importantes

- **Barème** : répartition des points entre les tâches de l'épreuve.
- **Verbe de consigne** : verbe qui indique l'action attendue (relever, expliquer, \
justifier, résumer, comparer, rédiger).
- **Contrainte** : exigence imposée par la consigne (longueur, destinataire, genre, \
documents à utiliser).
- **Brouillon** : espace de préparation (mots-clés, plan, tri des documents).
- **Gestion du temps** : répartition du temps disponible selon les points et les tâches.
- **Grille de relecture** : liste de vérifications faites en plusieurs passages ciblés.
- **Examen blanc** : épreuve d'entraînement complète, dans les conditions de l'examen.

## 4. Méthode étape par étape

1. Lis le sujet en entier : tâches, documents, barème.
2. Souligne les verbes de consigne et les contraintes de chaque tâche.
3. Note dans la marge l'heure de fin prévue pour chaque tâche.
4. Commence par la tâche que tu maîtrises le mieux, ou suis l'ordre du sujet.
5. Pour chaque tâche, prépare au brouillon avec la méthode du cours correspondant.
6. Rédige directement au propre les réponses courtes ; le texte long après un plan.
7. Si tu bloques, passe et reviens-y à la fin.
8. Garde 15 minutes pour la relecture avec la grille.
9. Vérifie que chaque tâche a une réponse et que ton nom figure sur chaque feuille.

## 5. Exemples commentés

### {FR20_SUBJECT_TITLE}

{FR20_SUBJECT_TEXT}

**Analyse commentée :** la tâche 3 rapporte la moitié des points : elle mérite environ la \
moitié du temps de travail. La tâche 1 contient **deux** consignes (un problème à \
identifier, deux compétences à relever) : une réponse qui en oublie une perd des points. \
La tâche 2 impose une **réduction** (25 mots maximum) : on reformule les chiffres \
principaux sans avis personnel. Pour la tâche 3, on trie les documents au brouillon : le \
document 1 (besoin de bénévoles) et le document 2 (compétences acquises) soutiennent la \
thèse ; le document 3 fournit des données et une objection (le manque de temps), à traiter \
par une concession.

### {FR20_CHECKLIST_TITLE}

{FR20_CHECKLIST_TEXT}

**Analyse commentée :** la grille se lit **ligne par ligne**, en relisant la copie pour une \
seule vérification à la fois. C'est plus long qu'une lecture rapide, mais c'est la méthode \
qui permet réellement de corriger les erreurs d'accord et d'homophones les plus fréquentes.

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise gestion** : passer deux heures sur la tâche de compréhension (6 points) \
et rédiger l'argumentation (10 points) en vingt minutes.
- ✅ **Bonne gestion** : répartir le temps selon le barème, noter les heures de fin dans la \
marge et garder 15 minutes pour la relecture.

- ❌ **Mauvaise réponse à la tâche 2** : « Je pense que les jeunes devraient faire plus de \
bénévolat parce que c'est important. » → avis personnel, aucune donnée du document 3.
- ✅ **Bonne réponse** : « Selon une enquête, près d'un jeune sur trois fait du bénévolat ; \
les autres invoquent surtout le manque de temps ou d'information. » (21 mots)

## 7. Pièges et erreurs fréquentes

- Commencer à écrire sans avoir lu tout le sujet.
- Répondre à une seule partie d'une consigne double.
- Ignorer le barème et manquer de temps pour la tâche la plus importante.
- Tout rédiger au brouillon puis manquer de temps pour recopier.
- Laisser une tâche blanche au lieu de donner une réponse partielle.
- Supprimer la relecture finale « pour gagner du temps ».

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Essaie avant de regarder la correction</summary>

Pour le sujet complet d'entraînement, l'épreuve dure 2 h 30. Propose une répartition du \
temps.

<details>
<summary>Voir la correction expliquée</summary>

Exemple : 15 minutes de lecture du sujet et des documents ; 30 minutes pour la tâche 1 \
(6 points) ; 20 minutes pour la tâche 2 (4 points) ; 1 h 10 pour la tâche 3 (10 points : \
tri des documents, plan, rédaction) ; 15 minutes de relecture avec la grille. Le temps \
suit le barème, et la relecture est prévue dès le départ.
</details>
</details>

<details>
<summary>Exercice 2 — Essaie avant de regarder la correction</summary>

Dans la tâche 1 du sujet, combien de réponses différentes sont attendues ?

<details>
<summary>Voir la correction expliquée</summary>

Trois éléments : **un** problème rencontré par l'épicerie (le manque de bénévoles jeunes, \
leur moyenne d'âge dépassant 60 ans) et **deux** compétences acquises par Lina (parler \
devant un groupe, gérer les conflits). Compter les éléments attendus avant de répondre \
évite d'en oublier un.
</details>
</details>

## 9. Corrigés très expliqués

**Question :** pourquoi relire en plusieurs passages ciblés plutôt qu'en une seule lecture ?

**Corrigé expliqué :** en relisant une seule fois, on lit surtout le **sens** de son texte : \
le cerveau corrige automatiquement les fautes qu'il s'attend à ne pas voir. En relisant \
pour **une seule chose à la fois** — d'abord la consigne (ai-je tout fait ?), puis le \
contenu (sources, thèse), puis la langue (accords, homophones), puis la présentation — \
l'attention se concentre sur chaque type d'erreur. C'est pourquoi la grille de relecture \
est organisée en rubriques et doit être suivie ligne par ligne.

## 10. Fiche mémo

- Lire TOUT le sujet (tâches, documents, barème) avant d'écrire.
- Verbes de consigne et contraintes soulignés ; consignes doubles repérées.
- Temps réparti selon les points, heures de fin dans la marge, 15 minutes de relecture.
- Brouillon = mots-clés, tri des documents, plan — pas un texte à recopier.
- Une méthode par tâche (voir le tableau des cours FR01→FR19).
- Bloqué ? Passe et reviens ; jamais de page blanche.
- Relecture en passages ciblés avec la grille.
"""
