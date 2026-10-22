"""Banque V1 Français — FR11→FR15 (ticket #94, PHASE C).

Même principe que `app.v1.francais_fr06_10_bank` (#94 PHASE B) : import idempotent,
hand-authored, revalidé par le registre #40 (`validate_content`) avant stockage. Aucune
question ne référence un texte sans un `SourceDocumentVersion` réellement rattaché ; une
question qui cite plusieurs documents d'un dossier les reçoit tous
(`source_document_version_ids`, ticket #151)."""

from sqlalchemy.orm import Session

from app.models import UAA, Module
from app.v1 import question_types  # noqa: F401 — enregistre les 26 types (#40) au chargement
from app.v1.francais_fr06_10_bank import _import_course
from app.v1.francais_fr11_15_content import (
    FR11_MINITEST_TEXT,
    FR11_MINITEST_TITLE,
    FR11_MODEL_TEXT,
    FR11_MODEL_TITLE,
    FR11_WEAK_TEXT,
    FR11_WEAK_TITLE,
    FR12_INTROS_TEXT,
    FR12_INTROS_TITLE,
    FR12_MINITEST_TEXT,
    FR12_MINITEST_TITLE,
    FR12_MODEL_TEXT,
    FR12_MODEL_TITLE,
    FR13_DOC1_TEXT,
    FR13_DOC1_TITLE,
    FR13_DOC2_TEXT,
    FR13_DOC2_TITLE,
    FR13_DOC3_TEXT,
    FR13_DOC3_TITLE,
    FR13_MINITEST_DOC1_TEXT,
    FR13_MINITEST_DOC1_TITLE,
    FR13_MINITEST_DOC2_TEXT,
    FR13_MINITEST_DOC2_TITLE,
    FR14_BAD_TEXT,
    FR14_BAD_TITLE,
    FR14_GOOD_TEXT,
    FR14_GOOD_TITLE,
    FR14_MINITEST_TEXT,
    FR14_MINITEST_TITLE,
    FR14_SITUATION_TEXT,
    FR14_SITUATION_TITLE,
    FR15_MINITEST_TEXT,
    FR15_MINITEST_TITLE,
    FR15_TRANSCRIPT_A_TEXT,
    FR15_TRANSCRIPT_A_TITLE,
    FR15_TRANSCRIPT_B_TEXT,
    FR15_TRANSCRIPT_B_TITLE,
)
from app.v1.models import (
    GenerationSource,
    Question,
    create_source_document,
)


def _already_imported(db: Session, uaa: UAA) -> bool:
    return bool(
        db.query(Question).filter_by(uaa_id=uaa.id, generation_source=GenerationSource.IMPORTED).count()
    )


def _documents(db: Session, module: Module, *pairs: tuple[str, str]) -> list[int]:
    documents = [
        create_source_document(db, title=title, content_text=text, module_id=module.id)
        for title, text in pairs
    ]
    db.flush()
    return [document.current_version_id for document in documents]


# =============================================================================================
# FR11 — Construire un argument développé
# =============================================================================================


def import_francais_fr11_to_bank(db: Session, module: Module, uaa: UAA) -> int:
    if _already_imported(db, uaa):
        return 0
    model_id, weak_id, mt_id = _documents(
        db, module,
        (FR11_MODEL_TITLE, FR11_MODEL_TEXT),
        (FR11_WEAK_TITLE, FR11_WEAK_TEXT),
        (FR11_MINITEST_TITLE, FR11_MINITEST_TEXT),
    )
    questions: list[tuple[str, dict]] = [
        (
            "classification",
            {
                "prompt": "Le paragraphe modèle sur le covoiturage est un argument développé. Classe chacune de ses phrases selon le rôle qu'elle joue dans l'argument.",
                "source_document_version_id": model_id,
                "categories": ["Idée annoncée", "Explication", "Exemple ou preuve", "Lien avec la thèse"],
                "elements": [
                    "« Ainsi, chez Transmétal, […] les employés inscrits au programme de covoiturage […] déclarent économiser en moyenne 85 euros par mois. »",
                    "« C'est pourquoi une entreprise qui organise le covoiturage améliore concrètement le pouvoir d'achat de son personnel, sans augmenter les salaires. »",
                    "« D'abord, le covoiturage permet aux travailleurs de réduire nettement leurs frais de déplacement. »",
                    "« En effet, lorsque deux ou trois collègues partagent la même voiture, le prix du carburant, du parking et de l'usure du véhicule est divisé entre eux. »",
                ],
                "correct_categories": [2, 3, 0, 1],
                "explanation": "L'idée est annoncée par « D'abord », expliquée par « En effet », prouvée par « Ainsi » (85 euros chez Transmétal) et reliée à la thèse par « C'est pourquoi ».",
            },
        ),
        (
            "document_analysis",
            {
                "prompt": "Le paragraphe à améliorer sur le télétravail n'est pas un argument développé. Relève deux défauts précis de ce paragraphe, en citant chaque fois le passage concerné, et explique pourquoi chacun affaiblit l'argumentation.",
                "source_document_version_id": weak_id,
                "rubric": "2 points : deux défauts distincts correctement identifiés et cités (1 point chacun), parmi : affirmations gratuites sans explication (« Le télétravail c'est bien », « c'est l'avenir ») ; généralisation (« Tout le monde est d'accord ») ; anecdote isolée présentée comme preuve (« Mon cousin télétravaille et il est content ») ; idée non développée (« on ne prend pas la voiture ») ; absence de connecteurs logiques ; répétitions du mot « télétravail ». Chaque défaut doit être accompagné d'une explication de la faiblesse (le lecteur n'est pas convaincu, un cas ne prouve pas une règle, etc.).",
                "expected_points": ["Défaut 1 identifié, cité et expliqué", "Défaut 2 identifié, cité et expliqué"],
                "max_score": 2.0,
            },
        ),
        (
            "long_answer",
            {
                "prompt": "Réécris le paragraphe à améliorer sur le télétravail pour en faire UN argument développé (5 à 7 phrases) : une idée annoncée, une explication, un exemple ou une preuve, puis une phrase de lien avec la thèse. Utilise au moins trois connecteurs logiques différents.",
                "source_document_version_id": weak_id,
                "rubric": "4 points : idée annoncée clairement en une phrase (1 point) ; explication du mécanisme, le « pourquoi » (1 point) ; exemple concret ou preuve, sans simple anecdote présentée comme une règle générale (1 point) ; phrase de lien avec la thèse « les employés de bureau devraient pouvoir télétravailler un jour par semaine » ET au moins trois connecteurs logiques différents correctement employés (1 point). Une réponse qui recopie le paragraphe d'origine ou se limite à des affirmations gratuites obtient 0.",
                "expected_points": ["Idée annoncée", "Explication", "Exemple ou preuve", "Lien avec la thèse et connecteurs variés"],
                "max_score": 4.0,
            },
        ),
        (
            "classification",
            {
                "prompt": "Classe chaque connecteur logique selon la relation qu'il exprime.",
                "categories": ["Cause", "Conséquence", "Opposition", "Concession"],
                "elements": ["par conséquent", "en effet", "certes… mais", "pourtant", "puisque", "c'est pourquoi", "bien que", "cependant"],
                "correct_categories": [1, 0, 3, 2, 0, 1, 3, 2],
                "explanation": "Cause : en effet, puisque. Conséquence : par conséquent, c'est pourquoi. Opposition : pourtant, cependant. Concession : certes… mais, bien que.",
            },
        ),
        (
            "long_answer",
            {
                "prompt": "À partir de la fiche de préparation sur les stages obligatoires, rédige UN paragraphe argumentatif développé qui défend la thèse imposée. Ton paragraphe doit utiliser au moins une des informations numérotées de la fiche, en précisant d'où elle vient.",
                "source_document_version_id": mt_id,
                "rubric": "4 points : idée annoncée en lien avec la thèse « le stage devrait être obligatoire » (1 point) ; explication du mécanisme (1 point) ; utilisation fidèle d'au moins une information de la fiche (enquête Avenir Jeunes 58 % / 39 %, témoignage de Kevin, avis de la directrice de menuiserie) avec sa source (1 point) ; phrase de lien avec la thèse et connecteurs logiques adaptés (1 point). Un chiffre déformé ou une information absente de la fiche présentée comme venant de la fiche fait perdre le point de l'exemple.",
                "expected_points": ["Idée annoncée", "Explication", "Information de la fiche utilisée avec sa source", "Lien avec la thèse"],
                "max_score": 4.0,
            },
        ),
        (
            "short_answer",
            {
                "prompt": "La fiche de préparation sur les stages obligatoires signale une objection (information 4). Rédige une concession de deux ou trois phrases qui reconnaît une part de vérité à cette objection, puis montre que la thèse reste défendable.",
                "source_document_version_id": mt_id,
                "rubric": "Bonne réponse si elle reconnaît d'abord la part de vérité de l'objection (les petites entreprises manquent de temps pour encadrer un stagiaire) avec une formule de concession (« Certes », « Il est vrai que », « Même si »), puis utilise un connecteur d'opposition (« mais », « pourtant », « cependant ») pour montrer que le stage obligatoire reste possible ou souhaitable (aide de l'école, autres entreprises, encadrement partagé...). Une simple opposition sans reconnaissance de l'objection n'est pas une concession.",
                "max_length": 700,
            },
        ),
        (
            "short_answer",
            {
                "prompt": "Dans la fiche de préparation sur les stages obligatoires, le témoignage de Kevin (information 2) peut-il, à lui seul, prouver que le stage devrait être obligatoire pour tous les élèves ? Justifie.",
                "source_document_version_id": mt_id,
                "rubric": "Bonne réponse si elle répond non : le témoignage de Kevin est un exemple, un cas particulier, qui illustre un argument mais ne prouve pas une règle générale à lui seul (risque de généralisation). Bonus de justification : l'enquête de l'information 1 (600 anciens élèves, données chiffrées) est une preuve plus large ; le témoignage peut compléter cette preuve.",
                "max_length": 600,
            },
        ),
        (
            "vocabulary",
            {
                "prompt": "Qu'appelle-t-on une « affirmation gratuite » dans un texte argumentatif ?",
                "rubric": "Bonne réponse si elle explique qu'il s'agit d'une idée lancée sans explication ni exemple ou preuve pour la justifier — le lecteur doit croire l'auteur sur parole, ce qui ne convainc pas.",
            },
        ),
    ]
    return _import_course(db, module, uaa, questions)


# =============================================================================================
# FR12 — Rédiger un texte argumentatif
# =============================================================================================


def import_francais_fr12_to_bank(db: Session, module: Module, uaa: UAA) -> int:
    if _already_imported(db, uaa):
        return 0
    model_id, intros_id, mt_id = _documents(
        db, module,
        (FR12_MODEL_TITLE, FR12_MODEL_TEXT),
        (FR12_INTROS_TITLE, FR12_INTROS_TEXT),
        (FR12_MINITEST_TITLE, FR12_MINITEST_TEXT),
    )
    questions: list[tuple[str, dict]] = [
        (
            "short_answer",
            {
                "prompt": "Dans la lettre ouverte pour une maison de jeunes, quelle est l'amorce de l'introduction ? Explique en une phrase pourquoi elle est efficace.",
                "source_document_version_id": model_id,
                "rubric": "Bonne réponse si elle identifie l'amorce : la fermeture de l'ancienne salle paroissiale en 2024, qui laisse les jeunes sans lieu de rencontre encadré, et explique qu'elle est efficace parce qu'elle part d'un fait concret, directement lié au sujet, qui fait comprendre le problème au lecteur.",
                "max_length": 500,
            },
        ),
        (
            "document_analysis",
            {
                "prompt": "Dans la lettre ouverte pour une maison de jeunes, quelle objection les auteurs traitent-ils ? S'agit-il d'une concession ou d'une réfutation ? Justifie en citant les mots qui le montrent et les éléments utilisés pour répondre.",
                "source_document_version_id": model_id,
                "rubric": "3 points : objection identifiée — le coût du projet pour la commune (1 point) ; reconnue comme une concession, justifiée par la structure « Certes… Pourtant… » qui reconnaît la crainte avant d'y répondre (1 point) ; éléments de réponse cités : bâtiment déjà communal, subvention de la Fédération des maisons de jeunes, coût restant d'environ 18 000 euros par an inférieur au budget des réparations du mobilier urbain (1 point).",
                "expected_points": ["Objection du coût identifiée", "Concession justifiée par « Certes… Pourtant »", "Éléments chiffrés de la réponse cités"],
                "max_score": 3.0,
            },
        ),
        (
            "classification",
            {
                "prompt": "L'introduction B (article sur l'uniforme) est complète. Classe chacun de ses passages selon la partie de l'introduction qu'il constitue.",
                "source_document_version_id": intros_id,
                "categories": ["Amorce", "Présentation du sujet", "Thèse", "Annonce du plan"],
                "elements": [
                    "« La direction propose d'imposer un uniforme dès la rentrée prochaine. »",
                    "« l'uniforme ne ferait pas disparaître les inégalités, il coûterait cher aux familles et il empêcherait les élèves d'exprimer leur personnalité »",
                    "« Chaque matin, devant les grilles, on remarque tout de suite qui porte des vêtements de marque et qui n'en porte pas. »",
                    "« Je pense que ce serait une erreur »",
                ],
                "correct_categories": [1, 3, 0, 2],
                "explanation": "L'amorce part d'une scène concrète (les grilles), le sujet est la proposition de la direction, la thèse est « ce serait une erreur » et la fin de phrase annonce les trois arguments.",
            },
        ),
        (
            "document_analysis",
            {
                "prompt": "Parmi les trois introductions à comparer sur l'uniforme, explique pourquoi l'introduction C ne convient pas pour un article d'opinion, en t'appuyant sur au moins deux éléments précis du texte.",
                "source_document_version_id": intros_id,
                "rubric": "2 points : amorce trop générale, sans lien direct avec le sujet (préhistoire, évolution des vêtements, mode à la télévision) (1 point) ; absence de thèse et d'annonce du plan — on ne sait pas si l'auteur est pour ou contre l'uniforme ni ce qu'il va développer ; le sujet de l'uniforme à l'école n'est même pas posé (1 point).",
                "expected_points": ["Amorce trop générale relevée", "Absence de thèse, de sujet ou d'annonce du plan relevée"],
                "max_score": 2.0,
            },
        ),
        (
            "short_answer",
            {
                "prompt": "Dans la lettre ouverte pour une maison de jeunes, quel passage fait le bilan dans la conclusion, et quelle ouverture la termine ?",
                "source_document_version_id": model_id,
                "rubric": "Bonne réponse si elle identifie le bilan (« une maison de jeunes rue des Tilleuls serait un investissement utile pour la sécurité, la vie du village et l'avenir de nos adolescents », qui rappelle les arguments) et l'ouverture (la proposition de présenter le projet en détail lors de la prochaine séance du conseil).",
                "max_length": 500,
            },
        ),
        (
            "long_answer",
            {
                "prompt": "Rédige le courriel argumentatif demandé dans le sujet du repair café (250 à 300 mots), adressé à M. Renard, en respectant toutes les exigences de la consigne.",
                "source_document_version_id": mt_id,
                "rubric": "6 points : codes du courriel respectés — objet précis, formule d'appel, formule de politesse, signature, registre courant ou soutenu sans tutoiement (1 point) ; introduction avec contexte et thèse en faveur du repair café (1 point) ; au moins deux arguments développés, chacun avec explication et exemple, en exploitant fidèlement les informations fournies (2 points) ; réponse à l'objection des habitants qui veulent garder la salle pour les fêtes, par concession ou réfutation (par exemple : la salle est libre trois samedis matin sur quatre) (1 point) ; conclusion avec bilan et longueur proche de 250-300 mots (1 point). Ne jamais pénaliser une longueur légèrement différente si le texte est complet ; pénaliser un texte nettement trop court qui ne développe pas ses arguments.",
                "expected_points": ["Codes du courriel et registre", "Introduction avec thèse", "Deux arguments développés", "Objection traitée", "Conclusion et longueur"],
                "max_score": 6.0,
            },
        ),
        (
            "short_answer",
            {
                "prompt": "Pour le sujet du repair café, quel registre de langue dois-tu utiliser dans ton courriel à M. Renard ? Propose une formule d'appel et une formule de politesse adaptées.",
                "source_document_version_id": mt_id,
                "rubric": "Bonne réponse si elle indique un registre courant ou soutenu (vouvoiement, sans abréviations ni familiarités), parce que M. Renard est le président du comité et que l'élève ne le connaît pas personnellement, et propose une formule d'appel adaptée (« Monsieur le Président, » ou « Monsieur, ») et une formule de politesse adaptée (« Je vous prie d'agréer, Monsieur le Président, mes salutations distinguées. » ou équivalent).",
                "max_length": 500,
            },
        ),
        (
            "short_answer",
            {
                "prompt": "Pourquoi ne faut-il pas ajouter un argument nouveau dans la conclusion d'un texte argumentatif ? Que doit contenir la conclusion à la place ?",
                "rubric": "Bonne réponse si elle explique que la conclusion sert à faire le bilan (rappeler la thèse et les arguments déjà développés, sans les recopier) et éventuellement à proposer une ouverture ; un argument nouveau ne serait ni développé ni prouvé et déséquilibrerait le plan — il a sa place dans le développement.",
                "max_length": 500,
            },
        ),
        (
            "vocabulary",
            {
                "prompt": "Qu'est-ce qu'une « lettre ouverte » ?",
                "rubric": "Bonne réponse si elle explique qu'il s'agit d'une lettre adressée à une personne ou à une autorité (par exemple un conseil communal) mais rendue publique, pour convaincre aussi un large public.",
            },
        ),
    ]
    return _import_course(db, module, uaa, questions)


# =============================================================================================
# FR13 — Utiliser un dossier documentaire dans son argumentation
# =============================================================================================


def import_francais_fr13_to_bank(db: Session, module: Module, uaa: UAA) -> int:
    if _already_imported(db, uaa):
        return 0
    d1_id, d2_id, d3_id, mt1_id, mt2_id = _documents(
        db, module,
        (FR13_DOC1_TITLE, FR13_DOC1_TEXT),
        (FR13_DOC2_TITLE, FR13_DOC2_TEXT),
        (FR13_DOC3_TITLE, FR13_DOC3_TEXT),
        (FR13_MINITEST_DOC1_TITLE, FR13_MINITEST_DOC1_TEXT),
        (FR13_MINITEST_DOC2_TITLE, FR13_MINITEST_DOC2_TEXT),
    )
    questions: list[tuple[str, dict]] = [
        (
            "classification",
            {
                "prompt": "Thèse à défendre : « la rue scolaire des Glycines doit devenir définitive ». Classe chaque information du dossier selon qu'elle soutient cette thèse, la contredit, ou la nuance.",
                "source_document_version_ids": [d1_id, d2_id, d3_id],
                "categories": ["Soutient la thèse", "Contredit la thèse", "Nuance la thèse"],
                "elements": [
                    "La part des enfants venant à pied ou à vélo est passée de 34 % à 52 %.",
                    "Le boulanger estime avoir perdu environ 10 % de son chiffre d'affaires du matin.",
                    "La rue scolaire ne règle pas la pollution le reste de la journée.",
                    "Aucun accident n'a été signalé devant l'école, contre trois accrochages l'année précédente.",
                    "Certains parents regrettent de devoir se garer plus loin les jours de pluie.",
                ],
                "correct_categories": [0, 1, 2, 0, 1],
                "explanation": "Les comptages et l'absence d'accident soutiennent la thèse ; la perte du boulanger et la gêne des parents la contredisent ; la limite indiquée par l'agence (pollution réduite seulement aux heures d'entrée et de sortie) la nuance.",
            },
        ),
        (
            "short_answer",
            {
                "prompt": "Reformule avec tes propres mots, sans guillemets et en indiquant la source, l'information principale du document 3 sur la pollution devant les écoles qui ont une rue scolaire.",
                "source_document_version_id": d3_id,
                "rubric": "Bonne réponse si elle reformule fidèlement (pollution au dioxyde d'azote environ un tiers ou 37 % plus faible, ou 24 au lieu de 38 microgrammes par mètre cube, devant les écoles avec une rue scolaire, aux heures d'entrée et de sortie), avec des mots personnels (pas de recopie de phrases entières) et avec la source (document 3, agence Air Wallon Mesures). Une réponse qui écrit que la pollution est supprimée déforme le document.",
                "max_length": 500,
            },
        ),
        (
            "source_comparison",
            {
                "prompt": "Le document 1 et le document 2 parlent tous deux de la rue scolaire des Glycines. Explique en quoi ils s'opposent, puis montre comment le document 2 peut quand même être utilisé dans un texte qui défend la rue scolaire.",
                "source_document_version_ids": [d1_id, d2_id],
                "rubric": "3 points : opposition identifiée — le document 1 présente un bilan positif chiffré (plus d'enfants à pied ou à vélo, aucun accident, 71 % des parents favorables) tandis que le document 2 exprime une perte de clientèle (environ 10 %) et un manque de consultation (1 point) ; nuance du document 2 relevée — le boulanger ne refuse pas la mesure et propose une signalisation des commerces (1 point) ; utilisation proposée — traiter le document 2 comme une objection, par concession, en reprenant sa propre proposition pour y répondre (1 point).",
                "expected_points": ["Opposition entre les deux documents expliquée", "Nuance du témoignage relevée", "Usage du document 2 comme objection traitée"],
                "max_score": 3.0,
            },
        ),
        (
            "document_analysis",
            {
                "prompt": "Un élève écrit dans sa rédaction : « Selon le document 1, tous les parents veulent que la rue scolaire devienne définitive. » Explique pourquoi cette phrase déforme le document 1, puis propose une phrase fidèle.",
                "source_document_version_id": d1_id,
                "rubric": "2 points : déformation expliquée — le document indique 71 % de parents favorables (une majorité, pas tous) et précise que certains regrettent de devoir se garer plus loin (1 point) ; phrase corrigée fidèle, avec la source, par exemple « D'après le document 1, 71 % des parents interrogés souhaitent que la rue scolaire devienne définitive » (1 point).",
                "expected_points": ["Déformation expliquée (71 %, pas tous)", "Phrase fidèle avec source proposée"],
                "max_score": 2.0,
            },
        ),
        (
            "classification",
            {
                "prompt": "Voici trois phrases d'élèves qui utilisent le dossier sur la rue scolaire. Classe chacune selon la manière dont elle utilise le document.",
                "source_document_version_ids": [d2_id, d3_id],
                "categories": ["Citation correctement intégrée", "Reformulation correcte avec source", "Copier-coller sans guillemets ni source"],
                "elements": [
                    "Le dioxyde d'azote irrite les voies respiratoires et aggrave l'asthme, en particulier chez les enfants.",
                    "Le boulanger du quartier reconnaît qu'il comprend « qu'on veuille protéger les enfants » (document 2).",
                    "D'après l'agence Air Wallon Mesures (document 3), l'air est nettement moins pollué devant les écoles fermées aux voitures aux heures d'entrée et de sortie.",
                ],
                "correct_categories": [2, 0, 1],
                "explanation": "La première phrase recopie le document 3 sans guillemets ni source ; la deuxième reprend les mots exacts du boulanger entre guillemets, introduits et sourcés ; la troisième redit l'information du document 3 avec d'autres mots, en citant la source.",
            },
        ),
        (
            "long_answer",
            {
                "prompt": "Thèse : « la ville de Hautmont-sur-Sambre devrait installer d'autres fontaines à eau gratuites ». En t'appuyant sur les documents 1 et 2 du mini-test, rédige un paragraphe argumentatif développé qui utilise au moins une information du document 1 (citée ou reformulée, avec sa source) et qui traite l'objection exprimée dans le document 2.",
                "source_document_version_id": mt1_id,
                "source_document_version_ids": [mt1_id, mt2_id],
                "rubric": "5 points : argument annoncé et expliqué en faveur de nouvelles fontaines (1 point) ; information du document 1 utilisée fidèlement (41 000 litres, environ 82 000 bouteilles évitées, coût d'installation et d'entretien, analyses mensuelles) et sourcée (1 point) ; citation entre guillemets ou reformulation correcte, sans copier-coller (1 point) ; objection du document 2 traitée honnêtement — fontaine en panne en août, crainte sur l'hygiène — par concession ou réfutation, par exemple avec les analyses mensuelles de qualité citées par la ville (1 point) ; lien final avec la thèse et connecteurs adaptés (1 point).",
                "expected_points": ["Argument annoncé et expliqué", "Information du document 1 fidèle et sourcée", "Citation ou reformulation correcte", "Objection du document 2 traitée", "Lien avec la thèse"],
                "max_score": 5.0,
            },
        ),
        (
            "short_answer",
            {
                "prompt": "Le courrier de Mme Gilson (document 2 du mini-test) soutient-il, contredit-il ou nuance-t-il le projet d'installer d'autres fontaines ? Justifie avec un élément précis du courrier.",
                "source_document_version_id": mt2_id,
                "rubric": "Bonne réponse si elle indique que le courrier nuance le projet (il reconnaît « une belle idée » mais demande d'abord d'entretenir les fontaines existantes et d'expliquer le contrôle de l'eau) — accepter aussi « contredit en partie » si la justification mentionne la panne d'août ou la crainte sur l'hygiène ET la reconnaissance que l'idée est bonne. Un élément précis du courrier doit être cité ou reformulé.",
                "max_length": 500,
            },
        ),
        (
            "vocabulary",
            {
                "prompt": "Quelle est la différence entre une « citation » et une « reformulation » quand on utilise un document dans son argumentation ?",
                "rubric": "Bonne réponse si elle explique que la citation reprend les mots exacts de l'auteur entre guillemets, alors que la reformulation redit l'idée avec ses propres mots sans guillemets — et que, dans les deux cas, il faut indiquer la source.",
            },
        ),
    ]
    return _import_course(db, module, uaa, questions)


# =============================================================================================
# FR14 — Réclamation et adaptation au destinataire
# =============================================================================================


def import_francais_fr14_to_bank(db: Session, module: Module, uaa: UAA) -> int:
    if _already_imported(db, uaa):
        return 0
    situation_id, bad_id, good_id, mt_id = _documents(
        db, module,
        (FR14_SITUATION_TITLE, FR14_SITUATION_TEXT),
        (FR14_BAD_TITLE, FR14_BAD_TEXT),
        (FR14_GOOD_TITLE, FR14_GOOD_TEXT),
        (FR14_MINITEST_TITLE, FR14_MINITEST_TEXT),
    )
    questions: list[tuple[str, dict]] = [
        (
            "document_analysis",
            {
                "prompt": "Relève trois défauts différents du courriel de Kevin à ÉlectroPlus et propose, pour chacun, une correction précise.",
                "source_document_version_id": bad_id,
                "rubric": "3 points (1 point par défaut identifié ET corrigé), parmi : objet inutilisable (« !!!!! ») → objet avec référence et motif ; formule d'appel familière (« Salut ») → « Madame, Monsieur, » ; faits absents (produit, commande, date, panne) → exposé daté et précis ; demande vague (« réglez ça vite ») → demande précise avec délai ; ton agressif et insultes (« produits pourris ») → ton ferme mais courtois ; menace (« avis négatifs partout ») → supprimée ; absence de formule de politesse et de coordonnées → ajoutées. Un défaut identifié sans correction vaut 0,5 point.",
                "expected_points": ["Défaut 1 et correction", "Défaut 2 et correction", "Défaut 3 et correction"],
                "max_score": 3.0,
            },
        ),
        (
            "short_answer",
            {
                "prompt": "D'après la situation de l'aspirateur livré en panne, quelles informations précises (références, dates, montant) Sarah doit-elle absolument mentionner dans sa réclamation ? Cites-en au moins quatre.",
                "source_document_version_id": situation_id,
                "rubric": "Bonne réponse si elle cite au moins quatre informations exactes parmi : numéro de commande EP-48213 ; modèle AS-300 ; date de commande (3 mars 2026) ; date de livraison (7 mars) ; date de la panne (8 mars) ; appel au service client le 10 mars avec promesse de rappel sous 48 heures non tenue ; prix de 189 euros. Une information inexacte annule le point correspondant.",
                "max_length": 600,
            },
        ),
        (
            "classification",
            {
                "prompt": "Classe chaque passage du courriel modèle de Sarah Lambert selon la partie de la réclamation qu'il constitue.",
                "source_document_version_id": good_id,
                "categories": ["Exposé des faits", "Justification de la demande", "Demande précise", "Formule de politesse"],
                "elements": [
                    "« Conformément à vos conditions générales de vente, qui prévoient l'échange ou le remboursement d'un produit défectueux signalé dans les 30 jours »",
                    "« je vous prie d'agréer, Madame, Monsieur, mes salutations distinguées »",
                    "« Dès la première utilisation, le 8 mars, la batterie ne s'est pas chargée »",
                    "« je vous demande de bien vouloir me rembourser la somme de 189 euros »",
                ],
                "correct_categories": [1, 3, 0, 2],
                "explanation": "Les faits sont datés (8 mars), la justification s'appuie sur les conditions générales de vente, la demande est chiffrée (189 euros) et la formule de politesse clôt le courriel.",
            },
        ),
        (
            "short_answer",
            {
                "prompt": "Dans le courriel modèle de Sarah Lambert, relève une formulation qui montre la fermeté et une formulation qui montre la courtoisie. Explique pourquoi ce mélange est efficace.",
                "source_document_version_id": good_id,
                "rubric": "Bonne réponse si elle cite une marque de fermeté (« je vous demande », le montant précis de 189 euros, le délai « avant le 31 mars 2026 », la référence aux conditions générales) et une marque de courtoisie (« de bien vouloir », « Je vous remercie », la formule de politesse, le vouvoiement), et explique que la demande reste claire et déterminée sans braquer le destinataire, ce qui augmente les chances d'obtenir le remboursement.",
                "max_length": 600,
            },
        ),
        (
            "long_answer",
            {
                "prompt": "À partir de la situation de l'abonnement prélevé après résiliation, rédige le courriel de réclamation que Nadia envoie au siège de FitZone.",
                "source_document_version_id": mt_id,
                "rubric": "6 points : objet précis avec la référence du contrat FZ-7731 et le motif (1 point) ; formule d'appel et registre adaptés à une entreprise, vouvoiement (1 point) ; exposé chronologique et exact des faits — résiliation le 2 janvier avec accusé de réception, prélèvements du 5 février et du 5 mars, réponse de l'accueil le 8 mars (1 point) ; justification par le contrat (préavis d'un mois, fin au 2 février) (1 point) ; double demande précise — remboursement de 69,80 euros ET confirmation écrite de la fin du contrat — avec un délai (1 point) ; ton ferme et courtois, pièce jointe mentionnée (accusé de réception), formule de politesse et signature (1 point). Une erreur sur les dates ou les montants fait perdre le point de l'exposé.",
                "expected_points": ["Objet avec référence", "Registre adapté", "Faits exacts et chronologiques", "Justification par le contrat", "Double demande précise avec délai", "Ton, pièce jointe, politesse"],
                "max_score": 6.0,
            },
        ),
        (
            "short_answer",
            {
                "prompt": "Propose un objet précis pour le courriel de réclamation de Nadia à FitZone.",
                "source_document_version_id": mt_id,
                "rubric": "Bonne réponse si l'objet contient la référence du contrat (FZ-7731) ET le motif (prélèvements après résiliation, demande de remboursement), par exemple « Contrat FZ-7731 — prélèvements après résiliation, demande de remboursement ». Un objet vague (« Problème », « Réclamation », « Urgent ») ne convient pas.",
                "max_length": 200,
            },
        ),
        (
            "short_answer",
            {
                "prompt": "Nadia raconte aussi la situation de son abonnement à son frère par message. Cite deux différences entre ce message et le courriel envoyé à FitZone, et explique ce qui les justifie.",
                "source_document_version_id": mt_id,
                "rubric": "Bonne réponse si elle cite deux différences pertinentes (registre familier et tutoiement possibles avec le frère / vouvoiement et registre courant ou soutenu avec l'entreprise ; expression des émotions possible avec le frère / faits, références et montants précis pour l'entreprise ; pas d'objet ni de formule de politesse obligatoires avec le frère / codes du courriel avec l'entreprise) et explique qu'elles viennent du destinataire et du but différents (partager une expérience vs obtenir un remboursement).",
                "max_length": 700,
            },
        ),
        (
            "vocabulary",
            {
                "prompt": "Que signifie adopter un ton « ferme mais courtois » dans une réclamation ?",
                "rubric": "Bonne réponse si elle explique qu'il faut formuler une demande claire et déterminée (faits précis, demande précise, délai) tout en restant poli et respectueux (vouvoiement, formules de politesse, aucune insulte ni menace).",
            },
        ),
    ]
    return _import_course(db, module, uaa, questions)


# =============================================================================================
# FR15 — Défendre une opinion oralement
# =============================================================================================


def import_francais_fr15_to_bank(db: Session, module: Module, uaa: UAA) -> int:
    if _already_imported(db, uaa):
        return 0
    a_id, b_id, mt_id = _documents(
        db, module,
        (FR15_TRANSCRIPT_A_TITLE, FR15_TRANSCRIPT_A_TEXT),
        (FR15_TRANSCRIPT_B_TITLE, FR15_TRANSCRIPT_B_TEXT),
        (FR15_MINITEST_TITLE, FR15_MINITEST_TEXT),
    )
    questions: list[tuple[str, dict]] = [
        (
            "short_answer",
            {
                "prompt": "Dans la transcription de l'intervention de Yanis, relève deux marqueurs oraux différents et explique le rôle de chacun pour les auditeurs.",
                "source_document_version_id": a_id,
                "rubric": "Bonne réponse si elle cite deux marqueurs exacts (« je voudrais vous donner deux raisons », « Première raison », « Deuxième raison », « Je sais que la question de la surveillance se pose », « Donc, pour résumer ») et explique leur rôle : annoncer le plan, signaler le passage d'une idée à l'autre, introduire l'objection ou la conclusion — l'auditeur, qui ne peut pas relire, peut ainsi suivre la structure.",
                "max_length": 600,
            },
        ),
        (
            "document_analysis",
            {
                "prompt": "Dans la transcription de l'intervention de Léa, relève deux défauts liés à la voix ou à l'attitude, puis un défaut lié au contenu de son propos. Cite chaque fois l'indice du texte qui le montre.",
                "source_document_version_id": b_id,
                "rubric": "3 points : deux défauts de voix ou d'attitude avec indice (reste assise ; lit sa feuille sans lever les yeux ; parle très vite ; hésitations « euh », « voilà » ; perd sa ligne) (2 points, 1 par défaut) ; un défaut de contenu avec indice (position jamais annoncée — un délégué doit la demander ; argument des vieux ordinateurs non développé ; attaque personnelle « c'est toujours les mêmes » ; généralisation « tout le monde le sait » ; absence de conclusion « c'est tout ») (1 point).",
                "expected_points": ["Défaut de voix ou d'attitude 1", "Défaut de voix ou d'attitude 2", "Défaut de contenu"],
                "max_score": 3.0,
            },
        ),
        (
            "source_comparison",
            {
                "prompt": "Compare la manière dont Yanis et Léa commencent et terminent leur intervention au conseil des élèves. Quelles conséquences ces choix ont-ils pour les auditeurs ?",
                "source_document_version_ids": [a_id, b_id],
                "rubric": "3 points : ouverture comparée — Yanis salue, donne sa position dès la première phrase et annonce deux raisons ; Léa commence par des hésitations et n'annonce jamais sa position (1 point) ; clôture comparée — Yanis résume (« plus d'égalité et plus de calme ») et remercie ; Léa termine par « Voilà, c'est tout » puis hésite sur sa position (1 point) ; conséquence pour les auditeurs — on suit et on retient le propos de Yanis, alors qu'on ne sait pas ce que défend Léa (un délégué doit le lui demander) (1 point).",
                "expected_points": ["Ouvertures comparées", "Clôtures comparées", "Conséquence pour les auditeurs"],
                "max_score": 3.0,
            },
        ),
        (
            "classification",
            {
                "prompt": "Classe chaque comportement d'orateur selon ce qu'il concerne à l'oral.",
                "categories": ["Communication non verbale (regard, posture, gestes)", "Voix (volume, débit, articulation, pauses)", "Contenu et structure du propos"],
                "elements": [
                    "Annoncer ses deux raisons dès le début",
                    "Regarder l'assemblée plutôt que sa feuille",
                    "Marquer une courte pause avant un argument important",
                    "Rester assis·e, les yeux baissés",
                    "Parler très vite",
                    "Résumer son avis en une phrase avant de remercier",
                ],
                "correct_categories": [2, 0, 1, 0, 1, 2],
                "explanation": "Le regard et la posture relèvent du non-verbal ; le débit et les pauses relèvent de la voix ; l'annonce des raisons et le résumé final relèvent de la structure du propos.",
            },
        ),
        (
            "long_answer",
            {
                "prompt": "Pour la réunion d'équipe sur les horaires d'été, choisis ta position (pour ou contre les horaires de 7 h à 14 h) et rédige ta fiche aide-mémoire en mots-clés : position, deux arguments avec un exemple ou un chiffre chacun, l'objection que tu prévois et ta réponse, ta phrase de conclusion.",
                "source_document_version_id": mt_id,
                "rubric": "5 points : position claire, pour ou contre — les deux sont acceptées (1 point) ; deux arguments distincts appuyés sur des informations fidèles de la situation (65 % des ventes avant 13 h, plus de 32 °C dans l'entrepôt pendant 18 jours, concurrents ouverts jusqu'à 18 h, difficulté des collègues parents) (2 points) ; objection prévue et réponse cohérente (1 point) ; forme d'une vraie fiche aide-mémoire — mots-clés, brève, organisée, pas un texte entièrement rédigé à lire — et phrase de conclusion (1 point).",
                "expected_points": ["Position claire", "Deux arguments appuyés", "Objection et réponse", "Forme aide-mémoire et conclusion"],
                "max_score": 5.0,
            },
        ),
        (
            "short_answer",
            {
                "prompt": "Pour la réunion d'équipe sur les horaires d'été, rédige les deux ou trois premières phrases que tu prononcerais pour ouvrir ton intervention.",
                "source_document_version_id": mt_id,
                "rubric": "Bonne réponse si l'ouverture salue l'auditoire (la responsable et les collègues), donne la position dès le début (pour ou contre les horaires de 7 h à 14 h, les deux sont acceptées) et annonce les raisons qui vont suivre avec un marqueur oral (« pour deux raisons », « je voudrais vous expliquer pourquoi ») ; registre courant adapté à une réunion de travail. Une ouverture sans position annoncée ne convient pas.",
                "max_length": 700,
            },
        ),
        (
            "short_answer",
            {
                "prompt": "Pendant la réunion d'équipe sur les horaires d'été, un collègue t'objecte : « Les concurrents restent ouverts jusqu'à 18 h, on va perdre des clients l'après-midi. » Rédige ta réponse orale en deux ou trois phrases, en commençant par reformuler l'objection.",
                "source_document_version_id": mt_id,
                "rubric": "Bonne réponse si elle reformule d'abord l'objection (« Tu crains qu'on perde des clients parce que les concurrents restent ouverts… »), puis répond calmement avec un argument ou une proposition (par exemple : 65 % des ventes de juillet se font déjà avant 13 h ; ouvrir quelques après-midis ; concession possible), sans attaque personnelle. Si l'élève est contre les nouveaux horaires, accepter une réponse qui reformule, concède et appuie l'objection de manière argumentée.",
                "max_length": 700,
            },
        ),
        (
            "vocabulary",
            {
                "prompt": "Qu'est-ce qu'une « attaque personnelle » dans un débat, et pourquoi faut-il l'éviter quand on défend une opinion oralement ?",
                "rubric": "Bonne réponse si elle explique qu'il s'agit de critiquer la personne (ou un groupe de personnes) au lieu de son idée ou de son argument, et qu'il faut l'éviter parce qu'elle ne prouve rien, blesse ou braque l'auditoire et fait perdre sa crédibilité à celui qui la prononce.",
            },
        ),
    ]
    return _import_course(db, module, uaa, questions)
