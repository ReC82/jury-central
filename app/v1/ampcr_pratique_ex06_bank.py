"""EX06 « Examen blanc global avancé — dossiers complexes » — les questions notées /100
(ticket #234).

Examen blanc **global avancé** (tout le parcours PR01 → PR30), plus exigeant que EX05 : un
client par variante et **quatre dossiers d'intervention**, chacun avec plusieurs causes
possibles, des indices plausibles mais non décisifs, des calculs, des procédures, des tests
discriminants et la protection des données. **12 situations** à réponse libre (réserve `exam`
uniquement, `ampcr-pratique-ex06:exam`) :

| Dossier | Situations | Points |
|---|---|---|
| A. Poste qui ne démarre plus, stockage et données | 1 (9), 2 (8), 3 (8) | 25 |
| B. Évolution du parc : compatibilité et installations | 4 (9), 5 (8), 6 (8) | 25 |
| C. Câblage cuivre et coaxial | 7 (8), 8 (9) | 17 |
| D. Réseau, Wi-Fi, partages et rapport | 9 (9), 10 (8), 11 (8), 12 (8) | 33 |

**Deux variantes de données** (`VARIANTS` : même structure, même barème ; client, pannes,
mesures et réponses différents), calculées et vérifiées par les règles des cours
(`app.v1.ampcr_pratique_ex06_figures`). Une session sert **une variante entière**, dans l'ordre
des situations (`app.v1.ampcr_pratique_bank.select_exam_variant`). Les situations ne reprennent
aucune situation de EX05 (couverture comparée sur la page du sujet). Situations fictives ;
aucune n'est présentée comme officielle ou déjà posée par le Jury.
"""

from app.v1.ampcr_pratique_ex06_figures import (
    CAUSE_CONTROLLER,
    SPEED_100,
    VARIANTS,
    Variant,
    boot_screen,
    duration_text,
    figure_file,
    fr,
    ipconfig_lines,
    lan_figure,
    tester_lines,
    wifi_figure,
)
from app.v1.ampcr_pratique_format import ExerciseDocument, validate_exercise
from app.v1.ampcr_pratique_pr02_figures import recommended_psu
from app.v1.ampcr_pratique_pr04_bank import _c, _console, _table
from app.v1.ampcr_pratique_pr05_figures import FS_EXFAT, FS_FAT32
from app.v1.ampcr_pratique_pr06_bank import USAGE_EXAM, PR06Item
from app.v1.ampcr_pratique_pr08_figures import ACTIVATES
from app.v1.ampcr_pratique_pr09_figures import DB_STOP, ISO_OK
from app.v1.ampcr_pratique_pr16_figures import ATTACH_STUB, FAULT_OPEN, THIN_SEGMENT_MAX_M
from app.v1.ampcr_pratique_pr25_figures import TARGET_DBM
from app.v1.ampcr_pratique_pr28_figures import CMOS_NOMINAL

EX06_CODE = "EX06"
EXAM_TOTAL_POINTS = 100
SITUATIONS = 12
KIND_DOC = "analyse de document"

# Dossiers (répartition annoncée des points) et cours à revoir par situation.
DOSSIERS: tuple[tuple[str, str, tuple[int, ...]], ...] = (
    ("A", "Poste qui ne démarre plus, stockage et données", (1, 2, 3)),
    ("B", "Évolution du parc : compatibilité et installations", (4, 5, 6)),
    ("C", "Câblage cuivre et coaxial", (7, 8)),
    ("D", "Réseau, Wi-Fi, partages et rapport", (9, 10, 11, 12)),
)
SITUATION_POINTS: dict[int, int] = {1: 9, 2: 8, 3: 8, 4: 9, 5: 8, 6: 8, 7: 8, 8: 9, 9: 9, 10: 8, 11: 8, 12: 8}
SITUATION_COURSES: dict[int, tuple[str, ...]] = {
    1: ("PR06", "PR11", "PR27"),
    2: ("PR05", "PR04"),
    3: ("PR28", "PR12"),
    4: ("PR02", "PR01", "PR03"),
    5: ("PR08", "PR07"),
    6: ("PR09", "PR28"),
    7: ("PR15", "PR14"),
    8: ("PR16", "PR13"),
    9: ("PR20", "PR24"),
    10: ("PR25",),
    11: ("PR23", "PR22"),
    12: ("PR29", "PR26"),
}
# Couverture comparée avec EX05 : ce que chaque situation ajoute (affiché sur la page).
EX05_COMPARISON: dict[int, str] = {
    1: "EX05 : disque à remplacer d'après SMART ; ici trois causes à départager par des tests",
    2: "nouveau : tables de partitions, unités affichées, système de fichiers, défragmentation",
    3: "EX05 : sauvegarde avant remplacement ; ici règle 3-2-1, contrôle d'une copie, effacement",
    4: "nouveau : devis à contrôler (compatibilité, budget de puissance)",
    5: "EX05 : prérequis du micrologiciel ; ici disque invisible ou disque MBR, édition et activation",
    6: "EX05 : partitions d'un Linux seul ; ici double démarrage, accord écrit, ordre de démarrage",
    7: "EX05 : paire inversée ou fil ouvert ; ici lien à 100 Mb/s ou paires séparées",
    8: "EX05 : terminateur ; ici dérivation, longueur ou coupure localisée par mesures",
    9: "EX05 : erreurs d'un plan /24 ou /23 ; ici agrandir le réseau (préfixe à calculer)",
    10: "nouveau : couverture, canal, sécurité, répéteur ou point d'accès câblé",
    11: "EX05 : partage + NTFS simples ; ici héritage désactivé, refus, accès local ou distant",
    12: "EX05 : rapport d'une intervention ; ici rapport d'une journée à quatre dossiers, avec pause",
}


def item_key(v: Variant, situation: int) -> str:
    return f"V{v.number}Q{situation:02d}"


def _schema(title: str, text: str, image: str) -> ExerciseDocument:
    return ExerciseDocument(title=title, kind="schéma", content_text=text, image=image)


def _ctx(v: Variant, dossier: str, text: str) -> str:
    name = next(title for letter, title, _n in DOSSIERS if letter == dossier)
    return f"{v.label}. Dossier {dossier} ({name.lower()}). {v.company} : {text}"


# Situations sur 9 points : le critère principal vaut 3 points (index), les autres 2.
_MAIN_CRITERION: dict[int, int] = {1: 1, 4: 0, 8: 0, 9: 1}
# Appareils en DHCP au moment de la demande d'agrandissement (document 19).
DHCP_CLIENTS: dict[int, int] = {1: 64, 2: 81}


def _pts(situation: int) -> tuple[float, ...]:
    if SITUATION_POINTS[situation] == 8:
        return (2, 2, 2, 2)
    return tuple(3 if i == _MAIN_CRITERION[situation] else 2 for i in range(4))


def _join(lines: list[str]) -> str:
    return " ; ".join(line.rstrip(".") for line in lines)


def _lower_first(text: str) -> str:
    return text[:1].lower() + text[1:]


# =============================================================================================
# Documents d'une variante
# =============================================================================================


class Docs:
    """Documents numérotés d'une variante (titres « Variante n, document k — … »)."""

    def __init__(self, v: Variant) -> None:
        self.v = v
        n = v.label
        box = v.box
        srv, nas = v.host("SRV-01"), v.host("NAS-01")
        coax = ", ".join(s.name for s in v.coax_bus.stations)
        self.client = _table(
            f"{n}, document 1 — Fiche du client",
            ("Rubrique", "Contenu"),
            ("Client", f"{v.company}, {v.activity} à {v.city} ; {v.staff} personnes ; responsable : {v.manager}"),
            ("Réseau", f"{v.lan} ; box en {box.ip} (passerelle, NAT, pare-feu, DNS, DHCP de {v.pool[0]} à {v.pool[1]})"),
            ("Serveur SRV-01", f"{srv.ip}, Windows Server 2022, serveur de fichiers, groupe de travail"),
            ("NAS-01", f"{nas.ip}, sauvegardes nocturnes du serveur"),
            ("Wi-Fi", "point d'accès AP-01 à l'accueil, réseau du personnel et des visiteurs"),
            ("Ancien matériel", f"{v.coax_room.capitalize()} : {coax}, sur un segment coaxial 10BASE2 hors switch"),
            ("Intervention", f"Journée de maintenance le {v.date} : quatre dossiers A à D ouverts par le client"),
        )
        lan = lan_figure(v)
        self.schema = _schema(lan.title, lan.alt, figure_file(lan))
        self.inventory = _table(
            f"{n}, document 3 — Inventaire du matériel",
            ("Poste", "Utilisateur", "Système", "Processeur et mémoire", "Stockage", "Année"),
            *((r.name, r.user, r.os, r.hardware, r.storage, str(r.year)) for r in v.inventory),
        )
        b = v.boot
        self.boot_request = _table(
            f"{n}, document 4 — Demande d'intervention sur {b.post}",
            ("Rubrique", "Contenu"),
            ("Symptôme", f"{b.symptom} ; {b.noise}"),
            *((f"Événement {i}", text) for i, text in enumerate(b.history, start=1)),
            ("Données", "Dossiers de travail sur le disque du poste et sur SRV-01" if v.number == 1
             else "Dossiers de travail du poste copiés chaque nuit sur NAS-01 (document 8)"),
        )
        self.boot_screen = _console(f"{n}, document 5 — Écran d'informations du micrologiciel de {b.post} (fictif)",
                                    *boot_screen(v))
        tests = [("Pile CR2032 mesurée au multimètre", f"{fr(b.battery_v)} V (nominal {fr(CMOS_NOMINAL)} V)")]
        if b.disk_in_firmware:
            tests.append(("Fiche d'installation du poste", f"Mode du contrôleur à l'installation : {b.controller_install}"))
            tests.append(("Démarrage sans échec", "inaccessible : l'écran bleu revient avant le menu"))
        else:
            tests.append(("Autre câble SATA, autre port", "toujours « aucun périphérique » dans le micrologiciel"))
            tests.append(("Disque dans un boîtier USB sur le PC de l'atelier",
                          "non reconnu, cliquetis réguliers, aucun volume"))
        self.boot_tests = _table(f"{n}, document 6 — Tests déjà réalisés sur {b.post}", ("Test", "Résultat"), *tests)
        self.storage = _table(
            f"{n}, document 7 — Demandes de stockage de {v.manager}",
            ("Demande", "Détail"),
            ("Nouveau disque", f"{v.new_disk_label}, PC démarrant en UEFI, disque vide, à préparer dans Windows"),
            ("Support amovible", (f"{v.removable_label} ; plus gros fichier : {v.removable_largest[0]} "
                                 f"({fr(v.removable_largest[1])} Gio)")),
            ("Entretien", v.defrag_request),
        )
        self.copies = _table(
            f"{n}, document 8 — Copies existantes des dossiers de travail",
            ("Copie", "Support", "Hors du bâtiment"),
            *((c.label, c.support, "oui" if c.offsite else "non") for c in v.copies),
        )
        self.copy_check = _table(
            f"{n}, document 9 — Contrôle de la dernière copie (empreintes SHA-256 abrégées, fictives)",
            ("Fichier", "Source : taille (octets) / empreinte", "Copie : taille (octets) / empreinte"),
            *((name, f"{size:,} / {fp}".replace(",", " "),
               next((f"{s:,} / {f}".replace(",", " ") for nm, s, f in v.backup_copy if nm == name), "absent"))
              for name, size, fp in v.manifest),
            ("Opération demandée", v.data_operation_text, "—"),
        )
        q = v.quote
        self.quote = _table(
            f"{n}, document 10 — Devis du poste {next(r.name for r in v.inventory if 'devis' in r.user)} (fiches fictives)",
            ("Pièce", "Caractéristiques de la fiche"),
            ("Processeur", f"socket {q.cpu_socket}"),
            ("Carte mère", f"socket {q.board_socket}, format {q.board_form}, mémoire {q.board_memory}, M.2 {q.board_m2}"),
            ("Mémoire", f"2 barrettes {q.ram}"),
            ("SSD", f"M.2 {q.ssd_m2}"),
            ("Carte graphique", (f"{q.gpu_length_mm} mm, {q.gpu_pcie8_needed} × PCIe 8 broches, alimentation "
                                f"recommandée {q.gpu_psu_recommendation_w} W")),
            ("Ventirad", f"{q.cooler_height_mm} mm, sockets {', '.join(q.cooler_sockets)}"),
            ("Boîtier", (f"cartes {' / '.join(q.case_forms)}, carte graphique ≤ {q.case_gpu_max_mm} mm, ventirad ≤ "
                        f"{q.case_cooler_max_mm} mm, bloc {' / '.join(q.case_psu_forms)}")),
            ("Bloc d'alimentation", f"{q.psu_form}, {q.psu_watts} W, {q.psu_pcie8} × PCIe 8 broches"),
        )
        self.power = _table(
            f"{n}, document 11 — Puissances maximales des fiches (fictives)",
            ("Élément", "Puissance maximale (W)"),
            *((load.name, str(load.watts)) for load in v.loads),
            ("Règle de l'atelier", ("total + 30 % de marge, arrondi au palier de 50 W supérieur, jamais sous la "
                                   "recommandation de la carte graphique")),
        )
        if v.win_problem == "vmd":
            win_rows = (
                ("Message de l'installateur", ("« Nous n'avons trouvé aucun lecteur. Pour obtenir un pilote de stockage, "
                                              "sélectionnez Charger un pilote. »")),
                ("Micrologiciel", "SSD NVMe 2 To listé ; contrôleur Intel VMD activé"),
                ("Remarque du vendeur", "« Le SSD est peut-être défectueux, renvoyez-le. »"),
                ("Licence achetée", "Windows 11 Pro, licence commerciale (clé sur carte)"),
                ("Après la première installation", "Paramètres > Activation : édition Windows 11 Famille, non activé"),
            )
        else:
            win_rows = (
                ("Demande", "passer PC-COMPTA à Windows 11 en démarrage UEFI, sans perdre D: (comptabilité, 180 Go)"),
                ("Message de l'installateur", ("« Impossible d'installer Windows sur ce disque. Le disque sélectionné "
                                              "n'est pas de style de partition GPT. »")),
                ("Gestion des disques", "disque 0 en MBR : Réservé au système, C: Windows 10, D: Comptabilité"),
                ("Conseil d'un collègue", "« Repasse le micrologiciel en mode hérité, ça s'installera. »"),
                ("Licence", "licence numérique Windows Pro liée à ce PC"),
            )
        self.windows = _table(f"{n}, document 12 — Installation de Windows 11 sur {v.win_post}", ("Élément", "Constat"),
                              *win_rows)
        status_backup = "vérifiée (copie relue, fichiers ouverts)" if v.backup_verified else "faite hier, pas encore relue"
        status_consent = ("accord écrit et signé de la gérante" if v.written_consent
                          else "accord donné oralement au téléphone par le gérant")
        self.linux = _table(
            f"{n}, document 13 — Préparation du double démarrage sur {v.linux_post}",
            ("Élément", "Constat"),
            ("Disque (GPT)", ("ESP FAT32 100 Mo ; MSR 16 Mo ; Windows C: NTFS ; Récupération NTFS ; espace libre de "
                             "200 Go préparé en réduisant C: depuis Windows")),
            ("Mémoire", f"{v.linux_ram_gb} Go ; hibernation non souhaitée"),
            ("Sauvegarde des données de Windows", status_backup),
            ("Accord du client", status_consent),
            ("Distribution", "Ubuntu 24.04 LTS, image téléchargée sur le site officiel"),
        )
        self.iso = _console(f"{n}, document 14 — Vérification de l'image téléchargée (relevé fictif)",
                            "$ sha256sum -c SHA256SUMS 2>/dev/null \\", f"    | grep {v.iso_line.split(':')[0]}",
                            v.iso_line)
        note = ("Ubuntu vient d'être installé, mais le portable démarre directement sur Windows."
                if "ubuntu" in " ".join(v.efibootmgr)
                else "Un stagiaire a tenté une installation la semaine passée avec la même image.")
        self.efi = _console(f"{n}, document 15 — Entrées de démarrage UEFI de {v.linux_post} (relevé fictif)",
                            *v.efibootmgr, "", note)
        self.tester = _console(f"{n}, document 16 — Test du cordon de {v.cord_post} (testeur de continuité fictif)",
                               *tester_lines(v.cord_links))
        cord_rows = [
            ("Plainte", "« Les fichiers du serveur sont lents à ouvrir » ; carte réseau : "
                        + (f"« {SPEED_100}, duplex intégral »" if v.cord_speed == SPEED_100
                           else "« 1 Gb/s », mais coupures fréquentes")),
            ("Lien prise → panneau", f"{v.cord_run_m} m, Cat6, certifié conforme à la pose"),
            ("Carte réseau", "vitesse en « négociation automatique », pilote à jour"),
            ("Port du switch", "les postes voisins sont à 1 Gb/s sur des ports du même switch"),
        ]
        if v.cord_ends:
            cord_rows.append(("Ordre des fils lu aux deux fiches", ", ".join(v.cord_ends[0])))
            cord_rows.append(("Certificateur du bureau d'études voisin", "diaphonie (NEXT) en échec sur 3-6 et 4-5"
                              if v.cord_next_fail else "conforme"))
            cord_rows.append(("Compteurs du port du switch", "nombreuses erreurs CRC"))
        else:
            cord_rows.append(("Marquage du câble du cordon", "Cat5e U/UTP"))
        self.cord = _table(f"{n}, document 17 — Constats sur le poste {v.cord_post}", ("Élément", "Constat"), *cord_rows)
        bus = v.coax_bus
        coax_rows = []
        for item in bus.items:
            if hasattr(item, "length_m"):
                coax_rows.append(("Tronçon", f"{fr(item.length_m)} m de RG-58 (relevé sur l'étiquette du rouleau)"))
            elif item.attachment == ATTACH_STUB:
                coax_rows.append(("Station", (f"{item.name} : T posé au bout d'un câble coaxial de 2 m, qui rejoint la "
                                             "carte réseau")))
            else:
                coax_rows.append(("Station", f"{item.name} : T BNC fixé directement sur la carte réseau"))
        first, last = bus.stations[0].name, bus.stations[-1].name
        coax_rows.append((f"Extrémité {first}", "terminateur 50 Ω, avec chaînette de mise à la terre"))
        coax_rows.append((f"Extrémité {last}", "terminateur 50 Ω"))
        for name, value in v.coax_readings:
            coax_rows.append(("Ohmmètre âme/blindage", (f"au T de {name}, machines arrêtées : "
                                                       f"{'infini' if value is None else fr(value) + ' Ω'}")))
        coax_rows.append(("Terminateurs dévissés et mesurés seuls", "50 Ω chacun"))
        for span in bus.spans:
            coax_rows.append((f"Tronçon de {fr(span.length_m)} m débranché, âme mesurée de bout en bout",
                              "infini" if span.fault == FAULT_OPEN else "continu (moins de 1 Ω)"))
        coax_rows.append(("Symptôme", "toutes les stations du segment ont perdu le réseau" if v.number == 2
                          else "coupures aléatoires depuis l'ajout de " + next(
                              s.name for s in bus.stations if s.attachment == ATTACH_STUB)))
        self.coax = _table(f"{n}, document 18 — Segment coaxial de la {v.coax_room}", ("Élément", "Constat"), *coax_rows)
        dhcp_clients = DHCP_CLIENTS[v.number]
        self.addressing = _table(
            f"{n}, document 19 — Demande d'agrandissement du réseau",
            ("Élément", "Détail"),
            ("Réseau actuel", f"{v.lan}, box {box.ip}, étendue DHCP {v.pool[0]} à {v.pool[1]}"),
            ("Appareils en DHCP aujourd'hui", f"{dhcp_clients} (postes, portables, téléphones, visiteurs)"),
            ("Besoin dans deux ans", f"{v.needed_addresses} adresses d'hôtes, dans un seul réseau"),
            ("Contrainte", f"garder la box en {box.ip} et le début de l'adressage actuel"),
            ("Nouvelle étendue DHCP prévue", f"{v.new_pool[0]} à {v.new_pool[1]}"),
            ("État", "la box a déjà été passée au nouveau masque ; trois appareils relevés au document 20"),
        )
        lines: list[str] = []
        for host in v.new_hosts:
            lines += [*ipconfig_lines(host), ""]
        self.ipconfig = _console(f"{n}, document 20 — Relevés de trois appareils après le changement (fictifs)",
                                 *lines[:-1])
        wifi = wifi_figure(v)
        self.wifi_plan = _schema(wifi.title, wifi.alt, figure_file(wifi))
        cfg = v.ap_config
        ext = v.extension
        self.wifi = _table(
            f"{n}, document 22 — Wi-Fi : voisins, configuration actuelle et extension",
            ("Élément", "Relevé"),
            *((f"Voisin {nb.ssid}", f"canal {nb.channel}, {nb.dbm} dBm") for nb in v.neighbors),
            ("AP-01 : sécurité et clé", f"{cfg.security}, clé « {cfg.passphrase} »"),
            ("AP-01 : réglages", (f"SSID « {cfg.ssid} »{' masqué' if cfg.ssid_hidden else ''}, canal {cfg.channel_24}, "
                                 f"{cfg.width_24} MHz, WPS {'activé' if cfg.wps else 'désactivé'}, mot de passe "
                                 f"d'administration {'d’usine' if cfg.admin_default else 'personnalisé'}")),
            ("Réseau des visiteurs", "aucun" if cfg.guest_isolated is None
             else ("isolé du réseau interne" if cfg.guest_isolated else "même réseau que les postes")),
            ("Répéteur existant", "un répéteur grand public distribue aussi des adresses (son DHCP est actif)"
             if cfg.dhcp_sources > 1 else "aucun"),
            ("Extension étudiée", (f"{ext.zone} : répéteur à {fr(ext.uplink_m)} m de AP-01 (à travers "
                                  f"{', '.join(ext.uplink_obstacles)}) et {fr(ext.client_m)} m des postes (à travers "
                                  f"{', '.join(ext.client_obstacles)}) ; ou point d'accès câblé, "
                                  f"{ext.cable_m} m de câble jusqu'au switch, même distance des postes")),
            ("Règles du cours", f"objectif {TARGET_DBM} dBm ; pertes d'obstacles et débits du cours PR25"),
        )
        self.accounts = _table(
            f"{n}, document 23 — Comptes et groupes locaux de SRV-01",
            ("Compte", "Personne", "Groupes"),
            *((a.login, a.person, ", ".join(a.groups)) for a in v.accounts),
        )
        share_rows = []
        for share in v.shares.values():
            share_rows.append((f"Partage « {share.name} »", share.path,
                               ", ".join(f"{e.principal} : {e.right}" for e in share.entries)))
            for folder in v.share_tree.values():
                if folder.path == share.path or folder.path.startswith(share.path + "\\"):
                    entries = ", ".join(f"{e.principal} : {'Refuser ' if e.deny else ''}{e.right}"
                                        for e in folder.entries)
                    inherit = "héritage activé" if folder.inherit else "héritage désactivé"
                    share_rows.append(("NTFS", folder.path, f"{entries} ({inherit})"))
        login, path, _wanted = v.need
        person = v.account(login).person.split(" (")[0]
        share_rows.append(("Plainte", person, f"ne peut pas enregistrer dans {path}"
                           + (" depuis son poste ; en session sur le serveur, il le peut" if v.number == 2 else "")))
        self.shares = _table(f"{n}, document 24 — Partage et autorisations NTFS de SRV-01",
                             ("Couche", "Objet", "Autorisations"), *share_rows)
        self.journal = _table(
            f"{n}, document 25 — Journal de ta journée du {v.date}",
            ("Début", "Fin", "Action"),
            *v.journal,
        )


# =============================================================================================
# Les 12 situations
# =============================================================================================


def _item(v: Variant, situation: int, title: str, reqs: tuple[str, ...], context: str,
          documents: tuple[ExerciseDocument, ...], instructions: tuple[str, ...],
          criteria: tuple[tuple[str, str], ...], correction: tuple[str, ...]) -> PR06Item:
    points = _pts(situation)
    return PR06Item(
        key=item_key(v, situation),
        usage=USAGE_EXAM,
        title=title,
        question_type="document_analysis",
        requirement_ids=reqs,
        kind=KIND_DOC,
        context=context,
        documents=documents,
        instructions=instructions,
        criteria=tuple(_c(label, p, expected) for (label, expected), p in zip(criteria, points, strict=True)),
        correction=correction,
    )


def _s1(v: Variant, d: Docs) -> PR06Item:
    b = v.boot
    battery = (f"la pile est à {fr(b.battery_v)} V, nettement sous les {fr(CMOS_NOMINAL)} V nominaux : elle est usée "
               "et explique la date perdue, mais une pile usée n'empêche pas de voir un disque ; elle se remplace en "
               "plus (même référence CR2032), réglages notés avant" if b.battery_worn else
               f"la pile est à {fr(b.battery_v)} V, normale : hors de cause")
    if b.cause == CAUSE_CONTROLLER:
        causes = ("Causes possibles : la mise à jour de vendredi, le disque (ou son câble), le réglage changé "
                  "samedi dans le micrologiciel.")
        tests = ("Le disque est listé dans le micrologiciel avec SMART « Bon » : disque, câble et port fonctionnent. "
                 f"Le mode du contrôleur est « {b.controller_now} » alors que Windows a été installé en "
                 f"« {b.controller_install} » (fiche) : le noyau démarre, mais n'a pas chargé le pilote de ce mode et "
                 "perd l'accès au disque système, d'où INACCESSIBLE_BOOT_DEVICE. La mise à jour reste possible, mais "
                 "elle ne se teste qu'après avoir annulé le seul changement connu.")
        fix = (f"Remettre le contrôleur en {b.controller_install} dans le micrologiciel (seul changement de samedi, "
               "réversible, sans toucher aux données), enregistrer, redémarrer : Windows démarre. Seulement si "
               "l'écran bleu persistait : environnement de récupération (WinRE) → désinstaller la dernière mise à "
               "jour. Ne pas réinstaller ni lancer de réparation qui écrit sur le disque avant d'avoir copié les "
               "dossiers de travail.")
        verify = ("Windows démarre et s'ouvre ; Gestionnaire de périphériques sans erreur sur le contrôleur ; "
                  "fichiers de travail ouverts ; noter l'incident et conseiller de protéger le micrologiciel par un "
                  "mot de passe administrateur.")
    else:
        causes = ("Causes possibles : le déplacement du PC (câble SATA débranché), la pile qui perd la date, le "
                  "disque lui-même.")
        tests = ("Le micrologiciel ne voit aucun disque, même avec un autre câble et un autre port : ni le câble ni "
                 "le port ne sont en cause. Dans un boîtier USB sur un autre PC, le disque n'est pas reconnu et "
                 "cliquette : panne mécanique, le disque est mort. " + battery[0].upper() + battery[1:] + ".")
        fix = ("Ne pas insister (chaque mise sous tension aggrave une panne mécanique) ; prévenir le client que les "
               "dossiers non sauvegardés ne sont récupérables que par un laboratoire spécialisé (devis, accord) ; "
               "poser un disque neuf, remplacer la pile CR2032, régler date et heure, restaurer depuis les copies.")
        verify = ("Le micrologiciel voit le nouveau disque ; date et heure conservées après une coupure du courant ; "
                  "Windows installé et données restaurées vérifiées avec l'utilisateur.")
    return _item(
        v, 1, "Poste qui ne démarre plus : départager plusieurs causes",
        ("AP-15", "AP-16"),
        _ctx(v, "A", f"{b.post} ne démarre plus (document 4). Tu as relevé l'écran d'informations du micrologiciel "
                     "(document 5) et réalisé quelques tests (document 6). L'inventaire est au document 3."),
        (d.inventory, d.boot_request, d.boot_screen, d.boot_tests),
        (
            "Liste les causes possibles que suggère le document 4, y compris les indices qui ne sont pas décisifs.",
            "Montre, avec les valeurs des documents 5 et 6, quels tests éliminent ou confirment chaque cause.",
            "Donne la cause retenue et l'intervention, dans l'ordre, sans mettre les données en danger.",
            "Indique les contrôles qui prouvent la réparation et ce que tu notes pour le client.",
        ),
        (
            ("Hypothèses", causes + " Chacune est nommée avec l'indice qui la suggère ; un indice n'est pas une preuve."),
            ("Tests discriminants", tests),
            ("Cause et intervention", f"Cause : {b.cause}. {fix}"),
            ("Vérifications", verify),
        ),
        (causes, tests, f"Cause retenue : {b.cause}. {fix}", f"Contrôles : {verify}"),
    )


def _s2(v: Variant, d: Docs) -> PR06Item:
    table = v.new_disk_table
    if v.new_disk_boots:
        why_table = (f"disque système d'un PC qui démarre en UEFI : {table} obligatoire (Windows 64 bits ne démarre "
                     "d'un disque GPT qu'en UEFI, et inversement)")
        partitions = "l'installateur crée lui-même ESP, MSR, C: et Récupération sur l'espace non alloué"
    else:
        why_table = (f"disque de données de {fr(v.new_disk_tb)} To : au-delà de 2 Tio, une table MBR ne gère pas "
                     f"tout (≈ {fr(v.new_disk_mbr_lost_tib)} Tio perdus) ; {table} pour un PC récent")
        partitions = "une seule partition sur tout le disque, lettre E:, nom de volume « Archives »"
    shown = (f"{fr(v.new_disk_tb)} To annoncés = {fr(v.new_disk_tb)} × 10¹² octets ; Windows divise par 2⁴⁰ et "
             f"affiche ≈ {fr(v.new_disk_shown_tib)} « To » : rien ne manque, ce sont deux unités différentes")
    removable = {
        FS_EXFAT: (f"exFAT : lu et écrit par Windows et macOS, sans limite de 4 Gio ; FAT32 refuserait "
                   f"{v.removable_largest[0]} ({fr(v.removable_largest[1])} Gio), NTFS n'est qu'en lecture sur Mac"),
        FS_FAT32: (f"FAT32 : seul système lu par l'appareil ; possible car le plus gros fichier "
                   f"({fr(v.removable_largest[1])} Gio) reste sous 4 Gio"),
    }[v.removable_fs]
    defrag = ("Défragmenter un SSD est inutile et l'use : Windows l'« optimise » par TRIM (Optimiser les lecteurs, "
              "planification hebdomadaire laissée par défaut) ; seul un disque dur (HDD) se défragmente, et Windows "
              "le fait déjà chaque semaine")
    return _item(
        v, 2, "Stockage : préparer les supports et répondre aux demandes d'entretien",
        ("AP-03",),
        _ctx(v, "A", f"{v.manager} a trois demandes de stockage (document 7). L'inventaire est au document 3."),
        (d.inventory, d.storage),
        (
            "Choisis la table de partitions du nouveau disque et justifie-la par un calcul ou une règle.",
            ("Décris la préparation dans Windows (outil, partitions, système de fichiers, formatage) et explique la "
            "capacité que Windows affichera, calcul à l'appui."),
            "Choisis le système de fichiers du support amovible et justifie-le avec le plus gros fichier.",
            "Réponds à la demande d'entretien (défragmentation) en distinguant les types de disques.",
        ),
        (
            ("Table de partitions", f"{table} : {why_table}."),
            ("Préparation et capacité", (f"Gestion des disques (diskmgmt.msc) ou installateur : initialiser en {table}, "
             f"{partitions} ; {v.new_disk_fs}, formatage rapide sur un disque neuf. {shown}.")),
            ("Support amovible", removable + " ; formatage seulement après avoir vidé le support de toute donnée à garder."),
            ("Défragmentation", defrag + "."),
        ),
        (
            f"Table : {table}, car {why_table}.",
            (f"Préparation : Gestion des disques, initialisation en {table}, {partitions}, système de fichiers "
            f"{v.new_disk_fs}. Capacité : {shown}."),
            f"Support amovible : {removable}.",
            f"Entretien : {defrag}.",
        ),
    )


def _s3(v: Variant, d: Docs) -> PR06Item:
    missing = v.missing_321
    lost, different = v.copy_check
    copies = len(v.copies)
    rule = ("Règle 3-2-1 : au moins 3 copies (l'original compris), sur 2 types de supports, dont 1 hors site. "
            f"Ici {copies} copies" + (" (l'original est sur un disque mort : il ne compte plus)" if v.number == 2 else "")
            + " ; manque : " + " ; ".join(missing) + ".")
    fix_321 = ("ajouter une copie d'un autre type hors du bâtiment (stockage en ligne chiffré ou disque externe "
               "emporté), garder NAS-01, tester une restauration chaque mois")
    if different:
        check = (f"{', '.join(different)} : même taille mais empreinte différente → copie altérée ; la recopier depuis "
                 "la source puis recalculer l'empreinte ; les autres fichiers sont identiques")
    else:
        check = (f"{', '.join(lost)} : absent de la copie → la copie est incomplète ; le récupérer ailleurs (poste de "
                 "l'auteur, courriels, client) et recopier, puis relancer le contrôle ; les autres fichiers sont "
                 "identiques")
    prereq = " ; ".join(v.data_prerequisites)
    operation = v.data_operation_text
    if v.number == 1:
        method = ("effacement sécurisé de tout le disque (outil d'effacement par écrasement ou commande d'effacement "
                  "sécurisé du fabricant), puis contrôle qu'aucun volume n'est lisible, attestation pour le client ; "
                  "un simple formatage ou une suppression ne suffit pas")
    else:
        method = ("vider puis reformater le disque externe en NTFS (usage Windows seul, fichiers de plus de 4 Gio "
                  "possibles), puis relancer et contrôler une sauvegarde complète")
    return _item(
        v, 3, "Protéger les données : copies, contrôle d'intégrité et opération qui efface",
        ("AP-C03", "AP-15"),
        _ctx(v, "A", "les dossiers de travail sont copiés selon le document 8 ; tu as contrôlé la dernière copie au "
                     "document 9, où figure aussi une opération demandée par le client."),
        (d.copies, d.copy_check),
        (
            "Évalue la protection actuelle avec la règle 3-2-1 et propose les ajouts nécessaires.",
            "Interprète le contrôle du document 9 fichier par fichier et dis ce que tu fais.",
            "Liste les conditions à réunir avant l'opération demandée au document 9.",
            "Décris l'opération elle-même et la trace que tu laisses.",
        ),
        (
            ("Règle 3-2-1", f"{rule} Proposition : {fix_321}."),
            ("Contrôle de la copie", check + "."),
            ("Conditions préalables", prereq + " ; rien n'est effacé avant."),
            ("Opération et trace", method + " ; noter l'opération, la date, le support et l'accord sur la fiche."),
        ),
        (
            f"{rule} Je propose de {fix_321}.",
            f"Contrôle : {check}.",
            f"Avant de {operation} : {prereq}.",
            f"Opération : {method}. Je note l'opération, la date, le support et l'accord sur la fiche d'intervention.",
        ),
    )


def _s4(v: Variant, d: Docs) -> PR06Item:
    checks = v.quote_checks
    bad = [f"{label} ({why})" for label, ok, why in checks if not ok]
    good = [label for label, ok, _w in checks if ok]
    total = v.budget_w
    margin = total * 1.3
    fixes = {
        "Processeur ↔ socket": f"carte mère socket {v.quote.cpu_socket} (ou processeur au socket de la carte)",
        "Mémoire ↔ carte": f"barrettes {v.quote.board_memory}",
        "Carte mère ↔ boîtier": f"boîtier qui accepte le format {v.quote.board_form} (ou carte microATX)",
        "SSD M.2 ↔ emplacement": "SSD du type accepté par l'emplacement",
        "Carte graphique ↔ boîtier": f"boîtier acceptant {v.quote.gpu_length_mm} mm (ou carte plus courte)",
        "Ventirad ↔ boîtier et socket": f"ventirad de {v.quote.case_cooler_max_mm} mm au plus",
        "Bloc : puissance": f"bloc d'au moins {v.psu_w} W",
        "Bloc : connecteurs PCIe": f"bloc avec {v.quote.gpu_pcie8_needed} connecteurs PCIe 8 broches",
        "Bloc ↔ boîtier": "bloc au format du boîtier",
    }
    fix_text = " ; ".join(fixes[label] for label, ok, _w in checks if not ok)
    psu_ok = v.quote.psu_watts >= v.psu_w
    return _item(
        v, 4, "Devis d'un nouveau poste : compatibilité et budget de puissance",
        ("AP-17",),
        _ctx(v, "B", "un fournisseur propose le devis du document 10 pour un poste exigeant ; les puissances des "
                     "fiches et la règle de l'atelier sont au document 11."),
        (d.quote, d.power),
        (
            "Contrôle chaque association de pièces du document 10 et liste les incompatibilités avec les valeurs.",
            "Calcule le budget de puissance et la puissance de bloc conseillée selon la règle du document 11.",
            "Propose les corrections du devis, pièce par pièce.",
            "Indique les contrôles à faire au premier démarrage du poste monté.",
        ),
        (
            ("Incompatibilités", "Incompatibles : " + " ; ".join(bad) + ". Conformes : " + ", ".join(good) + "."),
            ("Budget", f"Total des fiches = {total} W ; × 1,3 = {fr(round(margin, 1))} W → palier {recommended_psu(total)} W ; "
             f"recommandation de la carte graphique {v.quote.gpu_psu_recommendation_w} W → bloc conseillé {v.psu_w} W ; "
             f"le bloc du devis ({v.quote.psu_watts} W) " + ("suffit en puissance." if psu_ok else "est trop faible.")),
            ("Corrections", fix_text + " ; chaque pièce corrigée reste compatible avec les autres."),
            ("Premier démarrage", ("Micrologiciel : processeur, mémoire totale et SSD détectés, températures au repos "
             "normales ; test de charge (processeur et carte graphique) sans arrêt ni surchauffe ; tensions dans les "
             "tolérances ; ventilateurs qui tournent.")),
        ),
        (
            "Incompatibilités : " + " ; ".join(bad) + ". Les autres associations sont conformes (" + ", ".join(good) + ").",
            (f"Budget : {' + '.join(str(load.watts) for load in v.loads)} = {total} W ; avec 30 % de marge, "
            f"{fr(round(margin, 1))} W, arrondi au palier de 50 W supérieur ; jamais sous les "
            f"{v.quote.gpu_psu_recommendation_w} W recommandés par la carte graphique : bloc de {v.psu_w} W."),
            f"Corrections : {fix_text}.",
            ("Au premier démarrage : composants détectés dans le micrologiciel, températures, test de charge, "
            "tensions et ventilateurs contrôlés."),
        ),
    )


def _s5(v: Variant, d: Docs) -> PR06Item:
    result, reason = v.activation
    activates = result == ACTIVATES
    if v.win_problem == "vmd":
        reading = ("Le SSD est listé dans le micrologiciel : il fonctionne ; l'installateur ne le voit pas parce que "
                   "le contrôleur Intel VMD demande un pilote absent de la clé. L'avis du vendeur est un faux indice.")
        fix = ("Sur un autre PC, télécharger chez le fabricant de la carte mère le pilote Intel RST/VMD « F6 » "
               "(à extraire), le copier sur la clé ; dans l'installateur, « Charger un pilote » → dossier → "
               "contrôleur : le SSD apparaît ; installation personnalisée sur l'espace non alloué. On ne désactive "
               "pas VMD après l'installation.")
    else:
        reading = ("Le disque est en MBR et le PC démarre en UEFI : Windows 11 ne s'installe en UEFI que sur un disque "
                   "GPT. Repasser en mode hérité contournerait le message mais priverait Windows 11 de l'UEFI et du "
                   "démarrage sécurisé : conseil à refuser.")
        fix = ("Sauvegarde vérifiée de D: sur un autre support et accord écrit ; depuis Windows 10 : "
               "mbr2gpt /validate /allowFullOS puis mbr2gpt /convert /allowFullOS ; micrologiciel en UEFI ; "
               "installation de Windows 11 en supprimant seulement les partitions de l'ancien système, D: intacte.")
    activation = (f"Activation : {_lower_first(result)} — {reason}"
                  + ("" if activates else " : la licence est Pro ; réinstaller (ou mettre à niveau) en édition Pro, "
                     "puis entrer la clé commerciale ; ne jamais utiliser d'activateur ou de clé trouvée en ligne"))
    return _item(
        v, 5, "Installation de Windows 11 : lire le blocage et réussir l'activation",
        ("AP-10", "AP-15"),
        _ctx(v, "B", f"l'installation de Windows 11 sur {v.win_post} se passe comme décrit au document 12. "
                     "L'inventaire est au document 3."),
        (d.inventory, d.windows),
        (
            "Explique le blocage décrit au document 12 et dis si le conseil ou la remarque qui y figure est juste.",
            "Rédige la procédure qui débloque l'installation, sans perte de données.",
            "Dis si Windows sera activé et justifie-le ; corrige si nécessaire.",
            "Donne les vérifications de fin d'installation.",
        ),
        (
            ("Lecture du blocage", reading),
            ("Procédure", fix),
            ("Activation", activation + "."),
            ("Vérifications", ("msinfo32 : mode BIOS UEFI, démarrage sécurisé activé ; Gestion des disques : GPT ; "
             "Gestionnaire de périphériques sans erreur ; Windows Update ; Paramètres > Activation : activé ; données "
             "présentes et ouvertes avec l'utilisateur.")),
        ),
        (reading, f"Procédure : {fix}", activation + ".",
         "Contrôles : msinfo32 (UEFI, démarrage sécurisé), disque GPT, pilotes, mises à jour, activation, données."),
    )


def _s6(v: Variant, d: Docs) -> PR06Item:
    plan = v.dual_boot_plan
    stop = all(action == DB_STOP for _z, action in plan)
    plan_text = " ; ".join(f"{zone} : {_lower_first(action)}" for zone, action in plan)
    iso_ok = v.iso_verdict == ISO_OK
    first = v.first_boot
    if stop:
        conditions = ("Ici, ni la sauvegarde vérifiée ni l'accord écrit : on s'arrête avant tout partitionnement. Il "
                      "faut relire la copie de Windows et obtenir un accord écrit, daté, signé par le gérant.")
        after = ("ESP réutilisée sans formatage (/boot/efi) ; MSR, Windows et Récupération intacts ; Linux créé "
                 "dans l'espace libre")
    else:
        conditions = "Sauvegarde vérifiée et accord écrit réunis : le partitionnement manuel peut commencer."
        after = plan_text
    layout = (f"dans l'espace libre : / en ext4 (≈ 50 Go), swap de {fr(v.swap_gb)} Go ({v.linux_ram_gb} Go de "
              "mémoire, sans hibernation), /home en ext4 pour le reste")
    if "ubuntu" in " ".join(v.efibootmgr):
        boot = (f"BootOrder commence par 0000 : l'entrée démarrée en premier est « {first} », d'où Windows direct ; "
                "l'entrée ubuntu existe, l'installation a réussi : sudo efibootmgr -o 0001,0000,0002 (ou l'ordre de "
                "démarrage du micrologiciel), puis le menu GRUB propose Ubuntu et Windows")
    else:
        boot = (f"Aucune entrée ubuntu : la tentative précédente n'a pas abouti ; l'entrée « {first} » démarre "
                "toujours en premier, Windows est intact. Après la nouvelle installation, vérifier qu'une entrée "
                "ubuntu apparaît et passe en tête (efibootmgr -o)")
    image = ("sha256sum -c affiche OK : image intègre, la clé peut être écrite" if iso_ok else
             "sha256sum -c affiche FAILED : image corrompue (elle explique l'échec précédent) ; la supprimer, la "
             "retélécharger sur le site officiel et revérifier avant d'écrire la clé")
    return _item(
        v, 6, "Double démarrage Windows et Linux : conditions, partitions et démarrage",
        ("AP-10", "AP-C03"),
        _ctx(v, "B", f"{v.linux_post} doit garder Windows et recevoir Ubuntu (document 13) ; la vérification de "
                     "l'image est au document 14 et les entrées de démarrage au document 15."),
        (d.linux, d.iso, d.efi),
        (
            "Dis si l'installation peut commencer avec ce que montre le document 13 ; sinon, ce qui manque.",
            ("Donne, zone par zone du disque, ce que tu fais dans le partitionnement manuel, avec tailles et systèmes "
            "de fichiers."),
            "Interprète le document 14 et dis ce que tu fais de l'image.",
            "Lis le document 15 : quelle entrée démarre en premier, et que fais-tu ?",
        ),
        (
            ("Conditions", conditions),
            ("Partitionnement", f"{after} ; {layout}."),
            ("Image", image + "."),
            ("Démarrage", boot + "."),
        ),
        (conditions, f"Partitionnement : {after} ; {layout}.", f"Image : {image}.", f"Démarrage : {boot}."),
    )


def _s7(v: Variant, d: Docs) -> PR06Item:
    if v.cord_ends:
        pairs = ", ".join(f"{a}-{b}" for a, b in v.cord_split)
        reading = ("Le testeur de continuité montre 1→1 … 8→8 : il ne voit pas le défaut. Les fiches sont serties "
                   "dans l'ordre des couleurs côte à côte (blanc-orange, orange, blanc-vert, vert…) au lieu de "
                   "T568B : les broches " + pairs + " ne sont plus chacune sur une paire torsadée (paires séparées). "
                   "Le certificateur le confirme (diaphonie NEXT en échec) ; les erreurs CRC et les coupures en "
                   "découlent.")
        false_clue = (f"Faux indices : le lien {v.cord_run_m} m certifié est hors de cause, la carte et le port "
                      "aussi (voisins à 1 Gb/s, négociation automatique)")
    else:
        fault = ", ".join(v.cord_faults)
        reading = (f"Le testeur montre : {fault}. Le 100BASE-TX n'utilise que les paires 1-2 et 3-6, le 1000BASE-T "
                   "les quatre : avec une paire 7-8 coupée, les cartes se rabattent sur 100 Mb/s, d'où les fichiers "
                   "lents sans coupure.")
        false_clue = (f"Faux indices : le marquage Cat5e suffit au gigabit ; le lien de {v.cord_run_m} m est certifié, "
                      "la carte négocie automatiquement, le port du switch fonctionne pour les voisins")
    procedure = ("Refaire le cordon en T568B aux deux bouts (droit) : couper la fiche, dénuder environ 3 cm, "
                 "détorsader au minimum, ordonner blanc-orange, orange, blanc-vert, bleu, blanc-bleu, vert, "
                 "blanc-marron, marron, couper net à 12-13 mm, insérer jusqu'au fond (couleurs visibles à travers "
                 "la fiche), gaine sous le serre-câble, sertir ; idem à l'autre bout")
    test = ("Testeur : 1→1 à 8→8 sans ouvert ni croisement ; idéalement certificateur (NEXT) ; carte réseau à "
            "« 1 Gb/s, duplex intégral », compteurs d'erreurs du port stables, copie d'un gros fichier du serveur "
            "rapide")
    return _item(
        v, 7, "Cordon RJ45 : lien dégradé, causes à départager",
        ("AP-34", "AP-15"),
        _ctx(v, "C", f"le poste {v.cord_post} est relié au switch par un cordon fabriqué sur place ; le test du cordon "
                     "est au document 16 et les autres constats au document 17."),
        (d.tester, d.cord),
        (
            "Interprète les documents 16 et 17 : nomme le défaut et explique son effet sur le lien.",
            "Dis pourquoi les autres indices du document 17 ne sont pas la cause.",
            "Rédige la fabrication du cordon de remplacement (norme, ordre des fils, gestes).",
            "Donne les tests qui prouvent la réparation.",
        ),
        (
            ("Défaut et effet", reading),
            ("Indices écartés", false_clue + "."),
            ("Fabrication", procedure + "."),
            ("Tests", test + "."),
        ),
        (reading, false_clue + ".", f"Fabrication : {procedure}.", f"Tests : {test}."),
    )


def _s8(v: Variant, d: Docs) -> PR06Item:
    errors = v.coax_errors
    readings = ", ".join(f"{name} : {fr(value)} Ω" if value is not None else f"{name} : infini"
                         for name, value in v.coax_readings)
    bus = v.coax_bus
    if v.number == 1:
        reading = (f"Mesures : {readings}. Deux terminateurs de 50 Ω en parallèle donnent 25 Ω : les terminateurs et "
                   "la continuité de bout en bout sont bons, ils ne sont pas la cause.")
        cause = ("Non-conformités : " + _join(errors) + f" (longueur totale {fr(bus.length_m)} m, maximum "
                 f"{THIN_SEGMENT_MAX_M} m). La dérivation ajoutée crée des réflexions et l'allongement dépasse la "
                 "longueur du segment : d'où les coupures depuis l'ajout.")
        fix = ("Fixer le T directement sur la carte de la station (supprimer le câble de 2 m) ; ramener le segment "
               f"sous {THIN_SEGMENT_MAX_M} m (raccourcir un tronçon ou passer une station sur le switch avec une "
               "carte RJ45) ; câble RG-58 50 Ω neuf avec fiches BNC à sertir")
    else:
        cut = next(s for s in bus.spans if s.fault)
        idx = bus.items.index(cut)
        left, right = bus.items[idx - 1].name, bus.items[idx + 1].name
        reading = (f"Mesures : {readings}. Partout 50 Ω au lieu de 25 Ω : chaque T ne « voit » plus qu'un seul "
                   "terminateur. Les terminateurs mesurés seuls font 50 Ω : ils sont bons. Il y a donc une coupure "
                   "dans le câble.")
        cause = (f"Les mesures aux T ne situent pas la coupure ; les tronçons mesurés seuls, si : celui de "
                 f"{fr(cut.length_m)} m entre {left} et {right} est ouvert (infini), les autres sont continus. Une "
                 "coupure laisse chaque moitié sans terminaison à un bout : tout le segment s'arrête.")
        fix = (f"Remplacer le tronçon de {fr(cut.length_m)} m {left} — {right} par un RG-58 50 Ω neuf muni de fiches "
               "BNC mâles à sertir, en vérifiant d'abord sa continuité seul à l'ohmmètre")
    make = ("Fabrication : dénuder aux cotes de la fiche (gaine, tresse, isolant, âme), glisser la bague, sertir la "
            "broche centrale sur l'âme, enfoncer le corps sous la tresse, sertir la bague à la pince de la bonne "
            "taille ; contrôler : pas de court-circuit âme/tresse, continuité de l'âme et de la tresse, traction")
    verify = ("Machines arrêtées : 25 Ω entre âme et blindage à n'importe quel T ; une seule mise à la terre ; puis "
              "ping entre les stations du segment et accès aux fichiers")
    return _item(
        v, 8, "Segment coaxial et câble BNC : localiser et corriger",
        ("AP-35",),
        _ctx(v, "C", f"le segment coaxial de la {v.coax_room} pose problème ; ses éléments, les mesures à l'ohmmètre et "
                     "le symptôme sont au document 18."),
        (d.coax,),
        (
            "Interprète les mesures du document 18 (valeur attendue, valeurs relevées) et ce qu'elles éliminent.",
            "Donne la ou les causes, avec leur emplacement et la règle du 10BASE2 concernée.",
            "Décris la correction et la fabrication d'un câble coaxial muni de fiches BNC.",
            "Indique les mesures et essais de contrôle.",
        ),
        (
            ("Lecture des mesures", reading),
            ("Causes", cause),
            ("Correction et fabrication", f"{fix}. {make}."),
            ("Contrôles", verify + "."),
        ),
        (reading, cause, f"Correction : {fix}. {make}.", f"Contrôles : {verify}."),
    )


def _s9(v: Variant, d: Docs) -> PR06Item:
    old, new = v.lan_facts, v.new_facts
    prefix = v.new_prefix
    hosts_bigger = 2 ** (32 - (prefix + 1)) - 2
    errors = v.new_plan_errors
    host_text = _join(errors)
    clients = DHCP_CLIENTS[v.number]
    current = (f"Réseau actuel {old.cidr} : masque {old.mask}, {old.usable} hôtes au plus, alors qu'il en faut "
               f"{v.needed_addresses} ; étendue DHCP de {v.pool_size} adresses pour {clients} appareils en DHCP"
               + (" : elle est épuisée, les derniers venus n'obtiennent pas de bail (APIPA)" if clients > v.pool_size
                  else " : elle suffit encore, c'est le besoin futur qui impose le changement"))
    calc = (f"{v.needed_addresses} hôtes : /{prefix + 1} n'en offre que {hosts_bigger}, /{prefix} en offre "
            f"{new.usable} (2^{32 - prefix} − 2) → /{prefix}, masque {new.mask}")
    facts = (f"Réseau {new.network}/{prefix}, diffusion {new.broadcast}, hôtes de {new.first_host} à "
             f"{new.last_host} ({new.usable})")
    fixes = []
    for host in v.new_hosts:
        mine = [e for e in errors if e.startswith(host.name + " ")]
        if not mine:
            fixes.append(f"{host.name} : correct, rien à changer")
        elif host.ip.startswith("169.254."):
            fixes.append(f"{host.name} : APIPA, aucun bail ; après l'agrandissement de l'étendue, ipconfig /release "
                         "puis /renew (vérifier aussi le câble)")
        else:
            todo = []
            if any("masque" in e for e in mine):
                todo.append(f"masque {new.mask}")
            if any("passerelle" in e or "DNS" in e for e in mine):
                todo.append(f"passerelle et DNS {v.box.ip}")
            if any("étendue DHCP" in e for e in mine):
                todo.append(f"adresse fixe hors de l'étendue {v.new_pool[0]}–{v.new_pool[1]} (ou réservation DHCP)")
            fixes.append(f"{host.name} : " + ", ".join(todo))
    return _item(
        v, 9, "Agrandir le réseau IPv4 : calcul du masque et appareils mal configurés",
        ("AP-30",),
        _ctx(v, "D", "le réseau doit grandir (document 19) ; le schéma actuel est au document 2 et les relevés de "
                     "trois appareils après le changement au document 20."),
        (d.schema, d.addressing, d.ipconfig),
        (
            "À partir des documents 2 et 19, explique pourquoi le réseau actuel ne suffit plus.",
            "Calcule le plus petit masque qui convient et donne réseau, diffusion, plage et nombre d'hôtes.",
            "Lis le document 20 : pour chaque appareil, ce qui est faux (ou correct) et pourquoi.",
            "Donne la correction de chaque appareil et le test final.",
        ),
        (
            ("Constat", current + "."),
            ("Calcul", f"{calc} ; {facts}."),
            ("Lecture des relevés", host_text + "."),
            ("Corrections et test", " ; ".join(fixes) + f" ; test : ping {v.box.ip} et d'une adresse de la nouvelle "
             "partie du réseau, accès au serveur et à Internet."),
        ),
        (f"{current}.", f"Calcul : {calc}. {facts}.", f"Relevés : {host_text}.",
         "Corrections : " + " ; ".join(fixes) + f". Test : ping de la box {v.box.ip}, du serveur et d'un site Internet."),
    )


def _s10(v: Variant, d: Docs) -> PR06Item:
    rows = v.wifi_table
    table = " ; ".join(f"{k} : {a} dBm en 2,4 GHz ({sa}), {b} dBm en 5 GHz ({sb})" for k, a, sa, b, sb in rows)
    best = v.best_channel
    audit = " ; ".join(f"{param} : {fix}" for param, fix in v.ap_audit)
    ext = v.extension
    choice = ("point d'accès câblé" if ext.wired_mbps > ext.repeater_mbps else "répéteur")
    return _item(
        v, 10, "Wi-Fi : couverture, canal, sécurité et extension",
        ("AP-33",),
        _ctx(v, "D", "le personnel se plaint du Wi-Fi ; le plan et les points de mesure sont au document 21, les "
                     "voisins, la configuration actuelle et l'extension étudiée au document 22."),
        (d.wifi_plan, d.wifi),
        (
            "Calcule le signal attendu à chaque point du document 21, dans les deux bandes, et classe-le.",
            "Choisis le canal 2,4 GHz d'après les voisins du document 22 et justifie.",
            "Corrige la configuration de sécurité du point d'accès, réglage par réglage.",
            "Compare le répéteur et le point d'accès câblé pour la zone prioritaire, débits à l'appui, et choisis.",
        ),
        (
            ("Couverture", (f"20 dBm − affaiblissement en espace libre − obstacles (pertes du cours) : {table} ; "
             f"objectif {TARGET_DBM} dBm.")),
            ("Canal", (f"Canal {best} : parmi 1, 6 et 11 (seuls sans chevauchement), c'est celui où les voisins forts "
             "(au-dessus de −80 dBm) qui le chevauchent sont les moins nombreux et les plus faibles ; 20 MHz.")),
            ("Sécurité", audit + "."),
            ("Extension", (f"Répéteur : environ {fr(ext.repeater_mbps)} Mb/s utiles (une radio, chaque paquet passe deux "
             f"fois) ; point d'accès câblé : environ {fr(ext.wired_mbps)} Mb/s → {choice}, sur un canal différent, "
             "même SSID et même sécurité, une seule source DHCP.")),
        ),
        (
            f"Couverture : {table}.",
            f"Canal : {best}, le moins gêné parmi 1, 6 et 11.",
            f"Sécurité : {audit}.",
            (f"Extension : répéteur ≈ {fr(ext.repeater_mbps)} Mb/s, point d'accès câblé ≈ {fr(ext.wired_mbps)} Mb/s : "
            f"je choisis le {choice}."),
        ),
    )


def _s11(v: Variant, d: Docs) -> PR06Item:
    matrix = v.access_matrix
    short = {p: p.replace("D:\\Partages\\", "") for p in v.access_paths}
    matrix_text = " ; ".join(f"{login} : " + ", ".join(f"{short[p]} {lvl.lower()}" for p, lvl in row.items())
                             for login, row in matrix.items())
    login, path, wanted = v.need
    share, ntfs = v.need_layers
    layer = v.need_limiting_layer
    account = v.account(login)
    if layer == "NTFS":
        why = (f"partage {share.lower()}, NTFS {ntfs.lower()} : {short[path]} n'hérite pas de Projets (héritage "
               f"désactivé) et ne cite pas {', '.join(account.groups)} → NTFS bloque")
        fix = (f"ajouter sur {short[path]} l'autorisation NTFS Modification pour le groupe {account.groups[0]} (pas "
               "pour le compte seul) ; laisser l'héritage désactivé, qui protège le dossier des autres")
        extra = ("Inès n'a aucun accès à Chantiers : le refus explicite de G_Stagiaires l'emporte sur toute "
                 "autorisation, même celle de G_Admin hérité ; c'est voulu")
    else:
        why = (f"partage {share.lower()}, NTFS {ntfs.lower()} → le partage limite (le plus restrictif des deux "
               "par le réseau) ; en session sur le serveur, seul NTFS compte : c'est pourquoi cela fonctionne là")
        fix = ("autorisations du partage : Utilisateurs authentifiés Modifier (et retirer Tout le monde), laisser "
               "NTFS faire le tri par groupe")
        extra = ("Après la correction, la direction garde Lecture sur Production (NTFS) et Modification sur Tarifs ; "
                 "Laura garde Lecture sur Tarifs et obtient Modification sur BAT comme le prévoit NTFS")
    return _item(
        v, 11, "Partage et NTFS : héritage, refus et accès effectif",
        ("AP-25", "AP-27"),
        _ctx(v, "D", "un utilisateur ne peut pas enregistrer dans un dossier partagé ; les comptes sont au document 23 "
                     "et le partage avec ses autorisations NTFS au document 24."),
        (d.accounts, d.shares),
        (
            "Calcule l'accès effectif par le réseau de chaque compte du document 23 sur chaque dossier du document 24.",
            "Explique la plainte du document 24 : quelle couche limite et pourquoi.",
            "Propose la correction la plus sûre, sans élargir les accès des autres.",
            "Indique comment tu vérifies et ce que tu documentes.",
        ),
        (
            ("Accès effectifs", (f"Par le réseau, accès = le plus restrictif du partage et de NTFS ; dans NTFS, les "
             f"groupes se cumulent et un refus explicite l'emporte : {matrix_text}.")),
            ("Couche qui limite", why + "."),
            ("Correction", fix + ". " + extra + "."),
            ("Vérification", (f"Onglet Sécurité > Avancé > Accès effectif pour {login} ; essai réel depuis son poste "
             f"(créer, enregistrer, supprimer un fichier test dans {short[path]}) ; noter la modification et le "
             "groupe concerné dans la documentation du serveur.")),
        ),
        (
            (f"Accès effectifs (le plus restrictif du partage et de NTFS, groupes cumulés, refus prioritaire) : "
            f"{matrix_text}."),
            f"Plainte de {login} ({wanted.lower()} souhaitée sur {short[path]}) : {why}.",
            f"Correction : {fix}. {extra}.",
            (f"Vérification : accès effectif dans l'onglet Sécurité, essai réel depuis le poste de {login}, "
            "documentation mise à jour."),
        ),
    )


def _s12(v: Variant, d: Docs) -> PR06Item:
    worked, span = v.journal_minutes, v.journal_span
    pause = span - worked
    explain = {
        "micrologiciel (UEFI)": "le petit programme de la carte mère qui démarre le PC avant Windows et garde ses "
                                "réglages",
        "sauvegarde 3-2-1": "trois exemplaires de vos fichiers, sur deux sortes de supports, dont un hors du bureau",
        "WPA3": "la protection actuelle du Wi-Fi, qui chiffre les échanges et résiste aux essais de mots de passe",
        "SMART": "le carnet de santé que le disque tient lui-même ; il signale l'usure avant la panne",
        "WEP": "une ancienne protection du Wi-Fi, cassée en quelques minutes, qu'il ne faut plus utiliser",
        "masque de sous-réseau": "le réglage qui dit à chaque appareil quelles adresses font partie du bureau",
    }
    terms = " ; ".join(f"{t} : {explain[t]}" for t in v.explain_terms)
    terms_list = ", ".join(v.explain_terms)
    if v.number == 1:
        recos = ("ajouter une copie hors du bureau (règle 3-2-1, document 8) ; protéger le micrologiciel par un mot de "
                 "passe ; remplacer le segment coaxial par du câblage RJ45 sur le switch")
    else:
        recos = ("ajouter une copie d'un autre type de support (règle 3-2-1) et tester les restaurations ; finir le "
                 "double démarrage après accord écrit ; remplacer le segment coaxial et retirer le répéteur grand "
                 "public au profit d'un point d'accès câblé")
    return _item(
        v, 12, "Rapport de la journée et explication au client",
        ("AP-C01", "AP-16"),
        _ctx(v, "D", f"{v.manager} veut un rapport unique de la journée, compréhensible ; ton journal est au "
                     "document 25 et les copies existantes au document 8."),
        (d.copies, d.journal),
        (
            (f"Rédige le rapport destiné à {v.manager}, dossier par dossier, avec les rubriques d'un rapport "
            "professionnel."),
            "Calcule à partir du document 25 la durée de travail facturable et l'amplitude de la journée.",
            f"Explique en mots simples les termes {terms_list}.",
            "Termine par trois recommandations justifiées et classées par priorité.",
        ),
        (
            ("Structure et contenu", (f"Client ({v.company}), date ({v.date}), technicien ; pour chaque dossier A à D : "
             "demande, constats chiffrés, cause, actions, état final vérifié ; ce qui reste à faire (accords, pièces) ; "
             "phrases claires, sans jargon inutile.")),
            ("Durées", (f"Somme des lignes : {worked} minutes = {duration_text(worked)} facturables ; de "
             f"{v.journal[0][0]} à {v.journal[-1][1]} : {duration_text(span)} d'amplitude, dont {pause} minutes de "
             "pause non facturées.")),
            ("Vocabulaire", terms + "."),
            ("Recommandations", recos + " ; chacune justifiée par un constat du jour, la plus urgente d'abord."),
        ),
        (
            (f"Rapport : {v.company}, intervention du {v.date}. Dossier A : cause trouvée, données protégées. Dossier B : "
            "devis corrigé, installations menées ou suspendues dans l'attente des accords. Dossier C : cordon refait, "
            "segment coaxial corrigé. Dossier D : réseau agrandi, Wi-Fi sécurisé, droits corrigés. Chaque dossier "
            "indique demande, constats, cause, actions et état final vérifié."),
            (f"Durées : {worked} minutes de travail = {duration_text(worked)} ; amplitude {duration_text(span)} ; "
            f"pause de {pause} minutes exclue."),
            f"En mots simples : {terms}.",
            f"Recommandations, par priorité : {recos}.",
        ),
    )


_BUILDERS = (_s1, _s2, _s3, _s4, _s5, _s6, _s7, _s8, _s9, _s10, _s11, _s12)


def build_items(v: Variant) -> tuple[PR06Item, ...]:
    docs = Docs(v)
    return tuple(builder(v, docs) for builder in _BUILDERS)


VARIANT_ITEMS: dict[int, tuple[PR06Item, ...]] = {v.number: build_items(v) for v in VARIANTS}
VARIANT_DOCS: dict[int, Docs] = {v.number: Docs(v) for v in VARIANTS}
# Clés des questions de chaque variante, dans l'ordre des situations (sélection des sessions).
VARIANT_KEYS: tuple[tuple[str, ...], ...] = tuple(
    tuple(item.key for item in VARIANT_ITEMS[v.number]) for v in VARIANTS
)
EXAM_ITEMS: tuple[PR06Item, ...] = tuple(item for v in VARIANTS for item in VARIANT_ITEMS[v.number])
ALL_ITEMS: tuple[PR06Item, ...] = EXAM_ITEMS
PRACTICE_ITEMS: tuple[PR06Item, ...] = ()


def situation_of(item: PR06Item) -> int:
    return int(item.key[-2:])


def dossier_of(situation: int) -> str:
    return next(letter for letter, _t, nums in DOSSIERS if situation in nums)


def validate_items() -> list[str]:
    errors = []
    for v in VARIANTS:
        items = VARIANT_ITEMS[v.number]
        if len(items) != SITUATIONS:
            errors.append(f"{v.label} : {len(items)} situations au lieu de {SITUATIONS}.")
        if sum(i.total_points for i in items) != EXAM_TOTAL_POINTS:
            errors.append(f"{v.label} : total différent de 100 points.")
        for item in items:
            errors += [f"{item.key} : {e}" for e in validate_exercise(item.as_exercise())]
            if item.total_points != SITUATION_POINTS[situation_of(item)]:
                errors.append(f"{item.key} : {item.total_points:g} points au lieu de "
                              f"{SITUATION_POINTS[situation_of(item)]}.")
            if item.question_type != "document_analysis" or not item.documents:
                errors.append(f"{item.key} : réponse libre sur documents attendue.")
            if not item.context.startswith(f"{v.label}. Dossier {dossier_of(situation_of(item))} "):
                errors.append(f"{item.key} : la variante et le dossier doivent ouvrir le contexte.")
    return errors

