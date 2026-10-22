"""Documents support — FSE04 « Normes, valeurs et influence sociale » (ticket #97, cahier
des charges détaillé).

Deux documents originaux, rédigés pour ce cours (jamais une modification d'une source
officielle — `docs/content_workflow.md`), illustrant l'application explicitement demandée
par le ticket #97 : analyser un groupe public qui encourage la diffusion d'une vidéo
humiliante, sans réduire tout comportement à la seule influence du groupe. Traitement
volontairement sobre et non graphique (aucune scène décrite en détail, aucun nom réel) :
l'objectif pédagogique porte sur l'analyse des normes/valeurs/comportements, jamais sur le
contenu de la vidéo elle-même. Les personnes et le groupe cités sont fictifs."""

FSE04_GROUP_TITLE = "Publication dans un groupe en ligne « Fous rires du quotidien »"
FSE04_GROUP_TEXT = """[Publication et commentaires dans un groupe public en ligne fictif, créés pour cet \
exercice — le contenu de la vidéo elle-même n'est pas décrit : seuls le contexte de sa \
diffusion et les réactions qu'elle suscite sont présentés]

Groupe public « Fous rires du quotidien » (2 400 membres)

Publication d'un membre : « Regardez ce qui est arrivé à ce pauvre gars dans la rue \
aujourd'hui, j'étais mort de rire ! » [vidéo jointe, non reproduite ici : une personne \
trébuche dans un lieu public et est filmée à son insu par un passant, visiblement \
désorientée et gênée après sa chute]

En quelques heures, la vidéo est partagée 340 fois dans le groupe.

Commentaires affichés sous la publication :
- Membre A : « Hahaha, il a trop la honte ! »
- Membre B : « Quelqu'un sait qui c'est ? Faut vraiment pas avoir de chance »
- Membre C : « Je l'ai aussi envoyée à mes potes, trop drôle »
- Membre D : « Franchement, c'est méchant de se moquer comme ça, elle n'a rien demandé »
- Membre E : « Allez, c'est juste pour rire, personne n'est blessé »"""

FSE04_TESTIMONY_TITLE = "Témoignage de Karim, membre du groupe, qui n'a pas partagé la vidéo"
FSE04_TESTIMONY_TEXT = """[Témoignage fictif recueilli pour cet exercice]

« J'ai vu la vidéo passer dans le groupe, comme beaucoup d'autres membres. Honnêtement, \
la première réaction, c'est presque un réflexe de sourire parce que tout le monde autour \
de moi trouvait ça drôle, et le groupe entier semblait d'accord. Mais je me suis dit que \
cette personne n'avait rien demandé, et que ça pourrait être n'importe qui, moi y \
compris. Je n'ai ni partagé la vidéo, ni laissé de commentaire moqueur. Je sais que \
d'autres membres du groupe n'ont pas non plus participé, même s'ils ne l'ont pas dit \
publiquement. Ce n'est pas parce qu'un groupe entier semble pousser dans une direction \
que chaque personne qui en fait partie agit forcément de la même façon. »"""

# Ticket #115 : présentation réaliste — texte brut ci-dessus inchangé (utilisé par la
# banque de questions, `app.v1.fse_bank.import_fse04_to_bank`). Chaque membre garde la
# même couleur partout (voir `.jc-social-avatar--pN`, générique et réutilisable).
FSE04_GROUP_CARD_HTML = """<div class="jc-doc jc-social" id="document-groupe">
<div class="jc-doc-header"><strong>👥 Groupe public — « Fous rires du quotidien »</strong><span class="jc-doc-fictive-badge">Fictif</span></div>
<div class="jc-doc-body">
<div class="jc-social-post-head">
<span class="jc-social-avatar jc-social-avatar--p1" aria-hidden="true">?</span>
<div class="jc-social-meta">
<span class="jc-social-author">Fous rires du quotidien</span>
<span class="jc-social-time">Groupe public — 2 400 membres</span>
</div>
</div>
<p class="jc-social-text">« Regardez ce qui est arrivé à ce pauvre gars dans la rue aujourd'hui, j'étais mort de rire ! » <em>[vidéo jointe, non reproduite ici : une personne trébuche dans un lieu public et est filmée à son insu par un passant, visiblement désorientée et gênée après sa chute]</em></p>
<div class="jc-social-reactions">
<span>🔁 340 partages en quelques heures</span>
</div>
<div class="jc-social-comments">
<div class="jc-social-comment">
<span class="jc-social-avatar jc-social-avatar--sm jc-social-avatar--p2" aria-hidden="true">A</span>
<div><strong>Membre A</strong><p>« Hahaha, il a trop la honte ! »</p></div>
</div>
<div class="jc-social-comment">
<span class="jc-social-avatar jc-social-avatar--sm jc-social-avatar--p3" aria-hidden="true">B</span>
<div><strong>Membre B</strong><p>« Quelqu'un sait qui c'est ? Faut vraiment pas avoir de chance »</p></div>
</div>
<div class="jc-social-comment">
<span class="jc-social-avatar jc-social-avatar--sm jc-social-avatar--p4" aria-hidden="true">C</span>
<div><strong>Membre C</strong><p>« Je l'ai aussi envoyée à mes potes, trop drôle »</p></div>
</div>
<div class="jc-social-comment">
<span class="jc-social-avatar jc-social-avatar--sm jc-social-avatar--p5" aria-hidden="true">D</span>
<div><strong>Membre D</strong><p>« Franchement, c'est méchant de se moquer comme ça, elle n'a rien demandé »</p></div>
</div>
<div class="jc-social-comment">
<span class="jc-social-avatar jc-social-avatar--sm jc-social-avatar--p1" aria-hidden="true">E</span>
<div><strong>Membre E</strong><p>« Allez, c'est juste pour rire, personne n'est blessé »</p></div>
</div>
</div>
</div>
</div>"""

FSE04_TESTIMONY_CARD_HTML = """<div class="jc-doc" id="document-temoignage">
<div class="jc-doc-header"><strong>🗣️ Témoignage — Karim, membre du groupe</strong><span class="jc-doc-fictive-badge">Fictif</span></div>
<div class="jc-doc-body">
<div class="jc-quote-card">
<span class="jc-social-avatar jc-social-avatar--p2" aria-hidden="true">K</span>
<div>
<span class="jc-quote-author">Karim</span>
<p class="jc-quote-text">« J'ai vu la vidéo passer dans le groupe, comme beaucoup d'autres membres. Honnêtement, la première réaction, c'est presque un réflexe de sourire parce que tout le monde autour de moi trouvait ça drôle, et le groupe entier semblait d'accord. Mais je me suis dit que cette personne n'avait rien demandé, et que ça pourrait être n'importe qui, moi y compris. Je n'ai ni partagé la vidéo, ni laissé de commentaire moqueur. Je sais que d'autres membres du groupe n'ont pas non plus participé, même s'ils ne l'ont pas dit publiquement. Ce n'est pas parce qu'un groupe entier semble pousser dans une direction que chaque personne qui en fait partie agit forcément de la même façon. »</p>
</div>
</div>
</div>
</div>"""

# Ticket #133 (audit de couverture, issue #131) : 3e exemple commenté, exigé par le
# contrat de rédaction (issues #96-#101, "3 exemples commentés") mais absent jusqu'ici
# (seulement 2 — voir audit). Illustre concrètement la "frustration" (théorique jusqu'ici,
# jamais montrée dans un document travaillé) : message privé, jamais rendu public — à
# distinguer du désaccord PUBLIC du membre D (exemple 1), pour montrer que la frustration
# ne débouche pas toujours sur un comportement visible. Document original, aucune nouvelle
# image (avatar générique déjà utilisé ailleurs dans ce cours).
FSE04_FRUSTRATION_TITLE = "Message privé d'une autre membre du groupe, jamais rendu public"
FSE04_FRUSTRATION_TEXT = """[Message privé fictif envoyé par une autre membre du groupe à une amie, créé pour cet \
exercice — jamais publié dans le groupe lui-même]

Je ne sais pas trop quoi penser... tout le monde trouve ça drôle dans le groupe, et je \
n'ai pas envie de passer pour celle qui ne suit pas le mouvement, mais perso ça me met \
mal à l'aise de voir cette vidéo partagée comme ça. Je crois que je vais juste rien dire."""

FSE04_FRUSTRATION_CARD_HTML = """<div class="jc-doc" id="document-frustration">
<div class="jc-doc-header"><strong>🗣️ Message privé — une autre membre du groupe</strong><span class="jc-doc-fictive-badge">Fictif</span></div>
<div class="jc-doc-body">
<div class="jc-quote-card">
<span class="jc-social-avatar jc-social-avatar--p3" aria-hidden="true">?</span>
<div>
<span class="jc-quote-author">Membre E, à une amie (jamais publié dans le groupe)</span>
<p class="jc-quote-text">« Je ne sais pas trop quoi penser... tout le monde trouve ça drôle dans le groupe, et je n'ai pas envie de passer pour celle qui ne suit pas le mouvement, mais perso ça me met mal à l'aise de voir cette vidéo partagée comme ça. Je crois que je vais juste rien dire. »</p>
</div>
</div>
</div>
</div>"""
