"""Cours PR29 « Contrôles finaux et rapport professionnel d'intervention » — parcours AMPCR
pratique écrite (ticket #228).

Matière : intégralement celle du ticket #228 (critères d'acceptation avant / après, test
fonctionnel, stabilité, performance, réseau local et Internet, sécurité, pilote et périphérique,
journal des opérations, tests reproductibles, restauration et retour arrière, limites et
résultats non concluants ; compte rendu structuré : identité de l'équipement non sensible,
demande, symptômes, hypothèses, relevés, tests, résultats, action, pièces, validation, risques
résiduels, recommandation, signature et accord ; communication non technique au client,
escalade, documentation ; cinq rapports modèles complets — PC, système, RJ45, réseau, partage —,
exercices de correction de rapports et de rédaction, mini-examen et formulaires imprimables),
découpée en blocs titrés (le titre pilote le type de carte, `app.card_kind` : aucun titre de
bloc théorique ne contient « examen », « source », « ressource », « exemple », « exercice »,
« méthode », « piège », « attention », « transfert » ni « mémo »).
Règles, rapports modèles, schémas et formulaires : `app.v1.ampcr_pratique_pr29_figures` ;
exercices et mini-examen : `app.v1.ampcr_pratique_pr29_bank`. Le cours renvoie à PR26 (demande,
fiche d'incident, escalade), PR27 (diagnostic, retour arrière préparé), PR28 (sécurité, données)
et aux cours techniques dont les rapports modèles reprennent les gestes.
"""

from html import escape

from app.v1.ampcr_pratique_pr06_course import _exercise_card, _fig, _req
from app.v1.ampcr_pratique_pr26_figures import ESCALATION_CHECKS
from app.v1.ampcr_pratique_pr29_bank import EXAM_ITEMS, EXAM_TOTAL_POINTS, PRACTICE_ITEMS
from app.v1.ampcr_pratique_pr29_figures import (
    BEFORE_AFTER_FIGURE,
    CHECK_FAMILIES,
    CHECKLIST_FIGURE,
    DECISION_TREE,
    DECISION_TREE_FIGURE,
    DOC_TARGETS,
    FAMILIES_FIGURE,
    FINAL_CHECKLIST,
    FINAL_FIGURE,
    GRID_TOTAL,
    HANDOVER_DO_FIGURE,
    HANDOVER_FIGURE,
    INTERVENTION_KINDS,
    MESSAGES,
    MSG_OK,
    PRINTABLE_FORMS,
    PRINTABLE_PATHS,
    PROCEDURES,
    REPORT_FIELDS,
    REPORT_FIGURE,
    REPORT_GRID,
    REPORT_SECTIONS,
    REPORTS,
    REPRO_FIELDS,
    RESERVE_FIGURE,
    ROLLBACK_FIGURE,
    STATIC_FIGURES,
    WRITE_FIGURE,
    WRITTEN_AT,
    Report,
    fmt,
    required_checks,
)
from app.v1.ampcr_pratique_visuals import render_figure

PR29_TITLE = "Contrôles finaux et rapport professionnel d'intervention"
PR29_SLUG = "ampcr-pratique-pr29"

_SCHEMAS_BY_PATH = {path: figure for figure, path in STATIC_FIGURES}


def _card(number: int, item) -> str:
    """Carte d'exercice de PR06 ; un schéma à compléter est affiché (SVG) avant sa
    description textuelle."""
    html = _exercise_card(number, item, anchor_prefix="pr29")
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


def _families_table() -> str:
    rows = [(f.name, f.question, " ; ".join(f.tests), f.evidence) for f in CHECK_FAMILIES]
    return _html_table(("Famille", "Ce qu'elle prouve", "Tests concrets", "À écrire au rapport"), rows)


def _required_table() -> str:
    rows = []
    for kind in INTERVENTION_KINDS:
        need = {f.key for f in required_checks(kind)}
        rows.append((kind, *("oui" if f.key in need else "—" for f in CHECK_FAMILIES)))
    return _html_table(("Intervention", *(f.name for f in CHECK_FAMILIES)), rows,
                       caption="Contrôles exigés selon le type d'intervention (convention du cours)")


def _repro_table() -> str:
    example = (
        "PC INV-0388, session de l'avocate, câble sur la prise B4-02",
        "ping -n 50 192.168.1.1 dans l'invite de commandes",
        "lancer la commande, lire la ligne « Paquets »",
        "0 % de pertes",
        "50 envoyés, 50 reçus, 0 % de pertes, 1 ms en moyenne",
        "20/10/2026, 10:50, 1 min",
    )
    rows = [(label, value) for (_k, label), value in zip(REPRO_FIELDS, example, strict=True)]
    return _html_table(("Rubrique", "Exemple rempli (rapport 3)"), rows, caption="Un test reproductible")


def _report_fields_table() -> str:
    rows = [(f.section, f.label, f.content) for f in REPORT_FIELDS]
    return _html_table(("Partie", "Rubrique", "Ce qu'on y écrit"), rows,
                       caption="Le compte rendu structuré (modèle du cours)")


def _grid_table() -> str:
    rows = [(label, str(points), detail) for _k, label, points, detail in REPORT_GRID]
    return _html_table(("Critère", "Points", "Attendu"), rows, caption=f"Grille d'évaluation d'un rapport (sur {GRID_TOTAL})")


_VOCAB: tuple[tuple[str, str, str], ...] = (
    ("Critère d'acceptation", "mesure et valeur qui prouvent la réparation", "« ce que nous vérifierons ensemble »"),
    ("Régression", "fonction qui marchait et ne marche plus après l'intervention", "« ceci ne fonctionne plus depuis ma modification »"),
    ("Retour arrière (rollback)", "retour à l'état sauvegardé avant la modification", "« je remets le poste comme il était ce matin »"),
    ("Résultat non concluant", "mesure impossible ou absente : ni réussie, ni ratée", "« je n'ai pas encore pu le vérifier »"),
    ("Réserve", "limite écrite sur la réception", "« c'est réparé, sauf ce point qui reste à vérifier »"),
    ("Risque résiduel", "risque qui subsiste après l'intervention", "« ce qui peut encore arriver, et pourquoi »"),
    ("Escalade", "transmission à un niveau, un service ou un prestataire compétent", "« je confie ce point au service qui en a les droits »"),
    ("Procès-verbal de réception", "document signé par le client qui constate le résultat", "« votre signature confirme ce que nous avons vu »"),
)


def _vocab_table() -> str:
    return _html_table(("Terme du rapport", "Sens précis", "Formulation pour le client"), list(_VOCAB),
                       caption="Vocabulaire technique : le mot juste dans le rapport, les mots simples à l'oral")


def _escalation_list() -> str:
    return "\n".join(f"{i}. {question} — sinon : {action}" for i, (_k, question, action) in enumerate(ESCALATION_CHECKS, start=1))


def _forms_list() -> str:
    return "\n".join(
        f"- **[{form.title}](/static/{PRINTABLE_PATHS[form.key]})** — {form.intro}" for form in PRINTABLE_FORMS
    )


# =============================================================================================
# Cinq rapports modèles complets
# =============================================================================================


def _report_html(number: int, r: Report) -> str:
    filled = r.filled()
    rubrics = _html_table(("Rubrique", "Contenu"), [(f.label, filled[f.key]) for f in REPORT_FIELDS],
                          caption=f"Rapport {number} — compte rendu complet")
    measures = _html_table(
        ("Critère", "Avant", "Après", "Résultat"),
        [(m.criterion.text(), fmt(m.before), fmt(m.after), m.result) for m in r.measures],
    )
    journal = _html_table(("Heure", "Opération", "Résultat"), [(e.time, e.action, e.result) for e in r.journal])
    checks = ", ".join(f.name.lower() for f in required_checks(r.kind))
    return f"""## Rapport {number} — {r.theme} : {r.title}

**Situation.** {r.context}

**Type d'intervention** : {r.kind.lower()} → contrôles exigés : {checks}.

{rubrics}

**Critères d'acceptation, avant / après.**

{measures}

**Verdict** : {r.verdict}. **Décision** : {r.decision}.

**Journal des opérations.**

{journal}

**Message au client (non technique).** « {r.client_message} »
"""


# =============================================================================================
# Sections du cours (titre du bloc, Markdown / HTML)
# =============================================================================================


def _objectives() -> str:
    return f"""## Ce que tu sauras faire, par écrit

L'épreuve pratique AMPCR se passe **uniquement par écrit** (consignes officielles 2026-2027/1,
p. 3). Une intervention ne se termine pas quand la pièce est posée : elle se termine quand le
résultat est **prouvé**, **rendu** au client et **écrit**. Tu dois savoir :

1. fixer des **critères d'acceptation** mesurables et les comparer **avant / après** ;
2. choisir les **contrôles finaux** exigés : test fonctionnel, stabilité, performance, réseau
   local et Internet, sécurité, pilote et périphérique ;
3. tenir un **journal des opérations** et écrire des **tests reproductibles** ;
4. décider : **valider**, faire un **retour arrière**, **escalader** ou émettre une **réserve**
   quand un résultat est **non concluant** ;
5. rédiger un **compte rendu structuré** en quatorze rubriques, sans donnée sensible ;
6. expliquer le résultat au client **sans jargon**, escalader et **documenter**.

Ce cours contient **{len(PROCEDURES)} procédures illustrées**, un **arbre de clôture**, **cinq
rapports modèles complets** et **{len(PRINTABLE_FORMS)} formulaires imprimables** :

{_procedures_list()}

## Exigences travaillées dans ce cours

{_req("AP-16")}
{_req("AP-C01")}

AP-16 est une exigence **officielle** (p. 5) : le vocabulaire technique s'écrit juste dans le
rapport. AP-C01 est un **complément** du parcours : l'épreuve étant écrite, toute réponse est un
compte rendu de technicien. Le cours s'appuie aussi sur {_req("AP-15")[2:]} (les contrôles
prouvent le dépannage) et rappelle AP-C03 (confidentialité des données dans le rapport).

## Lien avec la théorie et les autres cours

La théorie AMPCR présente la méthode de dépannage ([MC29](/uaa/ampcr-mc29),
[MC30](/uaa/ampcr-mc30)) et la rédaction d'une intervention ([MC36](/uaa/ampcr-mc36)). Ce cours-ci
est **pratique** : il ferme le cycle commencé en [PR26](/uaa/ampcr-pratique-pr26) (analyser la
demande, fiche d'incident, escalade) et poursuivi en [PR27](/uaa/ampcr-pratique-pr27) (procédure
de diagnostic, retour arrière préparé). Les précautions et la protection des données sont dans
[PR28](/uaa/ampcr-pratique-pr28). Les gestes techniques des rapports modèles sont détaillés dans
[PR02](/uaa/ampcr-pratique-pr02) (bloc d'alimentation), [PR08](/uaa/ampcr-pratique-pr08)
(installation de Windows), [PR12](/uaa/ampcr-pratique-pr12) (restauration),
[PR15](/uaa/ampcr-pratique-pr15) (RJ45), [PR24](/uaa/ampcr-pratique-pr24) (dépannage réseau) et
[PR23](/uaa/ampcr-pratique-pr23) (partages et permissions).

## Comment travailler ce cours

Lis les chapitres dans l'ordre : chacun donne ses **objectifs**, la **théorie**, la
**procédure professionnelle**, l'**erreur fréquente**, ce qu'on attend **à l'écrit** et un
**repère rapide**, avec un renvoi vers les exercices liés. Étudie ensuite les **cinq rapports
modèles**, fais les **{len(PRACTICE_ITEMS)} exercices corrigés** (dont deux **schémas à
compléter** et de nombreuses **corrections de rapports**), puis passe le **mini-examen noté sur
{EXAM_TOTAL_POINTS}** dans l'onglet « Examen blanc ».

> **Important —** les personnes, entreprises, équipements, relevés et rapports de ce cours sont
> des **supports fictifs** construits pour s'entraîner (rédaction : {WRITTEN_AT}). Le modèle de
> rapport et les familles de contrôles sont une **convention du cours** : chaque entreprise a son
> propre formulaire, qui fait foi. Aucun exercice n'est une question officielle ni une question
> déjà posée par le Jury.
"""


def _criteria() -> str:
    return f"""**Objectifs** : écrire, avant d'intervenir, ce qui prouvera la réparation ; mesurer la
même chose après ; conclure critère par critère.

## 1.1 Un critère d'acceptation se mesure

Un **critère d'acceptation** dit **quoi** mesurer, **avec quoi** et **quelle valeur** attendre :
« démarrage jusqu'au bureau en 60 s au plus, chronométré », « ping de la passerelle : 0 % de
pertes sur 50 paquets », « la comptable ouvre et enregistre un fichier du dossier Compta ». Il
s'écrit **avec le client** au moment de la demande ([PR26](/uaa/ampcr-pratique-pr26)) : c'est
lui qui dira si le résultat lui convient.

« Le PC marche mieux », « Internet a l'air rapide », « le client est content » ne sont pas des
critères : deux personnes peuvent conclure l'inverse.

## 1.2 Avant / après : même mesure, mêmes conditions

{_fig(BEFORE_AFTER_FIGURE)}

On mesure **avant** toute action (c'est un relevé), puis **après**, **dans les mêmes conditions**
(même outil, même charge, même compte, même heure si la panne dépend de l'heure). Chaque critère
reçoit un résultat :

- **atteint** : la valeur après respecte la cible ;
- **non atteint** : elle ne la respecte pas — même si c'est **mieux qu'avant** (150 s → 75 s
  pour une cible de 60 s : non atteint) ;
- **non concluant** : la mesure n'a pas pu être faite (chapitre 4).

Le **verdict** d'ensemble suit une règle simple : un critère non atteint suffit à **ne pas
valider** ; sinon un résultat non concluant impose une **réserve** ; sinon tout est validé.

**Procédure professionnelle** : écrire les critères avec le client → relever l'avant → intervenir
→ mesurer l'après dans les mêmes conditions → résultat par critère → verdict.

**Erreur fréquente** : comparer à l'avant plutôt qu'à la cible (« c'est mieux, donc c'est bon ») ;
mesurer l'après sans avoir relevé l'avant ; ajouter un critère après coup parce qu'il est atteint.

**À l'écrit** : « Démarrage ≤ 60 s : avant 210 s, après 42 s → atteint. Périphériques en erreur
≤ 0 : avant 2, après 0 → atteint. Verdict : validé. »

**Repère rapide** : **cible écrite avant · même mesure après · un non atteint = non validé ·
mieux n'est pas réparé**. Exercices liés : {_ex("E03", "E04")}.
"""


def _checks() -> str:
    return f"""**Objectifs** : connaître les six familles de contrôles finaux et celles qu'exige chaque
type d'intervention.

## 2.1 Les six familles

{_fig(FAMILIES_FIGURE)}

{_families_table()}

## 2.2 Quels contrôles pour quelle intervention ?

Le **test fonctionnel** (refaire ce qui échouait, dans les conditions de l'utilisateur) et la
**sécurité** (le poste est rendu aussi sûr qu'avant : protections actives, compte technique
supprimé, capot fermé, câbles rangés) sont **toujours** exigés. Les autres familles dépendent de
l'intervention :

{_required_table()}

Une réinstallation remet des pilotes génériques et peut effacer la configuration réseau : on
contrôle donc aussi le réseau et les périphériques. Un remplacement de pièce se contrôle **sous
charge** et **dans la durée** : un bloc ou une barrette défaillants tiennent souvent quelques
minutes.

## 2.3 La procédure des contrôles finaux

{_fig(FINAL_FIGURE)}

**Procédure professionnelle** : relire les critères, choisir les familles exigées, mesurer,
comparer, décider, faire constater.

**Erreur fréquente** : s'arrêter au test fonctionnel (« ça démarre ») ; oublier la sécurité
(compte technique laissé actif, antivirus désactivé pendant l'intervention) ; tester avec son
propre compte au lieu de celui de l'utilisateur.

**À l'écrit** : « Contrôles : fonctionnel (impression du bon depuis le logiciel de la vendeuse),
pilote (Gestionnaire sans erreur, page de test), sécurité (compte technique supprimé). »

**Repère rapide** : **fonctionnel et sécurité toujours · stabilité et performance pour le
matériel · réseau et pilotes après une réinstallation**. Exercices liés : {_ex("E01", "E02", "E05")}.
"""


def _journal() -> str:
    return f"""**Objectifs** : tenir un journal des opérations exploitable ; écrire des tests qu'un
collègue peut refaire à l'identique.

## 3.1 Le journal des opérations

Le **journal** est la trace de l'atelier : **une ligne par opération**, dans l'**ordre des
heures**, avec un **résultat observé**. Il prouve ce qui a été fait, permet le retour arrière et
sert à rédiger le rapport. Trois défauts le rendent inutilisable :

- une ligne **hors de l'ordre chronologique** (on ne sait plus quel test a précédé quelle
  modification) ;
- un **résultat absent** ;
- un **résultat vague** — « OK », « fait », « ça marche » — qui ne dit pas ce qu'on a vu.

On fait **une seule modification à la fois** et on la note avant d'en faire une autre
([PR27](/uaa/ampcr-pratique-pr27)).

## 3.2 Un test reproductible

Un test est **reproductible** quand un collègue peut le refaire et obtenir un résultat
comparable. Il précise six rubriques :

{_repro_table()}

**Procédure professionnelle** : noter l'heure et le résultat **au moment** de l'opération, pas
de mémoire en fin de journée ; recopier la valeur exacte affichée.

**Erreur fréquente** : « Test : ping. Résultat : ça marche. » ; reconstituer le journal après coup ;
noter trois modifications sur une seule ligne.

**À l'écrit** : « 10:45 — PC rebranché, vitesse lue dans les propriétés de la carte : 1000 Mb/s.
10:50 — ping -n 50 192.168.1.1 : 0 % de pertes. »

**Repère rapide** : **une ligne · une heure · une modification · un résultat chiffré · jamais
« OK »**. Exercices liés : {_ex("E06", "E07")}.
"""


def _rollback() -> str:
    return f"""**Objectifs** : décider de la suite quand un contrôle échoue ou ne peut pas être fait ;
revenir à l'état initial et le vérifier ; écrire les limites du résultat.

## 4.1 L'arbre de clôture

{_fig(DECISION_TREE_FIGURE)}

On descend l'arbre « {DECISION_TREE.title.lower()} » tant que la réponse est « oui ». Quatre
issues sont possibles : **signer** (tout est validé), **retour arrière** (un critère non atteint
et l'état initial a été sauvegardé), **escalade** (un critère non atteint sans retour arrière
possible, ou hors de ses droits), **réserve** (un résultat non concluant).

## 4.2 Restauration et retour arrière

{_fig(ROLLBACK_FIGURE)}

Le retour arrière **se prépare avant** d'intervenir : état initial noté ou exporté, point de
restauration, ancien pilote gardé, câblage photographié, et un **critère d'échec** écrit à
l'avance ([PR27](/uaa/ampcr-pratique-pr27)). Après la restauration, on **vérifie** l'état
initial en refaisant les tests du « avant » : un retour arrière non vérifié n'est pas un retour
arrière. Une intervention qui casse une fonction qui marchait (une **régression**) est un
critère non atteint, même si le problème de départ est réglé. La restauration des données et du
système est détaillée en [PR12](/uaa/ampcr-pratique-pr12).

## 4.3 Limites et résultats non concluants

{_fig(RESERVE_FIGURE)}

Un résultat est **non concluant** quand la mesure n'a pas pu être faite : panne qui n'apparaît
que le soir, avec vingt personnes connectées, au bout de quelques jours. Il n'est **ni réussi, ni
raté** : on ne déclare pas la panne résolue, on écrit une **réserve** (ce qui a été mesuré, ce qui
ne l'a pas été), on **planifie** le test complémentaire et on dit au client quoi faire en
attendant.

**Procédure professionnelle** : verdict → arbre → décision écrite au rapport, avec la date du
suivi s'il y a une réserve.

**Erreur fréquente** : essayer d'autres modifications au hasard après un échec ; déclarer
« réparé » une panne intermittente testée à un autre moment ; cacher une régression.

**À l'écrit** : « Coupures du soir non reproduites ce matin : résultat non concluant. Validation
avec réserve ; test de 17 h à 19 h le 23/10/2026. »

**Repère rapide** : **retour arrière préparé, puis vérifié · non concluant = réserve écrite ·
jamais « réparé » sans mesure**. Exercices liés : {_ex("E10", "E13", "E14", "E15", "E17", "E22")}.
"""


def _structure() -> str:
    return f"""**Objectifs** : connaître les quatorze rubriques du compte rendu et ce qu'on écrit
dans chacune.

## 5.1 Six parties, quatorze rubriques

{_fig(REPORT_FIGURE)}

{_report_fields_table()}

L'ordre suit l'intervention : **qui et quoi** (identification), **ce qu'on demande et ce qu'on
voit** (demande, symptômes), **ce qu'on pense et ce qu'on prouve** (hypothèses, relevés, tests,
résultats), **ce qu'on fait** (action, pièces), **ce qui est prouvé** (validation, risques
résiduels) et **la suite** (recommandation, signature). Les parties sur la demande reprennent la
fiche d'incident de [PR26](/uaa/ampcr-pratique-pr26).

## 5.2 L'identité de l'équipement, sans donnée sensible

L'équipement s'identifie par son **n° d'inventaire**, son **modèle** et son **emplacement** — pas
par le nom de son utilisateur seul, jamais par un mot de passe. Les **pièces** posées ont leur
référence et leur n° de série : ils servent à la garantie et à l'inventaire.

## 5.3 La signature et l'accord

La **réception** est constatée par le client, qui **signe** (nom, date, heure). S'il n'accepte
pas, ou s'il y a une réserve, on note **ses mots** sur le rapport. Une signature n'efface pas une
réserve : elle constate que le client l'a lue.

**Procédure professionnelle** : remplir le modèle dans l'ordre, sans sauter de rubrique ; une
rubrique sans objet porte « sans objet » et sa raison.

**Erreur fréquente** : rapport réduit à « PC réparé » ; relevés absents (on ne peut plus prouver
l'avant) ; pièces posées sans référence ; aucune signature.

**À l'écrit** : « Pièces : posé bloc 650 W, n° de série PSU-65-88213 ; retiré bloc 550 W, filière
DEEE. »

**Repère rapide** : **6 parties · 14 rubriques · n° d'inventaire, pas de secret · signature ou
réserve**. Exercices liés : {_ex("E09", "E16")}.
"""


def _writing() -> str:
    return f"""**Objectifs** : séparer les faits des hypothèses ; employer le vocabulaire technique
exact ; ne jamais exposer une donnée du client.

## 6.1 Faits, hypothèses, conclusions

Un **fait** se vérifie : valeur et unité (« +12 V à 11,31 V »), message exact, constat (« voyant
éteint »). Une **hypothèse** est une cause supposée : on l'écrit comme telle (« hypothèse 1 :
bloc faible en charge »). Une **conclusion** ne s'écrit qu'après un test qui la prouve. « C'est
sûrement la box » dans la rubrique « Résultats » est une faute : c'est une hypothèse.

## 6.2 Le vocabulaire technique (AP-16)

{_vocab_table()}

Dans le rapport, le **mot juste** évite toute ambiguïté (le correcteur et le collègue suivant le
comprennent de la même façon). À l'oral avec le client, on emploie les mots simples de la
troisième colonne (chapitre 7).

## 6.3 Confidentialité

Ne s'écrivent **jamais** dans un rapport : un **mot de passe** ou un code PIN, une **clé de
récupération**, un numéro de **carte bancaire** vu à l'écran, ce qu'on a vu dans les **fichiers
personnels** ou les courriels, un **jugement** sur l'utilisateur. Un mot de passe trouvé sur un
post-it se signale de vive voix (le retirer, le changer) — il ne se recopie pas. Les règles de
protection des données sont dans [PR28](/uaa/ampcr-pratique-pr28).

## 6.4 Rédiger et relire

{_fig(WRITE_FIGURE)}

{_grid_table()}

**Procédure professionnelle** : rassembler, remplir, séparer faits et hypothèses, écrire la
validation, relire (aucune donnée sensible, chaque test refaisable), faire signer.

**Erreur fréquente** : recopier le mot de passe « pour la prochaine fois » ; « le client est
content » comme validation ; un sigle non défini dans une phrase destinée au client.

**À l'écrit** : « Hypothèse 1 : prise abîmée lors du déménagement. Test : testeur sur le lien
B4-02 ↔ port 14, switch débranché. Résultat : paires 3-6 croisées, fil 7 coupé : prise en cause. »

**Repère rapide** : **fait = valeur · hypothèse = écrite comme telle · mot juste · aucun
secret**. Exercices liés : {_ex("E08", "E18", "E19")}.
"""


def _client() -> str:
    ok = [text for text, kind in MESSAGES if kind == MSG_OK]
    return f"""**Objectifs** : restituer le résultat au client en mots simples ; escalader proprement ;
ranger chaque information au bon endroit.

## 7.1 Restituer au client

{_fig(HANDOVER_FIGURE)}

{_fig(HANDOVER_DO_FIGURE)}

Le client veut savoir **ce qui n'allait pas**, **ce qui a été fait**, **si c'est vérifié** et
**ce qu'il doit faire**. Exemples de phrases adaptées :

{chr(10).join(f"- « {text} »" for text in ok)}

## 7.2 Escalader

Quand un contrôle échoue et que la suite dépasse son rôle, ses droits ou ses compétences, on
**escalade** — vers le niveau 2, un service central, le fabricant ou le prestataire. Les
contrôles d'escalade de [PR26](/uaa/ampcr-pratique-pr26) s'appliquent aussi en fin
d'intervention :

{_escalation_list()}

Un message d'escalade identifie le poste et la demande, dit **ce qui a été fait**, donne les
**relevés** et les **tests**, formule **ce qui est demandé** et l'urgence ; le client est informé
et le rapport note la réserve.

## 7.3 Documenter

Chaque information a son lecteur et son endroit : {", ".join(f"**{t.lower()}**" for t in DOC_TARGETS)}.
Le **rapport** sert au client (verdict, risques, recommandation, signature) ; le **journal** à
l'atelier (chaque opération, retour arrière compris) ; la **base de connaissances** aux collègues
(symptôme, cause, solution qui a marché) ; l'**inventaire** au parc (pièce posée, n° de série,
garantie, adresse IP).

**Procédure professionnelle** : résumer, montrer, prévenir, conseiller, faire signer ; puis
documenter avant de partir.

**Erreur fréquente** : réciter les sigles au client ; promettre « plus jamais » ; accuser
l'utilisateur ou le prestataire précédent ; escalader par « ça ne marche pas, voyez ».

**À l'écrit** : « Message d'escalade : bureau 7, prise B7-01, port 22. Prise refaite, testeur
8 fils conformes ; deux appareils à 100 Mb/s sur cette prise, 1000 Mb/s sur la prise voisine.
Merci de vérifier le réglage de vitesse du port 22. »

**Repère rapide** : **mots simples · test montré · limites dites · escalade avec relevés · chaque
information à sa place**. Exercices liés : {_ex("E11", "E12", "E20", "E21")}.
"""


def _forms() -> str:
    checklist = "\n".join(f"- **{title}** : " + " ; ".join(items) + "." for title, items in FINAL_CHECKLIST)
    sections = ", ".join(f"« {s} »" for s in REPORT_SECTIONS)
    return f"""**Objectifs** : disposer des formulaires du cours sur papier ; ne rien oublier avant
de partir.

## 8.1 Formulaires imprimables (A4)

Trois formulaires vierges, à imprimer (Ctrl+P, format A4) pour s'entraîner à la main comme à
l'épreuve :

{_forms_list()}

Le rapport reprend les six parties du modèle ({sections}) ; la fiche de contrôles reprend les
six familles et le tableau avant / après ; le journal reprend les rubriques du test
reproductible et du retour arrière.

## 8.2 La liste de contrôle de clôture

{_fig(CHECKLIST_FIGURE)}

{checklist}

**Procédure professionnelle** : cocher la liste **avant** de ranger les outils ; une case vide
= on ne part pas.

**Erreur fréquente** : partir sans faire constater ; oublier d'effacer la copie temporaire des
données ; laisser le compte technique actif.

**À l'écrit** : « Liste de clôture cochée : critères mesurés, compte technique supprimé, copie
temporaire effacée, test refait devant la cliente, rapport signé. »

**Repère rapide** : **mesuré · remis en état · constaté · signé · documenté**. Exercices liés :
{_ex("E05", "E18")}.
"""


def _examples() -> str:
    return (
        "Cinq rapports modèles complets, un par grand type d'intervention de l'épreuve : PC (matériel), système "
        "d'exploitation, câblage RJ45, réseau, partage de dossiers. Chacun donne les quatorze rubriques, les critères "
        "avant / après, le verdict et la décision, le journal des opérations et le message au client. Les résultats, "
        "les verdicts, les décisions et les contrôles exigés sont **calculés** depuis les règles du cours ; le "
        "rapport 4 montre une **validation avec réserve**, le rapport 2 un **retour arrière** noté au journal.\n\n"
        + "\n".join(_report_html(i, r) for i, r in enumerate(REPORTS, start=1))
    )


def _pitfalls() -> str:
    return """> **Déclarer « réparé » sans critère mesuré**, ou parce que c'est « mieux qu'avant ».

> **S'arrêter au test fonctionnel** et oublier la stabilité, le réseau, les pilotes ou la sécurité.

> **Tester avec son propre compte** au lieu de celui de l'utilisateur.

> **Écrire « OK », « fait », « ça marche »** comme résultat.

> **Reconstituer le journal de mémoire** en fin de journée.

> **Enchaîner les modifications au hasard** après un échec au lieu de revenir à l'état initial.

> **Cacher une régression** ou un résultat non concluant.

> **Présenter une hypothèse comme un fait** (« c'est sûrement la box »).

> **Recopier un mot de passe ou une clé** dans le rapport.

> **Noyer le client sous les sigles**, ou lui promettre que la panne ne reviendra jamais.

> **Escalader sans relevés** (« ça ne marche pas, voyez »).

> **Partir sans signature** ni documentation.
"""


def _exercises_intro() -> str:
    return f"""{len(PRACTICE_ITEMS)} exercices corrigés : **contrôles finaux** (famille de chaque test,
contrôles manquants) ; **critères avant / après** (résultats et verdict, critère mesurable) ;
**journal et tests reproductibles** ; **corrections de rapports** (données sensibles, rubriques
manquantes, validation abusive, évaluation sur la grille) ; **communication au client** ;
**retour arrière, décision et escalade** ; **documentation** ; **deux schémas à compléter**
(arbre de clôture, structure du rapport) ; un **parcours d'arbre** et des **rédactions** (rapport
complet, réserve et limites). Rédige ta réponse sur papier **avant** d'ouvrir le corrigé ; toute
réponse équivalente et justifiée est acceptée. Ces mêmes exercices sont proposés dans
[S'entraîner](/uaa/{PR29_SLUG}/practice), avec correction après envoi.

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
    return f"""Le mini-examen se passe dans l'onglet [Examen blanc](/uaa/{PR29_SLUG}/exam) : **10 questions à réponse
libre**, chacune notée sur **2 points**, soit une note sur **{EXAM_TOTAL_POINTS}**. Les
questions ne figurent pas dans ce cours.

| N° | Thème | Type | Points |
|---|---|---|---|
{rows}

**Déroulement.** Chaque question est une situation complète : toutes les données nécessaires
sont dans l'énoncé et ses documents (critères avant / après, journaux, extraits de rapports
fictifs). **Aucune correction n'est visible pendant la passation** ; tes réponses sont
enregistrées au fur et à mesure. Après l'envoi, chaque réponse est corrigée selon le **barème
analytique** de la question (critères et points), puis tu vois ta note sur {EXAM_TOTAL_POINTS},
le corrigé et le barème.

**Ce que valorise le barème.** Un **verdict exact** tiré des mesures, les **contrôles exigés**,
une **décision** justifiée (signature, retour arrière, escalade, réserve), un rapport **complet,
précis et sans donnée sensible**, et un message **compréhensible** par le client — pas une liste
de mots.

**Nature de la correction.** Les réponses rédigées reçoivent une **proposition de correction
automatique** (assistée par IA) appuyée sur le barème : c'est un repère d'entraînement, pas une
note officielle ; en cas de doute, compare ta réponse au corrigé.
"""


def _memo() -> str:
    return """## Mémo

- **Critère d'acceptation** : quoi, avec quoi, quelle valeur ; écrit avec le client, avant.
- **Avant / après** : même mesure, mêmes conditions ; atteint, non atteint, non concluant.
- **Verdict** : un non atteint = non validé ; sinon un non concluant = réserve ; sinon validé.
- **Contrôles** : fonctionnel et sécurité toujours ; stabilité, performance, réseau, pilotes
  selon l'intervention.
- **Journal** : une ligne, une heure, une modification, un résultat chiffré ; jamais « OK ».
- **Test reproductible** : départ, outil, étapes, attendu, obtenu, quand.
- **Décision** : signer · retour arrière (préparé, puis vérifié) · escalade avec relevés ·
  réserve et suivi daté.
- **Rapport** : 6 parties, 14 rubriques ; faits ≠ hypothèses ; aucune donnée sensible.
- **Client** : mots simples, test montré, limites dites, recommandation datée, signature.
- **Documentation** : rapport (client), journal (atelier), base de connaissances (collègues),
  inventaire (parc).

## Glossaire des termes employés

- **Critère d'acceptation** : mesure et valeur cible qui prouvent la réparation.
- **Escalade** : transmission d'un problème à un niveau, un service ou un prestataire compétent.
- **Journal des opérations** : liste horodatée des opérations et de leurs résultats.
- **Non concluant** : résultat d'une mesure qui n'a pas pu être faite.
- **Régression** : fonction qui marchait avant l'intervention et ne marche plus après.
- **Réserve** : limite écrite sur la réception d'une intervention.
- **Retour arrière** : retour à l'état sauvegardé avant une modification, puis vérification.
- **Risque résiduel** : risque qui subsiste après l'intervention.
- **Test reproductible** : test décrit assez précisément pour être refait à l'identique.
"""


def _sources() -> str:
    return """## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles) : épreuve « uniquement par écrit » (p. 3) ; pp. 5-6, AP-15
  (dépannage) et AP-16 (vocabulaire technique). Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
  Programme officiel n° 345/2007/249 (option AMPCR).
- **Pratiques de centre de services** de type ITIL (critères d'acceptation, clôture d'un
  incident, escalade, base de connaissances), présentées comme repères et non comme norme.
- **Documentation Microsoft** : `ping`, `ipconfig`, `nslookup`, Gestionnaire de périphériques,
  points de restauration ; **pages de manuel Linux** pour les commandes équivalentes.
- **Règlement général sur la protection des données (RGPD)** : confidentialité des données
  vues pendant une intervention (rappel de PR28).

Les contrôles exigés, les résultats avant / après, les verdicts, les décisions, les défauts de
journal, les rubriques manquantes, les données sensibles relevées, les notes de la grille et le
parcours de l'arbre de clôture sont **produits par programme** depuis des données **vérifiées
par des tests automatiques** ; les schémas et les formulaires en sont construits directement.
Aucun schéma n'est tiré d'une image générée ni d'une photographie.

## Compléments pédagogiques (non imposés par la liste officielle)

Les pp. 5-6 ne décrivent pas le rapport d'intervention. Sont des **compléments**, signalés comme
tels, indispensables pour rédiger une réponse écrite de technicien (AP-C01) :

- le **modèle de rapport** en six parties et quatorze rubriques, et sa grille d'évaluation ;
- les **six familles de contrôles** et le tableau des contrôles exigés par intervention
  (convention du cours) ;
- l'**arbre de clôture** (signer, retour arrière, escalade, réserve) ;
- les **formulaires imprimables**.

Chaque entreprise a son propre formulaire et ses propres règles de clôture : ils font foi.

## Supports fictifs

Les personnes, entreprises, équipements, relevés, journaux et rapports de ce cours sont
**fictifs** et reconstitués pour l'entraînement ; ils ne décrivent aucun client réel. Aucun
n'est une question officielle ou déjà posée par le Jury.
"""


def pr29_course_sections() -> list[tuple[str, str]]:
    """Blocs du cours (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("PR29 — Objectifs et place dans l'épreuve", _objectives()),
        ("PR29 — 1. Critères d'acceptation : définir avant, mesurer après", _criteria()),
        ("PR29 — 2. Les six familles de contrôles finaux", _checks()),
        ("PR29 — 3. Journal des opérations et tests reproductibles", _journal()),
        ("PR29 — 4. Retour arrière, restauration et résultats non concluants", _rollback()),
        ("PR29 — 5. Le compte rendu structuré : six parties, quatorze rubriques", _structure()),
        ("PR29 — 6. Rédiger : faits, hypothèses, vocabulaire technique et confidentialité", _writing()),
        ("PR29 — 7. Restituer au client, escalader et documenter", _client()),
        ("PR29 — 8. Formulaires imprimables et liste de clôture", _forms()),
        ("PR29 — Exemples : cinq rapports modèles complets", _examples()),
        ("PR29 — Pièges et erreurs fréquentes", _pitfalls()),
        (f"PR29 — Exercices corrigés ({len(PRACTICE_ITEMS)}) et leurs corrigés", _exercises_intro()),
        ("PR29 — Mini-examen noté sur 20 : mode d'emploi", _mini_exam()),
        ("PR29 — Fiche mémo et glossaire", _memo()),
        ("PR29 — Sources et compléments pédagogiques", _sources()),
    ]
