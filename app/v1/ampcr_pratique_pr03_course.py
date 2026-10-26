"""Cours PR03 « Montage et démontage d'un PC — procédure écrite » — parcours AMPCR pratique
écrite (ticket #204).

Matière : intégralement celle du ticket #204 (préparation du poste, outillage, ESD,
inventaire et photos ; sauvegarde et autorisations ; vérification de compatibilité ; ordre de
montage : carte mère, entretoises, processeur, pâte thermique, refroidissement, mémoire, SSD,
bloc, carte graphique, câbles ; connecteurs de façade ; contrôle visuel ; premier démarrage
POST/UEFI ; tests mémoire, températures et disques ; gestion des câbles et flux d'air ;
démontage inverse documenté, visserie, fragilité des sockets, connecteurs et dissipateurs ;
remplacement d'un composant et remontage ; pannes au premier démarrage), découpée en blocs
titrés (le titre pilote le type de carte, `app.card_kind` : aucun titre de bloc théorique ne
contient « examen », « source », « exemple », « exercice », « méthode », « piège »,
« attention » ni « mémo »). Aucune manipulation sous tension ni ouverture de bloc
d'alimentation. Données et schémas : `app.v1.ampcr_pratique_pr03_figures` ; exercices et
mini-examen : `app.v1.ampcr_pratique_pr03_bank`. Mise en forme partagée avec les autres
cours pratiques.
"""

from html import escape

from app.v1.ampcr_pratique_pr03_bank import EXAM_ITEMS, EXAM_TOTAL_POINTS, PRACTICE_ITEMS
from app.v1.ampcr_pratique_pr03_figures import (
    ASSEMBLY_FIGURE,
    BOOT_TREE_FIGURE,
    CASE3_DETECTED,
    CASE3_EXPECTED,
    CASE3_SCREEN,
    CASE4_AFTER,
    CASE4_BEFORE,
    CASE4_LIMIT,
    CPU_FIGURE,
    DISASSEMBLY_FIGURE,
    FIRST_BOOT_FIGURE,
    FRONT_PANEL_FIGURE,
    FRONT_PANEL_PINS,
    PREP_FIGURE,
    PROCEDURES,
    SCREWS,
    STANDOFF_FIGURE,
    STATUS_LABELS,
    TEMP_ALERT_MARGIN,
    UEFI_FIGURE,
    VISUAL_CHECKS,
    inventory_gaps,
    temperature_verdict,
)
from app.v1.ampcr_pratique_pr06_course import _exercise_card, _fig, _req

PR03_TITLE = "Montage et démontage d'un PC — procédure écrite"
PR03_SLUG = "ampcr-pratique-pr03"


def _exercises_html() -> str:
    return "\n\n".join(
        _exercise_card(i, item, anchor_prefix="pr03") for i, item in enumerate(PRACTICE_ITEMS, start=1)
    )


def _console(*lines: str) -> str:
    return f'<pre class="jc-pr-console" tabindex="0">{escape(chr(10).join(lines))}</pre>'


def _ex(*keys: str) -> str:
    """Renvoi texte vers les exercices corrigés liés à un chapitre (séquence « Exercices
    corrigés ») : pas de lien d'ancre, la page n'affiche qu'une séquence à la fois et un
    clic sur une ancre d'une autre séquence ne la ferait pas apparaître."""
    return ", ".join(f"**{key}**" for key in keys) + " (séquence « Exercices corrigés »)"


# --- Tableaux de données (générés depuis les données vérifiées) ------------------------------


def _screws_table() -> str:
    rows = "\n".join(f"| {what} | {screw} | {note} |" for what, screw, note in SCREWS)
    return "| Élément fixé | Vis la plus courante | Remarque |\n|---|---|---|\n" + rows


def _visual_checks_table() -> str:
    rows = "\n".join(f"| ☐ | {what} | {check} |" for what, check in VISUAL_CHECKS)
    return "| Fait | Élément | Vérification |\n|---|---|---|\n" + rows


def _front_panel_table() -> str:
    rows = "\n".join(
        f"| {p.number} | {p.signal} | {p.role} | {'oui' if p.polarized else 'non'} |" for p in FRONT_PANEL_PINS
    )
    return "| Broche | Signal | Câble du boîtier | Polarisé |\n|---|---|---|---|\n" + rows


def _standoff_legend() -> str:
    rows = "\n".join(f"| {status} | {label} |" for status, label in STATUS_LABELS.items())
    return "| Verdict | Signification |\n|---|---|\n" + rows


def _procedures_list() -> str:
    return "\n".join(
        f"{i}. **{title}** ({len(steps)} étapes)" for i, (title, steps) in enumerate(PROCEDURES, start=1)
    )


def _temps_table(rows: tuple[tuple[str, int], ...]) -> str:
    body = "\n".join(
        f"| {moment} | {temp} °C | {temperature_verdict(temp, CASE4_LIMIT)} |" for moment, temp in rows
    )
    return "| Moment | Température du processeur | Verdict |\n|---|---|---|\n" + body


# =============================================================================================
# Sections du cours (titre du bloc, Markdown / HTML)
# =============================================================================================


def _objectives() -> str:
    return f"""## Ce que tu sauras faire, par écrit

L'épreuve pratique AMPCR se passe **uniquement par écrit** (consignes officielles 2026-2027/1,
p. 3) : on ne te demande pas de monter un PC devant le jury, mais de **rédiger** comment tu
le fais, dans quel ordre, avec quelles précautions, et de **repérer les erreurs** d'un
montage décrit ou photographié. À partir d'un bon de montage, d'une fiche d'intervention,
d'un relevé ou d'un écran de firmware, tu dois savoir :

1. **préparer** une intervention : autorisation, sauvegarde, état initial, mise hors tension,
   poste antistatique, photos ;
2. **ordonner et justifier** le montage complet d'un PC et le démontage inverse ;
3. **décrire les gestes délicats** : processeur, pâte thermique, ventirad, mémoire, M.2,
   entretoises, connecteurs de façade ;
4. **contrôler** un montage avant la mise sous tension, puis au **premier démarrage** (POST,
   UEFI, tests mémoire, températures, disques) ;
5. **diagnostiquer une panne au premier démarrage** due au montage et la corriger ;
6. **rédiger le compte rendu** de l'intervention.

Ce cours contient **5 procédures illustrées** :

{_procedures_list()}

## Exigences officielles travaillées dans ce cours

{_req("AP-14")}

Le **reconditionnement** (nettoyage, contrôles de remise, effacement des données) est l'autre
volet de cette exigence : il est traité en PR04.

Complément pédagogique (hors liste officielle des pp. 5-6, signalé comme tel) :

{_req("AP-C02")}

L'identification des composants est traitée en [PR01](/uaa/ampcr-pratique-pr01), les
connecteurs d'alimentation et la compatibilité en [PR02](/uaa/ampcr-pratique-pr02), la
démarche complète de diagnostic des pannes en [PR06](/uaa/ampcr-pratique-pr06).

## Lien avec la théorie

Les notions de base sont présentées dans la théorie AMPCR :
[MC05 Alimentation, refroidissement, ESD et sécurité électrique](/uaa/ampcr-mc05) et
[MC06 Montage, démontage et reconditionnement d'un PC](/uaa/ampcr-mc06). Ce cours-ci est
**pratique** : procédures rédigées, relevés, erreurs à repérer et réponses justifiées, comme
dans un dossier d'examen.

## Comment travailler ce cours

Lis les chapitres dans l'ordre : chacun donne ses **objectifs**, la **théorie**, la
**procédure professionnelle** à rédiger, l'**erreur fréquente**, ce qu'on attend **à l'écrit**
et un **repère rapide**, avec un renvoi vers les exercices liés. Étudie ensuite les **quatre
cas résolus**, fais les **{len(PRACTICE_ITEMS)} exercices corrigés** (ici ou dans
« S'entraîner », correction après envoi), puis passe le **mini-examen noté sur
{EXAM_TOTAL_POINTS}** dans l'onglet « Examen blanc ».

> **Important —** les bons de montage, fiches, relevés et écrans de ce cours sont des
> **supports fictifs** construits pour s'entraîner : ils ne décrivent aucun produit réel, et
> seuls la notice et le manuel du fabricant font foi pour un vrai matériel. Aucun exercice
> n'est une question officielle ni une question déjà posée par le Jury.
> **Aucune manipulation ne se fait sous tension, et un bloc d'alimentation ne s'ouvre jamais.**
"""


def _prepare() -> str:
    return f"""**Objectifs** : préparer un poste de travail sûr, choisir l'outillage, se protéger des
décharges électrostatiques et documenter l'état du PC avant d'y toucher.

## 1.1 Le poste et l'outillage

- **Table dégagée, stable et éclairée**, sans boisson ; le PC est posé **à plat**, côté à
  ouvrir vers le haut.
- **Outillage** : tournevis cruciformes **PH1 et PH2** (et PH0 pour les vis M.2), pince à
  bec fin, lampe, **bac à vis à cases** ou sachets étiquetés, colliers de câblage, alcool
  isopropylique et chiffon non pelucheux, pâte thermique, étiquettes et marqueur, appareil
  photo (téléphone).
- **Pas de visseuse électrique** réglée fort : elle arrache les filetages. Une pointe de
  tournevis aimantée évite de laisser tomber une vis sur la carte ; une vis tombée se
  récupère **avant** toute mise sous tension.

## 1.2 Électricité statique (ESD)

- Une **décharge électrostatique** imperceptible pour toi (quelques centaines de volts) peut
  endommager une puce **sans dégât visible** : panne immédiate ou aléatoire plus tard.
- **Bracelet antistatique** relié au châssis métallique (ou au tapis antistatique relié à la
  terre), **tapis antistatique**, ni pull en laine ni bijou ; pièces gardées dans leur
  **sachet antistatique** jusqu'au montage et tenues **par les bords**.
- Une carte mère se pose **sur son carton** ou sur le tapis, jamais sur la moquette.

## 1.3 Inventaire et photos

- **Inventaire** des pièces reçues (référence, numéro de série, état de l'emballage) comparé
  au **bon de montage** : une pièce manquante ou abîmée se signale **avant** de commencer.
- **Photos** : de l'extérieur à la réception, puis de l'intérieur **avant de débrancher quoi
  que ce soit** ; elles servent au remontage et prouvent l'état initial.

{_fig(PREP_FIGURE)}

**Procédure professionnelle (à rédiger)** : autoriser → relever l'état initial → couper
(arrêt, interrupteur sur 0, **câble secteur débranché**, appui sur le bouton) → installer le
poste → bracelet → photographier l'intérieur.

**Erreur fréquente** : travailler sur un PC « éteint » mais branché. Le bloc garde le
**+5 VSB** sur la carte mère tant que le câble secteur est branché : **éteint n'est pas hors
tension** (voir PR02).

**À l'écrit** : chaque précaution avec sa raison — « je débranche le câble secteur, car le
+5 VSB reste présent PC éteint ; je mets un bracelet relié au châssis, car une décharge
électrostatique peut détruire une puce sans trace visible ».

**Repère rapide** : poste dégagé · PH1/PH2 · bac à vis · **débrancher** · bracelet · photos
avant de débrancher. Exercices liés : {_ex("E01", "E09")}.
"""


def _authorization() -> str:
    return f"""**Objectifs** : protéger les données et le client avant toute intervention ; savoir ce
que contient une fiche d'intervention.

## 2.1 Sauvegarde et autorisation

- Un démontage peut **toujours** mal se passer (connecteur cassé, disque heurté). Avant
  d'ouvrir le PC d'un client : **sauvegarde** des données (copie **vérifiée**, qu'on sait
  relire) faite par le client ou avec son accord ; s'il refuse, son **refus est écrit**.
- **Autorisation écrite** : ce qui sera fait, le coût éventuel, ce qui peut être remplacé.
  Le technicien n'ouvre pas un PC, ne change pas une pièce et n'efface rien **sans accord**.
- **Confidentialité** : on ne consulte pas les fichiers du client ; un mot de passe confié
  sert uniquement à tester, puis le client est invité à le changer.

## 2.2 État initial et fiche d'intervention

La **fiche d'intervention** (papier ou logiciel) porte au minimum :

| Rubrique | Contenu |
|---|---|
| Identification | date, client, technicien, matériel, **numéro de série** |
| Demande | ce que le client a demandé, avec ses mots |
| Autorisation | accord signé, sauvegarde faite ou refus écrit |
| État initial | défauts visibles, ce qui fonctionne **avant**, accessoires remis, photos |
| Actions | ce qui a été fait, pièces posées et retirées (références, numéros de série) |
| Contrôles | tests effectués et valeurs relevées |
| Conclusion | résultat, conseils, date et signature de remise |

**Procédure professionnelle (à rédiger)** : demande notée → sauvegarde vérifiée (ou refus
écrit) → autorisation signée → état initial relevé (photos, numéro de série, défauts) →
intervention → contrôles → compte rendu remis.

**Erreur fréquente** : commencer le démontage « pour gagner du temps » avant la sauvegarde ou
l'accord. En cas de problème, rien ne prouve l'état d'origine ni l'accord du client.

**À l'écrit** : « je vérifie que la sauvegarde existe et se relit, sinon je la fais faire ;
je fais signer l'autorisation ; je relève l'état initial ». La protection des données
(effacement, réinstallation) est approfondie en PR04 et PR28.

**Repère rapide** : **sauvegarde → accord → état initial**, toujours avant le premier
tournevis. Exercices liés : {_ex("E09")}.
"""


def _compatibility() -> str:
    return """**Objectifs** : vérifier, avant de monter, que les pièces vont ensemble — sur les fiches,
pas en essayant.

## 3.1 La grille avant montage

La compatibilité se vérifie **sur papier avant le montage** (détail en
[PR01](/uaa/ampcr-pratique-pr01) et [PR02](/uaa/ampcr-pratique-pr02)) :

| Critère | Ce qu'on compare |
|---|---|
| Processeur ↔ carte mère | même **socket**, processeur dans la **liste** de la carte, version du **firmware** |
| Mémoire ↔ carte mère | même génération (**DDR4 ≠ DDR5**), format **DIMM**, capacité maximale |
| Carte mère ↔ boîtier | format **ATX / microATX / Mini-ITX** accepté par le boîtier |
| Ventirad ↔ socket et boîtier | fixation pour ce socket, **hauteur** inférieure au maximum du boîtier |
| Carte graphique ↔ boîtier et bloc | **longueur**, épaisseur, connecteurs PCIe/12V-2x6, puissance recommandée |
| SSD M.2 ↔ emplacement | longueur (2280), **interface NVMe ou SATA** acceptée par l'emplacement |
| Bloc ↔ boîtier et configuration | format **ATX/SFX**, puissance avec marge, connecteurs nécessaires |

## 3.2 Pendant le montage

- **Ne jamais forcer** : une pièce compatible s'insère sans effort, dans un seul sens
  (encoches, détrompeurs, triangle). Si elle résiste, **on s'arrête et on vérifie**.
- « **Ça rentre** » ne prouve pas la compatibilité (un SSD M.2 SATA entre dans un emplacement
  NVMe uniquement et n'est pas détecté) ; « **ça ne rentre pas** » signale presque toujours
  une erreur d'orientation ou de pièce.

**Procédure professionnelle (à rédiger)** : relever les fiches → contrôler chaque ligne de la
grille avec les valeurs → noter « conforme / non conforme / à vérifier » → corriger le bon de
montage **avant** de commencer.

**Erreur fréquente** : découvrir pendant le montage que la carte graphique est trop longue ou
que la mémoire est en DDR4 pour une carte DDR5 — la vérification se fait **avant**.

**À l'écrit** : un verdict par critère, avec les **valeurs** des fiches.

**Repère rapide** : socket + liste + firmware · DDR · format · hauteur · longueur · M.2 ·
bloc. **Ce qui résiste n'est pas à forcer.**
"""


def _order() -> str:
    return f"""**Objectifs** : connaître l'ordre de montage recommandé et savoir le **justifier**.

## 4.1 L'ordre recommandé

{_fig(ASSEMBLY_FIGURE)}

## 4.2 Pourquoi cet ordre

- **Carte mère équipée hors du boîtier** (processeur, mémoire, M.2, ventirad) : accès facile
  au socket et aux emplacements, pas de risque de heurter les broches du socket, la carte ne
  fléchit pas, on voit les repères et les clips.
- **Mémoire avant le ventirad** : un gros ventirad peut masquer les emplacements de mémoire.
- **Bloc et disques avant la carte graphique** : la carte graphique, longue et lourde, masque
  les emplacements voisins, les connecteurs SATA, M.2 et de façade ; elle vient tard.
- **Câblage en dernier** : on range les câbles proprement et on contrôle chaque connecteur.
- **Contrôle visuel puis premier démarrage boîtier ouvert** : on corrige sans tout redémonter.

**Quand adapter l'ordre** : la **notice** du ventirad ou du boîtier prime — ventirad à
**plaque arrière** à poser avant d'installer la carte, **watercooling tout-en-un (AIO)** dont
le radiateur se fixe au boîtier, boîtier compact où le bloc doit entrer en premier.

**Procédure professionnelle (à rédiger)** : la liste numérotée des dix étapes de la
procédure 2, avec **une raison** pour chaque choix d'ordre qui n'est pas évident.

**Erreur fréquente** : monter la carte mère vide dans le boîtier puis y installer le
processeur et le ventirad, à bout de bras, au risque de faire glisser le tournevis sur la
carte ou de tordre les broches.

**À l'écrit** : « j'installe le processeur, la mémoire et le SSD M.2 sur la carte posée sur
son carton, car l'accès est facile et la carte ne fléchit pas ».

**Repère rapide** : **carte équipée dehors → boîtier → bloc, disques → carte graphique →
câbles → contrôle → premier démarrage**. Exercices liés : {_ex("E02", "E14")}.
"""


def _board_outside() -> str:
    return f"""**Objectifs** : installer le processeur, la pâte thermique, le ventirad, la mémoire et
le SSD M.2 sans abîmer la carte ni les composants.

## 5.1 Le processeur

- **Socket LGA** (Intel LGA1700/LGA1851, AMD AM5) : les **broches sont sur la carte mère**,
  très fragiles ; un **capot de protection** les couvre jusqu'à la fermeture du levier.
- **Socket PGA** (AMD AM4) : les **broches sont sous le processeur** ; on lève le levier
  (ZIF), on aligne, le processeur **tombe seul** dans les trous.
- Dans les deux cas : **triangle doré** du processeur sur le **repère** du socket, encoches
  sur les ergots, pose **à la verticale**, **aucune pression**. Un processeur qui ne repose
  pas à plat est mal orienté : **on ne force jamais**.
- Le **capot** de protection du socket LGA **se garde** : il protège les broches si le
  processeur est retiré et il est souvent exigé pour un retour sous garantie.

{_fig(CPU_FIGURE)}

## 5.2 Pâte thermique et ventirad

- La **pâte thermique** remplit les micro-vides entre le processeur et la semelle du
  ventirad : **une fine couche suffit**. Méthode courante : **une petite noisette au centre**
  (taille d'un petit pois), la pression du ventirad l'étale ; suivre la notice si elle
  indique autre chose. Trop de pâte déborde et isole moins bien.
- Certains ventirads ont de la **pâte pré-appliquée** : on n'en rajoute pas.
- **Retirer le film plastique** de la semelle (oubli classique → surchauffe immédiate).
- **Serrage en croix et progressif** (un demi-tour par vis, en diagonale) : pression
  uniforme, ventirad à plat.
- Câble du ventilateur sur **CPU_FAN** (surveillé par la carte : sans lui, certaines cartes
  refusent de démarrer ou affichent une alerte) ; pompe d'un AIO sur **AIO_PUMP**.
- **À chaque démontage du ventirad, la pâte se renouvelle** : nettoyage à l'**alcool
  isopropylique** (90 % ou plus) avec un chiffon non pelucheux.

## 5.3 Mémoire et SSD M.2

- **Barrettes** : ouvrir les clips, aligner l'**encoche** sur le détrompeur, enfoncer **bien
  droit** avec les deux pouces jusqu'au **clic** (clips fermés des deux côtés). Une barrette à
  moitié enfoncée est la première cause de « pas d'image ».
- **Emplacements** : avec deux barrettes, utiliser ceux que le **manuel** indique pour le
  double canal (souvent **A2 et B2**, les deuxième et quatrième à partir du processeur).
- **SSD M.2** : vérifier l'**entretoise M.2** à la position de la longueur (2280), insérer le
  module **en biais (environ 30°)**, le rabattre et le fixer (**vis M2** ou loquet). Retirer
  le film du dissipateur M.2 de la carte s'il y en a un.

**Procédure professionnelle (à rédiger)** : procédure 3 (sept étapes) pour le processeur et
le ventirad ; puis mémoire (manuel, encoche, clic) et M.2 (entretoise, 30°, vis).

**Erreur fréquente** : forcer un processeur ou fermer le levier dessus quand il n'est pas à
plat ; oublier le film du ventirad ; étaler une couche épaisse de pâte au doigt.

**À l'écrit** : l'orientation (triangle, encoches), « sans pression », la quantité de pâte, le
film, le serrage en croix, CPU_FAN ; pour la mémoire, l'emplacement d'après le manuel.

**Repère rapide** : triangle sur repère · poser, jamais forcer · capot gardé · noisette de
pâte · **film retiré** · serrage en croix · CPU_FAN · barrette au clic · M.2 à 30° puis vissé.
Exercices liés : {_ex("E03", "E05", "E15")}.
"""


def _case() -> str:
    return f"""**Objectifs** : préparer le boîtier, poser les entretoises et installer la carte mère, le
bloc, les disques et la carte graphique.

## 6.1 Entretoises et plaque d'E/S

- La carte mère ne touche **jamais** directement le métal du boîtier : elle repose sur des
  **entretoises** (plots filetés) vissées dans le fond.
- Règle : **une entretoise sous chaque trou de la carte, aucune ailleurs**. Une entretoise
  sans trou en face touche les **pistes** au dos de la carte : **court-circuit** possible (le
  PC s'allume une fraction de seconde puis s'éteint, ou ne démarre pas). Une entretoise qui
  manque laisse la carte **fléchir** quand on branche une barrette ou un connecteur.
- Les boîtiers sont souvent livrés avec des entretoises **pour une carte ATX** : avec une carte
  microATX ou Mini-ITX, on **compare** chaque trou avant de poser la carte.
- **Plaque d'E/S** (cache arrière des ports) : à clipser dans le boîtier **avant** la carte,
  sauf si elle est intégrée à la carte ; ses languettes ne doivent pas entrer dans les ports.

{_fig(STANDOFF_FIGURE)}

{_standoff_legend()}

## 6.2 Carte mère, bloc et disques

- **Carte mère** : la présenter en biais, ports dans la plaque d'E/S, puis à plat sur les
  entretoises ; vérifier l'alignement de chaque trou ; visser **sans forcer**, en commençant
  par les vis centrales.
- **Bloc d'alimentation** : quatre vis à l'arrière ; **ventilateur vers le filtre** du fond
  quand le boîtier en a un, sinon vers l'intérieur ; câbles modulaires **du même bloc**
  uniquement (PR02).
- **Disques** : 3,5 pouces et 2,5 pouces dans leurs baies ou tiroirs ; câble de **données
  SATA** sur la carte mère et **alimentation SATA** du bloc.

## 6.3 Carte graphique

- Dans le **premier emplacement PCIe x16** (le plus proche du processeur, relié au
  processeur) sauf indication du manuel ; retirer les **caches** de l'arrière du boîtier.
- Enfoncer jusqu'au **clic du clip** de l'emplacement, visser l'**équerre** ; brancher **tous**
  les connecteurs PCIe ou le 12V-2x6 **à fond**, sans adaptateur.
- Une carte lourde peut demander un **support** (béquille) pour ne pas fléchir.

## 6.4 Visserie

{_screws_table()}

Une vis qui ne s'engage pas **à la main** n'est pas la bonne : forcer abîme le filetage. On
utilise les vis **livrées avec le boîtier et les pièces**.

**Procédure professionnelle (à rédiger)** : comparer trous et entretoises → plaque d'E/S →
carte mère vissée → bloc (ventilateur orienté) → disques → carte graphique (x16, clip,
équerre, alimentation complète).

**Erreur fréquente** : laisser les entretoises d'usine sans les comparer aux trous de la carte.

**À l'écrit** : « une entretoise sous chaque trou, aucune ailleurs, car une entretoise sans
trou touche le circuit au dos de la carte ».

**Repère rapide** : entretoise = trou · plaque d'E/S avant la carte · vis sans forcer · bloc
ventilateur vers le filtre · carte graphique x16, clip, équerre, câbles à fond. Exercices
liés : {_ex("E07", "E16")}.
"""


def _cabling() -> str:
    return f"""**Objectifs** : brancher sans erreur l'alimentation, la façade, les USB et l'audio
internes et les ventilateurs.

## 7.1 Alimentation

- **ATX 24 broches** (souvent 20+4) : carte mère, jusqu'au **clic** du loquet.
- **EPS 8 broches « CPU »** (4+4) : en haut à gauche de la carte en général ; **sans lui, le
  processeur n'est pas alimenté** (pas de démarrage ou arrêt immédiat).
- **PCIe 6+2 / 12V-2x6** : carte graphique, tous les connecteurs demandés.
- **SATA alimentation** : chaque disque. **EPS et PCIe 8 broches ne s'échangent jamais**
  (PR02).

## 7.2 Connecteur de façade

Les câbles du boîtier (**POWER SW**, **RESET SW**, **POWER LED**, **HDD LED**) se branchent
sur le connecteur de façade de la carte mère (souvent nommé **F_PANEL** ou **JFP1**).

{_fig(FRONT_PANEL_FIGURE)}

{_front_panel_table()}

- **Boutons** (Power, Reset) : simples contacts, **non polarisés**, sens indifférent.
- **LED** : **polarisées** ; le fil de couleur (ou marqué +) va sur la broche **+**. À
  l'envers, la LED reste éteinte, sans dégât.
- **Le manuel de la carte fait foi** : certaines cartes ont un autre brochage. Beaucoup de
  cartes fournissent un petit adaptateur sur lequel on branche les câbles avant de l'enficher.

## 7.3 USB, audio et ventilateurs

- **USB 3.x interne** (19 broches, gros connecteur à détrompeur, broches fragiles : **bien
  droit**), **USB 2.0 interne** (9 broches), **USB-C de façade** (connecteur dédié), **audio
  HD_AUDIO** (pas l'ancien AC'97 si le boîtier propose les deux).
- **Ventilateurs** : CPU_FAN (ventirad), SYS_FAN ou CHA_FAN (boîtier), AIO_PUMP (pompe) ;
  le sens du flux est indiqué par une **flèche** sur le cadre (chapitre 10).

**Procédure professionnelle (à rédiger)** : ATX 24 → EPS → PCIe → SATA (données et
alimentation) → façade d'après le manuel → USB et audio internes → ventilateurs → rangement.

**Erreur fréquente** : oublier l'EPS ; brancher POWER SW sur les broches Reset ; tordre les
broches du connecteur USB 3 en le forçant de travers.

**À l'écrit** : chaque câble, sa broche d'après le manuel, et « LED polarisée, bouton non ».

**Repère rapide** : 24 + **8 CPU** + PCIe · façade d'après le **manuel** · LED + sur + ·
USB 3 bien droit. Exercices liés : {_ex("E08")}.
"""


def _visual_check() -> str:
    return f"""**Objectifs** : contrôler un montage **PC débranché**, avant la première mise sous
tension, avec une grille écrite.

## 8.1 La grille de contrôle

{_visual_checks_table()}

- On contrôle **ligne par ligne**, en touchant chaque connecteur (il doit être clipsé), et on
  **coche** : la grille signée fait partie du compte rendu.
- On **secoue doucement** le boîtier : une vis qui roule s'entend.
- Ce contrôle évite la plupart des « pannes » au premier démarrage, qui sont des **oublis de
  montage**.

**Procédure professionnelle (à rédiger)** : PC débranché → grille complète, ligne par ligne →
corriger chaque anomalie → refaire le contrôle de la ligne corrigée → seulement ensuite,
brancher le secteur.

**Erreur fréquente** : allumer « pour voir » avant le contrôle, avec une vis libre ou l'EPS
débranché.

**À l'écrit** : chaque anomalie, sa **conséquence** prévisible et sa **correction**.

**Repère rapide** : **contrôle visuel PC débranché, avant le premier démarrage**. Exercices
liés : {_ex("E06", "E10")}.
"""


def _first_boot() -> str:
    gaps = inventory_gaps(CASE3_EXPECTED, CASE3_DETECTED)
    return f"""**Objectifs** : réussir et interpréter le premier démarrage ; vérifier dans l'UEFI ce qui
est détecté ; tester la mémoire, les températures et les disques.

## 9.1 POST et premier démarrage

- Au démarrage, le firmware fait le **POST** (*Power-On Self-Test*) : il vérifie le processeur,
  la mémoire et la carte graphique, puis cherche un périphérique de démarrage.
- **Premier démarrage long** : avec une mémoire neuve (surtout en **DDR5**), la carte
  **entraîne la mémoire** ; l'écran peut rester **noir plusieurs minutes**, LED « DRAM »
  allumée. **On ne coupe pas** : couper relance l'opération.
- **LED de diagnostic** (CPU, DRAM, VGA, BOOT), **afficheur de code** ou **bips** : leur sens
  dépend du **fabricant** ; on le lit dans le manuel de la carte (PR06).

## 9.2 Lire l'UEFI

On entre dans l'UEFI (touche **Suppr** ou **F2** en général, indiquée à l'écran) et on
**compare au bon de montage** :

- processeur reconnu (modèle) ;
- **mémoire totale** = somme des barrettes, et emplacements occupés ;
- **disques** reconnus (SATA, M.2) ;
- **température** du processeur au repos et **vitesse de CPU_FAN** ;
- **date et heure** ; ordre de démarrage.

{_fig(UEFI_FIGURE)}

Écarts sur cet écran : **{", ".join(gaps)}** — chacun a une cause de montage probable
(cas 3).

- La mémoire fonctionne d'abord à sa **fréquence standard** (ex. DDR5-4800) ; le **profil
  XMP/EXPO** qui la monte à la vitesse annoncée s'active **après** avoir vérifié la stabilité.

## 9.3 Tester avant la remise

| Test | Outil (exemples) | Ce qu'on relève |
|---|---|---|
| Mémoire | MemTest86 (clé USB), Diagnostic de mémoire Windows | aucune erreur après plusieurs passes |
| Températures | surveillance de l'UEFI, logiciel de surveillance, test de charge | repos et charge, comparés à la fiche |
| Disques | état **SMART** (CrystalDiskInfo, `smartctl`) | « bon » / attributs d'alerte |
| Ports et façade | clé USB, casque, boutons | chaque port, audio, Power, Reset, LED |
| Stabilité | charge de quelques dizaines de minutes | aucun arrêt, aucun redémarrage |

Une température qui atteint la **limite de la fiche** n'est pas normale : le processeur
réduit sa fréquence puis s'arrête pour se protéger. Dans ce cours, on considère « à
surveiller » une valeur à moins de **{TEMP_ALERT_MARGIN} °C** de la limite.

{_fig(FIRST_BOOT_FIGURE)}

**Procédure professionnelle (à rédiger)** : procédure 5 — contrôle visuel → mise sous tension
→ patienter → lire l'UEFI → tester → compte rendu avec les valeurs.

**Erreur fréquente** : conclure « ça marche » à la première image, sans comparer la mémoire,
les disques et les températures au bon de montage.

**À l'écrit** : les valeurs relevées, comparées à ce qui était attendu, puis la conclusion.

**Repère rapide** : POST → patienter → **UEFI comparé au bon** → mémoire, températures,
SMART, ports → compte rendu. Exercices liés : {_ex("E06", "E11", "E12", "E13")}.
"""


def _airflow() -> str:
    return """**Objectifs** : ranger les câbles et organiser le flux d'air pour refroidir et faciliter
la maintenance.

## 10.1 Le flux d'air

- **Entrée d'air frais** en façade (et en bas), **sortie** à l'arrière et en haut : l'air
  chaud monte. Le sens d'un ventilateur est indiqué par la **flèche** moulée sur son cadre.
- Trois ventilateurs qui **extraient** tous ne refroidissent pas mieux : il faut une entrée.
- **Filtres** à poussière sur les entrées ; détails en [PR02](/uaa/ampcr-pratique-pr02)
  (chapitre 5).

## 10.2 La gestion des câbles

- Câbles passés **derrière le plateau** de la carte mère par les passe-câbles, **attachés**
  par colliers ou velcro, **sans tension** sur les connecteurs.
- **Aucun câble** près des pales d'un ventilateur ni devant les entrées d'air ; câbles
  modulaires inutiles **non branchés**.
- Un câblage propre **refroidit mieux** et rend la maintenance plus rapide (on voit et on
  atteint chaque connecteur).

**Procédure professionnelle (à rédiger)** : sens de chaque ventilateur (flèche) → entrées à
l'avant, sorties à l'arrière/haut → câbles derrière le plateau, attachés → aucun câble près
des pales → contrôle.

**Erreur fréquente** : un paquet de câbles devant la façade, ou un ventilateur de façade monté
à l'envers.

**À l'écrit** : chaque défaut et sa correction, justifiée par le chemin de l'air.

**Repère rapide** : **avant → arrière/haut** · flèche du cadre · câbles derrière et attachés.
"""


def _disassembly() -> str:
    return f"""**Objectifs** : démonter un PC dans l'ordre inverse du montage, en documentant chaque
étape et sans abîmer les pièces fragiles.

{_fig(DISASSEMBLY_FIGURE)}

## 11.1 Documenter

- **Photos** de chaque zone et de chaque branchement **avant** de débrancher ; **étiquettes**
  sur les câbles si nécessaire (« SATA 1 — SSD système »).
- **Vis triées** par élément dans un **bac à cases** ou des sachets étiquetés ; les vis M.2,
  minuscules, à part.
- **Fiche de démontage** : ordre suivi, pièces retirées (référence, numéro de série),
  observations (pâte sèche, poussière, connecteur abîmé).

## 11.2 Les pièces fragiles

- **Connecteurs** : on appuie sur le **loquet** (ATX 24, EPS, PCIe, SATA) et on tire sur le
  **connecteur**, jamais sur les fils ; le 12V-2x6 se retire bien droit.
- **Carte graphique** : dévisser l'équerre, débrancher l'alimentation, **ouvrir le clip** de
  l'emplacement (parfois un bouton à pousser ou une languette cachée sous la carte), puis
  sortir à la verticale. Tirer sans ouvrir le clip arrache l'emplacement.
- **Dissipateur / ventirad** : la pâte sèche **colle** ; on tourne doucement le ventirad d'un
  côté à l'autre pour la décoller (elle cède mieux tiède, après quelques minutes de
  fonctionnement suivies d'une mise hors tension complète), puis on soulève. Sur un socket
  **PGA (AM4)**, tirer d'un coup peut **arracher le processeur** du socket, levier fermé :
  broches tordues.
- **Socket LGA** vide : remettre le **capot de protection** ; ne jamais toucher les broches.
- **Mémoire** : ouvrir les clips, la barrette se soulève seule.

**Procédure professionnelle (à rédiger)** : procédure 4 — préparer (autorisation,
sauvegarde, hors tension, ESD) → photographier → débrancher (loquets) → carte graphique →
stockage et mémoire → ventirad → carte mère → ranger et compléter la fiche.

**Erreur fréquente** : tout mettre dans le même gobelet et tirer sur les fils ; arracher un
ventirad collé.

**À l'écrit** : l'ordre, la manière de retirer chaque pièce fragile et la façon de documenter.

**Repère rapide** : **ordre inverse + photos + vis triées** · loquet avant de tirer · clip
PCIe ouvert · ventirad tourné, pas arraché · capot remis. Exercices liés :
{_ex("E04", "E15", "E16")}.
"""


def _replacement() -> str:
    return """**Objectifs** : remplacer un composant et remonter le PC, en contrôlant ce qui a été
touché.

## 12.1 La démarche

1. **Vérifier la panne** et la compatibilité du remplaçant (fiches, chapitre 3) **avant** de
   démonter ; obtenir l'accord du client (prix, pièce).
2. **Préparer** : sauvegarde, état initial, mise hors tension, ESD, photos (procédure 1).
3. **Démonter seulement ce qui est nécessaire** pour atteindre la pièce (procédure 4), en
   documentant.
4. **Remplacer** : même type de pièce ou pièce vérifiée compatible ; gestes du chapitre 5 ou 6.
5. **Remonter** dans l'ordre inverse : chaque câble à sa place (photos), **pâte neuve** si le
   ventirad a été retiré.
6. **Contrôler** : contrôle visuel, premier démarrage, UEFI, tests de ce qui a été touché
   **et** de ce qui fonctionnait avant (procédure 5).
7. **Rendre compte** : pièce retirée et posée (références, numéros de série), tests, résultat ;
   l'ancienne pièce est rendue au client ou recyclée selon son accord.

## 12.2 Cas fréquents

| Remplacement | Points d'attention |
|---|---|
| Barrette de mémoire | même génération, capacité et fréquence ; emplacements du manuel ; mémoire totale dans l'UEFI, test mémoire |
| SSD système | sauvegarde ou clonage avant ; entretoise et vis M.2 ; ordre de démarrage dans l'UEFI |
| Carte graphique | longueur, alimentation et connecteurs ; ancien pilote ; image, pilote, température en charge |
| Ventirad | fixation pour le socket, hauteur ; nettoyage, pâte neuve, serrage en croix ; températures |
| Bloc d'alimentation | format, puissance, connecteurs ; câbles du nouveau bloc uniquement ; tensions et charge (PR02) |

**Procédure professionnelle (à rédiger)** : les sept étapes ci-dessus, adaptées à la pièce.

**Erreur fréquente** : ne tester que la pièce changée, alors qu'un câble voisin a pu être
déplacé ; remonter un ventirad sans renouveler la pâte.

**À l'écrit** : les étapes dans l'ordre, les précautions et les **contrôles** finaux.

**Repère rapide** : panne confirmée → accord → hors tension, ESD → démonter le nécessaire →
remplacer → remonter → **tout retester** → compte rendu.
"""


def _boot_failures() -> str:
    return f"""**Objectifs** : diagnostiquer une panne au premier démarrage, presque toujours due au
montage, et la corriger sans risque.

## 13.1 Par où commencer

{_fig(BOOT_TREE_FIGURE)}

## 13.2 Symptômes et causes de montage

| Symptôme | Causes de montage les plus probables | Vérification, PC débranché |
|---|---|---|
| Rien ne se passe | secteur ou interrupteur du bloc, ATX 24, câble POWER SW mal placé | prise, interrupteur sur I, ATX 24 clipsé, façade d'après le manuel |
| S'allume une fraction de seconde puis s'éteint | EPS absent, entretoise ou vis en court-circuit | EPS 8 broches, entretoises = trous, aucune vis libre |
| Ventilateurs, pas d'image | barrette mal enfoncée, écran sur la carte mère sans partie graphique, câble PCIe manquant | LED de diagnostic, barrettes au clic, écran sur la carte graphique |
| Écran noir long au premier démarrage | entraînement de la mémoire (normal) | patienter plusieurs minutes avant de conclure |
| Mémoire incomplète dans l'UEFI | barrette pas enfoncée, emplacement non recommandé | clips, emplacements du manuel |
| Disque absent | câble données ou alimentation SATA, M.2 non vissé, port SATA partagé avec un M.2 | câbles, vis M.2, manuel (ports partagés) |
| Surchauffe, arrêts en charge | film du ventirad, pâte, serrage, CPU_FAN, flux d'air | démonter le ventirad, nettoyer, pâte neuve |
| Alerte « CPU fan error » | ventilateur branché ailleurs qu'en CPU_FAN | câble sur CPU_FAN |

## 13.3 Règles de sécurité du diagnostic

- **Toute correction se fait PC débranché**, bouton appuyé, bracelet au poignet ; on ne
  rebranche le secteur qu'après la correction.
- **Un seul changement à la fois**, puis on reteste : sinon on ne sait pas ce qui a réglé le
  problème.
- Après un montage, on **soupçonne le montage avant les pièces neuves**. Si tout le montage
  est correct, on passe à la démarche complète de [PR06](/uaa/ampcr-pratique-pr06)
  (configuration minimale, pièce connue fonctionnelle).
- **Odeur de brûlé, fumée, étincelle** : couper le secteur immédiatement, ne pas rallumer ;
  un bloc suspect ne s'ouvre jamais.

**Procédure professionnelle (à rédiger)** : symptôme exact → question de l'arbre → cause de
montage probable → vérification PC débranché → correction → nouveau test → compte rendu.

**Erreur fréquente** : renvoyer une pièce neuve « en panne » alors qu'elle était mal branchée.

**À l'écrit** : le symptôme, la cause retenue **et sa preuve**, la correction et le résultat du
nouveau test.

**Repère rapide** : **montage d'abord** · PC débranché · un changement à la fois · retester.
Exercices liés : {_ex("E10", "E11", "E12", "E13")}.
"""


def _examples() -> str:
    gaps = inventory_gaps(CASE3_EXPECTED, CASE3_DETECTED)
    before_load = CASE4_BEFORE[-1][1]
    after_load = CASE4_AFTER[-1][1]
    return f"""## Cas 1 — Rédiger la procédure complète de montage d'un PC

**Situation.** Un client commande un PC de bureau : carte mère ATX à socket LGA, processeur
compatible (liste de la carte vérifiée), 2 × 16 Go DDR5, SSD M.2 NVMe 2280, disque SATA de
2 To, carte graphique à deux PCIe 8 broches, bloc de 750 W, boîtier ATX avec entretoises
d'usine, ventirad à plaque arrière. Rédige la procédure de montage.

**Résolution.**

1. **Préparer** (procédure 1) : bon de montage comparé aux pièces (références, numéros de
   série) ; compatibilité déjà vérifiée (grille du chapitre 3) ; poste, tapis, **bracelet**.
2. **Lire les notices** : le ventirad a une **plaque arrière** ; elle se pose sous la carte,
   **avant** l'installation dans le boîtier (adaptation de l'ordre).
3. **Carte mère sur son carton** : processeur (triangle sur le repère, posé, levier fermé,
   capot gardé) ; barrettes en **A2 et B2** d'après le manuel, jusqu'au clic ; SSD M.2 dans
   M.2_1, entretoise à 2280, vissé.
4. **Refroidissement** : plaque arrière, noisette de pâte, **film retiré**, ventirad serré en
   croix, câble sur CPU_FAN.
5. **Boîtier** : comparer les entretoises d'usine aux trous de la carte ATX (une sous chaque
   trou), plaque d'E/S si elle n'est pas intégrée ; carte posée et vissée sans forcer.
6. **Bloc** vissé, ventilateur vers le filtre ; **disque SATA** dans sa baie.
7. **Carte graphique** dans le premier PCIe x16, clip, équerre, **deux** câbles PCIe 8 broches.
8. **Câbles** : ATX 24, EPS 8 broches, SATA données et alimentation, façade d'après le manuel,
   USB 3 et audio internes, ventilateurs ; rangement derrière le plateau.
9. **Contrôle visuel** avec la grille, puis **premier démarrage** et tests (procédure 5).

**Conclusion rédigée.** Une procédure en neuf étapes, chacune justifiée ; l'ordre est adapté à
la plaque arrière du ventirad, d'après sa notice.

## Cas 2 — Démonter un PC pour remplacer le ventirad

**Situation.** Un PC de bureau à socket AM4 (PGA) est très bruyant : le ventilateur du
ventirad d'origine frotte. Le client a donné son accord et sa sauvegarde est faite. Rédige le
démontage du ventirad et le remontage d'un modèle compatible.

**Résolution.**

1. **État initial** (photos, numéro de série) ; arrêt, **secteur débranché**, bouton appuyé ;
   bracelet ; photos de l'intérieur.
2. **Débrancher** le câble du ventilateur de **CPU_FAN** (on note l'emplacement).
3. **Ventirad** : dévisser **en croix** ; la pâte est sèche → **tourner doucement** de quelques
   degrés d'un côté à l'autre, puis soulever. **Ne pas tirer d'un coup** : sur AM4, le
   processeur pourrait sortir du socket collé au ventirad.
4. **Nettoyer** le processeur à l'alcool isopropylique, chiffon non pelucheux ; contrôler
   qu'il est toujours en place, levier fermé.
5. **Remonter** le nouveau ventirad : fixation **AM4** vérifiée, hauteur compatible avec le
   boîtier ; noisette de pâte neuve, **film retiré**, serrage en croix, câble sur CPU_FAN.
6. **Contrôler** : démarrage, vitesse du ventilateur et température au repos dans l'UEFI, puis
   en charge ; noter les valeurs.

**Conclusion rédigée.** Ventirad remplacé ; démontage par rotation pour ne pas arracher le
processeur PGA ; pâte neuve ; températures relevées au repos et en charge dans le compte rendu.

## Cas 3 — Corriger un premier démarrage incomplet

**Situation.** Premier démarrage d'un PC monté le matin. Bon de montage :
{CASE3_EXPECTED.memory_modules} barrettes pour {CASE3_EXPECTED.memory_gb} Go, SSD NVMe de 1 To en
M.2_1, disque SATA de 2 To. L'UEFI affiche :

{_console(*CASE3_SCREEN)}

**Résolution.**

1. **Comparer chaque ligne** au bon de montage : processeur conforme ; **mémoire 16 Go au lieu
   de 32** (DIMM_B2 vide) ; **disque SATA absent** ; **CPU_FAN : N/A** — écarts :
   {", ".join(gaps)}.
2. **Couper et débrancher** avant toute correction.
3. **Mémoire** : barrette de DIMM_B2 posée mais pas enfoncée → la renfoncer droite jusqu'au
   clic des deux côtés.
4. **Disque SATA** : câble d'alimentation SATA bien branché, mais câble de **données** non
   branché sur la carte mère → le brancher sur le port SATA 1.
5. **CPU_FAN** : le ventilateur est branché sur SYS_FAN → le déplacer sur **CPU_FAN** (sinon
   la carte ne surveille pas le ventilateur du processeur et peut alerter ou couper).
6. **Redémarrer** : 32 Go, deux disques, CPU_FAN à environ {CASE3_EXPECTED.cpu_fan_rpm} tr/min ;
   puis les tests de la procédure 5.

**Conclusion rédigée.** Trois oublis de montage, aucune pièce défectueuse ; corrigés un par un,
PC débranché, puis vérifiés dans l'UEFI.

## Cas 4 — Surchauffe après un montage

**Situation.** Un PC monté la veille s'arrête après deux minutes de jeu. Fiche du processeur :
**{CASE4_LIMIT} °C** au maximum. Relevés :

{_temps_table(CASE4_BEFORE)}

**Résolution.**

1. **Interpréter** : au repos, {CASE4_BEFORE[0][1]} °C reste sous le seuil d'alerte mais est
   nettement plus chaud qu'attendu pour un PC neuf ; en charge, la limite de {CASE4_LIMIT} °C
   est atteinte ({before_load} °C) : le processeur réduit sa fréquence puis s'arrête pour se
   protéger.
2. **Hypothèse de montage** avant une pièce défectueuse : refroidissement mal monté.
3. **Vérifier**, PC débranché : le ventilateur est bien sur CPU_FAN et tourne ; au démontage du
   ventirad, le **film plastique** de la semelle est toujours en place.
4. **Corriger** : retirer le film, nettoyer la pâte écrasée à l'alcool isopropylique, noisette
   de pâte neuve, serrage en croix.
5. **Retester** en charge pendant 30 minutes :

{_temps_table(CASE4_AFTER)}

**Conclusion rédigée.** « Film de protection laissé sur la semelle du ventirad : surchauffe à
{before_load} °C et arrêt en charge. Film retiré, pâte renouvelée : {after_load} °C après 30 minutes
de charge, sans arrêt. »
"""


def _pitfalls() -> str:
    return """> **Intervenir sur un PC « éteint » mais branché** : le +5 VSB est présent ; toujours
> débrancher le câble secteur et appuyer sur le bouton.

> **Ouvrir un bloc d'alimentation** : jamais — condensateurs chargés à une tension dangereuse.

> **Démonter avant la sauvegarde et l'autorisation**, ou sans relever l'état initial.

> **Forcer un processeur, une barrette ou un connecteur** : ce qui résiste est mal orienté.

> **Oublier le film plastique** sous le ventirad, ou étaler une couche épaisse de pâte.

> **Remonter un ventirad sans renouveler la pâte.**

> **Laisser une entretoise sans trou en face**, ou une vis libre dans le boîtier.

> **Oublier l'EPS 8 broches** ou un câble PCIe de la carte graphique.

> **Brancher la façade au hasard** : le manuel fait foi ; LED polarisées, boutons non.

> **Brancher l'écran sur la carte mère** quand le processeur n'a pas de partie graphique.

> **Couper pendant le long premier démarrage** (entraînement de la mémoire).

> **Arracher un ventirad collé** : sur un socket PGA, le processeur part avec.

> **Tirer sur les fils** au lieu du connecteur, ou sortir la carte graphique sans ouvrir le clip.

> **Mélanger toutes les vis** : une vis 6-32 forcée dans un filetage M3 l'abîme.

> **Conclure « ça marche »** sans comparer l'UEFI au bon de montage ni tester.
"""


def _exercises_intro() -> str:
    return f"""{len(PRACTICE_ITEMS)} exercices corrigés : remises en ordre (préparation, montage,
processeur et ventirad, remplacement d'une carte graphique), repérage d'erreurs (gestes,
entretoises, façade, contrôle visuel), premier démarrage (UEFI, écran noir, températures),
justifications (ordre, ventirad collé, visserie) et procédure écrite. Rédige ta réponse sur
papier **avant** d'ouvrir le corrigé ; toute réponse équivalente et justifiée est acceptée. Ces
mêmes exercices sont proposés dans [S'entraîner](/uaa/{PR03_SLUG}/practice), avec correction
après envoi.

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
    return f"""Le mini-examen se passe dans l'onglet [Examen blanc](/uaa/{PR03_SLUG}/exam) : **10 questions à réponse
libre**, chacune notée sur **2 points**, soit une note sur **{EXAM_TOTAL_POINTS}**. Les
questions ne figurent pas dans ce cours.

| N° | Thème | Type | Points |
|---|---|---|---|
{rows}

**Déroulement.** Chaque question est une situation complète : toutes les informations
nécessaires sont dans l'énoncé et ses documents (relevés, observations fictives).
**Aucune correction n'est visible pendant la passation** ; tes réponses sont enregistrées au
fur et à mesure. Après l'envoi, chaque réponse est corrigée selon le **barème analytique** de la
question (critères et points), puis tu vois ta note sur {EXAM_TOTAL_POINTS}, le corrigé et le
barème.

**Ce que valorise le barème.** L'**ordre** des étapes, les **précautions justifiées** (hors
tension, ESD, ne jamais forcer), l'**erreur repérée avec sa conséquence** et les **contrôles**
après intervention — pas la récitation de sigles. Une autre formulation juste est acceptée.

**Nature de la correction.** Les réponses rédigées reçoivent une **proposition de correction
automatique** (assistée par IA) appuyée sur le barème : c'est un repère d'entraînement, pas une
note officielle ; en cas de doute, compare ta réponse au corrigé.
"""


def _memo() -> str:
    return """## Mémo

- **Avant** : sauvegarde vérifiée (ou refus écrit) → autorisation signée → état initial
  (photos, numéro de série) → arrêt, interrupteur sur 0, **secteur débranché**, bouton appuyé
  → tapis, **bracelet** relié au châssis → photos de l'intérieur.
- **Ordre de montage** : carte équipée sur son carton (processeur, mémoire, M.2, ventirad) →
  entretoises et plaque d'E/S → carte mère → bloc, disques → carte graphique → câbles →
  contrôle visuel → premier démarrage. La notice peut adapter l'ordre.
- **Processeur** : triangle sur repère, **posé, jamais forcé**, capot du socket LGA gardé.
- **Pâte** : petite noisette, **film du ventirad retiré**, serrage en croix, pâte neuve à
  chaque démontage.
- **Mémoire** : emplacements du manuel (souvent A2/B2), encoche, clic des deux côtés.
- **M.2** : entretoise à la bonne longueur, insertion à 30°, vis M2.
- **Entretoises** : une sous chaque trou, aucune ailleurs.
- **Câbles** : ATX 24 + **EPS 8 « CPU »** + PCIe ; façade d'après le **manuel** (LED
  polarisées, boutons non).
- **Contrôle visuel** PC débranché, puis **premier démarrage** : patienter (entraînement de la
  mémoire), **UEFI comparé au bon de montage**, tests mémoire, températures, SMART, ports.
- **Démontage** : ordre inverse, photos, **vis triées**, loquets, clip PCIe ouvert, ventirad
  tourné et non arraché.
- **Panne au premier démarrage** : soupçonner le montage d'abord, PC débranché, un changement
  à la fois, retester.

## Glossaire des termes employés

- **Bracelet antistatique** : bracelet relié au châssis ou au tapis qui évacue l'électricité
  statique du technicien.
- **Capot de protection** : couvercle en plastique qui protège les broches d'un socket LGA.
- **Entretoise** : plot fileté qui maintient la carte mère à distance du fond du boîtier.
- **EPS** : connecteur 8 broches (4+4) d'alimentation du processeur.
- **ESD** : décharge électrostatique.
- **F_PANEL** : connecteur de façade de la carte mère (boutons et LED du boîtier).
- **LGA / PGA** : socket à broches sur la carte (LGA) ou sous le processeur (PGA).
- **Pâte thermique** : produit qui comble les micro-vides entre processeur et ventirad.
- **Plaque d'E/S** : cache arrière des ports de la carte mère.
- **POST** : autotest du firmware à la mise sous tension.
- **SMART** : autosurveillance des disques (attributs d'usure et d'erreurs).
- **UEFI** : firmware actuel de la carte mère, qui succède au BIOS.
- **Ventirad** : radiateur et ventilateur du processeur.
- **XMP / EXPO** : profils de mémoire qui la font fonctionner à la vitesse annoncée.
"""


def _sources() -> str:
    return """## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), pp. 3 et 5 : épreuve uniquement écrite, exigence AP-14
  « Montage, démontage et reconditionnement d'un PC ». Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
  Programme officiel n° 345/2007/249 (option AMPCR).
- **Connecteur de façade** : Intel, *Front Panel I/O Connectivity Design Guide* (brochage
  2 × 5 du connecteur de façade, broche 10 en détrompeur) ; les manuels des cartes mères
  précisent le brochage de chaque modèle.
- **Montage** : notices d'installation des fabricants de processeurs (Intel, AMD : sockets
  LGA1700, LGA1851, AM4, AM5), de cartes mères, de ventirads et de boîtiers ; spécification
  **ATX** (emplacements de fixation, plaque d'E/S) ; spécification PCI-SIG **M.2**
  (longueurs, fixation).
- **Tests** : documentation de MemTest86 et du Diagnostic de mémoire Windows ; attributs
  **SMART** (smartmontools).

Les procédures, le brochage de façade, le plan des entretoises, la visserie, la grille de
contrôle et les relevés du cours sont **produits par programme** depuis des données
**vérifiées par des tests automatiques** ; aucun schéma n'est tiré d'une image générée.

## Compléments pédagogiques (non imposés par la liste officielle)

La liste des pp. 5-6 demande le montage, le démontage et le reconditionnement d'un PC
(AP-14). Sont des **compléments**, signalés comme tels :

- la sécurité électrique et la protection ESD (AP-C02, déjà vues en PR02, reprises en PR28) ;
- la fiche d'intervention, la sauvegarde et l'autorisation (approfondies en PR04 et PR28) ;
- les tests après montage (mémoire, températures, SMART), utiles au compte rendu.

## Supports fictifs

Les bons de montage, fiches, relevés, écrans et situations de ce cours sont **fictifs** et
reconstitués pour l'entraînement ; ils ne décrivent aucun produit réel. Aucun n'est une question
officielle ou déjà posée par le Jury.
"""


def pr03_course_sections() -> list[tuple[str, str]]:
    """Blocs du cours (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("PR03 — Objectifs et place dans l'épreuve", _objectives()),
        ("PR03 — 1. Préparer le poste : outillage, ESD, inventaire et photos", _prepare()),
        ("PR03 — 2. Avant d'ouvrir : sauvegarde, autorisation et état initial", _authorization()),
        ("PR03 — 3. Vérifier la compatibilité avant le montage", _compatibility()),
        ("PR03 — 4. Ordre de montage : vue d'ensemble et justification", _order()),
        ("PR03 — 5. Carte mère hors boîtier : processeur, pâte thermique, ventirad, barrettes et M.2", _board_outside()),
        ("PR03 — 6. Boîtier : entretoises, carte mère, bloc, disques et carte graphique", _case()),
        ("PR03 — 7. Câblage : alimentation, connecteurs de façade, USB, audio et ventilateurs", _cabling()),
        ("PR03 — 8. Contrôle visuel avant la mise sous tension", _visual_check()),
        ("PR03 — 9. Premier démarrage : POST, UEFI et tests de la RAM, des températures et des disques", _first_boot()),
        ("PR03 — 10. Gestion des câbles et flux d'air", _airflow()),
        ("PR03 — 11. Démontage documenté : ordre inverse, visserie et pièces fragiles", _disassembly()),
        ("PR03 — 12. Remplacer un composant et remonter", _replacement()),
        ("PR03 — 13. Pannes au premier démarrage", _boot_failures()),
        ("PR03 — Exemples : quatre cas intégralement résolus", _examples()),
        ("PR03 — Pièges et erreurs fréquentes", _pitfalls()),
        (f"PR03 — Exercices corrigés ({len(PRACTICE_ITEMS)}) et leurs corrigés", _exercises_intro()),
        ("PR03 — Mini-examen noté sur 20 : mode d'emploi", _mini_exam()),
        ("PR03 — Fiche mémo et glossaire", _memo()),
        ("PR03 — Sources et compléments pédagogiques", _sources()),
    ]
