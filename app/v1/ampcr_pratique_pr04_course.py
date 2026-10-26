"""Cours PR04 « Reconditionnement, entretien et contrôles après intervention » — parcours
AMPCR pratique écrite (ticket #205).

Matière : intégralement celle du ticket #205 (état initial, inventaire et numéros de série,
diagnostic avant intervention, protection et effacement des données seulement avec
consentement et technique adaptée, nettoyage non destructif, poussière et refroidissement,
remplacement de pièces et contrôle de compatibilité, mises à jour du firmware et du système
avec précautions, tests RAM/SMART/températures/ports, stabilité, check-list de réception et
de remise, déchets DEEE, rapport et traçabilité ; distinction réparation, reconditionnement,
remise à zéro et effacement sécurisé HDD/SSD), découpée en blocs titrés (le titre pilote le
type de carte, `app.card_kind` : aucun titre de bloc théorique ne contient « examen »,
« source », « exemple », « exercice », « méthode », « piège », « attention » ni « mémo » —
donc pas « mémoire »). Aucune manipulation sous tension ni ouverture de bloc d'alimentation.
Données et schémas : `app.v1.ampcr_pratique_pr04_figures` ; exercices et mini-examen :
`app.v1.ampcr_pratique_pr04_bank`. Mise en forme partagée avec les autres cours pratiques.
"""

from html import escape

from app.v1.ampcr_pratique_pr04_bank import EXAM_ITEMS, EXAM_TOTAL_POINTS, PRACTICE_ITEMS
from app.v1.ampcr_pratique_pr04_figures import (
    AFTER_TESTS_FIGURE,
    BATTERY_REPLACE_BELOW,
    CASE2_SMART,
    CASE3_CYCLES,
    CASE3_DESIGN,
    CASE3_FULL,
    CASE3_SCREEN,
    CASE4_AFTER,
    CASE4_BEFORE,
    CASE4_LIMIT,
    CLEAN_FIGURE,
    CLEANING_FIGURE,
    CLEANING_POINTS,
    DATA_TREE_FIGURE,
    DEST_NEW_USER,
    ERASE_FIGURE,
    ERASE_METHODS,
    FIRMWARE_FIGURE,
    HANDOVER_CHECKS,
    OPERATIONS,
    PROCEDURES,
    RECEPTION_FIELDS,
    RECON_FIGURE,
    SMART_FIGURE,
    TEMP_ALERT_MARGIN,
    TEMPS_FIGURE,
    WASTE_STREAMS,
    battery_health_percent,
    battery_verdict,
    data_decision,
    smart_verdict,
    temperature_verdict,
)
from app.v1.ampcr_pratique_pr06_course import _exercise_card, _fig, _req

PR04_TITLE = "Reconditionnement, entretien et contrôles après intervention"
PR04_SLUG = "ampcr-pratique-pr04"


def _exercises_html() -> str:
    return "\n\n".join(
        _exercise_card(i, item, anchor_prefix="pr04") for i, item in enumerate(PRACTICE_ITEMS, start=1)
    )


def _console(*lines: str) -> str:
    return f'<pre class="jc-pr-console" tabindex="0">{escape(chr(10).join(lines))}</pre>'


def _ex(*keys: str) -> str:
    """Renvoi texte vers les exercices corrigés liés à un chapitre (séquence « Exercices
    corrigés ») : pas de lien d'ancre, la page n'affiche qu'une séquence à la fois."""
    return ", ".join(f"**{key}**" for key in keys) + " (séquence « Exercices corrigés »)"


# --- Tableaux de données (générés depuis les données vérifiées) ------------------------------


def _operations_table() -> str:
    rows = "\n".join(f"| **{op.name}** | {op.goal} | {op.data} | {op.owner} | {op.proof} |" for op in OPERATIONS)
    return "| Opération | But | Données du client | Pour qui | Trace |\n|---|---|---|---|---|\n" + rows


def _erase_table() -> str:
    rows = "\n".join(
        f"| **{media}** | {' ; '.join(ok)} | {' ; '.join(ko)} | {why} |" for media, ok, ko, why in ERASE_METHODS
    )
    return "| Support | Techniques adaptées | Insuffisantes | Pourquoi |\n|---|---|---|---|\n" + rows


def _reception_form() -> str:
    rows = "\n".join(f"| {field} | {content} | ……………… |" for field, content in RECEPTION_FIELDS)
    return "| Rubrique | Ce qu'on y écrit | À remplir |\n|---|---|---|\n" + rows


def _handover_form() -> str:
    rows = "\n".join(f"| ☐ | {what} | {check} |" for what, check in HANDOVER_CHECKS)
    return "| Fait | Point | Vérification |\n|---|---|---|\n" + rows


def _cleaning_table() -> str:
    rows = "\n".join(f"| {p.number} | {p.zone} | {p.action} |" for p in CLEANING_POINTS)
    return "| Repère | Zone | Geste |\n|---|---|---|\n" + rows


def _waste_table() -> str:
    rows = "\n".join(f"| **{name}** | {how} | {examples} |" for name, how, examples in WASTE_STREAMS)
    return "| Filière | Règle | Exemples à l'atelier |\n|---|---|---|\n" + rows


def _procedures_list() -> str:
    return "\n".join(
        f"{i}. **{title}** ({len(steps)} étapes)" for i, (title, steps) in enumerate(PROCEDURES, start=1)
    )


def _temps_table(rows: tuple[tuple[int, int], ...]) -> str:
    body = "\n".join(
        f"| {minute} min | {temp} °C | {temperature_verdict(temp, CASE4_LIMIT)} |" for minute, temp in rows
    )
    return "| Charge depuis | Température du processeur | Verdict |\n|---|---|---|\n" + body


# =============================================================================================
# Sections du cours (titre du bloc, Markdown / HTML)
# =============================================================================================


def _objectives() -> str:
    return f"""## Ce que tu sauras faire, par écrit

L'épreuve pratique AMPCR se passe **uniquement par écrit** (consignes officielles 2026-2027/1,
p. 3). On ne te demande pas de nettoyer un PC devant le jury, mais de **rédiger** comment tu
reconditionnes, entretiens et contrôles un ordinateur, dans quel ordre, avec quelles
précautions, et de **décider** ce que deviennent les données du client. À partir d'une fiche,
d'un relevé SMART, d'un rapport de batterie ou de températures, tu dois savoir :

1. **distinguer** réparation, reconditionnement, remise à zéro et effacement sécurisé ;
2. **réceptionner** un PC : état initial, inventaire, numéros de série, accord écrit ;
3. **diagnostiquer avant d'intervenir** ;
4. **protéger les données** : sauvegarde, confidentialité, effacement **seulement avec
   l'accord du propriétaire** et avec une **technique adaptée** au disque dur ou au SSD ;
5. **nettoyer sans rien abîmer**, traiter la poussière et le refroidissement ;
6. **remplacer** des pièces compatibles, **mettre à jour** firmware, système et pilotes avec
   précaution ;
7. **contrôler** après l'intervention (mémoire, SMART, températures, ports, stabilité) ;
8. **remettre** le PC avec une check-list, **trier les déchets** et **rédiger le rapport**.

Ce cours contient **5 procédures illustrées** :

{_procedures_list()}

## Exigences officielles travaillées dans ce cours

{_req("AP-14")}

Le **montage et le démontage** sont l'autre volet de cette exigence : ils sont traités en
[PR03](/uaa/ampcr-pratique-pr03). Ce cours-ci couvre le **reconditionnement**.

Complément pédagogique (hors liste officielle des pp. 5-6, signalé comme tel) :

{_req("AP-C03")}

Le stockage (partitions, formatage, systèmes de fichiers) est détaillé en PR05, la démarche
complète de diagnostic des pannes en [PR06](/uaa/ampcr-pratique-pr06), les connecteurs et la
sécurité électrique en [PR02](/uaa/ampcr-pratique-pr02).

## Lien avec la théorie

Les notions de base sont présentées dans la théorie AMPCR :
[MC06 Montage, démontage et reconditionnement d'un PC](/uaa/ampcr-mc06) et
[MC32 Maintenance préventive et entretien](/uaa/ampcr-mc32). Ce cours-ci est **pratique** :
procédures rédigées, décisions justifiées, relevés à interpréter et formulaires à remplir, comme
dans un dossier d'examen.

## Comment travailler ce cours

Lis les chapitres dans l'ordre : chacun donne ses **objectifs**, la **théorie**, la
**procédure professionnelle** à rédiger, l'**erreur fréquente**, ce qu'on attend **à l'écrit**
et un **repère rapide**, avec un renvoi vers les exercices liés. Étudie ensuite les **quatre
cas résolus**, fais les **{len(PRACTICE_ITEMS)} exercices corrigés** (ici ou dans
« S'entraîner », correction après envoi), puis passe le **mini-examen noté sur
{EXAM_TOTAL_POINTS}** dans l'onglet « Examen blanc ».

> **Important —** les fiches, relevés, rapports et situations de ce cours sont des **supports
> fictifs** construits pour s'entraîner : ils ne décrivent aucun produit réel, et seuls la
> notice et l'outil du fabricant font foi pour un vrai matériel. Aucun exercice n'est une
> question officielle ni une question déjà posée par le Jury.
> **Aucune manipulation ne se fait sous tension, et un bloc d'alimentation ne s'ouvre jamais.**
"""


def _operations() -> str:
    return f"""**Objectifs** : nommer correctement l'opération demandée, car le devis, l'accord à faire
signer, le sort des données et la trace à remettre en dépendent.

## 1.1 Quatre opérations différentes

{_operations_table()}

## 1.2 Ce qui les distingue vraiment

- **Réparation** : on corrige **une panne** ; le PC revient au **même client**, avec ses
  données.
- **Reconditionnement** : on remet un PC **complet** en état de servir à **quelqu'un
  d'autre** (revente, don, réaffectation dans une entreprise) : diagnostic, nettoyage,
  pièces usées, système propre, tests, étiquette. C'est un processus, pas un geste.
- **Remise à zéro** (« Réinitialiser ce PC », restauration d'usine, réinstallation) : le
  système repart propre, mais les anciens fichiers **ne sont pas forcément illisibles** sur
  le disque. Elle convient quand le PC **reste chez le même client** ou dans sa sphère.
- **Effacement sécurisé** : on rend les données **illisibles** avec une technique **adaptée
  au support** (chapitre 5), **vérifiée** et **certifiée**. Il est obligatoire avant que le
  support **change de main** (revente, don, fin de location, recyclage).

## 1.3 Le reconditionnement, étape par étape

Chaque étape est détaillée dans un chapitre de ce cours (réception : 2 ; diagnostic : 3 ;
données : 4 et 5 ; nettoyage : 6 et 7 ; pièces : 8 ; mises à jour : 9 ; tests : 10 ; remise :
11 à 13).

{_fig(RECON_FIGURE)}

**Procédure professionnelle (à rédiger)** : reformuler la demande du client → nommer
l'opération → en déduire l'accord à faire signer, le sort des données et la trace à remettre.

**Erreur fréquente** : appeler « reconditionnement » une simple réinstallation, ou croire
qu'une **remise à zéro** suffit avant une revente. Une remise à zéro n'est pas un effacement
sécurisé.

**À l'écrit** : nommer l'opération **et** justifier par son but, le destinataire du PC et le
sort des données.

**Repère rapide** : panne → **réparation** · nouvel utilisateur → **reconditionnement** ·
même client, système neuf → **remise à zéro** · support qui part → **effacement sécurisé**.
Exercices liés : {_ex("E04")}.
"""


def _reception() -> str:
    return f"""**Objectifs** : réceptionner un PC de façon à pouvoir prouver son état d'arrivée et
retrouver chaque pièce plus tard.

## 2.1 La fiche de réception (formulaire)

{_reception_form()}

## 2.2 Inventaire et numéros de série

- Le **numéro de série** du PC (étiquette sous le portable, au dos ou sur le côté de la
  tour, ou dans l'UEFI) identifie l'appareil sans ambiguïté ; dans un lot, on pose aussi une
  **étiquette d'inventaire** de l'atelier.
- On note les **accessoires** remis (chargeur, câbles, sacoche) : ce qui n'est pas noté à la
  réception n'existe pas en cas de litige.
- L'**état initial** se décrit précisément (« rayure de 3 cm sur le capot, charnière gauche
  dure ») et se **photographie** avec la date ; « bon état » ne prouve rien.
- Pendant l'intervention, chaque pièce **posée ou retirée** est notée avec sa référence et son
  numéro de série (garantie, traçabilité).

**Procédure professionnelle (à rédiger)** : identifier client et matériel (numéro de série) →
accessoires → état initial et photos → demande précise → données et accord écrit → signatures
et copie au client.

**Erreur fréquente** : réceptionner « un portable gris, bon état, remise à neuf » : rien
n'identifie l'appareil, rien ne prouve l'état, et la demande ne dit pas si l'on peut effacer.

**À l'écrit** : une rubrique par ligne, avec un contenu **vérifiable** (numéro, mesure,
photo).

**Repère rapide** : **qui · quoi (n° de série) · avec quoi · dans quel état · pour quoi ·
données · signatures**. Exercices liés : {_ex("E10")}.
"""


def _diagnosis() -> str:
    return f"""**Objectifs** : faire un diagnostic **avant** toute intervention, pour décider ce qui
vaut la peine d'être fait et éviter d'aggraver une panne.

## 3.1 Pourquoi diagnostiquer d'abord

- On sait ce qui **fonctionne** et ce qui ne fonctionne pas **avant** d'y toucher : en cas de
  problème après l'intervention, on peut dire si c'était déjà là.
- On évite de **nettoyer, mettre à jour ou réinstaller** un PC dont le disque est mourant :
  une réinstallation sur un disque défaillant peut faire perdre les données restantes.
- On chiffre le travail : un PC dont la carte mère est morte n'est souvent plus rentable à
  reconditionner.

## 3.2 Ce que comprend le diagnostic initial

| Contrôle | Ce qu'on relève |
|---|---|
| Démarrage | POST, messages, bips, temps de démarrage |
| UEFI | processeur, mémoire totale, disques détectés, date et heure, températures |
| Stockage | **état SMART** de chaque disque, espace libre |
| Mémoire | test de la mémoire si plantages ou écrans bleus |
| Batterie (portable) | capacité restante (rapport de batterie), gonflement |
| Extérieur et ports | écran, clavier, charnières, ports USB, audio, réseau |
| Poussière | grilles, ventilateurs, bruit, températures en charge |

**Procédure professionnelle (à rédiger)** : démarrer et observer → UEFI → SMART → mémoire si
besoin → batterie → ports et extérieur → conclusion écrite (ce qui marche, ce qui est à
remplacer, faisabilité).

**Erreur fréquente** : réinstaller « pour voir » avant d'avoir lu l'état SMART ; si le disque
meurt pendant l'opération, les données sont perdues **et** le travail est à refaire.

**À l'écrit** : le diagnostic se rédige avec des **valeurs** (« SMART : 8 secteurs en attente »)
et une conclusion.

**Repère rapide** : **diagnostiquer → décider → intervenir**, jamais l'inverse. Exercices liés :
{_ex("E07", "E16")}.
"""


def _data_protection() -> str:
    return f"""**Objectifs** : protéger les données et la vie privée du client ; savoir qui peut
décider d'un effacement.

## 4.1 Trois règles

1. **Seul le propriétaire décide**, **par écrit** (consentement explicite, signé), de ce que deviennent ses données. Une
   demande d'un proche, d'un collègue ou d'un vendeur « sûrement d'accord » ne vaut pas
   accord : on n'efface rien et on contacte le propriétaire.
2. **Sauvegarde vérifiée avant toute opération risquée** (réinstallation, remplacement du
   disque, mise à jour du firmware) : la copie est **relue** (on ouvre quelques fichiers). Si
   le client refuse la sauvegarde, il **signe son refus**.
3. **Confidentialité** : on n'ouvre pas les fichiers du client ; un mot de passe confié sert
   seulement à tester, puis le client est invité à le changer ; un disque retiré est rangé et
   tracé, jamais laissé sur un établi.

## 4.2 Décider du sort des données

{_fig(DATA_TREE_FIGURE)}

**Procédure professionnelle (à rédiger)** : accord écrit du propriétaire → sauvegarde
vérifiée (ou refus signé) → selon la destination : conserver (même client) ou effacer de façon
sécurisée (le PC change de main) → trace.

**Erreur fréquente** : effacer un PC « pour rendre service » sur un simple appel téléphonique.
Un effacement est **irréversible**.

**À l'écrit** : citer **qui** a donné l'accord, **comment** (écrit, signé), l'état de la
sauvegarde, puis la décision.

**Repère rapide** : **pas d'accord écrit, pas d'effacement · pas de sauvegarde vérifiée, pas de
réinstallation**. Exercices liés : {_ex("E05", "E14")}.
"""


def _secure_erase() -> str:
    example = data_decision(owner_consent=True, wants_data=False, backup_verified=False, destination=DEST_NEW_USER)
    return f"""**Objectifs** : choisir la technique d'effacement adaptée au **type de support** et
prouver qu'elle a été appliquée.

## 5.1 Supprimer n'est pas effacer

- **Supprimer un fichier**, vider la corbeille, **formater rapidement** ou supprimer les
  partitions ne retire que les **références** aux données : un logiciel de récupération les
  retrouve. Retiens : **un formatage rapide n'efface rien**.
- La publication de référence **NIST SP 800-88** distingue trois niveaux : **effacer**
  (écraser les données), **purger** (commande d'effacement du support lui-même, effacement
  cryptographique) et **détruire** (broyage par une filière agréée).

## 5.2 Disque dur ou SSD : pas la même technique

{_erase_table()}

- **Disque dur** : les données sont écrites à un endroit précis du plateau ; un **écrasement
  complet** les remplace (une passe suffit sur un disque récent), ou la **commande
  d'effacement sécurisé** du disque le fait elle-même.
- **SSD** : le contrôleur **répartit les écritures** (usure) et garde des **cellules de
  réserve** invisibles ; un logiciel lancé depuis le PC ne peut pas les atteindre toutes. On
  utilise la **commande intégrée au SSD** (effacement sécurisé ou Sanitize, NVMe Format) via
  l'**outil du fabricant** ou le **firmware** de la carte, ou l'**effacement cryptographique**
  si le SSD était chiffré. La **défragmentation** n'efface rien et use le SSD.
- Un support **hors d'usage** (illisible) ne peut pas être effacé : il est **détruit** par une
  filière agréée, avec un certificat.

{_fig(ERASE_FIGURE)}

## 5.3 Le certificat d'effacement

| Rubrique | Exemple de contenu |
|---|---|
| Support | SSD NVMe 512 Go, numéro de série |
| Propriétaire et accord | société X, accord signé le … |
| Technique | commande Sanitize via l'outil du fabricant |
| Vérification | aucune donnée lisible, outil de contrôle |
| Date, technicien, signature | … |

**Procédure professionnelle (à rédiger)** : accord écrit → sauvegarde ou renonciation →
identifier le support → effacer avec la technique adaptée → vérifier → certificat. Avec
l'accord écrit, pour un PC qui change de main, la décision est : « {example} ».

**Erreur fréquente** : effacer un SSD par sept passes d'écrasement, comme un vieux disque dur,
ou se contenter d'un formatage rapide.

**À l'écrit** : nommer le **support**, la **technique** et **pourquoi** elle convient, puis la
**preuve**.

**Repère rapide** : **HDD → écrasement complet · SSD → commande du SSD (ou cryptographique) ·
hors d'usage → destruction · toujours un certificat**. Exercices liés : {_ex("E06", "E13")}.
"""


def _cleaning() -> str:
    return f"""**Objectifs** : nettoyer un PC sans l'abîmer : ni décharge électrostatique, ni
ventilateur cassé, ni liquide sur un circuit.

## 6.1 Les règles du nettoyage non destructif

- **PC débranché** (interrupteur sur 0, câble secteur retiré, bouton appuyé) ; portable :
  chargeur débranché et **batterie déconnectée** si la notice le prévoit.
- **Bracelet antistatique** relié au châssis.
- **Air sec en bombe** (ou soufflette d'atelier **filtrée et sèche**), par **courtes
  impulsions**, bombe **tenue droite** (incliner la bombe projette du gaz liquide très froid).
- **Bloquer les pales** d'un ventilateur avant de souffler : entraîné par l'air, il tourne
  bien au-delà de sa vitesse normale et ses paliers peuvent s'abîmer.
- **Pinceau antistatique** pour la poussière collée ; **alcool isopropylique** et chiffon non
  pelucheux pour les contacts et l'ancienne pâte thermique ; **jamais d'eau ni de produit
  ménager** sur un circuit.
- **Pas d'aspirateur ménager** dans le boîtier : son flux d'air et son embout créent de
  l'**électricité statique** et il peut aspirer de petites pièces (cavaliers, vis).
- Le **bloc d'alimentation** se dépoussière **par ses grilles**, de l'extérieur : un bloc
  d'alimentation ne s'ouvre jamais.

## 6.2 Où se trouve la poussière (vue annotée)

{_fig(CLEANING_FIGURE)}

{_cleaning_table()}

{_fig(CLEAN_FIGURE)}

**Procédure professionnelle (à rédiger)** : couper → sortir le PC dans un local aéré →
filtres → bloquer les ventilateurs → air sec par impulsions et pinceau → contacts et pâte →
contrôler et mesurer.

**Erreur fréquente** : souffler un ventilateur sans le bloquer, ou passer l'aspirateur sur la
carte mère.

**À l'écrit** : chaque geste avec sa raison (« je bloque les pales, car un ventilateur entraîné
par l'air peut s'abîmer »).

**Repère rapide** : **débranché · bracelet · pales bloquées · air sec par impulsions · ni
aspirateur ni eau · bloc jamais ouvert**. Exercices liés : {_ex("E02")}.
"""


def _cooling() -> str:
    before = CASE4_BEFORE[-1][1]
    after = CASE4_AFTER[-1][1]
    return f"""**Objectifs** : relier poussière, pâte thermique et températures ; prouver par des
mesures l'effet d'un entretien.

## 7.1 Pourquoi un PC encrassé ralentit

- La poussière **bouche** les filtres et les ailettes des radiateurs : l'air passe moins,
  la chaleur reste.
- Une **pâte thermique sèche** (plusieurs années) transmet mal la chaleur du processeur au
  radiateur.
- Près de sa **limite de température**, le processeur **réduit sa fréquence** pour se
  protéger (ralentissement) ; à la limite, le PC peut **s'éteindre**.

## 7.2 Les gestes d'entretien

- Nettoyer filtres, ventilateurs et radiateurs (chapitre 6) ; vérifier que chaque ventilateur
  **tourne librement** et sans bruit de frottement ; remplacer un ventilateur bruyant.
- **Pâte thermique** : ancienne pâte retirée à l'alcool isopropylique, **pâte neuve** chaque
  fois que le ventirad ou le radiateur est démonté (voir PR03).
- Vérifier le **sens du flux d'air** : entrée à l'avant ou en bas, sortie à l'arrière et en
  haut.

## 7.3 Mesurer avant et après

Règle du cours (même seuil qu'en PR03) : **à surveiller** à moins de {TEMP_ALERT_MARGIN} °C de
la limite de la fiche, **anormal** à la limite.

{_fig(TEMPS_FIGURE)}

**Procédure professionnelle (à rédiger)** : relever les températures au repos et en charge
**avant** → nettoyer, pâte neuve si démontage → mêmes mesures **après**, même durée de charge →
comparer et noter.

**Erreur fréquente** : écrire « nettoyé, ça chauffe moins » sans valeurs. Le rapport donne les
mesures : ici {before} °C avant et {after} °C après, pour une limite de {CASE4_LIMIT} °C.

**À l'écrit** : valeurs avant/après, durée de charge, limite de la fiche, verdict.

**Repère rapide** : **poussière + vieille pâte → chaleur → baisse de fréquence → arrêt** ;
**mesurer avant, mesurer après**. Exercices liés : {_ex("E08")}.
"""


def _parts() -> str:
    return f"""**Objectifs** : remplacer les pièces usées ou défectueuses par des pièces compatibles,
et garder la trace de chaque échange.

## 8.1 Les pièces qu'on remplace le plus souvent

| Pièce | Signe d'usure | Contrôle de compatibilité |
|---|---|---|
| Disque dur → SSD | SMART dégradé, lenteur | format (2,5 pouces, M.2 2280), interface (SATA, NVMe) acceptée |
| Mémoire | erreurs au test, quantité insuffisante | génération (DDR4 ≠ DDR5), format (DIMM, SO-DIMM), capacité maximale |
| Ventilateur | bruit, vitesse faible | dimensions, connecteur (3 ou 4 broches), fixation |
| Pâte thermique | sèche, températures élevées | pâte non conductrice adaptée |
| Batterie de portable | capacité restante faible, gonflement | référence exacte du fabricant pour ce modèle |
| Pile de la carte mère | date et réglages perdus après débranchement | même référence (souvent CR2032) |
| Bloc d'alimentation | arrêts, bruit, odeur | format, puissance, connecteurs (PR02) — jamais ouvert ni réparé |

## 8.2 La démarche

- **Panne ou usure confirmée** par une mesure (SMART, test mémoire, rapport de batterie).
- **Compatibilité vérifiée sur les fiches** avant la commande (comme en PR01 et PR02).
- **Accord du client** sur la pièce et le prix (réparation) ou du responsable du lot
  (reconditionnement).
- Montage **hors tension** avec ESD (procédures de PR03), puis **tests**.
- **Traçabilité** : référence et **numéro de série** de la pièce posée et de la pièce retirée ;
  la pièce retirée est **rendue au client** ou **recyclée** (chapitre 12), un disque retiré
  étant d'abord **effacé ou détruit**.

**Procédure professionnelle (à rédiger)** : constater (mesure) → vérifier la compatibilité →
accord → remplacer hors tension → tester → noter références et numéros de série.

**Erreur fréquente** : commander une barrette « 8 Go » sans vérifier la génération ni le
format (SO-DIMM pour un portable), ou changer une batterie par un modèle « qui ressemble ».

**À l'écrit** : la mesure qui justifie l'échange, le critère de compatibilité, le contrôle
après.

**Repère rapide** : **mesure → fiche → accord → hors tension → test → trace**. Exercices liés :
{_ex("E15", "E16")}.
"""


def _updates() -> str:
    return f"""**Objectifs** : mettre à jour firmware, système et pilotes **quand c'est utile**, sans
rendre le PC inutilisable.

## 9.1 Firmware (UEFI/BIOS)

- On met à jour **pour une raison** : faille de sécurité, correctif de stabilité,
  compatibilité avec un processeur ou une mémoire. « Pour avoir la dernière » n'est pas une
  raison suffisante.
- **Modèle et révision exacts** : un firmware d'un autre modèle peut rendre la carte
  inutilisable. Fichier pris **sur le site du fabricant**, **notes de version** lues
  (version minimale à installer d'abord, par exemple).
- **Alimentation stable** : une coupure pendant l'écriture peut rendre la carte
  inutilisable ; un portable reste **sur son chargeur**, batterie chargée.
- **BitLocker** : suspendre la protection avant la mise à jour (sinon Windows demande la **clé
  de récupération** au redémarrage), la reprendre après. Vérifier d'abord que le client
  connaît sa clé.
- **Réglages UEFI notés** avant : ils peuvent revenir aux valeurs d'usine (mode de démarrage,
  mode du contrôleur de disque, profil de mémoire).

{_fig(FIRMWARE_FIGURE)}

## 9.2 Système et pilotes

- **Sauvegarde** ou **point de restauration** avant une grosse mise à jour ; **espace libre**
  suffisant sur le disque système.
- **Mises à jour du système** (Windows Update, gestionnaire de paquets sous Linux) jusqu'à ce
  qu'il n'y en ait plus ; redémarrages complets.
- **Pilotes** de préférence **chez le fabricant** du PC ou du composant (ou par Windows
  Update) ; jamais d'un site de « pilotes gratuits » inconnu.
- Le détail de l'installation des systèmes est traité en PR08 et PR09.

**Procédure professionnelle (à rédiger)** : justifier → identifier le modèle et la version →
télécharger chez le fabricant, lire les notes → sauvegarde, réglages notés, BitLocker suspendu,
secteur stable → mettre à jour sans couper → vérifier la version et reprendre BitLocker.

**Erreur fréquente** : flasher un portable sur batterie faible, ou oublier BitLocker et
découvrir au redémarrage que personne ne connaît la clé de récupération.

**À l'écrit** : les précautions **avant**, **pendant** et **après**, chacune avec sa raison.

**Repère rapide** : **utile · bon modèle · site du fabricant · secteur · BitLocker suspendu ·
ne jamais couper**. Exercices liés : {_ex("E03", "E12")}.
"""


def _tests() -> str:
    smart_example = smart_verdict(dict(CASE2_SMART))
    return f"""**Objectifs** : prouver par des tests que le PC est fiable avant de le remettre.

## 10.1 Les contrôles et ce qu'on note

| Contrôle | Outil (exemples) | Ce qu'on note |
|---|---|---|
| Mémoire (RAM) | MemTest86, Diagnostic de mémoire Windows | nombre de passes, erreurs (doit être 0) |
| Stockage | utilitaire SMART (CrystalDiskInfo, smartctl) | attributs lus, verdict |
| Températures | UEFI, HWiNFO, HWMonitor | repos et charge, limite de la fiche |
| Ports | clé USB, casque, câble réseau, écran | chaque port testé, résultat |
| Stabilité | test de charge d'au moins 30 minutes | aucun arrêt, aucune erreur |
| Batterie (portable) | rapport de batterie de Windows (`powercfg /batteryreport`) | capacité d'origine, capacité à pleine charge, cycles |

## 10.2 Lire un relevé SMART

Règle du cours : **disque dur** — secteurs **en attente** ou **illisibles** au-dessus de 0 → à
remplacer ; secteurs **réalloués** au-dessus de 0 → à surveiller. **SSD NVMe** — usure
(`Percentage_Used`) à 100 % ou plus, **erreurs du support** ou **réserve** sous son seuil → à
remplacer ; usure à partir de 80 % → à surveiller. Le **résultat global** (« PASSED »,
« OK ») ne suffit jamais : on lit les attributs.

{_fig(SMART_FIGURE)}

Verdict de ce relevé selon la règle du cours : **{smart_example}**.

## 10.3 Batterie d'un portable

Capacité restante = capacité à pleine charge ÷ capacité d'origine × 100. Convention de
l'atelier dans ce cours : **à remplacer sous {BATTERY_REPLACE_BELOW} %** (seuil d'usage
courant, pas une norme) ; une batterie **gonflée** est remplacée quelle que soit sa capacité.

{_fig(AFTER_TESTS_FIGURE)}

**Procédure professionnelle (à rédiger)** : contrôle visuel → démarrage et UEFI → mémoire →
SMART → températures → ports → stabilité (et batterie) → valeurs dans le rapport.

**Erreur fréquente** : « SMART : PASSED, donc disque comme neuf » ; ou « RAS » dans le rapport
au lieu des valeurs.

**À l'écrit** : un contrôle = un outil + une valeur + un verdict.

**Repère rapide** : **RAM · SMART · températures · ports · 30 min de stabilité · batterie**.
Exercices liés : {_ex("E07", "E15")}.
"""


def _handover() -> str:
    return f"""**Objectifs** : remettre un PC contrôlé, complet et propre, avec la preuve de ce qui a
été fait.

## 11.1 Check-list de remise (formulaire)

La remise se contrôle par rapport à la **fiche de réception** (chapitre 2) : ce qui est
arrivé doit repartir, et chaque demande notée doit avoir sa réponse.

{_handover_form()}

## 11.2 La remise au client

- On **montre** au client que le PC démarre et que ses données (ou le système neuf) sont là ;
  il vérifie quelques fichiers importants.
- On rend **tout ce qui figure** sur la fiche de réception (accessoires, pièces retirées s'il
  les veut).
- On donne des **conseils** utiles : sauvegardes régulières, mises à jour, ne pas obstruer les
  grilles d'un portable.
- Le client **signe** le rapport ; l'atelier en garde une copie.

**Procédure professionnelle (à rédiger)** : check-list complète → démonstration → accessoires
et pièces rendus → conseils → signature et copie.

**Erreur fréquente** : remettre un PC avec la session ou les fichiers de test du technicien,
ou sans le chargeur noté à la réception.

**À l'écrit** : la check-list point par point, chacun **vérifiable**.

**Repère rapide** : **tests · système · données · propreté · accessoires · pièces · conseils ·
signature**. Exercices liés : {_ex("E11")}.
"""


def _waste() -> str:
    return f"""**Objectifs** : orienter chaque déchet de l'atelier vers la bonne filière, en sécurité.

## 12.1 Les filières

{_waste_table()}

- Les **DEEE** (déchets d'équipements électriques et électroniques, directive européenne
  2012/19/UE) portent le symbole de la **poubelle barrée** : ils ne vont **jamais** dans la
  poubelle ordinaire (métaux récupérables, substances polluantes).
- En Belgique, l'organisme **Recupel** organise la collecte des appareils (recyparcs, points de
  collecte, reprise par le vendeur à l'achat d'un appareil neuf) et **Bebat** celle des **piles
  et batteries**.
- Un **disque** n'est déposé qu'après **effacement sécurisé ou destruction**, avec trace : un
  déchet électronique peut être récupéré et lu.

## 12.2 Batterie lithium gonflée

Une batterie **gonflée** est endommagée : **ne plus la charger**, ne **jamais la percer, la
plier ni l'écraser** (risque d'emballement thermique : feu violent, fumées toxiques). La
retirer sans la déformer si la notice le permet (sinon, la confier à un spécialiste), l'isoler
dans un **contenant non inflammable** (bac métallique, sable), loin de tout combustible, et la
déposer rapidement à la collecte des batteries.

**Procédure professionnelle (à rédiger)** : trier à la source (appareils, piles et batteries,
emballages) → disques effacés ou détruits → batteries isolées → dépôt à la filière → trace dans
le rapport.

**Erreur fréquente** : jeter la pile de la carte mère ou une vieille souris à la poubelle, ou
laisser une batterie gonflée sur l'établi.

**À l'écrit** : la filière **et** la raison (pollution, récupération, sécurité, données).

**Repère rapide** : **poubelle barrée → DEEE · piles et batteries à part · disque effacé avant
dépôt · batterie gonflée isolée**. Exercices liés : {_ex("E09")}.
"""


def _report() -> str:
    return f"""**Objectifs** : rédiger le rapport qui prouve ce qui a été fait, et assurer la
traçabilité du PC et de ses pièces.

## 13.1 Le rapport de reconditionnement

| Rubrique | Contenu |
|---|---|
| Identification | PC (marque, modèle, **numéro de série**), propriétaire ou lot, dates, technicien |
| Accord et données | accord signé ; sauvegarde vérifiée **ou** certificat d'effacement (support, technique) |
| Diagnostic initial | état à la réception, SMART, batterie, défauts relevés |
| Actions | nettoyage, pâte, pièces posées et retirées (références, **numéros de série**), mises à jour |
| Tests | valeurs : mémoire, SMART, températures repos/charge, ports, stabilité, batterie |
| Déchets | pièces retirées rendues ou déposées (DEEE, batteries) |
| Conclusion | « conforme » ou réserves, garantie, date, signatures |

## 13.2 Traçabilité

- Une **étiquette de reconditionnement** sur le PC (date, numéro de dossier, technicien) relie
  l'appareil à son rapport.
- Le registre de l'atelier permet de retrouver, pour chaque numéro de série : qui l'a confié,
  ce qui a été fait, quelles pièces ont été posées, où sont partis les supports effacés.
- Ces traces servent en cas de **garantie**, de **litige** ou de **contrôle** (preuve de
  l'effacement des données).

**Procédure professionnelle (à rédiger)** : identification → accord et données → diagnostic →
actions → tests chiffrés → déchets → conclusion signée → étiquette et archivage.

**Erreur fréquente** : un rapport « RAS, tout fonctionne », sans numéro de série, sans valeurs
ni certificat d'effacement.

**À l'écrit** : un plan en rubriques, chacune avec un contenu **vérifiable** par un tiers.

**Repère rapide** : **qui · quoi · données · actions · valeurs · déchets · signature**.
Exercices liés : {_ex("E12")}.
"""


def _examples() -> str:
    lot = data_decision(owner_consent=True, wants_data=True, backup_verified=True, destination=DEST_NEW_USER)
    smart = smart_verdict(dict(CASE2_SMART))
    pending = dict(CASE2_SMART)["Current_Pending_Sector"]
    health = battery_health_percent(CASE3_DESIGN, CASE3_FULL)
    verdict = battery_verdict(CASE3_DESIGN, CASE3_FULL)
    before = CASE4_BEFORE[-1][1]
    after = CASE4_AFTER[-1][1]
    return f"""## Cas 1 — Reconditionner un lot de PC pour une école

**Situation.** Une entreprise donne quinze PC de bureau de cinq ans à une école. Le gérant a
signé l'accord d'effacement ; l'entreprise a copié et vérifié ses données sur son serveur.
Chaque PC a un disque dur de 1 To. Rédige la procédure appliquée à chaque PC.

**Résolution.**

1. **Réception** : fiche par PC (numéro de série, étiquette d'inventaire, état, photos),
   accord du gérant joint au dossier.
2. **Diagnostic** : démarrage, UEFI, **SMART** de chaque disque, test mémoire, ports ; les
   PC irrécupérables sont écartés (pièces récupérées, reste en DEEE).
3. **Données** : accord écrit, copie vérifiée, PC qui change de main → « {lot} ». Disque
   dur : écrasement complet (une passe) ou commande d'effacement sécurisé, vérification,
   **certificat** par numéro de série.
4. **Nettoyage** non destructif (procédure 2), pâte neuve.
5. **Remplacements** : disque dur → SSD SATA 2,5 pouces (plus rapide, plus fiable) ; mémoire
   portée à 16 Go si la carte l'accepte ; numéros de série notés.
6. **Mises à jour** : firmware si correctif utile, système propre installé et à jour, pilotes
   du fabricant.
7. **Tests** : mémoire, SMART du SSD, températures en charge, ports, 30 minutes de stabilité.
8. **Remise** : check-list signée par la directrice, étiquette, rapport ; anciens disques
   effacés recyclés en DEEE avec leurs certificats.

**Pourquoi cet ordre.** Le diagnostic évite de travailler sur un PC irrécupérable ; les données
sont traitées avant toute autre manipulation du disque ; les tests viennent après toutes les
interventions, pour valider l'ensemble.

## Cas 2 — Un disque « PASSED » à remplacer

**Situation.** Pendant le diagnostic d'un PC à revendre, l'utilitaire SMART affiche « PASSED »
pour le disque dur (relevé du chapitre 10).

{_console(*(f"{name:<24}{value}" for name, value in CASE2_SMART))}

**Résolution.**

1. Lire les **attributs**, pas le résumé : {pending} secteurs en attente et autant
   d'illisibles, 24 réalloués.
2. Règle du cours : secteurs en attente au-dessus de 0 → verdict **{smart}**.
3. Décision : remplacer le disque (SSD compatible), **effacer ou détruire** l'ancien avec trace
   (s'il ne se lit plus entièrement, la destruction physique s'impose).
4. Rapport : valeurs SMART de l'ancien disque, numéro de série du nouveau, tests du nouveau.

**Conclusion rédigée.** « Disque dur d'origine : {pending} secteurs en attente et {pending}
illisibles malgré un résultat global PASSED ; remplacé par un SSD SATA (n° de série noté) ;
ancien disque détruit par la filière agréée, certificat joint. »

## Cas 3 — La batterie d'un portable de prêt

**Situation.** Un portable sera prêté aux élèves. Rapport de batterie de Windows :

{_console(*CASE3_SCREEN)}

**Résolution.**

1. Capacité restante = {CASE3_FULL} ÷ {CASE3_DESIGN} × 100 = **{health} %** (usure de
   {100 - health} %, {CASE3_CYCLES} cycles).
2. Convention de l'atelier : à remplacer sous {BATTERY_REPLACE_BELOW} % → verdict **{verdict}**.
3. Commander la **batterie de référence exacte** pour ce modèle (fiche du fabricant) ; PC
   éteint, chargeur débranché, remplacement selon la notice ; ancienne batterie à la
   **collecte des batteries**.
4. Nouveau rapport de batterie, test d'autonomie, rapport.

**Conclusion rédigée.** « Batterie d'origine à {health} % de sa capacité ({CASE3_CYCLES}
cycles) : remplacée par la référence du fabricant ; nouveau rapport : capacité à pleine charge
conforme ; ancienne batterie déposée à la collecte des batteries. »

## Cas 4 — Portable qui chauffe : nettoyer et prouver

**Situation.** Un portable s'éteint pendant les jeux. Limite du processeur (fiche) :
{CASE4_LIMIT} °C. Relevés en charge **avant** nettoyage :

{_temps_table(CASE4_BEFORE)}

**Résolution.**

1. **Diagnostic** : grilles encrassées, ventilateur bruyant ; à {before} °C le processeur
   frôle sa limite, baisse sa fréquence puis le PC s'arrête.
2. **Nettoyage** (accord et sauvegarde en ordre) : chargeur débranché, batterie déconnectée
   selon la notice, ventilateur bloqué, air sec par impulsions dans le radiateur, pâte neuve.
3. **Mesures après**, même charge :

{_temps_table(CASE4_AFTER)}

4. **Rapport** avec les valeurs avant/après.

**Conclusion rédigée.** « Radiateur et ventilateur nettoyés, pâte renouvelée : {after} °C après
30 minutes de charge contre {before} °C en 10 minutes avant, sans arrêt. »
"""


def _pitfalls() -> str:
    return """> **Effacer sans l'accord écrit du propriétaire** — sur la demande d'un proche, d'un
> collègue ou « pour rendre service ».

> **Réinstaller sans sauvegarde vérifiée** ni refus signé du client.

> **Croire qu'un formatage rapide, une suppression de partitions ou une remise à zéro
> efface les données** avant une revente.

> **Effacer un SSD par passes d'écrasement ou le défragmenter** : seule la commande du SSD (ou
> l'effacement cryptographique) atteint toutes les cellules.

> **Oublier le certificat d'effacement** : sans trace, rien ne prouve que les données ont
> disparu.

> **Passer l'aspirateur dans le boîtier** ou souffler un ventilateur sans bloquer ses pales.

> **Ouvrir un bloc d'alimentation** pour le dépoussiérer : jamais, on souffle par les grilles.

> **Flasher le firmware sur batterie faible**, avec un fichier d'un autre modèle, ou sans
> suspendre BitLocker.

> **Se fier au résultat global « PASSED »** d'un relevé SMART sans lire les attributs.

> **Écrire « RAS » ou « tout fonctionne »** au lieu des valeurs des tests.

> **Jeter une pile, une batterie ou un appareil à la poubelle** ; percer une batterie gonflée.

> **Remettre un PC sans numéro de série, sans check-list ni signature.**
"""


def _exercises_intro() -> str:
    return f"""{len(PRACTICE_ITEMS)} exercices corrigés : remises en ordre (reconditionnement, nettoyage,
firmware), décisions de protection des données (opérations, sort des données, technique
d'effacement, demande d'un tiers, SSD), lecture de relevés (SMART, températures, batterie, pile
de la carte mère), formulaires (réception, remise, tri des déchets) et rapport à corriger.
Rédige ta réponse sur papier **avant** d'ouvrir le corrigé ; toute réponse équivalente et
justifiée est acceptée. Ces mêmes exercices sont proposés dans
[S'entraîner](/uaa/{PR04_SLUG}/practice), avec correction après envoi.

{_exercises_html()}
"""


_ANSWER_TYPES = {
    "short_answer": "réponse courte",
    "long_answer": "réponse développée",
    "document_analysis": "analyse de document",
}


def _mini_exam() -> str:
    rows = "\n".join(
        f"| {i} | {item.title} | {_ANSWER_TYPES[item.question_type]} | {item.total_points:g} |"
        for i, item in enumerate(EXAM_ITEMS, start=1)
    )
    return f"""Le mini-examen se passe dans l'onglet [Examen blanc](/uaa/{PR04_SLUG}/exam) : **10 questions à réponse
libre**, chacune notée sur **2 points**, soit une note sur **{EXAM_TOTAL_POINTS}**. Les
questions ne figurent pas dans ce cours.

| N° | Thème | Type | Points |
|---|---|---|---|
{rows}

**Déroulement.** Chaque question est une situation complète : toutes les informations
nécessaires sont dans l'énoncé et ses documents (fiches, relevés fictifs).
**Aucune correction n'est visible pendant la passation** ; tes réponses sont enregistrées au
fur et à mesure. Après l'envoi, chaque réponse est corrigée selon le **barème analytique** de la
question (critères et points), puis tu vois ta note sur {EXAM_TOTAL_POINTS}, le corrigé et le
barème.

**Ce que valorise le barème.** La **bonne décision sur les données** (accord écrit, sauvegarde,
technique adaptée au support), les **précautions justifiées**, la **lecture correcte des
relevés** et la **trace** (valeurs, certificat, rapport) — pas la récitation de sigles. Une
autre formulation juste est acceptée.

**Nature de la correction.** Les réponses rédigées reçoivent une **proposition de correction
automatique** (assistée par IA) appuyée sur le barème : c'est un repère d'entraînement, pas une
note officielle ; en cas de doute, compare ta réponse au corrigé.
"""


def _memo() -> str:
    return f"""## Mémo

- **Opérations** : réparation (une panne, même client, données gardées) · reconditionnement
  (PC complet pour un nouvel utilisateur) · remise à zéro (système neuf, données pas forcément
  illisibles) · effacement sécurisé (données illisibles, certificat).
- **Réception** : numéro de série, accessoires, état précis et photos, demande claire, données
  et accord écrit, signatures.
- **Diagnostiquer avant d'intervenir** : UEFI, SMART, mémoire, batterie, ports.
- **Données** : pas d'accord écrit du propriétaire, pas d'effacement ; pas de sauvegarde
  vérifiée (ou de refus signé), pas de réinstallation ; confidentialité.
- **Effacement** : HDD → écrasement complet ou commande du disque ; SSD → commande d'effacement
  sécurisé / Sanitize ou effacement cryptographique ; hors d'usage → destruction ; **jamais**
  formatage rapide ; **toujours** un certificat.
- **Nettoyage** : débranché, bracelet, pales bloquées, air sec par impulsions, pinceau, alcool
  isopropylique ; ni aspirateur ni eau ; bloc jamais ouvert.
- **Refroidissement** : mesurer avant/après ; à surveiller à moins de {TEMP_ALERT_MARGIN} °C de la
  limite ; pâte neuve à chaque démontage.
- **Pièces** : mesure → compatibilité → accord → hors tension → test → numéros de série.
- **Firmware** : utile, bon modèle, site du fabricant, secteur stable, BitLocker suspendu, ne
  jamais couper.
- **Tests** : RAM, SMART (attributs, pas le résumé), températures, ports, 30 min de stabilité,
  batterie (sous {BATTERY_REPLACE_BELOW} % → à remplacer, convention du cours).
- **Remise** : check-list, démonstration, accessoires, conseils, signature.
- **Déchets** : DEEE (Recupel), piles et batteries à part (Bebat), disque effacé avant dépôt,
  batterie gonflée isolée.
- **Rapport** : identification, accord et données, diagnostic, actions, valeurs, déchets,
  conclusion signée, étiquette.

## Glossaire des termes employés

- **BitLocker** : chiffrement de disque de Windows ; une clé de récupération est demandée si le
  démarrage change (firmware).
- **Certificat d'effacement** : document qui prouve l'effacement d'un support (numéro de série,
  technique, date, technicien).
- **DEEE** : déchets d'équipements électriques et électroniques.
- **Effacement cryptographique** : destruction de la clé d'un support chiffré, qui rend ses
  données illisibles.
- **Firmware (UEFI/BIOS)** : logiciel de la carte mère qui démarre le PC.
- **Pâte thermique** : produit qui comble les micro-vides entre processeur et radiateur.
- **Reconditionnement** : remise en état complète d'un PC pour un nouvel utilisateur.
- **Remise à zéro** : réinitialisation ou réinstallation du système.
- **Sanitize** : commande d'effacement intégrée à un SSD ou un disque récent.
- **SMART** : autosurveillance des disques (attributs d'usure et d'erreurs).
- **Traçabilité** : possibilité de retrouver l'historique d'un appareil et de ses pièces.
"""


def _sources() -> str:
    return """## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), pp. 3 et 5 : épreuve uniquement écrite, exigence AP-14
  « Montage, démontage et reconditionnement d'un PC ». Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
  Programme officiel n° 345/2007/249 (option AMPCR).
- **Effacement des supports** : NIST SP 800-88, *Guidelines for Media Sanitization* (niveaux
  effacer / purger / détruire, particularités des SSD) ; documentation des commandes ATA
  Secure Erase, Sanitize et NVMe Format ; outils des fabricants de SSD.
- **Firmware et BitLocker** : notices des fabricants de cartes mères et de portables ;
  documentation Microsoft (suspension de BitLocker avant une mise à jour du firmware, rapport
  de batterie `powercfg /batteryreport`).
- **Tests** : documentation de MemTest86, du Diagnostic de mémoire Windows et de smartmontools
  (attributs SMART des disques durs et des SSD NVMe).
- **Déchets** : directive européenne 2012/19/UE relative aux DEEE ; Recupel (collecte des
  appareils électriques en Belgique) et Bebat (piles et batteries).

Les procédures, l'arbre de décision des données, le tableau des techniques d'effacement, la vue
annotée, les formulaires, les règles de lecture SMART et de batterie et les relevés du cours
sont **produits par programme** depuis des données **vérifiées par des tests automatiques** ;
aucun schéma n'est tiré d'une image générée ni d'une photographie.

## Compléments pédagogiques (non imposés par la liste officielle)

La liste des pp. 5-6 demande le montage, le démontage et le **reconditionnement** d'un PC
(AP-14), sans détailler son contenu. Sont des **compléments**, signalés comme tels :

- la protection des données du client : accord écrit, sauvegarde, confidentialité, effacement
  sécurisé (AP-C03, repris en PR12 et PR28) ;
- les seuils de lecture (SMART, batterie à 80 %, température à 10 °C de la limite) : ce sont
  des **conventions du cours**, pas des normes ; la fiche du fabricant fait foi ;
- la filière des déchets en Belgique (Recupel, Bebat).

## Supports fictifs

Les fiches, relevés, rapports, écrans et situations de ce cours sont **fictifs** et reconstitués
pour l'entraînement ; ils ne décrivent aucun produit réel. Aucun n'est une question officielle
ou déjà posée par le Jury.
"""


def pr04_course_sections() -> list[tuple[str, str]]:
    """Blocs du cours (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("PR04 — Objectifs et place dans l'épreuve", _objectives()),
        ("PR04 — 1. Réparation, reconditionnement, remise à zéro ou effacement sécurisé", _operations()),
        ("PR04 — 2. Réception : état initial, inventaire et numéros de série", _reception()),
        ("PR04 — 3. Diagnostic avant intervention", _diagnosis()),
        ("PR04 — 4. Protection des données : accord écrit, sauvegarde et confidentialité", _data_protection()),
        ("PR04 — 5. Effacement sécurisé HDD et SSD : la technique adaptée au support", _secure_erase()),
        ("PR04 — 6. Nettoyage non destructif", _cleaning()),
        ("PR04 — 7. Poussière, refroidissement et températures", _cooling()),
        ("PR04 — 8. Remplacement de pièces et contrôle de compatibilité", _parts()),
        ("PR04 — 9. Mises à jour du firmware, du système et des pilotes : précautions", _updates()),
        ("PR04 — 10. Tests après intervention : RAM, SMART, températures, ports et stabilité", _tests()),
        ("PR04 — 11. Check-list de réception et de remise au client", _handover()),
        ("PR04 — 12. Déchets : DEEE, piles et batteries", _waste()),
        ("PR04 — 13. Rapport et traçabilité", _report()),
        ("PR04 — Exemples : quatre cas intégralement résolus", _examples()),
        ("PR04 — Pièges et erreurs fréquentes", _pitfalls()),
        (f"PR04 — Exercices corrigés ({len(PRACTICE_ITEMS)}) et leurs corrigés", _exercises_intro()),
        ("PR04 — Mini-examen noté sur 20 : mode d'emploi", _mini_exam()),
        ("PR04 — Fiche mémo et glossaire", _memo()),
        ("PR04 — Sources et compléments pédagogiques", _sources()),
    ]
