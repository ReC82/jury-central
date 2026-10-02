"""Documents support — FSE01 « Communiquer : le schéma de communication » (ticket #96,
cahier des charges détaillé du ticket #97 ; refonte pédagogique et visuelle ticket #103).

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
- `FSE0N_*_CARD_HTML` (nouveau) : le MÊME contenu, mis en forme comme une carte de
  document lisible (`.jc-doc`, voir `docs/components/DocCard.md`) pour l'affichage sur la
  page Cours — jamais une reformulation des faits, uniquement une présentation visuelle."""

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

FSE01_MAIL_CARD_HTML = """<div class="jc-doc">
<div class="jc-doc-header"><strong>✉️ Mail — candidature</strong><span class="jc-doc-fictive-badge">Fictif</span></div>
<div class="jc-doc-body">
<dl class="jc-doc-meta">
<dt>De :</dt><dd>karim.haddad82@maileo.be</dd>
<dt>À :</dt><dd>recrutement@entrepots-dufresne.be</dd>
<dt>Objet :</dt><dd>Candidature — poste de manutentionnaire</dd>
<dt>Envoyé :</dt><dd>12 mars, 9h04</dd>
</dl>
<div class="jc-doc-text">
<p>Madame, Monsieur,</p>
<p>Je me permets de vous contacter suite à votre annonce parue sur le site du Forem pour \
le poste de manutentionnaire au sein de vos entrepôts de Wavre. Je dispose d'une \
expérience de trois ans dans la préparation de commandes et je suis titulaire du permis \
cariste catégorie 3.</p>
<p>Vous trouverez en pièce jointe mon</p>
<p><em>[Le message s'arrête ici, en pleine phrase, sans pièce jointe : une coupure de \
connexion a interrompu l'envoi à cet instant précis ; le logiciel de messagerie a \
transmis automatiquement le message resté inactif, sans que Karim ne s'en rende compte \
avant le lendemain.]</em></p>
</div>
<div class="jc-doc-comments">
<p class="jc-doc-comment"><strong>Réponse reçue le 13 mars, 14h20 :</strong> « Nous avons \
bien reçu votre message, mais celui-ci s'arrête au milieu d'une phrase et ne comporte \
aucune pièce jointe. Pourriez-vous nous renvoyer votre candidature complète, accompagnée \
de votre CV ? »</p>
</div>
</div>
</div>"""

# =============================================================================================
# Document 2 — Une affiche de sécurité routière (description textuelle fidèle, support
# visuel réel non reproductible dans ce format)
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

FSE01_AFFICHE_CARD_HTML = """<div class="jc-doc">
<div class="jc-doc-header"><strong>🪧 Affiche — sécurité routière</strong><span class="jc-doc-fictive-badge">Reconstitution pédagogique, fictive</span></div>
<div class="jc-doc-body">
<div class="jc-doc-text" style="text-align:center; background:#b02a37; color:#fff; padding:1.1rem 1rem; border-radius:6px;">
<p style="font-size:1.25rem; font-weight:800; letter-spacing:0.02em; margin-bottom:0.4rem;">\
90, C'EST DÉJÀ TROP VITE QUAND UN ENFANT TRAVERSE</p>
<p style="font-size:0.95rem; margin-bottom:0;">Ralentir, c'est voir à temps.</p>
</div>
<p class="jc-doc-text" style="margin-top:0.75rem;"><strong>Image :</strong> silhouette \
stylisée d'un enfant traversant près d'un passage piéton. <strong>En bas à droite :</strong> \
logo du Service public de Wallonie (SPW) — « Sécurité routière Wallonie ». \
<strong>En bas à gauche :</strong> un QR code renvoyant vers une page d'information sur \
les limitations de vitesse en zone habitée.</p>
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

FSE01_SOCIAL_CARD_HTML = """<div class="jc-doc">
<div class="jc-doc-header"><strong>📱 Publication — réseau social</strong><span class="jc-doc-fictive-badge">Fictif</span></div>
<div class="jc-doc-body">
<dl class="jc-doc-meta">
<dt>Page :</dt><dd>Techno Services Wallonie</dd>
<dt>Publié :</dt><dd>il y a 3 heures</dd>
</dl>
<div class="jc-doc-text">
<p>« Nous recrutons ! Techno Services cherche un·e technicien·ne de maintenance \
industrielle pour notre site de Charleroi. Contrat à durée indéterminée, expérience en \
électromécanique appréciée. Postulez via le lien en commentaire ! #emploi #Charleroi \
#technicien »</p>
<p>👍 24 réactions — 💬 7 commentaires — 🔁 5 partages</p>
</div>
<div class="jc-doc-comments">
<p class="jc-doc-comment"><strong>Fatima B. :</strong> « Le poste est-il ouvert aux \
débutant·e·s avec un certificat obtenu via le Forem ? »</p>
<p class="jc-doc-comment"><strong>Mourad T.</strong> (a partagé la publication) : « Je \
connais quelqu'un que ça peut intéresser, je transmets ! »</p>
<p class="jc-doc-comment"><strong>Julien P. :</strong> « Encore une offre qui ne précise \
pas le salaire... »</p>
<p class="jc-doc-comment"><strong>Techno Services Wallonie</strong> (en réponse à \
Fatima B.) : « Oui, une formation complémentaire est prévue à l'embauche. N'hésitez pas à \
postuler ! »</p>
</div>
</div>
</div>"""

# =============================================================================================
# Schéma de la communication — SVG (remplace le schéma en caractères, ticket #103 § 3)
# =============================================================================================
# Représente séparément les 8 éléments exigés par le ticket #103 : émetteur, récepteur,
# message, code, canal, contexte, obstacle et boucle de rétroaction. Voir
# `docs/components/Diagram.md` pour le choix technique (SVG natif, aucune dépendance).

FSE01_COMMUNICATION_DIAGRAM_SVG = """<div class="jc-diagram" role="img" aria-label="Schéma de la communication : l'émetteur \
envoie un message, mis en forme avec un code et transmis par un canal, à un récepteur ; \
un obstacle peut perturber cette transmission ; une rétroaction peut revenir du récepteur \
vers l'émetteur si le canal le permet ; l'ensemble se déroule dans un contexte.">
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
