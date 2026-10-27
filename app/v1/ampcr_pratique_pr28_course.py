"""Cours PR28 « Outillage, sécurité et protection des données » — parcours AMPCR pratique écrite
(ticket #227).

Matière : intégralement celle du ticket #227 (inventaire des outils PC : tournevis, pinces,
bracelet et tapis ESD selon la procédure, testeur d'alimentation autorisé, multimètre avec
précautions, pâte thermique, outils de nettoyage ; outils réseau : sertisseuse 8P8C, dénudeur,
outil d'insertion, testeur wiremap, outils coaxiaux BNC, fibre et sécurité laser ; ESD,
électricité, bloc jamais ouvert, batteries endommagées, ventilation, risques mécaniques, poste
de travail, débranchement ; sauvegarde 3-2-1 comme complément, intégrité et confidentialité,
chiffrement et droits, données du client, autorisation avant effacement ou réinstallation,
déchets DEEE ; fiches sécurité, choix d'outil selon l'intervention, gestion d'incident ; cinq cas
résolus, exercices corrigés, mini-examen, listes de contrôle et illustrations sûres), découpée en
blocs titrés (le titre pilote le type de carte, `app.card_kind` : aucun titre de bloc théorique
ne contient « examen », « source », « ressource », « exemple », « exercice », « méthode »,
« piège », « attention », « transfert » ni « mémo »).
Règles, procédures et schémas : `app.v1.ampcr_pratique_pr28_figures` ; exercices et
mini-examen : `app.v1.ampcr_pratique_pr28_bank`. Le cours renvoie aux cours publiés qui
détaillent chaque geste technique (PR02, PR03, PR04, PR05, PR12, PR15, PR16, PR17, PR18) et à
PR26 / PR27 pour la demande, le diagnostic et l'escalade.
"""

from html import escape

from app.v1.ampcr_pratique_pr02_figures import RAILS, tolerance_range, volts
from app.v1.ampcr_pratique_pr06_course import _exercise_card, _fig, _req
from app.v1.ampcr_pratique_pr28_bank import EXAM_ITEMS, EXAM_TOTAL_POINTS, PRACTICE_ITEMS
from app.v1.ampcr_pratique_pr28_figures import (
    AUTH_FIGURE,
    BATTERY_FIGURE,
    CASES,
    CHECKLIST,
    CHECKLIST_FIGURE,
    CLEAN_FIGURE,
    DISCONNECT_FIGURE,
    ESD_FIGURE,
    FIBRE_FIGURE,
    INCIDENT_FIGURE,
    INCIDENT_TREE,
    INCIDENT_TREE_FIGURE,
    INTERVENTIONS,
    MISS_1,
    MISS_2,
    MISS_3,
    MULTIMETER_FIGURE,
    NET_TOOLS_FIGURE,
    OPERATIONS,
    PC_TOOLS_FIGURE,
    PREREQUISITES,
    PROCEDURES,
    RISKS,
    RISKS_BY_KEY,
    RULE321_FIGURE,
    SAFETY_SHEET_FIELDS,
    STATIC_FIGURES,
    SUPPORT_TYPES,
    WASTE_FIGURE,
    WASTE_ITEMS,
    WRITTEN_AT,
    Case,
    kit,
    required_prerequisites,
    waste_route,
)
from app.v1.ampcr_pratique_visuals import render_figure

PR28_TITLE = "Outillage, sécurité et protection des données"
PR28_SLUG = "ampcr-pratique-pr28"

_SCHEMAS_BY_PATH = {path: figure for figure, path in STATIC_FIGURES}


def _card(number: int, item) -> str:
    """Carte d'exercice de PR06 ; un schéma à compléter est affiché (SVG) avant sa
    description textuelle."""
    html = _exercise_card(number, item, anchor_prefix="pr28")
    for document in item.documents:
        if document.image:
            text = f'<p class="jc-pr-doc-text">{escape(document.content_text)}</p>'
            figure = str(render_figure(_SCHEMAS_BY_PATH[document.image]))
            html = html.replace(text, figure + text, 1)
    return html


def _exercises_html() -> str:
    return "\n\n".join(_card(i, item) for i, item in enumerate(PRACTICE_ITEMS, start=1))


def _ex(*keys: str) -> str:
    """Renvoi texte vers les exercices corrigés liés à un chapitre (séquence « Exercices
    corrigés ») : pas de lien d'ancre, la page n'affiche qu'une séquence à la fois."""
    return ", ".join(f"**{key}**" for key in keys) + " (séquence « Exercices corrigés »)"


def _html_table(header: tuple[str, ...], rows: list[tuple[str, ...]], *, caption: str = "") -> str:
    head = "".join(f'<th scope="col">{escape(c)}</th>' for c in header)
    body = "".join("<tr>" + "".join(f"<td>{escape(c)}</td>" for c in row) + "</tr>" for row in rows)
    cap = f"<caption>{escape(caption)}</caption>" if caption else ""
    return (
        '<div class="table-responsive"><table class="table table-sm jc-pr-doc-table">'
        f"{cap}<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"
    )


def _procedures_list() -> str:
    return "\n".join(
        f"{i}. **{title}** ({len(steps)} étapes)" for i, (title, steps) in enumerate(PROCEDURES, start=1)
    )


def _interventions_table() -> str:
    rows = [
        (i.title, ", ".join(t.name for t in kit(i)), ", ".join(RISKS_BY_KEY[k].name for k in i.risks))
        for i in INTERVENTIONS
    ]
    return _html_table(("Intervention", "Kit d'outils", "Risques principaux"), rows,
                       caption="Choisir le kit selon l'intervention (inventaire du cours)")


def _risks_table(keys: tuple[str, ...]) -> str:
    rows = [(r.name, r.danger, r.prevention, r.reaction) for r in RISKS if r.key in keys]
    return _html_table(("Risque", "Danger", "Prévention", "Si cela arrive"), rows)


def _rails_table() -> str:
    rows = []
    for r in RAILS:
        low, high = tolerance_range(r)
        rows.append((r.name, f"±{r.tolerance_pct} %", f"{volts(low)} à {volts(high)}"))
    return _html_table(("Tension", "Tolérance", "Plage admise"), rows,
                       caption="Tolérances du bloc ATX (rappel de PR02)")


def _prereq_table() -> str:
    rows = []
    for op in OPERATIONS:
        need = required_prerequisites(op, keep_data=True, encrypted=True)
        rows.append((op, *("oui" if p in need else "—" for p in PREREQUISITES)))
    short = ("Sauvegarde vérifiée", "Accord écrit précis", "Personne habilitée", "Clé de récupération", "Licences notées")
    return _html_table(("Opération", *short), rows,
                       caption="Prérequis avant une opération qui efface (données à garder, disque chiffré)")


def _waste_table() -> str:
    rows = [(item, kind, waste_route(kind)) for item, kind in WASTE_ITEMS]
    return _html_table(("Objet", "Nature", "Filière"), rows)


def _safety_sheet_table() -> str:
    battery = RISKS_BY_KEY["batt"]
    rows = [
        ("Intervention", "Prise en charge d'un portable dont la batterie est gonflée"),
        ("Risques", f"{battery.name} : {battery.danger}"),
        ("Protections et outils", "bac ininflammable, gants, ruban adhésif isolant ; aucun outil pour forcer le capot"),
        ("Avant", "chargeur débranché, appareil non rallumé, garantie vérifiée"),
        ("Pendant", "aucune pression ni perforation ; appareil isolé loin des matières combustibles"),
        ("Après", "client informé, fiche complétée, batterie dans la filière des piles et batteries"),
        ("En cas d'incident", battery.reaction),
    ]
    return _html_table(("Rubrique", "Contenu"), rows, caption="Fiche sécurité (modèle du cours, exemple rempli)")


# =============================================================================================
# Cinq interventions entièrement résolues
# =============================================================================================


def _bullets(lines: tuple[str, ...]) -> str:
    return "\n".join(f"- {line}" for line in lines)


def _case_html(number: int, c: Case) -> str:
    risks = ", ".join(RISKS_BY_KEY[k].name for k in c.risks) or "aucun risque physique : le risque porte sur les données"
    tools = ", ".join(t.name for t in c.tools) or "aucun outil : on ne démonte rien"
    return f"""## Intervention {number} — {c.theme} : {c.title}

**Situation.** {c.context}

**1. Risques identifiés.** {risks}.

**2. Outils choisis.** {tools}.

**3. Avant l'intervention.**

{_bullets(c.before)}

**4. Pendant.**

{_bullets(c.during)}

**5. Après.**

{_bullets(c.after)}

**6. Données du client.** {c.data}

**7. En cas d'incident.** {c.incident}

**Conclusion rédigée.** « {c.conclusion} »
"""


# =============================================================================================
# Sections du cours (titre du bloc, Markdown / HTML)
# =============================================================================================


def _objectives() -> str:
    return f"""## Ce que tu sauras faire, par écrit

L'épreuve pratique AMPCR se passe **uniquement par écrit** (consignes officielles 2026-2027/1,
p. 3). Dans tout dossier d'intervention, le correcteur attend les **précautions** : le bon outil,
la sécurité de la personne et du matériel, la protection des données du client. Tu dois savoir :

1. choisir l'**outil** adapté à chaque geste, PC et réseau, et donner sa **précaution** ;
2. nommer les **risques** d'une intervention (ESD, électricité, bloc d'alimentation, batteries
   endommagées, ventilation, risques mécaniques, laser et éclats de fibre, poste de travail) et
   leur **prévention** ;
3. **débrancher** un poste avant de l'ouvrir, dans le bon ordre ;
4. protéger les **données du client** : intégrité, confidentialité, chiffrement et droits ;
5. vérifier une **sauvegarde** (règle 3-2-1, en complément) et obtenir l'**autorisation** avant
   tout effacement ou réinstallation ;
6. diriger chaque **déchet** vers sa filière (DEEE, piles et batteries, supports de données) ;
7. rédiger une **fiche sécurité** et réagir à un **incident**.

Ce cours contient **{len(PROCEDURES)} procédures illustrées**, un **arbre d'incident** et une
**liste de contrôle** :

{_procedures_list()}

## Exigences travaillées dans ce cours

{_req("AP-C02")}
{_req("AP-C03")}

Ces deux points sont des **compléments** du parcours : la liste officielle des pp. 5-6 ne les
cite pas en toutes lettres, mais toute intervention écrite les exige. Le cours s'appuie aussi
sur des exigences **officielles** : {_req("AP-14")[2:]} (outillage et sécurité du démontage),
et {_req("AP-20")[2:]} (précautions d'utilisation des câbles et connecteurs).

## Lien avec la théorie et les autres cours

La théorie AMPCR présente la sécurité électrique et l'ESD ([MC05](/uaa/ampcr-mc05)), le montage
([MC06](/uaa/ampcr-mc06)) et la maintenance préventive avec les sauvegardes
([MC32](/uaa/ampcr-mc32)). Ce cours-ci est **pratique** : il rassemble les précautions qu'on
écrit dans un dossier. Le détail de chaque geste est dans les cours déjà publiés : bloc
d'alimentation et tolérances ([PR02](/uaa/ampcr-pratique-pr02)), montage
([PR03](/uaa/ampcr-pratique-pr03)), effacement sécurisé ([PR04](/uaa/ampcr-pratique-pr04)),
stockage ([PR05](/uaa/ampcr-pratique-pr05)), sauvegarde et restauration
([PR12](/uaa/ampcr-pratique-pr12)), RJ45 ([PR15](/uaa/ampcr-pratique-pr15)), BNC
([PR16](/uaa/ampcr-pratique-pr16)), fibre ([PR17](/uaa/ampcr-pratique-pr17)) et pose d'un réseau
([PR18](/uaa/ampcr-pratique-pr18)). La demande et l'escalade sont dans
[PR26](/uaa/ampcr-pratique-pr26), la procédure de diagnostic dans [PR27](/uaa/ampcr-pratique-pr27).

## Comment travailler ce cours

Lis les chapitres dans l'ordre : chacun donne ses **objectifs**, la **théorie**, la
**procédure professionnelle**, l'**erreur fréquente**, ce qu'on attend **à l'écrit** et un
**repère rapide**, avec un renvoi vers les exercices liés. Étudie ensuite les **cinq
interventions entièrement résolues**, fais les **{len(PRACTICE_ITEMS)} exercices corrigés** (dont
deux **schémas à compléter**), puis passe le **mini-examen noté sur {EXAM_TOTAL_POINTS}** dans
l'onglet « Examen blanc ».

> **Important —** les personnes, entreprises, fichiers et dossiers de ce cours sont des
> **supports fictifs** construits pour s'entraîner (rédaction : {WRITTEN_AT}). Les consignes
> de sécurité de ce cours sont des **règles générales de prudence** : la procédure de
> l'atelier, le manuel du fabricant et les consignes du site font foi. Les illustrations ne
> montrent aucun geste dangereux. Aucun exercice n'est une question officielle ni une question
> déjà posée par le Jury.
"""


def _pc_tools() -> str:
    return f"""**Objectifs** : connaître l'outillage du poste de travail, son usage et sa précaution ;
choisir le kit d'une intervention.

## 1.1 L'inventaire de l'outillage PC

{_fig(PC_TOOLS_FIGURE)}

- **Tournevis** : cruciformes de petites tailles (PH0 à PH2) et Torx pour certains boîtiers et
  portables. Un embout trop petit abîme la tête de vis ; les vis sont rangées dans un **bac à
  compartiments**, par étape, pour être remontées à leur place.
- **Pinces** (à bec fin, brucelles) : récupérer une vis tombée, saisir un petit connecteur. Jamais
  dans un appareil sous tension, jamais comme levier.
- **Bracelet et tapis antistatiques (ESD)** : ils évitent la décharge qui détruit une puce. On les
  installe **selon la procédure de l'atelier** (chapitre 3).
- **Testeur d'alimentation** : l'outil **autorisé** pour contrôler un bloc, par ses connecteurs,
  hors de la carte mère. Il travaille presque à vide : il ne prouve pas la tenue en charge.
- **Multimètre** : basses tensions continues (pile CMOS, sorties d'un bloc), continuité,
  résistance — avec ses précautions (1.2).
- **Pâte thermique** : après chaque démontage du radiateur, l'ancienne pâte est retirée à
  l'**alcool isopropylique** et une petite quantité de pâte neuve est appliquée.
- **Nettoyage** : air sec, pinceau antistatique, chiffon microfibre — ventilateurs bloqués, pas
  d'aspirateur domestique (chapitre 4).

## 1.2 Le multimètre sans danger

{_fig(MULTIMETER_FIGURE)}

Pour une pile bouton CR2032, la tension nominale est de **3 V** : une pile neuve donne un peu
plus, une pile nettement en dessous est usée (l'horloge se dérègle à chaque coupure).

## 1.3 Le testeur d'alimentation et les tolérances

Le testeur affiche chaque tension du bloc. On compare aux **tolérances ATX** vues en
[PR02](/uaa/ampcr-pratique-pr02) : une tension hors de sa plage = bloc à remplacer, **jamais à
ouvrir**.

{_rails_table()}

**Procédure professionnelle** : choisir le kit **avant** de partir (tableau du chapitre 8),
contrôler chaque outil (piles du testeur, cordons du multimètre, bracelet), ranger les vis par
étape.

**Erreur fréquente** : garder le réglage du multimètre laissé par un collègue ; ouvrir le bloc
« pour voir » ; un tournevis trop petit qui arrondit la tête de vis.

**À l'écrit** : « Outils : tournevis PH2, bracelet relié au tapis, multimètre en tension continue
calibre 20 V, cordon noir sur COM. Mesure de la pile retirée : 2,4 V, nettement sous 3 V : pile
usée. »

**Repère rapide** : **un outil par geste · sa précaution · multimètre jamais sur le 230 V ·
bloc testé, jamais ouvert**. Exercices liés : {_ex("E01", "E05", "E06", "E07")}.
"""


def _net_tools() -> str:
    return f"""**Objectifs** : connaître l'outillage du câblage cuivre, coaxial et optique ; appliquer
la sécurité laser et éclats de fibre.

## 2.1 L'inventaire de l'outillage réseau

{_fig(NET_TOOLS_FIGURE)}

- **Dénudeur** : retire la gaine sans entailler les conducteurs ; profondeur réglée sur une chute.
- **Sertisseuse 8P8C** : fixe une fiche RJ45 ; fiche adaptée au câble (monobrin ou multibrin,
  catégorie), ordre T568A ou T568B identique aux deux bouts ([PR15](/uaa/ampcr-pratique-pr15)).
- **Outil d'insertion (punch-down)** : enfonce les fils dans les contacts autodénudants d'une
  prise murale ou d'un panneau de brassage ; lame **110** ou **LSA** selon le bloc, côté coupant
  vers la chute ([PR18](/uaa/ampcr-pratique-pr18)).
- **Testeur de câble (wiremap)** : coupure, court-circuit, inversion, croisement. Il ne se branche
  **jamais sur un port actif** (switch PoE, ligne téléphonique) et ne remplace pas une
  certification.
- **Pince à sertir BNC et dénudeur coaxial** : matrice adaptée au câble (RG58 ou RG59), cotes
  du fabricant ([PR16](/uaa/ampcr-pratique-pr16)).
- **Kit de nettoyage fibre** et **localisateur visuel** (stylo laser rouge) : chaque férule est
  nettoyée avant d'être emboîtée ([PR17](/uaa/ampcr-pratique-pr17)).

## 2.2 Sécurité laser et éclats de fibre

{_fig(FIBRE_FIGURE)}

{_risks_table(("laser",))}

**Procédure professionnelle** : annoncer la coupure du lien, éteindre ou débrancher, travailler
avec les capuchons, nettoyer, rebrancher, contrôler par les voyants ou un appareil de mesure.

**Erreur fréquente** : « je ne vois pas de lumière, donc il n'y a pas de laser » — la lumière
des modules est souvent **infrarouge, invisible** ; brancher le testeur de câble sur un port PoE.

**À l'écrit** : « Je débranche la jarretière, je ne regarde jamais l'extrémité ; férules
nettoyées au stylo de nettoyage, capuchons remis ; lien contrôlé aux voyants du switch. »

**Repère rapide** : **dénudeur réglé · bonne lame · testeur jamais sur un port actif · fibre
jamais regardée en face · éclats en récipient fermé**. Exercices liés : {_ex("E01", "E09", "E10")}.
"""


def _electric() -> str:
    return f"""**Objectifs** : débrancher un poste dans le bon ordre ; installer la protection
antistatique selon la procédure ; ne jamais ouvrir un bloc d'alimentation.

## 3.1 Électricité et bloc d'alimentation

{_risks_table(("elec", "psu"))}

Le **secteur 230 V** est mortel. Un PC débranché garde des charges dans ses condensateurs ; ceux
du **bloc d'alimentation** restent chargés longtemps à une tension dangereuse : **on n'ouvre
jamais un bloc**, ni pour le nettoyer ni pour le réparer ([PR02](/uaa/ampcr-pratique-pr02)).

## 3.2 Débrancher avant d'intervenir

{_fig(DISCONNECT_FIGURE)}

## 3.3 La protection antistatique (ESD)

{_fig(ESD_FIGURE)}

{_risks_table(("esd",))}

**Selon la procédure de l'atelier** : le tapis est relié au point de masse, le bracelet au tapis.
Sans tapis, la procédure relie le bracelet à une **partie métallique nue du châssis** du PC
débranché : technicien et pièce sont au même potentiel. On tient les cartes par les bords et on
range une pièce retirée dans un **sachet antistatique**.

**Procédure professionnelle** : prévenir → arrêter le système → bloc sur 0 → débrancher →
vider les charges → bracelet → ouvrir.

**Erreur fréquente** : ouvrir un PC « juste éteint » mais encore branché ; mettre le bracelet
avant de débrancher en croyant qu'il protège la personne (il protège la pièce) ; poser une
barrette sur la moquette.

**À l'écrit** : « Arrêt du système, interrupteur du bloc sur 0, câble secteur débranché, appui
sur le bouton de démarrage, bracelet relié au tapis selon la procédure de l'atelier. »

**Repère rapide** : **arrêter · 0 · débrancher · bouton · bracelet · bloc jamais ouvert**.
Exercices liés : {_ex("E02", "E03", "E16")}.
"""


def _workplace() -> str:
    return f"""**Objectifs** : reconnaître une batterie dangereuse ; travailler dans un poste aéré,
rangé et sûr ; nettoyer sans abîmer.

## 4.1 Batteries endommagées

{_fig(BATTERY_FIGURE)}

Une batterie **lithium-ion** gonflée (pavé tactile ou écran soulevé, coque déformée), percée,
chaude ou tombée peut **s'enflammer violemment** et dégager des fumées toxiques. On ne la charge
plus, on ne la presse pas, on ne la perce pas ; un appareil sous garantie n'est pas ouvert.

## 4.2 Ventilation, risques mécaniques, poste de travail

{_risks_table(("batt", "vent", "meca", "poste"))}

## 4.3 Dépoussiérer et refaire la pâte thermique

{_fig(CLEAN_FIGURE)}

**Procédure professionnelle** : poste dégagé et éclairé, boissons à l'écart, pièce aérée ;
débranchement (chapitre 3) ; pales bloquées, air sec par petites pressions ; pâte refaite en
petite quantité ; port à deux des charges lourdes.

**Erreur fréquente** : recharger un appareil dont la batterie gonfle « pour finir la journée » ;
l'aspirateur domestique ; laisser tourner un ventilateur sous le jet d'air.

**À l'écrit** : « Batterie gonflée : chargeur débranché, aucune pression, appareil isolé dans le
bac ininflammable, client et responsable prévenus, renvoi au fabricant. »

**Repère rapide** : **batterie gonflée = ne plus charger, ne pas presser, isoler · pièce aérée ·
pales bloquées · port à deux**. Exercices liés : {_ex("E02", "E04", "E08", "E19")}.
"""


def _data() -> str:
    return f"""**Objectifs** : protéger l'intégrité et la confidentialité des données du client ; tenir
compte du chiffrement et des droits.

## 5.1 Les données du client

Tout ce qui est sur le poste appartient au client : documents, courriels, favoris, photos,
données des logiciels métier, licences. Certaines sont **sensibles** (santé, salaires, dossiers
juridiques). Le technicien :

- **ne consulte** que ce qui est nécessaire à l'intervention — jamais les fichiers personnels
  « pour vérifier » ;
- **ne demande pas** le mot de passe d'une autre personne : le client ouvre lui-même sa session,
  ou un compte technique temporaire sert à l'intervention, puis il est supprimé ;
- **ne garde rien** : une copie temporaire est **chiffrée**, sur un support de l'atelier
  inventorié, et **effacée après restitution** (effacement noté sur la fiche).

En Europe, les données personnelles sont protégées par le **RGPD** : le client reste
**responsable** de ses données ; l'atelier qui les manipule pour lui doit les protéger et le
prévenir sans attendre en cas d'incident (chapitre 8).

## 5.2 Intégrité : une copie se vérifie

Une copie n'est une sauvegarde que si elle est **complète et identique**. On compare le nombre de
fichiers, les tailles et surtout les **empreintes** (SHA-256 : `Get-FileHash` sous Windows,
`sha256sum` sous Linux) : une taille identique ne prouve pas un contenu identique, une empreinte
identique, si. On ouvre aussi quelques fichiers **devant le client**.

## 5.3 Chiffrement et droits

Un disque **chiffré** (BitLocker sous Windows, LUKS sous Linux) est illisible sans sa clé. Après
une mise à jour du firmware ou un changement de carte mère, BitLocker peut demander la **clé de
récupération** (48 chiffres) : on la récupère **avant** d'intervenir (administrateur, compte de
l'organisation), on suspend BitLocker avant une mise à jour du firmware et on le réactive après.
La clé ne s'écrit jamais sur le PC et ne se garde pas après l'intervention. On ne désactive pas
le chiffrement « pour simplifier ».

Les **droits** suivent le même principe : le technicien utilise un compte prévu pour
l'intervention, avec les droits nécessaires et pas plus ; les permissions d'une copie sont
celles du client ([PR22](/uaa/ampcr-pratique-pr22), [PR23](/uaa/ampcr-pratique-pr23)).

**Procédure professionnelle** : inventorier les données avec le client, copier (chiffré),
vérifier par empreintes, récupérer les clés, travailler sans consulter, restituer, effacer la
copie.

**Erreur fréquente** : vérifier une copie en regardant seulement la taille du dossier ; prendre
le mot de passe sur un papier ; noter la clé BitLocker sur un autocollant.

**À l'écrit** : « Copie chiffrée sur le disque n° 3 de l'atelier, vérifiée par empreintes
SHA-256 (toutes identiques), effacée après contrôle du client. »

**Repère rapide** : **ne consulter que le nécessaire · jamais le mot de passe d'autrui · copie
chiffrée, vérifiée, effacée · clé de récupération avant d'intervenir**. Exercices liés :
{_ex("E12", "E13", "E18")}.
"""


def _backup_auth() -> str:
    return f"""**Objectifs** : vérifier un plan de sauvegarde avec la règle 3-2-1 ; réunir tous les
prérequis avant une opération qui efface.

## 6.1 La règle 3-2-1 (complément pédagogique)

{_fig(RULE321_FIGURE)}

- **3** copies des données, **l'original compris** ;
- sur **2** types de supports différents — convention prudente du cours : disque interne, disque
  externe et NAS sont tous des **disques** ; types retenus : {", ".join(sorted(set(SUPPORT_TYPES.values())))} ;
- dont **1** copie **hors site** (un incendie, un vol ou un rançongiciel n'emporte pas tout).

Un plan peut échouer sur un point : « {MISS_3} », « {MISS_2} » ou « {MISS_1} ». La règle 3-2-1
est un **complément** de bonne pratique : elle ne remplace pas la **vérification** de la copie
(chapitre 5) ni un **test de restauration** régulier ([PR12](/uaa/ampcr-pratique-pr12)).

## 6.2 Autorisation avant effacement ou réinstallation

{_fig(AUTH_FIGURE)}

{_prereq_table()}

Un accord **oral**, rapporté par un tiers, ne suffit pas : l'accord est **écrit, daté**, nomme
l'**opération** et le **support**, et vient d'une personne **habilitée** (propriétaire ou
responsable). La décision et la technique d'effacement adaptée à chaque support sont dans
[PR04](/uaa/ampcr-pratique-pr04) : un formatage rapide n'efface rien.

**Procédure professionnelle** : inventorier, sauvegarder, vérifier, récupérer les clés, faire
signer, puis seulement effacer ou réinstaller.

**Erreur fréquente** : « le patron est d'accord » dit par un stagiaire ; une seule copie sur le
NAS du même bureau appelée « sauvegarde » ; réinstaller avant d'avoir la clé de récupération.

**À l'écrit** : « Avant la réinstallation : copie vérifiée par empreintes, clé de récupération
obtenue de l'administrateur, licences notées, accord écrit signé par la gérante. »

**Repère rapide** : **3 copies · 2 types · 1 hors site · pas d'accord écrit, pas
d'effacement**. Exercices liés : {_ex("E11", "E14")}.
"""


def _waste() -> str:
    return f"""**Objectifs** : diriger chaque déchet vers sa filière ; ne jamais laisser partir un
support de données lisible.

## 7.1 Déchets d'équipements électriques et électroniques (DEEE)

{_fig(WASTE_FIGURE)}

{_waste_table()}

Les **DEEE** (écrans, PC, claviers, imprimantes) contiennent des métaux et des substances
dangereuses : ils ne vont **jamais** dans la poubelle ordinaire. En Belgique, la collecte est
organisée par **Recupel** (points de collecte, magasins, parcs à conteneurs, collecteurs agréés
pour les entreprises) ; les **piles et batteries** par **Bebat**. Les batteries ont leurs
**pôles isolés** au ruban adhésif.

## 7.2 Supports de données en fin de vie

Avant tout recyclage, un **disque**, un **SSD** ou une **clé USB** est **effacé de façon
certifiée** ou **détruit** par une filière agréée, avec l'accord écrit du propriétaire et un
**certificat** par support ([PR04](/uaa/ampcr-pratique-pr04)).

**Procédure professionnelle** : inventaire des objets et des supports (numéros de série),
accord écrit, effacement ou destruction certifiés, batteries retirées et isolées, chaque objet
dans sa filière, certificats joints à la fiche.

**Erreur fréquente** : jeter une pile bouton ou une batterie à la poubelle ; donner un PC au
recyclage avec son disque ; « formater » un SSD avant de le céder.

**À l'écrit** : « Disques : écrasement complet ou destruction, certificat par support ;
batteries : pôles isolés, collecte des batteries ; unités centrales : collecte DEEE. »

**Repère rapide** : **DEEE · piles et batteries · supports effacés ou détruits · cartouches
reprises · rien à la poubelle**. Exercices liés : {_ex("E15")}.
"""


def _sheets_incident() -> str:
    checklist = "\n".join(f"- **{title}** : " + " ; ".join(items) + "." for title, items in CHECKLIST)
    return f"""**Objectifs** : rédiger une fiche sécurité ; choisir le kit selon l'intervention ;
réagir à un incident dans le bon ordre.

## 8.1 La fiche sécurité

Une fiche sécurité par intervention courante, en sept rubriques :
{", ".join(f"**{f.lower()}**" for f in SAFETY_SHEET_FIELDS)}. Exemple rempli :

{_safety_sheet_table()}

## 8.2 Choisir l'outil selon l'intervention

{_interventions_table()}

## 8.3 La liste de contrôle

{_fig(CHECKLIST_FIGURE)}

{checklist}

## 8.4 Gérer un incident

{_fig(INCIDENT_FIGURE)}

{_fig(INCIDENT_TREE_FIGURE)}

L'ordre est toujours le même : **les personnes**, puis **les données**, puis **le matériel**. On
ne secourt pas dans une zone dangereuse ; on ne touche pas une victime encore en contact avec le
courant ; le **112** est le numéro d'urgence européen. Un incident sur les données (copie perdue,
fichiers effacés par erreur, données vues par une personne non autorisée) se signale **aussitôt**
au responsable, sans rien cacher : le client, responsable de ses données, décide de la suite —
s'il s'agit d'une violation de données personnelles présentant un risque, c'est lui qui la
notifie à l'**Autorité de protection des données**, au plus tard **72 heures** après en avoir
pris connaissance.

**Procédure professionnelle** : sécuriser, alerter, secourir, protéger les données, noter,
analyser ; arbre « {INCIDENT_TREE.title.lower()} » pour décider.

**Erreur fréquente** : réparer en silence une pièce abîmée ; relancer une copie interrompue au
hasard ; rester près d'une batterie qui fume pour « surveiller ».

**À l'écrit** : « Fumée du bloc : multiprise coupée sans risque, bloc isolé et étiqueté,
responsable prévenu, incident noté (heure, faits, mesures) ; analyse : multiprise surchargée. »

**Repère rapide** : **personnes · données · matériel · tout est noté · rien n'est caché**.
Exercices liés : {_ex("E17", "E19", "E20", "E21", "E22")}.
"""


def _examples() -> str:
    return (
        "Cinq interventions entièrement résolues : outillage et sécurité du poste, batterie endommagée, données "
        "du client, outillage réseau et fibre, fin de vie et DEEE. Dans chacune : risques, outils choisis, "
        "avant / pendant / après, données, incident et conclusion rédigée. Les kits, les manques de la règle "
        "3-2-1, les écarts d'empreintes, les prérequis manquants et les filières sont **calculés** depuis les "
        "règles du cours.\n\n"
        + "\n".join(_case_html(i, c) for i, c in enumerate(CASES, start=1))
    )


def _pitfalls() -> str:
    return """> **Ouvrir un PC encore branché**, ou mettre le bracelet antistatique en croyant qu'il protège la personne.

> **Ouvrir un bloc d'alimentation** pour le nettoyer ou le réparer.

> **Recharger ou presser une batterie gonflée.**

> **Mesurer le secteur 230 V** avec le multimètre de l'atelier, ou garder le réglage d'un collègue.

> **Brancher le testeur de câble sur un port actif** (PoE, ligne téléphonique).

> **Regarder une fibre** parce qu'on ne voit pas de lumière.

> **Souffler un ventilateur libre** ou passer l'aspirateur domestique sur la carte.

> **Appeler « sauvegarde » une copie non vérifiée**, ou une copie unique dans le même bureau.

> **Effacer ou réinstaller sur un accord oral**, ou sans la clé de récupération d'un disque chiffré.

> **Consulter les fichiers personnels** du client ou lui demander son mot de passe.

> **Jeter une batterie ou un disque** dans la poubelle ordinaire.

> **Cacher un incident.**
"""


def _exercises_intro() -> str:
    return f"""{len(PRACTICE_ITEMS)} exercices corrigés : **choix d'outil** (outil propre à chaque tâche, kit
d'une intervention, multimètre, testeur d'alimentation) ; **risques et sécurité** (situations,
dépoussiérage, fibre) ; **procédures à ordonner** (débranchement, batterie gonflée, prise
murale, incident) ; **protection des données** (règle 3-2-1, intégrité par empreintes,
chiffrement, autorisation, confidentialité) ; **fin de vie** (filières) ; **deux schémas à
compléter** (poste antistatique, arbre d'incident) ; un **parcours d'arbre** et des
**rédactions** (fiche sécurité, incident de données). Rédige ta réponse sur papier **avant**
d'ouvrir le corrigé ; toute réponse équivalente et justifiée est acceptée. Ces mêmes exercices
sont proposés dans [S'entraîner](/uaa/{PR28_SLUG}/practice), avec correction après envoi.

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
    return f"""Le mini-examen se passe dans l'onglet [Examen blanc](/uaa/{PR28_SLUG}/exam) : **10 questions à réponse
libre**, chacune notée sur **2 points**, soit une note sur **{EXAM_TOTAL_POINTS}**. Les
questions ne figurent pas dans ce cours.

| N° | Thème | Type | Points |
|---|---|---|---|
{rows}

**Déroulement.** Chaque question est une situation complète : toutes les données nécessaires
sont dans l'énoncé et ses documents (relevés, listes de fichiers, fiches fictives). **Aucune
correction n'est visible pendant la passation** ; tes réponses sont enregistrées au fur et à
mesure. Après l'envoi, chaque réponse est corrigée selon le **barème analytique** de la question
(critères et points), puis tu vois ta note sur {EXAM_TOTAL_POINTS}, le corrigé et le barème.

**Ce que valorise le barème.** Le **bon outil** et sa précaution, la **sécurité** de la
personne avant celle du matériel, la **protection des données** (copie vérifiée, accord écrit,
confidentialité) et la bonne **filière** — pas une liste de mots.

**Nature de la correction.** Les réponses rédigées reçoivent une **proposition de correction
automatique** (assistée par IA) appuyée sur le barème : c'est un repère d'entraînement, pas une
note officielle ; en cas de doute, compare ta réponse au corrigé.
"""


def _memo() -> str:
    return """## Mémo

- **Outils PC** : tournevis adaptés, pinces hors tension, bracelet et tapis selon la procédure,
  testeur d'alimentation (jamais ouvrir le bloc), multimètre (basse tension, hors secteur),
  pâte thermique et alcool isopropylique, air sec avec pales bloquées.
- **Outils réseau** : dénudeur réglé, sertisseuse 8P8C, outil d'insertion (110 ou LSA), testeur
  jamais sur un port actif, outils BNC adaptés au câble, kit de nettoyage fibre.
- **Débrancher** : prévenir · arrêter · 0 · débrancher · bouton · bracelet.
- **Risques** : ESD, électricité, bloc, batterie gonflée (ne plus charger, ne pas presser,
  isoler), ventilation, mécaniques, laser et éclats, poste de travail.
- **Données** : ne consulter que le nécessaire ; jamais le mot de passe d'autrui ; copie
  chiffrée, vérifiée par empreintes, effacée après restitution ; clé de récupération avant.
- **3-2-1** (complément) : 3 copies, 2 types de supports, 1 hors site.
- **Avant d'effacer** : sauvegarde vérifiée, accord écrit précis, personne habilitée, clé,
  licences.
- **Fin de vie** : DEEE, piles et batteries, supports effacés ou détruits, cartouches reprises.
- **Incident** : personnes, données, matériel ; tout est noté, rien n'est caché.

## Glossaire des termes employés

- **DEEE** : déchets d'équipements électriques et électroniques.
- **Empreinte (SHA-256)** : suite de caractères calculée depuis le contenu d'un fichier ; elle
  change dès qu'un seul octet change.
- **ESD** : décharge électrostatique, capable de détruire une puce sans qu'on la sente.
- **Férule** : pièce centrale d'un connecteur optique, qui tient la fibre.
- **Outil d'insertion** : outil qui enfonce et coupe les fils dans les contacts d'une prise ou
  d'un panneau.
- **Personne habilitée** : personne qui a le droit de décider pour le matériel ou les données.
- **PoE** : alimentation électrique fournie par le câble réseau, depuis le switch.
- **Règle 3-2-1** : 3 copies, 2 types de supports, 1 copie hors site.
- **Testeur wiremap** : testeur qui vérifie le chemin de chaque fil d'un câble.
"""


def _sources() -> str:
    return """## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles) : épreuve « uniquement par écrit » (p. 3) ; pp. 5-6, AP-14
  (montage, démontage) et AP-20 (précautions d'utilisation des câbles, connecteurs). Copie
  versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
  Programme officiel n° 345/2007/249 (option AMPCR).
- **Guide de conception des alimentations ATX12V** (Intel) : tolérances des tensions (rappel de
  PR02).
- **Documentation Microsoft** : BitLocker (clé de récupération, suspension avant une mise à jour
  du firmware), `Get-FileHash` ; **pages de manuel Linux** : `sha256sum`, LUKS.
- **NIST SP 800-88** (effacement des supports), comme en PR04.
- **Règlement général sur la protection des données (RGPD)**, art. 33 (notification d'une
  violation de données dans les 72 heures) ; Autorité de protection des données (Belgique).
- **Filières belges** : Recupel (DEEE), Bebat (piles et batteries).

Les kits d'outils, les plages de tension, les manques de la règle 3-2-1, les écarts
d'empreintes, les prérequis manquants, les filières et le parcours de l'arbre d'incident sont
**produits par programme** depuis des données **vérifiées par des tests automatiques** ; les
schémas en sont dessinés directement. Aucun schéma n'est tiré d'une image générée ni d'une
photographie, et aucun ne montre un geste dangereux.

## Compléments pédagogiques (non imposés par la liste officielle)

Les pp. 5-6 ne citent ni la sécurité ni la protection des données en toutes lettres. Sont des
**compléments**, signalés comme tels, indispensables pour rédiger une intervention :

- la sécurité électrique, l'ESD et les risques de l'atelier (AP-C02) ;
- la protection des données du client, la sauvegarde, la confidentialité et l'autorisation
  (AP-C03), dont la **règle 3-2-1** ;
- les filières de fin de vie, la fiche sécurité et la gestion d'incident ;
- la **convention du cours** sur les types de supports (disque interne, externe et NAS comptés
  comme un seul type).

Ces consignes sont des règles générales de prudence : la procédure de l'atelier, le manuel du
fabricant et les consignes du site font foi.

## Supports fictifs

Les personnes, entreprises, fichiers, empreintes, relevés et dossiers de ce cours sont
**fictifs** et reconstitués pour l'entraînement ; ils ne décrivent aucun client réel. Aucun
n'est une question officielle ou déjà posée par le Jury.
"""


def pr28_course_sections() -> list[tuple[str, str]]:
    """Blocs du cours (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("PR28 — Objectifs et place dans l'épreuve", _objectives()),
        ("PR28 — 1. Outillage du poste de travail : choisir, utiliser, contrôler", _pc_tools()),
        ("PR28 — 2. Outillage réseau : cuivre, coaxial, fibre et sécurité laser", _net_tools()),
        ("PR28 — 3. Électricité, bloc d'alimentation, débranchement et protection ESD", _electric()),
        ("PR28 — 4. Batteries endommagées, ventilation, risques mécaniques et poste de travail", _workplace()),
        ("PR28 — 5. Données du client : intégrité, confidentialité, chiffrement et droits", _data()),
        ("PR28 — 6. Sauvegarde 3-2-1 et autorisation avant effacement ou réinstallation", _backup_auth()),
        ("PR28 — 7. Fin de vie : déchets DEEE, piles et supports de données", _waste()),
        ("PR28 — 8. Fiches sécurité, choix d'outil et gestion d'incident", _sheets_incident()),
        ("PR28 — Exemples : cinq interventions entièrement résolues", _examples()),
        ("PR28 — Pièges et erreurs fréquentes", _pitfalls()),
        (f"PR28 — Exercices corrigés ({len(PRACTICE_ITEMS)}) et leurs corrigés", _exercises_intro()),
        ("PR28 — Mini-examen noté sur 20 : mode d'emploi", _mini_exam()),
        ("PR28 — Fiche mémo et glossaire", _memo()),
        ("PR28 — Sources et compléments pédagogiques", _sources()),
    ]

