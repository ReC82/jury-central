"""Cours PR15 « Câblage RJ45 T568A/B — fabrication, schémas et tests » — parcours AMPCR
pratique écrite (ticket #197).

Matière : intégralement celle du ticket #197 (1. supports et connecteurs, 2. brochage et
couleurs, 3. câble droit/croisé et normes, 4. fabrication et procédure de terrain, 5. tests et
dépannage, 6. contexte professionnel et sécurité), découpée en blocs titrés (le titre pilote le
type de carte, `app.card_kind` : aucun titre de bloc théorique ne contient « examen »,
« source », « exemple », « exercice » ni « méthode »). Schémas : `app.v1.ampcr_pratique_pr15_figures`
(brochages construits depuis les données T568A/T568B testées) ; exercices et mini-examen :
`app.v1.ampcr_pratique_pr15_bank`. Mise en forme partagée avec PR06/PR11.
"""

from app.v1.ampcr_pratique_pr06_course import _exercise_card, _fig, _req
from app.v1.ampcr_pratique_pr15_bank import (
    EXAM_ITEMS,
    EXAM_TOTAL_POINTS,
    PRACTICE_ITEMS,
    T568A_TEXT,
    T568B_TEXT,
)
from app.v1.ampcr_pratique_pr15_figures import (
    ANATOMY_FIGURE,
    CATEGORIES,
    CHAIN_FIGURE,
    CHANNEL_MAX_M,
    COMPARISON_FIGURE,
    CORDS_MAX_M,
    CRIMP_FIGURE,
    CROSSOVER_FIGURE,
    CROSSOVER_LINKS,
    ETHERNET_PIN_USE,
    EXAMPLE3_END_B,
    EXAMPLE3_FIGURE,
    PERMANENT_LINK_MAX_M,
    PLUG_ORIENTATION,
    SEQUENTIAL_WRONG_FIGURE,
    STRAIGHT_FIGURE,
    T568A_FIGURE,
    T568B_FIGURE,
    TESTER_FIGURES,
    wire_label,
)
from app.v1.ampcr_pratique_visuals import T568A, T568B

PR15_TITLE = "Câblage RJ45 T568A/B — fabrication, schémas et tests"
PR15_SLUG = "ampcr-pratique-pr15"


def _exercises_html() -> str:
    return "\n\n".join(
        _exercise_card(i, item, anchor_prefix="pr15") for i, item in enumerate(PRACTICE_ITEMS, start=1)
    )


def _figure_row(*figures) -> str:
    inner = "".join(_fig(f).strip() for f in figures)
    return f'\n\n<div class="jc-tech-figure-row">{inner}</div>\n\n'


# =============================================================================================
# Sections du cours (titre du bloc, Markdown / HTML)
# =============================================================================================


def _objectives() -> str:
    return f"""## Ce que tu sauras faire, par écrit

L'épreuve pratique AMPCR se passe **uniquement par écrit** (consignes officielles 2026-2027/1,
p. 3) : tu ne sertiras pas de câble devant le jury, mais tu dois savoir **décrire, interpréter
et justifier** la réalisation et le contrôle d'un câble RJ45. À partir d'un besoin, d'un câble,
d'un dessin de connecteur ou d'un rapport de testeur, tu sais :

1. **choisir** le câble, la catégorie et les connecteurs adaptés ;
2. **identifier** les 8 conducteurs, les 4 paires et leurs positions dans la fiche ;
3. **appliquer** T568A ou T568B, pour un câble droit ou croisé ;
4. **décrire** la fabrication d'un cordon et le raccordement d'une prise, étape par étape ;
5. **lire** le résultat d'un testeur et **proposer** la correction appropriée ;
6. **rédiger** le compte rendu de l'intervention.

## Exigences officielles travaillées dans ce cours

{_req("AP-34")}
{_req("AP-18")}
{_req("AP-20")}

AP-34 est le cœur du cours (réalisation et code des couleurs). AP-18 et AP-20 sont travaillées
**pour le câble à paires torsadées et le connecteur RJ45** ; le coaxial, la fibre, les débits
et les distances dans leur ensemble sont l'objet des cours PR13, PR14, PR16 et PR17 du
parcours. Le câble croisé touche aussi AP-28 (connexion directe de deux machines) et la chaîne
de câblage AP-36 (installation physique), approfondies en PR21 et PR18.

Complément pédagogique (hors liste officielle des pp. 5-6, signalé comme tel) :

{_req("AP-C01")}

## Prérequis : la théorie déjà publiée

Le parcours « Théorie » (séparé de ce parcours) contient une introduction :
[MC15 Câblage Ethernet et RJ45 : T568A/T568B](/uaa/ampcr-mc15). Ce cours-ci va plus loin :
schémas orientés, paires, fabrication, tests, dépannage et réponses écrites.

## Comment travailler ce cours

Apprends le brochage (2) avec ses schémas jusqu'à pouvoir le **réécrire sans regarder**, puis
lis les sections dans l'ordre. Étudie les **quatre exemples corrigés**, fais les
**{len(PRACTICE_ITEMS)} exercices corrigés** (ici ou dans « S'entraîner », correction après
envoi), puis passe le **mini-examen noté sur {EXAM_TOTAL_POINTS}** dans l'onglet « Examen blanc ».

> **Important —** les situations, relevés et affichages de testeur de ce cours sont des
> **supports fictifs** construits pour s'entraîner. Les brochages, eux, sont ceux des normes
> TIA/EIA-568 et sont vérifiés automatiquement. Aucun exercice n'est une question officielle
> ni une question déjà posée par le Jury.
"""


def _media() -> str:
    return """## 1.1 Quatre paires torsadées, huit conducteurs

Un câble Ethernet cuivre contient **4 paires torsadées**, soit **8 conducteurs**. Chaque
paire réunit un fil de couleur pleine et un fil blanc rayé de la même couleur : **orange**,
**vert**, **bleu**, **marron**.

**Rôle de la torsade.** Dans une paire, les deux fils transportent le même signal en
opposition (transmission différentielle). En les torsadant, les parasites extérieurs agissent
de la même façon sur les deux fils et s'annulent à la réception, et la paire rayonne moins vers
ses voisines. Chaque paire a un pas de torsade différent pour limiter la **diaphonie**
(signal d'une paire qui « fuit » sur une autre).

**Conséquence du détorsadage excessif.** Si on détorsade les paires sur plusieurs
centimètres au raccordement, on supprime cette protection à cet endroit : la diaphonie
augmente, le lien peut échouer aux tests de performance, faire des erreurs ou ne pas tenir le
débit prévu. Règle : détorsader **le moins possible**, environ **13 mm au plus** (½ pouce,
TIA-568) pour la Cat5e et la Cat6.

## 1.2 Blindage : U/UTP, F/UTP, U/FTP, S/FTP

Les noms historiques **UTP**, **FTP** et **STP** sont ambigus (« FTP » et « STP » désignent
selon les fabricants des câbles différents). La **notation normalisée** (ISO/IEC 11801) est
plus précise : **X/YTP**, où X = protection **globale** du câble et Y = protection **de chaque
paire**, avec U = aucune, F = écran en feuille (*foil*), S = tresse (*shield*).

- **U/UTP** (l'« UTP » historique) : aucun écran, ni global ni par paire. Bureau,
  environnement peu perturbé.
- **F/UTP** (souvent appelé « FTP ») : un écran en feuille autour des 4 paires, paires non
  écrantées. Environnement modérément perturbé.
- **U/FTP** : pas d'écran global, un écran en feuille autour de **chaque** paire. Courant en
  Cat6A : réduit aussi la diaphonie entre paires.
- **S/FTP** (souvent appelé « STP » ou « PiMF ») : une tresse globale **et** un écran par paire.
  Atelier, industrie, forte perturbation.

**Blindage efficace = continuité de bout en bout.** Un câble écranté ou blindé n'est utile
que si **toute la chaîne** l'est : fiches, keystones, panneau de brassage blindés, écran
raccordé à chaque connecteur, et **mise à la terre** selon les règles de l'installation (en
général par la baie). Un connecteur non blindé ou un écran interrompu fait perdre l'intérêt du
blindage.

## 1.3 Catégories : Cat5e, Cat6, Cat6A

La **catégorie** fixe la **fréquence** jusqu'à laquelle le câble garde ses performances (en
MHz). Le **débit** (en Gb/s) dépend de cette fréquence, de la technique de transmission et de la
**longueur**. Fréquence et débit ne sont pas la même chose.

{categories}

**Compatibilité.** Toute la chaîne (câble, prises, panneau, cordons, fiches) doit être **au
moins de la catégorie visée** : un seul élément d'une catégorie inférieure limite l'ensemble.
Les connecteurs doivent correspondre à la catégorie **et** au diamètre des conducteurs (le
câble Cat6A est plus épais).

## 1.4 Connecteur 8P8C, prises, keystones et panneaux

- La fiche **8P8C** (8 positions, 8 contacts) est **communément appelée RJ45**. On parle de
  **fiche** (mâle, au bout d'un cordon) et de **prise** (femelle, murale ou sur un équipement).
- Le **keystone** est un module de prise femelle qu'on clipse dans un boîtier mural ou un
  panneau ; le câble y est raccordé par **poinçonnage** (contacts autodénudants).
- Le **panneau de brassage**, dans la baie, reçoit l'arrivée des câbles permanents ; on relie
  ses ports aux équipements actifs (switch) par des **cordons de brassage**.
- Le **cordon** est un câble court muni de deux fiches (cordon de brassage dans la baie, cordon
  de poste entre la prise murale et l'appareil).

**Câble rigide ou souple.** Le **monobrin** (conducteur rigide, *solid*) sert à l'installation
fixe : il est poinçonné sur keystones et panneaux. Le **multibrin** (conducteur souple,
*stranded*) sert aux cordons, qu'on manipule souvent. Les fiches à sertir existent **pour
monobrin** ou **pour multibrin** : leurs contacts sont différents ; une fiche inadaptée donne
un mauvais contact.

## 1.5 Précautions de pose

- **Rayon de courbure** : au moins 4 fois le diamètre pour un câble U/UTP posé, 8 fois pour un
  câble blindé (TIA-568) ; jamais de pli.
- **Écrasement** : pas de collier serré à bloc, pas de câble sous un pied de bureau ou une porte.
- **Traction** : tirer sans dépasser la limite du fabricant (environ 110 N pour un câble
  4 paires) ; une traction excessive détord les paires et change les caractéristiques.
- **Humidité** : câble adapté (gaine extérieure) si nécessaire ; pas de prise dans une zone
  humide sans protection.
- **Perturbations (EMI) et secteur** : éloigner le câble des câbles d'alimentation, moteurs,
  ballasts d'éclairage ; les croiser à **angle droit** ; respecter les distances de séparation
  des normes d'installation (EN 50174-2, TIA-569) ; utiliser un câble blindé si nécessaire.
- **Cheminement** : chemins de câbles ou goulottes, étiquetage aux deux bouts.
- **Cohérence** : même catégorie et même type de blindage sur toute la chaîne.
""".replace("{categories}", _categories_table())


def _categories_table() -> str:
    rows = "\n".join(f"- **{name}** ({mhz} MHz) : {use}. {note}." for name, mhz, use, note in CATEGORIES)
    return (
        rows + "\n\n"
        f"Longueur maximale d'un **canal** Ethernet cuivre : **{CHANNEL_MAX_M} m** (dont "
        f"**{PERMANENT_LINK_MAX_M} m** de lien permanent au plus et environ **{CORDS_MAX_M} m** de "
        "cordons au total). **Ne donne jamais « 10 Gb/s sur 100 m » pour la Cat6** : la longueur "
        "possible dépend de l'environnement (diaphonie entre câbles voisins)."
    )


def _pinout() -> str:
    return f"""## 2.1 Orientation de lecture : à fixer avant tout

Un brochage n'a de sens qu'avec une orientation. Dans tout ce cours :

> **{PLUG_ORIENTATION}**

Si tu tiens la fiche **languette vers toi** (contacts dessous), la broche 1 passe **à droite** :
l'ordre est inversé. C'est l'erreur de débutant la plus fréquente (exercice E06).

## 2.2 T568B et T568A, broche par broche

| Broche | **T568B** | **T568A** |
|---|---|---|
{_pin_rows()}

{_figure_row(T568B_FIGURE, T568A_FIGURE)}

En une ligne :

- **T568B** : {T568B_TEXT}.
- **T568A** : {T568A_TEXT}.

## 2.3 Ce qui change entre A et B

**A et B échangent la paire orange et la paire verte** (broches 1, 2, 3 et 6). Les paires
**bleue (4-5)** et **marron (7-8)** restent **identiques**.

{_fig(COMPARISON_FIGURE)}

**Mémoriser.** Retiens d'abord T568B (le plus fréquent sur les cordons du commerce) ; pour
T568A, échange simplement orange et vert. Sur le terrain, **c'est l'installation existante qui
décide** de la norme. Le fil blanc est sur la broche impaire de chaque paire, **sauf la paire bleue**
(bleu en 4, blanc/bleu en 5).

## 2.4 Paires et positions : 1-2, 3-6, 4-5, 7-8

Les 8 broches forment **4 positions de paire** : **1-2**, **3-6**, **4-5** et **7-8**. La
position **3-6 « enjambe »** la position 4-5 : c'est voulu (compatibilité avec la téléphonie
historique, dont la paire centrale est 4-5).

| Position | Paire en T568B | Paire en T568A | Paire selon la numérotation TIA |
|---|---|---|---|
| 1-2 | orange | verte | paire 2 (orange) en B, paire 3 (verte) en A |
| 3-6 | verte | orange | paire 3 en B, paire 2 en A |
| 4-5 | bleue | bleue | paire 1 |
| 7-8 | marron | marron | paire 4 |

Chaque position doit recevoir **les deux fils d'une même paire torsadée** : c'est sur cette
paire que circule un signal différentiel.

## 2.5 Pourquoi « 1 à 8 continu » peut être électriquement faux : la paire séparée

Si on range les fils **paire par paire** (1-2, 3-4, 5-6, 7-8), la position 3-6 reçoit le
blanc/vert et le bleu, la position 4-5 le vert et le blanc/bleu. Si les deux bouts sont faits
de la même façon, un testeur de continuité affiche **1→1 … 8→8 réussi** : chaque fil arrive
bien en face. Pourtant le signal de la position 3-6 voyage sur **deux fils qui ne sont pas
torsadés ensemble** : diaphonie forte, erreurs, débit réduit, lien gigabit impossible. C'est
une **paire séparée** (*split pair*).

{_fig(SEQUENTIAL_WRONG_FIGURE)}
"""


def _pin_rows() -> str:
    return "\n".join(
        f"| {i} | {wire_label(b)} | {wire_label(a)} |" for i, (a, b) in enumerate(zip(T568A, T568B, strict=True), start=1)
    )


def _straight_crossover() -> str:
    pin_use = "\n".join(f"| {pin} | {fast} | {giga} |" for pin, fast, giga in ETHERNET_PIN_USE)
    links = ", ".join(f"{a}→{b}" for a, b in CROSSOVER_LINKS)
    return f"""## 3.1 Câble droit et câble croisé

- **Câble droit** : la **même norme aux deux bouts** (B-B, ou A-A). Chaque broche arrive sur
  la même broche (1→1 … 8→8).
- **Câble croisé** (historique) : **T568A à un bout, T568B à l'autre**. Liaisons : {links}.
  Il échange les positions 1-2 et 3-6.

{_figure_row(STRAIGHT_FIGURE, CROSSOVER_FIGURE)}

## 3.2 À quoi servent les broches selon le débit

| Broche | 10BASE-T / 100BASE-TX (carte réseau, MDI) | 1000BASE-T |
|---|---|---|
{pin_use}

- **10 et 100 Mb/s** (10BASE-T, 100BASE-TX) utilisent **deux paires** : 1-2 pour émettre, 3-6
  pour recevoir côté carte réseau ; un switch ou un hub (**MDI-X**) fait l'inverse. Les paires
  4-5 et 7-8 ne servent pas.
- **1 Gb/s** (1000BASE-T) utilise **les quatre paires**, et **chaque paire transmet dans les
  deux sens en même temps** (paires BI_DA à BI_DD).
- **Ne dis jamais qu'un seul jeu de paires transporte tous les débits.** Conséquence pratique :
  un défaut sur 4-5 ou 7-8 laisse passer le 100 Mb/s mais empêche le 1 Gb/s (exemple 4).

## 3.3 Cas historiques et Auto MDI-X

Sans détection automatique, il fallait relier une émission à une réception :

| Liaison | Câble historique | Pourquoi |
|---|---|---|
| PC ↔ switch (ou hub) | **droit** | types différents : MDI ↔ MDI-X |
| switch ↔ switch | **croisé** (ou port « uplink ») | même type : MDI-X ↔ MDI-X |
| PC ↔ PC | **croisé** | même type : MDI ↔ MDI |
| PC ↔ routeur | **croisé** | le port d'un routeur est de type MDI, comme un PC |

**Auto MDI-X.** La plupart des équipements récents détectent si le câble est droit ou croisé et
**inversent eux-mêmes** émission et réception : les deux câbles fonctionnent. Il suffit
généralement qu'**un seul des deux équipements** le fasse. Limites et conditions :

- les équipements anciens (beaucoup de cartes et switches 10/100) **n'en ont pas** ;
- la détection est liée à l'**auto-négociation** : sur certains équipements, forcer la vitesse
  et le duplex la désactive ;
- elle ne répare pas un câble **défectueux** (ouvert, paire séparée…) ;
- un câble croisé étiqueté « droit » fonctionne avec un équipement récent… et tombe en panne
  avec un ancien : on étiquette et on documente correctement.

## 3.4 Physique, négociation, configuration IP : trois niveaux distincts

1. **Raccordement physique** : câble conforme, connecteurs, port. Preuve : **voyant de lien**.
2. **Négociation du lien** : vitesse (10/100/1000 Mb/s) et duplex choisis par les deux
   équipements. Preuve : vitesse affichée par la carte ou le switch.
3. **Configuration IP** : adresse, masque, passerelle, DNS. Preuve : `ipconfig` / `ip addr`,
   `ping`. Un câble parfait ne corrige pas une mauvaise adresse IP, et une bonne adresse IP ne
   compense pas un câble défectueux : on teste **dans cet ordre**.
"""


def _fabrication() -> str:
    return f"""## 4.1 Choisir le matériel

- **Câble** de la catégorie voulue, **multibrin** pour un cordon, **monobrin** pour
  l'installation fixe ; blindé si l'environnement l'exige.
- **Fiches** de la **même catégorie**, adaptées au **type de conducteur** (monobrin ou
  multibrin) et au **diamètre** du câble ; fiches blindées pour un câble blindé.
- **Manchons** (protège-fiches), à enfiler **avant** de sertir.

## 4.2 Les outils

| Outil | Rôle |
|---|---|
| **Coupe-câble** | coupe franche du câble et recoupe des fils |
| **Dénudeur** | retire la gaine extérieure **sans entailler** les conducteurs |
| **Pince à sertir** (RJ45) | enfonce les 8 contacts de la fiche dans les conducteurs et écrase la patte de maintien sur la gaine |
| **Outil de poinçonnage** (insertion, type 110 ou LSA) | raccorde chaque fil d'un keystone ou d'un panneau et coupe l'excédent |
| **Testeur de continuité / wiremap** | vérifie le chemin de chaque fil (ouvert, court-circuit, inversion, croisement) |
| **Testeur de qualification** | dit si le lien supporte un débit donné (ex. 1 Gb/s), détecte les paires séparées |
| **Testeur de certification** | mesure les paramètres (longueur, perte d'insertion, diaphonies…) et les compare aux limites d'une catégorie ; produit un rapport par lien |

## 4.3 Fabriquer un cordon : procédure

{_fig(CRIMP_FIGURE)}

Points de détail :

1. **Coupe propre** et dénudage de 25 à 30 mm, en tournant le dénudeur une seule fois ; un fil
   entaillé casse plus tard (panne intermittente).
2. Retirer le **fil de déchirement** et, pour la Cat6, le **séparateur** (croisillon) au ras de
   la gaine.
3. **Détorsader le minimum**, ranger les fils dans l'ordre choisi en gardant les torsades **au
   plus près de la fiche**, aplatir.
4. **Recouper droit** à environ 12-13 mm : tous les fils à la même longueur, et la **gaine doit
   entrer dans la fiche** pour être pincée par la patte de maintien.
5. **Insérer** (contacts vers soi, broche 1 à gauche) jusqu'à ce que les 8 fils touchent le
   **fond** de la fiche ; on le voit en bout de fiche.
6. **Contrôler** avant de sertir : ordre des couleurs, fils en butée, gaine sous la patte.
7. **Sertir** à fond avec une pince adaptée à la fiche. On ne dénude **jamais** les fils un par
   un : les contacts percent l'isolant.
8. **Autre bout** : même norme pour un câble droit, l'autre norme pour un croisé.
9. **Contrôle visuel et mécanique** (léger effort de traction sur la gaine), puis **test au
   testeur avant toute mise en service**.

{_fig(ANATOMY_FIGURE)}

## 4.4 Sertir une fiche, raccorder une prise, terminer un câble permanent

- **Sertir une fiche** : sur un **cordon multibrin** (ou une fiche pour monobrin dans un cas
  particulier). Les contacts de la fiche sont enfoncés par la pince.
- **Raccorder une prise / un keystone** : sur un **câble monobrin** d'installation, par
  **poinçonnage** de chaque fil dans la fente indiquée par le repère couleur **A ou B** imprimé
  sur le keystone. On garde les torsades jusqu'aux fentes, on coupe l'excédent, on maintient la
  gaine.
- **Terminer un câble permanent** : raccorder ses **deux** extrémités (panneau de brassage et
  prise murale) selon **la même norme**, puis **tester le lien permanent** (panneau → prise) et
  **étiqueter** les deux bouts. On ne sertit pas de fiche sur un câble permanent : on y branche
  des cordons.
"""


def _tests() -> str:
    good, opened, reversed_, split = TESTER_FIGURES
    return f"""## 5.1 Lire un wiremap

Un **testeur de câble** se compose d'un boîtier principal et d'un **bouchon distant** branché à
l'autre bout. Il envoie un signal sur chaque broche et indique où il arrive (le *wiremap*,
« carte des fils »). Les défauts à reconnaître :

| Défaut | Ce qu'affiche le testeur | Cause typique |
|---|---|---|
| **Conforme** (droit) | 1→1, 2→2 … 8→8 | — |
| **Circuit ouvert** (*open*) | une broche sans liaison | fil coupé, pas en butée, contact pas enfoncé |
| **Court-circuit** (*short*) | deux broches reliées entre elles | contacts écrasés, fils dénudés qui se touchent |
| **Fils inversés / paire inversée** (*reversed pair*) | 1→2 et 2→1 (dans une même paire) | deux fils d'une paire permutés à un bout |
| **Paires croisées** (*crossed pairs*) | 1→3, 2→6, 3→1, 6→2 | une extrémité en A, l'autre en B (câble croisé là où on voulait un droit) |
| **Paire séparée** (*split pair*) | continuité 1→1 … 8→8 **correcte** | fils rangés paire par paire ; seul un testeur qui mesure la diaphonie le voit |
| **Défaut intermittent / mauvais contact** | résultat qui change quand on bouge le câble ou la fiche | fil entaillé, fiche mal sertie, gaine non maintenue |

Quatre affichages types :

{_figure_row(good, opened)}

{_figure_row(reversed_, split)}

**Un défaut de wiremap ne dit pas quelle extrémité est fausse** : on regarde les deux fiches à
travers le corps transparent et on compare à la norme. Certains testeurs donnent la **distance
jusqu'au défaut**, ce qui aide pour un câble permanent.

## 5.2 Ce qu'un testeur de continuité ne garantit pas

Un testeur de continuité simple (à LED) vérifie seulement le **chemin des fils**. Il ne
garantit **ni la catégorie, ni le débit, ni l'absence de diaphonie** : il ne voit pas les
paires séparées, ne mesure ni la longueur ni l'atténuation. Pour la **performance** :

- **qualification** : le lien supporte-t-il tel débit (100 Mb/s, 1 Gb/s, 10 Gb/s) ?
- **certification** : chaque paramètre respecte-t-il les limites de la catégorie (Cat5e, Cat6,
  Cat6A) ? C'est la preuve à remettre à un client après une installation.

## 5.3 Notions de mesure (niveau technicien)

- **Atténuation** (perte d'insertion) : le signal s'affaiblit avec la **longueur** et avec la
  **fréquence**. Trop de longueur → signal trop faible à l'arrivée.
- **Diaphonie** : signal d'une paire qui se retrouve sur une autre. La **NEXT** (*near-end
  crosstalk*, diaphonie proche) se mesure à l'extrémité où le signal est injecté ; elle
  augmente si on **détorsade** au raccordement.
- **Blindage** : réduit les parasites extérieurs et, par paire (U/FTP, S/FTP), la diaphonie.
- **Rapport signal/bruit** : le récepteur doit distinguer le signal (affaibli par la longueur)
  du bruit (diaphonie, parasites). Long câble + diaphonie + parasites = erreurs.

Longueurs : **canal {CHANNEL_MAX_M} m** typiquement ({PERMANENT_LINK_MAX_M} m de lien permanent
+ cordons). **Cat5e : 1 Gb/s sur 100 m. Cat6A : 10 Gb/s sur 100 m. Cat6 : 10 Gb/s seulement
sur une longueur réduite (environ 37 à 55 m), selon l'environnement** — jamais « 100 m » sans
nuance.

## 5.4 Diagnostiquer un problème de liaison

**Lien absent** (voyant éteint)
- *Câblage* : circuit ouvert ou court-circuit sur 1-2 ou 3-6, fiche mal sertie, câble croisé
  sans Auto MDI-X, prise non raccordée.
- *Hors câble* : port du switch désactivé ou en panne, carte réseau désactivée, pilote.
- *Premiers tests* : testeur de câble ; cordon connu bon ; autre port ; état de la carte.

**Lien à 100 Mb/s au lieu de 1 Gb/s**
- *Câblage* : paire 4-5 ou 7-8 ouverte ou mal sertie, câble Cat5 (sans « e ») ou à 2 paires.
- *Hors câble* : vitesse forcée sur la carte ou le port, équipement 100 Mb/s, pilote.
- *Premiers tests* : testeur (paires 4-5, 7-8) ; cordon connu bon ; réglages de vitesse.

**Instabilité, erreurs, coupures**
- *Câblage* : paire séparée, détorsadage, fil entaillé, longueur > 100 m, câble près d'une
  source de parasites (environnement EMI), connecteur non adapté (monobrin/multibrin).
- *Hors câble* : port ou carte défaillant, économie d'énergie de la carte.
- *Premiers tests* : testeur de qualification ; compteurs d'erreurs du switch ; parcours du
  câble.

**Erreur de brochage**
- *Câblage* : une fiche en A, l'autre en B ; fils inversés ; ordre faux.
- *Premiers tests* : wiremap ; lecture des deux fiches à travers le corps transparent.

Ordre de travail : **observer** (voyants, vitesse, message), **tester le câble** (cordon puis
lien permanent), **échanger** avec un élément connu bon (un seul changement à la fois),
**vérifier le port et la carte**, puis seulement la **configuration IP**.
"""


def _professional() -> str:
    return f"""## 6.1 De la baie au poste

{_fig(CHAIN_FIGURE)}

- **Liaison PC-switch typique** : switch → cordon de brassage → **panneau de brassage** →
  **câble permanent** (dans les murs ou les chemins de câbles) → **prise murale** → cordon de
  poste → PC.
- **Lien permanent** (panneau → prise, {PERMANENT_LINK_MAX_M} m au plus) : câble monobrin
  poinçonné aux deux bouts, testé et **étiqueté** (même repère sur la prise et sur le port du
  panneau, tableau de brassage à jour).
- **Canal** (switch → PC, {CHANNEL_MAX_M} m au plus) : lien permanent + cordons.

**Cordon préfabriqué ou fabriqué ?** En entreprise, on utilise de préférence des **cordons
préfabriqués** testés en usine (qualité constante, catégorie garantie) ; on fabrique un cordon
pour une longueur particulière, un dépannage ou une formation, **et on le teste**. Le câble
permanent, lui, n'est jamais remplacé par une longue rallonge de cordons.

**Sécurité.** Câble et outils coupants : gestes maîtrisés, chutes de fils ramassées. Ne pas
travailler dans une baie sans y être autorisé ; ne pas débrancher un port sans savoir ce qu'il
dessert (serveur, téléphone). Une prise réseau ne se raccorde jamais au secteur et ne se pose
pas à côté d'une prise électrique sans respecter la séparation des câbles.

## 6.2 Le rapport d'intervention

| Rubrique | Contenu attendu |
|---|---|
| **Besoin** | ce qui était demandé ou constaté (poste sans réseau, nouveau bureau…) |
| **Norme choisie** | T568A ou T568B, câble droit ou croisé, et pourquoi (installation existante) |
| **Schéma** | ordre des 8 fils ou schéma de liaison, repères des prises et ports |
| **Outils et matériel** | câble (catégorie, type), fiches/keystones, pince, outil de poinçonnage, testeur |
| **Tests avant** | ce qui a été mesuré avant l'intervention (wiremap, défaut constaté) |
| **Résultats et défauts corrigés** | cause retenue, ce qui a été refait |
| **Tests après** | wiremap conforme, longueur, qualification ou certification si nécessaire, lien et vitesse sur le poste |
| **Validation** | confirmation avec l'utilisateur, étiquetage, clôture |

**Ce qu'on attend d'une réponse écrite à l'épreuve** : des **étapes ordonnées**, l'**ordre
des couleurs** quand il est demandé (broche par broche), la **justification** de chaque choix
(norme, catégorie, câble droit ou croisé) et le **test** qui prouve le résultat.
"""


def _examples() -> str:
    end_b = ", ".join(f"{i} {wire_label(w)}" for i, w in enumerate(EXAMPLE3_END_B, start=1))
    return f"""Chaque exemple suit la même démarche : besoin, choix justifiés, réalisation ou
lecture des preuves, test et compte rendu. Supports fictifs, brochages vérifiés.

<h3 class="jc-example-title">Exemple 1 — Fabriquer un câble droit B-B</h3>

**Besoin.** Un cordon de 3 m pour relier un PC à la prise murale d'un bureau dont
l'installation est en T568B. Câble Cat6 U/UTP multibrin.

**Choix.** Cordon **droit** (PC ↔ switch via la prise : équipements de types différents), en
**T568B aux deux bouts** comme l'installation ; fiches Cat6 **pour multibrin**.

**Réalisation.**

1. Couper 3 m, enfiler les deux manchons.
2. Dénuder 25 à 30 mm sans entailler, retirer le fil de déchirement et le séparateur.
3. Ranger en T568B : {T568B_TEXT} ; aplatir.
4. Recouper droit à environ 12-13 mm.
5. Fiche contacts vers soi, broche 1 à gauche : pousser jusqu'en butée ; contrôler l'ordre et
   la gaine sous la patte ; sertir.
6. Même chose à l'autre bout, **aussi en T568B**.

**Test.** Testeur de câble : **1→1 … 8→8 réussi**. Branchement : voyant de lien, 1 Gb/s.

**Compte rendu.** « Cordon droit T568B/T568B, 3 m, Cat6 multibrin, testé conforme (wiremap) ;
poste connecté à 1 Gb/s. »

<h3 class="jc-example-title">Exemple 2 — Fabriquer un câble croisé A-B</h3>

**Besoin.** Relier directement deux anciens PC (cartes 100 Mb/s **sans Auto MDI-X**) pour
transférer des fichiers.

**Choix.** Deux équipements de même type sans détection automatique : **câble croisé**,
**T568A à un bout, T568B à l'autre**.

**Réalisation.** Bout 1 en T568A : {T568A_TEXT}. Bout 2 en T568B : {T568B_TEXT}. Même
procédure de sertissage qu'à l'exemple 1.

**Test.** Le testeur doit afficher **1→3, 2→6, 3→1, 6→2**, et 4, 5, 7, 8 droites : pour un
câble croisé, c'est le résultat **attendu** (beaucoup de testeurs l'annoncent « croisé »).
Branchement : voyants allumés à 100 Mb/s. Puis configuration IP des deux PC dans le même
réseau (ex. 192.168.10.1 et 192.168.10.2 /24) et `ping` réussi.

**Compte rendu.** « Câble croisé A/B fabriqué et testé (1→3, 2→6, 3→1, 6→2) ; lien 100 Mb/s
entre les deux PC ; adresses IP configurées, transfert réalisé. Câble étiqueté « CROISÉ ». »

<h3 class="jc-example-title">Exemple 3 — Diagnostiquer une erreur sur les broches 3/6</h3>

**Situation.** Un cordon droit T568B fabriqué par un stagiaire : le PC n'obtient pas de lien.

**Preuves.** Le testeur affiche l'écran ci-dessous. Le bout 2 a été réalisé ainsi :
{end_b}.

{_fig(EXAMPLE3_FIGURE)}

**Lecture.** 4→6 et 6→4 : au bout 2, le **vert** (qui doit être en 6) est en 4, et le
**bleu** (qui doit être en 4) est en 6. La position 3-6 reçoit donc blanc/vert + bleu : **deux
fils de paires différentes**. La position 4-5 reçoit vert + blanc/bleu. La paire servant à
la réception en 10/100 Mb/s est cassée, d'où l'absence de lien (en gigabit, deux paires sont
touchées).

**Correction.** Couper la fiche du bout 2 et la refaire en T568B : 3 blanc/vert, 4 bleu,
5 blanc/bleu, **6 vert**.

**Test.** 1→1 … 8→8 réussi ; lien établi.

**Compte rendu.** « Cordon non conforme : fils vert et bleu permutés à une extrémité (relevé
4↔6). Fiche refaite en T568B, cordon testé conforme, lien rétabli. »

<h3 class="jc-example-title">Exemple 4 — Expliquer un lien limité à 100 Mb/s</h3>

**Situation.** Un poste neuf (carte 1 Gb/s), branché sur un switch 1 Gb/s, affiche « 100 Mb/s,
duplex intégral ». Les postes voisins sont à 1 Gb/s.

**Raisonnement.** Le lien existe : les paires 1-2 et 3-6 fonctionnent (le 100 Mb/s n'utilise
qu'elles). Le 1 Gb/s a besoin des **quatre paires** : un défaut sur 4-5 ou 7-8 empêche le
gigabit, et les cartes se rabattent souvent sur 100 Mb/s.

**Tests.**

1. Testeur sur le cordon de poste : **circuit ouvert broche 7** (fil blanc/marron pas en butée,
   voir l'affichage « circuit ouvert » de la section 5.1).
2. Échange avec un cordon connu bon : le poste passe à **1 Gb/s**. La cause est confirmée.
3. (Si le cordon avait été bon : tester le lien permanent, puis vérifier que la vitesse n'est
   pas forcée à 100 Mb/s sur la carte ou le port, le pilote et la catégorie des éléments.)

**Correction.** Cordon remplacé (ou fiche refaite et retestée).

**Compte rendu.** « Lien à 100 Mb/s au lieu de 1 Gb/s : circuit ouvert sur la broche 7 du
cordon de poste (paire marron, nécessaire au gigabit). Cordon remplacé ; lien à 1 Gb/s
confirmé. »
"""


def _pitfalls() -> str:
    return """> **Tenir la fiche à l'envers.** Languette vers soi, la broche 1 est à droite : tout
> l'ordre est inversé. Contacts vers soi, broche 1 à gauche.

> **Ranger les paires côte à côte.** 1-2, 3-4, 5-6, 7-8 donne des paires séparées : le testeur
> de continuité dit « OK », le réseau fait des erreurs.

> **Mélanger A et B dans une installation.** On câble comme l'existant ; une prise en B sur un
> panneau en A donne un lien croisé.

> **Détorsader largement** « pour que ce soit plus facile ». La diaphonie augmente au point de
> raccordement : environ 13 mm au plus.

> **Oublier les manchons** avant de sertir, ou **laisser la gaine hors de la fiche** : la patte
> de maintien pince les fils au lieu de la gaine, le câble finit par casser.

> **Dénuder les fils un par un.** Les contacts de la fiche percent l'isolant : on ne dénude que
> la gaine extérieure.

> **Fiche pour multibrin sur un câble monobrin** (ou l'inverse), ou fiche d'une catégorie
> inférieure : mauvais contact, performance non garantie.

> **Croire qu'un testeur à LED « tout vert » certifie une installation.** Il ne voit ni les
> paires séparées, ni la longueur, ni la diaphonie.

> **Affirmer que la Cat6 fait 10 Gb/s sur 100 m.** C'est la Cat6A ; la Cat6 seulement sur une
> longueur réduite.

> **Dire que 1-2 et 3-6 suffisent toujours.** Vrai en 10/100 Mb/s seulement ; le 1 Gb/s utilise
> les quatre paires, dans les deux sens.

> **Conclure « câble bon » parce que le voyant de lien s'allume.** Le lien peut être à 100 Mb/s,
> instable, ou la configuration IP fausse : on vérifie aussi la vitesse et la communication.

> **Livrer un câble sans l'avoir testé**, ou sans étiquette sur un lien permanent.
"""


def _exercises_intro() -> str:
    return f"""{len(PRACTICE_ITEMS)} exercices corrigés : six exercices de brochage et de schéma,
quatre analyses de résultats de testeur, trois choix de câble ou d'installation et trois
procédures d'intervention écrites (dont une remise en ordre). Rédige ta réponse sur papier
**avant** d'ouvrir le corrigé. Ces mêmes exercices sont proposés dans
[S'entraîner](/uaa/{PR15_SLUG}/practice), avec correction après envoi.

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
    return f"""Le mini-examen se passe dans l'onglet [Examen blanc](/uaa/{PR15_SLUG}/exam) : **10 questions à réponse
libre**, chacune notée sur **2 points**, soit une note sur **{EXAM_TOTAL_POINTS}**. Les
questions ne figurent pas dans ce cours.

| N° | Thème | Type | Points |
|---|---|---|---|
{rows}

**Déroulement.** Toutes les informations nécessaires sont dans chaque question et ses
documents (relevés de testeur et rapports fictifs). **Aucune correction n'est visible pendant
la passation** ; tes réponses sont enregistrées au fur et à mesure. Après l'envoi, chaque
réponse est corrigée selon le **barème détaillé** de la question, puis tu vois ta note sur
{EXAM_TOTAL_POINTS}, le corrigé et le barème.

**Ce que valorise le barème.** L'**exactitude** (ordre des couleurs, broches, paires,
catégories et longueurs), la **justification** des choix, les **tests** cités avec leur
résultat attendu et l'**ordre** des étapes — pas la récitation de mots-clés. Une réponse
techniquement juste formulée autrement est acceptée.

**Nature de la correction.** Les réponses rédigées reçoivent une **proposition de correction
automatique** (assistée par IA) appuyée sur le barème : c'est un repère d'entraînement, pas une
note officielle ; en cas de doute, compare ta réponse au corrigé. Un brochage faux est toujours
pénalisé, même bien rédigé.
"""


def _memo() -> str:
    return f"""- **Orientation** : contacts dorés face à toi, languette dessous, câble vers le bas →
  **broche 1 à gauche**.
- **T568B** : {T568B_TEXT}.
- **T568A** : {T568A_TEXT}.
- **A ↔ B** : orange et vert échangés (broches 1, 2, 3, 6) ; bleu (4-5) et marron (7-8)
  identiques.
- **Positions de paire** : 1-2, 3-6, 4-5, 7-8 ; chaque position = les deux fils d'une même
  paire, sinon **paire séparée**.
- **Droit** = même norme aux deux bouts ; **croisé** = A d'un côté, B de l'autre (1→3, 2→6,
  3→1, 6→2). **Auto MDI-X** : les deux fonctionnent, sur un équipement qui le gère.
- **Débits** : 10/100 Mb/s = paires 1-2 et 3-6 ; 1 Gb/s = 4 paires, bidirectionnelles.
- **Fabrication** : manchons, dénuder sans entailler, détorsader ≈ 13 mm au plus, ranger,
  recouper, butée, gaine sous la patte, sertir, autre bout, **tester avant mise en service**.
- **Wiremap** : ouvert, court-circuit, paire inversée, paires croisées, paire séparée,
  intermittent. Continuité ≠ performance : **qualification**, **certification**.
- **Longueurs** : canal {CHANNEL_MAX_M} m = {PERMANENT_LINK_MAX_M} m permanent + cordons ;
  Cat5e 1 Gb/s ; Cat6A 10 Gb/s sur 100 m ; Cat6 10 Gb/s sur longueur réduite.
- **Blindage** : U/UTP, F/UTP, U/FTP, S/FTP ; efficace seulement s'il est continu et mis à la
  terre selon l'installation.
- **Diagnostic** : voyant → vitesse → testeur (cordon puis lien permanent) → échange connu bon
  → port/carte → IP.
- **Compte rendu** : besoin, norme, schéma, outils, tests avant/après, résultats, défauts
  corrigés, validation.
"""


def _sources() -> str:
    return """## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), pp. 3, 5 et 6 : épreuve uniquement écrite, exigences AP-18,
  AP-20 et AP-34. Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
- **Brochages T568A et T568B, positions de paire, longueur de canal (100 m, dont 90 m de lien
  permanent), détorsadage au raccordement, rayon de courbure, traction** : normes de câblage
  ANSI/TIA-568 (série 568.2-D pour les composants à paires torsadées).
- **Notation U/UTP, F/UTP, U/FTP, S/FTP** et classes de câblage : ISO/IEC 11801.
- **Usage des paires par Ethernet** (10BASE-T, 100BASE-TX sur deux paires, 1000BASE-T sur
  quatre paires bidirectionnelles, 10GBASE-T et longueurs selon la catégorie), MDI/MDI-X et
  Auto MDI-X : norme IEEE 802.3.
- **Séparation entre câbles de données et câbles d'énergie** : EN 50174-2 et TIA-569.
- **Paramètres de test** (wiremap, longueur, perte d'insertion, NEXT, qualification et
  certification) : documentation des normes de test de terrain (TIA-1152, IEC 61935-1) et des
  fabricants de testeurs.

Les brochages et les liaisons des schémas sont **calculés** à partir des deux tableaux
T568A/T568B et **vérifiés par des tests automatiques** ; aucun schéma n'est tiré d'une image
générée.

## Compléments pédagogiques (non imposés par la liste officielle)

La liste des pp. 5-6 demande la description de la réalisation d'un câble RJ45 et du code des
couleurs (AP-34), les types de câbles (AP-18) et leurs caractéristiques (AP-20). Sont des
**compléments**, signalés comme tels :

- la rédaction de la procédure et du compte rendu (AP-C01, approfondie en PR29) ;
- la notation ISO du blindage, les valeurs de rayon de courbure et de traction, les testeurs de
  qualification et de certification, la NEXT, les signaux BI_DA à BI_DD du 1000BASE-T ;
- les éléments sur la connexion directe de deux PC (AP-28, développée en PR21) et la chaîne de
  câblage (AP-36, développée en PR18).

## Supports fictifs

Les cas, relevés, affichages de testeur et rapports de ce cours sont **fictifs** et
reconstitués pour l'entraînement ; la présentation réelle varie selon le modèle de testeur.
Aucun n'est une question officielle ou déjà posée par le Jury.
"""


def pr15_course_sections() -> list[tuple[str, str]]:
    """Blocs du cours (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("PR15 — Objectifs et place dans l'épreuve", _objectives()),
        ("PR15 — 1. Supports et connecteurs : paires, blindage, catégories, 8P8C", _media()),
        ("PR15 — 2. Brochage T568A/T568B, paires et couleurs", _pinout()),
        ("PR15 — 3. Câble droit, câble croisé, Auto MDI-X et débits", _straight_crossover()),
        ("PR15 — 4. Fabrication : sertir une fiche, raccorder une prise", _fabrication()),
        ("PR15 — 5. Tests et dépannage : wiremap, qualification, diagnostic", _tests()),
        ("PR15 — 6. Contexte professionnel, sécurité et compte rendu", _professional()),
        ("PR15 — Exemples : quatre cas intégralement corrigés", _examples()),
        ("PR15 — Pièges et erreurs fréquentes", _pitfalls()),
        (f"PR15 — Exercices corrigés ({len(PRACTICE_ITEMS)})", _exercises_intro()),
        ("PR15 — Mini-examen noté sur 20 : mode d'emploi", _mini_exam()),
        ("PR15 — Fiche mémo", _memo()),
        ("PR15 — Sources et compléments pédagogiques", _sources()),
    ]
