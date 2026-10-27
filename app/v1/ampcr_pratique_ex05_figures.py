"""EX05 « Examen blanc global standard — épreuve pratique écrite » — données des deux variantes
du dossier et schémas (ticket #201).

Un seul dossier professionnel par variante : une petite entreprise de **6 postes** (box, switch,
serveur de fichiers, NAS, imprimante réseau, un ancien segment coaxial), avec fiche du client,
schéma du réseau local, inventaire du matériel, journal des pannes et relevés. Les deux
variantes ont la même structure (mêmes situations, même barème) et des **données différentes**
(entreprise, adresses, pannes, mesures) ; chaque valeur et chaque verdict est calculé avec la
règle **du cours** qui l'enseigne :

- mémoire et stockage d'un poste lent (PR01, PR05) ; règle d'atelier sur les relevés
  SMART (même règle que EX01) ;
- prérequis de Windows 11 dans le micrologiciel (`firmware_changes`) et activation
  (`activation_result`, PR08) ;
- image Linux et swap (`checksum_verdict`, `swap_advice`, PR09) ;
- canal cuivre (`copper_verdict`, PR14), brochage T568B et testeur (`T568B`, PR15) ;
- segment coaxial 10BASE2 (`bus_errors`, `ohmmeter_reading`, PR16) ;
- plan d'adressage IPv4 (`AddressPlan`, `plan_errors`, `subnet_facts`, PR20) ;
- accès effectif partage + NTFS (`weakest`, PR23) ;
- relevés `ipconfig`, `ping`, `nslookup` (PR20, PR21, PR24).

Entreprises, personnes, adresses et mesures sont **fictives** (adresses publiques des plages de
documentation RFC 5737). Les schémas ne donnent **aucun verdict** ; ils sont aussi enregistrés en
fichiers statiques (`app/static/img/ampcr-pratique/`), identiques au SVG produit ici (test).
"""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass
from html import escape

from app.v1.ampcr_pratique_pr08_figures import LIC_DIGITAL, LIC_OEM, activation_result
from app.v1.ampcr_pratique_pr09_figures import ISO_NAME, checksum_verdict, swap_advice
from app.v1.ampcr_pratique_pr14_figures import copper_verdict
from app.v1.ampcr_pratique_pr15_figures import TESTER_OPEN, TESTER_REVERSED
from app.v1.ampcr_pratique_pr16_figures import (
    GROUNDED_TERMINATOR,
    Bus,
    BusEnd,
    _stations_bus,
    bus_errors,
    ohmmeter_reading,
)
from app.v1.ampcr_pratique_pr20_figures import (
    AddressPlan,
    Host,
    ipconfig_all_lines,
    normalize_mac,
    plan_errors,
    subnet_facts,
)
from app.v1.ampcr_pratique_pr21_figures import OUT_REPLY, _pc_box, ping_lines, ping_outcome
from app.v1.ampcr_pratique_pr23_figures import LEVEL_MODIFY, LEVEL_NONE, LEVEL_READ, weakest
from app.v1.ampcr_pratique_pr24_figures import (
    NS_TIMEOUT,
    win_ping_lines,
    win_ping_unknown_name,
)
from app.v1.ampcr_pratique_pr24_figures import nslookup_lines as _nslookup_lines
from app.v1.ampcr_pratique_visuals import T568B, Figure, _svg, _text_lines, _wrap

STATIC_DIR_REF = "img/ampcr-pratique"
SCREEN_WIDTH = 56  # caractères au plus par ligne de capture (comme les cours)
_STROKE = "#33415c"
WEB_NAME = "www.exemple.be"
WEB_IP = "198.51.100.20"  # site de test fictif (RFC 5737)
WAN_IP = "203.0.113.45"  # adresse publique de la box (RFC 5737)

# --- Règles reprises des cours -------------------------------------------------------------

# Règle d'atelier sur les relevés SMART (même formulation que EX01, cours PR06).
SMART_RULE = ("Règle de l'atelier : secteurs en attente ou illisibles supérieurs à 0 → disque à remplacer ; "
              "secteurs réalloués seuls → à surveiller.")
SMART_REPLACE = "À remplacer"
SMART_WATCH = "À surveiller"
SMART_OK = "Sain"


def smart_verdict(reallocated: int, pending: int, uncorrectable: int) -> str:
    if pending > 0 or uncorrectable > 0:
        return SMART_REPLACE
    if reallocated > 0:
        return SMART_WATCH
    return SMART_OK


# Prérequis de Windows 11 vérifiés dans le micrologiciel (cours PR08) : démarrage UEFI sans
# CSM, démarrage sécurisé, TPM 2.0 ; contrôleur de stockage en AHCI pour que l'installateur
# voie le disque sans pilote supplémentaire (sinon : charger le pilote RST/VMD).
FIRMWARE_REQUIRED: dict[str, str] = {
    "Mode de démarrage": "UEFI (CSM désactivé)",
    "Démarrage sécurisé (Secure Boot)": "Activé",
    "TPM 2.0 (Intel PTT / AMD fTPM)": "Activé",
    "Mode du contrôleur SATA": "AHCI",
}


def firmware_changes(settings: dict[str, str]) -> list[tuple[str, str, str]]:
    """(réglage, valeur relevée, valeur à mettre) pour chaque réglage non conforme."""
    return [(name, settings[name], wanted) for name, wanted in FIRMWARE_REQUIRED.items() if settings[name] != wanted]


def effective_access(share: str, ntfs: str) -> str:
    """Accès par le réseau : le plus restrictif du partage et de NTFS (cours PR23)."""
    return weakest(share, ntfs)


def minutes(hhmm: str) -> int:
    hours, mins = hhmm.split(":")
    return int(hours) * 60 + int(mins)


def duration_text(total: int) -> str:
    return f"{total // 60} h {total % 60:02d}"


def fr(value: float) -> str:
    return f"{value:g}".replace(".", ",")


# --- Une variante du dossier -----------------------------------------------------------------


@dataclass(frozen=True)
class InventoryRow:
    name: str
    user: str
    os: str
    cpu: str
    ram: str
    storage: str
    year: int


@dataclass(frozen=True)
class SmartRow:
    post: str
    disk: str
    hours: int
    reallocated: int
    pending: int
    uncorrectable: int

    @property
    def verdict(self) -> str:
        return smart_verdict(self.reallocated, self.pending, self.uncorrectable)


@dataclass(frozen=True)
class Variant:
    number: int
    company: str
    activity: str
    city: str
    manager: str
    date: str
    network: str
    box_ip: str
    pool: tuple[str, str]
    srv_ip: str
    nas_ip: str
    printer_ip_rule: str
    hosts: tuple[Host, ...]  # configurations relevées (schéma du réseau), box en premier
    inventory: tuple[InventoryRow, ...]
    # Situation 1 — poste lent
    slow_post: str
    ram_type: str  # type de barrette installée
    ram_modules: tuple[int, ...]  # Go par barrette installée
    ram_slots: int
    ram_max_gb: int
    ram_used: tuple[float, float]  # Go utilisés / Go utilisables (Gestionnaire des tâches)
    disk_busy_pct: int
    disk_label: str
    # Situation 2 — relevés SMART
    smart: tuple[SmartRow, ...]
    # Situation 3 — Windows 11 sur le poste réparé
    firmware: dict[str, str]
    licence: str
    # Situation 4 — Linux
    linux_post: str
    iso_check_line: str
    linux_ram_gb: int
    linux_disk_gb: int
    # Situation 5 — RJ45
    tester_links: tuple[tuple[int, int | None], ...]
    run_post: str
    run_permanent_m: int
    run_cords_m: tuple[int, int]
    # Situation 6 — coaxial
    coax_bus: Bus
    coax_room: str
    # Situation 8 — partages
    accounts: tuple[tuple[str, str, tuple[str, ...]], ...]  # (prénom, fonction, groupes)
    shares: dict[str, str]  # dossier → autorisation du partage (pour tous les comptes)
    ntfs: dict[str, dict[str, str]]  # dossier → groupe → niveau NTFS
    need: tuple[str, str, str]  # (prénom, dossier, niveau demandé)
    # Situation 9 — portable sans Internet
    laptop: Host
    laptop_fault: str  # « dns » ou « gateway »
    old_dns: str
    # Situation 10 — journal d'intervention
    journal: tuple[tuple[str, str, str], ...]
    explain_terms: tuple[str, ...]

    # --- Valeurs calculées ----------------------------------------------------------------

    @property
    def label(self) -> str:
        return f"Variante {self.number}"

    @property
    def prefix(self) -> int:
        return ipaddress.IPv4Network(self.network).prefixlen

    @property
    def facts(self):
        return subnet_facts(self.box_ip, self.prefix)

    @property
    def plan(self) -> AddressPlan:
        return AddressPlan(self.network, self.hosts, self.box_ip, self.box_ip, self.pool)

    @property
    def plan_errors(self) -> list[str]:
        return plan_errors(self.plan)

    def host(self, name: str) -> Host:
        return next(h for h in self.hosts if h.name == name)

    # Situation 1
    @property
    def ram_installed_gb(self) -> int:
        return sum(self.ram_modules)

    @property
    def ram_added_gb(self) -> int:
        """Barrette identique à celle en place (même type, même capacité) dans un emplacement
        libre : double canal et compatibilité garantis."""
        assert len(self.ram_modules) < self.ram_slots
        return self.ram_modules[0]

    @property
    def ram_after_gb(self) -> int:
        total = self.ram_installed_gb + self.ram_added_gb
        assert total <= self.ram_max_gb
        return total

    @property
    def ram_used_pct(self) -> int:
        return round(100 * self.ram_used[0] / self.ram_used[1])

    # Situation 2
    @property
    def failing(self) -> SmartRow:
        rows = [r for r in self.smart if r.verdict == SMART_REPLACE]
        assert len(rows) == 1
        return rows[0]

    # Situation 3
    @property
    def firmware_changes(self) -> list[tuple[str, str, str]]:
        return firmware_changes(self.firmware)

    @property
    def activation(self) -> tuple[str, str]:
        return activation_result(self.licence, "Pro", "Pro", same_pc=True)

    # Situation 4
    @property
    def iso_verdict(self) -> str:
        return checksum_verdict(self.iso_check_line)

    @property
    def swap_gb(self) -> float:
        swap = swap_advice(self.linux_ram_gb, hibernation=False)
        assert swap is not None
        return swap

    @property
    def linux_layout(self) -> tuple[tuple[str, str, str, str], ...]:
        """(partition, système de fichiers, point de montage, taille) — ESP 1 Go, racine
        50 Go, swap selon la mémoire, /home pour le reste (repères du cours PR09)."""
        home = self.linux_disk_gb - 1 - 50 - self.swap_gb
        return (
            ("ESP", "FAT32", "/boot/efi", "1 Go"),
            ("Racine", "ext4", "/", "50 Go"),
            ("Swap", "swap", "[SWAP]", f"{fr(self.swap_gb)} Go"),
            ("Dossiers personnels", "ext4", "/home", f"le reste, environ {fr(home)} Go"),
        )

    # Situation 5
    @property
    def run_total_m(self) -> int:
        return self.run_permanent_m + sum(self.run_cords_m)

    @property
    def run_verdict(self) -> str:
        return copper_verdict("1000BASE-T", "Cat6", self.run_total_m)

    @property
    def tester_faults(self) -> list[str]:
        faults = []
        for pin_a, pin_b in self.tester_links:
            if pin_b is None:
                faults.append(f"broche {pin_a} ouverte (fil {T568B[pin_a - 1]})")
            elif pin_b != pin_a:
                faults.append(f"broche {pin_a} arrive en {pin_b}")
        return faults

    # Situation 6
    @property
    def coax_errors(self) -> list[str]:
        return bus_errors(self.coax_bus)

    @property
    def coax_reading(self) -> float | None:
        return ohmmeter_reading(self.coax_bus, 0)

    # Situation 8
    def ntfs_level(self, groups: tuple[str, ...], folder: str) -> str:
        levels = [self.ntfs[folder].get(g, LEVEL_NONE) for g in groups]
        return max(levels, key=(LEVEL_NONE, LEVEL_READ, LEVEL_MODIFY).index)

    def access(self, person: str, folder: str) -> str:
        groups = next(g for p, _f, g in self.accounts if p == person)
        return effective_access(self.shares[folder], self.ntfs_level(groups, folder))

    @property
    def access_matrix(self) -> dict[str, dict[str, str]]:
        return {p: {f: self.access(p, f) for f in self.shares} for p, _f, _g in self.accounts}

    @property
    def need_limiting_layer(self) -> str:
        person, folder, wanted = self.need
        groups = next(g for p, _f, g in self.accounts if p == person)
        ranks = (LEVEL_NONE, LEVEL_READ, LEVEL_MODIFY)
        share_ok = ranks.index(self.shares[folder]) >= ranks.index(wanted)
        ntfs_ok = ranks.index(self.ntfs_level(groups, folder)) >= ranks.index(wanted)
        assert not (share_ok and ntfs_ok)
        return "partage" if not share_ok else "NTFS"

    # Situation 9
    @property
    def laptop_screens(self) -> tuple[tuple[str, ...], ...]:
        lap = self.laptop
        ipconfig = ("C:\\> ipconfig /all", "", *ipconfig_all_lines(lap, dhcp_server=None, iface="Ethernet"))
        ping_box = ping_lines(lap, self.box_ip, ping_outcome(lap, self.box_ip, self.hosts[0]), ttl=64)
        if self.laptop_fault == "dns":
            return (ipconfig, ping_box, win_ping_lines(WEB_IP, (12, 11, 12, 13), ttl=56),
                    win_ping_unknown_name(WEB_NAME), nslookup_lines(WEB_NAME, self.old_dns, NS_TIMEOUT))
        ping_srv = ping_lines(lap, self.srv_ip, OUT_REPLY)
        ping_web = ping_lines(lap, WEB_IP, ping_outcome(lap, WEB_IP, None))
        return ipconfig, ping_box, ping_srv, ping_web

    # Situation 10
    @property
    def journal_minutes(self) -> int:
        return sum(minutes(end) - minutes(start) for start, end, _a in self.journal)


def nslookup_lines(name: str, server: str, status: str) -> tuple[str, ...]:
    return _nslookup_lines(name, server, status)


def _h(name: str, role: str, ip: str, prefix: int, gateway: str | None, mac: str, *, dns: str | None = None,
       dhcp: bool = False) -> Host:
    return Host(name, role, ip, prefix, gateway, (dns or gateway,) if (dns or gateway) else (), mac, dhcp)


# =============================================================================================
# Variante 1 — Fiduciaire Leclercq (Namur), réseau 192.168.1.0/24
# =============================================================================================

_V1_BOX = "192.168.1.1"
VARIANT_1 = Variant(
    number=1,
    company="Fiduciaire Leclercq",
    activity="bureau comptable",
    city="Namur",
    manager="Mme Leclercq (gérante)",
    date="mardi 3 novembre 2026",
    network="192.168.1.0/24",
    box_ip=_V1_BOX,
    pool=("192.168.1.100", "192.168.1.199"),
    srv_ip="192.168.1.5",
    nas_ip="192.168.1.10",
    printer_ip_rule="serveurs et NAS de .2 à .19, imprimantes de .20 à .29, postes fixes de .30 à .49",
    hosts=(
        _h("BOX", "box du fournisseur", _V1_BOX, 24, None, "00-1E-58-A1-00-01"),
        _h("SRV-01", "serveur de fichiers", "192.168.1.5", 24, _V1_BOX, "3C-52-82-11-00-05"),
        _h("NAS-01", "sauvegardes", "192.168.1.10", 24, _V1_BOX, "00-11-32-AB-00-10"),
        _h("IMP-01", "imprimante laser", "192.168.1.120", 24, _V1_BOX, "00-80-77-31-01-20"),
        _h("PC-01", "accueil", "192.168.1.101", 24, _V1_BOX, "3C-52-82-11-01-01", dhcp=True),
        _h("PC-02", "comptable", "192.168.1.102", 24, _V1_BOX, "3C-52-82-11-01-02", dhcp=True),
        _h("PC-03", "comptable", "192.168.1.103", 24, _V1_BOX, "3C-52-82-11-01-03", dhcp=True),
        _h("PC-04", "comptable", "192.168.1.104", 24, _V1_BOX, "3C-52-82-11-01-04", dhcp=True),
        _h("PC-05", "numérisation (Linux)", "192.168.1.105", 24, _V1_BOX, "3C-52-82-11-01-05", dhcp=True),
        _h("PC-06", "gérante", "192.168.1.30", 16, _V1_BOX, "3C-52-82-11-01-06"),
    ),
    inventory=(
        InventoryRow("PC-01", "accueil", "Windows 11 Pro", "Intel Core i5-12400", "16 Go DDR4", "SSD NVMe 512 Go", 2023),
        InventoryRow("PC-02", "comptable", "Windows 11 Pro", "Intel Core i5-10400", "16 Go DDR4",
                     "HDD SATA 1 To", 2020),
        InventoryRow("PC-03", "comptable", "Windows 11 Pro", "Intel Core i5-12400", "16 Go DDR4", "SSD NVMe 512 Go", 2023),
        InventoryRow("PC-04", "comptable", "Windows 11 Pro", "Intel Core i5-8500", "8 Go DDR4-2666 (1 barrette)",
                     "HDD SATA 1 To 7 200 tr/min", 2019),
        InventoryRow("PC-05", "numérisation", "à installer : Ubuntu 24.04 LTS", "Intel Core i3-10100", "8 Go DDR4",
                     "SSD SATA 256 Go", 2020),
        InventoryRow("PC-06", "gérante", "Windows 11 Pro", "Intel Core i7-12700", "32 Go DDR4", "SSD NVMe 1 To", 2023),
    ),
    slow_post="PC-04",
    ram_type="DDR4-2666 DIMM (barrette de PC fixe)",
    ram_modules=(8,),
    ram_slots=2,
    ram_max_gb=64,
    ram_used=(7.4, 7.9),
    disk_busy_pct=100,
    disk_label="HDD SATA 1 To 7 200 tr/min",
    smart=(
        SmartRow("PC-02", "HDD SATA 1 To", 31_200, 152, 24, 24),
        SmartRow("PC-04", "HDD SATA 1 To", 26_400, 0, 0, 0),
    ),
    firmware={
        "Mode de démarrage": "UEFI (CSM désactivé)",
        "Démarrage sécurisé (Secure Boot)": "Activé",
        "TPM 2.0 (Intel PTT / AMD fTPM)": "Désactivé",
        "Mode du contrôleur SATA": "AHCI",
    },
    licence=LIC_OEM,
    linux_post="PC-05",
    iso_check_line=f"{ISO_NAME}: OK",
    linux_ram_gb=8,
    linux_disk_gb=256,
    tester_links=TESTER_REVERSED,
    run_post="PC-06",
    run_permanent_m=82,
    run_cords_m=(3, 5),
    coax_bus=_stations_bus(("PC-ARCH1", "PC-ARCH2", "SRV-ARCH"), (9, 14), first=GROUNDED_TERMINATOR,
                           last=BusEnd(None)),
    coax_room="local des archives",
    accounts=(
        ("Anne", "gérante", ("G_Direction", "G_Compta")),
        ("Marc", "comptable", ("G_Compta",)),
        ("Julie", "accueil", ("G_Accueil",)),
    ),
    shares={"Compta": LEVEL_READ, "Clients": LEVEL_MODIFY},
    ntfs={
        "Compta": {"G_Compta": LEVEL_MODIFY, "G_Direction": LEVEL_READ},
        "Clients": {"G_Accueil": LEVEL_MODIFY, "G_Compta": LEVEL_READ, "G_Direction": LEVEL_MODIFY},
    },
    need=("Marc", "Compta", LEVEL_MODIFY),
    laptop=_h("PORT-GERANTE", "portable de la gérante", "192.168.1.40", 24, _V1_BOX, "A4-C3-F0-12-34-40",
              dns="192.168.1.2"),
    laptop_fault="dns",
    old_dns="192.168.1.2",
    journal=(
        ("08:40", "09:05", "Diagnostic de PC-02 : relevé SMART, journal système"),
        ("09:05", "09:50", "Sauvegarde des données de PC-02 vers NAS-01, contrôle de la copie"),
        ("09:50", "10:10", "Remplacement du disque (SSD SATA 1 To), poste hors tension, bracelet antistatique"),
        ("10:10", "11:05", "Réglage du micrologiciel et installation de Windows 11 Pro"),
        ("11:05", "11:40", "Pilotes, mises à jour, activation"),
        ("11:40", "12:05", "Restauration des données, lecteurs réseau, imprimante, tests avec Marc"),
    ),
    explain_terms=("SMART", "SSD", "sauvegarde"),
)

# =============================================================================================
# Variante 2 — Bureau de géomètres Hautem (Wavre), réseau 172.16.40.0/23
# =============================================================================================

_V2_BOX = "172.16.40.1"
VARIANT_2 = Variant(
    number=2,
    company="Bureau de géomètres Hautem",
    activity="bureau de géomètres-experts",
    city="Wavre",
    manager="M. Hautem (associé gérant)",
    date="jeudi 5 novembre 2026",
    network="172.16.40.0/23",
    box_ip=_V2_BOX,
    pool=("172.16.41.100", "172.16.41.199"),
    srv_ip="172.16.40.5",
    nas_ip="172.16.40.10",
    printer_ip_rule="serveurs et NAS de 172.16.40.2 à .19, imprimantes de .20 à .29, postes fixes de 172.16.41.10 à .49",
    hosts=(
        _h("BOX", "box du fournisseur", _V2_BOX, 23, None, "00-1E-58-B2-00-01"),
        _h("SRV-01", "serveur de fichiers", "172.16.40.5", 23, _V2_BOX, "3C-52-82-22-00-05"),
        _h("NAS-01", "sauvegardes", "172.16.40.10", 23, _V2_BOX, "00-11-32-CD-00-10"),
        _h("IMP-01", "traceur A0", "172.16.40.20", 23, _V2_BOX, "00-80-77-31-02-20"),
        _h("PC-01", "accueil", "172.16.41.101", 23, _V2_BOX, "3C-52-82-22-01-01", dhcp=True),
        _h("PC-02", "géomètre", "172.16.41.102", 23, _V2_BOX, "3C-52-82-22-01-02", dhcp=True),
        _h("PC-03", "dessinateur", "172.16.41.103", 23, _V2_BOX, "3C-52-82-22-01-03", dhcp=True),
        _h("PC-04", "géomètre", "172.16.41.30", 24, _V2_BOX, "3C-52-82-22-01-04"),
        _h("PC-05", "traitement des relevés (Linux)", "172.16.41.105", 23, _V2_BOX, "3C-52-82-22-01-05", dhcp=True),
        _h("PC-06", "associé", "172.16.40.10", 23, _V2_BOX, "3C-52-82-22-01-06"),
    ),
    inventory=(
        InventoryRow("PC-01", "accueil", "Windows 11 Pro", "Intel Core i5-12400", "16 Go DDR4", "SSD NVMe 512 Go", 2023),
        InventoryRow("PC-02", "géomètre", "Windows 11 Pro", "AMD Ryzen 7 5700G", "32 Go DDR4", "SSD NVMe 1 To", 2022),
        InventoryRow("PC-03", "dessinateur", "Windows 11 Pro", "Intel Core i7-10700", "32 Go DDR4",
                     "HDD SATA 2 To", 2020),
        InventoryRow("PC-04", "géomètre", "Windows 11 Pro", "AMD Ryzen 5 5600G", "16 Go DDR4", "SSD NVMe 512 Go", 2022),
        InventoryRow("PC-05", "relevés", "à installer : Ubuntu 24.04 LTS", "Intel Core i5-10500", "16 Go DDR4",
                     "SSD NVMe 512 Go", 2021),
        InventoryRow("PC-06", "associé (portable)", "Windows 11 Pro", "Intel Core Ultra 5 125U",
                     "8 Go DDR5-5600 SO-DIMM (1 barrette)", "SSD NVMe 512 Go", 2024),
    ),
    slow_post="PC-06",
    ram_type="DDR5-5600 SO-DIMM (barrette de portable)",
    ram_modules=(8,),
    ram_slots=2,
    ram_max_gb=96,
    ram_used=(7.3, 7.6),
    disk_busy_pct=35,
    disk_label="SSD NVMe 512 Go",
    smart=(
        SmartRow("PC-03", "HDD SATA 2 To", 29_800, 0, 8, 8),
        SmartRow("NAS-01", "disque 1, HDD 4 To", 21_300, 16, 0, 0),
    ),
    firmware={
        "Mode de démarrage": "Legacy (CSM activé)",
        "Démarrage sécurisé (Secure Boot)": "Désactivé",
        "TPM 2.0 (Intel PTT / AMD fTPM)": "Activé",
        "Mode du contrôleur SATA": "Intel RST (RAID)",
    },
    licence=LIC_DIGITAL,
    linux_post="PC-05",
    iso_check_line=f"{ISO_NAME}: FAILED",
    linux_ram_gb=16,
    linux_disk_gb=512,
    tester_links=TESTER_OPEN,
    run_post="PC-02",
    run_permanent_m=96,
    run_cords_m=(2, 5),
    coax_bus=_stations_bus(("PC-PLAN1", "PC-PLAN2", "PC-TRACE"), (11, 7), first=GROUNDED_TERMINATOR,
                           last=BusEnd(75), cables={1: "RG-59"}),
    coax_room="atelier de reprographie",
    accounts=(
        ("Paul", "associé", ("G_Associes", "G_Etudes")),
        ("Sarah", "géomètre", ("G_Etudes",)),
        ("Léo", "dessinateur", ("G_Dessin",)),
    ),
    shares={"Etudes": LEVEL_MODIFY, "Plans": LEVEL_MODIFY},
    ntfs={
        "Etudes": {"G_Associes": LEVEL_MODIFY, "G_Etudes": LEVEL_READ, "G_Dessin": LEVEL_READ},
        "Plans": {"G_Dessin": LEVEL_MODIFY, "G_Etudes": LEVEL_MODIFY},
    },
    need=("Sarah", "Etudes", LEVEL_MODIFY),
    laptop=_h("PORT-ASSOCIE", "portable de l'associé", "172.16.41.40", 23, None, "A4-C3-F0-56-78-40",
              dns=_V2_BOX),
    laptop_fault="gateway",
    old_dns="",
    journal=(
        ("13:15", "13:35", "Diagnostic de PC-03 : relevé SMART, observateur d'événements"),
        ("13:35", "14:40", "Sauvegarde des données de PC-03 vers NAS-01, contrôle de la copie"),
        ("14:40", "15:00", "Remplacement du disque (SSD SATA 2 To), poste hors tension, bracelet antistatique"),
        ("15:00", "16:10", "Réglage du micrologiciel et installation de Windows 11 Pro"),
        ("16:10", "16:45", "Pilotes, mises à jour, activation"),
        ("16:45", "17:20", "Restauration des données, lecteurs réseau, traceur, tests avec Léo"),
    ),
    explain_terms=("TPM", "SSD", "micrologiciel (UEFI)"),
)

VARIANTS: tuple[Variant, ...] = (VARIANT_1, VARIANT_2)


# =============================================================================================
# Schéma du réseau local (un par variante) — configurations relevées, sans verdict
# =============================================================================================


def lan_svg(v: Variant) -> str:
    """Box en haut, switch 16 ports à gauche, une boîte par appareil avec sa configuration
    relevée ; segment coaxial des archives en bas. Aucune indication de conformité."""
    width = 380
    box, *others = v.hosts
    parts = [
        _pc_box(72, 6, 304, [f"{box.name} — passerelle, DNS, DHCP",
                             f"LAN {box.ip}/{box.prefix} · Internet {WAN_IP}"]),
        f'<path d="M58 30 H72" stroke="{_STROKE}" stroke-width="2"/>',
    ]
    row_h, gap, top = 74, 6, 58
    bottom = top + len(others) * (row_h + gap) - gap
    parts.append(f'<rect x="4" y="6" width="54" height="{bottom - 6}" rx="8" fill="#e7ecf7" stroke="{_STROKE}" '
                 'stroke-width="1.5"/>')
    parts.append(_text_lines(31, 76, ["Switch"], size=11.5, weight="700", anchor="middle"))
    parts.append(_text_lines(31, 92, ["16 ports"], size=10, anchor="middle"))
    for index, host in enumerate(others):
        y = top + index * (row_h + gap)
        mid = y + row_h // 2
        mode = "DHCP" if host.dhcp else "fixe"
        parts.append(f'<path d="M58 {mid} H72" stroke="{_STROKE}" stroke-width="2"/>')
        parts.append(_pc_box(72, y, 304, [
            f"{host.name} — {host.role}",
            f"IP {host.ip} · masque {host.mask} ({mode})",
            f"passerelle {host.gateway or '(vide)'} · DNS {host.dns[0] if host.dns else '(vide)'}",
            f"MAC {normalize_mac(host.mac)}",
        ], key=host.name))
    y = bottom + 12
    names = [s.name for s in v.coax_bus.stations]
    parts.append(f'<rect x="4" y="{y}" width="372" height="40" rx="7" fill="#f7f8fb" stroke="{_STROKE}" '
                 'stroke-width="1.5" stroke-dasharray="5 3"/>')
    parts.append(_text_lines(12, y + 17, [f"Hors switch, {v.coax_room} : segment coaxial", " — ".join(names)],
                             size=10.5, step=15))
    y += 58
    lines = _wrap(f"Box : étendue DHCP de {v.pool[0]} à {v.pool[1]}. Valeurs relevées sur chaque appareil.", 60)
    parts.append(_text_lines(8, y, lines, size=10.5, step=13))
    return _svg(width, y + 13 * len(lines), parts)


def lan_alt(v: Variant) -> str:
    box, *others = v.hosts
    return (
        f"Réseau en étoile : la box {box.ip}/{box.prefix} (passerelle, DNS, DHCP, étendue {v.pool[0]} à "
        f"{v.pool[1]}) est reliée à un switch de 16 ports, qui relie : "
        + " ; ".join(
            f"{h.name} ({h.role}) adresse {h.ip}, masque {h.mask}, {'DHCP' if h.dhcp else 'adresse fixe'}, "
            f"passerelle {h.gateway or 'vide'}, DNS {h.dns[0] if h.dns else 'vide'}, MAC {normalize_mac(h.mac)}"
            for h in others)
        + f". Hors switch, dans le {v.coax_room}, un segment coaxial relie "
        + ", ".join(s.name for s in v.coax_bus.stations)
        + ". Le schéma ne donne aucun verdict."
    )


def lan_figure(v: Variant) -> Figure:
    return Figure(
        key=f"ex05-v{v.number}-plan-reseau",
        title=f"{v.label}, document 2 — Schéma du réseau de {v.company} (schéma fictif)",
        alt=lan_alt(v),
        caption="Configurations relevées sur chaque appareil (fictives). Le schéma ne dit pas ce qui est faux.",
        svg=lan_svg(v),
    )


def lan_figure_file(v: Variant) -> str:
    return f"{STATIC_DIR_REF}/ex05-v{v.number}-plan-reseau.svg"


LAN_FIGURES: tuple[Figure, ...] = tuple(lan_figure(v) for v in VARIANTS)
STATIC_FIGURES: tuple[tuple[Figure, str], ...] = tuple(
    (lan_figure(v), lan_figure_file(v)) for v in VARIANTS
)


def tester_lines(links: tuple[tuple[int, int | None], ...]) -> tuple[str, ...]:
    """Affichage texte d'un testeur de câble (carte des fils, extrémité A → B)."""
    return (
        "Testeur de câble — carte des fils",
        "Extrémité A : 1  2  3  4  5  6  7  8",
        "Extrémité B : " + "  ".join("-" if b is None else str(b) for _a, b in links),
        "(« - » : aucune continuité sur cette broche)",
    )


def arp_lines(v: Variant) -> tuple[str, ...]:
    """`arp -a` sur SRV-01 : correspondances IPv4 → MAC apprises sur le réseau. En cas de
    doublon d'adresse, l'entrée porte la MAC du dernier appareil qui a répondu (ici le poste
    configuré en dernier)."""
    srv = v.host("SRV-01")
    shown = ("BOX", "NAS-01", "IMP-01", "PC-01")
    owners: dict[str, Host] = {}
    for host in v.hosts:
        owners[host.ip] = host  # le dernier appareil déclaré à une adresse l'emporte
    lines = ["C:\\> arp -a", f"Interface : {srv.ip} --- 0x6",
             "  Adresse Internet   Adresse physique    Type"]
    for name in shown:
        ip = v.host(name).ip
        mac = normalize_mac(owners[ip].mac).lower()
        lines.append(f"  {ip:<18} {mac:<19} dynamique")
    return tuple(lines)


def screens(v: Variant) -> dict[str, tuple[str, ...]]:
    return {
        "tester": tester_lines(v.tester_links),
        "arp": arp_lines(v),
        "iso": ("$ sha256sum -c SHA256SUMS 2>/dev/null \\", f"    | grep {ISO_NAME}", v.iso_check_line),
        **{f"laptop_{i}": lines for i, lines in enumerate(v.laptop_screens)},
    }


def static_svg(figure: Figure) -> str:
    """Contenu exact du fichier statique d'un schéma (même règle que EX01 à EX04)."""
    head_end = figure.svg.index(">") + 1
    return (
        figure.svg[:head_end]
        + f"<title>{escape(figure.title)}</title><desc>{escape(figure.alt)}</desc>"
        + figure.svg[head_end:]
        + "\n"
    )
