"""Cours PR02 « Alimentation, connectique, compatibilité et sécurité » — parcours AMPCR pratique
écrite (ticket #203).

Matière : intégralement celle du ticket #203 (courant alternatif et continu, bloc
d'alimentation : puissance, rails, rendement, connecteurs ATX 24, EPS 4+4, PCIe 6/8 et
12V-2x6, SATA, Molex ; budget de puissance et marges ; ventilateurs et refroidissement ;
protections ; sécurité électrique, mise hors tension, ESD, batteries gonflées, interdiction
d'ouvrir un bloc, outils ; USB, HDMI, DisplayPort ; SATA, PCIe, M.2 SATA/NVMe ; DDR, socket,
facteurs de forme ; dossiers pratiques de compatibilité, mauvais branchements, remplacement
sûr et symptômes d'alimentation), découpée en blocs titrés (le titre pilote le type de carte,
`app.card_kind` : aucun titre de bloc théorique ne contient « examen », « source »,
« exemple », « exercice », « méthode », « piège », « attention » ni « mémo »). Données et
schémas : `app.v1.ampcr_pratique_pr02_figures` ; exercices et mini-examen :
`app.v1.ampcr_pratique_pr02_bank`. Mise en forme partagée avec les autres cours pratiques.
"""

from html import escape

from app.v1.ampcr_pratique_pr01_figures import USB_SPEEDS, fr_number
from app.v1.ampcr_pratique_pr02_bank import EXAM_ITEMS, EXAM_TOTAL_POINTS, PRACTICE_ITEMS
from app.v1.ampcr_pratique_pr02_figures import (
    AIRFLOW_FIGURE,
    ATX24_FIGURE,
    BUDGET_FIGURE,
    CASE1_CONFIG,
    CASE2_GPU_RECOMMENDATION,
    CASE2_LOADS,
    CASE2_MARGIN_ONLY,
    CASE2_RECOMMENDED,
    CASE2_TOTAL,
    CASE4_MEASURES,
    CHAIN_FIGURE,
    DEFAULT_MARGIN,
    EFFICIENCY_LEVELS,
    EPS8_FIGURE,
    HPWR_MAX_WATTS,
    M2_KEYS,
    MAINS_FREQUENCY,
    MAINS_VOLTAGE,
    PCIE6_WATTS,
    PCIE8_WATTS,
    PCIE_SLOT_WATTS,
    POWER_CONNECTORS,
    PSU_FORMS,
    RAILS,
    RAILS_BY_NAME,
    SAFE_FIGURE,
    SATA_MOLEX_FIGURE,
    SYMPTOM_FIGURE,
    USB_POWER,
    VIDEO_STANDARDS,
    check_configuration,
    current_12v,
    gpu_power_capacity,
    losses,
    measure_lines,
    tolerance_range,
    volts,
    wall_power,
    within_tolerance,
)
from app.v1.ampcr_pratique_pr06_course import _exercise_card, _fig, _req

PR02_TITLE = "Alimentation, connectique, compatibilité et sécurité"
PR02_SLUG = "ampcr-pratique-pr02"


def _exercises_html() -> str:
    return "\n\n".join(
        _exercise_card(i, item, anchor_prefix="pr02") for i, item in enumerate(PRACTICE_ITEMS, start=1)
    )


def _console(*lines: str) -> str:
    return f'<pre class="jc-pr-console" tabindex="0">{escape(chr(10).join(lines))}</pre>'


def _usb(gbits: float) -> str:
    return f"{int(gbits * 1000)} Mbit/s" if gbits < 1 else f"{gbits:g} Gbit/s"


# --- Tableaux de données (générés depuis les données vérifiées) ------------------------------


def _rails_table() -> str:
    rows = []
    for rail in RAILS:
        low, high = tolerance_range(rail)
        rows.append(
            f"| {rail.name} | {rail.color} | ±{rail.tolerance_pct} % | {volts(low)} à {volts(high)} | {rail.uses} |"
        )
    return (
        "| Sortie | Fil | Tolérance | Plage admise | Ce qu'elle alimente |\n|---|---|---|---|---|\n"
        + "\n".join(rows)
    )


def _connectors_table() -> str:
    rows = "\n".join(
        f"| {name} | {pins} | {voltages} | {power} | {dest} |" for name, pins, voltages, power, dest in POWER_CONNECTORS
    )
    return (
        "| Connecteur | Broches | Tensions | Puissance de référence | Alimente |\n|---|---|---|---|---|\n" + rows
    )


def _efficiency_table() -> str:
    rows = "\n".join(f"| {name} | {a} % | {b} % | {c} % |" for name, a, b, c in EFFICIENCY_LEVELS)
    return "| Niveau 80 PLUS | 20 % de charge | 50 % | 100 % |\n|---|---|---|---|\n" + rows


def _psu_forms_table() -> str:
    rows = "\n".join(f"| {name} | {dims} | {use} |" for name, dims, use in PSU_FORMS)
    return "| Format de bloc | Dimensions | Usage |\n|---|---|---|\n" + rows


def _budget_table() -> str:
    rows = "\n".join(
        f"| {load.name} | {load.watts} W | {'oui' if load.on_12v else 'non'} |" for load in CASE2_LOADS
    )
    return "| Composant (fiche fictive) | Puissance maximale | Surtout sur le +12 V |\n|---|---|---|\n" + rows


def _video_table() -> str:
    rows = "\n".join(f"| {name} | {fr_number(rate, 1)} Gbit/s | {example} |" for name, rate, example in VIDEO_STANDARDS)
    return "| Norme | Débit maximal du lien | Exemple de ce qu'elle permet |\n|---|---|---|\n" + rows


def _usb_table() -> str:
    rows = "\n".join(f"| {name} | {old} | {_usb(speed)} | {conn} |" for name, old, speed, conn in USB_SPEEDS)
    return "| Norme | Ancien nom courant | Débit maximal | Connecteurs |\n|---|---|---|---|\n" + rows


def _usb_power_table() -> str:
    rows = "\n".join(f"| {case} | {u} | {i} | {fr_number(p, 1).replace(',0', '')} W |" for case, u, i, p in USB_POWER)
    return "| Cas | Tension | Courant | Puissance |\n|---|---|---|---|\n" + rows


def _m2_table() -> str:
    rows = "\n".join(f"| {key} | {meaning} | {where} |" for key, meaning, where in M2_KEYS)
    return "| Clé du module | Ce qu'elle indique en général | Où elle entre |\n|---|---|---|\n" + rows


def _check_table(config) -> str:
    rows = "\n".join(
        f"| {label} | {'conforme' if ok else '**non conforme**'} | {why} |" for label, ok, why in check_configuration(config)
    )
    return "| Critère | Verdict | Valeurs relevées |\n|---|---|---|\n" + rows


def _measures_table() -> str:
    rows = []
    for name, idle, load in CASE4_MEASURES:
        rail = RAILS_BY_NAME[name]
        low, high = tolerance_range(rail)
        verdict = "conforme" if within_tolerance(rail, load) else "**hors tolérance**"
        rows.append(f"| {name} | {volts(low)} à {volts(high)} | {volts(idle)} | {volts(load)} | {verdict} |")
    return "| Sortie | Plage admise | À vide | En charge | Verdict en charge |\n|---|---|---|---|---|\n" + "\n".join(rows)


# =============================================================================================
# Sections du cours (titre du bloc, Markdown / HTML)
# =============================================================================================


def _objectives() -> str:
    return f"""## Ce que tu sauras faire, par écrit

L'épreuve pratique AMPCR se passe **uniquement par écrit** (consignes officielles 2026-2027/1,
p. 3). Pour l'alimentation et la connectique, on te remet une fiche, une étiquette de bloc, un
relevé de mesures, un devis ou la description d'un montage, et tu dois, sur papier :

1. **identifier** les connecteurs d'alimentation et de données et dire **ce qu'ils alimentent
   ou relient** ;
2. **lire les caractéristiques d'un bloc** (puissance, +12 V, rendement) et **calculer** un
   budget de puissance avec sa marge ;
3. **déterminer la compatibilité** d'une configuration, critère par critère, avec les valeurs ;
4. **repérer un mauvais branchement** et dire comment le corriger ;
5. **évaluer des symptômes d'alimentation** et proposer des tests ;
6. **rédiger une procédure de remplacement sûre** (mise hors tension, ESD, contrôles).

## Exigences officielles travaillées dans ce cours

{_req("AP-04")}
{_req("AP-06")}
{_req("AP-17")}

Complément pédagogique (hors liste officielle des pp. 5-6, signalé comme tel) :

{_req("AP-C02")}

L'identification des composants est traitée en [PR01](/uaa/ampcr-pratique-pr01) ; la démarche
complète de diagnostic des pannes en [PR06](/uaa/ampcr-pratique-pr06). Le montage pas à pas
sera détaillé en PR03.

## Lien avec la théorie

Les notions de base sont présentées dans la théorie AMPCR :
[MC02 Carte mère, formats, bus et connectiques](/uaa/ampcr-mc02),
[MC03 Processeur et mémoire RAM](/uaa/ampcr-mc03), [MC04 Stockage](/uaa/ampcr-mc04) et
[MC05 Alimentation, refroidissement, ESD et sécurité électrique](/uaa/ampcr-mc05). Ce cours-ci
est **pratique** : étiquettes, relevés, devis, calculs et réponses rédigées, comme dans un
dossier d'examen.

## Comment travailler ce cours

Lis les chapitres dans l'ordre : chacun donne ses **objectifs**, la **théorie**, ce qu'on
attend **à l'écrit** et un **repère rapide**. Étudie ensuite les **quatre cas résolus**, fais
les **{len(PRACTICE_ITEMS)} exercices corrigés** (ici ou dans « S'entraîner », correction après
envoi), puis passe le **mini-examen noté sur {EXAM_TOTAL_POINTS}** dans l'onglet « Examen blanc ».

> **Important —** les fiches produits, étiquettes, devis et relevés de ce cours sont des
> **supports fictifs** construits pour s'entraîner : ils ne décrivent aucun produit réel, et
> seule la fiche du fabricant fait foi pour un vrai matériel. Les valeurs normalisées
> (tolérances ATX, puissances PCIe, seuils 80 PLUS, débits USB, HDMI et DisplayPort) viennent
> des spécifications citées en fin de cours. Aucun exercice n'est une question officielle ni
> une question déjà posée par le Jury.
"""


def _ac_dc() -> str:
    return f"""**Objectifs** : distinguer courant alternatif et continu ; expliquer le rôle du bloc
d'alimentation et de chacune de ses tensions.

## 1.1 Alternatif et continu

- Le **secteur** fournit du **courant alternatif** (AC) : en Belgique, **{MAINS_VOLTAGE} V à
  {MAINS_FREQUENCY} Hz** — la tension change de sens {MAINS_FREQUENCY} fois par seconde.
- Les composants électroniques d'un PC fonctionnent en **courant continu** (DC), à basse
  tension : **+12 V**, **+5 V**, **+3,3 V**.
- Le **bloc d'alimentation** (PSU) fait la conversion : il **redresse** le courant alternatif,
  le **découpe** à haute fréquence dans un transformateur (alimentation à découpage), puis
  **régule** chaque tension de sortie. Les blocs actuels acceptent en général **100 à 240 V**
  automatiquement (PFC actif) ; certains anciens blocs ont un **sélecteur 115/230 V** à vérifier.
- Un **portable** fait la même chose en deux temps : l'**adaptateur secteur** fournit une
  tension continue (souvent 19-20 V, ou par USB-C Power Delivery), puis la carte mère fabrique
  les basses tensions.

{_fig(CHAIN_FIGURE, wide=True)}

## 1.2 Les tensions de sortie

{_rails_table()}

- Le **+12 V** porte l'essentiel de la puissance d'un PC moderne : le processeur (par l'EPS et
  le **VRM**, qui abaisse le +12 V à environ 1 V) et la carte graphique.
- Le **+5 VSB** (*standby*, fil violet) est présent **dès que le câble secteur est branché**,
  même PC éteint : il alimente la veille, le réveil par le réseau et la LED de la carte mère.
  **Éteint n'est pas hors tension.**
- Deux fils de **signal** : **PS_ON#** (vert) — la carte mère le relie à la masse pour allumer le
  bloc quand on appuie sur le bouton ; **PWR_OK** (gris) — le bloc signale que ses tensions sont
  stables, la carte peut démarrer.

**À l'écrit** : « le bloc convertit le 230 V alternatif du secteur en tensions continues
(+12 V, +5 V, +3,3 V) ; le +5 VSB reste présent tant que le PC est branché » — chaque tension
avec son rôle.

**Repère rapide** : AC → bloc → DC ; +12 V = puissance (CPU, GPU) ; +5 VSB = veille, donc
**débrancher** avant d'intervenir.
"""


def _psu_specs() -> str:
    example_wall = wall_power(400, 90)
    return f"""**Objectifs** : lire l'étiquette et la fiche d'un bloc ; comprendre puissance, rails,
rendement et format.

## 2.1 Puissance et étiquette

- La **puissance nominale** (ex. 650 W) est la puissance **maximale continue** que le bloc peut
  **fournir**. Il ne fournit que ce que les composants demandent : un PC qui consomme 200 W
  sur un bloc de 650 W n'utilise que 200 W.
- L'étiquette donne, par sortie, le **courant maximal** (A) et la **puissance maximale** :
  sur le +12 V, **P = U × I** (ex. 12 V × 54 A = {12 * 54} W). Le +3,3 V et le +5 V ont une
  puissance **combinée** (ex. 120 W) : on ne peut pas tirer le maximum des deux en même temps.
- **Ce qui compte pour un PC moderne, c'est le +12 V** : il doit couvrir presque toute la
  puissance du processeur et de la carte graphique.
- **Mono-rail ou multi-rails** : un seul +12 V à fort courant, ou plusieurs +12 V protégés
  chacun ; les deux sont normaux, la fiche l'indique.

## 2.2 Rendement et certification 80 PLUS

Le **rendement** est le rapport entre la puissance **fournie** aux composants et la puissance
**absorbée** au secteur ; le reste est perdu en **chaleur** dans le bloc.

**Puissance absorbée = puissance fournie / rendement.** Exemple : 400 W fournis à 90 % de
rendement → 400 / 0,90 ≈ {fr_number(example_wall, 0)} W absorbés, dont
{fr_number(losses(400, 90), 0)} W de pertes.

{_efficiency_table()}

Seuils minimaux de la certification **80 PLUS** (secteur 115 V, usage interne ; Titanium exige
aussi 90 % à 10 % de charge). Le rendement est **meilleur vers 50 % de charge** : un bloc
énorme pour un petit PC fonctionne dans sa zone la moins efficace. Un meilleur rendement
signifie **moins de consommation, moins de chaleur, moins de bruit** — pas plus de puissance.

## 2.3 Format, câbles et qualité

{_psu_forms_table()}

- **Câbles fixes, semi-modulaires ou modulaires** : un bloc modulaire permet de ne brancher que
  les câbles utiles. **Les câbles modulaires ne sont pas normalisés côté bloc** : on n'utilise
  **que** ceux livrés avec le bloc installé.
- **ATX 3.x** : norme récente qui tolère mieux les pics de consommation des cartes graphiques et
  fournit en natif le connecteur **12V-2x6**.
- Un bloc de qualité indique ses **protections** (chapitre 6), sa **garantie** et ses
  **certifications** ; une puissance énorme sur un bloc très bon marché est un signal d'alerte.

**À l'écrit** : « la puissance disponible sur le +12 V est de 12 × 54 = 648 W » ; « à 90 % de
rendement, 400 W fournis = {fr_number(example_wall, 0)} W absorbés ». Toujours la formule, les
valeurs et l'unité.

**Repère rapide** : puissance nominale = maximum fourni · +12 V = P = 12 × I · rendement =
fourni / absorbé · meilleur vers 50 % de charge.
"""


def _connectors() -> str:
    return f"""**Objectifs** : reconnaître chaque connecteur du bloc, ses tensions et ce qu'il
alimente ; savoir ce qui ne s'échange jamais.

## 3.1 Vue d'ensemble

{_connectors_table()}

- **ATX 24 broches** (souvent **20+4**) : alimentation principale de la carte mère. Le bloc
  détachable de 4 broches sert aux anciennes cartes à 20 broches.
- **EPS 8 broches** (souvent **4+4**, marqué « CPU ») : le +12 V du processeur, transformé par le
  VRM. Certaines cartes en demandent deux (8 + 8 ou 8 + 4) ; les anciennes ou modestes se
  contentent d'un **ATX12V 4 broches** (un demi-EPS).
- **PCIe 6 et 8 broches** (« PCIe », « VGA ») : le +12 V de la carte graphique. Une carte peut
  tirer **{PCIE_SLOT_WATTS} W par l'emplacement x16**, **{PCIE6_WATTS} W par un 6 broches** et
  **{PCIE8_WATTS} W par un 8 broches** : une carte avec 2 × 8 broches peut donc consommer jusqu'à
  {PCIE_SLOT_WATTS} + 2 × {PCIE8_WATTS} = **{gpu_power_capacity(pcie8=2)} W**.
- **12V-2x6** (successeur du 12VHPWR, 16 broches : 12 de puissance + 4 de détection) : cartes
  graphiques récentes, **jusqu'à {HPWR_MAX_WATTS} W**. Il doit être **enfoncé à fond**, sans
  pliure serrée près du connecteur : un contact partiel chauffe.
- **Alimentation SATA 15 broches** : disques et lecteurs ; **Molex 4 broches** : anciens disques
  et accessoires.

## 3.2 Brochages à connaître

{_fig(ATX24_FIGURE)}

{_fig(EPS8_FIGURE)}

{_fig(SATA_MOLEX_FIGURE)}

**Les échanges interdits.**

- **EPS 8 broches ≠ PCIe 8 broches** : même taille, mais l'EPS a ses quatre +12 V sur une
  rangée et le PCIe trois +12 V placés autrement ; les **détrompeurs** diffèrent. Forcé, l'un à
  la place de l'autre met le +12 V en **court-circuit**.
- **Câble de données SATA (7 contacts) ≠ alimentation SATA (15 contacts)** : un disque a besoin
  des deux.
- **Adaptateurs Molex ou SATA → PCIe** pour une carte graphique puissante : à proscrire, ces
  connecteurs ne sont pas prévus pour un tel courant (échauffement, fonte).

**À l'écrit** : « connecteur EPS 8 broches (4+4) marqué CPU, qui alimente le processeur à
travers le VRM » — le nom exact, puis ce qu'il alimente.

**Repère rapide** : 24 = carte · 8 « CPU » = processeur · 6/8 « PCIe » = carte graphique
({PCIE6_WATTS}/{PCIE8_WATTS} W) · 16 = carte graphique récente · 15 = disque · **un connecteur
qui résiste n'est pas le bon : ne jamais forcer.**
"""


def _budget() -> str:
    raw_margin = round(CASE2_TOTAL * (1 + DEFAULT_MARGIN))
    return f"""**Objectifs** : calculer la puissance nécessaire d'une configuration, choisir un bloc avec
une marge justifiée et vérifier le +12 V et les connecteurs.

## 4.1 La démarche en cinq points

1. **Relever** la puissance **maximale** de chaque composant sur sa fiche (processeur, carte
   graphique — « puissance totale de la carte » —, carte mère, mémoire, disques, ventilateurs).
   Une valeur absente se note « à vérifier », jamais inventée.
2. **Additionner** : c'est le **total**.
3. **Ajouter une marge** (en général **20 à 30 %**) : pics de consommation, vieillissement du
   bloc, rendement meilleur vers 50-60 % de charge, évolutions futures.
4. **Arrondir au palier commercial supérieur** (450, 500, 550… W) et **ne jamais descendre sous
   la recommandation** du fabricant de la carte graphique.
5. **Vérifier le +12 V** (P = 12 × I) et les **connecteurs** : nombre de PCIe 8 broches ou
   12V-2x6, EPS, SATA.

## 4.2 Un budget calculé

{_budget_table()}

{_fig(BUDGET_FIGURE, wide=True)}

Total : **{CASE2_TOTAL} W** ; avec {int(DEFAULT_MARGIN * 100)} % de marge : {CASE2_TOTAL} × 1,3 ≈
{raw_margin} W, soit le palier de **{CASE2_MARGIN_ONLY} W**. La carte graphique recommande
**{CASE2_GPU_RECOMMENDATION} W** : on retient **{CASE2_RECOMMENDED} W**. Courant sur le +12 V :
environ {fr_number(current_12v(CASE2_LOADS))} A, à comparer à l'étiquette du bloc.

**À l'écrit** : le calcul complet (liste, total, marge, palier, recommandation), puis le choix
justifié par la puissance, le +12 V, les connecteurs et le format.

**Repère rapide** : total des maximums + 20-30 % → palier supérieur → ≥ recommandation GPU →
+12 V et connecteurs. **Ni trop petit (arrêts), ni démesuré (prix, rendement).**
"""


def _cooling() -> str:
    return f"""**Objectifs** : expliquer le flux d'air d'un boîtier, brancher et régler les ventilateurs,
reconnaître un fonctionnement normal du ventilateur du bloc.

## 5.1 Le flux d'air

{_fig(AIRFLOW_FIGURE, wide=True)}

- Toute l'énergie consommée finit en **chaleur** : elle doit sortir du boîtier.
- Flux classique : **entrée d'air frais en façade (et en bas), sortie à l'arrière et en haut**
  (l'air chaud monte). Une **flèche moulée** sur le cadre du ventilateur indique le sens du
  flux.
- **Filtres** à nettoyer régulièrement ; **câbles rangés** pour ne pas bloquer l'air ; un bloc
  dont le ventilateur est dessous se monte **ventilateur vers le filtre** du fond, quand le
  boîtier en a un.

## 5.2 Ventilateurs et connecteurs

- **3 broches** : vitesse réglée par la **tension** (mode « DC ») ; **4 broches** : vitesse réglée
  par un signal **PWM**, plus précis. Le connecteur se règle dans le firmware (DC ou PWM).
- **CPU_FAN** : réservé au ventilateur du processeur, **surveillé** par le firmware (alerte ou
  refus de démarrer s'il ne tourne pas) ; **SYS_FAN / CHA_FAN** : ventilateurs du boîtier ;
  **AIO_PUMP** : pompe d'un watercooling tout-en-un.
- Un **répartiteur** sur un seul connecteur : le courant total ne doit pas dépasser la limite du
  connecteur (manuel).
- **Ventirad** : pâte thermique fine et neuve à chaque remontage, hauteur compatible avec le
  boîtier, fixation adaptée au socket.

## 5.3 Le ventilateur du bloc

Beaucoup de blocs ont un **mode semi-passif** : à faible charge, leur ventilateur **reste
arrêté** et ne démarre que quand le bloc chauffe. **Un ventilateur de bloc arrêté en
bureautique n'est donc pas forcément une panne** : lire la fiche. Un bloc qui sent le brûlé,
claque ou dont le ventilateur ne tourne jamais en charge, lui, est suspect.

**À l'écrit** : « les ventilateurs de façade doivent faire entrer l'air ; le ventirad se branche
sur CPU_FAN, surveillé par le firmware ».

**Repère rapide** : façade/bas → arrière/haut · 3 broches = DC, 4 broches = PWM · CPU_FAN pour
le processeur · ventilateur de bloc arrêté à faible charge = souvent normal.
"""


def _protections() -> str:
    return """**Objectifs** : connaître les protections internes d'un bloc et les protections de
l'installation (parafoudre, onduleur).

## 6.1 Protections du bloc

Un bloc de qualité coupe ses sorties en cas de problème ; c'est pourquoi un défaut provoque un
**arrêt brutal** plutôt qu'une destruction :

| Protection | Elle coupe le bloc quand… |
|---|---|
| **Surtension** (OVP) | une sortie dépasse sa tension maximale |
| **Sous-tension** (UVP) | une sortie tombe trop bas |
| **Surintensité** (OCP) | un rail fournit trop de courant |
| **Surpuissance** (OPP) | la puissance totale dépasse la limite |
| **Court-circuit** (SCP) | une sortie est reliée à la masse |
| **Surchauffe** (OTP) | le bloc est trop chaud (poussière, ventilateur bloqué) |

Après une coupure de protection, on **cherche la cause** (court-circuit, surcharge, chaleur)
avant de relancer ; relancer en boucle peut aggraver un défaut.

## 6.2 Protections de l'installation

- **Prise de terre** : le châssis métallique du PC est relié à la terre par le câble secteur ;
  jamais d'adaptateur qui supprime la terre.
- **Disjoncteur différentiel** du tableau électrique : protège les personnes contre les fuites
  de courant (rôle de l'installation, pas du PC).
- **Multiprise parafoudre** : limite les surtensions brèves (orages) ; ne protège pas d'une
  coupure. Éviter de chaîner les multiprises.
- **Onduleur** (UPS) : une batterie prend le relais pendant une **coupure** et laisse le temps
  d'un **arrêt propre**. On le choisit sur sa **puissance active en watts** (les VA ne suffisent
  pas), avec une **marge**, et sur son **autonomie** à la charge réelle. Types : *off-line*
  (bascule à la coupure), *line-interactive* (régule aussi les variations de tension),
  *on-line* (le matériel est toujours alimenté par l'onduleur, la meilleure protection).

**À l'écrit** : « l'onduleur de 600 W serait chargé à 50 % par les 300 W du serveur et offre
12 minutes pour un arrêt propre ».

**Repère rapide** : arrêt brutal = souvent une protection qui a coupé · parafoudre ≠ onduleur ·
onduleur choisi en **watts**, avec marge et autonomie.
"""


def _safety() -> str:
    return """**Objectifs** : intervenir sans danger pour soi et pour le matériel : mise hors tension,
électricité statique, batteries, outils.

## 7.1 Risques électriques

- Le **230 V** du secteur est dangereux pour les personnes ; à l'intérieur du PC, les tensions
  sont basses, mais **le bloc et l'écran contiennent des condensateurs** qui restent chargés à
  des centaines de volts **longtemps après le débranchement**.
- **On n'ouvre jamais un bloc d'alimentation** (ni pour le nettoyer, ni pour le réparer) : un
  bloc suspect se **teste** puis se **remplace**.
- Un PC **éteint mais branché** n'est pas hors tension : le +5 VSB alimente la carte mère.

## 7.2 Mise hors tension avant toute intervention

1. **Arrêter** le système proprement (fichiers fermés).
2. **Interrupteur du bloc sur 0**, puis **débrancher le câble secteur** (et la batterie d'un
   portable si elle est amovible).
3. **Appuyer quelques secondes sur le bouton de démarrage** pour vider l'énergie résiduelle ;
   la LED de veille de la carte doit s'éteindre.
4. **Se protéger de l'électricité statique** (ci-dessous), puis seulement ouvrir.

## 7.3 Électricité statique (ESD)

- Une **décharge électrostatique** que l'on ne sent même pas peut endommager un composant,
  parfois sans trace visible (panne plus tard).
- **Bracelet antistatique** relié à une partie métallique nue du **châssis** (il met la
  personne et le PC au même potentiel), **tapis antistatique**, pas de moquette ni de pull
  synthétique, pas de bijoux.
- Pièces gardées dans leur **sachet antistatique** jusqu'au montage, tenues **par les bords**,
  jamais par les contacts ; ne jamais poser une carte sur le sachet extérieur ou sur la
  moquette.

## 7.4 Batteries lithium-ion gonflées

- Signes : **coque déformée, pavé tactile soulevé, écran qui ne ferme plus**, batterie chaude.
- Danger : gaz de dégradation, **emballement thermique**, incendie, fumées toxiques — surtout si
  on la **perce, la presse, la plie ou la recharge**.
- Conduite : ne plus charger ni allumer ; retirer selon la notice avec des outils non
  coupants ; placer dans un **bac métallique ou du sable**, loin de tout combustible ; remettre
  au **point de collecte des piles et batteries** (en Belgique, Bebat), jamais à la poubelle.

## 7.5 Outils

| Outil | Usage | Précaution |
|---|---|---|
| Tournevis cruciforme (PH1, PH2), embouts | vis du boîtier, de la carte mère, du bloc | bonne taille, ne pas forcer ni riper sur la carte |
| Bracelet et tapis antistatiques | protection ESD | pince sur métal nu du châssis |
| Testeur d'alimentation | vérifier les tensions du bloc par ses connecteurs | ne prouve pas la tenue en charge |
| Multimètre | mesurer une tension continue sur un connecteur | calibre adapté ; jamais à l'intérieur du bloc |
| Lampe, pince à bec, colliers | voir, saisir une vis, ranger les câbles | pas d'outil métallique dans un PC sous tension |
| Bombe d'air sec, pinceau antistatique | dépoussiérer | bloquer les ventilateurs (survitesse), à l'extérieur |

**À l'écrit** : chaque précaution est **justifiée** : « je débranche le câble secteur, car le
+5 VSB reste présent PC éteint ».

**Repère rapide** : arrêter → 0 → débrancher → bouton → bracelet · bloc jamais ouvert ·
batterie gonflée : ni charger, ni percer, bac métallique, collecte.
"""


def _external() -> str:
    return f"""**Objectifs** : choisir le bon port et le bon câble USB, HDMI ou DisplayPort selon le débit
et la puissance nécessaires.

## 8.1 USB : la forme n'est pas la vitesse

{_usb_table()}

- **USB-A, USB-B, micro-B, USB-C** sont des **formes de connecteur** ; la **vitesse** dépend de
  la **norme du port** et du **câble**. **USB-C est une forme de connecteur** : un port USB-C peut
  être en USB 2.0. Le manuel (ou le marquage SS 5, SS 10 du port) fait foi.
- Les ports USB **alimentent** aussi les périphériques :

{_usb_power_table()}

- Un **concentrateur non alimenté** partage le courant d'un seul port : un disque dur 2,5"
  peut s'y déconnecter. Un **chargeur USB-C Power Delivery** négocie tension et courant avec
  l'appareil (câble 5 A nécessaire au-delà de 60 W).

## 8.2 Vidéo : HDMI et DisplayPort

{_video_table()}

- Les connecteurs HDMI ont **la même forme** de la version 1.4 à 2.1 : c'est le **débit des
  ports et du câble** qui fixe la définition et la fréquence. Câbles : « High Speed »
  (10,2 Gbit/s), « Premium High Speed » (18 Gbit/s), « Ultra High Speed » (48 Gbit/s).
- **HDMI et DisplayPort transportent aussi le son**. Le DisplayPort permet le **chaînage**
  d'écrans (MST) ; un adaptateur **DisplayPort → HDMI** simple fonctionne si le port est
  « DP++ » ; l'inverse (HDMI → DisplayPort) demande un adaptateur **actif**.
- **DVI** (numérique, parfois analogique) et **VGA** (analogique) : anciens écrans et
  vidéoprojecteurs.
- **Avec une carte graphique, l'écran se branche sur elle**, pas sur les sorties de la carte
  mère.

**À l'écrit** : « le câble High Speed limite la liaison à 10,2 Gbit/s, soit la 4K à 30 Hz ; un
câble DisplayPort entre les ports DP 1.4 permet la 4K à 120 Hz ».

**Repère rapide** : USB-C = forme · vitesse = norme du port + câble · HDMI : même prise, débit
différent · écran sur la carte graphique.
"""


def _internal() -> str:
    return f"""**Objectifs** : brancher correctement les liaisons internes SATA, PCIe et M.2 et repérer
les incompatibilités d'interface.

## 9.1 SATA

- Chaque disque SATA reçoit **deux câbles** : **données** (7 contacts, vers la carte mère) et
  **alimentation** (15 broches, vers le bloc). L'un sans l'autre : disque absent.
- **SATA révision 3 : 6 Gbit/s**, environ **600 Mo/s utiles** — la limite d'un SSD SATA.
- Le **numéro du port** compte : certains ports SATA sont **partagés** avec un emplacement M.2
  et désactivés quand celui-ci est utilisé en SATA (manuel).

## 9.2 PCIe

- Un emplacement se décrit par sa **taille mécanique** (x1, x4, x16) et ses **lignes câblées**
  (« x16 mécanique, x4 électrique »). Une carte x1 fonctionne dans un emplacement plus long.
- Le PCIe est **rétrocompatible** : une carte PCIe 4.0 dans un emplacement 3.0 fonctionne, au
  débit de la génération la plus ancienne.
- L'emplacement x16 fournit au plus **{PCIE_SLOT_WATTS} W** ; au-delà, la carte graphique demande
  ses connecteurs PCIe d'alimentation.
- Une carte graphique épaisse peut **masquer l'emplacement voisin**.

## 9.3 M.2 : forme, clé et interface

{_m2_table()}

- Trois informations à vérifier : la **longueur** (2280 = 22 × 80 mm, aussi 2242, 2260, 22110),
  la **clé** (encoche) et surtout l'**interface** : **NVMe** (PCIe) ou **SATA**.
- **Même forme ne veut pas dire même interface** : un SSD M.2 **SATA** (clé B+M) entre
  physiquement dans un emplacement à clé M **NVMe uniquement**, mais **n'y est pas détecté**.
- Un M.2 utilisé en SATA peut **désactiver un port SATA** ; un M.2 relié au chipset peut
  partager ses lignes avec un emplacement PCIe : tableau du manuel.

**À l'écrit** : « le SSD M.2 SATA n'est pas pris en charge par l'emplacement M.2_1, NVMe
uniquement ; le placer en M.2_2 (NVMe ou SATA) et déplacer le disque du port SATA6 partagé ».

**Repère rapide** : SATA = données 7 + alimentation 15 · PCIe rétrocompatible · M.2 : longueur,
clé **et** interface (NVMe ou SATA) · ports partagés → manuel.
"""


def _compatibility() -> str:
    return """**Objectifs** : déterminer la compatibilité d'une configuration complète, critère par
critère, avec les valeurs qui justifient chaque verdict.

## 10.1 Mémoire et processeur

- **Génération de mémoire** : DDR3, DDR4 et DDR5 **ne sont pas interchangeables** (encoche-
  détrompeur à un autre endroit, tensions différentes). La carte mère accepte **une seule**
  génération ; **DIMM** (bureau) et **SO-DIMM** (portable) sont des formats différents.
- **Socket** : AMD **AM4** (DDR4), **AM5** (DDR5 uniquement) ; Intel **LGA1700** (DDR4 **ou** DDR5
  selon la carte), **LGA1851** (DDR5). **Même socket ne veut pas dire compatibilité garantie** :
  la **liste des processeurs pris en charge** de la carte et la **version du firmware** font foi.
- **Ventirad** : compatible avec le socket (fixation) et assez bas pour le boîtier.

## 10.2 Formats

- Carte mère : **ATX** (305 × 244 mm), **microATX** (244 × 244 mm), **Mini-ITX**
  (170 × 170 mm) ; une carte **plus petite** entre dans un boîtier prévu pour un format **plus
  grand**, jamais l'inverse (détail en [PR01](/uaa/ampcr-pratique-pr01)).
- Bloc : **ATX** ou **SFX** selon le boîtier ; longueur de la carte graphique et hauteur du
  ventirad limitées par le boîtier.

## 10.3 La grille complète

| Critère | On compare | Source |
|---|---|---|
| Processeur ↔ carte | socket, liste des processeurs, version du firmware | fiches et liste du fabricant de la carte |
| Mémoire ↔ carte | génération DDR, DIMM/SO-DIMM, capacité maximale | manuel de la carte |
| Carte ↔ boîtier | format de carte | fiche du boîtier |
| Stockage ↔ carte | interface (SATA, NVMe), longueur M.2, ports partagés | manuel de la carte |
| Carte graphique ↔ boîtier, carte | longueur, épaisseur, emplacement x16 | fiches |
| Ventirad ↔ boîtier, socket | hauteur, fixation | fiches |
| Bloc ↔ configuration | puissance, +12 V, connecteurs (EPS, PCIe), format | fiche et étiquette du bloc |

**« Ça rentre » ne veut pas dire « compatible »** : une barrette DDR4 ne rentre pas dans un
emplacement DDR5 (heureusement), mais un SSD M.2 SATA rentre dans un emplacement NVMe et ne
fonctionne pas. On ne suppose **rien** qui ne figure pas sur une fiche : on écrit « à vérifier ».

**À l'écrit** : un tableau critère / verdict / valeurs, puis la correction proposée pour chaque
point non conforme.

**Repère rapide** : socket + liste + firmware · DDR4 ≠ DDR5 · petit format dans grand boîtier ·
M.2 : interface · bloc : W, +12 V, connecteurs, format.
"""


def _symptoms() -> str:
    return f"""**Objectifs** : évaluer des symptômes d'alimentation, distinguer une hypothèse d'une
preuve et choisir des tests sans risque.

## 11.1 Symptômes et pistes

| Symptôme | Pistes liées à l'alimentation | Premier test |
|---|---|---|
| **Rien** : aucun voyant, aucun ventilateur | prise, câble, multiprise, interrupteur du bloc, bouton de façade, bloc | autre prise et câble ; testeur d'alimentation |
| **Démarre une seconde puis s'arrête** | EPS ou ATX 24 mal branché, court-circuit, protection du bloc | contrôler les connecteurs ; configuration minimale |
| **S'éteint sous forte charge** (jeu, calcul) | bloc sous-dimensionné ou fatigué, connecteurs PCIe manquants, adaptateur | mesurer en charge ; bloc connu bon assez puissant |
| **Redémarrages aléatoires** | tension hors tolérance, bloc vieillissant (aussi mémoire, chaleur : PR06) | mesures ; bloc connu bon |
| **Odeur de brûlé, claquement, fumée** | composant du bloc détruit | **débrancher immédiatement** ; ne pas rallumer ; remplacer |
| **Ventilateur du bloc arrêté** | souvent **mode semi-passif normal** à faible charge | lire la fiche ; observer en charge |

{_fig(SYMPTOM_FIGURE, wide=True)}

## 11.2 Mesurer et conclure

- La norme ATX admet **±5 %** sur +12 V, +5 V, +3,3 V et +5 VSB et **±10 %** sur −12 V (tableau
  du chapitre 1).
- Un **testeur d'alimentation** mesure à vide ou sous très faible charge : **une mesure conforme
  n'innocente pas un bloc** qui s'effondre en charge. Les sondes du firmware ou d'un logiciel
  donnent une indication en charge, moins précise.
- Le **test décisif** reste le **bloc connu fonctionnel**, assez puissant, dans les mêmes
  conditions.
- **Pas de diagnostic catégorique sans mesure ni test croisé** : « c'est l'alimentation » reste
  une hypothèse jusqu'à la preuve. La démarche complète est en [PR06](/uaa/ampcr-pratique-pr06).

**À l'écrit** : symptôme exact → hypothèses classées → test le plus simple et le moins risqué →
résultat → conclusion justifiée.

**Repère rapide** : arrêt sous charge = bloc à vérifier en charge · ±5 % · testeur à vide ≠
preuve · bloc connu bon = test décisif.
"""


def _procedure() -> str:
    return f"""**Objectifs** : rédiger une procédure de remplacement de bloc complète, sûre et
vérifiable.

{_fig(SAFE_FIGURE)}

## 12.1 Avant : choisir le remplaçant

- **Format** (ATX ou SFX) accepté par le boîtier, **puissance** issue du budget (chapitre 4),
  **+12 V** suffisant, **connecteurs** nécessaires (EPS, PCIe ou 12V-2x6, nombre de SATA),
  **longueur des câbles** (tour haute), **rendement** et **protections**.
- Prévenir le client de la durée d'indisponibilité ; noter l'état initial.

## 12.2 Pendant : intervenir

1. **Couper** : arrêt du système, interrupteur sur 0, câble secteur débranché.
2. **Décharger** : bouton de démarrage quelques secondes, LED de veille éteinte.
3. **Se protéger** : bracelet antistatique au châssis, tapis ; aucun bijou.
4. **Repérer** : photographier et noter chaque câble et son emplacement.
5. **Débrancher** tous les câbles du bloc en pressant les clips (ne jamais tirer sur les fils).
6. **Déposer** l'ancien bloc (quatre vis à l'arrière), **poser** le nouveau, ventilateur vers son
   filtre, et le visser.
7. **Rebrancher** avec **les câbles du nouveau bloc uniquement** : ATX 24, EPS, PCIe, SATA —
   chaque connecteur jusqu'au clic ; ranger les câbles hors des ventilateurs.

## 12.3 Après : contrôler et rendre compte

- Interrupteur sur I, secteur rebranché : démarrage, **tensions** dans le firmware ou au
  testeur, **test en charge** (jeu ou logiciel de charge) pendant un temps suffisant, bruit et
  températures.
- **Compte rendu** : symptôme, tests, cause, pièce remplacée (modèle, puissance), contrôles et
  résultat ; ancien bloc remis à la filière de recyclage des équipements électriques.

**À l'écrit** : chaque étape est **nommée et justifiée** (« je débranche le câble secteur, car
le +5 VSB reste présent »), dans l'ordre.

**Repère rapide** : couper → décharger → bracelet → repérer → remplacer avec ses câbles →
contrôler → compte rendu.
"""


def _examples() -> str:
    failed = [label for label, ok, _ in check_configuration(CASE1_CONFIG) if not ok]
    measures = measure_lines(CASE4_MEASURES)
    rail12 = RAILS_BY_NAME["+12 V"]
    low12, _high12 = tolerance_range(rail12)
    load12 = CASE4_MEASURES[0][2]
    return f"""## Cas 1 — Déterminer la compatibilité d'une configuration

**Situation.** Un client a composé ce devis (fiches fictives) : processeur socket
{CASE1_CONFIG.cpu_socket} ; carte mère {CASE1_CONFIG.board_form} {CASE1_CONFIG.board_socket}, 4 ×
{CASE1_CONFIG.board_memory}, M.2 {CASE1_CONFIG.board_m2} uniquement ; 2 × 16 Go
{CASE1_CONFIG.ram} ; SSD M.2 2280 {CASE1_CONFIG.ssd_m2} ; carte graphique de
{CASE1_CONFIG.gpu_length_mm} mm, {CASE1_CONFIG.gpu_pcie8_needed} × PCIe 8 broches, bloc
recommandé {CASE1_CONFIG.gpu_psu_recommendation_w} W ; ventirad de
{CASE1_CONFIG.cooler_height_mm} mm ; boîtier {' / '.join(CASE1_CONFIG.case_forms)}, carte graphique
{CASE1_CONFIG.case_gpu_max_mm} mm et ventirad {CASE1_CONFIG.case_cooler_max_mm} mm au plus, bloc
{' / '.join(CASE1_CONFIG.case_psu_forms)} ; bloc {CASE1_CONFIG.psu_form} de {CASE1_CONFIG.psu_watts} W
avec {CASE1_CONFIG.psu_pcie8} × PCIe 6+2.

**Résolution, critère par critère (grille du chapitre 10).**

{_check_table(CASE1_CONFIG)}

**Conclusion rédigée.** {len(failed)} points non conformes : la **mémoire DDR4** ne s'insère pas
dans une carte **DDR5** → 2 × 16 Go DIMM DDR5 ; le **SSD M.2 SATA** ne serait pas détecté dans un
emplacement **NVMe uniquement** → SSD M.2 NVMe ; le **bloc de 550 W** est sous les 650 W
recommandés et n'a qu'**un** PCIe 8 broches pour deux nécessaires → bloc de 650 W au moins avec
deux PCIe 8 broches (pas d'adaptateur). Le processeur (même socket) reste à vérifier dans la
liste de la carte, avec la version du firmware.

## Cas 2 — Dimensionner un bloc d'alimentation

**Situation.** Pour la configuration du chapitre 4 (fiches fictives), le client hésite entre un
bloc de 450 W « largement suffisant selon un forum » et un bloc de 1000 W « pour être
tranquille ».

**Résolution.**

1. **Total** des puissances maximales : {' + '.join(str(load.watts) for load in CASE2_LOADS)} =
   **{CASE2_TOTAL} W**.
2. **Marge** de 30 % : ≈ {round(CASE2_TOTAL * 1.3)} W → palier **{CASE2_MARGIN_ONLY} W**.
3. **Recommandation** de la carte graphique : **{CASE2_GPU_RECOMMENDATION} W** → on retient
   **{CASE2_RECOMMENDED} W**.
4. **+12 V** : environ {fr_number(current_12v(CASE2_LOADS))} A demandés ; un bloc de
   {CASE2_RECOMMENDED} W de qualité fournit en général plus de 50 A sur le +12 V (à lire sur
   l'étiquette).
5. **Connecteurs** : EPS 8 broches, PCIe demandés par la carte graphique, SATA pour le disque dur.

**Conclusion rédigée.** 450 W est **trop juste** (sous le total avec marge et sous la
recommandation : risque d'arrêts en jeu). 1000 W est **surdimensionné** : plus cher, et le PC
l'utiliserait vers 40 % au maximum, souvent bien moins. Choix : un bloc de **{CASE2_RECOMMENDED} W**,
80 PLUS Gold, avec les connecteurs nécessaires.

## Cas 3 — Repérer un mauvais branchement

**Situation.** Après le montage d'un PC par un stagiaire, rien ne s'affiche ; les ventilateurs
tournent. Relevé : ATX 24 clipsé ; **EPS branché** ; carte graphique dans le x16 avec **un seul
de ses deux connecteurs 8 broches branché** ; **écran branché sur la sortie HDMI de la carte
mère** ; processeur **sans partie graphique intégrée** (fiche) ; SSD NVMe en M.2_1.

**Résolution.**

1. **Lire chaque branchement** et le comparer aux fiches : la carte graphique demande **deux**
   8 broches → l'un manque ; beaucoup de cartes refusent alors de démarrer (voyant ou message
   sur la carte).
2. L'écran est sur la **carte mère**, mais le processeur **n'a pas de partie graphique** : ces
   sorties ne fournissent aucune image.
3. **Corriger**, PC débranché et déchargé, bracelet au poignet : brancher le second 8 broches
   **du même bloc** (pas d'adaptateur), puis l'écran sur une sortie de la **carte graphique**.
4. **Vérifier** : image au démarrage, firmware accessible, carte graphique reconnue.

**Conclusion rédigée.** Deux erreurs de branchement : alimentation incomplète de la carte
graphique et écran sur une sortie inactive. Aucune pièce n'est en cause.

## Cas 4 — Évaluer des symptômes d'alimentation et remplacer le bloc en sécurité

**Situation.** Un PC de bureau s'éteint d'un coup après quelques minutes de jeu, jamais en
bureautique. Températures normales. Un collègue a relevé les tensions au testeur à vide, puis
avec les sondes du firmware sous charge :

{_console(*measures)}

**Résolution.**

{_measures_table()}

1. **À vide**, toutes les tensions sont dans la tolérance : le testeur seul aurait « innocenté »
   le bloc.
2. **En charge**, le +12 V tombe à {volts(load12)}, sous le minimum de {volts(low12)} : il ne
   tient pas la charge, ce qui explique les arrêts en jeu (protection de sous-tension ou
   arrêt de la carte).
3. **Confirmation** : avec un **bloc connu fonctionnel** de puissance suffisante, le PC reste
   stable dans le même jeu → cause confirmée.
4. **Remplacement sûr** (chapitre 12) : arrêt, interrupteur sur 0, câble secteur débranché,
   bouton pour décharger, bracelet antistatique ; photo des câbles ; dépose ; pose du nouveau
   bloc avec **ses** câbles ; contrôles ; **l'ancien bloc n'est pas ouvert**, il part au
   recyclage.

**Conclusion rédigée.** « Le +12 V chute à {volts(load12)} sous charge (minimum {volts(low12)}) :
bloc défaillant, confirmé par un bloc de remplacement ; bloc remplacé, tensions conformes et
test en charge de 30 minutes sans arrêt. »
"""


def _pitfalls() -> str:
    return """> **Travailler sur un PC « éteint » mais branché** : le +5 VSB est présent ; toujours
> débrancher le câble secteur.

> **Ouvrir un bloc d'alimentation** : condensateurs chargés à une tension dangereuse ; un bloc
> se teste et se remplace.

> **Confondre EPS 8 broches et PCIe 8 broches**, ou forcer un connecteur qui résiste.

> **Réutiliser les câbles modulaires d'un autre bloc** : brochage différent côté bloc,
> destruction possible.

> **Alimenter une carte graphique puissante par un adaptateur Molex ou SATA.**

> **Oublier l'EPS** : le PC démarre une seconde puis s'arrête.

> **Lire la puissance totale du bloc au lieu du +12 V**, ou choisir un bloc démesuré « pour être
> tranquille ».

> **Conclure « le bloc est bon » sur une mesure à vide** : seule la mesure en charge ou un bloc
> connu bon le confirment.

> **Croire un ventilateur de bloc arrêté en panne** sans lire la fiche (mode semi-passif).

> **Prendre USB-C pour une vitesse**, ou un ancien câble HDMI pour un écran 4K à haute fréquence.

> **Installer un SSD M.2 SATA dans un emplacement NVMe uniquement**, ou oublier le port SATA
> désactivé par un M.2.

> **Mélanger DDR4 et DDR5**, ou conclure à la compatibilité sur le seul socket, sans la liste des
> processeurs.

> **Percer, presser ou recharger une batterie gonflée**, ou la jeter à la poubelle.
"""


def _exercises_intro() -> str:
    return f"""{len(PRACTICE_ITEMS)} exercices corrigés : identifications de connecteurs, classements,
remise en ordre d'une procédure, calculs (rendement, budget, +12 V, tolérances), contrôles de
compatibilité, mauvais branchements, sécurité et symptômes d'alimentation. Rédige ta réponse sur
papier **avant** d'ouvrir le corrigé ; toute réponse équivalente et justifiée est acceptée. Ces
mêmes exercices sont proposés dans [S'entraîner](/uaa/{PR02_SLUG}/practice), avec correction
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
    return f"""Le mini-examen se passe dans l'onglet [Examen blanc](/uaa/{PR02_SLUG}/exam) : **10 questions à réponse
libre**, chacune notée sur **2 points**, soit une note sur **{EXAM_TOTAL_POINTS}**. Les
questions ne figurent pas dans ce cours.

| N° | Thème | Type | Points |
|---|---|---|---|
{rows}

**Déroulement.** Chaque question est une situation complète : toutes les informations
nécessaires sont dans l'énoncé et ses documents (fiches fictives, étiquettes, relevés).
**Aucune correction n'est visible pendant la passation** ; tes réponses sont enregistrées au
fur et à mesure. Après l'envoi, chaque réponse est corrigée selon le **barème analytique** de la
question (critères et points), puis tu vois ta note sur {EXAM_TOTAL_POINTS}, le corrigé et le
barème.

**Ce que valorise le barème.** L'**identification exacte**, les **calculs posés avec leurs
unités**, la **justification** d'un verdict de compatibilité et des **précautions** justifiées —
pas la récitation de sigles. Une autre formulation juste est acceptée.

**Nature de la correction.** Les réponses rédigées reçoivent une **proposition de correction
automatique** (assistée par IA) appuyée sur le barème : c'est un repère d'entraînement, pas une
note officielle ; en cas de doute, compare ta réponse au corrigé.
"""


def _memo() -> str:
    return f"""## Mémo

- **Secteur** {MAINS_VOLTAGE} V AC {MAINS_FREQUENCY} Hz → **bloc** → +12 V, +5 V, +3,3 V DC ; **+5 VSB**
  présent dès le branchement.
- **Tolérances ATX** : ±5 % (+12 V : 11,40 à 12,60 V ; +5 V : 4,75 à 5,25 V ; +3,3 V : 3,14 à
  3,47 V) ; −12 V : ±10 %.
- **Puissance** : nominale = maximum fourni ; **+12 V = 12 × I** ; absorbée = fournie / rendement.
- **80 PLUS** : meilleur rendement vers 50 % de charge ; Gold ≈ 90 % à 50 %.
- **Connecteurs** : ATX 24 (carte) · EPS 4+4 « CPU » · PCIe 6 ({PCIE6_WATTS} W) / 8 ({PCIE8_WATTS} W)
  + {PCIE_SLOT_WATTS} W par l'emplacement · 12V-2x6 (≤ {HPWR_MAX_WATTS} W) · SATA 15 · Molex 4.
- **Interdits** : EPS ↔ PCIe, câbles modulaires d'un autre bloc, adaptateurs Molex → PCIe,
  forcer un connecteur.
- **Budget** : total des maximums + 20-30 % → palier → ≥ recommandation GPU → +12 V et
  connecteurs.
- **Refroidissement** : façade/bas → arrière/haut ; CPU_FAN ; 3 broches DC, 4 broches PWM.
- **Protections** : OVP, UVP, OCP, OPP, SCP, OTP ; parafoudre ≠ onduleur (choisi en W).
- **Sécurité** : arrêter → 0 → débrancher → bouton → bracelet ; bloc **jamais ouvert** ;
  batterie gonflée : ni charge ni perçage, bac métallique, collecte.
- **USB-C** = forme ; HDMI 2.0 = 4K 60 Hz, 2.1 = 4K 120 Hz ; DP 1.4 = 4K 120 Hz ; câble adapté.
- **M.2** : longueur, clé **et** interface (NVMe/SATA) ; ports SATA partagés.
- **Compatibilité** : socket + liste + firmware · DDR4 ≠ DDR5 · formats · « ça rentre » ≠
  compatible.

## Glossaire des termes employés

- **12V-2x6** : connecteur 16 broches des cartes graphiques récentes (successeur du 12VHPWR).
- **80 PLUS** : certification du rendement d'un bloc (Bronze, Gold, Platinum…).
- **EPS** : connecteur 8 broches (4+4) d'alimentation du processeur.
- **ESD** : décharge électrostatique.
- **Onduleur** : appareil à batterie qui alimente le matériel pendant une coupure.
- **PS_ON#** : signal (fil vert) qui commande la mise en marche du bloc.
- **PWM** : réglage de vitesse d'un ventilateur 4 broches par impulsions.
- **PWR_OK** : signal (fil gris) indiquant que les tensions sont stables.
- **Rendement** : puissance fournie / puissance absorbée.
- **+5 VSB** : tension de veille, présente tant que le bloc est branché.
- **VRM** : étage de la carte mère qui transforme le +12 V en tension du processeur.
"""


def _sources() -> str:
    return """## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), pp. 3 et 5 : épreuve uniquement écrite, exigences AP-04,
  AP-06 et AP-17. Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
  Programme officiel n° 345/2007/249 (option AMPCR).
- **Alimentation** : guide de conception des alimentations ATX12V / ATX 3.x (Intel) — tensions,
  tolérances, couleurs de fil, PS_ON#, PWR_OK, +5 VSB ; SSI EPS12V ; **PCI Express** :
  spécification CEM (PCI-SIG) — 75 W par l'emplacement x16, 75 W (6 broches), 150 W
  (8 broches), connecteur 12V-2x6 ; **rendement** : programme 80 PLUS (CLEAResult), seuils
  115 V usage interne ; **SATA** : spécification Serial ATA révision 3 ; **M.2** : spécification
  PCI-SIG M.2 ; **USB** : USB-IF (USB 2.0, USB 3.2, USB4, USB Type-C, USB Power Delivery 3.1) ;
  **HDMI** : HDMI Licensing Administrator (versions et catégories de câbles) ; **DisplayPort** :
  VESA (DP 1.2, 1.4, 2.1).
- **Sécurité** : notices des fabricants de portables pour les batteries lithium-ion ; collecte
  des piles et batteries en Belgique (Bebat).

Les tableaux de valeurs du cours (tolérances, connecteurs, rendements, budgets, compatibilité,
débits) et les schémas sont **produits par programme** depuis ces données, **vérifiés par des
tests automatiques** ; aucun schéma n'est tiré d'une image générée.

## Compléments pédagogiques (non imposés par la liste officielle)

La liste des pp. 5-6 demande les caractéristiques d'une alimentation (AP-04), les
branchements, interfaces et connexions (AP-06) et la notion de compatibilité (AP-17). Sont des
**compléments**, signalés comme tels :

- la sécurité électrique, la protection ESD, les batteries gonflées et les outils (AP-C02,
  approfondis en PR03 et PR28) ;
- les seuils 80 PLUS, les onduleurs, les débits chiffrés HDMI/DisplayPort et la puissance USB.

## Supports fictifs

Les fiches produits, étiquettes, devis, relevés et situations de ce cours sont **fictifs** et
reconstitués pour l'entraînement ; ils ne décrivent aucun produit réel. Aucun n'est une question
officielle ou déjà posée par le Jury.
"""


def pr02_course_sections() -> list[tuple[str, str]]:
    """Blocs du cours (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("PR02 — Objectifs et place dans l'épreuve", _objectives()),
        ("PR02 — 1. Courant alternatif, courant continu et rôle du bloc d'alimentation", _ac_dc()),
        ("PR02 — 2. Caractéristiques d'un bloc : puissance, +12 V, rendement et format", _psu_specs()),
        ("PR02 — 3. Connecteurs d'alimentation : ATX 24, EPS, PCIe, 12V-2x6, SATA, Molex", _connectors()),
        ("PR02 — 4. Budget de puissance et marges", _budget()),
        ("PR02 — 5. Ventilateurs, flux d'air et refroidissement", _cooling()),
        ("PR02 — 6. Protections du bloc et de l'installation, onduleur", _protections()),
        ("PR02 — 7. Sécurité électrique, mise hors tension, ESD, batteries et outils", _safety()),
        ("PR02 — 8. Connectique externe : USB, HDMI et DisplayPort", _external()),
        ("PR02 — 9. Connectique interne : SATA, PCIe et M.2 SATA/NVMe", _internal()),
        ("PR02 — 10. Compatibilité : génération DDR, socket, formats et grille complète", _compatibility()),
        ("PR02 — 11. Évaluer des symptômes d'alimentation", _symptoms()),
        ("PR02 — 12. Procédure écrite : remplacer un bloc d'alimentation en sécurité", _procedure()),
        ("PR02 — Exemples : quatre cas intégralement résolus", _examples()),
        ("PR02 — Pièges et erreurs fréquentes", _pitfalls()),
        (f"PR02 — Exercices corrigés ({len(PRACTICE_ITEMS)}) et leurs corrigés", _exercises_intro()),
        ("PR02 — Mini-examen noté sur 20 : mode d'emploi", _mini_exam()),
        ("PR02 — Fiche mémo et glossaire", _memo()),
        ("PR02 — Sources et compléments pédagogiques", _sources()),
    ]
