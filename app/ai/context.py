"""Registre des contextes pédagogiques bornés, un par cours.

Chaque entrée délimite strictement ce que l'IA a le droit de couvrir pour un cours donné
(notions, compétences, vocabulaire, contraintes) — rédigée à la main à partir du contenu
réellement enseigné dans `app/seed.py`, jamais générée automatiquement. Un bloc
`ai_exercise` référence une clé de ce registre (`AIExerciseBlockConfig.context_key`, voir
`app/ai_exercise_blocks.py`) ; si la clé est absente, la génération/correction est refusée
plutôt que de retomber sur un contexte non borné.
"""

from app.ai.schemas import PedagogicalContext

PEDAGOGICAL_CONTEXTS: dict[str, PedagogicalContext] = {
    "ampcr-mc01": PedagogicalContext(
        course_key="ampcr-mc01",
        course_title="Informatique AMPCR — Mini-cours 01 : Architecture générale d'un PC",
        level="CESS Professionnel, niveau débutant (le cours part de zéro)",
        allowed_notions=[
            "matériel (hardware) vs logiciel (software)",
            "unité centrale vs périphériques",
            "chemin entrée → traitement → mémoire/stockage → sortie",
            (
                "carte mère : rôle, socket CPU, emplacements RAM, PCIe, connecteurs "
                "de stockage et E/S, chipset, compatibilité entre composants"
            ),
            (
                "processeur (CPU) : rôle, cœurs, threads, fréquence, cache — sans "
                "architecture avancée"
            ),
            (
                "mémoire vive (RAM) : rôle, volatilité, capacité en Go — sans "
                "détail DDR/dual-channel"
            ),
            (
                "stockage (HDD/SSD) : rôle, capacité vs performance, persistance "
                "hors tension — SATA/NVMe seulement introduits"
            ),
            (
                "carte graphique (GPU) : rôle, intégré vs dédié, VRAM — sans "
                "architecture GPU avancée"
            ),
            (
                "alimentation (PSU) : rôle, puissance en watts, sécurité (ne "
                "jamais l'ouvrir) — sans détail électrique"
            ),
            "périphériques et connecteurs E/S : entrée, sortie, mixte",
            (
                "scénario d'interaction : lancement d'un programme depuis un SSD "
                "(stockage → RAM → CPU → GPU → écran), rôle de la carte mère et du PSU"
            ),
            (
                "vocabulaire FR/EN de base (hardware/software, motherboard, CPU, "
                "RAM, storage, HDD, SSD, graphics card/GPU, power supply/PSU, "
                "device/peripheral, input, output)"
            ),
            (
                "vocabulaire ancien du référentiel (lecteur de disquettes, "
                "graveur optique) comme repère historique uniquement"
            ),
        ],
        competencies=[
            "1.1.1 identifier et nommer les composants d'un PC",
            "1.1.2 décrire leurs caractéristiques principales",
            "1.1.3 expliquer le rôle de chaque composant",
            (
                "1.1.4 expliquer les interactions entre composants et utiliser "
                "le vocabulaire informatique FR/EN"
            ),
        ],
        vocabulary=[
            "hardware", "software", "motherboard", "CPU", "RAM", "storage", "HDD",
            "SSD", "graphics card", "GPU", "power supply", "PSU", "device",
            "peripheral", "input", "output",
        ],
        constraints=(
            "Ne jamais poser de question qui exige des connaissances détaillées "
            "d'architecture CPU, de DDR/dual-channel (réservés au mini-cours 03), "
            "d'interfaces SATA/NVMe en détail ou de fiabilité/sauvegarde du stockage "
            "(réservés au mini-cours 04), ou d'électricité/refroidissement détaillés "
            "de l'alimentation (réservés au mini-cours 05). Rester strictement au "
            "niveau d'introduction de ce mini-cours 01."
        ),
    ),
    "ampcr-mc02": PedagogicalContext(
        course_key="ampcr-mc02",
        course_title=(
            "Informatique AMPCR — Mini-cours 02 : Carte mère, formats et connectiques"
        ),
        level="CESS Professionnel, suite du mini-cours 01",
        allowed_notions=[
            (
                "rôle détaillé de la carte mère : interconnexion, alimentation "
                "distribuée aux composants, firmware, contrôleurs intégrés"
            ),
            (
                "formats ATX, micro-ATX, Mini-ITX : dimensions relatives, nombre "
                "d'emplacements, compatibilité boîtier, conséquences pratiques — le "
                "format ne détermine pas à lui seul les performances"
            ),
            (
                "socket CPU : compatibilité mécanique, distincte de la compatibilité "
                "complète (génération CPU, chipset, version BIOS/UEFI)"
            ),
            (
                "chipset moderne : circuit unique gérant USB/SATA/PCIe "
                "additionnels — sans description historique north/south bridge"
            ),
            (
                "slots RAM (DIMM) : détrompeur, canaux mémoire, emplacements "
                "recommandés par le manuel — sans détail DDR/dual-channel approfondi"
            ),
            (
                "PCI Express : lanes, tailles x1/x4/x8/x16, taille physique vs "
                "liaison électrique réelle, générations et rétrocompatibilité"
            ),
            (
                "stockage sur la carte mère : connecteur SATA data, M.2 comme format "
                "de connecteur (pas synonyme de NVMe) — introduction seulement"
            ),
            (
                "alimentation interne : ATX 24 broches, EPS CPU 4/8 broches, "
                "distinction avec les connecteurs GPU, SATA Power venant du PSU"
            ),
            (
                "connecteurs internes : CPU_FAN, SYS_FAN/CHA_FAN, USB internes, "
                "audio façade, RGB/ARGB comme extension moderne"
            ),
            (
                "connectique arrière E/S : USB-A/USB-C, audio, Ethernet, vidéo, "
                "PS/2 — connecteur physique différent du protocole supporté"
            ),
            (
                "F_PANEL : Power SW, Reset SW, Power LED, HDD LED — interrupteurs "
                "sans polarité, LED avec polarité"
            ),
            "BIOS/UEFI : rôle de firmware, initialisation matérielle, POST",
            (
                "méthode de compatibilité d'une configuration : besoin → format → "
                "socket/CPU/BIOS → RAM → stockage → PCIe → alimentation/connecteurs "
                "→ boîtier → manuel/QVL"
            ),
            (
                "diagnostic professionnel no-POST : procédure structurée (couper "
                "l'alimentation, contrôle visuel, ATX/EPS, RAM, GPU/écran, codes "
                "LED/beep, configuration minimale, clear CMOS, documentation)"
            ),
            (
                "sécurité : toujours hors tension, décharge électrostatique (ESD), "
                "manipulation par les bords, ne jamais forcer un connecteur"
            ),
            (
                "vocabulaire FR/EN : motherboard, socket, chipset, slot, header, "
                "front panel, expansion slot, I/O, lane, firmware, POST"
            ),
        ],
        competencies=[
            "1.1.1 identifier et nommer les composants d'un PC",
            "1.1.2 décrire leurs caractéristiques principales",
            "1.1.3 expliquer le rôle de chaque composant",
            (
                "1.1.4 expliquer les interactions entre composants et utiliser "
                "le vocabulaire informatique FR/EN"
            ),
            "1.2.3 repérer les branchements et connexions",
            "2.3.2 choisir des composants adéquats à un besoin",
            "2.3.3 vérifier la compatibilité de composants choisis",
            "3.4.1 connecter un périphérique correctement",
            "3.4.2 choisir le câblage approprié",
        ],
        vocabulary=[
            "motherboard", "socket", "chipset", "slot", "header", "front panel",
            "expansion slot", "I/O", "lane", "firmware", "POST",
        ],
        constraints=(
            "Ne jamais poser de question qui exige des connaissances détaillées de "
            "DDR/dual-channel (réservées au mini-cours 03), d'interfaces SATA/NVMe "
            "en détail ou de fiabilité/sauvegarde du stockage (réservées au "
            "mini-cours 04), ou d'électricité/refroidissement détaillés de "
            "l'alimentation (réservés au mini-cours 05). Ne jamais présenter "
            "l'architecture historique « north bridge / south bridge » comme la "
            "réalité actuelle. Rester strictement au niveau de ce mini-cours 02."
        ),
    ),
}


def get_context(course_key: str) -> PedagogicalContext | None:
    return PEDAGOGICAL_CONTEXTS.get(course_key)
