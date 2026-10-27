"""Cours PR26 « Analyser une demande d'intervention technique » — parcours AMPCR pratique écrite
(ticket #225).

Matière : intégralement celle du ticket #225 (recueil de la demande du client, symptômes et
interprétation, contexte matériel / logiciel / réseau, utilisateurs touchés, date, changements
récents, impact et urgence, priorisation, inventaire et références, consentement et
confidentialité, sauvegarde, risques et autorisation ; reformulation, questions utiles, fiche
d'incident, critères de réussite, plan d'action, estimation et escalade ; panne reproductible ou
intermittente, observation ou hypothèse ; cinq dossiers entièrement corrigés : PC inerte,
impression, lenteur, accès partagé, Wi-Fi ; formulaires professionnels et grille d'évaluation),
découpée en blocs titrés (le titre pilote le type de carte, `app.card_kind` : aucun titre de
bloc théorique ne contient « examen », « source », « ressource », « exemple », « exercice »,
« méthode », « piège », « attention », « transfert » ni « mémo »).
Règles, formulaires et schémas : `app.v1.ampcr_pratique_pr26_figures` ; exercices et
mini-examen : `app.v1.ampcr_pratique_pr26_bank`. Les dossiers renvoient aux cours techniques
publiés (PR06, PR12, PR23, PR24, PR25) pour le diagnostic lui-même.
"""

from html import escape

from app.v1.ampcr_pratique_pr06_course import _exercise_card, _fig, _req
from app.v1.ampcr_pratique_pr26_bank import EXAM_ITEMS, EXAM_TOTAL_POINTS, PRACTICE_ITEMS
from app.v1.ampcr_pratique_pr26_figures import (
    ANALYSIS_FIGURE,
    DOSSIERS,
    ESCALATION_CHECKS,
    ESCALATION_FIGURE,
    ESCALATION_PROC_FIGURE,
    EVAL_GRID,
    EVAL_TOTAL,
    FIELDS_BY_KEY,
    FORM_FIGURE,
    HIGH,
    IMPACT_LABELS,
    IMPACT_RULES,
    INCIDENT_FIELDS,
    INTERVIEW_FIGURE,
    LEVELS,
    LOW,
    MARGIN,
    MATRIX_FIGURE,
    MEDIUM,
    OBS_FIGURE,
    PRIORITIES,
    PRIORITY_DELAYS,
    PRIORITY_LABELS,
    PROCEDURES,
    QUESTIONS,
    SECTIONS,
    STATIC_FIGURES,
    URGENCY_LABELS,
    URGENCY_RULES,
    USEFUL,
    WRITTEN_AT,
    Dossier,
    estimate,
    fr,
    hm,
    priority,
    priority_text,
)
from app.v1.ampcr_pratique_visuals import render_figure

PR26_TITLE = "Analyser une demande d'intervention technique"
PR26_SLUG = "ampcr-pratique-pr26"

_SCHEMAS_BY_PATH = {path: figure for figure, path in STATIC_FIGURES}


def _card(number: int, item) -> str:
    """Carte d'exercice de PR06 ; un schéma à compléter est affiché (SVG) avant sa
    description textuelle."""
    html = _exercise_card(number, item, anchor_prefix="pr26")
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


def _impact_table() -> str:
    rows = [(IMPACT_LABELS[level], IMPACT_RULES[level]) for level in LEVELS]
    return _html_table(("Impact", "Règle"), rows)


def _urgency_table() -> str:
    rows = [(URGENCY_LABELS[level], URGENCY_RULES[level]) for level in LEVELS]
    return _html_table(("Urgence", "Règle"), rows)


def _delays_table() -> str:
    return _html_table(("Priorité", "Délai de prise en charge (convention du cours)"),
                       [(PRIORITY_LABELS[p], PRIORITY_DELAYS[p]) for p in PRIORITIES])


def _form_table() -> str:
    rows = [(f.section, f.label + ("" if f.required else " (facultatif)"), f.why) for f in INCIDENT_FIELDS]
    return _html_table(("Section", "Rubrique", "À quoi elle sert"), rows, caption="Fiche d'incident — rubriques")


def _grid_table() -> str:
    rows = [(label, str(points), detail) for _k, label, points, detail in EVAL_GRID]
    rows.append(("Total", str(EVAL_TOTAL), "acquis = tous les points ; partiel = la moitié ; absent = 0"))
    return _html_table(("Critère", "Points", "Attendu"), rows, caption="Grille d'évaluation d'une fiche d'incident")


def _questions_table() -> str:
    return _html_table(("Question", "Verdict", "Pourquoi"), [(q, k, w) for q, k, w in QUESTIONS])


def _checks_table() -> str:
    return _html_table(("Contrôle", "Si non"),
                       [(f"{i}. {q}", a) for i, (_k, q, a) in enumerate(ESCALATION_CHECKS, start=1)])


# =============================================================================================
# Cinq dossiers entièrement corrigés (données et décisions calculées par le module de figures)
# =============================================================================================


def _dossier_html(number: int, d: Dossier) -> str:
    rows = []
    for key, value in d.fiche:
        if key == "plan":
            value = f"{value} — durée annoncée {hm(d.estimate_minutes)}"
        rows.append((FIELDS_BY_KEY[key].label, value))
    tasks = " + ".join(f"{m}" for _t, m in d.tasks)
    total = sum(m for _t, m in d.tasks)
    questions = "\n".join(f"- *{escape(q)}* — {escape(a)}" for q, a in d.questions)
    observations = " ; ".join(d.observations)
    hypotheses = " ; ".join(d.hypotheses)
    criteria = "\n".join(f"- {c}" for c in d.criteria)
    decision = (
        "aucun contrôle en échec : intervention directe"
        if d.escalation is None
        else "contrôle « " + next(q for k, q, _a in ESCALATION_CHECKS if k == d.escalation)
        + " » en échec : " + next(a for k, _q, a in ESCALATION_CHECKS if k == d.escalation)
    )
    return f"""## Dossier {number} — {d.title}

**Demande reçue.** {d.request}

**1. Questions posées et réponses obtenues.**

{questions}

**2. Qualification.** Observations : {observations}. Hypothèses (à tester) : {hypotheses}.
Fréquence : **{d.occurrence.lower()}**.

**3. Priorité.** {priority_text(d.impact, d.urgency)}.

**4. Critères de réussite.**

{criteria}

**5. Plan et estimation.** Tâches : {tasks} = {total} min ; + {int(MARGIN * 100)} % = {fr(total * (1 + MARGIN))} min ;
arrondi au quart d'heure supérieur : **{hm(d.estimate_minutes)}**.

**6. Escalade.** {decision}.

**Fiche d'incident complétée :**

{_html_table(("Rubrique", "Contenu"), rows, caption=f"Fiche {d.field('numero')} (support fictif)")}

**Conclusion rédigée.** « {d.conclusion} »
"""


# =============================================================================================
# Sections du cours (titre du bloc, Markdown / HTML)
# =============================================================================================


def _objectives() -> str:
    return f"""## Ce que tu sauras faire, par écrit

L'épreuve pratique AMPCR se passe **uniquement par écrit** (consignes officielles 2026-2027/1,
p. 3). Avant tout diagnostic, un dossier d'examen commence presque toujours par une **demande** :
un appel, un courriel, un ticket. On attend de toi que tu la transformes en une **fiche
d'incident** exploitable, avec les bons mots. Tu dois savoir :

1. **recueillir** une demande : demandeur, date, symptômes dits avec ses mots, et séparer les
   **symptômes** de l'**interprétation** du client ;
2. relever le **contexte matériel, logiciel et réseau**, l'**inventaire** et les **références**
   de l'appareil, les **utilisateurs touchés** et les **changements récents** ;
3. **qualifier** : distinguer **observation** et **hypothèse**, panne **reproductible** ou
   **intermittente** ;
4. évaluer **impact** et **urgence**, et en déduire la **priorisation** ;
5. traiter **consentement et confidentialité**, **sauvegarde**, **risques et autorisation** ;
6. poser les **questions utiles**, faire une **reformulation** et la faire valider ;
7. rédiger la **fiche d'incident**, les **critères de réussite**, le **plan d'action** et
   l'**estimation** ;
8. décider d'une **escalade** et la rédiger.

Ce cours contient **{len(PROCEDURES)} procédures illustrées** :

{_procedures_list()}

## Exigences travaillées dans ce cours

{_req("AP-16")}
{_req("AP-C01")}

AP-16 est une exigence **officielle** (consignes, p. 5) ; AP-C01 est un **complément** du
parcours (méthode de rédaction : l'épreuve se fait uniquement par écrit). La protection des
données du client (AP-C03) est reprise au chapitre 5.

## Lien avec la théorie et les autres cours

La théorie AMPCR présente la relation avec le client et le compte rendu :
[MC36 Communication client et rapport technique](/uaa/ampcr-mc36). Ce cours-ci est
**pratique** : demandes, tickets, courriels et fiches à analyser et à rédiger, comme dans un
dossier d'examen. Il prépare le **diagnostic** lui-même, traité dans les cours techniques :
pannes matérielles ([PR06](/uaa/ampcr-pratique-pr06)), dépannage logiciel
([PR12](/uaa/ampcr-pratique-pr12)), partages ([PR23](/uaa/ampcr-pratique-pr23)), réseau
([PR24](/uaa/ampcr-pratique-pr24)) et Wi-Fi ([PR25](/uaa/ampcr-pratique-pr25)).

## Comment travailler ce cours

Lis les chapitres dans l'ordre : chacun donne ses **objectifs**, la **théorie**, la
**procédure professionnelle** à rédiger, l'**erreur fréquente**, ce qu'on attend **à l'écrit**
et un **repère rapide**, avec un renvoi vers les exercices liés. Étudie ensuite les **cinq
dossiers entièrement corrigés**, fais les **{len(PRACTICE_ITEMS)} exercices corrigés** (rédaction,
analyse de tickets, qualification, deux **schémas à compléter**), puis passe le **mini-examen
noté sur {EXAM_TOTAL_POINTS}** dans l'onglet « Examen blanc ».

> **Important —** les personnes, entreprises, demandes et numéros de ce cours sont des
> **supports fictifs** construits pour s'entraîner (rédaction : {WRITTEN_AT}). La matrice de
> priorité, les délais, la marge d'estimation et la grille sur 20 sont des **conventions du
> cours** : chaque entreprise ou centre de services fixe les siens, et **la procédure de
> l'entreprise fait foi**. Aucun exercice n'est une question officielle ni une question déjà
> posée par le Jury.
"""


def _collect() -> str:
    return f"""**Objectifs** : noter une demande sans la déformer ; séparer ce que dit le client de ce qu'il
en pense.

## 1.1 La démarche complète

{_fig(ANALYSIS_FIGURE)}

Les neuf étapes de la procédure 1 structurent tout le cours : chaque chapitre en détaille une ou
deux, et chacune laisse une trace sur la fiche d'incident.

## 1.2 Ce que contient une demande

Une **demande d'intervention** (appel, courriel, ticket, visite) contient presque toujours trois
choses mélangées :

- des **symptômes** : ce que la personne voit, entend, lit (« aucun voyant », « le message
  Imprimante hors ligne ») ;
- une **interprétation** : la cause qu'elle suppose (« c'est la carte mère », « un virus ») ;
- une **attente** et une **échéance** (« il me le faut pour la TVA d'aujourd'hui »).

On note d'abord la demande **telle qu'elle est dite**, avec le **demandeur** (nom, service,
moyen de rappel), la **date et l'heure** de la demande. Puis on range chaque élément à sa place
sur la fiche : les symptômes dans « Symptômes observés », l'interprétation dans les hypothèses,
l'échéance dans l'urgence.

## 1.3 Symptômes et interprétation

Le client a souvent raison sur **ce qu'il voit**, et parfois tort sur **la cause**. Recopier
« carte mère HS » comme symptôme engage tout le diagnostic dans une seule direction. On garde
son avis, **noté comme hypothèse**, et on le vérifie ensuite.

**Procédure professionnelle** : 1) noter mot pour mot la demande ; 2) souligner les faits ;
3) entourer les avis et les causes supposées ; 4) relever l'échéance ; 5) compléter les rubriques
correspondantes de la fiche.

**Erreur fréquente** : écrire « PC en panne » ou « réseau HS » dans la rubrique « Symptômes » :
ce sont des conclusions, pas des faits.

**À l'écrit** : « Symptômes : aucun voyant ni ventilateur à l'appui sur le bouton. Hypothèse de
la demandeuse : carte mère. »

**Repère rapide** : **ce que l'on voit → symptômes · ce que l'on croit → hypothèses · ce que
l'on attend → urgence**. Exercices liés : {_ex("E02", "E10", "E11")}.
"""


def _context() -> str:
    return f"""**Objectifs** : identifier sans erreur l'appareil, son environnement et ce qui a changé.

## 2.1 Contexte matériel, logiciel et réseau

Avant de se déplacer, on relève :

- **matériel** : type d'appareil, modèle, périphériques concernés ;
- **logiciel** : système d'exploitation, logiciel utilisé au moment du problème ;
- **réseau** : câble ou Wi-Fi, serveur ou partage utilisé, imprimante réseau.

Ces informations orientent vers le bon cours technique : matériel ([PR06](/uaa/ampcr-pratique-pr06)),
système et logiciels ([PR12](/uaa/ampcr-pratique-pr12)), réseau ([PR24](/uaa/ampcr-pratique-pr24)).

## 2.2 Inventaire et références

L'**inventaire** de l'entreprise donne, pour chaque appareil, un **numéro d'inventaire**
(étiquette), le **modèle**, le **numéro de série**, l'**utilisateur** et la **fin de garantie**.
On recoupe toujours le numéro donné au téléphone avec l'inventaire et l'étiquette : intervenir
sur le mauvais appareil fait perdre du temps et peut toucher les données d'une autre personne.
Un appareil **sous garantie** ne s'ouvre pas : on passe par le fabricant (escalade).

## 2.3 Date, changements récents, utilisateurs touchés

- **Date d'apparition** : « depuis lundi matin » situe le problème par rapport aux événements.
- **Changements récents** : mise à jour, nouveau logiciel, déplacement, nettoyage, nouveau
  matériel, réorganisation des droits. C'est souvent **la** cause.
- **Utilisateurs touchés** : une personne, un service, toute l'entreprise. Un seul poste touché
  oriente vers le poste ; tous les postes, vers un équipement commun (serveur, box, licence).

**Procédure professionnelle** : 1) relever la référence citée ; 2) la recouper dans l'inventaire
(utilisateur, modèle, n° de série, garantie) ; 3) noter le contexte ; 4) demander ce qui a
changé ; 5) demander qui d'autre est touché.

**Erreur fréquente** : oublier les **changements récents** ; ou traiter séparément trois tickets
identiques au lieu de voir un incident commun.

**À l'écrit** : « LT-COMPTA-01 (n° de série 5CD2401AB, sous garantie jusqu'au 15/03/2027) ;
Windows 11 ; trois postes de deux services touchés depuis lundi. »

**Repère rapide** : **un poste → le poste · plusieurs postes → l'élément commun · il y a eu un
changement → on commence par lui**. Exercices liés : {_ex("E09", "E16", "E18")}.
"""


def _qualify() -> str:
    return f"""**Objectifs** : distinguer ce qui est constaté de ce qui est supposé ; savoir si l'on peut
reproduire la panne.

## 3.1 Observation ou hypothèse

{_fig(OBS_FIGURE, wide=True)}

- Une **observation** est un **fait vérifiable** : on peut le constater, le lire, le mesurer
  (message exact, voyant, durée mesurée, nombre de personnes).
- Une **hypothèse** est une **cause supposée** : elle explique les observations et se **teste**.
  L'avis du client est une hypothèse, la tienne aussi.

On écrit les observations dans « Symptômes » et les hypothèses à part, **classées de la plus
simple à vérifier à la plus lourde**. Une hypothèse peut être **contredite** par une
observation : un projecteur qui affiche « Aucun signal » sur fond bleu a une lampe qui éclaire.

## 3.2 Panne reproductible ou intermittente

- **Reproductible** : la panne apparaît **à chaque essai dans les mêmes conditions** (à chaque
  démarrage, toujours sur le port de gauche). On peut la montrer, la tester et contrôler tout de
  suite sa disparition.
- **Intermittente** : elle apparaît **de temps en temps**, sans qu'on puisse la provoquer. On la
  rend **observable** par un **journal** (date, heure, message, ce qui était en cours, autres
  personnes touchées) pour trouver ce qui la déclenche (heure, charge, appareil voisin).

Le **critère de réussite** d'une panne intermittente porte sur une **durée** sans incident (une
semaine par exemple), jamais sur un seul essai réussi.

**Procédure professionnelle** : 1) relire les phrases de la demande ; 2) marquer O (observation)
ou H (hypothèse) ; 3) demander « à chaque fois ou de temps en temps ? » ; 4) si intermittente,
mettre en place un journal ; 5) ordonner les hypothèses à tester.

**Erreur fréquente** : déclarer réparée une panne intermittente parce qu'elle ne s'est pas
produite pendant l'intervention.

**À l'écrit** : « Panne intermittente : trois redémarrages en cinq jours, tous pendant un export
vidéo. Hypothèse : surchauffe sous charge. Test : export long avec relevé des températures. »

**Repère rapide** : **O = je l'ai vu · H = je le suppose · à chaque fois = reproductible ·
parfois = journal**. Exercices liés : {_ex("E02", "E03", "E20")}.
"""


def _prioritize() -> str:
    return f"""**Objectifs** : décider de l'ordre de traitement des demandes avec une règle explicable.

## 4.1 Impact et urgence

L'**impact** mesure l'**étendue des conséquences** (combien de personnes, quelle activité) ;
l'**urgence** mesure le **délai avant un dommage réel** (échéance, clients qui attendent).

{_impact_table()}

{_urgency_table()}

Un **contournement** (autre poste, autre imprimante, téléphone) baisse l'impact ; une
**échéance** proche monte l'urgence.

## 4.2 Priorisation : la matrice

{_fig(MATRIX_FIGURE)}

On lit la priorité au croisement de la ligne (impact) et de la colonne (urgence). En chiffres
(1 = élevé, 3 = faible) : 1+1 → P1 ; 1+2 → P2 ; 1+3 ou 2+2 → P3 ; au-delà → P4. La matrice est
**symétrique** : une demande d'une seule personne mais avec une échéance dans l'heure monte en
P3 ({priority_text(LOW, HIGH)}).

{_delays_table()}

**Procédure professionnelle** : 1) compter les personnes touchées et noter le contournement ;
2) noter l'échéance ; 3) choisir impact et urgence ; 4) lire la priorité ; 5) annoncer le délai au
demandeur.

**Erreur fréquente** : reprendre la priorité choisie par l'utilisateur (« URGENT !!! ») sans
la justifier, ou classer en P1 toute demande du directeur.

**À l'écrit** : « Impact moyen (poste d'accueil, deux autres postes peuvent scanner) × urgence
élevée (patients qui attendent) = {PRIORITY_LABELS[priority(MEDIUM, HIGH)]}. »

**Repère rapide** : **impact = combien · urgence = quand · contournement ↓ impact · échéance ↑
urgence**. Exercices liés : {_ex("E04", "E07", "E12", "E16")}.
"""


def _protect() -> str:
    return f"""**Objectifs** : protéger les données et les personnes avant d'agir ; savoir ce que l'on a
le droit de faire.

## 5.1 Sauvegarde

On demande **toujours** : « Où sont vos fichiers ? Existe-t-il une copie récente ? » On note la
réponse sur la fiche (rubrique « Données et sauvegarde »). Sans copie, toute action risquée
(réinstallation, remplacement de disque, réparation du système) commence par une **sauvegarde** ;
un disque mécanique qui **claque** ne se manipule plus : on arrête et on propose un spécialiste
en récupération (voir aussi [PR12](/uaa/ampcr-pratique-pr12)).

## 5.2 Consentement et confidentialité

- Le **consentement** : le client accepte, **par écrit** quand l'action est risquée, ce que l'on
  va faire et l'accès à ses données.
- La **confidentialité** : on ne consulte, ne copie ni ne divulgue aucune donnée au-delà de ce
  que l'intervention exige (courriels, dossiers personnels, données de clients ou de patients) ;
  la copie de sauvegarde est effacée après restitution.
- Les **mots de passe** d'autres personnes ne se communiquent jamais.

## 5.3 Risques et autorisation

On **annonce les risques** (effacement, perte de réglages, durée, coût) et on fait **autoriser**
l'opération par une personne qui en a le droit (client, responsable). L'autorisation décrit
l'opération précise : une réinstallation acceptée n'autorise pas un remplacement de carte mère.

**Modèle de bon d'accord** (à recopier sur la copie d'examen) :

{_html_table(("Rubrique", "Contenu à écrire"), [
        ("Opération autorisée", "description précise (ex. réinstallation de Windows, effacement du disque)"),
        ("Sauvegarde", "dossiers copiés, support, par qui ; ce qui n'est pas garanti"),
        ("Risques annoncés", "effacement, réglages à refaire, durée et coût estimés"),
        ("Confidentialité", "pas de consultation des fichiers ; copie effacée après restitution"),
        ("Suite", "toute autre opération fera l'objet d'un nouvel accord"),
        ("Accord", "nom, date, signature du client ou du responsable"),
    ], caption="Bon d'accord avant une opération risquée (modèle du cours)")}

**Procédure professionnelle** : 1) localiser les données ; 2) vérifier la copie ; 3) annoncer les
risques ; 4) faire signer le bon d'accord ; 5) noter tout sur la fiche avant de commencer.

**Erreur fréquente** : réinstaller « parce que le client a dit de tout réinstaller » sans
sauvegarde ni accord écrit ; ouvrir les fichiers personnels « pour vérifier ».

**À l'écrit** : « Offres commerciales uniquement sur le portable : copie sur support chiffré avant
toute action ; réinstallation complète refusée sans nouvel accord écrit. »

**Repère rapide** : **où sont les données ? · copie ? · risques dits · accord signé · rien de
plus que nécessaire**. Exercices liés : {_ex("E06", "E14", "E15", "E17")}.
"""


def _interview() -> str:
    useful = sum(1 for _q, k, _w in QUESTIONS if k == USEFUL)
    return f"""**Objectifs** : obtenir des faits en peu de questions ; vérifier que l'on a bien compris.

## 6.1 Questions utiles

{_fig(INTERVIEW_FIGURE)}

On commence par des **questions ouvertes** (« que voyez-vous ? », « depuis quand ? », « qu'est-ce
qui a changé ? »), puis des **questions fermées** pour préciser (« à chaque fois ? », « d'autres
collègues ? », « quel message exact ? »). Une question utile est **compréhensible sans
connaissance technique** et **ne suggère pas la réponse**. Dans la liste ci-dessous, {useful}
questions sont utiles :

{_questions_table()}

## 6.2 Reformulation

La **reformulation** résume la demande en deux ou trois phrases : **quoi, depuis quand, à quelle
fréquence, qui est touché, quel enjeu**. Elle reprend les faits, pas les hypothèses. On la fait
**valider** : « Si je résume bien : … Est-ce exact ? Ai-je oublié quelque chose ? » Elle évite de
réparer autre chose que ce que le client attend.

**Procédure professionnelle** : suivre les six étapes de la procédure 2 ci-dessus.

**Erreur fréquente** : poser une question en jargon (« votre DHCP répond ? ») ou orientée (« c'est
le disque, non ? ») ; reformuler avec ses propres hypothèses.

**À l'écrit** : « Depuis lundi, sur le PC des devis, le logiciel de devis se ferme seul environ
deux secondes après son lancement, à chaque essai ; le reste fonctionne ; trois devis à envoyer
avant vendredi. »

**Repère rapide** : **ouvertes puis fermées · sans jargon · sans accuser · « si je résume
bien… »**. Exercices liés : {_ex("E05", "E10")}.
"""


def _form() -> str:
    return f"""**Objectifs** : remplir une fiche d'incident complète ; employer le vocabulaire technique
exact ; évaluer une fiche avec une grille.

## 7.1 La fiche d'incident

La **fiche d'incident** (ou fiche d'intervention, ticket) est le **formulaire professionnel** qui
suit la demande de bout en bout. Elle compte six sections ; une rubrique vide se voit tout de
suite.

{_fig(FORM_FIGURE)}

{_form_table()}

## 7.2 Vocabulaire technique

La fiche emploie des **termes exacts** (exigence officielle AP-16) : on écrit « le voyant
d'alimentation reste éteint », pas « le PC est mort » ; « message *Accès refusé* sur le partage
`\\\\SRV-01\\Compta` », pas « le réseau bug ». Quelques termes de la fiche :

- **demande** (ce qui est reçu), **incident** (interruption ou dégradation d'un service),
  **ticket** (enregistrement de la demande) ;
- **symptôme**, **hypothèse**, **panne reproductible**, **panne intermittente** ;
- **impact**, **urgence**, **priorité**, **délai de prise en charge** ;
- **contournement** (solution provisoire), **escalade** (transfert au niveau compétent),
  **clôture** (fin validée par le demandeur).

Un sigle est écrit en entier la première fois si le lecteur peut l'ignorer.

## 7.3 Grille d'évaluation

Pour se relire, ou évaluer la fiche d'un collègue, on utilise une **grille d'évaluation** : chaque
critère est **acquis** (tous les points), **partiel** (la moitié) ou **absent** (0).

{_grid_table()}

**Procédure professionnelle** : 1) remplir la fiche section par section ; 2) relire les
rubriques obligatoires ; 3) appliquer la grille ; 4) compléter les critères partiels ou absents
avant d'intervenir.

**Erreur fréquente** : laisser vides « Changements récents » ou « Données et sauvegarde » ;
écrire « voir sur place » dans le plan.

**À l'écrit** : recopier les six sections et remplir **toutes** les rubriques obligatoires, même
par « sans objet » justifié.

**Repère rapide** : **six sections · rubrique vide = question à poser · mots exacts · grille sur
{EVAL_TOTAL}**. Exercices liés : {_ex("E09", "E19")}.
"""


def _plan() -> str:
    example = (30, 25, 60, 30, 20)
    return f"""**Objectifs** : dire à l'avance comment on prouvera la réussite, ce que l'on va faire et
combien de temps cela prendra.

## 8.1 Critères de réussite

Un **critère de réussite** est un **test** que l'on fera devant le client, avec un **résultat
attendu**, chiffré si possible : « 50 pages imprimées sans bourrage », « démarrage en moins d'une
minute, mesuré trois fois », « les trois comptables enregistrent un fichier dans Compta ». « Le PC
marche », « c'est mieux », « le client est content » ne sont pas vérifiables. On convient des
critères avec le client lors de la **reformulation**.

## 8.2 Plan d'action

Le **plan d'action** liste les étapes **dans l'ordre** : d'abord ce qui protège (sauvegarde),
puis les vérifications **les plus simples et les moins risquées**, puis les actions plus lourdes,
enfin le **contrôle des critères**. Chaque étape a une durée ; un **plan B** (poste de prêt,
contournement) est prévu pour une demande urgente.

## 8.3 Estimation

Convention du cours : **somme des tâches + {int(MARGIN * 100)} % d'imprévus, arrondie au quart d'heure
supérieur**. Exemple : {" + ".join(str(m) for m in example)} = {sum(example)} min ;
+ {int(MARGIN * 100)} % = {fr(sum(example) * (1 + MARGIN))} min ; annoncé : **{hm(estimate(example))}**. Le coût
des pièces est donné à part, sur devis. Si l'intervention va **dépasser** l'estimation, on
**prévient avant** et on fait accepter une nouvelle estimation.

**Procédure professionnelle** : 1) écrire les critères ; 2) ordonner les tâches ; 3) donner une
durée à chacune ; 4) calculer l'estimation ; 5) faire valider plan, durée et coût.

**Erreur fréquente** : commencer par l'action la plus lourde (réinstallation) ; annoncer une durée
sans marge ; dépasser sans prévenir.

**À l'écrit** : « Plan : 1. sauvegarde ; 2. … ; 5. contrôle des critères avec l'utilisatrice.
Durée annoncée : {hm(estimate(example))}. »

**Repère rapide** : **critère = test + résultat · protéger d'abord · simple avant lourd · + {int(MARGIN * 100)} %
· prévenir avant de dépasser**. Exercices liés : {_ex("E13", "E14", "E20")}.
"""


def _escalate() -> str:
    return f"""**Objectifs** : reconnaître les limites de son rôle ; transmettre une demande sans perdre
d'information.

## 9.1 Quand escalader ?

Avant d'agir, on passe cinq contrôles, **du plus grave au moins grave**. Au premier « non », on
s'arrête et on applique l'action prévue.

{_fig(ESCALATION_FIGURE)}

{_checks_table()}

La **sécurité** vient en premier : un virus ou une intrusion **continue d'agir** pendant qu'on
réfléchit. On **isole** (câble débranché, Wi-Fi coupé), on **n'efface rien** (traces utiles), on
prévient.

## 9.2 Comment escalader ?

{_fig(ESCALATION_PROC_FIGURE)}

**Escalader n'est pas abandonner** : on transmet au bon niveau (responsable, niveau 2, fabricant,
prestataire, laboratoire de récupération) une **fiche d'escalade** qui contient les **faits**, les
**tests déjà faits** (et leurs résultats), les **hypothèses**, ce qu'il **ne faut pas faire**,
l'**urgence** et le **contact**. On note le numéro de suivi et on informe le demandeur.

**Procédure professionnelle** : suivre les six étapes de la procédure 3 ci-dessus.

**Erreur fréquente** : élargir les droits « pour tester » sur un serveur que l'on n'administre
pas ; lancer un logiciel de récupération sur un disque qui claque ; escalader par un simple
« ça ne marche pas » sans faits.

**À l'écrit** : « Escalade au prestataire (administration du serveur, hors de mes droits) : refus
d'accès sur Compta pour trois comptables depuis la réorganisation des droits de mercredi ;
échéance des salaires à midi. »

**Repère rapide** : **sécurité · droits · données · compétence · budget — au premier non, on
s'arrête et on transmet des faits**. Exercices liés : {_ex("E06", "E08", "E17", "E18")}.
"""


def _examples() -> str:
    return (
        "Cinq dossiers entièrement corrigés, du premier appel à la décision, avec la fiche d'incident complétée. "
        "Ils couvrent un PC inerte, une impression, une lenteur, un accès partagé et le Wi-Fi ; le diagnostic "
        "technique qui suit est traité dans les cours [PR06](/uaa/ampcr-pratique-pr06), "
        "[PR12](/uaa/ampcr-pratique-pr12), [PR23](/uaa/ampcr-pratique-pr23) et [PR25](/uaa/ampcr-pratique-pr25).\n\n"
        + "\n".join(_dossier_html(i, d) for i, d in enumerate(DOSSIERS, start=1))
    )


def _pitfalls() -> str:
    return """> **Recopier l'avis du client comme symptôme** (« carte mère HS », « virus ») au lieu des faits.

> **Oublier les changements récents** : mise à jour, déplacement, nettoyage, droits réorganisés.

> **Prendre la priorité de l'utilisateur** sans évaluer impact et urgence.

> **Commencer sans savoir où sont les données** ni s'il existe une copie.

> **Agir sans accord écrit** sur une opération risquée, ou au-delà de ce qui a été accepté.

> **Ouvrir des fichiers personnels** ou communiquer le mot de passe d'une autre personne.

> **Écrire des critères vagues** (« le PC marche ») qui ne prouvent rien.

> **Déclarer réparée une panne intermittente** après un seul essai réussi.

> **Dépasser l'estimation sans prévenir** le client.

> **Escalader sans faits** (« ça ne marche pas ») ou ne pas escalader quand la limite est atteinte.
"""


def _exercises_intro() -> str:
    return f"""{len(PRACTICE_ITEMS)} exercices corrigés : remise en ordre de la démarche ; **qualification**
(observation ou hypothèse, reproductible ou intermittente, priorité, questions, escalade, journal
d'une panne intermittente) ; **deux schémas à compléter** (matrice de priorité, arbre d'escalade) ;
**analyse de tickets** (fiche incomplète, courriel, journal de tickets, inventaire, évaluation avec
la grille) ; **rédaction** (reformulation, critères de réussite, plan et estimation, accord du
client, fiche d'escalade). Rédige ta réponse sur papier **avant** d'ouvrir le corrigé ; toute
réponse équivalente et justifiée est acceptée. Ces mêmes exercices sont proposés dans
[S'entraîner](/uaa/{PR26_SLUG}/practice), avec correction après envoi.

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
    return f"""Le mini-examen se passe dans l'onglet [Examen blanc](/uaa/{PR26_SLUG}/exam) : **10 questions à réponse
libre**, chacune notée sur **2 points**, soit une note sur **{EXAM_TOTAL_POINTS}**. Les
questions ne figurent pas dans ce cours.

| N° | Thème | Type | Points |
|---|---|---|---|
{rows}

**Déroulement.** Chaque question est une situation complète : toutes les données nécessaires
sont dans l'énoncé et ses documents (demandes et fiches fictives). **Aucune correction n'est
visible pendant la passation** ; tes réponses sont enregistrées au fur et à mesure. Après
l'envoi, chaque réponse est corrigée selon le **barème analytique** de la question (critères et
points), puis tu vois ta note sur {EXAM_TOTAL_POINTS}, le corrigé et le barème.

**Ce que valorise le barème.** Les **faits séparés des hypothèses**, la **priorité justifiée**,
la **protection des données** et l'**autorisation**, des **critères vérifiables** et une
**escalade** à bon escient — pas la récitation de définitions. Une autre formulation juste et
justifiée est acceptée.

**Nature de la correction.** Les réponses rédigées reçoivent une **proposition de correction
automatique** (assistée par IA) appuyée sur le barème : c'est un repère d'entraînement, pas une
note officielle ; en cas de doute, compare ta réponse au corrigé.
"""


def _memo() -> str:
    return f"""## Mémo

- **Démarche** : recueillir → identifier → questionner → qualifier → prioriser → protéger →
  reformuler → planifier → décider.
- **Demande** : symptômes (faits) ≠ interprétation (avis) ≠ attente (échéance).
- **Contexte** : matériel, logiciel, réseau ; n° d'inventaire recoupé ; garantie ; date ;
  changements récents ; utilisateurs touchés.
- **Qualifier** : O = observation vérifiable ; H = hypothèse à tester ; reproductible (à chaque
  fois) ou intermittente (journal, critère sur une durée).
- **Priorité** : impact (combien) × urgence (quand) ; 1+1 → P1, 1+2 → P2, 1+3 ou 2+2 → P3,
  sinon P4 ; contournement ↓ impact, échéance ↑ urgence.
- **Protéger** : sauvegarde, confidentialité, risques annoncés, accord écrit et précis.
- **Entretien** : questions ouvertes puis fermées, sans jargon ni accusation ; « si je résume
  bien… ».
- **Fiche** : {len(SECTIONS)} sections, toutes les rubriques obligatoires ; grille sur {EVAL_TOTAL}.
- **Plan** : critères = test + résultat ; protéger d'abord ; simple avant lourd ; + {int(MARGIN * 100)} %,
  quart d'heure supérieur ; prévenir avant de dépasser.
- **Escalade** : sécurité → droits → données → compétence → budget ; transmettre des faits.

## Glossaire des termes employés

- **Contournement** : solution provisoire qui permet de continuer à travailler.
- **Critère de réussite** : test convenu avec le client qui prouve la fin de l'intervention.
- **Escalade** : transfert d'une demande au niveau ou à l'organisme compétent.
- **Fiche d'incident** : formulaire qui suit une demande de la réception à la clôture.
- **Hypothèse** : cause supposée, à vérifier par un test.
- **Impact** : étendue des conséquences d'un incident.
- **Inventaire** : liste des appareils (n° d'inventaire, modèle, n° de série, utilisateur, garantie).
- **Observation** : fait constaté, vérifiable.
- **Panne intermittente** : panne qui apparaît de temps en temps, sans qu'on puisse la provoquer.
- **Panne reproductible** : panne qui apparaît à chaque essai dans les mêmes conditions.
- **Priorité** : ordre de traitement, déduit de l'impact et de l'urgence.
- **Reformulation** : résumé de la demande validé par le demandeur.
- **Urgence** : délai avant un dommage réel.
"""


def _sources() -> str:
    return f"""## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), p. 5 : « Vocabulaire technique » (AP-16) ; p. 3 : épreuve
  « uniquement par écrit ». Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
  Programme officiel n° 345/2007/249 (option AMPCR).
- **Pratiques de gestion des incidents des centres de services** (référentiel ITIL : incident,
  impact, urgence, priorité, escalade) : la matrice et les délais du cours en sont une version
  simplifiée.
- **Protection des données** : règlement général sur la protection des données (RGPD) —
  principes de minimisation et de confidentialité appliqués à l'intervention.

Les règles du cours (matrice, délais, marge d'estimation, ordre des contrôles d'escalade, grille
sur {EVAL_TOTAL}) sont **produites par programme** depuis des données **vérifiées par des tests
automatiques** ; les schémas en sont dessinés directement. Aucun schéma n'est tiré d'une image
générée ni d'une photographie.

## Compléments pédagogiques (non imposés par la liste officielle)

La p. 5 cite le vocabulaire technique. Sont des **compléments**, signalés comme tels, utiles pour
traiter un dossier écrit :

- la démarche d'analyse d'une demande et la fiche d'incident (AP-C01) ;
- les **conventions du cours** : matrice impact × urgence en quatre priorités, délais de prise en
  charge, marge de {int(MARGIN * 100)} % arrondie au quart d'heure, grille d'évaluation sur {EVAL_TOTAL} ;
- la sauvegarde, la confidentialité et l'autorisation (complément AP-C03).

## Supports fictifs

Les personnes, entreprises, demandes, numéros d'inventaire et fiches de ce cours sont **fictifs**
et reconstitués pour l'entraînement ; ils ne décrivent aucun client réel. Aucune n'est une
question officielle ou déjà posée par le Jury.
"""


def pr26_course_sections() -> list[tuple[str, str]]:
    """Blocs du cours (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("PR26 — Objectifs et place dans l'épreuve", _objectives()),
        ("PR26 — 1. Recueillir la demande : demandeur, symptômes et interprétation", _collect()),
        ("PR26 — 2. Contexte matériel, logiciel et réseau ; inventaire, changements récents", _context()),
        ("PR26 — 3. Qualifier : observation ou hypothèse, panne reproductible ou intermittente", _qualify()),
        ("PR26 — 4. Utilisateurs touchés, impact, urgence et priorisation", _prioritize()),
        ("PR26 — 5. Sauvegarde, consentement, confidentialité, risques et autorisation", _protect()),
        ("PR26 — 6. Questions utiles et reformulation", _interview()),
        ("PR26 — 7. Fiche d'incident, vocabulaire technique et grille d'évaluation", _form()),
        ("PR26 — 8. Critères de réussite, plan d'action et estimation", _plan()),
        ("PR26 — 9. Escalade : quand s'arrêter, comment transmettre", _escalate()),
        ("PR26 — Exemples : cinq dossiers entièrement corrigés", _examples()),
        ("PR26 — Pièges et erreurs fréquentes", _pitfalls()),
        (f"PR26 — Exercices corrigés ({len(PRACTICE_ITEMS)}) et leurs corrigés", _exercises_intro()),
        ("PR26 — Mini-examen noté sur 20 : mode d'emploi", _mini_exam()),
        ("PR26 — Fiche mémo et glossaire", _memo()),
        ("PR26 — Sources et compléments pédagogiques", _sources()),
    ]

