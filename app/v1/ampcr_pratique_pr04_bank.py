"""PR04 « Reconditionnement, entretien et contrôles après intervention » — exercices corrigés
et mini-examen (ticket #205).

Même organisation que les cours pratiques déjà publiés (`app.v1.ampcr_pratique_pr06_bank`, dont
ce module réutilise le type d'item et la règle d'acceptation) :
- `PRACTICE_ITEMS` : 16 exercices corrigés affichés dans le cours (corrigé replié) et proposés
  dans « S'entraîner » — remises en ordre, décisions de protection des données, choix de la
  technique d'effacement, lecture de relevés (SMART, batterie, températures), formulaires de
  réception et de remise, tri des déchets, rapport à corriger ;
- `EXAM_ITEMS` : les 10 questions du mini-examen noté /20 (2 points chacune), réponses libres,
  uniquement dans « Examen blanc », jamais affichées dans le cours.

Les situations, fiches et relevés sont **fictifs** ; les procédures, décisions, techniques
d'effacement et verdicts viennent de `app.v1.ampcr_pratique_pr04_figures` (mêmes données que
les schémas). Aucune manipulation sous tension ni ouverture de bloc d'alimentation n'est
demandée.
"""

from app.v1.ampcr_pratique_format import ExerciseDocument, ScoringCriterion, validate_exercise
from app.v1.ampcr_pratique_pr04_figures import (
    CLEAN_STEPS,
    DEST_NEW_USER,
    DEST_RECYCLING,
    DEST_SAME_CLIENT,
    FIRMWARE_STEPS,
    MEDIA_HDD,
    MEDIA_NVME_SSD,
    MEDIA_SATA_SSD,
    OP_ERASE,
    OP_RECON,
    OP_REPAIR,
    OP_RESET,
    RECON_STEPS,
    TEMP_ALERT_MARGIN,
    WASTE_BATTERY,
    WASTE_DEEE,
    WASTE_ITEMS,
    WASTE_PAPER,
    battery_health_percent,
    battery_verdict,
    data_decision,
    erase_method_ok,
    smart_lines,
    smart_verdict,
    temperature_verdict,
)
from app.v1.ampcr_pratique_pr06_bank import (
    USAGE_EXAM,
    USAGE_PRACTICE,
    Classification,
    Ordering,
    PR06Item,
)

PR04_CODE = "PR04"

KIND_ORDER = "ordonnancement"
KIND_DATA = "protection des données"
KIND_TESTS = "contrôles et relevés"
KIND_FORM = "formulaire et traçabilité"
KIND_ERROR = "repérage d'erreurs"

# Exigence officielle du cours (matrice #192, audit #236) : chaque item la cite.
REQ = frozenset({"AP-14"})


def _c(label: str, points: float, expected: str) -> ScoringCriterion:
    return ScoringCriterion(label=label, points=points, expected=expected)


def _table(title: str, header: tuple[str, ...], *rows: tuple[str, ...]) -> ExerciseDocument:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return ExerciseDocument(title=title, kind="tableau", content_text="\n".join(lines))


def _console(title: str, *lines: str) -> ExerciseDocument:
    return ExerciseDocument(title=title, kind="console", content_text="\n".join(lines))


def _shuffled_ordering(steps: tuple[str, ...], shown: tuple[int, ...]) -> Ordering:
    """`shown` = ordre d'affichage (indices dans `steps`, la bonne suite) ; renvoie l'ordre
    attendu exprimé en positions d'affichage, comme le type « ordering » le demande."""
    displayed = tuple(steps[i] for i in shown)
    correct = tuple(shown.index(i) for i in range(len(steps)))
    return Ordering(steps=displayed, correct=correct)


def _labels(steps: tuple[tuple[str, str], ...]) -> tuple[str, ...]:
    return tuple(f"{label} — {detail}" for label, detail in steps)


# --- Données calculées réutilisées dans les énoncés et les corrigés --------------------------

E01_STEPS = _labels(RECON_STEPS)
E02_STEPS = _labels(CLEAN_STEPS)
E03_STEPS = _labels(FIRMWARE_STEPS)

E04_CATEGORIES = (OP_REPAIR, OP_RECON, OP_RESET, OP_ERASE)
E04_ELEMENTS: tuple[tuple[str, str], ...] = (
    ("Remplacer le ventilateur bruyant du portable d'une cliente, qui garde ses fichiers", OP_REPAIR),
    ("Préparer dix PC d'une entreprise pour les donner à une école : tests, nettoyage, SSD, système neuf", OP_RECON),
    ("« Réinitialiser ce PC » à la demande du client qui garde l'ordinateur", OP_RESET),
    ("Rendre illisible le SSD d'un portable de location avant son retour, avec certificat", OP_ERASE),
    ("Changer l'écran fêlé d'un portable, données conservées", OP_REPAIR),
    ("Réinstaller le système d'usine pour le même client après une infection, sauvegarde restaurée", OP_RESET),
    ("Rendre illisibles les disques de PC déclassés avant leur recyclage, support par support", OP_ERASE),
    ("Remettre en état un PC d'occasion avant revente : diagnostic, pièces usées, mises à jour, tests", OP_RECON),
)

E05_CATEGORIES = (
    "Effacement sécurisé autorisé",
    "Sauvegarder et vérifier d'abord",
    "Ne rien effacer : accord écrit du propriétaire nécessaire",
    "Conserver les données",
)
_E05_DECISION_TO_CATEGORY = {
    "Effacement sécurisé adapté au support, vérifié et certifié": 0,
    "Effacement sécurisé ou destruction physique du support, avec trace": 0,
    "Sauvegarder et vérifier la copie avant toute intervention sur le disque": 1,
    "Ne rien effacer : obtenir d'abord l'accord écrit du propriétaire": 2,
    "Conserver les données (sauvegarde vérifiée), aucun effacement": 3,
}
# (situation, accord écrit du propriétaire, veut garder ses données, copie vérifiée, destination)
E05_CASES: tuple[tuple[str, bool, bool, bool, str], ...] = (
    ("PC d'une PME donné à une association ; le gérant a signé l'accord d'effacement, copie faite et relue",
     True, True, True, DEST_NEW_USER),
    ("Le fils d'un client téléphone : « effacez tout sur le PC de mon père, il est d'accord »",
     False, False, False, DEST_NEW_USER),
    ("Une cliente signe pour une réinstallation, veut garder ses photos ; aucune sauvegarde n'existe",
     True, True, False, DEST_SAME_CLIENT),
    ("Disque hors d'usage d'un client qui a signé l'accord de recyclage et n'a besoin d'aucun fichier",
     True, False, False, DEST_RECYCLING),
    ("Réparation d'un portable pour le même client, accord signé, sauvegarde vérifiée sur disque externe",
     True, True, True, DEST_SAME_CLIENT),
    ("PC repris à l'achat d'un neuf, à revendre ; le vendeur pense que le propriétaire est « sûrement d'accord »",
     False, False, False, DEST_NEW_USER),
)
E05_CORRECT = tuple(
    _E05_DECISION_TO_CATEGORY[
        data_decision(owner_consent=c, wants_data=w, backup_verified=b, destination=d)
    ]
    for _s, c, w, b, d in E05_CASES
)

E06_CATEGORIES = ("Technique adaptée", "Technique insuffisante")
E06_ELEMENTS: tuple[tuple[str, str, str], ...] = (
    ("Disque dur : formatage rapide avant revente", MEDIA_HDD, "formatage rapide"),
    ("Disque dur : écrasement complet du disque, une passe, puis vérification", MEDIA_HDD,
     "écrasement complet du disque (une passe suffit sur un disque récent)"),
    ("SSD SATA : sept passes d'écrasement avec un logiciel de PC", MEDIA_SATA_SSD,
     "passes d'écrasement multiples avec un logiciel de PC"),
    ("SSD SATA : commande d'effacement sécurisé lancée par l'outil du fabricant", MEDIA_SATA_SSD,
     "commande d'effacement sécurisé ou Sanitize du SSD (outil du fabricant ou firmware)"),
    ("SSD NVMe : défragmentation puis suppression des fichiers", MEDIA_NVME_SSD, "défragmentation"),
    ("SSD NVMe chiffré : effacement cryptographique (clé de chiffrement détruite)", MEDIA_NVME_SSD,
     "effacement cryptographique si le SSD est chiffré (clé détruite)"),
    ("Disque dur : suppression des partitions dans l'installateur", MEDIA_HDD, "suppression des partitions"),
    ("Disque dur hors d'usage : destruction physique par une filière agréée", MEDIA_HDD,
     "destruction physique par une filière agréée (disque hors d'usage)"),
)
E06_CORRECT = tuple(0 if erase_method_ok(media, tech) else 1 for _l, media, tech in E06_ELEMENTS)

E07_SMART: tuple[tuple[str, int], ...] = (
    ("Power_On_Hours", 21040),
    ("Reallocated_Sector_Ct", 0),
    ("Current_Pending_Sector", 0),
    ("Offline_Uncorrectable", 0),
    ("Temperature_Celsius", 36),
)
E07_NVME: tuple[tuple[str, int], ...] = (
    ("Percentage_Used", 104),
    ("Available_Spare", 100),
    ("Available_Spare_Threshold", 10),
    ("Media_Errors", 0),
    ("Temperature_Celsius", 41),
)
E07_HDD_VERDICT = smart_verdict(dict(E07_SMART))  # bon
E07_NVME_VERDICT = smart_verdict(dict(E07_NVME))  # à remplacer (usure ≥ 100 %)

E08_LIMIT = 95
E08_BEFORE = (("Repos", 58), ("Charge, 10 min", 93))
E08_AFTER = (("Repos", 41), ("Charge, 30 min", 77))
E08_VERDICTS = tuple(temperature_verdict(t, E08_LIMIT) for _m, t in E08_BEFORE + E08_AFTER)

E09_CATEGORIES = (WASTE_DEEE, WASTE_BATTERY, WASTE_PAPER)
E09_CORRECT = tuple(E09_CATEGORIES.index(stream) for _item, stream in WASTE_ITEMS)

E15_DESIGN = 50000
E15_FULL = 43500
E15_HEALTH = battery_health_percent(E15_DESIGN, E15_FULL)  # 87 %
E15_VERDICT = battery_verdict(E15_DESIGN, E15_FULL)  # bonne


def _verdicts(rows: tuple[tuple[str, int], ...], limit: int) -> str:
    return " ; ".join(f"{m} {t} °C : {temperature_verdict(t, limit)}" for m, t in rows)


# =============================================================================================
# 16 exercices corrigés (cours + « S'entraîner »)
# =============================================================================================

PRACTICE_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="E01",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre le reconditionnement d'un PC",
        question_type="ordering",
        requirement_ids=("AP-14", "AP-C03"),
        kind=KIND_ORDER,
        context=(
            "Une entreprise confie à l'atelier un lot de PC de bureau qu'elle remplace ; ils "
            "seront revendus d'occasion. Le responsable te demande la fiche de procédure qui "
            "servira pour chaque appareil. Le stagiaire a noté les neuf étapes, mais dans le "
            "désordre."
        ),
        instructions=("Remets les neuf étapes du reconditionnement dans l'ordre professionnel.",),
        criteria=(
            _c("Ordre", 3, "Réceptionner → autoriser → diagnostiquer → protéger les données → nettoyer → remplacer → mettre à jour → tester → remettre."),
        ),
        correction=(
            "1. Réceptionner (fiche, numéro de série, état, photos) et 2. autoriser (accord écrit sur le travail et les données) : rien ne commence sans trace ni accord. 3. Diagnostiquer avant d'intervenir : on sait ce qui fonctionne et ce qui doit être remplacé, et on évite de nettoyer ou réparer un appareil irrécupérable.",
            "4. Protéger les données (sauvegarde ou effacement sécurisé selon l'accord) avant toute manipulation du disque. 5. Nettoyer, 6. remplacer les pièces usées, 7. mettre à jour, 8. tester avec des valeurs notées, 9. remettre avec check-list, étiquette et rapport.",
        ),
        ordering=_shuffled_ordering(E01_STEPS, (4, 7, 1, 8, 2, 6, 0, 5, 3)),
    ),
    PR06Item(
        key="E02",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre le nettoyage d'une tour",
        question_type="ordering",
        requirement_ids=("AP-14", "AP-C02"),
        kind=KIND_ORDER,
        context=(
            "Un client se plaint que son PC de bureau est devenu bruyant et chauffe. À "
            "l'ouverture, filtres, ventilateurs et radiateur du ventirad sont couverts de "
            "poussière. Tu rédiges pour un stagiaire la procédure de nettoyage non destructif, "
            "dont les étapes ont été mélangées."
        ),
        instructions=("Remets les sept étapes du nettoyage dans l'ordre.",),
        criteria=(
            _c("Ordre", 3, "Couper → sortir le PC → filtres → bloquer les ventilateurs → dépoussiérer → contacts et pâte → contrôler."),
        ),
        correction=(
            "1. Couper : arrêt, interrupteur sur 0, secteur débranché, appui sur le bouton. 2. Sortir le PC dans un local aéré (la poussière ne doit pas retomber sur le poste de montage). 3. Retirer les filtres pour les brosser ou les rincer : ils sèchent pendant la suite.",
            "4. Bloquer les pales avant de souffler : un ventilateur entraîné par l'air tourne trop vite et peut s'abîmer. 5. Air sec par courtes impulsions, bombe tenue droite, pinceau antistatique. 6. Alcool isopropylique sur les contacts ; pâte neuve si le ventirad a été retiré. 7. Contrôler (rien oublié, filtres secs remis) puis mesurer les températures.",
        ),
        ordering=_shuffled_ordering(E02_STEPS, (3, 6, 0, 4, 1, 5, 2)),
    ),
    PR06Item(
        key="E03",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre une mise à jour du firmware",
        question_type="ordering",
        requirement_ids=("AP-14",),
        kind=KIND_ORDER,
        context=(
            "Pendant le reconditionnement d'un PC de bureau, tu constates que le fabricant de "
            "la carte mère a publié une version du firmware UEFI qui corrige un défaut de "
            "stabilité de la mémoire. Le disque système est chiffré avec BitLocker. Tu rédiges "
            "la procédure ; les étapes ont été mélangées."
        ),
        instructions=("Remets les six étapes de la mise à jour dans l'ordre.",),
        criteria=(
            _c("Ordre", 3, "Justifier → identifier le modèle et la version → télécharger et lire les notes → préparer (sauvegarde, réglages, BitLocker suspendu, secteur) → flasher sans couper → vérifier."),
        ),
        correction=(
            "1. Justifier : ici un correctif de stabilité utile. 2. Identifier le modèle et la révision exacts et la version installée : un firmware d'un autre modèle peut rendre la carte inutilisable. 3. Télécharger le fichier du fabricant et lire les notes (version minimale, ordre des mises à jour).",
            "4. Préparer : sauvegarde, réglages UEFI notés (ils peuvent revenir aux valeurs d'usine), BitLocker suspendu (sinon la clé de récupération sera demandée au redémarrage), alimentation stable. 5. Flasher avec l'outil du fabricant, sans couper. 6. Vérifier la version, remettre les réglages et reprendre BitLocker.",
        ),
        ordering=_shuffled_ordering(E03_STEPS, (2, 5, 0, 4, 1, 3)),
    ),
    PR06Item(
        key="E04",
        usage=USAGE_PRACTICE,
        title="Réparation, reconditionnement, remise à zéro ou effacement sécurisé ?",
        question_type="classification",
        requirement_ids=("AP-14", "AP-C03"),
        kind=KIND_DATA,
        context=(
            "Le carnet de commandes de l'atelier mélange des demandes de natures différentes. "
            "Le devis, l'accord à faire signer, le sort des données et la trace à remettre ne "
            "sont pas les mêmes selon qu'il s'agit d'une réparation, d'un reconditionnement, "
            "d'une remise à zéro ou d'un effacement sécurisé."
        ),
        instructions=("Range chacune des huit demandes dans l'opération qui lui correspond.",),
        criteria=(
            _c("Classement", 4, "Réparation : ventilateur, écran. Reconditionnement : dix PC pour l'école, PC d'occasion avant revente. Remise à zéro : « Réinitialiser ce PC » pour le même client, réinstallation après infection. Effacement sécurisé : SSD de location, disques déclassés (0,5 pt par élément)."),
        ),
        correction=(
            "Réparation : on corrige une panne précise pour le même client, qui garde ses données (ventilateur, écran). Reconditionnement : on remet un PC complet en état pour un nouvel utilisateur (diagnostic, nettoyage, pièces, système, tests) — les dix PC donnés, le PC d'occasion.",
            "Remise à zéro : on réinitialise ou réinstalle le système pour le même client, les fichiers supprimés n'étant pas forcément illisibles sur le disque. Effacement sécurisé : on rend les données illisibles avec une technique adaptée et un certificat, avant que le support quitte son propriétaire (location, recyclage).",
        ),
        classification=Classification(
            categories=E04_CATEGORIES,
            elements=tuple(e for e, _op in E04_ELEMENTS),
            correct=tuple(E04_CATEGORIES.index(op) for _e, op in E04_ELEMENTS),
        ),
    ),
    PR06Item(
        key="E05",
        usage=USAGE_PRACTICE,
        title="Décider du sort des données : six situations d'atelier",
        question_type="classification",
        requirement_ids=("AP-14", "AP-C03"),
        kind=KIND_DATA,
        context=(
            "Six appareils attendent sur l'étagère de l'atelier. Pour chacun, tu dois décider "
            "ce que tu fais des données avant d'intervenir, d'après ce qui est écrit sur la "
            "fiche : l'accord écrit du propriétaire, son souhait de garder ses fichiers, "
            "l'existence d'une copie vérifiée et la destination de l'appareil."
        ),
        instructions=("Range chaque situation dans la décision correcte.",),
        criteria=(
            _c("Classement", 3, "Effacement autorisé : PME → association, disque à recycler. Sauvegarder d'abord : réinstallation sans sauvegarde. Accord nécessaire : appel du fils, PC repris « sûrement d'accord ». Conserver : réparation pour le même client avec sauvegarde (0,5 pt par élément)."),
        ),
        correction=(
            "Seul le propriétaire décide, par écrit : un appel d'un proche ou une supposition du vendeur ne vaut pas accord — on n'efface rien et on contacte le propriétaire. Une cliente qui veut garder ses photos sans aucune sauvegarde : on sauvegarde et on vérifie la copie avant de toucher au disque.",
            "Avec l'accord écrit et la copie vérifiée, un PC qui change de main reçoit un effacement sécurisé adapté au support et certifié ; un disque à recycler est effacé ou détruit physiquement, avec trace. Un PC réparé et rendu au même client garde ses données.",
        ),
        classification=Classification(
            categories=E05_CATEGORIES,
            elements=tuple(s for s, *_rest in E05_CASES),
            correct=E05_CORRECT,
        ),
    ),
    PR06Item(
        key="E06",
        usage=USAGE_PRACTICE,
        title="Technique d'effacement adaptée au support ou insuffisante ?",
        question_type="classification",
        requirement_ids=("AP-14", "AP-C03"),
        kind=KIND_DATA,
        context=(
            "Avant la revente d'un lot de PC, un collègue a noté comment il comptait effacer "
            "chaque support. Les propriétaires ont tous signé l'accord d'effacement et leurs "
            "données ont été sauvegardées. Tu vérifies que chaque technique rend vraiment les "
            "données illisibles sur ce type de support."
        ),
        instructions=("Classe chacune des huit techniques : adaptée au support ou insuffisante.",),
        criteria=(
            _c("Classement", 4, "Adaptées : écrasement complet du HDD, commande d'effacement du SSD SATA, effacement cryptographique du NVMe chiffré, destruction du HDD hors d'usage. Insuffisantes : formatage rapide, sept passes sur SSD, défragmentation, suppression des partitions (0,5 pt par élément)."),
        ),
        correction=(
            "Formatage rapide et suppression des partitions ne réécrivent que les structures du disque : les données restent récupérables. Un disque dur s'efface par un écrasement complet (une passe suffit sur un disque récent) ou par sa commande d'effacement sécurisé ; hors d'usage, il est détruit par une filière agréée.",
            "Sur un SSD, le contrôleur répartit l'usure et garde des cellules de réserve : des passes d'écrasement lancées depuis le PC n'atteignent pas tout, et la défragmentation n'efface rien (elle use le SSD). On utilise la commande d'effacement sécurisé ou Sanitize du SSD, ou l'effacement cryptographique s'il est chiffré.",
        ),
        classification=Classification(
            categories=E06_CATEGORIES,
            elements=tuple(label for label, _m, _t in E06_ELEMENTS),
            correct=E06_CORRECT,
        ),
    ),
    PR06Item(
        key="E07",
        usage=USAGE_PRACTICE,
        title="Lire deux relevés SMART avant de reconditionner",
        question_type="document_analysis",
        requirement_ids=("AP-14",),
        kind=KIND_TESTS,
        context=(
            "Un PC de bureau à reconditionner contient un disque dur de données et un SSD NVMe "
            "système. Les deux utilitaires affichent un résultat global « bon ». Tu lis les "
            "attributs des documents 1 et 2 avec la règle du cours pour décider de garder ou "
            "de remplacer chaque support."
        ),
        documents=(
            _console("Document 1 — Disque dur 2 To (fictif)",
                     *smart_lines("Relevé SMART — disque dur 2 To", "PASSED", E07_SMART)[1:]),
            _console("Document 2 — SSD NVMe 512 Go (fictif)",
                     *smart_lines("Relevé SMART — SSD NVMe", "OK", E07_NVME)[1:]),
        ),
        instructions=(
            "Donne le verdict de chaque support (bon, à surveiller, à remplacer) en citant les attributs.",
            "Indique la décision pour le reconditionnement et ce que tu notes dans le rapport.",
        ),
        criteria=(
            _c("Disque dur", 1, f"Verdict « {E07_HDD_VERDICT} » : aucun secteur réalloué, en attente ni illisible ; température normale ; on le garde."),
            _c("SSD NVMe", 1.5, f"Verdict « {E07_NVME_VERDICT} » : usure (Percentage_Used) à 104 %, au-delà de l'endurance prévue, même sans erreur ni baisse de la réserve ; le résultat global « OK » ne suffit pas."),
            _c("Décision et rapport", 1, "Remplacer le SSD (accord, effacement sécurisé ou destruction de l'ancien, avec trace) ; noter les valeurs SMART des deux supports et le numéro de série du nouveau."),
        ),
        correction=(
            "Disque dur : 0 secteur réalloué, 0 en attente, 0 illisible, 36 °C : bon, on le garde. SSD NVMe : 104 % d'usure — il a dépassé l'endurance garantie par le fabricant ; il fonctionne encore, mais un PC revendu ne doit pas partir avec un support en fin de vie : à remplacer, malgré le « OK » global.",
            "Décision : remplacer le SSD par un modèle compatible (format M.2, interface NVMe), installer le système, tester ; l'ancien SSD est effacé de façon sécurisée ou détruit, avec trace. Le rapport reprend les valeurs lues et le numéro de série du nouveau SSD.",
        ),
    ),
    PR06Item(
        key="E08",
        usage=USAGE_PRACTICE,
        title="Prouver l'effet d'un nettoyage par les températures",
        question_type="document_analysis",
        requirement_ids=("AP-14",),
        kind=KIND_TESTS,
        context=(
            "Un PC de bureau ralentissait en charge. Tu as relevé la température du processeur "
            f"avant et après un nettoyage complet (filtres, ventirad, pâte neuve). La limite de "
            f"la fiche du processeur est de {E08_LIMIT} °C. Le document 1 reprend tes relevés."
        ),
        documents=(
            _table(
                "Document 1 — Relevés de température du processeur",
                ("Moment", "Avant nettoyage", "Après nettoyage"),
                (E08_BEFORE[0][0], f"{E08_BEFORE[0][1]} °C", f"{E08_AFTER[0][1]} °C"),
                ("Charge", f"{E08_BEFORE[1][1]} °C (10 min)", f"{E08_AFTER[1][1]} °C (30 min)"),
            ),
        ),
        instructions=(
            "Donne le verdict de chaque relevé avec la règle du cours (normal, à surveiller, anormal).",
            "Explique le ralentissement constaté avant le nettoyage.",
            "Rédige la phrase du rapport qui prouve le résultat.",
        ),
        criteria=(
            _c("Verdicts", 1.5, f"Avant : {_verdicts(E08_BEFORE, E08_LIMIT)}. Après : {_verdicts(E08_AFTER, E08_LIMIT)}."),
            _c("Explication", 1, "À 93 °C, près de la limite, le processeur réduit sa fréquence pour se protéger : d'où le ralentissement ; la poussière et une vieille pâte empêchent la chaleur de partir."),
            _c("Rapport", 0.5, "Phrase avec les valeurs avant/après et la durée de charge, pas seulement « nettoyé »."),
        ),
        correction=(
            f"Règle du cours : à surveiller à moins de {TEMP_ALERT_MARGIN} °C de la limite (ici dès {E08_LIMIT - TEMP_ALERT_MARGIN} °C), anormal à la limite ({E08_LIMIT} °C), normal en dessous. Avant : {_verdicts(E08_BEFORE, E08_LIMIT)} ; après : {_verdicts(E08_AFTER, E08_LIMIT)}.",
            "Près de sa limite, le processeur baisse sa fréquence pour ne pas dépasser sa température maximale : c'est le ralentissement observé. Rapport : « Nettoyage complet et pâte neuve : processeur à 41 °C au repos et 77 °C après 30 minutes de charge, contre 58 °C et 93 °C avant. »",
        ),
    ),
    PR06Item(
        key="E09",
        usage=USAGE_PRACTICE,
        title="Trier les déchets d'une journée d'atelier",
        question_type="classification",
        requirement_ids=("AP-14",),
        kind=KIND_FORM,
        context=(
            "En fin de journée, la caisse des déchets de l'atelier, en Belgique, contient des "
            "pièces remplacées pendant des reconditionnements et des emballages. Les disques "
            "ont déjà été effacés ou détruits avec un certificat. Tu dois orienter chaque "
            "déchet vers la bonne filière de collecte."
        ),
        instructions=("Range chacun des huit déchets dans sa filière.",),
        criteria=(
            _c("Classement", 4, "DEEE : carte mère, bloc d'alimentation, disque effacé, écran LCD. Piles et batteries : CR2032, batterie de portable gonflée, piles AA. Papier-carton : carton du SSD (0,5 pt par élément)."),
        ),
        correction=(
            "Les équipements électriques et électroniques (carte mère, bloc, disque effacé, écran) vont à la collecte des DEEE (Recupel en Belgique : recyparc, point de collecte, reprise en magasin), jamais à la poubelle ordinaire : ils contiennent des métaux à récupérer et des substances polluantes.",
            "Les piles et batteries suivent une collecte séparée (Bebat) : pile CR2032, piles de la souris et batterie de portable — une batterie gonflée est isolée dans un contenant non inflammable, sans la percer ni l'écraser, et déposée rapidement. Le carton propre part au papier-carton.",
        ),
        classification=Classification(
            categories=E09_CATEGORIES,
            elements=tuple(item for item, _stream in WASTE_ITEMS),
            correct=E09_CORRECT,
        ),
    ),
    PR06Item(
        key="E10",
        usage=USAGE_PRACTICE,
        title="Compléter une fiche de réception incomplète",
        question_type="document_analysis",
        requirement_ids=("AP-14", "AP-C03"),
        kind=KIND_FORM,
        context=(
            "Un stagiaire a réceptionné seul le portable d'un client qui demande « une remise à "
            "neuf, il est lent ». Avant que le client ne quitte le comptoir, tu relis la fiche "
            "de réception (document 1) : plusieurs rubriques indispensables manquent ou sont "
            "inutilisables."
        ),
        documents=(
            _table(
                "Document 1 — Fiche de réception remplie par le stagiaire",
                ("Rubrique", "Contenu noté"),
                ("Date / client", "Lundi ; M. D."),
                ("Matériel", "Portable gris"),
                ("Accessoires", "—"),
                ("État", "Bon état"),
                ("Demande", "Remise à neuf, il est lent"),
                ("Données", "—"),
                ("Signature", "—"),
            ),
        ),
        instructions=(
            "Relève les rubriques à compléter ou à corriger et ce qu'il faut y écrire.",
            "Explique pourquoi la rubrique « Données » doit être réglée avant le départ du client.",
        ),
        criteria=(
            _c("Identification", 0.75, "Date complète, nom et coordonnées du client, numéro de fiche ; marque, modèle et numéro de série, étiquette d'inventaire."),
            _c("État et accessoires", 0.75, "Accessoires remis (chargeur…) ; défauts précis et photos datées au lieu de « bon état »."),
            _c("Demande", 0.5, "Préciser « remise à neuf » : réparation, nettoyage, réinstallation ? Avec les mots du client et ce qu'il accepte."),
            _c("Données et signature", 1, "Données à garder ou non, sauvegarde existante, accord écrit (réinstallation = risque de perte) ; signature du client et du technicien, copie remise."),
        ),
        correction=(
            "Il manque l'identification exploitable (date complète, coordonnées, marque, modèle et numéro de série), les accessoires remis (le chargeur est-il là ?), un état initial précis avec photos (« bon état » ne prouve rien en cas de litige), une demande clarifiée (« remise à neuf » peut vouloir dire nettoyage, pièces ou réinstallation) et les signatures.",
            "Les données doivent être réglées avant le départ : une remise à neuf passe souvent par une réinstallation qui efface le disque. Sans accord écrit et sans savoir si une sauvegarde existe, on ne peut rien faire — ou on risque de perdre les fichiers du client.",
        ),
    ),
    PR06Item(
        key="E11",
        usage=USAGE_PRACTICE,
        title="Rédiger la check-list de remise d'un PC reconditionné",
        question_type="long_answer",
        requirement_ids=("AP-14",),
        kind=KIND_FORM,
        context=(
            "L'atelier remet aujourd'hui à une école dix PC de bureau reconditionnés, donnés "
            "par une entreprise. La directrice veut une check-list de remise signée pour chaque "
            "PC, qui prouve qu'il a été contrôlé et que les données de l'entreprise ont disparu."
        ),
        instructions=("Rédige la check-list de remise : au moins sept points à contrôler, chacun avec ce qu'on vérifie.",),
        criteria=(
            _c("Tests", 1, "Mémoire, SMART, températures, ports, stabilité : valeurs dans le rapport."),
            _c("Données et système", 1, "Effacement certifié des anciens supports ; système propre, à jour, activé, sans compte ni fichier de l'entreprise ou du technicien."),
            _c("État et accessoires", 0.5, "Boîtier fermé, vis, propreté ; câbles et accessoires prévus."),
            _c("Traçabilité", 0.5, "Numéro de série, pièces remplacées, étiquette datée, signature de la directrice."),
        ),
        correction=(
            "1. Tests notés : mémoire sans erreur, SMART bon, températures normales en charge, chaque port testé, 30 minutes de stabilité. 2. Données : certificat d'effacement de chaque ancien support (numéro de série, technique, date). 3. Système : installé proprement, à jour, activé, aucun compte ni fichier de l'entreprise ou de l'atelier.",
            "4. Propreté : boîtier fermé, toutes les vis, extérieur propre. 5. Accessoires : câble secteur, clavier, souris prévus. 6. Pièces remplacées listées avec leurs numéros de série. 7. Étiquette de reconditionnement datée et rapport signé par la directrice (copie conservée à l'atelier).",
        ),
    ),
    PR06Item(
        key="E12",
        usage=USAGE_PRACTICE,
        title="Corriger un rapport de reconditionnement",
        question_type="document_analysis",
        requirement_ids=("AP-14", "AP-C03"),
        kind=KIND_ERROR,
        context=(
            "Ton responsable te demande de relire le rapport de reconditionnement d'un "
            "portable rédigé par un stagiaire, avant sa revente. Le portable avait un SSD NVMe "
            "et appartenait à une autre cliente, qui a signé l'accord d'effacement. Plusieurs "
            "lignes du document 1 posent problème."
        ),
        documents=(
            _table(
                "Document 1 — Extrait du rapport du stagiaire",
                ("Étape", "Ce qui est noté"),
                ("Données", "Formatage rapide du SSD : données effacées"),
                ("Firmware", "Mise à jour UEFI lancée sur batterie (15 %), chargeur oublié"),
                ("Nettoyage", "Aspirateur de l'atelier sur la carte mère"),
                ("Tests", "SMART : PASSED, donc SSD comme neuf"),
                ("Remise", "RAS, tout fonctionne"),
            ),
        ),
        instructions=("Pour chaque ligne, explique l'erreur et ce qu'il fallait faire et noter.",),
        criteria=(
            _c("Données", 1, "Formatage rapide ≠ effacement : commande d'effacement sécurisé ou Sanitize du SSD NVMe (ou effacement cryptographique), vérification et certificat."),
            _c("Firmware", 0.75, "Risque de coupure pendant l'écriture : chargeur branché, batterie chargée, aucune interruption."),
            _c("Nettoyage", 0.75, "Aspirateur : électricité statique, aspiration de petites pièces ; air sec par impulsions, ventilateur bloqué, pinceau antistatique."),
            _c("Tests et remise", 1.5, "PASSED ne dit rien de l'usure : lire les attributs (usure, réserve, erreurs). « RAS » n'est pas un résultat : valeurs des tests (mémoire, SMART, températures, ports, batterie) dans le rapport."),
        ),
        correction=(
            "Données : un formatage rapide laisse les données lisibles ; il fallait la commande d'effacement sécurisé ou Sanitize du SSD (ou un effacement cryptographique s'il était chiffré), vérifier, puis noter support, numéro de série, technique et date sur un certificat. Firmware : sur batterie faible, une coupure pendant l'écriture peut rendre la carte inutilisable ; chargeur branché obligatoire.",
            "Nettoyage : un aspirateur crée de l'électricité statique et peut aspirer de petits composants ; il fallait l'air sec par impulsions, ventilateur bloqué, et un pinceau antistatique. Tests : « PASSED » est un résumé ; on note l'usure, la réserve et les erreurs. Remise : remplacer « RAS » par les valeurs mesurées et la conclusion signée.",
        ),
    ),
    PR06Item(
        key="E13",
        usage=USAGE_PRACTICE,
        title="Expliquer à un collègue pourquoi on n'efface pas un SSD par passes",
        question_type="short_answer",
        requirement_ids=("AP-14", "AP-C03"),
        kind=KIND_DATA,
        context=(
            "Un collègue veut effacer le SSD SATA d'un PC avant sa revente avec le logiciel "
            "qu'il utilise depuis des années pour les disques durs : sept passes d'écrasement, "
            "puis une défragmentation « pour tout mélanger ». L'accord d'effacement est signé "
            "et les données ont été sauvegardées."
        ),
        instructions=("Explique pourquoi ces deux opérations ne conviennent pas et indique la technique à utiliser et la trace à garder.",),
        criteria=(
            _c("Passes", 1, "Le contrôleur du SSD répartit les écritures et garde des cellules de réserve : le logiciel n'écrit pas partout, des données peuvent rester ; et les passes usent le SSD."),
            _c("Défragmentation", 0.5, "Inutile sur un SSD (pas de tête de lecture) et n'efface rien ; elle l'use."),
            _c("Technique et trace", 1.5, "Commande d'effacement sécurisé ou Sanitize du SSD via l'outil du fabricant ou le firmware (ou effacement cryptographique s'il est chiffré) ; vérifier ; certificat avec numéro de série, technique, date, technicien."),
        ),
        correction=(
            "Sur un SSD, le contrôleur décide où il écrit (répartition de l'usure) et garde des cellules de réserve invisibles pour le système : des passes lancées depuis le PC ne garantissent pas que toutes les cellules sont écrasées, et elles usent le SSD. La défragmentation ne sert à rien sur un SSD et n'efface aucune donnée.",
            "On utilise la commande d'effacement intégrée au SSD (effacement sécurisé ou Sanitize) via l'outil du fabricant ou le firmware de la carte, ou l'effacement cryptographique si le SSD était chiffré ; on vérifie, puis on remplit le certificat (support, numéro de série, technique, date, technicien).",
        ),
    ),
    PR06Item(
        key="E14",
        usage=USAGE_PRACTICE,
        title="Une demande d'effacement venue d'un tiers",
        question_type="short_answer",
        requirement_ids=("AP-14", "AP-C03"),
        kind=KIND_DATA,
        context=(
            "Le PC portable de M. Lambert est à l'atelier pour un remplacement de clavier. Sa "
            "fille téléphone : son père va le vendre, il faut « tout effacer et remettre "
            "Windows d'usine » pendant que le PC est là. La fiche de réception ne mentionne "
            "qu'un remplacement de clavier et M. Lambert y a coché « garder mes données »."
        ),
        instructions=("Indique ce que tu fais, ce que tu ne fais pas, et pourquoi.",),
        criteria=(
            _c("Refus d'agir", 1, "Aucun effacement ni réinstallation sur la demande d'un tiers : seul le propriétaire décide, par écrit ; la fiche dit « garder mes données »."),
            _c("Démarche", 1, "Réaliser le clavier prévu ; contacter M. Lambert ; s'il confirme, nouvelle autorisation écrite, sauvegarde vérifiée de ce qu'il garde, puis effacement sécurisé adapté avant la vente (certificat)."),
        ),
        correction=(
            "On n'efface rien : la demande vient d'un tiers, alors que le propriétaire a écrit vouloir garder ses données. Un effacement est irréversible ; sans accord écrit du propriétaire, il expose l'atelier à un litige et le client à une perte.",
            "On fait le remplacement de clavier prévu et on contacte M. Lambert. S'il confirme la vente, on lui fait signer une nouvelle autorisation (effacement sécurisé, sauvegarde préalable de ce qu'il garde), puis on efface avec une technique adaptée au support et on remet le certificat.",
        ),
    ),
    PR06Item(
        key="E15",
        usage=USAGE_PRACTICE,
        title="Faut-il changer la batterie du portable reconditionné ?",
        question_type="document_analysis",
        requirement_ids=("AP-14",),
        kind=KIND_TESTS,
        context=(
            "Tu reconditionnes un portable destiné au prêt aux élèves d'une école. Tu as "
            "généré le rapport de batterie de Windows (commande powercfg /batteryreport, dans "
            "une invite de commandes) ; le document 1 en reprend l'extrait utile. La convention "
            "de l'atelier : batterie à remplacer sous 80 % de sa capacité d'origine."
        ),
        documents=(
            _console(
                "Document 1 — Rapport de batterie (extrait, fictif)",
                f"DESIGN CAPACITY        {E15_DESIGN} mWh",
                f"FULL CHARGE CAPACITY   {E15_FULL} mWh",
                "CYCLE COUNT            298",
            ),
        ),
        instructions=(
            "Calcule la capacité restante en pourcentage de la capacité d'origine.",
            "Donne ta décision et ce que tu notes dans le rapport de reconditionnement.",
        ),
        criteria=(
            _c("Calcul", 1.5, f"{E15_FULL} / {E15_DESIGN} × 100 = {E15_HEALTH} % de la capacité d'origine (usure {100 - E15_HEALTH} %)."),
            _c("Décision", 0.75, f"{E15_HEALTH} % ≥ 80 % : batterie « {E15_VERDICT} », on la garde."),
            _c("Rapport", 0.75, "Capacités, pourcentage, nombre de cycles et décision ; vérifier aussi l'absence de gonflement."),
        ),
        correction=(
            f"Capacité restante = capacité à pleine charge / capacité d'origine = {E15_FULL} / {E15_DESIGN} = {E15_HEALTH / 100:.2f}, soit {E15_HEALTH} % (usure de {100 - E15_HEALTH} %).",
            f"{E15_HEALTH} % est au-dessus du seuil de 80 % fixé par l'atelier : on garde la batterie. Le rapport note les deux capacités, le pourcentage, les 298 cycles et la décision, ainsi que le contrôle visuel (batterie non gonflée).",
        ),
    ),
    PR06Item(
        key="E16",
        usage=USAGE_PRACTICE,
        title="L'horloge se dérègle à chaque coupure de courant",
        question_type="short_answer",
        requirement_ids=("AP-14",),
        kind=KIND_TESTS,
        context=(
            "Pendant le diagnostic avant reconditionnement d'un PC de bureau de huit ans, tu "
            "remarques qu'après chaque débranchement du câble secteur, la date de l'UEFI "
            "revient au 1er janvier et les réglages sont perdus (mode de démarrage, ordre des "
            "disques). Le PC fonctionne normalement par ailleurs."
        ),
        instructions=("Donne la cause la plus probable, la pièce à remplacer et les précautions, puis le contrôle après remplacement.",),
        criteria=(
            _c("Cause", 0.75, "Pile de la carte mère (CR2032 le plus souvent) usée : elle garde l'horloge et les réglages quand le PC est débranché."),
            _c("Remplacement", 0.75, "PC débranché, bracelet ; relever les réglages ; pile de même référence, polarité + vers le haut le plus souvent ; ancienne pile à la collecte des piles."),
            _c("Contrôle", 0.5, "Régler date, heure et réglages notés ; débrancher puis rebrancher : réglages conservés."),
        ),
        correction=(
            "La pile de la carte mère (le plus souvent une CR2032) entretient l'horloge et les réglages quand le PC est débranché ; usée, elle ne les garde plus. PC débranché, bracelet relié, on note les réglages, on remplace la pile par la même référence (face + visible le plus souvent, selon le support) et on dépose l'ancienne à la collecte des piles.",
            "On remet la date, l'heure et les réglages (mode de démarrage, ordre des disques), puis on débranche le câble secteur quelques minutes et on vérifie que tout est conservé au redémarrage.",
        ),
    ),
)

# =============================================================================================
# Mini-examen : 10 questions à réponse libre, 2 points chacune (« Examen blanc » uniquement)
# =============================================================================================

EXAM_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="X01",
        usage=USAGE_EXAM,
        title="Réparation ou reconditionnement ?",
        question_type="short_answer",
        requirement_ids=("AP-14",),
        kind=KIND_DATA,
        context=(
            "Deux demandes arrivent le même jour : une cliente veut faire changer le disque "
            "dur défaillant de son PC et retrouver ses fichiers ; une commune veut que ses "
            "vingt anciens PC soient remis en état pour être prêtés à des associations."
        ),
        instructions=("Nomme l'opération de chaque demande et indique, pour chacune, ce que deviennent les données.",),
        criteria=(
            _c("Cliente", 1, "Réparation : panne précise pour la même personne ; données conservées (sauvegarde ou récupération, puis restauration sur le nouveau disque)."),
            _c("Commune", 1, "Reconditionnement : diagnostic, nettoyage, pièces, système, tests pour un nouvel utilisateur ; effacement sécurisé certifié des anciens supports après accord écrit de la commune."),
        ),
        correction=(
            "La cliente demande une réparation : on remplace le disque et on restaure ses fichiers (sauvegarde existante, ou récupération si l'ancien disque est encore lisible) ; elle garde ses données.",
            "La commune demande un reconditionnement : chaque PC est diagnostiqué, nettoyé, réparé, mis à jour et testé pour de nouveaux utilisateurs ; les données de la commune sont effacées de façon sécurisée, après son accord écrit, avec un certificat par support.",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Le formatage rapide avant la revente",
        question_type="short_answer",
        requirement_ids=("AP-14", "AP-C03"),
        kind=KIND_DATA,
        context=(
            "Un client te dit qu'il a « formaté » le disque dur de son ancien PC avant de le "
            "vendre sur un site d'occasion : il a choisi « formatage rapide » dans Windows. Il "
            "te demande si ses documents bancaires sont désormais illisibles."
        ),
        instructions=("Réponds au client et indique ce qu'il aurait fallu faire sur ce disque dur.",),
        criteria=(
            _c("Réponse", 1, "Non : le formatage rapide ne réécrit que la table du système de fichiers ; les données restent récupérables avec un logiciel."),
            _c("Technique", 1, "Écrasement complet du disque (une passe suffit sur un disque dur récent) ou commande d'effacement sécurisé, vérification, trace ; destruction physique s'il est hors d'usage."),
        ),
        correction=(
            "Non : un formatage rapide ne fait que recréer un système de fichiers vide ; les données restent sur le disque et un logiciel de récupération peut les retrouver.",
            "Il fallait un écrasement complet du disque (une passe suffit sur un disque dur récent) ou la commande d'effacement sécurisé du disque, puis vérifier le résultat et garder une trace ; un disque hors d'usage se détruit par une filière agréée.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="Effacer le SSD NVMe d'un portable de location",
        question_type="document_analysis",
        requirement_ids=("AP-14", "AP-C03"),
        kind=KIND_DATA,
        context=(
            "Une société de location te confie un portable rendu par un client, à préparer "
            "pour la location suivante. Le document 1 reprend la fiche de prise en charge. Le "
            "loueur demande la preuve que les données du client précédent ont disparu."
        ),
        documents=(
            _table(
                "Document 1 — Fiche de prise en charge",
                ("Rubrique", "Contenu"),
                ("Propriétaire", "Société de location (accord d'effacement signé)"),
                ("Support", "SSD NVMe 512 Go, numéro de série noté"),
                ("Chiffrement", "Aucun"),
                ("Données à garder", "Aucune"),
            ),
        ),
        instructions=("Indique la technique d'effacement adaptée, ce qu'il ne faut pas faire, et le contenu de la preuve à remettre.",),
        criteria=(
            _c("Technique", 1, "Commande NVMe d'effacement sécurisé ou Sanitize (outil du fabricant ou firmware) ; pas d'effacement cryptographique possible ici (SSD non chiffré) ; pas de formatage rapide ni de passes d'écrasement."),
            _c("Preuve", 1, "Vérification du résultat puis certificat : support, numéro de série, technique, date, technicien, résultat."),
        ),
        correction=(
            "L'accord du propriétaire (le loueur) est signé et rien n'est à garder : on efface avec la commande intégrée au SSD NVMe (Format avec effacement sécurisé ou Sanitize), via l'outil du fabricant ou le firmware. Le SSD n'étant pas chiffré, l'effacement cryptographique ne s'applique pas ; formatage rapide et passes d'écrasement sont insuffisants sur un SSD.",
            "On vérifie que plus aucune donnée n'est lisible, puis on remet un certificat : support, numéro de série, technique employée, date, nom du technicien et résultat.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="Nettoyer un portable qui chauffe",
        question_type="long_answer",
        requirement_ids=("AP-14", "AP-C02"),
        kind=KIND_ORDER,
        context=(
            "Un portable de quatre ans est bruyant et s'éteint parfois pendant les jeux. Les "
            "grilles d'aération sont encrassées. La notice du fabricant permet d'ouvrir le "
            "capot inférieur ; le ventilateur et le radiateur sont alors accessibles. Le "
            "client a signé l'autorisation et ses données sont sauvegardées."
        ),
        instructions=("Rédige la procédure de nettoyage non destructif et le contrôle final.",),
        criteria=(
            _c("Sécurité", 0.5, "Arrêt complet, chargeur débranché, batterie déconnectée si la notice le prévoit ; bracelet."),
            _c("Nettoyage", 0.9, "Ventilateur bloqué, air sec par impulsions dans le radiateur et les grilles, pinceau antistatique ; pas d'aspirateur ni de liquide ; pâte renouvelée si le radiateur est démonté."),
            _c("Contrôle", 0.6, "Remontage complet, températures au repos et en charge comparées à avant, ventilateur, stabilité ; valeurs dans le rapport."),
        ),
        correction=(
            "1. Arrêt complet, chargeur débranché, batterie déconnectée de la carte si la notice le prévoit ; bracelet. 2. Ouvrir le capot selon la notice, vis triées. 3. Bloquer le ventilateur, souffler l'air sec par courtes impulsions dans le radiateur et les grilles, pinceau antistatique sur les pales ; ni aspirateur, ni liquide.",
            "4. Si le radiateur est démonté : ancienne pâte retirée à l'alcool isopropylique, pâte neuve. 5. Remonter, rebrancher la batterie. 6. Mesurer les températures au repos et en charge et les comparer aux valeurs d'avant, vérifier le ventilateur et l'absence d'arrêt en jeu ; noter les valeurs dans le rapport.",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Mettre à jour l'UEFI d'un PC chiffré par BitLocker",
        question_type="short_answer",
        requirement_ids=("AP-14",),
        kind=KIND_ORDER,
        context=(
            "Le fabricant d'un PC de bureau publie un firmware UEFI qui corrige une faille de "
            "sécurité. Le disque système est chiffré avec BitLocker et le client n'a jamais "
            "noté sa clé de récupération. Le PC est branché sur une multiprise de l'atelier."
        ),
        instructions=("Donne les précautions à prendre avant, pendant et après la mise à jour.",),
        criteria=(
            _c("Avant", 1, "Modèle et version exacts, fichier du fabricant, notes lues ; sauvegarde ; clé de récupération retrouvée et sauvegardée ; BitLocker suspendu ; réglages UEFI notés ; alimentation stable."),
            _c("Pendant et après", 1, "Ne jamais couper ni redémarrer pendant l'écriture ; vérifier la version, remettre les réglages, reprendre BitLocker, tester le démarrage."),
        ),
        correction=(
            "Avant : vérifier le modèle exact et la version installée, télécharger le fichier du fabricant et lire les notes ; sauvegarder ; retrouver et sauvegarder la clé de récupération BitLocker (compte du client ou outil de gestion) et suspendre BitLocker, sinon la clé sera exigée au redémarrage ; noter les réglages UEFI ; alimentation stable.",
            "Pendant : aucune coupure ni redémarrage forcé — une écriture interrompue peut rendre la carte inutilisable. Après : contrôler la nouvelle version, remettre les réglages, reprendre la protection BitLocker et vérifier que le système démarre.",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Un relevé SMART « PASSED » à interpréter",
        question_type="document_analysis",
        requirement_ids=("AP-14",),
        kind=KIND_TESTS,
        context=(
            "Avant de revendre un PC reconditionné, tu lis l'état SMART de son disque dur de "
            "1 To (document 1). L'utilitaire affiche un résultat global « PASSED » et le client "
            "acheteur ne compte stocker que des photos de famille."
        ),
        documents=(
            _console(
                "Document 1 — Relevé SMART (fictif)",
                *smart_lines("Relevé SMART — disque dur 1 To", "PASSED", (
                    ("Reallocated_Sector_Ct", 24),
                    ("Current_Pending_Sector", 8),
                    ("Offline_Uncorrectable", 8),
                ))[1:],
            ),
        ),
        instructions=("Donne ton verdict, justifie-le à partir des attributs et indique la décision.",),
        criteria=(
            _c("Verdict", 1, "À remplacer : 8 secteurs en attente et 8 illisibles (données déjà perdues), 24 réalloués ; « PASSED » ne suffit pas."),
            _c("Décision", 1, "Ne pas revendre avec ce disque : le remplacer, effacer ou détruire l'ancien avec trace, noter les valeurs et le nouveau numéro de série."),
        ),
        correction=(
            "Le résumé « PASSED » signifie seulement qu'aucun seuil du fabricant n'est franchi. Les attributs montrent 8 secteurs en attente et 8 illisibles — le disque n'arrive plus à lire certaines zones — et 24 secteurs déjà réalloués : verdict « à remplacer ».",
            "On ne revend pas un PC avec ce disque (les photos de l'acheteur seraient en danger) : on le remplace, on efface ou détruit l'ancien avec une trace, et le rapport reprend les valeurs SMART et le numéro de série du nouveau disque.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Contrôles après remplacement d'un disque par un SSD",
        question_type="short_answer",
        requirement_ids=("AP-14",),
        kind=KIND_TESTS,
        context=(
            "Dans le cadre d'un reconditionnement, tu viens de remplacer le disque dur d'un PC "
            "de bureau par un SSD SATA et d'installer le système. Le PC démarre. Ton "
            "responsable veut savoir quels contrôles tu fais avant de le déclarer prêt."
        ),
        instructions=("Énumère les contrôles à faire et ce que tu notes pour chacun.",),
        criteria=(
            _c("Contrôles", 1.4, "Contrôle visuel (fixation, câbles SATA) ; UEFI (SSD détecté, mode de démarrage) ; test mémoire ; SMART du SSD ; températures repos/charge ; ports ; stabilité."),
            _c("Notes", 0.6, "Valeurs relevées, numéro de série du SSD, conclusion datée — pas « tout fonctionne »."),
        ),
        correction=(
            "Contrôle visuel PC débranché (SSD fixé, câbles SATA données et alimentation, aucune vis libre), puis UEFI (SSD détecté, mode de démarrage), test mémoire, état SMART du SSD, températures au repos et en charge, chaque port et 30 minutes de stabilité.",
            "Pour chacun, on note la valeur (mémoire sans erreur, état SMART, températures, ports testés), le numéro de série du SSD posé et une conclusion datée.",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Une batterie de portable gonflée",
        question_type="short_answer",
        requirement_ids=("AP-14", "AP-C02"),
        kind=KIND_ERROR,
        context=(
            "En ouvrant un portable à reconditionner, tu constates que sa batterie lithium est "
            "gonflée et soulève légèrement le pavé tactile. Un collègue propose de la percer "
            "« pour la dégonfler » puis de la jeter dans la poubelle de l'atelier."
        ),
        instructions=("Explique pourquoi la proposition est dangereuse et ce que tu fais de la batterie.",),
        criteria=(
            _c("Danger", 0.8, "Percer ou écraser une batterie lithium peut provoquer un emballement thermique, un feu et des fumées toxiques ; poubelle interdite."),
            _c("Gestes", 1.2, "Ne plus charger, débrancher le chargeur, retirer la batterie sans la déformer si la notice le permet (sinon spécialiste), l'isoler dans un contenant non inflammable loin des matières combustibles, collecte des batteries (Bebat) rapidement ; batterie neuve compatible."),
        ),
        correction=(
            "Une batterie lithium gonflée est endommagée : la percer ou l'écraser peut déclencher un emballement thermique (feu violent, fumées toxiques). Elle ne va jamais à la poubelle.",
            "On ne la charge plus, on débranche le chargeur, on la retire sans la plier ni appuyer dessus si la notice le permet, on l'isole dans un contenant non inflammable (bac métallique, sable), loin de tout combustible, et on la dépose rapidement à la collecte des batteries (Bebat). On installe une batterie neuve compatible.",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="Le client refuse la sauvegarde",
        question_type="short_answer",
        requirement_ids=("AP-14", "AP-C03"),
        kind=KIND_DATA,
        context=(
            "Un client demande la réinstallation complète de son PC, infecté. Tu lui proposes "
            "de sauvegarder d'abord ses fichiers ; il refuse : « pas le temps, il n'y a rien "
            "d'important dessus ». Le disque contient pourtant un dossier « Comptabilité »."
        ),
        instructions=("Explique ce que tu fais avant de réinstaller.",),
        criteria=(
            _c("Information", 1, "Expliquer que la réinstallation efface le disque et que la perte est définitive ; signaler le dossier visible sans l'ouvrir (confidentialité)."),
            _c("Trace", 1, "Faire signer un refus de sauvegarde (renonciation écrite) et l'autorisation de réinstallation avant d'agir ; sinon ne pas réinstaller."),
        ),
        correction=(
            "On explique au client que la réinstallation efface tout le disque et qu'aucune récupération ne sera possible ensuite ; on lui signale qu'un dossier « Comptabilité » est présent, sans l'ouvrir ni le lire.",
            "S'il maintient son refus, on lui fait signer une renonciation écrite à la sauvegarde et l'autorisation de réinstallation avant d'agir. Sans signature, on ne réinstalle pas.",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Le rapport de reconditionnement",
        question_type="long_answer",
        requirement_ids=("AP-14", "AP-C03"),
        kind=KIND_FORM,
        context=(
            "Tu as terminé le reconditionnement d'un PC de bureau qui sera revendu : SSD "
            "neuf à la place du disque dur usé, nettoyage, pâte neuve, système installé, tests "
            "réussis. Le futur acheteur et l'ancien propriétaire doivent pouvoir vérifier ce "
            "qui a été fait."
        ),
        instructions=("Rédige le plan du rapport de reconditionnement, avec le contenu de chaque rubrique.",),
        criteria=(
            _c("Identification et données", 0.7, "Numéro de série du PC, ancien propriétaire, date, technicien ; accord et certificat d'effacement de l'ancien disque (technique, numéro de série)."),
            _c("Actions et pièces", 0.6, "Diagnostic initial ; nettoyage ; pièces remplacées avec références et numéros de série ; mises à jour."),
            _c("Tests et conclusion", 0.7, "Valeurs : mémoire, SMART, températures, ports, stabilité ; destination des pièces retirées (DEEE) ; conclusion, garantie, signature."),
        ),
        correction=(
            "1. Identification : PC (marque, modèle, numéro de série), ancien propriétaire, dates, technicien. 2. Données : accord signé et certificat d'effacement ou de destruction de l'ancien disque. 3. Diagnostic initial : état à la réception, SMART de l'ancien disque, défauts. 4. Actions : nettoyage, pâte neuve, SSD posé (référence, numéro de série), système et pilotes, firmware éventuel.",
            "5. Tests : mémoire, SMART du SSD, températures au repos et en charge, ports, stabilité — avec les valeurs. 6. Pièces retirées : remises ou déposées à la collecte DEEE. 7. Conclusion : « conforme », garantie, date et signature ; étiquette de reconditionnement sur le PC.",
        ),
    ),
)

ALL_ITEMS: tuple[PR06Item, ...] = PRACTICE_ITEMS + EXAM_ITEMS
EXAM_TOTAL_POINTS = 20

# Supports couverts par E06 (les trois du tableau `ERASE_BY_MEDIA`, contrôlé par les tests).
E06_MEDIA = frozenset(media for _l, media, _t in E06_ELEMENTS)


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
