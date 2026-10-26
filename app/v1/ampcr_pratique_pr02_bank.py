"""PR02 « Alimentation, connectique, compatibilité et sécurité » — exercices corrigés et
mini-examen (ticket #203).

Même organisation que les cours pratiques déjà publiés (`app.v1.ampcr_pratique_pr06_bank`, dont
ce module réutilise le type d'item et la règle d'acceptation) :
- `PRACTICE_ITEMS` : 16 exercices corrigés affichés dans le cours (corrigé replié) et proposés
  dans « S'entraîner » — identifications de connecteurs, calculs (rendement, budget,
  tolérances), compatibilité d'une configuration, mauvais branchements, sécurité, symptômes et
  procédures écrites ;
- `EXAM_ITEMS` : les 10 questions du mini-examen noté /20 (2 points chacune), réponses libres,
  uniquement dans « Examen blanc », jamais affichées dans le cours.

Les fiches produits sont **fictives** ; les valeurs normalisées et tous les résultats chiffrés
viennent de `app.v1.ampcr_pratique_pr02_figures` (calculés, pas recopiés).
"""

from app.v1.ampcr_pratique_format import ExerciseDocument, ScoringCriterion, validate_exercise
from app.v1.ampcr_pratique_pr01_figures import fr_number
from app.v1.ampcr_pratique_pr02_figures import (
    E07_MEASURES,
    E08_CONFIG,
    RAILS_BY_NAME,
    Load,
    check_configuration,
    current_12v,
    losses,
    power_budget,
    recommended_psu,
    tolerance_range,
    volts,
    wall_power,
    within_tolerance,
)
from app.v1.ampcr_pratique_pr06_bank import (
    USAGE_EXAM,
    USAGE_PRACTICE,
    Classification,
    Ordering,
    PR06Item,
)

PR02_CODE = "PR02"

KIND_ID = "identification"
KIND_CALC = "calcul justifié"
KIND_COMPAT = "compatibilité"
KIND_WIRING = "branchement"
KIND_SAFETY = "sécurité"
KIND_SYMPTOM = "symptômes"
KIND_PROCEDURE = "procédure écrite"

# Exigences officielles du cours (matrice #192, audit #236) : chaque item en cite au moins une.
REQ = frozenset({"AP-04", "AP-06", "AP-17"})


def _c(label: str, points: float, expected: str) -> ScoringCriterion:
    return ScoringCriterion(label=label, points=points, expected=expected)


def _table(title: str, header: tuple[str, ...], *rows: tuple[str, ...]) -> ExerciseDocument:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return ExerciseDocument(title=title, kind="tableau", content_text="\n".join(lines))


def _console(title: str, *lines: str) -> ExerciseDocument:
    return ExerciseDocument(title=title, kind="console", content_text="\n".join(lines))


def _w(value: float) -> str:
    return f"{fr_number(value, 0)} W"


def _range(rail: str) -> str:
    low, high = tolerance_range(RAILS_BY_NAME[rail])
    return f"{volts(low)} à {volts(high)}"


# --- Données calculées réutilisées dans les énoncés et les corrigés --------------------------

E04_OUTPUT, E04_EFF = 360, 90  # bloc Gold à 50 % de charge environ
E04_WALL = wall_power(E04_OUTPUT, E04_EFF)  # 400 W
E04_LOSS = losses(E04_OUTPUT, E04_EFF)  # 40 W
E04_OLD_EFF = 75
E04_OLD_WALL = wall_power(E04_OUTPUT, E04_OLD_EFF)  # 480 W

E05_LOADS: tuple[Load, ...] = (
    Load("Processeur", 105, True),
    Load("Carte graphique", 170, True),
    Load("Carte mère", 35, False),
    Load("Mémoire (2 barrettes)", 8, False),
    Load("2 SSD", 12, False),
    Load("3 ventilateurs", 9, True),
)
E05_TOTAL = power_budget(E05_LOADS)  # 339 W
E05_GPU_RECO = 550
E05_RECOMMENDED = recommended_psu(E05_TOTAL, gpu_recommendation=E05_GPU_RECO)  # 450 → 550

E06_12V_AMPS = 45
E06_12V_WATTS = 12 * E06_12V_AMPS  # 540 W
E06_LOADS: tuple[Load, ...] = (Load("Processeur", 150, True), Load("Carte graphique", 320, True),
                               Load("Ventilateurs et disques", 30, True))
E06_12V_NEED = current_12v(E06_LOADS)  # 41,7 A

E07_OUT = [name for name, value in E07_MEASURES if not within_tolerance(RAILS_BY_NAME[name], value)]
E08_FAILED = [label for label, ok, _ in check_configuration(E08_CONFIG) if not ok]

X02_OUTPUT, X02_EFF = 450, 90
X02_WALL = wall_power(X02_OUTPUT, X02_EFF)  # 500 W
X03_LOADS: tuple[Load, ...] = (
    Load("Processeur", 65, True), Load("Carte mère", 30, False), Load("Mémoire", 6, False),
    Load("SSD NVMe", 7, False), Load("2 ventilateurs", 6, True),
)
X03_TOTAL = power_budget(X03_LOADS)  # 114 W
X03_RECOMMENDED = recommended_psu(X03_TOTAL)  # 150 W

E02_CATEGORIES = (
    "Carte mère (alimentation principale)",
    "Processeur (par le VRM)",
    "Carte graphique",
    "Unités de stockage et accessoires",
)
E13_CATEGORIES = ("Pratique correcte", "Pratique dangereuse ou interdite")


# =============================================================================================
# 16 exercices corrigés (cours + « S'entraîner »)
# =============================================================================================

PRACTICE_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="E01",
        usage=USAGE_PRACTICE,
        title="Identifier six câbles d'un bloc d'alimentation d'après leur description",
        question_type="document_analysis",
        requirement_ids=("AP-04", "AP-06"),
        kind=KIND_ID,
        context=(
            "Tu reçois en atelier un bloc d'alimentation ATX neuf, livré sans notice. Avant de le "
            "monter, tu relèves l'aspect de six câbles (document 1) pour préparer le branchement. "
            "Aucune étiquette n'est lisible, sauf les inscriptions indiquées."
        ),
        documents=(
            _table(
                "Document 1 — Relevé des câbles (bloc fictif)",
                ("Repère", "Aspect relevé"),
                ("A", "Gros connecteur à deux rangées, 20 broches + un bloc détachable de 4 broches"),
                ("B", "Connecteur 4+4 broches, fils jaunes et noirs, inscription « CPU »"),
                ("C", "Connecteur 6+2 broches, inscription « PCIe »"),
                ("D", "Connecteur plat et coudé en L, 15 contacts, plusieurs par câble"),
                ("E", "Connecteur blanc à 4 broches rondes en ligne : jaune, noir, noir, rouge"),
                ("F", "Connecteur à 16 broches : 12 grosses + 4 petites, une seule rangée de petites"),
            ),
        ),
        instructions=(
            "Nomme chaque connecteur A à F.",
            "Indique pour chacun ce qu'il alimente.",
            "Indique les deux connecteurs qu'un débutant risque de confondre et pourquoi il ne faut jamais forcer.",
        ),
        criteria=(
            _c("Noms", 1.5, "A ATX 24 broches (20+4) ; B EPS 8 broches (4+4) ; C PCIe 8 broches (6+2) ; D alimentation SATA 15 broches ; E Molex 4 broches ; F 12V-2x6 (12VHPWR) 16 broches (0,25 pt chacun)."),
            _c("Destinations", 1.5, "A carte mère ; B processeur par le VRM ; C et F carte graphique ; D disques et lecteurs SATA ; E anciens disques ou accessoires."),
            _c("Confusion", 1, "EPS 8 et PCIe 8 : même taille, mais tensions placées autrement et détrompeurs différents ; forcer provoque un court-circuit ou détruit le matériel."),
        ),
        correction=(
            "A : connecteur ATX 24 broches, souvent sécable en 20 + 4 : alimentation principale de la carte mère. B : EPS 8 broches (4+4), marqué CPU : alimente le processeur à travers le VRM. C : PCIe 8 broches (6+2) : carte graphique (150 W par connecteur 8 broches).",
            "D : alimentation SATA 15 broches, coudée : disques durs, SSD 2,5 pouces et lecteurs. E : Molex 4 broches (+12 V jaune, deux masses, +5 V rouge) : anciens disques et accessoires. F : 12V-2x6 (successeur du 12VHPWR) : carte graphique récente, jusqu'à 600 W.",
            "Le piège classique est EPS 8 / PCIe 8 : ils se ressemblent, mais l'EPS a ses quatre +12 V sur une rangée, le PCIe trois +12 V placés autrement, et les détrompeurs diffèrent. Un connecteur qui résiste n'est pas le bon : forcer peut mettre le +12 V en court-circuit.",
        ),
    ),
    PR06Item(
        key="E02",
        usage=USAGE_PRACTICE,
        title="Ranger les connecteurs du bloc selon ce qu'ils alimentent",
        question_type="classification",
        requirement_ids=("AP-04", "AP-06"),
        kind=KIND_ID,
        context=(
            "Un stagiaire prépare la fiche de câblage d'un PC de bureau qu'il va monter. Pour qu'il "
            "ne se trompe pas de prise, tu lui demandes de ranger chaque connecteur du bloc "
            "d'alimentation selon l'élément qu'il alimente dans la configuration."
        ),
        instructions=("Classe chacun des sept connecteurs dans la catégorie de l'élément qu'il alimente.",),
        criteria=(
            _c("Classement", 3.5, "ATX 24 : carte mère ; EPS 8 « CPU » et ATX12V 4 broches : processeur ; PCIe 6+2 et 12V-2x6 : carte graphique ; SATA 15 et Molex : stockage et accessoires (0,5 pt par élément)."),
        ),
        correction=(
            "Carte mère : le connecteur ATX 24 broches (alimentation principale). Processeur : l'EPS 8 broches marqué CPU et, sur les cartes plus anciennes ou modestes, l'ATX12V 4 broches (un demi-EPS) ; ils alimentent le VRM qui fabrique la tension du processeur.",
            "Carte graphique : le PCIe 6+2 broches et le 12V-2x6 à 16 broches. Stockage et accessoires : l'alimentation SATA 15 broches (disques, SSD 2,5 pouces, lecteurs) et le Molex 4 broches (anciens disques, ventilateurs, accessoires).",
        ),
        classification=Classification(
            categories=E02_CATEGORIES,
            elements=(
                "ATX 24 broches (20+4)",
                "EPS 8 broches (4+4) marqué « CPU »",
                "PCIe 6+2 broches",
                "Alimentation SATA 15 broches",
                "12V-2x6 à 16 broches",
                "Molex 4 broches",
                "ATX12V 4 broches carré, fils jaunes et noirs",
            ),
            correct=(0, 1, 2, 3, 2, 3, 1),
        ),
    ),
    PR06Item(
        key="E03",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre le remplacement d'un bloc d'alimentation",
        question_type="ordering",
        requirement_ids=("AP-04", "AP-C02"),
        kind=KIND_PROCEDURE,
        context=(
            "Le bloc d'alimentation d'un PC de bureau a été déclaré défectueux après un test avec "
            "un bloc connu fonctionnel. Tu rédiges la procédure de remplacement pour un collègue "
            "débutant. Les étapes ci-dessous sont mélangées."
        ),
        instructions=("Remets les sept étapes dans l'ordre d'une intervention sûre.",),
        criteria=(
            _c("Ordre", 3, "Arrêter et débrancher → décharger (bouton) → bracelet antistatique → repérer et débrancher les câbles → déposer l'ancien bloc et poser le nouveau → rebrancher chaque connecteur → contrôler les tensions et tester en charge."),
        ),
        correction=(
            "1. Arrêter le système, mettre l'interrupteur du bloc sur 0 et débrancher le câble secteur. 2. Appuyer quelques secondes sur le bouton de démarrage pour vider l'énergie résiduelle (LED de veille éteinte). 3. Mettre le bracelet antistatique relié au châssis.",
            "4. Photographier puis débrancher chaque câble (ATX 24, EPS, PCIe, SATA). 5. Dévisser et sortir l'ancien bloc, installer le nouveau, ventilateur orienté vers son filtre. 6. Rebrancher chaque connecteur jusqu'au clic, avec les câbles du nouveau bloc. 7. Rebrancher le secteur, vérifier les tensions et tester en charge, puis rédiger le compte rendu.",
        ),
        ordering=Ordering(
            steps=(
                "Rebrancher chaque connecteur jusqu'au clic, avec les câbles du nouveau bloc.",
                "Mettre le bracelet antistatique relié au châssis.",
                "Arrêter le système, interrupteur du bloc sur 0, débrancher le câble secteur.",
                "Dévisser l'ancien bloc et installer le nouveau, ventilateur vers son filtre.",
                "Rebrancher le secteur, vérifier les tensions et tester en charge.",
                "Appuyer quelques secondes sur le bouton de démarrage pour vider l'énergie résiduelle.",
                "Photographier puis débrancher chaque câble du bloc.",
            ),
            correct=(2, 5, 1, 6, 3, 0, 4),
        ),
    ),
    PR06Item(
        key="E04",
        usage=USAGE_PRACTICE,
        title="Calculer la puissance absorbée et les pertes d'un bloc",
        question_type="document_analysis",
        requirement_ids=("AP-04",),
        kind=KIND_CALC,
        context=(
            "Un client remplace un vieux bloc sans certification par un bloc « 80 PLUS Gold ». "
            f"Son PC consomme {E04_OUTPUT} W côté composants pendant ses longues sessions de "
            "calcul. Il veut comprendre la notion de rendement et ce que le changement "
            "apporte. Les rendements mesurés à cette charge sont dans le document 1 (fictifs)."
        ),
        documents=(
            _table(
                "Document 1 — Rendement à la charge du client (fictif)",
                ("Bloc", "Rendement mesuré"),
                ("Ancien bloc", f"{E04_OLD_EFF} %"),
                ("Nouveau bloc Gold", f"{E04_EFF} %"),
            ),
        ),
        instructions=(
            "Explique en une phrase ce qu'est le rendement d'un bloc.",
            "Calcule, pour chaque bloc, la puissance absorbée au secteur et les pertes.",
            "Indique deux avantages concrets du nouveau bloc pour le client.",
        ),
        criteria=(
            _c("Définition", 1, "Rendement = puissance fournie aux composants / puissance absorbée au secteur ; le reste est perdu en chaleur."),
            _c("Calculs", 2, f"Ancien : {E04_OUTPUT} / 0,{E04_OLD_EFF} = {_w(E04_OLD_WALL)} absorbés, {_w(E04_OLD_WALL - E04_OUTPUT)} perdus ; nouveau : {E04_OUTPUT} / 0,{E04_EFF} = {_w(E04_WALL)} absorbés, {_w(E04_LOSS)} perdus."),
            _c("Avantages", 1, f"Moins d'électricité consommée ({_w(E04_OLD_WALL - E04_WALL)} de moins pendant le calcul), moins de chaleur dans le bloc, donc ventilateur plus lent et plus silencieux, composants moins sollicités."),
        ),
        correction=(
            "Le rendement est le rapport entre la puissance que le bloc fournit aux composants et celle qu'il absorbe au secteur. Ce qui manque est transformé en chaleur dans le bloc.",
            f"Ancien bloc : puissance absorbée = {E04_OUTPUT} W / 0,{E04_OLD_EFF} = {_w(E04_OLD_WALL)} ; pertes = {_w(E04_OLD_WALL)} − {E04_OUTPUT} W = {_w(E04_OLD_WALL - E04_OUTPUT)}. Nouveau bloc : {E04_OUTPUT} W / 0,{E04_EFF} = {_w(E04_WALL)} ; pertes = {_w(E04_LOSS)}.",
            f"Le client économise {_w(E04_OLD_WALL - E04_WALL)} au secteur à chaque instant de calcul ; le bloc chauffe deux fois moins, son ventilateur tourne moins vite (moins de bruit) et l'intérieur du boîtier est moins chaud. Le rendement ne change pas la puissance disponible pour les composants.",
        ),
    ),
    PR06Item(
        key="E05",
        usage=USAGE_PRACTICE,
        title="Dimensionner le bloc d'un PC de bureautique et de jeu léger",
        question_type="document_analysis",
        requirement_ids=("AP-04", "AP-17"),
        kind=KIND_CALC,
        context=(
            "Un client fait monter un PC pour la bureautique et quelques jeux. Tu as relevé les "
            "puissances maximales des fiches (document 1, fictives) ; la fiche de la carte "
            f"graphique recommande un bloc de {E05_GPU_RECO} W avec un connecteur PCIe 8 broches. "
            "Le vendeur propose les blocs du document 2."
        ),
        documents=(
            _table(
                "Document 1 — Puissances maximales des fiches (fictives)",
                ("Composant", "Puissance"),
                *((load.name, f"{load.watts} W") for load in E05_LOADS),
            ),
            _table(
                "Document 2 — Blocs proposés (fictifs)",
                ("Offre", "Puissance", "Certification", "Connecteurs PCIe"),
                ("P1", "400 W", "80 PLUS", "1 × 6 broches"),
                ("P2", "550 W", "Bronze", "aucun"),
                ("P3", "550 W", "Gold", "2 × 6+2 broches"),
                ("P4", "1200 W", "Platinum", "6 × 6+2 broches"),
            ),
        ),
        instructions=(
            "Calcule la puissance totale et la puissance conseillée avec une marge de 30 %, arrondie au palier de 50 W.",
            "Choisis le bloc en justifiant la puissance et les connecteurs.",
            "Explique pourquoi le bloc le plus puissant n'est pas le meilleur choix.",
        ),
        criteria=(
            _c("Budget", 1.5, f"Total {E05_TOTAL} W ; × 1,3 ≈ {round(E05_TOTAL * 1.3)} W → palier {recommended_psu(E05_TOTAL)} W ; la recommandation de la carte graphique ({E05_GPU_RECO} W) l'emporte : {E05_RECOMMENDED} W."),
            _c("Choix", 1.5, "P3 : 550 W, connecteurs 6+2 pour la carte graphique, rendement Gold ; P1 trop faible et sans 8 broches ; P2 sans connecteur PCIe (adaptateur à proscrire)."),
            _c("Surdimensionnement", 1, "P4 : plus cher, fonctionnerait à faible charge où le rendement est moins bon ; aucun bénéfice pour cette configuration."),
        ),
        correction=(
            f"Total des puissances maximales : {' + '.join(str(load.watts) for load in E05_LOADS)} = {E05_TOTAL} W. Avec 30 % de marge : {E05_TOTAL} × 1,3 ≈ {round(E05_TOTAL * 1.3)} W, soit le palier de {recommended_psu(E05_TOTAL)} W. La carte graphique recommande {E05_GPU_RECO} W : on retient la valeur la plus élevée, {E05_RECOMMENDED} W.",
            "P1 (400 W) est trop faible et n'a qu'un 6 broches. P2 a la puissance mais aucun câble PCIe : il faudrait un adaptateur depuis des Molex ou SATA, à proscrire. P3 convient : 550 W, deux 6+2 broches, rendement Gold.",
            "P4 n'apporte rien : le PC l'utiliserait autour de 25 % de sa puissance, zone où le rendement est moins bon, pour un prix bien plus élevé. On choisit la bonne taille, pas la plus grosse.",
        ),
    ),
    PR06Item(
        key="E06",
        usage=USAGE_PRACTICE,
        title="Lire l'étiquette d'un bloc : le +12 V suffit-il ?",
        question_type="document_analysis",
        requirement_ids=("AP-04", "AP-17"),
        kind=KIND_CALC,
        context=(
            "Un client veut installer une carte graphique plus puissante dans son PC sans changer "
            "de bloc. Tu relèves l'étiquette collée sur le bloc (document 1, fictive) et les "
            "puissances maximales des composants alimentés en +12 V (document 2, fictives)."
        ),
        documents=(
            _table(
                "Document 1 — Étiquette du bloc (fictive)",
                ("Sortie", "+3,3 V", "+5 V", "+12 V", "−12 V", "+5 VSB"),
                ("Courant max", "20 A", "20 A", f"{E06_12V_AMPS} A", "0,3 A", "2,5 A"),
                ("Puissance max", "120 W (+3,3 V et +5 V combinés)", "", f"{E06_12V_WATTS} W", "3,6 W", "12,5 W"),
                ("Puissance totale", "550 W", "", "", "", ""),
            ),
            _table(
                "Document 2 — Charges sur le +12 V après le changement (fiches fictives)",
                ("Composant", "Puissance maximale"),
                *((load.name, f"{load.watts} W") for load in E06_LOADS),
            ),
        ),
        instructions=(
            "Calcule la puissance disponible sur le +12 V à partir du courant de l'étiquette.",
            "Calcule le courant demandé sur le +12 V par la nouvelle configuration.",
            "Conclus : le bloc convient-il ? Justifie avec la marge.",
        ),
        criteria=(
            _c("Puissance +12 V", 1, f"P = U × I = 12 V × {E06_12V_AMPS} A = {E06_12V_WATTS} W."),
            _c("Courant demandé", 1.5, f"{power_budget(E06_LOADS)} W / 12 V ≈ {fr_number(E06_12V_NEED)} A."),
            _c("Conclusion", 1.5, f"{fr_number(E06_12V_NEED)} A sur {E06_12V_AMPS} A disponibles : à peine {fr_number(100 * (1 - E06_12V_NEED / E06_12V_AMPS), 0)} % de marge, insuffisant (pics de la carte graphique, vieillissement) : bloc plus puissant conseillé."),
        ),
        correction=(
            f"Sur le +12 V, le bloc fournit au plus P = U × I = 12 V × {E06_12V_AMPS} A = {E06_12V_WATTS} W. La puissance totale de 550 W n'est pas disponible en entier sur le +12 V : il faut lire la ligne du rail.",
            f"Les composants sur le +12 V demandent {' + '.join(str(load.watts) for load in E06_LOADS)} = {power_budget(E06_LOADS)} W, soit I = P / U = {power_budget(E06_LOADS)} / 12 ≈ {fr_number(E06_12V_NEED)} A.",
            f"Le bloc tiendrait sur le papier ({fr_number(E06_12V_NEED)} A < {E06_12V_AMPS} A), mais la marge n'est que d'environ {fr_number(100 * (1 - E06_12V_NEED / E06_12V_AMPS), 0)} % : les pics de consommation de la carte graphique et le vieillissement du bloc risquent de provoquer des arrêts en jeu. Conseil : un bloc plus puissant, avec les connecteurs demandés par la nouvelle carte.",
        ),
    ),
    PR06Item(
        key="E07",
        usage=USAGE_PRACTICE,
        title="Interpréter un relevé de tensions au testeur",
        question_type="document_analysis",
        requirement_ids=("AP-04",),
        kind=KIND_SYMPTOM,
        context=(
            "Un PC de bureau redémarre parfois sans raison. Un collègue a branché un testeur "
            "d'alimentation sur les connecteurs du bloc, PC débranché de ses composants, et a noté "
            "les tensions affichées (document 1). La norme ATX admet ±5 % sur +12 V, +5 V, "
            "+3,3 V et +5 VSB, et ±10 % sur −12 V."
        ),
        documents=(
            _table(
                "Document 1 — Relevé du testeur (fictif)",
                ("Sortie", "Tension mesurée"),
                *((name, volts(value)) for name, value in E07_MEASURES),
            ),
        ),
        instructions=(
            "Calcule la plage admise pour chaque sortie.",
            "Indique les sorties hors tolérance.",
            "Conclus sur le bloc et sur ce que la mesure ne prouve pas.",
        ),
        criteria=(
            _c("Plages", 1.5, f"+12 V : {_range('+12 V')} ; +5 V et +5 VSB : {_range('+5 V')} ; +3,3 V : {_range('+3,3 V')} ; −12 V : {_range('−12 V')}."),
            _c("Hors tolérance", 1.5, f"{' et '.join(E07_OUT)} hors plage ; les autres sont dans la tolérance."),
            _c("Conclusion", 1, "Bloc à remplacer (jamais l'ouvrir) ; une mesure à vide ne prouve pas qu'un bloc tient en charge : une mesure conforme n'innocente pas le bloc."),
        ),
        correction=(
            f"Plages : +12 V de {_range('+12 V')} ; +5 V et +5 VSB de {_range('+5 V')} ; +3,3 V de {_range('+3,3 V')} (environ 3,14 à 3,47 V) ; −12 V de {_range('−12 V')}.",
            f"+12 V à {volts(E07_MEASURES[0][1])} : conforme. +5 V à {volts(E07_MEASURES[1][1])} : trop haut. +3,3 V à {volts(E07_MEASURES[2][1])} : conforme. +5 VSB à {volts(E07_MEASURES[3][1])} : trop bas. −12 V à {volts(E07_MEASURES[4][1])} : conforme. Deux sorties sont hors tolérance : {' et '.join(E07_OUT)}.",
            "Le bloc est défaillant et se remplace ; on ne l'ouvre jamais. Remarque : un testeur mesure à vide ou sous très faible charge ; un bloc conforme au testeur peut encore s'effondrer sous la charge d'un jeu. La conclusion se confirme en remettant un bloc connu fonctionnel.",
        ),
    ),
    PR06Item(
        key="E08",
        usage=USAGE_PRACTICE,
        title="Contrôler la compatibilité d'un devis avant commande",
        question_type="document_analysis",
        requirement_ids=("AP-17", "AP-06", "AP-04"),
        kind=KIND_COMPAT,
        context=(
            "Un client a préparé seul le devis d'un PC de jeu (document 1, fiches fictives) et te "
            "demande de le valider avant de commander. Tu appliques la grille de compatibilité "
            "du cours, critère par critère, sans rien supposer qui ne figure pas sur les fiches."
        ),
        documents=(
            _table(
                "Document 1 — Extraits des fiches du devis (fictives)",
                ("Pièce", "Caractéristiques"),
                ("Processeur", f"socket {E08_CONFIG.cpu_socket}"),
                ("Carte mère", f"{E08_CONFIG.board_form}, socket {E08_CONFIG.board_socket}, 4 × {E08_CONFIG.board_memory}, M.2 {E08_CONFIG.board_m2}"),
                ("Mémoire", f"2 × 16 Go {E08_CONFIG.ram}"),
                ("SSD", f"M.2 2280 {E08_CONFIG.ssd_m2}"),
                ("Carte graphique", f"longueur {E08_CONFIG.gpu_length_mm} mm, {E08_CONFIG.gpu_pcie8_needed} × PCIe 8 broches, bloc recommandé {E08_CONFIG.gpu_psu_recommendation_w} W"),
                ("Ventirad", f"hauteur {E08_CONFIG.cooler_height_mm} mm, sockets {', '.join(E08_CONFIG.cooler_sockets)}"),
                ("Boîtier", f"cartes {' / '.join(E08_CONFIG.case_forms)}, carte graphique {E08_CONFIG.case_gpu_max_mm} mm max, ventirad {E08_CONFIG.case_cooler_max_mm} mm max, bloc {' / '.join(E08_CONFIG.case_psu_forms)}"),
                ("Bloc", f"{E08_CONFIG.psu_watts} W, {E08_CONFIG.psu_form}, {E08_CONFIG.psu_pcie8} × PCIe 6+2 broches"),
            ),
        ),
        instructions=(
            "Contrôle chaque critère de compatibilité et note conforme ou non conforme avec la valeur qui le justifie.",
            "Propose une correction pour chaque point non conforme.",
        ),
        criteria=(
            _c("Points conformes", 1.5, "Socket LGA1700 identique, DDR5 DIMM conforme, SSD NVMe dans un M.2 NVMe ou SATA, carte graphique 310 ≤ 330 mm, bloc 750 W ≥ 700 W avec 2 × 8 broches, bloc ATX accepté."),
            _c("Non conformes", 1.5, f"{' ; '.join(E08_FAILED)} : carte ATX dans un boîtier microATX/Mini-ITX ; ventirad 158 mm pour 150 mm au plus."),
            _c("Corrections", 1, "Boîtier acceptant l'ATX (ou carte microATX équivalente) ; ventirad de 150 mm au plus (ou boîtier plus large)."),
        ),
        correction=(
            "Conformes : processeur et carte en LGA1700 (vérifier aussi la liste des processeurs pris en charge et la version du firmware) ; mémoire DDR5 DIMM comme la carte ; SSD M.2 NVMe dans un emplacement NVMe ou SATA ; carte graphique de 310 mm pour 330 mm au plus ; bloc ATX de 750 W pour 700 W recommandés, avec deux PCIe 6+2 pour deux 8 broches demandés.",
            "Non conformes : la carte mère est ATX, le boîtier n'accepte que le microATX et le Mini-ITX (une carte plus grande n'entre jamais dans un boîtier prévu pour plus petit) ; le ventirad mesure 158 mm pour 150 mm au plus : le panneau latéral ne fermerait pas.",
            "Corrections : choisir un boîtier qui accepte l'ATX (ou une carte microATX de même socket et mémoire) et un ventirad de 150 mm au plus compatible LGA1700 (ou un boîtier plus large). Noter les références vérifiées dans le devis.",
        ),
    ),
    PR06Item(
        key="E09",
        usage=USAGE_PRACTICE,
        title="SSD M.2 non détecté : SATA ou NVMe ?",
        question_type="document_analysis",
        requirement_ids=("AP-06", "AP-17"),
        kind=KIND_COMPAT,
        context=(
            "Un client a acheté un SSD M.2 2280 et l'a installé lui-même. Le SSD n'apparaît ni "
            "dans le firmware ni dans Windows. Tu relèves l'étiquette du SSD et le tableau des "
            "emplacements du manuel de sa carte mère (document 1, fictifs)."
        ),
        documents=(
            _table(
                "Document 1 — Étiquette et manuel (fictifs)",
                ("Élément", "Information"),
                ("Étiquette du SSD", "M.2 2280, interface SATA 6 Gb/s, deux encoches (clé B+M)"),
                ("M.2_1 (près du processeur)", "clé M, PCIe 4.0 x4, NVMe uniquement — SSD installé ici"),
                ("M.2_2 (près du chipset)", "clé M, PCIe 3.0 x4 ou SATA ; en mode SATA, le port SATA6 est désactivé"),
                ("Ports SATA", "SATA1 à SATA6 ; un disque dur est branché sur SATA6"),
            ),
        ),
        instructions=(
            "Explique pourquoi le SSD n'est pas détecté alors qu'il est entré dans l'emplacement.",
            "Indique où l'installer et la conséquence à anticiper.",
            "Rédige le conseil donné au client pour un prochain achat.",
        ),
        criteria=(
            _c("Cause", 1.5, "SSD M.2 SATA dans un emplacement NVMe uniquement : la forme (clé B+M) entre dans une clé M, mais l'interface n'est pas prise en charge."),
            _c("Solution", 1.5, "Le placer en M.2_2 qui accepte le SATA ; SATA6 sera désactivé : déplacer le disque dur sur un autre port SATA libre."),
            _c("Conseil", 1, "Vérifier l'interface (NVMe ou SATA) dans le manuel et la fiche, pas seulement la taille 2280 ; un SSD NVMe aurait été plus rapide en M.2_1."),
        ),
        correction=(
            "Le SSD est un M.2 SATA (clé B+M) : son encoche lui permet d'entrer dans un emplacement à clé M, mais M.2_1 ne gère que le NVMe. Même forme ne veut pas dire même interface : le SSD n'est pas vu.",
            "Il faut l'installer en M.2_2, qui accepte le SATA. Le manuel prévient que, dans ce mode, le port SATA6 est désactivé (lignes partagées) : avant de remonter, déplacer le câble du disque dur sur SATA1 à SATA5.",
            "Conseil : pour un M.2, vérifier l'interface demandée par l'emplacement (NVMe, SATA ou les deux) et les partages de ports dans le manuel. Un SSD NVMe en M.2_1 (PCIe 4.0 x4) aurait été bien plus rapide qu'un SATA plafonné à environ 600 Mo/s.",
        ),
    ),
    PR06Item(
        key="E10",
        usage=USAGE_PRACTICE,
        title="Choisir la liaison vidéo d'un écran 4K à 120 Hz",
        question_type="document_analysis",
        requirement_ids=("AP-06", "AP-17"),
        kind=KIND_COMPAT,
        context=(
            "Un client a acheté un écran 4K (3840 × 2160) à 120 Hz. Branché avec le vieux câble "
            "HDMI qu'il possédait, l'écran n'affiche que 30 Hz. Tu relèves les sorties de sa carte "
            "graphique et les entrées de l'écran (document 1, fictifs)."
        ),
        documents=(
            _table(
                "Document 1 — Sorties et entrées (fictives)",
                ("Appareil", "Connecteurs"),
                ("Carte graphique", "1 × HDMI 2.1, 3 × DisplayPort 1.4"),
                ("Écran", "1 × HDMI 2.1, 1 × DisplayPort 1.4"),
                ("Câble du client", "HDMI « High Speed » (prévu pour HDMI 1.4, 10,2 Gbit/s)"),
            ),
        ),
        instructions=(
            "Explique pourquoi l'écran reste à 30 Hz.",
            "Propose deux solutions de branchement qui permettent 4K à 120 Hz.",
            "Indique où l'écran doit être branché dans le PC et pourquoi.",
        ),
        criteria=(
            _c("Cause", 1.5, "Le câble limite le débit à celui du HDMI 1.4 (10,2 Gbit/s) : 4K à 30 Hz au plus ; les ports ne sont pas en cause."),
            _c("Solutions", 1.5, "Câble DisplayPort entre les ports DP 1.4 (4K 120 Hz) ; ou câble HDMI « Ultra High Speed » (HDMI 2.1, 48 Gbit/s) entre les ports HDMI 2.1."),
            _c("Branchement", 1, "Sur la carte graphique, pas sur les sorties de la carte mère (graphique intégré absent ou moins puissant)."),
        ),
        correction=(
            "Le câble est la limite : un câble HDMI « High Speed » n'est garanti que pour 10,2 Gbit/s (HDMI 1.4), ce qui permet la 4K à 30 Hz seulement. La forme du connecteur est identique d'une version HDMI à l'autre ; c'est le débit du câble et des ports qui compte.",
            "Solution 1 : un câble DisplayPort entre un DisplayPort 1.4 de la carte (32,4 Gbit/s) et l'entrée DisplayPort 1.4 de l'écran : 4K à 120 Hz. Solution 2 : un câble HDMI certifié « Ultra High Speed » (48 Gbit/s) entre les ports HDMI 2.1.",
            "L'écran se branche sur une sortie de la carte graphique : si on le branche sur la carte mère, on utilise la partie graphique du processeur (quand elle existe), moins performante, ou on n'a aucune image.",
        ),
    ),
    PR06Item(
        key="E11",
        usage=USAGE_PRACTICE,
        title="Brancher les périphériques USB au bon port",
        question_type="document_analysis",
        requirement_ids=("AP-06",),
        kind=KIND_COMPAT,
        context=(
            "Une cliente se plaint : son SSD externe USB-C (10 Gbit/s) copie à peine plus vite "
            "qu'une vieille clé, et son disque dur externe 2,5 pouces se déconnecte quand il est "
            "branché à son concentrateur USB non alimenté. Tu relèves les ports de son PC "
            "(document 1, fictif)."
        ),
        documents=(
            _table(
                "Document 1 — Ports du PC (fictif)",
                ("Port", "Norme indiquée dans le manuel"),
                ("Façade, USB-C", "USB 2.0"),
                ("Façade, 2 × USB-A", "USB 3.2 Gen 1 (5 Gbit/s)"),
                ("Arrière, USB-C", "USB 3.2 Gen 2 (10 Gbit/s)"),
                ("Arrière, 4 × USB-A", "USB 2.0"),
            ),
        ),
        instructions=(
            "Explique pourquoi le SSD est lent sur le port USB-C de façade.",
            "Indique le port à utiliser pour le SSD et la vitesse attendue.",
            "Explique la déconnexion du disque dur et propose une solution.",
        ),
        criteria=(
            _c("Cause", 1, "USB-C est une forme de connecteur, pas une vitesse : le port de façade est en USB 2.0 (480 Mbit/s)."),
            _c("Bon port", 1.5, "Port USB-C arrière en USB 3.2 Gen 2 : jusqu'à 10 Gbit/s, la vitesse du SSD."),
            _c("Disque dur", 1.5, "Un concentrateur non alimenté partage le courant d'un seul port (0,9 A en USB 3) ; au démarrage du moteur le disque manque de courant : le brancher directement au PC ou utiliser un concentrateur alimenté."),
        ),
        correction=(
            "Le port USB-C de façade est câblé en USB 2.0 : 480 Mbit/s au plus. USB-C décrit la forme de la prise ; la vitesse dépend de la norme du port (et du câble).",
            "Le SSD doit aller sur l'USB-C arrière, en USB 3.2 Gen 2 : 10 Gbit/s, comme le SSD. À défaut, un USB-A 3.2 Gen 1 (5 Gbit/s) reste dix fois plus rapide que l'USB 2.0.",
            "Un disque dur 2,5 pouces est alimenté par le port USB. Un concentrateur non alimenté partage entre tous ses ports le courant d'un seul port du PC (0,9 A en USB 3) : au démarrage du moteur, le courant manque et le disque se déconnecte. Solution : le brancher directement sur un port USB 3 du PC, ou utiliser un concentrateur avec son propre bloc secteur.",
        ),
    ),
    PR06Item(
        key="E12",
        usage=USAGE_PRACTICE,
        title="Repérer les mauvais branchements d'un montage",
        question_type="document_analysis",
        requirement_ids=("AP-06", "AP-04"),
        kind=KIND_WIRING,
        context=(
            "Un stagiaire a monté un PC de bureau et décrit ses branchements (document 1). Au "
            "premier essai, les ventilateurs tournent une seconde puis tout s'arrête. Tu relis sa "
            "description avant de rallumer quoi que ce soit."
        ),
        documents=(
            _table(
                "Document 1 — Branchements décrits par le stagiaire",
                ("N°", "Branchement réalisé"),
                ("1", "ATX 24 broches branché et clipsé sur la carte mère"),
                ("2", "Connecteur EPS « CPU » de la carte mère laissé libre : « il y avait déjà le 24 broches »"),
                ("3", "Carte graphique alimentée par deux câbles PCIe pris dans le carton d'un ancien bloc modulaire d'une autre marque"),
                ("4", "Ventirad branché sur le connecteur SYS_FAN2"),
                ("5", "SSD SATA : câble de données branché, alimentation SATA branchée"),
                ("6", "Écran branché sur la sortie HDMI de la carte mère"),
            ),
        ),
        instructions=(
            "Relève chaque branchement incorrect et explique le risque ou la conséquence.",
            "Indique la correction et l'ordre des vérifications avant le nouvel essai.",
        ),
        criteria=(
            _c("Erreurs", 2, "2 : EPS obligatoire, sans lui le processeur n'est pas alimenté (arrêt immédiat) ; 3 : câbles modulaires d'un autre bloc, brochage côté bloc différent, risque de destruction ; 4 : ventirad sur CPU_FAN (sinon alerte ou arrêt) ; 6 : écran sur la carte graphique."),
            _c("Corrections et ordre", 2, "PC débranché et déchargé, bracelet : retirer les câbles étrangers et utiliser ceux du bloc ; brancher l'EPS ; ventirad sur CPU_FAN ; écran sur la carte graphique ; vérifier chaque clip, puis essai."),
        ),
        correction=(
            "Branchement 2 : l'EPS est obligatoire ; le 24 broches alimente la carte, pas le VRM du processeur. Sans EPS, le PC s'allume une seconde puis s'arrête, ce qui correspond au symptôme.",
            "Branchement 3 : très dangereux. Les câbles modulaires ne sont pas normalisés côté bloc : un câble d'une autre marque ou d'un autre modèle peut envoyer du +12 V sur une masse ou sur une broche de signal et détruire la carte graphique ou le SSD. On n'utilise que les câbles livrés avec le bloc installé.",
            "Branchement 4 : le ventirad doit aller sur CPU_FAN, que le firmware surveille ; sur SYS_FAN la carte peut refuser de démarrer ou afficher « CPU fan error ». Branchement 6 : avec une carte graphique installée, l'écran se branche sur elle. Le 1 et le 5 sont corrects.",
            "Ordre : débrancher le secteur et décharger, bracelet antistatique ; retirer les câbles PCIe étrangers et poser ceux du bloc ; brancher l'EPS jusqu'au clic ; ventirad sur CPU_FAN ; écran sur la carte graphique ; vérifier tous les clips, puis rallumer.",
        ),
    ),
    PR06Item(
        key="E13",
        usage=USAGE_PRACTICE,
        title="Trier les pratiques sûres et dangereuses à l'atelier",
        question_type="classification",
        requirement_ids=("AP-C02", "AP-04"),
        kind=KIND_SAFETY,
        context=(
            "Pour l'accueil d'un nouveau stagiaire, l'atelier affiche une liste de pratiques "
            "observées lors des interventions sur les PC et les portables. Le stagiaire doit "
            "distinguer celles qui sont correctes de celles qui mettent en danger les personnes "
            "ou le matériel."
        ),
        instructions=("Classe chacune des huit pratiques : correcte, ou dangereuse ou interdite.",),
        criteria=(
            _c("Classement", 4, "Correctes : débrancher puis appuyer sur le bouton ; bracelet relié au châssis ; batterie gonflée isolée dans un bac métallique ; testeur sur les connecteurs du bloc. Dangereuses : ouvrir le bloc ; travailler branché « car éteint » ; percer ou presser une batterie gonflée ; adaptateur Molex → PCIe pour une carte puissante (0,5 pt par élément)."),
        ),
        correction=(
            "Correctes : débrancher le câble secteur puis appuyer sur le bouton de démarrage (le +5 VSB reste présent tant que le PC est branché) ; porter un bracelet antistatique relié au châssis ; isoler une batterie gonflée dans un bac métallique ou ininflammable, loin de tout combustible ; mesurer avec un testeur branché sur les connecteurs du bloc.",
            "Dangereuses ou interdites : ouvrir un bloc d'alimentation (condensateurs chargés à plusieurs centaines de volts même débranché) ; travailler dans un PC éteint mais branché ; percer, presser ou recharger une batterie gonflée (risque d'incendie) ; alimenter une carte graphique puissante par un adaptateur Molex ou SATA vers PCIe (connecteurs prévus pour bien moins de courant : échauffement, fonte).",
        ),
        classification=Classification(
            categories=E13_CATEGORIES,
            elements=(
                "Ouvrir le bloc d'alimentation pour souffler la poussière à l'intérieur",
                "Débrancher le câble secteur puis appuyer quelques secondes sur le bouton de démarrage",
                "Travailler dans un PC éteint mais resté branché « puisqu'il est éteint »",
                "Porter un bracelet antistatique relié au châssis",
                "Percer une batterie gonflée pour la dégonfler",
                "Placer une batterie gonflée dans un bac métallique, loin de tout combustible",
                "Alimenter une carte graphique de 250 W par un adaptateur Molex vers PCIe 8 broches",
                "Mesurer les tensions avec un testeur branché sur les connecteurs du bloc",
            ),
            correct=(1, 0, 1, 0, 1, 0, 1, 0),
        ),
    ),
    PR06Item(
        key="E14",
        usage=USAGE_PRACTICE,
        title="Prendre en charge un portable à la batterie gonflée",
        question_type="long_answer",
        requirement_ids=("AP-C02", "AP-04"),
        kind=KIND_SAFETY,
        context=(
            "Un client dépose un ordinateur portable dont le pavé tactile est soulevé et dont la "
            "coque ne ferme plus bien. Il précise que le portable chauffe en charge et qu'il "
            "l'utilise toujours branché. Tu soupçonnes une batterie lithium-ion gonflée. Le "
            "portable est éteint et débranché sur ton plan de travail."
        ),
        instructions=(
            "Explique le danger d'une batterie lithium-ion gonflée.",
            "Rédige les mesures immédiates et la procédure de retrait.",
            "Indique ce que deviennent la batterie et ce que tu dis au client.",
        ),
        criteria=(
            _c("Danger", 1, "Gaz produits par la dégradation des cellules ; risque d'emballement thermique, d'incendie et de fumées toxiques, surtout si on la perce, la presse ou la charge."),
            _c("Mesures et retrait", 2, "Ne plus charger ni allumer ; ne pas presser ; zone dégagée, sans combustible ; retirer avec des outils non coupants selon la notice ; jamais percer ni plier ; placer dans un bac métallique ou du sable ; surveiller."),
            _c("Suite", 1, "Batterie au point de collecte des piles et batteries (Bebat en Belgique), jamais à la poubelle ; batterie de remplacement compatible (référence, tension, capacité) ; conseil d'usage."),
        ),
        correction=(
            "Une batterie lithium-ion gonfle quand ses cellules se dégradent et produisent des gaz. Percée, écrasée, chauffée ou rechargée, elle peut s'emballer : flammes, projections et fumées toxiques, difficiles à éteindre.",
            "Mesures immédiates : ne plus brancher le chargeur ni allumer le portable ; ne pas appuyer sur la coque. Travailler sur une surface dégagée, sans combustible à proximité, extincteur adapté accessible. Retirer la batterie selon la notice du fabricant, avec des outils non coupants (spatule plastique), sans plier ni percer la batterie. La placer aussitôt dans un bac métallique (ou sur du sable), loin du reste, et la surveiller.",
            "La batterie part au point de collecte des piles et batteries (en Belgique, réseau Bebat), jamais à la poubelle. On commande une batterie compatible (référence du fabricant, tension, capacité, connecteur). Au client : expliquer le danger, conseiller de ne pas laisser le portable en charge permanente à chaud, et noter l'intervention dans le compte rendu.",
        ),
    ),
    PR06Item(
        key="E15",
        usage=USAGE_PRACTICE,
        title="Arrêts en jeu : évaluer l'hypothèse de l'alimentation",
        question_type="document_analysis",
        requirement_ids=("AP-04", "AP-17"),
        kind=KIND_SYMPTOM,
        context=(
            "Depuis l'installation d'une nouvelle carte graphique, un PC s'éteint d'un coup "
            "(écran noir, ventilateurs arrêtés) après quelques minutes de jeu ; il fonctionne "
            "normalement en bureautique. Tu as relevé les informations du document 1 (fictives)."
        ),
        documents=(
            _table(
                "Document 1 — Relevés (fictifs)",
                ("Élément", "Information"),
                ("Bloc", "500 W, 1 × PCIe 6+2 broches, 7 ans d'usage"),
                ("Nouvelle carte graphique", "2 × PCIe 8 broches, bloc recommandé 650 W"),
                ("Branchement constaté", "un 8 broches du bloc + un adaptateur 2 × Molex vers PCIe 8 broches"),
                ("Températures en jeu", "processeur 72 °C, carte graphique 70 °C (fiche : limites bien supérieures)"),
                ("Journal Windows", "Kernel-Power 41 : arrêt inattendu, sans écran bleu"),
            ),
        ),
        instructions=(
            "Indique l'hypothèse la plus probable et justifie-la avec au moins trois indices.",
            "Écarte au moins une autre hypothèse avec un relevé.",
            "Propose les tests et la correction, avec les précautions.",
        ),
        criteria=(
            _c("Hypothèse et indices", 1.5, "Bloc insuffisant : 500 W pour 650 W recommandés ; un seul câble PCIe, adaptateur Molex ; arrêt brutal sous charge seulement, depuis la nouvelle carte ; bloc âgé."),
            _c("Hypothèse écartée", 1, "Surchauffe peu probable : 72 et 70 °C, bien sous les limites ; Kernel-Power 41 confirme une coupure brutale, pas sa cause."),
            _c("Tests et correction", 1.5, "Supprimer l'adaptateur ; essai en charge avec un bloc connu bon d'au moins 650 W et deux câbles PCIe ; si stable : remplacer le bloc ; PC débranché, ESD."),
        ),
        correction=(
            "Hypothèse principale : le bloc ne suit pas la charge. Indices : 500 W pour 650 W recommandés par la carte ; un seul câble PCIe, le second alimenté par un adaptateur Molex (prévu pour bien moins de courant) ; arrêt brutal uniquement sous forte charge et depuis le changement de carte ; bloc de 7 ans, dont la capacité réelle a baissé. La protection de surintensité ou de surpuissance du bloc coupe tout.",
            "La surchauffe est peu probable : 72 °C et 70 °C restent bien sous les limites des fiches. L'événement Kernel-Power 41 dit seulement que l'arrêt a été brutal ; ce n'est pas une preuve de la cause.",
            "Test : PC débranché et déchargé, bracelet antistatique ; retirer l'adaptateur, installer un bloc connu fonctionnel d'au moins 650 W avec deux câbles PCIe 8 broches, puis rejouer dans les mêmes conditions. Si le PC reste stable, la cause est confirmée : remplacer le bloc (puissance et connecteurs adaptés) et le noter dans le compte rendu.",
        ),
    ),
    PR06Item(
        key="E16",
        usage=USAGE_PRACTICE,
        title="Ventilation et refroidissement : corriger un montage bruyant",
        question_type="document_analysis",
        requirement_ids=("AP-04", "AP-06"),
        kind=KIND_WIRING,
        context=(
            "Un PC monté par un client est bruyant et chauffe. Il s'inquiète aussi : « le "
            "ventilateur du bloc ne tourne pas, il est cassé ». Tu relèves la configuration du "
            "refroidissement (document 1, fictive)."
        ),
        documents=(
            _table(
                "Document 1 — Relevé du refroidissement (fictif)",
                ("Élément", "Constat"),
                ("Ventilateurs de façade (2)", "montés pour souffler vers l'extérieur du boîtier"),
                ("Ventilateur arrière (1)", "souffle vers l'extérieur"),
                ("Ventilateurs", "3 broches, branchés sur un répartiteur unique sur SYS_FAN1"),
                ("Bloc", "certifié Gold, mode « ventilateur arrêté à faible charge » indiqué sur la fiche ; ventilateur arrêté en bureautique, tourne en jeu"),
                ("Filtre de façade", "couvert de poussière"),
            ),
        ),
        instructions=(
            "Relève les défauts du refroidissement et explique leur effet.",
            "Réponds à l'inquiétude du client sur le ventilateur du bloc.",
            "Propose les corrections.",
        ),
        criteria=(
            _c("Défauts", 2, "Façade montée à l'envers : tous les ventilateurs extraient, l'air entre par les fentes sans filtre, flux désorganisé ; filtre encrassé ; ventilateurs 3 broches regroupés sur un seul connecteur : vitesse mal réglée (3 broches = réglage par la tension, pas en PWM) et charge du connecteur à vérifier."),
            _c("Bloc", 1, "Fonction normale : à faible charge le ventilateur s'arrête (mode semi-passif) et tourne quand le bloc chauffe ; il n'est pas en panne."),
            _c("Corrections", 1, "Retourner les ventilateurs de façade (entrée), nettoyer le filtre, répartir les ventilateurs sur les connecteurs de la carte et régler leur mode (DC pour 3 broches) dans le firmware."),
        ),
        correction=(
            "Les ventilateurs de façade soufflent vers l'extérieur : avec l'arrière, tout extrait ; l'air entre n'importe où, sans filtre, et ne passe plus sur les composants. Le flux attendu est façade → arrière et bas → haut (la flèche moulée sur le cadre du ventilateur indique le sens). Le filtre encrassé réduit encore l'arrivée d'air.",
            "Trois ventilateurs 3 broches sur un seul connecteur : leur vitesse se règle par la tension (mode DC), pas par le signal PWM d'un 4 broches ; si le connecteur est réglé en PWM, ils tournent à fond (bruit). Le courant total doit rester dans la limite du connecteur (manuel).",
            "Le ventilateur du bloc n'est pas en panne : la fiche indique un mode semi-passif ; à faible charge il reste arrêté, et il démarre quand le bloc chauffe, ce qui est observé en jeu.",
            "Corrections : retourner les ventilateurs de façade en entrée, nettoyer le filtre, répartir les ventilateurs sur les connecteurs SYS_FAN de la carte, régler le mode DC et une courbe de vitesse dans le firmware, puis contrôler températures et bruit.",
        ),
    ),
)

# =============================================================================================
# Mini-examen (10 questions × 2 points)
# =============================================================================================

EXAM_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="X01",
        usage=USAGE_EXAM,
        title="Nommer quatre connecteurs d'alimentation d'après leur description",
        question_type="document_analysis",
        requirement_ids=("AP-04", "AP-06"),
        kind=KIND_ID,
        context=(
            "Un collègue démonte un PC pour le recycler et te décrit quatre connecteurs encore "
            "branchés (document 1). Il veut savoir ce que chacun alimentait avant de les retirer, "
            "pour la fiche de démontage."
        ),
        documents=(
            _table(
                "Document 1 — Description des connecteurs",
                ("Repère", "Description"),
                ("1", "4+4 broches, fils jaunes et noirs, sur la carte mère près du processeur, câble marqué « CPU »"),
                ("2", "15 contacts en ligne, plat et coudé, sur un SSD 2,5 pouces"),
                ("3", "6+2 broches sur la tranche de la carte graphique"),
                ("4", "Fil vert et fil gris parmi 24 broches, sur le bord de la carte mère"),
            ),
        ),
        instructions=("Nomme chaque connecteur et indique ce qu'il alimente.",),
        criteria=(
            _c("Repère 1", 0.5, "EPS 8 broches (4+4) : processeur, par le VRM."),
            _c("Repère 2", 0.5, "Alimentation SATA 15 broches : le SSD 2,5 pouces."),
            _c("Repère 3", 0.5, "PCIe 8 broches (6+2) : la carte graphique (150 W par connecteur)."),
            _c("Repère 4", 0.5, "ATX 24 broches : alimentation principale de la carte mère (vert = PS_ON#, gris = PWR_OK)."),
        ),
        correction=(
            "1 : EPS 8 broches (4+4) marqué CPU, qui alimente le processeur à travers le VRM. 2 : alimentation SATA 15 broches du SSD. 3 : PCIe 8 broches (6+2) de la carte graphique. 4 : connecteur ATX 24 broches, alimentation principale de la carte mère ; le fil vert (PS_ON#) commande la mise en marche, le gris (PWR_OK) signale des tensions stables.",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Calculer la puissance absorbée par un bloc",
        question_type="short_answer",
        requirement_ids=("AP-04",),
        kind=KIND_CALC,
        context=(
            f"Pendant un rendu vidéo, les composants d'un PC consomment {X02_OUTPUT} W. Le bloc "
            f"a un rendement de {X02_EFF} % à cette charge. Le client pense que son bloc « de "
            f"750 W » consomme donc 750 W au secteur en permanence et veut comprendre."
        ),
        instructions=(
            "Calcule la puissance absorbée au secteur et les pertes.",
            "Corrige l'idée du client sur la puissance indiquée sur le bloc.",
        ),
        criteria=(
            _c("Calcul", 1, f"{X02_OUTPUT} / 0,{X02_EFF} = {_w(X02_WALL)} absorbés ; {_w(X02_WALL - X02_OUTPUT)} de pertes en chaleur."),
            _c("Puissance nominale", 1, "750 W est la puissance maximale que le bloc peut fournir ; il ne fournit que ce que les composants demandent."),
        ),
        correction=(
            f"Puissance absorbée = puissance fournie / rendement = {X02_OUTPUT} / 0,{X02_EFF} = {_w(X02_WALL)} ; pertes = {_w(X02_WALL - X02_OUTPUT)}, dissipées en chaleur. Les 750 W indiqués sont la puissance maximale que le bloc peut fournir en continu : il ne délivre que ce que les composants demandent, ici {X02_OUTPUT} W.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="Dimensionner le bloc d'un PC de bureautique",
        question_type="document_analysis",
        requirement_ids=("AP-04", "AP-17"),
        kind=KIND_CALC,
        context=(
            "Une école commande des PC de bureautique compacts, sans carte graphique (partie "
            "graphique du processeur). Tu relèves les puissances maximales des fiches (document 1, "
            "fictives) pour choisir le bloc."
        ),
        documents=(
            _table(
                "Document 1 — Puissances maximales (fictives)",
                ("Composant", "Puissance"),
                *((load.name, f"{load.watts} W") for load in X03_LOADS),
            ),
        ),
        instructions=(
            "Calcule le total, puis la puissance conseillée avec 30 % de marge, arrondie au palier de 50 W.",
            "Dis si un bloc de 750 W serait un bon choix.",
        ),
        criteria=(
            _c("Calcul", 1.5, f"Total {X03_TOTAL} W ; × 1,3 ≈ {round(X03_TOTAL * 1.3)} W → {X03_RECOMMENDED} W (en pratique, le plus petit bloc de qualité disponible)."),
            _c("750 W", 0.5, "Non : surdimensionné, plus cher, rendement médiocre à très faible charge."),
        ),
        correction=(
            f"Total : {' + '.join(str(load.watts) for load in X03_LOADS)} = {X03_TOTAL} W. Avec 30 % de marge : ≈ {round(X03_TOTAL * 1.3)} W, palier de {X03_RECOMMENDED} W ; en pratique, on prend le plus petit bloc de qualité proposé pour ce boîtier. Un bloc de 750 W tournerait autour de 15 % de charge, où le rendement est moins bon, pour un prix plus élevé : mauvais choix.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="Juger trois tensions mesurées",
        question_type="short_answer",
        requirement_ids=("AP-04",),
        kind=KIND_SYMPTOM,
        context=(
            "Au testeur, un bloc ATX affiche +12 V : 11,35 V ; +5 V : 5,10 V ; +3,3 V : 3,30 V. "
            "Les normes ATX admettent ±5 % sur ces trois sorties. Le PC du client redémarre "
            "parfois sous charge."
        ),
        instructions=(
            "Calcule les plages admises et dis quelles mesures sont hors tolérance.",
            "Conclus sur le bloc.",
        ),
        criteria=(
            _c("Plages", 1, f"+12 V : {_range('+12 V')} ; +5 V : {_range('+5 V')} ; +3,3 V : {_range('+3,3 V')}."),
            _c("Conclusion", 1, "11,35 V est sous 11,40 V : +12 V hors tolérance, les deux autres conformes ; bloc à remplacer (sans l'ouvrir), cohérent avec les redémarrages sous charge."),
        ),
        correction=(
            f"Plages : +12 V de {_range('+12 V')} ; +5 V de {_range('+5 V')} ; +3,3 V de {_range('+3,3 V')}. Le +12 V à 11,35 V est sous le minimum : hors tolérance. Le +5 V (5,10 V) et le +3,3 V (3,30 V) sont conformes. Le +12 V alimente le processeur et la carte graphique : un +12 V trop bas explique les redémarrages sous charge. Le bloc se remplace ; on ne l'ouvre jamais.",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Mémoire et processeur : la mise à niveau est-elle possible ?",
        question_type="document_analysis",
        requirement_ids=("AP-17", "AP-06"),
        kind=KIND_COMPAT,
        context=(
            "Un client veut remplacer seulement la carte mère et le processeur de son PC de "
            "bureau, et garder ses barrettes de mémoire pour limiter la dépense. Avant de "
            "valider le devis, tu relèves les fiches (document 1, fictives)."
        ),
        documents=(
            _table(
                "Document 1 — Fiches (fictives)",
                ("Pièce", "Caractéristiques"),
                ("Mémoire actuelle", "2 × 16 Go DIMM DDR4-3200"),
                ("Nouveau processeur", "socket AM5"),
                ("Nouvelle carte mère", "socket AM5, 4 × DIMM DDR5, ATX"),
                ("Boîtier actuel", "accepte ATX, microATX, Mini-ITX"),
            ),
        ),
        instructions=("Dis si la mise à niveau est possible telle quelle et justifie ; propose la correction du devis.",),
        criteria=(
            _c("Diagnostic", 1, "Processeur et carte en AM5 : conformes ; boîtier conforme ; mais la carte n'accepte que la DDR5 : la DDR4 ne s'insère pas (encoche différente)."),
            _c("Correction", 1, "Ajouter 2 × 16 Go DIMM DDR5 au devis (ou rester sur une plateforme DDR4) ; vérifier la liste des processeurs et le firmware de la carte."),
        ),
        correction=(
            "Le socket est identique (AM5) et le boîtier accepte l'ATX : ces points sont conformes. La mémoire ne l'est pas : la carte AM5 n'accepte que la DDR5, et une barrette DDR4 ne peut pas s'y insérer (encoche-détrompeur à un autre endroit). Il faut ajouter au devis deux barrettes DIMM DDR5, ou choisir une plateforme qui garde la DDR4. Vérifier aussi que le processeur figure dans la liste de la carte, avec la version de firmware requise.",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Expliquer un SSD M.2 non détecté",
        question_type="short_answer",
        requirement_ids=("AP-06", "AP-17"),
        kind=KIND_COMPAT,
        context=(
            "Un SSD M.2 2280 à deux encoches (clé B+M), d'interface SATA, est installé dans le "
            "seul emplacement M.2 d'une carte mère. Le manuel indique pour cet emplacement : "
            "« clé M, PCIe 4.0 x4, NVMe uniquement ». Le SSD n'est vu ni par le firmware ni par "
            "le système."
        ),
        instructions=("Explique la cause et propose deux solutions.",),
        criteria=(
            _c("Cause", 1, "La forme permet l'insertion, mais l'emplacement ne gère que le NVMe : un SSD M.2 SATA n'y est pas pris en charge."),
            _c("Solutions", 1, "Échanger contre un SSD M.2 NVMe ; ou utiliser un SSD SATA 2,5 pouces sur un port SATA (câbles de données et d'alimentation)."),
        ),
        correction=(
            "Même forme ne veut pas dire même interface : la clé B+M entre dans un emplacement à clé M, mais celui-ci ne gère que le NVMe ; le SSD SATA n'est pas reconnu. Solutions : échanger contre un SSD M.2 NVMe (plus rapide) ; ou garder le SATA sous forme de SSD 2,5 pouces relié par un câble de données SATA et une alimentation SATA.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Écran limité à 30 Hz en 4K",
        question_type="short_answer",
        requirement_ids=("AP-06",),
        kind=KIND_COMPAT,
        context=(
            "Un écran 4K à 60 Hz est relié à un PC par HDMI. La carte graphique et l'écran ont "
            "des ports HDMI 2.0, mais l'affichage reste à 30 Hz. Le câble utilisé est un ancien "
            "câble « High Speed », prévu pour le HDMI 1.4 (10,2 Gbit/s)."
        ),
        instructions=("Explique la limite et propose une solution.",),
        criteria=(
            _c("Cause", 1, "Le câble n'assure que le débit du HDMI 1.4 : 4K à 30 Hz au plus ; les ports ne sont pas en cause."),
            _c("Solution", 1, "Câble HDMI « Premium High Speed » (18 Gbit/s, HDMI 2.0) ou plus récent, ou liaison DisplayPort si les deux appareils en ont."),
        ),
        correction=(
            "Le HDMI 2.0 permet la 4K à 60 Hz (18 Gbit/s), mais le câble ne garantit que 10,2 Gbit/s : la liaison est limitée à la 4K à 30 Hz. Solution : un câble certifié « Premium High Speed » (HDMI 2.0) ou « Ultra High Speed » (HDMI 2.1), ou un câble DisplayPort si la carte et l'écran en ont.",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Un câble « CPU » sur la carte graphique",
        question_type="short_answer",
        requirement_ids=("AP-06", "AP-04"),
        kind=KIND_WIRING,
        context=(
            "En relisant le montage d'un stagiaire, tu constates qu'il a essayé de brancher un "
            "câble 8 broches marqué « CPU » sur la carte graphique, faute de câble PCIe. Il a "
            "« un peu forcé » mais n'a pas encore allumé le PC."
        ),
        instructions=("Explique le risque et la conduite à tenir.",),
        criteria=(
            _c("Risque", 1, "EPS et PCIe 8 broches ont des tensions placées autrement et des détrompeurs différents : forcer peut mettre le +12 V sur une masse, court-circuit, destruction de la carte ou du bloc."),
            _c("Conduite", 1, "Ne pas allumer ; PC débranché, retirer le câble, contrôler les connecteurs (broches, plastique) ; brancher un vrai câble PCIe du bloc, sinon changer de bloc ; jamais forcer."),
        ),
        correction=(
            "L'EPS « CPU » et le PCIe 8 broches ne s'échangent pas : l'EPS a ses quatre +12 V sur une rangée, le PCIe trois +12 V placés autrement, et les détrompeurs sont différents. Forcé, le câble peut relier le +12 V à une masse : court-circuit, carte graphique ou bloc détruits. Ne pas allumer ; PC débranché, retirer le câble, inspecter les deux connecteurs ; brancher un câble PCIe du bloc ou, s'il n'en a pas assez, choisir un bloc adapté.",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="Mettre un PC hors tension avant d'intervenir",
        question_type="long_answer",
        requirement_ids=("AP-C02", "AP-04"),
        kind=KIND_SAFETY,
        context=(
            "Tu dois remplacer une carte d'extension dans un PC de bureau resté branché, écran "
            "éteint. Un collègue te dit : « Pas besoin de débrancher, il est éteint ; et si le "
            "bloc fait un bruit bizarre, ouvre-le pour regarder. »"
        ),
        instructions=(
            "Rédige la mise hors tension correcte et justifie chaque étape.",
            "Réponds au conseil d'ouvrir le bloc.",
        ),
        criteria=(
            _c("Mise hors tension", 1.2, "Arrêt du système ; interrupteur du bloc sur 0 ; câble secteur débranché, car le +5 VSB reste présent PC éteint ; appui sur le bouton pour décharger ; bracelet antistatique au châssis."),
            _c("Bloc", 0.8, "Jamais ouvrir un bloc : condensateurs chargés à une tension dangereuse même débranché ; un bloc suspect se teste et se remplace."),
        ),
        correction=(
            "1. Arrêter le système proprement. 2. Mettre l'interrupteur du bloc sur 0 et débrancher le câble secteur : un PC « éteint » mais branché garde le +5 VSB sur la carte mère (veille, réveil, LED). 3. Appuyer quelques secondes sur le bouton de démarrage pour vider l'énergie résiduelle. 4. Mettre un bracelet antistatique relié au châssis avant de toucher les cartes.",
            "On n'ouvre jamais un bloc d'alimentation : ses condensateurs restent chargés à plusieurs centaines de volts longtemps après le débranchement. Un bloc bruyant ou suspect se teste (testeur, bloc connu bon) et se remplace.",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Choisir un onduleur pour un petit serveur",
        question_type="document_analysis",
        requirement_ids=("AP-04",),
        kind=KIND_CALC,
        context=(
            "Un petit bureau veut protéger son serveur de fichiers et son switch contre les "
            "coupures de courant courtes, le temps d'un arrêt propre. Ensemble, ils consomment "
            "au plus 300 W. Tu compares trois onduleurs (document 1, fictifs)."
        ),
        documents=(
            _table(
                "Document 1 — Onduleurs proposés (fictifs)",
                ("Modèle", "Puissance apparente", "Puissance active", "Autonomie à 300 W"),
                ("U1", "500 VA", "300 W", "2 min"),
                ("U2", "1000 VA", "600 W", "12 min"),
                ("U3", "650 VA", "390 W", "4 min"),
            ),
        ),
        instructions=("Choisis l'onduleur en justifiant par la puissance active, la marge et l'autonomie.",),
        criteria=(
            _c("Critère", 1, "Comparer la puissance active (W), pas seulement les VA ; garder une marge."),
            _c("Choix", 1, "U2 : 600 W pour 300 W (50 % de charge), 12 min pour un arrêt propre ; U1 à 100 %, U3 sans marge suffisante et autonomie courte."),
        ),
        correction=(
            "On compare la puissance active en watts (les VA ne suffisent pas) et on garde une marge. U1 serait à 100 % de charge, 2 minutes d'autonomie : trop juste. U3 serait chargé à environ 77 %, 4 minutes. U2 (600 W, 50 % de charge, 12 minutes) laisse le temps de déclencher un arrêt propre du serveur : c'est le bon choix.",
        ),
    ),
)

ALL_ITEMS: tuple[PR06Item, ...] = PRACTICE_ITEMS + EXAM_ITEMS
EXAM_TOTAL_POINTS = 20


def validate_items() -> list[str]:
    """Contrôles éditoriaux : format d'exercice du socle (#192), 2 points par question du
    mini-examen, réponses libres à l'examen, données des classements et remises en ordre,
    exigence officielle du cours citée."""
    errors: list[str] = []
    for item in ALL_ITEMS:
        errors += [f"{item.key} : {e}" for e in validate_exercise(item.as_exercise())]
        if item.question_type == "classification" and (
            item.classification is None
            or len(item.classification.correct) != len(item.classification.elements)
            or len(set(item.classification.elements)) != len(item.classification.elements)
            or max(item.classification.correct) >= len(item.classification.categories)
        ):
            errors.append(f"{item.key} : classification incohérente.")
        if item.question_type == "ordering" and (
            item.ordering is None
            or sorted(item.ordering.correct) != list(range(len(item.ordering.steps)))
            or list(item.ordering.correct) == list(range(len(item.ordering.steps)))
        ):
            errors.append(f"{item.key} : remise en ordre invalide ou déjà dans l'ordre attendu.")
        if item.question_type == "document_analysis" and not item.documents:
            errors.append(f"{item.key} : analyse de document sans document.")
        if not REQ & set(item.requirement_ids):
            errors.append(f"{item.key} : au moins une exigence officielle du cours doit être citée.")
    for item in EXAM_ITEMS:
        if abs(item.total_points - 2) > 1e-9:
            errors.append(f"{item.key} : une question du mini-examen vaut 2 points.")
        if item.question_type not in ("short_answer", "long_answer", "document_analysis"):
            errors.append(f"{item.key} : le mini-examen n'accepte que des réponses libres.")
    return errors

