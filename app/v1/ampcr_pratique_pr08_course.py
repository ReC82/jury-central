"""Cours PR08 « Installation complète de Windows — préparation et dépannage » — parcours AMPCR
pratique écrite (ticket #208).

Matière : intégralement celle du ticket #208 (procédure complète sur poste vierge : inventaire,
compatibilité avec la version visée, licence, sauvegarde, média USB, firmware UEFI, démarrage,
langue et édition, disque et partitions GPT/ESP, compte, réseau, mises à jour, pilotes,
activation, restauration, sécurité et validation ; variantes installation propre/migration,
stockage non détecté, échec de démarrage, pilotes manquants, partitionnement incorrect ; jamais
d'effacement sans autorisation ; cinq cas résolus, liste de contrôle et rapport d'intervention),
découpée en blocs titrés (le titre pilote le type de carte, `app.card_kind` : aucun titre de
bloc théorique ne contient « examen », « source », « ressource », « exemple », « exercice »,
« méthode », « piège », « attention », « transfert » ni « mémo » — donc pas « mémoire »).
Données et schémas : `app.v1.ampcr_pratique_pr08_figures` ; exercices et mini-examen :
`app.v1.ampcr_pratique_pr08_bank`. Mise en forme partagée avec les autres cours pratiques.
Le choix du système et les prérequis relèvent de PR07 (publié, lien) ; l'installation de Linux
(PR09), les comptes et commandes (PR10) et la restauration du système (PR12) ne sont pas publiés
à la rédaction : renvoi en texte seulement.
"""

from html import escape

from app.v1.ampcr_pratique_pr06_course import _exercise_card, _fig, _req
from app.v1.ampcr_pratique_pr08_bank import EXAM_ITEMS, EXAM_TOTAL_POINTS, PRACTICE_ITEMS
from app.v1.ampcr_pratique_pr08_figures import (
    CHECKLIST,
    DEVMGR_FIGURE,
    FINAL_FIGURE,
    INSTALLER_DISKS_FIGURE,
    INVENTORY_FIELDS,
    LAYOUT_FIGURE,
    LIC_DIGITAL,
    LIC_OEM,
    LIC_RETAIL,
    MBR_ERROR_FIGURE,
    MIGRATION_ITEMS,
    NO_DRIVE_FIGURE,
    NO_DRIVE_FIGURE_SCREEN,
    PART_DELETE,
    PART_KEEP,
    PART_STOP,
    PREP_FIGURE,
    PROCEDURES,
    REPORT_SECTIONS,
    SETUP_FIGURE,
    STANDARD_LAYOUT,
    TR_CATEGORIES,
    TROUBLES_BY_CATEGORY,
    VENDOR_IDS,
    WRITTEN_AT,
    activation_result,
)

PR08_TITLE = "Installation complète de Windows — préparation et dépannage"
PR08_SLUG = "ampcr-pratique-pr08"


def _exercises_html() -> str:
    return "\n\n".join(
        _exercise_card(i, item, anchor_prefix="pr08") for i, item in enumerate(PRACTICE_ITEMS, start=1)
    )


def _console(*lines: str) -> str:
    return f'<pre class="jc-pr-console" tabindex="0">{escape(chr(10).join(lines))}</pre>'


def _ex(*keys: str) -> str:
    """Renvoi texte vers les exercices corrigés liés à un chapitre (séquence « Exercices
    corrigés ») : pas de lien d'ancre, la page n'affiche qu'une séquence à la fois."""
    return ", ".join(f"**{key}**" for key in keys) + " (séquence « Exercices corrigés »)"


# --- Tableaux de données (générés depuis les données vérifiées) ------------------------------


def _inventory_table() -> str:
    rows = "\n".join(f"| **{field}** | {what} | {why} |" for field, what, why in INVENTORY_FIELDS)
    return "| Rubrique | Ce que l'on relève | Pourquoi |\n|---|---|---|\n" + rows


def _activation_table() -> str:
    cases = (
        (f"{LIC_OEM}, édition Famille", "Famille, même PC", activation_result(LIC_OEM, "Famille", "Famille", same_pc=True)),
        (f"{LIC_OEM}, édition Famille", "Professionnel, même PC", activation_result(LIC_OEM, "Famille", "Pro", same_pc=True)),
        (f"{LIC_OEM}, édition Professionnel", "Professionnel, autre PC", activation_result(LIC_OEM, "Pro", "Pro", same_pc=False)),
        (f"{LIC_RETAIL}, Professionnel", "Professionnel, nouveau PC, clé retirée de l'ancien",
         activation_result(LIC_RETAIL, "Pro", "Pro", same_pc=False, removed_from_old_pc=True)),
        (f"{LIC_DIGITAL}, Professionnel", "Professionnel, même matériel",
         activation_result(LIC_DIGITAL, "Pro", "Pro", same_pc=True)),
    )
    rows = "\n".join(f"| {lic} | {installed} | {result} ({why}) |" for lic, installed, (result, why) in cases)
    return "| Licence | Installation | Résultat |\n|---|---|---|\n" + rows


def _layout_table() -> str:
    rows = "\n".join(f"| **{p.name}** | {p.filesystem} | {p.size_label} | {p.role} |" for p in STANDARD_LAYOUT)
    return "| Partition | Système de fichiers | Taille indicative | Rôle |\n|---|---|---|---|\n" + rows


def _migration_table() -> str:
    rows = "\n".join(f"| **{item}** | {where} | {how} |" for item, where, how in MIGRATION_ITEMS)
    return "| Élément | Où le trouver | Comment le transférer |\n|---|---|---|\n" + rows


def _vendors_table() -> str:
    rows = "\n".join(f"| `VEN_{code}` | {name} |" for code, name in VENDOR_IDS.items())
    return "| Identifiant | Fabricant |\n|---|---|\n" + rows


def _troubles_tables() -> str:
    parts = []
    for number, category in enumerate(TR_CATEGORIES, start=1):
        rows = "\n".join(
            f"| {t.symptom} | {t.check} | {t.action} | {t.never} |" for t in TROUBLES_BY_CATEGORY[category]
        )
        parts.append(
            f"### 12.{number + 1} {category}\n\n"
            "| Symptôme | Vérifier | Agir | Ne jamais |\n|---|---|---|---|\n" + rows
        )
    return "\n\n".join(parts)


def _checklist_table() -> str:
    rows = "\n".join(f"| **{point}** | {where} | {expected} | ☐ |" for point, where, expected in CHECKLIST)
    return "| Point | Où / comment | Résultat attendu | Fait |\n|---|---|---|---|\n" + rows


def _report_list() -> str:
    return "\n".join(f"{i}. **{title}** : {content}" for i, (title, content) in enumerate(REPORT_SECTIONS, start=1))


def _procedures_list() -> str:
    return "\n".join(
        f"{i}. **{title}** ({len(steps)} étapes)" for i, (title, steps) in enumerate(PROCEDURES, start=1)
    )


# =============================================================================================
# Sections du cours (titre du bloc, Markdown / HTML)
# =============================================================================================


def _objectives() -> str:
    return f"""## Ce que tu sauras faire, par écrit

L'épreuve pratique AMPCR se passe **uniquement par écrit** (consignes officielles 2026-2027/1,
p. 3). On ne te demande pas d'installer Windows devant le jury, mais de **rédiger** une
installation complète et sûre, de **lire** les écrans et relevés d'une installation, et de
**dépanner** par écrit une installation qui échoue. Tu dois savoir :

1. **préparer** l'intervention : demande, **accord écrit**, **inventaire** du poste ;
2. **vérifier** la compatibilité avec la version visée et la disponibilité des **pilotes** ;
3. **choisir** l'édition qui correspond à la **licence** et prévoir l'**activation** ;
4. **sauvegarder** et choisir entre **installation propre**, **mise à niveau** et **migration** ;
5. **préparer** le **média USB** et les pilotes de stockage et de réseau ;
6. **régler** le firmware **UEFI** et **démarrer** sur la clé dans le bon mode ;
7. **conduire** l'installateur : langue, édition, **disque et partitions GPT/ESP** ;
8. **configurer** le compte, le réseau et la confidentialité ;
9. **finaliser** : pilotes, mises à jour, activation, sécurité, **restauration** ;
10. **dépanner** : stockage non détecté, échec de démarrage, partitionnement incorrect, pilotes
    manquants, activation ;
11. **contrôler** avec une **liste de contrôle** et **rédiger le rapport d'intervention**.

Ce cours contient **3 procédures illustrées** :

{_procedures_list()}

## Exigence officielle travaillée dans ce cours

{_req("AP-10")}

Le cours s'appuie aussi sur la protection des données du client vue en
[PR04](/uaa/ampcr-pratique-pr04) :

{_req("AP-C03")}

Le choix du système, de l'édition et la vérification des prérequis (UEFI, démarrage sécurisé,
TPM 2.0) sont expliqués en [PR07](/uaa/ampcr-pratique-pr07) ; les partitions, MBR/GPT et la
partition EFI en [PR05](/uaa/ampcr-pratique-pr05) ; les messages de démarrage et les écrans
d'arrêt en [PR11](/uaa/ampcr-pratique-pr11) ; le diagnostic d'un disque en
[PR06](/uaa/ampcr-pratique-pr06). L'installation de Linux (PR09), les comptes, pilotes et
commandes (PR10) et la restauration du système (PR12) font l'objet des cours suivants du
parcours.

## Lien avec la théorie

Les notions de base sont présentées dans la théorie AMPCR :
[MC07 BIOS, UEFI, POST et démarrage](/uaa/ampcr-mc07),
[MC08 Partitionnement, GPT/MBR et formatage](/uaa/ampcr-mc08),
[MC09 Installer Windows proprement](/uaa/ampcr-mc09),
[MC10 Windows : administration et commandes essentielles](/uaa/ampcr-mc10) et
[MC12 Pilotes, périphériques et logiciels](/uaa/ampcr-mc12). Ce cours-ci est **pratique** :
procédures rédigées, écrans à lire, pannes à résoudre et rapports, comme dans un dossier
d'examen.

## Comment travailler ce cours

Lis les chapitres dans l'ordre : chacun donne ses **objectifs**, la **théorie**, la
**procédure professionnelle** à rédiger, l'**erreur fréquente**, ce qu'on attend **à l'écrit**
et un **repère rapide**, avec un renvoi vers les exercices liés. Étudie ensuite les **cinq cas
résolus**, fais les **{len(PRACTICE_ITEMS)} exercices corrigés** (ici ou dans « S'entraîner »,
correction après envoi), puis passe le **mini-examen noté sur {EXAM_TOTAL_POINTS}** dans l'onglet
« Examen blanc ».

> **Important —** les captures, relevés et situations de ce cours sont des **supports fictifs**
> construits pour s'entraîner ; les libellés des écrans de l'installateur sont **approximatifs**
> et changent selon la version de Windows (rédaction : {WRITTEN_AT}) : la **documentation de
> Microsoft fait foi**. Aucun exercice n'est une question officielle ni une question déjà posée
> par le Jury. **Installer Windows efface les partitions choisies : jamais sans sauvegarde
> vérifiée et accord écrit du propriétaire.**
"""


def _prepare() -> str:
    return f"""**Objectifs** : recueillir la demande, obtenir l'autorisation et relever tout ce qui
décidera de l'installation, avant de toucher au poste.

## 1.1 La demande et l'accord écrit

- On note **ce que veut le client** (« un Windows propre », « garder mes logiciels », « passer à
  Windows 11 ») et **ce qu'il faut garder** (données, comptes, logiciels).
- Une installation propre **efface** les partitions du disque cible : il faut l'**accord écrit**
  du propriétaire (bon d'intervention signé, courriel), qui précise ce qui peut être effacé. Un
  « effacez tout » au téléphone ne suffit pas, surtout si le PC contient les données d'autres
  personnes.
- Les données du client sont **confidentielles** : on les copie, on ne les consulte pas.

## 1.2 La fiche d'inventaire

{_inventory_table()}

Outils (vus en [PR07](/uaa/ampcr-pratique-pr07)) : `msinfo32` (Informations système),
Gestion des disques, Gestionnaire de périphériques, `winver`, Paramètres → Système →
Activation ; l'étiquette et le numéro de série du boîtier.

**Procédure professionnelle (à rédiger)** : demande → accord écrit → fiche d'inventaire
complète → liste de ce qu'il faut sauvegarder et préparer.

**Erreur fréquente** : démarrer sur la clé « pour gagner du temps » avant d'avoir relevé
l'édition, la licence, le mode du contrôleur de stockage ou la présence d'un second disque.

**À l'écrit** : la **fiche** (rubrique — relevé) puis, pour chaque relevé important, **ce qu'il
change** à la préparation.

**Repère rapide** : **demande → accord écrit → inventaire**. Exercices liés : {_ex("E01", "E08")}.
"""


def _compatibility() -> str:
    return f"""**Objectifs** : vérifier que le poste peut recevoir la version visée, et que ses pilotes
existent pour cette version.

## 2.1 Comparer aux prérequis de la version visée

La démarche complète est en [PR07](/uaa/ampcr-pratique-pr07) : relever le processeur (64 bits,
liste de compatibilité), la mémoire, le stockage, le mode du firmware (UEFI), le démarrage
sécurisé et le TPM 2.0, puis comparer à la **page officielle de Microsoft** pour la version
visée. Trois verdicts : **compatible tel quel**, **compatible après réglages du firmware**,
**non compatible** (on ne contourne pas un blocage matériel).

## 2.2 Les pilotes du fabricant

- Sur le **site du fabricant** (page du modèle, numéro de série), on vérifie que des pilotes
  existent pour la version visée : **chipset**, **stockage** (Intel RST/VMD, RAID),
  **réseau** (Ethernet, Wi-Fi), **graphique**, et les outils propres au modèle.
- Le pilote de **stockage** et le pilote **réseau** sont les plus importants **avant**
  l'installation : sans eux, l'installateur peut ne voir **aucun disque** et Windows peut
  démarrer **sans réseau** (donc sans Windows Update).
- Un périphérique ancien (imprimante, scanner, carte d'acquisition) sans pilote pour la
  nouvelle version est un **frein à signaler au client** avant l'intervention.

**Procédure professionnelle (à rédiger)** : prérequis comparés à la page officielle → verdict →
liste des pilotes à télécharger (modèle, version) → périphériques sans pilote signalés.

**Erreur fréquente** : promettre « Windows 11 sans souci » sans avoir vérifié le mode du firmware
ni l'existence du pilote de l'imprimante du client.

**À l'écrit** : « critère — relevé — minimum — conforme ? », puis la **liste des pilotes**.

**Repère rapide** : **prérequis (PR07) + pilotes stockage et réseau d'abord**. Exercices liés :
{_ex("E08", "E11")}.
"""


def _licence() -> str:
    return f"""**Objectifs** : installer l'édition qui correspond à la licence pour que Windows s'active,
et ne jamais rendre un PC non activé.

## 3.1 Types de licences

- **OEM** (préinstallée) : vendue avec le PC ; sur les PC récents, la clé est **inscrite dans le
  firmware** et l'installateur la lit seul ; elle reste **liée à ce PC**.
- **Commerciale** : clé achetée ; **transférable** vers un autre PC si elle est retirée de
  l'ancien.
- **Licence numérique** : liée au matériel (par exemple après une mise à niveau) ; Windows se
  réactive seul sur le **même matériel**, avec la **même édition**.

## 3.2 L'édition doit être celle de la licence

Dans l'installateur, on saisit la clé ou on choisit **« Je n'ai pas de clé de produit »** ; on
choisit alors **l'édition de la licence** (Famille ou Professionnel). Une licence Famille
n'active **pas** une installation Professionnel.

{_activation_table()}

{_console(
    "C:\\> slmgr /xpr",
    "La machine est activée de manière permanente.",
    "",
    "PS C:\\> (Get-CimInstance SoftwareLicensingService).OA3xOriginalProductKey",
    "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX      (clé OEM lue dans le firmware)",
)}

*Relevés fictifs. Paramètres → Système → Activation indique l'état et l'édition.*

**Procédure professionnelle (à rédiger)** : relever l'édition et le type de licence → installer
la même édition → contrôler « Windows est activé » → en cas d'échec, utilitaire de résolution des
problèmes d'activation ou information du client.

**Erreur fréquente** : installer l'édition Professionnel « parce que c'est mieux » sur un PC à
licence Famille ; utiliser une clé trouvée sur Internet ou un « activateur » (illégal et
dangereux).

**À l'écrit** : **licence → édition installée → résultat** et la **correction** si besoin.

**Repère rapide** : **même édition que la licence · OEM liée au PC · commerciale transférable**.
Exercices liés : {_ex("E06")}.
"""


def _backup_and_strategy() -> str:
    return f"""**Objectifs** : protéger les données et choisir la démarche : installation propre, mise à
niveau sur place ou migration vers un autre PC.

## 4.1 Sauvegarde vérifiée

- On copie **sur un autre support** (disque externe, partage réseau) les **profils** (Documents,
  Bureau, Images, Téléchargements de **chaque** compte), les **dossiers hors profil**, le
  courrier local et les favoris.
- On **vérifie** la copie (nombre et taille des fichiers, ouverture de quelques fichiers) : une
  sauvegarde non vérifiée n'est pas une sauvegarde.
- On relève la **clé de récupération BitLocker** (ou du chiffrement de l'appareil) avant tout
  réglage du firmware.

## 4.2 Installation propre, mise à niveau ou migration

- **Mise à niveau sur place** : lancée depuis Windows ; garde fichiers, programmes et réglages ;
  seulement si le système est **sain**, de même architecture, et le PC compatible (arbre de
  décision en [PR07](/uaa/ampcr-pratique-pr07)).
- **Installation propre** : système neuf sur un disque cible effacé ; recommandée pour un
  système infecté ou instable, un nouveau disque, un changement d'architecture.
- **Migration** : installation propre (ou PC neuf), puis **transfert** des données et des
  réglages du client depuis l'ancien système.

{_migration_table()}

**Procédure professionnelle (à rédiger)** : sauvegarde vérifiée → choix justifié de la démarche
→ liste de ce qui sera migré et comment → contrôle avec le client.

**Erreur fréquente** : oublier un dossier hors profil (C:\\Compta), le second compte d'un PC
familial, ou une licence logicielle limitée à un poste.

**À l'écrit** : la **démarche choisie et sa raison**, puis la **liste de migration** (élément —
méthode — contrôle).

**Repère rapide** : **copie vérifiée · propre si doute · migration = tout ce que le client
utilise**. Exercices liés : {_ex("E07", "E14")}.
"""


def _media() -> str:
    return f"""**Objectifs** : préparer une clé d'installation fiable et les pilotes nécessaires.

## 5.1 La clé d'installation

- Source : **site de Microsoft** uniquement — **outil de création de support** (il prépare la
  clé) ou **image ISO** (dont on contrôle la somme SHA-256 avec celle publiée ;
  `Get-FileHash`, vu en [PR07](/uaa/ampcr-pratique-pr07)).
- Clé USB de **8 Go au moins**, **effacée** par l'opération (on sauvegarde son contenu avant).
- Avec **Rufus** : schéma de partition **GPT**, cible **UEFI** pour un PC UEFI. Une clé écrite en
  schéma MBR / cible BIOS ne démarre qu'en mode hérité.
- Le système de fichiers FAT32 limite un fichier à 4 Gio : l'outil de Microsoft et Rufus savent
  gérer une image plus grande.

## 5.2 Les pilotes à emporter

- **Stockage** : pilote du contrôleur Intel RST/VMD ou RAID, en version « à extraire » (dite
  **F6**), copié dans un dossier de la clé : il se charge par **« Charger un pilote »**.
- **Réseau** : pilote Ethernet et Wi-Fi du modèle, pour avoir Internet dès le premier démarrage.
- On les télécharge **chez le fabricant**, jamais dans un « pack de pilotes » d'un site inconnu.

**Procédure professionnelle (à rédiger)** : image officielle (somme contrôlée) → clé écrite en
GPT/UEFI → dossier des pilotes stockage et réseau → test de démarrage.

**Erreur fréquente** : image téléchargée sur un site de partage ; clé « BIOS ou UEFI-CSM » pour un
PC réglé en UEFI seul.

**À l'écrit** : la **source**, le **contrôle**, l'**outil et ses réglages**, les **pilotes
emportés**.

**Repère rapide** : **site officiel · somme contrôlée · GPT/UEFI · dossier F6 + réseau**.
Exercices liés : {_ex("E01", "E12")}.
"""


def _firmware_boot() -> str:
    return f"""**Objectifs** : régler le firmware et démarrer l'installateur dans le bon mode.

## 6.1 Réglages avant de démarrer

- **Mode UEFI** (CSM désactivé), **démarrage sécurisé** activé, **TPM 2.0** actif (puce, Intel
  PTT, AMD fTPM) : prérequis de Windows 11 (voir [PR07](/uaa/ampcr-pratique-pr07)).
- Noter le **mode du contrôleur de stockage** (AHCI, RAID, Intel VMD) : on **ne le change plus**
  une fois Windows installé, sinon écran d'arrêt `INACCESSIBLE_BOOT_DEVICE` (voir
  [PR11](/uaa/ampcr-pratique-pr11)).
- Sur un PC **à plusieurs disques**, débrancher les disques qui ne sont pas la cible : sinon
  l'installateur peut placer le chargeur dans une **partition système EFI** d'un autre disque
  (par exemple celle d'un ancien Windows).

## 6.2 Démarrer sur la clé

- **Menu de démarrage ponctuel** (touche selon le fabricant : souvent **F12**, F11, F8 ou
  Échap) : choisir l'entrée **« UEFI: »** de la clé. L'entrée sans « UEFI: » démarrerait en mode
  hérité et Windows serait installé sur un disque **MBR**.
- Une clé officielle démarre **avec** le démarrage sécurisé : on ne le désactive pas.
- Après la copie, l'installateur **redémarre** : si la clé passe avant le disque dans l'ordre de
  démarrage, l'installation recommence ; on retire la clé ou on met **« Windows Boot Manager »**
  en premier.

**Procédure professionnelle (à rédiger)** : firmware relevé et réglé (un réglage à la fois) →
disques non ciblés débranchés → menu de démarrage → entrée « UEFI: ».

**Erreur fréquente** : activer le CSM ou désactiver le démarrage sécurisé « pour que la clé
démarre », au lieu de réécrire la clé en GPT/UEFI.

**À l'écrit** : les **réglages** et l'**entrée choisie**, avec la raison.

**Repère rapide** : **UEFI + démarrage sécurisé + TPM · entrée « UEFI: » · mode du stockage
noté**. Exercices liés : {_ex("E02", "E12", "E13")}.
"""


def _installer() -> str:
    return f"""**Objectifs** : conduire l'installateur de Windows, écran par écran, en prenant les bonnes
décisions.

{_fig(PREP_FIGURE)}

{_fig(SETUP_FIGURE)}

## 7.1 Les écrans, dans l'ordre

1. **Langue, format régional, clavier** : par exemple français (Belgique) et clavier **belge
   (AZERTY)** ; un mauvais clavier fausse le mot de passe tapé plus tard.
2. **Clé de produit** : saisie, lue dans le firmware (OEM), ou **« Je n'ai pas de clé de
   produit »** (activation plus tard).
3. **Édition** : celle de la **licence** (chapitre 3).
4. **Conditions de licence** acceptées.
5. **Type d'installation** : pour une installation propre, **« Personnalisée »** (installer
   Windows uniquement) ; la **mise à niveau** se lance depuis Windows, pas depuis la clé.
6. **Emplacement** : choix du disque et des partitions (chapitre 8).
7. **Copie et redémarrages** automatiques.

Les libellés exacts changent selon la version de l'installateur ; **l'ordre des décisions**
reste le même.

**Procédure professionnelle (à rédiger)** : procédures 1 et 2 ci-dessus, avec pour chaque écran
le **choix fait** et sa **raison**.

**Erreur fréquente** : choisir l'édition « au hasard », ou chercher la mise à niveau dans
l'installateur démarré sur la clé.

**À l'écrit** : les écrans **dans l'ordre** et les **valeurs choisies** (langue, clavier,
édition, type).

**Repère rapide** : **langue → clé → édition → personnalisée → disque**. Exercices liés :
{_ex("E02", "E07")}.
"""


def _disk_partitions() -> str:
    return f"""**Objectifs** : identifier le disque cible, ne supprimer que ce qui est autorisé, et
obtenir la disposition GPT standard.

## 8.1 Identifier le disque cible

- L'installateur liste **Lecteur 0, Lecteur 1…** et leurs partitions avec leur **taille** : on
  identifie le disque cible **par sa taille** et son contenu (relevés de l'inventaire).
- Un second disque (données, sauvegarde) **ne se touche pas** ; mieux : on le débranche pendant
  l'installation.

{_fig(INSTALLER_DISKS_FIGURE)}

## 8.2 Supprimer seulement ce qui est autorisé

Règle de l'atelier pour chaque partition affichée :

- **{PART_DELETE}** — sur le **disque cible** seulement ;
- **{PART_KEEP}** — tout autre disque (données, disque USB de sauvegarde) ;
- **{PART_STOP}** — disque cible, mais sauvegarde non vérifiée ou accord non signé.

## 8.3 La disposition GPT standard

Sur un **espace non alloué**, en mode UEFI, l'installateur crée lui-même le style **GPT** et les
partitions :

{_layout_table()}

{_fig(LAYOUT_FIGURE)}

- « **Windows ne peut être installé que sur des disques GPT** » (systèmes EFI) : le disque est en
  **MBR**. Disque à effacer (autorisé) : supprimer ses partitions → espace non alloué → GPT
  automatique. Windows à garder sur ce disque : conversion `mbr2gpt` depuis ce Windows (voir
  [PR07](/uaa/ampcr-pratique-pr07)). On ne passe **pas** en mode hérité pour contourner le
  message.
- **Partition de données à garder sur le disque cible** : ne supprimer que les partitions de
  l'ancien système (EFI, MSR, Windows, Récupération) et installer dans l'espace libéré.
- Vérifier avec `diskpart` (invite ouverte par **Maj + F10** dans l'installateur) :
  `list disk` (astérisque dans la colonne GPT), `list volume` — **sans** `clean`, qui efface
  tout le disque sélectionné.

**Procédure professionnelle (à rédiger)** : identifier le disque (taille) → appliquer la règle de
suppression → sélectionner l'espace non alloué → vérifier après l'installation (Gestion des
disques : GPT, ESP sur le disque système).

**Erreur fréquente** : supprimer « toutes les partitions » des deux disques ; formater une
partition de données en croyant qu'elle est celle de Windows.

**À l'écrit** : **disque cible + raison**, **partitions supprimées**, **partitions conservées**.

**Repère rapide** : **taille → cible · supprimer seulement après accord · espace non alloué = GPT
automatique**. Exercices liés : {_ex("E05", "E10", "E13")}.
"""


def _oobe() -> str:
    return f"""**Objectifs** : terminer la configuration initiale (OOBE) avec un compte et un réseau
adaptés au client.

## 9.1 Les écrans de la configuration initiale

1. **Région** et **clavier** (on peut ajouter un second clavier).
2. **Réseau** : câble Ethernet ou Wi-Fi (nom et clé notés à l'inventaire). Windows 11 demande
   en général une connexion Internet pendant cette étape : c'est pourquoi le **pilote réseau**
   se prépare à l'avance.
3. **Nom du PC** (convention de l'entreprise ou du client).
4. **Compte** : pour l'édition **Famille**, un **compte Microsoft** est exigé ; en entreprise,
   l'édition Professionnel se configure **pour le travail ou l'établissement scolaire** (compte
   de l'organisation), ou rejoint le **domaine** après l'installation. C'est le **client** qui
   saisit son mot de passe.
5. **Code PIN** (Windows Hello) et questions de sécurité éventuelles.
6. **Paramètres de confidentialité** : on les **explique** au client et on choisit avec lui
   (localisation, données de diagnostic, publicité).

## 9.2 Comptes

- **Un compte par personne** ; le compte **administrateur** a un **mot de passe** ; on conseille
  un **compte standard** pour l'usage quotidien (détails des comptes en PR10, à venir).
- Jamais de compte administrateur partagé sans mot de passe.

**Procédure professionnelle (à rédiger)** : région et clavier → réseau → nom du PC → compte du
client (saisi par lui) → confidentialité expliquée.

**Erreur fréquente** : créer le compte avec l'adresse ou le mot de passe du technicien ;
accepter tous les paramètres de confidentialité sans en parler au client.

**À l'écrit** : chaque **choix** et **qui** le fait (client ou technicien).

**Repère rapide** : **réseau prêt · compte du client · administrateur protégé · confidentialité
expliquée**. Exercices liés : {_ex("E08", "E16")}.
"""


def _drivers_updates() -> str:
    return f"""**Objectifs** : obtenir un poste sans périphérique inconnu et à jour.

## 10.1 Pilotes

- **Ordre** : **chipset**, puis **stockage** et **réseau**, puis **graphique**, puis le reste
  (audio, lecteur d'empreintes, outils du fabricant).
- **Sources** : Windows Update (y compris **mises à jour facultatives** des pilotes) et **site du
  fabricant** du PC ou du composant. Si le réseau manque, on télécharge le pilote sur un **autre
  PC** et on le copie par **clé USB**.
- **Gestionnaire de périphériques** : un point d'exclamation (!) ou « Périphérique inconnu »
  signale un pilote manquant ; « **Carte graphique de base Microsoft** » = pilote graphique
  absent.
- **Identifier un matériel inconnu** : Propriétés → Détails → **ID du matériel** ;
  `VEN_xxxx` désigne le fabricant, `DEV_xxxx` le modèle.

{_vendors_table()}

## 10.2 Mises à jour

- **Windows Update** jusqu'à « **Vous êtes à jour** » (plusieurs redémarrages possibles), puis
  les mises à jour des applications.

**Procédure professionnelle (à rédiger)** : pilote réseau d'abord si nécessaire → Windows Update
→ pilotes du fabricant dans l'ordre → Gestionnaire de périphériques sans (!) → nouvelle
recherche de mises à jour.

**Erreur fréquente** : installer un « pack de pilotes » d'un site inconnu ; conclure à une panne
de la carte réseau alors qu'il manque seulement son pilote.

**À l'écrit** : le **matériel** (identifié par son ID), la **source** du pilote et l'**ordre**.

**Repère rapide** : **chipset → stockage/réseau → graphique · ID du matériel · « Vous êtes à
jour »**. Exercices liés : {_ex("E03", "E11")}.
"""


def _activation_security() -> str:
    return f"""**Objectifs** : rendre un poste activé, protégé et restaurable.

{_fig(FINAL_FIGURE)}

## 11.1 Activation

Paramètres → Système → **Activation** : « Windows est activé ». Sinon : vérifier l'**édition**
(chapitre 3), saisir la bonne clé ou lancer l'**utilitaire de résolution des problèmes
d'activation**, et informer le client si la licence ne suit pas le PC.

## 11.2 Sécurité

- **Sécurité Windows** : Microsoft Defender (antivirus) et **pare-feu** actifs.
- **Chiffrement** : BitLocker (Professionnel) ou chiffrement de l'appareil ; la **clé de
  récupération** est conservée **hors du PC** (compte du client, papier remis).
- **Comptes** : administrateur protégé, compte standard au quotidien.

## 11.3 Restauration

- **Données du client** restaurées depuis la sauvegarde et **vérifiées avec lui**.
- **Point de restauration** du poste propre (activer la **protection du système** sur C: si
  elle est désactivée), et/ou **lecteur de récupération** sur une clé dédiée : ils permettront
  de revenir à cet état (la restauration du système est détaillée en PR12, à venir).
- Un point de restauration **n'est pas une sauvegarde** des données du client.

**Procédure professionnelle (à rédiger)** : procédure 3 ci-dessus.

**Erreur fréquente** : rendre un PC « Windows n'est pas activé » ; chiffrer le disque sans remettre
la clé de récupération au client.

**À l'écrit** : l'**état** de chaque point (activé, Defender, pare-feu, chiffrement, clé
remise) et la **restauration** faite.

**Repère rapide** : **activé · Defender + pare-feu · clé de récupération remise · données
vérifiées · point de restauration**. Exercices liés : {_ex("E03", "E06", "E15")}.
"""


def _troubleshooting() -> str:
    return f"""**Objectifs** : diagnostiquer une installation qui échoue, par familles de pannes, sans
jamais effacer de données non autorisées.

## 12.1 L'installateur ne propose pas le bon disque

{_fig(NO_DRIVE_FIGURE)}

{_troubles_tables()}

**Procédure professionnelle (à rédiger)** : relever le **message exact** → famille de panne →
**vérification** → **action** → contrôle ; à chaque étape, se demander si l'action risque
d'effacer des données.

**Erreur fréquente** : conclure « disque en panne » quand le firmware le voit ; « réparer » en
désactivant le démarrage sécurisé ou en passant en mode hérité ; recommencer l'installation en
supprimant à nouveau les partitions.

**À l'écrit** : **symptôme → cause → vérification → action → ce qu'on ne fait pas**.

**Repère rapide** : **stockage · démarrage · partitions · pilotes · licence**. Exercices liés :
{_ex("E04", "E09", "E10", "E11", "E12", "E13")}.
"""


def _checklist_report() -> str:
    return f"""**Objectifs** : valider l'installation devant le client et laisser une trace écrite
complète.

## 13.1 Liste de contrôle finale

{_checklist_table()}

## 13.2 Rapport d'intervention

{_report_list()}

Le rapport ne contient **que ce qui a été fait et vérifié** ; on n'y écrit jamais de mot de
passe. Il est signé par le technicien et par le client.

**Procédure professionnelle (à rédiger)** : passer la liste de contrôle **avec le client** →
reporter chaque résultat → rédiger le rapport par rubriques → recommandations.

**Erreur fréquente** : rendre le PC « le client vérifiera » ; rapport réduit à « Windows
réinstallé ».

**À l'écrit** : la **liste** (point — outil — résultat) et le **rapport en rubriques**.

**Repère rapide** : **contrôler devant le client · rubriques · recommandations · signatures**.
Exercices liés : {_ex("E15", "E16")}.
"""


def _examples() -> str:
    return f"""## Cas 1 — Installation propre complète avec migration des données

**Situation.** Un comptable indépendant fait réinstaller son PC de bureau (Windows 11
Professionnel, licence numérique, SSD 500 Go, firmware UEFI, TPM 2.0), devenu instable. Il veut
retrouver ses dossiers (dont C:\\Clients, hors profil), son courrier en fichier local (.pst) et
son logiciel de comptabilité (clé, licence pour un seul poste).

**Résolution.**

1. **Demande et accord** : installation propre (système instable), accord écrit signé.
2. **Inventaire** : Professionnel, licence numérique, contrôleur en AHCI, un seul disque.
3. **Sauvegarde** : profil, C:\\Clients et le fichier .pst sur disque externe, copie vérifiée ;
   clé du logiciel relevée et licence désactivée dans le logiciel.
4. **Média** : outil de création de Microsoft, clé de 16 Go ; pilote réseau du modèle copié.
5. **Installation** : entrée « UEFI: » ; clé non saisie (« Je n'ai pas de clé ») ; édition
   **Professionnel** (celle de la licence) ; « Personnalisée » ; suppression des quatre
   partitions du SSD ; espace non alloué sélectionné.
6. **Configuration** : région et clavier belges, réseau, compte saisi par le client.
7. **Finalisation** : pilotes, Windows Update, « Windows est activé » (licence numérique, même
   matériel), Defender et pare-feu, BitLocker avec clé remise sur papier.
8. **Migration** : fichiers restaurés, .pst importé, logiciel réinstallé et réactivé, imprimante
   testée ; point de restauration.

**Conclusion rédigée.** « Windows 11 Professionnel réinstallé proprement (accord du 03/10),
activé automatiquement ; données, courrier et comptabilité migrés et vérifiés avec le client ;
BitLocker actif, clé remise. »

## Cas 2 — Stockage non détecté

**Situation.** Sur un portable neuf livré sans système, l'installateur affiche :

{_fig(NO_DRIVE_FIGURE_SCREEN)}

**Résolution.**

1. Le **firmware voit le SSD** : il n'est pas en panne.
2. **Intel VMD activé** : l'installateur n'a pas le pilote du contrôleur.
3. Sur un autre PC, **pilote Intel RST/VMD** du fabricant du portable, version « F6 », copié sur
   la clé.
4. **« Charger un pilote »** → dossier → contrôleur : le SSD apparaît ; installation poursuivie.
5. Le **mode du contrôleur n'est plus modifié** ensuite ; il est noté dans le rapport.

**Conclusion rédigée.** « Aucun lecteur : contrôleur Intel VMD sans pilote dans l'installateur ;
pilote du fabricant chargé, SSD détecté, installation réalisée ; SSD sain. »

## Cas 3 — Échec de démarrage après l'installation

**Situation.** Windows 11 a été installé hier sur le SSD neuf d'une tour ; l'ancien disque dur
(disque 0), qui portait l'ancien Windows et garde des données, est resté branché. Le client a
retiré le disque dur : « Aucun périphérique de démarrage ».

**Résolution.**

1. **Disque remis** : le PC redémarre ; **Gestion des disques** montre la partition système EFI
   sur le **disque 0** (disque dur) et Windows sur le SSD.
2. Cause : l'installateur a **réutilisé la partition EFI existante** de l'ancien disque pour y
   placer le **chargeur**.
3. Installation d'hier, sans données : **réinstallation avec le SSD seul branché**, plus sûre
   qu'une réparation du démarrage (vue en PR11).
4. Contrôle : ESP, Windows et Récupération sur le SSD ; le disque dur est rebranché ensuite ;
   son ancienne partition EFI ne sert plus, mais on n'y supprime rien sans l'accord du client.

**Conclusion rédigée.** « Démarrage impossible sans le disque dur : le chargeur avait été placé
dans la partition EFI de ce disque lors de l'installation. Réinstallation avec le SSD seul ; démarrage contrôlé avec et sans
disque dur. »

## Cas 4 — Pilotes manquants après l'installation

**Situation.** Après l'installation sur un PC de bureau, pas de réseau, affichage en basse
résolution :

{_fig(DEVMGR_FIGURE)}

**Résolution.**

1. **(!)** = pilotes manquants ; **Carte graphique de base Microsoft** = pilote graphique absent.
2. **ID du matériel** : `VEN_10EC` = {VENDOR_IDS["10EC"]} (Ethernet), `VEN_8086` =
   {VENDOR_IDS["8086"]} (contrôleur de réseau Wi-Fi).
3. Sur le PC de l'atelier : pilote **réseau** du fabricant de la carte mère, copié par clé,
   installé → réseau rétabli.
4. **Windows Update** (mises à jour facultatives des pilotes), puis pilotes **chipset** et
   **graphique** du fabricant.
5. Contrôle : plus de (!), résolution native, « Vous êtes à jour ».

**Conclusion rédigée.** « Pilotes réseau (Realtek, Intel) installés depuis le site du fabricant,
puis Windows Update et pilote graphique ; aucun périphérique inconnu. »

## Cas 5 — Partitionnement incorrect : disque MBR avec une partition de données

**Situation.** Une graphiste veut Windows 11 propre sur son PC (UEFI, TPM 2.0). Son disque unique
contient un ancien Windows 10 démarré en mode hérité et une partition D: de 300 Go de projets à
garder. L'installateur affiche :

{_fig(MBR_ERROR_FIGURE)}

**Résolution.**

1. **Lecture** : disque 0 en **MBR** (pas d'astérisque) ; en UEFI, Windows ne s'installe que sur
   GPT. Le disque 1 (14 Go) est la clé.
2. **Sauvegarde vérifiée de D:** sur un disque externe, quoi qu'il arrive.
3. **Conversion sans effacer D:** : retour sur l'ancien Windows 10 ;
   `mbr2gpt /validate /allowFullOS` réussit, puis `mbr2gpt /convert /allowFullOS`.
4. **Installation** : entrée « UEFI: » ; suppression des **seules** partitions de l'ancien
   système (après accord écrit) ; installation dans l'espace libéré ; **D: intacte**.
5. **Contrôle** : msinfo32 « UEFI », Gestion des disques « GPT », projets présents et ouverts
   avec la cliente.

**Conclusion rédigée.** « Disque MBR refusé en UEFI ; D: sauvegardée puis disque converti en GPT
par mbr2gpt ; seules les partitions de l'ancien système supprimées ; Windows 11 installé, D:
intacte et vérifiée. » Si `mbr2gpt` avait échoué : sauvegarde de D: restaurée après suppression
de toutes les partitions, toujours avec l'accord écrit.
"""


def _pitfalls() -> str:
    return """> **Effacer sans accord écrit** ni sauvegarde vérifiée, sur la foi d'un « effacez tout » au
> téléphone.

> **Supprimer les partitions de tous les disques** au lieu du seul disque cible ; formater la
> partition de données.

> **Installer une autre édition que celle de la licence** et rendre un PC non activé ; utiliser
> un activateur ou une clé trouvée sur Internet.

> **Utiliser une image non officielle** ou une clé écrite pour le mode hérité.

> **Désactiver le démarrage sécurisé ou activer le CSM** pour « faire démarrer la clé » ou
> contourner le message GPT.

> **Conclure « SSD en panne »** quand l'installateur ne voit aucun lecteur alors que le firmware
> le voit : il manque le pilote de stockage.

> **Changer le mode du contrôleur (RAID/VMD ↔ AHCI)** après l'installation :
> INACCESSIBLE_BOOT_DEVICE.

> **Laisser un second disque branché** : le chargeur peut se retrouver dans sa partition EFI.

> **Supprimer à nouveau les partitions** quand l'installation recommence : c'est l'ordre de
> démarrage.

> **Installer un « pack de pilotes »** d'un site inconnu.

> **Créer le compte avec les identifiants du technicien**, ou un administrateur sans mot de passe.

> **Rendre le PC sans liste de contrôle** ni rapport, ou sans remettre la clé de récupération.
"""


def _exercises_intro() -> str:
    return f"""{len(PRACTICE_ITEMS)} exercices corrigés : remises en ordre (préparation, installation,
finalisation), classements (symptôme → cause, partitions à supprimer ou non, activation, avant /
pendant / après), fiche d'inventaire, écrans de l'installateur, ID du matériel, clé
d'installation, PC à deux disques, migration, rapport et procédure à corriger. Rédige ta réponse
sur papier **avant** d'ouvrir le corrigé ; toute réponse équivalente et justifiée est acceptée.
Ces mêmes exercices sont proposés dans [S'entraîner](/uaa/{PR08_SLUG}/practice), avec
correction après envoi.

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
    return f"""Le mini-examen se passe dans l'onglet [Examen blanc](/uaa/{PR08_SLUG}/exam) : **10 questions à réponse
libre**, chacune notée sur **2 points**, soit une note sur **{EXAM_TOTAL_POINTS}**. Les
questions ne figurent pas dans ce cours.

| N° | Thème | Type | Points |
|---|---|---|---|
{rows}

**Déroulement.** Chaque question est une situation complète : toutes les informations
nécessaires sont dans l'énoncé et ses documents (fiches, captures fictives).
**Aucune correction n'est visible pendant la passation** ; tes réponses sont enregistrées au
fur et à mesure. Après l'envoi, chaque réponse est corrigée selon le **barème analytique** de la
question (critères et points), puis tu vois ta note sur {EXAM_TOTAL_POINTS}, le corrigé et le
barème.

**Ce que valorise le barème.** La **lecture correcte** des écrans, la **cause** identifiée,
l'**ordre** des opérations et les **précautions** (accord écrit, sauvegarde vérifiée, disque
cible, édition de la licence) — pas la récitation de sigles. Une autre formulation juste est
acceptée.

**Nature de la correction.** Les réponses rédigées reçoivent une **proposition de correction
automatique** (assistée par IA) appuyée sur le barème : c'est un repère d'entraînement, pas une
note officielle ; en cas de doute, compare ta réponse au corrigé.
"""


def _memo() -> str:
    return """## Mémo

- **Avant tout** : demande, **accord écrit**, **inventaire** (modèle, édition et licence,
  disques, firmware, mode du stockage, réseau).
- **Compatibilité** : prérequis de la version visée (PR07) ; pilotes stockage et réseau
  disponibles.
- **Licence** : installer **l'édition de la licence** ; OEM et numérique liées au PC ;
  commerciale transférable ; « Je n'ai pas de clé » possible.
- **Sauvegarde** : profils de tous les comptes + dossiers hors profil + courrier + favoris ;
  **copie vérifiée** ; clé BitLocker relevée.
- **Démarche** : mise à niveau seulement si sain et compatible ; sinon installation propre ;
  migration = transférer tout ce que le client utilise.
- **Média** : site de Microsoft, somme contrôlée, clé ≥ 8 Go, **GPT/UEFI** ; dossier **F6**
  (stockage) et pilote réseau.
- **Firmware** : UEFI, démarrage sécurisé, TPM 2.0 ; mode du stockage **noté et plus modifié** ;
  autres disques débranchés.
- **Démarrage** : menu (F12, F11, F8, Échap) → entrée **« UEFI: »** ; installation qui recommence
  → retirer la clé.
- **Installateur** : langue → clavier → clé → édition → **Personnalisée** → disque.
- **Partitions** : disque cible identifié par sa **taille** ; supprimer seulement après accord ;
  espace non alloué → **ESP, MSR, Windows, Récupération** en GPT.
- **Message GPT** : disque MBR → supprimer (autorisé) ou `mbr2gpt` (Windows à garder) ; jamais
  le mode hérité.
- **Aucun lecteur** : firmware le voit ? → pilote VMD/RST par « Charger un pilote ».
- **Après** : pilotes (chipset → réseau → graphique), Windows Update, activation, Defender et
  pare-feu, chiffrement + clé, compte standard, données restaurées, point de restauration.
- **Contrôle** : liste de contrôle avec le client ; **rapport** en rubriques, signé.

## Glossaire des termes employés

- **Activation** : vérification par Microsoft que la licence correspond à l'installation.
- **Espace non alloué** : partie du disque sans partition, où l'installateur crée les siennes.
- **ESP (partition système EFI)** : petite partition FAT32 qui contient le chargeur de
  démarrage lu par l'UEFI.
- **F6 (pilote)** : pilote de stockage fourni en fichiers à charger pendant l'installation.
- **ID du matériel** : identifiant d'un périphérique (VEN = fabricant, DEV = modèle).
- **Installation personnalisée** : installation propre, sur un emplacement choisi.
- **Licence OEM** : licence vendue avec le PC et liée à lui.
- **Migration** : transfert des données et réglages d'un ancien système vers un nouveau.
- **MSR** : petite partition réservée par Windows sur un disque GPT.
- **OOBE** : configuration initiale de Windows au premier démarrage (région, réseau, compte).
- **Point de restauration** : état enregistré des fichiers système, pour revenir en arrière.
- **VMD / RST** : technologies Intel de gestion du stockage qui demandent leur propre pilote.
- **WinRE** : environnement de récupération de Windows, sur la partition Récupération.
"""


def _sources() -> str:
    return f"""## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), pp. 3 et 5 : épreuve uniquement écrite, exigence AP-10
  « Installation complète des différents systèmes d'exploitation courants ». Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
  Programme officiel n° 345/2007/249 (option AMPCR).
- **Windows** : documentation Microsoft (créer un support d'installation, configuration requise de
  Windows 11, partitions de disque dur UEFI/GPT, MBR2GPT, chargement d'un pilote de stockage
  pendant l'installation, activation et licences numériques, Windows Update, BitLocker et
  chiffrement de l'appareil, protection du système et lecteur de récupération, `slmgr`,
  `diskpart`, code d'arrêt INACCESSIBLE_BOOT_DEVICE).
- **Fabricants** : notices et pages de pilotes (Intel Rapid Storage Technology / VMD) ; liste
  publique des identifiants de fabricants PCI (PCI-SIG) pour les codes VEN.
- **Outils** : documentation de Rufus (schéma de partition et système de destination).

Les écrans de l'installateur cités sont ceux de Windows 11 en {WRITTEN_AT} ; leurs libellés
changent avec les versions : la documentation de Microsoft fait foi le jour de l'intervention.
Les procédures, la disposition des partitions, la règle de suppression, les résultats
d'activation, le tableau de dépannage, l'arbre de décision et la liste de contrôle du cours sont
**produits par programme** depuis des données **vérifiées par des tests automatiques** ; aucun
schéma n'est tiré d'une image générée ni d'une photographie.

## Compléments pédagogiques (non imposés par la liste officielle)

La liste des pp. 5-6 cite l'installation complète des systèmes courants (AP-10). Sont des
**compléments**, signalés comme tels, utiles pour traiter un dossier écrit :

- la protection des données et l'accord écrit (AP-C03, complément du parcours, repris de PR04) ;
- l'activation et les licences, la migration des données ;
- le dépannage de l'installation par familles de pannes et l'identification des pilotes ;
- la liste de contrôle et le plan du rapport d'intervention : ce sont des **conventions du
  cours**, pas une norme.

## Supports fictifs

Les captures, relevés et situations de ce cours sont **fictifs** et reconstitués pour
l'entraînement ; ils ne décrivent aucun client réel. Aucun n'est une question officielle ou
déjà posée par le Jury.
"""


def pr08_course_sections() -> list[tuple[str, str]]:
    """Blocs du cours (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("PR08 — Objectifs et place dans l'épreuve", _objectives()),
        ("PR08 — 1. Préparer l'intervention : demande, accord écrit et inventaire", _prepare()),
        ("PR08 — 2. Compatibilité avec la version visée et pilotes du fabricant", _compatibility()),
        ("PR08 — 3. Licence, édition et activation", _licence()),
        ("PR08 — 4. Sauvegarde ; installation propre, mise à niveau ou migration", _backup_and_strategy()),
        ("PR08 — 5. Média USB d'installation et pilotes à emporter", _media()),
        ("PR08 — 6. Firmware UEFI et démarrage sur la clé", _firmware_boot()),
        ("PR08 — 7. L'installateur : langue, clé, édition, type d'installation", _installer()),
        ("PR08 — 8. Disque et partitions : GPT, ESP, choix du disque cible", _disk_partitions()),
        ("PR08 — 9. Configuration initiale : réseau, compte, confidentialité", _oobe()),
        ("PR08 — 10. Pilotes et mises à jour", _drivers_updates()),
        ("PR08 — 11. Activation, sécurité et restauration", _activation_security()),
        ("PR08 — 12. Dépannage de l'installation : cinq familles de pannes", _troubleshooting()),
        ("PR08 — 13. Liste de contrôle finale et rapport d'intervention", _checklist_report()),
        ("PR08 — Exemples : cinq cas résolus", _examples()),
        ("PR08 — Pièges et erreurs fréquentes", _pitfalls()),
        (f"PR08 — Exercices corrigés ({len(PRACTICE_ITEMS)}) et leurs corrigés", _exercises_intro()),
        ("PR08 — Mini-examen noté sur 20 : mode d'emploi", _mini_exam()),
        ("PR08 — Fiche mémo et glossaire", _memo()),
        ("PR08 — Sources et compléments pédagogiques", _sources()),
    ]
