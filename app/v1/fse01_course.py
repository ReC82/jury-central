"""Contenu de cours — FSE01 « Communiquer : le schéma de communication » (ticket #96,
cahier des charges détaillé du ticket #97).

Structure reprise de `app.v1.francais_fr01_05_courses` (même convention, ticket #94) :
1. Ce que tu dois savoir faire à l'examen (objectifs observables, prérequis rappelés) —
2. Théorie progressive — 3. Définitions importantes (glossaire du seul vocabulaire
enseigné) — 4. Méthode étape par étape — 5. Exemples commentés (mail, affiche, réseau
social — les trois applications explicitement demandées par le ticket #97) — 6. Mauvaises
réponses comparées aux bonnes — 7. Pièges et erreurs fréquentes — 8. Exercices guidés
(corrigés masqués par défaut, `<details>`/`<summary>`) — 9. Corrigés très expliqués —
10. Fiche mémo. (S'entraîner/S'évaluer sont déjà fournis génériquement par
`_uaa_space_nav.html`, ticket #22 — jamais dupliqués ici.)

Périmètre strict (ticket #96/#97, programme p. 43-45) : émetteur, récepteur, message,
code, canal/contact, contexte/référent, obstacle/bruit, rétroaction — appliqués à un mail,
une affiche et une publication sur réseau social. Aucune autre notion (fonctions du
langage de Jakobson, etc.) n'est introduite : elle n'est pas au programme de ce
mini-cours."""

from app.v1.fse01_content import (
    FSE01_AFFICHE_TEXT,
    FSE01_AFFICHE_TITLE,
    FSE01_MAIL_TEXT,
    FSE01_MAIL_TITLE,
    FSE01_SOCIAL_TEXT,
    FSE01_SOCIAL_TITLE,
)


def fse01_course_markdown() -> str:
    return f"""# FSE01 — Communiquer : le schéma de communication

## 1. Ce que tu dois savoir faire à l'examen

Tu dois être capable d'identifier, dans une situation de communication réelle (un mail, \
une affiche, une publication sur un réseau social...), qui parle, à qui, ce qui est \
transmis, avec quel système de signes, par quel support, et dans quel contexte. Tu dois \
aussi pouvoir repérer ce qui empêche un message de bien passer, et dire si une réponse du \
récepteur est possible ou non selon le support utilisé.

Ce cours est le premier de la Formation sociale et économique : il ne suppose aucun \
prérequis particulier.

## 2. Théorie progressive

Communiquer, c'est transmettre quelque chose à quelqu'un. Même dans les situations les \
plus simples (un SMS, une affiche, un post sur un réseau social), cette transmission \
repose toujours sur les mêmes éléments. Les repérer systématiquement permet de comprendre \
pourquoi une communication réussit — ou pourquoi elle échoue.

Une communication met toujours en relation un **émetteur** (celui ou celle qui envoie le \
message) et un **récepteur** (celui ou celle qui le reçoit). Entre les deux circule un \
**message** : ce qui est réellement transmis (une information, une demande, une \
publicité...).

Pour que ce message soit compris, il doit être mis en forme à l'aide d'un **code** : un \
système de signes partagé par l'émetteur et le récepteur (une langue, mais aussi des \
images, des couleurs, des pictogrammes, des émojis...). Ce code a besoin d'un support \
concret pour circuler : c'est le **canal** (aussi appelé contact) — le moyen matériel ou \
technique par lequel le message est transmis (une ligne internet, une feuille affichée, \
une plateforme en ligne...).

Un même message peut enfin être compris différemment selon le **contexte** (aussi appelé \
référent) : la situation, le moment, le lieu ou le sujet dont il est question. Un même mot \
n'a pas le même sens dans un contexte professionnel ou dans une conversation entre amis.

Deux autres éléments permettent d'expliquer ce qui se passe concrètement dans une \
interaction réelle : un **obstacle** (ou bruit) est tout ce qui perturbe la transmission \
du message — une coupure technique, un bruit ambiant, un mot mal choisi, une information \
manquante. La **rétroaction** est la réponse que le récepteur peut renvoyer à l'émetteur ; \
elle n'est pas toujours possible : elle dépend directement du canal utilisé. Un mail ou un \
réseau social permettent une rétroaction rapide et visible ; une affiche, elle, ne permet \
en général aucune rétroaction directe vers son émetteur.

## 3. Définitions importantes

- **Émetteur** : la personne (ou l'organisation) qui envoie le message.
- **Récepteur** : la personne (ou le groupe de personnes) à qui le message est destiné.
- **Message** : ce qui est réellement transmis — l'information, la demande, l'annonce.
- **Code** : le système de signes utilisé pour mettre le message en forme (langue, images, \
couleurs, pictogrammes, émojis...). L'émetteur et le récepteur doivent partager le même \
code pour que le message soit compris.
- **Canal (ou contact)** : le support matériel ou technique par lequel le message \
circule (une connexion internet, une feuille affichée, une plateforme en ligne...). Le \
canal, c'est PAR OÙ passe le message ; le code, c'est AVEC QUOI il est construit — les deux \
ne doivent jamais être confondus.
- **Contexte (ou référent)** : la situation, le sujet ou les circonstances qui permettent \
de donner son sens exact au message.
- **Obstacle (ou bruit)** : tout ce qui perturbe ou empêche la bonne transmission du \
message (panne technique, bruit ambiant, formulation ambiguë, information manquante...).
- **Rétroaction** : la réponse que le récepteur peut renvoyer à l'émetteur. Sa possibilité \
dépend du canal : certains canaux la permettent immédiatement et publiquement, d'autres ne \
la permettent pas du tout.

## 4. Méthode étape par étape

Face à une situation de communication (un document, une affiche, une publication...), \
procède toujours dans cet ordre :

1. Identifie l'**émetteur** : qui a produit ce message ?
2. Identifie le **récepteur** : à qui ce message s'adresse-t-il ?
3. Résume en une phrase le **message** : qu'est-ce qui est réellement transmis ?
4. Observe le **code** utilisé : quelle(s) langue(s), quelles images, quelles couleurs, \
quels symboles ?
5. Identifie le **canal** : par quel support concret le message circule-t-il ?
6. Précise le **contexte** : dans quelle situation ce message est-il émis ?
7. Cherche un éventuel **obstacle** : quelque chose a-t-il perturbé ou pourrait-il \
perturber la transmission ?
8. Demande-toi si une **rétroaction** est possible : le récepteur peut-il répondre à \
l'émetteur ? Par quel moyen, et à quelle vitesse ?

## 5. Exemples commentés

### Exemple 1 — {FSE01_MAIL_TITLE}

{FSE01_MAIL_TEXT}

**Analyse commentée :**
- Émetteur : Karim Haddad, candidat à un emploi.
- Récepteur : le service recrutement des Entrepôts Dufresne.
- Message : une candidature pour un poste de manutentionnaire.
- Code : la langue française écrite, mise en forme selon les codes du mail professionnel \
(formule d'appel, présentation, pièce jointe).
- Canal : la messagerie électronique, qui dépend elle-même d'une connexion internet.
- Contexte : une procédure de recrutement pour un poste précis.
- Obstacle : une coupure de connexion a interrompu l'envoi avant la fin du message et \
avant l'ajout du CV en pièce jointe — un obstacle purement technique, indépendant de la \
qualité de la candidature elle-même.
- Rétroaction : le service recrutement a pu répondre directement à Karim pour signaler le \
problème et lui demander de renvoyer sa candidature complète — le canal (le mail) rend \
cette rétroaction rapide et facile.

### Exemple 2 — {FSE01_AFFICHE_TITLE}

{FSE01_AFFICHE_TEXT}

**Analyse commentée :**
- Émetteur : le Service public de Wallonie (SPW), via sa campagne de sécurité routière.
- Récepteur : les automobilistes qui circulent sur cette route.
- Message : inciter à ralentir à l'approche d'un passage piéton.
- Code : un texte court et percutant, une image (silhouette d'enfant), des couleurs \
porteuses de sens (le rouge signale le danger), un logo institutionnel.
- Canal : un panneau d'affichage fixe, installé en bordure de route.
- Contexte : la sécurité routière, à proximité d'un passage piéton.
- Obstacle : le conducteur lit l'affiche en quelques secondes, à pleine vitesse, souvent \
en étant partiellement concentré sur la conduite — la rapidité de lecture et la distraction \
possible limitent ce que le message peut transmettre.
- Rétroaction : une affiche ne permet, par nature, aucune rétroaction directe et \
immédiate vers son émetteur ; le conducteur ne peut pas « répondre » au panneau. Seul le \
QR code permet une forme de rétroaction indirecte et très différée, si l'automobiliste le \
scanne plus tard.

### Exemple 3 — {FSE01_SOCIAL_TITLE}

{FSE01_SOCIAL_TEXT}

**Analyse commentée :**
- Émetteur : l'entreprise Techno Services Wallonie.
- Récepteur : les utilisateurs du réseau social susceptibles de chercher un emploi dans \
ce secteur.
- Message : une offre d'emploi de technicien·ne de maintenance industrielle.
- Code : un texte court, des émojis, des hashtags — des signes propres au langage des \
réseaux sociaux, différents de ceux d'un mail professionnel.
- Canal : une plateforme de réseau social en ligne.
- Contexte : une campagne de recrutement dans le secteur de la maintenance industrielle.
- Obstacle : l'absence d'information sur le salaire crée une incompréhension visible \
(le commentaire de Julien P.) — un manque d'information dans le message lui-même peut \
constituer un obstacle à une communication réussie, même sans aucune panne technique.
- Rétroaction : très visible et rapide — les commentaires, les partages, et la réponse de \
l'entreprise au commentaire de Fatima B. montrent que ce canal permet une rétroaction \
publique, immédiate, et même un dialogue (l'émetteur répond à son tour à une réaction du \
récepteur).

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse** (question : « Quel est le canal utilisé dans le mail de \
Karim ? ») : « Le français. » → confond le canal (le support de transmission) avec le \
code (le système de signes utilisé).
- ✅ **Bonne réponse** : « Le canal est la messagerie électronique, qui dépend d'une \
connexion internet ; le français écrit, lui, est le code utilisé pour rédiger le \
message. »

- ❌ **Mauvaise réponse** (question : « Une affiche permet-elle une rétroaction ? ») : \
« Oui, parce que n'importe qui peut réagir à un message. » → ignore que la rétroaction \
dépend concrètement du canal utilisé, pas d'une possibilité théorique.
- ✅ **Bonne réponse** : « Non, pas directement : une affiche ne permet pas au récepteur de \
répondre immédiatement à son émetteur. Seul le QR code offre une rétroaction indirecte et \
différée, si le récepteur choisit de le scanner. »

## 7. Pièges et erreurs fréquentes

- **Confondre canal et code** : le canal est le support PAR OÙ passe le message (une \
connexion internet, une feuille affichée) ; le code est le système de signes AVEC LEQUEL \
le message est construit (une langue, des images, des couleurs). Un même code peut \
circuler par différents canaux, et un même canal peut transporter différents codes.
- **Oublier l'obstacle quand il n'est pas technique** : un obstacle n'est pas toujours une \
panne (coupure de connexion) — un manque d'information ou une formulation ambiguë peuvent \
aussi perturber une communication, comme dans l'exemple du réseau social.
- **Croire que la rétroaction est toujours possible** : elle dépend du canal. Un mail ou \
un réseau social la permettent facilement ; une affiche, en général, ne la permet pas \
directement.
- **Confondre message et sujet général** : le message est ce qui est RÉELLEMENT transmis \
dans cette situation précise (« ralentir à l'approche de ce passage piéton »), pas le \
thème général (« la sécurité routière »).

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Annoter le schéma de l'affiche (essaie avant de regarder la \
correction)</summary>

Reprends l'affiche de sécurité routière (exemple 2). Pour chacun des six éléments du \
schéma (émetteur, récepteur, message, code, canal, contexte), note en une phrase ce qui \
correspond, PUIS indique si une rétroaction directe est possible et pourquoi.

<details>
<summary>Voir la correction expliquée</summary>

- Émetteur : le Service public de Wallonie (organisme à l'origine de la campagne).
- Récepteur : les automobilistes circulant sur cette route.
- Message : inciter les conducteurs à ralentir près d'un passage piéton.
- Code : texte court, image (silhouette d'enfant), couleurs (rouge = danger), logo \
institutionnel.
- Canal : un panneau d'affichage fixe installé en bordure de route.
- Contexte : la sécurité routière, à proximité d'un passage piéton.
- Rétroaction : non, pas directement — une affiche ne permet pas au conducteur de répondre \
immédiatement à son émetteur ; seul le QR code permet une rétroaction indirecte et très \
différée.

Ce corrigé fonctionne parce qu'il traite les six éléments un par un, sans les mélanger, et \
qu'il justifie la réponse sur la rétroaction par une caractéristique réelle du canal \
(l'affiche), pas par une impression générale.
</details>
</details>

<details>
<summary>Exercice 2 — Analyser la candidature de Karim (essaie avant de regarder la \
correction)</summary>

Reprends le mail de Karim Haddad (exemple 1). Identifie précisément l'obstacle qui a \
perturbé cette communication, explique sa conséquence concrète pour le récepteur, puis \
explique comment la rétroaction du service recrutement permet de résoudre le problème.

<details>
<summary>Voir la correction expliquée</summary>

L'obstacle est une coupure de connexion internet survenue pendant la rédaction du mail de \
Karim : son logiciel de messagerie a envoyé automatiquement le message resté inactif, \
alors qu'il était incomplet et sans pièce jointe. Conséquence concrète pour le récepteur : \
le service recrutement reçoit un message qui s'arrête en pleine phrase, sans CV, ce qui \
l'empêche d'évaluer la candidature. La rétroaction (la réponse du service recrutement \
signalant le problème) permet de résoudre la situation : parce que le canal utilisé (le \
mail) autorise une réponse rapide, Karim peut être informé de l'incident et renvoyer une \
candidature complète, ce qui n'aurait pas été possible avec un canal qui ne permettrait \
aucune rétroaction.

Ce corrigé fonctionne parce qu'il distingue bien l'obstacle (la cause technique), sa \
conséquence (un message incomplet et incompréhensible), et la rétroaction (la réponse qui \
permet de corriger la situation), sans les confondre.
</details>
</details>

## 9. Corrigés très expliqués

**Question :** « Dans la publication de Techno Services Wallonie, quel élément du schéma \
de communication le commentaire de Julien P. (« Encore une offre qui ne précise pas le \
salaire... ») met-il en évidence ? »

**Corrigé expliqué :** ce commentaire met en évidence un obstacle à la communication : \
une information manquante dans le message initial (l'absence du salaire) crée une \
incompréhension, voire une insatisfaction, chez une partie des récepteurs. Ce commentaire \
est lui-même un exemple de rétroaction : grâce au canal utilisé (le réseau social), le \
récepteur peut exprimer directement et publiquement sa réaction à l'émetteur. On voit donc \
ici deux éléments du schéma à la fois : un obstacle (le manque d'information) ET une \
rétroaction (le commentaire qui le signale).

Ce corrigé fonctionne parce qu'il identifie précisément DEUX éléments du schéma présents \
dans la même phrase du document, sans se limiter à un seul, et parce qu'il justifie chaque \
élément par un passage exact du document.

## 10. Fiche mémo

- Une communication réunit toujours : émetteur, récepteur, message, code, canal, contexte.
- Canal = PAR OÙ passe le message (support) ; code = AVEC QUOI le message est construit \
(système de signes) — ne jamais confondre les deux.
- Un obstacle (bruit) peut être technique (une coupure) ou lié au contenu du message \
(une information manquante, une formulation ambiguë).
- La rétroaction dépend du canal : un mail ou un réseau social la permettent facilement ; \
une affiche, en général, ne la permet pas directement.
- Face à un document, applique toujours la méthode dans l'ordre : émetteur → récepteur → \
message → code → canal → contexte → obstacle → rétroaction.
"""
