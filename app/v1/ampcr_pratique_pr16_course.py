"""Cours PR16 « Câble coaxial et BNC — impédance, fabrication et diagnostic écrit » — parcours
AMPCR pratique écrite (ticket #198).

Matière : intégralement celle du ticket #198 (1. structure du coaxial, 2. impédance
caractéristique, 3. réflexions, 4. connecteurs BNC, 5. 10BASE2, 6. 10BASE5, 7. liaisons vidéo
75 Ω, 8. fabrication, 9. outils, 10. lecture de schémas, 11. diagnostic, 12. sécurité et
rapport), découpée en blocs titrés (le titre pilote le type de carte, `app.card_kind` : aucun
titre de bloc théorique ne contient « examen », « source », « exemple », « exercice »,
« méthode », « piège » ni « attention »). Schémas : `app.v1.ampcr_pratique_pr16_figures` (bus,
lectures et distances calculés depuis un modèle testé) ; exercices et mini-examen :
`app.v1.ampcr_pratique_pr16_bank`. Mise en forme partagée avec PR06/PR11/PR15.
"""

from app.v1.ampcr_pratique_pr06_course import _exercise_card, _fig, _req
from app.v1.ampcr_pratique_pr16_bank import EXAM_ITEMS, EXAM_TOTAL_POINTS, PRACTICE_ITEMS
from app.v1.ampcr_pratique_pr16_figures import (
    AUI_MAX_M,
    BNC_PARTS_FIGURE,
    BUS_FAULT_FIGURES,
    BUS_OK_FIGURE,
    CABLE_TYPES,
    COAX_SECTION_FIGURE,
    COMPARISON_FIGURE,
    CRIMP_CHECK_FIGURE,
    CRIMP_FIGURE,
    READINGS,
    READINGS_FIGURE,
    STRIP_FIGURE,
    TDR_FIGURES,
    TDR_OPEN_NS,
    TDR_VF,
    THICK_SEGMENT_MAX_M,
    THICK_TAP_SPACING_M,
    THICK_TRANSCEIVERS_MAX,
    THIN_MIN_SPACING_M,
    THIN_SEGMENT_MAX_M,
    THIN_STATIONS_MAX,
    fr,
    reading_text,
    reflection_coefficient,
    tdr_distance_m,
)

PR16_TITLE = "Câble coaxial et BNC — impédance, fabrication et diagnostic écrit"
PR16_SLUG = "ampcr-pratique-pr16"
# Titres des blocs remplacés après la première installation (tableaux trop larges à 390 px
# convertis en listes) : le seed retire ces anciens blocs et crée les nouveaux.
PR16_OBSOLETE_TITLES = frozenset({
    "PR16 — 1. Structure du câble coaxial et familles RG",
    "PR16 — 2-3. Impédance caractéristique, adaptation et réflexions",
    "PR16 — 5-7. Ethernet 10BASE2, 10BASE5 et liaisons vidéo 75 Ω",
    "PR16 — Exercices corrigés (16)",
})


def _exercises_html() -> str:
    return "\n\n".join(
        _exercise_card(i, item, anchor_prefix="pr16") for i, item in enumerate(PRACTICE_ITEMS, start=1)
    )


def _gamma(load: float | None, line: float = 50) -> str:
    value = reflection_coefficient(load, line)
    sign = "+" if value > 0 else ("−" if value < 0 else "")
    return f"{sign}{fr(abs(value), 2)}"


# =============================================================================================
# Sections du cours (titre du bloc, Markdown / HTML)
# =============================================================================================


def _objectives() -> str:
    return f"""## Ce que tu sauras faire, par écrit

L'épreuve pratique AMPCR se passe **uniquement par écrit** (consignes officielles 2026-2027/1,
p. 3) : tu ne monteras pas de connecteur devant le jury, mais tu dois savoir **décrire,
interpréter et justifier** la réalisation et le contrôle d'une liaison coaxiale. À partir d'un
schéma, d'un besoin et de symptômes, tu sais :

1. **reconnaître** un câble coaxial, ses couches et son impédance (marquage) ;
2. **choisir** un câble, un connecteur et une terminaison **de même impédance** (50 Ω ou 75 Ω) ;
3. **dessiner et corriger** un bus Ethernet coaxial 10BASE2 (T, terminateurs, longueurs) ;
4. **distinguer** 10BASE2, 10BASE5 et une liaison vidéo 75 Ω ;
5. **décrire** la fabrication d'une liaison BNC, étape par étape, avec ses contrôles ;
6. **diagnostiquer** une panne (mesures, réflexions, défauts de connecteur) et **rédiger** le
   compte rendu.

## Exigences officielles travaillées dans ce cours

{_req("AP-35")}
{_req("AP-18")}
{_req("AP-20")}

AP-35 est le cœur du cours (réalisation d'un câble à connecteurs BNC). AP-18 et AP-20 sont
travaillées **pour le câble coaxial** (type de câble, impédance, blindage, longueur d'un
tronçon, connecteurs) ; la comparaison de tous les supports (paires torsadées, fibre) et les
débits sont l'objet des cours PR13, PR14 et PR17. Le bus coaxial touche aussi les topologies
(AP-23, PR19) et l'installation physique (AP-36, PR18).

Complément pédagogique (hors liste officielle des pp. 5-6, signalé comme tel) :

{_req("AP-C01")}

## Pourquoi apprendre une technologie ancienne ?

L'Ethernet coaxial (10BASE2, 10BASE5) est **historique** : il a été remplacé par les paires
torsadées et les switchs, et la norme IEEE 802.3 l'a retiré pour les nouvelles installations en
2011. Les consignes officielles demandent pourtant de savoir **décrire la réalisation d'un câble
à connecteurs BNC** ; le coaxial reste aussi très présent en **vidéo** (vidéosurveillance, SDI),
en **télévision** et en **radiofréquence**. Ce cours prépare aux deux usages, sans jamais les
confondre.

Aucun mini-cours de la théorie AMPCR ne traite le coaxial : ce cours est autonome.

## Comment travailler ce cours

Lis les sections dans l'ordre ; apprends par cœur la **règle des impédances** (2) et le **schéma
du bus 10BASE2** (5) jusqu'à pouvoir les redessiner. Étudie les **quatre exemples corrigés**,
fais les **{len(PRACTICE_ITEMS)} exercices corrigés** (ici ou dans « S'entraîner », correction
après envoi), puis passe le **mini-examen noté sur {EXAM_TOTAL_POINTS}** dans l'onglet
« Examen blanc ».

> **Important —** les situations, relevés, mesures et traces de ce cours sont des **supports
> fictifs** construits pour s'entraîner. Les impédances, limites et règles de câblage sont
> celles des normes (IEEE 802.3) et de la documentation technique. Aucun exercice n'est une
> question officielle ni une question déjà posée par le Jury.
"""


def _structure() -> str:
    rows = "\n".join(f"- **{name}** — **{ohm} Ω**, {diameter} : {use}." for name, ohm, diameter, use in CABLE_TYPES)
    return f"""## 1.1 Quatre couches autour d'un même axe

{_fig(COAX_SECTION_FIGURE)}

Un câble **coaxial** est formé de deux conducteurs qui partagent **le même axe** :

1. **L'âme** : conducteur central en cuivre (massif ou multibrin). Elle porte le signal.
2. **Le diélectrique** : isolant (polyéthylène plein ou expansé…) qui maintient l'âme
   **exactement au centre**, à distance constante du blindage.
3. **Le blindage** : feuille d'aluminium et/ou **tresse** de fils de cuivre, parfois les deux
   (double blindage). Il sert de **conducteur de retour** du signal et de **protection** contre
   les parasites.
4. **La gaine** : enveloppe extérieure (PVC…) qui protège mécaniquement et porte le
   **marquage** (type, impédance, fabricant).

## 1.2 Rôle et propriétés

- **Protection contre les perturbations électromagnétiques (EMI)** : le champ du signal reste
  entre l'âme et le blindage ; le blindage protège aussi des parasites extérieurs. Il n'est
  efficace que **continu** d'un bout à l'autre, connecteurs compris.
- **Atténuation** : le signal s'affaiblit avec la **longueur** et avec la **fréquence** ; c'est
  pourquoi chaque usage fixe une longueur maximale de tronçon.
- **Bande passante** : le coaxial transporte des signaux de fréquence élevée (vidéo, radio,
  télévision) ; plus la fréquence monte, plus la qualité du câble et des connecteurs compte.
- **Souplesse** : un câble fin (RG-58, ≈ 5 mm) se pose facilement ; un câble épais (≈ 10 mm)
  est raide et atténue moins.
- **Contraintes de pose** : pas de pli ni d'écrasement (respecter le rayon de courbure du
  fabricant), pas de traction excessive, pas d'agrafe qui traverse le câble : tout ce qui
  déforme le câble change son impédance à cet endroit (section 3).

## 1.3 Les familles « RG » et le marquage

La désignation **RG** (*Radio Guide*, ancienne nomenclature militaire américaine) sert encore à
désigner des familles de câbles. Elle ne suffit pas toujours : il existe des variantes (A/U,
C/U…). **On lit le marquage de la gaine**, en particulier l'**impédance**.

{rows}

Deux câbles de même diamètre peuvent avoir des impédances différentes (RG-58 50 Ω et RG-59
75 Ω se ressemblent) : **jamais de choix « à l'œil »**.
"""


def _impedance() -> str:
    rows = "\n".join(
        f"- **{label}** (charge {load}) : Γ = **{_gamma(value)}**, {meaning}."
        for label, load, value, meaning in (
            ("Terminateur 50 Ω sur câble 50 Ω", "50 Ω", 50, "adaptation : rien n'est renvoyé"),
            ("Terminateur 75 Ω sur câble 50 Ω", "75 Ω", 75, "20 % de l'amplitude renvoyée"),
            ("Extrémité libre (pas de terminateur)", "infinie", None, "tout est renvoyé, même sens"),
            ("Court-circuit âme/blindage", "0 Ω", 0, "tout est renvoyé, sens inverse"),
        )
    )
    return f"""## 2.1 L'impédance caractéristique, en mots simples

Quand un signal se propage dans un câble, le câble lui oppose un rapport fixe entre **tension**
et **courant** : c'est son **impédance caractéristique**, en **ohms (Ω)**. Elle dépend
**uniquement de la géométrie** (diamètre de l'âme, diamètre du blindage) et de
**l'isolant** — **pas de la longueur** du câble.

Conséquences pratiques :

- un câble de 1 m et un câble de 100 m du même type ont **la même** impédance (50 Ω, 75 Ω…) ;
- **un ohmmètre ne mesure pas l'impédance caractéristique** : entre l'âme et le blindage d'un
  câble seul, il affiche l'infini (ce sont deux conducteurs isolés) ;
- écraser ou plier le câble change sa géométrie, donc son impédance **à cet endroit**.

## 2.2 Les deux valeurs à connaître

- **50 Ω** : Ethernet coaxial historique (**10BASE2** et **10BASE5**), radiofréquence
  d'émission (antennes, appareils de mesure), données.
- **75 Ω** : **vidéo** (vidéosurveillance analogique, **SDI** numérique), **télévision** et
  **satellite**, et d'autres applications de transmission.

**Câble, connecteur, terminaison et équipement doivent avoir la même impédance.** Ce sont
quatre éléments distincts : un câble 50 Ω, un connecteur 50 Ω, un terminateur 50 Ω, une entrée
d'équipement 50 Ω. Un seul élément différent crée une **désadaptation**.

> **À retenir —** le connecteur **BNC existe en 50 Ω et en 75 Ω**. Ne jamais dire que « tous
> les BNC sont à 50 Ω » : on vérifie le marquage du connecteur comme celui du câble.

## 3. Réflexions et désadaptation

Un signal qui arrive sur un changement d'impédance est **en partie renvoyé** vers l'émetteur,
comme un écho. La part renvoyée est le **coefficient de réflexion**
**Γ = (Zc − Z0) / (Zc + Z0)**, où Z0 est l'impédance du câble et Zc celle de ce qu'il rencontre.

Sur un câble 50 Ω :

{rows}

Ce qui crée une réflexion :

- **mauvaise impédance** : tronçon 75 Ω dans un bus 50 Ω, terminateur ou connecteur de la
  mauvaise valeur ;
- **terminaison absente** : l'extrémité libre renvoie tout le signal ;
- **terminaison erronée** : un terminateur 75 Ω ou 93 Ω sur un câble 50 Ω ;
- **rupture** (câble coupé) : extrémité libre au milieu du câble ;
- **connecteur défectueux** ou **câble écrasé** : petite zone d'impédance différente.

**Pourquoi c'est grave sur un bus Ethernet coaxial ?** Tous les postes partagent le même câble.
Les échos se superposent aux trames suivantes : les cartes détectent des **collisions** qui
n'existent pas, les trames arrivent **corrompues**, et souvent **plus aucun poste** ne communique.
En vidéo, les réflexions donnent des images dédoublées (vidéo analogique) ou des erreurs et
coupures (SDI).

L'effet d'une petite désadaptation dépend de la **fréquence** : à basse fréquence (en dessous
d'une dizaine de MHz environ), un court connecteur de la mauvaise impédance passe presque
inaperçu ; en vidéo numérique (SDI, plusieurs centaines de MHz à plusieurs GHz), il dégrade la
liaison. Un **tronçon de câble** de mauvaise impédance ou un **terminateur** faux, eux, posent
problème dans tous les cas.
"""


def _bnc() -> str:
    return f"""## 4.1 Le principe du BNC

Le **BNC** est un connecteur coaxial à **verrouillage à baïonnette** : on enfonce la fiche sur la
prise, puis on tourne l'écrou d'**un quart de tour** pour engager les **deux ergots** de la prise
dans les rainures de l'écrou. Il se branche et se débranche vite, sans outil, et ne se dévisse
pas tout seul. Il est utilisé jusqu'à quelques GHz.

{_fig(BNC_PARTS_FIGURE)}

- **Mâle** (fiche) : contact central en forme de **broche**, écrou à baïonnette tournant. Il
  équipe le bout des câbles.
- **Femelle** (prise, embase) : contact central **creux**, deux ergots. Elle équipe les cartes,
  les appareils, les T et les raccords.
- **Adaptateur en T** : une entrée mâle (sur la carte réseau) et deux sorties femelles (le câble
  qui arrive, le câble qui repart). C'est une simple **dérivation passive**, pas un switch.
- **Terminateur** : bouchon qui contient une **résistance** égale à l'impédance du câble
  (50 Ω pour l'Ethernet coaxial). Certains ont une petite chaîne pour la mise à la terre.
- **Raccord droit** (femelle/femelle) : relie deux câbles équipés de fiches mâles.

## 4.2 Compatibilité et variantes

- **Impédance** : BNC **50 Ω** ou **75 Ω**. Ils **s'emboîtent mécaniquement** (conçus pour
  s'accoupler sans dommage), ce qui rend l'erreur facile. Le 75 Ω a parfois moins de
  diélectrique visible sur la face avant, mais ce n'est pas un repère fiable : **on lit le
  marquage** ou la référence.
- **Câble prévu** : chaque connecteur est fait pour un **diamètre de câble** et une **taille
  d'âme** (RG-58, RG-59…). Un connecteur RG-59 sur du RG-58 serre mal la tresse.
- **Mode de fixation**, selon le produit :
  - **à sertir** (le plus courant) : contact central et bague sertis à la pince, avec la
    **matrice** prévue pour ce connecteur ;
  - **à compression** : un outil comprime le connecteur sur le câble (étanche, fiable, courant
    en vidéo) ;
  - **à souder / à visser** (*twist-on*) : le soudage demande du soin ; le connecteur vissé à la
    main tient mal et assure un mauvais contact du blindage, à éviter pour une installation
    durable.
- **Outils** : chaque système a son outil ; une pince à sertir RJ45 ne convient pas.
"""


def _ethernet() -> str:
    return f"""## 5. Ethernet fin : 10BASE2 (*thin Ethernet*, « cheapernet »)

**Lecture du nom :** 10 = **10 Mb/s** ; BASE = bande de base ; 2 = segment d'environ
**200 m** (en réalité **{THIN_SEGMENT_MAX_M} m**).

| Caractéristique | Valeur |
|---|---|
| Débit | 10 Mb/s, partagé par tous les postes (semi-duplex) |
| Topologie | **bus** : un seul câble passe de poste en poste |
| Câble | coaxial fin **RG-58 (A/U ou C/U), 50 Ω**, ≈ 5 mm |
| Longueur d'un segment | **{THIN_SEGMENT_MAX_M} m au plus** |
| Nombre de postes par segment | **{THIN_STATIONS_MAX} au plus** |
| Écart entre deux T | **{fr(THIN_MIN_SPACING_M)} m au moins** |
| Raccordement d'un poste | **T BNC branché directement sur la carte**, sans câble entre T et carte |
| Extrémités | **un terminateur 50 Ω à chaque extrémité** du bus (deux en tout) |
| Mise à la terre | en **un seul point** (une extrémité) selon les règles de l'installation, jamais aux deux |

{_fig(BUS_OK_FIGURE)}

**Ce qu'il faut comprendre :**

- Ce n'est **pas** une étoile : il n'y a ni switch ni câble individuel par poste. Le câble
  **entre** dans le T d'un poste et **en ressort** vers le poste suivant.
- Les **deux** extrémités du bus reçoivent un terminateur 50 Ω, vissé sur la sortie libre du T
  du premier et du dernier poste. Un seul manquant suffit à bloquer **tout** le segment.
- Le T doit être **directement** sur la carte : un câble entre le T et la carte est une
  dérivation non terminée qui réfléchit le signal.
- On peut **retirer un poste** en débranchant son T **de la carte** : le bus reste fermé. Si on
  **sépare les câbles du T**, on ouvre le bus et tout le segment tombe.
- Mise à la terre en **un seul point** : deux points de terre créent une **boucle de masse**
  (courants parasites dans le blindage).
- Pour aller plus loin que {THIN_SEGMENT_MAX_M} m ou {THIN_STATIONS_MAX} postes, on reliait
  plusieurs segments par des **répéteurs** (règle dite « 5-4-3 » : au plus 5 segments,
  4 répéteurs, 3 segments peuplés entre deux postes).

## 6. Ethernet épais : 10BASE5 (*thick Ethernet*)

| Caractéristique | Valeur |
|---|---|
| Débit, topologie | 10 Mb/s, **bus** |
| Câble | coaxial **épais 50 Ω**, ≈ 10 mm, raide (souvent jaune) |
| Longueur d'un segment | **{THICK_SEGMENT_MAX_M} m au plus** |
| Raccordement | **prise vampire** (*vampire tap*) percée à travers la gaine et le blindage jusqu'à l'âme, sur un **transceiver** (MAU) posé sur le câble |
| Vers la station | **câble AUI** (connecteur 15 broches), **{AUI_MAX_M} m au plus** |
| Transceivers | **{THICK_TRANSCEIVERS_MAX} au plus**, posés sur les **repères tous les {fr(THICK_TAP_SPACING_M)} m** imprimés sur la gaine |
| Extrémités | terminateurs **50 Ω** sur connecteurs **N** |

**10BASE5 n'est pas du 10BASE2 en plus gros** : pas de BNC, pas de T sur la carte. Le câble
reste **d'un seul tenant** et la station est reliée par transceiver et câble AUI. Les deux
partagent seulement le principe du **bus 50 Ω terminé aux deux bouts**.

## 7. Liaisons vidéo et RF 75 Ω : la forme ne fait pas le protocole

{_fig(COMPARISON_FIGURE)}

- **10BASE2** : **50 Ω**, RG-58, BNC 50 Ω + T + terminateurs 50 Ω ; **bus** de plusieurs
  postes ; **deux terminateurs 50 Ω**.
- **10BASE5** : **50 Ω**, coaxial épais, connecteurs N + prise vampire + câble AUI ; **bus** de
  plusieurs stations ; **deux terminateurs 50 Ω**.
- **Vidéo (analogique, SDI)** : **75 Ω**, RG-59 (ou câble vidéo numérique), BNC 75 Ω ;
  **point à point** (une source, un récepteur) ; l'entrée du récepteur fait 75 Ω.

En **télévision** et **satellite**, on rencontre du **RG-6 75 Ω** avec des **fiches F** (à
visser) ou la fiche d'antenne TV, pas des BNC. En **radio**, le 50 Ω domine (BNC, N, PL-259…).

**La forme d'un connecteur ne suffit pas** à savoir ce qui circule dans le câble ni son
impédance : un BNC peut porter de l'Ethernet 10BASE2 (50 Ω), de la vidéo SDI (75 Ω), un signal
de mesure… On identifie la liaison par **les équipements**, **le marquage du câble** et **la
documentation**.
"""


def _fabrication() -> str:
    return f"""## 8.1 Avant de commencer

1. **Choisir le matériel cohérent** : câble de la bonne impédance (lire la gaine),
   connecteur **de la même impédance** et **prévu pour ce câble** (référence, notice).
2. **Sécurité** : travailler sur un câble **non raccordé** ; sur un réseau en service, prévenir
   les utilisateurs (ouvrir un bus coupe tout le segment) ; sur une installation TV ou satellite,
   débrancher (un récepteur satellite peut alimenter la tête de la parabole par le câble).
   Lames et dénudeur : gestes maîtrisés ; ramasser les chutes de tresse.
3. **Lire la notice** du connecteur : elle donne les **cotes de dénudage** et l'outil.

## 8.2 Préparer le câble : les cotes viennent de la notice

{_fig(STRIP_FIGURE)}

Le câble est dénudé **en gradins** : la gaine est retirée sur une longueur A, la tresse reste
apparente sur B, l'âme est nue sur C. **Ces cotes dépendent du modèle de connecteur** : on les
lit dans la notice et on règle le dénudeur en conséquence. Il n'existe **pas de cotes
universelles** à apprendre par cœur.

## 8.3 Monter un BNC à sertir

{_fig(CRIMP_FIGURE)}

Points de détail :

- **Manchon et bague d'abord** : une fois le connecteur monté, impossible de les enfiler.
- **Coupe franche**, puis dénudage **sans entailler** l'âme (elle casserait) ni couper la
  tresse.
- **Contact central** : l'âme entre jusqu'en butée, puis on sertit le contact avec la matrice
  prévue (ou on le soude, selon le modèle). Il doit être **à la bonne hauteur** dans le corps :
  ni en retrait (mauvais contact), ni trop sorti.
- **Corps** : on le pousse jusqu'à ce que le contact s'enclenche ; la tresse s'étale sur le fût
  arrière ; **aucun brin** ne doit toucher l'âme ou le contact central (court-circuit).
- **Bague** ramenée sur la tresse et **sertie** : elle ne doit plus tourner.
- Pour un connecteur **à compression** : même préparation, puis l'outil de compression adapté.

## 8.4 Contrôler la liaison réalisée

{_fig(CRIMP_CHECK_FIGURE)}

1. **Contrôle visuel** : hauteur du contact central, pas de brin libre, diélectrique intact.
2. **Contrôle mécanique** : la bague ne tourne pas, le câble résiste à une traction ferme.
3. **Continuité** (multimètre, câble **non raccordé**) : âme ↔ âme et blindage ↔ blindage
   d'un bout à l'autre : quelques ohms au plus.
4. **Absence de court-circuit** : entre l'âme et le blindage, résistance **infinie**.
5. **Adaptation d'impédance** : câble, connecteurs et terminaisons de la **même** impédance
   (marquages) ; sur un bus 10BASE2 refermé et arrêté, **≈ 25 Ω** entre âme et blindage.
6. **Test en service** : communication des postes ou image correcte ; noter le résultat.

## 9. Les outils

| Outil | Usage |
|---|---|
| **Coupe-câble** | coupe franche du câble, sans l'écraser |
| **Dénudeur coaxial calibré** | lames réglées aux cotes de la notice, dénudage en gradins sans entailler |
| **Pince à sertir** avec **matrice adaptée** (ou outil de compression) | sertir contact et bague du modèle choisi |
| **Testeur de continuité / multimètre** | continuité âme et blindage, absence de court-circuit, ≈ 25 Ω sur un bus 10BASE2 — **toujours réseau arrêté, câble hors tension** |
| **Testeur de câble coaxial** | continuité et court-circuit d'un cordon, avec bouchon distant |
| **Réflectomètre (TDR)** et mesures spécialisées | localiser une coupure, un court-circuit ou un écrasement, à distance (section 11) |
"""


def _schemas() -> str:
    figures = "".join(_fig(f) for f in BUS_FAULT_FIGURES)
    return f"""## 10. Lire et corriger un schéma de bus coaxial

Pour relire un schéma 10BASE2, on vérifie **dans cet ordre** :

1. **Topologie** : un seul câble, de T en T ; pas d'étoile, pas de branche.
2. **Raccordement des postes** : chaque T **directement** sur la carte.
3. **Extrémités** : un terminateur **50 Ω** à **chaque** bout.
4. **Impédance** : tous les tronçons en **50 Ω** (RG-58), tous les connecteurs 50 Ω.
5. **Limites** : longueur totale ≤ {THIN_SEGMENT_MAX_M} m, ≤ {THIN_STATIONS_MAX} postes,
   ≥ {fr(THIN_MIN_SPACING_M)} m entre deux T.
6. **Terre** : un seul point.
7. **État** : câble ouvert, court-circuit, connecteur mal serti, câble écrasé signalés.

Les quatre schémas ci-dessous sont **volontairement faux** ; la liste des non-conformités sous
chacun est calculée automatiquement à partir des mêmes règles.

{figures}

**Corrections :** 1) ajouter un terminateur 50 Ω sur le T du Serveur ; 2) brancher le T
directement sur la carte du PC-2 et ne garder qu'un point de terre ; 3) remplacer le tronçon
RG-59 par du RG-58 50 Ω et le terminateur 75 Ω par un 50 Ω ; 4) réparer ou remplacer le
tronçon coupé (deux BNC 50 Ω et un raccord, ou un tronçon neuf), puis contrôler.
"""


def _diagnosis() -> str:
    readings = "\n".join(f"| {situation} | {reading_text(value)} | {meaning} |" for situation, value, meaning in READINGS)
    open_distance = fr(tdr_distance_m(TDR_OPEN_NS, TDR_VF))
    return f"""## 11.1 Symptômes typiques

| Symptôme | Causes à envisager |
|---|---|
| **Perte totale** (aucun poste ne communique) | terminateur manquant, câble coupé, câbles séparés d'un T, court-circuit, terminateur de mauvaise valeur |
| **Signal intermittent** (coupures quand on bouge) | connecteur desserré ou mal serti, tresse mal serrée, câble abîmé près d'un connecteur |
| **Erreurs, collisions, image dégradée** (réflexions) | tronçon de mauvaise impédance, câble écrasé, branche non terminée, BNC 75/50 Ω mélangés en vidéo |
| **Un seul poste isolé** | T ou carte du poste, réglage de la carte, câble AUI ou transceiver (10BASE5) |
| **Parasites, ronflements** | blindage rompu, deux points de terre (boucle de masse), câble près de câbles d'énergie |

## 11.2 Démarche : tests non destructifs d'abord

**Étape 1 — Observer.** Depuis quand, quels postes, après quel événement (déménagement, travaux,
nettoyage) ; parcourir le câble à la recherche d'un connecteur desserré, d'un câble écrasé,
d'un T dont on a séparé les câbles.

**Étape 2 — Mesurer réseau arrêté** (utilisateurs prévenus), à l'ohmmètre entre âme et blindage
au T d'un poste.

{_fig(READINGS_FIGURE)}

| Situation | Lecture | Conclusion |
|---|---|---|
{readings}

Sur un long segment, la résistance du câble s'ajoute : on lit un peu plus de 25 Ω. **Le câble
écrasé ou le connecteur mal serti ne se voient généralement pas** à l'ohmmètre : on mesure aussi
en **manipulant** le câble (une lecture qui saute = contact intermittent).

**Étape 3 — Localiser.**

- Par **moitiés** (dichotomie) : ouvrir le bus vers le milieu, mesurer chaque moitié, garder
  celle qui contient le défaut, recommencer.
- Au **réflectomètre (TDR)** : il envoie une impulsion et mesure le temps de retour de l'écho.
  Une réflexion **de même sens** = impédance plus élevée (jusqu'au **circuit ouvert**) ; une
  réflexion **inversée** = impédance plus faible (jusqu'au **court-circuit**). Distance :
  **d = facteur de vélocité × c × t ÷ 2** (l'impulsion fait l'aller-retour).

{"".join(_fig(f) for f in TDR_FIGURES)}

Exemple de calcul : réflexion positive à {TDR_OPEN_NS} ns, facteur de vélocité {fr(TDR_VF, 2)}
(lu sur la fiche du câble) : d = {fr(TDR_VF, 2)} × 0,2998 m/ns × {TDR_OPEN_NS} ns ÷ 2 ≈
**{open_distance} m**.

**Étape 4 — Réparer.** Remettre le terminateur 50 Ω, refaire le connecteur, remplacer le tronçon
abîmé (ou couper de part et d'autre, deux BNC et un raccord droit 50 Ω), revisser les câbles sur
le T.

**Étape 5 — Vérifier.** ≈ 25 Ω réseau arrêté, plus de réflexion au TDR si disponible,
communication de **tous** les postes, mesure stable en manipulant le câble.
"""


def _safety() -> str:
    return """## 12.1 Sécurité et bonnes pratiques

- **Hors tension quand c'est nécessaire** : mesures à l'ohmmètre **réseau arrêté**, câble non
  raccordé pour fabriquer ou contrôler un cordon ; en TV/satellite, débrancher le récepteur
  (tension d'alimentation de la tête de réception sur le câble).
- **Prévenir avant d'ouvrir un bus** : sur un 10BASE2, débrancher un câble d'un T coupe tout le
  segment ; faire enregistrer le travail des utilisateurs, intervenir à un moment convenu.
- **Ménager connecteurs et câbles** : verrouiller la baïonnette sans forcer, ne pas tirer sur le
  câble pour débrancher, ne pas plier ni écraser, protéger les passages (goulotte,
  passe-câble), éloigner des câbles d'énergie.
- **Un seul point de terre** sur un bus coaxial ; ne pas improviser une mise à la terre.
- **Matériel cohérent** : câble, connecteurs, terminateurs et équipements de même impédance ;
  rechange étiquetée (terminateurs 50 Ω, T, raccords).
- **Caractère historique** : un réseau Ethernet coaxial existant se dépanne, mais on conseille
  au client sa **migration** vers un câblage à paires torsadées et un switch.

## 12.2 Le rapport d'intervention

| Rubrique | Contenu attendu |
|---|---|
| **Demande** | ce qui était demandé ou constaté (réseau en panne, poste à ajouter, liaison vidéo à créer) |
| **Constats** | symptômes, postes touchés, événement déclencheur, observations du câble |
| **Hypothèses** | causes possibles, de la plus probable à la moins probable |
| **Tests et résultats** | mesures (ohmmètre réseau arrêté, réflectomètre), avec les valeurs lues |
| **Cause retenue** | ce que les tests prouvent (ou « non déterminée ») |
| **Action** | ce qui a été remplacé ou refait, matériel utilisé (impédance, référence) |
| **Validation** | mesures après réparation, communication ou image vérifiée avec l'utilisateur |
| **Recommandation** | prévention, rechange, migration éventuelle |

**Ce qu'on attend d'une réponse écrite à l'épreuve** : des **étapes ordonnées**, les **valeurs**
quand elles comptent (50 Ω, 75 Ω, 185 m, deux terminateurs…), la **justification** de chaque
choix, le **test** qui prouve le résultat et la **sécurité**.
"""


def _examples() -> str:
    good = reading_text(READINGS[0][1])
    missing = reading_text(READINGS[1][1])
    return f"""Chaque exemple suit la même démarche : besoin ou symptôme, choix justifiés, réalisation
ou lecture des preuves, contrôle et compte rendu. Supports fictifs ; valeurs et règles vérifiées.

<h3 class="jc-example-title">Exemple 1 — Réaliser une liaison 10BASE2</h3>

**Besoin.** Relier trois PC anciens d'un atelier de démonstration (cartes à prise BNC), distants
de 6 m et 9 m.

**Choix justifiés.** Bus 10BASE2 : RG-58 **50 Ω** ; trois **T BNC 50 Ω** branchés directement
sur les cartes ; **deux terminateurs 50 Ω** ; longueur totale 15 m (≤ {THIN_SEGMENT_MAX_M} m),
3 postes (≤ {THIN_STATIONS_MAX}), écarts ≥ {fr(THIN_MIN_SPACING_M)} m.

**Réalisation.**

1. Fabriquer deux cordons RG-58 de 6 m et 9 m, BNC mâles 50 Ω à sertir à chaque bout (section 8).
2. Contrôler chaque cordon : continuité âme et blindage, résistance infinie entre âme et blindage.
3. T sur chaque carte ; PC 1 → 6 m → PC 2 → 9 m → PC 3.
4. Terminateur 50 Ω sur la sortie libre du T du PC 1 (relié à la terre si l'installation le
   prévoit) et du PC 3 (sans terre).

**Contrôle.** Réseau arrêté, au T du PC 2 : **{good}** (deux 50 Ω en parallèle). Puis
communication entre les trois postes.

**Compte rendu.** « Bus 10BASE2 de 3 postes, 15 m de RG-58 50 Ω, T sur les cartes, deux
terminateurs 50 Ω, une terre. Cordons testés ; {good} au T du PC 2 ; échanges vérifiés. »

<h3 class="jc-example-title">Exemple 2 — Diagnostiquer un terminateur absent</h3>

**Symptôme.** Dans un bureau, les quatre postes du segment 10BASE2 ne communiquent plus depuis
qu'un meuble a été déplacé.

**Mesure.** Réseau arrêté, utilisateurs prévenus, au T du premier poste : **{missing}** au lieu
de {good}. Un seul terminateur est vu : terminateur absent **ou** coupure.

**Recherche.** Au bout du segment, le T du dernier poste a une sortie libre : le terminateur est
tombé derrière le meuble (schéma fautif 1).

**Correction.** Revisser un terminateur 50 Ω (vérifier sa valeur marquée, ou le mesurer seul :
50 Ω).

**Contrôle.** {good} au T du premier poste, communication des quatre postes rétablie.

**Compte rendu.** « Réseau 10BASE2 en panne : {missing} au lieu de {good} ; terminateur 50 Ω
absent à l'extrémité du dernier poste. Terminateur remis ; {good} ; réseau rétabli. »

<h3 class="jc-example-title">Exemple 3 — Détecter une mauvaise impédance</h3>

**Symptôme.** Après une « réparation », un segment 10BASE2 de trois postes fonctionne mal :
erreurs et collisions nombreuses, sans coupure totale.

**Lecture des preuves.** Le marquage du tronçon ajouté indique « RG-59 75 Ω » ; le terminateur
neuf porte « 75 Ω » (schéma fautif 3). Au T du premier poste : 50 Ω ∥ 75 Ω = **30 Ω** au lieu de
25 Ω.

**Raisonnement.** Le bus est prévu pour 50 Ω. Au passage 50 → 75 Ω, Γ = (75 − 50) / (75 + 50) =
**{_gamma(75)}** : 20 % de l'amplitude est renvoyée, au tronçon et au terminateur. Les échos
corrompent les trames, d'où les erreurs.

**Correction.** Tronçon en RG-58 50 Ω avec BNC 50 Ω ; terminateur 50 Ω.

**Contrôle.** 25 Ω, réseau arrêté ; échanges sans erreur.

**Compte rendu.** « Tronçon RG-59 75 Ω et terminateur 75 Ω sur un bus 50 Ω : réflexions.
Remplacés par du RG-58 50 Ω et un terminateur 50 Ω ; 25 Ω ; erreurs disparues. »

<h3 class="jc-example-title">Exemple 4 — Vérifier un connecteur mal serti</h3>

**Symptôme.** Un poste perd le réseau quand on touche le câble derrière lui ; au repos, l'ohmmètre
lit {good} (réseau arrêté).

**Contrôle du connecteur.** Bague qui tourne autour du câble, câble qui recule à la traction,
contact central en retrait. En tordant le câble, la lecture saute de 25 Ω à 50 Ω.

**Conclusion.** Connecteur **mal serti** : contact intermittent du blindage et du contact
central. La mesure statique ne le révélait pas.

**Correction.** Couper le connecteur ; en monter un neuf 50 Ω, prévu pour le RG-58, selon la
notice et avec la bonne matrice ; contrôle visuel et traction.

**Contrôle.** Lecture stable à 25 Ω en manipulant le câble ; plus de coupures.

**Compte rendu.** « Coupures intermittentes : BNC mal serti (bague libre, contact en retrait).
Connecteur refait ; mesure stable à 25 Ω en manipulation ; câble fixé pour éviter les efforts. »
"""


def _pitfalls() -> str:
    return """> **Dire que tous les BNC sont à 50 Ω.** Il existe des BNC 50 Ω et 75 Ω qui s'emboîtent :
> on lit le marquage.

> **Choisir un câble « à l'œil ».** RG-58 (50 Ω) et RG-59 (75 Ω) se ressemblent : on lit la gaine.

> **Croire qu'un ohmmètre mesure l'impédance d'un câble.** Il lit l'infini entre âme et blindage
> d'un câble seul ; l'impédance caractéristique est une propriété de la géométrie.

> **Câbler un 10BASE2 en étoile** avec un T « comme un switch » : chaque branche est une
> extrémité non terminée.

> **Mettre un câble entre le T et la carte** : dérivation non terminée, réflexions.

> **Oublier un terminateur**, ou mettre un terminateur 75 Ω sur un bus 50 Ω : tout le segment
> est perturbé.

> **Séparer les câbles d'un T** pour déplacer un poste : on ouvre le bus pour tout le monde.
> On débranche le T de la carte.

> **Mettre le blindage à la terre aux deux bouts** : boucle de masse.

> **Confondre 10BASE5 et 10BASE2** : l'épais n'a ni BNC ni T, il se raccorde par prise vampire,
> transceiver et câble AUI.

> **Apprendre des cotes de dénudage « universelles »** : elles dépendent du connecteur, on lit la
> notice.

> **Enfiler la bague après avoir monté le contact** : impossible, tout est à refaire.

> **Mesurer sur un réseau en service** ou conclure « câble bon » sur une seule mesure statique :
> un connecteur mal serti ou un câble écrasé ne se voient qu'en manipulant ou au réflectomètre.
"""


def _exercises_intro() -> str:
    return f"""{len(PRACTICE_ITEMS)} exercices corrigés : cinq interprétations ou corrections de schémas,
quatre choix d'impédance et de connecteurs, trois procédures de fabrication écrites (dont une
remise en ordre) et quatre diagnostics d'installation. Rédige ta réponse sur papier **avant**
d'ouvrir le corrigé. Ces mêmes exercices sont proposés dans
[S'entraîner](/uaa/{PR16_SLUG}/practice), avec correction après envoi.

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
    return f"""Le mini-examen se passe dans l'onglet [Examen blanc](/uaa/{PR16_SLUG}/exam) : **10 questions à réponse
libre**, chacune notée sur **2 points**, soit une note sur **{EXAM_TOTAL_POINTS}**. Les
questions ne figurent pas dans ce cours.

| N° | Thème | Type | Points |
|---|---|---|---|
{rows}

**Déroulement.** Toutes les informations nécessaires sont dans chaque question et ses
documents (relevés, schémas décrits, mesures fictives). **Aucune correction n'est visible
pendant la passation** ; tes réponses sont enregistrées au fur et à mesure. Après l'envoi,
chaque réponse est corrigée selon le **barème détaillé** de la question, puis tu vois ta note
sur {EXAM_TOTAL_POINTS}, le corrigé et le barème.

**Ce que valorise le barème.** L'**exactitude** (impédances, terminaisons, longueurs, lecture
des mesures), le **raisonnement** (pourquoi ce choix, pourquoi ce défaut), la **procédure**
ordonnée, la **sécurité** et le **contrôle** final — pas la récitation de sigles. Une réponse
techniquement juste formulée autrement est acceptée.

**Nature de la correction.** Les réponses rédigées reçoivent une **proposition de correction
automatique** (assistée par IA) appuyée sur le barème : c'est un repère d'entraînement, pas une
note officielle ; en cas de doute, compare ta réponse au corrigé. Une impédance fausse ou un bus
mal terminé est toujours pénalisé, même bien rédigé.
"""


def _memo() -> str:
    return f"""- **Coaxial** : âme, diélectrique, blindage (feuille et/ou tresse), gaine ; blindage
  efficace s'il est continu.
- **Impédance caractéristique** : géométrie + isolant, **pas la longueur** ; ne se mesure pas à
  l'ohmmètre.
- **50 Ω** : 10BASE2, 10BASE5, radio. **75 Ω** : vidéo (SDI, vidéosurveillance), TV, satellite.
  **BNC 50 Ω et 75 Ω existent** et s'emboîtent : lire le marquage.
- **Câble = connecteur = terminaison = équipement** (même impédance). Sinon réflexion :
  Γ = (Zc − Z0)/(Zc + Z0) ; ouvert +1, court-circuit −1, adapté 0, 75 sur 50 : {_gamma(75)}.
- **10BASE2** : bus, 10 Mb/s, RG-58 50 Ω, **{THIN_SEGMENT_MAX_M} m**, **{THIN_STATIONS_MAX}
  postes**, **{fr(THIN_MIN_SPACING_M)} m** entre T, **T sur la carte**, **deux terminateurs 50 Ω**,
  **une seule terre**.
- **10BASE5** : coax épais 50 Ω, **{THICK_SEGMENT_MAX_M} m**, prise vampire + transceiver,
  AUI ≤ {AUI_MAX_M} m, {THICK_TRANSCEIVERS_MAX} transceivers, repères tous les
  {fr(THICK_TAP_SPACING_M)} m, connecteurs N.
- **Fabrication** : matériel cohérent, notice ; manchon + bague d'abord ; dénuder aux **cotes de
  la notice** ; contact serti ; corps ; bague sertie ; contrôles.
- **Contrôles** : visuel, traction, continuité âme et blindage, âme/blindage infini ; bus
  refermé : **≈ 25 Ω** (réseau arrêté).
- **Lectures** : 25 Ω normal ; 50 Ω un terminateur vu (absent ou coupure) ; 0 Ω court-circuit ;
  OL bus ouvert ; 30 / 37,5 Ω terminateur faux.
- **TDR** : réflexion de même sens = ouvert, inversée = court-circuit ; d = VF × c × t ÷ 2.
- **Rapport** : demande, constats, hypothèses, tests et valeurs, cause, action, validation,
  recommandation (migration).
"""


def _sources() -> str:
    return """## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), pp. 3, 5 et 6 : épreuve uniquement écrite, exigences AP-18,
  AP-20 et AP-35. Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
- **10BASE2 et 10BASE5** (50 Ω, 10 Mb/s, 185 m / 30 postes / 0,5 m, T directement sur la carte,
  terminateurs 50 Ω aux deux extrémités, terre en un point ; 500 m / 100 transceivers / repères
  de 2,5 m, prise vampire, AUI, connecteurs N) : norme IEEE 802.3, clauses 8 (10BASE5) et 10
  (10BASE2), retirées pour les nouvelles installations en 2011 ; valeurs recoupées sur la
  documentation technique publiée (articles « 10BASE2 » et « 10BASE5 » de Wikipédia, qui citent
  ces clauses).
- **Connecteur BNC** (baïonnette quart de tour, variantes 50 Ω et 75 Ω qui s'accouplent sans
  dommage selon IEC 61169-8, effet négligeable de la désadaptation sous ≈ 10 MHz, usages vidéo,
  SDI, RF, réseaux historiques) : norme IEC 61169-8 et documentation technique publiée (article
  « BNC connector »).
- **Coefficient de réflexion, réflectométrie (TDR)** : théorie des lignes de transmission
  (formule Γ = (Zc − Z0)/(Zc + Z0), d = v × t ÷ 2) ; facteur de vélocité : fiche du câble.

Les non-conformités des schémas, les lectures d'ohmmètre et les distances sont **calculées** à
partir d'un modèle de bus et **vérifiées par des tests automatiques** ; aucun schéma n'est tiré
d'une image générée.

## Compléments pédagogiques (non imposés par la liste officielle)

La liste des pp. 5-6 demande la description de la réalisation d'un câble à connecteurs BNC
(AP-35), les types de câbles dont le coaxial (AP-18) et leurs caractéristiques, dont l'impédance
(AP-20). Sont des **compléments**, signalés comme tels :

- la rédaction de la procédure et du compte rendu (AP-C01, approfondie en PR29) ;
- le coefficient de réflexion, le réflectomètre (TDR) et le facteur de vélocité ;
- les liaisons vidéo, TV et radio (SDI, fiches F), le 10BASE5 et la règle 5-4-3, utiles pour ne
  pas confondre les usages du coaxial ;
- la topologie en bus (AP-23, développée en PR19) et l'installation physique (AP-36, PR18).

## Supports fictifs

Les cas, relevés, mesures, traces de réflectomètre et extraits de catalogue de ce cours sont
**fictifs** et reconstitués pour l'entraînement ; la présentation réelle varie selon les
appareils. Aucun n'est une question officielle ou déjà posée par le Jury.
"""


def pr16_course_sections() -> list[tuple[str, str]]:
    """Blocs du cours (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("PR16 — Objectifs et place dans l'épreuve", _objectives()),
        ("PR16 — 1. Structure du câble coaxial, rôle et familles RG", _structure()),
        ("PR16 — 2-3. Impédance caractéristique, adaptation et réflexions du signal", _impedance()),
        ("PR16 — 4. Connecteurs BNC, T, terminateurs et variantes", _bnc()),
        ("PR16 — 5-7. Ethernet coaxial 10BASE2, 10BASE5 et liaisons vidéo 75 Ω", _ethernet()),
        ("PR16 — 8-9. Fabriquer une liaison BNC : procédure, contrôles et outils", _fabrication()),
        ("PR16 — 10. Lire et corriger un schéma de bus coaxial", _schemas()),
        ("PR16 — 11. Diagnostic : symptômes, mesures, localisation, réparation", _diagnosis()),
        ("PR16 — 12. Sécurité, bonnes pratiques et rapport d'intervention", _safety()),
        ("PR16 — Exemples : quatre cas intégralement corrigés", _examples()),
        ("PR16 — Pièges et erreurs fréquentes", _pitfalls()),
        (f"PR16 — Exercices corrigés ({len(PRACTICE_ITEMS)}) et leurs corrigés", _exercises_intro()),
        ("PR16 — Mini-examen noté sur 20 : mode d'emploi", _mini_exam()),
        ("PR16 — Fiche mémo", _memo()),
        ("PR16 — Sources et compléments pédagogiques", _sources()),
    ]
