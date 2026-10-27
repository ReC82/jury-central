"""Cours PR30 « Grand laboratoire écrit — installation et dépannage d'un réseau complet » —
parcours AMPCR pratique écrite (ticket #229).

Matière : intégralement celle du ticket #229 — dossier intégrateur d'une PME fictive (plan de
deux salles, six postes Windows et Linux, switch, routeur et point d'accès, imprimante, partage
et serveur) : inventaire, contraintes, budget indicatif sans prix inventé, câblage T568B,
baie, plan IPv4, DHCP et DNS, comptes, groupe de travail ou domaine selon le scénario, droits,
installation des systèmes, panne matérielle et panne logicielle, Wi-Fi, sécurité, procédure de
recette et rapport ; huit études de cas graduées et intégralement corrigées, exercices
transversaux, mini-examen /20, plusieurs solutions acceptées si elles sont justifiées, lien
explicite avec les exigences officielles et compléments identifiés.
Découpage en blocs titrés (le titre pilote le type de carte, `app.card_kind` : aucun titre de
bloc théorique ne contient « examen », « source », « ressource », « exemple », « exercice »,
« méthode », « piège », « attention », « transfert » ni « mémo »).
Données et valeurs calculées : `app.v1.ampcr_pratique_pr30_figures` ; exercices et
mini-examen : `app.v1.ampcr_pratique_pr30_bank`. Le cours renvoie aux cours techniques dont il
applique les règles (PR07, PR08, PR09, PR13, PR15, PR18, PR20, PR22, PR23, PR24, PR25, PR29).
"""

from html import escape

from app.v1.ampcr_pratique_plan import REQUIREMENTS_BY_ID
from app.v1.ampcr_pratique_pr06_course import _exercise_card, _fig, _req
from app.v1.ampcr_pratique_pr29_figures import REPORT_FIELDS, fmt, required_checks
from app.v1.ampcr_pratique_pr30_bank import EXAM_ITEMS, EXAM_TOTAL_POINTS, PRACTICE_ITEMS
from app.v1.ampcr_pratique_pr30_figures import (
    ACCOUNTS,
    AP_IP,
    BOM_BY_GROUP,
    CABLE_BOXES,
    CASES,
    CHANNEL_5,
    CHANNEL_24,
    COMPANY,
    CONSTRAINTS,
    COST_GROUPS,
    COVERED_OFFICIAL,
    DRAFT_ERRORS,
    FACTS,
    FAILED_LINKS,
    FINAL_REPORT,
    FIXED_HOSTS,
    FOLDERS,
    FUTURE_POSTES,
    GUEST_GATEWAY,
    GUEST_NETWORK,
    GUEST_VLAN,
    HOSTS,
    LAB_FIGURE,
    LAN_FIGURE,
    LEASE_HOURS,
    LINKS,
    LINKS_FIGURE,
    LINUX_FIGURE,
    LONGEST_RUN,
    MATRIX,
    MATRIX_FIGURE,
    MODEL,
    MODEL_LATER,
    NEEDS,
    NEIGHBORS,
    NETWORK,
    NOT_COVERED_OFFICIAL,
    OS_PLAN,
    P08_LENGTH_M,
    PANELS,
    PASSPHRASE_PRO,
    PATCH,
    PC_CHECKS,
    PCS,
    PEOPLE,
    PINOUT_FIGURE,
    PINS,
    PLAN,
    PLAN_ERRORS,
    PLAN_FIGURE,
    POE_NEED_W,
    POE_RESULT,
    POOL,
    POOL_SIZE,
    PORTS_LATER,
    PORTS_NOW,
    PRICE_NOTE,
    PROCEDURES,
    RACK_FIGURE,
    RACK_U,
    RACK_USED_U,
    RAM_FAULT_STEPS,
    RECETTE_DIAG,
    RECETTE_EVIDENCE,
    RECETTE_FIGURE,
    RECETTE_PROC_FIGURE,
    RIGHT_ACCESS,
    ROUTER_IP,
    RUNS,
    SEC_GOOD,
    SECURITY_FIGURE,
    SECURITY_ITEMS,
    SERVER_IP,
    SERVER_OS,
    SSID_GUEST,
    SSID_PRO,
    STATIC_FIGURES,
    STORED_ACCESS,
    STORED_LOGIN,
    SURVEY_FIGURE,
    SURVEY_ROWS,
    SWITCH_IP,
    SWITCH_POE_BUDGET_W,
    SWITCH_PORTS,
    TOTAL_CABLE_M,
    TREE_FIGURE,
    UPLINKS,
    WAN_IP,
    WIN_FIGURE,
    WORST_5,
    WRITTEN_AT,
)
from app.v1.ampcr_pratique_visuals import render_figure

PR30_TITLE = "Grand laboratoire écrit — installation et dépannage d'un réseau complet"
PR30_SLUG = "ampcr-pratique-pr30"

_SCHEMAS_BY_PATH = {path: figure for figure, path in STATIC_FIGURES}


def _card(number: int, item) -> str:
    """Carte d'exercice de PR06 ; un schéma à compléter est affiché (SVG) avant sa
    description textuelle."""
    html = _exercise_card(number, item, anchor_prefix="pr30")
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


def _md(text: str) -> str:
    """Markdown mange une barre oblique inverse sur deux hors du code : on double celles des
    chemins UNC (\\\\serveur) en dehors des passages entre accents graves (comme PR23)."""
    pieces = text.split("`")
    return "`".join(p.replace("\\\\", "\\\\\\\\") if i % 2 == 0 else p for i, p in enumerate(pieces))


def _lc(text: str) -> str:
    """Minuscule sur la première lettre seulement (garde les sigles : DHCP, QVL, Active Directory)."""
    return text[:1].lower() + text[1:]


def _sentences(items) -> str:
    """Phrases d'une liste jointes par « ; », sans point final doublé."""
    return " ; ".join(i.rstrip(".") for i in items) + "."


def _fr(value: float) -> str:
    return f"{value:g}".replace(".", ",")


def _procedures_list() -> str:
    return "\n".join(
        f"{i}. **{title}** ({len(steps)} étapes)" for i, (title, steps) in enumerate(PROCEDURES, start=1)
    )


def _reqs_line(ids: tuple[str, ...]) -> str:
    return " ; ".join(f"**{r}** « {REQUIREMENTS_BY_ID[r].text.rstrip('.')} »" for r in ids)


def _complements_line(items: tuple[str, ...]) -> str:
    return " ; ".join(
        f"**{c}** ({_lc(REQUIREMENTS_BY_ID[c].text.rstrip('.'))})" if c in REQUIREMENTS_BY_ID else c for c in items
    )


# --- Tableaux de données du dossier ----------------------------------------------------------


def _people_table() -> str:
    rows = [(name, role, poste, OS_PLAN[poste]) for _l, name, role, poste in PEOPLE]
    return _html_table(("Personne (fictive)", "Fonction", "Poste", "Système retenu"), rows,
                       caption=f"{COMPANY} — personnel et postes")


def _pcs_table() -> str:
    rows = []
    for name, desc, _spec in PCS:
        verdict, blockers, settings = PC_CHECKS[name]
        detail = "; ".join(blockers or settings) or "—"
        rows.append((name, desc, verdict, detail, OS_PLAN[name]))
    return _html_table(("Poste", "Relevé", "Windows 11", "Blocages ou réglages", "Choix"), rows,
                       caption="Compatibilité Windows 11 (règles de PR07)")


def _runs_table() -> str:
    rows = [(key, PLAN.outlets[i].label, _fr(h), str(length), PATCH[i][0])
            for i, (key, h, length) in enumerate(RUNS)]
    return _html_table(("Prise", "Destination", "Parcours horizontal (m)", "Câble à prévoir (m)", "Repère"), rows,
                       caption=f"Longueurs (parcours + 3 m de montée et descente + 2 m de réserve) : total {TOTAL_CABLE_M} m")


def _bom_table() -> str:
    rows = [(group, b.item, b.quantity, b.why) for group in COST_GROUPS for b in BOM_BY_GROUP[group]]
    return _html_table(("Poste de dépense", "Article", "Quantité", "Justification"), rows,
                       caption="Nomenclature et budget indicatif — sans prix")


def _pins_table() -> str:
    return _html_table(("Broche", "Couleur T568B"), [(str(p), c) for p, c in PINS])


def _hosts_table() -> str:
    rows = [(h.name, h.role, f"{h.ip}/{h.prefix}", "DHCP" if h.dhcp else "fixe", h.gateway or "—",
             h.dns[0] if h.dns else "—") for h in HOSTS]
    return _html_table(("Équipement", "Rôle", "Adresse", "Mode", "Passerelle", "DNS"), rows,
                       caption=f"Plan d'adressage du réseau {NETWORK}")


def _matrix_table() -> str:
    rows = [(login, *(MATRIX[login][f].lower() for f in FOLDERS)) for login in MATRIX]
    return _html_table(("Compte", *FOLDERS), rows, caption="Droits effectifs par le réseau (calculés)")


def _needs_table() -> str:
    return _html_table(("Dossier", "Besoin écrit par le client"), list(NEEDS))


def _accounts_table() -> str:
    rows = [(a.login, a.person, ", ".join(g for g in a.groups)) for a in ACCOUNTS]
    return _html_table(("Compte sur SRV-01", "Personne", "Groupes"), rows)


def _survey_table() -> str:
    rows = [(p, o, f"{a} dBm", f"{b} dBm", v) for p, o, a, b, v in SURVEY_ROWS]
    return _html_table(("Point", "Obstacle", "2,4 GHz", "5 GHz", "Verdict"), rows)


def _neighbors_table() -> str:
    return _html_table(("Réseau voisin", "Canal 2,4 GHz", "Signal"), [(n.ssid, str(n.channel), f"{n.dbm} dBm") for n in NEIGHBORS])


def _final_measures_table() -> str:
    rows = [(m.criterion.text(), fmt(m.before), fmt(m.after), m.result) for m in FINAL_REPORT.measures]
    return _html_table(("Critère", "1re recette", "Après corrections", "Résultat"), rows)


def _final_report_table() -> str:
    filled = FINAL_REPORT.filled()
    return _html_table(("Rubrique", "Contenu"), [(f.label, filled[f.key]) for f in REPORT_FIELDS],
                       caption="Rapport final du chantier (modèle de PR29)")


def _requirements_table() -> str:
    rows = [(f"Cas {c.number}", f"niveau {c.level}", c.title, ", ".join(c.official), _complements_line(c.complements).replace("**", ""))
            for c in CASES]
    return _html_table(("Cas", "Niveau", "Sujet", "Exigences officielles", "Compléments"), rows,
                       caption="Lien explicite entre les études de cas et les consignes officielles")


# =============================================================================================
# Sections du cours
# =============================================================================================


def _objectives() -> str:
    return f"""## Ce que tu sauras faire, par écrit

L'épreuve pratique AMPCR se passe **uniquement par écrit** (consignes officielles 2026-2027/1,
p. 3). Un sujet peut te confier **tout un réseau** : l'étudier, le chiffrer, le câbler,
l'adresser, le configurer, le dépanner et le rendre au client. Ce laboratoire réunit ces
étapes en **un seul dossier**, celui d'une PME fictive, {COMPANY}. Tu dois savoir :

1. lire une demande et en tirer l'**inventaire**, les **contraintes** et un **budget
   indicatif** par postes de dépense, **sans inventer de prix** ;
2. décrire le **câblage** T568B, la **baie**, le **repérage** et la **recette des liens** ;
3. établir le **plan IPv4**, le **DHCP** et le **DNS** ;
4. choisir **groupe de travail ou domaine**, créer les **comptes**, les **groupes**, les
   **partages** et vérifier les **droits** ;
5. décrire l'**installation des systèmes** Windows et Linux et le raccordement des postes ;
6. diagnostiquer une **panne matérielle** et une **panne logicielle** à la mise en service ;
7. configurer le **Wi-Fi** du personnel et des invités, et lister les **mesures de sécurité** ;
8. mener la **recette**, dépanner l'accès au réseau et rédiger le **rapport** final.

Ce cours contient **{len(PROCEDURES)} procédures illustrées**, un **arbre de recette**, des
schémas techniques construits depuis les données du dossier et **{len(CASES)} études de cas
graduées**, intégralement corrigées :

{_procedures_list()}

## Exigences travaillées dans ce cours

{_req("AP-36")}
{_req("AP-37")}
{_req("AP-38")}

Ce sont les trois exigences **officielles** (p. 6) du laboratoire. Chaque étude de cas cite en
plus les exigences qu'elle mobilise ; le tableau de la séquence « Sources et compléments »
donne la correspondance complète, et sépare les **compléments** du parcours (rédaction AP-C01,
sécurité électrique AP-C02, protection des données AP-C03, budget, onduleur, VLAN invités).

## Lien avec la théorie et les autres cours

La théorie AMPCR présente les réseaux locaux ([MC15](/uaa/ampcr-mc15),
[MC16](/uaa/ampcr-mc16), [MC23](/uaa/ampcr-mc23)), le Wi-Fi ([MC25](/uaa/ampcr-mc25)) et
le dépannage ([MC31](/uaa/ampcr-mc31)). Ce cours-ci est **pratique** et **intégrateur** : il
applique, sans les recopier, les règles des cours pratiques — câblage
([PR13](/uaa/ampcr-pratique-pr13), [PR15](/uaa/ampcr-pratique-pr15),
[PR18](/uaa/ampcr-pratique-pr18)), adressage ([PR20](/uaa/ampcr-pratique-pr20)), comptes et
partages ([PR22](/uaa/ampcr-pratique-pr22), [PR23](/uaa/ampcr-pratique-pr23)), systèmes
([PR07](/uaa/ampcr-pratique-pr07), [PR08](/uaa/ampcr-pratique-pr08),
[PR09](/uaa/ampcr-pratique-pr09)), dépannage ([PR24](/uaa/ampcr-pratique-pr24)), Wi-Fi
([PR25](/uaa/ampcr-pratique-pr25)) et rapport ([PR29](/uaa/ampcr-pratique-pr29)).

## Comment travailler ce cours

Lis les chapitres dans l'ordre : chacun donne ses **objectifs**, la **théorie** utile au
dossier, la **procédure professionnelle**, l'**erreur fréquente**, ce qu'on attend **à
l'écrit** et un **repère rapide**, avec un renvoi vers les exercices liés. Fais ensuite les
**huit études de cas**, du niveau 1 (guidé) au niveau 4 (ouvert) : rédige ta réponse sur papier
**avant** de lire le corrigé. Termine par les **{len(PRACTICE_ITEMS)} exercices corrigés** et le
**mini-examen noté sur {EXAM_TOTAL_POINTS}** de l'onglet « Examen blanc ».

> **Important —** {COMPANY}, ses locaux, son personnel, ses équipements, ses adresses MAC et
> ses relevés sont des **supports fictifs** construits pour s'entraîner (rédaction :
> {WRITTEN_AT}). Plusieurs solutions sont **acceptées si elles sont justifiées** : les variantes
> valables sont signalées dans chaque corrigé. Aucun cas n'est une question officielle ni une
> question déjà posée par le Jury.
"""


def _dossier() -> str:
    constraints = "\n".join(f"- {c}" for c in CONSTRAINTS)
    return f"""**Objectifs** : lire un dossier complet ; repérer les besoins, les contraintes et ce qui
manque ; savoir ce que chaque phase du laboratoire devra produire.

## 1.1 La demande du client

{COMPANY} (fictif) est un cabinet de six personnes qui emménage sur un plateau de bureaux d'un
seul niveau. La fibre de l'opérateur arrive dans le local technique, entre les deux salles.

{_fig(PLAN_FIGURE, wide=True)}

{_people_table()}

**Contraintes écrites dans la demande :**

{constraints}

## 1.2 Les huit phases du laboratoire

{_fig(LAB_FIGURE)}

Chaque phase produit une pièce du **dossier technique** remis au client : inventaire et
budget, plan de câblage et rapport du testeur, plan d'adressage, matrice des droits, fiches
d'installation, configuration Wi-Fi, liste de sécurité, fiche de recette et rapport.

**Procédure professionnelle** : relire la demande, reformuler chaque besoin en une phrase
vérifiable, lister les **questions au client** (ici : horaires du chantier, budget, personnes
autorisées à la baie), puis seulement concevoir.

**Erreur fréquente** : commencer par choisir du matériel « qu'on connaît » sans relire les
contraintes (extension prévue, invités, coupures de courant) ; oublier que tout doit être
**vérifiable** à la recette.

**À l'écrit** : « Besoin 4 : Wi-Fi des clients sans accès aux fichiers → réseau invités isolé,
contrôlé à la recette par un appareil invité qui n'atteint pas le serveur. »

**Repère rapide** : **une demande · des besoins vérifiables · des contraintes · huit phases ·
un dossier remis**. Exercices liés : {_ex("E04", "E22")}.
"""


def _inventory() -> str:
    return f"""**Objectifs** : dimensionner switch, panneau, baie et câble ; choisir les systèmes ;
présenter un budget **par postes de dépense**, sans prix inventé.

## 2.1 Dimensionner avec les règles de PR18

- **Switch** : liens à brasser + 20 % de réserve (arrondi au-dessus) + cordons directs (box,
  serveur). Aujourd'hui : {LINKS} liens → **{PORTS_NOW} ports** ; avec les {FUTURE_POSTES}
  postes prévus : **{PORTS_LATER} ports** → switch de **{SWITCH_PORTS} ports**, administrable
  (VLAN), PoE+.
- **Panneau** : {LINKS} ports → **{PANELS} panneau de 24 ports**.
- **Câble** : {TOTAL_CABLE_M} m à poser (plus long lien {LONGEST_RUN[0]}, {LONGEST_RUN[2]} m,
  bien sous les 90 m du lien permanent) → **{CABLE_BOXES} boîte de 305 m**.
- **Baie** : {RACK_USED_U} U d'équipements + 25 % de réserve → **baie de {RACK_U} U**.
- **PoE** : le point d'accès (classe 4) demande {_fr(POE_NEED_W)} W ; le switch en fournit
  {SWITCH_POE_BUDGET_W:g} W : {POE_RESULT.lower()}.

## 2.2 Choisir le système de chaque poste

{_pcs_table()}

Windows 10 n'est plus pris en charge depuis le **14 octobre 2025** : COMPTA passe à Windows 11
Pro (activation du TPM dans le firmware). LINUX1 n'est pas compatible (processeur absent de la
liste, pas de TPM) : il reçoit **Ubuntu 24.04 LTS**, maintenu, adapté aux logiciels libres du
cartographe. Le serveur SRV-01 reçoit {SERVER_OS}.

## 2.3 Nomenclature et budget indicatif

{_bom_table()}

> **Budget sans prix inventé —** {PRICE_NOTE}

**Procédure professionnelle** : compter les liens sur le plan, appliquer les réserves, choisir
les tailles standard, écrire la justification de chaque ligne, regrouper par poste de dépense.

**Erreur fréquente** : dimensionner pour aujourd'hui alors que l'extension est écrite dans la
demande ; inventer des prix « de mémoire » ; oublier les licences d'accès client du serveur ou
la main-d'œuvre de recette.

**À l'écrit** : « Switch {SWITCH_PORTS} ports : {LINKS + FUTURE_POSTES} liens à terme × 1,2 →
{PORTS_LATER - UPLINKS} + {UPLINKS} cordons = {PORTS_LATER} ports ; taille standard supérieure :
{SWITCH_PORTS}. »

**Repère rapide** : **compter · réserver 20 % · taille standard · justifier · grouper par poste
de dépense · prix = devis**. Exercices liés : {_ex("E01", "E02", "E03")}.
"""


def _cabling() -> str:
    failed = ", ".join(FAILED_LINKS)
    return f"""**Objectifs** : décrire la pose, le raccordement T568B, la baie et le repérage ; lire le
rapport du testeur et décider.

## 3.1 Câble, pose et raccordement

Câble **Cat6 U/UTP** monobrin (1 Gb/s sur 100 m de canal, bien au-delà des besoins du
cabinet), gaine sans halogène. Le blindage (F/UTP) ne s'impose que près de sources de
parasites ([PR13](/uaa/ampcr-pratique-pr13)). Pose en faux plafond et en goulotte, séparée du
courant fort, croisements à angle droit, rayon de courbure respecté, aucun câble au sol dans un
passage.

{_fig(PINOUT_FIGURE)}

{_pins_table()}

Toute l'installation est en **T568B**, à la prise comme au panneau : chaque lien est **droit**.
T568A serait aussi correct, **à condition** d'être utilisé partout ([PR15](/uaa/ampcr-pratique-pr15)).

## 3.2 Baie, brassage et repérage

{_fig(RACK_FIGURE)}

{_runs_table()}

Le repère est **le même aux deux bouts** : la prise P01 porte « {PATCH[0][0]} », comme le port 1
du panneau, brassé sur le port 1 du switch. Le tableau de brassage fait partie du dossier.

## 3.3 Recette des liens

{_fig(LINKS_FIGURE)}

Le rapport se lit dans l'ordre : câblage des 8 fils, longueur (90 m au plus), certification.
Ici, **{failed}** est en défaut de câblage (fil 6 ouvert) : la prise est refaite et le lien
retesté **avant** de brancher le poste.

**Procédure professionnelle** : étiqueter avant de tirer, poser, raccorder, tester **chaque**
lien, refaire et retester les liens en défaut, archiver les rapports.

**Erreur fréquente** : mélanger T568A et T568B ; détorsader sur plusieurs centimètres ; brancher
les postes sans avoir testé les liens, puis chercher la panne dans Windows.

**À l'écrit** : « P08 : fil 6 ouvert → keystone refait en T568B, détorsadage ≤ 13 mm ;
retest : 8 fils conformes, {P08_LENGTH_M:g} m, PASS. »

**Repère rapide** : **Cat6 · T568B partout · même repère aux deux bouts · tester chaque lien
avant les postes**. Exercices liés : {_ex("E05", "E06", "E19")}.
"""


def _addressing() -> str:
    fixed = ", ".join(f"{h.name} {h.ip}" for h in FIXED_HOSTS)
    return f"""**Objectifs** : établir le plan IPv4 ; régler le DHCP et le DNS ; contrôler un plan.

## 4.1 Le réseau du personnel

Réseau privé **{NETWORK}** : masque {FACTS.mask}, adresse du réseau {FACTS.network}, diffusion
{FACTS.broadcast}, {FACTS.usable} adresses d'hôtes ({FACTS.first_host} à {FACTS.last_host}) ([PR20](/uaa/ampcr-pratique-pr20)).

{_fig(LAN_FIGURE)}

{_hosts_table()}

- **Adresses fixes**, hors de l'étendue : {fixed}. Les autres appareils doivent toujours les
  trouver.
- **DHCP** sur la box : étendue {POOL[0]} à {POOL[1]} ({POOL_SIZE} adresses pour une trentaine
  d'appareils), bail de {LEASE_HOURS} h, passerelle et DNS {ROUTER_IP}.
- **DNS** : la box relaie vers les serveurs de l'opérateur ; les postes joignent le serveur par
  son adresse ({SERVER_IP}) ou par son nom SRV-01.
- **Réseau invités** : VLAN {GUEST_VLAN}, {GUEST_NETWORK}, passerelle {GUEST_GATEWAY}, isolé
  du réseau du personnel (chapitre 7).

Contrôle du plan par les règles de PR20 : **{len(PLAN_ERRORS)} erreur** — aucune adresse en
double, aucune adresse fixe dans l'étendue, même masque et même passerelle partout.

**Procédure professionnelle** : choisir le réseau, réserver les adresses fixes, placer
l'étendue sans chevauchement, écrire le tableau, vérifier poste par poste à la recette
(ipconfig, ip addr).

**Erreur fréquente** : une adresse fixe dans l'étendue (conflit le jour où la box la donne) ;
un masque différent sur un équipement ; une passerelle d'un autre réseau.

**À l'écrit** : « IMP-01 : 192.168.50.20/24 fixe, hors étendue ; passerelle et DNS
192.168.50.1 ; port TCP/IP des postes vers 192.168.50.20. »

**Repère rapide** : **un réseau · fixes hors étendue · même masque · passerelle = box ·
contrôle poste par poste**. Exercices liés : {_ex("E07", "E08", "E09")}.
"""


def _accounts() -> str:
    return f"""**Objectifs** : choisir le modèle de gestion des comptes ; créer comptes et groupes ;
poser les partages et les droits ; vérifier la matrice.

## 5.1 Groupe de travail ou domaine ?

Repère de [PR22](/uaa/ampcr-pratique-pr22) : au-delà d'une dizaine de postes, ou dès qu'il faut
gérer comptes et règles depuis un point central, un domaine ; sinon un groupe de travail. Ici,
six postes stables, une personne par poste : **{_lc(MODEL)}**. Si le cabinet accueille des
stagiaires qui changent souvent, le choix devient **{MODEL_LATER}** : c'est le
« selon scénario » du dossier.

## 5.2 Comptes, groupes et partages sur SRV-01

Un **compte par personne** sur le serveur, des **groupes par service** ; les droits se donnent
aux groupes, jamais aux personnes.

{_accounts_table()}

{_needs_table()}

Partages : « Utilisateurs authentifiés : Modifier » ; les autorisations **NTFS** décident
([PR23](/uaa/ampcr-pratique-pr23)). Par le réseau, le plus restrictif des deux s'applique.

{_fig(MATRIX_FIGURE)}

{_matrix_table()}

La matrice est **calculée** depuis les autorisations : elle répond exactement aux besoins écrits.
L'imprimante IMP-01 est installée **par son adresse IP** sur chaque poste : l'impression ne
dépend d'aucun PC allumé.

**Procédure professionnelle** : écrire les besoins, créer groupes puis comptes, poser NTFS sur
les dossiers, partager, **tester avec chaque compte** (lecture, écriture, refus).

**Erreur fréquente** : « Tout le monde : contrôle total » pour aller vite ; des droits donnés
nom par nom ; tester avec le compte administrateur, qui passe partout.

**À l'écrit** : « Compta : NTFS G_Compta modification, G_Direction lecture ; partage
Utilisateurs authentifiés modifier ; test : flemaire crée un fichier, amartin est refusée. »

**Repère rapide** : **modèle selon le scénario · un compte par personne · droits aux groupes ·
NTFS décide · tester avec chaque compte**. Exercices liés : {_ex("E10", "E11")}.
"""


def _systems() -> str:
    return f"""**Objectifs** : décrire l'installation de Windows 11 Pro et d'Ubuntu ; raccorder chaque
poste au serveur et à l'imprimante.

## 6.1 Windows 11 Pro sur ETUDES2 (et mise à niveau de COMPTA)

{_fig(WIN_FIGURE)}

ETUDES2 est livrée **sans système** : installation propre, disque en GPT, mode UEFI, TPM et
démarrage sécurisé actifs ([PR08](/uaa/ampcr-pratique-pr08)). COMPTA, sous Windows 10 Pro,
passe à Windows 11 Pro par mise à niveau sur place **après sauvegarde vérifiée** de ses
données (AP-C03), une fois le TPM activé.

## 6.2 Ubuntu 24.04 LTS sur LINUX1

{_fig(LINUX_FIGURE)}

L'image est contrôlée (sha256sum) avant d'écrire la clé ([PR09](/uaa/ampcr-pratique-pr09)) ;
le SSD ne contient aucune donnée à garder (vérifié avec le cartographe).

## 6.3 Raccorder les postes

- **Windows** : profil réseau « Privé » ; lecteur réseau vers `\\\\SRV-01\\<service>` avec le
  compte de la personne ; imprimante ajoutée par l'adresse IP {HOSTS[4].ip}.
- **Ubuntu** : `smb://{SERVER_IP}/Etudes` dans le gestionnaire de fichiers, compte tvidal ;
  imprimante par son adresse IP.
- **Contrôles** : Gestionnaire de périphériques sans erreur (ou `lspci`, `ip -br link`),
  mises à jour faites, adresse du plan.

**Procédure professionnelle** : vérifier la compatibilité, sauvegarder, régler le firmware,
installer, mettre à jour, raccorder, tester avec l'utilisateur.

**Erreur fréquente** : garder un système qui ne reçoit plus de mises à jour ; réinstaller sans
sauvegarde vérifiée ; laisser le profil réseau « Public », qui bloque le partage.

**À l'écrit** : « LINUX1 non compatible Windows 11 (processeur hors liste, pas de TPM) →
Ubuntu 24.04 LTS, mode UEFI, partition EFI + racine ext4 ; partage smb://{SERVER_IP}/Etudes. »

**Repère rapide** : **compatibilité · sauvegarde · firmware · installer · mettre à jour ·
raccorder · tester avec l'utilisateur**. Exercices liés : {_ex("E03", "E12")}.
"""


def _wifi_security() -> str:
    good = sum(1 for _t, k in SECURITY_ITEMS if k == SEC_GOOD)
    return f"""**Objectifs** : configurer le Wi-Fi du personnel et des invités ; vérifier la couverture ;
lister les mesures de sécurité de toute l'installation.

## 7.1 Deux réseaux, un point d'accès

- **{SSID_PRO}** (personnel) : WPA2/WPA3-Personnel (AES), clé longue (une phrase de plus de
  20 caractères, sans le nom du cabinet), WPS coupé, mot de passe d'administration changé ;
  réseau {NETWORK}.
- **{SSID_GUEST}** (invités) : VLAN {GUEST_VLAN} ({GUEST_NETWORK}), Internet seulement,
  isolé du réseau du personnel et des autres invités ; clé changée régulièrement.
- **Canaux** : 2,4 GHz sur le canal **{CHANNEL_24}** (1 et 6 occupés par des voisins forts),
  20 MHz ; 5 GHz sur le canal **{CHANNEL_5}**, sans détection radar ([PR25](/uaa/ampcr-pratique-pr25)).
- Point d'accès AP-01 au plafond du couloir, adresse de gestion {AP_IP}, alimenté par PoE.

{_neighbors_table()}

**Variante acceptée** : si le matériel ne gère pas les VLAN, la fonction « réseau invités » du
point d'accès (isolation des clients, accès au réseau local bloqué) est correcte **si elle est
vérifiée** à la recette.

## 7.2 Couverture

{_fig(SURVEY_FIGURE)}

{_survey_table()}

Au pire, {WORST_5} dBm en 5 GHz : **un seul point d'accès suffit**. Ce n'est qu'une estimation :
la recette mesure le signal aux mêmes points.

## 7.3 Sécurité de l'installation

{_fig(SECURITY_FIGURE)}

Sur les {len(SECURITY_ITEMS)} pratiques relevées pendant le chantier, {good} protègent vraiment
le réseau ; les autres sont de **fausses sécurités** (SSID masqué, miroir pris pour une
sauvegarde) ou des pratiques à **proscrire** (compte administrateur partagé, secrets écrits dans
le rapport).

**Procédure professionnelle** : configurer, auditer la fiche, mesurer, cocher la liste de
sécurité, remettre les identifiants **sous pli** au client.

**Erreur fréquente** : mettre les invités sur le réseau du personnel ; masquer le SSID en guise
de protection ; écrire la clé Wi-Fi dans le rapport.

**À l'écrit** : « {SSID_GUEST} : VLAN {GUEST_VLAN}, Internet seul ; test à la recette : un
smartphone invité ouvre un site, mais pas `\\\\{SERVER_IP}`. »

**Repère rapide** : **deux SSID · WPA2/WPA3 · WPS coupé · invités isolés · 1, 6 ou 11 ·
mesurer · secrets sous pli**. Exercices liés : {_ex("E14", "E15", "E16")}.
"""


def _commissioning() -> str:
    lines = "\n".join(_md(f"- **{name}** : {RECETTE_DIAG[name]} — relevé : {RECETTE_EVIDENCE[name]}.")
                      for name in ("COMPTA", "ETUDES2", "LINUX1"))
    checks = ", ".join(_lc(f.name) for f in required_checks(FINAL_REPORT.kind))
    ram = "\n".join(f"{i}. **{label}** — {detail}" for i, (label, detail) in enumerate(RAM_FAULT_STEPS, start=1))
    return f"""**Objectifs** : diagnostiquer une panne matérielle et une panne logicielle ; mener la recette
avec le client ; conclure et rédiger le rapport.

## 8.1 Une panne matérielle : ETUDES1 après l'ajout de mémoire

Après l'ajout de deux barrettes, la station ne montre plus d'image et émet des bips longs
répétés (défaut de mémoire selon le manuel de la carte mère). On applique la démarche de
[PR06](/uaa/ampcr-pratique-pr06), une modification à la fois :

{ram}

## 8.2 La recette

{_fig(RECETTE_PROC_FIGURE)}

{_fig(TREE_FIGURE)}

{_fig(RECETTE_FIGURE)}

Trois postes échouent à la première recette, chacun pour une cause différente :

{lines}

La panne de COMPTA est **logicielle** : le poste présente au serveur l'identifiant enregistré
SRV-01\\{STORED_LOGIN}, qui n'a **{STORED_ACCESS.lower()}** à Compta ; avec le compte du
comptable, le droit est **{RIGHT_ACCESS.lower()}**. On supprime l'identifiant enregistré ; on ne
touche pas aux droits.

## 8.3 Conclure : verdict, réserve et rapport

Contrôles exigés pour ce type d'intervention ([PR29](/uaa/ampcr-pratique-pr29)) : {checks}.

{_final_measures_table()}

**Verdict** : {FINAL_REPORT.verdict}. **Décision** : {FINAL_REPORT.decision}.

**Procédure professionnelle** : critères écrits avant, liens puis postes, une correction à la
fois, recette refaite après chaque correction, verdict, réserve écrite, PV signé.

**Erreur fréquente** : faire signer « sans réserve » alors qu'un test n'a pas pu être fait ;
élargir les droits pour faire disparaître un « Accès refusé » ; chercher dans Windows une panne
de câble.

**À l'écrit** : « Coupure de courant : non testée (heures de bureau) → non concluant ; réserve
écrite, test le samedi 7/11 avec la directrice. »

**Repère rapide** : **premier échec = piste · une correction · refaire la recette · verdict ·
réserve écrite · PV signé**. Exercices liés : {_ex("E13", "E17", "E18", "E20", "E21", "E23")}.
"""


# --- Huit études de cas -------------------------------------------------------------------------


def _case_head(number: int) -> str:
    c = next(case for case in CASES if case.number == number)
    return f"""## Cas {c.number} — {c.title} (niveau {c.level})

**Exigences officielles** : {_reqs_line(c.official)}.
**Compléments** : {_complements_line(c.complements)}.
"""


def _case1() -> str:
    return f"""{_case_head(1)}
**Énoncé.** À partir de la demande et du plan (chapitre 1) : 1) dresse l'inventaire du matériel
réseau et dimensionne switch, panneau, baie et câble ; 2) choisis le système de chaque poste ;
3) présente le budget indicatif par postes de dépense.

**Corrigé.**

1. Switch : {LINKS} liens aujourd'hui → {PORTS_NOW} ports ; {LINKS + FUTURE_POSTES} à terme →
   {PORTS_LATER} ports → **{SWITCH_PORTS} ports** administrable PoE+. Panneau : **{PANELS} × 24
   ports**. Câble : {TOTAL_CABLE_M} m → **{CABLE_BOXES} boîte**. Baie : {RACK_USED_U} U →
   **{RACK_U} U**. PoE : {_fr(POE_NEED_W)} W sur {SWITCH_POE_BUDGET_W:g} W.
2. Windows 11 Pro sur ACCUEIL, DIRECTION, ETUDES1, ETUDES2 ; COMPTA après activation du TPM ;
   **Ubuntu 24.04 LTS** sur LINUX1 (non compatible) ; {SERVER_OS} sur SRV-01.
3. Quatre postes de dépense (tableau du chapitre 2), quantités et justifications, **aucun prix**.

**Variantes acceptées** : un NAS à la place du serveur Windows (droits par utilisateur et par
groupe, à justifier) ; un switch de 16 ports **plus** un second plus tard, si le client refuse
l'investissement et que c'est écrit ; Ubuntu ou une autre distribution LTS maintenue.
"""


def _case2() -> str:
    return f"""{_case_head(2)}
**Énoncé.** 1) Décris le câble, la pose et le raccordement ; 2) donne la longueur de câble et
le repérage ; 3) interprète le rapport du testeur (chapitre 3).

**Corrigé.**

1. Cat6 U/UTP monobrin, faux plafond et goulottes, séparé du courant fort, rayon de courbure
   respecté ; prises et panneau en **T568B** : blanc-orange, orange, blanc-vert, bleu,
   blanc-bleu, vert, blanc-marron, marron ; détorsadage minimal.
2. {TOTAL_CABLE_M} m (parcours + 3 m + 2 m de réserve par lien), plus long lien
   {LONGEST_RUN[2]} m ; repère B1-P1-01 à B1-P1-{LINKS:02d}, identique à la prise et au panneau,
   port n du panneau → port n du switch.
3. Neuf liens conformes ; **P08 : fil 6 ouvert** → prise refaite, lien retesté avant de
   brancher LINUX1.

**Variantes acceptées** : T568A partout ; câble F/UTP avec mise à la terre de la baie ; repérage
par salle (A01…B05) s'il est identique aux deux bouts et reporté au tableau de brassage.
"""


def _case3() -> str:
    errors = _sentences(DRAFT_ERRORS)
    return f"""{_case_head(3)}
**Énoncé.** 1) Établis le plan d'adressage ; 2) règle le DHCP et le DNS ; 3) corrige le
brouillon d'un collègue (document de l'exercice E07).

**Corrigé.**

1. Réseau {NETWORK} ; box {ROUTER_IP}, switch {SWITCH_IP}, point d'accès {AP_IP}, serveur
   {SERVER_IP}, imprimante {HOSTS[4].ip} en adresses fixes ; postes par DHCP.
2. Étendue {POOL[0]}–{POOL[1]} ({POOL_SIZE} adresses), bail {LEASE_HOURS} h, passerelle et DNS
   {ROUTER_IP} ; invités : {GUEST_NETWORK} sur le VLAN {GUEST_VLAN}.
3. Erreurs relevées par les règles de PR20 : {errors}

**Variantes acceptées** : un autre réseau privé (10.x, 172.16-31.x) cohérent ; des réservations
DHCP au lieu d'adresses fixes, si elles sont notées dans le dossier ; le DHCP sur le serveur
plutôt que sur la box, à condition de le couper sur la box (une seule source DHCP).
"""


def _case4() -> str:
    return f"""{_case_head(4)}
**Énoncé.** 1) Groupe de travail ou domaine, aujourd'hui et dans deux ans avec des stagiaires ?
2) Crée comptes, groupes et partages ; 3) vérifie la matrice des droits.

**Corrigé.**

1. Aujourd'hui : **{_lc(MODEL)}** (six postes stables). Avec des stagiaires qui changent
   souvent : **{MODEL_LATER}** (comptes et règles gérés en un point).
2. Comptes amartin, cdubois, flemaire, jroux, nperrin, tvidal ; groupes G_Administration,
   G_Direction, G_Compta, G_Etudes ; dossiers Commun, Administration, Etudes, Compta sous
   D:\\Partages, partagés « Utilisateurs authentifiés : Modifier ».
3. Matrice calculée (chapitre 5) : conforme aux quatre besoins du client.

**Variantes acceptées** : un domaine dès aujourd'hui si le client veut préparer l'extension
(justifié, coût du contrôleur de domaine signalé) ; les droits posés sur le partage plutôt que
sur NTFS, si l'effet est identique et justifié.
"""


def _case5() -> str:
    return f"""{_case_head(5)}
**Énoncé.** 1) Décris l'installation de Windows 11 Pro sur ETUDES2 et la mise à niveau de
COMPTA ; 2) celle d'Ubuntu sur LINUX1 ; 3) le raccordement de chaque poste au serveur et à
l'imprimante.

**Corrigé.**

1. ETUDES2 : firmware en UEFI, TPM et démarrage sécurisé actifs, installation propre en GPT,
   compte de l'utilisatrice, Windows Update, pilotes du fabricant, profil « Privé ». COMPTA :
   **sauvegarde vérifiée**, TPM activé, mise à niveau sur place, contrôle des logiciels.
2. LINUX1 : image vérifiée, mode UEFI, partition EFI + racine ext4, mises à jour, adresse DHCP
   du plan.
3. Windows : lecteur réseau vers `\\\\SRV-01\\Etudes` (ou le dossier du service), imprimante par
   IP ; Ubuntu : `smb://{SERVER_IP}/Etudes`, imprimante par IP ; test avec chaque utilisateur.

**Variantes acceptées** : installation propre de COMPTA (après sauvegarde et accord) ; une autre
distribution LTS ; un montage permanent du partage sous Ubuntu (fstab, cifs) s'il est justifié.
"""


def _case6() -> str:
    ram = "\n".join(f"   {i}. {label} : {_lc(detail)}" for i, (label, detail) in enumerate(RAM_FAULT_STEPS, start=1))
    return f"""{_case_head(6)}
**Énoncé.** 1) ETUDES1 ne montre plus d'image après l'ajout de mémoire : rédige le diagnostic ;
2) COMPTA reçoit « Accès refusé » sur Compta : explique la cause et la correction.

**Corrigé.**

1. Diagnostic, une modification à la fois :

{ram}

2. Le poste présente au serveur l'identifiant enregistré SRV-01\\{STORED_LOGIN} (droit :
   {STORED_ACCESS.lower()}) au lieu de celui du comptable ({RIGHT_ACCESS.lower()}). On supprime
   l'identifiant enregistré (Gestionnaire d'identification ou `cmdkey /delete:SRV-01`), on se
   reconnecte avec flemaire, on teste en écriture ; les droits du serveur ne changent pas.

**Variantes acceptées** : essai des barrettes dans une autre machine compatible ; pour COMPTA,
`net use \\\\SRV-01 /delete` puis reconnexion avec les bons identifiants.
"""


def _case7() -> str:
    return f"""{_case_head(7)}
**Énoncé.** 1) Configure le Wi-Fi du personnel et des invités ; 2) vérifie la couverture ;
3) liste les mesures de sécurité de l'installation.

**Corrigé.**

1. {SSID_PRO} : WPA2/WPA3-Personnel, clé longue remise sous pli, WPS coupé ; {SSID_GUEST} :
   VLAN {GUEST_VLAN}, Internet seul, isolé ; canal {CHANNEL_24} en 2,4 GHz (20 MHz), canal
   {CHANNEL_5} en 5 GHz ; mot de passe d'administration changé, micrologiciel à jour.
2. Estimation : {WORST_5} dBm au pire en 5 GHz ≥ −67 : un point d'accès suffit ; mesure à la
   recette.
3. Liste du chapitre 7 : équipements (mots de passe, mises à jour, baie à clé), comptes et
   données (compte par personne, droits, sauvegarde externe testée), postes et Wi-Fi.

**Variantes acceptées** : WPA2-Personnel seul si un appareil ne gère pas WPA3 ; WPA3-Entreprise
avec un serveur d'authentification, si le client l'accepte ; réseau invités par la fonction du
point d'accès, vérifiée à la recette.
"""


def _case8() -> str:
    return f"""{_case_head(8)}
**Énoncé.** À la recette, COMPTA, ETUDES2 et LINUX1 échouent (chapitre 8) : 1) donne la piste de
chacun ; 2) les corrections ; 3) le verdict et la décision ; 4) les rubriques principales du
rapport final et le message à la directrice.

**Corrigé.**

1. COMPTA : {_lc(RECETTE_DIAG["COMPTA"])} ; ETUDES2 : {_lc(RECETTE_DIAG["ETUDES2"])} ;
   LINUX1 : {_lc(RECETTE_DIAG["LINUX1"])}.
2. Identifiant enregistré supprimé ; port 7 remis dans le VLAN du personnel ; prise P08 refaite
   et retestée ; recette complète refaite sur les trois postes.
3. {FINAL_REPORT.verdict} ; {FINAL_REPORT.decision.lower()}.
4. Rapport complet :

{_final_report_table()}

Message à la directrice : « {FINAL_REPORT.client_message} »

**Variantes acceptées** : toute formulation du rapport qui reprend les quatorze rubriques ; une
date de test différente, si elle est fixée avec le client.
"""


def _cases_a() -> str:
    return f"""Les huit cas suivent les phases du laboratoire et montent en difficulté : **niveau 1**
(dimensionner, appliquer une règle), **niveau 2** (concevoir et contrôler), **niveau 3**
(diagnostiquer), **niveau 4** (recette complète et rapport). Rédige ta réponse **avant** de lire
le corrigé ; une solution différente est acceptée **si elle est justifiée**.

{_requirements_table()}

{_case1()}

{_case2()}

{_case3()}

{_case4()}
"""


def _cases_b() -> str:
    return f"""{_case5()}

{_case6()}

{_case7()}

{_case8()}
"""


def _pitfalls() -> str:
    return """> **Dimensionner pour aujourd'hui** alors que l'extension est écrite dans la demande.

> **Inventer des prix** : le budget indicatif présente des quantités par poste de dépense.

> **Mélanger T568A et T568B** dans une même installation, ou brancher les postes sans avoir testé les liens.

> **Placer une adresse fixe dans l'étendue DHCP**, ou donner un masque différent à un équipement.

> **« Tout le monde : contrôle total »** pour faire disparaître un « Accès refusé ».

> **Garder Windows 10** sans mises à jour, ou réinstaller sans sauvegarde vérifiée.

> **Mettre les invités sur le réseau du personnel** ; masquer le SSID en guise de protection.

> **Prendre le miroir des disques pour une sauvegarde.**

> **Lire tous les contrôles d'une recette** au lieu du premier échec.

> **Faire signer « sans réserve »** alors qu'un test n'a pas pu être fait.

> **Écrire une clé Wi-Fi ou un mot de passe** dans le rapport.
"""


def _exercises_intro() -> str:
    return f"""{len(PRACTICE_ITEMS)} exercices corrigés, **transversaux** : chacun reprend une phase du
dossier de la PME — **inventaire et budget**, **câblage et recette des liens**, **plan IPv4 et
DHCP**, **comptes et droits**, **systèmes**, **pannes de mise en service**, **Wi-Fi et
sécurité**, **recette**, **rapport** et **lien avec les exigences officielles** ; deux
**schémas à compléter** (baie, arbre de recette), deux **procédures à ordonner** et un
**parcours d'arbre**. Rédige ta réponse sur papier **avant** d'ouvrir le corrigé ; toute
réponse équivalente et justifiée est acceptée. Ces mêmes exercices sont proposés dans
[S'entraîner](/uaa/{PR30_SLUG}/practice), avec correction après envoi.

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
    return f"""Le mini-examen se passe dans l'onglet [Examen blanc](/uaa/{PR30_SLUG}/exam) : **10 questions à réponse
libre**, chacune notée sur **2 points**, soit une note sur **{EXAM_TOTAL_POINTS}**. Les
questions ne figurent pas dans ce cours.

| N° | Thème | Type | Points |
|---|---|---|---|
{rows}

**Déroulement.** Chaque question est une situation complète : toutes les données nécessaires
sont dans l'énoncé et ses documents (longueurs, relevés, configurations, fiches de recette).
**Aucune correction n'est visible pendant la passation** ; tes réponses sont enregistrées au
fur et à mesure. Après l'envoi, chaque réponse est corrigée selon le **barème analytique** de
la question, puis tu vois ta note sur {EXAM_TOTAL_POINTS}, le corrigé et le barème.

**Ce que valorise le barème.** Des **calculs montrés**, un **diagnostic** qui suit l'ordre des
contrôles, une **décision justifiée**, des **variantes** acceptées si elles sont argumentées, et
un message **compréhensible** par le client.

**Nature de la correction.** Les réponses rédigées reçoivent une **proposition de correction
automatique** (assistée par IA) appuyée sur le barème : c'est un repère d'entraînement, pas une
note officielle ; en cas de doute, compare ta réponse au corrigé.
"""


def _memo() -> str:
    return f"""## Mémo

- **Dossier** : demande → besoins vérifiables → contraintes → huit phases → dossier remis.
- **Dimensionner** : liens + 20 % + cordons directs → taille standard ; extension comprise ;
  baie + 25 % ; câble par boîtes de 305 m sans raboutage.
- **Budget** : quantités par poste de dépense (actif, passif, licences, main-d'œuvre) ; prix =
  devis.
- **Câblage** : Cat6, T568B partout, même repère aux deux bouts, chaque lien testé.
- **IPv4** : {NETWORK}, fixes hors étendue {POOL[0]}–{POOL[1]}, passerelle et DNS {ROUTER_IP}.
- **Comptes** : modèle selon le scénario ; un compte par personne ; droits aux groupes ; NTFS
  décide ; tester avec chaque compte.
- **Systèmes** : compatibilité, sauvegarde, firmware, installation, mises à jour, raccordement.
- **Wi-Fi** : deux SSID, WPA2/WPA3, WPS coupé, invités isolés, canal 1, 6 ou 11, mesure.
- **Recette** : liens, puis postes (lien, adresse, passerelle, serveur, Internet, partage) ;
  premier échec = piste ; verdict ; réserve ; PV.

## Glossaire des termes employés

- **Budget indicatif** : quantités et postes de dépense, sans prix, à compléter par des devis.
- **Étendue DHCP** : plage d'adresses que le serveur DHCP distribue automatiquement.
- **Lien permanent** : câble fixe entre la prise murale et le panneau (90 m au plus).
- **Matrice des droits** : tableau comptes × dossiers des droits effectifs.
- **Procès-verbal (PV) de recette** : document signé par le client qui constate le résultat.
- **Recette** : vérification, avec le client, de l'installation sur des critères écrits.
- **Réserve** : limite écrite sur la réception, avec un test complémentaire daté.
- **VLAN** : réseau logique séparé sur le même switch (ici, les invités).
"""


def _sources() -> str:
    not_covered = ", ".join(NOT_COVERED_OFFICIAL)
    return f"""## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles) : épreuve « uniquement par écrit » (p. 3) ; pp. 5-6, exigences
  AP-36 (câblage et installation physique), AP-37 (dépannage de l'accès au réseau), AP-38
  (création d'un mini réseau) et celles citées par chaque cas. Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
  Programme officiel n° 345/2007/249 (option AMPCR).
- **Normes de câblage** TIA-568 (codes T568A/T568B, lien permanent de 90 m, canal de 100 m).
- **Documentation Microsoft** : configuration requise de Windows 11, fin de prise en charge de
  Windows 10 (14 octobre 2025), `ipconfig`, `cmdkey`, partages et autorisations NTFS.
- **Documentation Ubuntu** : configuration recommandée d'Ubuntu Desktop, `ip`, partages SMB.
- **Wi-Fi Alliance / IEEE 802.11** : WPA2, WPA3, canaux 2,4 et 5 GHz en Europe.

Les dimensionnements, le contrôle du plan IPv4, la matrice des droits, les compatibilités, les
défauts de la fiche Wi-Fi, le choix du canal, la couverture estimée, les verdicts des liens,
les diagnostics de recette, le verdict et la décision sont **produits par programme** avec les
règles déjà vérifiées des cours PR07, PR18, PR20, PR22, PR23, PR25, PR27 et PR29 ; les schémas
en sont construits directement. Aucun schéma n'est tiré d'une image générée ni d'une
photographie.

## Compléments pédagogiques (non imposés par la liste officielle)

Ce laboratoire couvre {len(COVERED_OFFICIAL)} des 38 exigences officielles. Sont des
**compléments**, signalés comme tels : la rédaction du rapport et du PV (AP-C01), la sécurité
électrique (AP-C02), la protection des données (AP-C03), le budget par postes de dépense,
l'onduleur, le VLAN invités et la sauvegarde externe.

Non travaillées dans ce dossier, parce qu'elles relèvent d'autres cours : {not_covered}
(voir les cours PR02 à PR06, PR16, PR17 et PR21).

## Supports fictifs

{COMPANY}, ses locaux, son personnel, ses équipements, ses adresses MAC, ses relevés et ses
rapports sont **fictifs** et reconstitués pour l'entraînement ; l'adresse publique {WAN_IP}
vient de la plage de documentation RFC 5737. La clé Wi-Fi d'exemple ({len(PASSPHRASE_PRO)}
caractères) n'est jamais écrite dans un rapport. Aucun cas n'est une question officielle ou
déjà posée par le Jury.
"""


def pr30_course_sections() -> list[tuple[str, str]]:
    """Blocs du cours (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("PR30 — Objectifs et place dans l'épreuve", _objectives()),
        ("PR30 — 1. Le dossier de la PME : demande, plan et contraintes", _dossier()),
        ("PR30 — 2. Inventaire, dimensionnement et budget indicatif", _inventory()),
        ("PR30 — 3. Câblage T568B, baie, brassage et recette des liens", _cabling()),
        ("PR30 — 4. Plan IPv4, DHCP et DNS", _addressing()),
        ("PR30 — 5. Groupe de travail ou domaine, comptes, partages et droits", _accounts()),
        ("PR30 — 6. Installation des systèmes et raccordement des postes", _systems()),
        ("PR30 — 7. Wi-Fi du personnel et des invités, sécurité de l'installation", _wifi_security()),
        ("PR30 — 8. Pannes de mise en service, recette et rapport final", _commissioning()),
        ("PR30 — Exemples : études de cas 1 à 4 (niveaux 1 et 2), corrigées", _cases_a()),
        ("PR30 — Exemples : études de cas 5 à 8 (niveaux 3 et 4), corrigées", _cases_b()),
        ("PR30 — Pièges et erreurs fréquentes", _pitfalls()),
        (f"PR30 — Exercices corrigés ({len(PRACTICE_ITEMS)}) et leurs corrigés", _exercises_intro()),
        ("PR30 — Mini-examen noté sur 20 : mode d'emploi", _mini_exam()),
        ("PR30 — Fiche mémo et glossaire", _memo()),
        ("PR30 — Sources et compléments pédagogiques", _sources()),
    ]
