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
}


def get_context(course_key: str) -> PedagogicalContext | None:
    return PEDAGOGICAL_CONTEXTS.get(course_key)
