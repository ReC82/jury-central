"""Banque V1 Français — FR16→FR19 (ticket #94, PHASE D).

Même principe que `app.v1.francais_fr11_15_bank` (PHASE C) : import idempotent,
hand-authored, revalidé par le registre #40 avant stockage, chaque support cité réellement
rattaché. FR20 n'a pas de banque propre : son entraînement et son examen blanc tirent dans
FR01→FR19 (`app.v1.session_service._start_francais_transversal_session`), comme FSE17."""

from sqlalchemy.orm import Session

from app.models import UAA, Module
from app.v1 import question_types  # noqa: F401 — enregistre les 26 types (#40) au chargement
from app.v1.francais_fr06_10_bank import _import_course
from app.v1.francais_fr11_15_bank import _already_imported, _documents
from app.v1.francais_fr16_20_content import (
    FR16_BAD_TEXT,
    FR16_BAD_TITLE,
    FR16_GOOD_TEXT,
    FR16_GOOD_TITLE,
    FR16_MINITEST_TEXT,
    FR16_MINITEST_TITLE,
    FR17_MINITEST_TEXT,
    FR17_MINITEST_TITLE,
    FR17_STORY_TEXT,
    FR17_STORY_TITLE,
    FR18_AMPLIFIED_TEXT,
    FR18_AMPLIFIED_TITLE,
    FR18_MINITEST_TEXT,
    FR18_MINITEST_TITLE,
    FR18_SCENE_TEXT,
    FR18_SCENE_TITLE,
    FR18_SOURCE_TEXT,
    FR18_SOURCE_TITLE,
    FR19_MINITEST_TEXT,
    FR19_MINITEST_TITLE,
    FR19_MODEL_TEXT,
    FR19_MODEL_TITLE,
    FR19_WEAK_TEXT,
    FR19_WEAK_TITLE,
)

# =============================================================================================
# FR16 — Discuter et négocier
# =============================================================================================


def import_francais_fr16_to_bank(db: Session, module: Module, uaa: UAA) -> int:
    if _already_imported(db, uaa):
        return 0
    good_id, bad_id, mt_id = _documents(
        db, module,
        (FR16_GOOD_TITLE, FR16_GOOD_TEXT),
        (FR16_BAD_TITLE, FR16_BAD_TEXT),
        (FR16_MINITEST_TITLE, FR16_MINITEST_TEXT),
    )
    questions: list[tuple[str, dict]] = [
        (
            "short_answer",
            {
                "prompt": "Dans la négociation des congés d'été, quelle est la position de départ d'Amira, et quel besoin réel révèle-t-elle ensuite ?",
                "source_document_version_id": good_id,
                "rubric": "Bonne réponse si elle distingue la position (trois semaines de congé du 1er au 21 juillet) et le besoin réel (être en vacances la semaine du 14 juillet, la seule où sa sœur peut garder ses enfants en Espagne). Une réponse qui confond les deux ne convient pas.",
                "max_length": 500,
            },
        ),
        (
            "classification",
            {
                "prompt": "Classe chaque réplique de la négociation des congés d'été selon l'outil de négociation qu'elle utilise.",
                "source_document_version_id": good_id,
                "categories": ["Reformulation", "Proposition conditionnelle", "Concession", "Récapitulation de l'accord"],
                "elements": [
                    "« Et je peux faire deux dimanches de plus en juin pour compenser. »",
                    "« Donc on note : congés du 14 juillet au 3 août, et je travaille les dimanches 15 et 22 juin. »",
                    "« Si je comprends bien, le problème, c'est d'avoir au moins quatre personnes présentes pendant les deux premières semaines ? »",
                    "« Si je prends du 14 juillet au 3 août, je suis présente pendant la première quinzaine, quand Julien et Sofia sont absents. »",
                ],
                "correct_categories": [2, 3, 0, 1],
                "explanation": "Amira reformule le problème de M. Lenoir, fait une proposition « si…, alors », concède deux dimanches de travail et récapitule l'accord final.",
            },
        ),
        (
            "document_analysis",
            {
                "prompt": "Explique pourquoi la discussion entre Bruno et Dylan sur la salle de pause échoue. Relève trois comportements précis qui bloquent l'échange, en citant chaque fois la réplique concernée.",
                "source_document_version_id": bad_id,
                "rubric": "3 points (1 par comportement cité et nommé), parmi : accusation au lieu d'un message en « je » (« Tu le fais exprès ou quoi ? ») ; généralisation (« Tout le monde aime bien, sauf toi », « Les jeunes, de toute façon, vous ne respectez rien ») ; attaque personnelle (« tu râles tout le temps, c'est pour ça que personne ne mange avec toi ») ; menace (« je vais aller voir le patron ») ; refus de poursuivre l'échange (« je m'en fiche ») ; aucune reformulation, question ou proposition. Bonus de compréhension attendu : la conséquence (le problème n'est pas réglé, la musique continue, Bruno mange dans sa voiture).",
                "expected_points": ["Comportement bloquant 1 cité", "Comportement bloquant 2 cité", "Comportement bloquant 3 cité"],
                "max_score": 3.0,
            },
        ),
        (
            "short_answer",
            {
                "prompt": "Réécris la première réplique de Bruno dans la discussion sur la salle de pause sous la forme d'un message en « je », suivi d'une question ouverte.",
                "source_document_version_id": bad_id,
                "rubric": "Bonne réponse si la réplique exprime le ressenti ou le besoin de Bruno à la première personne (par exemple : « J'ai besoin de calme pour me reposer pendant le temps de midi »), sans accusation, et se termine par une vraie question ouverte qui invite Dylan à proposer une solution (« Comment pourrait-on faire… ? », « Qu'est-ce que tu proposerais ? »). Une question fermée (oui/non) ou une accusation maintenue ne convient pas.",
                "max_length": 500,
            },
        ),
        (
            "long_answer",
            {
                "prompt": "À partir de la situation de la sortie de fin d'année, identifie le besoin réel de chacun des deux groupes, puis propose une solution de compromis ou gagnant-gagnant qui respecte toutes les contraintes du titulaire. Justifie ta proposition.",
                "source_document_version_id": mt_id,
                "rubric": "5 points : besoin du groupe de Marwa identifié (un moment de détente tous ensemble) (1 point) ; besoin du groupe de Lucas identifié (que des élèves découvrent la mer, un souvenir commun) (1 point) ; solution qui respecte le budget de 30 euros et la limite de 15 euros pour trois élèves — le parc à 39 euros plus le car dépasse le budget, alors que la mer en train à 9 euros avec pique-nique le respecte (1 point) ; solution qui satisfait aussi le besoin de l'autre groupe (par exemple des activités ludiques à la plage, un jeu organisé, une activité de détente) (1 point) ; justification claire et respect du jour de semaine entre le 15 et le 25 juin (1 point).",
                "expected_points": ["Besoin du groupe de Marwa", "Besoin du groupe de Lucas", "Respect du budget et de la limite de 15 euros", "Solution qui satisfait les deux besoins", "Justification et contraintes de date"],
                "max_score": 5.0,
            },
        ),
        (
            "short_answer",
            {
                "prompt": "Lors de la réunion de vendredi sur la sortie de fin d'année, Marwa dit : « La mer, c'est nul, on s'ennuie. » Rédige la réponse de Lucas : il reformule d'abord ce que dit Marwa, puis pose une question ouverte pour comprendre son besoin.",
                "source_document_version_id": mt_id,
                "rubric": "Bonne réponse si Lucas reformule calmement la crainte de Marwa (« Si je comprends bien, tu as peur qu'on s'ennuie à la mer ? ») sans l'attaquer, puis pose une question ouverte sur son besoin (« Qu'est-ce qui serait important pour toi pendant cette journée ? »). Une réponse agressive, une contre-attaque ou une question fermée ne convient pas.",
                "max_length": 500,
            },
        ),
        (
            "vocabulary",
            {
                "prompt": "Dans une négociation, quelle est la différence entre la « position » et le « besoin » d'une personne ?",
                "rubric": "Bonne réponse si elle explique que la position est ce que la personne demande ou réclame, alors que le besoin (ou intérêt) est la raison profonde de cette demande — et que chercher les besoins permet souvent de trouver un accord quand les positions semblent incompatibles.",
            },
        ),
        (
            "vocabulary",
            {
                "prompt": "Qu'est-ce qu'une solution « gagnant-gagnant », et en quoi est-elle différente d'un simple compromis ?",
                "rubric": "Bonne réponse si elle explique qu'une solution gagnant-gagnant satisfait les besoins essentiels des deux parties, alors que dans un compromis chacun cède une partie de sa demande (chacun perd un peu).",
            },
        ),
    ]
    return _import_course(db, module, uaa, questions)


# =============================================================================================
# FR17 — Comprendre et transformer une œuvre culturelle
# =============================================================================================


def import_francais_fr17_to_bank(db: Session, module: Module, uaa: UAA) -> int:
    if _already_imported(db, uaa):
        return 0
    story_id, mt_id = _documents(
        db, module,
        (FR17_STORY_TITLE, FR17_STORY_TEXT),
        (FR17_MINITEST_TITLE, FR17_MINITEST_TEXT),
    )
    questions: list[tuple[str, dict]] = [
        (
            "short_answer",
            {
                "prompt": "Dans la nouvelle « Le dernier bus », relève deux indications de lieu et deux indications de temps qui forment le cadre spatio-temporel du récit.",
                "source_document_version_id": story_id,
                "rubric": "Bonne réponse si elle cite deux indications de lieu exactes (Charleroi, l'arrêt de bus de la ligne 52, l'avenue, la route qui longe des entrepôts déserts, l'immeuble, la boulangerie) et deux indications de temps exactes (un soir de novembre, 21 h 40, le mardi, sous la pluie depuis des heures, le dimanche suivant). Une indication inventée annule le point correspondant.",
                "max_length": 500,
            },
        ),
        (
            "classification",
            {
                "prompt": "Classe chaque passage de la nouvelle « Le dernier bus » selon l'étape du schéma narratif qu'il représente.",
                "source_document_version_id": story_id,
                "categories": ["Situation initiale", "Élément perturbateur", "Péripétie", "Élément de résolution", "Situation finale"],
                "elements": [
                    "Une camionnette blanche ralentit à la hauteur de Maëlle, qui a peur.",
                    "Maëlle ne sort plus jamais sans une batterie de secours dans son sac.",
                    "Maëlle sort de son entraînement de basket et compte prendre le bus de 21 h 40.",
                    "La mère de Maëlle, au téléphone, donne son accord et Monsieur Ferreira la ramène.",
                    "Maëlle voit le dernier bus disparaître et son téléphone s'éteint.",
                ],
                "correct_categories": [2, 4, 0, 3, 1],
                "explanation": "Équilibre de départ (le bus habituel), rupture (le bus raté, le téléphone éteint), obstacle (la camionnette inquiétante), résolution (l'accord de la mère et le trajet), nouvel équilibre (la batterie de secours).",
            },
        ),
        (
            "document_analysis",
            {
                "prompt": "Dans « Le dernier bus », le narrateur dit « elle » : est-ce un narrateur interne ou externe ? Quel point de vue adopte-t-il ? Justifie ta réponse par deux passages précis du texte.",
                "source_document_version_id": story_id,
                "rubric": "3 points : narrateur externe, car il n'est pas un personnage et raconte à la troisième personne (1 point) ; point de vue interne, centré sur Maëlle (1 point) ; deux passages justificatifs qui montrent les sensations ou pensées de Maëlle seule (« la gorge serrée », « Son cœur se mit à battre très fort », « Elle hésita. Sa mère lui avait toujours dit… ») — jamais les pensées de Monsieur Ferreira (1 point).",
                "expected_points": ["Narrateur externe justifié", "Point de vue interne de Maëlle", "Deux passages justificatifs"],
                "max_score": 3.0,
            },
        ),
        (
            "long_answer",
            {
                "prompt": "Réécris la scène de la rencontre sur la route (de l'arrivée de la camionnette jusqu'à l'appel à la mère) du point de vue de Monsieur Ferreira, en 10 à 15 lignes. Respecte les faits et le cadre de la nouvelle.",
                "source_document_version_id": story_id,
                "rubric": "5 points : point de vue de Monsieur Ferreira réellement adopté — ses perceptions et pensées, pas celles de Maëlle (2 points) ; cohérence avec les faits — camionnette blanche, retour de livraison d'un restaurant, nuit et pluie, route des entrepôts, Maëlle demande qu'il téléphone à sa mère avec son portable (2 points) ; temps de narration cohérent avec la nouvelle (passé simple et imparfait) et longueur respectée (1 point). Un fait contredit (moto, plein jour, Maëlle monte sans prévenir sa mère) fait perdre des points de cohérence.",
                "expected_points": ["Point de vue de Monsieur Ferreira", "Cohérence avec les faits et le cadre", "Temps et longueur"],
                "max_score": 5.0,
            },
        ),
        (
            "short_answer",
            {
                "prompt": "Dans le récit mini-test « La boîte dans le grenier », qui raconte l'histoire ? S'agit-il d'un narrateur interne ou externe ? Justifie par un indice du texte.",
                "source_document_version_id": mt_id,
                "rubric": "Bonne réponse si elle indique que l'histoire est racontée par le petit-fils de la grand-mère, un personnage de l'histoire, donc un narrateur interne, et le justifie par l'emploi de la première personne (« j'ai trouvé », « je me suis assis », « ma grand-mère »). Accepter « le petit-enfant » ou « un membre de la famille » si l'indice est correct.",
                "max_length": 400,
            },
        ),
        (
            "document_analysis",
            {
                "prompt": "Dans le récit mini-test « La boîte dans le grenier », quel est l'élément perturbateur, et quelle est la situation finale ? Explique ce qui a changé entre le début et la fin du récit.",
                "source_document_version_id": mt_id,
                "rubric": "3 points : élément perturbateur identifié — la découverte de la boîte en fer cachée dans le grenier (1 point) ; situation finale identifiée — la photo de Jumet encadrée dans le salon et la réflexion du narrateur sur les histoires de famille (1 point) ; changement expliqué — une histoire familiale inconnue est révélée et partagée, la famille se rapproche (souvenirs de l'oncle, émotion de la mère) (1 point).",
                "expected_points": ["Élément perturbateur", "Situation finale", "Changement expliqué"],
                "max_score": 3.0,
            },
        ),
        (
            "long_answer",
            {
                "prompt": "Écris une suite de 10 à 15 lignes au récit mini-test « La boîte dans le grenier » : le narrateur décide de retrouver la famille italienne de sa grand-mère. Ta suite doit rester cohérente avec le récit (personnages, faits, narrateur).",
                "source_document_version_id": mt_id,
                "rubric": "5 points : narrateur interne conservé (« je ») (1 point) ; cohérence avec les faits établis — lettres à la sœur restée en Italie, photo de Jumet en 1962, grand-père réparateur de vélos, famille qui découvre la boîte (2 points) ; suite logique centrée sur la recherche de la famille italienne, avec au moins une action concrète (1 point) ; temps du récit cohérent avec l'original (passé composé et imparfait) et longueur respectée (1 point).",
                "expected_points": ["Narrateur interne conservé", "Cohérence avec les faits", "Suite logique et concrète", "Temps et longueur"],
                "max_score": 5.0,
            },
        ),
        (
            "vocabulary",
            {
                "prompt": "Quelle est la différence entre l'« auteur » et le « narrateur » d'un récit ?",
                "rubric": "Bonne réponse si elle explique que l'auteur est la personne réelle qui a écrit le texte, tandis que le narrateur est la voix qui raconte l'histoire dans le texte (il peut être un personnage, « je », ou être absent de l'histoire, « il/elle »).",
            },
        ),
    ]
    return _import_course(db, module, uaa, questions)


# =============================================================================================
# FR18 — Amplifier, recomposer et transposer
# =============================================================================================


def import_francais_fr18_to_bank(db: Session, module: Module, uaa: UAA) -> int:
    if _already_imported(db, uaa):
        return 0
    source_id, amplified_id, scene_id, mt_id = _documents(
        db, module,
        (FR18_SOURCE_TITLE, FR18_SOURCE_TEXT),
        (FR18_AMPLIFIED_TITLE, FR18_AMPLIFIED_TEXT),
        (FR18_SCENE_TITLE, FR18_SCENE_TEXT),
        (FR18_MINITEST_TITLE, FR18_MINITEST_TEXT),
    )
    questions: list[tuple[str, dict]] = [
        (
            "short_answer",
            {
                "prompt": "Relève les éléments essentiels du fait divers sur le chien Pilou, en répondant aux questions qui ? quoi ? où ? quand ?",
                "source_document_version_id": source_id,
                "rubric": "Bonne réponse si elle indique : qui — le chien Pilou et son maître Arnaud Collard, 68 ans (et/ou les bénévoles) ; quoi — le chien perdu pendant une promenade en forêt a retrouvé seul la maison de son maître, épuisé mais en bonne santé ; où — à Durbuy ; quand — lundi, après trois jours de disparition. Au moins trois des quatre réponses exactes.",
                "max_length": 500,
            },
        ),
        (
            "source_comparison",
            {
                "prompt": "Compare le fait divers sur Pilou et sa version amplifiée. Relève trois ajouts différents de la version amplifiée et nomme chaque fois le procédé d'amplification utilisé (description, portrait, dialogue, pensées, précisions).",
                "source_document_version_ids": [source_id, amplified_id],
                "rubric": "3 points (1 par ajout cité ET procédé correctement nommé), parmi : pensées (« Je n'aurais jamais dû le lâcher dans la forêt », « se répétait-il ») ; description (le chien couvert de boue, les pattes en sang, la langue pendante ; la gamelle pleine dans la cuisine) ; paroles/dialogue (« Pilou ! ») ; émotions (sans appétit, la voix cassée) ; précisions ou suite vraisemblable (le vétérinaire, la tarte aux pommes avec les bénévoles).",
                "expected_points": ["Ajout 1 et procédé", "Ajout 2 et procédé", "Ajout 3 et procédé"],
                "max_score": 3.0,
            },
        ),
        (
            "document_analysis",
            {
                "prompt": "La transposition en scène de théâtre du retour de Pilou n'a plus de narrateur. Explique comment le texte de théâtre transmet malgré tout le décor, les gestes et les émotions, en citant deux exemples précis.",
                "source_document_version_id": scene_id,
                "rubric": "2 points : explication — le décor, les gestes et le ton passent par les didascalies, et l'histoire avance par les répliques des personnages et les bruits (1 point) ; deux exemples précis cités (« La cuisine d'Arnaud. Une table, une chaise, une gamelle pleine posée par terre », « fixant la gamelle », « On entend un grattement à la porte », « s'agenouillant, la voix tremblante », « Il prend le chien dans ses bras. Noir. ») (1 point).",
                "expected_points": ["Rôle des didascalies et des répliques", "Deux exemples précis"],
                "max_score": 2.0,
            },
        ),
        (
            "classification",
            {
                "prompt": "Classe chaque consigne de réécriture selon la technique qu'elle demande.",
                "categories": ["Amplifier", "Recomposer", "Transposer"],
                "elements": [
                    "Raconte l'histoire en commençant par la fin, puis reviens trois jours en arrière.",
                    "Ajoute le portrait du maître et ses pensées pendant l'attente.",
                    "Fais de ce récit une scène de théâtre avec répliques et didascalies.",
                    "Raconte la même histoire comme si elle se passait au Moyen Âge.",
                    "Commence au milieu de l'action, au moment où le chien gratte à la porte.",
                    "Insère un dialogue entre le maître et un bénévole.",
                ],
                "correct_categories": [1, 0, 2, 2, 1, 0],
                "explanation": "Changer l'ordre (fin d'abord, in medias res) = recomposer ; ajouter portrait, pensées ou dialogue = amplifier ; changer de genre ou d'époque = transposer.",
            },
        ),
        (
            "long_answer",
            {
                "prompt": "Amplifie le texte bref de la panne d'ascenseur en un récit de 15 à 20 lignes. Ajoute au moins une description, un court dialogue et les pensées d'un des deux personnages, sans changer les faits du texte.",
                "source_document_version_id": mt_id,
                "rubric": "5 points : au moins une description (lieu, ascenseur, personnages) (1 point) ; un dialogue correctement ponctué entre Mme Dewez et Yassine (1 point) ; les pensées ou émotions d'un personnage (1 point) ; faits conservés — jeudi soir, Liège, entre le 4e et le 5e étage, quarante minutes, pompiers, pizza partagée dans le hall (1 point) ; ajouts vraisemblables, cohérents et longueur respectée (1 point).",
                "expected_points": ["Description", "Dialogue", "Pensées ou émotions", "Faits conservés", "Vraisemblance et longueur"],
                "max_score": 5.0,
            },
        ),
        (
            "long_answer",
            {
                "prompt": "Transpose le texte bref de la panne d'ascenseur en article de presse : rédige un titre, un chapeau qui répond à qui ? quoi ? où ? quand ?, puis un court paragraphe au ton neutre.",
                "source_document_version_id": mt_id,
                "rubric": "4 points : titre informatif et accrocheur (1 point) ; chapeau qui répond à qui (Mme Dewez et un livreur de pizzas, Yassine), quoi (bloqués dans un ascenseur en panne), où (immeuble de Liège, entre le 4e et le 5e étage), quand (jeudi soir) (1 point) ; paragraphe factuel à la troisième personne, sans pensées intimes inventées (1 point) ; faits fidèles au texte (quarante minutes, intervention des pompiers, pizza partagée) (1 point).",
                "expected_points": ["Titre", "Chapeau complet", "Ton neutre et factuel", "Faits fidèles"],
                "max_score": 4.0,
            },
        ),
        (
            "short_answer",
            {
                "prompt": "Recompose le début du texte bref de la panne d'ascenseur en commençant in medias res. Rédige les deux ou trois premières phrases de ta version.",
                "source_document_version_id": mt_id,
                "rubric": "Bonne réponse si le récit commence au milieu de l'action (par exemple au moment où l'ascenseur s'arrête brutalement, ou pendant l'attente dans la cabine bloquée) et non par la présentation chronologique « jeudi soir, dans un immeuble… », tout en respectant les faits du texte (Mme Dewez, Yassine, la panne entre deux étages).",
                "max_length": 600,
            },
        ),
        (
            "vocabulary",
            {
                "prompt": "Qu'est-ce qu'une « didascalie » dans un texte de théâtre ?",
                "rubric": "Bonne réponse si elle explique qu'il s'agit d'une indication de mise en scène, distincte des répliques, qui précise le décor, les gestes, les déplacements ou le ton des personnages.",
            },
        ),
    ]
    return _import_course(db, module, uaa, questions)


# =============================================================================================
# FR19 — Relater une expérience culturelle et motiver son appréciation
# =============================================================================================


def import_francais_fr19_to_bank(db: Session, module: Module, uaa: UAA) -> int:
    if _already_imported(db, uaa):
        return 0
    model_id, weak_id, mt_id = _documents(
        db, module,
        (FR19_MODEL_TITLE, FR19_MODEL_TEXT),
        (FR19_WEAK_TITLE, FR19_WEAK_TEXT),
        (FR19_MINITEST_TITLE, FR19_MINITEST_TEXT),
    )
    questions: list[tuple[str, dict]] = [
        (
            "short_answer",
            {
                "prompt": "Dans le compte rendu de l'exposition « Mains d'artisans », relève les informations qui relatent la situation de la visite (quoi, où, quand, avec qui).",
                "source_document_version_id": model_id,
                "rubric": "Bonne réponse si elle relève : quoi — l'exposition temporaire « Mains d'artisans » sur une trentaine de métiers manuels ; où — au musée de la Vie wallonne, à Liège ; quand — samedi dernier ; avec qui — avec la classe de 5e année. Au moins trois des quatre éléments exacts.",
                "max_length": 500,
            },
        ),
        (
            "document_analysis",
            {
                "prompt": "Dans le compte rendu de l'exposition « Mains d'artisans », l'appréciation est organisée en trois raisons. Pour chacune, indique le critère utilisé et l'exemple précis qui la justifie.",
                "source_document_version_id": model_id,
                "rubric": "3 points (1 par raison complète) : interactivité / possibilité de toucher et d'essayer — exemple : raboter une planche ; lien entre le passé et le présent — exemple : le forgeron placé à côté du réparateur de smartphones ; rencontre avec un artisan / émotion — exemple : l'ébéniste qui a quitté un emploi de bureau à 35 ans. Critère sans exemple : 0,5 point.",
                "expected_points": ["Raison 1 : critère et exemple", "Raison 2 : critère et exemple", "Raison 3 : critère et exemple"],
                "max_score": 3.0,
            },
        ),
        (
            "classification",
            {
                "prompt": "Classe chaque phrase d'avis selon qu'elle exprime un simple goût personnel ou une appréciation motivée.",
                "categories": ["Goût personnel non justifié", "Appréciation motivée (critère + exemple)"],
                "elements": [
                    "J'ai adoré, c'était le meilleur concert de ma vie.",
                    "Le décor est simple mais efficace : la lumière qui passe de l'orange au bleu suffit à faire sentir le changement de saison.",
                    "Franchement, c'était trop bien.",
                    "L'exposition est interactive : on peut raboter une planche et sentir la difficulté du geste.",
                    "Je n'ai pas aimé, c'était nul.",
                ],
                "correct_categories": [0, 1, 0, 1, 0],
                "explanation": "Une appréciation motivée nomme un critère (décor, interactivité) et l'illustre par un exemple précis ; les autres phrases n'expriment qu'un ressenti sans justification.",
            },
        ),
        (
            "document_analysis",
            {
                "prompt": "Explique pourquoi l'avis sur le concert de Nova Lys ne convainc pas le lecteur. Relève trois défauts précis, en citant chaque fois le passage concerné.",
                "source_document_version_id": weak_id,
                "rubric": "3 points (1 par défaut cité), parmi : rien n'est relaté — ni lieu, ni date, ni style de musique ; goût personnel sans critère ni exemple (« J'ai adoré », « c'était trop bien ») ; superlatifs vides (« le meilleur concert de ma vie », « Tout était parfait ») ; attaque des lecteurs qui pensent autrement (« Ceux qui n'aiment pas sont nuls ») ; registre familier et ponctuation excessive (« trop bien !!! ») ; aucune nuance ni limite ; recommandation non justifiée (« Allez-y c'est trop bien »).",
                "expected_points": ["Défaut 1 cité", "Défaut 2 cité", "Défaut 3 cité"],
                "max_score": 3.0,
            },
        ),
        (
            "long_answer",
            {
                "prompt": "À partir des notes de sortie sur la pièce « Le Banc », rédige un compte rendu de 200 à 250 mots pour le journal de ton école : relate la sortie, donne une appréciation motivée par au moins deux critères avec des exemples précis, mentionne une limite et termine par une recommandation.",
                "source_document_version_id": mt_id,
                "rubric": "6 points : situation relatée fidèlement — titre, compagnie, lieu, date, sortie de classe (1 point) ; histoire présentée brièvement sans tout dévoiler (1 point) ; au moins deux critères d'appréciation illustrés par des exemples tirés des notes — jeu de l'actrice, humour ou excès du boxeur, décor et lumière, accordéon, scène de l'apprentissage de la lecture (2 points) ; une limite formulée avec nuance — début lent, acteur qui crie dans les scènes tristes (1 point) ; recommandation adaptée au lectorat du journal de l'école, vocabulaire appréciatif précis, longueur respectée (1 point).",
                "expected_points": ["Situation relatée", "Histoire résumée", "Deux critères illustrés", "Limite nuancée", "Recommandation et vocabulaire"],
                "max_score": 6.0,
            },
        ),
        (
            "short_answer",
            {
                "prompt": "D'après les notes de sortie sur la pièce « Le Banc », rédige une phrase d'appréciation nuancée sur le jeu de l'acteur qui interprète l'ancien boxeur, en utilisant au moins un modalisateur.",
                "source_document_version_id": mt_id,
                "rubric": "Bonne réponse si la phrase reconnaît une qualité (il fait rire toute la salle avec ses histoires de combat) ET une limite (il crie un peu trop dans les scènes tristes), avec au moins un modalisateur (« un peu », « parfois », « assez », « malgré », « même si »…). Une phrase uniquement positive ou uniquement négative ne convient pas.",
                "max_length": 400,
            },
        ),
        (
            "vocabulary",
            {
                "prompt": "Qu'est-ce qu'un « modalisateur » dans une appréciation ? Donne deux exemples.",
                "rubric": "Bonne réponse si elle explique qu'un modalisateur est un mot ou une expression qui nuance un jugement (en atténuant ou en renforçant), avec deux exemples corrects (« un peu », « assez », « particulièrement », « plutôt », « parfois », « malgré »…).",
            },
        ),
        (
            "vocabulary",
            {
                "prompt": "Que signifie « relater » une expérience culturelle ?",
                "rubric": "Bonne réponse si elle explique qu'il s'agit de raconter l'expérience avec précision pour quelqu'un qui ne l'a pas vécue : quoi, où, quand, avec qui, et le déroulement ou le contenu, avant de donner son avis.",
            },
        ),
    ]
    return _import_course(db, module, uaa, questions)
