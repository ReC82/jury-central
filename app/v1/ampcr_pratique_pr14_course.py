"""Cours PR14 « Débits, distances, atténuation et impédance » — parcours AMPCR pratique écrite
(ticket #217).

Matière : intégralement celle du ticket #217 (bits et octets, b/s et multiples décimaux, durée
d'une copie, débit utile et nominal ; Ethernet 10/100/1000/10G, canal cuivre de 100 m = 90 m
de lien permanent + cordons, Cat5e 1 Gb/s sur 100 m, Cat6A 10 Gb/s sur 100 m, Cat6 à 10 Gb/s
sur distance conditionnelle ; 10BASE2 185 m, 10BASE5 500 m ; atténuation en dB, bruit,
diaphonie NEXT, blindage, réflexions, impédance coaxiale 50/75 Ω ; fibre monomode ou
multimode, pertes et portée selon le module optique ; duplex, négociation, collisions
historiques, liaison à 100 Mb/s au lieu de 1 Gb/s ; cinq cas résolus chiffrés), découpée en
blocs titrés (le titre pilote le type de carte, `app.card_kind` : aucun titre de bloc
théorique ne contient « examen », « source », « ressource », « exemple », « exercice »,
« méthode », « piège », « attention », « transfert » ni « mémo »).
Données et schémas : `app.v1.ampcr_pratique_pr14_figures` ; exercices et mini-examen :
`app.v1.ampcr_pratique_pr14_bank`. Le choix et la pose des câbles relèvent de PR13, le
brochage et les testeurs de PR15, le coaxial BNC et la réflectométrie de PR16 (publiés,
liens) ; la fibre optique (pose, connecteurs, raccordement) est l'objet de PR17, non publié à
la rédaction : renvoi en texte seulement.
"""

from app.v1.ampcr_pratique_pr06_course import _exercise_card, _fig, _req
from app.v1.ampcr_pratique_pr14_bank import EXAM_ITEMS, EXAM_TOTAL_POINTS, PRACTICE_ITEMS
from app.v1.ampcr_pratique_pr14_figures import (
    BUDGET_EXAMPLE,
    BUDGET_FIGURE,
    BYTE_FIGURE,
    CABLE_LOSS_100MHZ,
    CHANNEL_MAX_M,
    COAX_SEGMENT_MAX_DB,
    COAX_STANDARDS,
    CONNECTOR_PAIR_DB,
    COPPER_STANDARDS,
    CROSSTALK_FIGURE,
    DB_FIGURE,
    ETH_FCS,
    ETH_HEADER,
    ETH_IFG,
    ETH_MTU,
    ETH_PREAMBLE_SFD,
    ETH_WIRE_BYTES,
    FIBRE_ATTENUATION,
    FIBRE_FIGURE,
    FIBRE_REACH,
    FIBRE_TYPES,
    FULL,
    HALF,
    IPV4_HEADER,
    LINK_FIGURE,
    MULTIMODE,
    PROCEDURES,
    REACH_FIGURE,
    REFLECTION_EXAMPLES,
    REFLECTION_FIGURE,
    SPLICE_DB,
    TCP_EFFICIENCY,
    TCP_HEADER,
    TCP_PAYLOAD,
    TEN_G_CAT6_MAX_M,
    TEN_G_CAT6_WORST_M,
    TRANSFER_FIGURE,
    TWISTED_PAIR_OHM,
    TWISTED_PAIR_TOLERANCE_OHM,
    UNIT_ROWS,
    WRITTEN_AT,
    Port,
    attenuation_for,
    cable_loss_db,
    duration_fr,
    fr,
    fraction_after,
    negotiate,
    pct,
    rate_bps,
    reflected_power_pct,
    reflection_coefficient,
    return_loss_db,
    to_bits,
    transfer_time_s,
)
from app.v1.ampcr_pratique_pr15_figures import CORDS_MAX_M, PERMANENT_LINK_MAX_M

PR14_TITLE = "Débits, distances, atténuation et impédance"
PR14_SLUG = "ampcr-pratique-pr14"


def _exercises_html() -> str:
    return "\n\n".join(
        _exercise_card(i, item, anchor_prefix="pr14") for i, item in enumerate(PRACTICE_ITEMS, start=1)
    )


def _ex(*keys: str) -> str:
    """Renvoi texte vers les exercices corrigés liés à un chapitre (séquence « Exercices
    corrigés ») : pas de lien d'ancre, la page n'affiche qu'une séquence à la fois."""
    return ", ".join(f"**{key}**" for key in keys) + " (séquence « Exercices corrigés »)"


# --- Tableaux de données (générés depuis les données vérifiées) ------------------------------


def _units_table() -> str:
    rows = "\n".join(f"| **{unit}** | {value} | {use} |" for unit, value, use in UNIT_ROWS)
    return "| Unité | Valeur | Emploi |\n|---|---|---|\n" + rows


def _copper_table() -> str:
    rows = "\n".join(
        f"| **{s.name}** | {s.rate} | {s.min_category} au moins | {s.pairs} | {CHANNEL_MAX_M} m | {s.note} |"
        for s in COPPER_STANDARDS
    )
    return ("| Norme | Débit | Câble | Paires utilisées | Canal maximal | Remarque |\n"
            "|---|---|---|---|---|---|\n" + rows)


def _coax_table() -> str:
    rows = "\n".join(f"| **{name}** | {cable} | {metres} m | {note} |" for name, cable, metres, note in COAX_STANDARDS)
    return "| Norme | Câble | Segment maximal | Remarque |\n|---|---|---|---|\n" + rows


def _cable_loss_table() -> str:
    rows = "\n".join(
        f"| **{cat}** | {fr(db)} dB | {fr(cable_loss_db(50, db))} dB | {pct(fraction_after(cable_loss_db(100, db)))} |"
        for cat, db in CABLE_LOSS_100MHZ.items()
    )
    return ("| Câble | Affaiblissement max. sur 100 m | Sur 50 m | Puissance restante après 100 m |\n"
            "|---|---|---|---|\n" + rows)


def _reflection_table() -> str:
    rows = []
    for label, line, load in REFLECTION_EXAMPLES:
        gamma = reflection_coefficient(load, line)
        rl = return_loss_db(gamma)
        rows.append(
            f"| {label} | {fr(gamma, 2)} | {fr(reflected_power_pct(gamma), 1)} % | "
            f"{'aucune réflexion' if rl is None else fr(rl, 1) + ' dB'} |"
        )
    return ("| Liaison | Γ | Puissance réfléchie | Affaiblissement de réflexion |\n|---|---|---|---|\n"
            + "\n".join(rows))


def _fibre_types_table() -> str:
    rows = "\n".join(f"| **{name}** | {kind} | {core} | {note} |" for name, kind, core, note in FIBRE_TYPES)
    return "| Fibre | Type | Cœur | Usage |\n|---|---|---|---|\n" + rows


def _fibre_loss_table() -> str:
    names = {MULTIMODE: "Multimode (OM1 à OM4)", "OS1": "Monomode OS1 (intérieur)", "OS2": "Monomode OS2"}
    rows = "\n".join(f"| {names[kind]} | {wl} nm | {fr(db)} dB/km |" for (kind, wl), db in FIBRE_ATTENUATION.items())
    return "| Fibre | Longueur d'onde | Affaiblissement maximal |\n|---|---|---|\n" + rows


def _reach_table() -> str:
    rows = "\n".join(
        f"| **{module}** | {fibre} | {wl} nm | {m if m < 1000 else fr(m / 1000)} {'m' if m < 1000 else 'km'} |"
        for module, fibre, wl, m in FIBRE_REACH
    )
    return "| Module optique | Fibre | Longueur d'onde | Portée maximale |\n|---|---|---|---|\n" + rows


def _negotiation_table() -> str:
    cases = (
        ("Auto", "Auto", Port(), Port()),
        ("Auto", "Forcé 100 Mb/s full", Port(), Port(auto=False, speed=100, duplex=FULL)),
        ("Forcé 100 Mb/s full", "Forcé 100 Mb/s full", Port(auto=False, speed=100, duplex=FULL),
         Port(auto=False, speed=100, duplex=FULL)),
        ("Auto", "Forcé 100 Mb/s half", Port(), Port(auto=False, speed=100, duplex=HALF)),
    )
    rows = []
    for left, right, a, b in cases:
        link = negotiate(a, b)
        verdict = "**désaccord de duplex**" if link.mismatch else "cohérent"
        rows.append(f"| {left} | {right} | {link.speed} Mb/s | {link.duplex_a} / {link.duplex_b} | {verdict} |")
    return ("| Carte du PC | Port du switch | Vitesse | Duplex PC / switch | Résultat |\n"
            "|---|---|---|---|---|\n" + "\n".join(rows))


def _procedures_list() -> str:
    return "\n".join(
        f"{i}. **{title}** ({len(steps)} étapes)" for i, (title, steps) in enumerate(PROCEDURES, start=1)
    )


# --- Cinq cas résolus (valeurs calculées) -----------------------------------------------------

C1_BITS = to_bits(50, "Go")
C1_GIGA = transfer_time_s(C1_BITS, rate_bps(1, "Gb/s"), 0.94)
C1_FAST = transfer_time_s(C1_BITS, rate_bps(100, "Mb/s"), 0.94)
C3_LOSS = cable_loss_db(60, CABLE_LOSS_100MHZ["Cat6"])
C3_LEFT = fraction_after(C3_LOSS)
C4_FIBRE_DB = BUDGET_EXAMPLE.length_m / 1000 * attenuation_for(BUDGET_EXAMPLE.fibre, BUDGET_EXAMPLE.wavelength_nm)

CASES: tuple[tuple[str, str, tuple[str, ...], str], ...] = (
    (
        "Cas 1 — Durée d'une sauvegarde",
        (
            "Une PME sauvegarde 50 Go (taille décimale) chaque nuit vers un NAS. Le rendement mesuré est "
            "de 94 %. Combien de temps dure la copie à 1 Gb/s ? Et si le lien tombe à 100 Mb/s ?"
        ),
        (
            f"**Taille en bits** : 50 Go = 50 × 10⁹ octets × 8 = {fr(C1_BITS / 1e9)} × 10⁹ bits.",
            "**Débit utile** : 1 Gb/s × 0,94 = 940 × 10⁶ b/s ; 100 Mb/s × 0,94 = 94 × 10⁶ b/s.",
            f"**Durées** : {fr(C1_BITS / 1e9)} × 10⁹ / 940 × 10⁶ ≈ {fr(C1_GIGA)} s ; à 100 Mb/s, dix fois plus : ≈ {fr(C1_FAST, 0)} s.",
        ),
        (
            f"La sauvegarde dure environ {duration_fr(C1_GIGA)} à 1 Gb/s, et {duration_fr(C1_FAST)} si le lien "
            "tombe à 100 Mb/s : un lien rétrogradé se voit tout de suite dans la durée des sauvegardes."
        ),
    ),
    (
        "Cas 2 — 10 Gb/s sur un câblage Cat6 existant",
        (
            "Un bureau d'études veut passer son serveur à 10 Gb/s. Le lien Cat6 existant mesure 48 m de "
            "canal, au milieu d'un faisceau de 24 câbles."
        ),
        (
            (
                f"**Règle** : 10GBASE-T demande du Cat6A sur {CHANNEL_MAX_M} m ; en Cat6, {TEN_G_CAT6_MAX_M} m au plus, "
                f"{TEN_G_CAT6_WORST_M} m dans le pire cas de diaphonie entre câbles voisins."
            ),
            (
                f"**Situation** : 48 m est entre {TEN_G_CAT6_WORST_M} et {TEN_G_CAT6_MAX_M} m, dans un gros faisceau : la "
                "diaphonie exogène (entre câbles) peut empêcher le 10 Gb/s."
            ),
            (
                "**Décision** : certifier le lien à 10 Gb/s (diaphonie exogène comprise) ; s'il échoue, tirer un "
                "câble Cat6A."
            ),
        ),
        (
            "Possible sous conditions : on ne promet 10 Gb/s sur ce Cat6 qu'après une certification réussie ; "
            "sinon, câble Cat6A."
        ),
    ),
    (
        "Cas 3 — Affaiblissement d'un lien Cat6",
        (
            f"Un lien Cat6 de 60 m. La norme fixe à {fr(CABLE_LOSS_100MHZ['Cat6'])} dB pour 100 m, à 100 MHz, "
            "l'affaiblissement maximal du câble. Quelle part de la puissance arrive au bout, au pire ?"
        ),
        (
            f"**Proportionnalité** : en dB, l'affaiblissement suit la longueur : {fr(CABLE_LOSS_100MHZ['Cat6'])} × 60 / 100 = {fr(C3_LOSS, 2)} dB.",
            f"**Conversion** : 10^(−{fr(C3_LOSS, 2)} / 10) ≈ {fr(C3_LEFT, 3)}, soit {pct(C3_LEFT)} de la puissance.",
            "**Repère de tête** : 10 dB → un dixième, 2 dB de plus → un peu moins des deux tiers de ce dixième : environ 6 %.",
        ),
        (
            f"Au pire, il reste environ {pct(C3_LEFT)} de la puissance émise après 60 m à 100 MHz : c'est normal, "
            "le récepteur est prévu pour ; plus long ou plus haut en fréquence, il resterait encore moins."
        ),
    ),
    (
        "Cas 4 — Bilan d'une liaison multimode à 10 Gb/s",
        (
            f"Deux baies d'un même bâtiment sont reliées par {fr(BUDGET_EXAMPLE.length_m)} m de fibre OM3, avec deux "
            f"connecteurs et aucune épissure. Modules 10GBASE-SR ; budget de la fiche du module : "
            f"{fr(BUDGET_EXAMPLE.budget_db)} dB."
        ),
        (
            f"**Portée** : 10GBASE-SR tient 300 m sur OM3 ; {fr(BUDGET_EXAMPLE.length_m)} m conviennent.",
            (
                f"**Perte** : fibre 0,22 km × 3,5 dB/km = {fr(C4_FIBRE_DB, 2)} dB ; connecteurs 2 × {fr(CONNECTOR_PAIR_DB, 2)} = 1,5 dB ; "
                f"total {fr(BUDGET_EXAMPLE.loss_db, 2)} dB."
            ),
            f"**Marge** : {fr(BUDGET_EXAMPLE.budget_db)} − {fr(BUDGET_EXAMPLE.loss_db, 2)} = {fr(BUDGET_EXAMPLE.margin_db, 2)} dB.",
        ),
        (
            f"La liaison respecte la portée et le budget, avec une marge faible ({fr(BUDGET_EXAMPLE.margin_db, 2)} dB) "
            "calculée sur des valeurs maximales : on nettoie les connecteurs et on mesure la perte réelle à la réception."
        ),
    ),
    (
        "Cas 5 — Un PC à 100 Mb/s au lieu de 1 Gb/s",
        (
            "Un poste Gigabit affiche 100 Mb/s full duplex. La carte et le switch sont en auto-négociation "
            "et annoncent tous deux 1000BASE-T. Le testeur montre la paire 7-8 ouverte dans la prise murale."
        ),
        (
            "**Configuration** : rien n'est forcé et les deux côtés savent faire 1 Gb/s : ce n'est ni un réglage ni un équipement limité.",
            "**Câble** : 1000BASE-T utilise les quatre paires ; 100BASE-TX seulement 1-2 et 3-6. Avec une paire coupée, la carte rétrograde à 100 Mb/s.",
            "**Correction** : refaire le poinçonnage de la prise, retester les huit conducteurs.",
        ),
        (
            "Cause : paire 7-8 ouverte à la prise. Après reprise du raccordement, le lien remonte à 1 Gb/s full duplex ; "
            "on le vérifie des deux côtés et on consigne."
        ),
    ),
)

# =============================================================================================
# Sections du cours (titre du bloc, Markdown / HTML)
# =============================================================================================


def _objectives() -> str:
    return f"""## Ce que tu sauras faire, par écrit

L'épreuve pratique AMPCR se passe **uniquement par écrit** (consignes officielles 2026-2027/1,
p. 3). Devant un dossier, on attend de toi des **calculs justes, unités écrites**, et un
**diagnostic justifié** par les valeurs. Tu dois savoir :

1. **convertir** bits et octets, b/s et ses multiples, préfixes décimaux et binaires ;
2. **calculer** la durée d'une copie et distinguer **débit nominal** et **débit utile** ;
3. **citer et appliquer** les débits et longueurs d'Ethernet cuivre (10 Mb/s à 10 Gb/s, canal
   de {CHANNEL_MAX_M} m) et du coaxial historique (10BASE2, 10BASE5) ;
4. **calculer** en **décibels** un affaiblissement, et lire un **rapport de testeur**
   (affaiblissement, **NEXT**) ;
5. **expliquer** l'**impédance** (100 Ω, 50 Ω, 75 Ω) et les **réflexions** ;
6. **faire le bilan** d'une liaison en **fibre** (monomode ou multimode, portée du module) ;
7. **diagnostiquer** un problème de **duplex**, de **négociation**, et une liaison à
   **100 Mb/s au lieu de 1 Gb/s**.

Ce cours contient **{len(PROCEDURES)} procédures illustrées** :

{_procedures_list()}

## Exigences travaillées dans ce cours

{_req("AP-19")}
{_req("AP-20")}

Ce sont deux exigences **officielles** (consignes, p. 6). La fibre est traitée ici pour ses
**pertes** et sa **portée** (exigence AP-21, approfondie par le cours PR17, à venir). Le
**choix** et la **pose** des câbles sont étudiés en [PR13](/uaa/ampcr-pratique-pr13), le brochage
et les testeurs en [PR15](/uaa/ampcr-pratique-pr15), le coaxial BNC et la réflectométrie en
[PR16](/uaa/ampcr-pratique-pr16).

## Lien avec la théorie

Les notions de base sont présentées dans la théorie AMPCR :
[MC15 Câblage Ethernet et RJ45](/uaa/ampcr-mc15). Ce cours-ci est **pratique** : calculs à
poser, relevés et rapports de mesure à lire, diagnostics à rédiger, comme dans un dossier
d'examen.

## Comment travailler ce cours

Lis les chapitres dans l'ordre : chacun donne ses **objectifs**, la **théorie**, la
**procédure professionnelle** à rédiger, l'**erreur fréquente**, ce qu'on attend **à l'écrit**
et un **repère rapide**, avec un renvoi vers les exercices liés. Étudie ensuite les **cinq cas
résolus**, fais les **{len(PRACTICE_ITEMS)} exercices corrigés** (ici ou dans « S'entraîner »,
correction après envoi), puis passe le **mini-examen noté sur {EXAM_TOTAL_POINTS}** dans l'onglet
« Examen blanc ».

> **Important —** les relevés, rapports de testeur, sorties de commande et chantiers de ce cours
> sont des **supports fictifs** construits pour s'entraîner. Les valeurs citées viennent des
> normes nommées dans les sources (rédaction : {WRITTEN_AT}) ; **la fiche technique du
> fabricant et les normes en vigueur font foi**. Aucun exercice n'est une question officielle
> ni une question déjà posée par le Jury.
"""


def _units() -> str:
    gio = to_bits(1, "Gio") / 8
    return f"""**Objectifs** : écrire sans erreur une taille et un débit, et passer de l'un à l'autre.

## 1.1 Bit et octet

Le **bit** (symbole **b**) vaut 0 ou 1. L'**octet** (symbole **o**, *byte* **B** en anglais)
regroupe **8 bits**. Un **débit** se compte en **bits par seconde** (b/s, parfois écrit bps) ;
une **taille** (fichier, disque, mémoire) en **octets**. Majuscule ou minuscule changent tout :
**Mb** = mégabit, **MB** ou **Mo** = mégaoctet, huit fois plus.

{_fig(BYTE_FIGURE)}

## 1.2 Préfixes décimaux et binaires

{_units_table()}

Les **débits** utilisent toujours les préfixes **décimaux** : 1 Gb/s = 1 000 000 000 b/s. Les
fabricants de disques aussi : un disque de 1 To contient 10¹² octets. Certains systèmes
comptent les tailles en préfixes **binaires** : 1 Gio = {f"{int(gio):,}".replace(",", " ")} octets, soit
{pct(gio / 1e9 - 1)} de plus qu'un Go ; Windows écrit alors « Go » pour des Gio. Un disque de
1 To y apparaît comme environ « 931 Go ».

## 1.3 Conversions

- octets → bits : **× 8** ; bits → octets : **÷ 8** ;
- 100 Mb/s ÷ 8 = **12,5 Mo/s** ; 1 Gb/s ÷ 8 = **125 Mo/s** ;
- on garde les **puissances de 10** dans les calculs : 18 Go = 18 × 10⁹ o = 144 × 10⁹ b.

**Procédure professionnelle (à rédiger)** : écrire la valeur avec son unité → convertir vers
bits et b/s → calculer → reconvertir dans l'unité demandée.

**Erreur fréquente** : comparer des Mb/s à des Mo/s ; oublier le × 8 ; confondre Go et Gio.

**À l'écrit** : « **valeur + unité** à chaque ligne du calcul ».

**Repère rapide** : **b = bit · o = octet = 8 b · débits en décimal**. Exercices liés :
{_ex("E10", "E15")}.
"""


def _transfer() -> str:
    gross_mo_s = 1e9 / 8 / 1e6
    return f"""**Objectifs** : calculer la durée d'une copie et expliquer l'écart entre débit annoncé et
débit obtenu.

## 2.1 La formule

**Durée (s) = taille (bits) / débit utile (b/s)**. Le **débit nominal** est celui de la norme
ou de la carte (100 Mb/s, 1 Gb/s) ; le **débit utile** est ce qui reste pour les données :
**débit utile = débit nominal × rendement**.

{_fig(TRANSFER_FIGURE)}

## 2.2 Débit utile et débit nominal

Sur Ethernet, une partie du débit transporte autre chose que les données : chaque trame de
{ETH_MTU} octets de données occupe aussi le préambule et le délimiteur ({ETH_PREAMBLE_SFD} octets),
l'en-tête ({ETH_HEADER}), le contrôle FCS ({ETH_FCS}) et l'intervalle entre trames ({ETH_IFG}), soit
{ETH_WIRE_BYTES} octets sur la ligne ; dans la trame, IPv4 ({IPV4_HEADER}) et TCP ({TCP_HEADER})
laissent {TCP_PAYLOAD} octets aux données. Rendement maximal d'une copie TCP :
{TCP_PAYLOAD} / {ETH_WIRE_BYTES} ≈ **{pct(TCP_EFFICIENCY)}**. Sur un lien Gigabit, on obtient donc au mieux
environ {fr(gross_mo_s * TCP_EFFICIENCY, 0)} Mo/s (et non {fr(gross_mo_s, 0)}).

En pratique, le débit utile est souvent plus bas : **disques** lents, **processeur**, nombreux
**petits fichiers**, autres utilisateurs, **Wi-Fi**, antivirus, liaison en **half duplex**. Les
exercices donnent le **rendement mesuré** quand il compte.

**Procédure professionnelle (à rédiger)** : taille en bits → débit utile en b/s → division →
conversion → vérification de l'ordre de grandeur.

**Erreur fréquente** : diviser des octets par des bits par seconde ; prendre le débit nominal
pour un débit garanti ; conclure à une panne pour un débit utile normal.

**À l'écrit** : « {to_bits(18, "Go") / 1e9:g} × 10⁹ b / 900 × 10⁶ b/s = 160 s = 2 min 40 s ».

**Repère rapide** : **durée = bits / (b/s utiles) · rendement ≤ {pct(TCP_EFFICIENCY, 0)}**. Exercices
liés : {_ex("E01", "E09", "E10", "E15")}.
"""


def _ethernet() -> str:
    return f"""**Objectifs** : associer chaque norme Ethernet à son débit, à son câble et à sa longueur
maximale, et vérifier un projet.

## 3.1 Ethernet en paire torsadée

{_copper_table()}

Quel que soit le débit, le **canal** cuivre est limité à **{CHANNEL_MAX_M} m** : **lien
permanent** de {PERMANENT_LINK_MAX_M} m au plus (panneau → prise) + **cordons** de {CORDS_MAX_M} m au
plus en tout. Une catégorie supérieure convient toujours à un débit plus faible.

- **Cat5e** : 1 Gb/s sur 100 m (un ancien câble Cat5 n'est pas garanti : on le certifie) ;
- **Cat6A** : 10 Gb/s sur 100 m ;
- **Cat6** : 10 Gb/s seulement sur une **distance conditionnelle** : {TEN_G_CAT6_MAX_M} m au plus,
  {TEN_G_CAT6_WORST_M} m dans le pire cas, quand beaucoup de câbles voisins créent de la
  diaphonie entre câbles (TIA TSB-155) ; on **certifie** le lien avant de le promettre.

Les normes 2,5GBASE-T et 5GBASE-T (2016) visent 100 m sur Cat5e et Cat6 : complément, hors
du programme officiel.

## 3.2 Ethernet coaxial (historique)

{_coax_table()}

Les deux coaxiaux ont une impédance de **50 Ω**, des **terminateurs 50 Ω** à chaque bout et
fonctionnent en **half duplex** sur un **bus** partagé. Leur longueur vient de
l'**affaiblissement** : un segment ne doit pas perdre plus de **{fr(COAX_SEGMENT_MAX_DB)} dB à
10 MHz**. Le coaxial fin, plus atténuant, est donc limité à 185 m, l'épais à 500 m.

## 3.3 Portées comparées

{_fig(REACH_FIGURE)}

**Procédure professionnelle (à rédiger)** : débit voulu → norme → câble minimal → longueur
mesurée ≤ maximum → verdict ; au-delà : fibre ou équipement actif intermédiaire.

**Erreur fréquente** : croire qu'un meilleur câble permet plus de 100 m ; promettre 10 Gb/s sur
du Cat6 sans certification ; oublier la limite de {PERMANENT_LINK_MAX_M} m du lien permanent.

**À l'écrit** : « **débit** → **norme** → **catégorie** ; **longueur** ≤ {CHANNEL_MAX_M} m ».

**Repère rapide** : **100 m partout en cuivre · 1G = Cat5e · 10G = Cat6A (Cat6 ≤ 55 m) · 185 /
500 m en coaxial**. Exercices liés : {_ex("E04", "E14", "E17")}.
"""


def _decibels() -> str:
    return f"""**Objectifs** : calculer en décibels et lire l'affaiblissement d'une liaison.

## 4.1 L'affaiblissement en dB

Le long d'un câble, le signal perd de la puissance : c'est l'**atténuation** (ou
**affaiblissement**). On l'exprime en **décibels** :
**affaiblissement (dB) = 10 × log10(P entrée / P sortie)**. Pour des **tensions**, on écrit
20 × log10(U entrée / U sortie) : le résultat en dB est le même.

{_fig(DB_FIGURE)}

- **3 dB** ≈ puissance divisée par **2** ; **10 dB** = divisée par **10** ; **20 dB** = par
  **100** ;
- les dB **s'additionnent** le long d'une liaison : câble + connecteurs + cordons ;
- une puissance absolue s'écrit en **dBm** : **0 dBm = 1 mW**, 10 dBm = 10 mW, −20 dBm = 0,01 mW.

## 4.2 Ce qui fait varier l'atténuation

L'affaiblissement d'un câble est **proportionnel à sa longueur** (en dB) et **augmente avec la
fréquence** et la **température**. Valeurs maximales du câble seul, à 100 MHz et 20 °C
(TIA-568) :

{_cable_loss_table()}

Le récepteur est prévu pour un signal affaibli ; au-delà des longueurs de la norme, il ne
distingue plus le signal du bruit : erreurs, débit réduit, pas de lien.

**Procédure professionnelle (à rédiger)** : dB/100 m × longueur / 100 → total en dB (on ajoute
les connecteurs) → comparer à la limite → verdict.

**Erreur fréquente** : additionner des pourcentages au lieu des dB ; croire que 6 dB = 6 % de
perte.

**À l'écrit** : « {fr(CABLE_LOSS_100MHZ["Cat6"])} dB/100 m × 60 m = {fr(cable_loss_db(60, CABLE_LOSS_100MHZ["Cat6"]), 2)} dB ».

**Repère rapide** : **3 dB = ÷ 2 · 10 dB = ÷ 10 · les dB s'additionnent**. Exercices liés :
{_ex("E05", "E12", "E14")}.
"""


def _noise() -> str:
    return f"""**Objectifs** : expliquer bruit et diaphonie et lire un NEXT sur un rapport de testeur.

## 5.1 Bruit et rapport signal sur bruit

Le **bruit** est tout signal indésirable qui s'ajoute au signal utile : parasites
électromagnétiques (moteurs, néons, câbles d'énergie), **diaphonie**. Le récepteur fonctionne
tant que le signal reste nettement au-dessus du bruit : c'est le **rapport signal sur bruit**,
en dB. Une liaison longue (signal affaibli) dans un milieu perturbé (bruit fort) devient
instable.

## 5.2 Diaphonie : NEXT et FEXT

La **diaphonie** est le signal d'une paire qui passe sur une autre. La **paradiaphonie**
(**NEXT**, *near-end crosstalk*) se mesure **du côté de l'émetteur**, la **télédiaphonie**
(**FEXT**) à **l'autre extrémité**. Le testeur exprime le NEXT comme l'**affaiblissement du
signal parasite** : **plus la valeur en dB est grande, moins il y a de diaphonie**. Le NEXT se
dégrade surtout près des **raccordements** : paires **détorsadées** sur plus de 13 mm, prise mal
poinçonnée, câble écrasé.

{_fig(CROSSTALK_FIGURE)}

L'**ACR** (rapport atténuation/diaphonie) = **NEXT − affaiblissement**, en dB : il doit rester
positif, et plus il est grand, plus le signal se distingue de la diaphonie. À 10 Gb/s, la
**diaphonie entre câbles voisins** (exogène) compte aussi : c'est ce qui limite le Cat6.

## 5.3 Blindage

Un **écran** (feuille ou tresse) relié à la terre protège des parasites extérieurs et de la
diaphonie entre câbles ; un écran **par paire** (U/FTP, S/FTP) réduit aussi la diaphonie entre
paires. Il n'est efficace que **continu** et **relié à la terre** (voir
[PR13](/uaa/ampcr-pratique-pr13)).

**Procédure professionnelle (à rédiger)** : valeur mesurée face à la limite (NEXT ≥ limite) →
extrémité concernée → cause au raccordement → reprise → nouveau test.

**Erreur fréquente** : croire qu'un petit NEXT est bon ; chercher le défaut au milieu du câble
alors que le NEXT mauvais est mesuré à une extrémité.

**À l'écrit** : « NEXT 29,8 dB < 35,3 dB côté bureau → détorsadage à la prise → refaire ».

**Repère rapide** : **NEXT grand = bon · ACR = NEXT − affaiblissement · raccordement d'abord**.
Exercices liés : {_ex("E12", "E18")}.
"""


def _impedance() -> str:
    return f"""**Objectifs** : expliquer l'impédance caractéristique et prévoir une réflexion.

## 6.1 Impédance caractéristique

Chaque câble a une **impédance caractéristique**, fixée par sa **géométrie** (écart et diamètre
des conducteurs, isolant) et indépendante de sa longueur : **{TWISTED_PAIR_OHM} Ω** (± {TWISTED_PAIR_TOLERANCE_OHM} Ω)
pour la **paire torsadée** Ethernet, **50 Ω** pour le coaxial **Ethernet** (10BASE2, 10BASE5),
la radio et la mesure, **75 Ω** pour la **vidéo** et la **télévision**. L'ancien câble IBM type 1
(STP) faisait 150 Ω. Ce n'est **pas** une résistance mesurable à l'ohmmètre.

## 6.2 Réflexions

Quand le signal rencontre une impédance différente (autre câble, connecteur, extrémité ouverte,
câble écrasé), une partie **revient** vers l'émetteur. Le **coefficient de réflexion** vaut
**Γ = (Zcharge − Zligne) / (Zcharge + Zligne)** ; la part de puissance réfléchie vaut **Γ²**,
l'**affaiblissement de réflexion** (*return loss*) −20 × log10 |Γ| (plus il est grand, mieux
c'est).

{_fig(REFLECTION_FIGURE)}

{_reflection_table()}

D'où les règles : **une seule impédance** sur toute la liaison (câble et connecteurs),
**terminateurs** à l'impédance du câble aux extrémités d'un bus coaxial, câble jamais écrasé ni
plié trop serré. Un réflectomètre (TDR) utilise justement ces réflexions pour localiser un
défaut : voir [PR16](/uaa/ampcr-pratique-pr16).

**Procédure professionnelle (à rédiger)** : relever les impédances de chaque maillon → calculer
Γ → expliquer le symptôme (image doublée, erreurs) → rétablir une impédance unique.

**Erreur fréquente** : mélanger 50 et 75 Ω « parce que les fiches BNC se ressemblent » ;
mesurer l'impédance à l'ohmmètre.

**À l'écrit** : « Γ = (75 − 50) / (75 + 50) = 0,2 → {fr(reflected_power_pct(0.2), 1)} % réfléchis ».

**Repère rapide** : **100 Ω paire · 50 Ω réseau coaxial · 75 Ω vidéo · ouvert +1 · court-circuit
−1**. Exercices liés : {_ex("E08", "E14")}.
"""


def _fibre() -> str:
    return f"""**Objectifs** : choisir monomode ou multimode et faire le bilan d'une liaison optique.

## 7.1 Monomode et multimode

La fibre transporte de la **lumière** : elle est insensible aux parasites électriques et isole
électriquement deux bâtiments. Le **multimode** (cœur de 50 ou 62,5 µm) est utilisé à 850 nm
avec des émetteurs bon marché, sur quelques centaines de mètres ; le **monomode** (cœur d'environ
9 µm) avec des lasers à 1 310 ou 1 550 nm, sur des kilomètres.

{_fibre_types_table()}

## 7.2 Pertes

{_fibre_loss_table()}

Chaque **paire de connecteurs** raccordée perd au plus **{fr(CONNECTOR_PAIR_DB, 2)} dB**, chaque
**épissure** **{fr(SPLICE_DB)} dB** (TIA-568). Un connecteur sale perd bien davantage : on le
**nettoie** et on l'**inspecte** avant de le brancher.

## 7.3 La portée dépend du module optique

La portée n'est pas une propriété de la fibre seule : elle dépend du **module optique**
(émetteur-récepteur) **et** du type de fibre. En multimode, la **dispersion modale** limite la
longueur même quand les pertes sont faibles.

{_reach_table()}

Le **budget** du module (puissance émise minimale − sensibilité du récepteur, ou budget de canal
de la fiche) doit couvrir la perte de la liaison ; la **marge** est la différence. Un module
longue portée sur une liaison très courte peut au contraire **saturer** le récepteur : on suit
la fiche (atténuateur si demandé).

{_fig(BUDGET_FIGURE)}

{_fig(FIBRE_FIGURE)}

Le raccordement, les connecteurs et la pose de la fibre sont l'objet du cours PR17 (à venir).

**Procédure professionnelle (à rédiger)** : relever → valeurs → perte → portée et budget →
marge → verdict et mesure.

**Erreur fréquente** : vérifier le budget en oubliant la portée (10GBASE-SR à 450 m sur OM3) ;
oublier les connecteurs ; mélanger multimode et monomode.

**À l'écrit** : « 0,22 km × 3,5 + 2 × 0,75 = {fr(BUDGET_EXAMPLE.loss_db, 2)} dB ≤ {fr(BUDGET_EXAMPLE.budget_db)} dB ;
220 m ≤ 300 m → conforme ».

**Repère rapide** : **multimode 850 nm, centaines de m · monomode 1 310 nm, km · 0,75 dB par
connecteur · portée ET budget**. Exercices liés : {_ex("E03", "E07", "E13")}.
"""


def _duplex() -> str:
    return f"""**Objectifs** : expliquer half et full duplex, l'auto-négociation et les collisions, et
reconnaître un désaccord de duplex.

## 8.1 Half duplex, full duplex, collisions

- **Half duplex** : on émet **ou** on reçoit, chacun son tour. C'était le cas des bus
  **coaxiaux** et des **hubs** : tous les postes partageaient le support. Deux émissions
  simultanées provoquaient une **collision** ; la méthode **CSMA/CD** consistait à écouter avant
  d'émettre, détecter la collision, attendre un délai aléatoire et réémettre. Plus il y avait de
  postes actifs, plus le débit utile chutait.
- **Full duplex** : on émet **et** on reçoit **en même temps**, sur des paires séparées (ou les
  4 paires en Gigabit), avec un **switch** : **plus de collision**, chaque port a son débit.

## 8.2 Auto-négociation

À la connexion, deux ports en **auto-négociation** s'annoncent leurs capacités et choisissent la
**meilleure vitesse commune**, en **full duplex**. Le Gigabit (1000BASE-T) **exige**
l'auto-négociation. Si un seul côté est **forcé**, l'autre détecte la vitesse mais **pas le
duplex** : il se met en **half duplex**. C'est le **désaccord de duplex** : collisions tardives
côté half, erreurs CRC côté full, lenteurs et coupures.

{_negotiation_table()}

**Règle** : laisser les **deux côtés en auto** ; si un équipement impose un réglage fixe, forcer
**les deux côtés à l'identique**.

**Procédure professionnelle (à rédiger)** : relever vitesse et duplex des deux côtés → repérer
un réglage forcé d'un seul côté → corriger → vérifier les compteurs d'erreurs.

**Erreur fréquente** : forcer « 100 full » sur un seul côté pour « stabiliser » ; remplacer un
hub par un autre hub.

**À l'écrit** : « auto face à forcé → half / full → désaccord → remettre les deux en auto ».

**Repère rapide** : **auto + auto = OK · auto + forcé = half · hub = collisions · switch = full
duplex**. Exercices liés : {_ex("E06", "E16", "E19")}.
"""


def _diagnosis() -> str:
    return f"""**Objectifs** : diagnostiquer par écrit une liaison établie à 100 Mb/s au lieu de 1 Gb/s.

## 9.1 Les causes possibles

1. **Un équipement limité** : switch, carte, prise de téléphone IP ou ancien switch
   intermédiaire à 100 Mb/s ;
2. **Un réglage forcé** à 100 Mb/s (carte ou port), parfois avec un désaccord de duplex ;
3. **Le câble** : le Gigabit utilise les **4 paires**, le 100 Mb/s seulement **1-2 et 3-6**.
   Une paire **4-5 ou 7-8** coupée ou mal sertie, un cordon à 2 paires, un câble trop long ou
   de mauvaise qualité : la carte **rétrograde** à 100 Mb/s (*downshift*) au lieu de couper le
   lien.

## 9.2 Lire l'état de la liaison

- **Linux** : `ethtool enp3s0` affiche `Speed`, `Duplex`, `Auto-negotiation` et, souvent, les
  modes annoncés par l'autre côté (`Link partner advertised link modes`) ;
- **Windows** : `Get-NetAdapter` (colonne `LinkSpeed`) ou l'état de la carte réseau ;
- **Switch** : l'état du port (vitesse, duplex) et ses compteurs d'erreurs.

Si les deux côtés **annoncent** 1000BASE-T en auto mais que le lien est à 100 Mb/s, ce n'est
ni un réglage ni un équipement : on cherche dans le **câble**.

{_fig(LINK_FIGURE)}

**Procédure professionnelle (à rédiger)** : relever → configuration → capacités → câble
(8 conducteurs) → isoler (cordon, port) → contrôler et consigner.

**Erreur fréquente** : remplacer la carte réseau avant de tester le câble ; tester seulement la
continuité de 4 conducteurs.

**À l'écrit** : « annonces 1000/Full des deux côtés, Speed 100 → paire 7-8 ouverte → reprise
→ Speed 1000 ».

**Repère rapide** : **Gigabit = 4 paires · 100 Mb/s = 2 paires · annonces OK + 100 Mb/s = câble**.
Exercices liés : {_ex("E02", "E06", "E11")}.
"""


def _examples() -> str:
    blocks: list[str] = []
    for title, situation, steps, conclusion in CASES:
        lines = "\n".join(f"{i}. {line}" for i, line in enumerate(steps, start=1))
        blocks.append(
            f"""## {title}

**Situation.** {situation}

**Résolution.**

{lines}

**Conclusion rédigée.** « {conclusion} »
"""
        )
    return (
        "Cinq dossiers chiffrés, résolus pas à pas avec les règles du cours. Chaque nombre est "
        "calculé, avec son unité, comme dans les exercices.\n\n" + "\n".join(blocks)
    )


def _pitfalls() -> str:
    return f"""> **Confondre Mb/s et Mo/s** : 1 Gb/s ÷ 8 = 125 Mo/s au maximum.

> **Confondre Go et Gio** : 1 Gio = 1 073 741 824 octets ; Windows écrit « Go ».

> **Prendre le débit nominal pour le débit utile** : au mieux {pct(TCP_EFFICIENCY, 0)} en TCP sur
> Ethernet, souvent moins.

> **Croire qu'un meilleur câble dépasse {CHANNEL_MAX_M} m** : la limite vaut pour toutes les
> catégories.

> **Promettre 10 Gb/s sur du Cat6** au-delà de {TEN_G_CAT6_MAX_M} m, ou sans certification.

> **Additionner des pourcentages de perte** au lieu des dB.

> **Lire un NEXT à l'envers** : une grande valeur en dB est bonne.

> **Mélanger 50 Ω et 75 Ω**, ou laisser un bus coaxial sans terminateur.

> **Oublier la portée du module** dans un bilan optique, ou oublier les connecteurs.

> **Forcer vitesse et duplex d'un seul côté** : désaccord de duplex.

> **Accuser la carte réseau** d'un lien à 100 Mb/s sans tester les 8 conducteurs.
"""


def _exercises_intro() -> str:
    return f"""{len(PRACTICE_ITEMS)} exercices corrigés : remises en ordre (durée d'une copie, liaison à
100 Mb/s, bilan optique), classements (norme et longueur, décibels, auto-négociation, support à
10 Gb/s, réflexions), documents chiffrés (durée d'une sauvegarde, débit mesuré, sortie
d'ethtool, rapport de testeur, bilan monomode, segments coaxiaux) et rédactions (1 Gb/s et Mo/s,
désaccord de duplex, Cat6 à 10 Gb/s, NEXT, hub). Rédige ta réponse sur papier **avant** d'ouvrir
le corrigé, calculs et unités compris ; toute réponse équivalente et justifiée est acceptée. Ces
mêmes exercices sont proposés dans [S'entraîner](/uaa/{PR14_SLUG}/practice), avec correction après
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
    return f"""Le mini-examen se passe dans l'onglet [Examen blanc](/uaa/{PR14_SLUG}/exam) : **10 questions à réponse
libre**, chacune notée sur **2 points**, soit une note sur **{EXAM_TOTAL_POINTS}**. Les
questions ne figurent pas dans ce cours.

| N° | Thème | Type | Points |
|---|---|---|---|
{rows}

**Déroulement.** Chaque question est une situation complète : toutes les données nécessaires
sont dans l'énoncé et ses documents (relevés et sorties de commande fictifs). Une calculatrice
n'est pas nécessaire. **Aucune correction n'est visible pendant la passation** ; tes réponses
sont enregistrées au fur et à mesure. Après l'envoi, chaque réponse est corrigée selon le
**barème analytique** de la question (critères et points), puis tu vois ta note sur
{EXAM_TOTAL_POINTS}, le corrigé et le barème.

**Ce que valorise le barème.** Le **calcul posé avec ses unités**, la **règle** appliquée, le
**diagnostic justifié** par les valeurs et la **correction** proposée — pas la récitation de
sigles. Un résultat arrondi raisonnablement ou une autre formulation juste est accepté.

**Nature de la correction.** Les réponses rédigées reçoivent une **proposition de correction
automatique** (assistée par IA) appuyée sur le barème : c'est un repère d'entraînement, pas une
note officielle ; en cas de doute, compare ta réponse au corrigé.
"""


def _memo() -> str:
    return f"""## Mémo

- **Unités** : b = bit, o = octet = 8 b ; débits en b/s et préfixes **décimaux** ; Gio = 2³⁰ o.
- **Durée** = taille en bits / débit utile ; débit utile = nominal × rendement (≤ {pct(TCP_EFFICIENCY, 0)}
  en TCP sur Ethernet).
- **Cuivre** : canal ≤ {CHANNEL_MAX_M} m = lien permanent ≤ {PERMANENT_LINK_MAX_M} m + cordons ≤ {CORDS_MAX_M} m ;
  10/100 Mb/s : 2 paires ; 1 Gb/s : 4 paires, Cat5e ; 10 Gb/s : Cat6A (Cat6 ≤ {TEN_G_CAT6_MAX_M} m,
  {TEN_G_CAT6_WORST_M} m au pire, certifié).
- **Coaxial** : 10BASE2 RG-58 185 m, 10BASE5 500 m ; 50 Ω, terminateurs ; ≤ {fr(COAX_SEGMENT_MAX_DB)} dB à 10 MHz.
- **dB** : 10 × log10(Pe/Ps) ; 3 dB = ÷ 2, 10 dB = ÷ 10 ; on additionne ; 0 dBm = 1 mW.
- **Diaphonie** : NEXT côté émetteur, FEXT à l'autre bout ; grand NEXT = bon ; ACR = NEXT −
  affaiblissement ; détorsadage ≤ 13 mm.
- **Impédance** : 100 Ω paire, 50 Ω coaxial réseau, 75 Ω vidéo ; Γ = (Zc − Z0)/(Zc + Z0) ;
  ouvert +1, court-circuit −1, adapté 0.
- **Fibre** : multimode 3,5 dB/km à 850 nm, monomode OS2 0,4 dB/km ; {fr(CONNECTOR_PAIR_DB, 2)} dB
  par connecteur, {fr(SPLICE_DB)} dB par épissure ; vérifier **portée du module** et **budget**.
- **Duplex** : auto + auto ; auto face à forcé = half → désaccord ; hub = collisions (CSMA/CD).
- **100 Mb/s au lieu de 1 Gb/s** : équipement limité, réglage forcé, ou paire 4-5 / 7-8 en
  défaut.

## Glossaire des termes employés

- **ACR** : NEXT − affaiblissement, en dB ; écart entre signal utile et diaphonie.
- **Affaiblissement (atténuation)** : perte de puissance le long d'une liaison, en dB.
- **Auto-négociation** : échange des capacités entre deux ports pour choisir vitesse et duplex.
- **Budget optique** : perte maximale qu'un module optique accepte entre émetteur et récepteur.
- **CSMA/CD** : méthode d'accès des réseaux Ethernet partagés (écoute, détection de collision,
  réémission).
- **Débit nominal / utile** : débit de la norme / débit réellement disponible pour les données.
- **Décibel (dB)** : unité logarithmique d'un rapport de puissances ; dBm : puissance rapportée
  à 1 mW.
- **Diaphonie (NEXT, FEXT)** : signal d'une paire passé sur une autre, mesuré du côté de
  l'émetteur (NEXT) ou à l'autre bout (FEXT).
- **Duplex (half, full)** : émission et réception à tour de rôle (half) ou simultanées (full).
- **Impédance caractéristique** : propriété d'un câble fixée par sa géométrie (100, 50, 75 Ω).
- **Réflexion** : partie du signal renvoyée par un changement d'impédance.
"""


def _sources() -> str:
    return f"""## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), p. 6 : « Les débits binaires des câbles » (AP-19) et « Les
  caractéristiques des câbles : atténuation, notion d'impédance, sensibilité aux parasites,
  blindage, précautions d'utilisation, avantages, inconvénients…, longueur maximale d'un tronçon
  suivant le débit, connecteurs » (AP-20) ; la fibre et ses caractéristiques (AP-21). Copie
  versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
  Programme officiel n° 345/2007/249 (option AMPCR).
- **IEEE 802.3** : 10BASE5 et 10BASE2 (clauses 8 et 10 : 500 et 185 m, 8,5 dB à 10 MHz),
  10BASE-T, 100BASE-TX, 1000BASE-T, 10GBASE-T ; 1000BASE-SX/LX, 10GBASE-SR/LR (portées par
  type de fibre) ; auto-négociation (clause 28) et détection parallèle ; format de trame.
- **TIA-568** et **TIA TSB-155** : canal de 100 m, lien permanent de 90 m ; affaiblissement
  maximal du câble à 100 MHz (Cat5e 22,0 dB, Cat6 19,8 dB, Cat6A 19,1 dB pour 100 m) ;
  10GBASE-T sur Cat6 limité à 55 m (37 m dans le pire cas) ; impédance 100 Ω ± 15 Ω ; fibre :
  3,5 et 1,5 dB/km en multimode, 0,75 dB par connecteur, 0,3 dB par épissure.
- **ISO/IEC 11801** : fibres OM1 à OM4, OS1 (1,0 dB/km) et OS2 (0,4 dB/km).

Les valeurs sont celles de {WRITTEN_AT} ; les normes évoluent et les fabricants précisent
leurs propres valeurs : **la fiche technique et les normes en vigueur font foi**. Les tableaux,
barres, coefficients, bilans et procédures du cours sont **produits par programme** depuis des
données **vérifiées par des tests automatiques** ; aucun schéma n'est tiré d'une image générée
ni d'une photographie.

## Compléments pédagogiques (non imposés par la liste officielle)

La p. 6 cite les débits et les caractéristiques des câbles. Sont des **compléments**, signalés
comme tels, utiles pour traiter un dossier écrit :

- le calcul du rendement d'une copie TCP et les préfixes binaires ;
- l'ACR, la diaphonie exogène, le coefficient de réflexion et l'affaiblissement de réflexion ;
- le bilan optique et la règle de choix d'un support à 10 Gb/s (cuivre jusqu'à 100 m dans un
  bâtiment, puis OM3, OM4, monomode) : **convention du cours** ;
- 2,5GBASE-T et 5GBASE-T, et les commandes `ethtool` et `Get-NetAdapter`.

## Supports fictifs

Les relevés, rapports de testeur, sorties de commande, budgets de modules et entreprises de ce
cours sont **fictifs** et reconstitués pour l'entraînement ; ils ne décrivent aucun client réel.
Aucune n'est une question officielle ou déjà posée par le Jury. Pour un cas réel, on utilise la
fiche du fabricant et un appareil de mesure.
"""


def pr14_course_sections() -> list[tuple[str, str]]:
    """Blocs du cours (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("PR14 — Objectifs et place dans l'épreuve", _objectives()),
        ("PR14 — 1. Bits, octets, b/s et multiples décimaux ou binaires", _units()),
        ("PR14 — 2. Durée d'une copie : débit nominal et débit utile", _transfer()),
        ("PR14 — 3. Ethernet 10/100/1000/10G et coaxial : débits et longueurs", _ethernet()),
        ("PR14 — 4. Atténuation et décibels", _decibels()),
        ("PR14 — 5. Bruit, diaphonie NEXT et blindage", _noise()),
        ("PR14 — 6. Impédance et réflexions : 100 Ω, 50 Ω, 75 Ω", _impedance()),
        ("PR14 — 7. Fibre monomode ou multimode : pertes et portée", _fibre()),
        ("PR14 — 8. Duplex, auto-négociation et collisions", _duplex()),
        ("PR14 — 9. Diagnostic : liaison à 100 Mb/s au lieu de 1 Gb/s", _diagnosis()),
        ("PR14 — Exemples : cinq cas chiffrés résolus", _examples()),
        ("PR14 — Pièges et erreurs fréquentes", _pitfalls()),
        (f"PR14 — Exercices corrigés ({len(PRACTICE_ITEMS)}) et leurs corrigés", _exercises_intro()),
        ("PR14 — Mini-examen noté sur 20 : mode d'emploi", _mini_exam()),
        ("PR14 — Fiche mémo et glossaire", _memo()),
        ("PR14 — Sources et compléments pédagogiques", _sources()),
    ]
