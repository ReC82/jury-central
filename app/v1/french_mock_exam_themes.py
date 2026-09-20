"""Catalogue de thèmes — Examen blanc CESS Français (§ 4 du chantier).

Liste INDICATIVE, jamais une limite stricte pour le moteur (le prompt de génération,
`app.ai.french_mock_exam_prompts`, autorise explicitement un thème hors liste si
accessible/non spécialisé/riche/compatible synthèse-argumentation — mais la sélection
SERVEUR, ci-dessous, reste bornée à cette liste pour garder l'anti-répétition fiable et
testable sans dépendre du bon vouloir du modèle)."""

MOCK_EXAM_THEMES: tuple[tuple[str, str], ...] = (
    ("theme-ia", "L'intelligence artificielle dans la vie quotidienne"),
    ("theme-ecole", "L'école et les méthodes d'apprentissage"),
    ("theme-reseaux-sociaux", "Les réseaux sociaux et leurs usages"),
    ("theme-monde-travail", "Le monde du travail aujourd'hui"),
    ("theme-teletravail", "Le télétravail"),
    ("theme-environnement", "L'environnement et les gestes du quotidien"),
    ("theme-lecture", "La lecture à l'ère du numérique"),
    ("theme-culture", "L'accès à la culture"),
    ("theme-mobilite", "La mobilité et les déplacements"),
    ("theme-alimentation", "L'alimentation et les habitudes de consommation"),
    ("theme-sport", "Le sport et son rôle dans la société"),
    ("theme-consommation", "La consommation responsable"),
    ("theme-vie-privee-numerique", "La vie privée à l'ère numérique"),
    ("theme-ecrans", "Le temps passé devant les écrans"),
    ("theme-technologie", "La technologie et ses usages au quotidien"),
    ("theme-engagement-citoyen", "L'engagement citoyen des jeunes"),
    ("theme-rapport-travail", "Le rapport au travail chez les jeunes générations"),
    ("theme-medias", "Les médias et l'information"),
    ("theme-sante-publique", "La santé publique au quotidien"),
    ("theme-societe", "Les évolutions de la société"),
)

MOCK_EXAM_THEMES_BY_KEY: dict[str, str] = dict(MOCK_EXAM_THEMES)
