"""PR15 « Câblage RJ45 T568A/B — fabrication, schémas et tests » — exercices corrigés et
mini-examen (ticket #197).

Même organisation que PR06 et PR11 (`app.v1.ampcr_pratique_pr06_bank`, dont ce module
réutilise le type d'item et la règle d'acceptation) :
- `PRACTICE_ITEMS` : 16 exercices corrigés affichés dans le cours (corrigé replié) et proposés
  dans « S'entraîner » — au moins 5 exercices de brochage ou de schéma, 4 analyses de résultats
  de testeur, 3 choix de câble ou d'installation et 3 procédures d'intervention écrites ;
- `EXAM_ITEMS` : les 10 questions du mini-examen noté /20 (2 points chacune), réponses libres,
  uniquement dans « Examen blanc », jamais affichées dans le cours.

Brochages et liaisons broche à broche : calculés depuis `T568A` / `T568B` (normes TIA/EIA-568,
vérifiées par les tests du ticket) ; affichages de testeur et relevés : supports fictifs.
"""

from app.v1.ampcr_pratique_format import ExerciseDocument, ScoringCriterion, validate_exercise
from app.v1.ampcr_pratique_pr06_bank import (
    USAGE_EXAM,
    USAGE_PRACTICE,
    Classification,
    Ordering,
    PR06Item,
)
from app.v1.ampcr_pratique_pr15_figures import (
    CRIMP_STEPS,
    SEQUENTIAL_WRONG,
    links_between,
    wire_label,
)
from app.v1.ampcr_pratique_visuals import T568A, T568B

PR15_CODE = "PR15"

KIND_PINOUT = "brochage et schéma"
KIND_TESTER = "analyse de résultat de testeur"
KIND_CHOICE = "choix de câble et d'installation"
KIND_PROCEDURE = "procédure d'intervention écrite"
KIND_SCENARIO = "scénario"


def _c(label: str, points: float, expected: str) -> ScoringCriterion:
    return ScoringCriterion(label=label, points=points, expected=expected)


def _table(title: str, header: tuple[str, ...], *rows: tuple[str, ...]) -> ExerciseDocument:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return ExerciseDocument(title=title, kind="tableau", content_text="\n".join(lines))


def _console(title: str, *lines: str) -> ExerciseDocument:
    return ExerciseDocument(title=title, kind="console", content_text="\n".join(lines))


def _order(wires: tuple[str, ...]) -> str:
    return ", ".join(f"{i} {wire_label(w)}" for i, w in enumerate(wires, start=1))


T568A_TEXT = _order(T568A)
T568B_TEXT = _order(T568B)

# --- Données calculées des exercices ------------------------------------------------------

# E01 : fils de T568B présentés dans le désordre ; la bonne broche est calculée.
E01_ELEMENTS: tuple[str, ...] = (
    "blanc-vert", "marron", "orange", "blanc-bleu", "blanc-orange", "vert", "bleu", "blanc-marron",
)
E01_CORRECT: tuple[int, ...] = tuple(T568B.index(w) for w in E01_ELEMENTS)

# E04 : couleur sur une broche donnée → A seulement, B seulement, ou A et B.
E04_CASES: tuple[tuple[int, str], ...] = (
    (1, "blanc-vert"), (4, "bleu"), (2, "orange"), (6, "orange"),
    (7, "blanc-marron"), (3, "blanc-vert"), (6, "vert"), (5, "blanc-bleu"),
)


def _e04_category(pin: int, wire: str) -> int:
    in_a, in_b = T568A[pin - 1] == wire, T568B[pin - 1] == wire
    if in_a and in_b:
        return 2
    return 0 if in_a else 1


E04_CORRECT: tuple[int, ...] = tuple(_e04_category(p, w) for p, w in E04_CASES)

# E05 : câble bout 1 en T568B, bout 2 en T568A.
E05_LINKS = links_between(T568B, T568A)

# E06 : fiche tenue languette visible (contacts dessous), extrémité vers l'avant : l'ordre
# rangé « de gauche à droite » arrive à l'envers, broche 8 → broche 1.
E06_RESULT: tuple[str, ...] = tuple(reversed(T568B))

# E08 : relevé de testeur à LED : 3 → 6 et 6 → 3 (paire 3-6 inversée à un bout).
E08_ROWS: tuple[tuple[int, int], ...] = ((1, 1), (2, 2), (3, 6), (4, 4), (5, 5), (6, 3), (7, 7), (8, 8))

# E14 : étapes de sertissage, affichées dans le désordre.
E14_SHOWN: tuple[int, ...] = (3, 0, 6, 1, 7, 4, 2, 5)


# =============================================================================================
# 16 exercices corrigés (cours + « S'entraîner »)
# =============================================================================================

PRACTICE_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="E01",
        usage=USAGE_PRACTICE,
        title="Placer les huit fils d'une fiche T568B",
        question_type="classification",
        requirement_ids=("AP-34",),
        kind=KIND_PINOUT,
        context=(
            "À l'atelier d'une école, tu prépares un cordon de brassage pour la salle informatique. "
            "Le câblage du bâtiment est entièrement en T568B. Tu tiens la fiche contacts dorés face "
            "à toi, languette dessous, câble vers le bas : la broche 1 est à gauche."
        ),
        instructions=("Range chacun des huit fils sur la broche qu'il doit occuper en T568B.",),
        criteria=(
            _c("Placement", 8, "T568B : " + T568B_TEXT + " (1 point par fil bien placé)."),
        ),
        correction=(
            "En T568B, de la broche 1 à la broche 8 : " + T568B_TEXT + ".",
            "Repère : la paire orange occupe 1-2, la verte 3-6 (elle « enjambe » la bleue), la bleue 4-5 et la marron 7-8 ; le fil blanc de chaque paire est sur la broche impaire, sauf la paire bleue (bleu en 4, blanc/bleu en 5).",
        ),
        classification=Classification(
            categories=tuple(f"Broche {n}" for n in range(1, 9)),
            elements=tuple(f"Fil {wire_label(w)}" for w in E01_ELEMENTS),
            correct=E01_CORRECT,
        ),
    ),
    PR06Item(
        key="E02",
        usage=USAGE_PRACTICE,
        title="Écrire l'autre bout d'un câble croisé",
        question_type="short_answer",
        requirement_ids=("AP-34", "AP-28"),
        kind=KIND_PINOUT,
        context=(
            "Pour relier deux anciens PC dont les cartes réseau 100 Mb/s n'ont pas de détection "
            "automatique (Auto MDI-X), un formateur te demande un câble croisé. Une extrémité est "
            "déjà sertie en T568B et testée visuellement : " + T568B_TEXT + "."
        ),
        instructions=(
            "Écris, broche par broche, l'ordre des couleurs de l'autre extrémité.",
            "Indique quelles broches changent par rapport à la première extrémité et pourquoi les autres restent identiques.",
        ),
        criteria=(
            _c("Ordre de l'autre bout", 1.5, "T568A : " + T568A_TEXT + "."),
            _c("Broches qui changent", 0.5, "1, 2, 3 et 6 changent (paires orange et verte échangées) ; 4, 5, 7, 8 identiques (paires bleue et marron)."),
        ),
        correction=(
            "Un croisé historique a une extrémité en T568B et l'autre en T568A. L'autre bout est donc : " + T568A_TEXT + ".",
            "Seules les broches 1, 2, 3 et 6 changent : A et B échangent la paire orange et la paire verte, ce qui relie l'émission d'un PC (1-2) à la réception de l'autre (3-6). Les paires bleue (4-5) et marron (7-8) restent identiques.",
        ),
    ),
    PR06Item(
        key="E03",
        usage=USAGE_PRACTICE,
        title="Testeur « OK » mais réseau instable : lire l'ordre des fils",
        question_type="document_analysis",
        requirement_ids=("AP-34", "AP-20"),
        kind=KIND_PINOUT,
        context=(
            "Un stagiaire a fabriqué dix cordons pour un bureau. Son testeur de continuité à LED "
            "allume les voyants 1 à 8 dans l'ordre pour chaque cordon. Pourtant, les postes branchés "
            "avec ces cordons perdent régulièrement la connexion. Tu regardes une fiche à travers "
            "son corps transparent (document 1) : les deux extrémités sont identiques."
        ),
        instructions=(
            "Compare l'ordre relevé au T568B et nomme le défaut.",
            "Explique pourquoi le testeur de continuité affiche un résultat correct, et quelle conséquence a ce défaut sur la transmission.",
            "Décris la correction et le test à faire ensuite.",
        ),
        documents=(
            _table(
                "Document 1 — Ordre des fils relevé dans la fiche (fiche vue côté contacts, broche 1 à gauche, relevé fictif)",
                ("Broche", "Fil"),
                *((str(i), wire_label(w)) for i, w in enumerate(SEQUENTIAL_WRONG, start=1)),
            ),
        ),
        criteria=(
            _c("Défaut nommé", 0.75, "Fils rangés paire par paire (1-2, 3-4, 5-6, 7-8) : les positions 3-6 et 4-5 reçoivent des fils de deux paires différentes, paires séparées (split pair)."),
            _c("Pourquoi le testeur dit OK", 0.75, "Les deux bouts sont identiques : chaque broche arrive sur la même broche, la continuité est parfaite ; un testeur de continuité ne vérifie pas que 3 et 6 sont sur la même paire torsadée."),
            _c("Conséquence", 0.75, "Le signal de la position 3-6 circule sur deux fils non torsadés ensemble : forte diaphonie et parasites, erreurs, coupures, débit réduit ou lien impossible en gigabit."),
            _c("Correction et test", 0.75, "Refaire les deux fiches en T568B (3 blanc/vert, 6 vert, 4 bleu, 5 blanc/bleu) et tester avec un testeur qui détecte les paires séparées (qualification) ; vérifier aussi les neuf autres cordons."),
        ),
        correction=(
            "Le stagiaire a rangé les fils paire par paire : " + _order(SEQUENTIAL_WRONG) + ". En T568B, la broche 4 reçoit le bleu et la broche 6 le vert.",
            "Les deux extrémités sont faites de la même façon : chaque fil arrive sur la même broche, d'où les voyants 1 à 8 dans l'ordre. Le testeur de continuité vérifie le chemin des fils, pas le fait que les broches 3 et 6 soient sur la même paire torsadée.",
            "Or Ethernet transmet un signal sur chaque position de paire (1-2, 3-6, 4-5, 7-8). Ici, la position 3-6 utilise un fil de la paire verte et un fil de la paire bleue : ces deux fils ne sont pas torsadés ensemble, la protection contre la diaphonie disparaît. Résultat : erreurs, coupures, débit réduit, voire lien impossible en gigabit. C'est une paire séparée (split pair).",
            "Correction : refaire les deux fiches dans l'ordre T568B, puis tester avec un testeur capable de détecter les paires séparées (testeur de qualification ou de certification). Vérifier les neuf autres cordons, sans doute faits de la même façon.",
        ),
    ),
    PR06Item(
        key="E04",
        usage=USAGE_PRACTICE,
        title="T568A, T568B ou les deux ?",
        question_type="classification",
        requirement_ids=("AP-34",),
        kind=KIND_PINOUT,
        context=(
            "Lors de l'audit du câblage d'une PME, tu relèves sur plusieurs fiches la couleur du fil "
            "présent sur une broche précise (fiche vue côté contacts, broche 1 à gauche). Il faut "
            "savoir à quelle norme chaque observation correspond pour repérer les cordons croisés."
        ),
        instructions=("Pour chaque observation, indique si elle correspond à T568A seulement, à T568B seulement, ou aux deux normes.",),
        criteria=(
            _c("Classement", 8, "1 blanc/vert = A ; 4 bleu = A et B ; 2 orange = B ; 6 orange = A ; 7 blanc/marron = A et B ; 3 blanc/vert = B ; 6 vert = B ; 5 blanc/bleu = A et B (1 point chacun)."),
        ),
        correction=(
            "T568A : " + T568A_TEXT + ".",
            "T568B : " + T568B_TEXT + ".",
            "Les broches 4, 5, 7 et 8 sont identiques dans les deux normes (paires bleue et marron) : « 4 bleu », « 5 blanc/bleu » et « 7 blanc/marron » valent pour A et B. Les broches 1, 2, 3 et 6 distinguent les normes : blanc/vert en 1 et orange en 6 = A ; orange en 2, blanc/vert en 3 et vert en 6 = B.",
        ),
        classification=Classification(
            categories=("T568A seulement", "T568B seulement", "T568A et T568B"),
            elements=tuple(f"Broche {p} : {wire_label(w)}" for p, w in E04_CASES),
            correct=E04_CORRECT,
        ),
    ),
    PR06Item(
        key="E05",
        usage=USAGE_PRACTICE,
        title="Tracer les liaisons d'un câble B-A",
        question_type="document_analysis",
        requirement_ids=("AP-34", "AP-28"),
        kind=KIND_PINOUT,
        context=(
            "Dans un lot de vieux câbles d'une salle de formation, un cordon porte l'étiquette "
            "« B / A ». Avant de le réutiliser, ton responsable veut savoir où arrive chaque fil et "
            "à quoi ce cordon pouvait servir. Le document 1 donne l'ordre lu à chaque bout."
        ),
        instructions=(
            "Pour chaque broche du bout 1, indique la broche du bout 2 où arrive le même fil.",
            "Nomme ce type de câble et explique, pour le 10/100 Mb/s, ce qu'il relie entre les deux équipements.",
        ),
        documents=(
            _table(
                "Document 1 — Ordre des fils aux deux bouts (fiche vue côté contacts, broche 1 à gauche)",
                ("Broche", "Bout 1", "Bout 2"),
                *((str(i), wire_label(b), wire_label(a)) for i, (b, a) in enumerate(zip(T568B, T568A, strict=True), start=1)),
            ),
        ),
        criteria=(
            _c("Liaisons", 1.5, "Bout 1 → bout 2 : " + ", ".join(f"{a}→{b}" for a, b in E05_LINKS) + "."),
            _c("Type de câble", 0.5, "Câble croisé (T568B d'un côté, T568A de l'autre)."),
            _c("Rôle en 10/100 Mb/s", 1, "L'émission d'un équipement (broches 1-2) arrive sur la réception de l'autre (3-6) et inversement ; utilisé historiquement entre équipements de même type (PC-PC, switch-switch)."),
        ),
        correction=(
            "On suit chaque couleur : " + ", ".join(f"broche {a} → broche {b}" for a, b in E05_LINKS) + ".",
            "Les paires orange et verte changent de position, les paires bleue et marron restent droites : c'est un câble croisé (T568B d'un côté, T568A de l'autre).",
            "En 10/100 Mb/s, une carte réseau émet sur 1-2 et reçoit sur 3-6. Le croisement relie l'émission de chaque côté à la réception de l'autre : on l'utilisait entre deux équipements de même type (PC-PC, switch-switch) sans détection automatique (Auto MDI-X).",
        ),
    ),
    PR06Item(
        key="E06",
        usage=USAGE_PRACTICE,
        title="Fiche tenue à l'envers : quel ordre obtient-on ?",
        question_type="short_answer",
        requirement_ids=("AP-34",),
        kind=KIND_PINOUT,
        context=(
            "Un nouveau collègue sertit une fiche en la tenant languette de verrouillage vers lui "
            "(contacts dorés dessous, extrémité de la fiche vers l'avant, câble vers lui). Il range "
            "les fils de gauche à droite dans l'ordre T568B qu'il a appris : blanc/orange à gauche."
        ),
        instructions=(
            "Indique sur quelle broche arrive le fil blanc/orange et donne l'ordre réellement obtenu de la broche 1 à la broche 8.",
            "Dis si les paires restent sur les bonnes positions et ce qu'il faut corriger dans la manière de tenir la fiche.",
        ),
        criteria=(
            _c("Ordre obtenu", 1, "Vu côté languette, la broche 1 est à droite : blanc/orange arrive en 8 ; ordre obtenu " + _order(E06_RESULT) + "."),
            _c("Paires et conformité", 0.5, "Chaque paire reste sur une position de paire (1-2 marron, 3-6 verte, 4-5 bleue, 7-8 orange) mais la fiche n'est ni T568A ni T568B : non conforme, et incompatible avec l'autre bout fait correctement."),
            _c("Bonne tenue", 0.5, "Contacts dorés vers soi, languette dessous, câble vers soi : broche 1 à gauche ; refaire la fiche."),
        ),
        correction=(
            "Vue côté languette, l'extrémité vers l'avant, la broche 1 est à droite et la broche 8 à gauche. Le fil blanc/orange, rangé à gauche, arrive donc sur la broche 8, et l'ordre est inversé : " + _order(E06_RESULT) + ".",
            "Les paires restent sur des positions de paire (marron en 1-2, verte en 3-6, bleue en 4-5, orange en 7-8), mais la fiche ne respecte ni T568A ni T568B : si l'autre bout est correct, le cordon ne fonctionne pas comme prévu ; même si les deux bouts sont faits ainsi, il est non conforme et source d'erreurs à la maintenance.",
            "Correction : tenir la fiche contacts dorés vers soi, languette dessous, câble vers soi (broche 1 à gauche), ranger dans l'ordre T568B et refaire la fiche.",
        ),
    ),
    PR06Item(
        key="E07",
        usage=USAGE_PRACTICE,
        title="Plus de lien après le remplacement d'une fiche",
        question_type="document_analysis",
        requirement_ids=("AP-34", "AP-37"),
        kind=KIND_TESTER,
        context=(
            "Dans un cabinet d'architectes, la fiche d'un cordon de 5 m a été écrasée par une "
            "chaise ; un collègue l'a refaite. Depuis, le PC du poste ne voit plus le réseau (voyant "
            "de lien éteint). Tu passes le cordon au testeur de câble (document 1)."
        ),
        instructions=(
            "Interprète le résultat du testeur et explique pourquoi le lien est totalement absent.",
            "Indique où chercher la cause et décris la correction et la validation.",
        ),
        documents=(
            _console(
                "Document 1 — Écran du testeur (affichage fictif)",
                "WIREMAP          RESULTAT : ECHEC",
                "1 ----------- 1",
                "2 ---X          OUVERT",
                "3 ----------- 3",
                "4 ----------- 4",
                "5 ----------- 5",
                "6 ----------- 6",
                "7 ----------- 7",
                "8 ----------- 8",
            ),
        ),
        criteria=(
            _c("Lecture", 0.75, "Circuit ouvert sur la broche 2 : le fil orange (T568B) n'établit pas de contact ; les 7 autres liaisons sont bonnes."),
            _c("Pourquoi aucun lien", 0.75, "La paire 1-2 est indispensable en 10/100 Mb/s (émission/réception) comme en 1 Gb/s (4 paires) : avec un fil ouvert sur 1-2, aucune vitesse ne fonctionne."),
            _c("Où chercher", 0.5, "D'abord la fiche refaite : fil pas en butée, trop court, ou contact mal serti ; regarder à travers la fiche."),
            _c("Correction et validation", 1, "Couper la fiche refaite, en sertir une nouvelle en T568B (fils en butée, gaine sous la patte), retester : 1→1 … 8→8 réussi, puis voyant de lien allumé et vitesse attendue sur le PC."),
        ),
        correction=(
            "Le testeur indique un circuit ouvert sur la broche 2 : le fil orange (en T568B) n'arrive pas. Les sept autres liaisons sont correctes.",
            "La position 1-2 sert en 10 et 100 Mb/s (une des deux paires utilisées) et en 1 Gb/s (les quatre paires) : un fil ouvert sur cette paire empêche tout lien.",
            "La cause est très probablement dans la fiche refaite : fil orange pas poussé jusqu'en butée, coupé trop court ou contact pas complètement enfoncé par la pince. On le voit souvent à travers le corps transparent.",
            "Correction : couper la fiche refaite, en sertir une nouvelle (fils dans l'ordre T568B, en butée, gaine sous la patte), puis retester : 1→1 … 8→8 réussi. Validation sur le poste : voyant de lien allumé, vitesse négociée attendue, accès au réseau.",
        ),
    ),
    PR06Item(
        key="E08",
        usage=USAGE_PRACTICE,
        title="Testeur à LED : voyants 3 et 6 croisés",
        question_type="document_analysis",
        requirement_ids=("AP-34",),
        kind=KIND_TESTER,
        context=(
            "Dans une bibliothèque, tu contrôles un cordon droit T568B fabriqué la veille avec un "
            "testeur à LED : le boîtier principal envoie un signal sur chaque broche l'une après "
            "l'autre, et tu notes quelle LED s'allume sur le bouchon distant (document 1)."
        ),
        instructions=(
            "Nomme le défaut d'après le relevé.",
            "Explique ce qu'a probablement fait le fabricant à l'une des extrémités et pourquoi ce câble ne peut pas être livré.",
            "Indique comment trouver la fiche à refaire et la vérification finale.",
        ),
        documents=(
            _table(
                "Document 1 — Relevé du testeur à LED (fictif)",
                ("LED du boîtier principal", "LED allumée sur le bouchon"),
                *((str(a), str(b)) for a, b in E08_ROWS),
            ),
        ),
        criteria=(
            _c("Défaut", 0.75, "3→6 et 6→3 : les deux fils de la paire verte sont inversés à un bout (paire inversée), les autres liaisons sont droites."),
            _c("Cause probable", 0.75, "À une extrémité, blanc/vert et vert permutés (vert en 3, blanc/vert en 6)."),
            _c("Pourquoi refuser", 0.5, "Le cordon n'est pas conforme (ni droit ni croisé) ; selon les équipements, lien absent ou instable : un câble non conforme ne se livre pas."),
            _c("Trouver et vérifier", 1, "Comparer chaque fiche au T568B à travers le corps transparent ; refaire celle qui a vert en 3 ; retester jusqu'à 1→1 … 8→8."),
        ),
        correction=(
            "La LED 3 du principal allume la 6 du bouchon et inversement : les deux fils de la position 3-6 sont inversés à un bout. Les autres liaisons sont droites. C'est une paire inversée (fils inversés).",
            "Le fabricant a sans doute permuté le blanc/vert et le vert à l'une des extrémités (vert en 3, blanc/vert en 6).",
            "Le cordon n'est ni droit ni croisé : il n'est pas conforme. Selon les cartes réseau, le lien peut être absent ou instable ; on ne livre pas un câble qui échoue au test.",
            "On compare chaque fiche au T568B à travers le corps transparent, on refait celle qui est fausse, puis on reteste jusqu'à obtenir 1→1 … 8→8.",
        ),
    ),
    PR06Item(
        key="E09",
        usage=USAGE_PRACTICE,
        title="Associer chaque relevé de testeur à son défaut",
        question_type="classification",
        requirement_ids=("AP-34",),
        kind=KIND_TESTER,
        context=(
            "Tu prépares une fiche d'aide pour les stagiaires d'un service technique. Elle rassemble "
            "six relevés réels obtenus sur des cordons censés être droits, avec un testeur de câble "
            "(wiremap) et, pour le dernier, un testeur de qualification qui mesure la diaphonie."
        ),
        instructions=("Associe chaque relevé au défaut qu'il révèle.",),
        criteria=(
            _c("Classement", 6, "1→1…8→8 = conforme ; 7 sans liaison = circuit ouvert ; 1→2 et 2→1 = paire inversée ; 1→3, 2→6, 3→1, 6→2 = paires croisées ; LED 4 et 5 ensemble = court-circuit ; continuité correcte mais diaphonie entre 3-6 et 4-5 = paire séparée (1 point chacun)."),
        ),
        correction=(
            "1→1 … 8→8 sans anomalie : câble droit conforme (du point de vue du câblage seulement).",
            "Une broche sans liaison : circuit ouvert (fil coupé, pas en butée, non serti).",
            "1→2 et 2→1 : les deux fils d'une même paire sont permutés à un bout, paire inversée.",
            "1→3, 2→6, 3→1, 6→2 : la paire 1-2 arrive sur 3-6 et inversement, paires croisées. C'est exactement un câble croisé A-B, faux ici puisqu'on attendait un câble droit.",
            "Deux LED qui s'allument ensemble : deux conducteurs se touchent, court-circuit.",
            "Continuité correcte mais diaphonie anormale entre 3-6 et 4-5 : paire séparée (split pair), invisible pour un testeur de continuité simple.",
        ),
        classification=Classification(
            categories=("Conforme (droit)", "Circuit ouvert", "Court-circuit", "Paire inversée", "Paires croisées", "Paire séparée"),
            elements=(
                "1→1, 2→2, 3→3, 4→4, 5→5, 6→6, 7→7, 8→8, aucune anomalie signalée.",
                "1→1 à 6→6 et 8→8 ; aucune liaison pour la broche 7.",
                "1→2, 2→1, toutes les autres broches droites.",
                "1→3, 2→6, 3→1, 6→2, broches 4, 5, 7 et 8 droites.",
                "Quand le principal envoie sur la broche 4, les LED 4 et 5 du bouchon s'allument en même temps.",
                "Continuité 1→1 … 8→8, mais le testeur de qualification signale une diaphonie anormale entre 3-6 et 4-5.",
            ),
            correct=(0, 1, 3, 4, 2, 5),
        ),
    ),
    PR06Item(
        key="E10",
        usage=USAGE_PRACTICE,
        title="Wiremap réussi, liaison instable : lire un rapport de qualification",
        question_type="document_analysis",
        requirement_ids=("AP-20", "AP-19", "AP-34"),
        kind=KIND_TESTER,
        context=(
            "Dans un entrepôt, le PC du quai de chargement perd souvent la connexion. Le câble, "
            "posé par le client lui-même, va du switch du bureau jusqu'au quai. Le testeur de "
            "continuité du client affichait « OK ». Tu passes un testeur de qualification sur le "
            "canal complet, cordons compris (document 1)."
        ),
        instructions=(
            "Explique pourquoi le testeur du client affichait « OK » malgré la panne.",
            "Interprète chaque ligne du rapport et indique la cause de l'instabilité.",
            "Propose deux solutions conformes.",
        ),
        documents=(
            _table(
                "Document 1 — Rapport du testeur de qualification (fictif)",
                ("Mesure", "Résultat", "Limite", "Verdict"),
                ("Wiremap", "1→1 … 8→8", "conforme T568B", "RÉUSSI"),
                ("Longueur", "128 m", "100 m (canal)", "ÉCHEC"),
                ("Perte d'insertion (atténuation)", "au-delà de la limite", "Cat5e, 100 MHz", "ÉCHEC"),
                ("NEXT (diaphonie proche)", "dans la limite", "Cat5e", "RÉUSSI"),
                ("Aptitude 1000BASE-T", "—", "—", "ÉCHEC"),
            ),
        ),
        criteria=(
            _c("Testeur du client", 0.5, "Un testeur de continuité ne vérifie que le chemin des fils (wiremap) : il ne mesure ni longueur, ni atténuation, ni diaphonie, ni aptitude à un débit."),
            _c("Lecture du rapport", 1.25, "Wiremap bon ; longueur 128 m > 100 m de canal ; l'atténuation dépasse la limite (conséquence de la longueur) ; NEXT correct ; le canal n'est pas apte au gigabit."),
            _c("Cause", 0.5, "Longueur excessive : le signal arrive trop affaibli, d'où les pertes de lien."),
            _c("Solutions", 0.75, "Raccourcir le canal sous 100 m (switch plus proche, nouveau tracé) ou couper la liaison par un équipement actif (switch intermédiaire dans un local adapté) ou passer en fibre ; retester ensuite."),
        ),
        correction=(
            "Le testeur du client ne contrôle que la continuité broche à broche : le wiremap est effectivement bon. Il ne dit rien de la longueur, de l'atténuation, de la diaphonie ni du débit possible.",
            "Rapport : wiremap conforme ; longueur 128 m, au-delà des 100 m d'un canal Ethernet cuivre ; la perte d'insertion (atténuation) dépasse la limite, conséquence directe de cette longueur ; la diaphonie proche (NEXT) est correcte ; le canal n'est pas apte au 1000BASE-T.",
            "Cause : le câble est trop long, le signal arrive trop affaibli et la liaison décroche.",
            "Solutions : ramener le canal sous 100 m (rapprocher le switch, nouveau tracé plus court) ou installer un équipement actif intermédiaire (switch dans un local ou un coffret adapté) qui régénère le signal, ou relier le quai en fibre optique. Retester ensuite le canal.",
        ),
    ),
    PR06Item(
        key="E11",
        usage=USAGE_PRACTICE,
        title="Choisir le câble de trois liaisons",
        question_type="long_answer",
        requirement_ids=("AP-18", "AP-19", "AP-20"),
        kind=KIND_CHOICE,
        context=(
            "Une imprimerie te demande un devis de câblage pour trois liaisons : A) huit postes de "
            "bureau en 1 Gb/s, câbles de 20 à 60 m dans un faux plafond ; B) deux postes dans "
            "l'atelier, à 1 m de gros moteurs de presses et de câbles d'alimentation, 1 Gb/s, 40 m ; "
            "C) liaison 10 Gb/s entre deux baies de la salle serveur, 75 m."
        ),
        instructions=(
            "Propose une catégorie et un type de câble (U/UTP, F/UTP, U/FTP ou S/FTP) pour chaque liaison et justifie.",
            "Indique pour la liaison B les conditions pour que le blindage soit efficace.",
        ),
        criteria=(
            _c("Liaison A", 0.75, "Cat5e ou Cat6 U/UTP suffit pour 1 Gb/s sur moins de 100 m ; Cat6 donne de la marge."),
            _c("Liaison B", 0.75, "Environnement perturbé : câble écranté ou blindé (F/UTP, U/FTP ou S/FTP), Cat6 par exemple, et éloigné des câbles d'alimentation (croisement à angle droit)."),
            _c("Liaison C", 0.75, "10 Gb/s sur 75 m : Cat6A (10GBASE-T sur 100 m) ; la Cat6 n'est garantie en 10 Gb/s que sur une longueur réduite."),
            _c("Conditions du blindage", 0.75, "Blindage continu de bout en bout : fiches, prises et panneau blindés de la même catégorie, mise à la terre selon l'installation ; sinon le blindage ne protège plus."),
        ),
        correction=(
            "A) 1 Gb/s sur 20 à 60 m dans un bureau : un câble Cat5e U/UTP suffit (1000BASE-T jusqu'à 100 m) ; une Cat6 U/UTP donne de la marge pour l'avenir.",
            "B) Les moteurs et câbles d'alimentation créent des parasites électromagnétiques : on choisit un câble écranté ou blindé (F/UTP, U/FTP ou S/FTP, par exemple Cat6), en le posant à distance des câbles d'alimentation et en les croisant à angle droit.",
            "C) 10 Gb/s sur 75 m : Cat6A, garantie pour le 10GBASE-T sur 100 m. Une Cat6 n'est prévue en 10 Gb/s que sur une longueur réduite (environ 37 à 55 m selon l'environnement).",
            "Le blindage n'est efficace que s'il est continu de bout en bout (fiches, keystones et panneau blindés, de la même catégorie) et relié à la terre selon les règles de l'installation ; un seul élément non blindé ou mal raccordé fait perdre l'intérêt du blindage.",
        ),
    ),
    PR06Item(
        key="E12",
        usage=USAGE_PRACTICE,
        title="Monobrin ou multibrin ?",
        question_type="classification",
        requirement_ids=("AP-18", "AP-20", "AP-36"),
        kind=KIND_CHOICE,
        context=(
            "Pour l'aménagement d'un nouveau bureau, ton responsable te remet une liste de câbles à "
            "commander. Le câble rigide (monobrin) est prévu pour l'installation fixe et le câble "
            "souple (multibrin) pour les cordons qu'on manipule. Il faut affecter chaque besoin."
        ),
        instructions=("Range chaque besoin dans le type de câble adapté.",),
        criteria=(
            _c("Classement", 5, "Monobrin : câble entre panneau de brassage et prise murale ; câble poinçonné sur un keystone ; câble de 60 m tiré dans une goulotte. Multibrin : cordon de brassage de 1 m dans la baie ; cordon de 3 m entre prise murale et portable (1 point chacun)."),
        ),
        correction=(
            "Le monobrin (conducteurs rigides) est fait pour l'installation fixe : câble permanent du panneau à la prise murale, tiré dans les chemins de câbles ou goulottes, et raccordé par poinçonnage sur keystone ou panneau.",
            "Le multibrin (conducteurs souples) supporte les manipulations répétées : cordons de brassage dans la baie et cordons de poste. On sertit des fiches adaptées au multibrin sur ces cordons ; une fiche pour multibrin sertie sur du monobrin fait de mauvais contacts.",
        ),
        classification=Classification(
            categories=("Monobrin (rigide)", "Multibrin (souple)"),
            elements=(
                "Câble entre le panneau de brassage et la prise murale du bureau.",
                "Cordon de brassage de 1 m entre le panneau et le switch, dans la baie.",
                "Câble raccordé par poinçonnage à l'arrière d'un keystone.",
                "Cordon de 3 m entre la prise murale et un PC portable souvent déplacé.",
                "Câble de 60 m tiré dans une goulotte le long du mur.",
            ),
            correct=(0, 1, 0, 1, 0),
        ),
    ),
    PR06Item(
        key="E13",
        usage=USAGE_PRACTICE,
        title="Relier deux PC directement",
        question_type="short_answer",
        requirement_ids=("AP-28", "AP-34"),
        kind=KIND_CHOICE,
        context=(
            "Un artisan veut copier des photos d'un ancien PC (carte réseau 10/100 Mb/s sans Auto "
            "MDI-X) vers son PC neuf (carte 1 Gb/s avec Auto MDI-X), sans switch, avec un câble "
            "direct. Après branchement, il dira que « le câble marche » si les voyants s'allument."
        ),
        instructions=(
            "Indique quel câble utiliser (droit ou croisé) et justifie en tenant compte des deux cartes.",
            "Explique pourquoi des voyants allumés ne suffisent pas pour échanger des fichiers et ce qu'il faut encore vérifier.",
        ),
        criteria=(
            _c("Choix du câble", 1, "Un seul côté suffit à faire l'Auto MDI-X : avec la carte neuve, un câble droit fonctionne ; un croisé A-B fonctionne aussi (et c'est le choix sûr si aucune des deux cartes ne fait l'Auto MDI-X). Lien à 100 Mb/s, vitesse de la carte la plus lente."),
            _c("Lien ≠ communication", 1, "Voyants = lien physique et négociation (vitesse, duplex) ; il faut encore une configuration IP compatible (même réseau, adresses différentes), le partage et les droits, et un test (ping, accès au partage)."),
        ),
        correction=(
            "Historiquement, deux PC se relient par un câble croisé (A-B) : l'émission de l'un (1-2) doit arriver sur la réception de l'autre (3-6). Ici la carte neuve dispose de l'Auto MDI-X : elle inverse elle-même émission et réception, donc un câble droit fonctionne aussi. Le câble croisé reste le choix sûr si aucune des deux cartes ne fait l'Auto MDI-X. Le lien s'établira à 100 Mb/s, la vitesse de la carte la plus lente.",
            "Les voyants prouvent seulement le lien physique et la négociation (vitesse, duplex). Pour échanger des fichiers, il faut encore une configuration IP compatible (deux adresses différentes du même réseau, par exemple 192.168.10.1 et 192.168.10.2 en /24), un partage avec les bons droits, puis un test (ping, ouverture du partage).",
        ),
    ),
    PR06Item(
        key="E14",
        usage=USAGE_PRACTICE,
        title="Remettre en ordre la fabrication d'un cordon",
        question_type="ordering",
        requirement_ids=("AP-34",),
        kind=KIND_PROCEDURE,
        context=(
            "Un stagiaire a noté sur des fiches cartonnées les étapes de fabrication d'un cordon "
            "RJ45 vues en atelier, mais les fiches se sont mélangées. Tu dois les remettre dans "
            "l'ordre pour une extrémité, du choix du matériel au test final du cordon."
        ),
        instructions=("Remets les étapes dans l'ordre d'exécution.",),
        criteria=(
            _c("Ordre", 2, "Préparer (matériel compatible, manchons enfilés), couper et dénuder, ranger, recouper, insérer, contrôler, sertir, tester."),
        ),
        correction=(
            "Ordre : " + " ; ".join(f"{i}. {name}" for i, (name, _d) in enumerate(CRIMP_STEPS, start=1)) + ".",
            "Pièges : enfiler les manchons après le sertissage (impossible ensuite), recouper avant de ranger (fils de longueurs inégales), sertir sans avoir contrôlé l'ordre et la butée, livrer sans test.",
        ),
        ordering=Ordering(
            steps=tuple(f"{CRIMP_STEPS[i][0]} : {CRIMP_STEPS[i][1]}" for i in E14_SHOWN),
            correct=tuple(E14_SHOWN.index(i) for i in range(len(CRIMP_STEPS))),
        ),
    ),
    PR06Item(
        key="E15",
        usage=USAGE_PRACTICE,
        title="Poser une prise murale et tester le lien permanent",
        question_type="long_answer",
        requirement_ids=("AP-34", "AP-36"),
        kind=KIND_PROCEDURE,
        context=(
            "Dans une agence immobilière, un nouveau bureau doit être raccordé. Le câble Cat6 U/UTP "
            "monobrin est déjà tiré depuis le panneau de brassage de la baie jusqu'au futur boîtier "
            "mural (45 m). L'installation existante est en T568B, et le port 14 du panneau est libre."
        ),
        instructions=(
            "Rédige la procédure de raccordement du keystone de la prise murale, outils compris.",
            "Décris les tests et l'étiquetage qui terminent l'intervention.",
        ),
        criteria=(
            _c("Préparation", 0.5, "Keystone Cat6 adapté au monobrin, outil de poinçonnage, dénudeur, coupe-câble ; vérifier la norme de l'installation (T568B)."),
            _c("Raccordement", 1.5, "Dénuder sans entailler, garder les torsades jusqu'au plus près des contacts, placer chaque fil selon le repère B du keystone, poinçonner (outil d'insertion), couper l'excédent, serrer la gaine, clipser dans le boîtier."),
            _c("Tests", 1, "Tester le lien permanent (panneau port 14 → prise) au testeur : wiremap, longueur ; si possible qualification ; puis cordon et poste : lien et vitesse."),
            _c("Étiquetage et traçabilité", 1, "Même repère sur la prise et le port 14 du panneau, plan ou tableau de brassage mis à jour, résultats de test notés."),
        ),
        correction=(
            "Préparation : keystone Cat6 pour câble monobrin, outil de poinçonnage (insertion), dénudeur, coupe-câble, testeur. On vérifie que l'installation est en T568B pour câbler le keystone avec le même repère que le panneau.",
            "Raccordement : dénuder la gaine sans entailler les conducteurs ; garder les torsades jusqu'au plus près des contacts ; placer chaque fil dans la fente indiquée par le code couleur « B » imprimé sur le keystone ; poinçonner chaque fil avec l'outil ; couper l'excédent ; serrer la gaine (collier ou capot) pour qu'elle ne tire pas sur les fils ; clipser le keystone dans le boîtier.",
            "Tests : brancher le testeur entre le port 14 du panneau et la prise : wiremap conforme, longueur cohérente (environ 45 m) ; si l'agence a un testeur de qualification, vérifier l'aptitude au débit voulu. Puis brancher le PC avec un cordon et vérifier le voyant de lien et la vitesse négociée.",
            "Étiquetage : même repère sur la prise et sur le port 14 du panneau ; mise à jour du tableau de brassage ; résultats des tests consignés dans le compte rendu.",
        ),
    ),
    PR06Item(
        key="E16",
        usage=USAGE_PRACTICE,
        title="Compte rendu après le remplacement d'un cordon",
        question_type="long_answer",
        requirement_ids=("AP-34", "AP-37", "AP-C01"),
        kind=KIND_PROCEDURE,
        context=(
            "À l'accueil d'une mutuelle, le PC n'avait plus de réseau. Tu as constaté un cordon de "
            "poste écrasé par un pied de bureau ; le testeur a indiqué un circuit ouvert sur la "
            "broche 3. Tu as fabriqué un nouveau cordon droit T568B de 3 m, testé, puis branché."
        ),
        instructions=(
            "Rédige le compte rendu d'intervention en reprenant les rubriques attendues (besoin, norme, schéma, outils, tests avant et après, résultats, défaut corrigé, validation).",
        ),
        criteria=(
            _c("Besoin et constat", 0.5, "PC de l'accueil sans réseau ; cordon écrasé constaté."),
            _c("Norme et schéma", 0.75, "Cordon droit T568B aux deux bouts, ordre des 8 fils cité ou schéma joint."),
            _c("Outils et tests avant", 0.75, "Testeur de câble : circuit ouvert broche 3 sur l'ancien cordon ; pince à sertir, dénudeur, coupe-câble, fiches adaptées au multibrin."),
            _c("Tests après et validation", 1, "Nouveau cordon : wiremap 1→1 … 8→8 réussi ; PC : lien, vitesse négociée, accès au réseau confirmé avec l'utilisateur."),
            _c("Défaut corrigé et recommandation", 1, "Cause : cordon écrasé ; cordon remplacé ; recommandation : faire passer le cordon hors des pieds de bureau (goulotte, passe-câble)."),
        ),
        correction=(
            "Besoin : le PC de l'accueil n'a plus d'accès au réseau. Constat : cordon de poste écrasé par un pied de bureau.",
            "Test avant : testeur de câble sur l'ancien cordon, circuit ouvert sur la broche 3. Outils : testeur, pince à sertir, dénudeur, coupe-câble, fiches 8P8C pour câble multibrin.",
            "Norme : cordon droit T568B aux deux bouts (" + T568B_TEXT + ").",
            "Test après : nouveau cordon, wiremap 1→1 … 8→8 réussi ; sur le PC, voyant de lien allumé, liaison à 1 Gb/s, accès aux ressources confirmé avec l'utilisatrice.",
            "Défaut corrigé : cordon écrasé remplacé. Recommandation : faire passer le cordon dans une goulotte ou un passe-câble, hors de portée des pieds de bureau. Intervention clôturée.",
        ),
    ),
)


# =============================================================================================
# Mini-examen : 10 questions à réponse libre, 2 points chacune (note sur 20)
# =============================================================================================

X02_LINKS = links_between(T568A, T568B)

EXAM_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="X01",
        usage=USAGE_EXAM,
        title="Raccorder une prise à une installation en T568A",
        question_type="short_answer",
        requirement_ids=("AP-34",),
        kind=KIND_SCENARIO,
        context=(
            "Dans une ancienne école, toutes les prises murales et le panneau de brassage sont "
            "câblés en T568A (repère inscrit dans la baie). Tu dois remplacer un keystone cassé et "
            "le raccorder comme les autres. Le keystone neuf porte les repères A et B."
        ),
        instructions=(
            "Donne l'ordre des couleurs T568A de la broche 1 à la broche 8 et précise quelle paire occupe la position 3-6.",
            "Explique pourquoi il ne faut pas câbler ce keystone en T568B « parce que c'est plus courant ».",
        ),
        criteria=(
            _c("Ordre T568A", 1.25, "T568A : " + T568A_TEXT + " ; paire orange sur 3-6."),
            _c("Pourquoi pas B", 0.75, "Le panneau est en A : une prise en B donnerait un lien permanent croisé (A-B) et non conforme ; on respecte la norme de l'installation."),
        ),
        correction=(
            "T568A : " + T568A_TEXT + ". La position 3-6 est occupée par la paire orange (blanc/orange en 3, orange en 6).",
            "L'autre bout du câble permanent (panneau) est en T568A : câbler la prise en T568B ferait de ce lien un câble croisé A-B, non conforme à l'installation et source de confusion à la maintenance. On câble toujours comme l'installation existante.",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Un cordon « droit » qui ne l'est pas",
        question_type="document_analysis",
        requirement_ids=("AP-34", "AP-28"),
        kind=KIND_SCENARIO,
        context=(
            "Dans une PME, un cordon étiqueté « droit » relie un PC récent à un switch récent et le "
            "réseau fonctionne. En faisant l'inventaire, tu passes ce cordon au testeur de câble "
            "(document 1) et le résultat t'étonne."
        ),
        instructions=(
            "Indique quel type de câble montre le relevé et comment le lien peut fonctionner malgré tout.",
            "Dis ce que tu fais de ce cordon et pourquoi.",
        ),
        documents=(
            _table(
                "Document 1 — Relevé du testeur de câble (fictif)",
                ("Broche côté testeur", "Broche côté bouchon"),
                *((str(a), str(b)) for a, b in X02_LINKS),
            ),
        ),
        criteria=(
            _c("Type de câble", 0.75, "1→3, 2→6, 3→1, 6→2, le reste droit : câble croisé (T568A à un bout, T568B à l'autre), et non droit."),
            _c("Pourquoi le lien marche", 0.75, "Le PC ou le switch récent fait l'Auto MDI-X : il inverse émission et réception, le croisé fonctionne aussi."),
            _c("Décision", 0.5, "Le cordon est mal étiqueté : le réétiqueter « croisé » ou le remplacer par un cordon droit conforme, pour éviter une panne avec un équipement sans Auto MDI-X."),
        ),
        correction=(
            "Le relevé montre 1→3, 2→6, 3→1, 6→2 et les broches 4, 5, 7, 8 droites : c'est un câble croisé (T568A d'un côté, T568B de l'autre), pas un câble droit.",
            "Le lien fonctionne parce que le PC ou le switch récent dispose de l'Auto MDI-X : il détecte le croisement et inverse lui-même émission et réception.",
            "Le cordon est mal étiqueté. On le réétiquette « croisé » ou, mieux, on le remplace par un cordon droit conforme : avec un équipement sans Auto MDI-X, il provoquerait une panne difficile à comprendre.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="Lien à 100 Mb/s au lieu de 1 Gb/s",
        question_type="short_answer",
        requirement_ids=("AP-34", "AP-19", "AP-37"),
        kind=KIND_SCENARIO,
        context=(
            "Dans un bureau d'études, un poste neuf (carte réseau 1 Gb/s) est branché par un cordon "
            "fabriqué sur place à une prise murale reliée à un switch 1 Gb/s. La carte réseau "
            "indique « 100 Mb/s, duplex intégral » alors que les postes voisins sont à 1 Gb/s."
        ),
        instructions=(
            "Explique pourquoi un défaut de câblage peut limiter le lien à 100 Mb/s sans le couper.",
            "Donne, dans l'ordre, trois vérifications à faire pour trouver la cause.",
        ),
        criteria=(
            _c("Explication", 1, "Le 100 Mb/s n'utilise que les paires 1-2 et 3-6, le 1 Gb/s les quatre paires : si 4-5 ou 7-8 est ouverte ou défectueuse, la négociation retombe à 100 Mb/s."),
            _c("Vérifications ordonnées", 1, "Tester le cordon (wiremap, paires 4-5 et 7-8) ; échanger avec un cordon connu bon ; tester le lien permanent et le port (autre port, réglages de vitesse forcée, pilote) ; aussi la catégorie du câble."),
        ),
        correction=(
            "Le 100BASE-TX n'utilise que deux paires (1-2 et 3-6) ; le 1000BASE-T utilise les quatre paires. Si l'une des paires 4-5 ou 7-8 est coupée ou mal sertie, les cartes ne peuvent pas établir le gigabit et se rabattent souvent sur 100 Mb/s : le lien existe, mais moins rapide.",
            "Vérifications : 1) passer le cordon fabriqué au testeur (circuit ouvert sur 4, 5, 7 ou 8 ?) ; 2) le remplacer par un cordon connu bon et observer la vitesse ; 3) tester le lien permanent prise → panneau, puis vérifier le port du switch et les réglages de la carte (vitesse non forcée à 100 Mb/s, pilote) et la catégorie des éléments.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="Erreurs réseau avec des cordons « testés »",
        question_type="document_analysis",
        requirement_ids=("AP-34", "AP-20"),
        kind=KIND_SCENARIO,
        context=(
            "Dans une salle de formation, les postes perdent souvent la connexion et le switch "
            "compte beaucoup d'erreurs sur leurs ports. Tous les cordons ont été fabriqués par le "
            "même stagiaire et réussissent le test de continuité. Le document 1 montre l'ordre lu "
            "aux deux bouts de l'un d'eux."
        ),
        instructions=(
            "Nomme le défaut et explique pourquoi le test de continuité ne le révèle pas.",
            "Indique la correction et l'outil de test qui permet de valider les cordons refaits.",
        ),
        documents=(
            _table(
                "Document 1 — Ordre des fils, identique aux deux bouts (fiche vue côté contacts, broche 1 à gauche)",
                ("Broche", "Fil"),
                *((str(i), wire_label(w)) for i, w in enumerate(SEQUENTIAL_WRONG, start=1)),
            ),
        ),
        criteria=(
            _c("Défaut", 0.75, "Paires séparées (split pair) : les positions 3-6 et 4-5 reçoivent des fils de paires différentes (vert en 4, bleu en 6)."),
            _c("Pourquoi le test passe", 0.5, "Les deux bouts sont identiques : continuité 1→1 … 8→8 ; le testeur de continuité ne vérifie pas l'appariement des paires torsadées."),
            _c("Correction et validation", 0.75, "Refaire les fiches en T568B (ou T568A) aux deux bouts ; valider avec un testeur de qualification ou de certification qui détecte les paires séparées (diaphonie)."),
        ),
        correction=(
            "Les fils sont rangés paire par paire (1-2, 3-4, 5-6, 7-8). Les positions 3-6 et 4-5 reçoivent chacune deux fils de paires différentes : ce sont des paires séparées (split pair). La diaphonie et les parasites augmentent, d'où les erreurs et les coupures.",
            "Les deux bouts sont faits de la même façon : la continuité broche à broche est parfaite et le testeur de continuité affiche « réussi ». Il ne contrôle pas que les deux broches d'une position sont sur une même paire torsadée.",
            "Correction : refaire les fiches dans l'ordre T568B (3 blanc/vert, 4 bleu, 5 blanc/bleu, 6 vert) aux deux bouts, puis valider chaque cordon avec un testeur capable de détecter les paires séparées (qualification ou certification).",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Choisir la catégorie d'une liaison 10 Gb/s",
        question_type="short_answer",
        requirement_ids=("AP-19", "AP-20"),
        kind=KIND_SCENARIO,
        context=(
            "Une société de montage vidéo veut relier sa baie de stockage au switch de l'étage en "
            "10 Gb/s, en cuivre. Le trajet du câble permanent mesure 82 m, plus deux cordons de 3 m. "
            "Le fournisseur propose du Cat6, moins cher et plus fin que le Cat6A."
        ),
        instructions=(
            "Indique la catégorie à retenir et justifie avec la longueur du canal.",
            "Précise ce qui doit être de la même catégorie que le câble, et comment valider l'installation.",
        ),
        criteria=(
            _c("Catégorie", 1, "Canal de 88 m : Cat6A (10GBASE-T sur 100 m) ; Cat6 seulement sur une longueur réduite (environ 37 à 55 m), insuffisante ici."),
            _c("Composants et validation", 1, "Prises, panneau, cordons et fiches de catégorie 6A ; validation par un testeur de certification du lien selon la catégorie."),
        ),
        correction=(
            "Le canal mesure 82 + 3 + 3 = 88 m. La Cat6A est garantie pour le 10GBASE-T jusqu'à 100 m ; la Cat6 ne l'est que sur une longueur réduite (environ 37 à 55 m selon l'environnement). Il faut donc du Cat6A.",
            "Toute la chaîne doit être de la même catégorie : câble, keystones, panneau, cordons et fiches Cat6A ; un seul composant de catégorie inférieure limite l'ensemble. On valide avec un testeur de certification (mesures comparées aux limites Cat6A).",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Procédure écrite : fabriquer un cordon droit",
        question_type="long_answer",
        requirement_ids=("AP-34",),
        kind=KIND_SCENARIO,
        context=(
            "Ton responsable te demande une fiche de procédure pour les nouveaux techniciens : "
            "fabriquer un cordon droit T568B de 2 m à partir d'une bobine de câble Cat6 U/UTP "
            "multibrin, puis le contrôler avant de le remettre à un utilisateur."
        ),
        instructions=(
            "Rédige la procédure, du matériel au test, en ordonnant les étapes et en citant les points de contrôle.",
        ),
        criteria=(
            _c("Matériel", 0.4, "Fiches 8P8C Cat6 pour multibrin, manchons, coupe-câble, dénudeur, pince à sertir, testeur."),
            _c("Préparation des fils", 0.6, "Manchons enfilés, dénuder sans entailler, détorsader le minimum, ranger en T568B (ordre cité), aplatir, recouper droit pour que la gaine entre dans la fiche."),
            _c("Insertion et sertissage", 0.5, "Contacts vers soi, broche 1 à gauche, fils en butée, contrôle visuel de l'ordre, gaine sous la patte, sertissage complet, puis l'autre bout en T568B."),
            _c("Test", 0.5, "Testeur de câble : 1→1 … 8→8 avant remise ; étiquette ou note du résultat."),
        ),
        correction=(
            "Matériel : câble Cat6 multibrin, fiches 8P8C Cat6 pour multibrin, manchons, coupe-câble, dénudeur, pince à sertir, testeur.",
            "Étapes : 1) enfiler les manchons ; 2) couper franc et dénuder 25 à 30 mm sans entailler ; 3) détorsader le minimum et ranger en T568B (" + T568B_TEXT + ") ; 4) aplatir et recouper droit à environ 12-13 mm ; 5) fiche contacts vers soi, broche 1 à gauche, pousser les fils jusqu'en butée ; 6) contrôler l'ordre à travers la fiche et la gaine sous la patte de maintien ; 7) sertir complètement ; 8) même chose à l'autre bout, en T568B aussi pour un cordon droit.",
            "Test : testeur de câble, 1→1 … 8→8 réussi avant toute remise ; noter le résultat.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Diaphonie mesurée côté panneau",
        question_type="document_analysis",
        requirement_ids=("AP-20", "AP-34", "AP-36"),
        kind=KIND_SCENARIO,
        context=(
            "Après l'installation de 24 prises Cat6 dans un open space, la certification d'un lien "
            "échoue. Le technicien qui a poinçonné le panneau avait détorsadé largement les paires "
            "« pour gagner du temps ». Le document 1 donne le résultat de ce lien."
        ),
        instructions=(
            "Interprète le rapport et relie l'échec à la façon dont le panneau a été raccordé.",
            "Décris la correction et la validation.",
        ),
        documents=(
            _table(
                "Document 1 — Certification du lien permanent n° 17 (fictif)",
                ("Mesure", "Résultat", "Verdict"),
                ("Wiremap", "1→1 … 8→8", "RÉUSSI"),
                ("Longueur", "38 m", "RÉUSSI"),
                ("Perte d'insertion", "dans la limite Cat6", "RÉUSSI"),
                ("NEXT, extrémité panneau", "hors limite (paires 3-6 / 4-5)", "ÉCHEC"),
                ("NEXT, extrémité prise", "dans la limite", "RÉUSSI"),
                ("Résultat global", "—", "ÉCHEC"),
            ),
        ),
        criteria=(
            _c("Lecture", 0.75, "Câblage, longueur et atténuation corrects ; seule la diaphonie proche (NEXT) échoue, côté panneau."),
            _c("Lien avec le raccordement", 0.5, "Détorsader largement supprime l'effet de la torsade au point de raccordement : la diaphonie augmente là où les paires sont détorsadées (côté panneau)."),
            _c("Correction et validation", 0.75, "Refaire le raccordement du port 17 au panneau en gardant les torsades jusqu'aux contacts (≈ 13 mm détorsadés au plus) ; recertifier le lien ; contrôler les autres ports raccordés par ce technicien."),
        ),
        correction=(
            "Le câblage (wiremap), la longueur et l'atténuation sont bons. Seule la diaphonie proche (NEXT) mesurée à l'extrémité panneau échoue.",
            "La torsade protège chaque paire des signaux voisins. En détorsadant largement les paires pour les poinçonner, le technicien a supprimé cette protection juste avant les contacts : la diaphonie augmente précisément à cette extrémité.",
            "Correction : refaire le raccordement de ce port au panneau en conservant les torsades jusqu'au plus près des contacts (environ 13 mm détorsadés au plus), puis recertifier le lien. Les autres ports raccordés de la même façon sont à contrôler.",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Continuité, qualification ou certification ?",
        question_type="short_answer",
        requirement_ids=("AP-34", "AP-20"),
        kind=KIND_SCENARIO,
        context=(
            "Un client a fait poser 40 prises Cat6A dans ses nouveaux locaux et veut une preuve que "
            "l'installation supporte le 10 Gb/s. L'installateur lui présente les résultats de son "
            "petit testeur à LED : « tout est vert, 1 à 8 sur chaque prise »."
        ),
        instructions=(
            "Explique pourquoi ces résultats ne prouvent pas ce que le client demande.",
            "Indique le type de testeur et les mesures qui apportent cette preuve.",
        ),
        criteria=(
            _c("Limites du testeur à LED", 1, "Il ne vérifie que la continuité broche à broche : ni paires séparées, ni longueur, ni atténuation, ni diaphonie, donc ni la catégorie ni le débit."),
            _c("Preuve attendue", 1, "Testeur de certification : mesures (longueur, perte d'insertion, NEXT et autres diaphonies, affaiblissement de réflexion) comparées aux limites Cat6A, rapport par lien ; un testeur de qualification dit si un débit passe mais ne certifie pas la catégorie."),
        ),
        correction=(
            "Un testeur à LED ne vérifie que la continuité broche à broche (wiremap) : il ne voit ni les paires séparées, ni la longueur, ni l'atténuation, ni la diaphonie. Il ne prouve donc ni la catégorie Cat6A ni l'aptitude au 10 Gb/s.",
            "La preuve demandée est un rapport de testeur de certification : pour chaque lien, longueur, perte d'insertion, diaphonies (NEXT…), affaiblissement de réflexion, comparés aux limites Cat6A. Un testeur de qualification indique si un débit donné passe, mais ne certifie pas la catégorie.",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="Lien établi, mais pas de communication",
        question_type="short_answer",
        requirement_ids=("AP-28", "AP-34", "AP-37"),
        kind=KIND_SCENARIO,
        context=(
            "Pour un test d'atelier, tu relies deux PC anciens (cartes 10/100 Mb/s sans Auto MDI-X) "
            "avec un câble croisé que tu viens de fabriquer et de tester. Les voyants de lien "
            "s'allument à 100 Mb/s, mais le ping de l'un vers l'autre échoue."
        ),
        instructions=(
            "Explique ce que prouvent les voyants allumés et ce qu'ils ne prouvent pas.",
            "Indique les vérifications suivantes, en dehors du câble.",
        ),
        criteria=(
            _c("Ce que prouvent les voyants", 1, "Lien physique correct et négociation réussie (100 Mb/s) : le câble croisé convient ; ils ne prouvent pas la configuration IP ni l'autorisation du trafic."),
            _c("Vérifications suivantes", 1, "Adresses IP : même réseau et masque, adresses différentes (ipconfig / ip addr) ; pare-feu qui bloque le ping ; puis nouveau test."),
        ),
        correction=(
            "Les voyants prouvent le lien physique (câble et cartes) et la négociation de la vitesse et du duplex : le croisé fait son travail. Ils ne disent rien de la configuration IP ni du filtrage.",
            "Vérifications : adresses IP des deux PC (même réseau, même masque, adresses différentes) avec ipconfig ou ip addr ; pare-feu qui peut refuser le ping ; puis nouveau test de ping. Le câble n'est plus en cause.",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Compte rendu : prise murale réparée",
        question_type="long_answer",
        requirement_ids=("AP-34", "AP-36", "AP-C01"),
        kind=KIND_SCENARIO,
        context=(
            "Dans une maison médicale, le poste du secrétariat n'avait plus de réseau. Le cordon "
            "testé était bon ; le lien permanent (prise 2.07 → panneau port 7) présentait un circuit "
            "ouvert sur la broche 5 : un fil était sorti du keystone. Tu as refait le keystone en "
            "T568B, comme l'installation."
        ),
        instructions=(
            "Rédige le compte rendu de cette intervention : besoin, diagnostic et tests avant, norme, outils, action, tests après, validation et recommandation.",
        ),
        criteria=(
            _c("Besoin et diagnostic", 0.5, "Poste sans réseau ; cordon testé bon ; lien permanent prise 2.07 → port 7 : circuit ouvert broche 5, fil sorti du keystone."),
            _c("Norme, outils, action", 0.5, "Keystone refait en T568B comme l'installation, torsades conservées, outil de poinçonnage ; testeur."),
            _c("Tests après et validation", 0.5, "Lien permanent retesté conforme (wiremap 1→1 … 8→8, longueur) ; poste reconnecté, vitesse négociée, accès confirmé avec l'utilisateur."),
            _c("Recommandation et traçabilité", 0.5, "Cause possible (traction sur le câble, gaine mal serrée) et recommandation ; étiquettes vérifiées, intervention consignée."),
        ),
        correction=(
            "Besoin : poste du secrétariat sans réseau. Diagnostic : cordon testé bon ; lien permanent prise 2.07 → panneau port 7 testé : circuit ouvert sur la broche 5 ; un fil était sorti du keystone.",
            "Action : keystone refait en T568B, comme l'installation, torsades conservées jusqu'aux contacts, gaine serrée ; outils : outil de poinçonnage, dénudeur, testeur.",
            "Tests après : lien permanent conforme (1→1 … 8→8, longueur cohérente) ; poste reconnecté, lien et vitesse négociée corrects, accès au réseau confirmé avec la secrétaire.",
            "Recommandation : la gaine n'était pas maintenue et le câble avait subi une traction ; vérifier la fixation des boîtiers voisins. Étiquettes 2.07 / port 7 contrôlées, intervention consignée.",
        ),
    ),
)

ALL_ITEMS: tuple[PR06Item, ...] = PRACTICE_ITEMS + EXAM_ITEMS
EXAM_TOTAL_POINTS = 20


def validate_items() -> list[str]:
    """Contrôles éditoriaux : format d'exercice du socle (#192), 2 points par question du
    mini-examen, réponses libres à l'examen, données des classements et remises en ordre."""
    errors: list[str] = []
    for item in ALL_ITEMS:
        errors += [f"{item.key} : {e}" for e in validate_exercise(item.as_exercise())]
        if item.question_type == "classification" and (
            item.classification is None
            or len(item.classification.correct) != len(item.classification.elements)
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
    for item in EXAM_ITEMS:
        if abs(item.total_points - 2) > 1e-9:
            errors.append(f"{item.key} : une question du mini-examen vaut 2 points.")
        if item.question_type not in ("short_answer", "long_answer", "document_analysis"):
            errors.append(f"{item.key} : le mini-examen n'accepte que des réponses libres.")
    return errors
