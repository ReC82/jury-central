"""Contenu de cours — FSE10 « Élections et participation citoyenne » (ticket #99, cahier
des charges détaillé).

Même structure que FSE01-FSE09 : 1. Ce que tu dois savoir faire à l'examen —
2. Théorie progressive — 3. Définitions importantes — 4. Méthode étape par étape —
5. Exemples commentés — 6. Mauvaises réponses comparées aux bonnes — 7. Pièges et erreurs
fréquentes — 8. Exercices guidés (corrigés masqués par défaut) — 9. Corrigés très
expliqués — 10. Fiche mémo — 11. Sources officielles vérifiées.

Périmètre strict (ticket #99, programme p. 61-62) : niveaux pour lesquels on vote,
périodicité, scrutin proportionnel, procuration, vote blanc/nul, témoin du dépouillement,
pétition, distinction consultation/référendum. Toute condition d'âge/obligation/calendrier
est vérifiée par scrutin et région (voir § 11) — jamais présentée comme universelle quand
elle ne l'est pas."""

from app.v1.fse10_content import (
    FSE10_BALLOTS_TEXT,
    FSE10_TABLE_TEXT,
)


def fse10_course_markdown() -> str:
    return f"""# FSE10 — Élections et participation citoyenne

## 1. Ce que tu dois savoir faire à l'examen

Tu dois être capable d'identifier les niveaux de pouvoir pour lesquels on vote en Belgique, \
de distinguer vote valable, vote blanc et vote nul, d'expliquer la procuration, le témoin \
du dépouillement, la pétition et la distinction entre consultation et référendum — sans \
jamais présenter une règle (âge, obligation, calendrier) comme universelle si elle diffère \
selon le scrutin ou la région.

**Prérequis** : ce cours réutilise les niveaux de pouvoir vus en FSE08-FSE09 (fédéral, \
Régions, Communautés).

## 2. Théorie progressive

En Belgique, on vote pour plusieurs niveaux de pouvoir distincts : le **scrutin fédéral** \
(Chambre des représentants), le **scrutin régional** (parlements de Région/Communauté), le \
**scrutin européen** (Parlement européen) et les **scrutins communal et provincial** \
(conseils locaux). La plupart de ces scrutins utilisent un **scrutin proportionnel** : les \
sièges sont répartis entre les listes selon leur nombre de voix, pas seulement attribués à \
la liste arrivée en tête — ce qui explique pourquoi plusieurs partis obtiennent des sièges \
et doivent ensuite former une **coalition** pour gouverner ensemble.

L'**obligation de vote** et les **conditions d'âge** ne sont pas les mêmes partout : elles \
dépendent du scrutin ET, pour les scrutins communal/provincial, de la région (voir le \
tableau daté ci-dessous, § 5). Il ne faut jamais répondre « le vote est obligatoire en \
Belgique » sans préciser le scrutin et, si nécessaire, la région.

Un électeur absent le jour du vote peut recourir à la **procuration** : il mandate une autre \
personne pour voter à sa place. Un **vote valable** exprime un choix clair pour une seule \
liste. Un **vote blanc** ne comporte aucune marque. Un **vote nul** comporte une marque qui \
empêche de connaître l'intention de l'électeur (plusieurs listes cochées, inscription \
personnelle...). Vote blanc et vote nul ne profitent à aucune liste et ne comptent pas dans \
la répartition des sièges.

Un **témoin du dépouillement** est une personne, désignée par un parti ou une liste, qui \
assiste au comptage des voix pour en garantir la transparence. Une **pétition** est une \
demande collective adressée à une autorité, sans effet contraignant automatique. Une \
**consultation populaire** recueille l'avis des citoyens sur une question précise, sans que \
le résultat lie obligatoirement l'autorité qui l'organise ; un **référendum contraignant** \
au sens strict (dont le résultat s'imposerait automatiquement) n'existe pas au niveau \
national belge — la consultation reste la forme utilisée en pratique.

## 3. Définitions importantes

- **Scrutin proportionnel** : répartition des sièges entre listes selon leur nombre de \
voix, pas seulement à la liste arrivée en tête.
- **Coalition** : accord entre plusieurs partis pour former ensemble un gouvernement, \
nécessaire quand aucun parti n'a la majorité à lui seul.
- **Procuration** : mandat donné à une autre personne pour voter à sa place.
- **Vote valable** : vote exprimant un choix clair pour une seule liste.
- **Vote blanc** : vote ne comportant aucune marque.
- **Vote nul** : vote comportant une marque qui empêche de connaître l'intention de \
l'électeur.
- **Témoin du dépouillement** : personne désignée pour assister au comptage des voix.
- **Pétition** : demande collective adressée à une autorité, sans effet contraignant \
automatique.
- **Consultation populaire** : recueil de l'avis des citoyens sur une question précise, \
sans effet automatiquement contraignant.

## 4. Méthode étape par étape

Face à une question sur les élections, procède dans cet ordre :

1. Identifie le **scrutin** précis concerné (fédéral, régional, européen, communal, \
provincial).
2. Vérifie, pour ce scrutin ET cette région si nécessaire, les règles réellement en \
vigueur (obligation, âge) — ne généralise jamais une règle d'un scrutin à un autre.
3. Distingue vote valable, blanc et nul à partir de ce qui est réellement marqué sur le \
bulletin.
4. Identifie les mécanismes de participation évoqués (procuration, témoin, pétition, \
consultation) à partir de leur fonction précise, pas de leur nom seul.

## 5. Exemples commentés

### Exemple 1 — Tableau daté des scrutins

{FSE10_TABLE_TEXT}

**Analyse commentée :** ce tableau montre que l'obligation de vote n'est **pas la même \
partout** pour les scrutins communal et provincial : obligatoire en Wallonie et à \
Bruxelles, plus obligatoire en Flandre depuis 2024. Pour les scrutins fédéral et régional, \
en revanche, l'obligation reste la même partout en Belgique.

### Exemple 2 — Bulletin B (vote valable)

{FSE10_BALLOTS_TEXT.splitlines()[4]}

**Analyse commentée :** une seule case remplie, pour une seule liste : c'est un **vote \
valable**, qui compte dans la répartition des sièges.

### Exemple 3 — Bulletin C (vote nul)

{FSE10_BALLOTS_TEXT.splitlines()[6]}

**Analyse commentée :** le commentaire personnel ajouté dans la marge empêche de garantir \
que seule l'intention de vote est exprimée : c'est un **vote nul**, à distinguer du vote \
blanc (bulletin A, totalement vierge).

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse** : « Le vote est obligatoire en Belgique, point final. » → ignore \
que l'obligation diffère désormais selon le scrutin et la région (communal/provincial en \
Flandre).
- ✅ **Bonne réponse** : « Le vote reste obligatoire pour les scrutins fédéral, régional et \
européen partout en Belgique ; pour les scrutins communal et provincial, il reste \
obligatoire en Wallonie et à Bruxelles mais plus en Flandre depuis 2024. »

- ❌ **Mauvaise réponse** (bulletin A) : « C'est un vote nul, puisqu'il n'exprime aucun \
choix. » → confond vote blanc (aucune marque) et vote nul (marque ambiguë).
- ✅ **Bonne réponse** : « C'est un vote blanc : aucune marque n'est présente sur le \
bulletin. »

## 7. Pièges et erreurs fréquentes

- **Généraliser une règle d'un scrutin à tous les autres** : l'obligation de vote, en \
particulier, diffère désormais entre scrutins et, pour le communal/provincial, entre \
régions.
- **Confondre vote blanc et vote nul** : l'absence de marque (blanc) n'est pas la même \
chose qu'une marque ambiguë (nul).
- **Confondre pétition et consultation populaire** : la pétition est une demande, la \
consultation recueille un avis sur une question précise — ni l'une ni l'autre ne lie \
automatiquement l'autorité.
- **Présenter une donnée datée (ex. réforme de 2024) comme immuable** : toujours vérifier \
la situation à jour avant d'affirmer une règle électorale dans un cas réel.

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Vote obligatoire selon le scrutin et la région (essaie avant de \
regarder la correction)</summary>

Une personne habitant en Région flamande doit-elle obligatoirement voter aux élections \
communales ? Et aux élections régionales ?

<details>
<summary>Voir la correction expliquée</summary>

Pour les élections communales, non : le vote n'est plus obligatoire en Région flamande \
depuis le scrutin du 13 octobre 2024. Pour les élections régionales, oui : l'obligation de \
vote reste la même sur tout le territoire belge, y compris en Flandre.

Ce corrigé fonctionne parce qu'il traite séparément les deux scrutins au lieu de donner une \
réponse unique pour « les élections » en général.
</details>
</details>

<details>
<summary>Exercice 2 — Distinguer blanc et nul (essaie avant de regarder la correction)</summary>

Reprends le bulletin D (deux listes cochées). S'agit-il d'un vote blanc ou d'un vote nul ? \
Justifie.

<details>
<summary>Voir la correction expliquée</summary>

C'est un vote nul : deux cases remplies pour deux listes différentes rendent impossible de \
connaître l'intention de l'électeur pour une seule liste. Un vote blanc, par définition, ne \
comporte aucune marque.

Ce corrigé fonctionne parce qu'il applique la définition exacte du vote nul (marque \
ambiguë) plutôt que de supposer que « deux votes valent mieux qu'aucun ».
</details>
</details>

## 9. Corrigés très expliqués

**Question :** « Pourquoi dit-on qu'un scrutin proportionnel mène souvent à une coalition ? »

**Corrigé expliqué :** dans un scrutin proportionnel, les sièges sont répartis entre \
plusieurs listes selon leur nombre de voix, ce qui aboutit presque toujours à ce qu'aucun \
parti n'obtienne, à lui seul, la majorité des sièges nécessaire pour gouverner. Plusieurs \
partis doivent alors s'accorder pour réunir ensemble une majorité : c'est la coalition. \
C'est l'inverse d'un système où un seul parti arrivé en tête obtiendrait automatiquement \
tous les sièges ou le pouvoir.

Ce corrigé fonctionne parce qu'il relie explicitement le mécanisme (répartition \
proportionnelle) à sa conséquence (nécessité d'une coalition), plutôt que de présenter la \
coalition comme un fait isolé.

## 10. Fiche mémo

- Scrutins distincts : fédéral, régional, européen, communal, provincial — chacun avec ses \
propres règles.
- Scrutin proportionnel = sièges répartis selon le nombre de voix → mène souvent à une \
coalition.
- Vote obligatoire : fédéral/régional/européen partout en Belgique ; communal/provincial \
obligatoire en Wallonie/Bruxelles, plus obligatoire en Flandre depuis 2024.
- Vote blanc = aucune marque ; vote nul = marque ambiguë ; aucun des deux ne compte dans la \
répartition des sièges.
- Procuration = mandater une autre personne pour voter ; témoin du dépouillement = \
surveille le comptage.
- Pétition = demande collective ; consultation populaire = recueil d'avis sur une question \
précise — ni l'une ni l'autre n'a d'effet automatiquement contraignant.

## 11. Sources officielles vérifiées

Les règles décrites ci-dessus sont vérifiées auprès de sources belges officielles et \
publiques, à la date du 2026-10-01 :

- Loi du 25 décembre 2023 et arrêt de la Cour constitutionnelle du 21 mars 2024 (vote à 16 \
ans pour le scrutin européen, avec obligation de vote) — rapportés par « Questions \
Justice », https://questions-justice.be/Elections-europeennes-vote, consulté le 2026-10-01.
- VRT NWS, « Suppression du vote obligatoire en Flandre » (communal/provincial, depuis le \
scrutin du 13 octobre 2024), \
https://www.vrt.be/vrtnws/fr/2024/09/11/suppression-du-vote-obligatoire-en-flandre-faut-il-encore-alle/ \
— consulté le 2026-10-01.
- Élections locales Wallonie (portail officiel), lexique vote blanc/vote nul, \
https://electionslocales.wallonie.be/home/lexique.default.html — consulté le 2026-10-01.

Ces règles peuvent évoluer : avant toute affirmation sur un scrutin réel, vérifie la date \
et la région auprès d'une source officielle plutôt que de ce cours.
"""
