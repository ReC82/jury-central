# Assets visuels V1 et questions d'identification (ticket #48)

## Modèle

Aucune nouvelle table : le ticket réutilise `Asset` et `QuestionAsset` (ticket #38, § F).

| Besoin | Où |
|---|---|
| Format (image raster, SVG…) | `Asset.kind` |
| Origine (externe, IA, manuel, officiel) | `Asset.source_type` |
| Nature : photo réelle / illustration générée / schéma technique | `Asset.metadata_json["visual_type"]` (`app.v1.assets.VisualType`) |
| Source, licence, provenance | `Asset.source_url`, `Asset.license`, `Asset.provenance` ; auteur, texte alternatif, légende dans `metadata_json` |
| Consigne de génération (illustration IA) | `metadata_json["generation_prompt"]` |
| Lien question → image | `QuestionAsset(question_version_id, asset_id, role)` — la **version** de question référence l'asset **par ID** |
| Statut (actif, invalide…) | `Asset.status` (`ContentStatus`) |

Fichiers livrés avec le code : `app/static/img/ampcr/`.

## Règles

- **Pas de doublon** : `get_or_create_asset` compare l'empreinte SHA-256 du fichier ; un
  fichier déjà connu est réutilisé, jamais réenregistré. Un même asset sert plusieurs
  questions (ex. le schéma de carte mère : 2 questions).
- **Pas de nouvelle image si un asset adapté existe** : les questions d'une banque rédigée
  pointent vers les assets existants ; aucune génération à l'ouverture d'une page.
- **Asset IA conservé** dans la banque avec sa consigne de génération.
- **Pas de validation manuelle obligatoire** : un asset est actif dès sa création.
- **Signalement** : l'élève signale « image incorrecte » depuis les résultats ; l'admin
  marque l'asset incorrect (`/admin/bank/assets`) → les questions dont la version courante
  l'utilise sortent du tirage (`unusable_asset_question_ids`), jusqu'à réactivation ou
  remplacement. Les sessions déjà créées ne changent jamais.
- **Régénération** : manuelle (`python -m app.v1.assets regenerate`), uniquement pour un
  asset IA avec consigne conservée ; crée un nouvel asset et une nouvelle version de
  chaque question concernée. Photo et schéma : remplacement manuel du fichier.
- Le contrat d'assets de chaque type de question (`AssetContract`, ticket #40) est vérifié
  à chaque rattachement (`link_asset`).

## Types de question servis

| Type | Réponse élève | Correction (locale, sans IA) |
|---|---|---|
| `image_identification`, mode `choice` | choix unique parmi des composants | comme un QCM |
| `image_identification`, mode `text` | nom du composant écrit | réponses acceptées (normalisées) ; sinon grille |
| `diagram_labeling` | une liste déroulante par repère (A, B…) | comme une classification, avec points partiels |

Ces types ne sont **jamais générés par l'IA** (`BRIDGE_TYPES` inchangé) : une question
visuelle n'a de sens qu'avec une image réelle déjà enregistrée. L'image n'est jamais
envoyée au correcteur.

`hotspot` (zones cliquables) existe dans le registre mais n'est **pas** branché en V1
(préparé : schéma à repères lettrés + `diagram_labeling` couvre le besoin sans
interaction tactile complexe).

## Affichage

`_question_assets.html` : image pleine largeur du conteneur, hauteur plafonnée (60 % de
l'écran), lien « agrandir » (nouvel onglet, zoom natif sur mobile), légende : nature,
auteur, licence, lien source. Présent sur la question et dans les résultats.

## Banque MC01 (`app/v1/ampcr_visual_bank.py`)

10 questions, 9 assets : 7 photos réelles (Wikimedia Commons, licences libres), 1
illustration générée (carte graphique, SVG), 1 schéma technique (carte mère, repères
A–F). Import idempotent au premier accès « S'entraîner »/« S'évaluer » de MC01.
