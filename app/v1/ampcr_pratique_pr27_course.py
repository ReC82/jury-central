"""Cours PR27 « Construire et justifier une procédure de diagnostic » — parcours AMPCR pratique
écrite (ticket #226).

Matière : intégralement celle du ticket #226 (cycle hypothèse → test discriminant → résultat
attendu → interprétation → action → validation ; diagnostic du moins invasif au plus invasif,
approche par couches, isolation de variables, test croisé, contrôle de configuration, journaux,
conditions de reproduction ; arbres décisionnels matériel / démarrage / système / réseau ; test
négatif et faux positifs, alternatives et escalade, conservation de preuves, plan de retour
arrière, mesure d'impact et sécurité ; six dossiers mixtes résolus : démarrage, périphérique,
DHCP, DNS, partage, panne intermittente), découpée en blocs titrés (le titre pilote le type de
carte, `app.card_kind` : aucun titre de bloc théorique ne contient « examen », « source »,
« ressource », « exemple », « exercice », « méthode », « piège », « attention », « transfert »
ni « mémo »).
Règles, arbres et schémas : `app.v1.ampcr_pratique_pr27_figures` ; exercices et mini-examen :
`app.v1.ampcr_pratique_pr27_bank`. Le cours renvoie aux cours techniques publiés (PR06, PR12,
PR20, PR23, PR24) pour le détail de chaque panne, et à PR26 pour la demande et l'escalade.
"""

from html import escape

from app.v1.ampcr_pratique_pr06_course import _exercise_card, _fig, _req
from app.v1.ampcr_pratique_pr27_bank import EXAM_ITEMS, EXAM_TOTAL_POINTS, PRACTICE_ITEMS
from app.v1.ampcr_pratique_pr27_figures import (
    CASES,
    CROSS_FIGURE,
    D6_FACTORS,
    D6_HEADER,
    D6_ROWS,
    DHCP_FIGURE,
    EVIDENCE_FIGURE,
    FALSE_NEGATIVE,
    FALSE_POSITIVE,
    FALSE_RESULTS,
    LADDER_FIGURE,
    LEVELS,
    METHOD_FIGURE,
    NET_LAYERS_FIGURE,
    P_BACKUP,
    PC_LAYERS_FIGURE,
    PROCEDURES,
    ROLLBACK_FIGURE,
    STATIC_FIGURES,
    STRATEGIES,
    TREE_FIGURES,
    TREES,
    WRITTEN_AT,
    Case,
    level_label,
)
from app.v1.ampcr_pratique_visuals import render_figure

PR27_TITLE = "Construire et justifier une procédure de diagnostic"
PR27_SLUG = "ampcr-pratique-pr27"

_SCHEMAS_BY_PATH = {path: figure for figure, path in STATIC_FIGURES}


def _card(number: int, item) -> str:
    """Carte d'exercice de PR06 ; un schéma à compléter est affiché (SVG) avant sa
    description textuelle."""
    html = _exercise_card(number, item, anchor_prefix="pr27")
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


def _levels_table() -> str:
    rows = [
        (str(lv.number), lv.name, lv.examples, " ; ".join(lv.precautions) or "aucune : rien n'est modifié")
        for lv in LEVELS
    ]
    return _html_table(("Niveau", "Nom", "Exemples", "Précautions avant le test"), rows,
                       caption="Échelle d'invasivité (convention du cours)")


def _strategies_list() -> str:
    return "\n".join(f"- **{name}** : {detail}" for name, detail in STRATEGIES)


def _false_table() -> str:
    rows = [(text, "faux positif" if kind == FALSE_POSITIVE else "faux négatif", why) for text, kind, why in FALSE_RESULTS]
    return _html_table(("Situation", "Type", "Pourquoi le test trompe"), rows)


def _trees_list() -> str:
    return "\n".join(f"{i}. **{t.title}** — départ : {t.start}" for i, t in enumerate(TREES, start=1))


def _trees_figures() -> str:
    return "".join(_fig(f) for f in TREE_FIGURES)


# =============================================================================================
# Six dossiers entièrement résolus (hypothèses écartées, cause et parcours calculés)
# =============================================================================================


def _tests_table(c: Case) -> str:
    rows = []
    for i, t in enumerate(c.tests):
        alive = c.alive_before(i)
        after = c.alive_before(i + 1)
        expected = " · ".join(f"H{h + 1} : {t.expected[h]}" for h in alive)
        dropped = [f"H{h + 1}" for h in alive if h not in after]
        left = ", ".join(f"H{h + 1}" for h in after)
        rows.append((
            f"T{i + 1}. {t.label} ({level_label(t.level)})",
            expected,
            t.observed,
            f"écarte {', '.join(dropped)} ; reste {left}",
        ))
    return _html_table(("Test (niveau)", "Résultat attendu selon l'hypothèse", "Résultat obtenu", "Interprétation"),
                       rows, caption=f"Dossier {c.key} — tests du moins au plus invasif (support fictif)")


def _case_html(number: int, c: Case) -> str:
    hyps = "\n".join(f"- **H{i}** — {h}" for i, h in enumerate(c.hypotheses, start=1))
    symptoms = " ; ".join(c.symptoms)
    question, track = c.tree_result
    tree_line = (
        f"Arrêt à la question {question} (« {c.tree.questions[question - 1][0]} » → non) : {track}"
        if question is not None
        else f"Toutes les réponses sont « oui » : {track}"
    )
    journal = ""
    if c.key == "D6":
        factors = " ; ".join(f"{name} = « {value} »" for name, value in D6_FACTORS)
        journal = (
            "\n\n" + _html_table(D6_HEADER, list(D6_ROWS), caption="Journal de la réceptionniste (support fictif)")
            + f"\n\n**Conditions de reproduction.** Facteur présent à chaque coupure et jamais sans coupure : "
            f"{factors}. Les autres colonnes changent ou restent identiques avec ou sans coupure : elles ne "
            "désignent rien.\n"
        )
    validation = "\n".join(f"- {v}" for v in c.validation)
    cause = c.hypotheses[c.cause]
    return f"""## Dossier {number} — {c.theme} : {c.title}

**Situation.** {c.context}

**Symptômes observés.** {symptoms}.{journal}

**1. Hypothèses** (de la plus simple à vérifier à la plus lourde) :

{hyps}

**2. Tests discriminants, résultat attendu écrit avant chaque test, interprétation :**

{_tests_table(c)}

**3. Cause retenue.** H{c.cause + 1} — {cause}.

**4. Arbre « {c.tree.title} ».** {tree_line}

**5. Action** ({level_label(c.action_level)}). {c.action}

**6. Mesure d'impact et sécurité.** {c.impact}

**7. Retour arrière.** {c.rollback}

**8. Preuves conservées.** {c.evidence}

**9. Validation.**

{validation}

**10. Escalade.** {c.escalation}

**Conclusion rédigée.** « {c.conclusion} »
"""


# =============================================================================================
# Sections du cours (titre du bloc, Markdown / HTML)
# =============================================================================================


def _objectives() -> str:
    return f"""## Ce que tu sauras faire, par écrit

L'épreuve pratique AMPCR se passe **uniquement par écrit** (consignes officielles 2026-2027/1,
p. 3). Dans un dossier de dépannage, on attend une **procédure de diagnostic justifiée** : pas
une liste de gestes au hasard, mais des **tests choisis pour départager des hypothèses**, dans un
ordre défendable, avec leurs précautions. Tu dois savoir :

1. dérouler le cycle **hypothèse → test discriminant → résultat attendu → interprétation →
   action → validation** ;
2. ordonner les tests **du moins invasif au plus invasif**, avec la **mesure d'impact** et la
   **sécurité** de chacun ;
3. appliquer l'**approche par couches** et l'**isolation de variables** (une seule variable
   changée à la fois) ;
4. utiliser le **test croisé**, et te méfier du **test négatif**, des **faux positifs** et des
   faux négatifs ;
5. faire un **contrôle de configuration**, lire des **journaux** (logs) et établir les
   **conditions de reproduction** d'une panne ;
6. suivre **quatre arbres décisionnels** : matériel, démarrage (boot), système (OS) et réseau ;
7. assurer la **conservation de preuves**, préparer un **plan de retour arrière**, proposer des
   **alternatives** et décider d'une **escalade**.

Ce cours contient **{len(PROCEDURES)} procédures illustrées** et **{len(TREES)} arbres de décision** :

{_procedures_list()}

## Exigences travaillées dans ce cours

{_req("AP-15")}
{_req("AP-C01")}

AP-15 est une exigence **officielle** (consignes, p. 5) ; AP-C01 est un **complément** du
parcours (rédiger une réponse de technicien et justifier chaque choix). La protection des
données (AP-C03) et la sécurité de l'intervention dans le matériel (AP-C02) sont reprises aux
chapitres 2 et 7.

## Lien avec la théorie et les autres cours

La théorie AMPCR présente la démarche de dépannage : [MC29](/uaa/ampcr-mc29) et
[MC30](/uaa/ampcr-mc30). Ce cours-ci est **pratique** : il apprend à **construire et
écrire** la procédure. Il s'appuie sur [PR26](/uaa/ampcr-pratique-pr26) (analyse de la demande,
priorité, escalade) et renvoie aux cours techniques pour le détail de chaque panne : matériel
([PR06](/uaa/ampcr-pratique-pr06)), logiciel ([PR12](/uaa/ampcr-pratique-pr12)), adressage IP
([PR20](/uaa/ampcr-pratique-pr20)), partages ([PR23](/uaa/ampcr-pratique-pr23)) et réseau
([PR24](/uaa/ampcr-pratique-pr24)).

## Comment travailler ce cours

Lis les chapitres dans l'ordre : chacun donne ses **objectifs**, la **théorie**, la
**procédure professionnelle**, l'**erreur fréquente**, ce qu'on attend **à l'écrit** et un
**repère rapide**, avec un renvoi vers les exercices liés. Étudie ensuite les **six dossiers
entièrement résolus**, fais les **{len(PRACTICE_ITEMS)} exercices corrigés** (dont huit procédures à
ordonner et justifier, et deux **schémas à compléter**), puis passe le **mini-examen noté sur
{EXAM_TOTAL_POINTS}** dans l'onglet « Examen blanc ».

> **Important —** les personnes, entreprises, adresses et dossiers de ce cours sont des
> **supports fictifs** construits pour s'entraîner (rédaction : {WRITTEN_AT}). L'échelle
> d'invasivité 0 à 5 et la règle « à niveau égal, le plus rapide d'abord » sont des
> **conventions du cours** ; la procédure de l'entreprise fait foi. Aucun exercice n'est une
> question officielle ni une question déjà posée par le Jury.
"""


def _cycle() -> str:
    return f"""**Objectifs** : transformer une liste d'hypothèses en tests qui prouvent quelque chose ;
écrire chaque test de façon justifiée.

## 1.1 Le cycle de diagnostic

{_fig(METHOD_FIGURE)}

On applique ce cycle **à chaque hypothèse**, jusqu'à ce qu'il n'en reste qu'une :

- **Hypothèse** : une cause possible qui explique **tous** les symptômes observés. Une hypothèse
  qui n'explique pas un symptôme est déjà fragile.
- **Test discriminant** : un test dont le résultat **change selon l'hypothèse vraie**. Un test
  qui donne le même résultat pour toutes les hypothèses (redémarrer un PC dont l'écran est noir,
  quelle que soit la cause) ne **départage rien** : il fait perdre du temps.
- **Résultat attendu** : écrit **avant** de lancer le test, pour chaque hypothèse (« si c'est le
  câble : image avec un câble neuf ; si c'est l'écran : toujours rien »). Sans résultat attendu,
  on interprète après coup ce que l'on espérait voir.
- **Interprétation** : on compare le résultat obtenu aux résultats attendus ; on **écarte** les
  hypothèses contredites et on **garde** les autres.
- **Action** : on corrige la cause **confirmée**, jamais une cause supposée, avec ses
  précautions (chapitre 2) et son plan de retour arrière (chapitre 7).
- **Validation** : on refait **le test du symptôme de départ** et on contrôle que rien d'autre
  n'est touché. Une panne intermittente se valide sur une **durée**.

## 1.2 Écrire un test justifié

Sur la copie, chaque test tient en une ligne de tableau : **hypothèses visées · test (niveau) ·
résultat attendu selon l'hypothèse · résultat obtenu · interprétation**. Les six dossiers
résolus suivent exactement cette forme.

**Procédure professionnelle** : 1) lister les hypothèses ; 2) choisir le test le moins invasif
qui en départage au moins deux ; 3) écrire les résultats attendus ; 4) faire le test et noter le
résultat obtenu ; 5) écarter ; 6) recommencer jusqu'à une seule hypothèse ; 7) agir ; 8) valider.

**Erreur fréquente** : enchaîner des gestes (« je redémarre, je réinstalle le pilote, je
change le câble ») sans dire ce que chacun prouve ; ou changer trois choses à la fois.

**À l'écrit** : « T2 — même écran et même câble sur un portable connu bon (niveau 2). Attendu :
écran en panne → pas d'image ; sortie vidéo du PC → image. Obtenu : image. H3 retenue. »

**Repère rapide** : **une hypothèse · un test qui départage · le résultat attendu écrit avant ·
on écarte · on valide sur le symptôme de départ**. Exercices liés : {_ex("E01", "E06")}.
"""


def _invasive() -> str:
    return f"""**Objectifs** : ordonner les tests du moins invasif au plus invasif ; mesurer l'impact de
chaque test et prendre les précautions de sécurité avant de le lancer.

## 2.1 L'échelle d'invasivité

{_fig(LADDER_FIGURE)}

Un test est **invasif** quand il modifie l'état du poste, interrompt des utilisateurs ou risque
les données. Convention du cours : six niveaux, **du moins invasif (0) au plus invasif (5)** ;
**à niveau égal, le plus rapide d'abord**. Commencer par le bas de l'échelle, c'est risquer de
détruire une preuve ou des données avant d'avoir compris la panne.

{_levels_table()}

## 2.2 Mesure d'impact et sécurité

Avant chaque test, on se pose trois questions et on note les réponses :

- **Qui est touché, et combien de temps ?** Redémarrer un switch coupe tous les postes, les
  téléphones et le Wi-Fi qui y sont branchés ; redémarrer un poste coupe son utilisateur.
- **Quand ?** Un test qui coupe un service se fait à un moment annoncé (pause, fin de journée).
- **Quel risque ?** Électrique (hors tension, débranché, bracelet antistatique), pour les
  données ({P_BACKUP}), pour la garantie (on n'ouvre pas un appareil sous garantie).

**Procédure professionnelle** : 1) donner un niveau à chaque test ; 2) les classer ; 3) pour
chacun, écrire impact et précautions ; 4) annoncer les coupures ; 5) ne passer au niveau suivant
que si les tests précédents n'ont pas suffi.

**Erreur fréquente** : réinstaller « pour gagner du temps » avant d'avoir lu les journaux ;
redémarrer un switch à 10 h sans prévenir ; ouvrir un portable sous garantie.

**À l'écrit** : « Redémarrage de la box ({level_label(2)}) : coupe les huit postes environ 5
minutes ; fait après avoir prévenu l'équipe et fait enregistrer les travaux. »

**Repère rapide** : **regarder · lire · manipuler · configurer · ouvrir · effacer — dans cet
ordre, et chaque niveau ajoute ses précautions**. Exercices liés : {_ex("E02", "E03", "E20", "E22")}.
"""


def _layers() -> str:
    return f"""**Objectifs** : découper le problème en couches ; ne changer qu'une variable à la fois.

## 3.1 Approche par couches

Un service ne fonctionne que si **toutes les couches du dessous** fonctionnent. On teste donc
couche par couche, et on **valide** chacune avant de passer à la suivante.

{_fig(NET_LAYERS_FIGURE)}

{_fig(PC_LAYERS_FIGURE)}

Trois façons de parcourir les couches :

{_strategies_list()}

Le détail des couches réseau et de leurs commandes est dans [PR20](/uaa/ampcr-pratique-pr20) et
[PR24](/uaa/ampcr-pratique-pr24) ; celui du démarrage d'un PC dans [PR06](/uaa/ampcr-pratique-pr06).

## 3.2 Isolation de variables

**Une seule variable change entre deux essais.** Si l'on change à la fois le câble et le port,
et que cela fonctionne, on ne sait pas lequel était en cause : on ne peut ni écrire la cause ni
prévenir la récidive. On procède par **substitution** : on remplace **un** élément par un
élément **connu bon** (câble, port, prise, compte, profil), on teste, puis on passe au suivant.

Quand beaucoup d'éléments sont candidats (huit programmes au démarrage), on **coupe par
moitiés** : on en réactive quatre ; si la panne revient, le coupable est parmi eux ; puis deux,
puis un. Huit programmes demandent au plus trois essais.

**Procédure professionnelle** : 1) choisir la couche de départ selon le symptôme ; 2) tester la
couche ; 3) la valider ou y rester ; 4) dans la couche en cause, substituer un élément à la fois ;
5) noter chaque essai.

**Erreur fréquente** : chercher le DNS d'un poste sans lien ; changer câble, port et pilote en
même temps.

**À l'écrit** : « Même câble, autre port USB (seule variable changée) : toujours non détectée.
Le port est écarté ; reste le câble. »

**Repère rapide** : **du bas vers le haut · une couche validée avant la suivante · une variable
à la fois · par moitiés quand ils sont nombreux**. Exercices liés : {_ex("E12", "E16", "E23")}.
"""


def _cross() -> str:
    positives = sum(1 for _t, k, _w in FALSE_RESULTS if k == FALSE_POSITIVE)
    negatives = sum(1 for _t, k, _w in FALSE_RESULTS if k == FALSE_NEGATIVE)
    return f"""**Objectifs** : savoir si la panne suit l'élément ou reste sur le poste ; ne pas se faire
tromper par un test.

## 4.1 Le test croisé

Le **test croisé** se fait en deux montages : **A**, l'élément suspect sur un **poste sain** ;
**B**, un élément **connu bon** sur le **poste suspect**. Les deux résultats ensemble désignent
le coupable.

{_fig(CROSS_FIGURE)}

Si les deux montages échouent, il y a deux causes, ou l'élément « sain » ne l'est pas : on le
revérifie. Si les deux fonctionnent, la panne n'est pas reproduite : un mauvais contact a pu être
corrigé par le démontage, ou la panne est intermittente (chapitre 5).

## 4.2 Test négatif, faux positifs et faux négatifs

On dit qu'un test est **positif** quand il signale une panne, **négatif** quand il n'en signale
pas.

- Un **faux positif** signale une panne qui n'existe pas : le test échoue pour une autre raison
  (pare-feu qui bloque le ping, piles du testeur, mauvaise entrée HDMI, cordon de test coupé).
- Un **faux négatif** ne voit pas une panne qui existe : le test ne mesure pas la bonne chose,
  il est trop court, ou il est fait hors des conditions de la panne.
- Un **test négatif n'innocente que ce qu'il teste vraiment** : un ping réussi prouve que la
  machine répond, pas que le partage fonctionne ; un testeur de continuité prouve la continuité,
  pas la qualité des paires.

Parade : vérifier l'outil et le montage sur un élément **témoin** connu bon, et confirmer un
résultat important par un **second test différent**. Ci-dessous, {positives} faux positifs et
{negatives} faux négatifs :

{_false_table()}

**Procédure professionnelle** : 1) préparer un élément connu bon ; 2) faire le montage A ; 3)
faire le montage B ; 4) conclure avec le tableau ; 5) se demander si le test pouvait voir la
panne cherchée, sinon le confirmer autrement.

**Erreur fréquente** : conclure « carte réseau morte » avec un cordon de test non vérifié ;
déclarer un câble « bon » parce que le testeur de continuité est vert.

**À l'écrit** : « A (clé suspecte sur un portable sain) : connexion ; B (clé neuve sur le PC) :
échec. La clé n'est pas en cause ; reste le port USB, le pilote ou le profil Wi-Fi du PC. »

**Repère rapide** : **la panne suit l'élément → l'élément · elle reste → le poste · un test
négatif ne prouve que ce qu'il mesure**. Exercices liés : {_ex("E04", "E05", "E16")}.
"""


def _config_logs() -> str:
    return f"""**Objectifs** : trouver un réglage modifié par comparaison ; lire un journal ; rendre
reproductible une panne qui ne l'est pas.

## 5.1 Contrôle de configuration

On compare, **paramètre par paramètre**, la configuration relevée à une **référence écrite** :
fiche du poste, plan d'adressage, configuration d'un poste identique qui fonctionne, export
d'avant la panne. Chaque écart est une hypothèse. Exemple : un poste dont le masque est
255.255.0.0 et la passerelle 192.168.2.1 au lieu de 255.255.255.0 et 192.168.20.1 joint le
serveur de son réseau, mais plus Internet ([PR20](/uaa/ampcr-pratique-pr20)).

## 5.2 Journaux (logs)

- **Windows** : Observateur d'événements, journaux **Système** et **Application** ; filtrer par
  niveau (Critique, Erreur) et par heure. Kernel-Power **41** et EventLog **6008** disent
  seulement qu'un arrêt n'était pas prévu : ce sont des **conséquences**, pas la cause.
- **Linux** : `journalctl -b -1 -p err` (erreurs du démarrage précédent), `dmesg` (noyau),
  `/var/log/syslog` (Debian, Ubuntu).

On lit dans l'**ordre chronologique**, on se place **juste avant** l'heure du problème et on
cherche le **premier** événement anormal ; les suivants en sont souvent la conséquence.

## 5.3 Conditions de reproduction

Une panne se diagnostique bien quand on sait la **reproduire**. On note les conditions exactes :
**qui**, **sur quel poste**, **quand**, **pendant quelle action**, **avec quel réseau ou quel
appareil branché**. Pour une panne **intermittente**, on tient un **journal** (pannes et moments
sans panne) et on cherche le **facteur présent à chaque panne et jamais sans** : ce facteur
donne le test qui reproduit la panne à volonté. Le dossier D6 en est un exemple complet.

**Procédure professionnelle** : 1) relever la configuration et la comparer à la référence ;
2) lire les journaux autour de l'heure du problème ; 3) noter les conditions de chaque
occurrence ; 4) chercher le facteur commun ; 5) reproduire la panne, puis tester l'hypothèse.

**Erreur fréquente** : prendre l'événement 41 pour la cause ; lire un journal sans regarder
l'heure ; tester une panne intermittente dix minutes et conclure qu'elle est réparée.

**À l'écrit** : « Trois erreurs disk 7 entre 16:41 et 16:57, avant l'arrêt forcé de 16:58 :
hypothèse disque défaillant ; sauvegarde immédiate, puis SMART. »

**Repère rapide** : **comparer à une référence · premier événement avant l'heure · facteur
présent à chaque panne et jamais sans**. Exercices liés : {_ex("E07", "E08", "E09")}.
"""


def _trees() -> str:
    return f"""**Objectifs** : suivre et écrire un arbre de décision exact pour les quatre familles de pannes.

## 6.1 Lire un arbre de décision

Chaque arbre pose des **questions fermées**, dans l'ordre des couches et du moins invasif au
plus invasif. On descend tant que la réponse est **« oui »** ; au **premier « non »**, on suit la
piste de droite, qui donne les tests suivants. Sur la copie, on écrit le chemin suivi (« 1 oui,
2 oui, 3 non → piste 3 ») : le correcteur voit le raisonnement.

{_trees_list()}

{_trees_figures()}

## 6.2 Bien utiliser les arbres

- Un arbre **oriente**, il ne remplace pas le test discriminant : chaque réponse « oui » ou
  « non » doit venir d'un **test noté**.
- La piste d'un arbre peut renvoyer à un autre arbre (démarrage → système) ou à un cours
  technique : PR06 pour le matériel, PR12 pour le logiciel, PR24 pour le réseau.
- L'arbre « réseau » s'arrête aux services : pour un partage, on continue avec l'arbre des
  partages de [PR24](/uaa/ampcr-pratique-pr24) et les droits de [PR23](/uaa/ampcr-pratique-pr23).

**Procédure professionnelle** : 1) choisir l'arbre selon le symptôme de départ ; 2) répondre à
chaque question par un test ; 3) s'arrêter au premier « non » ; 4) dérouler la piste avec le
cycle du chapitre 1 ; 5) écrire le chemin sur la copie.

**Erreur fréquente** : sauter des questions (« le lien, c'est sûrement bon ») ; répondre « oui »
sans test.

**À l'écrit** : « Arbre réseau : lien oui, adresse non (169.254.37.112) → piste DHCP : test croisé
d'un portable sur la même prise. »

**Repère rapide** : **matériel · démarrage · système · réseau — oui on descend, non on suit la
piste, et chaque réponse vient d'un test**. Exercices liés : {_ex("E10", "E11", "E12", "E13")}.
"""


def _evidence_rollback() -> str:
    return f"""**Objectifs** : ne rien perdre de ce qui prouve la panne ; pouvoir revenir à l'état initial
après chaque modification.

## 7.1 Conservation de preuves

Ce que l'on modifie ne peut plus être observé. Avant de toucher, on conserve les **preuves** :
elles servent au diagnostic, au rapport, à l'escalade et, en cas d'incident de sécurité, au
responsable.

{_fig(EVIDENCE_FIGURE)}

En cas d'**incident de sécurité** (prise de main à distance, fichiers chiffrés), on **isole** le
poste du réseau **sans l'éteindre ni rien effacer**, et on escalade : « nettoyer » soi-même
détruit les traces.

## 7.2 Plan de retour arrière

Toute modification à partir du **niveau 3** demande un **plan de retour arrière** écrit
**avant** : comment revenir, et à partir de quand.

{_fig(ROLLBACK_FIGURE)}

{_html_table(("Rubrique", "Contenu à écrire"), [
        ("État initial", "configuration exportée, version du pilote ou du micrologiciel, photo du câblage"),
        ("Sauvegarde", "point de restauration, copie de la configuration, ancien pilote conservé"),
        ("Modification", "une seule, décrite précisément"),
        ("Critère d'échec", "ce qui déclenche le retour et le délai maximum (ex. pas de réseau 5 min après)"),
        ("Retour arrière", "gestes exacts pour revenir (ex. « Restaurer le pilote », réimport de la configuration)"),
        ("Vérification", "retour à l'état initial contrôlé ; tout noté sur la fiche"),
    ], caption="Plan de retour arrière (modèle du cours)")}

**Procédure professionnelle** : 1) horodater et capturer ; 2) exporter journaux et
configuration ; 3) photographier le câblage ; 4) écrire le plan de retour arrière ; 5) modifier ;
6) tester ; 7) revenir ou valider.

**Erreur fréquente** : réinstaller un poste suspect « pour le nettoyer » ; mettre à jour un
pilote sans noter l'ancienne version ; débrancher toute une baie de brassage sans photo.

**À l'écrit** : « Avant : version du pilote notée, point de restauration créé. Critère d'échec :
écran noir ou plantage dans les 30 min. Retour : mode sans échec, « Restaurer le pilote ». »

**Repère rapide** : **preuves avant de toucher · état initial noté · critère d'échec écrit
avant · une modification à la fois**. Exercices liés : {_ex("E15", "E18", "E19")}.
"""


def _escalate() -> str:
    return f"""**Objectifs** : savoir s'arrêter ; proposer une solution provisoire ; rédiger la procédure
complète sur la copie.

## 8.1 Alternatives et escalade

Le diagnostic s'arrête quand la cause est trouvée, ou quand une **limite** est atteinte : action
hors de ses droits (switch, serveur, annuaire), appareil **sous garantie**, données menacées sans
copie, compétence ou pièces manquantes, durée dépassée. On applique alors l'arbre d'escalade de
[PR26](/uaa/ampcr-pratique-pr26) et on transmet **les preuves et les tests déjà faits**, avec
leurs résultats : le niveau suivant ne recommence pas tout.

En attendant, on propose une **alternative** (contournement) : poste ou portable de prêt, autre
prise du bon VLAN, écran externe, impression depuis un autre poste. On la note sur la fiche.

## 8.2 Rédiger la procédure de diagnostic sur la copie

{_html_table(("Colonne", "Ce qu'on y écrit"), [
        ("Hypothèses", "H1, H2… de la plus simple à vérifier à la plus lourde"),
        ("Test (niveau)", "le geste exact, son niveau d'invasivité, ses précautions"),
        ("Résultat attendu", "pour chaque hypothèse encore possible, écrit avant le test"),
        ("Résultat obtenu", "ce qui est réellement observé"),
        ("Interprétation", "hypothèses écartées, hypothèses restantes"),
        ("Action et validation", "correction de la cause confirmée, retour arrière, test du symptôme de départ"),
    ], caption="Procédure de diagnostic écrite (modèle du cours)")}

**Procédure professionnelle** : 1) remplir le tableau test par test ; 2) s'arrêter à une seule
hypothèse ou à une limite ; 3) agir ou escalader avec les preuves ; 4) proposer une alternative ;
5) valider.

**Erreur fréquente** : escalader en écrivant « ça ne marche pas » ; ouvrir un appareil sous
garantie ; laisser l'utilisateur sans solution provisoire.

**À l'écrit** : « Port 15 du switch en VLAN 99 (hors de mes droits) : escalade à
l'administrateur réseau avec ipconfig /all et les deux tests croisés ; le poste reste sur la prise
12-A en attendant. »

**Repère rapide** : **une limite = on transmet des faits · une alternative pour continuer à
travailler · le tableau de diagnostic sur la copie**. Exercices liés : {_ex("E14", "E17", "E21")}.
"""


def _examples() -> str:
    return (
        "Six dossiers entièrement résolus, du symptôme à la validation : démarrage, périphérique, DHCP, DNS, "
        "partage et panne intermittente. Dans chacun, les tests sont ordonnés du moins au plus invasif, chacun "
        "départage des hypothèses, et le chemin dans l'arbre de décision est indiqué. Le détail technique est dans "
        "[PR06](/uaa/ampcr-pratique-pr06), [PR20](/uaa/ampcr-pratique-pr20), [PR23](/uaa/ampcr-pratique-pr23) et "
        "[PR24](/uaa/ampcr-pratique-pr24). Une procédure illustrée accompagne le dossier DHCP :\n\n"
        + _fig(DHCP_FIGURE)
        + "\n".join(_case_html(i, c) for i, c in enumerate(CASES, start=1))
    )


def _pitfalls() -> str:
    return """> **Enchaîner des gestes sans hypothèse** ni résultat attendu : on ne sait plus ce qui a réparé.

> **Faire un test qui ne départage rien** (redémarrer « pour voir » quand toutes les hypothèses prévoient la même chose).

> **Commencer par l'action la plus lourde** : réinstallation, réinitialisation d'usine, formatage.

> **Changer plusieurs variables à la fois** : câble et port, pilote et paramètres.

> **Croire un test négatif** qui ne mesurait pas la panne cherchée, ou un test positif fait avec un outil défaillant.

> **Prendre une conséquence pour la cause** (événements 41 et 6008).

> **Redémarrer un équipement partagé sans mesurer l'impact** ni prévenir.

> **Modifier sans état initial ni plan de retour arrière.**

> **Effacer les preuves** : « nettoyer » un poste compromis, débrancher sans photographier.

> **Valider une panne intermittente sur un seul essai réussi.**
"""


def _exercises_intro() -> str:
    return f"""{len(PRACTICE_ITEMS)} exercices corrigés : **huit procédures à ordonner et justifier** (cycle de
diagnostic, tests du moins au plus invasif, adresse 169.254, retour arrière, test croisé d'une
barrette, imprimante réseau, coupure Internet, couches réseau) ; **choix et interprétation des
tests** (invasivité, test croisé, faux positifs et faux négatifs, test discriminant, contrôle de
configuration, journal, conditions de reproduction) ; **deux schémas à compléter** (arbres réseau
et démarrage) ; **deux arbres à parcourir** (système, matériel) ; **rédactions** (retour arrière,
preuves, mesure d'impact, alternative et escalade). Rédige ta réponse sur papier **avant**
d'ouvrir le corrigé ; toute réponse équivalente et justifiée est acceptée. Ces mêmes exercices
sont proposés dans [S'entraîner](/uaa/{PR27_SLUG}/practice), avec correction après envoi.

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
    return f"""Le mini-examen se passe dans l'onglet [Examen blanc](/uaa/{PR27_SLUG}/exam) : **10 questions à réponse
libre**, chacune notée sur **2 points**, soit une note sur **{EXAM_TOTAL_POINTS}**. Les
questions ne figurent pas dans ce cours.

| N° | Thème | Type | Points |
|---|---|---|---|
{rows}

**Déroulement.** Chaque question est une situation complète : toutes les données nécessaires
sont dans l'énoncé et ses documents (relevés, journaux, tableaux fictifs). **Aucune correction
n'est visible pendant la passation** ; tes réponses sont enregistrées au fur et à mesure. Après
l'envoi, chaque réponse est corrigée selon le **barème analytique** de la question (critères et
points), puis tu vois ta note sur {EXAM_TOTAL_POINTS}, le corrigé et le barème.

**Ce que valorise le barème.** Des **tests qui départagent**, le **résultat attendu** annoncé,
l'ordre **du moins au plus invasif**, les **précautions** (impact, sauvegarde, retour arrière)
et une conclusion **justifiée par les tests** — pas une liste de gestes. Une autre procédure
juste et justifiée est acceptée.

**Nature de la correction.** Les réponses rédigées reçoivent une **proposition de correction
automatique** (assistée par IA) appuyée sur le barème : c'est un repère d'entraînement, pas une
note officielle ; en cas de doute, compare ta réponse au corrigé.
"""


def _memo() -> str:
    return """## Mémo

- **Cycle** : hypothèse → test discriminant → résultat attendu (écrit avant) → interprétation →
  action → validation sur le symptôme de départ.
- **Invasivité** : 0 observer · 1 lire · 2 manipuler · 3 configurer · 4 ouvrir · 5 effacer ; du
  moins au plus invasif, à niveau égal le plus rapide ; impact et précautions avant chaque test.
- **Couches** : du bas vers le haut (ascendante), du haut (descendante) ou par le milieu
  (division) ; une couche validée avant la suivante.
- **Isolation** : une variable à la fois ; par moitiés quand les candidats sont nombreux.
- **Test croisé** : A = suspect sur poste sain, B = sain sur poste suspect ; la panne suit
  l'élément → l'élément ; elle reste → le poste.
- **Faux positif / faux négatif** : contrôler l'outil sur un témoin ; un test négatif ne prouve
  que ce qu'il mesure.
- **Configuration, journaux, reproduction** : comparer à une référence ; premier événement avant
  l'heure ; facteur présent à chaque panne et jamais sans.
- **Arbres** : matériel, démarrage, système, réseau ; chaque réponse vient d'un test.
- **Preuves et retour arrière** : capturer et exporter avant ; état initial, critère d'échec,
  une modification, tester, revenir ou valider.
- **Limite atteinte** : escalader avec les preuves et les tests faits ; proposer une alternative.

## Glossaire des termes employés

- **Approche par couches** : test couche par couche, chacune validée avant la suivante.
- **Conditions de reproduction** : circonstances exactes dans lesquelles la panne se produit.
- **Contrôle de configuration** : comparaison des réglages relevés avec une référence écrite.
- **Faux négatif** : test qui ne voit pas une panne qui existe.
- **Faux positif** : test qui signale une panne qui n'existe pas.
- **Invasif** : qui modifie le poste, interrompt des utilisateurs ou risque les données.
- **Isolation de variables** : un seul élément changé entre deux essais.
- **Plan de retour arrière** : moyen écrit à l'avance de revenir à l'état initial.
- **Test croisé** : échange d'un élément suspect et d'un élément connu bon entre deux postes.
- **Test discriminant** : test dont le résultat diffère selon l'hypothèse vraie.
- **Test négatif** : test qui ne signale pas de panne.
- **Validation** : nouveau test du symptôme de départ qui prouve la réparation.
"""


def _sources() -> str:
    return """## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), p. 5 : « Dépannage sur les dysfonctionnements courants
  (hardware ou software) » (AP-15) ; p. 3 : épreuve « uniquement par écrit ». Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
  Programme officiel n° 345/2007/249 (option AMPCR).
- **Documentation Microsoft** (Windows 11) : Observateur d'événements (Kernel-Power 41, EventLog
  6008), démarrage minimal, mode sans échec, `sfc /scannow`, `DISM /Online /Cleanup-Image
  /RestoreHealth`, `ipconfig`, `nslookup`, `whoami /groups`, « Restaurer le pilote ».
- **Pages de manuel Linux** : `journalctl`, `dmesg`.
- **Modèle en couches** (OSI et TCP/IP) pour l'approche par couches du réseau.

L'échelle d'invasivité, l'ordre des tests, les conclusions du test croisé, les arbres de
décision, les hypothèses écartées et les causes des six dossiers sont **produits par
programme** depuis des données **vérifiées par des tests automatiques** ; les schémas en sont
dessinés directement. Aucun schéma n'est tiré d'une image générée ni d'une photographie.

## Compléments pédagogiques (non imposés par la liste officielle)

La p. 5 cite le dépannage des dysfonctionnements courants. Sont des **compléments**, signalés
comme tels, utiles pour rédiger une procédure de diagnostic :

- la rédaction de la procédure sous forme de tableau justifié (AP-C01) ;
- les **conventions du cours** : échelle d'invasivité 0 à 5, précautions par niveau, règle
  « à niveau égal, le plus rapide d'abord » ;
- la sauvegarde et l'autorisation avant une opération destructive (complément AP-C03) et la
  sécurité de l'intervention dans le matériel (complément AP-C02).

## Supports fictifs

Les personnes, entreprises, adresses IP, journaux et dossiers de ce cours sont **fictifs** et
reconstitués pour l'entraînement ; ils ne décrivent aucun client réel. Aucun n'est une question
officielle ou déjà posée par le Jury.
"""


def pr27_course_sections() -> list[tuple[str, str]]:
    """Blocs du cours (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("PR27 — Objectifs et place dans l'épreuve", _objectives()),
        ("PR27 — 1. Le cycle de diagnostic : hypothèse, test discriminant, résultat attendu, interprétation, action, validation", _cycle()),
        ("PR27 — 2. Du moins invasif au plus invasif : mesure d'impact et sécurité", _invasive()),
        ("PR27 — 3. Approche par couches et isolation de variables", _layers()),
        ("PR27 — 4. Test croisé, test négatif, faux positifs et faux négatifs", _cross()),
        ("PR27 — 5. Contrôle de configuration, journaux et conditions de reproduction", _config_logs()),
        ("PR27 — 6. Quatre arbres de décision : matériel, démarrage, système, réseau", _trees()),
        ("PR27 — 7. Conservation de preuves et plan de retour arrière", _evidence_rollback()),
        ("PR27 — 8. Alternatives, escalade et rédaction de la procédure", _escalate()),
        ("PR27 — Exemples : six dossiers de diagnostic entièrement résolus", _examples()),
        ("PR27 — Pièges et erreurs fréquentes", _pitfalls()),
        (f"PR27 — Exercices corrigés ({len(PRACTICE_ITEMS)}) et leurs corrigés", _exercises_intro()),
        ("PR27 — Mini-examen noté sur 20 : mode d'emploi", _mini_exam()),
        ("PR27 — Fiche mémo et glossaire", _memo()),
        ("PR27 — Sources et compléments pédagogiques", _sources()),
    ]
