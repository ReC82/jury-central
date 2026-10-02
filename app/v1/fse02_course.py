"""Contenu de cours — FSE02 « Les médias et leurs financements » (ticket #97, cahier des
charges détaillé).

Même structure que FSE01 (`app.v1.fse01_course`, ticket #96) : 1. Ce que tu dois savoir
faire à l'examen — 2. Théorie progressive — 3. Définitions importantes — 4. Méthode étape
par étape — 5. Exemples commentés (les trois médias explicitement demandés par le ticket
#97 : payant, gratuit/publicitaire, financé par fonds publics) — 6. Mauvaises réponses
comparées aux bonnes — 7. Pièges et erreurs fréquentes — 8. Exercices guidés (corrigés
masqués par défaut) — 9. Corrigés très expliqués — 10. Fiche mémo.

Périmètre strict (ticket #97, programme p. 43, 45) : offre médiatique, interactivité,
financement (vente, abonnement, publicité, fonds publics), lien entre financement et
recherche d'audience. Aucune autre notion (ex. régulation des médias, déontologie
journalistique) n'est introduite : elle n'est pas au programme de ce mini-cours."""

from app.v1.fse02_content import (
    FSE02_FREE_AD_TEXT,
    FSE02_FREE_AD_TITLE,
    FSE02_PAID_TEXT,
    FSE02_PAID_TITLE,
    FSE02_PUBLIC_TEXT,
    FSE02_PUBLIC_TITLE,
)


def fse02_course_markdown() -> str:
    return f"""# FSE02 — Les médias et leurs financements

## 1. Ce que tu dois savoir faire à l'examen

Tu dois être capable d'identifier comment un média se finance à partir d'un document (vente, \
abonnement, publicité, fonds publics), d'expliquer le lien entre ce financement et la \
recherche d'audience, et de comparer plusieurs médias sur ce critère.

**Prérequis** : ce cours réutilise le schéma de communication vu dans FSE01 (émetteur, \
récepteur, message, canal) — un média y est un émetteur qui transmet des messages \
(articles, émissions) à un large public de récepteurs.

## 2. Théorie progressive

Un **média** est un support qui transmet de l'information à un large public : la presse \
(journaux, magazines), la radio, la télévision, les sites d'information et les réseaux \
sociaux. L'ensemble de ces supports disponibles constitue l'**offre médiatique**.

Certains médias sont **interactifs** : ils permettent au récepteur de réagir directement \
(commenter un article, appeler une émission en direct, partager une publication), alors \
que d'autres médias plus anciens (un journal papier, une émission de radio sans ligne \
ouverte) ne le permettent pas, ou seulement de façon différée (un courrier des lecteurs \
publié la semaine suivante).

Un média a besoin de revenus pour fonctionner : rémunérer les journalistes, produire des \
contenus, maintenir un site ou une antenne. Quatre modes de financement sont possibles, \
souvent combinés :
- la **vente** : le récepteur paie pour accéder à un contenu précis (un numéro de journal \
à l'unité, un article en ligne) ;
- l'**abonnement** : le récepteur paie une somme régulière pour accéder à l'ensemble des \
contenus pendant une période ;
- la **publicité** : des annonceurs paient le média pour diffuser leurs messages \
publicitaires ; le contenu reste gratuit pour le récepteur ;
- les **fonds publics** : une dotation financée par la collectivité (impôts) permet au \
média de fonctionner sans faire payer le récepteur ni dépendre de la publicité.

Le mode de financement influence directement le comportement du média. Un média financé \
par la publicité cherche à maximiser son **audience** (le nombre de personnes qui le \
consultent), car plus l'audience est grande, plus les annonceurs sont prêts à payer — ce \
qui peut pousser à privilégier des sujets qui attirent beaucoup de clics plutôt que des \
sujets moins populaires mais utiles. Un média financé par fonds publics n'a pas cette \
contrainte : il peut traiter des sujets qui intéressent peu de monde, sans perdre de \
revenus. Un média payant (vente/abonnement) dépend, lui, de la fidélité de ses \
lecteurs/lectrices : il doit leur apporter une valeur suffisante pour qu'ils continuent à \
payer.

## 3. Définitions importantes

- **Média** : support qui transmet de l'information à un large public (presse, radio, \
télévision, sites d'information, réseaux sociaux).
- **Offre médiatique** : l'ensemble des médias disponibles pour s'informer.
- **Interactivité** : possibilité, pour le récepteur, de réagir au message (commenter, \
appeler, partager), immédiatement ou en différé.
- **Vente** : paiement pour accéder à un contenu précis et ponctuel.
- **Abonnement** : paiement régulier pour accéder à l'ensemble des contenus pendant une \
période.
- **Publicité (comme mode de financement)** : des annonceurs paient le média pour \
diffuser leurs messages ; le contenu reste gratuit pour le récepteur.
- **Fonds publics** : financement par une dotation collective (impôts), sans paiement \
direct du récepteur ni dépendance à la publicité.
- **Audience** : le nombre de personnes qui consultent un média — un enjeu central pour \
un média financé par la publicité.

## 4. Méthode étape par étape

Face à un document présentant un média, procède dans cet ordre :

1. Identifie le **type de média** (presse, radio, télévision, site, réseau social).
2. Cherche si un **prix** est mentionné (abonnement, numéro à l'unité) : indice d'un \
financement par la vente/l'abonnement.
3. Cherche la présence de **publicités** dans le document : indice d'un financement \
publicitaire.
4. Cherche une mention de **dotation**, de **service public** ou de **financement \
collectif** : indice d'un financement par fonds publics.
5. Identifie un élément d'**interactivité** (commentaires, appel en direct, partage) s'il \
est mentionné.
6. Mets en relation le mode de financement identifié avec le comportement du média \
(recherche d'audience ou non) décrit dans le document.

## 5. Exemples commentés

### Exemple 1 — {FSE02_PAID_TITLE}

{FSE02_PAID_TEXT}

**Analyse commentée :** ce média se finance par la **vente** (numéro à l'unité à 2,50 €) \
et l'**abonnement** (9 ou 14 €/mois). Le document précise explicitement l'absence de \
publicité : L'Hebdo du Littoral dépend donc entièrement de la fidélité de ses \
lecteurs/lectrices, pas de l'audience publicitaire. Son interactivité est limitée et \
différée : un encadré « Vos lettres » publié chaque semaine, pas de réaction immédiate.

### Exemple 2 — {FSE02_FREE_AD_TITLE}

{FSE02_FREE_AD_TEXT}

**Analyse commentée :** ce média est gratuit pour le récepteur et se finance \
exclusivement par la **publicité** (deux bannières publicitaires visibles, et le texte \
l'indique explicitement). Le document précise que plus un article est consulté, plus il \
génère de revenus : Le Flash Infos a donc un intérêt direct à maximiser son **audience**, \
ce qui peut l'inciter à privilégier des sujets qui attirent beaucoup de clics. Son \
interactivité est forte et immédiate : compteur de vues, partage, commentaires publics.

### Exemple 3 — {FSE02_PUBLIC_TITLE}

{FSE02_PUBLIC_TEXT}

**Analyse commentée :** ce média se finance par des **fonds publics** (une dotation \
votée chaque année). Le document précise qu'il ne diffuse aucune publicité commerciale et \
qu'il peut traiter des sujets qui intéressent peu les annonceurs (santé publique, \
éducation) — contrairement au Flash Infos, RCW n'a pas besoin de maximiser son audience \
pour obtenir des revenus. Son interactivité est forte et immédiate : une émission en \
direct où les auditeurs peuvent appeler l'antenne.

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse** (question : « Comment Le Flash Infos se finance-t-il ? ») : \
« Il est gratuit. » → décrit une conséquence (l'accès gratuit pour le récepteur), pas le \
mode de financement réel.
- ✅ **Bonne réponse** : « Le Flash Infos se finance par la publicité : les annonceurs \
paient pour que leurs messages apparaissent sur le site, ce qui permet de ne rien faire \
payer aux lecteurs. »

- ❌ **Mauvaise réponse** (question : « RCW cherche-t-elle à maximiser son audience ? ») : \
« Oui, comme tous les médias. » → généralisation incorrecte qui ignore l'information \
donnée dans le document.
- ✅ **Bonne réponse** : « Non : financée par des fonds publics, RCW ne dépend pas de la \
publicité ni du nombre de lecteurs pour obtenir des revenus, ce qui lui permet de traiter \
des sujets peu populaires sans perdre de financement. »

## 7. Pièges et erreurs fréquentes

- **Confondre « gratuit pour le récepteur » et « sans financement »** : un média gratuit \
pour son public est presque toujours financé autrement (publicité, fonds publics) — \
jamais sans aucune source de revenus.
- **Supposer qu'un média combine un seul mode de financement** : en réalité, plusieurs \
médias combinent plusieurs sources (ex. un journal avec abonnement ET un peu de \
publicité) ; reste toujours basé sur ce que le document précise réellement, sans inventer.
- **Oublier le lien entre financement et comportement du média** : identifier le mode de \
financement ne suffit pas, il faut aussi expliquer son effet (recherche d'audience ou \
non).
- **Confondre interactivité et mode de financement** : ce sont deux notions \
indépendantes — un média payant peut être interactif (forum de lecteurs) et un média \
gratuit peut ne pas l'être.

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Identifier le financement et son effet (essaie avant de regarder la \
correction)</summary>

Reprends le document du Flash Infos (exemple 2). Identifie son mode de financement, PUIS \
explique en quoi ce mode de financement peut influencer le choix des sujets traités par \
ce média.

<details>
<summary>Voir la correction expliquée</summary>

Mode de financement : la publicité (bannières publicitaires visibles, confirmé par le \
texte). Effet sur le choix des sujets : comme les revenus dépendent directement du nombre \
de vues de chaque article, Le Flash Infos a intérêt à privilégier des sujets qui attirent \
beaucoup de clics, ce qui peut l'inciter à délaisser des sujets importants mais moins \
populaires.

Ce corrigé fonctionne parce qu'il ne se limite pas à nommer le mode de financement : il \
relie explicitement ce financement à un effet concret sur le comportement du média, \
appuyé sur une information précise du document (le lien entre vues et revenus).
</details>
</details>

<details>
<summary>Exercice 2 — Comparer deux médias (essaie avant de regarder la correction)</summary>

Compare L'Hebdo du Littoral (exemple 1) et Radio Communauté Wallonie (exemple 3) : les \
deux médias évitent-ils la publicité pour la même raison ?

<details>
<summary>Voir la correction expliquée</summary>

Non, pas pour la même raison. L'Hebdo du Littoral évite la publicité parce qu'il se \
finance par la vente et l'abonnement : ses lecteurs paient directement pour un contenu \
sans publicité intrusive. RCW évite la publicité parce qu'elle est financée par des fonds \
publics : sa mission de service public ne dépend ni des lecteurs payants, ni des \
annonceurs.

Ce corrigé fonctionne parce qu'il ne se contente pas de constater un point commun (aucun \
des deux ne fait de publicité) : il explique que ce point commun repose sur deux \
logiques de financement totalement différentes, en les nommant précisément.
</details>
</details>

## 9. Corrigés très expliqués

**Question :** « Pourquoi Radio Communauté Wallonie peut-elle traiter des sujets comme la \
santé publique ou l'éducation, alors que ce sont des sujets qui intéressent peu les \
annonceurs publicitaires ? »

**Corrigé expliqué :** RCW est financée par des fonds publics (une dotation votée chaque \
année), et non par la publicité ou la vente de ses programmes. Ses revenus ne dépendent \
donc ni du nombre de personnes qui la regardent/l'écoutent, ni de l'intérêt des \
annonceurs pour un sujet donné. Un média financé par la publicité, lui, doit attirer un \
large public pour que les annonceurs continuent à payer — un sujet peu populaire mais \
important (comme la santé publique) risque d'y être moins traité. L'indépendance de RCW \
vis-à-vis de l'audience et de la publicité lui permet donc de traiter ce type de sujet \
sans perdre de revenus.

Ce corrigé fonctionne parce qu'il relie explicitement le mode de financement (fonds \
publics) à sa conséquence concrète (pas de contrainte d'audience), en comparant avec ce \
qui se passerait pour un média financé autrement.

## 10. Fiche mémo

- Quatre modes de financement d'un média : vente, abonnement, publicité, fonds publics — \
souvent combinés.
- Un média financé par la publicité dépend de son audience : plus il attire de vues, plus \
il génère de revenus publicitaires.
- Un média financé par des fonds publics ne dépend ni de l'audience ni de la publicité : \
il peut traiter des sujets peu populaires sans perdre de financement.
- Un média payant (vente/abonnement) dépend de la fidélité de son public.
- Interactivité (réagir au message) et mode de financement sont deux notions \
indépendantes — ne jamais les confondre.
"""
