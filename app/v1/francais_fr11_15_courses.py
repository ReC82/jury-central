"""Contenu de cours — Français FR11→FR15 (ticket #94, PHASE C).

Même structure imposée que PHASE A/B (`app.v1.francais_fr01_05_courses`, docstring) :
1. Ce que tu dois savoir faire à l'examen — 2. Théorie progressive — 3. Définitions —
4. Méthode étape par étape — 5. Exemples commentés — 6. Mauvaises réponses vs bonnes —
7. Pièges — 8. Exercices guidés — 9. Corrigés expliqués — 10. Fiche mémo (reprise dans la
séquence finale « À retenir », ticket #136). S'entraîner / S'évaluer sont fournis
génériquement par `_uaa_space_nav.html` (ticket #22).

Chaque notion interrogée par la banque (`app.v1.francais_fr11_15_bank`) est enseignée ici
(ticket #83 : jamais une question sur une notion absente du cours)."""

from app.v1.francais_fr11_15_content import (
    FR11_MODEL_TEXT,
    FR11_MODEL_TITLE,
    FR11_WEAK_TEXT,
    FR11_WEAK_TITLE,
    FR12_INTROS_TEXT,
    FR12_INTROS_TITLE,
    FR12_MODEL_TEXT,
    FR12_MODEL_TITLE,
    FR13_DOC1_TEXT,
    FR13_DOC1_TITLE,
    FR13_DOC2_TEXT,
    FR13_DOC2_TITLE,
    FR13_DOC3_TEXT,
    FR13_DOC3_TITLE,
    FR14_BAD_TEXT,
    FR14_BAD_TITLE,
    FR14_GOOD_TEXT,
    FR14_GOOD_TITLE,
    FR14_SITUATION_TEXT,
    FR14_SITUATION_TITLE,
    FR15_TRANSCRIPT_A_TEXT,
    FR15_TRANSCRIPT_A_TITLE,
    FR15_TRANSCRIPT_B_TEXT,
    FR15_TRANSCRIPT_B_TITLE,
)


def fr11_course_markdown() -> str:
    return f"""# Construire un argument développé

## 1. Ce que tu dois savoir faire à l'examen

Tu dois pouvoir transformer une simple idée (« c'est bien », « c'est mauvais ») en un \
**argument développé** : une idée annoncée clairement, expliquée, appuyée par un exemple ou \
une preuve, puis reliée à la thèse que tu défends. Tu dois aussi savoir enchaîner tes idées \
avec des **connecteurs logiques** adaptés et tenir compte d'une objection.

## 2. Théorie progressive

**Étape 1 — De l'opinion à l'argument.** Dire « je suis pour » est une **opinion** : cela \
indique ta position, mais ne convainc personne. Un **argument** est la *raison* qui \
justifie cette position (« parce que cela fait économiser de l'argent aux travailleurs »). \
Le lecteur ne te croit pas sur parole : il faut lui montrer pourquoi ta raison est valable.

**Étape 2 — Les quatre éléments d'un argument développé.** Un argument complet tient en \
un paragraphe et contient, dans cet ordre :

1. l'**idée annoncée** (une phrase claire qui dit l'argument) ;
2. l'**explication** (le mécanisme : *comment* et *pourquoi* cette idée est vraie) ;
3. l'**exemple** ou la **preuve** (un cas concret, un chiffre, un témoignage, un fait \
vérifiable) ;
4. le **lien avec la thèse** (une phrase de conclusion du paragraphe qui rappelle ce que \
l'argument prouve).

Un paragraphe qui s'arrête à l'idée annoncée est une **affirmation gratuite**. Un \
paragraphe qui ne contient qu'un exemple est une **anecdote** : un cas isolé ne prouve pas \
une règle générale.

**Étape 3 — Les connecteurs logiques.** Ils montrent au lecteur la relation entre tes \
idées. Les principaux :

| Relation | Connecteurs |
|---|---|
| Addition, progression | d'abord, ensuite, de plus, en outre, enfin |
| Cause | car, parce que, en effet, puisque, étant donné que |
| Conséquence | donc, ainsi, c'est pourquoi, par conséquent |
| Opposition | mais, pourtant, cependant, au contraire |
| Concession | certes… mais, bien que, même si |
| Illustration | par exemple, ainsi, notamment, comme le montre |
| Conclusion | en somme, pour toutes ces raisons, finalement |

**Étape 4 — Tenir compte d'une objection.** Un argument est plus fort quand il anticipe ce \
que l'adversaire pourrait répondre. Deux façons de traiter une **objection** : la \
**réfutation** (montrer que l'objection est fausse ou exagérée) et la **concession** \
(reconnaître une part de vérité à l'objection, puis montrer que ton argument reste plus \
important : « Certes…, mais… »).

## 3. Définitions importantes

- **Opinion** : position personnelle sur une question (pour, contre, nuancé).
- **Thèse** : opinion défendue dans tout un texte.
- **Argument** : raison qui justifie la thèse.
- **Argument développé** : idée annoncée + explication + exemple ou preuve + lien avec la \
thèse, en un paragraphe.
- **Explication** : partie de l'argument qui montre le mécanisme, le « pourquoi ».
- **Exemple** : cas particulier concret qui illustre l'argument.
- **Preuve** : donnée vérifiable (chiffre, étude, fait daté, source identifiée).
- **Affirmation gratuite** : idée lancée sans explication ni exemple.
- **Connecteur logique** : mot ou expression qui indique la relation entre deux idées.
- **Objection** : argument possible de la position adverse.
- **Réfutation** : réponse qui montre qu'une objection est fausse ou exagérée.
- **Concession** : reconnaissance d'une part de vérité de l'objection (« Certes… mais »).

## 4. Méthode étape par étape

1. Écris ta thèse en une phrase.
2. Note l'idée de ton argument en une phrase courte (« Le covoiturage fait économiser de \
l'argent »).
3. Demande-toi « Pourquoi ? Comment ? » et écris l'explication (deux phrases maximum).
4. Cherche un exemple concret ou une preuve chiffrée ; précise d'où vient la donnée.
5. Termine par une phrase qui relie l'argument à la thèse (« C'est pourquoi… »).
6. Relis en vérifiant les connecteurs : chaque phrase est-elle reliée logiquement à la \
précédente ?
7. Si une objection évidente existe, ajoute une concession ou une réfutation.

## 5. Exemples commentés

### {FR11_MODEL_TITLE}

{FR11_MODEL_TEXT}

**Analyse commentée :** les quatre éléments sont présents et repérables par leurs \
connecteurs. *Idée annoncée* : « D'abord, le covoiturage permet… de réduire nettement leurs \
frais de déplacement. » *Explication* (introduite par « En effet ») : les frais sont divisés \
entre les passagers. *Preuve* (introduite par « Ainsi ») : 85 euros économisés par mois chez \
Transmétal, avec une source identifiée (le programme de l'entreprise). *Lien avec la thèse* \
(introduit par « C'est pourquoi ») : l'entreprise améliore le pouvoir d'achat de son \
personnel. Le connecteur « D'abord » annonce que d'autres arguments suivront.

### {FR11_WEAK_TITLE}

{FR11_WEAK_TEXT}

**Analyse commentée :** ce paragraphe accumule des affirmations gratuites (« c'est bien », \
« c'est l'avenir ») et une **généralisation** (« Tout le monde est d'accord »). L'exemple du \
cousin est une anecdote : un seul cas ne prouve rien pour tous les employés. L'idée « on ne \
prend pas la voiture » pourrait devenir un vrai argument, mais elle n'est ni expliquée ni \
reliée à la thèse. Aucun connecteur logique ne relie les phrases, et le mot « télétravail » \
est répété quatre fois.

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse** : « Le stage obligatoire c'est utile. Kevin a aimé son stage. »
- ✅ **Bonne réponse** : « D'abord, un stage obligatoire aiderait les élèves à trouver un \
emploi. En effet, l'employeur peut juger le sérieux d'un jeune en le voyant travailler, ce \
qu'aucun bulletin ne montre. Ainsi, selon l'enquête de l'institut Avenir Jeunes, 58 % des \
anciens stagiaires ont trouvé un emploi dans les six mois, contre 39 % des autres. C'est \
pourquoi rendre le stage obligatoire donnerait à tous les élèves cette chance d'insertion. »

La bonne réponse annonce l'idée, l'explique, la prouve avec une donnée sourcée, puis la \
relie à la thèse. La mauvaise se contente d'une affirmation et d'une anecdote.

## 7. Pièges et erreurs fréquentes

- Confondre l'exemple et l'argument : un exemple illustre une idée, il ne la remplace pas.
- Empiler plusieurs idées dans un même paragraphe sans en développer aucune.
- Utiliser un connecteur qui ne correspond pas à la relation (« donc » devant une cause, \
« car » devant une conséquence).
- Citer un chiffre sans dire d'où il vient.
- Oublier la phrase de lien avec la thèse : le lecteur ne sait plus à quoi sert l'argument.
- Ignorer l'objection la plus évidente : le lecteur y pense quand même.

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Essaie avant de regarder la correction</summary>

Dans la phrase « Le covoiturage réduit les embouteillages, **donc** il faut l'encourager », \
quelle relation exprime le connecteur « donc » ? Par quel autre connecteur pourrais-tu le \
remplacer sans changer le sens ?

<details>
<summary>Voir la correction expliquée</summary>

« Donc » exprime une **conséquence** : encourager le covoiturage est la conséquence logique \
du fait qu'il réduit les embouteillages. On peut le remplacer par « c'est pourquoi », « par \
conséquent » ou « ainsi ». « Car » serait faux : il exprime une cause et inverserait le \
raisonnement.
</details>
</details>

<details>
<summary>Exercice 2 — Essaie avant de regarder la correction</summary>

Réécris l'idée « En plus on ne prend pas la voiture » (paragraphe sur le télétravail) en \
un argument développé de trois ou quatre phrases.

<details>
<summary>Voir la correction expliquée</summary>

Exemple de réponse : « De plus, le télétravail diminue les trajets en voiture. En effet, un \
employé qui reste chez lui un jour par semaine supprime un aller-retour domicile-travail, \
donc du carburant, des bouchons et de la pollution. Par exemple, pour un trajet de 25 km, \
cela représente plus de 2 000 km en moins sur une année. Ainsi, le télétravail profite à \
la fois au portefeuille des employés et à l'environnement. » On retrouve l'idée (« De \
plus… »), l'explication (« En effet… »), l'exemple chiffré et le lien final.
</details>
</details>

<details>
<summary>Exercice 3 — Essaie avant de regarder la correction</summary>

Objection : « Un stage obligatoire est impossible, car les petites entreprises n'ont pas le \
temps d'encadrer un stagiaire. » Rédige une concession.

<details>
<summary>Voir la correction expliquée</summary>

« Certes, certaines petites entreprises manquent de temps pour encadrer un stagiaire. \
Pourtant, l'école pourrait les aider en organisant les stages dans des entreprises plus \
grandes ou en partageant l'encadrement avec un professeur référent. » La concession \
reconnaît la part de vérité (« Certes… »), puis le connecteur d'opposition (« Pourtant ») \
montre que la thèse reste défendable.
</details>
</details>

## 9. Corrigés très expliqués

**Question :** pourquoi l'exemple du cousin qui télétravaille ne suffit-il pas à prouver \
que le télétravail est bon pour tous les employés ?

**Corrigé expliqué :** un exemple est un cas particulier. Le cousin est **une seule \
personne**, dont la situation (métier, logement, famille) n'est peut-être pas celle des \
autres employés. Passer d'un cas isolé à une règle générale (« c'est bien pour tout le \
monde ») est une généralisation. Pour convaincre, il faudrait une explication du mécanisme \
(pourquoi le télétravail aiderait la plupart des employés) et, si possible, une preuve plus \
large : une enquête, une donnée chiffrée, une source identifiée.

## 10. Fiche mémo

- Opinion ≠ argument : l'argument est la **raison** qui justifie l'opinion.
- Argument développé = idée annoncée + explication + exemple/preuve + lien avec la thèse.
- Un exemple seul est une anecdote ; une idée seule est une affirmation gratuite.
- Connecteurs : cause (car, en effet), conséquence (donc, c'est pourquoi), opposition \
(mais, pourtant), concession (certes… mais), illustration (par exemple, ainsi).
- Objection : la réfuter ou la concéder, puis revenir à la thèse.
"""


def fr12_course_markdown() -> str:
    return f"""# Rédiger un texte argumentatif

## 1. Ce que tu dois savoir faire à l'examen

Tu dois pouvoir rédiger un texte argumentatif complet (article d'opinion, lettre ouverte, \
courriel argumentatif) qui respecte la **situation de communication** imposée par la \
consigne, suit un **plan** clair (introduction, développement, conclusion) et respecte la \
**longueur demandée**.

## 2. Théorie progressive

**Étape 1 — Lire la situation de communication.** Avant d'écrire, la consigne te dit : \
*qui* écrit (ton rôle), *à qui* (le **destinataire**), *pour quoi* (le **but** : convaincre, \
obtenir quelque chose), *sous quelle forme* (le **genre** : lettre, courriel, article) et \
*combien* (la longueur). Ces éléments décident du **registre de langue** : un courriel à \
un président de comité ou une lettre au conseil communal demandent un registre courant ou \
soutenu, jamais familier.

**Étape 2 — Construire le plan.** Un texte argumentatif suit trois parties.

- L'**introduction** contient une **amorce** (une entrée en matière liée au sujet : un \
fait, une situation concrète), la **présentation du sujet**, la **thèse** et, si possible, \
l'**annonce du plan** (les arguments qui vont suivre).
- Le **développement** contient deux ou trois paragraphes, un argument développé par \
paragraphe (voir le cours « Construire un argument développé »), reliés par des \
connecteurs (d'abord, ensuite, enfin). Il traite aussi l'objection principale \
(concession ou réfutation).
- La **conclusion** fait le **bilan** (rappel de la thèse et des arguments, sans les \
recopier) et peut proposer une **ouverture** (une demande concrète, une proposition, une \
question qui prolonge le débat).

**Étape 3 — Respecter les codes du genre.** Une lettre ou un courriel comporte une \
**formule d'appel** (« Madame, Monsieur, »), une **formule de politesse** finale et une \
signature. Un courriel a en plus un **objet** précis. Un article d'opinion a un titre \
accrocheur et pas de formule d'appel.

**Étape 4 — Gérer la longueur.** Une longueur imposée fait partie de la consigne. Pour \
un texte de 250 à 300 mots, compte environ 50 mots d'introduction, deux paragraphes de 70 \
à 80 mots et 40 mots de conclusion. Trop court, le texte ne développe pas ses arguments ; \
trop long, il ne respecte pas la consigne.

## 3. Définitions importantes

- **Situation de communication** : émetteur, destinataire, but, genre et contexte d'un texte.
- **Destinataire** : la personne ou le groupe à qui le texte est adressé.
- **Registre de langue** : niveau de langage (familier, courant, soutenu) choisi selon le \
destinataire.
- **Amorce** : première phrase de l'introduction, qui fait entrer le lecteur dans le sujet.
- **Annonce du plan** : phrase qui présente les arguments qui vont être développés.
- **Développement** : partie centrale du texte, organisée en paragraphes argumentatifs.
- **Bilan** : rappel synthétique de la thèse et des arguments dans la conclusion.
- **Ouverture** : fin de conclusion qui élargit ou propose une suite concrète.
- **Formule d'appel / formule de politesse** : début et fin conventionnels d'une lettre ou \
d'un courriel.
- **Lettre ouverte** : lettre adressée à une personne ou une autorité, mais rendue publique \
pour convaincre un large public.

## 4. Méthode étape par étape

1. Souligne dans la consigne : ton rôle, le destinataire, le but, le genre, la longueur.
2. Formule ta thèse en une phrase.
3. Cherche au brouillon trois arguments et garde les deux ou trois plus solides.
4. Pour chaque argument, note un exemple ou une preuve (utilise les informations fournies).
5. Repère l'objection principale et prépare une concession ou une réfutation.
6. Rédige l'introduction : amorce, sujet, thèse, annonce du plan.
7. Rédige un paragraphe par argument, avec des connecteurs.
8. Rédige la conclusion : bilan puis ouverture (demande, proposition).
9. Vérifie les codes du genre (objet, formule d'appel, politesse, signature) et compte les \
mots.

## 5. Exemples commentés

### {FR12_MODEL_TITLE}

{FR12_MODEL_TEXT}

**Analyse commentée :** la situation de communication est respectée : des jeunes \
(émetteurs) écrivent à la bourgmestre et au conseil (destinataires) pour obtenir une \
décision (but), dans un registre soutenu (« Veuillez agréer… »). L'**introduction** part \
d'un fait concret (amorce : la fermeture de la salle en 2024), présente le sujet (l'avenir \
de l'ancienne poste), énonce la thèse et annonce les trois idées du plan. Le \
**développement** consacre un paragraphe à chaque argument (« Tout d'abord », « Ensuite ») \
puis traite l'objection du coût par une concession (« Certes… Pourtant… »), avec des \
chiffres. La **conclusion** fait le bilan et ouvre sur une proposition concrète (présenter \
le projet au conseil).

### {FR12_INTROS_TITLE}

{FR12_INTROS_TEXT}

**Analyse commentée :** l'introduction **B** est la seule complète : une amorce concrète \
(les vêtements de marque devant les grilles), le sujet (la proposition de la direction), \
la thèse (« ce serait une erreur ») et l'annonce de trois arguments. L'introduction **A** \
donne la thèse sans amorce ni annonce et commence par « Je vais parler de », formule à \
éviter. L'introduction **C** part de trop loin (la préhistoire) : son amorce est sans lien \
direct avec le sujet et elle ne donne même pas la thèse.

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise conclusion** : « Voilà, c'est pour ça que je suis pour. Bisous. » → \
registre familier, aucun bilan des arguments, aucune ouverture.
- ✅ **Bonne conclusion** : « Pour toutes ces raisons, un repair café le samedi matin \
rendrait service aux habitants, réduirait nos déchets et créerait des liens entre voisins. \
Je serais heureux de participer à une réunion pour en organiser le premier essai. »

La bonne conclusion rappelle les arguments sans les recopier, puis fait une proposition \
concrète adaptée au destinataire.

## 7. Pièges et erreurs fréquentes

- Commencer à écrire sans avoir identifié le destinataire : le registre devient inadapté.
- Une introduction sans thèse : le lecteur ne sait pas ce que tu défends.
- Une amorce trop générale (« Depuis la nuit des temps… »).
- Un développement en un seul bloc, sans paragraphes ni connecteurs.
- Une conclusion qui ajoute un argument nouveau au lieu de faire le bilan.
- Oublier l'objet, la formule d'appel ou la formule de politesse d'un courriel ou d'une \
lettre.
- Ignorer la longueur imposée.

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Essaie avant de regarder la correction</summary>

Dans la lettre ouverte sur la maison de jeunes, retrouve la phrase qui annonce le plan et \
cite les trois idées annoncées.

<details>
<summary>Voir la correction expliquée</summary>

La phrase est : « nous vous demandons d'y installer une maison de jeunes, parce qu'elle \
offrirait un lieu sûr aux adolescents, qu'elle renforcerait la vie du village et qu'elle \
coûterait moins cher qu'on ne le pense. » Les trois idées annoncées (sécurité, vie du \
village, coût) sont ensuite traitées dans le même ordre dans le développement : l'annonce \
du plan sert de « table des matières » au lecteur.
</details>
</details>

<details>
<summary>Exercice 2 — Essaie avant de regarder la correction</summary>

Réécris l'introduction A (« Je vais parler de l'uniforme. Je suis contre. ») pour qu'elle \
devienne complète.

<details>
<summary>Voir la correction expliquée</summary>

Exemple : « La direction de notre école propose d'imposer un uniforme dès septembre \
prochain. Officiellement, il s'agirait de réduire les moqueries liées aux vêtements. Je \
pense pourtant que ce serait une mauvaise décision, d'abord parce qu'elle pèserait sur le \
budget des familles, ensuite parce qu'elle ne réglerait pas le vrai problème du \
harcèlement. » On a ajouté une amorce concrète, le sujet, la thèse et l'annonce de deux \
arguments.
</details>
</details>

## 9. Corrigés très expliqués

**Question :** pour la consigne du repair café, quel registre faut-il utiliser et quelles \
formules doivent apparaître ?

**Corrigé expliqué :** le destinataire est M. Renard, président du comité, que l'élève ne \
connaît pas personnellement : il faut un **registre courant ou soutenu**, sans tutoiement \
ni abréviations. Le courriel commence par un **objet** précis (« Proposition de repair café \
le samedi matin »), une **formule d'appel** (« Monsieur le Président, ») et se termine par \
une **formule de politesse** (« Je vous prie d'agréer, Monsieur le Président, mes \
salutations distinguées. ») suivie de la signature. Ces codes font partie de la consigne : \
les oublier fait perdre des points même si les arguments sont bons.

## 10. Fiche mémo

- Avant d'écrire : qui ? à qui ? pour quoi ? quel genre ? combien de mots ?
- Introduction = amorce + sujet + thèse + annonce du plan.
- Développement = un argument développé par paragraphe + traitement de l'objection.
- Conclusion = bilan (sans recopier) + ouverture (demande, proposition).
- Lettre/courriel : objet, formule d'appel, formule de politesse, signature.
- Registre adapté au destinataire ; longueur imposée respectée.
"""


def fr13_course_markdown() -> str:
    return f"""# Utiliser un dossier documentaire dans son argumentation

## 1. Ce que tu dois savoir faire à l'examen

Face à un dossier de plusieurs documents, tu dois pouvoir **sélectionner** les \
informations utiles à ta thèse, les **intégrer** dans ton texte en citant ou en \
reformulant, **indiquer la source** de chaque information, et tenir compte des documents \
qui contredisent ta position, sans jamais déformer ce qu'ils disent.

## 2. Théorie progressive

**Étape 1 — Lire le dossier avec sa thèse en tête.** Un dossier documentaire n'est pas à \
résumer document par document : c'est une **réserve d'arguments et de preuves**. Pour \
chaque document, demande-toi : qui parle (journal, témoin, organisme) ? Cette information \
soutient-elle ma thèse, la contredit-elle, ou la nuance-t-elle ? Note-la dans un tableau à \
trois colonnes : *pour*, *contre*, *nuance*.

**Étape 2 — Deux façons d'utiliser un document.**

- La **citation** reprend les mots exacts de l'auteur, **entre guillemets**, avec la \
source : *Le boulanger du quartier affirme avoir perdu « environ 10 % de [son] chiffre \
d'affaires du matin » (document 2).* Une citation est courte (une phrase ou un morceau de \
phrase) et elle est **introduite** par une phrase à toi.
- La **reformulation** redit l'information avec tes propres mots, sans guillemets, mais \
toujours avec la source : *Selon l'agence Air Wallon Mesures, la pollution devant les \
écoles est environ un tiers plus faible quand la rue est fermée aux voitures \
(document 3).*

**Étape 3 — Toujours indiquer la source.** Une information sans source ressemble à une \
opinion personnelle. Les formules utiles : *selon…*, *d'après…*, *comme l'indique…*, \
*le document 1 montre que…*, *l'agence X constate que…*. Mentionner la source montre aussi \
au lecteur que l'information est **vérifiable**.

**Étape 4 — Ne pas déformer.** Utiliser un document honnêtement, c'est respecter son \
sens : ne pas couper une phrase pour lui faire dire le contraire, ne pas exagérer un \
chiffre (« 37 % de moins » n'est pas « plus de pollution du tout »), ne pas présenter un \
témoignage personnel comme une étude.

**Étape 5 — Tenir compte du document qui dérange.** Si un document du dossier défend la \
position contraire, l'ignorer affaiblit ton texte. Mieux vaut l'utiliser comme \
**objection** puis y répondre (concession ou réfutation), en t'appuyant au besoin sur un \
autre document.

**Étape 6 — Ajouter ce que tu sais.** La consigne permet souvent d'utiliser aussi tes \
**connaissances personnelles** (une expérience, un exemple local). Elles complètent le \
dossier, mais ne remplacent pas l'exploitation des documents demandée.

## 3. Définitions importantes

- **Dossier documentaire** : ensemble de documents fournis pour nourrir une réflexion ou \
une argumentation.
- **Citation** : reprise des mots exacts d'un auteur, entre guillemets, avec sa source.
- **Reformulation** : reprise d'une idée avec ses propres mots, sans guillemets, avec sa \
source.
- **Source** : origine d'une information (auteur, organisme, document).
- **Intégrer une citation** : l'insérer dans une phrase personnelle qui l'introduit et la \
relie à l'argument.
- **Copier-coller** : recopie de passages sans les introduire, les sourcer ni les relier à \
l'argument — à éviter.
- **Déformer un document** : lui faire dire ce qu'il ne dit pas (coupure, exagération, \
changement de sens).
- **Connaissances personnelles** : exemples ou informations que tu possèdes en dehors du \
dossier.

## 4. Méthode étape par étape

1. Lis la consigne et formule ta thèse.
2. Survole chaque document : nature, auteur, date, idée principale.
3. Classe les informations utiles dans un tableau *pour / contre / nuance*, avec le numéro \
du document.
4. Choisis, pour chaque argument, au moins une information du dossier qui le prouve.
5. Décide pour chaque information : citation courte entre guillemets ou reformulation.
6. Introduis chaque information par une formule de source (« selon le document 3… »).
7. Utilise le document qui contredit ta thèse comme objection, puis réponds-y.
8. Relis : aucune information sans source, aucune citation trop longue, aucun sens déformé.

## 5. Exemples commentés

Le dossier d'exemple porte sur la question : « Faut-il rendre définitive la rue scolaire \
devant l'école des Glycines ? »

### {FR13_DOC1_TITLE}

{FR13_DOC1_TEXT}

### {FR13_DOC2_TITLE}

{FR13_DOC2_TEXT}

### {FR13_DOC3_TITLE}

{FR13_DOC3_TEXT}

**Tableau de tri commenté (thèse : la rue scolaire doit devenir définitive)** :

| Pour | Contre | Nuance |
|---|---|---|
| Plus d'enfants à pied ou à vélo (34 % → 52 %, document 1) | Perte de clientèle du boulanger (environ 10 %, document 2) | Pollution réduite seulement aux heures d'entrée et de sortie (document 3) |
| Aucun accident contre trois accrochages (document 1) | Parents obligés de se garer loin les jours de pluie (document 1) | Le boulanger accepte la mesure si les commerces restent signalés (document 2) |
| NO2 environ 37 % plus faible (document 3) | | |

**Paragraphe commenté (intégration réussie)** : « Ensuite, la rue scolaire protège la \
santé des enfants. En effet, d'après les mesures de l'agence Air Wallon Mesures, la \
concentration de dioxyde d'azote devant les écoles équipées d'une rue scolaire est \
d'environ 37 % inférieure aux heures d'entrée et de sortie (document 3). Or ce gaz \
« aggrave l'asthme, en particulier chez les enfants ». Certes, le boulanger voisin dit \
avoir perdu une partie de sa clientèle du matin (document 2), mais une signalisation \
indiquant que les commerces restent accessibles à pied, comme il le propose lui-même, \
limiterait ce problème. » → Chaque information est sourcée, la citation est courte et \
introduite, l'objection du document 2 est traitée honnêtement.

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse (copier-coller)** : « Le dioxyde d'azote (NO2) est un gaz polluant \
émis principalement par la circulation automobile. Il irrite les voies respiratoires et \
aggrave l'asthme. Donc il faut la rue scolaire. » → deux phrases recopiées sans \
guillemets ni source, aucun lien expliqué avec la rue scolaire.
- ❌ **Mauvaise réponse (déformation)** : « Le document 3 prouve que la rue scolaire \
supprime la pollution. » → le document parle d'environ 37 % de moins, et seulement aux \
heures d'entrée et de sortie.
- ✅ **Bonne réponse** : « Selon le document 3, la pollution au dioxyde d'azote est \
environ 37 % plus faible devant les écoles qui ont une rue scolaire, au moment où les \
enfants sont les plus nombreux. »

## 7. Pièges et erreurs fréquentes

- Résumer les documents l'un après l'autre au lieu de les mettre au service de sa thèse.
- Recopier un passage sans guillemets : c'est présenter les mots d'un autre comme les \
siens.
- Citer de très longs passages : la citation doit rester courte et ciblée.
- Oublier la source, ou se tromper de numéro de document.
- Déformer un chiffre ou couper une phrase pour lui faire dire autre chose.
- Ignorer le document qui contredit sa thèse.
- Ne parler que de ses connaissances personnelles, sans exploiter le dossier.

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Essaie avant de regarder la correction</summary>

Le témoignage du boulanger (document 2) soutient-il, contredit-il ou nuance-t-il la thèse \
« la rue scolaire doit devenir définitive » ?

<details>
<summary>Voir la correction expliquée</summary>

Il la **contredit en partie** (il dit avoir perdu environ 10 % de son chiffre d'affaires du \
matin et regrette de ne pas avoir été consulté) mais la **nuance** aussi : il ne refuse pas \
la mesure (« je comprends qu'on veuille protéger les enfants ») et propose une solution \
(une signalisation des commerces). Un bon texte peut donc l'utiliser comme objection, puis \
reprendre sa propre proposition pour y répondre.
</details>
</details>

<details>
<summary>Exercice 2 — Essaie avant de regarder la correction</summary>

Reformule, avec tes mots et avec la source, l'information « la part des enfants venant à \
pied ou à vélo est passée de 34 % à 52 % ».

<details>
<summary>Voir la correction expliquée</summary>

Exemple : « D'après le bilan publié par le journal local (document 1), environ un enfant \
sur deux vient désormais à l'école à pied ou à vélo, contre un sur trois avant la rue \
scolaire. » Les chiffres sont fidèles (52 % ≈ un sur deux, 34 % ≈ un sur trois), la \
phrase est personnelle et la source est indiquée.
</details>
</details>

## 9. Corrigés très expliqués

**Question :** pourquoi la phrase « Le document 3 prouve que la rue scolaire supprime la \
pollution » est-elle une déformation ?

**Corrigé expliqué :** le document 3 donne deux limites précises. D'abord, il parle d'une \
pollution **réduite** d'environ 37 % (24 au lieu de 38 microgrammes par mètre cube), pas \
supprimée. Ensuite, il précise que cette baisse concerne les **heures d'entrée et de \
sortie** et que la rue scolaire « ne règle pas la pollution le reste de la journée ». \
Dire « supprime » exagère le chiffre et efface une nuance que l'agence a pris soin \
d'écrire. Un correcteur le remarque immédiatement : une information fidèle est plus \
convaincante qu'une information exagérée.

## 10. Fiche mémo

- Le dossier est une réserve d'arguments : tri *pour / contre / nuance*, avec le numéro du \
document.
- Citation = mots exacts + guillemets + source, courte et introduite.
- Reformulation = tes mots + source, sans guillemets.
- Toujours la source : « selon…, d'après…, le document 2 montre que… ».
- Jamais de copier-coller, jamais de déformation.
- Le document qui dérange devient une objection à traiter.
"""


def fr14_course_markdown() -> str:
    return f"""# Réclamation et adaptation au destinataire

## 1. Ce que tu dois savoir faire à l'examen

Tu dois pouvoir rédiger une **réclamation** (lettre ou courriel) qui expose des faits \
précis, formule une **demande claire** et adopte un **ton ferme mais courtois**, adapté au \
destinataire. Tu dois aussi savoir analyser une réclamation mal rédigée et l'améliorer.

## 2. Théorie progressive

**Étape 1 — Le but d'une réclamation.** Une réclamation n'est pas un moyen de se défouler : \
son but est d'**obtenir quelque chose** (un remboursement, un échange, une réparation, une \
correction de facture). Tout ce qui ne sert pas ce but (insultes, menaces, généralisations) \
réduit les chances de l'obtenir.

**Étape 2 — La structure.** Une réclamation efficace suit un ordre logique :

1. les **coordonnées** de l'expéditeur (et, dans une lettre papier, du destinataire, le \
lieu et la date) ;
2. un **objet** précis qui permet au destinataire de retrouver le dossier (« Commande \
EP-48213 — produit défectueux ») ;
3. une **formule d'appel** (« Madame, Monsieur, ») ;
4. l'**exposé des faits** : ce qui s'est passé, dans l'ordre chronologique, avec des \
**dates**, des **références** (numéro de commande, de contrat) et des montants ;
5. la **justification** : pourquoi ta demande est légitime (garantie, conditions \
générales, contrat, promesse non tenue) ;
6. la **demande précise** : ce que tu veux exactement, et dans quel délai ;
7. les **pièces jointes** éventuelles (bon de livraison, photo, accusé de réception) ;
8. une **formule de politesse** et la signature.

**Étape 3 — Le ton.** Le ton doit être **ferme** (la demande est claire, le délai est \
indiqué, les faits sont exacts) et **courtois** (vouvoiement, aucune insulte, aucune \
menace disproportionnée). La personne qui lit n'est souvent pas responsable du problème : \
la respecter rend la réponse plus rapide.

**Étape 4 — Adapter au destinataire.** On ne s'adresse pas de la même manière à un ami, à \
un service client ou à une administration. Le destinataire décide du **registre** \
(familier entre amis, courant ou soutenu pour une entreprise ou une administration), de la \
**formule d'appel** et du niveau de détail. Le même problème raconté à un ami (« Mon \
aspirateur est déjà fichu, la galère ! ») devient, pour le service client, un exposé daté \
avec numéro de commande et demande précise.

## 3. Définitions importantes

- **Réclamation** : écrit qui signale un problème et demande sa réparation.
- **Objet** : ligne qui résume le motif du message et permet de retrouver le dossier.
- **Exposé des faits** : récit précis et chronologique de ce qui s'est passé.
- **Référence** : numéro qui identifie une commande, un contrat, une facture.
- **Demande précise** : ce que l'on attend exactement (remboursement, échange, délai).
- **Pièce jointe** : document ajouté au message pour prouver les faits.
- **Ton ferme et courtois** : demande claire et déterminée, exprimée poliment.
- **Registre de langue** : familier, courant ou soutenu, choisi selon le destinataire.
- **Destinataire** : personne ou service à qui le message est adressé.

## 4. Méthode étape par étape

1. Relève dans la situation : dates, références, montants, ce qui a déjà été tenté.
2. Identifie le destinataire et choisis le registre (courant ou soutenu).
3. Écris un objet précis avec la référence et le motif.
4. Rédige l'exposé des faits dans l'ordre chronologique, sans jugement.
5. Justifie ta demande par une règle (garantie, conditions générales, contrat).
6. Formule une demande précise et un délai raisonnable.
7. Mentionne les pièces jointes.
8. Termine par une formule de politesse et tes coordonnées.
9. Relis en supprimant toute insulte, menace ou exagération.

## 5. Exemples commentés

### {FR14_SITUATION_TITLE}

{FR14_SITUATION_TEXT}

### {FR14_BAD_TITLE}

{FR14_BAD_TEXT}

**Analyse commentée :** ce courriel n'a presque aucune chance d'aboutir. L'**objet** \
(« !!!!! ») ne dit rien du problème. La formule d'appel « Salut » est familière. Les \
**faits** sont absents : quel produit ? quelle commande ? quelle date ? quelle panne ? La \
**demande** est vague (« réglez ça »). Le ton est agressif (« produits pourris », « vous vous \
fichez des clients ») et se termine par une menace. Aucune formule de politesse.

### {FR14_GOOD_TITLE}

{FR14_GOOD_TEXT}

**Analyse commentée :** l'objet contient la référence et le motif. Les faits sont datés et \
chronologiques (commande, livraison, panne, appel, absence de rappel). La demande est \
justifiée par les conditions générales de vente, précise (189 euros) et accompagnée d'un \
délai (31 mars). Le ton est ferme (« je vous demande ») mais courtois (« de bien vouloir », \
formule de politesse). Les pièces jointes sont mentionnées.

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse** : « Vous êtes des voleurs, rendez-moi mon argent. »
- ✅ **Bonne réponse** : « Je constate que 34,90 euros ont été prélevés le 5 février et le \
5 mars, alors que j'ai résilié mon contrat le 2 janvier. Je vous demande de me rembourser \
ces deux prélèvements, soit 69,80 euros. »

La bonne réponse remplace l'accusation par des **faits datés** et une **demande chiffrée**.

## 7. Pièges et erreurs fréquentes

- Un objet vague (« Problème », « Urgent ») ou absent.
- Raconter ses émotions au lieu des faits.
- Oublier la référence de la commande ou du contrat.
- Ne pas dire ce que l'on veut exactement.
- Insulter ou menacer : le destinataire se braque.
- Utiliser un registre familier (« Salut », tutoiement, abréviations) avec une entreprise.
- Oublier de mentionner les preuves que l'on possède.

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Essaie avant de regarder la correction</summary>

Propose un objet précis pour la réclamation de Kevin, en imaginant qu'il a commandé le même \
aspirateur (commande EP-50177).

<details>
<summary>Voir la correction expliquée</summary>

Exemple : « Commande EP-50177 — aspirateur AS-300 en panne dès la livraison ». L'objet \
donne la référence (pour retrouver le dossier), le produit et le motif. Le destinataire sait \
de quoi il s'agit avant même d'ouvrir le message.
</details>
</details>

<details>
<summary>Exercice 2 — Essaie avant de regarder la correction</summary>

Transforme la phrase « Je veux que vous régliez ça vite sinon je mets des avis négatifs \
partout » en une demande ferme et courtoise.

<details>
<summary>Voir la correction expliquée</summary>

Exemple : « Je vous demande de bien vouloir procéder au remplacement de l'appareil ou à son \
remboursement, et de me répondre avant le 31 mars. » La menace disparaît, la demande \
devient précise et le délai rend la réponse plus probable : c'est cela, la fermeté.
</details>
</details>

## 9. Corrigés très expliqués

**Question :** Sarah raconte aussi sa panne à son amie Julie par message. En quoi ce message \
sera-t-il différent du courriel envoyé à ÉlectroPlus ?

**Corrigé expliqué :** le **destinataire** change, donc le registre et le contenu changent. \
À Julie, Sarah peut tutoyer, utiliser un registre familier et parler de ses émotions \
(« je suis dégoûtée, je n'ai même pas pu l'utiliser ! ») : le but est de partager une \
expérience. À ÉlectroPlus, le but est d'obtenir un remboursement : il faut le vouvoiement, \
un objet, la référence de commande, des faits datés, la règle des conditions générales, \
une demande chiffrée et une formule de politesse. Le problème est le même ; le texte \
s'adapte au destinataire et au but.

## 10. Fiche mémo

- But : obtenir une solution, pas se défouler.
- Structure : coordonnées, objet, formule d'appel, faits datés, justification, demande \
précise + délai, pièces jointes, politesse, signature.
- Ton ferme (demande claire, délai) et courtois (vouvoiement, aucune insulte ni menace).
- Le destinataire décide du registre et du niveau de détail.
"""


def fr15_course_markdown() -> str:
    return f"""# Défendre une opinion oralement

## 1. Ce que tu dois savoir faire à l'examen

Tu dois pouvoir **préparer** une courte intervention orale pour défendre une opinion \
(réunion, conseil, entretien), la **structurer** pour qu'elle soit facile à suivre à \
l'écoute, utiliser ta **voix** et ton **attitude** pour convaincre, et **répondre à une \
objection** de manière calme et argumentée. À l'écrit, on peut te demander de préparer \
cette intervention ou d'analyser la transcription d'un oral.

## 2. Théorie progressive

**Étape 1 — L'oral n'est pas un écrit lu à voix haute.** Celui qui écoute ne peut pas \
revenir en arrière comme un lecteur. L'orateur doit donc **annoncer** ce qu'il va dire, \
marquer clairement le passage d'une idée à l'autre et **résumer** à la fin. Les phrases sont \
plus courtes qu'à l'écrit.

**Étape 2 — Préparer.** On prépare une **fiche aide-mémoire** en **mots-clés** (jamais un \
texte entièrement rédigé que l'on lirait) : la thèse, deux ou trois arguments avec un \
exemple chacun, l'objection prévisible et la réponse prévue, la phrase de conclusion. On \
s'entraîne en se chronométrant pour respecter le **temps de parole**.

**Étape 3 — Structurer à l'oral.** Une intervention efficace contient :

- une **ouverture** : saluer, se présenter si nécessaire, donner sa position dès le début \
(« Je suis pour…, et je voudrais vous donner deux raisons. ») ;
- les **arguments**, annoncés par des **marqueurs oraux** qui servent de panneaux \
indicateurs (« Première raison… », « Deuxième raison… », « J'ajoute que… ») ;
- la **prise en compte de l'objection** (« Je sais que la question de… se pose. Je propose \
que… ») ;
- une **clôture** courte : un résumé en une phrase et un remerciement.

**Étape 4 — La voix et le corps.** À l'oral, le message passe aussi par la \
**communication non verbale** : le **regard** (regarder l'auditoire, pas sa feuille), la \
**posture** (droite, stable), les **gestes** (mesurés), et par la voix : le **volume** \
(audible par tous), le **débit** (ni trop rapide ni trop lent), l'**articulation** et les \
**pauses**, qui laissent le temps de comprendre. Les **hésitations** répétées (« euh », \
« voilà ») donnent une impression d'improvisation.

**Étape 5 — Répondre à une objection.** On écoute la question jusqu'au bout, on la \
**reformule** brièvement pour montrer qu'on l'a comprise, puis on répond avec un argument \
ou une proposition, sans s'énerver et sans attaquer la personne. On peut concéder une part \
de vérité (« Vous avez raison sur ce point, mais… »).

**Étape 6 — Respecter les autres.** Défendre une opinion, c'est critiquer des **idées**, \
jamais des **personnes** : une attaque personnelle (« c'est toujours les mêmes qui… ») \
discrédite celui qui la prononce.

## 3. Définitions importantes

- **Intervention orale** : prise de parole préparée devant un auditoire.
- **Fiche aide-mémoire** : notes en mots-clés qui guident l'orateur sans être lues.
- **Temps de parole** : durée accordée à chaque intervenant.
- **Marqueur oral** : expression qui signale la structure à l'auditeur (« première \
raison », « pour résumer »).
- **Communication non verbale** : regard, posture, gestes, expressions du visage.
- **Débit** : vitesse à laquelle on parle.
- **Articulation** : prononciation nette de chaque mot.
- **Pause** : court silence volontaire qui met une idée en valeur.
- **Reformuler une objection** : redire brièvement la question posée avant d'y répondre.
- **Attaque personnelle** : critique de la personne au lieu de son idée.

## 4. Méthode étape par étape

1. Lis la situation : qui écoute ? combien de temps as-tu ? quelle décision est en jeu ?
2. Choisis ta position et formule-la en une phrase simple.
3. Sélectionne deux arguments solides avec un exemple ou un chiffre chacun.
4. Prévois l'objection la plus probable et ta réponse.
5. Écris ta fiche aide-mémoire en mots-clés, avec les marqueurs oraux.
6. Entraîne-toi à voix haute, chronomètre-toi.
7. Pendant l'oral : regarde l'auditoire, articule, fais des pauses, garde ta fiche en \
appui.
8. Face à une question : écoute, reformule, réponds calmement, conclus.

## 5. Exemples commentés

### {FR15_TRANSCRIPT_A_TITLE}

{FR15_TRANSCRIPT_A_TEXT}

**Analyse commentée :** Yanis donne sa position dès la première phrase et **annonce** deux \
raisons. Les **marqueurs oraux** (« Première raison », « Deuxième raison », « Donc, pour \
résumer ») permettent de le suivre sans support écrit. Chaque argument est appuyé (six \
élèves sur vingt travaillent sur leur téléphone ; la pluie). Il **anticipe l'objection** de \
la surveillance et propose une solution. Son attitude soutient son message : il se lève, \
regarde l'assemblée, parle d'une voix posée, fait une pause et ne jette qu'un coup d'œil à \
sa fiche.

### {FR15_TRANSCRIPT_B_TITLE}

{FR15_TRANSCRIPT_B_TEXT}

**Analyse commentée :** Léa **lit** sa feuille sans regarder l'auditoire et parle trop \
vite. Sa position n'est jamais annoncée (un délégué doit la lui demander). Les hésitations \
(« euh », « voilà ») et l'absence de marqueurs rendent l'intervention impossible à suivre. \
L'argument sur les vieux ordinateurs n'est pas développé, et la phrase « c'est toujours les \
mêmes qui veulent jouer » est une **attaque personnelle** accompagnée d'une généralisation \
(« tout le monde le sait »).

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse à une objection** : « N'importe quoi, tu n'as rien compris. »
- ✅ **Bonne réponse** : « Tu dis que commencer à 7 h serait difficile pour les parents de \
jeunes enfants. C'est vrai, et on pourrait prévoir pour eux un horaire de 8 h à 14 h. »

La bonne réponse **reformule** l'objection, **concède** une part de vérité et **propose** \
une solution, sans attaquer la personne.

## 7. Pièges et erreurs fréquentes

- Lire un texte entièrement rédigé au lieu de parler à l'auditoire.
- Ne pas annoncer sa position au début.
- Parler trop vite ou trop bas.
- Accumuler les hésitations faute de préparation.
- Dépasser le temps de parole.
- Répondre à une objection en s'énervant ou en attaquant la personne.
- Terminer sans conclusion (« Voilà, c'est tout »).

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Essaie avant de regarder la correction</summary>

Relève dans l'intervention de Yanis les marqueurs oraux qui structurent son propos.

<details>
<summary>Voir la correction expliquée</summary>

« Je voudrais vous donner deux raisons » (annonce), « Première raison », « Deuxième \
raison » (enchaînement), « Je sais que la question de la surveillance se pose » (prise en \
compte de l'objection), « Donc, pour résumer » (clôture). Ces marqueurs remplacent, à \
l'oral, les paragraphes et les titres d'un texte écrit.
</details>
</details>

<details>
<summary>Exercice 2 — Essaie avant de regarder la correction</summary>

Rédige, en mots-clés, une fiche aide-mémoire pour l'intervention de Yanis.

<details>
<summary>Voir la correction expliquée</summary>

Exemple :
- Position : POUR salle info ouverte à midi — 2 raisons.
- 1. Égalité : pas d'ordi à la maison — 6/20 dans ma classe sur téléphone.
- 2. Calme : pluie, couloirs → réviser, projets.
- Objection surveillance → rhétos volontaires (comme bibliothèque).
- Conclusion : égalité + calme. Merci.

La fiche tient en quelques lignes : elle rappelle l'ordre et les chiffres, sans phrases \
complètes à lire.
</details>
</details>

## 9. Corrigés très expliqués

**Question :** pourquoi l'intervention de Léa ne convainc-elle pas, même si son idée (les \
ordinateurs sont vieux) pourrait être un argument valable ?

**Corrigé expliqué :** une idée valable ne suffit pas à l'oral. D'abord, Léa n'annonce \
jamais sa position : l'auditoire ne sait pas ce qu'elle défend, et elle-même hésite à la \
fin (« contre, je crois »). Ensuite, l'argument des vieux ordinateurs n'est ni expliqué ni \
illustré. De plus, sa forme dessert le fond : elle lit sa feuille sans regarder personne, \
parle très vite et multiplie les hésitations. Enfin, l'attaque personnelle (« c'est \
toujours les mêmes ») et la généralisation (« tout le monde le sait ») font perdre du \
crédit à tout son propos. Pour convaincre, il lui faudrait une position annoncée, des \
arguments développés, des marqueurs oraux et une attitude tournée vers l'auditoire.

## 10. Fiche mémo

- L'oral s'écoute : annonce, marqueurs (« premièrement… pour résumer »), conclusion.
- Fiche aide-mémoire en mots-clés, jamais un texte à lire.
- Voix : volume, débit, articulation, pauses. Corps : regard, posture, gestes mesurés.
- Objection : écouter, reformuler, répondre calmement (concession possible).
- Critiquer les idées, jamais les personnes ; respecter le temps de parole.
"""
