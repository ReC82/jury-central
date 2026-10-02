"""Documents support — FSE07 « Analyser un dossier médiatique » (ticket #98, cahier des
charges détaillé).

Trois documents fictifs, rédigés pour ce cours, formant un dossier complet autour d'une même
situation (ticket #98 § FSE07, "Application attendue" : « dossier original complet de 3
documents sur une vidéo diffusée dans un groupe »), volontairement de fiabilité différente
pour entraîner la vérification d'auteur/date/contexte/preuves : une note signée et datée de la
direction d'une école (haute fiabilité), un échange de messages dans un groupe-classe (mélange
de faits, interprétations et opinions), et une publication anonyme sur un forum, non datée et
sans preuve (faible fiabilité, à questionner). Cette situation réutilise volontairement des
notions déjà enseignées (FSE01 schéma de communication, FSE04 normes/valeurs, FSE05 droit à
l'image, FSE06 comportements en ligne) sans les réévaluer directement : FSE07 porte sur la
méthode d'analyse d'un dossier, pas sur une nouvelle matière de fond."""

FSE07_SCHOOL_TITLE = "Note de la direction — école fictive « Athénée du Parc »"
FSE07_SCHOOL_TEXT = """[Document fictif, rédigé pour cet exercice]

Note interne — Athénée du Parc
Signée par : M. Devos, directeur adjoint
Date : 14 mars 2026

Le 12 mars 2026, durant la récréation de midi, un élève a filmé un camarade qui trébuchait dans \
la cour, sans le consentement de la personne filmée. La vidéo a été partagée le jour même dans le \
groupe de discussion de la classe de 5e B, comptant 24 élèves. La direction a été informée le 13 \
mars par un enseignant. L'élève ayant filmé et partagé la vidéo a été reçu avec ses parents le 14 \
mars. La vidéo a été supprimée du groupe à la demande de la direction. Aucune autre mesure n'est \
communiquée dans cette note."""

FSE07_CHAT_TITLE = "Messages échangés dans le groupe de la classe de 5e B"
FSE07_CHAT_TEXT = """[Échange fictif, rédigé pour cet exercice — prénoms fictifs]

Yasmine, 12 mars, 12h41 : « Vous avez vu la vidéo de Lucas qui tombe dans la cour ? Trop drôle »
Karim, 12 mars, 12h43 : « Pas cool de filmer ça sans lui demander, non ? »
Yasmine, 12 mars, 12h45 : « Oh ça va, c'est juste une vidéo, il va pas en mourir »
Elena, 12 mars, 12h50 : « Moi je trouve que ça craint, il a eu l'air vraiment gêné après »
Thibault, 12 mars, 13h02 : « De toute façon tout le monde filme tout le temps, c'est normal \
maintenant »
Karim, 12 mars, 13h10 : « Justement, je pense que c'est là le problème »
Elena, 13 mars, 08h15 : « La direction est au courant, Lucas a dû être super mal à l'aise \
pendant deux jours »"""

FSE07_FORUM_TITLE = "Publication anonyme sur un forum local (non datée, auteur non identifié)"
FSE07_FORUM_TEXT = """[Document fictif, rédigé pour cet exercice]

Sujet : « Encore une école qui ne fait rien contre le harcèlement »

Posté par : Utilisateur anonyme « parent_inquiet93 »

« On m'a raconté qu'un élève de l'Athénée du Parc a été filmé et humilié devant toute l'école, et \
que la direction n'a strictement rien fait. C'est à chaque fois pareil dans ces écoles, elles \
préfèrent cacher les problèmes plutôt que de sanctionner vraiment les responsables. Il paraît même \
que ce genre de vidéo circule encore ailleurs. Il serait temps que les autorités s'occupent \
sérieusement de ce problème qui ne fait qu'empirer d'année en année. »"""

# Ticket #115 : présentation réaliste — textes bruts ci-dessus inchangés (banque de
# questions, `app.v1.fse_bank.import_fse07_to_bank`). Chaque élève garde la même couleur
# partout dans le fil de discussion (`.jc-social-avatar--pN`, générique et réutilisable).
FSE07_SCHOOL_CARD_HTML = """<div class="jc-doc" id="document-note">
<div class="jc-doc-header"><strong>📋 Note interne — Athénée du Parc</strong><span class="jc-doc-fictive-badge">Fictif</span></div>
<div class="jc-doc-body">
<dl class="jc-doc-meta">
<dt>Signée par :</dt><dd>M. Devos, directeur adjoint</dd>
<dt>Date :</dt><dd>14 mars 2026</dd>
</dl>
<div class="jc-doc-text">
<p>Le 12 mars 2026, durant la récréation de midi, un élève a filmé un camarade qui trébuchait dans la cour, sans le consentement de la personne filmée. La vidéo a été partagée le jour même dans le groupe de discussion de la classe de 5e B, comptant 24 élèves.</p>
<p>La direction a été informée le 13 mars par un enseignant. L'élève ayant filmé et partagé la vidéo a été reçu avec ses parents le 14 mars. La vidéo a été supprimée du groupe à la demande de la direction. Aucune autre mesure n'est communiquée dans cette note.</p>
</div>
</div>
</div>"""

FSE07_CHAT_CARD_HTML = """<div class="jc-doc" id="document-chat">
<div class="jc-doc-header"><strong>💬 Messages — groupe de la classe de 5e B</strong><span class="jc-doc-fictive-badge">Fictif</span></div>
<div class="jc-doc-body">
<div class="jc-chat-thread">
<div class="jc-chat-message">
<span class="jc-social-avatar jc-social-avatar--sm jc-social-avatar--p1" aria-hidden="true">Y</span>
<div><div class="jc-chat-meta"><span class="jc-chat-author">Yasmine</span><span class="jc-chat-time">12 mars, 12h41</span></div><p class="jc-chat-text">« Vous avez vu la vidéo de Lucas qui tombe dans la cour ? Trop drôle »</p></div>
</div>
<div class="jc-chat-message">
<span class="jc-social-avatar jc-social-avatar--sm jc-social-avatar--p2" aria-hidden="true">K</span>
<div><div class="jc-chat-meta"><span class="jc-chat-author">Karim</span><span class="jc-chat-time">12 mars, 12h43</span></div><p class="jc-chat-text">« Pas cool de filmer ça sans lui demander, non ? »</p></div>
</div>
<div class="jc-chat-message">
<span class="jc-social-avatar jc-social-avatar--sm jc-social-avatar--p1" aria-hidden="true">Y</span>
<div><div class="jc-chat-meta"><span class="jc-chat-author">Yasmine</span><span class="jc-chat-time">12 mars, 12h45</span></div><p class="jc-chat-text">« Oh ça va, c'est juste une vidéo, il va pas en mourir »</p></div>
</div>
<div class="jc-chat-message">
<span class="jc-social-avatar jc-social-avatar--sm jc-social-avatar--p3" aria-hidden="true">E</span>
<div><div class="jc-chat-meta"><span class="jc-chat-author">Elena</span><span class="jc-chat-time">12 mars, 12h50</span></div><p class="jc-chat-text">« Moi je trouve que ça craint, il a eu l'air vraiment gêné après »</p></div>
</div>
<div class="jc-chat-message">
<span class="jc-social-avatar jc-social-avatar--sm jc-social-avatar--p4" aria-hidden="true">T</span>
<div><div class="jc-chat-meta"><span class="jc-chat-author">Thibault</span><span class="jc-chat-time">12 mars, 13h02</span></div><p class="jc-chat-text">« De toute façon tout le monde filme tout le temps, c'est normal maintenant »</p></div>
</div>
<div class="jc-chat-message">
<span class="jc-social-avatar jc-social-avatar--sm jc-social-avatar--p2" aria-hidden="true">K</span>
<div><div class="jc-chat-meta"><span class="jc-chat-author">Karim</span><span class="jc-chat-time">12 mars, 13h10</span></div><p class="jc-chat-text">« Justement, je pense que c'est là le problème »</p></div>
</div>
<div class="jc-chat-message">
<span class="jc-social-avatar jc-social-avatar--sm jc-social-avatar--p3" aria-hidden="true">E</span>
<div><div class="jc-chat-meta"><span class="jc-chat-author">Elena</span><span class="jc-chat-time">13 mars, 08h15</span></div><p class="jc-chat-text">« La direction est au courant, Lucas a dû être super mal à l'aise pendant deux jours »</p></div>
</div>
</div>
</div>
</div>"""

FSE07_FORUM_CARD_HTML = """<div class="jc-doc" id="document-forum">
<div class="jc-doc-header"><strong>🌐 Publication — forum local</strong><span class="jc-doc-fictive-badge">Fictif</span></div>
<div class="jc-doc-body">
<dl class="jc-doc-meta">
<dt>Sujet :</dt><dd>« Encore une école qui ne fait rien contre le harcèlement »</dd>
<dt>Posté par :</dt><dd>Utilisateur anonyme « parent_inquiet93 »</dd>
</dl>
<div class="jc-doc-text">
<p>« On m'a raconté qu'un élève de l'Athénée du Parc a été filmé et humilié devant toute l'école, et que la direction n'a strictement rien fait. C'est à chaque fois pareil dans ces écoles, elles préfèrent cacher les problèmes plutôt que de sanctionner vraiment les responsables. Il paraît même que ce genre de vidéo circule encore ailleurs. Il serait temps que les autorités s'occupent sérieusement de ce problème qui ne fait qu'empirer d'année en année. »</p>
</div>
</div>
</div>"""
