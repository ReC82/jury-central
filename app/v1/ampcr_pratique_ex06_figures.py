"""EX06 « Examen blanc global avancé — dossiers complexes » — données des deux variantes et
schémas (ticket #234).

Un client par variante, **quatre dossiers d'intervention** (A : poste qui ne démarre plus,
stockage et données ; B : évolution du parc et installations ; C : câblage cuivre et coaxial ;
D : réseau, Wi-Fi, partages et rapport). Chaque dossier contient **plusieurs causes possibles**
(dont des **indices plausibles mais non décisifs**) que le candidat départage par des tests
discriminants. Les deux variantes ont la même structure et le même barème, avec des données,
des pannes et des réponses différentes. Chaque valeur et chaque verdict est calculé avec la
règle **du cours** qui l'enseigne :

- diagnostic de non-démarrage (`boot_diagnosis` : chaîne de démarrage de PR06/PR11, pile
  CR2032 de PR28) ;
- tables de partitions, systèmes de fichiers, unités (`partition_table_choice`,
  `filesystem_for`, `tb_to_tib`, `mbr_usable_bytes`, PR05) ;
- protection des données (`check_321`, `compare_copy`, `required_prerequisites`, PR28) ;
- compatibilité et budget de puissance (`check_configuration`, `power_budget`,
  `recommended_psu`, PR02) ;
- installation de Windows (`activation_result`, PR08) et de Linux (`checksum_verdict`,
  `swap_advice`, `dual_boot_action`, `first_boot_entry`, PR09) ;
- cordon RJ45 (`T568B`, `split_pairs`, PR15) et vitesse négociée (`negotiated_speed`, PR15 X03) ;
- segment coaxial 10BASE2 (`bus_errors`, `ohmmeter_reading`, PR16) ;
- adressage IPv4 (`smallest_prefix_for`, `subnet_facts`, `plan_errors`, PR20) ;
- Wi-Fi (`received_dbm`, `signal_verdict`, `best_channel_24`, `audit_config`,
  `repeater_mbps`, PR25) ;
- partages et NTFS avec héritage et refus (`effective_access`, PR23).

Entreprises, personnes, adresses et mesures sont **fictives** (plages privées RFC 1918, adresses
publiques de documentation RFC 5737). Les schémas ne donnent **aucun verdict** ; ils sont aussi
enregistrés en fichiers statiques (`app/static/img/ampcr-pratique/`), identiques au SVG produit
ici (test). Aucun dossier n'est présenté comme un sujet officiel.
"""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass
from html import escape

from app.v1.ampcr_pratique_pr02_figures import (
    Configuration,
    Load,
    check_configuration,
    failed_checks,
    power_budget,
    recommended_psu,
)
from app.v1.ampcr_pratique_pr05_figures import (
    TB,
    USE_LEGACY_DEVICE,
    USE_SHARED_REMOVABLE,
    USE_WINDOWS_DATA,
    USE_WINDOWS_SYSTEM,
    filesystem_for,
    mbr_usable_bytes,
    partition_table_choice,
    tb_to_tib,
)
from app.v1.ampcr_pratique_pr08_figures import LIC_DIGITAL, LIC_RETAIL, activation_result
from app.v1.ampcr_pratique_pr09_figures import (
    ISO_NAME,
    PK_ESP,
    PK_FREE,
    PK_MSR,
    PK_RECOVERY,
    PK_WINDOWS,
    checksum_verdict,
    dual_boot_action,
    first_boot_entry,
    swap_advice,
)
from app.v1.ampcr_pratique_pr15_figures import SEQUENTIAL_WRONG, split_pairs
from app.v1.ampcr_pratique_pr16_figures import (
    ATTACH_STUB,
    FAULT_OPEN,
    GOOD_TERMINATOR,
    GROUNDED_TERMINATOR,
    Bus,
    Span,
    Station,
    bus_errors,
    ohmmeter_reading,
)
from app.v1.ampcr_pratique_pr20_figures import (
    AddressPlan,
    Host,
    normalize_mac,
    plan_errors,
    smallest_prefix_for,
    subnet_facts,
)
from app.v1.ampcr_pratique_pr21_figures import _pc_box
from app.v1.ampcr_pratique_pr23_figures import (
    LEVEL_MODIFY,
    LEVEL_NONE,
    LEVEL_READ,
    Account,
    Ace,
    Folder,
    Share,
    effective_access,
    ntfs_level,
    share_level,
)
from app.v1.ampcr_pratique_pr25_figures import (
    BAND_5,
    BAND_24,
    WEP,
    WPA_TKIP,
    ApConfig,
    Neighbor,
    audit_config,
    best_channel_24,
    link_rate,
    received_dbm,
    repeater_mbps,
    signal_verdict,
    useful_mbps,
)
from app.v1.ampcr_pratique_pr28_figures import (
    OP_ERASE,
    OP_FORMAT,
    SUP_EXTERNAL,
    SUP_INTERNAL,
    SUP_NAS,
    Copy,
    check_321,
    compare_copy,
    required_prerequisites,
)
from app.v1.ampcr_pratique_visuals import T568B, Figure, _svg, _text_lines, _wrap

STATIC_DIR_REF = "img/ampcr-pratique"
SCREEN_WIDTH = 56  # caractères au plus par ligne de capture (comme les cours)
_STROKE = "#33415c"
WAN_IP = "203.0.113.80"  # adresse publique de la box (RFC 5737)


def fr(value: float) -> str:
    return f"{value:g}".replace(".", ",")


def minutes(hhmm: str) -> int:
    hours, mins = hhmm.split(":")
    return int(hours) * 60 + int(mins)


def duration_text(total: int) -> str:
    return f"{total // 60} h {total % 60:02d}"


# --- Règles reprises des cours (formulées pour l'examen) ----------------------------------

# Dossier A — chaîne de démarrage (PR06, PR11) : le disque doit être vu par le micrologiciel ;
# s'il est vu, un écran bleu INACCESSIBLE_BOOT_DEVICE après un changement du mode du contrôleur
# vient de ce changement ; un disque invisible partout (autre câble, autre port, autre PC) est
# mort. La pile CR2032 (3 V nominal) usée dérègle l'horloge mais n'empêche pas de voir un disque.
CAUSE_CONTROLLER = "mode du contrôleur de stockage modifié"
CAUSE_DISK_DEAD = "disque mort (panne matérielle)"
CAUSE_CABLE = "câble ou port SATA"
CAUSE_UPDATE = "mise à jour de Windows"
BATTERY_WORN_V = 2.7  # en dessous : pile nettement sous les 3 V nominaux, usée (PR28)


@dataclass(frozen=True)
class BootCase:
    post: str
    symptom: str  # message affiché
    noise: str
    history: tuple[str, ...]  # événements récents rapportés (dont l'indice trompeur)
    disk_in_firmware: bool
    disk_seen_other_cable: bool | None  # None : test inutile (disque vu)
    disk_seen_other_pc: bool | None
    smart_status: str | None  # « Bon » si lisible
    controller_now: str
    controller_install: str  # mode noté sur la fiche d'installation du poste
    battery_v: float
    date_shown: str

    @property
    def cause(self) -> str:
        return boot_diagnosis(self)

    @property
    def battery_worn(self) -> bool:
        return self.battery_v < BATTERY_WORN_V


def boot_diagnosis(case: BootCase) -> str:
    if not case.disk_in_firmware:
        if case.disk_seen_other_cable:
            return CAUSE_CABLE
        if case.disk_seen_other_pc is False:
            return CAUSE_DISK_DEAD
        raise ValueError("Test discriminant manquant.")
    if case.controller_now != case.controller_install:
        return CAUSE_CONTROLLER
    return CAUSE_UPDATE


# Dossier C — vitesse négociée selon le cordon (PR15, X03) : 1-2 et 3-6 servent à toutes les
# vitesses ; 4-5 et 7-8 seulement au gigabit (le lien retombe alors à 100 Mb/s).
SPEED_NONE = "aucun lien"
SPEED_100 = "100 Mb/s"
SPEED_1000 = "1 Gb/s"


def negotiated_speed(links: tuple[tuple[int, int | None], ...]) -> str:
    broken = {a for a, b in links if b != a}
    if broken & {1, 2, 3, 6}:
        return SPEED_NONE
    if broken & {4, 5, 7, 8}:
        return SPEED_100
    return SPEED_1000


def tester_faults(links: tuple[tuple[int, int | None], ...]) -> list[str]:
    faults = []
    for pin_a, pin_b in links:
        if pin_b is None:
            faults.append(f"broche {pin_a} ouverte (fil {T568B[pin_a - 1]})")
        elif pin_b != pin_a:
            faults.append(f"broche {pin_a} arrive en {pin_b}")
    return faults


def tester_lines(links: tuple[tuple[int, int | None], ...]) -> tuple[str, ...]:
    return (
        "Testeur de câble — carte des fils",
        "Extrémité A : 1  2  3  4  5  6  7  8",
        "Extrémité B : " + "  ".join("-" if b is None else str(b) for _a, b in links),
        "(« - » : aucune continuité sur cette broche)",
    )


# Dossier D — Wi-Fi : point de mesure (distance et obstacles depuis le point d'accès).
@dataclass(frozen=True)
class WifiPoint:
    key: str
    place: str
    distance_m: float
    obstacles: tuple[str, ...]

    def dbm(self, band: str) -> int:
        return received_dbm(self.distance_m, band, self.obstacles)


@dataclass(frozen=True)
class Extension:
    """Zone mal couverte : répéteur (liaison radio) ou second point d'accès câblé."""
    zone: str
    uplink_m: float
    uplink_obstacles: tuple[str, ...]
    client_m: float
    client_obstacles: tuple[str, ...]
    cable_m: int  # longueur de câble jusqu'au switch pour un point d'accès câblé

    @property
    def repeater_mbps(self) -> float:
        up = received_dbm(self.uplink_m, BAND_24, self.uplink_obstacles)
        cl = received_dbm(self.client_m, BAND_24, self.client_obstacles)
        return repeater_mbps(up, cl)

    @property
    def wired_mbps(self) -> float:
        return useful_mbps(link_rate(received_dbm(self.client_m, BAND_24, self.client_obstacles)))


# --- Une variante --------------------------------------------------------------------------


@dataclass(frozen=True)
class InventoryRow:
    name: str
    user: str
    os: str
    hardware: str
    storage: str
    year: int


@dataclass(frozen=True)
class Variant:
    number: int
    company: str
    activity: str
    city: str
    manager: str
    staff: int
    date: str
    hosts: tuple[Host, ...]  # schéma du réseau (box en premier)
    pool: tuple[str, str]
    inventory: tuple[InventoryRow, ...]
    # Dossier A
    boot: BootCase
    new_disk_label: str
    new_disk_tb: float
    new_disk_boots: bool
    new_disk_use: str
    removable_label: str
    removable_use: str
    removable_largest: tuple[str, float]  # (fichier, Gio)
    defrag_request: str
    copies: tuple[Copy, ...]
    manifest: tuple[tuple[str, int, str], ...]  # source (nom, taille, empreinte)
    backup_copy: tuple[tuple[str, int, str], ...]
    data_operation: str
    data_operation_text: str
    data_keep: bool
    data_encrypted: bool
    # Dossier B
    quote: Configuration
    loads: tuple[Load, ...]
    win_problem: str  # « vmd » ou « mbr »
    win_post: str
    licence: str
    licence_edition: str
    installed_edition: str
    linux_post: str
    linux_ram_gb: int
    iso_line: str
    backup_verified: bool
    written_consent: bool
    efibootmgr: tuple[str, ...]
    # Dossier C
    cord_post: str
    cord_links: tuple[tuple[int, int | None], ...]
    cord_ends: tuple[tuple[str, ...], tuple[str, ...]] | None  # ordre des fils lu aux deux bouts
    cord_next_fail: bool  # certificateur : diaphonie (NEXT) en échec
    cord_run_m: int
    coax_room: str
    coax_bus: Bus
    coax_measure_at: tuple[int, ...]  # stations où l'ohmmètre a été posé
    # Dossier D
    lan: str  # réseau actuel
    needed_addresses: int
    new_hosts: tuple[Host, ...]  # postes relevés après l'agrandissement
    new_pool: tuple[str, str]
    wifi_points: tuple[WifiPoint, ...]
    neighbors: tuple[Neighbor, ...]
    ap_config: ApConfig
    extension: Extension
    share_tree: dict[str, Folder]
    shares: dict[str, Share]
    accounts: tuple[Account, ...]
    access_paths: tuple[str, ...]
    need: tuple[str, str, str]  # (login, chemin, niveau demandé)
    journal: tuple[tuple[str, str, str], ...]
    explain_terms: tuple[str, ...]

    # --- Valeurs calculées ----------------------------------------------------------------

    @property
    def label(self) -> str:
        return f"Variante {self.number}"

    @property
    def box(self) -> Host:
        return self.hosts[0]

    def host(self, name: str) -> Host:
        return next(h for h in (*self.hosts, *self.new_hosts) if h.name == name)

    # Dossier A
    @property
    def new_disk_bytes(self) -> int:
        return round(self.new_disk_tb * TB)

    @property
    def new_disk_table(self) -> str:
        return partition_table_choice(disk_bytes=self.new_disk_bytes, boots_os=self.new_disk_boots,
                                      firmware_uefi=True)

    @property
    def new_disk_shown_tib(self) -> float:
        return tb_to_tib(self.new_disk_tb)

    @property
    def new_disk_mbr_lost_tib(self) -> float:
        return round((self.new_disk_bytes - mbr_usable_bytes(self.new_disk_bytes)) / 2**40, 2)

    @property
    def new_disk_fs(self) -> str:
        return filesystem_for(self.new_disk_use)

    @property
    def removable_fs(self) -> str:
        return filesystem_for(self.removable_use, largest_file_bytes=round(self.removable_largest[1] * 2**30))

    @property
    def missing_321(self) -> tuple[str, ...]:
        return check_321(self.copies)

    @property
    def copy_check(self) -> tuple[tuple[str, ...], tuple[str, ...]]:
        return compare_copy(self.manifest, self.backup_copy)

    @property
    def data_prerequisites(self) -> tuple[str, ...]:
        return required_prerequisites(self.data_operation, keep_data=self.data_keep, encrypted=self.data_encrypted)

    # Dossier B
    @property
    def quote_checks(self) -> list[tuple[str, bool, str]]:
        return check_configuration(self.quote)

    @property
    def quote_failures(self) -> list[str]:
        return failed_checks(self.quote)

    @property
    def budget_w(self) -> int:
        return power_budget(self.loads)

    @property
    def psu_w(self) -> int:
        return recommended_psu(self.budget_w, gpu_recommendation=self.quote.gpu_psu_recommendation_w)

    @property
    def activation(self) -> tuple[str, str]:
        return activation_result(self.licence, self.licence_edition, self.installed_edition, same_pc=True)

    @property
    def swap_gb(self) -> float:
        swap = swap_advice(self.linux_ram_gb, hibernation=False)
        assert swap is not None
        return swap

    @property
    def iso_verdict(self) -> str:
        return checksum_verdict(self.iso_line)

    @property
    def dual_boot_plan(self) -> tuple[tuple[str, str], ...]:
        zones = ((PK_ESP, "ESP (FAT32, 100 Mo)"), (PK_MSR, "MSR (16 Mo)"), (PK_WINDOWS, "Windows C: (NTFS)"),
                 (PK_RECOVERY, "Récupération (NTFS)"), (PK_FREE, "Espace libre préparé depuis Windows"))
        return tuple((label, dual_boot_action(kind, backup_verified=self.backup_verified,
                                              written_consent=self.written_consent)) for kind, label in zones)

    @property
    def first_boot(self) -> str:
        return first_boot_entry(self.efibootmgr)

    # Dossier C
    @property
    def cord_speed(self) -> str:
        return negotiated_speed(self.cord_links)

    @property
    def cord_faults(self) -> list[str]:
        return tester_faults(self.cord_links)

    @property
    def cord_split(self) -> list[tuple[int, int]]:
        return split_pairs(self.cord_ends[0]) if self.cord_ends else []

    @property
    def coax_errors(self) -> list[str]:
        return bus_errors(self.coax_bus)

    @property
    def coax_readings(self) -> tuple[tuple[str, float | None], ...]:
        names = self.coax_bus.stations
        return tuple((names[i].name, ohmmeter_reading(self.coax_bus, i)) for i in self.coax_measure_at)

    # Dossier D
    @property
    def lan_facts(self):
        net = ipaddress.IPv4Network(self.lan)
        return subnet_facts(str(net.network_address), net.prefixlen)

    @property
    def pool_size(self) -> int:
        low, high = (int(ipaddress.IPv4Address(a)) for a in self.pool)
        return high - low + 1

    @property
    def new_prefix(self) -> int:
        return smallest_prefix_for(self.needed_addresses)

    @property
    def new_facts(self):
        return subnet_facts(self.box.ip, self.new_prefix)

    @property
    def new_plan(self) -> AddressPlan:
        return AddressPlan(self.new_facts.cidr, (self.box.__class__(
            self.box.name, self.box.role, self.box.ip, self.new_prefix, None, (), self.box.mac),
            *self.new_hosts), self.box.ip, self.box.ip, self.new_pool)

    @property
    def new_plan_errors(self) -> list[str]:
        return plan_errors(self.new_plan)

    @property
    def wifi_table(self) -> tuple[tuple[str, int, str, int, str], ...]:
        return tuple((p.key, p.dbm(BAND_24), signal_verdict(p.dbm(BAND_24)), p.dbm(BAND_5),
                      signal_verdict(p.dbm(BAND_5))) for p in self.wifi_points)

    @property
    def best_channel(self) -> int:
        return best_channel_24(self.neighbors)

    @property
    def ap_audit(self) -> tuple[tuple[str, str], ...]:
        return audit_config(self.ap_config)

    def account(self, login: str) -> Account:
        return next(a for a in self.accounts if a.login == login)

    def access(self, login: str, path: str, *, remote: bool = True) -> str:
        return effective_access(self.account(login), path, remote=remote, tree=self.share_tree, shares=self.shares)

    @property
    def access_matrix(self) -> dict[str, dict[str, str]]:
        return {a.login: {p: self.access(a.login, p) for p in self.access_paths} for a in self.accounts}

    @property
    def need_layers(self) -> tuple[str, str]:
        login, path, _wanted = self.need
        account = self.account(login)
        return share_level(account, path, self.shares), ntfs_level(account, path, self.share_tree)

    @property
    def need_limiting_layer(self) -> str:
        _login, _path, wanted = self.need
        ranks = (LEVEL_NONE, LEVEL_READ, LEVEL_MODIFY)
        share, ntfs = self.need_layers
        share_ok = ranks.index(share) >= ranks.index(wanted)
        ntfs_ok = ranks.index(ntfs) >= ranks.index(wanted)
        assert not (share_ok and ntfs_ok)
        return "partage" if not share_ok else "NTFS"

    @property
    def journal_minutes(self) -> int:
        return sum(minutes(end) - minutes(start) for start, end, _a in self.journal)

    @property
    def journal_span(self) -> int:
        return minutes(self.journal[-1][1]) - minutes(self.journal[0][0])


def _h(name: str, role: str, ip: str, prefix: int, gateway: str | None, mac: str, *, dns: str | None = None,
       dhcp: bool = False) -> Host:
    return Host(name, role, ip, prefix, gateway, (dns or gateway,) if (dns or gateway) else (), mac, dhcp)


def _f(path: str, *entries: Ace, inherit: bool = True) -> Folder:
    return Folder(path, entries, inherit=inherit)


ADMINS = "Administrateurs"
AUTH = "Utilisateurs authentifiés"
EVERYONE = "Tout le monde"
ROOT = "D:\\Partages"

# =============================================================================================
# Variante 1 — Atelier d'architecture Morel (Liège), réseau 192.168.50.0/25
# =============================================================================================

_V1_BOX = "192.168.50.1"
_V1_TREE = {
    f.path: f for f in (
        _f(ROOT, Ace(ADMINS, "Contrôle total"), inherit=False),
        _f(f"{ROOT}\\Projets", Ace("G_Archi", "Modification"), Ace("G_Admin", "Lecture et exécution")),
        _f(f"{ROOT}\\Projets\\Concours", Ace(ADMINS, "Contrôle total"), Ace("G_Associes", "Modification"),
           inherit=False),
        _f(f"{ROOT}\\Projets\\Chantiers", Ace("G_Stagiaires", "Contrôle total", deny=True)),
    )
}
_V1_SHARES = {"Projets": Share("Projets", f"{ROOT}\\Projets", (Ace(AUTH, "Modifier"),))}

VARIANT_1 = Variant(
    number=1,
    company="Atelier d'architecture Morel",
    activity="bureau d'architectes",
    city="Liège",
    manager="Mme Morel (architecte gérante)",
    staff=9,
    date="lundi 16 novembre 2026",
    hosts=(
        _h("BOX", "box du fournisseur", _V1_BOX, 25, None, "00-1E-58-C3-00-01"),
        _h("SRV-01", "serveur de fichiers", "192.168.50.5", 25, _V1_BOX, "3C-52-82-33-00-05"),
        _h("NAS-01", "sauvegardes", "192.168.50.10", 25, _V1_BOX, "00-11-32-EF-00-10"),
        _h("AP-01", "point d'accès Wi-Fi", "192.168.50.20", 25, _V1_BOX, "9C-53-22-33-00-20"),
        _h("IMP-01", "traceur A0", "192.168.50.25", 25, _V1_BOX, "00-80-77-33-00-25"),
        _h("PC-DIR", "gérante", "192.168.50.30", 25, _V1_BOX, "3C-52-82-33-01-30"),
        _h("PC-01…08", "postes des architectes", "DHCP", 25, _V1_BOX, "3C-52-82-33-01-01", dhcp=True),
    ),
    pool=("192.168.50.64", "192.168.50.120"),
    inventory=(
        InventoryRow("PC-DIR", "gérante", "Windows 11 Pro", "Intel Core i7-12700, 32 Go DDR4",
                     "SSD SATA 1 To (contrôleur en AHCI à l'installation)", 2022),
        InventoryRow("PC-01 à PC-06", "architectes", "Windows 11 Pro", "Intel Core i7-13700, 32 Go DDR5",
                     "SSD NVMe 1 To", 2023),
        InventoryRow("PC-07", "ancien poste de dessin (retiré)", "Windows 10 Pro", "Intel Core i5-8400, 16 Go DDR4",
                     "HDD SATA 2 To", 2018),
        InventoryRow("PC-CAO", "nouveau poste de calcul (devis)", "à installer : Windows 11 Pro",
                     "voir devis", "SSD NVMe 2 To", 2026),
        InventoryRow("PORT-STAG", "portable des stagiaires", "Windows 11 Pro + Ubuntu à ajouter",
                     "Intel Core i5-1235U, 16 Go DDR4", "SSD NVMe 512 Go", 2022),
        InventoryRow("PC-ARCH1, PC-ARCH2", "salle des archives", "Windows 10 Pro", "anciens PC, carte BNC",
                     "HDD 500 Go", 2014),
    ),
    boot=BootCase(
        post="PC-DIR",
        symptom="Écran bleu « Code d'arrêt : INACCESSIBLE_BOOT_DEVICE », puis « Réparation automatique » qui échoue",
        noise="aucun bruit anormal",
        history=(
            "Une grosse mise à jour de Windows s'est installée vendredi soir à l'arrêt du PC.",
            "Samedi, le neveu de la gérante a « optimisé les réglages » du micrologiciel.",
        ),
        disk_in_firmware=True,
        disk_seen_other_cable=None,
        disk_seen_other_pc=None,
        smart_status="Bon",
        controller_now="Intel RST (RAID)",
        controller_install="AHCI",
        battery_v=3.02,
        date_shown="16/11/2026 08:12",
    ),
    new_disk_label="HDD SATA 4 To (archives des plans)",
    new_disk_tb=4,
    new_disk_boots=False,
    new_disk_use=USE_WINDOWS_DATA,
    removable_label="clé USB de 128 Go pour échanger avec l'associé qui travaille sur Mac",
    removable_use=USE_SHARED_REMOVABLE,
    removable_largest=("visite-3D-maison-Lambert.mp4", 6.4),
    defrag_request="défragmenter le SSD de PC-DIR chaque semaine « pour aller plus vite »",
    copies=(
        Copy("Original sur SRV-01", SUP_INTERNAL, False),
        Copy("Copie nocturne sur NAS-01 (même armoire)", SUP_NAS, False),
    ),
    manifest=(
        ("Lambert-plans-v12.dwg", 48_213_504, "8f41c0aa21e6b7d3"),
        ("Lambert-permis.pdf", 6_291_456, "1c9e44b0d2f87a65"),
        ("Concours-ecole-maquette.skp", 312_475_648, "a7d2e90f5b3c1846"),
        ("Honoraires-2026.xlsx", 1_048_576, "5e8b13c7a9f02d44"),
    ),
    backup_copy=(
        ("Lambert-plans-v12.dwg", 48_213_504, "8f41c0aa21e6b7d3"),
        ("Lambert-permis.pdf", 6_291_456, "1c9e44b0d2f87a65"),
        ("Concours-ecole-maquette.skp", 312_475_648, "03b9e1d4c7a25f88"),
        ("Honoraires-2026.xlsx", 1_048_576, "5e8b13c7a9f02d44"),
    ),
    data_operation=OP_ERASE,
    data_operation_text="donner PC-07 (disque d'origine avec des plans de clients) à une école de devoirs",
    data_keep=True,
    data_encrypted=False,
    quote=Configuration(
        cpu_socket="AM5", board_socket="AM5", board_form="ATX", board_memory="DDR5 DIMM",
        board_m2="NVMe", ram="DDR4 DIMM", ssd_m2="NVMe",
        case_forms=("ATX", "microATX"), case_gpu_max_mm=360, case_cooler_max_mm=160,
        gpu_length_mm=304, gpu_pcie8_needed=2, gpu_psu_recommendation_w=750,
        cooler_height_mm=165, cooler_sockets=("AM4", "AM5", "LGA1700"),
        psu_watts=650, psu_pcie8=2, psu_form="ATX", case_psu_forms=("ATX",),
    ),
    loads=(
        Load("Processeur (fiche)", 170, True),
        Load("Carte graphique (fiche)", 285, True),
        Load("Carte mère et chipset", 45, False),
        Load("2 barrettes de mémoire", 10, False),
        Load("SSD NVMe", 8, False),
        Load("5 ventilateurs", 15, True),
    ),
    win_problem="vmd",
    win_post="PC-CAO",
    licence=LIC_RETAIL,
    licence_edition="Pro",
    installed_edition="Famille",
    linux_post="PORT-STAG",
    linux_ram_gb=16,
    iso_line=f"{ISO_NAME}: OK",
    backup_verified=True,
    written_consent=True,
    efibootmgr=(
        "$ sudo efibootmgr",
        "BootCurrent: 0000",
        "BootOrder: 0000,0001,0002",
        "Boot0000* Windows Boot Manager",
        "Boot0001* ubuntu",
        "Boot0002* UEFI: clé USB",
    ),
    cord_post="PC-03",
    cord_links=tuple((p, None if p == 8 else p) for p in range(1, 9)),
    cord_ends=None,
    cord_next_fail=False,
    cord_run_m=38,
    coax_room="salle des archives",
    coax_bus=Bus(
        GROUNDED_TERMINATOR,
        (Station("PC-ARCH1"), Span(64), Station("PC-ARCH2", ATTACH_STUB), Span(71), Station("SCAN-A0"), Span(57),
         Station("PC-ARCH3")),
        GOOD_TERMINATOR,
    ),
    coax_measure_at=(0, 3),
    lan="192.168.50.0/25",
    needed_addresses=180,
    new_hosts=(
        _h("PC-04", "architecte (DHCP)", "169.254.18.77", 16, None, "3C-52-82-33-01-04", dhcp=True),
        _h("IMP-02", "imprimante neuve (fixe)", "192.168.50.130", 24, _V1_BOX, "00-80-77-33-01-30"),
        _h("PC-DIR", "gérante (fixe)", "192.168.50.30", 24, _V1_BOX, "3C-52-82-33-01-30"),
    ),
    new_pool=("192.168.50.100", "192.168.50.250"),
    wifi_points=(
        WifiPoint("P1", "Salle de réunion", 9, ("cloison",)),
        WifiPoint("P2", "Bureau des stagiaires", 16, ("brique", "brique")),
        WifiPoint("P3", "Mezzanine (étage)", 14, ("dalle", "cloison")),
    ),
    neighbors=(
        Neighbor("Proximus-4F2A", 1, -62),
        Neighbor("Boulangerie-Wifi", 6, -71),
        Neighbor("Cabinet-Dentaire", 4, -77),
        Neighbor("TelenetWiFree", 11, -88),
    ),
    ap_config=ApConfig("Morel-Archi", WPA_TKIP, "morel2020", wps=True, admin_default=True, channel_24=3,
                       guest_isolated=False, names=("Morel", "Archi")),
    extension=Extension("Mezzanine (étage)", 7, ("dalle",), 9, ("cloison",), 24),
    share_tree=_V1_TREE,
    shares=_V1_SHARES,
    accounts=(
        Account("cmorel", "Claire Morel (gérante)", ("G_Associes", "G_Archi")),
        Account("hdubois", "Hugo Dubois (architecte)", ("G_Archi",)),
        Account("ilambert", "Inès Lambert (stagiaire, secrétariat)", ("G_Admin", "G_Stagiaires")),
    ),
    access_paths=(f"{ROOT}\\Projets", f"{ROOT}\\Projets\\Concours", f"{ROOT}\\Projets\\Chantiers"),
    need=("hdubois", f"{ROOT}\\Projets\\Concours", LEVEL_MODIFY),
    journal=(
        ("08:30", "09:20", "PC-DIR : diagnostic du non-démarrage, micrologiciel remis en AHCI, contrôles"),
        ("09:20", "10:05", "NAS-01 : vérification des sauvegardes, recopie du fichier en écart"),
        ("10:05", "11:45", "PC-CAO : montage, installation de Windows 11 Pro, pilotes, activation"),
        ("11:45", "12:30", "PC-03 : cordon refait et testé ; salle des archives : segment coaxial corrigé"),
        ("13:15", "14:10", "PORT-STAG : installation d'Ubuntu en double démarrage"),
        ("14:10", "15:40", "Réseau : nouveau plan d'adressage, point d'accès reconfiguré, droits du partage"),
    ),
    explain_terms=("micrologiciel (UEFI)", "sauvegarde 3-2-1", "WPA3"),
)

# =============================================================================================
# Variante 2 — Imprimerie Dufour (Charleroi), réseau 10.20.0.0/24
# =============================================================================================

_V2_BOX = "10.20.0.1"
_V2_TREE = {
    f.path: f for f in (
        _f(ROOT, Ace(ADMINS, "Contrôle total"), inherit=False),
        _f(f"{ROOT}\\Production", Ace("G_Prod", "Modification"), Ace("G_Commercial", "Lecture et exécution"),
           Ace("G_Direction", "Lecture et exécution")),
        _f(f"{ROOT}\\Production\\BAT", Ace("G_Commercial", "Modification")),
        _f(f"{ROOT}\\Production\\Tarifs", Ace(ADMINS, "Contrôle total"), Ace("G_Direction", "Modification"),
           Ace("G_Commercial", "Lecture et exécution"), inherit=False),
    )
}
_V2_SHARES = {
    "Production": Share("Production", f"{ROOT}\\Production", (Ace(EVERYONE, "Lecture"),
                                                              Ace("G_Direction", "Contrôle total"))),
}

VARIANT_2 = Variant(
    number=2,
    company="Imprimerie Dufour",
    activity="imprimerie et atelier de façonnage",
    city="Charleroi",
    manager="M. Dufour (gérant)",
    staff=14,
    date="mercredi 18 novembre 2026",
    hosts=(
        _h("BOX", "box du fournisseur", _V2_BOX, 24, None, "00-1E-58-D4-00-01"),
        _h("SRV-01", "serveur de fichiers", "10.20.0.5", 24, _V2_BOX, "3C-52-82-44-00-05"),
        _h("NAS-01", "sauvegardes", "10.20.0.10", 24, _V2_BOX, "00-11-32-AA-00-10"),
        _h("AP-01", "point d'accès Wi-Fi", "10.20.0.20", 24, _V2_BOX, "9C-53-22-44-00-20"),
        _h("IMP-01", "presse numérique", "10.20.0.25", 24, _V2_BOX, "00-80-77-44-00-25"),
        _h("PC-PAO", "mise en page (fixe)", "10.20.0.30", 24, _V2_BOX, "3C-52-82-44-01-30"),
        _h("PC-01…10", "postes de l'atelier et des bureaux", "DHCP", 24, _V2_BOX, "3C-52-82-44-01-01", dhcp=True),
    ),
    pool=("10.20.0.100", "10.20.0.200"),
    inventory=(
        InventoryRow("PC-PAO", "graphiste", "Windows 11 Pro", "Intel Core i7-10700, 32 Go DDR4",
                     "HDD SATA 2 To", 2020),
        InventoryRow("PC-01 à PC-10", "atelier et bureaux", "Windows 11 Pro", "Intel Core i5-12400, 16 Go DDR4",
                     "SSD NVMe 512 Go", 2022),
        InventoryRow("PC-COMPTA", "comptabilité", "Windows 10 Pro (démarrage hérité, disque MBR)",
                     "Intel Core i5-10500, 16 Go DDR4", "SSD SATA 1 To : C: système + D: comptabilité", 2020),
        InventoryRow("PC-RIP", "nouveau poste de traitement d'images (devis)", "à monter", "voir devis",
                     "SSD NVMe 2 To", 2026),
        InventoryRow("PORT-ATELIER", "portable de l'atelier", "Windows 11 Pro + Ubuntu à ajouter",
                     "Intel Core i5-1135G7, 8 Go DDR4", "SSD NVMe 512 Go", 2021),
        InventoryRow("PC-MASS1, PC-MASS2", "massicot et plieuse (pilotage)", "Windows 7 embarqué",
                     "anciens PC, carte BNC", "HDD 250 Go", 2012),
    ),
    boot=BootCase(
        post="PC-PAO",
        symptom="« No bootable device — insert boot disk and press any key »",
        noise="cliquetis réguliers venant du disque dès la mise sous tension",
        history=(
            "Depuis un mois, la date revient au 01/01/2020 après chaque coupure du courant.",
            "Le PC a été déplacé vendredi pour repeindre le bureau.",
        ),
        disk_in_firmware=False,
        disk_seen_other_cable=False,
        disk_seen_other_pc=False,
        smart_status=None,
        controller_now="AHCI",
        controller_install="AHCI",
        battery_v=2.41,
        date_shown="01/01/2020 00:03",
    ),
    new_disk_label="SSD SATA 2 To (nouveau disque système de PC-PAO)",
    new_disk_tb=2,
    new_disk_boots=True,
    new_disk_use=USE_WINDOWS_SYSTEM,
    removable_label="clé USB de 16 Go pour la mise à jour du contrôleur de la presse (lit seulement FAT32)",
    removable_use=USE_LEGACY_DEVICE,
    removable_largest=("presse-firmware-v4.2.bin", 0.35),
    defrag_request="défragmenter chaque semaine le nouveau SSD de PC-PAO et le HDD externe des sauvegardes",
    copies=(
        Copy("Copie nocturne sur NAS-01 (local technique)", SUP_NAS, False),
        Copy("Disque externe USB emporté chaque vendredi chez le gérant", SUP_EXTERNAL, True),
    ),
    manifest=(
        ("Catalogue-Noel-2026.indd", 182_452_224, "b61f0e2a9c47d315"),
        ("Affiches-ville-A1.pdf", 94_371_840, "3d8a5c21f07e9b64"),
        ("Charte-client-Brasserie.ai", 27_262_976, "e92c4b7a10d6f358"),
        ("Devis-novembre.xlsx", 524_288, "47f1a3d8c2e95b06"),
    ),
    backup_copy=(
        ("Catalogue-Noel-2026.indd", 182_452_224, "b61f0e2a9c47d315"),
        ("Affiches-ville-A1.pdf", 94_371_840, "3d8a5c21f07e9b64"),
        ("Devis-novembre.xlsx", 524_288, "47f1a3d8c2e95b06"),
    ),
    data_operation=OP_FORMAT,
    data_operation_text="reformater le disque externe des sauvegardes, aujourd'hui en FAT32",
    data_keep=True,
    data_encrypted=False,
    quote=Configuration(
        cpu_socket="LGA1851", board_socket="LGA1700", board_form="ATX", board_memory="DDR5 DIMM",
        board_m2="NVMe ou SATA", ram="DDR5 DIMM", ssd_m2="NVMe",
        case_forms=("microATX", "Mini-ITX"), case_gpu_max_mm=320, case_cooler_max_mm=170,
        gpu_length_mm=336, gpu_pcie8_needed=2, gpu_psu_recommendation_w=700,
        cooler_height_mm=158, cooler_sockets=("AM5", "LGA1700", "LGA1851"),
        psu_watts=750, psu_pcie8=1, psu_form="ATX", case_psu_forms=("ATX", "SFX"),
    ),
    loads=(
        Load("Processeur (fiche)", 125, True),
        Load("Carte graphique (fiche)", 260, True),
        Load("Carte mère et chipset", 40, False),
        Load("2 barrettes de mémoire", 10, False),
        Load("SSD NVMe", 8, False),
        Load("Disque dur 3,5\" (archives)", 9, True),
        Load("4 ventilateurs", 12, True),
    ),
    win_problem="mbr",
    win_post="PC-COMPTA",
    licence=LIC_DIGITAL,
    licence_edition="Pro",
    installed_edition="Pro",
    linux_post="PORT-ATELIER",
    linux_ram_gb=8,
    iso_line=f"{ISO_NAME}: FAILED",
    backup_verified=False,
    written_consent=False,
    efibootmgr=(
        "$ sudo efibootmgr",
        "BootCurrent: 0000",
        "BootOrder: 0000,0002",
        "Boot0000* Windows Boot Manager",
        "Boot0002* UEFI: clé USB",
    ),
    cord_post="PC-07",
    cord_links=tuple((p, p) for p in range(1, 9)),
    cord_ends=(SEQUENTIAL_WRONG, SEQUENTIAL_WRONG),
    cord_next_fail=True,
    cord_run_m=46,
    coax_room="atelier de façonnage",
    coax_bus=Bus(
        GROUNDED_TERMINATOR,
        (Station("PC-MASS1"), Span(18), Station("PC-MASS2"), Span(22, fault=FAULT_OPEN), Station("PC-PLIEUSE"),
         Span(15), Station("PC-ENCART")),
        GOOD_TERMINATOR,
    ),
    coax_measure_at=(0, 1, 2, 3),
    lan="10.20.0.0/24",
    needed_addresses=400,
    new_hosts=(
        _h("PC-11", "nouveau poste (fixe)", "10.20.1.40", 24, "10.20.1.1", "3C-52-82-44-01-11"),
        _h("PC-PAO", "mise en page (fixe)", "10.20.0.30", 23, "10.20.0.254", "3C-52-82-44-01-30"),
        _h("IMP-01", "presse numérique (fixe)", "10.20.0.25", 23, _V2_BOX, "00-80-77-44-00-25"),
    ),
    new_pool=("10.20.1.10", "10.20.1.250"),
    wifi_points=(
        WifiPoint("P1", "Accueil des clients", 7, ("vitre",)),
        WifiPoint("P2", "Atelier de façonnage", 18, ("béton", "métal")),
        WifiPoint("P3", "Bureau commercial", 12, ("brique",)),
    ),
    neighbors=(
        Neighbor("Garage-Martin", 11, -60),
        Neighbor("Orange-7731", 9, -69),
        Neighbor("Fitness-Club", 6, -84),
        Neighbor("DIRECT-Imprimante", 1, -74),
    ),
    ap_config=ApConfig("Dufour", WEP, "Dufour1234", ssid_hidden=True, channel_24=8, width_24=40,
                       guest_isolated=None, dhcp_sources=2, names=("Imprimerie",)),
    extension=Extension("Atelier de façonnage", 9, ("béton",), 11, ("métal",), 32),
    share_tree=_V2_TREE,
    shares=_V2_SHARES,
    accounts=(
        Account("mdufour", "Marc Dufour (gérant)", ("G_Direction",)),
        Account("lpetit", "Laura Petit (commerciale)", ("G_Commercial",)),
        Account("kbenali", "Karim Benali (opérateur PAO)", ("G_Prod",)),
    ),
    access_paths=(f"{ROOT}\\Production", f"{ROOT}\\Production\\BAT", f"{ROOT}\\Production\\Tarifs"),
    need=("kbenali", f"{ROOT}\\Production", LEVEL_MODIFY),
    journal=(
        ("08:00", "08:45", "PC-PAO : diagnostic, disque mort confirmé, pile CR2032 remplacée"),
        ("08:45", "10:30", "PC-PAO : nouveau SSD, installation de Windows 11, restauration depuis NAS-01"),
        ("10:30", "11:20", "PC-COMPTA : sauvegarde de D:, conversion mbr2gpt, Windows 11"),
        ("11:20", "12:10", "Atelier : cordon de PC-07 refait, segment coaxial réparé"),
        ("13:00", "13:50", "PC-RIP : devis corrigé ; PORT-ATELIER : préparation du double démarrage"),
        ("13:50", "15:35", "Réseau : passage en /23, Wi-Fi reconfiguré, autorisations du partage"),
    ),
    explain_terms=("SMART", "WEP", "masque de sous-réseau"),
)

VARIANTS: tuple[Variant, ...] = (VARIANT_1, VARIANT_2)


# =============================================================================================
# Schémas (un plan du réseau et un plan Wi-Fi par variante) — données relevées, sans verdict
# =============================================================================================


def lan_svg(v: Variant) -> str:
    """Box en haut, switch à gauche, une boîte par appareil avec sa configuration relevée ;
    segment coaxial à part. Aucune indication de conformité."""
    width = 380
    box, *others = v.hosts
    parts = [
        _pc_box(72, 6, 304, [f"{box.name} — passerelle, DNS, DHCP", f"LAN {box.ip}/{box.prefix} · Internet {WAN_IP}"]),
        f'<path d="M58 30 H72" stroke="{_STROKE}" stroke-width="2"/>',
    ]
    row_h, gap, top = 59, 6, 58
    bottom = top + len(others) * (row_h + gap) - gap
    parts.append(f'<rect x="4" y="6" width="54" height="{bottom - 6}" rx="8" fill="#e7ecf7" stroke="{_STROKE}" '
                 'stroke-width="1.5"/>')
    parts.append(_text_lines(31, 76, ["Switch"], size=11.5, weight="700", anchor="middle"))
    parts.append(_text_lines(31, 92, ["24 ports"], size=10, anchor="middle"))
    for index, host in enumerate(others):
        y = top + index * (row_h + gap)
        mid = y + row_h // 2
        address = "adresse par DHCP" if host.ip == "DHCP" else f"IP {host.ip} · masque {host.mask}"
        parts.append(f'<path d="M58 {mid} H72" stroke="{_STROKE}" stroke-width="2"/>')
        parts.append(_pc_box(72, y, 304, [
            f"{host.name} — {host.role}",
            address,
            f"passerelle {host.gateway or '(vide)'} · DNS {host.dns[0] if host.dns else '(vide)'}",
        ], key=host.name))
    y = bottom + 12
    names = [s.name for s in v.coax_bus.stations]
    parts.append(f'<rect x="4" y="{y}" width="372" height="40" rx="7" fill="#f7f8fb" stroke="{_STROKE}" '
                 'stroke-width="1.5" stroke-dasharray="5 3"/>')
    parts.append(_text_lines(12, y + 17, [f"Hors switch, {v.coax_room} : segment coaxial", " — ".join(names)],
                             size=10.5, step=15))
    y += 58
    lines = _wrap(f"Box : étendue DHCP de {v.pool[0]} à {v.pool[1]}. Valeurs relevées avant l'intervention.", 60)
    parts.append(_text_lines(8, y, lines, size=10.5, step=13))
    return _svg(width, y + 13 * len(lines), parts)


def lan_alt(v: Variant) -> str:
    box, *others = v.hosts
    return (
        f"Réseau en étoile de {v.company} : la box {box.ip}/{box.prefix} (passerelle, DNS, DHCP, étendue "
        f"{v.pool[0]} à {v.pool[1]}) est reliée à un switch de 24 ports, qui relie : "
        + " ; ".join(
            f"{h.name} ({h.role}) " + ("adresse par DHCP" if h.ip == "DHCP" else f"adresse {h.ip}, masque {h.mask}")
            + f", passerelle {h.gateway or 'vide'}"
            for h in others)
        + f". Hors switch, dans la {v.coax_room}, un segment coaxial relie "
        + ", ".join(s.name for s in v.coax_bus.stations)
        + ". Le schéma ne donne aucun verdict."
    )


def lan_figure(v: Variant) -> Figure:
    return Figure(
        key=f"ex06-v{v.number}-plan-reseau",
        title=f"{v.label}, document 2 — Schéma du réseau de {v.company} (schéma fictif)",
        alt=lan_alt(v),
        caption="Configurations relevées avant l'intervention (fictives). Le schéma ne dit pas ce qui est faux.",
        svg=lan_svg(v),
    )


_OBSTACLE_SHORT = {"vitre": "vitre", "cloison": "cloison", "brique": "mur de briques", "béton": "mur en béton",
                   "dalle": "dalle d'étage", "métal": "rayonnage métallique"}


def _obstacles_text(obstacles: tuple[str, ...]) -> str:
    if not obstacles:
        return "aucun obstacle"
    counts: dict[str, int] = {}
    for o in obstacles:
        counts[o] = counts.get(o, 0) + 1
    return ", ".join(f"{n} × {_OBSTACLE_SHORT[o]}" if n > 1 else _OBSTACLE_SHORT[o] for o, n in counts.items())


def wifi_svg(v: Variant) -> str:
    """Plan schématique (non à l'échelle) : point d'accès AP-01 et points de mesure, avec la
    distance et les obstacles traversés. Aucun niveau de signal ni verdict."""
    width = 380
    parts = [
        (f'<rect x="4" y="6" width="372" height="{75 + 62 * len(v.wifi_points)}" rx="8" fill="#f7f8fb" '
        f'stroke="{_STROKE}" stroke-width="1.5"/>'),
        f'<circle cx="40" cy="38" r="21" fill="#dbe4f3" stroke="{_STROKE}" stroke-width="1.5"/>',
        _text_lines(40, 42, ["AP-01"], size=9.5, weight="700", anchor="middle"),
        _text_lines(66, 36, ["Point d'accès AP-01 (accueil)", "20 dBm rayonnés, 2,4 et 5 GHz"], size=10.5, step=14),
    ]
    for index, point in enumerate(v.wifi_points):
        y = 82 + 62 * index
        parts.append(f'<path d="M40 59 V{y + 14} H92" stroke="{_STROKE}" stroke-width="1.5" stroke-dasharray="4 3" '
                     'fill="none"/>')
        parts.append(_pc_box(92, y, 276, [f"{point.key} — {point.place}",
                                          f"{fr(point.distance_m)} m du point d'accès",
                                          f"traverse : {_obstacles_text(point.obstacles)}"], key=point.key))
    y = 81 + 62 * len(v.wifi_points) + 20
    lines = _wrap(f"Zone à couvrir en priorité : {v.extension.zone}. Plan non à l'échelle.", 60)
    parts.append(_text_lines(8, y, lines, size=10.5, step=13))
    return _svg(width, y + 13 * len(lines), parts)


def wifi_alt(v: Variant) -> str:
    return (
        f"Plan Wi-Fi de {v.company}, non à l'échelle : le point d'accès AP-01 est à l'accueil (20 dBm rayonnés, "
        "2,4 et 5 GHz). Points de mesure : "
        + " ; ".join(f"{p.key}, {p.place}, à {fr(p.distance_m)} m, à travers {_obstacles_text(p.obstacles)}"
                     for p in v.wifi_points)
        + f". Zone à couvrir en priorité : {v.extension.zone}. Aucun niveau de signal n'est indiqué."
    )


def wifi_figure(v: Variant) -> Figure:
    return Figure(
        key=f"ex06-v{v.number}-plan-wifi",
        title=f"{v.label}, document 21 — Plan Wi-Fi et points de mesure (schéma fictif)",
        alt=wifi_alt(v),
        caption="Distances et obstacles relevés sur place (fictifs) ; le signal est à calculer.",
        svg=wifi_svg(v),
    )


def figure_file(figure: Figure) -> str:
    return f"{STATIC_DIR_REF}/{figure.key}.svg"


LAN_FIGURES: tuple[Figure, ...] = tuple(lan_figure(v) for v in VARIANTS)
WIFI_FIGURES: tuple[Figure, ...] = tuple(wifi_figure(v) for v in VARIANTS)
STATIC_FIGURES: tuple[tuple[Figure, str], ...] = tuple(
    (figure, figure_file(figure)) for figure in (*LAN_FIGURES, *WIFI_FIGURES)
)


def boot_screen(v: Variant) -> tuple[str, ...]:
    b = v.boot
    disk = ("SATA port 0 : SSD SATA 1 To (Samsung 870)" if b.disk_in_firmware
            else "SATA port 0 : aucun périphérique")
    return (
        f"Micrologiciel de {b.post} — Informations",
        f"Date et heure : {b.date_shown}",
        disk,
        "SATA port 1 : aucun périphérique",
        f"Mode du contrôleur SATA : {b.controller_now}",
        "Démarrage : UEFI, Secure Boot activé",
        f"Statut SMART : {b.smart_status or 'non disponible'}",
    )


def ipconfig_lines(host: Host) -> tuple[str, ...]:
    auto = host.ip.startswith("169.254.")
    lines = [
        f"C:\\> ipconfig /all   ({host.name})",
        f"   DHCP activé. . . . . . . . . : {'Oui' if host.dhcp else 'Non'}",
        f"   Adresse physique . . . . . . : {normalize_mac(host.mac)}",
        f"   Adresse IPv4 {'autoconfig.' if auto else '. . . . . .'} : {host.ip}",
        f"   Masque de sous-réseau. . . . : {host.mask}",
        f"   Passerelle par défaut. . . . : {host.gateway or ''}".rstrip(),
    ]
    return tuple(lines)


def screens(v: Variant) -> dict[str, tuple[str, ...]]:
    out = {
        "boot": boot_screen(v),
        "tester": tester_lines(v.cord_links),
        "iso": ("$ sha256sum -c SHA256SUMS 2>/dev/null \\", f"    | grep {ISO_NAME}", v.iso_line),
        "efibootmgr": v.efibootmgr,
    }
    for host in v.new_hosts:
        out[f"ipconfig_{host.name}"] = ipconfig_lines(host)
    return out


def static_svg(figure: Figure) -> str:
    """Contenu exact du fichier statique d'un schéma (même règle que EX01 à EX05)."""
    head_end = figure.svg.index(">") + 1
    return (
        figure.svg[:head_end]
        + f"<title>{escape(figure.title)}</title><desc>{escape(figure.alt)}</desc>"
        + figure.svg[head_end:]
        + "\n"
    )

