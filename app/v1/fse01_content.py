"""Documents support — FSE01 « Communiquer : le schéma de communication » (ticket #96,
cahier des charges détaillé du ticket #97 ; refonte pédagogique et visuelle tickets #103,
#105, #108).

Trois situations originales, rédigées pour ce cours (jamais une modification d'une source
officielle — `docs/content_workflow.md`, § « Contenu rédigé à partir d'un cahier des
charges »), couvrant les trois applications explicitement demandées par le ticket #97 :
un mail, une affiche et une publication sur un réseau social. Chacune permet d'identifier
émetteur/récepteur/message/code/canal/contexte, un obstacle (bruit) et la rétroaction
disponible — ou son absence — selon le canal utilisé.

Deux formes pour chaque document (ticket #103, § 4 : « Sépare le document de son
analyse ») :
- `FSE0N_*_TEXT` (texte brut, inchangé depuis le ticket #96) : utilisé pour créer le
  `SourceDocument`/`SourceDocumentVersion` de la banque de questions
  (`app.v1.fse_bank.import_fse01_to_bank`) — jamais modifié, pour ne jamais faire dévier le
  texte vu par l'IA de correction de celui vu par l'étudiant pendant la question.
- `FSE0N_*_CARD_HTML` (nouveau, enrichi au ticket #108) : le MÊME contenu, mis en forme
  comme un vrai document lisible (mail/publication en HTML/CSS réaliste — texte réel,
  sélectionnable ; affiche avec illustration générée, voir `app.v1.fse01_image`) — jamais
  une reformulation des faits, uniquement une présentation visuelle. Composants réutilisables
  documentés dans `docs/components/EmailCard.md`, `docs/components/SocialPostCard.md`,
  `docs/components/PosterCard.md` — appliqués à FSE01 uniquement pour cette étape (ticket
  #108 : l'extension à FSE02-17 attend un retour visuel explicite)."""

from pathlib import Path

# =============================================================================================
# Document 1 — Une candidature par mail interrompue par une coupure de connexion
# =============================================================================================

FSE01_MAIL_TITLE = "Candidature par mail — coupure de connexion"
FSE01_MAIL_TEXT = """[Mail envoyé le 12 mars à 9h04, par Karim Haddad, candidat]

De : karim.haddad82@maileo.be
À : recrutement@entrepots-dufresne.be
Objet : Candidature — poste de manutentionnaire

Madame, Monsieur,

Je me permets de vous contacter suite à votre annonce parue sur le site du Forem pour le \
poste de manutentionnaire au sein de vos entrepôts de Wavre. Je dispose d'une expérience \
de trois ans dans la préparation de commandes et je suis titulaire du permis cariste \
catégorie 3.

Vous trouverez en pièce jointe mon

[Le message s'arrête ici, en pleine phrase, sans pièce jointe. La connexion internet de \
Karim a été coupée à ce moment précis ; son logiciel de messagerie a automatiquement \
envoyé le message resté inactif quelques minutes plus tard, tel quel, sans que Karim ne \
s'en rende compte avant le lendemain.]

[Réponse reçue le 13 mars à 14h20, du service recrutement]

De : recrutement@entrepots-dufresne.be
À : karim.haddad82@maileo.be
Objet : RE: Candidature — poste de manutentionnaire

Bonjour,

Nous avons bien reçu votre message, mais celui-ci s'arrête au milieu d'une phrase et ne \
comporte aucune pièce jointe. Pourriez-vous nous renvoyer votre candidature complète, \
accompagnée de votre CV ?

Cordialement,
Le service recrutement — Entrepôts Dufresne"""

# Ticket #108 § 3 : vraie mise en page de messagerie (en-têtes, avatars, fil de discussion),
# texte réel et sélectionnable — jamais une image. Voir docs/components/EmailCard.md.
FSE01_MAIL_CARD_HTML = """<div class="jc-doc jc-mail">
<div class="jc-doc-header"><strong>✉️ Mail — candidature</strong><span class="jc-doc-fictive-badge">Fictif</span></div>
<div class="jc-mail-thread">
<div class="jc-mail-message">
<div class="jc-mail-message-head">
<span class="jc-mail-avatar" aria-hidden="true">KH</span>
<div class="jc-mail-meta">
<span class="jc-mail-from">Karim Haddad <span class="jc-mail-address">&lt;karim.haddad82@maileo.be&gt;</span></span>
<span class="jc-mail-to">à recrutement@entrepots-dufresne.be</span>
</div>
<span class="jc-mail-date">12 mars, 9h04</span>
</div>
<p class="jc-mail-subject">Candidature — poste de manutentionnaire</p>
<div class="jc-mail-body">
<p>Madame, Monsieur,</p>
<p>Je me permets de vous contacter suite à votre annonce parue sur le site du Forem pour \
le poste de manutentionnaire au sein de vos entrepôts de Wavre. Je dispose d'une \
expérience de trois ans dans la préparation de commandes et je suis titulaire du permis \
cariste catégorie 3.</p>
<p>Vous trouverez en pièce jointe mon</p>
<p class="jc-mail-interrupted">⚠️ Message interrompu ici, en pleine phrase, sans pièce \
jointe — une coupure de connexion a interrompu l'envoi à cet instant précis ; le logiciel \
de messagerie a transmis automatiquement le message resté inactif, sans que Karim ne s'en \
rende compte avant le lendemain.</p>
</div>
</div>
<div class="jc-mail-message jc-mail-message--reply">
<div class="jc-mail-message-head">
<span class="jc-mail-avatar jc-mail-avatar--reply" aria-hidden="true">ED</span>
<div class="jc-mail-meta">
<span class="jc-mail-from">Service recrutement <span class="jc-mail-address">&lt;recrutement@entrepots-dufresne.be&gt;</span></span>
<span class="jc-mail-to">à karim.haddad82@maileo.be</span>
</div>
<span class="jc-mail-date">13 mars, 14h20</span>
</div>
<p class="jc-mail-subject">RE: Candidature — poste de manutentionnaire</p>
<div class="jc-mail-body">
<p>Bonjour,</p>
<p>Nous avons bien reçu votre message, mais celui-ci s'arrête au milieu d'une phrase et ne \
comporte aucune pièce jointe. Pourriez-vous nous renvoyer votre candidature complète, \
accompagnée de votre CV ?</p>
<p>Cordialement,<br>Le service recrutement — Entrepôts Dufresne</p>
</div>
</div>
</div>
</div>"""

# =============================================================================================
# Document 2 — Une affiche de sécurité routière (illustration générée + texte HTML/CSS)
# =============================================================================================

FSE01_AFFICHE_TITLE = "Affiche de sécurité routière — bord d'autoroute"
FSE01_AFFICHE_TEXT = """[Affiche grand format installée en bordure d'autoroute, visible depuis les véhicules en \
circulation]

Texte principal, en grandes lettres blanches sur fond rouge :
« 90, C'EST DÉJÀ TROP VITE QUAND UN ENFANT TRAVERSE »

Sous-titre, en lettres plus petites, sous le texte principal :
« Ralentir, c'est voir à temps. »

Image : silhouette noire et stylisée d'un enfant en train de traverser, à côté d'un \
passage piéton dessiné de façon simplifiée.

Logo institutionnel, en bas à droite de l'affiche : logo du Service public de Wallonie \
(SPW), accompagné de la mention « Sécurité routière Wallonie ».

Un petit QR code est imprimé dans le coin inférieur gauche de l'affiche ; il renvoie, une \
fois scanné, vers une page d'information sur les limitations de vitesse en zone habitée."""

# Ticket #108 § 3-4 : illustration générée une seule fois via l'API OpenAI et conservée
# durablement sur disque (voir app/v1/fse01_image.py) — jamais un appel API à l'ouverture
# du cours. Le slogan et les mentions restent en HTML/CSS (jamais du texte intégré à
# l'image) pour garantir leur exactitude et leur lisibilité. Vérification d'existence du
# fichier au chargement du module (lecture disque locale, pas un appel réseau) : si
# l'image n'a jamais été générée ou a été supprimée, un rendu de secours en CSS pur est
# utilisé à la place, jamais une image cassée. Voir docs/components/PosterCard.md.
_POSTER_IMAGE_REL_URL = "/static/img/fse01_affiche_securite_routiere.png"
_POSTER_IMAGE_FILE = (
    Path(__file__).resolve().parent.parent / "static" / "img" / "fse01_affiche_securite_routiere.png"
)

_POSTER_ALT_TEXT = (
    "Illustration pédagogique et fictive : une silhouette d'enfant traverse un passage "
    "piéton pendant qu'une voiture ralentit."
)

_POSTER_FALLBACK_SVG = """<div class="jc-poster-fallback" role="img" aria-label="Illustration non disponible : silhouette schématique d'un enfant qui traverse devant une voiture qui ralentit.">
<svg viewBox="0 0 200 160" xmlns="http://www.w3.org/2000/svg">
<rect x="0" y="120" width="200" height="12" fill="#d7dce1"></rect>
<rect x="10" y="123" width="20" height="6" fill="#fff"></rect>
<rect x="50" y="123" width="20" height="6" fill="#fff"></rect>
<rect x="90" y="123" width="20" height="6" fill="#fff"></rect>
<rect x="130" y="123" width="20" height="6" fill="#fff"></rect>
<rect x="170" y="123" width="20" height="6" fill="#fff"></rect>
<circle cx="70" cy="70" r="10" fill="#b02a37"></circle>
<rect x="63" y="80" width="14" height="30" rx="4" fill="#b02a37"></rect>
<rect x="120" y="85" width="55" height="25" rx="6" fill="#b02a37"></rect>
<circle cx="132" cy="112" r="6" fill="#55606b"></circle>
<circle cx="163" cy="112" r="6" fill="#55606b"></circle>
</svg>
</div>"""


def _poster_visual_html() -> str:
    if _POSTER_IMAGE_FILE.exists():
        return (
            f'<img src="{_POSTER_IMAGE_REL_URL}" alt="{_POSTER_ALT_TEXT}" '
            f'class="jc-poster-image" loading="lazy">'
        )
    return _POSTER_FALLBACK_SVG


FSE01_AFFICHE_CARD_HTML = f"""<div class="jc-doc jc-poster">
<div class="jc-doc-header"><strong>🪧 Affiche — sécurité routière</strong><span class="jc-doc-fictive-badge">Reconstitution pédagogique fictive — pas une véritable campagne officielle</span></div>
{_poster_visual_html()}
<div class="jc-poster-textblock">
<p class="jc-poster-slogan">90, C'EST DÉJÀ TROP VITE QUAND UN ENFANT TRAVERSE</p>
<p class="jc-poster-subtitle">Ralentir, c'est voir à temps.</p>
</div>
<div class="jc-poster-footer">
<span>Logo (bas à droite, fictif) : Service public de Wallonie — Sécurité routière Wallonie</span>
<span>QR code (bas à gauche, fictif) : renvoie vers une page d'information sur les limitations de vitesse en zone habitée</span>
</div>
</div>"""

# =============================================================================================
# Document 3 — Une publication sur un réseau social professionnel (offre d'emploi)
# =============================================================================================

FSE01_SOCIAL_TITLE = "Publication sur un réseau social — offre d'emploi"
FSE01_SOCIAL_TEXT = """[Publication de la page « Techno Services Wallonie » sur un réseau social professionnel, \
publiée il y a 3 heures]

Techno Services Wallonie :
« Nous recrutons ! Techno Services cherche un·e technicien·ne de maintenance \
industrielle pour notre site de Charleroi. Contrat à durée indéterminée, expérience en \
électromécanique appréciée. Postulez via le lien en commentaire ! #emploi #Charleroi \
#technicien »

👍 24 réactions — 💬 7 commentaires — 🔁 5 partages

Commentaires affichés sous la publication :
- Fatima B. : « Le poste est-il ouvert aux débutant·e·s avec un certificat obtenu via le \
Forem ? »
- Mourad T. (a partagé la publication) : « Je connais quelqu'un que ça peut intéresser, \
je transmets ! »
- Julien P. : « Encore une offre qui ne précise pas le salaire... »
- Techno Services Wallonie (en réponse au commentaire de Fatima B.) : « Oui, une \
formation complémentaire est prévue à l'embauche. N'hésitez pas à postuler ! »"""

# Ticket #108 § 3 : vraie mise en page de publication (avatar, réactions, fil de
# commentaires), texte réel et sélectionnable. Voir docs/components/SocialPostCard.md.
FSE01_SOCIAL_CARD_HTML = """<div class="jc-doc jc-social">
<div class="jc-doc-header"><strong>📱 Publication — réseau social</strong><span class="jc-doc-fictive-badge">Fictif</span></div>
<div class="jc-doc-body">
<div class="jc-social-post-head">
<span class="jc-social-avatar" aria-hidden="true">TS</span>
<div class="jc-social-meta">
<span class="jc-social-author">Techno Services Wallonie</span>
<span class="jc-social-time">Publié il y a 3 heures</span>
</div>
</div>
<p class="jc-social-text">« Nous recrutons ! Techno Services cherche un·e technicien·ne \
de maintenance industrielle pour notre site de Charleroi. Contrat à durée indéterminée, \
expérience en électromécanique appréciée. Postulez via le lien en commentaire ! #emploi \
#Charleroi #technicien »</p>
<div class="jc-social-reactions">
<span>👍 24 réactions</span><span>💬 7 commentaires</span><span>🔁 5 partages</span>
</div>
<div class="jc-social-comments">
<div class="jc-social-comment">
<span class="jc-social-avatar jc-social-avatar--sm" aria-hidden="true">FB</span>
<div><strong>Fatima B.</strong><p>« Le poste est-il ouvert aux débutant·e·s avec un \
certificat obtenu via le Forem ? »</p></div>
</div>
<div class="jc-social-comment">
<span class="jc-social-avatar jc-social-avatar--sm" aria-hidden="true">MT</span>
<div><strong>Mourad T.</strong> <em>(a partagé la publication)</em><p>« Je connais \
quelqu'un que ça peut intéresser, je transmets ! »</p></div>
</div>
<div class="jc-social-comment">
<span class="jc-social-avatar jc-social-avatar--sm" aria-hidden="true">JP</span>
<div><strong>Julien P.</strong><p>« Encore une offre qui ne précise pas le salaire... »</p></div>
</div>
<div class="jc-social-comment jc-social-comment--company">
<span class="jc-social-avatar jc-social-avatar--sm" aria-hidden="true">TS</span>
<div><strong>Techno Services Wallonie</strong><span class="jc-social-reply-badge">Réponse \
de l'entreprise</span><p>« Oui, une formation complémentaire est prévue à l'embauche. \
N'hésitez pas à postuler ! »</p></div>
</div>
</div>
</div>
</div>"""

# =============================================================================================
# Schéma de la communication — SVG responsive (ticket #103 § 3, adapté au mobile ticket
# #108 § 5)
# =============================================================================================
# Représente séparément les 8 éléments exigés : émetteur, récepteur, message, code, canal,
# contexte, obstacle et boucle de rétroaction. Deux rendus SVG distincts (desktop large /
# mobile en colonne, permutés par média-requête CSS — voir .jc-diagram--desktop/--mobile
# dans design-system.css) : un simple redimensionnement du schéma large rendrait le texte
# illisible sur téléphone (ticket #108 : « adapte sa disposition... plutôt que réduire tout
# le dessin »). Voir docs/components/Diagram.md pour le choix technique (SVG natif).

_DIAGRAM_ARIA_LABEL = (
    "Schéma de la communication : l'émetteur envoie un message, mis en forme avec un code "
    "et transmis par un canal, à un récepteur ; un obstacle peut perturber cette "
    "transmission ; une rétroaction peut revenir du récepteur vers l'émetteur si le canal "
    "le permet ; l'ensemble se déroule dans un contexte."
)

_DIAGRAM_DESKTOP_SVG = f"""<div class="jc-diagram jc-diagram--desktop" role="img" aria-label="{_DIAGRAM_ARIA_LABEL}">
<svg viewBox="0 0 900 440" xmlns="http://www.w3.org/2000/svg">
<defs>
<marker id="fse01-arrow-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
<path d="M0,0 L10,5 L0,10 z" fill="#1565c0"></path>
</marker>
<marker id="fse01-arrow-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
<path d="M0,0 L10,5 L0,10 z" fill="#1e7e45"></path>
</marker>
</defs>

<rect x="15" y="10" width="870" height="415" rx="18" fill="none" stroke="#8a97a3" stroke-width="2" stroke-dasharray="8 6"></rect>
<text x="34" y="36" font-size="15" font-weight="700" fill="#55606b">Contexte (situation, moment, lieu)</text>

<rect x="50" y="58" width="190" height="90" rx="12" fill="#eaf4ff" stroke="#1565c0" stroke-width="2"></rect>
<text x="145" y="96" font-size="19" font-weight="700" text-anchor="middle" fill="#1f2933">Émetteur</text>
<text x="145" y="119" font-size="13" text-anchor="middle" fill="#55606b">envoie le message</text>

<rect x="660" y="58" width="190" height="90" rx="12" fill="#eaf4ff" stroke="#1565c0" stroke-width="2"></rect>
<text x="755" y="96" font-size="19" font-weight="700" text-anchor="middle" fill="#1f2933">Récepteur</text>
<text x="755" y="119" font-size="13" text-anchor="middle" fill="#55606b">reçoit le message</text>

<line x1="248" y1="103" x2="655" y2="103" stroke="#1565c0" stroke-width="3" marker-end="url(#fse01-arrow-blue)"></line>
<text x="452" y="88" font-size="18" font-weight="700" text-anchor="middle" fill="#1565c0">Message</text>
<text x="452" y="128" font-size="13" text-anchor="middle" fill="#55606b">Canal : support de transmission (mail, affiche, réseau social...)</text>
<text x="452" y="146" font-size="13" text-anchor="middle" fill="#55606b">Code : système de signes utilisé (langue, images, couleurs...)</text>

<g>
<circle cx="452" cy="196" r="24" fill="#fdecea" stroke="#b02a37" stroke-width="2"></circle>
<path d="M443,196 L450,183 L454,193 L461,181 L457,201 L446,206 Z" fill="#b02a37"></path>
</g>
<text x="452" y="234" font-size="14" font-weight="700" text-anchor="middle" fill="#b02a37">Obstacle (bruit)</text>
<text x="452" y="251" font-size="12" text-anchor="middle" fill="#55606b">peut perturber la transmission du message</text>

<path d="M655,275 C 530,345 374,345 248,275" fill="none" stroke="#1e7e45" stroke-width="3" marker-end="url(#fse01-arrow-green)"></path>
<text x="452" y="372" font-size="16" font-weight="700" text-anchor="middle" fill="#1e7e45">Rétroaction</text>
<text x="452" y="391" font-size="12" text-anchor="middle" fill="#55606b">réponse du récepteur vers l'émetteur — possible seulement si le canal le permet</text>
</svg>
</div>"""

_DIAGRAM_MOBILE_SVG = f"""<div class="jc-diagram jc-diagram--mobile" role="img" aria-label="{_DIAGRAM_ARIA_LABEL}">
<svg viewBox="0 0 380 660" xmlns="http://www.w3.org/2000/svg">
<defs>
<marker id="fse01-m-arrow-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
<path d="M0,0 L10,5 L0,10 z" fill="#1565c0"></path>
</marker>
<marker id="fse01-m-arrow-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
<path d="M0,0 L10,5 L0,10 z" fill="#1e7e45"></path>
</marker>
</defs>

<text x="190" y="22" font-size="14" font-style="italic" text-anchor="middle" fill="#55606b">Contexte : situation, moment, lieu</text>

<rect x="30" y="40" width="320" height="82" rx="12" fill="#eaf4ff" stroke="#1565c0" stroke-width="2"></rect>
<text x="190" y="76" font-size="21" font-weight="700" text-anchor="middle" fill="#1f2933">Émetteur</text>
<text x="190" y="100" font-size="14" text-anchor="middle" fill="#55606b">envoie le message</text>

<line x1="190" y1="122" x2="190" y2="172" stroke="#1565c0" stroke-width="3" marker-end="url(#fse01-m-arrow-blue)"></line>
<text x="215" y="152" font-size="18" font-weight="700" text-anchor="start" fill="#1565c0">Message</text>

<text x="190" y="196" font-size="14" text-anchor="middle" fill="#55606b">Code : langue, images, couleurs...</text>
<text x="190" y="216" font-size="14" text-anchor="middle" fill="#55606b">Canal : mail, affiche, réseau social...</text>

<line x1="190" y1="226" x2="190" y2="266" stroke="#1565c0" stroke-width="3" marker-end="url(#fse01-m-arrow-blue)"></line>

<g>
<circle cx="190" cy="300" r="26" fill="#fdecea" stroke="#b02a37" stroke-width="2"></circle>
<path d="M180,300 L188,286 L192,297 L200,284 L196,306 L184,312 Z" fill="#b02a37"></path>
</g>
<text x="190" y="342" font-size="16" font-weight="700" text-anchor="middle" fill="#b02a37">Obstacle (bruit)</text>
<text x="190" y="362" font-size="13" text-anchor="middle" fill="#55606b">peut perturber la transmission</text>

<line x1="190" y1="372" x2="190" y2="412" stroke="#1565c0" stroke-width="3" marker-end="url(#fse01-m-arrow-blue)"></line>

<rect x="30" y="412" width="320" height="82" rx="12" fill="#eaf4ff" stroke="#1565c0" stroke-width="2"></rect>
<text x="190" y="448" font-size="21" font-weight="700" text-anchor="middle" fill="#1f2933">Récepteur</text>
<text x="190" y="472" font-size="14" text-anchor="middle" fill="#55606b">reçoit le message</text>

<path d="M30,460 C -40,460 -40,80 30,80" fill="none" stroke="#1e7e45" stroke-width="3" marker-end="url(#fse01-m-arrow-green)" transform="translate(45,0)"></path>
<text x="190" y="540" font-size="18" font-weight="700" text-anchor="middle" fill="#1e7e45">Rétroaction</text>
<text x="190" y="566" font-size="13" text-anchor="middle" fill="#55606b">réponse du récepteur vers l'émetteur,</text>
<text x="190" y="585" font-size="13" text-anchor="middle" fill="#55606b">possible seulement si le canal le permet</text>
<text x="190" y="612" font-size="13" font-style="italic" text-anchor="middle" fill="#55606b">(sa rapidité ne change rien à cette</text>
<text x="190" y="631" font-size="13" font-style="italic" text-anchor="middle" fill="#55606b">possibilité)</text>
</svg>
</div>"""

FSE01_COMMUNICATION_DIAGRAM_SVG = _DIAGRAM_DESKTOP_SVG + "\n" + _DIAGRAM_MOBILE_SVG
