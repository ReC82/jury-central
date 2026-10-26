"""Cours PR06 « Diagnostic des pannes matérielles » — parcours AMPCR pratique écrite
(ticket #193).

Matière : intégralement celle du ticket #193 (A. méthodologie, B. chaîne de démarrage et
symptômes, C. sous-systèmes et tests, D. documentation et interprétation), découpée en blocs
titrés (le titre pilote le type de carte, `app.card_kind`). Les schémas viennent de
`app.v1.ampcr_pratique_pr06_figures` (SVG construits sur données vérifiées) ; les exercices
et le mini-examen de `app.v1.ampcr_pratique_pr06_bank` (même source que la banque des
sessions). Le contenu est piloté par le code : un nouveau titre de bloc force sa mise à jour
au prochain seed (voir `app.seed`).
"""

from html import escape

from app.v1.ampcr_pratique_format import ExerciseDocument
from app.v1.ampcr_pratique_plan import REQUIREMENTS_BY_ID
from app.v1.ampcr_pratique_pr06_bank import EXAM_ITEMS, EXAM_TOTAL_POINTS, PRACTICE_ITEMS, PR06Item
from app.v1.ampcr_pratique_pr06_figures import (
    ATX24_FIGURE,
    BOARD_FIGURE,
    BOOT_CHAIN_FIGURE,
    EPS8_FIGURE,
    FIRMWARE_SCREEN_FIGURE,
    MINIMAL_CONFIG_FIGURE,
    NO_BOOT_TREE_FIGURE,
    OTHER_CONNECTORS,
    TEMPERATURE_FIGURE,
    TEMPERATURE_LIMIT,
    TEMPERATURE_LOG,
)
from app.v1.ampcr_pratique_visuals import DIAGNOSTIC_METHOD_FIGURE, Figure, render_figure

PR06_TITLE = "Diagnostic des pannes matérielles"
PR06_SLUG = "ampcr-pratique-pr06"


def _fig(figure: Figure, *, wide: bool = False) -> str:
    html = str(render_figure(figure))
    if wide:
        html = html.replace('class="jc-tech-figure"', 'class="jc-tech-figure jc-tech-figure--wide"', 1)
    return f"\n\n{html}\n\n"


def _req(req_id: str) -> str:
    req = REQUIREMENTS_BY_ID[req_id]
    where = f"p. {req.page}" if req.page else req.kind
    return f"- **{req.id}** ({where}) — « {req.text} »"


def _table_html(document: ExerciseDocument) -> str:
    if document.kind == "console":  # ticket #194 : terminal / journal, ligne à ligne
        return f'<pre class="jc-pr-console" tabindex="0">{escape(document.content_text)}</pre>'
    if document.kind != "tableau":
        return f'<p class="jc-pr-doc-text">{escape(document.content_text)}</p>'
    header, *rows = document.table_rows()
    head = "".join(f'<th scope="col">{escape(cell)}</th>' for cell in header)
    body = "".join(
        "<tr>" + "".join(f"<td>{escape(cell)}</td>" for cell in row) + "</tr>" for row in rows
    )
    return (
        '<div class="table-responsive"><table class="table table-sm jc-pr-doc-table">'
        f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"
    )


def _document_html(document: ExerciseDocument) -> str:
    return (
        '<div class="jc-pr-doc">'
        f'<p class="jc-pr-doc-title">{escape(document.title)}</p>'
        f"{_table_html(document)}</div>"
    )


def _exercise_card(number: int, item: PR06Item, anchor_prefix: str = "pr06") -> str:
    reqs = ", ".join(item.requirement_ids)
    documents = "".join(_document_html(d) for d in item.documents)
    elements = ""
    if item.classification is not None:
        options = " · ".join(item.classification.categories)
        elements = (
            f'<p class="small mb-1"><strong>Catégories :</strong> {escape(options)}</p><ol type="a">'
            + "".join(f"<li>{escape(e)}</li>" for e in item.classification.elements)
            + "</ol>"
        )
    if item.ordering is not None:  # ticket #194 : procédure à remettre en ordre
        elements = (
            '<p class="small mb-1"><strong>Étapes à remettre en ordre :</strong></p><ul>'
            + "".join(f"<li>{escape(step)}</li>" for step in item.ordering.steps)
            + "</ul>"
        )
    instructions = "".join(f"<li>{escape(text)}</li>" for text in item.instructions)
    criteria = "".join(
        f"<tr><td>{escape(c.label)}</td><td>{c.points:g}</td><td>{escape(c.expected)}</td></tr>"
        for c in item.criteria
    )
    correction = "".join(f"<p>{escape(step)}</p>" for step in item.correction)
    return (
        f'<div class="jc-exercise-card" id="{anchor_prefix}-{item.key.lower()}">\n'
        f'<div class="jc-exercise-card-header"><span class="jc-exercise-number" aria-hidden="true">{number}</span>'
        f'<h4 class="jc-exercise-title">{escape(item.title)}</h4></div>\n'
        f'<p class="small text-muted mb-2">{escape(item.key)} · {escape(item.kind)} · exigences {escape(reqs)} · '
        f"{item.total_points:g} points</p>\n"
        f'<div class="jc-exercise-instructions"><p>{escape(item.context)}</p>{documents}{elements}'
        f"<ol>{instructions}</ol></div>\n"
        f'<details class="jc-exercise-correction"><summary>Voir le corrigé et le barème</summary>\n'
        f'<div class="jc-exercise-correction-body">{correction}'
        '<div class="table-responsive"><table class="table table-sm"><thead><tr><th scope="col">Critère</th>'
        '<th scope="col">Points</th><th scope="col">Attendu (toute formulation juste est acceptée)</th></tr></thead>'
        f"<tbody>{criteria}</tbody></table></div></div>\n</details>\n</div>"
    )


def _exercises_html() -> str:
    return "\n\n".join(_exercise_card(i, item) for i, item in enumerate(PRACTICE_ITEMS, start=1))


def _temperature_table() -> str:
    rows = "\n".join(
        f"| {m} | {t} °C | {f} GHz | {v} tr/min |" for m, t, f, v in TEMPERATURE_LOG
    )
    return (
        "| Minute de charge | Température CPU | Fréquence CPU | Ventilateur CPU |\n"
        "|---|---|---|---|\n" + rows
    )


def _connectors_table() -> str:
    rows = "\n".join(f"| {name} | {pins} | {power} | {use} |" for name, pins, power, use in OTHER_CONNECTORS)
    return "| Connecteur | Broches | Tensions / puissance | Usage |\n|---|---|---|---|\n" + rows


# =============================================================================================
# Sections du cours (titre du bloc, Markdown / HTML)
# =============================================================================================


def _objectives() -> str:
    return f"""## Ce que tu sauras faire, par écrit

L'épreuve pratique AMPCR se passe **uniquement par écrit** (consignes officielles 2026-2027/1,
p. 3) : on ne te demandera pas de dépanner un vrai PC, mais de **rédiger** comment tu le
dépannes. À la fin de ce cours, tu sais, sur papier et sans matériel :

1. **recueillir** les informations utiles sur une panne (symptômes, chronologie, données) ;
2. **formuler des hypothèses ordonnées**, de la plus simple et la moins risquée à la plus invasive ;
3. **choisir des tests non destructifs** et **interpréter leurs résultats**, y compris un test négatif ;
4. **proposer une intervention sûre** pour les personnes, le matériel et les données ;
5. **vérifier la réparation** et **rédiger un compte rendu** professionnel.

## Exigences officielles travaillées dans ce cours

{_req("AP-15")}
{_req("AP-17")}

Complément pédagogique (hors liste officielle des pp. 5-6, signalé comme tel) :

{_req("AP-C02")}

Ce cours mobilise aussi, **sous l'angle du diagnostic**, des notions enseignées ailleurs :
composants (AP-02), stockage (AP-03), alimentation (AP-04), périphériques et pilotes (AP-05),
carte mère (AP-07). Elles sont rappelées ici seulement quand le diagnostic en a besoin.

## Prérequis : la théorie déjà publiée

Relis au besoin les mini-cours théoriques (parcours « Théorie », séparé de ce parcours) :
[MC02 Carte mère](/uaa/ampcr-mc02), [MC03 CPU et RAM](/uaa/ampcr-mc03),
[MC04 Stockage](/uaa/ampcr-mc04), [MC05 Alimentation, refroidissement, ESD](/uaa/ampcr-mc05),
[MC07 BIOS, UEFI, POST](/uaa/ampcr-mc07), [MC12 Pilotes et périphériques](/uaa/ampcr-mc12),
[MC29 Dépannage matériel](/uaa/ampcr-mc29), [MC36 Rapport technique](/uaa/ampcr-mc36).

## Comment travailler ce cours

Lis la méthode (A) et la sécurité, puis la chaîne de démarrage (B), les sous-systèmes (C) et
la lecture des documents (D). Étudie les **quatre cas résolus**, fais les **12 exercices
corrigés** (ici ou dans « S'entraîner », correction après envoi), puis passe le **mini-examen
noté sur {EXAM_TOTAL_POINTS}** dans l'onglet « Examen blanc ».

> **Important —** les situations, captures et relevés de ce cours sont des **supports
> fictifs** construits pour s'entraîner. Ce ne sont pas des questions officielles ni des
> questions déjà posées par le Jury.
"""


def _method() -> str:
    return f"""## A1. Recueillir les informations avant de toucher

Un bon diagnostic commence au comptoir ou au téléphone. Note, **avec les mots du client** puis
en termes techniques :

| À recueillir | Exemple de question | Pourquoi |
|---|---|---|
| Symptômes exacts | « Que se passe-t-il quand vous appuyez sur le bouton ? » | Situe la panne sur la chaîne de démarrage. |
| Messages | « Un message, des bips ? Pouvez-vous le lire ou le photographier ? » | Un texte exact vaut mieux qu'un souvenir. |
| Chronologie | « Depuis quand ? » | Une panne récente a souvent une cause récente. |
| Modifications récentes | « Qu'est-ce qui a changé juste avant ? » (orage, déménagement, ajout de matériel, mise à jour, chute, liquide) | La cause est souvent là. |
| Fréquence | « Toujours, ou de temps en temps ? À quel moment ? » | Une panne intermittente demande de la reproduire et de lire les journaux. |
| Environnement | Poussière, chaleur, multiprise surchargée, onduleur | Oriente vers surchauffe ou alimentation. |
| Données et sauvegarde | « Y a-t-il des données importantes ? Une sauvegarde récente ? » | Fixe la priorité et les précautions. |
| Autorisations | Accord pour le diagnostic, pour un coût, pour toute action sur les données | Rien d'irréversible sans accord écrit. |

## A2. Observation, hypothèse, test, résultat, conclusion

Une réponse de technicien **sépare** clairement ces cinq notions :

| Notion | Définition | Exemple |
|---|---|---|
| **Observation** | Ce que l'on constate, sans interprétation | « Aucun voyant ne s'allume, prise branchée. » |
| **Hypothèse** | Une cause possible, pas encore vérifiée | « Le bloc d'alimentation est peut-être défectueux. » |
| **Test** | Une action qui vérifie une hypothèse | « Je branche un bloc connu fonctionnel. » |
| **Résultat** | Ce que le test a donné | « Le PC démarre avec ce bloc. » |
| **Conclusion** | La cause retenue, **justifiée par les résultats** | « Le bloc d'origine est défectueux. » |

**Du plus simple et moins risqué au plus invasif.** On classe les tests ainsi :

1. observer sans rien toucher (voyants, bruits, odeur, messages) ;
2. vérifier l'extérieur (prise, câbles, interrupteur, écran, entrée sélectionnée) ;
3. lire ce que la machine dit déjà (firmware, journaux, outils de diagnostic non destructifs) ;
4. ouvrir, PC débranché, et contrôler connecteurs et composants (réinsertion) ;
5. échanger un composant par un composant **connu fonctionnel** (test croisé) ;
6. remplacer définitivement ;
7. en dernier, et **seulement avec l'accord du client**, toute action qui touche aux données.

> **Erreur fréquente —** écrire « la carte mère est morte » après une seule observation. Une
> conclusion sans test n'est qu'une hypothèse.

## A3. Reproduire, isoler, croiser

- **Reproduire sans aggraver** : déclencher le symptôme dans les mêmes conditions (charge,
  durée), en surveillant (températures, journaux) et en s'arrêtant au moindre danger (odeur
  de brûlé, fumée, bruit mécanique d'un disque contenant des données).
- **Isoler les variables** : **un seul changement à la fois**, puis on teste. Changer trois
  pièces d'un coup peut réparer, mais on ne sait plus laquelle était en panne.
- **Configuration minimale** : ne garder que l'indispensable pour atteindre le POST et une
  image, puis rajouter les éléments un par un.
- **Test croisé** : mettre le composant suspect dans un PC qui fonctionne, ou un composant
  connu fonctionnel dans le PC en panne. Si la panne suit le composant, il est en cause.
- **Interpréter un test négatif** : un test « sans erreur » élimine **seulement ce qu'il
  teste, dans ses conditions**. Un testeur d'alimentation à vide ne teste pas le bloc sous
  forte charge ; un test mémoire court peut manquer une erreur rare ; une panne intermittente
  peut ne pas se montrer pendant le test.

{_fig(MINIMAL_CONFIG_FIGURE)}

## A5. Tracer l'intervention

Note **avant, pendant et après** : état initial (aspect, numéro de série, accessoires),
chaque action et son résultat, tests avant et après la réparation, **accord écrit** avant toute
intervention destructive ou coûteuse. Le compte rendu final reprend ces notes (voir D).

{_fig(DIAGNOSTIC_METHOD_FIGURE)}

**À retenir —** observation, hypothèse, test, résultat, conclusion ; un changement à la fois ;
du plus simple au plus invasif ; tout est noté.
"""


def _safety() -> str:
    return """## A4. Avant toute manipulation

**Pour les personnes et le matériel**

1. **Couper** : arrêter proprement le système, mettre l'interrupteur du bloc sur 0 et
   **retirer le câble secteur**. Tant que le PC est branché, le bloc fournit la tension de veille
   (+5 VSB) à la carte mère, même PC « éteint ».
2. **Décharge résiduelle prudente** : câble retiré, appuyer quelques secondes sur le bouton
   d'allumage pour vider la charge restante des circuits de la carte. Cela ne concerne **pas**
   l'intérieur du bloc d'alimentation.
3. **ESD (électricité statique)** : bracelet antistatique relié à la masse (ou tapis
   antistatique), composants tenus par les bords, jamais par les contacts ; pose sur un sachet
   antistatique ; pas de travail sur la moquette.
4. **Ne jamais ouvrir un bloc d'alimentation** : ses condensateurs peuvent rester chargés à une
   tension dangereuse longtemps après le débranchement. Un bloc suspect se teste (testeur,
   bloc de remplacement) et se **remplace**.
5. **Aucune manipulation sous tension** : on ne branche ni ne débranche un composant interne PC
   allumé. Les mesures de tension sous tension ne se font que si l'on est **habilité et
   outillé**, en suivant la procédure de l'atelier.

**Équipement endommagé**

- **Batterie gonflée** (coque bombée, pavé tactile soulevé) : ne plus charger, ne plus utiliser,
  ne pas appuyer, percer ni chauffer ; retrait seulement selon la procédure du fabricant et
  sans forcer, sinon service qualifié ; batterie isolée dans un contenant non inflammable, puis
  filière de collecte des batteries.
- **Liquide renversé, odeur de brûlé, trace de fumée, composant fondu** : ne **pas** remettre
  sous tension « pour voir » ; débrancher, retirer la batterie d'un portable si c'est possible
  sans démontage risqué, et faire évaluer.

**Pour les données**

- Avant toute intervention qui peut toucher au disque : **sauvegarde** vérifiée ou **accord
  écrit** du client.
- Disque suspect (bruits, erreurs) : la récupération des données passe **avant** la réparation.

> **Erreur fréquente —** penser qu'un PC éteint n'est plus alimenté. Tant que la prise est
> branchée, la veille +5 VSB est présente sur la carte mère.
"""


def _boot_chain() -> str:
    return f"""## B6. La chaîne de démarrage

Un PC démarre **étape par étape** ; chaque étape suppose que la précédente a réussi. Le
diagnostic consiste à trouver **la dernière étape réussie**.

{_fig(BOOT_CHAIN_FIGURE)}

## Six situations à ne pas confondre

| Situation | Ce que l'on observe | Où chercher |
|---|---|---|
| **Absence de courant** | Rien : aucun voyant, aucun ventilateur, aucun bruit | Secteur, câble, interrupteur, bloc, bouton |
| **Alimentation partielle** | Un voyant ou un ventilateur réagit brièvement, puis plus rien ; ou arrêt après 1-2 secondes | Bloc, connecteurs ATX 24 et EPS, court-circuit |
| **Absence de POST** | Ventilateurs, mais pas d'image ; LED de diagnostic ou bips qui signalent un arrêt | Processeur, mémoire, carte graphique, carte mère |
| **Absence d'image** | Le PC semble démarrer (activité du disque, son de démarrage du système), mais l'écran reste noir | Écran, entrée, câble, mauvaise sortie vidéo |
| **Échec de démarrage** | Le firmware s'affiche, puis un message : aucun périphérique, système introuvable | Stockage, ordre et mode de démarrage, chargeur |
| **Plantage du système** | Le logo du système apparaît, puis écran bleu, gel ou redémarrage | Pilotes, mémoire, température, disque, alimentation sous charge |

**Absence d'image ≠ absence de POST.** « Aucun signal » sur l'écran dit seulement que l'écran
ne reçoit rien. Pour trancher : tester l'écran avec une autre source, vérifier la sortie
utilisée, lire les indicateurs du POST (LED, bips, code) avec le manuel, et chercher des signes
que le système démarre quand même.

{_fig(NO_BOOT_TREE_FIGURE, wide=True)}
"""


def _boot_failures() -> str:
    return """## B7. PC totalement inerte

| Hypothèse (de la plus simple à la plus invasive) | Test | Interprétation |
|---|---|---|
| Prise, multiprise, câble | Autre appareil sur la prise ; autre câble secteur | Si le PC démarre : cause trouvée. |
| Interrupteur du bloc sur 0 | Le mettre sur I | — |
| Bouton de façade ou son câble | Contrôler son raccordement au connecteur de façade (manuel) ; bouton intégré à la carte s'il existe | Si le PC démarre par la carte : bouton ou câble en cause. |
| Connecteurs ATX 24 / EPS mal enfichés | PC débranché : réenfoncer jusqu'au clic | — |
| Bloc d'alimentation | Testeur d'alimentation ; bloc connu fonctionnel | Testeur sans tension ou démarrage avec l'autre bloc : bloc en cause. |
| Court-circuit (vis sous la carte, carte d'extension) | Configuration minimale | Démarre en minimal : réintroduire un élément à la fois. |
| Carte mère | Seulement après tout le reste | — |

**Pas de diagnostic catégorique sans mesure ni test croisé** : « c'est l'alimentation » reste
une hypothèse tant qu'un testeur ou un bloc de remplacement ne l'a pas confirmé.

## B8. Ventilateurs en marche, écran noir

1. **Écran** : allumé, bonne entrée sélectionnée, câble testé, écran essayé avec une autre source.
2. **Bonne sortie** : avec une carte graphique dédiée, l'écran se branche **sur elle**. Certains
   processeurs n'ont pas de circuit graphique intégré (par exemple les Intel Core à suffixe F) :
   les sorties vidéo de la carte mère ne peuvent alors rien afficher.
3. **Indicateurs du POST** : LED de diagnostic, bips, afficheur de code — lus **dans le manuel
   de la carte**.
4. **Mémoire** : réinsertion, puis **une barrette** dans le slot recommandé par le manuel.
   Après un changement de mémoire, le premier démarrage peut être long (entraînement de la
   mémoire, surtout en DDR5) : attendre quelques minutes avant de conclure.
5. **Carte graphique** : connecteurs PCIe d'alimentation branchés, essai sur l'iGPU s'il existe,
   ou autre carte connue fonctionnelle.
6. **Alimentation, processeur** : bloc connu fonctionnel ; processeur et ses broches en dernier.
7. **Configuration minimale**, puis réintroduction pièce par pièce.

## B9. Bips, LED de diagnostic et codes POST

Ils sont **précieux mais propres à chaque fabricant** (de la carte et du firmware). Il n'existe
**aucune correspondance universelle** : « trois bips » n'a pas le même sens sur deux cartes
différentes.

- Relever le **modèle exact** de la carte et le motif précis (bips longs/courts, LED restée
  allumée, code affiché).
- Chercher ce motif **dans le manuel ou sur le site du fabricant**.
- **Confirmer par un test** avant de commander une pièce.

## B10. « No boot device », « Operating System not found », disque absent

Le firmware s'affiche : l'alimentation, le processeur, la mémoire et l'affichage fonctionnent.
On cherche dans le stockage et le démarrage, **sans formater** :

| Hypothèse | Vérification |
|---|---|
| Câble SATA de données ou d'alimentation débranché | Les deux extrémités ; autre câble, autre port |
| Disque non détecté | Liste des périphériques dans le firmware |
| SSD M.2 incompatible avec l'emplacement | M.2 **SATA** ou **PCIe (NVMe)** : le manuel dit ce que chaque emplacement accepte |
| Port désactivé par un autre périphérique | Certaines cartes désactivent un port SATA quand un emplacement M.2 est utilisé (manuel) |
| Ordre de démarrage | Le bon disque (ou « Windows Boot Manager ») en premier |
| Mode de démarrage | Installation UEFI sur disque **GPT** avec partition système EFI ; installation « héritée » sur disque **MBR** : ne démarre qu'avec le CSM activé |
| Disque défaillant | Bruits, SMART, détection intermittente : **données d'abord** |

> **Erreur fréquente —** formater ou réinstaller dès qu'apparaît « No boot device ». Le
> disque contient peut-être toutes les données du client et n'est souvent même pas en panne.

## B11. Redémarrages, gels, écrans bleus, extinction sous charge

| Piste | Indice | Test qui apporte une preuve |
|---|---|---|
| Mémoire | Écrans bleus variés (par exemple MEMORY_MANAGEMENT) | Test mémoire de plusieurs passes, une barrette à la fois |
| Température | Arrêt sous charge, ventilateurs au maximum, fréquence qui chute | Relevé des températures sous charge, après nettoyage |
| Alimentation | Arrêt brutal en jeu ou en calcul, bloc sous-dimensionné | Même charge avec un bloc adapté connu fonctionnel |
| Pilotes | Écran bleu après une mise à jour, nom d'un pilote cité | Retour au pilote précédent, démarrage minimal |
| Stockage | Gels pendant les accès disque, erreurs dans le journal | SMART, test du fabricant, après sauvegarde |

**Indice ou preuve ?** L'événement Windows **Kernel-Power 41** dit seulement que le système ne
s'est pas arrêté proprement : c'est un **indice**, pas une cause. Un code d'arrêt d'écran bleu
oriente, mais un pilote peut aussi le provoquer. Une **preuve** est un résultat reproductible
qui suit le composant : erreurs mémoire qui suivent une barrette, panne qui disparaît avec un
bloc de remplacement.
"""


def _connectors() -> str:
    return f"""## Les connecteurs à reconnaître dans un relevé

Un compte rendu doit nommer correctement les connecteurs : « le câble CPU 8 broches était mal
enfiché » est une observation utile ; « un câble était mal mis » ne l'est pas.

{_fig(ATX24_FIGURE)}

{_fig(EPS8_FIGURE)}

{_connectors_table()}

- **ATX 20+4** : le connecteur principal est souvent sécable (20 + 4 broches) pour les anciennes
  cartes à 20 broches ; sur une carte 24 broches, les deux parties doivent être branchées.
- **EPS 4+4** : le connecteur du processeur est souvent sécable ; une carte qui prévoit 8 broches
  doit les recevoir. Un EPS absent empêche le démarrage.
- **EPS et PCIe 8 broches** se ressemblent mais ne sont **pas interchangeables** : le
  détrompage diffère, ne jamais forcer.
- **Carte graphique** : l'emplacement PCIe x16 fournit au plus 75 W ; au-delà, la carte a besoin
  de ses connecteurs PCIe 6 ou 8 broches. Les cartes récentes peuvent utiliser un connecteur
  16 broches (12VHPWR / 12V-2x6), à enfoncer complètement.
- **Mesures** : un **testeur d'alimentation** se branche sur les connecteurs du bloc et affiche
  les tensions ; les mesures au multimètre sous tension ne se font que si l'on est habilité et
  outillé.
"""


def _subsystems_core() -> str:
    return f"""## C12. Mémoire vive (RAM)

- **Symptômes** : pas de POST (LED DRAM, bips), écrans bleus variés, plantages aléatoires,
  capacité affichée inférieure à celle installée.
- **Barrette ou slot ?** Tester **une barrette à la fois** dans le même slot, puis mettre une
  barrette saine dans le slot suspect : si l'erreur suit la barrette, c'est elle ; si elle reste
  sur le slot, c'est le slot.
- **Insertion** : encoche alignée sur le détrompeur, clips fermés des deux côtés, sans forcer.
- **Compatibilité** : génération (DDR3, DDR4, DDR5 : encoches différentes, non interchangeables),
  format (DIMM pour PC de bureau, SO-DIMM pour portable), capacité maximale, fréquences,
  **liste de compatibilité** du fabricant. Mélanger des barrettes différentes peut empêcher le
  démarrage même si chacune fonctionne seule.
- **ECC ou non-ECC** : la mémoire ECC détecte et corrige certaines erreurs ; utile pour un
  serveur ou une station de travail, mais elle exige un processeur **et** une carte qui la
  prennent en charge. La plupart des PC grand public n'acceptent que du non-ECC.
- **Test** : logiciel de test mémoire hors système (sur clé USB) ou Diagnostic de mémoire
  Windows, plusieurs passes ; réglages mémoire par défaut pendant le test.

## C13. Processeur et refroidissement

- **Symptômes** : extinction sous charge, ventilateur au maximum, lenteur sous charge (la
  fréquence baisse), LED CPU.
- **Throttling** : quand la température approche de la limite fixée par le fabricant, le
  processeur **réduit sa fréquence** pour se protéger ; au-delà, un **arrêt de protection**
  éteint le PC.
- **À contrôler** : ventilateur qui tourne et accélère avec la charge, radiateur propre et bien
  fixé, **pâte thermique** sèche ou absente, sens et état des ventilateurs du boîtier,
  poussière.
- **Compatibilité** : même socket ne veut pas dire compatibilité assurée — un processeur plus
  récent peut exiger une **mise à jour du firmware** (liste des processeurs pris en charge).

## C14. Bloc d'alimentation

- **Puissance et compatibilité** : puissance suffisante pour la configuration (la carte
  graphique indique souvent une alimentation recommandée), connecteurs nécessaires présents
  (EPS, PCIe), format adapté au boîtier.
- **Symptômes** : PC inerte, démarrage puis arrêt immédiat, **extinction sous charge**,
  redémarrages en jeu, odeur de brûlé, bruit anormal.
- **Tests** : testeur d'alimentation, puis **bloc connu fonctionnel** sous la même charge.
- **Jamais** : ouvrir le bloc, utiliser des adaptateurs de fortune pour alimenter une carte
  graphique puissante, mesurer sous tension sans habilitation ni outillage.

## C15. Carte mère

- **Connecteurs** : ATX 24, EPS, façade, ventilateurs, SATA, M.2 — bien enfichés et non abîmés.
- **Inspection visuelle**, PC débranché : condensateurs **bombés ou qui fuient**, traces de
  brûlure, broches tordues du socket, traces de **liquide** ou d'oxydation.
- **VRM** (étage d'alimentation du processeur, autour du socket) : il transforme le +12 V en
  tension du processeur ; trop chaud, il provoque baisse de performance ou instabilité ; ses
  radiateurs doivent être ventilés.
- **Codes de diagnostic** : LED, afficheur de code, bips — toujours avec le manuel.

{_fig(BOARD_FIGURE)}
"""


def _subsystems_more() -> str:
    return """## C16. Carte graphique et affichage

| Élément | Vérification |
|---|---|
| Écran | Allumé, entrée sélectionnée, essayé avec une autre source |
| Câble | Autre câble ; HDMI, DisplayPort ou DVI bien enfoncé |
| Sortie utilisée | Carte graphique dédiée si présente ; sortie de la carte mère seulement s'il y a un iGPU |
| Alimentation de la carte graphique | Connecteurs PCIe 6/8 broches (ou 16 broches) tous branchés |
| Test croisé | Autre carte connue fonctionnelle, ou iGPU si disponible |

## C17. Stockage

- **HDD** (disque mécanique) : bruits (clics, grattements) = alerte ; **arrêter** de l'utiliser
  si les données sont précieuses. **SSD** : pas de bruit, panne souvent brutale.
- **SMART** : indicateurs de santé du disque (secteurs réalloués, en attente, non corrigibles,
  usure d'un SSD). C'est un **indice**, jamais une garantie : un disque « bon » peut lâcher, et
  une valeur isolée doit être recoupée.
- **Détection** : le firmware voit-il le disque ? Le système le voit-il (gestion des disques) ?
  Câbles, ports, type d'emplacement M.2 (SATA ou NVMe).
- **Priorité aux données** : sauvegarde ou copie **avant** toute réparation, défragmentation ou
  formatage. Un disque qui clique et contient des données uniques relève d'un laboratoire de
  récupération ; on ne l'ouvre jamais.

## C18. Périphériques : panne, connexion ou logiciel ?

| Constat | Conclusion |
|---|---|
| Le périphérique fonctionne sur un autre PC | Le périphérique (et son câble) est bon |
| Un autre périphérique fonctionne sur les mêmes ports | Les ports (la connexion) sont bons |
| Le périphérique ne fonctionne que sur certains ports | Connexion : port abîmé, câble de façade, hub |
| Le système le voit mais « inconnu » ou avec un triangle jaune | Logiciel : pilote à installer ou réinstaller |

Le **Gestionnaire de périphériques** (Windows) montre l'état de chaque périphérique ; on
installe le pilote du fabricant correspondant au modèle et au système.

## C19. Compatibilité : la liste à vérifier

| Point | Ce qu'il faut vérifier |
|---|---|
| Socket | Processeur et carte de même socket **et** processeur dans la liste de la carte (version du firmware) |
| Mémoire | Génération DDR, format DIMM/SO-DIMM, capacité, fréquence, ECC |
| Alimentation | Puissance, connecteurs EPS et PCIe disponibles |
| PCIe | Emplacement adapté à la carte, place dans le boîtier |
| SATA / M.2 | Interface acceptée par chaque emplacement, ports partagés |
| Facteur de forme | Carte mère (ATX, micro-ATX, mini-ITX), bloc, longueur de la carte graphique, hauteur du refroidisseur |
| Firmware BIOS/UEFI | Version nécessaire, mode de démarrage (UEFI, CSM) |

**Source de vérité : la documentation du fabricant** (manuel, listes de compatibilité), jamais
un forum ni une supposition.
"""


def _documents_and_decisions() -> str:
    return """## D20. Lire un document technique

À l'examen, tu reçois des **documents** et tu dois en tirer des faits. Pour chacun :
**que dit-il exactement ? qu'est-ce qu'il prouve ? qu'est-ce qu'il ne dit pas ?**

| Document | Ce qu'on y cherche | Piège |
|---|---|---|
| Capture du firmware (BIOS/UEFI) | Composants détectés, ordre et mode de démarrage | Un disque absent n'est pas forcément en panne (câble, mode) |
| Photo de composant | Condensateurs bombés, broches tordues, connecteur mal enfiché, poussière, liquide | Ne pas déduire une valeur ou un brochage d'une photo |
| Voyants, LED, codes POST | Étape où le démarrage s'arrête | Signification propre au fabricant |
| Message d'erreur | Texte exact, moment où il apparaît | Ne pas « traduire » approximativement |
| Journal système | Événements, heures, codes d'arrêt | Un événement est un indice, pas forcément la cause |
| Inventaire | Modèles, références, branchements | Vérifier la compatibilité de chaque élément |
| Tableau de températures | Évolution, comparaison au maximum du fabricant | Une seule mesure ne suffit pas |
| Schéma de câblage | Connecteurs attendus et réels | Lire l'orientation indiquée |
| Devis de remplacement | Coût, délai, compatibilité | Comparer à la valeur du PC et des données |

## D21. Du constat à la prévention

| Étape | Question | Exemple (cas 4) |
|---|---|---|
| **Constat** | Qu'a-t-on observé ? | Le PC s'éteint après 10 minutes de charge. |
| **Cause probable** | Quelle hypothèse l'explique le mieux ? | Refroidissement insuffisant. |
| **Test de confirmation** | Quel test le prouve ? | Températures relevées sous charge. |
| **Action corrective** | Que fait-on ? | Nettoyage, pâte thermique neuve, réglage du ventilateur. |
| **Test final** | Comment vérifie-t-on ? | 30 minutes de charge sans arrêt, températures normales. |
| **Prévention** | Comment éviter le retour ? | Entretien régulier, emplacement aéré. |

## D22. Escalader, préserver, remplacer

- **Escalader** (au responsable, au fabricant, à un spécialiste) quand l'intervention dépasse
  ta compétence, ton habilitation ou ton outillage : mesure sous tension, réparation de carte,
  récupération de données sur disque défaillant, matériel sous garantie (ne pas l'ouvrir sans
  accord), batterie endommagée.
- **Préserver les données** dès qu'un disque est suspect ou qu'une action peut les toucher :
  sauvegarde ou copie d'abord, accord écrit ensuite.
- **Remplacer plutôt que réparer** quand la réparation coûte plus que le composant ou le PC,
  quand la pièce n'existe plus, quand la fiabilité n'est plus assurée (bloc d'alimentation,
  disque qui a déjà montré des erreurs), ou quand le matériel ne répond plus au besoin.

## Méthode examen : rédiger ta réponse

1. **Reformule la situation** en une phrase (le symptôme exact).
2. **Liste les hypothèses** de la plus probable/simple à la moins probable/invasive.
3. Pour chaque test : **ce que tu fais, ce que tu attends, ce que tu conclus**.
4. **Conclus** en citant les résultats qui le prouvent.
5. Décris l'**intervention** avec ses précautions (sécurité, données, accord).
6. Donne le **test final** et un conseil de **prévention**.
7. Si on te le demande, rédige le **compte rendu** au client : simple, sans jargon inutile.

**Modèle de compte rendu (5 lignes)** — *Constat* : … *Tests réalisés* : … *Cause* : …
*Intervention* : … *Résultat et conseil* : …
"""


def _cases() -> str:
    temperature_table = _temperature_table()
    return f"""Chaque cas suit la même démarche : situation, observations, hypothèses ordonnées, tests
et résultats, conclusion, intervention, vérification et compte rendu. Les supports sont
fictifs.

<h3 class="jc-example-title">Cas 1 — PC totalement inerte</h3>

**Situation.** Un comptable signale que son PC ne s'allume plus depuis ce matin. La veille,
le bâtiment a subi une coupure de courant. L'écran, branché sur la même multiprise, s'allume.

**Observations.** Aucun voyant, aucun ventilateur à l'appui sur le bouton. Le câble
d'alimentation est bien enfoncé. Le client n'a aucune donnée non sauvegardée (sauvegarde en
ligne quotidienne).

**Hypothèses ordonnées.** 1) câble secteur ou interrupteur du bloc ; 2) bloc d'alimentation
(coupure brutale, surtension au retour du courant) ; 3) bouton de façade ; 4) court-circuit ;
5) carte mère.

**Tests et résultats.**

1. Interrupteur du bloc : sur I. Câble secteur remplacé par celui de l'écran : aucun changement.
2. PC débranché, ouvert, bracelet ESD relié : connecteurs ATX 24 et EPS bien enfichés. PC
   rebranché, capot ouvert sans rien toucher : le voyant de veille de la carte reste éteint.
3. Testeur d'alimentation sur le bloc d'origine (PC débranché pour le raccordement) : aucune
   tension affichée.
4. Bloc de l'atelier connu fonctionnel, branché temporairement : le PC démarre, logo affiché.

**Conclusion.** Bloc d'alimentation défectueux, prouvé par les tests 3 et 4 (le secteur et le
câble ont été mis hors de cause par le test 1).

**Intervention.** PC débranché, ESD : remplacement par un bloc de puissance et de connecteurs
adaptés. L'ancien bloc n'est pas ouvert ; il part au recyclage.

**Vérification.** Démarrage, tensions correctes dans le firmware, une heure d'utilisation
normale sans arrêt.

**Compte rendu.** « PC inerte. Prise et câble testés : en ordre. Le bloc d'alimentation ne
délivrait plus de tension (testeur) et le PC démarre avec un bloc de test. Bloc remplacé. PC
fonctionnel. Conseil : multiprise avec parafoudre ou onduleur. »

<h3 class="jc-example-title">Cas 2 — Ventilateurs en marche, aucun affichage</h3>

**Situation.** Une étudiante a nettoyé l'intérieur de son PC. Depuis, les ventilateurs
tournent mais l'écran reste noir (« Aucun signal »). Le PC a une carte graphique dédiée.

**Observations.** L'écran fonctionne avec un autre PC. Le câble est branché sur la carte
graphique. La LED **DRAM** de la carte mère reste allumée (le manuel indique : « mémoire non
détectée ou défaillante »).

**Hypothèses ordonnées.** 1) barrette mal insérée après le nettoyage ; 2) barrette ou slot
défectueux ; 3) autre composant (carte graphique, carte mère).

**Tests et résultats.**

1. PC débranché, ESD : les deux barrettes sont retirées puis réinsérées ; un clip n'était pas
   fermé. Résultat : la LED DRAM reste allumée.
2. Une seule barrette (n° 1) dans le slot recommandé par le manuel : le PC démarre, image
   présente.
3. Barrette n° 2 seule dans le même slot : LED DRAM allumée, pas d'image.
4. Barrette n° 1 dans le second slot : démarrage normal.

**Conclusion.** Barrette n° 2 défectueuse (la panne la suit ; les slots fonctionnent).
L'absence d'image venait d'un **arrêt au POST**, pas de l'affichage.

**Intervention.** Remplacement de la barrette n° 2 par une barrette compatible (même
génération et même capacité, idéalement identique), avec l'accord de la cliente sur le coût.

**Vérification.** Démarrage, capacité totale reconnue, test mémoire de plusieurs passes sans
erreur.

**Compte rendu.** « Pas d'image après nettoyage. L'écran et le câble fonctionnaient ; la carte
signalait un défaut mémoire. Tests barrette par barrette : la barrette n° 2 est défectueuse.
Barrette remplacée, test mémoire sans erreur. »

<h3 class="jc-example-title">Cas 3 — Stockage non détecté</h3>

**Situation.** Un client a remplacé lui-même le boîtier de son PC. Au démarrage, l'écran
ci-dessous s'affiche. Son disque SSD SATA contient ses photos de famille, sans sauvegarde.

{_fig(FIRMWARE_SCREEN_FIGURE)}

**Observations (lecture du document).** Le processeur et la mémoire sont détectés, l'image
s'affiche : alimentation, POST et affichage fonctionnent. Le lecteur DVD est vu sur SATA3_1,
mais **aucun disque** n'est détecté sur SATA3_0 ni sur M.2_1. Le message final indique qu'aucun
périphérique de démarrage n'a été trouvé.

**Hypothèses ordonnées.** 1) câble SATA de données ou d'alimentation du SSD débranché pendant
le changement de boîtier ; 2) câble ou port SATA défectueux ; 3) SSD défaillant.

**Tests et résultats.**

1. PC débranché, ESD : le câble d'alimentation SATA du SSD n'est pas branché (il est resté
   replié derrière la carte). On le branche.
2. Démarrage : le firmware affiche le SSD sur SATA3_0 ; « Windows Boot Manager » réapparaît
   dans l'ordre de démarrage.

**Conclusion.** SSD simplement non alimenté depuis le remontage ; il n'est pas en panne.

**Intervention.** Câble d'alimentation branché et rangé, ordre de démarrage vérifié (Windows
Boot Manager en premier). **Aucun formatage, aucune réinstallation** : les photos sont intactes.

**Vérification.** Démarrage complet du système, photos accessibles. Conseil : mettre en place
une sauvegarde des photos.

<h3 class="jc-example-title">Cas 4 — Extinction après 10 minutes de charge</h3>

**Situation.** Un PC de bureau utilisé pour du montage vidéo s'éteint sans message après une
dizaine de minutes d'exportation. En bureautique, aucun problème. Dernier entretien : jamais,
le PC a 5 ans.

**Relevé (document).** Test de charge du processeur, températures lues avec un logiciel de
surveillance. Fiche du processeur : température maximale **{TEMPERATURE_LIMIT} °C**.

{temperature_table}

{_fig(TEMPERATURE_FIGURE)}

**Observations.** La température monte jusqu'au maximum du fabricant ; la **fréquence chute**
à partir de la minute 6 (le processeur se protège : throttling), puis le PC s'éteint. Le
ventilateur du processeur **n'accélère pas** (environ 650 tr/min tout le temps). À l'ouverture
(PC débranché, ESD) : radiateur bouché par la poussière.

**Hypothèses ordonnées.** 1) refroidissement insuffisant (poussière, ventilateur qui
n'accélère pas, pâte thermique sèche) ; 2) bloc d'alimentation défaillant sous charge ;
3) autre cause (carte mère, logiciel).

**Ce que le relevé prouve, et ce qu'il ne prouve pas.** La concordance température maximale,
baisse de fréquence puis extinction est un **indice fort** d'un arrêt de protection thermique.
Elle ne prouve pas à elle seule que l'alimentation est hors de cause : c'est le **test final**,
après correction, qui confirmera.

**Intervention.** Nettoyage du radiateur et des ventilateurs (air sec, ventilateurs bloqués
pendant le soufflage), remplacement de la pâte thermique, contrôle du raccordement du
ventilateur (connecteur CPU_FAN) et de son réglage de vitesse dans le firmware.

**Vérification (test final).** Même test de charge pendant 30 minutes : la température se
stabilise nettement sous le maximum, le ventilateur accélère, la fréquence reste stable, plus
d'extinction. L'hypothèse thermique est confirmée ; l'alimentation n'est plus suspectée.

**Prévention.** Entretien annuel (poussière), PC posé dans un endroit aéré, pas contre un mur
ou dans un meuble fermé.

**Compte rendu.** « Extinctions pendant les exports. Relevé : le processeur atteignait sa
température maximale, puis se protégeait. Cause : radiateur encrassé et ventilateur qui
n'accélérait pas. Nettoyage, pâte thermique neuve, réglage du ventilateur. Test de 30 minutes
sans arrêt. Conseil : entretien annuel. »
"""


def _pitfalls() -> str:
    return """> **Changer plusieurs pièces à la fois.** Le PC refonctionne peut-être, mais on ne sait
> pas ce qui était en panne et on facture des pièces inutiles.

> **Conclure sans test.** « C'est la carte mère » après une observation n'est qu'une hypothèse.

> **Confondre absence d'image et absence de POST.** Vérifier l'écran, l'entrée, le câble et
> la sortie utilisée avant de suspecter un composant interne.

> **Croire à un code universel de bips.** Les bips, LED et codes dépendent du fabricant : le
> manuel de la carte fait foi.

> **Formater dès qu'un disque n'est pas trouvé.** Câbles, type d'emplacement M.2, ordre et mode
> de démarrage d'abord ; les données avant tout.

> **Lancer une réparation de disque sur un disque qui clique.** Elle peut détruire les
> dernières données récupérables.

> **Ouvrir un bloc d'alimentation ou manipuler sous tension.** Danger électrique : on teste
> et on remplace le bloc, on travaille PC débranché.

> **Oublier l'ESD.** Un composant abîmé par l'électricité statique peut tomber en panne plus
> tard, de façon intermittente.

> **Prendre un indice pour une preuve.** Kernel-Power 41 ou une valeur SMART isolée orientent
> le diagnostic ; un test reproductible le prouve.

> **Oublier le test final et le compte rendu.** Une intervention non vérifiée et non tracée
> n'est pas terminée.
"""


def _exercises_intro() -> str:
    return f"""Douze exercices corrigés : huit scénarios professionnels écrits et quatre analyses de
documents (relevés, manuel, journal, rapport SMART). Rédige ta réponse sur papier **avant**
d'ouvrir le corrigé. Ces mêmes exercices sont proposés dans
[S'entraîner](/uaa/{PR06_SLUG}/practice), avec correction après envoi.

{_exercises_html()}
"""


def _mini_exam() -> str:
    rows = "\n".join(
        f"| {i} | {item.title} | {item.kind} | {item.total_points:g} |"
        for i, item in enumerate(EXAM_ITEMS, start=1)
    )
    return f"""Le mini-examen se passe dans l'onglet [Examen blanc](/uaa/{PR06_SLUG}/exam) : **10 questions à réponse
libre**, chacune notée sur **2 points**, soit une note sur **{EXAM_TOTAL_POINTS}**. Les
questions ne figurent pas dans ce cours.

| N° | Thème | Type | Points |
|---|---|---|---|
{rows}

**Déroulement.** Toutes les informations nécessaires sont dans chaque question et ses
documents. **Aucune correction n'est visible pendant la passation** ; tes réponses sont
enregistrées au fur et à mesure. Après l'envoi, chaque réponse est corrigée selon le barème
détaillé de la question (critères et points), puis tu vois ta note sur {EXAM_TOTAL_POINTS}, le
corrigé et le barème.

**Correction.** Une réponse techniquement juste est acceptée même si elle est formulée
autrement : il n'y a pas de mot-clé obligatoire. Les réponses rédigées reçoivent une
**proposition de correction automatique** (assistée par IA) appuyée sur le barème : c'est un
repère d'entraînement, pas une note officielle ; en cas de doute, compare ta réponse au corrigé.
Une action dangereuse ou destructive pour les données, proposée sans précaution, fait perdre
des points.
"""


def _memo() -> str:
    return """- **Recueillir** : symptôme exact, messages, chronologie, changements, fréquence,
  environnement, données, sauvegarde, accord.
- **Séparer** observation, hypothèse, test, résultat, conclusion ; **un changement à la fois** ;
  du plus simple au plus invasif.
- **Sécurité** : PC débranché (la veille +5 VSB est présente tant que la prise est branchée),
  décharge résiduelle, ESD, jamais ouvrir un bloc ni une batterie gonflée, rien sous tension.
- **Chaîne de démarrage** : secteur → bloc → carte mère → POST → firmware → stockage → chargeur
  → système. Trouver la dernière étape réussie.
- **Absence d'image ≠ absence de POST** : écran, entrée, câble, bonne sortie (pas d'iGPU sur
  un processeur à suffixe F), puis LED/bips avec le manuel.
- **Bips, LED, codes** : propres au fabricant, jamais universels.
- **No boot device** : câbles, détection, type M.2 (SATA ou NVMe), ordre et mode (UEFI/GPT ou
  CSM/MBR). **Pas de formatage réflexe.**
- **Redémarrages et écrans bleus** : mémoire (test, une barrette à la fois), température,
  alimentation sous charge, pilotes, stockage. Kernel-Power 41 = indice.
- **Disque qui clique** : données d'abord, aucune réparation ni défragmentation, laboratoire si
  besoin.
- **Compatibilité** : socket + firmware, DDR et format, alimentation et connecteurs, PCIe,
  SATA/M.2, facteur de forme ; la documentation du fabricant fait foi.
- **Finir** : test final, prévention, compte rendu (constat, tests, cause, action, résultat).
"""


def _sources() -> str:
    return """## Sources utilisées pour les données techniques

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), pp. 3, 5 et 6 : modalités (épreuve uniquement écrite) et
  exigences AP-15 et AP-17. Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
- **Connecteurs ATX 24 broches et EPS 8 broches** (brochage, couleurs usuelles des fils,
  PS_ON#, PWR_OK, +5 VSB) : guide de conception des alimentations ATX12V (Intel) et norme
  EPS12V (SSI).
- **Puissance PCIe** (emplacement x16 : 75 W ; connecteur 6 broches : 75 W ; 8 broches :
  150 W) : spécification PCI Express CEM (PCI-SIG).
- **Connecteurs SATA** (alimentation 15 broches, données 7 broches) : spécification Serial ATA.
- **Démarrage UEFI/GPT et hérité/MBR, outil MBR2GPT** : documentation Microsoft sur
  l'installation de Windows et la conversion MBR vers GPT.
- **Événement Kernel-Power 41, codes d'arrêt MEMORY_MANAGEMENT (0x1A) et
  IRQL_NOT_LESS_OR_EQUAL (0xA)** : documentation Microsoft (référence des codes d'arrêt).
- **Processeurs Intel Core à suffixe F sans graphique intégré** : fiches produits Intel.

## Compléments pédagogiques (non imposés par la liste officielle)

La liste des pp. 5-6 demande le dépannage des dysfonctionnements courants (AP-15) et la notion
de compatibilité (AP-17). Les éléments suivants sont des **compléments** utiles pour rédiger
une intervention sûre, à ce titre signalés :

- sécurité électrique et ESD (AP-C02), batteries gonflées, matériel endommagé ;
- traçabilité et compte rendu (proches de AP-C01, approfondis en PR30) ;
- mémoire ECC, VRM, LED de diagnostic, entraînement de la mémoire DDR5, attributs SMART,
  journaux Windows (Kernel-Power 41), connecteur 16 broches des cartes graphiques récentes.

## Supports fictifs

Les cas, relevés, écrans, journaux et plans de carte de ce cours sont **fictifs** et
reconstitués pour l'entraînement ; les références de produits citées ne servent qu'à rendre la
situation réaliste. Aucun n'est une question officielle ou déjà posée par le Jury.
"""


def pr06_course_sections() -> list[tuple[str, str]]:
    """Blocs du cours (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("PR06 — Objectifs et place dans l'épreuve", _objectives()),
        ("PR06 — A. Méthode de diagnostic", _method()),
        ("PR06 — A. Sécurité des personnes, du matériel et des données", _safety()),
        ("PR06 — B. Chaîne de démarrage et symptômes", _boot_chain()),
        ("PR06 — B. Pannes de démarrage : tester dans l'ordre", _boot_failures()),
        ("PR06 — Connecteurs d'alimentation à reconnaître", _connectors()),
        ("PR06 — C. Sous-systèmes : mémoire, processeur, alimentation, carte mère", _subsystems_core()),
        ("PR06 — C. Sous-systèmes : affichage, stockage, périphériques, compatibilité", _subsystems_more()),
        ("PR06 — D. Lire les documents et décider", _documents_and_decisions()),
        ("PR06 — Exemples : quatre cas intégralement résolus", _cases()),
        ("PR06 — Pièges et erreurs fréquentes", _pitfalls()),
        ("PR06 — Exercices corrigés (12)", _exercises_intro()),
        ("PR06 — Mini-examen noté sur 20 : mode d'emploi", _mini_exam()),
        ("PR06 — Fiche mémo", _memo()),
        ("PR06 — Sources et compléments pédagogiques", _sources()),
    ]
