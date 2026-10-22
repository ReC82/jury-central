"""Contenu de cours — FSE01 « Communiquer : le schéma de communication » (ticket #96,
cahier des charges détaillé du ticket #97 ; refonte pédagogique et visuelle ticket #103).

Refonte ticket #103 : le cours n'est plus un seul bloc Markdown « Cours complet » (une
seule carte indifférenciée, cause du rendu « mur de texte » signalé) mais plusieurs blocs
distincts (`fse01_course_sections()`, consommé par `app.seed._fse_course_blocks`) — chaque
titre pilote automatiquement le type de carte affiché (`app.card_kind`) :
1. Présentation et objectifs (théorie, par défaut) — 2. Théorie : le schéma de
communication (théorie, avec grille de définitions + schéma SVG + pièges en citations) —
3. Méthode (carte Méthode) — 4. Exemples commentés (carte Exemple, documents séparés de
leur analyse) — 5. Comparer pour ne pas confondre (théorie, grilles de comparaison) —
6. Exercices guidés (carte Exercice, corrigés masqués par défaut) — 7. Fiche mémo (carte
À retenir).

Bug corrigé par cette refonte (diagnostic ticket #103 § 1) : `app.content.render_markdown`
(bibliothèque `markdown`, extensions `fenced_code`/`tables`, sans `sane_lists`) exige une
ligne vide avant toute liste, sinon elle est fondue dans le paragraphe précédent sous forme
de texte brut avec des tirets littéraux — chaque liste de ce fichier est donc précédée d'une
ligne vide, systématiquement.

Second bug corrigé (ticket #112) : ce même `render_markdown` ne retraite JAMAIS le Markdown
situé à l'intérieur d'un bloc HTML brut (`<details>`, `<div>`...) — une liste à tirets à
l'intérieur d'un `<details>` restait donc fondue en texte brut quelle que soit la présence
d'une ligne vide. `_section_exercises()` écrit désormais ses corrigés entièrement en HTML
réel (tableaux, sections, listes), jamais en syntaxe Markdown imbriquée dans du HTML brut —
voir `docs/components/ExerciseStepCard.md`.

Périmètre strict (ticket #96/#97, programme p. 43-45) : émetteur, récepteur, message,
code, canal/contact, contexte/référent, obstacle/bruit, rétroaction — appliqués à un mail,
une affiche et une publication sur réseau social. Aucune autre notion (fonctions du
langage de Jakobson, etc.) n'est introduite : elle n'est pas au programme de ce
mini-cours."""

from app.v1.fse01_content import (
    FSE01_AFFICHE_CARD_HTML,
    FSE01_AFFICHE_TITLE,
    FSE01_COMMUNICATION_DIAGRAM_SVG,
    FSE01_MAIL_CARD_HTML,
    FSE01_MAIL_TITLE,
    FSE01_SOCIAL_CARD_HTML,
    FSE01_SOCIAL_TITLE,
)


def _section_intro() -> str:
    return """Tu dois être capable d'identifier, dans une situation de communication réelle (un mail, \
une affiche, une publication sur un réseau social...), qui parle, à qui, ce qui est \
transmis, avec quel système de signes, par quel support, et dans quel contexte. Tu dois \
aussi pouvoir repérer ce qui empêche un message de bien passer, et dire si une réponse du \
récepteur est possible ou non selon le support utilisé — sans jamais confondre cette \
possibilité avec la rapidité de cette réponse.

Ce cours est le premier de la Formation sociale et économique : il ne suppose aucun \
prérequis particulier.

<div class="jc-definitions">
<div class="jc-definition">
<span class="jc-definition-term">Ce que tu vas apprendre</span>
<p class="jc-definition-body">Les 8 éléments présents dans toute communication, et une \
méthode pour les repérer dans n'importe quel document.</p>
</div>
<div class="jc-definition">
<span class="jc-definition-term">Ce qu'on va te demander à l'examen</span>
<p class="jc-definition-body">Identifier ces 8 éléments dans un document fourni, et \
justifier si une réponse du récepteur est possible.</p>
</div>
</div>"""


def _section_theory() -> str:
    return f"""Communiquer, c'est transmettre quelque chose à quelqu'un. Même dans les situations les \
plus simples (un SMS, une affiche, un post sur un réseau social), cette transmission \
repose toujours sur les mêmes éléments. Les repérer systématiquement permet de comprendre \
pourquoi une communication réussit — ou pourquoi elle échoue. Voici le schéma complet :

{FSE01_COMMUNICATION_DIAGRAM_SVG}

Une communication met toujours en relation un **émetteur** (celui ou celle qui envoie le \
message) et un **récepteur** (celui ou celle qui le reçoit). Entre les deux circule un \
**message** : ce qui est réellement transmis (une information, une demande, une \
publicité...). Pour que ce message soit compris, il doit être mis en forme à l'aide d'un \
**code**, puis transmis par un **canal** — deux notions que l'on confond souvent (voir \
§ « Comparer pour ne pas confondre » plus bas). Un même message peut enfin être compris \
différemment selon le **contexte** : la situation, le moment, le lieu ou le sujet dont il \
est question.

<div class="jc-definitions">
<div class="jc-definition">
<div class="jc-definition-head"><span class="jc-definition-icon" aria-hidden="true">🗣️</span><span class="jc-definition-term">Émetteur</span></div>
<p class="jc-definition-body">La personne (ou l'organisation) qui envoie le message.</p>
</div>
<div class="jc-definition">
<div class="jc-definition-head"><span class="jc-definition-icon" aria-hidden="true">👂</span><span class="jc-definition-term">Récepteur</span></div>
<p class="jc-definition-body">La personne (ou le groupe) à qui le message est destiné.</p>
</div>
<div class="jc-definition">
<div class="jc-definition-head"><span class="jc-definition-icon" aria-hidden="true">💬</span><span class="jc-definition-term">Message</span></div>
<p class="jc-definition-body">Ce qui est réellement transmis — l'information, la demande, \
l'annonce.</p>
</div>
<div class="jc-definition">
<div class="jc-definition-head"><span class="jc-definition-icon" aria-hidden="true">🔤</span><span class="jc-definition-term">Code</span></div>
<p class="jc-definition-body">Le système de signes utilisé pour mettre le message en \
forme.</p>
<p class="jc-definition-example"><strong>Exemple :</strong> une langue, des images, des \
couleurs, des pictogrammes, des émojis.</p>
</div>
<div class="jc-definition">
<div class="jc-definition-head"><span class="jc-definition-icon" aria-hidden="true">📡</span><span class="jc-definition-term">Canal (ou contact)</span></div>
<p class="jc-definition-body">Le support matériel ou technique par lequel le message \
circule.</p>
<p class="jc-definition-example"><strong>Exemple :</strong> une connexion internet, une \
feuille affichée, une plateforme en ligne.</p>
</div>
<div class="jc-definition">
<div class="jc-definition-head"><span class="jc-definition-icon" aria-hidden="true">🧭</span><span class="jc-definition-term">Contexte (ou référent)</span></div>
<p class="jc-definition-body">La situation, le sujet ou les circonstances qui donnent son \
sens exact au message.</p>
</div>
<div class="jc-definition">
<div class="jc-definition-head"><span class="jc-definition-icon" aria-hidden="true">⚠️</span><span class="jc-definition-term">Obstacle (ou bruit)</span></div>
<p class="jc-definition-body">Tout ce qui perturbe ou empêche la bonne transmission du \
message.</p>
<p class="jc-definition-example"><strong>Exemple :</strong> une panne technique, un bruit \
ambiant, une formulation ambiguë, une information manquante.</p>
</div>
<div class="jc-definition">
<div class="jc-definition-head"><span class="jc-definition-icon" aria-hidden="true">🔁</span><span class="jc-definition-term">Rétroaction</span></div>
<p class="jc-definition-body">La réponse que le récepteur peut renvoyer à l'émetteur. Sa \
possibilité dépend UNIQUEMENT du canal utilisé — jamais de la rapidité de la réponse.</p>
</div>
</div>

> **Piège fréquent :** le canal et le code ne sont jamais la même chose. Le canal, c'est \
PAR OÙ passe le message (une connexion internet, une feuille affichée) ; le code, c'est \
AVEC QUOI il est construit (une langue, des images, des couleurs). Un même code peut \
circuler par différents canaux, et un même canal peut transporter différents codes.

> **Piège fréquent :** la rétroaction dépend du canal, jamais du délai de réponse. Un mail \
ou un réseau social permettent d'adresser une réponse directement à l'émetteur, que cette \
réponse arrive en quelques minutes ou beaucoup plus tard — peu importe : le canal la \
permet. Une affiche, elle, ne permet en général aucune rétroaction directe vers son \
émetteur, quel que soit le délai."""


def _section_method() -> str:
    return """Face à une situation de communication (un document, une affiche, une publication...), \
procède toujours dans cet ordre :

<ol>
<li>Identifie l'<strong>émetteur</strong> : qui a produit ce message ?</li>
<li>Identifie le <strong>récepteur</strong> : à qui ce message s'adresse-t-il ?</li>
<li>Résume en une phrase le <strong>message</strong> : qu'est-ce qui est réellement \
transmis ?</li>
<li>Observe le <strong>code</strong> utilisé : quelle(s) langue(s), quelles images, \
quelles couleurs, quels symboles ?</li>
<li>Identifie le <strong>canal</strong> : par quel support concret le message \
circule-t-il ?</li>
<li>Précise le <strong>contexte</strong> : dans quelle situation ce message est-il \
émis ?</li>
<li>Cherche un éventuel <strong>obstacle</strong> : quelque chose a-t-il perturbé ou \
pourrait-il perturber la transmission ?</li>
<li>Demande-toi si une <strong>rétroaction</strong> est possible : le récepteur dispose-t-il \
d'un moyen, par ce canal, d'adresser une réponse à l'émetteur — peu importe le délai avant \
qu'elle n'arrive ?</li>
</ol>"""


def _analysis_table(rows: list[tuple[str, str]]) -> str:
    header = "| Élément du schéma | Ce qu'on observe dans ce document |\n|---|---|\n"
    return header + "\n".join(f"| **{label}** | {text} |" for label, text in rows)


def _section_examples() -> str:
    mail_rows = [
        ("Émetteur", "Karim Haddad, candidat à un emploi."),
        ("Récepteur", "Le service recrutement des Entrepôts Dufresne."),
        ("Message", "Une candidature pour un poste de manutentionnaire."),
        ("Code", "La langue française écrite, mise en forme selon les codes du mail professionnel (formule d'appel, présentation, pièce jointe)."),
        ("Canal", "La messagerie électronique, qui dépend elle-même d'une connexion internet."),
        ("Contexte", "Une procédure de recrutement pour un poste précis."),
        ("Obstacle", "Une coupure de connexion a interrompu l'envoi avant la fin du message et avant l'ajout du CV — un obstacle purement technique, indépendant de la qualité de la candidature."),
        ("Rétroaction", "Oui, directe : le service recrutement répond à Karim par le même canal pour signaler le problème — la réponse n'arrive que le lendemain, mais cela ne change rien à sa possibilité."),
    ]
    affiche_rows = [
        ("Émetteur", "Le Service public de Wallonie (SPW), via sa campagne de sécurité routière."),
        ("Récepteur", "Les automobilistes qui circulent sur cette route."),
        ("Message", "Inciter à ralentir à l'approche d'un passage piéton."),
        ("Code", "Un texte court et percutant, une image (silhouette d'enfant), des couleurs porteuses de sens (le rouge signale le danger), un logo institutionnel."),
        ("Canal", "Un panneau d'affichage fixe, installé en bordure de route."),
        ("Contexte", "La sécurité routière, à proximité d'un passage piéton."),
        ("Obstacle", "Le conducteur lit l'affiche en quelques secondes, à pleine vitesse, souvent partiellement concentré sur la conduite."),
        ("Rétroaction", "Non, pas directement : une affiche ne permet aucune rétroaction directe vers son émetteur. Seul le QR code offre une rétroaction indirecte (vers une page d'information, pas vers l'émetteur)."),
    ]
    social_rows = [
        ("Émetteur", "L'entreprise Techno Services Wallonie."),
        ("Récepteur", "Les utilisateurs du réseau social susceptibles de chercher un emploi dans ce secteur."),
        ("Message", "Une offre d'emploi de technicien·ne de maintenance industrielle."),
        ("Code", "Un texte court, des émojis, des hashtags — des signes propres au langage des réseaux sociaux, différents de ceux d'un mail professionnel."),
        ("Canal", "Une plateforme de réseau social en ligne."),
        ("Contexte", "Une campagne de recrutement dans le secteur de la maintenance industrielle."),
        ("Obstacle", "L'absence d'information sur le salaire crée une incompréhension visible (le commentaire de Julien P.) — un manque d'information peut constituer un obstacle, même sans panne technique."),
        ("Rétroaction", "Oui, directe et quasi immédiate : les commentaires, les partages et la réponse de l'entreprise à Fatima B. montrent un dialogue réel, adressé publiquement à l'émetteur."),
    ]
    decrypt_title = '<h4 class="jc-decrypt-title"><span aria-hidden="true">🔍</span> Décryptons ce document</h4>'
    return f"""<h3 class="jc-example-title">Exemple 1 — {FSE01_MAIL_TITLE}</h3>

{FSE01_MAIL_CARD_HTML}

{decrypt_title}

{_analysis_table(mail_rows)}

<h3 class="jc-example-title">Exemple 2 — {FSE01_AFFICHE_TITLE}</h3>

{FSE01_AFFICHE_CARD_HTML}

{decrypt_title}

{_analysis_table(affiche_rows)}

<h3 class="jc-example-title">Exemple 3 — {FSE01_SOCIAL_TITLE}</h3>

{FSE01_SOCIAL_CARD_HTML}

{decrypt_title}

{_analysis_table(social_rows)}"""


def _section_compare() -> str:
    return """Trois confusions reviennent très souvent à l'examen. Voici comment les éviter.

**Code et canal ne sont jamais la même chose :**

<div class="jc-compare">
<div class="jc-compare-item jc-compare-item--a">
<span class="jc-compare-label">Code</span>
<p>AVEC QUOI le message est construit : une langue, des images, des couleurs, des \
symboles.</p>
</div>
<div class="jc-compare-item jc-compare-item--b">
<span class="jc-compare-label">Canal</span>
<p>PAR OÙ le message circule : une connexion internet, une feuille affichée, une \
plateforme en ligne.</p>
</div>
</div>

**Rétroaction directe et rétroaction immédiate ne sont pas la même chose :**

<div class="jc-compare">
<div class="jc-compare-item jc-compare-item--a">
<span class="jc-compare-label">Rétroaction directe</span>
<p>Le récepteur peut adresser sa réponse À L'ÉMETTEUR, par le même canal — que ce soit \
rapide ou non. C'est la SEULE question qui compte pour dire si une rétroaction est \
possible.</p>
</div>
<div class="jc-compare-item jc-compare-item--b">
<span class="jc-compare-label">Rétroaction immédiate (rapide)</span>
<p>Le DÉLAI avant que la réponse n'arrive. Il ne change jamais la réponse à « une \
rétroaction est-elle possible ? » — le mail de Karim reçoit une réponse directe, mais \
seulement le lendemain : ce n'est pas immédiat, mais c'est bien direct.</p>
</div>
</div>

**Une mauvaise réponse fréquente, comparée à la bonne :**

<div class="jc-compare">
<div class="jc-compare-item jc-compare-item--bad">
<span class="jc-compare-label">❌ Mauvaise réponse</span>
<p>Question : « Quel est le canal utilisé dans le mail de Karim ? » Réponse : « Le \
français. » → confond le canal avec le code.</p>
</div>
<div class="jc-compare-item jc-compare-item--good">
<span class="jc-compare-label">✅ Bonne réponse</span>
<p>« Le canal est la messagerie électronique, qui dépend d'une connexion internet ; le \
français écrit est le code utilisé pour rédiger le message. »</p>
</div>
</div>

<div class="jc-compare">
<div class="jc-compare-item jc-compare-item--bad">
<span class="jc-compare-label">❌ Mauvaise réponse</span>
<p>Question : « Une affiche permet-elle une rétroaction ? » Réponse : « Oui, parce que \
n'importe qui peut réagir à un message. » → ignore que la rétroaction dépend du canal \
réellement utilisé, pas d'une possibilité théorique.</p>
</div>
<div class="jc-compare-item jc-compare-item--good">
<span class="jc-compare-label">✅ Bonne réponse</span>
<p>« Non, pas directement : une affiche ne permet pas au récepteur d'adresser une réponse \
à son émetteur. Seul le QR code offre une rétroaction indirecte, vers une page \
d'information. »</p>
</div>
</div>"""


def _section_exercises() -> str:
    return """<div class="jc-exercise-card">
<div class="jc-exercise-card-header">
<span class="jc-exercise-number" aria-hidden="true">1</span>
<h4 class="jc-exercise-title">Annoter le schéma de l'affiche</h4>
</div>
<div class="jc-exercise-instructions">
<p>Reprends l'affiche de sécurité routière et procède en deux étapes :</p>
<ol>
<li>Pour chacun des six premiers éléments du schéma (émetteur, récepteur, message, code, \
canal, contexte), note en une phrase ce qui correspond dans ce document.</li>
<li>Indique si une rétroaction directe est possible, et justifie ta réponse.</li>
</ol>
<p class="jc-exercise-doclink"><a href="#document-affiche">↑ Revoir l'affiche</a></p>
</div>
<details class="jc-exercise-correction">
<summary>Voir le corrigé</summary>
<div class="jc-exercise-correction-body">
<table>
<thead><tr><th>Élément</th><th>Réponse</th><th>Justification</th></tr></thead>
<tbody>
<tr><td>Émetteur</td><td>Le Service public de Wallonie (SPW)</td><td>Organisme à l'origine de la campagne.</td></tr>
<tr><td>Récepteur</td><td>Les automobilistes</td><td>Ce sont eux qui circulent sur cette route et lisent l'affiche.</td></tr>
<tr><td>Message</td><td>Inciter à ralentir près d'un passage piéton</td><td>C'est ce que le slogan demande explicitement.</td></tr>
<tr><td>Code</td><td>Texte court, image (silhouette d'enfant), couleurs (rouge = danger), logo institutionnel</td><td>Ce sont les signes utilisés pour construire le message.</td></tr>
<tr><td>Canal</td><td>Un panneau d'affichage fixe en bordure de route</td><td>C'est le support matériel par lequel le message circule.</td></tr>
<tr><td>Contexte</td><td>La sécurité routière, à proximité d'un passage piéton</td><td>C'est la situation qui donne son sens au message.</td></tr>
<tr><td>Rétroaction</td><td>Non, pas directement</td><td>Une affiche ne permet pas au conducteur d'adresser une réponse à son émetteur, quel que soit le délai ; seul le QR code permet une rétroaction indirecte, vers une page d'information — jamais vers l'émetteur lui-même.</td></tr>
</tbody>
</table>
<div class="jc-why-correct">
<span class="jc-why-correct-label">Pourquoi cette réponse est correcte</span>
<p>Elle traite les six éléments un par un, sans les mélanger, et justifie la réponse sur la \
rétroaction par une caractéristique réelle du canal (l'affiche), pas par une impression \
générale.</p>
</div>
</div>
</details>
</div>

<div class="jc-exercise-card">
<div class="jc-exercise-card-header">
<span class="jc-exercise-number" aria-hidden="true">2</span>
<h4 class="jc-exercise-title">Analyser la candidature de Karim</h4>
</div>
<div class="jc-exercise-instructions">
<p>Reprends le mail de Karim Haddad et réponds en trois temps :</p>
<ol>
<li>Identifie précisément l'obstacle qui a perturbé cette communication.</li>
<li>Explique sa conséquence concrète pour le récepteur.</li>
<li>Explique comment la rétroaction du service recrutement permet de résoudre le \
problème.</li>
</ol>
<p class="jc-exercise-doclink"><a href="#document-mail">↑ Revoir le mail</a></p>
</div>
<details class="jc-exercise-correction">
<summary>Voir le corrigé</summary>
<div class="jc-exercise-correction-body">
<div class="jc-exercise-section">
<span class="jc-exercise-section-label">Obstacle</span>
<p>Une coupure de connexion internet survenue pendant la rédaction du mail de Karim : son \
logiciel de messagerie a envoyé automatiquement le message resté inactif, alors qu'il \
était incomplet et sans pièce jointe.</p>
</div>
<div class="jc-exercise-section">
<span class="jc-exercise-section-label">Conséquence</span>
<p>Le service recrutement reçoit un message qui s'arrête en pleine phrase, sans CV, ce qui \
l'empêche d'évaluer la candidature.</p>
</div>
<div class="jc-exercise-section">
<span class="jc-exercise-section-label">Rétroaction</span>
<p>La réponse du service recrutement signalant le problème permet de résoudre la \
situation : parce que le canal utilisé (le mail) autorise une réponse adressée directement \
à Karim — même arrivée le lendemain —, celui-ci peut être informé de l'incident et \
renvoyer une candidature complète.</p>
</div>
<div class="jc-why-correct">
<span class="jc-why-correct-label">Pourquoi cette réponse est correcte</span>
<p>Elle distingue bien l'obstacle (la cause technique), sa conséquence (un message \
incomplet et incompréhensible), et la rétroaction (la réponse qui permet de corriger la \
situation), sans les confondre.</p>
</div>
</div>
</details>
</div>

<div class="jc-exercise-card">
<div class="jc-exercise-card-header">
<span class="jc-exercise-number" aria-hidden="true">3</span>
<h4 class="jc-exercise-title">Question flash — la publication Techno Services Wallonie</h4>
</div>
<div class="jc-exercise-instructions">
<p>Dans la publication, quel(s) élément(s) du schéma de communication le commentaire de \
Julien P. (« Encore une offre qui ne précise pas le salaire... ») met-il en évidence ?</p>
<p class="jc-exercise-doclink"><a href="#document-social">↑ Revoir la publication</a></p>
</div>
<details class="jc-exercise-correction">
<summary>Voir le corrigé</summary>
<div class="jc-exercise-correction-body">
<p>Ce commentaire met en évidence <strong>deux éléments à la fois</strong> :</p>
<div class="jc-compare">
<div class="jc-compare-item jc-compare-item--a">
<span class="jc-compare-label">Obstacle</span>
<p>Une information manquante dans le message initial (l'absence du salaire) crée une \
incompréhension chez une partie des récepteurs.</p>
</div>
<div class="jc-compare-item jc-compare-item--b">
<span class="jc-compare-label">Rétroaction</span>
<p>Ce commentaire est lui-même une rétroaction : grâce au canal utilisé (le réseau \
social), le récepteur peut exprimer directement et publiquement sa réaction à \
l'émetteur.</p>
</div>
</div>
<div class="jc-why-correct">
<span class="jc-why-correct-label">Pourquoi cette réponse est correcte</span>
<p>Elle identifie précisément deux éléments du schéma présents dans la même phrase du \
document, sans se limiter à un seul, et justifie chaque élément par un passage exact du \
document.</p>
</div>
</div>
</details>
</div>"""


def _section_memo() -> str:
    return """- Une communication réunit toujours : émetteur, récepteur, message, code, canal, \
contexte.
- Canal = PAR OÙ passe le message (support) ; code = AVEC QUOI le message est construit \
(système de signes) — ne jamais confondre les deux.
- Un obstacle (bruit) peut être technique (une coupure) ou lié au contenu du message \
(une information manquante, une formulation ambiguë).
- La rétroaction dépend UNIQUEMENT du canal, jamais du délai de réponse : un mail ou un \
réseau social permettent d'adresser une réponse directement à l'émetteur (vite ou après \
un délai) ; une affiche, en général, ne le permet pas du tout.
- Face à un document, applique toujours la méthode dans l'ordre : émetteur → récepteur → \
message → code → canal → contexte → obstacle → rétroaction."""


def fse01_course_sections() -> list[tuple[str, str]]:
    """Sections (titre, Markdown) du cours FSE01 — chaque titre pilote le type de carte
    affiché (`app.card_kind.classify_block_title`), voir docstring du module."""
    return [
        ("FSE01 — Présentation et objectifs", _section_intro()),
        ("FSE01 — Théorie : le schéma de communication", _section_theory()),
        ("FSE01 — Méthode", _section_method()),
        ("FSE01 — Exemples commentés : mail, affiche, réseau social", _section_examples()),
        ("FSE01 — Comparer pour ne pas confondre", _section_compare()),
        ("FSE01 — Exercices guidés", _section_exercises()),
        ("FSE01 — Fiche mémo", _section_memo()),
    ]
