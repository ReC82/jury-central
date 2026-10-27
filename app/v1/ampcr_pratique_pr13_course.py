"""Cours PR13 « Câbles UTP, FTP, STP et coaxial — choix et pose » — parcours AMPCR pratique
écrite (ticket #216).

Matière : intégralement celle du ticket #216 (composition 4 paires torsadées, rôle de la
torsade, diaphonie, perturbations électromagnétiques, atténuation, débit et catégorie ; U/UTP,
F/UTP, U/FTP, S/FTP et équivalences historiques UTP/FTP/STP ; blindage, continuité et mise à
la terre selon le système ; catégories 5e/6/6A, conducteurs rigides/souples, 8P8C, prises,
cordons, baie ; coaxial âme/diélectrique/tresse/gaine, 50 Ω ou 75 Ω, usages 10BASE2 et vidéo ;
règles de pose : séparation électrique, courbure, traction, longueurs, repérage et test ;
cinq cas résolus de sélection selon les contraintes), découpée en blocs titrés (le titre
pilote le type de carte, `app.card_kind` : aucun titre de bloc théorique ne contient
« examen », « source », « ressource », « exemple », « exercice », « méthode », « piège »,
« attention », « transfert » ni « mémo »).
Données et schémas : `app.v1.ampcr_pratique_pr13_figures` ; exercices et mini-examen :
`app.v1.ampcr_pratique_pr13_bank`. Mise en forme partagée avec les autres cours pratiques.
Le brochage, le sertissage et les tests au testeur relèvent de PR15, la fabrication et le
diagnostic d'un coaxial BNC de PR16 (publiés, liens) ; les débits, distances, l'atténuation et
l'impédance chiffrés (PR14) et la fibre optique (PR17) ne sont pas publiés à la rédaction :
renvoi en texte seulement.
"""

from app.v1.ampcr_pratique_pr06_course import _exercise_card, _fig, _req
from app.v1.ampcr_pratique_pr13_bank import EXAM_ITEMS, EXAM_TOTAL_POINTS, PRACTICE_ITEMS
from app.v1.ampcr_pratique_pr13_figures import (
    BEND_EXAMPLES,
    BEND_FACTOR_COAX,
    BEND_FACTOR_SCREENED,
    BEND_FACTOR_UNSCREENED,
    BEND_FIGURE,
    CHAIN_FIGURE,
    CHANNEL_MAX_M,
    CHOICE_FIGURE,
    CHOICE_STEPS_FIGURE,
    COAX_FIGURE,
    CONDUCTORS,
    CORDS_MAX_M,
    EMI_HIGH,
    EMI_LOW,
    EMI_MEDIUM,
    HISTORICAL,
    JACKET_FIELDS,
    JACKET_MARKING,
    PERMANENT_LINK_MAX_M,
    POSE_FIGURE,
    PROCEDURES,
    PULL_MAX_N,
    SCREEN_FIGURE,
    SECTIONS_FIGURE,
    SEPARATION_FIGURE,
    SEPARATION_MM,
    SEPARATION_UNKNOWN_MM,
    SERVICE_VIDEO,
    SHIELDINGS,
    THIN_SEGMENT_MAX_M,
    UNTWIST_MAX_MM,
    WRITTEN_AT,
    Need,
    choose,
    describe,
    fr,
    label_for,
    min_bend_radius_mm,
    structure_of,
)
from app.v1.ampcr_pratique_pr15_figures import CATEGORIES
from app.v1.ampcr_pratique_pr16_figures import CABLE_TYPES

PR13_TITLE = "Câbles UTP, FTP, STP et coaxial — choix et pose"
PR13_SLUG = "ampcr-pratique-pr13"


def _exercises_html() -> str:
    return "\n\n".join(
        _exercise_card(i, item, anchor_prefix="pr13") for i, item in enumerate(PRACTICE_ITEMS, start=1)
    )


def _ex(*keys: str) -> str:
    """Renvoi texte vers les exercices corrigés liés à un chapitre (séquence « Exercices
    corrigés ») : pas de lien d'ancre, la page n'affiche qu'une séquence à la fois."""
    return ", ".join(f"**{key}**" for key in keys) + " (séquence « Exercices corrigés »)"


# --- Tableaux de données (générés depuis les données vérifiées) ------------------------------


def _shielding_table() -> str:
    rows = "\n".join(
        f"| **{d}** | {describe(d)} | {structure_of(d)} | {use} |" for d, use in SHIELDINGS
    )
    return "| Désignation | Construction | Écran | Usage typique |\n|---|---|---|---|\n" + rows


def _historical_table() -> str:
    rows = "\n".join(f"| **{old}** | {new} | {note} |" for old, new, note in HISTORICAL)
    return "| Nom historique | Désignation X/YTP | Remarque |\n|---|---|---|\n" + rows


def _categories_table() -> str:
    rows = "\n".join(f"| **{cat}** | {mhz} MHz | {rate} | {note} |" for cat, mhz, rate, note in CATEGORIES)
    return "| Catégorie | Fréquence garantie | Débit sur le canal | Remarque |\n|---|---|---|---|\n" + rows


def _conductors_table() -> str:
    rows = "\n".join(f"| **{kind}** | {use} | {detail} |" for kind, use, detail in CONDUCTORS)
    return "| Conducteur | Usage | Raccordement et propriétés |\n|---|---|---|\n" + rows


def _jacket_table() -> str:
    rows = "\n".join(f"| `{field}` | {meaning} |" for field, meaning in JACKET_FIELDS)
    return "| Inscription | Signification |\n|---|---|\n" + rows


def _coax_table() -> str:
    rows = "\n".join(f"| **{name}** | {ohm} Ω | {diameter} | {use} |" for name, ohm, diameter, use in CABLE_TYPES)
    return "| Câble | Impédance | Diamètre | Usage typique |\n|---|---|---|---|\n" + rows


def _separation_table() -> str:
    rows = "\n".join(f"| Classe **{cls}** | {mm} mm |" for cls, mm in SEPARATION_MM.items())
    return (
        "| Classe de séparation du câble de données | Distance minimale sans cloison |\n|---|---|\n"
        + rows
        + f"\n| Classe inconnue | {SEPARATION_UNKNOWN_MM} mm (cas le plus défavorable) |"
    )


def _bend_table() -> str:
    rows = "\n".join(
        f"| {name} | {fr(d)} mm | {fr(min_bend_radius_mm(d, des))} mm |" for name, des, d in BEND_EXAMPLES
    )
    return "| Câble | Diamètre | Rayon minimal |\n|---|---|---|\n" + rows


def _procedures_list() -> str:
    return "\n".join(
        f"{i}. **{title}** ({len(steps)} étapes)" for i, (title, steps) in enumerate(PROCEDURES, start=1)
    )


# Les cinq cas résolus : contraintes → choix calculé par la règle du cours.
CASES: tuple[tuple[str, str, Need], ...] = (
    ("Cas 1 — Bureaux calmes", "Une agence d'assurances câble quinze bureaux : postes à 1 Gb/s, plus long parcours 72 m, aucune machine, aucun câble électrique de forte puissance.",
     Need(rate_gbps=1, length_m=72, emi=EMI_LOW)),
    ("Cas 2 — Atelier industriel", "Une imprimerie relie son serveur de production à 10 Gb/s, à 38 m, au-dessus des rotatives et de leurs variateurs ; la baie est reliée à la terre et le client accepte un système blindé complet.",
     Need(rate_gbps=10, length_m=38, emi=EMI_HIGH, grounded=True)),
    ("Cas 3 — Perturbations sans terre", "Un entrepôt éclairé par de nombreux tubes fluorescents (perturbations moyennes) : coffrets et prises en plastique, aucune liaison à la terre possible pour un écran ; 1 Gb/s, 80 m.",
     Need(rate_gbps=1, length_m=80, emi=EMI_MEDIUM, grounded=False)),
    ("Cas 4 — Longue distance", "Une école relie la salle informatique au bâtiment administratif voisin : 150 m de parcours dans une gaine enterrée, 1 Gb/s.",
     Need(rate_gbps=1, length_m=150, emi=EMI_LOW)),
    ("Cas 5 — Vidéosurveillance analogique", "Une boulangerie fait poser une caméra analogique à 45 m de l'enregistreur ; caméra et enregistreur ont des entrées et sorties vidéo 75 Ω.",
     Need(service=SERVICE_VIDEO, length_m=45)),
)

_CASE_REASONING: dict[str, tuple[str, ...]] = {
    "Cas 1 — Bureaux calmes": (
        "**Service et longueur** : Ethernet, 72 m de lien permanent, sous les 90 m : paire torsadée.",
        "**Catégorie** : 1 Gb/s → Cat5e au minimum (une Cat6 donne de la marge).",
        "**Blindage** : perturbations faibles → aucun écran n'est nécessaire.",
    ),
    "Cas 2 — Atelier industriel": (
        "**Service et longueur** : Ethernet, 38 m : paire torsadée.",
        "**Catégorie** : 10 Gb/s sur un canal normalisé → Cat6A.",
        "**Blindage** : perturbations fortes et terre disponible → tresse globale et paires sous feuille ; toute la chaîne blindée, écran repris à 360°, baie reliée à la terre.",
    ),
    "Cas 3 — Perturbations sans terre": (
        "**Service et longueur** : Ethernet, 80 m : paire torsadée.",
        "**Catégorie** : 1 Gb/s → Cat5e au minimum.",
        "**Blindage** : un écran sans terre ni continuité n'apporte rien (il peut même capter les parasites) → câble non écranté, éloigné des alimentations des luminaires, croisements à angle droit.",
    ),
    "Cas 4 — Longue distance": (
        f"**Longueur** : 150 m dépasse les {CHANNEL_MAX_M} m d'un canal en paire torsadée, quel que soit le câble.",
        "**Choix** : fibre optique (détaillée dans le cours PR17), qui relie aussi sans liaison électrique deux bâtiments aux terres différentes ; câble prévu pour l'extérieur.",
        "**Variante en cuivre** : seulement avec un équipement actif intermédiaire, alimenté et abrité, ce qu'une gaine enterrée ne permet pas ici.",
    ),
    "Cas 5 — Vidéosurveillance analogique": (
        "**Service** : vidéo analogique → coaxial, à l'impédance des appareils.",
        "**Câble** : 75 Ω (RG-59), d'une seule longueur, sans T ni terminateur.",
        "**Connecteurs** : BNC 75 Ω sertis ; jamais de RG-58 ni de BNC 50 Ω récupérés.",
    ),
}

# =============================================================================================
# Sections du cours (titre du bloc, Markdown / HTML)
# =============================================================================================


def _objectives() -> str:
    return f"""## Ce que tu sauras faire, par écrit

L'épreuve pratique AMPCR se passe **uniquement par écrit** (consignes officielles 2026-2027/1,
p. 3). Devant un dossier de câblage, on attend de toi un **choix de câble justifié** par les
contraintes et une **pose conforme**, décrite et contrôlée. Tu dois savoir :

1. **expliquer** la composition d'un câble à 4 paires torsadées, le rôle de la torsade, la
   diaphonie, les perturbations électromagnétiques et l'atténuation ;
2. **lire** une désignation **U/UTP, F/UTP, U/FTP, S/FTP** et traduire les noms historiques
   **UTP, FTP, STP** ;
3. **dire** quand un blindage est utile : **continuité** de l'écran et **mise à la terre**
   selon le système ;
4. **choisir** la **catégorie** (5e, 6, 6A), le conducteur **rigide ou souple**, la
   connectique (**8P8C**, prises, cordons, baie) ;
5. **décrire** un **coaxial** (âme, diélectrique, tresse, gaine), choisir entre **50 Ω** et
   **75 Ω** selon l'usage (10BASE2, vidéo) ;
6. **poser** : séparation des câbles électriques, **rayon de courbure**, **traction**,
   **longueurs**, **repérage** et **tests** de réception.

Ce cours contient **{len(PROCEDURES)} procédures illustrées** :

{_procedures_list()}

## Exigences travaillées dans ce cours

{_req("AP-18")}
{_req("AP-20")}

Ce sont deux exigences **officielles** (consignes, pp. 5-6). Le **brochage**, le sertissage et
les testeurs sont étudiés en [PR15](/uaa/ampcr-pratique-pr15) ; la **fabrication** et le
**diagnostic** d'une liaison coaxiale BNC en [PR16](/uaa/ampcr-pratique-pr16). Les débits, les
distances, l'atténuation et l'impédance **chiffrés** font l'objet du cours suivant du parcours
(PR14) ; la **fibre optique** d'un cours ultérieur (PR17).

## Lien avec la théorie

Les notions de base sont présentées dans la théorie AMPCR :
[MC15 Câblage Ethernet et RJ45](/uaa/ampcr-mc15). Ce cours-ci est **pratique** : choix
justifiés, relevés de chantier à lire, poses à contrôler et rapports, comme dans un dossier
d'examen.

## Comment travailler ce cours

Lis les chapitres dans l'ordre : chacun donne ses **objectifs**, la **théorie**, la
**procédure professionnelle** à rédiger, l'**erreur fréquente**, ce qu'on attend **à l'écrit**
et un **repère rapide**, avec un renvoi vers les exercices liés. Étudie ensuite les **cinq cas
résolus**, fais les **{len(PRACTICE_ITEMS)} exercices corrigés** (ici ou dans « S'entraîner »,
correction après envoi), puis passe le **mini-examen noté sur {EXAM_TOTAL_POINTS}** dans l'onglet
« Examen blanc ».

> **Important —** les chantiers, relevés et marquages de ce cours sont des **supports fictifs**
> construits pour s'entraîner. Les valeurs citées (rayons, distances, longueurs) viennent des
> normes nommées dans les sources (rédaction : {WRITTEN_AT}) ; **la fiche technique du
> fabricant et les normes en vigueur font foi** le jour du chantier. Aucun exercice n'est une
> question officielle ni une question déjà posée par le Jury.
"""


def _twisted_pair() -> str:
    return f"""**Objectifs** : décrire un câble à paires torsadées et expliquer, par écrit, ce qui
limite la qualité d'une liaison.

## 1.1 Quatre paires, huit conducteurs

Un câble Ethernet cuivre contient **4 paires torsadées**, soit **8 conducteurs** isolés. Chaque
paire réunit un fil de couleur pleine et un fil blanc rayé de la même couleur : **bleu**,
**orange**, **vert**, **marron** (paires 1 à 4 de la norme TIA-568). Une gaine protège
l'ensemble ; certains câbles ajoutent un **écran** (chapitre 2) ou un croisillon central qui
écarte les paires.

## 1.2 Rôle de la torsade

Dans une paire, les deux fils transportent le **même signal en opposition** (transmission
**différentielle**). Un parasite extérieur agit presque de la même façon sur les deux fils
torsadés ensemble : le récepteur, qui lit la **différence** entre les deux, l'élimine en
grande partie. La torsade réduit aussi le rayonnement de la paire vers ses voisines.

## 1.3 Diaphonie, perturbations, atténuation

- **Diaphonie** : une partie du signal d'une paire « fuit » sur une autre paire du même câble
  (ou d'un câble voisin). Chaque paire a un **pas de torsade différent** pour la limiter. Un
  **détorsadage** excessif au raccordement (plus de {UNTWIST_MAX_MM} mm) la fait augmenter.
- **Perturbations électromagnétiques** : moteurs, variateurs de vitesse, tubes fluorescents,
  postes à souder, câbles d'énergie, émetteurs radio induisent des parasites dans les
  conducteurs. On s'en protège par la **torsade**, la **distance** (chapitre 8) et, si
  nécessaire, un **écran** relié à la terre.
- **Atténuation** : le signal s'affaiblit le long du câble ; l'affaiblissement augmente avec
  la **longueur** et avec la **fréquence**. C'est une des raisons de la limite de
  {CHANNEL_MAX_M} m d'un canal.

## 1.4 Débit et catégorie

La **catégorie** fixe la **fréquence** jusqu'à laquelle le câble garde ses performances (en
MHz) ; le **débit** (en Gb/s) dépend de cette fréquence, de la technique de transmission et de
la **longueur**. Fréquence et débit ne sont pas la même chose : on choisit la catégorie qui
garantit le débit voulu sur la longueur prévue (chapitre 4). Les valeurs chiffrées
d'atténuation et d'impédance (100 Ω pour la paire torsadée) sont détaillées dans le cours
suivant (PR14).

**Procédure professionnelle (à rédiger)** : symptôme (erreurs, débit faible) → cause physique
probable (diaphonie, parasites, atténuation) → vérification (détorsadage, distance au câble
électrique, longueur) → correction.

**Erreur fréquente** : confondre catégorie et débit (« Cat6 = 6 Gb/s ») ; croire que la gaine
seule protège des parasites.

**À l'écrit** : nommer le **phénomène** (diaphonie, parasite, atténuation), sa **cause** et
la **règle** qui l'évite.

**Repère rapide** : **torsade = différentiel · pas différents = moins de diaphonie · longueur
et fréquence = atténuation**. Exercices liés : {_ex("E12", "E17")}.
"""


def _shielding() -> str:
    return f"""**Objectifs** : lire une désignation de blindage et la traduire en construction réelle.

## 2.1 La notation X/YTP

Les noms **UTP**, **FTP** et **STP** sont ambigus : selon les fabricants, ils désignent des
câbles différents. La norme **ISO/IEC 11801** utilise la notation **X/YTP** :

- **X** = protection **globale**, autour des quatre paires ;
- **Y** = protection **de chaque paire** ;
- **U** = aucune, **F** = écran en **feuille** (*foil*), **S** = **tresse** (*shield, braid*),
  **SF** = tresse et feuille.

{_fig(SECTIONS_FIGURE)}

{_shielding_table()}

Autres désignations rencontrées : **SF/UTP** (tresse et feuille globales), **S/UTP** (tresse
globale), **F/FTP** (feuille globale et paires sous feuille). Les **règles d'usage** du tableau
sont une **convention du cours** : la fiche technique et le cahier des charges font foi.

## 2.2 Les noms historiques

{_historical_table()}

Devant « FTP » ou « STP » dans une commande, on **fait préciser la désignation X/YTP** et on
l'écrit sur le bon de commande.

**Procédure professionnelle (à rédiger)** : lire la désignation → dire où est l'écran → en
déduire la protection et la connectique nécessaire (blindée ou non).

**Erreur fréquente** : commander « du FTP » sans préciser ; croire que U/FTP n'a pas d'écran
parce qu'il commence par U.

**À l'écrit** : « **X** = global, **Y** = par paire ; U/F/S = aucun/feuille/tresse ».

**Repère rapide** : **avant la barre = autour de tout · avant TP = autour de chaque paire**.
Exercices liés : {_ex("E04", "E09", "E16")}.
"""


def _grounding() -> str:
    return f"""**Objectifs** : dire à quelles conditions un câble écranté protège réellement, et les
vérifier par écrit.

## 3.1 Un écran n'est utile que s'il est continu

L'écran capte les parasites et les **écoule vers la terre**. Il faut donc qu'il soit
**continu de bout en bout** : câble écranté, **keystones et panneau de brassage blindés**,
écran **repris sur tout le pourtour** (360°) dans chaque connecteur, **cordons blindés**. Un
seul maillon non blindé interrompt l'écran.

{_fig(SCREEN_FIGURE)}

## 3.2 Mise à la terre selon le système

- Côté **baie** : le panneau blindé est relié à la baie, la baie à la **barrette de terre** du
  bâtiment (réseau d'équipotentialité). Cette liaison suit l'installation électrique :
  elle est réalisée ou vérifiée par l'électricien.
- Côté **poste** : l'écran continue par le cordon blindé jusqu'à l'équipement.
- Le **système** (câble, connecteurs, accessoires d'un même fabricant) précise comment
  reprendre l'écran ; on suit sa notice. Relier l'écran à des terres de potentiels différents
  (entre deux bâtiments, par exemple) peut faire circuler un courant dans l'écran : entre
  bâtiments, on préfère la **fibre**.

Un écran **non relié à la terre** ou **interrompu** n'apporte rien et peut même **capter** les
parasites comme une antenne : dans ce cas, mieux vaut un câble **U/UTP** bien posé.

**Procédure professionnelle (à rédiger)** : relever chaque maillon (câble, prises, panneau,
cordons, baie, terre) → repérer l'interruption → corriger → contrôler la **continuité de
l'écran** au testeur.

**Erreur fréquente** : poser du F/UTP sur des keystones non blindés ; couper la feuille ras ;
oublier la liaison de la baie à la terre.

**À l'écrit** : « écran **continu** + **relié à la terre** par la baie, sinon inutile ».

**Repère rapide** : **câble + prises + panneau + cordons blindés + baie à la terre**.
Exercices liés : {_ex("E11", "E15")}.
"""


def _categories() -> str:
    return f"""**Objectifs** : choisir la catégorie et le type de conducteur, et lire le marquage
d'une gaine.

## 4.1 Catégories 5e, 6 et 6A

{_categories_table()}

**Toute la chaîne** (câble, prises, panneau, cordons, fiches) doit être **au moins de la
catégorie visée** : un seul élément d'une catégorie inférieure limite l'ensemble. Le câble
Cat6A est plus épais : les connecteurs doivent accepter son diamètre.

## 4.2 Conducteurs rigides ou souples

{_conductors_table()}

Les **cordons** étant plus atténuants, leur longueur totale est limitée ({CORDS_MAX_M} m pour
l'ensemble des cordons d'un canal). Les conducteurs sont en **cuivre massif** ; un câble en
aluminium cuivré (**CCA**) n'est pas conforme aux normes de câblage et chauffe davantage s'il
transporte l'alimentation d'un appareil (PoE).

## 4.3 Lire le marquage d'une gaine

Exemple de marquage (fictif, construit comme un marquage réel) :
`{JACKET_MARKING}`

{_jacket_table()}

**Procédure professionnelle (à rédiger)** : débit et longueur → catégorie ; installation fixe
ou cordon → monobrin ou multibrin ; lecture du marquage pour vérifier ce qui est livré.

**Erreur fréquente** : poser un câble multibrin en lien permanent ; mélanger des prises Cat5e
avec un câble Cat6A ; accepter du CCA parce qu'il est moins cher.

**À l'écrit** : « **catégorie** (MHz → débit sur la longueur) + **conducteur** (/1 ou /7) +
**construction** X/YTP ».

**Repère rapide** : **1 Gb/s → Cat5e · 10 Gb/s → Cat6A · /1 = posé · /7 = cordon**.
Exercices liés : {_ex("E07", "E09")}.
"""


def _connectors() -> str:
    return f"""**Objectifs** : nommer chaque élément d'une liaison, de la baie à la prise, et dire
où va quel type de câble.

## 5.1 Connecteur 8P8C, prises et cordons

- La fiche **8P8C** (8 positions, 8 contacts) est **communément appelée RJ45**. On distingue
  la **fiche** (mâle, au bout d'un cordon) et la **prise** (femelle, murale ou sur un
  appareil).
- Le **keystone** est un module de prise qu'on clipse dans un boîtier mural ou un panneau ; le
  câble y est **poinçonné** (contacts autodénudants).
- Un **cordon** est un câble court muni de deux fiches : **cordon de brassage** dans la baie,
  **cordon de poste** entre la prise murale et l'appareil.
- Blindé ou non, catégorie : la connectique **suit le câble**.

## 5.2 La baie

La **baie** (armoire 19 pouces) réunit le **panneau de brassage**, où arrivent les câbles
permanents, les **équipements actifs** (switch), les **guide-câbles** et une **liaison à la
terre**. Les **cordons de brassage** relient les ports du panneau à ceux du switch.

{_fig(CHAIN_FIGURE)}

Le **lien permanent** va du panneau à la prise murale ({PERMANENT_LINK_MAX_M} m au plus) ; le
**canal** comprend en plus les cordons ({CHANNEL_MAX_M} m au plus en tout). Le brochage et le
sertissage des fiches sont détaillés en [PR15](/uaa/ampcr-pratique-pr15).

**Procédure professionnelle (à rédiger)** : décrire la liaison élément par élément, avec le
type de câble et le repère de chaque extrémité.

**Erreur fréquente** : appeler « câble » tout ce qui va du switch au PC ; brancher un PC
directement sur un câble permanent sans prise.

**À l'écrit** : « switch → cordon → panneau → **lien permanent** → prise → cordon → poste ».

**Repère rapide** : **posé = monobrin poinçonné · manipulé = multibrin serti**. Exercices
liés : {_ex("E03", "E07")}.
"""


def _coax() -> str:
    return f"""**Objectifs** : décrire un câble coaxial et choisir son impédance selon l'usage.

## 6.1 Structure

Du centre vers l'extérieur : l'**âme** (conducteur central), le **diélectrique** (isolant qui
maintient l'écart), le **blindage** (tresse, souvent doublée d'une feuille), la **gaine**.
L'âme et le blindage ont le **même axe** : d'où le nom de coaxial.

{_fig(COAX_FIGURE)}

## 6.2 50 Ω ou 75 Ω

L'**impédance caractéristique** dépend du rapport des diamètres de l'âme et du blindage et du
diélectrique ; elle est marquée sur la gaine. **75 Ω** donne une très faible atténuation : on
la retient pour la **vidéo** et la **télévision**. **50 Ω** est un compromis entre puissance
transmissible et pertes : on la retient pour la **radio**, la **mesure** et l'**Ethernet
coaxial**. On ne **mélange jamais** les deux impédances sur une liaison : chaque changement
d'impédance réfléchit une partie du signal.

{_coax_table()}

## 6.3 Usages : 10BASE2 et vidéo

- **10BASE2** (Ethernet fin, historique) : **RG-58** 50 Ω en **bus**, T BNC sur chaque carte,
  **terminateur 50 Ω** à chaque extrémité, segment de {THIN_SEGMENT_MAX_M} m au plus. On ne le
  rencontre plus qu'en maintenance ou en formation.
- **Vidéo analogique** : liaison **point à point** caméra → enregistreur en **RG-59** 75 Ω,
  **BNC 75 Ω**, sans T ni terminateur ; **télévision et satellite** : **RG-6** 75 Ω et fiches
  **F**.

La fabrication d'une liaison BNC, les terminateurs et le diagnostic sont détaillés en
[PR16](/uaa/ampcr-pratique-pr16).

**Procédure professionnelle (à rédiger)** : usage → impédance → câble (RG) → connecteur de la
même impédance → pose sans écrasement.

**Erreur fréquente** : réutiliser du RG-58 et des BNC 50 Ω pour une caméra 75 Ω ; écraser le
câble avec des agrafes (impédance modifiée à cet endroit).

**À l'écrit** : « **âme / diélectrique / tresse / gaine** ; 50 Ω = 10BASE2, radio ; 75 Ω =
vidéo, TV ».

**Repère rapide** : **RG-58 = 50 Ω · RG-59 et RG-6 = 75 Ω · une seule impédance par
liaison**. Exercices liés : {_ex("E08", "E13")}.
"""


def _choice() -> str:
    return f"""**Objectifs** : choisir un câble à partir des contraintes d'un dossier et justifier
ce choix par écrit.

## 7.1 La démarche

{_fig(CHOICE_STEPS_FIGURE)}

## 7.2 La règle de choix du cours

On part du **service**, puis de la **longueur**, des **perturbations** et de la possibilité
d'un **écran relié à la terre**. Cette règle est une **convention du cours**, cohérente avec
les normes ; un cahier des charges peut imposer davantage.

{_fig(CHOICE_FIGURE)}

## 7.3 Comparatif

| Critère | U/UTP | F/UTP | S/FTP | Coaxial |
|---|---|---|---|---|
| Écran | aucun | feuille globale | tresse globale + feuille par paire | tresse (+ feuille) |
| Perturbations | {EMI_LOW} | {EMI_MEDIUM} | {EMI_HIGH} | selon le câble |
| Mise à la terre | non | oui, chaîne continue | oui, chaîne continue | blindage relié aux appareils |
| Rayon de courbure | {BEND_FACTOR_UNSCREENED} × Ø | {BEND_FACTOR_SCREENED} × Ø | {BEND_FACTOR_SCREENED} × Ø | fiche du fabricant (cours : {BEND_FACTOR_COAX} × Ø) |
| Pose et coût | simple, le moins cher | plus soignée | la plus exigeante, la plus chère | connecteurs à l'impédance |
| Usage | bureaux | perturbations moyennes | industrie | vidéo, TV, 10BASE2 |

Au-delà de {CHANNEL_MAX_M} m, ou s'il faut traverser entre deux bâtiments, la paire torsadée ne
convient plus : **fibre optique** (cours PR17).

**Procédure professionnelle (à rédiger)** : « Besoin → longueur → environnement → catégorie →
blindage → référence exacte », chaque étape justifiée par une donnée du dossier.

**Erreur fréquente** : choisir « le meilleur câble » (S/FTP partout) sans terre ni connectique
blindée ; oublier la limite de longueur.

**À l'écrit** : « **Contrainte** → donc **choix** », pour chaque élément du câble.

**Repère rapide** : **service · ≤ {CHANNEL_MAX_M} m · perturbations · terre · catégorie**.
Exercices liés : {_ex("E02", "E05", "E15")}.
"""


def _pose_rules() -> str:
    return f"""**Objectifs** : poser un câble sans le dégrader et contrôler une pose existante,
valeurs à l'appui.

## 8.1 Séparation des câbles électriques

Un câble de données qui longe un câble d'énergie capte des parasites. La norme **EN 50174-2**
fixe la distance minimale selon la **classe de séparation** du câble de données (de **a**, le
moins protégé, à **d**, le mieux protégé, indiquée par le fabricant) :

{_separation_table()}

Ces valeurs valent **sans cloison** et pour **trois circuits d'énergie au plus** ; au-delà, la
distance est multipliée, et une **cloison métallique** (goulotte à compartiments) la réduit
selon les tableaux de la norme. On **croise** un câble d'énergie **à angle droit**.

{_fig(SEPARATION_FIGURE)}

## 8.2 Rayon de courbure

Plié trop serré, un câble se déforme : la géométrie des paires change, la diaphonie et les
réflexions augmentent, l'écran se fend. Rayon minimal d'un câble 4 paires installé (TIA-568) :
**{BEND_FACTOR_UNSCREENED} × son diamètre** s'il n'est pas écranté, **{BEND_FACTOR_SCREENED} ×**
s'il l'est. Pour un **coaxial**, on suit la fiche du fabricant ; à défaut, le cours retient
**{BEND_FACTOR_COAX} ×** le diamètre.

{_bend_table()}

{_fig(BEND_FIGURE)}

## 8.3 Traction et fixation

- **Traction** : {PULL_MAX_N} N au plus pendant le tirage d'un câble 4 paires (environ le
  poids d'une masse de 11 kg) ; au-delà, le câble s'étire et ses paires se déforment.
- **Fixation** : colliers **non serrés** ou bandes auto-agrippantes ; **jamais d'agrafe**,
  qui écrase le câble ; pas de câble posé sur un faux plafond sans support, ni tendu entre
  deux points.
- **Raccordement** : détorsader **{UNTWIST_MAX_MM} mm au plus**, garder la gaine jusqu'au
  contact ; laisser une **réserve** de câble à chaque extrémité.

**Procédure professionnelle (à rédiger)** : pour chaque tronçon, comparer la valeur relevée à
la règle (rayon, traction, distance), conclure **conforme / non conforme** et proposer la
correction.

**Erreur fréquente** : partager la goulotte du 230 V sans cloison ; plier à angle vif derrière
la baie ; fixer à l'agrafeuse.

**À l'écrit** : « **valeur relevée** ≥ ou < **valeur exigée** (calcul) → verdict →
correction ».

**Repère rapide** : **rayon {BEND_FACTOR_UNSCREENED}/{BEND_FACTOR_SCREENED} × Ø · ≤ {PULL_MAX_N} N ·
classe inconnue {SEPARATION_UNKNOWN_MM} mm · croiser à 90° · pas d'agrafe**. Exercices liés :
{_ex("E06", "E12", "E13", "E17")}.
"""


def _lengths_labels_tests() -> str:
    return f"""**Objectifs** : vérifier les longueurs, repérer chaque lien et réceptionner une
installation.

## 9.1 Longueurs

- **Lien permanent** (panneau → prise) : **{PERMANENT_LINK_MAX_M} m** au plus ;
- **cordons** (brassage + poste) : **{CORDS_MAX_M} m** au plus au total ;
- **canal** (switch → poste) : **{CHANNEL_MAX_M} m** au plus.

Les trois règles s'appliquent **ensemble** : un lien permanent de 93 m est non conforme même si
le canal reste sous {CHANNEL_MAX_M} m. On mesure la longueur au **testeur** (ou d'après les
repères métriques de la gaine), pas « à vue ».

## 9.2 Repérage

Chaque câble porte le **même repère aux deux extrémités**, posé **avant** le tirage, sur une
étiquette durable. Convention du cours : **baie, panneau, port** — par exemple
`{label_for(1, 1, 7)}` sur le port 7 du panneau 1 de la baie 1 **et** sur la prise murale
reliée. Le **plan de câblage** et le **tableau de brassage** de la baie reprennent ces repères.

## 9.3 Tests de réception

Chaque lien est testé et le résultat consigné avec son repère : **câblage** broche à broche
(continuité, paires, inversions), **longueur**, **performances** de la catégorie (avec un
testeur qui les mesure) et, pour un câble écranté, **continuité de l'écran**. Un PC « qui se
connecte » ne prouve pas que le lien tient son débit. Les testeurs et leurs affichages sont
étudiés en [PR15](/uaa/ampcr-pratique-pr15).

{_fig(POSE_FIGURE)}

**Procédure professionnelle (à rédiger)** : repères → tests de chaque lien → tableau des
résultats → plan mis à jour → remise au client.

**Erreur fréquente** : étiqueter après la pose ; ne contrôler que le canal total ; ne rien
consigner.

**À l'écrit** : « repère `{label_for(1, 1, 7)}` aux deux bouts ; tests câblage, longueur,
performances, écran ; résultats remis ».

**Repère rapide** : **{PERMANENT_LINK_MAX_M} + {CORDS_MAX_M} = {CHANNEL_MAX_M} · même repère
aux deux bouts · tester et consigner**. Exercices liés : {_ex("E01", "E10", "E14")}.
"""


def _examples() -> str:
    blocks: list[str] = []
    for title, situation, need in CASES:
        choice = choose(need)
        steps = "\n".join(f"{i}. {line}" for i, line in enumerate(_CASE_REASONING[title], start=1))
        blocks.append(
            f"""## {title}

**Situation.** {situation}

**Résolution.**

{steps}

**Choix retenu** : **{choice.cable}**, connectique : {choice.connector}.

**Conclusion rédigée.** « {choice.reason} Choix : {choice.cable} ({choice.connector}). »
"""
        )
    return (
        "Cinq dossiers de sélection, résolus avec la règle du cours (chapitre 7). Le choix est "
        "calculé à partir des contraintes, comme dans les exercices.\n\n" + "\n".join(blocks)
    )


def _pitfalls() -> str:
    return f"""> **Commander « du FTP » ou « du STP »** sans désignation X/YTP.

> **Poser un câble écranté** sur des prises non blindées, ou sans relier la baie à la terre.

> **Choisir S/FTP partout** « parce que c'est le meilleur », sans terre ni connectique
> blindée.

> **Confondre catégorie et débit** ; mélanger des éléments de catégories différentes.

> **Poser du multibrin en lien permanent**, ou fabriquer des cordons avec du monobrin.

> **Mélanger 50 Ω et 75 Ω** : RG-58 ou BNC 50 Ω sur une caméra 75 Ω.

> **Partager la goulotte du 230 V** sans cloison ; longer un câble d'énergie au lieu de le
> croiser à angle droit.

> **Plier sous le rayon minimal** ({BEND_FACTOR_UNSCREENED} × Ø, {BEND_FACTOR_SCREENED} × Ø
> écranté) ; **tirer au-delà de {PULL_MAX_N} N** ; **agrafer**.

> **Détorsader plus de {UNTWIST_MAX_MM} mm** au raccordement.

> **Oublier la limite de {PERMANENT_LINK_MAX_M} m** du lien permanent parce que le canal fait
> moins de {CHANNEL_MAX_M} m.

> **Étiqueter après coup**, ou un seul bout ; **ne pas tester** ni consigner.
"""


def _exercises_intro() -> str:
    return f"""{len(PRACTICE_ITEMS)} exercices corrigés : remises en ordre (pose, choix, chaîne de la
baie au poste), classements (construction d'après la désignation, câble selon les contraintes,
conformité de tronçons posés, monobrin ou multibrin, coaxial 50 Ω ou 75 Ω), documents à lire
(marquage de gaine, longueurs, continuité de l'écran, rayon de courbure, étiquetage), commande
« FTP » ambiguë, comparatif, coaxial écrasé, fiche à corriger. Rédige ta réponse sur papier
**avant** d'ouvrir le corrigé ; toute réponse équivalente et justifiée est acceptée. Ces mêmes
exercices sont proposés dans [S'entraîner](/uaa/{PR13_SLUG}/practice), avec correction après
envoi.

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
    return f"""Le mini-examen se passe dans l'onglet [Examen blanc](/uaa/{PR13_SLUG}/exam) : **10 questions à réponse
libre**, chacune notée sur **2 points**, soit une note sur **{EXAM_TOTAL_POINTS}**. Les
questions ne figurent pas dans ce cours.

| N° | Thème | Type | Points |
|---|---|---|---|
{rows}

**Déroulement.** Chaque question est une situation complète : toutes les informations
nécessaires sont dans l'énoncé et ses documents (marquages et relevés fictifs).
**Aucune correction n'est visible pendant la passation** ; tes réponses sont enregistrées au
fur et à mesure. Après l'envoi, chaque réponse est corrigée selon le **barème analytique** de la
question (critères et points), puis tu vois ta note sur {EXAM_TOTAL_POINTS}, le corrigé et le
barème.

**Ce que valorise le barème.** Le **choix justifié** par les contraintes (contrainte → choix),
la **règle** appliquée avec son **calcul** (rayon, distance, longueur), la **correction**
proposée et le **contrôle** — pas la récitation de sigles. Une autre formulation juste est
acceptée.

**Nature de la correction.** Les réponses rédigées reçoivent une **proposition de correction
automatique** (assistée par IA) appuyée sur le barème : c'est un repère d'entraînement, pas une
note officielle ; en cas de doute, compare ta réponse au corrigé.
"""


def _memo() -> str:
    return f"""## Mémo

- **Câble 4 paires** : 8 conducteurs, transmission différentielle ; torsade = moins de
  parasites et de diaphonie ; détorsader ≤ {UNTWIST_MAX_MM} mm.
- **X/YTP** : X = global, Y = par paire ; U = aucun, F = feuille, S = tresse. U/UTP · F/UTP ·
  U/FTP · S/FTP. « FTP », « STP » : ambigus, faire préciser.
- **Écran** : utile seulement s'il est **continu** (prises, panneau, cordons blindés) et
  **relié à la terre** par la baie ; sinon U/UTP.
- **Catégories** : Cat5e 100 MHz (1 Gb/s) · Cat6 250 MHz · Cat6A 500 MHz (10 Gb/s sur 100 m) ;
  toute la chaîne de la même catégorie.
- **Conducteurs** : monobrin (/1) posé et poinçonné · multibrin (/7) pour les cordons.
- **Coaxial** : âme, diélectrique, tresse, gaine ; 50 Ω (RG-58, 10BASE2, radio) · 75 Ω
  (RG-59 vidéo, RG-6 TV) ; jamais de mélange.
- **Choix** : service → ≤ {CHANNEL_MAX_M} m → perturbations → terre → catégorie ; sinon fibre.
- **Pose** : rayon {BEND_FACTOR_UNSCREENED} × Ø (non écranté), {BEND_FACTOR_SCREENED} × Ø (écranté) ;
  ≤ {PULL_MAX_N} N ; distance au 230 V selon la classe ({SEPARATION_UNKNOWN_MM} mm si inconnue),
  croisement à 90° ; pas d'agrafe.
- **Longueurs** : lien permanent ≤ {PERMANENT_LINK_MAX_M} m, cordons ≤ {CORDS_MAX_M} m, canal ≤
  {CHANNEL_MAX_M} m.
- **Réception** : même repère aux deux bouts ; tests câblage, longueur, performances, écran ;
  résultats consignés.

## Glossaire des termes employés

- **Atténuation** : affaiblissement du signal le long du câble ; augmente avec la longueur et
  la fréquence.
- **Canal** : liaison complète d'un équipement à l'autre, cordons compris.
- **Diaphonie** : signal d'une paire qui se retrouve sur une autre paire.
- **Diélectrique** : isolant entre l'âme et le blindage d'un coaxial.
- **Écran (feuille) / tresse** : enveloppe conductrice qui protège des parasites ; la feuille
  est une bande métallisée, la tresse un tissage de fils fins.
- **Impédance caractéristique** : propriété d'un câble fixée par sa géométrie (50 Ω, 75 Ω,
  100 Ω pour la paire torsadée) ; la liaison et les appareils doivent avoir la même.
- **Keystone** : module de prise femelle, poinçonné, clipsé dans un boîtier ou un panneau.
- **Lien permanent** : partie fixe de l'installation, du panneau de brassage à la prise
  murale.
- **Panneau de brassage** : panneau de prises dans la baie où arrivent les liens permanents.
- **Poinçonnage** : raccordement d'un conducteur dans un contact autodénudant, à l'outil.
"""


def _sources() -> str:
    return f"""## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), pp. 5-6 : « Les différents types de câbles : UTP, FTP, STP,
  Coax » (AP-18) et « Les caractéristiques des câbles : atténuation, notion d'impédance,
  sensibilité aux parasites, blindage, précautions d'utilisation, avantages, inconvénients…,
  longueur maximale d'un tronçon suivant le débit, connecteurs » (AP-20). Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
  Programme officiel n° 345/2007/249 (option AMPCR).
- **Normes de câblage** : ISO/IEC 11801 (désignation X/YTP, classes et catégories) ;
  ANSI/TIA-568 (paires, lien permanent de 90 m, canal de 100 m, rayon de courbure 4 × et
  8 × le diamètre, traction de 110 N, détorsadage de 13 mm) ; EN 50174-2 (pose, distances
  entre câbles de données et d'énergie selon la classe de séparation) ; IEEE 802.3 (10BASE2,
  1000BASE-T, 10GBASE-T).
- **Coaxial** : valeurs nominales des câbles RG-58, RG-59, RG-6 (fiches de fabricants) et
  IEEE 802.3 clause 10 pour 10BASE2.

Les valeurs sont celles de {WRITTEN_AT} ; les normes évoluent et les fabricants précisent
leurs propres valeurs : **la fiche technique et les normes en vigueur font foi**. Les coupes de
câble, l'arbre de choix, les distances, les rayons, les longueurs et les repères du cours sont
**produits par programme** depuis des données **vérifiées par des tests automatiques** ; aucun
schéma n'est tiré d'une image générée ni d'une photographie.

## Compléments pédagogiques (non imposés par la liste officielle)

Les pp. 5-6 citent les types de câbles et leurs caractéristiques. Sont des **compléments**,
signalés comme tels, utiles pour traiter un dossier écrit :

- la règle de choix (service, longueur, perturbations, terre, catégorie) et les usages
  typiques de chaque blindage : ce sont des **conventions du cours** ;
- le rayon de courbure du coaxial ({BEND_FACTOR_COAX} × le diamètre quand la fiche manque) et le
  schéma de repérage baie-panneau-port : **conventions du cours** ;
- le marquage de gaine, la réaction au feu et le câble CCA.

## Supports fictifs

Les chantiers, marquages, relevés et entreprises de ce cours sont **fictifs** et reconstitués
pour l'entraînement ; ils ne décrivent aucun client réel. Aucune n'est une question officielle
ou déjà posée par le Jury. Pour un cas réel, on utilise la fiche du fabricant et un testeur.
"""


def pr13_course_sections() -> list[tuple[str, str]]:
    """Blocs du cours (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("PR13 — Objectifs et place dans l'épreuve", _objectives()),
        ("PR13 — 1. Paire torsadée : composition, torsade, diaphonie, parasites, atténuation", _twisted_pair()),
        ("PR13 — 2. Blindage : U/UTP, F/UTP, U/FTP, S/FTP et noms historiques", _shielding()),
        ("PR13 — 3. Blindage efficace : continuité et mise à la terre selon le système", _grounding()),
        ("PR13 — 4. Catégories 5e, 6, 6A, conducteurs rigides ou souples, marquage", _categories()),
        ("PR13 — 5. Connectique et baie : 8P8C, prises, cordons, panneau de brassage", _connectors()),
        ("PR13 — 6. Câble coaxial : structure, 50 Ω ou 75 Ω, 10BASE2 et vidéo", _coax()),
        ("PR13 — 7. Choisir un câble selon les contraintes", _choice()),
        ("PR13 — 8. Règles de pose : séparation électrique, courbure, traction, fixation", _pose_rules()),
        ("PR13 — 9. Longueurs, repérage et tests de réception", _lengths_labels_tests()),
        ("PR13 — Exemples : cinq cas de sélection résolus", _examples()),
        ("PR13 — Pièges et erreurs fréquentes", _pitfalls()),
        (f"PR13 — Exercices corrigés ({len(PRACTICE_ITEMS)}) et leurs corrigés", _exercises_intro()),
        ("PR13 — Mini-examen noté sur 20 : mode d'emploi", _mini_exam()),
        ("PR13 — Fiche mémo et glossaire", _memo()),
        ("PR13 — Sources et compléments pédagogiques", _sources()),
    ]

