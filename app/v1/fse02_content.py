"""Documents support — FSE02 « Les médias et leurs financements » (ticket #97, cahier des
charges détaillé ; présentation réaliste ticket #115).

Trois situations originales, rédigées pour ce cours (jamais une modification d'une source
officielle — `docs/content_workflow.md`), illustrant les trois modes de financement
explicitement demandés par le ticket #97 : un média payant (vente/abonnement), un média
gratuit financé par la publicité, et un média financé par des fonds publics. Les trois
organisations citées sont fictives, créées pour cet exercice.

Deux formes pour chaque document (même principe que FSE01, ticket #103/#108) :
- `FSE02_*_TEXT` (texte brut, inchangé depuis le ticket #96) : utilisé pour créer le
  `SourceDocument`/`SourceDocumentVersion` de la banque de questions
  (`app.v1.fse_bank.import_fse02_to_bank`) — jamais modifié.
- `FSE02_*_CARD_HTML` (nouveau, ticket #115) : le MÊME contenu, mis en forme comme une
  vraie page de média (maquette HTML/CSS) — jamais une reformulation des faits. Ce sont des
  supports pédagogiques fictifs : aucun paiement réel, aucun formulaire n'envoie de
  données."""

FSE02_PAID_TITLE = "L'Hebdo du Littoral — page d'abonnement"
FSE02_PAID_TEXT = """[Page d'abonnement du site de L'Hebdo du Littoral, journal hebdomadaire papier et \
numérique — média fictif créé pour cet exercice]

L'HEBDO DU LITTORAL — Abonnez-vous

Accédez à l'intégralité de nos articles, dossiers et enquêtes locales.

Nos formules :
- Édition papier + numérique : 14 € par mois
- Édition numérique seule : 9 € par mois
- Numéro à l'unité, en kiosque : 2,50 €

« Sans publicité intrusive, sans contenu sponsorisé : notre seule source de revenus est \
constituée par nos lecteurs et lectrices. »

Aucun article complet n'est consultable sans abonnement ou achat du numéro. Un encadré \
« Vos lettres » publie chaque semaine une sélection de courriers de lecteurs en réaction \
aux articles parus."""

FSE02_PAID_CARD_HTML = """<div class="jc-doc" id="document-hebdo">
<div class="jc-doc-header"><strong>📰 Page d'abonnement — L'Hebdo du Littoral</strong><span class="jc-doc-fictive-badge">Fictif</span></div>
<div class="jc-doc-body">
<div class="jc-webpage-masthead">L'HEBDO DU LITTORAL</div>
<p class="jc-webpage-tagline">Accédez à l'intégralité de nos articles, dossiers et enquêtes locales.</p>
<div class="jc-pricing-cards">
<div class="jc-pricing-card">
<span class="jc-pricing-card-label">Papier + numérique</span>
<span class="jc-pricing-card-price">14 €<small>/mois</small></span>
</div>
<div class="jc-pricing-card">
<span class="jc-pricing-card-label">Numérique seul</span>
<span class="jc-pricing-card-price">9 €<small>/mois</small></span>
</div>
<div class="jc-pricing-card">
<span class="jc-pricing-card-label">Numéro à l'unité (kiosque)</span>
<span class="jc-pricing-card-price">2,50 €</span>
</div>
</div>
<p class="jc-webpage-quote">« Sans publicité intrusive, sans contenu sponsorisé : notre seule source de revenus est constituée par nos lecteurs et lectrices. »</p>
<p class="jc-webpage-note">Aucun article complet n'est consultable sans abonnement ou achat du numéro.</p>
<div class="jc-reader-letters">
<span class="jc-reader-letters-title">✉️ Vos lettres</span>
<p>Chaque semaine, une sélection de courriers de lecteurs en réaction aux articles parus.</p>
</div>
</div>
</div>"""

FSE02_FREE_AD_TITLE = "Le Flash Infos — page d'accueil"
FSE02_FREE_AD_TEXT = """[Capture de la page d'accueil du site d'information Le Flash Infos — média fictif créé \
pour cet exercice]

LE FLASH INFOS — Toute l'actu, 100 % gratuite

[Bannière publicitaire : « Soldes chez MégaStore, -40 % cette semaine »]

À LA UNE : Travaux sur le pont de la gare, circulation perturbée dès lundi

[Bannière publicitaire : « Assurance auto moins chère avec AutoPlus »]

Tous nos articles sont accessibles gratuitement, sans inscription. Le Flash Infos vit \
exclusivement des revenus publicitaires générés par les annonceurs visibles sur le site : \
plus un article est consulté, plus il génère de revenus publicitaires pour le site. \
Chaque article affiche un compteur de vues et un bouton « Partager », et permet de laisser \
un commentaire visible publiquement sous le texte."""

FSE02_FREE_AD_CARD_HTML = """<div class="jc-doc" id="document-flashinfos">
<div class="jc-doc-header"><strong>📰 Page d'accueil — Le Flash Infos</strong><span class="jc-doc-fictive-badge">Fictif</span></div>
<div class="jc-doc-body">
<div class="jc-webpage-masthead jc-webpage-masthead--free">LE FLASH INFOS<span class="jc-webpage-masthead-tag">Toute l'actu, 100 % gratuite</span></div>
<p class="jc-ad-banner jc-ad-banner--a">📢 Soldes chez MégaStore, -40 % cette semaine</p>
<p class="jc-webpage-headline">À LA UNE : Travaux sur le pont de la gare, circulation perturbée dès lundi</p>
<p class="jc-ad-banner jc-ad-banner--b">📢 Assurance auto moins chère avec AutoPlus</p>
<div class="jc-webpage-article-meta">
<span>👁️ Compteur de vues visible</span>
<span>🔁 Bouton Partager</span>
<span>💬 Commentaire public possible</span>
</div>
</div>
</div>"""

FSE02_PUBLIC_TITLE = "Radio Communauté Wallonie (RCW) — page « Qui sommes-nous »"
FSE02_PUBLIC_TEXT = """[Extrait de la page « Qui sommes-nous » du site de Radio Communauté Wallonie (RCW) — \
média de service public fictif, créé pour cet exercice]

Radio Communauté Wallonie (RCW) est un média de service public. Son fonctionnement est \
financé par une dotation publique, votée chaque année, et non par la vente de ses \
programmes ni par la publicité commerciale.

Notre mission : informer l'ensemble de la population, y compris sur des sujets qui \
intéressent peu les annonceurs publicitaires (santé publique, éducation, actualité \
institutionnelle locale).

RCW ne diffuse aucune publicité commerciale entre ses programmes. Chaque matin, une \
émission en direct permet aux auditeurs d'appeler l'antenne pour réagir à l'actualité du \
jour."""

FSE02_PUBLIC_CARD_HTML = """<div class="jc-doc" id="document-rcw">
<div class="jc-doc-header"><strong>📻 Page « Qui sommes-nous » — Radio Communauté Wallonie</strong><span class="jc-doc-fictive-badge">Fictif</span></div>
<div class="jc-doc-body">
<div class="jc-webpage-masthead jc-webpage-masthead--public">RADIO COMMUNAUTÉ WALLONIE</div>
<p class="jc-webpage-tagline">Média de service public, financé par une dotation publique votée chaque année — et non par la vente de ses programmes ni par la publicité commerciale.</p>
<p>Notre mission : informer l'ensemble de la population, y compris sur des sujets qui intéressent peu les annonceurs publicitaires (santé publique, éducation, actualité institutionnelle locale).</p>
<p class="jc-webpage-note">RCW ne diffuse aucune publicité commerciale entre ses programmes.</p>
<div class="jc-webpage-feature">
<span class="jc-webpage-feature-icon" aria-hidden="true">📞</span>
<div><strong>Émission du matin</strong><p>Chaque matin, une émission en direct permet aux auditeurs d'appeler l'antenne pour réagir à l'actualité du jour.</p></div>
</div>
</div>
</div>"""
