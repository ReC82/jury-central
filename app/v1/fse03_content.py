"""Documents support — FSE03 « Identités, traces numériques et appartenance » (ticket
#97, cahier des charges détaillé ; présentation réaliste ticket #118).

Deux documents originaux, rédigés pour ce cours (jamais une modification d'une source
officielle — `docs/content_workflow.md`), illustrant l'application explicitement demandée
par le ticket #97 : classer des traces numériques puis expliquer les conséquences
d'anciennes publications dans une candidature. Les personnes et organisations citées sont
fictives, créées pour cet exercice.

Deux formes pour chaque document (même principe que FSE01/FSE02, tickets #103/#108/#115) :
- `FSE03_*_TEXT` (texte brut, inchangé depuis le ticket #96) : utilisé pour créer le
  `SourceDocument`/`SourceDocumentVersion` de la banque de questions
  (`app.v1.fse_bank.import_fse03_to_bank`) — jamais modifié.
- `FSE03_*_CARD_HTML` (ticket #118) : le MÊME contenu, mis en forme comme de vrais
  documents visibles (carte de profil professionnel, publication de réseau social, forum,
  recommandation, groupes). Les classifications pédagogiques (trace volontaire/involontaire,
  ancienne...) ne sont JAMAIS indiquées sur les documents eux-mêmes — elles appartiennent
  uniquement à l'analyse placée après, dans `app.v1.fse03_course`."""

from pathlib import Path

FSE03_PROFILE_TITLE = "Présence en ligne de Sophie Lambert — éléments retrouvés par une recherche"
FSE03_PROFILE_TEXT = """[Éléments retrouvés en ligne au sujet de Sophie Lambert, candidate fictive à un poste \
de gestionnaire de stock, créés pour cet exercice]

1. Une photo de profil professionnelle, publiée par Sophie elle-même sur un réseau \
professionnel, accompagnée d'un résumé de son parcours.

2. Une photo prise lors d'un anniversaire il y a deux ans, sur laquelle Sophie apparaît : \
la photo a été publiée par une amie, qui y a identifié Sophie par son nom. Sophie n'a \
jamais publié cette photo elle-même et n'a pas demandé son retrait.

3. Un commentaire écrit par Sophie il y a cinq ans, sous son vrai nom, sur un forum de \
jeux vidéo : le ton y est très familier et comporte des insultes adressées à d'autres \
joueurs dans le feu d'une partie en ligne.

4. Une recommandation professionnelle écrite par un ancien collègue de Sophie sur le même \
réseau professionnel, décrivant Sophie comme « rigoureuse et fiable dans la gestion des \
commandes ».

5. Sophie est membre visible de deux groupes en ligne : un groupe de randonneurs \
amateurs de sa région, et un groupe professionnel rassemblant des gestionnaires de stock \
du secteur de la logistique."""

# ---------------------------------------------------------------------------------------
# Présentation réaliste (ticket #118) — cinq documents distincts, chacun un fichier
# statique illustré quand pertinent. Portrait et scène d'anniversaire : voir
# `app.v1.fse03_image` (même personnage dans les deux, image de référence réutilisée pour
# la cohérence). Vérification d'existence au chargement du module (lecture disque locale,
# jamais un appel réseau) : rendu de secours en CSS/SVG pur si l'image est absente.
# ---------------------------------------------------------------------------------------

_IMG_DIR = Path(__file__).resolve().parent.parent / "static" / "img"
_PORTRAIT_FILE = _IMG_DIR / "fse03_sophie_portrait.png"
_BIRTHDAY_FILE = _IMG_DIR / "fse03_sophie_birthday.png"
_PORTRAIT_URL = "/static/img/fse03_sophie_portrait.png"
_BIRTHDAY_URL = "/static/img/fse03_sophie_birthday.png"

_PORTRAIT_FALLBACK_SVG = """<div class="jc-poster-fallback" role="img" aria-label="Portrait non disponible : silhouette générique.">
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<circle cx="50" cy="50" r="48" fill="#e3e6ea"></circle>
<circle cx="50" cy="40" r="18" fill="#aeb6bd"></circle>
<path d="M20,88 C20,65 35,58 50,58 C65,58 80,65 80,88 Z" fill="#aeb6bd"></path>
</svg>
</div>"""

_BIRTHDAY_FALLBACK_SVG = """<div class="jc-poster-fallback" role="img" aria-label="Illustration non disponible : trois silhouettes génériques.">
<svg viewBox="0 0 160 100" xmlns="http://www.w3.org/2000/svg">
<circle cx="40" cy="40" r="16" fill="#e3e6ea"></circle>
<path d="M14,86 C14,65 26,58 40,58 C54,58 66,65 66,86 Z" fill="#e3e6ea"></path>
<circle cx="80" cy="36" r="18" fill="#aeb6bd"></circle>
<path d="M50,86 C50,62 64,54 80,54 C96,54 110,62 110,86 Z" fill="#aeb6bd"></path>
<circle cx="122" cy="40" r="16" fill="#e3e6ea"></circle>
<path d="M96,86 C96,65 108,58 122,58 C136,58 148,65 148,86 Z" fill="#e3e6ea"></path>
</svg>
</div>"""


def _portrait_html() -> str:
    if _PORTRAIT_FILE.exists():
        return (
            f'<img src="{_PORTRAIT_URL}" alt="Portrait illustré de Sophie Lambert" '
            f'class="jc-profile-portrait" loading="lazy">'
        )
    return _PORTRAIT_FALLBACK_SVG


def _birthday_html() -> str:
    if _BIRTHDAY_FILE.exists():
        return (
            f'<div class="jc-zoomable" role="img" aria-label="Illustration : Sophie fête son anniversaire avec deux amies, soirée extérieure avec guirlande lumineuse et gâteau.">'
            f'<img src="{_BIRTHDAY_URL}" alt="" class="jc-doc-scene-image" loading="lazy"></div>'
        )
    return _BIRTHDAY_FALLBACK_SVG


FSE03_PROFILE_CARD_HTML = f"""<div class="jc-doc" id="document-profil">
<div class="jc-doc-header"><strong>💼 Profil — réseau professionnel</strong><span class="jc-doc-fictive-badge">Fictif</span></div>
<div class="jc-doc-body">
<div class="jc-profile-head">
{_portrait_html()}
<div>
<p class="jc-profile-name">Sophie Lambert</p>
<p class="jc-profile-function">Gestionnaire de stock</p>
</div>
</div>
<p class="jc-profile-summary">5 ans d'expérience dans la gestion des commandes et le suivi des stocks, secteur de la logistique.</p>
</div>
</div>"""

FSE03_BIRTHDAY_CARD_HTML = f"""<div class="jc-doc jc-social" id="document-anniversaire">
<div class="jc-doc-header"><strong>📱 Publication — réseau social</strong><span class="jc-doc-fictive-badge">Fictif</span></div>
<div class="jc-doc-body">
<div class="jc-social-post-head">
<span class="jc-social-avatar jc-social-avatar--p2" aria-hidden="true">?</span>
<div class="jc-social-meta">
<span class="jc-social-author">Une amie de Sophie</span>
<span class="jc-social-time">il y a deux ans</span>
</div>
</div>
{_birthday_html()}
<p class="jc-social-text">« Meilleur anniversaire entourée de mes copines ! 🎂 » <span class="jc-doc-tag">Sophie Lambert identifiée sur la photo</span></p>
</div>
</div>"""

FSE03_FORUM_CARD_HTML = """<div class="jc-doc" id="document-forum-jeu">
<div class="jc-doc-header"><strong>🎮 Forum — jeux vidéo</strong><span class="jc-doc-fictive-badge">Fictif</span></div>
<div class="jc-doc-body">
<dl class="jc-doc-meta">
<dt>Forum :</dt><dd>Communauté francophone de joueurs</dd>
<dt>Auteur :</dt><dd>Sophie Lambert</dd>
<dt>Publié :</dt><dd>il y a cinq ans</dd>
</dl>
<div class="jc-doc-text">
<p>« Sérieux, t'es vraiment nul à ce jeu, apprends à jouer avant de nous faire perdre la partie ! »</p>
</div>
</div>
</div>"""

FSE03_RECOMMENDATION_CARD_HTML = """<div class="jc-doc" id="document-recommandation">
<div class="jc-doc-header"><strong>💼 Recommandation — réseau professionnel</strong><span class="jc-doc-fictive-badge">Fictif</span></div>
<div class="jc-doc-body">
<div class="jc-quote-card">
<span class="jc-social-avatar jc-social-avatar--p3" aria-hidden="true">?</span>
<div>
<span class="jc-quote-author">Un ancien collègue de Sophie</span>
<p class="jc-quote-text">« Rigoureuse et fiable dans la gestion des commandes. »</p>
</div>
</div>
</div>
</div>"""

FSE03_GROUPS_CARD_HTML = """<div class="jc-doc" id="document-groupes">
<div class="jc-doc-header"><strong>👥 Groupes en ligne</strong><span class="jc-doc-fictive-badge">Fictif</span></div>
<div class="jc-doc-body">
<div class="jc-group-cards">
<div class="jc-group-card">
<span class="jc-group-icon" aria-hidden="true">🥾</span>
<p class="jc-group-name">Randonneurs amateurs de la région</p>
</div>
<div class="jc-group-card">
<span class="jc-group-icon" aria-hidden="true">📦</span>
<p class="jc-group-name">Gestionnaires de stock — secteur logistique</p>
</div>
</div>
</div>
</div>"""

FSE03_HR_NOTE_TITLE = "Note interne du service recrutement — avant l'entretien de Sophie Lambert"
FSE03_HR_NOTE_TEXT = """[Note interne rédigée par un membre du service recrutement d'une entreprise fictive, \
avant un entretien d'embauche, créée pour cet exercice]

Avant l'entretien de demain avec Sophie Lambert, j'ai consulté sa présence en ligne.

Première impression plutôt bonne : la recommandation d'un ancien collègue, qui la décrit \
comme rigoureuse et fiable, correspond bien au profil recherché pour ce poste. Son \
appartenance au groupe professionnel de gestionnaires de stock confirme aussi son \
implication dans le secteur.

Un point m'a cependant interpellé : un ancien commentaire, publié il y a cinq ans sur un \
forum de jeux vidéo, où elle s'exprime de façon très familière et insultante envers \
d'autres joueurs. Ce commentaire date d'avant le début de sa carrière professionnelle et \
concerne un contexte de loisir sans aucun rapport avec le poste, mais il reste visible \
publiquement sous son vrai nom et pourrait donner une impression négative à qui tombe \
dessus sans contexte.

Je vais quand même mener l'entretien normalement, en me concentrant sur son parcours et \
ses compétences réelles — mais ce point me rappelle qu'une publication ancienne, même \
sans lien avec la vie professionnelle, peut rester visible des années plus tard et \
influencer la première impression que l'on se fait de quelqu'un."""

# Ticket #118 : vraie mise en page d'e-mail interne (réutilise EmailCard, voir
# docs/components/EmailCard.md), texte identique à FSE03_HR_NOTE_TEXT ci-dessus, aéré en
# paragraphes, avec expéditeur/destinataire/objet/date fictifs et une signature. Mention
# discrète "Document pédagogique fictif" portée par .jc-doc-fictive-badge (en-tête).
FSE03_HR_NOTE_CARD_HTML = """<div class="jc-doc jc-mail" id="document-note-rh">
<div class="jc-doc-header"><strong>✉️ E-mail interne — service recrutement</strong><span class="jc-doc-fictive-badge">Document pédagogique fictif</span></div>
<div class="jc-mail-thread">
<div class="jc-mail-message">
<div class="jc-mail-message-head">
<span class="jc-mail-avatar" aria-hidden="true">JP</span>
<div class="jc-mail-meta">
<span class="jc-mail-from">Julie Petit <span class="jc-mail-address">&lt;j.petit@entreprise-fictive.be&gt;</span></span>
<span class="jc-mail-to">à Marc Dubois, responsable recrutement</span>
</div>
<span class="jc-mail-date">9 avril 2026, 17h12</span>
</div>
<p class="jc-mail-subject">Préparation de l'entretien — Sophie Lambert</p>
<div class="jc-mail-body">
<p>Bonjour Marc,</p>
<p>Avant l'entretien de demain avec Sophie Lambert, j'ai consulté sa présence en ligne.</p>
<p>Première impression plutôt bonne : la recommandation d'un ancien collègue, qui la décrit comme rigoureuse et fiable, correspond bien au profil recherché pour ce poste. Son appartenance au groupe professionnel de gestionnaires de stock confirme aussi son implication dans le secteur.</p>
<p>Un point m'a cependant interpellé : un ancien commentaire, publié il y a cinq ans sur un forum de jeux vidéo, où elle s'exprime de façon très familière et insultante envers d'autres joueurs. Ce commentaire date d'avant le début de sa carrière professionnelle et concerne un contexte de loisir sans aucun rapport avec le poste, mais il reste visible publiquement sous son vrai nom et pourrait donner une impression négative à qui tombe dessus sans contexte.</p>
<p>Je vais quand même mener l'entretien normalement, en me concentrant sur son parcours et ses compétences réelles — mais ce point me rappelle qu'une publication ancienne, même sans lien avec la vie professionnelle, peut rester visible des années plus tard et influencer la première impression que l'on se fait de quelqu'un.</p>
<p>Cordialement,<br>Julie Petit<br>Service recrutement</p>
</div>
</div>
</div>
</div>"""

# Ticket #133 (audit de couverture, issue #131) : 3e exemple commenté, exigé par le
# contrat de rédaction (issues #96-#101, "3 exemples commentés") mais absent jusqu'ici
# (seulement 2 — voir audit). Document original, texte brut inchangé une fois écrit (même
# convention que les deux documents ci-dessus). Aucune nouvelle image : avatar générique
# déjà utilisé ailleurs dans ce cours (`.jc-social-avatar--p1`, inutilisé jusqu'ici pour
# Sophie elle-même).
FSE03_RECENT_POST_TITLE = "Une publication professionnelle récente de Sophie Lambert"
FSE03_RECENT_POST_TEXT = """[Publication récente et volontaire de Sophie Lambert elle-même sur son profil \
professionnel, créée pour cet exercice]

Fière d'avoir terminé ma formation en gestion des stocks cette semaine ! Un grand merci à \
toute l'équipe logistique pour son soutien pendant ces trois mois."""

FSE03_RECENT_POST_CARD_HTML = """<div class="jc-doc jc-social" id="document-publication-recente">
<div class="jc-doc-header"><strong>📱 Publication — réseau social</strong><span class="jc-doc-fictive-badge">Fictif</span></div>
<div class="jc-doc-body">
<div class="jc-social-post-head">
<span class="jc-social-avatar jc-social-avatar--p1" aria-hidden="true">?</span>
<div class="jc-social-meta">
<span class="jc-social-author">Sophie Lambert</span>
<span class="jc-social-time">il y a trois semaines</span>
</div>
</div>
<p class="jc-social-text">« Fière d'avoir terminé ma formation en gestion des stocks cette semaine ! Un grand merci à toute l'équipe logistique pour son soutien pendant ces trois mois. »</p>
</div>
</div>"""
