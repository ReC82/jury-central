"""PR12 « Dépannage logiciel et restauration du système » — données de référence, règles de
décision et schémas SVG (ticket #215).

Tout est construit **depuis des données** de ce module (tuples, fonctions), contrôlées par
`tests/test_ticket215_ampcr_pratique_pr12.py` :

- les sept familles de causes logicielles (`CAUSES`) et l'isolement de la cause par une suite
  de tests (`ISOLATION_TREE`, `isolate`) ;
- le recueil des faits (`FACTS`) et les journaux à lire (`LOGS`) ;
- l'échelle des interventions, du geste le moins invasif à la réinstallation (`LADDER`), avec
  leur effet sur les fichiers et les programmes, et la précaution exigée (`precaution_for`) ;
- les outils du démarrage avancé de Windows (`WINRE_TOOLS`) ;
- la sauvegarde et la vérification d'intégrité par empreinte SHA-256 (`sha256_hex`,
  `BACKUP_FILES`, `copy_check`) ;
- l'espace disque sous Linux (`df_use_percent`) et les commandes de dépannage Linux
  (`LINUX_FIXES`) ;
- la distinction panne réseau logicielle / physique (`NETWORK_TREE`, `network_layer`) ;
- cinq procédures illustrées (`METHOD_STEPS`, `BACKUP_STEPS`, `RESTORE_STEPS`, `BOOT_STEPS`,
  `LINUX_SERVICE_STEPS`) et des relevés fictifs (Windows en français, Linux en anglais).

Les libellés de Windows 11 et des distributions Linux sont ceux **de la rédaction (octobre
2026)** ; ils changent selon les versions : la documentation de l'éditeur fait foi. Les
captures sont **fictives** et abrégées ; aucun schéma ne vient d'une image générée ni d'une
photographie. Les empreintes SHA-256 des exercices sont **calculées** (bibliothèque `hashlib`)
sur des contenus fictifs : elles sont exactes pour ces contenus.
"""

import hashlib
import math
from dataclasses import dataclass
from html import escape

from app.v1.ampcr_pratique_visuals import (
    Figure,
    _svg,
    _text_lines,
    _wrap,
    decision_tree_svg,
    screen_svg,
    step_flow_svg,
)

SCREEN_WIDTH = 56  # caractères au plus par ligne de capture (lisible sur mobile, comme PR01-PR10)
WRITTEN_AT = "octobre 2026"
FICTIVE_LABEL = "Capture fictive — sortie abrégée"

# =============================================================================================
# 1. Familles de causes et isolement
# =============================================================================================

CAUSE_STORAGE = "Stockage (disque plein ou défaillant)"
CAUSE_APP = "Application"
CAUSE_ACCOUNT = "Compte ou profil utilisateur"
CAUSE_DRIVER = "Pilote, service ou programme au démarrage"
CAUSE_MALWARE = "Logiciel malveillant"
CAUSE_OS = "Système d'exploitation"
CAUSE_SERVICE = "Service"


@dataclass(frozen=True)
class Cause:
    name: str
    signs: str  # symptômes typiques
    test: str  # test qui confirme ou écarte
    first_action: str


CAUSES: tuple[Cause, ...] = (
    Cause(CAUSE_OS, "Tout le poste est touché, dans tous les comptes ; plantages de l'Explorateur, menu Démarrer, mises à jour qui échouent.",
          "Persiste en mode sans échec et dans un compte de test ; SFC signale des fichiers corrompus.",
          "DISM puis SFC ; désinstaller la dernière mise à jour ; restauration du système."),
    Cause(CAUSE_APP, "Un seul programme plante, refuse de s'ouvrir ou affiche une erreur ; les autres fonctionnent.",
          "Le même programme échoue dans un compte de test ; les autres programmes vont bien.",
          "Mettre à jour, réparer (Paramètres → Applications) ou réinstaller le programme."),
    Cause(CAUSE_DRIVER, "Écran noir ou plantage après l'installation d'un pilote ou d'un logiciel ; périphérique qui ne répond plus.",
          "Disparaît en mode sans échec (pilotes et services de base seulement).",
          "Restaurer le pilote, désinstaller le dernier logiciel, démarrage minimal (msconfig)."),
    Cause(CAUSE_SERVICE, "Une fonction précise ne marche plus (impression, site web, partage) ; message « service arrêté ».",
          "services.msc ou systemctl status : service arrêté ou en échec ; journal du service.",
          "Lire le journal du service, corriger la cause, redémarrer le service."),
    Cause(CAUSE_ACCOUNT, "Un seul utilisateur a le problème ; « profil temporaire » ; bureau vide ; réglages perdus.",
          "Tout fonctionne dans un autre compte sur le même poste.",
          "Sauvegarder le profil, réparer ou recréer le profil, recopier les données."),
    Cause(CAUSE_MALWARE, "Fenêtres publicitaires, page d'accueil changée, processus inconnu, fichiers renommés et chiffrés.",
          "Analyse hors ligne de Microsoft Defender ; extensions et programmes inconnus.",
          "Isoler du réseau, analyser, restaurer depuis une sauvegarde saine ; prévenir le responsable."),
    Cause(CAUSE_STORAGE, "Lenteurs, « espace insuffisant », « No space left on device », erreurs de lecture, fichiers illisibles.",
          "Espace libre (Stockage, df -h) ; état SMART ; journaux du disque.",
          "Disque plein : libérer de l'espace. Disque défaillant : sauvegarder d'abord, puis remplacer (PR05, PR06)."),
)
CAUSE_NAMES = tuple(c.name for c in CAUSES)

# Arbre d'isolement (convention du cours) : chaque question, si la réponse est « non », désigne
# une famille ; si « oui », on passe à la suivante. Le stockage est contrôlé en premier, car un
# disque qui lâche commande de sauvegarder avant toute autre manipulation.
ISOLATION_TREE: tuple[tuple[str, str, str], ...] = (
    ("disk_ok", "Le disque est-il sain et a-t-il de l'espace libre ?",
     f"{CAUSE_STORAGE} : sauvegarder, libérer ou remplacer."),
    ("several_apps", "Le problème touche-t-il plusieurs programmes ?",
     f"{CAUSE_APP} : réparer, mettre à jour ou réinstaller ce programme."),
    ("other_account", "Existe-t-il aussi dans un compte de test ?",
     f"{CAUSE_ACCOUNT} : sauvegarder puis réparer ou recréer le profil."),
    ("safe_mode", "Persiste-t-il en mode sans échec ?",
     f"{CAUSE_DRIVER} : restaurer, désinstaller, démarrage minimal."),
    ("scan_clean", "L'analyse antivirus hors ligne est-elle propre ?",
     f"{CAUSE_MALWARE} : isoler, nettoyer, restaurer depuis une sauvegarde saine."),
)
ISOLATION_FINAL = (
    f"{CAUSE_OS} : DISM puis SFC, désinstaller la mise à jour, restauration du système ; "
    "réinstallation seulement en dernier recours, avec sauvegarde et accord."
)
_ISOLATION_RESULT = (CAUSE_STORAGE, CAUSE_APP, CAUSE_ACCOUNT, CAUSE_DRIVER, CAUSE_MALWARE)


def isolate(*, disk_ok: bool, several_apps: bool, other_account: bool, safe_mode: bool,
            scan_clean: bool) -> str:
    """Famille de cause désignée par l'arbre d'isolement (un service en panne se repère
    directement par son état : voir `CAUSE_SERVICE`)."""
    answers = {"disk_ok": disk_ok, "several_apps": several_apps, "other_account": other_account,
               "safe_mode": safe_mode, "scan_clean": scan_clean}
    for (key, _question, _no), cause in zip(ISOLATION_TREE, _ISOLATION_RESULT, strict=True):
        if not answers[key]:
            return cause
    return CAUSE_OS


# =============================================================================================
# 2. Recueil des faits et journaux
# =============================================================================================

# (fait à recueillir, question à poser ou geste)
FACTS: tuple[tuple[str, str], ...] = (
    ("Symptôme exact", "Que se passe-t-il ? Message et code d'erreur recopiés mot pour mot, photo de l'écran."),
    ("Depuis quand", "Date et heure de la première apparition ; le problème est-il permanent ou intermittent ?"),
    ("Reproductibilité", "Peut-on le déclencher à la demande ? Avec quelles actions, dans quel ordre ?"),
    ("Portée", "Un programme ou tous ? Un utilisateur ou tous ? Un poste ou plusieurs ?"),
    ("Changements récents", "Mise à jour, logiciel ou pilote installé, matériel ajouté, coupure de courant, réglage modifié ?"),
    ("Données et sauvegarde", "Quelles données comptent ? Existe-t-il une sauvegarde récente, et où ?"),
)

# (système, outil ou commande, ce qu'on y lit)
LOGS: tuple[tuple[str, str, str], ...] = (
    ("Windows", "Observateur d'événements (eventvwr.msc) → Journaux Windows → Système et Application",
     "Erreurs et avertissements horodatés, source et ID de l'événement."),
    ("Windows", "Moniteur de fiabilité (« Afficher l'historique de fiabilité », perfmon /rel)",
     "Une colonne par jour : plantages d'applications, échecs de Windows, installations et mises à jour."),
    ("Windows", "Paramètres → Windows Update → Historique des mises à jour",
     "Mises à jour installées, avec leur date et leur numéro KB."),
    ("Linux", "journalctl -b -p err (erreurs du démarrage en cours) ; journalctl -b -1 (démarrage précédent, si le journal est conservé)",
     "Messages du système et des services, par priorité."),
    ("Linux", "systemctl --failed ; journalctl -u service -b",
     "Services en échec et leurs messages."),
    ("Linux", "/var/log/apt/history.log (Debian, Ubuntu) ; dnf history (Fedora)",
     "Paquets installés, mis à jour ou retirés, avec la date."),
)

# =============================================================================================
# 3. Échelle des interventions : effet sur les données et précaution
# =============================================================================================

PREC_NOTE = "Noter l'état avant d'agir"
PREC_BACKUP = "Sauvegarde à jour et accord du client"
PREC_WRITTEN = "Sauvegarde vérifiée et accord écrit du client"
PRECAUTIONS = (PREC_NOTE, PREC_BACKUP, PREC_WRITTEN)


@dataclass(frozen=True)
class Intervention:
    name: str
    keeps_files: bool  # fichiers personnels (Documents, Bureau, Images…)
    keeps_programs: bool  # programmes et pilotes installés
    reinstalls: bool  # réinstalle Windows (sur place ou à neuf)
    detail: str


# Du geste le moins invasif au plus invasif (convention du cours, d'après la documentation de
# Microsoft pour les effets de chaque outil).
LADDER: tuple[Intervention, ...] = (
    Intervention("Annuler le dernier changement", True, True, False,
                 "Restaurer le pilote, désinstaller le dernier programme ou la dernière mise à jour."),
    Intervention("Réparer les fichiers système", True, True, False,
                 "DISM /Online /Cleanup-Image /RestoreHealth puis sfc /scannow."),
    Intervention("Restauration du système", True, False, False,
                 "Retour à un point de restauration : programmes, pilotes et mises à jour installés après sont retirés."),
    Intervention("Réinstaller via Windows Update", True, True, True,
                 "Récupération → « Résoudre les problèmes à l'aide de Windows Update » : réinstalle la version actuelle."),
    Intervention("Réinitialiser en conservant les fichiers", True, False, True,
                 "« Réinitialiser ce PC » → « Conserver mes fichiers » : applications et réglages retirés."),
    Intervention("Réinstallation complète", False, False, True,
                 "« Supprimer tout » ou installation propre : disque effacé, tout est à réinstaller."),
)
LADDER_BY_NAME = {i.name: i for i in LADDER}


def precaution_for(intervention: Intervention) -> str:
    """Précaution minimale (convention du cours) : rien n'est retiré ni réinstallé → noter
    l'état ; programmes retirés ou Windows réinstallé sur place → sauvegarde à jour et accord ;
    fichiers effacés, ou réinstallation qui retire les applications → sauvegarde **vérifiée** et
    accord **écrit**."""
    if not intervention.keeps_files or (intervention.reinstalls and not intervention.keeps_programs):
        return PREC_WRITTEN
    if not intervention.keeps_programs or intervention.reinstalls:
        return PREC_BACKUP
    return PREC_NOTE


EFFECT_ALL = "Fichiers et programmes conservés"
EFFECT_PROGRAMS = "Fichiers conservés, programmes récents ou applications retirés"
EFFECT_NOTHING = "Fichiers et programmes effacés"
EFFECTS = (EFFECT_ALL, EFFECT_PROGRAMS, EFFECT_NOTHING)


def effect_of(intervention: Intervention) -> str:
    if not intervention.keeps_files:
        return EFFECT_NOTHING
    return EFFECT_ALL if intervention.keeps_programs else EFFECT_PROGRAMS


def ladder_svg(steps: tuple[Intervention, ...], *, width: int = 380) -> str:
    """Échelle des interventions : une marche par geste, du moins invasif (1) au plus
    invasif ; pour chaque marche, fichiers et programmes conservés (✓) ou non (✗) et la
    précaution. Les symboles et le texte portent l'information, pas la couleur."""
    parts: list[str] = [
        (f'<text x="{width // 2}" y="18" text-anchor="middle" font-size="12.5" font-weight="700">'
         "Du moins invasif (1) au plus invasif</text>")
    ]
    y = 28
    for index, step in enumerate(steps, start=1):
        indent = 6 + (index - 1) * 6
        box_w = width - indent - 6
        prec = precaution_for(step)
        name_lines = _wrap(f"{index}. {step.name}", 40)
        prec_lines = _wrap(f"Précaution : {prec}", 52)
        box_h = 16 * len(name_lines) + 14 * len(prec_lines) + 28
        parts.append(
            f'<g data-step="{index}" data-files="{int(step.keeps_files)}" data-programs="{int(step.keeps_programs)}">'
            f'<rect x="{indent}" y="{y}" width="{box_w}" height="{box_h}" rx="6" fill="#f4f6fb" '
            'stroke="#33415c" stroke-width="1.5"/>'
        )
        parts.append(_text_lines(indent + 8, y + 17, name_lines, size=12.5, weight="700", step=16))
        marks = (f"Fichiers {'✓' if step.keeps_files else '✗'} · "
                 f"Programmes {'✓' if step.keeps_programs else '✗'}")
        line_y = y + 17 + 16 * len(name_lines)
        parts.append(f'<text x="{indent + 8}" y="{line_y}" font-size="11.5">{escape(marks)}</text>')
        parts.append(_text_lines(indent + 8, line_y + 15, prec_lines, size=11, step=14))
        parts.append("</g>")
        y += box_h + 6
    parts.append(
        f'<text x="{width // 2}" y="{y + 14}" text-anchor="middle" font-size="11">'
        "✓ conservés · ✗ retirés ou effacés</text>"
    )
    return _svg(width, y + 24, parts)


# Outils du démarrage avancé (WinRE) : Dépannage → Options avancées, et Réinitialiser ce PC.
# (outil, rôle, effet sur les données)
WINRE_TOOLS: tuple[tuple[str, str, str], ...] = (
    ("Outil de redémarrage système (réparation du démarrage)", "Répare automatiquement les fichiers de démarrage.", "Aucun sur les fichiers ni les programmes."),
    ("Paramètres → mode sans échec (touche 4 ou F4)", "Démarre avec les pilotes et services de base : diagnostic et retour arrière.", "Aucun."),
    ("Désinstaller des mises à jour", "Retire la dernière mise à jour qualité ou de fonctionnalité.", "Fichiers conservés ; la mise à jour est retirée."),
    ("Restauration du système", "Revient à un point de restauration.", "Fichiers conservés ; programmes et pilotes installés après le point retirés."),
    ("Invite de commandes", "Lecture (dir, bcdedit) et réparations manuelles (sfc hors ligne).", "Selon la commande : identifier les lecteurs avant tout."),
    ("Réinitialiser ce PC", "Réinstalle Windows : « Conserver mes fichiers » ou « Supprimer tout ».", "Applications retirées ; « Supprimer tout » efface aussi les fichiers."),
    ("Paramètres du microprogramme UEFI", "Ouvre le firmware (ordre de démarrage, mode, voir PR11).", "Aucun."),
)

# =============================================================================================
# 4. Sauvegarde et vérification d'intégrité
# =============================================================================================


def sha256_hex(content: bytes) -> str:
    """Empreinte SHA-256 (64 caractères hexadécimaux), comme Get-FileHash ou sha256sum."""
    return hashlib.sha256(content).hexdigest()


@dataclass(frozen=True)
class BackupFile:
    name: str
    original: bytes  # contenu fictif sur le disque du client
    copy: bytes  # contenu fictif sur le disque de sauvegarde


# Exercice E15 : la troisième copie est tronquée (copie interrompue) ; les autres sont identiques.
BACKUP_FILES: tuple[BackupFile, ...] = (
    BackupFile("compta-2026.ods", b"Comptabilite 2026 - fichier fictif Jury Central\n" * 40,
               b"Comptabilite 2026 - fichier fictif Jury Central\n" * 40),
    BackupFile("clients.csv", b"nom;ville\nDupont;Namur\nMartin;Liege\n" * 25,
               b"nom;ville\nDupont;Namur\nMartin;Liege\n" * 25),
    BackupFile("photos-chantier.zip", b"PK-archive-fictive-photos-chantier-" * 60,
               (b"PK-archive-fictive-photos-chantier-" * 60)[:1500]),
    BackupFile("devis-0412.pdf", b"%PDF-1.7 devis fictif 0412\n" * 30,
               b"%PDF-1.7 devis fictif 0412\n" * 30),
)

COPY_OK = "Copie identique"
COPY_BAD = "Copie différente : recopier puis revérifier"


def copy_check(f: BackupFile) -> str:
    return COPY_OK if sha256_hex(f.original) == sha256_hex(f.copy) else COPY_BAD


# (système, commande d'empreinte)
HASH_COMMANDS: tuple[tuple[str, str], ...] = (
    ("Windows (PowerShell)", "Get-FileHash E:\\Sauvegarde\\compta-2026.ods  (SHA256 par défaut)"),
    ("Windows (invite de commandes)", "certutil -hashfile E:\\Sauvegarde\\compta-2026.ods SHA256"),
    ("Linux", "sha256sum compta-2026.ods ; sha256sum -c empreintes.sha256 (vérifie une liste)"),
)

BACKUP_STEPS: tuple[tuple[str, str], ...] = (
    ("Inventorier les données", "Documents, Bureau, Images, courriels, favoris, données d'un logiciel."),
    ("Préparer le support", "Disque externe assez grand, sain, étiqueté au nom du client."),
    ("Copier sans déplacer", "Copie (robocopy, rsync, Explorateur) ; l'original reste en place."),
    ("Vérifier la copie", "Nombre et taille des fichiers, empreintes SHA-256, ouverture d'essai."),
    ("Consigner", "Ce qui est sauvegardé, où, quand, et ce qui ne l'est pas."),
    ("Obtenir l'accord", "Accord écrit du client avant d'effacer ou de réinstaller."),
)

# =============================================================================================
# 5. Windows : restauration du système, démarrage, profil
# =============================================================================================

RESTORE_STEPS: tuple[tuple[str, str], ...] = (
    ("Vérifier la sauvegarde", "Données du client sauvegardées ; accord pour retirer les programmes récents."),
    ("Ouvrir la restauration", "rstrui.exe, ou WinRE → Dépannage → Options avancées."),
    ("Choisir le point", "Le dernier point antérieur au début de la panne (date, description)."),
    ("Programmes concernés", "« Rechercher les programmes concernés » : noter ce qui sera retiré."),
    ("Lancer et attendre", "Ne pas éteindre le PC ; redémarrage automatique."),
    ("Contrôler", "Symptôme disparu ; programmes retirés réinstallés si besoin ; rapport."),
)

BOOT_STEPS: tuple[tuple[str, str], ...] = (
    ("Noter l'écran", "Message, code, depuis quand, dernier changement (pilote, mise à jour)."),
    ("Ouvrir WinRE", "Après 2 échecs de démarrage, ou clé d'installation → Réparer l'ordinateur."),
    ("Réparation du démarrage", "Outil automatique ; ne touche pas aux fichiers."),
    ("Mode sans échec", "Paramètres → Redémarrer → 4 : annuler le dernier pilote ou logiciel."),
    ("Mise à jour, restauration", "Désinstaller la dernière mise à jour, puis point de restauration."),
    ("Contrôler", "Démarrage normal, deux fois ; journaux sans nouvelle erreur ; rapport."),
)

# Profil temporaire (cas 3) : message affiché par Windows 11 à l'ouverture de session.
TEMP_PROFILE_SCREEN: tuple[str, ...] = (
    "Notification à l'ouverture de session",
    "  Nous ne pouvons pas nous connecter à votre compte",
    "  Vous êtes connecté avec un profil temporaire.",
    "  Vous ne pouvez pas accéder à vos fichiers, et les",
    "  fichiers créés dans ce profil seront supprimés lors",
    "  de votre déconnexion.",
    "",
    "Observateur d'événements → Application :",
    "  Avertissement  User Profile Service  ID 1511",
    "  Windows ne trouve pas le profil local et ouvre",
    "  une session avec un profil temporaire.",
)

PROFILE_STEPS: tuple[tuple[str, str], ...] = (
    ("Ne rien enregistrer", "Le profil temporaire est vidé à la déconnexion."),
    ("Sauvegarder l'ancien profil", "Depuis un compte administrateur : copie de C:\\Users\\nom."),
    ("Vérifier le disque", "Espace libre, état SMART, DISM puis SFC."),
    ("Créer un nouveau profil", "Nouveau compte, ou ancien compte après renommage du dossier."),
    ("Recopier les données", "Documents, Bureau, Images, favoris ; pas tout AppData."),
    ("Contrôler", "Ouverture de session normale, fichiers présents, courrier configuré."),
)

# Cas 4 : historique des mises à jour (dates de la situation fictive).
UPDATE_CASE_KB = "KB5099999"  # numéro fictif, hors de la plage des mises à jour réelles connues
UPDATE_CASE_ROWS: tuple[tuple[str, str], ...] = (
    ("21/10/2026", f"Mise à jour cumulative de Windows 11 ({UPDATE_CASE_KB})"),
    ("14/10/2026", "Mise à jour de la définition de Microsoft Defender"),
    ("08/10/2026", "Mise à jour des pilotes : imprimante (facultative)"),
)

# =============================================================================================
# 6. Linux : service, paquets, GRUB, système de fichiers, espace disque
# =============================================================================================

LINUX_SERVICE_STEPS: tuple[tuple[str, str], ...] = (
    ("Lister les échecs", "systemctl --failed ; systemctl status nginx."),
    ("Lire le journal", "journalctl -u nginx -b : le message exact."),
    ("Tester la configuration", "sudo nginx -t (sshd -t, apache2ctl configtest…)."),
    ("Corriger prudemment", "Copie du fichier avant, ou retour à la copie qui marchait."),
    ("Redémarrer le service", "sudo systemctl restart nginx ; enabled au démarrage."),
    ("Contrôler", "active (running), page testée, journal sans erreur ; rapport."),
)

NGINX_SCREEN: tuple[str, ...] = (
    "$ systemctl status nginx",
    "× nginx.service - A high performance web server",
    "     Loaded: loaded (/usr/lib/systemd/system/",
    "             nginx.service; enabled; preset: enabled)",
    "     Active: failed (Result: exit-code)",
    "$ sudo nginx -t",
    'nginx: [emerg] unexpected "}" in',
    "  /etc/nginx/sites-enabled/boutique:14",
    "nginx: configuration file /etc/nginx/nginx.conf",
    "  test failed",
)

DPKG_SCREEN: tuple[str, ...] = (
    "$ sudo apt upgrade",
    "E: dpkg was interrupted, you must manually run",
    "   'sudo dpkg --configure -a' to correct the problem.",
)

# Exercice E16 : documents restaurés depuis la sauvegarde avec « sudo cp », donc à root.
RESTORED_SCREEN: tuple[str, ...] = (
    "$ ls -l /home/anne/Documents",
    "-rw-r--r-- 1 root root 48213 Oct 20 09:12 devis.odt",
    "-rw-r--r-- 1 root root 20117 Oct 20 09:12 notes.txt",
    "$ echo test >> /home/anne/Documents/notes.txt",
    "bash: /home/anne/Documents/notes.txt:",
    "  Permission denied",
)
RESTORED_MODE = "-rw-r--r--"

GRUB_SCREEN: tuple[str, ...] = (
    "GNU GRUB — Advanced options for Ubuntu",
    "  Ubuntu, with Linux 6.8.0-49-generic",
    "  Ubuntu, with Linux 6.8.0-49-generic (recovery mode)",
    "* Ubuntu, with Linux 6.8.0-47-generic",
    "  Ubuntu, with Linux 6.8.0-47-generic (recovery mode)",
    "",
    "$ uname -r     # après démarrage sur la 3e entrée",
    "6.8.0-47-generic",
)
GRUB_NEW_KERNEL = "6.8.0-49-generic"
GRUB_OLD_KERNEL = "6.8.0-47-generic"


def df_use_percent(used: float, avail: float) -> int:
    """Use% de `df` : utilisé / (utilisé + disponible), arrondi **au-dessus** (les blocs
    réservés à root ne comptent pas dans le disponible)."""
    return math.ceil(used * 100 / (used + avail))


def _size(value: float) -> str:
    """Taille au format de `df -h` / `du -h` (Gio) : une décimale sous 10, entier au-delà,
    arrondi **au-dessus** comme le fait GNU coreutils."""
    if value < 10:
        return f"{math.ceil(round(value * 10, 6)) / 10:.1f}G"
    return f"{math.ceil(round(value, 6))}G"


# Cas 5 : partition racine pleine. Tailles en Gio ; 1,5 Gio réservé à root (5 %).
CASE5_SIZE = 30.0
CASE5_RESERVED = 1.5
CASE5_USED_BEFORE = 28.5
CASE5_AVAIL_BEFORE = CASE5_SIZE - CASE5_RESERVED - CASE5_USED_BEFORE  # 0
CASE5_VAR: tuple[tuple[str, float], ...] = (  # sudo du -xh -d1 /var
    ("/var/cache", 2.4),
    ("/var/lib", 3.1),
    ("/var/log", 6.2),
)
CASE5_VAR_TOTAL = round(sum(size for _p, size in CASE5_VAR) + 0.1, 1)  # + petits dossiers
CASE5_FREED: tuple[tuple[str, float], ...] = (
    ("sudo journalctl --vacuum-size=500M", 5.7),
    ("sudo apt clean", 2.2),
)
CASE5_USED_AFTER = round(CASE5_USED_BEFORE - sum(v for _c, v in CASE5_FREED), 1)
CASE5_AVAIL_AFTER = round(CASE5_SIZE - CASE5_RESERVED - CASE5_USED_AFTER, 1)


DF_HEADER = f"{'Filesystem':<16}{'Size':>5}{'Used':>6}{'Avail':>6}{'Use%':>5} Mounted on"


def _df_line(used: float, avail: float) -> str:
    pct = f"{df_use_percent(used, avail)}%"
    shown_avail = _size(avail) if avail else "0"
    return f"{'/dev/sda2':<16}{_size(CASE5_SIZE):>5}{_size(used):>6}{shown_avail:>6}{pct:>5} /"


CASE5_DF_BEFORE: tuple[str, ...] = ("$ df -h /", DF_HEADER, _df_line(CASE5_USED_BEFORE, CASE5_AVAIL_BEFORE))
CASE5_DU: tuple[str, ...] = (
    "$ sudo du -xh -d1 /var | sort -h",
    *(f"{_size(size):<6}{path}" for path, size in CASE5_VAR),
    f"{_size(CASE5_VAR_TOTAL):<6}/var",
)
CASE5_DF_AFTER: tuple[str, ...] = ("$ df -h /", DF_HEADER, _df_line(CASE5_USED_AFTER, CASE5_AVAIL_AFTER))
DISK_SCREEN: tuple[str, ...] = (*CASE5_DF_BEFORE, *CASE5_DU)

# (besoin, commande) — commandes Linux de dépannage du cours.
LINUX_FIXES: tuple[tuple[str, str], ...] = (
    ("Lister les services en échec", "systemctl --failed"),
    ("Lire les erreurs du démarrage précédent", "journalctl -b -1 -p err"),
    ("Terminer une installation de paquets interrompue", "sudo dpkg --configure -a"),
    ("Réparer des dépendances de paquets cassées", "sudo apt --fix-broken install"),
    ("Mesurer l'espace libre des partitions", "df -h"),
    ("Trouver les dossiers qui occupent la place", "sudo du -xh -d1 /var | sort -h"),
    ("Vérifier un système de fichiers démonté", "sudo fsck -f /dev/sdb1"),
    ("Régénérer le menu de démarrage", "sudo update-grub"),
)

# =============================================================================================
# 7. Panne réseau : logicielle ou physique ?
# =============================================================================================

NET_PHYSICAL = "Physique : câble, prise, port du switch, carte, Wi-Fi désactivé"
NET_DHCP = "Logiciel/réseau : pas d'adresse DHCP (169.254.x.x)"
NET_LOCAL = "Configuration IP ou réseau local : adresse, masque, passerelle"
NET_INTERNET = "Accès Internet : box ou fournisseur"
NET_DNS = "Logiciel : serveur DNS"
NET_APP = "Logiciel : application, proxy ou pare-feu du poste"
NET_LAYERS = (NET_PHYSICAL, NET_DHCP, NET_LOCAL, NET_INTERNET, NET_DNS, NET_APP)

NETWORK_TREE: tuple[tuple[str, str], ...] = (
    ("La carte a-t-elle un lien (pas de « Média déconnecté ») ?", "Physique : câble, prise, port, carte."),
    ("A-t-elle une adresse valide (pas de 169.254) ?", "DHCP : box, serveur DHCP, ipconfig /renew."),
    ("La passerelle répond-elle au ping ?", "Adresse, masque, passerelle ; réseau local."),
    ("Une adresse Internet répond-elle ?", "Box ou fournisseur d'accès."),
    ("Le nom est-il résolu (nslookup) ?", "Serveur DNS du poste."),
)
NETWORK_FINAL = (
    "Réseau correct jusqu'au nom : application, proxy ou pare-feu du poste ; comparer avec un "
    "autre navigateur ou un autre poste (dépannage complet : PR24)."
)


def network_layer(*, link: bool, valid_ip: bool, gateway_ok: bool, internet_ok: bool,
                  dns_ok: bool) -> str:
    """Où se situe la panne, du plus proche au plus lointain (même ordre que l'arbre)."""
    if not link:
        return NET_PHYSICAL
    if not valid_ip:
        return NET_DHCP
    if not gateway_ok:
        return NET_LOCAL
    if not internet_ok:
        return NET_INTERNET
    if not dns_ok:
        return NET_DNS
    return NET_APP


MEDIA_DISCONNECTED_SCREEN: tuple[str, ...] = (
    "C:\\> ipconfig",
    "Carte Ethernet Ethernet :",
    "   Statut du média. . : Média déconnecté",
    "   Suffixe DNS. . . . :",
)

# =============================================================================================
# 8. Procédures et figures
# =============================================================================================

METHOD_STEPS: tuple[tuple[str, str], ...] = (
    ("Recueillir les faits", "Symptôme exact, depuis quand, portée, changements récents."),
    ("Reproduire et délimiter", "Compte de test, mode sans échec, autre programme."),
    ("Lire les journaux", "Observateur d'événements, Fiabilité ; journalctl, systemctl."),
    ("Protéger les données", "Sauvegarde vérifiée avant la première modification."),
    ("Corriger par étapes", "Du geste le moins invasif au plus invasif ; un seul à la fois."),
    ("Contrôler et rédiger", "Symptôme disparu, redémarrage, journaux ; rapport."),
)

PROCEDURES: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("Démarche de dépannage logiciel", METHOD_STEPS),
    ("Sauvegarder et vérifier avant d'intervenir", BACKUP_STEPS),
    ("Restaurer Windows à un point de restauration", RESTORE_STEPS),
    ("Windows ne démarre plus : de WinRE au démarrage normal", BOOT_STEPS),
    ("Service en échec sous Linux", LINUX_SERVICE_STEPS),
)


def _procedure_alt(intro: str, steps: tuple[tuple[str, str], ...]) -> str:
    return (
        f"{intro} {len(steps)} étapes reliées par des flèches : "
        + " ; ".join(f"{i} {label} : {detail}" for i, (label, detail) in enumerate(steps, start=1))
        + "."
    )


def _screen_alt(lines: tuple[str, ...]) -> str:
    return "Capture texte. " + " ; ".join(line.strip() for line in lines if line.strip()) + "."


METHOD_FIGURE = Figure(
    key="pr12-demarche",
    title="Procédure 1 — Démarche de dépannage logiciel",
    alt=_procedure_alt("Démarche générale de dépannage d'un problème logiciel.", METHOD_STEPS),
    caption=(
        "On comprend avant d'agir, on protège les données avant de modifier, et on corrige un "
        "geste à la fois pour savoir lequel a résolu la panne."
    ),
    svg=step_flow_svg(METHOD_STEPS),
)

ISOLATION_FIGURE = Figure(
    key="pr12-isoler",
    title="Arbre de décision — situer la cause d'une panne logicielle",
    alt=(
        "Arbre de décision en cinq questions. "
        + " ".join(f"Question {i} : {q} Si non : {n}" for i, (_k, q, n) in enumerate(ISOLATION_TREE, start=1))
        + f" Si toutes les réponses sont oui : {ISOLATION_FINAL}"
    ),
    caption=(
        "Le stockage passe en premier : un disque qui lâche impose de sauvegarder avant tout. "
        "Un service en panne se repère directement par son état. Convention du cours."
    ),
    svg=decision_tree_svg(tuple((q, n) for _k, q, n in ISOLATION_TREE), ISOLATION_FINAL),
)

LADDER_FIGURE = Figure(
    key="pr12-echelle",
    title="Échelle des interventions : effet sur les données et précaution",
    alt=(
        f"Échelle de {len(LADDER)} marches, du geste le moins invasif au plus invasif. "
        + " ".join(
            f"Marche {i} : {s.name} ; fichiers {'conservés' if s.keeps_files else 'effacés'}, "
            f"programmes {'conservés' if s.keeps_programs else 'retirés'} ; précaution : {precaution_for(s)}."
            for i, s in enumerate(LADDER, start=1)
        )
    ),
    caption=(
        "On monte d'une marche seulement si la précédente n'a pas suffi. Plus on monte, plus il "
        "faut de garanties : sauvegarde vérifiée et accord écrit avant toute réinitialisation."
    ),
    svg=ladder_svg(LADDER),
)

BACKUP_FIGURE = Figure(
    key="pr12-sauvegarde",
    title="Procédure 2 — Sauvegarder et vérifier avant d'intervenir",
    alt=_procedure_alt("Sauvegarde préalable des données du client.", BACKUP_STEPS),
    caption=(
        "Une sauvegarde non vérifiée n'est pas une sauvegarde : on compare les empreintes et on "
        "ouvre quelques fichiers avant d'effacer quoi que ce soit."
    ),
    svg=step_flow_svg(BACKUP_STEPS),
)

RESTORE_FIGURE = Figure(
    key="pr12-restauration",
    title="Procédure 3 — Restaurer Windows à un point de restauration",
    alt=_procedure_alt("Restauration du système Windows.", RESTORE_STEPS),
    caption=(
        "La restauration du système ne touche pas aux documents, mais retire les programmes, "
        "pilotes et mises à jour installés après le point choisi."
    ),
    svg=step_flow_svg(RESTORE_STEPS),
)

BOOT_FIGURE = Figure(
    key="pr12-demarrage",
    title="Procédure 4 — Windows ne démarre plus : de WinRE au démarrage normal",
    alt=_procedure_alt("Dépannage d'un Windows qui ne démarre plus.", BOOT_STEPS),
    caption=(
        "Les outils sont essayés du moins invasif au plus invasif ; la réinitialisation n'est "
        "envisagée qu'après eux, avec sauvegarde et accord écrit."
    ),
    svg=step_flow_svg(BOOT_STEPS),
)

LINUX_SERVICE_FIGURE = Figure(
    key="pr12-service-linux",
    title="Procédure 5 — Service en échec sous Linux",
    alt=_procedure_alt("Remise en route d'un service systemd en échec.", LINUX_SERVICE_STEPS),
    caption=(
        "On teste la configuration avant de redémarrer le service : un redémarrage sur une "
        "configuration fausse échoue de nouveau."
    ),
    svg=step_flow_svg(LINUX_SERVICE_STEPS),
)

NETWORK_FIGURE = Figure(
    key="pr12-reseau",
    title="Arbre de décision — panne réseau logicielle ou physique ?",
    alt=(
        "Arbre de décision en cinq questions. "
        + " ".join(f"Question {i} : {q} Si non : {n}" for i, (q, n) in enumerate(NETWORK_TREE, start=1))
        + f" Si toutes les réponses sont oui : {NETWORK_FINAL}"
    ),
    caption=(
        "Seule la première question relève du matériel ; les suivantes de la configuration et "
        "des logiciels. On teste du plus proche au plus lointain."
    ),
    svg=decision_tree_svg(NETWORK_TREE, NETWORK_FINAL),
)

PROFILE_FIGURE = Figure(
    key="pr12-profil",
    title="Cas 3 — Profil temporaire : message et journal (fictif)",
    alt=_screen_alt(TEMP_PROFILE_SCREEN),
    caption=(
        "Windows n'a pas pu charger le profil de l'utilisatrice et en a ouvert un temporaire, "
        "vidé à la déconnexion : on n'y enregistre rien. Capture fictive."
    ),
    svg=screen_svg(TEMP_PROFILE_SCREEN, label=FICTIVE_LABEL),
)

NGINX_FIGURE = Figure(
    key="pr12-nginx",
    title="Cas 2 — Service web en échec et test de configuration (fictif)",
    alt=_screen_alt(NGINX_SCREEN),
    caption=(
        "Le service est en échec (failed) ; nginx -t désigne le fichier et la ligne fautifs. "
        "Capture fictive."
    ),
    svg=screen_svg(NGINX_SCREEN, label=FICTIVE_LABEL),
)

DISK_FIGURE = Figure(
    key="pr12-espace",
    title="Cas 5 — Partition racine pleine : df et du (fictif)",
    alt=_screen_alt(DISK_SCREEN),
    caption=(
        f"La racine est pleine ({df_use_percent(CASE5_USED_BEFORE, CASE5_AVAIL_BEFORE)} %) ; "
        "du montre que /var/log (journaux) occupe la plus grande place. Capture fictive."
    ),
    svg=screen_svg(DISK_SCREEN, label=FICTIVE_LABEL),
)

PR12_FIGURES: tuple[Figure, ...] = (
    METHOD_FIGURE,
    ISOLATION_FIGURE,
    BACKUP_FIGURE,
    LADDER_FIGURE,
    RESTORE_FIGURE,
    BOOT_FIGURE,
    PROFILE_FIGURE,
    LINUX_SERVICE_FIGURE,
    NGINX_FIGURE,
    DISK_FIGURE,
    NETWORK_FIGURE,
)

# =============================================================================================
# 9. Liste de contrôle
# =============================================================================================

# (point contrôlé, commande ou outil, résultat attendu)
CHECKLIST: tuple[tuple[str, str, str], ...] = (
    ("Symptôme", "Reproduction de l'action qui échouait", "Le problème ne se reproduit plus"),
    ("Redémarrage", "Deux démarrages complets", "Démarrage normal, sans réparation automatique"),
    ("Journaux", "Observateur d'événements ; journalctl -b -p err", "Plus de nouvelle erreur liée à la panne"),
    ("Intégrité", "sfc /scannow ; systemctl --failed", "Aucune violation d'intégrité ; aucun service en échec"),
    ("Données", "Ouverture de fichiers du client ; empreintes", "Fichiers présents et identiques à la sauvegarde"),
    ("Espace", "Paramètres → Stockage ; df -h", "Espace libre suffisant (repère du cours : 15 % au moins)"),
)
