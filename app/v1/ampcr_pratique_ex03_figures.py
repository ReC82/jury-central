"""EX03 « Examen blanc écrit — câblage RJ45, BNC et fibre » — données des dossiers et schémas
(ticket #232).

Une seule source pour le sujet affiché, les documents des questions et le corrigé ; chaque
verdict est calculé avec la règle **du cours** qui l'enseigne :
- **partie 1** : fiche RJ45 contrôlée contre T568A/T568B (`T568A`, `T568B`, `links_between`,
  `split_pairs`, PR15) ; cordon droit ou croisé selon les ports (MDI, MDI-X, Auto MDI-X, PR15) ;
- **dossier A** (cuivre) : choix du câble (`choose`, `Need`, PR13), certification des liens
  (`channel_errors`, PR13 ; `copper_verdict`, PR14 ; affichage de testeur, PR15), relevé de
  pose (`Run`, `run_errors`, `min_bend_radius_mm`, PR13) ;
- **dossier B** (coaxial) : bus 10BASE2 (`Bus`, `bus_errors`, `reflection_coefficient`, PR16),
  lectures d'ohmmètre (`ohmmeter_reading`, PR16) ;
- **dossier C** (fibre) : choix des liaisons (`choose_10g`, PR14 ; `module_verdict`, PR17),
  bilan et photométrie (`max_link_loss_db`, `measured_loss_db`, `photometry_verdict`,
  `rx_power_dbm`, `rx_status`, PR17), réflectométrie (`otdr_event_kind`, `break_position_m`,
  PR17).

Toutes les situations, entreprises, repères et mesures sont **fictifs**. Les quatre schémas
utilisés dans les questions sont aussi enregistrés en fichiers statiques
(`app/static/img/ampcr-pratique/`) ; un test vérifie qu'ils sont identiques au SVG produit ici.
Les schémas du sujet ne donnent **aucun verdict** (pas de ✓ / ✗) : c'est au candidat de
conclure ; ils restent lisibles imprimés en noir et blanc (tout est écrit en texte).
"""

from html import escape

from app.v1.ampcr_pratique_pr13_figures import (
    EMI_HIGH,
    EMI_LOW,
    EMI_MEDIUM,
    SERVICE_VIDEO,
    Need,
    Run,
    channel_errors,
    choose,
    label_for,
    min_bend_radius_mm,
    run_errors,
)
from app.v1.ampcr_pratique_pr14_figures import (
    M_10G_COPPER,
    M_10G_LR,
    choose_10g,
    copper_verdict,
)
from app.v1.ampcr_pratique_pr15_figures import (
    PLUG_ORIENTATION,
    links_between,
    pinout_svg,
    split_pairs,
    wiremap_svg,
)
from app.v1.ampcr_pratique_pr16_figures import (
    ATTACH_STUB,
    ATTACH_T,
    FAULT_SHORT,
    Bus,
    BusEnd,
    Span,
    _stations_bus,
    bus_errors,
    ohmmeter_reading,
    reflection_coefficient,
)
from app.v1.ampcr_pratique_pr17_figures import (
    C_OK,
    LR_SPEC,
    OtdrEvent,
    OtdrTrace,
    attenuation_for,
    break_position_m,
    dbm_fr,
    fr,
    max_link_loss_db,
    measured_loss_db,
    module_verdict,
    otdr_event_kind,
    photometry_verdict,
    rx_power_dbm,
    rx_status,
    trace_points,
)
from app.v1.ampcr_pratique_pr17_figures import (
    min_bend_radius_mm as min_bend_radius_fibre_mm,
)
from app.v1.ampcr_pratique_visuals import T568A, T568B, Figure, _svg, _text_lines, _wrap

STATIC_DIR_REF = "img/ampcr-pratique"
SCREEN_WIDTH = 56  # caractères au plus par ligne de capture (lisible sur mobile, comme les cours)
_STROKE = "#33415c"

# =============================================================================================
# Partie 1 — fiche RJ45 réalisée par un stagiaire (question X01)
# =============================================================================================

# Le stagiaire voulait du T568B ; il a inversé les deux fils de la paire bleue (4-5) et ceux de
# la paire marron (7-8). Les paires restent sur leurs positions : pas de paire séparée.
TARGET_STANDARD = "T568B"
MADE_PLUG: tuple[str, ...] = (
    "blanc-orange", "orange", "blanc-vert", "blanc-bleu", "bleu", "vert", "marron", "blanc-marron",
)
WRONG_PINS = tuple(pin for pin, (made, ref) in enumerate(zip(MADE_PLUG, T568B, strict=True), start=1) if made != ref)
MADE_PLUG_SPLIT = tuple(split_pairs(MADE_PLUG))  # vide : aucune paire séparée
# Testeur : extrémité 1 = fiche correcte en T568B, extrémité 2 = fiche du stagiaire.
MADE_PLUG_LINKS = links_between(T568B, MADE_PLUG)

PLUG_FIGURE = Figure(
    key="ex03-fiche-stagiaire",
    title="Document 1 — Fiche RJ45 sertie par le stagiaire",
    alt=(
        f"{PLUG_ORIENTATION} Ordre des fils relevé de la broche 1 à la broche 8 : "
        + ", ".join(f"broche {pin} {wire.replace('-', '/')}" for pin, wire in enumerate(MADE_PLUG, start=1))
        + ". Le schéma ne donne aucun verdict."
    ),
    caption=(
        "Fiche fictive relevée sur le cordon du stagiaire, dans l'orientation de lecture du cours : contacts "
        "vers soi, languette dessous, broche 1 à gauche. Les couleurs sont aussi écrites en toutes lettres."
    ),
    svg=pinout_svg(MADE_PLUG, title="Fiche relevée (cordon du stagiaire)"),
)
PLUG_FIGURE_FILE = f"{STATIC_DIR_REF}/ex03-fiche-stagiaire.svg"

# =============================================================================================
# Partie 1 — cordon droit ou croisé (question X02)
# =============================================================================================

MDI = "MDI (carte réseau, PC, imprimante, routeur)"
MDI_X = "MDI-X (switch, hub)"
STRAIGHT = "Droit (même norme aux deux bouts)"
CROSSOVER = "Croisé (T568A à un bout, T568B à l'autre)"


def cable_for(port_a: str, port_b: str, *, auto_mdix: bool) -> str:
    """Règle de PR15 : un port MDI se relie à un port MDI-X par un cordon droit ; deux ports de
    même type se relient par un croisé, sauf si l'un des deux fait l'Auto MDI-X (il inverse
    lui-même émission et réception) : un cordon droit suffit alors, et c'est celui qu'on pose."""
    if port_a != port_b or auto_mdix:
        return STRAIGHT
    return CROSSOVER


# (liaison, port A, port B, Auto MDI-X disponible sur au moins un des deux)
LINKS: tuple[tuple[str, str, str, bool], ...] = (
    ("1. PC de l'accueil → prise murale → panneau de brassage → switch", MDI, MDI_X, False),
    ("2. Deux anciens switchs 10/100 Mb/s sans Auto MDI-X ni port « uplink »", MDI_X, MDI_X, False),
    ("3. Deux PC avec cartes 1 Gb/s (Auto MDI-X indiqué dans la fiche technique), reliés directement", MDI, MDI, True),
    ("4. Deux anciens PC à cartes 100 Mb/s sans Auto MDI-X, reliés directement", MDI, MDI, False),
)
LINK_CABLES = {name: cable_for(a, b, auto_mdix=auto) for name, a, b, auto in LINKS}
CROSSOVER_LINKS = links_between(T568A, T568B)  # 1→3, 2→6, 3→1, 6→2 ; 4, 5, 7, 8 droits

# =============================================================================================
# Dossier A — Imprimerie Lambert : choix des câbles (question X03)
# =============================================================================================

# (repère, trajet, besoin du cours, description de l'environnement)
CABLE_NEEDS: tuple[tuple[str, str, Need, str], ...] = (
    ("L1", "Bureaux de l'étage → baie (12 prises)", Need(rate_gbps=1, length_m=45, emi=EMI_LOW),
     "1 Gb/s, 45 m au plus, bureaux sans machine"),
    ("L2", "Serveur → switch cœur, local technique", Need(rate_gbps=10, length_m=25, emi=EMI_MEDIUM, grounded=True),
     "10 Gb/s, 25 m, onduleur et climatisation à proximité ; baie reliée à la terre"),
    ("L3", "Atelier des presses → baie", Need(rate_gbps=1, length_m=60, emi=EMI_HIGH, grounded=True),
     "1 Gb/s, 60 m, moteurs des presses et variateurs ; terre de l'atelier disponible"),
    ("L4", "Caméra analogique du quai → enregistreur", Need(service=SERVICE_VIDEO, length_m=35),
     "Vidéo analogique existante (sortie BNC 75 Ω), 35 m"),
    ("L5", "Baie → magasin de papier au fond du site", Need(rate_gbps=1, length_m=140, emi=EMI_LOW),
     "1 Gb/s, 140 m de parcours mesuré"),
)
CABLE_CHOICES = {ref: choose(need) for ref, _path, need, _env in CABLE_NEEDS}

# =============================================================================================
# Dossier A — certification des liens (question X04)
# =============================================================================================

# Prise mal raccordée : panneau poinçonné en T568B, prise murale en T568A → liaison croisée.
CERT_PORT_FIGURE = label_for(1, 1, 9)
CERT_FIGURE_LINKS = links_between(T568B, T568A)
CERT_FIGURE_NOTE = "Affichage de testeur fictif ; présentation variable selon le modèle."

CERT_FIGURE = Figure(
    key="ex03-testeur-b1-p1-09",
    title=f"Dossier A, document A4 — Testeur sur le lien {CERT_PORT_FIGURE}",
    alt=(
        f"Affichage de testeur fictif sur le lien {CERT_PORT_FIGURE} (testeur côté panneau, bouchon distant "
        "côté prise murale) : "
        + ", ".join(f"broche {a} vers broche {b}" for a, b in CERT_FIGURE_LINKS)
        + ". Résultat affiché : échec, câblage."
    ),
    caption="Lien permanent panneau → prise de bureau, testé à la réception du chantier (affichage fictif).",
    svg=wiremap_svg(
        CERT_FIGURE_LINKS,
        title=f"Wiremap : lien {CERT_PORT_FIGURE}",
        verdict="RÉSULTAT : ÉCHEC — câblage.",
        left="Testeur (panneau)",
        right="Bouchon (prise)",
        notes=(CERT_FIGURE_NOTE,),
    ),
)
CERT_FIGURE_FILE = f"{STATIC_DIR_REF}/ex03-testeur-b1-p1-09.svg"

# Autres liens du rapport de certification.
LONG_PORT = label_for(1, 1, 3)
LONG_PERMANENT_M = 96
LONG_CORDS_M = 5  # 2 m côté baie + 3 m côté bureau
LONG_ERRORS = channel_errors(LONG_PERMANENT_M, LONG_CORDS_M)
OPEN_PORT = label_for(1, 1, 7)
SPLIT_PORT = label_for(1, 1, 12)
TEN_G_PORT = label_for(1, 1, 14)
TEN_G_CATEGORY = "Cat6"
TEN_G_LENGTH_M = 70
TEN_G_VERDICT = copper_verdict("10GBASE-T", TEN_G_CATEGORY, TEN_G_LENGTH_M)

CERT_ROWS: tuple[tuple[str, str, str], ...] = (
    (LONG_PORT, f"Wiremap réussi ; lien permanent mesuré {LONG_PERMANENT_M} m", "Cordons prévus : 2 m côté baie, 3 m côté bureau"),
    (OPEN_PORT, "Wiremap : échec — broche 7 sans liaison", "Lien de 38 m"),
    (SPLIT_PORT, "Wiremap 1→1 … 8→8 réussi ; diaphonie (NEXT) : échec sur 3-6 et 4-5", "Lien de 52 m"),
    (TEN_G_PORT, f"Wiremap réussi ; câble marqué « {TEN_G_CATEGORY} U/UTP », {TEN_G_LENGTH_M} m",
     "Lien prévu à 10 Gb/s (10GBASE-T) vers le poste de PAO"),
)

# =============================================================================================
# Dossier A — relevé de pose (question X05)
# =============================================================================================

RUNS: tuple[Run, ...] = (
    Run("T1 — Bureaux, goulotte (U/UTP, Ø 5,6 mm)", "U/UTP", 5.6, 15, 80, 120, "b"),
    Run("T2 — Atelier, chemin de câbles (S/FTP, Ø 7,8 mm)", "S/FTP", 7.8, 70, 160, 60, "c"),
    Run("T3 — Local technique (F/UTP, Ø 7,2 mm)", "F/UTP", 7.2, 60, 90, 40, "b"),
    Run("T4 — Quai, caméra (coaxial RG-59, Ø 6,1 mm)", None, 6.1, 40, 50, None),
    Run("T5 — Magasin, goulotte (U/UTP, Ø 5,6 mm)", "U/UTP", 5.6, 30, 100, 80, "b", metal_divider=True),
)
RUN_ERRORS = {run.name: run_errors(run) for run in RUNS}
RUN_MIN_RADIUS = {run.name: min_bend_radius_mm(run.diameter_mm, run.designation) for run in RUNS}


def run_rows() -> tuple[tuple[str, ...], ...]:
    rows = []
    for run in RUNS:
        power = "aucun" if run.power_distance_mm is None else (
            f"{run.power_distance_mm:g} mm"
            + (f", classe de séparation « {run.separation_class} »" if run.separation_class else "")
            + (", cloison métallique" if run.metal_divider else ", sans cloison")
        )
        pull = "—" if run.designation is None else f"{run.pull_n:g} N"
        rows.append((run.name, f"{fr(run.bend_radius_mm)} mm", pull, power))
    return tuple(rows)


# =============================================================================================
# Dossier B — Musée « Octet » : bus 10BASE2 de la salle rétro (question X06)
# =============================================================================================

MUSEUM_NAMES = ("Poste 1", "Poste 2", "Poste 3", "Poste 4", "Serveur")
MUSEUM_LENGTHS = (6, 9, 0.3, 7)
MUSEUM_STUB = "Poste 3"
MUSEUM_STUB_M = 2
MUSEUM_RG59_SPAN = 1  # tronçon Poste 2 → Poste 3
MUSEUM_BUS = _stations_bus(
    MUSEUM_NAMES, MUSEUM_LENGTHS, first=BusEnd(50, grounded=True), last=BusEnd(75),
    attachments={MUSEUM_STUB: ATTACH_STUB}, cables={MUSEUM_RG59_SPAN: "RG-59"},
)
MUSEUM_ERRORS = bus_errors(MUSEUM_BUS)
WRONG_TERMINATOR_GAMMA = reflection_coefficient(75, 50)  # 0,2 : 20 % de l'amplitude renvoyée


def bus_plain_svg(bus: Bus, *, title: str, stub_m: float) -> str:
    """Bus vertical comme dans PR16, mais **sans verdict** : chaque élément est décrit tel
    qu'il a été relevé (terminateur et sa valeur, câble et longueur, raccordement de chaque
    station, mise à la terre). Le candidat conclut lui-même."""
    width, bus_x, pc_x = 380, 92, 250
    parts = [_text_lines(width // 2, 18, [title], size=14, weight="700", anchor="middle")]
    y = 32

    def end_box(end: BusEnd, where: str) -> None:
        nonlocal y
        parts.append(
            f'<rect data-end="{where}" data-terminator="{end.terminator_ohm}" x="{bus_x - 30}" y="{y}" width="60" '
            f'height="22" rx="5" fill="#f4f6fb" stroke="{_STROKE}" stroke-width="2"/>'
        )
        parts.append(_text_lines(bus_x, y + 15, [f"{end.terminator_ohm} Ω"], size=12, weight="700", anchor="middle"))
        parts.append(_text_lines(bus_x + 38, y + 15, ["terminateur (valeur gravée)"], size=11.5))
        if end.grounded:
            gx = 22
            parts.append(
                f'<path data-ground="{where}" d="M{bus_x - 30} {y + 11} H{gx} V{y + 20} M{gx - 9} {y + 20} H{gx + 9} '
                f'M{gx - 6} {y + 24} H{gx + 6} M{gx - 3} {y + 28} H{gx + 3}" fill="none" stroke="{_STROKE}" stroke-width="1.6"/>'
            )
            parts.append(_text_lines(gx - 12, y + 40, ["terre"], size=10))
        y += 22

    end_box(bus.first, "1")
    for item in bus.items:
        if isinstance(item, Span):
            h = 46
            parts.append(
                f'<path data-span="{escape(item.cable)}|{item.length_m:g}" d="M{bus_x} {y} V{y + h}" '
                f'stroke="{_STROKE}" stroke-width="4"/>'
            )
            parts.append(_text_lines(bus_x - 12, y + 20, [item.cable, f"{fr(item.length_m)} m"], size=10.5, step=13, anchor="end"))
            y += h
        else:
            stub = item.attachment != ATTACH_T
            parts.append(
                f'<rect data-station="{escape(item.name)}" data-attachment="{"stub" if stub else "T"}" x="{bus_x - 11}" '
                f'y="{y}" width="22" height="22" rx="3" fill="#ffffff" stroke="{_STROKE}" stroke-width="2"/>'
            )
            parts.append(_text_lines(bus_x, y + 16, ["T"], size=12, weight="700", anchor="middle"))
            dash = ' stroke-dasharray="6 4"' if stub else ""
            parts.append(f'<path d="M{bus_x + 11} {y + 11} H{pc_x}" stroke="{_STROKE}" stroke-width="2"{dash}/>')
            note = f"cordon coaxial de {fr(stub_m)} m" if stub else "T vissé sur la carte"
            parts.append(_text_lines(bus_x + 18, y + 7, [note], size=9.5))
            parts.append(
                f'<rect x="{pc_x}" y="{y - 2}" width="120" height="26" rx="5" fill="#f4f6fb" stroke="{_STROKE}" stroke-width="1.5"/>'
            )
            parts.append(_text_lines(pc_x + 60, y + 15, [item.name], size=11.5, weight="700", anchor="middle"))
            y += 22
    end_box(bus.last, "2")
    y += 40 if bus.last.grounded else 18
    stats = f"{len(bus.stations)} stations · {fr(bus.length_m)} m de câble entre les T extrêmes"
    parts.append(_text_lines(10, y, [stats], size=11))
    parts.append(_text_lines(10, y + 16, ["Relevé fictif ; le schéma ne donne aucun verdict."], size=10.5))
    return _svg(width, y + 26, parts)


def _bus_alt(bus: Bus, stub_m: float) -> str:
    parts = [f"Bus vertical, de haut en bas. Extrémité haute : terminateur {bus.first.terminator_ohm} Ω"
             + (", relié à la terre" if bus.first.grounded else "")]
    for item in bus.items:
        if isinstance(item, Span):
            parts.append(f"tronçon {item.cable} de {fr(item.length_m)} m")
        elif item.attachment == ATTACH_T:
            parts.append(f"{item.name} : T vissé sur la carte")
        else:
            parts.append(f"{item.name} : T relié à la carte par un cordon coaxial de {fr(stub_m)} m")
    parts.append(f"extrémité basse : terminateur {bus.last.terminator_ohm} Ω"
                 + (", relié à la terre" if bus.last.grounded else ", sans terre"))
    return " ; ".join(parts) + f". Total : {len(bus.stations)} stations, {fr(bus.length_m)} m. Aucun verdict."


BUS_FIGURE = Figure(
    key="ex03-bus-salle-retro",
    title="Dossier B, document B2 — Bus 10BASE2 de la salle rétro, relevé avant intervention",
    alt=_bus_alt(MUSEUM_BUS, MUSEUM_STUB_M),
    caption="Relevé fictif fait par le bénévole : valeurs gravées sur les terminateurs, marquage des câbles, longueurs mesurées.",
    svg=bus_plain_svg(MUSEUM_BUS, title="Salle rétro — segment 10BASE2", stub_m=MUSEUM_STUB_M),
)
BUS_FIGURE_FILE = f"{STATIC_DIR_REF}/ex03-bus-salle-retro.svg"

# =============================================================================================
# Dossier B — mesures à l'ohmmètre sur le segment de la salle 2 (question X07)
# =============================================================================================

ROOM2_NAMES = ("Poste A", "Poste B", "Poste C", "Poste D")
ROOM2_LENGTHS = (5, 8, 6)
_ROOM2_OK = _stations_bus(ROOM2_NAMES, ROOM2_LENGTHS, first=BusEnd(50, grounded=True), last=BusEnd(50))
_ROOM2_MISSING = _stations_bus(ROOM2_NAMES, ROOM2_LENGTHS, first=BusEnd(50, grounded=True), last=BusEnd(None))
_ROOM2_SHORT = _stations_bus(ROOM2_NAMES, ROOM2_LENGTHS, first=BusEnd(50, grounded=True), last=BusEnd(50),
                             faults={1: FAULT_SHORT})
# (jour, contexte, lecture au T du Poste A, réseau arrêté)
OHM_READINGS: tuple[tuple[str, str, float | None], ...] = (
    ("Lundi", "Contrôle d'ouverture, rien n'a changé", ohmmeter_reading(_ROOM2_OK, 0)),
    ("Mercredi", "Plus aucun poste ne communique après une visite scolaire", ohmmeter_reading(_ROOM2_MISSING, 0)),
    ("Vendredi", ("Un bénévole vient de refaire le BNC du câble Poste B → Poste C ; plus aucun poste "
                  "ne communique"), ohmmeter_reading(_ROOM2_SHORT, 0)),
)
OHM_MEANINGS = {
    "Lundi": "normal : deux terminateurs 50 Ω en parallèle",
    "Mercredi": "un seul terminateur vu : terminateur manquant ou desserré, ou coupure",
    "Vendredi": "court-circuit âme/blindage, le BNC refait est suspect",
}

# =============================================================================================
# Dossier C — Brasserie Van Daele : choix des liaisons (question X08)
# =============================================================================================

FIBRE_L1_M = 420  # bureaux → entrepôt, entre deux bâtiments
COPPER_L2_M = 70  # salle serveur → plateau du 1er étage, même bâtiment
HALL_FIBRE = "OM2"
HALL_M = 180
L1_CHOICE = choose_10g(FIBRE_L1_M, between_buildings=True)
L2_CHOICE = choose_10g(COPPER_L2_M)
HALL_1G_VERDICT = module_verdict("1000BASE-SX", "1000BASE-SX", HALL_FIBRE, HALL_M)
HALL_10G_VERDICT = module_verdict("10GBASE-SR", "10GBASE-SR", HALL_FIBRE, HALL_M)
L1_OM4_VERDICT = module_verdict("10GBASE-SR", "10GBASE-SR", "OM4", FIBRE_L1_M)
L1_LR_VERDICT = module_verdict("10GBASE-LR", "10GBASE-LR", "OS2", FIBRE_L1_M)
assert L1_CHOICE == M_10G_LR and L2_CHOICE == M_10G_COPPER and L1_LR_VERDICT == C_OK

# =============================================================================================
# Dossier C — réception de la liaison L1 (question X09)
# =============================================================================================

L1_WAVELENGTH = 1310
L1_CONNECTORS = 2  # une paire de connecteurs à chaque tiroir optique
L1_SPLICES = 2  # une épissure de pigtail dans chaque tiroir
L1_DB_PER_KM = attenuation_for("OS2", L1_WAVELENGTH)
L1_MAX_LOSS = max_link_loss_db(FIBRE_L1_M, "OS2", L1_WAVELENGTH, L1_CONNECTORS, L1_SPLICES)
PHOTO_REFERENCE_DBM = -5.0
PHOTO_READINGS: tuple[tuple[str, float], ...] = (("Fibre 1", -7.1), ("Fibre 2", -9.62))
PHOTO_LOSSES = {name: measured_loss_db(PHOTO_REFERENCE_DBM, reading) for name, reading in PHOTO_READINGS}
PHOTO_VERDICTS = {name: photometry_verdict(loss, L1_MAX_LOSS) for name, loss in PHOTO_LOSSES.items()}
L1_TX_DBM = -2.1
L1_RX_EXPECTED = rx_power_dbm(L1_TX_DBM, L1_MAX_LOSS)
L1_RX_STATUS = rx_status(L1_RX_EXPECTED, LR_SPEC)
L1_RX_MARGIN = round(L1_RX_EXPECTED - LR_SPEC.sensitivity_dbm, 2)

# =============================================================================================
# Dossier C — panne de la liaison L1 six mois plus tard (question X10)
# =============================================================================================

OUTAGE_SCREEN: tuple[str, ...] = (
    "Switch BUREAUX, port Te1/0/49 (10GBASE-LR)",
    "  Lien : DOWN",
    f"  Tx : {dbm_fr(L1_TX_DBM)} dBm   Rx : {dbm_fr(-40.0)} dBm (LOS)",
    "Switch ENTREPÔT, port Te1/0/49 (10GBASE-LR)",
    "  Lien : DOWN",
    f"  Tx : {dbm_fr(-2.0)} dBm   Rx : {dbm_fr(round(L1_TX_DBM - 2.3, 1))} dBm",
    "Les deux modules sont reconnus (même référence).",
)
OUTAGE_TRACE = OtdrTrace(
    name="Tiroir BUREAUX → ENTREPÔT, fibre 2, 1 550 nm",
    launch_m=150,
    link_m=FIBRE_L1_M,
    db_per_km=attenuation_for("OS2", 1550),
    events=(
        OtdrEvent(150, True, 0.4, 0.4, label="Connecteur du tiroir BUREAUX"),
        OtdrEvent(280, False, 0.12, 0.8, label="Courbure"),
        OtdrEvent(325, True, 0.0, 0.0, end=True, label="Cassure"),
    ),
)
OUTAGE_KINDS = tuple(otdr_event_kind(e) for e in OUTAGE_TRACE.events)
OUTAGE_BREAK_M = break_position_m(OUTAGE_TRACE.end_m, OUTAGE_TRACE.launch_m)
OUTAGE_BEND_M = break_position_m(OUTAGE_TRACE.events[1].position_m, OUTAGE_TRACE.launch_m)
REPAIR_CABLE_DIAMETER_MM = 6
REPAIR_BEND_REST_MM = min_bend_radius_fibre_mm(REPAIR_CABLE_DIAMETER_MM, pulling=False)
REPAIR_BEND_PULL_MM = min_bend_radius_fibre_mm(REPAIR_CABLE_DIAMETER_MM, pulling=True)
REPAIR_SPLICES = 2  # une épissure de chaque côté du tronçon remplacé
REPAIRED_MAX_LOSS = max_link_loss_db(FIBRE_L1_M, "OS2", L1_WAVELENGTH, L1_CONNECTORS, L1_SPLICES + REPAIR_SPLICES)


def otdr_plain_svg(trace: OtdrTrace) -> str:
    """Trace de réflectomètre (1 550 nm) **sans interprétation** : courbe, événements numérotés,
    puis pour chacun sa position, la présence d'un pic et les pertes mesurées aux deux longueurs
    d'onde. La nature de l'événement est laissée au candidat."""
    width, height = 380, 210
    left, right, top, bottom = 40, 14, 22, 36
    plot_w, plot_h = width - left - right, height - top - bottom
    points = trace_points(trace)
    x_max = max(x for x, _ in points)
    y_max, y_min = 2.0, min(y for _x, y in points) - 0.5

    def sx(x: float) -> float:
        return left + plot_w * x / x_max

    def sy(y: float) -> float:
        return top + plot_h * (y_max - y) / (y_max - y_min)

    parts = [
        _text_lines(width // 2, 14, [f"Trace : {trace.name}"], size=12, weight="700", anchor="middle"),
        f'<path d="M{left} {top} V{top + plot_h} H{left + plot_w}" fill="none" stroke="{_STROKE}" stroke-width="1.2"/>',
        _text_lines(left + plot_w // 2, height - 6, ["Distance depuis le réflectomètre (m)"], size=11, anchor="middle"),
        (f'<text x="12" y="{top + plot_h / 2:.0f}" font-size="11" text-anchor="middle" '
         f'transform="rotate(-90 12 {top + plot_h / 2:.0f})">Niveau (dB)</text>'),
    ]
    for tick in range(0, int(x_max) + 1, 100):
        parts.append(f'<path d="M{sx(tick):.1f} {top + plot_h} v4" stroke="{_STROKE}"/>')
        parts.append(_text_lines(int(sx(tick)), top + plot_h + 15, [str(tick)], size=10, anchor="middle"))
    path = " ".join(f"{'M' if i == 0 else 'L'}{sx(x):.1f} {sy(y):.1f}" for i, (x, y) in enumerate(points))
    parts.append(f'<path data-trace="1" d="{path}" fill="none" stroke="#1f5fbf" stroke-width="2"/>')
    parts.append(f'<rect x="{left}" y="{top}" width="{sx(trace.launch_m) - left:.1f}" height="{plot_h}" fill="#f4f4f4" opacity="0.6"/>')
    parts.append(_text_lines(int(sx(trace.launch_m / 2)), top + plot_h - 6, ["amorce"], size=10, anchor="middle"))
    for number, event in enumerate(trace.events, start=1):
        x = sx(event.position_m)
        parts.append(f'<g data-event="{number}" data-m="{event.position_m:g}"><circle cx="{x:.1f}" cy="{top + 8}" r="8" '
                     f'fill="#ffffff" stroke="{_STROKE}"/><text x="{x:.1f}" y="{top + 12}" font-size="10.5" '
                     f'font-weight="700" text-anchor="middle">{number}</text></g>')
    lines = []
    for number, text in enumerate(otdr_event_lines(trace), start=1):
        lines += _wrap(f"{number}. {text}", 62)
    lines += _wrap(f"Pente de la trace : {fr(trace.db_per_km, 1)} dB/km. Bobine amorce de {trace.launch_m:g} m "
                   "entre le réflectomètre et le tiroir BUREAUX.", 62)
    parts.append(_text_lines(10, height + 8, lines, size=11, step=14))
    return _svg(width, height + 8 + 14 * len(lines), parts)


def otdr_event_lines(trace: OtdrTrace) -> list[str]:
    """Description factuelle de chaque événement (ce que l'appareil mesure)."""
    lines = []
    for event in trace.events:
        peak = "pic de réflexion" if event.reflective else "sans pic"
        if event.end:
            lines.append(f"{event.position_m:g} m — {peak}, puis la trace retombe dans le bruit")
        else:
            lines.append(f"{event.position_m:g} m — {peak}, perte {fr(event.loss_1550, 2)} dB à 1 550 nm "
                         f"et {fr(event.loss_1310, 2)} dB à 1 310 nm")
    return lines


OTDR_FIGURE = Figure(
    key="ex03-otdr-fibre-2",
    title="Dossier C, document C5 — Réflectomètre sur la fibre 2, depuis le tiroir BUREAUX",
    alt=(
        f"Trace de réflectomètre fictive, 1 550 nm, fibre 2 depuis le tiroir BUREAUX, bobine amorce de "
        f"{OUTAGE_TRACE.launch_m:g} m. Événements : "
        + " ; ".join(f"{n}. {t}" for n, t in enumerate(otdr_event_lines(OUTAGE_TRACE), start=1))
        + f". Pente {fr(OUTAGE_TRACE.db_per_km, 1)} dB/km. Aucune interprétation n'est donnée."
    ),
    caption="Trace fictive relevée le jour de la panne (mesures de 1 310 nm reportées dans la liste).",
    svg=otdr_plain_svg(OUTAGE_TRACE),
)
OTDR_FIGURE_FILE = f"{STATIC_DIR_REF}/ex03-otdr-fibre-2.svg"

# =============================================================================================
# Fichiers statiques
# =============================================================================================

EX03_FIGURES: tuple[Figure, ...] = (PLUG_FIGURE, CERT_FIGURE, BUS_FIGURE, OTDR_FIGURE)
STATIC_FIGURES: tuple[tuple[Figure, str], ...] = (
    (PLUG_FIGURE, PLUG_FIGURE_FILE),
    (CERT_FIGURE, CERT_FIGURE_FILE),
    (BUS_FIGURE, BUS_FIGURE_FILE),
    (OTDR_FIGURE, OTDR_FIGURE_FILE),
)
SCREENS: dict[str, tuple[str, ...]] = {"outage": OUTAGE_SCREEN}


def static_svg(figure: Figure) -> str:
    """Contenu exact du fichier statique d'un schéma (même règle que EX01 et EX02)."""
    head_end = figure.svg.index(">") + 1
    return (
        figure.svg[:head_end]
        + f"<title>{escape(figure.title)}</title><desc>{escape(figure.alt)}</desc>"
        + figure.svg[head_end:]
        + "\n"
    )

