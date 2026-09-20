"""Contenu de cours — Français FR01→FR05 (ticket #94, PHASE A).

Structure imposée par le ticket (§ « STRUCTURE MINIMALE DE CHAQUE COURS ») : 1. Ce que je
dois savoir faire à l'examen — 2. Théorie progressive — 3. Définitions importantes —
4. Méthode étape par étape — 5. Exemples commentés — 6. Mauvaises réponses comparées aux
bonnes — 7. Pièges et erreurs fréquentes — 8. Exercices guidés — 9. Corrigés très
expliqués — 10. Fiche mémo. (11. S'entraîner / 12. S'évaluer sont déjà fournis
génériquement par `_uaa_space_nav.html`, ticket #22 — jamais dupliqués ici.)

Les corrigés des exercices guidés (§ 8) sont visibles mais MASQUÉS PAR DÉFAUT
(`<details>`/`<summary>` HTML, préservés tels quels par `app.content.render_markdown` —
aucune nouvelle architecture, le moteur Markdown existant laisse déjà passer le HTML brut).

**Statut explicite : PROVISIONAL_TECHNICAL_SAMPLE** (voir `app.v1.francais_fr01_05_content`)."""

from app.v1.francais_fr01_05_content import (
    FR01_D1_TEXT,
    FR01_D1_TITLE,
    FR01_D2_TEXT,
    FR01_D2_TITLE,
    FR01_LEARNING_A_TEXT,
    FR01_LEARNING_A_TITLE,
    FR01_LEARNING_B_TEXT,
    FR01_LEARNING_B_TITLE,
    FR03_TEXT1_TEXT,
    FR03_TEXT1_TITLE,
    FR03_TEXT2_TEXT,
    FR03_TEXT2_TITLE,
    FR04_DISORGANIZED_TEXT,
    FR04_DISORGANIZED_TITLE,
    FR04_IDEAS_JUMBLE_TEXT,
    FR04_IDEAS_JUMBLE_TITLE,
    FR05_FLAWED1_CORRECTED,
    FR05_FLAWED1_TEXT,
    FR05_FLAWED1_TITLE,
    FR05_FLAWED2_CORRECTED,
    FR05_FLAWED2_TEXT,
    FR05_FLAWED2_TITLE,
)


def fr01_course_markdown() -> str:
    return f"""# FR01 — Comprendre une consigne d'examen

**Statut : contenu de validation technique provisoire (ticket #94) — PAS un examen CESS \
officiel.**

## 1. Ce que tu dois savoir faire à l'examen

Avant même de répondre à une question, tu dois être capable de décoder EXACTEMENT ce \
qu'une consigne demande : quel verbe d'action (« opérateur ») est utilisé, sur quel objet \
il porte, quelles contraintes elle impose (nombre d'éléments, documents à utiliser), et \
à qui/dans quel genre de texte tu dois répondre.

## 2. Théorie progressive

Une consigne d'examen n'est presque jamais une simple question. C'est un ensemble de \
plusieurs exigences empilées dans une seule phrase. Une consigne bien décodée se \
décompose toujours en :

- un **verbe opérateur** (l'action demandée) ;
- un **objet** (sur quoi porte l'action) ;
- des **contraintes** (nombre d'éléments, longueur, documents à utiliser) ;
- parfois un **destinataire** et un **genre** de texte attendu.

Rater UNE seule de ces exigences, même si le reste de la réponse est excellent, fait \
perdre des points.

## 3. Définitions importantes

- **Verbe opérateur** : le mot qui indique l'action précise attendue (relever, citer, \
reformuler, expliquer, justifier, expliciter, comparer, analyser, résumer, synthétiser, \
argumenter, apprécier).
- **Relever / citer** : reprendre un élément EXACT du texte, sans le transformer.
- **Reformuler** : redire une idée du texte avec tes propres mots, sans copier.
- **Expliquer** : développer le sens ou la cause de quelque chose.
- **Justifier** : donner une raison précise, appuyée sur un élément vérifiable.
- **Expliciter** : rendre clair et complet ce qui était seulement suggéré.
- **Comparer** : mettre en relation deux éléments pour en dégager un point commun ou une \
différence précise.
- **Analyser** : décomposer un élément en ses parties pour en comprendre le \
fonctionnement.
- **Résumer / synthétiser** : réduire un texte (ou plusieurs) à l'essentiel, sans \
opinion personnelle ajoutée.
- **Argumenter** : défendre une position à l'aide de raisons organisées.
- **Apprécier** : donner un avis personnel justifié.

## 4. Méthode étape par étape

1. Lis la consigne ENTIÈREMENT avant de commencer à répondre, même si elle est longue.
2. Souligne (mentalement ou sur brouillon) chaque verbe opérateur présent.
3. Note chaque contrainte chiffrée (« deux éléments », « en une phrase »...).
4. Identifie les documents que la consigne t'autorise ou t'oblige à utiliser.
5. Transforme la consigne en petite checklist : une ligne par exigence.
6. Réponds à CHAQUE ligne de la checklist, dans l'ordre, avant de rendre ta copie.
7. Relis ta réponse en te demandant : « Ai-je répondu à TOUT ce qui était demandé, et \
uniquement à cela ? »

## 5. Exemples commentés

### Texte d'apprentissage 1 — {FR01_LEARNING_A_TITLE}

{FR01_LEARNING_A_TEXT}

**Consigne d'exemple :** « Relève deux objectifs du covoiturage mentionnés par les \
ressources humaines, puis explique pourquoi le bilan reste partagé après un an. »

**Analyse commentée :** cette consigne a DEUX parties : (1) relever deux objectifs \
— verbe « relever », contrainte « deux » — puis (2) expliquer le bilan partagé — verbe \
« expliquer ». Une réponse qui ne traite que les objectifs, sans expliquer le bilan, est \
INCOMPLÈTE même si elle est bien écrite.

### Texte d'apprentissage 2 — {FR01_LEARNING_B_TITLE}

{FR01_LEARNING_B_TEXT}

**Consigne d'exemple :** « Explicite les avantages de l'alternance pour l'apprenti, \
selon le texte. »

**Analyse commentée :** le verbe « expliciter » demande de développer clairement, pas \
seulement de citer un mot. Une réponse comme « la rémunération » est incomplète : il \
faut développer (« l'apprenti perçoit une rémunération pendant sa formation, ce qui lui \
permet de... »).

### Comparaison D1/D2 — Le télétravail

**{FR01_D1_TITLE}**

{FR01_D1_TEXT}

**{FR01_D2_TITLE}**

{FR01_D2_TEXT}

**Consigne d'exemple :** « Compare les deux documents : sur quel point la direction et \
les employés sont-ils le plus en désaccord ? »

**Analyse commentée :** le verbe « comparer » exige de mentionner les DEUX documents, \
jamais un seul, et de dégager un point de désaccord PRÉCIS (pas juste « ils ne sont pas \
d'accord » sans dire sur quoi).

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse** (consigne : « Relève deux objectifs, puis explique le bilan ») : \
« Le covoiturage sert à réduire les voitures. » → ne relève qu'UN objectif et n'explique \
pas le bilan : réponse partielle.
- ✅ **Bonne réponse** : « Le covoiturage vise à réduire le nombre de voitures sur le \
parking et à diminuer les frais de déplacement des employés habitant loin. Le bilan reste \
partagé car de nombreux employés renoncent après quelques semaines, en raison d'horaires \
trop différents ou d'une organisation difficile avec des collègues peu connus. »

## 7. Pièges et erreurs fréquentes

- **Hors sujet** : répondre à une question proche mais différente de celle posée.
- **Réponse partielle** : traiter une seule partie d'une consigne à plusieurs exigences.
- **Répondre au fond alors que la consigne demande seulement d'analyser** : par exemple, \
donner ton avis personnel alors que la consigne demandait uniquement de relever un fait.
- **Oublier une contrainte** : ignorer le nombre d'éléments demandé (par exemple, n'en \
citer qu'un quand la consigne en demande deux).

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Essaie avant de regarder la correction</summary>

Consigne : « Résume en une phrase le problème principal évoqué dans le texte sur \
l'alternance, puis apprécie si ce problème te semble facile à résoudre. »

Décompose cette consigne en checklist avant de répondre.

<details>
<summary>Voir la correction expliquée</summary>

Checklist attendue :
1. Résumer en UNE phrase le problème principal (verbe « résumer », contrainte « une \
phrase »).
2. Donner un avis personnel justifié sur la difficulté à résoudre ce problème (verbe \
« apprécier »).

Une réponse qui ne fait que résumer, sans donner d'avis justifié sur la difficulté, est \
incomplète : le verbe « apprécier » demande explicitement un avis personnel argumenté, \
pas seulement un résumé.
</details>
</details>

<details>
<summary>Exercice 2 — Essaie avant de regarder la correction</summary>

Consigne : « Compare les deux documents sur le télétravail (D1/D2) et cite un élément \
précis de chacun pour justifier ta réponse. »

Combien d'éléments cette consigne demande-t-elle exactement, et lesquels ?

<details>
<summary>Voir la correction expliquée</summary>

Cette consigne demande 3 éléments : (1) une comparaison globale entre les deux documents, \
(2) une citation précise tirée du Document 1, (3) une citation précise tirée du \
Document 2. Une réponse qui ne cite qu'un seul document est incomplète.
</details>
</details>

## 9. Corrigés très expliqués

**Consigne :** « Justifie, à l'aide d'un élément du texte, pourquoi la direction de \
Berteau & Fils considère le télétravail comme un choix révisable et non un droit acquis. »

**Corrigé expliqué :** le document 1 précise que « cette souplesse reste un choix de \
l'entreprise, révisable si la productivité venait à baisser ». Cet élément justifie \
directement l'idée que la direction ne considère pas le télétravail comme acquis \
définitivement : il reste conditionné à un résultat (la productivité), ce qui en fait un \
choix réversible plutôt qu'un droit.

Ce corrigé fonctionne parce qu'il (1) cite un élément EXACT du texte, (2) explique \
pourquoi cet élément répond à la consigne, sans ajouter d'information absente du \
document.

## 10. Fiche mémo

- Un verbe opérateur = une action précise attendue, jamais interchangeable avec un autre.
- Une consigne à plusieurs parties = une checklist à cocher intégralement.
- Relever/citer ≠ reformuler ≠ expliquer ≠ justifier : ne confonds jamais ces verbes.
- Comparer = toujours mentionner les DEUX éléments comparés.
- Avant de rendre ta copie : relis la consigne une dernière fois et vérifie chaque \
exigence.
"""


def fr02_course_markdown() -> str:
    return """# FR02 — Lire et comprendre un document

**Statut : contenu de validation technique provisoire (ticket #94) — PAS un examen CESS \
officiel.**

## 1. Ce que tu dois savoir faire à l'examen

Face à un document inconnu, tu dois pouvoir identifier rapidement qui l'a écrit, pour qui, \
dans quel but, et en dégager l'idée principale ainsi que les idées secondaires qui la \
complètent — avant même de répondre à des questions précises sur son contenu.

## 2. Théorie progressive

Comprendre un document commence par construire sa **situation de communication** : qui \
parle (l'auteur ou l'énonciateur), à qui (le destinataire), pourquoi (l'intention), dans \
quel contexte, sur quel support, et dans quel genre de texte (article, lettre, note, \
texte informatif...).

Ensuite seulement vient la lecture du contenu lui-même : un **survol** rapide pour \
repérer la structure générale, puis un **repérage** des informations utiles selon la \
question posée, puis une lecture sélective (seulement les passages utiles) ou intégrale \
(tout le texte) selon le besoin.

Enfin, il faut distinguer l'**idée principale** (ce dont parle vraiment le texte, en une \
phrase) des **idées secondaires** (les éléments qui la précisent, l'illustrent ou la \
nuancent).

## 3. Définitions importantes

- **Situation de communication** : l'ensemble auteur/destinataire/intention/contexte/genre \
d'un document.
- **Idée principale** : le message central du texte, ce qu'il faudrait retenir si on ne \
pouvait garder qu'une seule phrase.
- **Idée secondaire** : une information qui développe, illustre ou nuance l'idée \
principale, sans être le sujet central du texte.
- **Sens explicite** : ce qui est écrit noir sur blanc, sans besoin de déduction.
- **Vocabulaire en contexte** : le sens d'un mot déduit de la phrase et du texte qui \
l'entourent, plutôt que d'une définition générale apprise par cœur.

## 4. Méthode étape par étape

1. Identifie d'abord le genre du document (article, lettre, note interne, texte \
informatif...) à partir d'indices visuels et de style.
2. Repère l'auteur/l'énonciateur et le destinataire si le texte le permet.
3. Fais un survol rapide : titre, premières et dernières phrases de chaque paragraphe.
4. Formule l'idée principale en UNE phrase, avant de chercher les détails.
5. Relis plus lentement pour repérer les idées secondaires, paragraphe par paragraphe.
6. Pour un mot inconnu, relis la phrase entière (et la précédente si besoin) pour en \
déduire le sens à partir du contexte, plutôt que de deviner au hasard.

## 5. Exemples commentés

**Extrait :** « La nouvelle ligne, numérotée 47, circulera toutes les vingt minutes aux \
heures de pointe et reliera la gare centrale au cœur de la zone industrielle en moins de \
vingt-cinq minutes. »

**Analyse commentée :** ce passage donne des idées SECONDAIRES (fréquence, durée du \
trajet) qui précisent l'idée principale du texte (la création d'une nouvelle ligne de bus \
pour la zone industrielle), sans être elles-mêmes le sujet central de l'article.

**Extrait d'une lettre professionnelle :** « Je me permets de vous écrire afin de \
solliciter un congé de deux semaines... »

**Analyse commentée :** la situation de communication est ici immédiatement repérable : \
l'auteur (« je ») s'adresse directement à un destinataire nommé, dans une intention \
précise (demander un congé) — typique du genre « lettre professionnelle », à distinguer \
d'un article qui ne s'adresse à personne en particulier.

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse** (« Quelle est l'idée principale ? ») : une réponse qui recopie la \
première phrase du texte mot pour mot, sans reformuler ni synthétiser.
- ✅ **Bonne réponse** : une phrase reformulée avec ses propres mots, qui résume ce dont \
parle VRAIMENT l'ensemble du texte, pas seulement son premier paragraphe.

## 7. Pièges et erreurs fréquentes

- Confondre l'idée principale avec le premier détail rencontré dans le texte.
- Oublier de vérifier le genre du document avant d'interpréter son intention.
- Deviner le sens d'un mot inconnu sans relire son contexte immédiat.
- Répondre à partir de connaissances personnelles plutôt que du contenu réel du document.

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Essaie avant de regarder la correction</summary>

À partir du titre seul « Article — Une nouvelle ligne de bus pour la zone industrielle », \
formule une hypothèse sur l'idée principale du texte, avant de le lire en entier.

<details>
<summary>Voir la correction expliquée</summary>

Une hypothèse raisonnable à partir du seul titre : le texte annonce probablement la \
création d'une nouvelle ligne de bus desservant une zone industrielle. Après lecture \
complète, cette hypothèse se confirme et se précise : la ligne répond à un besoin de \
transport en commun pour les employés de la zone, jusque-là mal desservie. Cet exercice \
montre l'intérêt du survol avant la lecture complète.
</details>
</details>

<details>
<summary>Exercice 2 — Essaie avant de regarder la correction</summary>

Dans la phrase « Ce système enregistre également des informations utiles pour analyser \
les habitudes des clients », que signifie ici le mot « habitudes », déduit du contexte ?

<details>
<summary>Voir la correction expliquée</summary>

Dans ce contexte, « habitudes » désigne les comportements récurrents des clients \
(horaires d'achat, produits achetés ensemble, moyens de paiement préférés) — un sens \
précis déduit de la phrase et du paragraphe qui l'entourent, pas le sens très général du \
mot dans le dictionnaire.
</details>
</details>

## 9. Corrigés très expliqués

**Question :** « Quel est le genre de ce texte et quelle est son intention ? » (à propos \
d'une lettre de demande de congé)

**Corrigé expliqué :** il s'agit d'une lettre professionnelle, reconnaissable à sa \
formule d'ouverture (« Madame Kowalski »), à l'usage de la première personne, et à sa \
formule de politesse finale. Son intention est de solliciter un congé de deux semaines, \
tout en anticipant les objections possibles (elle propose une solution pour assurer la \
continuité du travail). Ce corrigé fonctionne car il identifie le genre à partir d'indices \
concrets, puis relie l'intention à un passage précis du texte.

## 10. Fiche mémo

- Toujours identifier la situation de communication AVANT le contenu détaillé.
- Idée principale = une seule phrase de synthèse, jamais une simple citation.
- Idée secondaire = précise ou illustre l'idée principale, sans être le sujet central.
- Un mot inconnu se comprend toujours à partir de son contexte immédiat.
- Ne jamais répondre à partir de ce que tu sais déjà : réponds à partir du texte.
"""


def fr03_course_markdown() -> str:
    return f"""# FR03 — Implicite, inférences et justification

**Statut : contenu de validation technique provisoire (ticket #94) — PAS un examen CESS \
officiel.**

## 1. Ce que tu dois savoir faire à l'examen

Tu dois pouvoir distinguer ce qu'un texte dit clairement (l'explicite) de ce qu'il laisse \
seulement entendre (l'implicite), et être capable de justifier une déduction à l'aide \
d'un indice PRÉCIS du texte — jamais en inventant une information absente.

## 2. Théorie progressive

Un texte ne dit jamais tout explicitement. Beaucoup d'informations doivent être \
**déduites** à partir d'**indices** : un détail, un choix de mot, une réaction, une \
omission. Déduire correctement s'appelle **inférer** — c'est différent d'inventer : une \
inférence s'appuie toujours sur un ou plusieurs indices réellement présents dans le \
texte, alors qu'une invention ajoute une information sans aucun appui textuel.

## 3. Définitions importantes

- **Explicite** : ce qui est écrit clairement, sans besoin de déduction.
- **Implicite** : ce qui n'est pas écrit directement, mais que le texte laisse entendre.
- **Indice** : un élément concret du texte (mot, détail, comportement) qui permet une \
déduction.
- **Inférence** : une conclusion raisonnable tirée d'un ou plusieurs indices du texte.
- **Invention** : une information ajoutée sans aucun appui dans le texte — toujours à \
proscrire.

## 4. Méthode étape par étape

Méthode 1 — **INDICE → RAISONNEMENT → CONCLUSION** :
1. Repère un indice précis dans le texte (une phrase, un mot, un détail).
2. Explique le raisonnement qui relie cet indice à une idée qui n'est pas écrite \
directement.
3. Formule une conclusion claire, qui reste cohérente avec l'ensemble du texte.

Méthode 2 — **PREUVE → EXPLICATION → CONCLUSION** (pour une justification directe) :
1. Cite la preuve exacte (une citation ou un fait du texte).
2. Explique en quoi cette preuve répond à la question posée.
3. Conclus clairement, sans ambiguïté.

## 5. Exemples commentés

### {FR03_TEXT1_TITLE}

{FR03_TEXT1_TEXT}

**Question :** le texte suggère que Karim est nerveux pour son premier jour, sans le dire \
explicitement. Justifie.

**Analyse commentée (INDICE → RAISONNEMENT → CONCLUSION) :** INDICE : « il tendit sa \
carte d'identité... d'une main légèrement tremblante ». RAISONNEMENT : une main qui \
tremble est un signe physique associé au stress ou à la nervosité. CONCLUSION : Karim est \
donc probablement nerveux pour ce premier jour, même si le texte ne le dit jamais avec le \
mot « nerveux ».

### {FR03_TEXT2_TITLE}

{FR03_TEXT2_TEXT}

**Question :** le rapport laisse entendre que la situation de la ligne 3 est plus \
préoccupante que le ton mesuré du rapport ne le suggère. Justifie avec la méthode \
PREUVE → EXPLICATION → CONCLUSION.

**Analyse commentée :** PREUVE : « l'équipe de maintenance a été sollicitée à plusieurs \
reprises, parfois en dehors des horaires habituels ». EXPLICATION : des interventions \
répétées et en dehors des horaires normaux indiquent un problème qui dépasse une simple \
panne ponctuelle. CONCLUSION : la situation est donc plus sérieuse que ne le suggère le \
ton mesuré du rapport, ce que confirme la phrase soulignée par le directeur en réunion.

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse** : « Karim est stressé parce que c'est toujours stressant un \
premier jour de travail. » → ne s'appuie sur AUCUN indice précis du texte, uniquement sur \
une connaissance générale : c'est une invention, pas une inférence.
- ✅ **Bonne réponse** : « Karim est probablement nerveux : le texte précise que sa main \
tremblait légèrement en tendant sa carte d'identité, un signe physique de stress. »

## 7. Pièges et erreurs fréquentes

- Confondre une inférence avec une opinion personnelle non appuyée sur le texte.
- Citer un indice sans expliquer le raisonnement qui mène à la conclusion.
- Donner une justification trop vague (« parce que c'est écrit comme ça ») au lieu d'une \
preuve précise.
- Refuser toute conclusion qui n'a qu'UN SEUL indice possible dans un texte qui en \
propose plusieurs, alors qu'accepter une conclusion raisonnable parmi plusieurs indices \
valables est parfois correct.

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Essaie avant de regarder la correction</summary>

Dans le texte sur Karim, relève un indice qui suggère qu'il est quelqu'un de préparé et \
organisé, puis applique la méthode INDICE → RAISONNEMENT → CONCLUSION.

<details>
<summary>Voir la correction expliquée</summary>

INDICE : « Il resta assis dans sa voiture, relisant une troisième fois le plan des \
bâtiments ». RAISONNEMENT : relire un document à plusieurs reprises avant d'agir est un \
comportement associé à la préparation minutieuse. CONCLUSION : Karim semble être une \
personne organisée, qui aime être bien préparée avant une situation nouvelle.
</details>
</details>

<details>
<summary>Exercice 2 — Essaie avant de regarder la correction</summary>

Dans le rapport du responsable qualité, pourquoi peut-on penser que le directeur est \
préoccupé malgré le ton globalement rassurant du texte ?

<details>
<summary>Voir la correction expliquée</summary>

Le directeur a souligné en réunion la phrase « la situation reste sous contrôle, mais \
elle mériterait de ne pas se prolonger sur plusieurs mois sans intervention technique ». \
Souligner spécifiquement cette phrase, plutôt qu'une autre plus rassurante du rapport, \
suggère que c'est justement ce point qui l'inquiète, malgré le ton mesuré de l'ensemble du \
rapport.
</details>
</details>

## 9. Corrigés très expliqués

**Question :** le texte sur Karim ne dit jamais qu'il est timide, mais le suggère. \
Justifie à l'aide de deux indices.

**Corrigé expliqué :** premier indice : à la pause de midi, il choisit une table où une \
seule personne est installée plutôt que de s'approcher d'un groupe plus animé — un choix \
qui évite le contact avec plusieurs personnes à la fois. Deuxième indice : il reste debout \
dans le hall d'accueil alors qu'un canapé est disponible, ce qui peut traduire une gêne à \
s'installer confortablement dans un lieu inconnu. Ensemble, ces deux indices suggèrent une \
certaine réserve, sans que le texte l'affirme jamais directement — c'est une inférence \
solide, appuyée sur deux éléments concrets et convergents.

## 10. Fiche mémo

- Explicite = écrit clairement ; implicite = à déduire à partir d'indices réels.
- Une inférence s'appuie TOUJOURS sur un indice présent dans le texte.
- Méthode : INDICE → RAISONNEMENT → CONCLUSION, ou PREUVE → EXPLICATION → CONCLUSION.
- Ne jamais conclure à partir d'une connaissance générale non appuyée sur le texte.
- Plusieurs conclusions peuvent être valables si chacune est bien justifiée par un indice \
réel.
"""


def fr04_course_markdown() -> str:
    return f"""# FR04 — Écrire correctement et organiser ses idées

**Statut : contenu de validation technique provisoire (ticket #94) — PAS un examen CESS \
officiel.**

## 1. Ce que tu dois savoir faire à l'examen

Tu dois pouvoir transformer des idées en vrac, ou un texte mal organisé, en un écrit \
clair et structuré : adapté à son destinataire, à son intention et à son genre, avec une \
introduction, un développement organisé et une conclusion.

## 2. Théorie progressive

Avant d'écrire, il faut définir la **situation de communication** du texte à produire : \
qui va le lire (destinataire), dans quel but (intention), et sous quelle forme (genre : \
courriel, lettre, note...), ce qui détermine le **registre** (plus ou moins formel) à \
utiliser.

Ensuite vient la **planification** : organiser les idées disponibles dans un **ordre \
logique**, généralement en paragraphes, chacun développant une idée, reliés par des \
**connecteurs logiques** (« cependant », « par conséquent », « de plus »...) qui rendent \
la **progression** du texte claire pour le lecteur.

## 3. Définitions importantes

- **Registre** : le niveau de langue adapté à la situation (familier, courant, soutenu/\
professionnel).
- **Planification** : l'étape où l'on organise ses idées avant de rédiger.
- **Connecteur logique** : un mot ou une expression qui relie deux idées en précisant \
leur relation (opposition, conséquence, addition, exemple...).
- **Progression** : la manière dont un texte avance d'idée en idée sans rupture ni \
répétition inutile.
- **Reprise** : un mot ou un pronom qui renvoie à un élément déjà mentionné, pour éviter \
de le répéter.

## 4. Méthode étape par étape

1. Identifie le destinataire, l'intention et le genre attendu du texte à produire.
2. Liste toutes les informations à inclure, sans te soucier de l'ordre au départ.
3. Regroupe les informations proches par thème : chaque groupe deviendra un paragraphe.
4. Choisis un ordre logique entre les groupes (chronologique, du plus important au moins \
important, cause puis conséquence...).
5. Rédige une introduction qui présente clairement le sujet et l'intention.
6. Rédige chaque paragraphe en reliant les idées avec des connecteurs logiques.
7. Termine par une conclusion qui reprend l'essentiel ou propose une suite.

## 5. Exemples commentés

### {FR04_IDEAS_JUMBLE_TITLE}

{FR04_IDEAS_JUMBLE_TEXT}

**Analyse commentée :** ces idées, prises une par une, ne forment pas un texte. Il faut \
d'abord les regrouper (la demande elle-même / les raisons personnelles / les garanties \
proposées à l'employeur), puis les organiser en paragraphes reliés par des connecteurs \
(« Je souhaiterais... », « En effet... », « Afin de garantir... »).

### {FR04_DISORGANIZED_TITLE}

{FR04_DISORGANIZED_TEXT}

**Analyse commentée :** ce compte-rendu suit en réalité un ordre chronologique logique \
(panne constatée → intervention → durée/conséquence → résolution), mais les paragraphes \
sont mélangés. Un texte bien organisé suivrait l'ordre B → A → D → C, avec des \
connecteurs temporels (« d'abord », « ensuite », « finalement ») pour guider le lecteur.

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse** : un texte qui reprend les idées en vrac dans le désordre, sans \
connecteur ni paragraphe distinct, difficile à suivre.
- ✅ **Bonne réponse** : un texte en trois paragraphes distincts (demande / justification / \
garanties), reliés par des connecteurs logiques, avec une introduction et une conclusion \
claires.

## 7. Pièges et erreurs fréquentes

- Écrire sans planifier, en espérant que l'ordre viendra naturellement.
- Répéter le même mot plusieurs fois au lieu d'utiliser une reprise (pronom, synonyme).
- Oublier les connecteurs logiques, ce qui rend les liens entre idées peu clairs.
- Ne pas adapter le registre au destinataire (trop familier pour un courriel \
professionnel, par exemple).

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Essaie avant de regarder la correction</summary>

À partir des idées en vrac sur l'aménagement d'horaires, propose un ordre logique en 3 \
groupes de paragraphes.

<details>
<summary>Voir la correction expliquée</summary>

Un ordre logique possible : Paragraphe 1 (la demande elle-même : commencer/finir une \
heure plus tôt) ; Paragraphe 2 (la raison personnelle : récupérer son fils à l'école) ; \
Paragraphe 3 (les garanties données à l'employeur : trois ans sans retard, période \
d'essai proposée, accord déjà obtenu de la responsable directe). Cet ordre va du plus \
concret (la demande) vers ce qui la justifie et la rend acceptable pour l'employeur.
</details>
</details>

<details>
<summary>Exercice 2 — Essaie avant de regarder la correction</summary>

Dans le compte-rendu de panne désorganisé, quel connecteur logique pourrait relier le \
paragraphe B (constat de la panne) au paragraphe A (intervention du technicien) ?

<details>
<summary>Voir la correction expliquée</summary>

Un connecteur temporel comme « Peu après » ou « C'est pourquoi » conviendrait : « La \
machine numéro 4 s'est arrêtée brutalement vers 13h15 [...]. Peu après, le technicien de \
maintenance est intervenu vers 14h30... ». Ce connecteur marque à la fois l'enchaînement \
chronologique et le lien de cause à conséquence entre les deux paragraphes.
</details>
</details>

## 9. Corrigés très expliqués

**Consigne :** rédige un court paragraphe expliquant pourquoi la pause de midi trop \
courte pose problème, à partir des idées suivantes (en vrac) : « pause réduite à trente \
minutes », « repas pris devant un écran », « fatigue en fin d'après-midi ».

**Corrigé expliqué :** « Dans de nombreuses entreprises, la pause de midi ne dure plus \
qu'une trentaine de minutes. Ce temps réduit pousse souvent les employés à manger \
rapidement, parfois devant un écran, sans vraie coupure dans leur journée. Cette absence \
de pause réelle peut alors entraîner une fatigue plus importante en fin d'après-midi. » \
Ce corrigé fonctionne car il relie les trois idées avec des connecteurs logiques \
(« Ce temps réduit... », « sans vraie coupure... », « peut alors entraîner... ») dans un \
ordre de cause à conséquence clair.

## 10. Fiche mémo

- Toujours définir destinataire / intention / genre AVANT de commencer à écrire.
- Planifier : regrouper les idées par thème avant de les mettre en paragraphes.
- Un connecteur logique par transition importante entre deux idées.
- Utiliser des reprises (pronoms, synonymes) plutôt que de répéter le même mot.
- Introduction claire + développement organisé + conclusion = structure minimale.
"""


def fr05_course_markdown() -> str:
    return f"""# FR05 — Corriger et améliorer un texte

**Statut : contenu de validation technique provisoire (ticket #94) — PAS un examen CESS \
officiel.**

## 1. Ce que tu dois savoir faire à l'examen

Tu dois pouvoir relire un texte de façon méthodique pour repérer de vraies erreurs \
(accords, homophones, ponctuation, répétitions, registre...) et les corriger sans changer \
le sens du message ni en inventer un nouveau.

## 2. Théorie progressive

Réviser un texte n'est pas relire une seule fois « pour voir » : c'est appliquer une \
méthode qui enchaîne plusieurs actions précises : **repérer** une erreur potentielle, \
**corriger** si c'est une vraie erreur, **remplacer** un mot mal choisi, **supprimer** une \
répétition inutile, **ajouter** un mot manquant (connecteur, ponctuation), ou **déplacer** \
un élément mal placé dans la phrase.

Les erreurs les plus fréquentes concernent la **cohérence** générale du texte, les \
**répétitions**, les **connecteurs** manquants ou mal choisis, la **syntaxe**, les \
**accords**, les **homophones**, la **ponctuation**, le **lexique**, le **registre** et la \
**typographie** (majuscules, espaces).

## 3. Définitions importantes

- **Accord** : l'adaptation d'un mot (verbe, adjectif...) à son sujet ou à son nom \
(genre, nombre).
- **Homophone** : deux mots qui se prononcent pareil mais s'écrivent différemment et ont \
un sens différent (ex. « a »/« à », « on »/« ont », « ou »/« où »).
- **Registre** : le niveau de langue d'un texte (familier, courant, soutenu/\
professionnel) — il doit rester cohérent du début à la fin d'un même texte.
- **Cohérence** : le fait qu'un texte reste logique et compréhensible d'un bout à l'autre, \
sans contradiction.

## 4. Méthode étape par étape

1. Lis le texte une première fois entièrement, sans corriger, pour comprendre le sens \
global.
2. Relis phrase par phrase en vérifiant les accords sujet-verbe et les accords dans le \
groupe nominal.
3. Vérifie chaque homophone grammatical (a/à, on/ont, ou/où, ce/se...).
4. Vérifie la ponctuation et les majuscules en début de phrase.
5. Repère les répétitions inutiles et remplace-les par un synonyme ou un pronom.
6. Vérifie que le registre reste cohérent du début à la fin (pas de familiarité soudaine \
dans un texte professionnel).
7. Relis une dernière fois en vérifiant que le sens d'origine n'a pas changé.

## 5. Exemples commentés

### {FR05_FLAWED1_TITLE}

{FR05_FLAWED1_TEXT}

**Version corrigée :**

{FR05_FLAWED1_CORRECTED}

**Analyse commentée :** les erreurs corrigées touchent plusieurs catégories : accords \
(« on constatés » → « ont constaté »), homophones (« ou » → « où »), majuscule manquante \
(« A tout » → « À tout ») et ponctuation (ajout d'un point-virgule pour séparer deux \
idées liées). Le sens du message reste rigoureusement identique.

### {FR05_FLAWED2_TITLE}

{FR05_FLAWED2_TEXT}

**Version corrigée :**

{FR05_FLAWED2_CORRECTED}

**Analyse commentée :** ce texte mélange fautes d'orthographe (« mieu » → « meilleur », \
« sa serait » → « il serait ») et registre trop oral pour un message professionnel \
(« moi je trouve », répété plusieurs fois). La version corrigée garde le même avis, mais \
dans un registre plus soigné et sans répétitions inutiles.

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse** (corriger la note de service) : une réécriture qui change le \
sens du message original (par exemple en ajoutant une sanction non mentionnée dans le \
texte de départ).
- ✅ **Bonne réponse** : une correction qui garde EXACTEMENT le même contenu et la même \
intention, en ne touchant qu'à la forme (orthographe, accords, ponctuation, registre).

## 7. Pièges et erreurs fréquentes

- Corriger le sens du texte au lieu de corriger seulement sa forme.
- Oublier de vérifier les homophones grammaticaux, souvent invisibles à une lecture \
rapide.
- Laisser un registre incohérent (mélange de tournures familières et professionnelles).
- Ajouter des informations absentes du texte original sous prétexte de « l'améliorer ».

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Essaie avant de regarder la correction</summary>

Dans la phrase « Plusieurs employés on constatés que de la vaisselle sale rester parfois \
plusieurs jours dans le évier », relève TOUTES les erreurs avant de comparer avec la \
correction.

<details>
<summary>Voir la correction expliquée</summary>

Erreurs : « on constatés » → « ont constaté » (accord sujet-verbe, pluriel) ; « rester » \
→ « reste » (accord de conjugaison) ; « le évier » → « l'évier » (élision obligatoire \
devant une voyelle). Phrase corrigée : « Plusieurs employés ont constaté que de la \
vaisselle sale reste parfois plusieurs jours dans l'évier. »
</details>
</details>

<details>
<summary>Exercice 2 — Essaie avant de regarder la correction</summary>

Réécris la phrase « Le logiciel d'avant était mieu je trouve, même si il était un peu \
vieux il marchait bien au moins » dans un registre plus soigné.

<details>
<summary>Voir la correction expliquée</summary>

Version corrigée possible : « Le logiciel précédent était meilleur, à mon avis : même \
s'il était un peu ancien, il fonctionnait bien. » Corrections : « mieu » → « meilleur » \
(orthographe et niveau de langue), « je trouve » déplacé et reformulé en « à mon avis » \
(registre plus soigné), « si il » → « s'il » (élision obligatoire), « vieux »/« marchait \
bien » reformulés en des termes plus neutres (« ancien »/« fonctionnait bien »).
</details>
</details>

## 9. Corrigés très expliqués

**Consigne :** corrige la phrase « Nous somme vraiment désolé pour ce contretemps \
independant de notre volonté » en conservant exactement le même sens.

**Corrigé expliqué :** « Nous sommes vraiment désolés pour ce contretemps indépendant de \
notre volonté. » Corrections : « somme » → « sommes » (conjugaison du verbe être, \
première personne du pluriel) ; « désolé » → « désolés » (accord avec le sujet pluriel \
« nous ») ; « independant » → « indépendant » (accent manquant). Le sens du message \
(présenter des excuses pour un contretemps non maîtrisé) reste rigoureusement identique.

## 10. Fiche mémo

- Corriger la FORME, jamais le FOND : le sens d'origine ne doit jamais changer.
- Vérifier systématiquement : accords, homophones, ponctuation, registre.
- Un registre professionnel ne mélange jamais tournures familières et soignées.
- Une répétition inutile se remplace par un synonyme ou un pronom, jamais en changeant le \
sens.
- Toujours relire une dernière fois pour vérifier que rien n'a été ajouté ou perdu.
"""
