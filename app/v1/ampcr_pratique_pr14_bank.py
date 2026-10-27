"""PR14 « Débits, distances, atténuation et impédance » — exercices corrigés et mini-examen
(ticket #217).

Même organisation que PR13 (`app.v1.ampcr_pratique_pr13_bank`) : type d'item de PR06, petits
constructeurs de PR04.
- `PRACTICE_ITEMS` : 19 exercices corrigés affichés dans le cours (corrigé replié) et proposés
  dans « S'entraîner » — remises en ordre (durée d'une copie, liaison à 100 Mb/s, bilan
  optique), classements (norme, catégorie et longueur ; décibels ; auto-négociation ; support à
  10 Gb/s ; réflexions), documents chiffrés (durée, débit mesuré, `ethtool`, rapport de
  testeur, bilan optique, segments coaxiaux), rédactions ;
- `EXAM_ITEMS` : les 10 questions du mini-examen noté /20 (2 points chacune), réponses libres,
  uniquement dans « Examen blanc », jamais affichées dans le cours.

Les situations sont **fictives** ; tous les nombres des énoncés, barèmes et corrigés viennent des
fonctions de `app.v1.ampcr_pratique_pr14_figures` (mêmes données que les schémas).
"""

from app.v1.ampcr_pratique_format import validate_exercise
from app.v1.ampcr_pratique_pr04_bank import _c, _console, _labels, _shuffled_ordering, _table
from app.v1.ampcr_pratique_pr06_bank import (
    USAGE_EXAM,
    USAGE_PRACTICE,
    Classification,
    PR06Item,
)
from app.v1.ampcr_pratique_pr14_figures import (
    COAX_SEGMENT_MAX_DB,
    CONNECTOR_PAIR_DB,
    COPPER_VERDICTS,
    FIBRE_STEPS,
    FULL,
    HALF,
    LINK_STEPS,
    MEDIA_10G,
    NEGOTIATION_RESULTS,
    REFLECTION_KINDS,
    SPLICE_DB,
    TCP_EFFICIENCY,
    TRANSFER_STEPS,
    FibreLink,
    Port,
    acr_db,
    cable_loss_db,
    choose_10g,
    copper_verdict,
    duration_fr,
    fibre_errors,
    fr,
    fraction_after,
    link_result,
    mw,
    negotiate,
    pct,
    rate_bps,
    reflected_power_pct,
    reflection_coefficient,
    reflection_kind,
    return_loss_db,
    to_bits,
    transfer_time_s,
)
from app.v1.ampcr_pratique_pr15_figures import PERMANENT_LINK_MAX_M
from app.v1.ampcr_pratique_pr16_figures import THICK_SEGMENT_MAX_M, THIN_SEGMENT_MAX_M

PR14_CODE = "PR14"

KIND_ORDER = "ordonnancement"
KIND_RATE = "débits et durées"
KIND_DISTANCE = "normes et distances"
KIND_SIGNAL = "atténuation, bruit, impédance"
KIND_FIBRE = "fibre optique"
KIND_LINK = "duplex et négociation"

# Exigences du cours (matrice #192, audit #236) : chaque item en cite au moins une.
REQ = frozenset({"AP-19", "AP-20"})

# --- Données calculées réutilisées dans les énoncés et les corrigés --------------------------

E01_STEPS = _labels(TRANSFER_STEPS)
E02_STEPS = _labels(LINK_STEPS)
E03_STEPS = _labels(FIBRE_STEPS)

E04_CASES: tuple[tuple[str, str, float], ...] = (
    ("1000BASE-T", "Cat5e", 85),
    ("10GBASE-T", "Cat6A", 95),
    ("10GBASE-T", "Cat6", 45),
    ("10GBASE-T", "Cat6", 80),
    ("10GBASE-T", "Cat5e", 30),
    ("1000BASE-T", "Cat6A", 120),
    ("100BASE-TX", "Cat5e", 98),
    ("1000BASE-T", "Cat3", 40),
)
_RATE_OF = {"10BASE-T": "10 Mb/s", "100BASE-TX": "100 Mb/s", "1000BASE-T": "1 Gb/s", "10GBASE-T": "10 Gb/s"}
E04_ELEMENTS = tuple(f"{_RATE_OF[s]} ({s}), câble {c}, canal de {fr(m)} m" for s, c, m in E04_CASES)
E04_CORRECT = tuple(COPPER_VERDICTS.index(copper_verdict(s, c, m)) for s, c, m in E04_CASES)

E05_FRACTIONS: tuple[tuple[str, float], ...] = (
    ("La moitié", 0.5), ("Le quart", 0.25), ("Un dixième", 0.1), ("Un centième", 0.01), ("Un millième", 0.001),
)
E05_CATEGORIES = tuple(name for name, _f in E05_FRACTIONS)
E05_ELEMENTS: tuple[tuple[str, float], ...] = (
    ("Affaiblissement de 10 dB", 10),
    ("Affaiblissement de 3 dB", 3),
    ("Affaiblissement de 20 dB", 20),
    ("Affaiblissement de 6 dB", 6),
    ("Affaiblissement de 30 dB", 30),
    ("Deux tronçons de 10 dB chacun, l'un après l'autre", 10 + 10),
    ("Un connecteur de 3 dB puis un câble de 7 dB", 3 + 7),
)


def _nearest_fraction(loss: float) -> int:
    remaining = fraction_after(loss)
    index = min(range(len(E05_FRACTIONS)), key=lambda i: abs(E05_FRACTIONS[i][1] - remaining) / E05_FRACTIONS[i][1])
    if abs(E05_FRACTIONS[index][1] - remaining) / E05_FRACTIONS[index][1] > 0.03:
        raise ValueError(f"{loss} dB : aucune fraction simple à 3 % près.")
    return index


E05_CORRECT = tuple(_nearest_fraction(loss) for _e, loss in E05_ELEMENTS)

# (description, PC, switch, 4 paires en bon état)
E06_CASES: tuple[tuple[str, Port, Port, bool], ...] = (
    ("PC et switch Gigabit en auto-négociation, câble Cat6 testé conforme", Port(), Port(), True),
    ("PC et switch Gigabit en auto-négociation, paire 7-8 coupée dans la prise murale", Port(), Port(), False),
    ("PC en auto-négociation, port du switch forcé à 100 Mb/s full duplex", Port(),
     Port(auto=False, speed=100, duplex=FULL), True),
    ("PC et port du switch tous deux forcés à 100 Mb/s full duplex", Port(auto=False, speed=100, duplex=FULL),
     Port(auto=False, speed=100, duplex=FULL), True),
    ("PC Gigabit en auto-négociation sur un ancien switch 100 Mb/s en auto-négociation", Port(),
     Port(max_speed=100), True),
    ("PC forcé à 10 Mb/s half duplex, port du switch forcé à 100 Mb/s full duplex",
     Port(auto=False, speed=10, duplex=HALF), Port(auto=False, speed=100, duplex=FULL), True),
    ("PC forcé à 100 Mb/s full duplex, port du switch forcé à 100 Mb/s half duplex",
     Port(auto=False, speed=100, duplex=FULL), Port(auto=False, speed=100, duplex=HALF), True),
)
E06_CORRECT = tuple(NEGOTIATION_RESULTS.index(link_result(negotiate(a, b, four_pairs_ok=ok)))
                    for _t, a, b, ok in E06_CASES)

# (description, longueur, entre deux bâtiments)
E07_CASES: tuple[tuple[str, float, bool], ...] = (
    ("Serveur vers le switch de la même salle, 70 m de chemin de câbles", 70, False),
    ("Switch du bâtiment A vers celui du bâtiment B, 90 m en gaine enterrée", 90, True),
    ("Baie du rez-de-chaussée vers celle du 4e étage, 140 m", 140, False),
    ("Atelier vers bureaux du même site, 250 m", 250, False),
    ("Entrepôt vers bureaux du même site, 360 m", 360, False),
    ("Siège vers un dépôt à 1,8 km, fibre noire louée", 1800, True),
    ("Deux sites d'une commune reliés par une fibre de 8 km", 8000, True),
)
E07_CORRECT = tuple(MEDIA_10G.index(choose_10g(m, between_buildings=b)) for _t, m, b in E07_CASES)

# (situation, impédance de la ligne, charge ou None si ouverte)
E08_CASES: tuple[tuple[str, int, float | None], ...] = (
    ("Bus 10BASE2 en RG-58 fermé par un terminateur 50 Ω", 50, 50),
    ("Bus RG-58 dont le terminateur a été retiré", 50, None),
    ("Câble RG-59 (75 Ω) fermé par un terminateur 50 Ω récupéré", 75, 50),
    ("RG-59 vers l'entrée vidéo 75 Ω d'un enregistreur", 75, 75),
    ("Coaxial 50 Ω dont l'âme touche la tresse au bout du câble", 50, 0),
    ("Paire torsadée 100 Ω prolongée par un ancien câble IBM 150 Ω", 100, 150),
    ("RG-58 (50 Ω) branché sur une caméra 75 Ω", 50, 75),
)
E08_CORRECT = tuple(REFLECTION_KINDS.index(reflection_kind(reflection_coefficient(z, line)))
                    for _t, line, z in E08_CASES)

E09_SIZE_GO = 18
E09_EFF = 0.9
E09_BITS = to_bits(E09_SIZE_GO, "Go")
E09_T_GIGA = transfer_time_s(E09_BITS, rate_bps(1, "Gb/s"), E09_EFF)
E09_T_FAST = transfer_time_s(E09_BITS, rate_bps(100, "Mb/s"), E09_EFF)

E10_SIZE_GIO = 4.5
E10_SECONDS = 7 * 60 + 30
E10_BITS = to_bits(E10_SIZE_GIO, "Gio")
E10_MEASURED_MBPS = E10_BITS / E10_SECONDS / 1e6
E10_WRONG_MBPS = to_bits(E10_SIZE_GIO, "Go") / E10_SECONDS / 1e6
E10_GIGA_MAX_MBPS = 1000 * TCP_EFFICIENCY

E12_IL_LIMIT = 31.1
E12_NEXT_LIMIT = 35.3
E12_ROWS: tuple[tuple[str, float, float, float], ...] = (
    ("B1-P1-01", 42, 13.6, 41.0),
    ("B1-P1-02", 88, 28.4, 37.2),
    ("B1-P1-03", 61, 19.8, 30.9),
    ("B1-P1-04", 97, 31.6, 36.0),
)


def e12_faults(length: float, il: float, next_db: float) -> list[str]:
    faults: list[str] = []
    if length > PERMANENT_LINK_MAX_M:
        faults.append("longueur")
    if il > E12_IL_LIMIT:
        faults.append("affaiblissement")
    if next_db < E12_NEXT_LIMIT:
        faults.append("NEXT")
    return faults


E12_FAULTS = {port: e12_faults(length, il, nx) for port, length, il, nx in E12_ROWS}
E12_ACR_02 = acr_db(37.2, 28.4)

E13_LINK = FibreLink("siège → dépôt, OS2, 1310 nm", "10GBASE-LR", "OS2", 1310, 6000, 2, 3, 6.2)
E13_MARGIN_REQUIRED = 3.0

E14_THIN_DB_PER_100M = 4.6
E14_THICK_DB_PER_100M = 1.7
E14_THIN_M = 210
E14_THICK_M = 480
E14_THIN_LOSS = cable_loss_db(E14_THIN_M, E14_THIN_DB_PER_100M)
E14_THICK_LOSS = cable_loss_db(E14_THICK_M, E14_THICK_DB_PER_100M)

E15_MAX_MO_S = 1e9 / 8 / 1e6
E15_USEFUL_MO_S = E15_MAX_MO_S * TCP_EFFICIENCY
E15_USEFUL_MIO_S = E15_USEFUL_MO_S * 1e6 / 2**20

X01_BITS = to_bits(2.4, "Go")
X01_T = transfer_time_s(X01_BITS, rate_bps(100, "Mb/s"), 0.9)
X02_MAX_MO_S = rate_bps(500, "Mb/s") / 8 / 1e6
X05_OUT_MW = 20 * fraction_after(13)
X06_LINK = FibreLink("bâtiment A → bâtiment C, OS2, 1310 nm", "10GBASE-LR", "OS2", 1310, 3500, 2, 2, 6.2)
X09_GAMMA = reflection_coefficient(75, 50)
X09_RL = return_loss_db(X09_GAMMA)

# =============================================================================================
# 19 exercices corrigés (cours + « S'entraîner »)
# =============================================================================================

PRACTICE_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="E01",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre le calcul d'une durée de copie",
        question_type="ordering",
        requirement_ids=("AP-19",),
        kind=KIND_ORDER,
        context=(
            "Une cliente veut savoir combien de temps prendra la copie de ses photos vers le NAS "
            "du bureau. Ton collègue a noté les six étapes du calcul sur un post-it, mais dans le "
            "désordre, et il a oublié d'écrire les unités à chaque étape."
        ),
        instructions=("Remets les six étapes du calcul dans l'ordre.",),
        criteria=(
            _c("Ordre", 3, "Taille en bits → débit en b/s → débit utile → diviser → convertir → vérifier (0,5 pt par étape)."),
        ),
        correction=(
            "1. On convertit la taille en bits (octets × 8, en tenant compte du préfixe décimal ou binaire). 2. On convertit le débit nominal en bits par seconde (1 Gb/s = 10⁹ b/s). 3. On applique le rendement : le débit utile est plus bas que le nominal (en-têtes, disques).",
            "4. Durée = taille en bits / débit utile en b/s. 5. On convertit les secondes en minutes et heures, avec l'unité écrite. 6. On vérifie l'ordre de grandeur et, si possible, on compare à une copie réelle.",
        ),
        ordering=_shuffled_ordering(E01_STEPS, (3, 0, 5, 2, 4, 1)),
    ),
    PR06Item(
        key="E02",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre le diagnostic d'une liaison à 100 Mb/s",
        question_type="ordering",
        requirement_ids=("AP-19", "AP-20"),
        kind=KIND_ORDER,
        context=(
            "Dans une agence de voyages, le PC du comptable affiche une connexion à 100 Mb/s alors "
            "que sa carte et le switch sont Gigabit. La fiche de diagnostic de l'atelier a ses six "
            "étapes mélangées ; tu dois la remettre en ordre avant de l'envoyer au stagiaire."
        ),
        instructions=("Remets les six étapes du diagnostic dans l'ordre, de la plus simple à la plus longue.",),
        criteria=(
            _c("Ordre", 3, "Relever → configuration → capacités → câble → isoler → contrôler et consigner (0,5 pt par étape)."),
        ),
        correction=(
            "1. On relève la vitesse et le duplex des deux côtés (carte et port du switch) et les compteurs d'erreurs. 2. On vérifie la configuration : auto-négociation des deux côtés, rien de forcé d'un seul côté. 3. On vérifie les capacités de chaque maillon : carte, switch, et tout appareil intermédiaire (téléphone IP, ancien switch).",
            "4. On teste le câble : les 8 conducteurs (le Gigabit utilise les 4 paires), la longueur, la catégorie. 5. On isole le maillon fautif en changeant le cordon, puis le port. 6. On contrôle 1 Gb/s full duplex des deux côtés, des compteurs stables, et on consigne.",
        ),
        ordering=_shuffled_ordering(E02_STEPS, (2, 5, 0, 3, 1, 4)),
    ),
    PR06Item(
        key="E03",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre le bilan d'une liaison optique",
        question_type="ordering",
        requirement_ids=("AP-20", "AP-21"),
        kind=KIND_ORDER,
        context=(
            "Une commune veut relier la bibliothèque à la maison communale par une fibre. Avant "
            "de commander les modules optiques, ton responsable te demande un bilan écrit. Les six "
            "étapes du modèle de bilan ont été recopiées dans le désordre."
        ),
        instructions=("Remets les six étapes du bilan dans l'ordre.",),
        criteria=(
            _c("Ordre", 3, "Relever → valeurs → calculer la perte → portée et budget → marge → conclure et mesurer (0,5 pt par étape)."),
        ),
        correction=(
            "1. On relève la longueur, le type de fibre, la longueur d'onde, le nombre de connecteurs et d'épissures. 2. On prend les valeurs d'affaiblissement : dB/km de la fibre, 0,75 dB par paire de connecteurs, 0,3 dB par épissure. 3. On calcule la perte : fibre + connecteurs + épissures.",
            "4. On vérifie la portée du module sur ce type de fibre et on relève son budget sur la fiche technique. 5. Marge = budget − perte, comparée à la marge demandée. 6. On conclut par écrit, puis on mesure la liaison réelle (photomètre ou réflectomètre).",
        ),
        ordering=_shuffled_ordering(E03_STEPS, (4, 1, 3, 0, 5, 2)),
    ),
    PR06Item(
        key="E04",
        usage=USAGE_PRACTICE,
        title="Huit liaisons cuivre : la catégorie et la longueur conviennent-elles ?",
        question_type="classification",
        requirement_ids=("AP-19", "AP-20"),
        kind=KIND_DISTANCE,
        context=(
            "Tu relis les devis de câblage préparés par un collègue. Pour chaque liaison, il a noté "
            "le débit voulu, la catégorie de câble prévue et la longueur du canal (cordons compris). "
            "Règles : canal de 100 m au plus ; 1 Gb/s demande au moins du Cat5e ; 10 Gb/s du Cat6A, "
            "ou du Cat6 jusqu'à 55 m après certification."
        ),
        instructions=("Range chaque liaison selon le verdict qui convient.",),
        criteria=(
            _c("Classement", 4, "85 m Cat5e 1 Gb/s, 95 m Cat6A 10 Gb/s, 98 m Cat5e 100 Mb/s → conformes ; Cat6 45 m 10 Gb/s → sous conditions ; Cat6 80 m et Cat5e à 10 Gb/s, Cat3 à 1 Gb/s → catégorie insuffisante ; 120 m → trop long (0,5 pt par élément)."),
        ),
        correction=(
            "On regarde d'abord la longueur : au-delà de 100 m de canal, aucune catégorie ne convient (120 m → fibre ou équipement intermédiaire). Ensuite la catégorie : Cat5e pour 1 Gb/s sur 100 m, Cat6A pour 10 Gb/s sur 100 m ; une catégorie supérieure convient toujours (Cat5e pour 100 Mb/s).",
            "Le Cat6 ne tient 10 Gb/s que sur une longueur réduite : 55 m au plus, 37 m s'il y a beaucoup de câbles voisins ; à 45 m, c'est possible après certification du lien ; à 80 m, il faut du Cat6A. Le Cat5e n'est pas prévu pour 10 Gb/s, et un ancien câblage téléphonique Cat3 ne tient que 10 Mb/s.",
        ),
        classification=Classification(categories=COPPER_VERDICTS, elements=E04_ELEMENTS, correct=E04_CORRECT),
    ),
    PR06Item(
        key="E05",
        usage=USAGE_PRACTICE,
        title="Décibels : quelle part de la puissance reste-t-il ?",
        question_type="classification",
        requirement_ids=("AP-20",),
        kind=KIND_SIGNAL,
        context=(
            "Pour préparer un stagiaire aux rapports de testeur, tu lui fais estimer de tête la "
            "puissance qui reste après un affaiblissement. Règles à utiliser : 3 dB divisent la "
            "puissance par 2, 10 dB la divisent par 10, et les dB de tronçons successifs "
            "s'additionnent."
        ),
        instructions=("Range chaque affaiblissement selon la part de la puissance d'entrée qui arrive au bout.",),
        criteria=(
            _c("Classement", 3.5, "3 dB → la moitié ; 6 dB → le quart ; 10 dB et 3 + 7 dB → un dixième ; 20 dB et 10 + 10 dB → un centième ; 30 dB → un millième (0,5 pt par élément)."),
        ),
        correction=(
            "Affaiblissement en dB = 10 × log10(Pentrée / Psortie). 10 dB = rapport 10, 20 dB = 100, 30 dB = 1 000 : il reste un dixième, un centième, un millième. 3 dB ≈ rapport 2 (10^0,3 ≈ 2) : il reste la moitié ; 6 dB = 3 + 3 dB : la moitié de la moitié, le quart.",
            "Les dB s'additionnent : deux tronçons de 10 dB font 20 dB (un centième) ; un connecteur de 3 dB suivi d'un câble de 7 dB font 10 dB (un dixième). On n'additionne jamais des pourcentages ni des milliwatts perdus.",
        ),
        classification=Classification(
            categories=E05_CATEGORIES, elements=tuple(e for e, _l in E05_ELEMENTS), correct=E05_CORRECT,
        ),
    ),
    PR06Item(
        key="E06",
        usage=USAGE_PRACTICE,
        title="Auto-négociation : quel résultat pour chaque liaison ?",
        question_type="classification",
        requirement_ids=("AP-19", "AP-20"),
        kind=KIND_LINK,
        context=(
            "Un client se plaint de lenteurs sur plusieurs postes. Tu as relevé, pour sept "
            "liaisons, le réglage de la carte du PC et du port du switch, et l'état du câble. Rappel : "
            "un port en auto-négociation face à un port forcé détecte la vitesse, mais se met en "
            "half duplex."
        ),
        instructions=("Range chaque liaison selon l'état qu'elle obtiendra.",),
        criteria=(
            _c("Classement", 3.5, "Auto/auto conforme → 1 Gb/s full ; paire 7-8 coupée, forcés 100 full des deux côtés, ancien switch 100 Mb/s → 100 Mb/s full ; auto face à forcé 100 full, forcé full face à forcé half → désaccord de duplex ; 10 face à 100 forcés → pas de lien (0,5 pt par élément)."),
        ),
        correction=(
            "Deux ports en auto-négociation choisissent la meilleure vitesse commune en full duplex : 1 Gb/s si les quatre paires sont bonnes et si les deux équipements sont Gigabit, sinon 100 Mb/s (un ancien switch 100 Mb/s, ou une paire 4-5 ou 7-8 coupée : la carte rétrograde). Deux ports forcés de la même façon fonctionnent aussi.",
            "Un port en auto face à un port forcé détecte la vitesse mais pas le duplex : il passe en half duplex, l'autre reste en full : désaccord de duplex (collisions tardives, erreurs CRC, lenteurs). Deux ports forcés à des duplex différents donnent le même désaccord ; à des vitesses différentes (10 et 100 Mb/s), il n'y a pas de lien.",
        ),
        classification=Classification(
            categories=NEGOTIATION_RESULTS, elements=tuple(t for t, *_r in E06_CASES), correct=E06_CORRECT,
        ),
    ),
    PR06Item(
        key="E07",
        usage=USAGE_PRACTICE,
        title="Liaisons à 10 Gb/s : quel support et quel module ?",
        question_type="classification",
        requirement_ids=("AP-19", "AP-21"),
        kind=KIND_FIBRE,
        context=(
            "Une intercommunale prépare sept liaisons à 10 Gb/s. La règle de l'atelier : la solution "
            "la plus simple qui tient la distance, jamais de cuivre entre deux bâtiments. Portées : "
            "10GBASE-T 100 m sur Cat6A ; 10GBASE-SR 300 m sur OM3 et 400 m sur OM4 ; 10GBASE-LR "
            "10 km sur monomode OS2."
        ),
        instructions=("Range chaque liaison selon le support et le module à prévoir.",),
        criteria=(
            _c("Classement", 3.5, "70 m même salle → Cat6A ; 90 m entre bâtiments, 140 m et 250 m → SR sur OM3 ; 360 m → SR sur OM4 ; 1,8 km et 8 km → LR sur OS2 (0,5 pt par élément)."),
        ),
        correction=(
            "Jusqu'à 100 m dans un même bâtiment, le cuivre Cat6A suffit. Entre deux bâtiments, même à 90 m, on passe à la fibre : elle ne conduit pas l'électricité (terres différentes, foudre). En multimode, la portée dépend du module et de la fibre : 10GBASE-SR tient 300 m sur OM3 (140 m et 250 m) et 400 m sur OM4 (360 m).",
            "Au-delà, il faut du monomode avec un module longue portée : 10GBASE-LR tient 10 km sur OS2 (1,8 km et 8 km). Le choix se justifie toujours par la portée du module sur la fibre réellement posée, puis par un bilan de pertes.",
        ),
        classification=Classification(
            categories=MEDIA_10G, elements=tuple(t for t, *_r in E07_CASES), correct=E07_CORRECT,
        ),
    ),
    PR06Item(
        key="E08",
        usage=USAGE_PRACTICE,
        title="Impédance : réflexion ou pas ?",
        question_type="classification",
        requirement_ids=("AP-20",),
        kind=KIND_SIGNAL,
        context=(
            "Dans le laboratoire de formation, sept montages coaxiaux et cuivre sont étiquetés. "
            "Avant de les présenter aux élèves, tu dois dire pour chacun ce qui arrive au signal au "
            "bout de la ligne, avec Γ = (Zcharge − Zligne) / (Zcharge + Zligne)."
        ),
        instructions=("Range chaque montage selon le type de réflexion à l'extrémité.",),
        criteria=(
            _c("Classement", 3.5, "50 sur 50 Ω et 75 sur 75 Ω → adaptée ; terminateur retiré → totale, même signe ; âme sur tresse → totale inversée ; 75 Ω sur 50 Ω, 50 Ω sur 75 Ω, 100 Ω sur 150 Ω → partielle (0,5 pt par élément)."),
        ),
        correction=(
            "Une ligne fermée sur sa propre impédance (50 Ω sur 50 Ω, 75 Ω sur 75 Ω) ne réfléchit rien : Γ = 0. Sans terminateur, l'extrémité est ouverte : Γ = +1, tout revient avec le même signe ; si l'âme touche la tresse, c'est un court-circuit : Γ = −1, tout revient inversé. Sur un bus 10BASE2, ces deux défauts bloquent tout le segment.",
            f"Entre deux impédances différentes, une partie revient : 75 Ω sur 50 Ω donne Γ = {fr(reflection_coefficient(50, 75), 2)}, 50 Ω sur 75 Ω Γ = +{fr(reflection_coefficient(75, 50), 2)} ({fr(reflected_power_pct(0.2), 1)} % de la puissance), 100 Ω sur 150 Ω Γ = +{fr(reflection_coefficient(150, 100), 2)}. D'où la règle : une seule impédance par liaison, câble et connecteurs compris.",
        ),
        classification=Classification(
            categories=REFLECTION_KINDS, elements=tuple(t for t, *_r in E08_CASES), correct=E08_CORRECT,
        ),
    ),
    PR06Item(
        key="E09",
        usage=USAGE_PRACTICE,
        title="Durée de copie d'une image disque",
        question_type="document_analysis",
        requirement_ids=("AP-19",),
        kind=KIND_RATE,
        context=(
            "Un garage veut faire chaque soir une image disque de son serveur vers un NAS. Le "
            "document 1 donne la taille de l'image et le rendement mesuré lors d'un essai. Le "
            "gérant hésite entre garder son ancien switch 100 Mb/s et acheter un switch Gigabit ; "
            "la sauvegarde doit tenir dans la fenêtre de nuit d'une heure."
        ),
        documents=(
            _table(
                "Document 1 — Données de la sauvegarde",
                ("Élément", "Valeur"),
                ("Taille de l'image disque", f"{E09_SIZE_GO} Go (décimal, indiqué par le logiciel)"),
                ("Rendement mesuré (débit utile / nominal)", pct(E09_EFF, 0)),
                ("Débits possibles", "100 Mb/s (switch actuel) ou 1 Gb/s (switch Gigabit)"),
                ("Fenêtre de sauvegarde", "1 h"),
            ),
        ),
        instructions=(
            "Calcule la durée de la copie à 100 Mb/s et à 1 Gb/s, unités écrites à chaque étape.",
            "Dis si chaque solution tient dans la fenêtre d'une heure et conseille le gérant.",
        ),
        criteria=(
            _c("Conversion", 1, f"{E09_SIZE_GO} Go × 10⁹ × 8 = {fr(E09_BITS / 1e9)} × 10⁹ bits ; débits utiles : {fr(0.9 * 100)} Mb/s et {fr(0.9 * 1000)} Mb/s."),
            _c("Durées", 1, f"100 Mb/s : {fr(E09_T_FAST)} s = {duration_fr(E09_T_FAST)} ; 1 Gb/s : {fr(E09_T_GIGA)} s = {duration_fr(E09_T_GIGA)}."),
            _c("Conseil", 1, "100 Mb/s : 26 min 40 s, tient dans 1 h mais sans marge pour une image qui grossit ; 1 Gb/s : moins de 3 min ; vérifier que le NAS et les disques suivent ; conseil justifié."),
        ),
        correction=(
            f"Taille : {E09_SIZE_GO} Go = {E09_SIZE_GO} × 10⁹ octets × 8 = {fr(E09_BITS / 1e9)} × 10⁹ bits. Débit utile = nominal × {pct(E09_EFF, 0)} : 90 Mb/s = 90 × 10⁶ b/s sur le switch actuel, 900 Mb/s sur un switch Gigabit.",
            f"À 100 Mb/s : {fr(E09_BITS / 1e9)} × 10⁹ / 90 × 10⁶ = {fr(E09_T_FAST)} s, soit {duration_fr(E09_T_FAST)} : la sauvegarde tient dans l'heure, mais la marge fondra si l'image grossit. À 1 Gb/s : {fr(E09_T_GIGA)} s, soit {duration_fr(E09_T_GIGA)}. Conseil : le switch Gigabit, en vérifiant que la carte du serveur, le NAS et ses disques suivent ce débit (sinon le gain sera moindre).",
        ),
    ),
    PR06Item(
        key="E10",
        usage=USAGE_PRACTICE,
        title="Débit mesuré d'une copie : Gio ou Go ?",
        question_type="document_analysis",
        requirement_ids=("AP-19",),
        kind=KIND_RATE,
        context=(
            "Un graphiste se plaint : « mon PC est en Gigabit, mais la copie de mon dossier vers le "
            "serveur est très lente ». Le document 1 reprend ce que Windows affiche et le temps "
            "chronométré. Windows écrit « Go » mais compte en gibioctets (1 Gio = 2³⁰ octets)."
        ),
        documents=(
            _table(
                "Document 1 — Relevé de la copie",
                ("Élément", "Valeur relevée"),
                ("Taille affichée par Windows", f"{fr(E10_SIZE_GIO)} Go (en réalité {fr(E10_SIZE_GIO)} Gio)"),
                ("Durée chronométrée", "7 min 30 s"),
                ("Carte réseau du PC", "Gigabit (10/100/1000)"),
            ),
        ),
        instructions=(
            "Calcule le débit utile réellement obtenu, en Mb/s.",
            "Compare-le au débit utile maximal d'un lien Gigabit et d'un lien à 100 Mb/s, puis propose ce qu'il faut vérifier.",
        ),
        criteria=(
            _c("Calcul", 1.5, f"{fr(E10_SIZE_GIO)} × 2³⁰ × 8 = {fr(E10_BITS / 1e9, 2)} × 10⁹ bits ; / 450 s = {fr(E10_MEASURED_MBPS)} Mb/s (et non {fr(E10_WRONG_MBPS)} Mb/s en oubliant le préfixe binaire)."),
            _c("Interprétation et contrôles", 1.5, f"Lien Gigabit : environ {fr(E10_GIGA_MAX_MBPS, 0)} Mb/s utiles au mieux ; {fr(E10_MEASURED_MBPS)} Mb/s ≈ {pct(E10_MEASURED_MBPS / 100, 0)} de 100 Mb/s : le lien est sans doute à 100 Mb/s ; vérifier la vitesse affichée des deux côtés, le câble (4 paires), le port, l'équipement intermédiaire."),
        ),
        correction=(
            f"Taille : {fr(E10_SIZE_GIO)} Gio = {fr(E10_SIZE_GIO)} × 1 073 741 824 octets ≈ {fr(E10_BITS / 8 / 1e9, 3)} × 10⁹ octets, soit {fr(E10_BITS / 1e9, 2)} × 10⁹ bits. Durée : 7 min 30 s = 450 s. Débit utile : {fr(E10_BITS / 1e9, 2)} × 10⁹ / 450 = {fr(E10_MEASURED_MBPS)} Mb/s. En prenant 4,5 × 10⁹ octets, on trouverait {fr(E10_WRONG_MBPS)} Mb/s : l'écart vient du préfixe binaire.",
            f"Sur un lien Gigabit, une copie TCP peut atteindre environ {pct(TCP_EFFICIENCY, 0)} du nominal, soit près de {fr(E10_GIGA_MAX_MBPS, 0)} Mb/s si les disques suivent. {fr(E10_MEASURED_MBPS)} Mb/s, c'est près du maximum d'un lien à 100 Mb/s : le lien a probablement été établi à 100 Mb/s. On vérifie la vitesse affichée sur la carte et sur le port du switch, puis le câble (les 4 paires) et les équipements intermédiaires.",
        ),
    ),
    PR06Item(
        key="E11",
        usage=USAGE_PRACTICE,
        title="Lire une sortie ethtool et un test de câble",
        question_type="document_analysis",
        requirement_ids=("AP-19", "AP-20"),
        kind=KIND_LINK,
        context=(
            "Un poste Linux d'un bureau d'études plafonne à 100 Mb/s depuis le déménagement des "
            "bureaux. Le document 1 est la sortie de la commande ethtool sur ce poste ; le "
            "document 2 le résultat du testeur de câblage sur le lien entre la prise murale et le "
            "panneau de brassage."
        ),
        documents=(
            _console(
                "Document 1 — Sortie de « ethtool enp3s0 » (extrait, capture fictive)",
                "Settings for enp3s0:",
                "        Advertised link modes:  10baseT/Half 10baseT/Full",
                "                                100baseT/Half 100baseT/Full",
                "                                1000baseT/Full",
                "        Link partner advertised link modes:  10baseT/Half 10baseT/Full",
                "                                             100baseT/Half 100baseT/Full",
                "                                             1000baseT/Full",
                "        Speed: 100Mb/s",
                "        Duplex: Full",
                "        Auto-negotiation: on",
                "        Link detected: yes",
            ),
            _table(
                "Document 2 — Testeur de câblage, lien bureau 14",
                ("Paire", "Résultat"),
                ("1-2", "OK, 38 m"),
                ("3-6", "OK, 38 m"),
                ("4-5", "OK, 38 m"),
                ("7-8", "Ouvert à 37 m (conducteur 8)"),
            ),
        ),
        instructions=(
            "Explique ce que montre chaque document.",
            "Donne la cause probable du 100 Mb/s, la correction et le contrôle final.",
        ),
        criteria=(
            _c("Lecture", 1.5, "Les deux côtés annoncent 1000baseT/Full, auto-négociation active, mais lien à 100 Mb/s full : ce n'est ni un réglage forcé ni un équipement limité ; le testeur montre la paire 7-8 ouverte près du panneau."),
            _c("Cause, correction, contrôle", 1.5, "Le Gigabit exige les 4 paires ; avec une paire coupée, la carte rétrograde à 100 Mb/s (2 paires) ; refaire le raccordement côté panneau (poinçonnage du conducteur 8), retester les 8 conducteurs, vérifier Speed: 1000Mb/s, consigner."),
        ),
        correction=(
            "Document 1 : la carte et le switch (« Link partner ») annoncent tous deux 1000baseT/Full et l'auto-négociation est active ; pourtant le lien est établi à 100 Mb/s en full duplex. Ce n'est donc ni un réglage forcé, ni un équipement limité à 100 Mb/s. Document 2 : la paire 7-8 est ouverte à 37 m, c'est-à-dire près du panneau (le lien mesure 38 m).",
            "Cause : 1000BASE-T utilise les quatre paires ; 100BASE-TX n'utilise que 1-2 et 3-6. Avec une paire coupée, les cartes rétrogradent à 100 Mb/s. Correction : refaire le poinçonnage du conducteur 8 sur le panneau (ou le keystone), retester les 8 conducteurs, puis vérifier « Speed: 1000Mb/s » dans ethtool et consigner le résultat.",
        ),
    ),
    PR06Item(
        key="E12",
        usage=USAGE_PRACTICE,
        title="Rapport de testeur : affaiblissement et NEXT",
        question_type="document_analysis",
        requirement_ids=("AP-20",),
        kind=KIND_SIGNAL,
        context=(
            "Tu réceptionnes quatre liens permanents Cat6 posés par un sous-traitant dans une école. "
            "Le document 1 est l'extrait du rapport du testeur : longueur, affaiblissement et "
            "paradiaphonie (NEXT) de la pire paire, avec les limites affichées par le testeur pour "
            "un lien permanent Cat6. Le lien permanent ne dépasse pas 90 m."
        ),
        documents=(
            _table(
                "Document 1 — Extrait du rapport (lien permanent Cat6, 250 MHz)",
                ("Lien", "Longueur (m)", "Affaiblissement (dB)", "NEXT pire paire (dB)"),
                *((port, fr(length), fr(il), fr(nx)) for port, length, il, nx in E12_ROWS),
                ("Limites du testeur", f"≤ {PERMANENT_LINK_MAX_M}", f"≤ {fr(E12_IL_LIMIT)}", f"≥ {fr(E12_NEXT_LIMIT)}"),
            ),
        ),
        instructions=(
            "Pour chaque lien, dis s'il est accepté et, sinon, la ou les valeurs hors limites.",
            "Pour chaque lien refusé, propose la cause probable et la correction ; calcule l'ACR du lien 02.",
        ),
        criteria=(
            _c("Verdicts", 1.5, "01 et 02 acceptés ; 03 refusé : NEXT 30,9 < 35,3 dB ; 04 refusé : 97 m > 90 m et affaiblissement 31,6 > 31,1 dB."),
            _c("Causes et corrections", 1, "03 : diaphonie au raccordement (détorsadage, prise mal poinçonnée ou écrasée) : refaire la terminaison et retester ; 04 : trop long, raccourcir le chemin ou déplacer la prise / l'équipement."),
            _c("ACR", 0.5, f"ACR = NEXT − affaiblissement = 37,2 − 28,4 = {fr(E12_ACR_02)} dB, positif : le signal reste au-dessus de la diaphonie."),
        ),
        correction=(
            "Un affaiblissement doit rester sous sa limite (moins de signal perdu), un NEXT au-dessus de la sienne (plus de dB = moins de diaphonie). 01 (42 m, 13,6 dB, 41,0 dB) et 02 (88 m, 28,4 dB, 37,2 dB) sont acceptés. 03 a un affaiblissement correct mais un NEXT de 30,9 dB, sous 35,3 dB : refusé. 04 mesure 97 m (plus de 90 m) et perd 31,6 dB (plus de 31,1 dB) : refusé.",
            f"03 : un NEXT mauvais sur un lien court vient presque toujours du raccordement (paires détorsadées sur plus de 13 mm, mauvais poinçonnage, câble écrasé près de la prise) : on refait la terminaison et on reteste. 04 : il est trop long, l'affaiblissement suit la longueur ; on raccourcit le parcours ou l'on rapproche l'équipement. ACR du lien 02 : 37,2 − 28,4 = {fr(E12_ACR_02)} dB.",
        ),
    ),
    PR06Item(
        key="E13",
        usage=USAGE_PRACTICE,
        title="Bilan d'une liaison monomode et marge exigée",
        question_type="document_analysis",
        requirement_ids=("AP-20", "AP-21"),
        kind=KIND_FIBRE,
        context=(
            "Une entreprise de transport relie son siège à un dépôt par une fibre monomode louée. "
            "Le document 1 décrit la liaison et le module optique prévu. Le cahier des charges du "
            "client exige une marge d'au moins 3 dB pour couvrir les réparations futures."
        ),
        documents=(
            _table(
                "Document 1 — Liaison et module prévu",
                ("Élément", "Valeur"),
                ("Fibre", "Monomode OS2, 0,4 dB/km à 1 310 nm"),
                ("Longueur", f"{fr(E13_LINK.length_m / 1000)} km"),
                ("Connecteurs (paires raccordées)", f"{E13_LINK.connectors}, 0,75 dB chacun au plus"),
                ("Épissures", f"{E13_LINK.splices}, 0,3 dB chacune au plus"),
                ("Module optique", "10GBASE-LR (portée 10 km), budget de la fiche : 6,2 dB"),
                ("Marge exigée", f"{fr(E13_MARGIN_REQUIRED)} dB"),
            ),
        ),
        instructions=(
            "Calcule la perte de la liaison et la marge.",
            "Dis si la liaison fonctionnera et si elle respecte le cahier des charges ; propose une suite.",
        ),
        criteria=(
            _c("Calcul", 1.5, f"6 × 0,4 = 2,4 dB ; 2 × 0,75 = 1,5 dB ; 3 × 0,3 = 0,9 dB ; total {fr(E13_LINK.loss_db, 2)} dB ; marge 6,2 − {fr(E13_LINK.loss_db, 2)} = {fr(E13_LINK.margin_db, 2)} dB."),
            _c("Verdict et suite", 1.5, f"6 km < 10 km et perte < budget : la liaison fonctionnera ; marge {fr(E13_LINK.margin_db, 2)} dB < 3 dB : cahier des charges non respecté sur le calcul ; mesurer la perte réelle (valeurs du calcul = maximums), ou réduire connecteurs et épissures, ou module de budget plus grand, en vérifiant la puissance reçue."),
        ),
        correction=(
            f"Perte : fibre 6 km × 0,4 dB/km = 2,4 dB ; connecteurs 2 × {fr(CONNECTOR_PAIR_DB, 2)} = 1,5 dB ; épissures 3 × {fr(SPLICE_DB)} = 0,9 dB ; total {fr(E13_LINK.loss_db, 2)} dB. Marge : 6,2 − {fr(E13_LINK.loss_db, 2)} = {fr(E13_LINK.margin_db, 2)} dB. La longueur (6 km) reste sous la portée du module (10 km) et la perte sous son budget : la liaison fonctionnera.",
            f"Mais la marge calculée ({fr(E13_LINK.margin_db, 2)} dB) est inférieure aux 3 dB exigés. Comme le calcul utilise les valeurs maximales, on mesure la perte réelle au photomètre (des épissures par fusion perdent souvent bien moins de 0,3 dB). Si la mesure ne suffit pas, on réduit le nombre de connecteurs et d'épissures, ou l'on choisit un module de budget plus grand, en contrôlant que la puissance reçue ne sature pas le récepteur.",
        ),
    ),
    PR06Item(
        key="E14",
        usage=USAGE_PRACTICE,
        title="Segments coaxiaux du laboratoire : longueur et affaiblissement",
        question_type="document_analysis",
        requirement_ids=("AP-19", "AP-20"),
        kind=KIND_DISTANCE,
        context=(
            "Un centre de formation conserve un réseau coaxial historique pour ses élèves. Le "
            "document 1 décrit ses deux segments. Règle IEEE 802.3 : l'affaiblissement d'un "
            "segment ne doit pas dépasser 8,5 dB à 10 MHz ; segments de 185 m (10BASE2) et 500 m "
            "(10BASE5) au plus."
        ),
        documents=(
            _table(
                "Document 1 — Segments relevés",
                ("Segment", "Câble", "Longueur", "Affaiblissement à 10 MHz (fiche)"),
                ("Salle 1", "RG-58, 10BASE2", f"{E14_THIN_M} m", f"{fr(E14_THIN_DB_PER_100M)} dB/100 m"),
                ("Couloir", "Coaxial épais, 10BASE5", f"{E14_THICK_M} m", f"{fr(E14_THICK_DB_PER_100M)} dB/100 m"),
            ),
        ),
        instructions=(
            "Calcule l'affaiblissement de chaque segment et compare-le à la règle.",
            "Dis quel segment est non conforme et comment le corriger.",
        ),
        criteria=(
            _c("Calculs", 1.5, f"Salle 1 : 2,1 × 4,6 = {fr(E14_THIN_LOSS, 2)} dB > 8,5 dB ; couloir : 4,8 × 1,7 = {fr(E14_THICK_LOSS, 2)} dB ≤ 8,5 dB."),
            _c("Verdict et correction", 1.5, f"Salle 1 non conforme ({E14_THIN_M} m > {THIN_SEGMENT_MAX_M} m, affaiblissement trop fort) : raccourcir le bus sous 185 m ou le couper en deux segments reliés par un répéteur, chaque segment avec ses deux terminateurs 50 Ω ; couloir conforme ({E14_THICK_M} m ≤ {THICK_SEGMENT_MAX_M} m)."),
        ),
        correction=(
            f"Salle 1 : 210 m = 2,1 × 100 m, donc 2,1 × 4,6 = {fr(E14_THIN_LOSS, 2)} dB, plus que les 8,5 dB admis ; le segment dépasse aussi les 185 m du 10BASE2. Couloir : 4,8 × 1,7 = {fr(E14_THICK_LOSS, 2)} dB, sous 8,5 dB, et 480 m restent sous les 500 m du 10BASE5 : conforme.",
            "La longueur maximale d'un segment coaxial vient justement de cette limite d'affaiblissement : le câble fin, plus atténuant, doit être plus court. Correction de la salle 1 : raccourcir le bus sous 185 m, ou le couper en deux segments reliés par un répéteur, chacun fermé par ses deux terminateurs 50 Ω.",
        ),
    ),
    PR06Item(
        key="E15",
        usage=USAGE_PRACTICE,
        title="Expliquer pourquoi 1 Gb/s ne donne pas 1 Go/s",
        question_type="long_answer",
        requirement_ids=("AP-19",),
        kind=KIND_RATE,
        context=(
            "Le patron d'une petite imprimerie a acheté un switch « 1 Gb/s » et s'attendait à "
            "copier un gigaoctet par seconde. Il voit plutôt une centaine de « Mo/s » dans "
            "l'explorateur de Windows et pense que le matériel est défectueux. Il te demande une "
            "explication écrite, simple et chiffrée."
        ),
        instructions=("Rédige l'explication : unités, débit utile maximal, et ce qui peut encore le réduire.",),
        criteria=(
            _c("Unités", 1, f"b = bit, o = octet = 8 bits ; 1 Gb/s = 10⁹ b/s ÷ 8 = {fr(E15_MAX_MO_S, 0)} Mo/s au maximum."),
            _c("Débit utile", 1.5, f"En-têtes Ethernet, IP, TCP et intervalle entre trames : environ {pct(TCP_EFFICIENCY, 0)} au mieux, soit ≈ {fr(E15_USEFUL_MO_S, 0)} Mo/s ≈ {fr(E15_USEFUL_MIO_S, 0)} Mio/s, ce que Windows affiche comme « Mo/s »."),
            _c("Autres limites et conclusion", 1.5, "Disques, processeur, petits fichiers, autres utilisateurs, antivirus ; une centaine de Mo/s est normal : matériel en bon état."),
        ),
        correction=(
            f"Les débits se comptent en bits par seconde, les fichiers en octets ; un octet vaut 8 bits. 1 Gb/s = 1 000 000 000 bits par seconde, soit au plus {fr(E15_MAX_MO_S, 0)} millions d'octets par seconde ({fr(E15_MAX_MO_S, 0)} Mo/s).",
            f"Une partie de ce débit transporte les en-têtes (Ethernet, IP, TCP) et les intervalles entre trames : pour une copie, il reste au mieux environ {pct(TCP_EFFICIENCY, 0)}, soit près de {fr(E15_USEFUL_MO_S, 0)} Mo/s. Windows compte en Mio (1 048 576 octets) mais écrit « Mo » : il affiche environ {fr(E15_USEFUL_MIO_S, 0)} « Mo/s ». Les disques, le processeur, les petits fichiers ou d'autres copies en même temps réduisent encore ce chiffre. Une centaine de Mo/s est donc normale : le matériel fonctionne.",
        ),
    ),
    PR06Item(
        key="E16",
        usage=USAGE_PRACTICE,
        title="Rédiger le diagnostic d'un désaccord de duplex",
        question_type="long_answer",
        requirement_ids=("AP-19", "AP-20"),
        kind=KIND_LINK,
        context=(
            "Dans un cabinet d'architectes, un seul PC est très lent sur le réseau : les pages "
            "s'ouvrent par à-coups et les copies échouent parfois. Un ancien technicien a forcé le "
            "port 12 du switch à 100 Mb/s full duplex ; le PC est resté en auto-négociation. Le "
            "switch compte de nombreuses erreurs CRC sur ce port, le PC des collisions tardives."
        ),
        instructions=("Rédige le diagnostic : ce que chaque côté a négocié, pourquoi c'est lent, la correction et le contrôle.",),
        criteria=(
            _c("Négociation", 1.5, "Le PC en auto face à un port forcé détecte 100 Mb/s mais pas le duplex : il passe en half duplex ; le switch reste en full : désaccord de duplex."),
            _c("Symptômes expliqués", 1, "Le PC (half) attend que la ligne soit libre et voit des collisions tardives ; le switch (full) émet en même temps et reçoit des trames abîmées : erreurs CRC ; retransmissions, lenteurs."),
            _c("Correction et contrôle", 1.5, "Remettre le port en auto-négociation (ou forcer les deux côtés à l'identique si un équipement l'exige) ; vérifier 1 Gb/s ou 100 Mb/s full des deux côtés, compteurs remis à zéro qui restent stables ; consigner."),
        ),
        correction=(
            "Le PC en auto-négociation ne reçoit pas d'annonce du port forcé : il détecte la vitesse (100 Mb/s) par le signal, mais ne peut pas connaître le duplex et se met en half duplex. Le switch, forcé, reste en full duplex : c'est un désaccord de duplex.",
            "En half duplex, le PC arrête d'émettre quand il reçoit : il voit des collisions tardives. Le switch, en full duplex, émet sans attendre et reçoit des trames coupées : erreurs CRC. Les trames perdues sont retransmises : lenteur et copies qui échouent. Correction : remettre le port 12 en auto-négociation (ou, si un appareil l'impose, forcer les deux côtés à l'identique) ; contrôle : même vitesse et full duplex des deux côtés, compteurs remis à zéro qui restent stables pendant une copie, intervention consignée.",
        ),
    ),
    PR06Item(
        key="E17",
        usage=USAGE_PRACTICE,
        title="Réutiliser un câblage Cat6 pour du 10 Gb/s ?",
        question_type="short_answer",
        requirement_ids=("AP-19", "AP-20"),
        kind=KIND_DISTANCE,
        context=(
            "Un studio de montage vidéo veut passer ses trois stations de travail à 10 Gb/s. Le "
            "câblage existant est en Cat6 U/UTP ; les liens mesurent 32 m, 48 m et 70 m de canal, "
            "dans un faisceau de vingt câbles. Le gérant voudrait seulement changer les cartes et "
            "le switch."
        ),
        instructions=("Dis, pour chaque lien, si le Cat6 peut convenir à 10 Gb/s, et ce que tu proposes.",),
        criteria=(
            _c("Règle", 1, "10GBASE-T : Cat6A sur 100 m ; Cat6 seulement jusqu'à 55 m, 37 m dans le pire cas de diaphonie entre câbles voisins (faisceau)."),
            _c("Verdicts et proposition", 2, "32 m : possible ; 48 m : seulement après certification (faisceau de 20 câbles, diaphonie exogène) ; 70 m : non, recâbler en Cat6A ; certifier tous les liens à 10 Gb/s avant de conclure."),
        ),
        correction=(
            "La norme 10GBASE-T est prévue sur 100 m en Cat6A. En Cat6, elle ne tient que sur une longueur réduite : 55 m au plus, et seulement 37 m dans le pire cas, quand beaucoup de câbles voisins créent de la diaphonie entre câbles (diaphonie exogène).",
            "32 m : sous 37 m, c'est possible. 48 m : entre 37 et 55 m dans un faisceau de vingt câbles, seulement si une certification à 10 Gb/s le confirme. 70 m : non, il faut un câble Cat6A (ou de la fibre). Proposition : certifier les liens de 32 et 48 m, recâbler celui de 70 m en Cat6A, puis changer cartes et switch.",
        ),
    ),
    PR06Item(
        key="E18",
        usage=USAGE_PRACTICE,
        title="Corriger une idée fausse sur le NEXT",
        question_type="short_answer",
        requirement_ids=("AP-20",),
        kind=KIND_SIGNAL,
        context=(
            "En lisant un rapport de testeur, un stagiaire affirme : « le lien A a un NEXT de 32 dB "
            "et le lien B de 44 dB ; plus le NEXT est petit, moins il y a de diaphonie, donc A est "
            "meilleur ». Les deux liens ont le même affaiblissement, 20 dB, à la fréquence du test."
        ),
        instructions=("Corrige l'affirmation et compare les deux liens avec l'ACR.",),
        criteria=(
            _c("Correction", 1.5, "Le NEXT est l'affaiblissement du signal parasite passé d'une paire à l'autre, mesuré du côté de l'émetteur : plus il est grand, moins de diaphonie ; B (44 dB) est meilleur."),
            _c("ACR", 1.5, f"ACR = NEXT − affaiblissement : A = {fr(acr_db(32, 20))} dB, B = {fr(acr_db(44, 20))} dB ; B garde plus d'écart entre signal et diaphonie."),
        ),
        correction=(
            "Le NEXT (paradiaphonie) mesure de combien le signal qui fuit d'une paire vers sa voisine est affaibli, du côté de l'émetteur. Une grande valeur en dB veut dire que peu de signal fuit : 44 dB est meilleur que 32 dB. L'affirmation du stagiaire est donc inversée : le lien B est meilleur.",
            f"L'ACR (NEXT − affaiblissement) compare le signal utile à la diaphonie : A = 32 − 20 = {fr(acr_db(32, 20))} dB, B = 44 − 20 = {fr(acr_db(44, 20))} dB. Plus l'ACR est grand, plus le récepteur distingue facilement le signal de la diaphonie.",
        ),
    ),
    PR06Item(
        key="E19",
        usage=USAGE_PRACTICE,
        title="Collisions sur un ancien hub",
        question_type="long_answer",
        requirement_ids=("AP-19", "AP-20"),
        kind=KIND_LINK,
        context=(
            "Une association utilise encore un hub 10BASE-T à 16 ports pour douze PC. Le réseau "
            "devient très lent quand plusieurs bénévoles impriment ou copient en même temps ; les "
            "voyants « collision » du hub clignotent sans cesse. Le trésorier demande pourquoi, et "
            "s'il suffit d'acheter un hub plus récent."
        ),
        instructions=("Explique le fonctionnement du hub, l'origine des collisions et ta proposition.",),
        criteria=(
            _c("Fonctionnement", 1.5, "Le hub répète chaque trame sur tous les ports : un seul domaine de collision ; tous les PC partagent 10 Mb/s en half duplex ; méthode CSMA/CD : écouter, émettre, détecter la collision, attendre un délai aléatoire, réémettre."),
            _c("Explication", 1, "Plus de PC actifs → plus de collisions et d'attentes → débit utile bien inférieur à 10 Mb/s."),
            _c("Proposition", 1.5, "Remplacer par un switch (le hub n'est plus vendu) : chaque port est son propre domaine de collision, full duplex, sans collision, à 100 Mb/s ou 1 Gb/s ; vérifier câbles et cartes, auto-négociation ; contrôle."),
        ),
        correction=(
            "Un hub répète chaque trame reçue sur tous ses ports : les douze PC partagent le même support, à 10 Mb/s, en half duplex. Ils suivent la méthode CSMA/CD : écouter avant d'émettre ; si deux PC émettent en même temps, il y a collision, chacun attend un délai aléatoire et réémet. Plus il y a de PC actifs, plus les collisions et les attentes se multiplient : le débit utile chute bien en dessous de 10 Mb/s.",
            "Un hub plus récent ne changerait rien (et ne se vend plus) : il faut un switch. Il envoie chaque trame seulement vers le port du destinataire ; chaque liaison fonctionne en full duplex, sans collision, à 100 Mb/s ou 1 Gb/s selon les cartes et les câbles. On laisse l'auto-négociation, on vérifie la vitesse obtenue sur chaque port et l'on consigne.",
        ),
    ),
)

# =============================================================================================
# Mini-examen : 10 questions × 2 points = /20 (réserve « Examen blanc »)
# =============================================================================================

EXAM_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="X01",
        usage=USAGE_EXAM,
        title="Durée de la sauvegarde d'un cabinet",
        question_type="short_answer",
        requirement_ids=("AP-19",),
        kind=KIND_RATE,
        context=(
            "Un cabinet de kinésithérapie sauvegarde chaque soir 2,4 Go de données (taille "
            "décimale) vers un disque réseau, à travers un switch à 100 Mb/s. Le rendement mesuré "
            "lors d'un essai est de 90 %. La secrétaire veut savoir combien de temps laisser le PC "
            "allumé."
        ),
        instructions=("Calcule la durée de la sauvegarde, en écrivant les unités à chaque étape.",),
        criteria=(
            _c("Conversions", 1, f"2,4 × 10⁹ × 8 = {fr(X01_BITS / 1e9, 1)} × 10⁹ bits ; débit utile 100 × 0,9 = 90 Mb/s = 90 × 10⁶ b/s."),
            _c("Résultat", 1, f"{fr(X01_BITS / 1e9, 1)} × 10⁹ / 90 × 10⁶ ≈ {fr(X01_T)} s, soit {duration_fr(X01_T)} environ."),
        ),
        correction=(
            f"Taille : 2,4 Go = 2,4 × 10⁹ octets × 8 = {fr(X01_BITS / 1e9, 1)} × 10⁹ bits. Débit utile : 100 Mb/s × 90 % = 90 × 10⁶ b/s.",
            f"Durée : {fr(X01_BITS / 1e9, 1)} × 10⁹ / 90 × 10⁶ ≈ {fr(X01_T)} s, soit environ {duration_fr(X01_T)}. On laisse le PC allumé quelques minutes de plus par prudence.",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Un abonnement à 500 Mb/s",
        question_type="short_answer",
        requirement_ids=("AP-19",),
        kind=KIND_RATE,
        context=(
            "Un client a souscrit un abonnement Internet « 500 Mb/s ». Il se plaint : « je ne "
            "télécharge jamais à plus de 60 Mo/s, on m'avait promis 500 ! ». Le test de débit du "
            "fournisseur affiche 480 Mb/s. Il te demande si le fournisseur le trompe."
        ),
        instructions=("Réponds au client par écrit, calcul à l'appui.",),
        criteria=(
            _c("Calcul", 1, f"500 Mb/s ÷ 8 = {fr(X02_MAX_MO_S, 1)} Mo/s au maximum ; 480 Mb/s ÷ 8 = 60 Mo/s."),
            _c("Conclusion", 1, "Mb/s (bits) et Mo/s (octets) ne sont pas la même unité ; 60 Mo/s correspond à 480 Mb/s, proche du nominal : l'abonnement est respecté."),
        ),
        correction=(
            f"Le débit de l'abonnement est en mégabits par seconde, le téléchargement s'affiche en mégaoctets par seconde ; un octet vaut 8 bits. 500 Mb/s ÷ 8 = {fr(X02_MAX_MO_S, 1)} Mo/s au maximum.",
            "Le test mesure 480 Mb/s, soit 480 ÷ 8 = 60 Mo/s : c'est exactement ce que le client observe, et c'est proche du débit nominal (les en-têtes en prennent une petite part). Le fournisseur ne le trompe pas.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="10 Gb/s sur un lien Cat6 de 75 m",
        question_type="short_answer",
        requirement_ids=("AP-19", "AP-20"),
        kind=KIND_DISTANCE,
        context=(
            "Une agence de communication veut relier son nouveau serveur à 10 Gb/s au switch de la "
            "baie. Le câble Cat6 U/UTP déjà posé entre la baie et le local du serveur mesure 75 m "
            "de canal, cordons compris. Le gérant demande si l'on peut le garder."
        ),
        instructions=("Réponds en justifiant par la règle, puis propose une solution.",),
        criteria=(
            _c("Règle et verdict", 1, "10GBASE-T : Cat6A sur 100 m ; Cat6 au plus 55 m (37 m dans le pire cas) ; 75 m > 55 m : le Cat6 ne convient pas."),
            _c("Solution", 1, "Tirer un câble Cat6A (connectique Cat6A) de 75 m, ou une fibre multimode avec modules 10GBASE-SR ; certifier le lien."),
        ),
        correction=(
            "La norme 10GBASE-T prévoit 100 m en Cat6A ; en Cat6, la portée est réduite à 55 m au plus (37 m quand beaucoup de câbles voisins créent de la diaphonie). Avec 75 m, le câble Cat6 existant ne convient pas à 10 Gb/s.",
            "Solution : poser un câble Cat6A avec prises et cordons Cat6A (75 m reste sous les 100 m), ou une fibre multimode avec des modules 10GBASE-SR ; dans les deux cas, on certifie le lien avant la mise en service.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="Allonger un bus 10BASE2 de formation",
        question_type="short_answer",
        requirement_ids=("AP-19", "AP-20"),
        kind=KIND_DISTANCE,
        context=(
            "Un formateur veut ajouter quatre postes à la salle de démonstration 10BASE2 de son "
            "école. Pour les atteindre, le bus en RG-58 passerait de 160 m à 230 m d'un "
            "terminateur à l'autre. Il compte simplement rallonger le câble avec des raccords BNC."
        ),
        instructions=("Dis si c'est possible et propose une solution conforme.",),
        criteria=(
            _c("Verdict", 1, f"Non : un segment 10BASE2 ne dépasse pas {THIN_SEGMENT_MAX_M} m (affaiblissement ≤ 8,5 dB à 10 MHz) ; 230 m > 185 m."),
            _c("Solution", 1, "Deux segments de moins de 185 m reliés par un répéteur, chacun fermé par ses deux terminateurs 50 Ω ; ou passer ces postes sur un switch en paire torsadée."),
        ),
        correction=(
            f"Un segment 10BASE2 en RG-58 est limité à {THIN_SEGMENT_MAX_M} m : au-delà, l'affaiblissement dépasse les {fr(COAX_SEGMENT_MAX_DB)} dB admis à 10 MHz et les signaux (et la détection des collisions) deviennent peu fiables. 230 m n'est donc pas possible, même avec de bons raccords.",
            "Solution : couper le bus en deux segments de moins de 185 m reliés par un répéteur, chaque segment fermé par ses deux terminateurs 50 Ω ; ou, plus simple aujourd'hui, raccorder les nouveaux postes en paire torsadée sur un switch.",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Puissance en sortie d'une liaison de 13 dB",
        question_type="short_answer",
        requirement_ids=("AP-20",),
        kind=KIND_SIGNAL,
        context=(
            "Lors d'un exercice de mesure en laboratoire, un émetteur injecte 20 mW dans une "
            "liaison. Le câble et ses deux connecteurs font perdre au total 13 dB à la fréquence "
            "utilisée. Le professeur demande la puissance qui arrive au récepteur, sans "
            "calculatrice."
        ),
        instructions=("Calcule la puissance reçue en mW en expliquant ton raisonnement en dB.",),
        criteria=(
            _c("Raisonnement", 1, "13 dB = 10 dB + 3 dB : divisé par 10, puis par 2 (soit par 20)."),
            _c("Résultat", 1, f"20 mW ÷ 20 = {fr(X05_OUT_MW, 1)} mW (≈ 0 dBm) ; en dBm : 20 mW ≈ 13 dBm, 13 − 13 = 0 dBm = 1 mW."),
        ),
        correction=(
            "Les dB s'additionnent et se décomposent : 13 dB = 10 dB + 3 dB. 10 dB divisent la puissance par 10, 3 dB environ par 2 : 13 dB la divisent par environ 20.",
            f"Puissance reçue : 20 mW ÷ 20 = {fr(X05_OUT_MW, 1)} mW. Même résultat en dBm : 20 mW ≈ 13 dBm ; 13 dBm − 13 dB = 0 dBm, soit {fr(mw(0))} mW.",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Bilan d'une liaison entre deux bâtiments",
        question_type="document_analysis",
        requirement_ids=("AP-20", "AP-21"),
        kind=KIND_FIBRE,
        context=(
            "Un hôpital relie deux bâtiments par une fibre monomode. Le document 1 donne la liaison "
            "et le module optique prévu. Le directeur technique veut savoir, par écrit, si la "
            "liaison fonctionnera et avec quelle marge."
        ),
        documents=(
            _table(
                "Document 1 — Liaison prévue",
                ("Élément", "Valeur"),
                ("Fibre", "Monomode OS2, 0,4 dB/km à 1 310 nm"),
                ("Longueur", f"{fr(X06_LINK.length_m / 1000)} km"),
                ("Connecteurs (paires raccordées)", f"{X06_LINK.connectors} × 0,75 dB au plus"),
                ("Épissures", f"{X06_LINK.splices} × 0,3 dB au plus"),
                ("Module optique", "10GBASE-LR, portée 10 km, budget de la fiche : 6,2 dB"),
            ),
        ),
        instructions=("Calcule la perte et la marge, puis conclus en vérifiant aussi la portée.",),
        criteria=(
            _c("Calcul", 1, f"3,5 × 0,4 = 1,4 dB + 2 × 0,75 = 1,5 dB + 2 × 0,3 = 0,6 dB = {fr(X06_LINK.loss_db, 2)} dB ; marge 6,2 − {fr(X06_LINK.loss_db, 2)} = {fr(X06_LINK.margin_db, 2)} dB."),
            _c("Conclusion", 1, "3,5 km ≤ 10 km et perte < budget : la liaison fonctionnera ; mesure de réception au photomètre."),
        ),
        correction=(
            f"Perte : fibre 3,5 km × 0,4 dB/km = 1,4 dB ; connecteurs 2 × 0,75 = 1,5 dB ; épissures 2 × 0,3 = 0,6 dB ; total {fr(X06_LINK.loss_db, 2)} dB. Marge : 6,2 − {fr(X06_LINK.loss_db, 2)} = {fr(X06_LINK.margin_db, 2)} dB.",
            "La longueur (3,5 km) reste sous la portée du module (10 km) et la perte sous son budget : la liaison fonctionnera, avec une marge confortable. On la confirme par une mesure au photomètre à la réception.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Un poste bloqué à 100 Mb/s",
        question_type="document_analysis",
        requirement_ids=("AP-19", "AP-20"),
        kind=KIND_LINK,
        context=(
            "Une comptable d'une fiduciaire trouve ses copies lentes. Son PC Linux et le switch sont "
            "Gigabit. Le document 1 est un extrait de la sortie d'ethtool ; le document 2 le "
            "résultat du testeur sur son cordon de poste de 3 m, refait la veille par un collègue."
        ),
        documents=(
            _console(
                "Document 1 — Sortie de « ethtool eno1 » (extrait, capture fictive)",
                "        Link partner advertised link modes:  10baseT/Half 10baseT/Full",
                "                                             100baseT/Half 100baseT/Full",
                "                                             1000baseT/Full",
                "        Speed: 100Mb/s",
                "        Duplex: Full",
                "        Auto-negotiation: on",
            ),
            _table(
                "Document 2 — Testeur, cordon de poste",
                ("Paire", "Résultat"),
                ("1-2", "OK"), ("3-6", "OK"), ("4-5", "Ouvert (conducteur 4)"), ("7-8", "OK"),
            ),
        ),
        instructions=("Donne la cause du 100 Mb/s et la correction, avec le contrôle final.",),
        criteria=(
            _c("Cause", 1, "Le switch annonce 1000baseT/Full et l'auto-négociation est active, mais la paire 4-5 du cordon est ouverte : le Gigabit exige les 4 paires, la carte rétrograde à 100 Mb/s."),
            _c("Correction et contrôle", 1, "Remplacer ou refaire le cordon (sertissage), retester les 8 conducteurs, vérifier Speed: 1000Mb/s full, consigner."),
        ),
        correction=(
            "Le switch annonce 1000baseT/Full et l'auto-négociation est active : ni réglage forcé, ni switch limité. Le testeur montre la paire 4-5 ouverte sur le cordon refait la veille. 1000BASE-T utilise les quatre paires ; avec une paire coupée, les cartes rétrogradent à 100 Mb/s, qui n'utilise que 1-2 et 3-6.",
            "Correction : remplacer le cordon (ou le resertir correctement), retester les 8 conducteurs, puis vérifier dans ethtool « Speed: 1000Mb/s » et « Duplex: Full », et consigner l'intervention.",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Collisions tardives sur un port du switch",
        question_type="short_answer",
        requirement_ids=("AP-19", "AP-20"),
        kind=KIND_LINK,
        context=(
            "Sur le switch d'une PME, le port 7 compte des milliers de collisions tardives ; "
            "l'utilisatrice du PC raccordé se plaint de lenteurs. Tu découvres que la carte réseau "
            "de son PC a été forcée à 100 Mb/s full duplex, alors que le port 7 du switch est en "
            "auto-négociation."
        ),
        instructions=("Explique ce qui se passe et comment le corriger.",),
        criteria=(
            _c("Explication", 1, "Le port auto détecte 100 Mb/s mais pas le duplex : il se met en half duplex ; le PC est en full : désaccord de duplex ; le port half voit des collisions tardives, le PC des erreurs CRC."),
            _c("Correction", 1, "Remettre la carte du PC en auto-négociation ; vérifier même vitesse et full duplex des deux côtés, compteurs stables."),
        ),
        correction=(
            "Face à une carte forcée, le port en auto-négociation ne reçoit aucune annonce : il détecte la vitesse (100 Mb/s) mais se met en half duplex. La carte, forcée en full duplex, émet à tout moment : le port voit des collisions tardives, le PC reçoit des trames abîmées (erreurs CRC) ; les retransmissions provoquent les lenteurs.",
            "Correction : remettre la carte du PC en auto-négociation, puis vérifier des deux côtés la même vitesse en full duplex et des compteurs d'erreurs qui n'augmentent plus.",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="Une caméra 75 Ω sur du RG-58",
        question_type="short_answer",
        requirement_ids=("AP-20",),
        kind=KIND_SIGNAL,
        context=(
            "Un commerçant a raccordé une caméra analogique (sortie vidéo 75 Ω) à son enregistreur "
            "avec un câble RG-58 récupéré d'un ancien réseau. L'image présente des contours "
            "doublés et un léger « fantôme ». Il demande si le câble y est pour quelque chose."
        ),
        instructions=("Explique le problème en calculant le coefficient de réflexion, puis propose la correction.",),
        criteria=(
            _c("Calcul", 1, f"RG-58 = 50 Ω, caméra et enregistreur 75 Ω ; Γ = (75 − 50) / (75 + 50) = {fr(X09_GAMMA, 2)} ; {fr(reflected_power_pct(X09_GAMMA), 1)} % de la puissance réfléchie (affaiblissement de réflexion ≈ {fr(X09_RL, 0)} dB)."),
            _c("Correction", 1, "Rupture d'impédance → réflexions qui reviennent décalées : image doublée ; remplacer par du RG-59 75 Ω avec BNC 75 Ω, d'une seule longueur."),
        ),
        correction=(
            f"Le RG-58 a une impédance de 50 Ω, la caméra et l'enregistreur de 75 Ω. À chaque changement d'impédance, une partie du signal est réfléchie : Γ = (75 − 50) / (75 + 50) = {fr(X09_GAMMA, 2)}, soit {fr(reflected_power_pct(X09_GAMMA), 1)} % de la puissance (affaiblissement de réflexion d'environ {fr(X09_RL, 0)} dB). Le signal réfléchi revient avec un retard : contours doublés, fantôme.",
            "Correction : remplacer le câble par du coaxial 75 Ω (RG-59) avec des connecteurs BNC 75 Ω, d'une seule longueur, puis vérifier l'image.",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Un lien refusé pour le NEXT",
        question_type="document_analysis",
        requirement_ids=("AP-20",),
        kind=KIND_SIGNAL,
        context=(
            "À la réception d'un câblage Cat6 dans une crèche, un seul lien est refusé par le "
            "testeur (document 1). En ouvrant la prise murale du bureau 3, tu constates que les "
            "paires ont été détorsadées sur environ 40 mm avant le poinçonnage."
        ),
        documents=(
            _table(
                "Document 1 — Lien B1-P1-09 (lien permanent Cat6)",
                ("Mesure", "Valeur", "Limite du testeur"),
                ("Longueur", "34 m", f"≤ {PERMANENT_LINK_MAX_M} m"),
                ("Affaiblissement (250 MHz)", "12,1 dB", f"≤ {fr(E12_IL_LIMIT)} dB"),
                ("NEXT côté bureau 3", "29,8 dB", f"≥ {fr(E12_NEXT_LIMIT)} dB"),
                ("NEXT côté panneau", "42,5 dB", f"≥ {fr(E12_NEXT_LIMIT)} dB"),
            ),
        ),
        instructions=("Explique pourquoi le lien est refusé, la cause et la correction.",),
        criteria=(
            _c("Analyse", 1, "Longueur et affaiblissement conformes ; NEXT côté bureau 3 = 29,8 < 35,3 dB : trop de diaphonie à cette extrémité seulement (côté panneau 42,5 dB : bon)."),
            _c("Cause et correction", 1, "Détorsadage de 40 mm (> 13 mm) à la prise : la torsade ne protège plus, la diaphonie augmente ; refaire la terminaison (≤ 13 mm), retester et consigner."),
        ),
        correction=(
            "Le lien est court (34 m) et son affaiblissement correct ; seul le NEXT mesuré côté bureau 3 (29,8 dB) est sous la limite de 35,3 dB, alors que côté panneau il vaut 42,5 dB. Le NEXT se mesure du côté de l'émetteur : le défaut est donc près de la prise du bureau 3.",
            "Cause : les paires détorsadées sur 40 mm (au lieu de 13 mm au plus) ne bénéficient plus de la torsade, et le signal passe d'une paire à l'autre. Correction : couper et refaire la terminaison en gardant la torsade jusqu'au contact, retester le lien et consigner le résultat.",
        ),
    ),
)

ALL_ITEMS: tuple[PR06Item, ...] = PRACTICE_ITEMS + EXAM_ITEMS
EXAM_TOTAL_POINTS = 20


def validate_items() -> list[str]:
    """Contrôles éditoriaux : format d'exercice du socle (#192), 2 points par question du
    mini-examen, réponses libres à l'examen, données des classements et remises en ordre,
    exigence du cours citée."""
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
            errors.append(f"{item.key} : au moins une exigence du cours doit être citée.")
    for item in EXAM_ITEMS:
        if abs(item.total_points - 2) > 1e-9:
            errors.append(f"{item.key} : une question du mini-examen vaut 2 points.")
        if item.question_type not in ("short_answer", "long_answer", "document_analysis"):
            errors.append(f"{item.key} : le mini-examen n'accepte que des réponses libres.")
    for key, link in (("E13", E13_LINK), ("X06", X06_LINK)):
        if fibre_errors(link):
            errors.append(f"{key} : la liaison du corrigé doit respecter portée et budget.")
    return errors
