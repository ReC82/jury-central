"""Documents support — FSE16 « Analyser une décision publique » (ticket #100, cahier des
charges détaillé).

Trois documents fictifs, rédigés pour ce cours, formant un dossier complet sur une
proposition d'aide aux transports (ticket #100 § FSE16, "Application attendue" : « dossier
original de 3 documents... effets sur ménages, entreprises, État et reste du monde ;
conclusion justifiée »). Réutilise volontairement budget (FSE12), sécurité sociale
(FSE13-14) et circuit économique (FSE15) comme outils d'analyse, sans les ré-enseigner."""

FSE16_PROPOSAL_TITLE = "Proposition fictive — carte de transport collectif subventionnée"
FSE16_PROPOSAL_TEXT = """[Proposition entièrement fictive, rédigée pour cet exercice — aucun montant, \
aucun organisme réel]

Un gouvernement régional fictif propose de subventionner une partie du prix des abonnements \
de transport collectif (bus, train régional) pour les travailleurs à revenus modestes, \
financée par le budget régional. L'objectif affiché est de faciliter l'accès à l'emploi et \
de réduire l'usage de la voiture individuelle pour les trajets domicile-travail."""

FSE16_BUDGET_NOTE_TITLE = "Note budgétaire fictive accompagnant la proposition"
FSE16_BUDGET_NOTE_TEXT = """[Document fictif, rédigé pour cet exercice — aucun montant réel]

La subvention serait financée par une partie du budget régional existant (compétence \
territoriale, voir FSE09). À court terme, la dépense régionale augmente. À moyen terme, la \
note budgétaire évoque un effet indirect possible : si davantage de travailleurs à revenus \
modestes accèdent plus facilement à un emploi grâce au transport subventionné, les recettes \
fiscales et parafiscales de cet emploi (vues en FSE12-13) pourraient partiellement compenser \
la dépense initiale — un effet incertain, présenté comme une hypothèse, pas un résultat \
garanti."""

FSE16_REACTIONS_TITLE = "Réactions fictives de trois groupes concernés"
FSE16_REACTIONS_TEXT = """[Réactions fictives, rédigées pour cet exercice — aucune personne ni \
organisation réelle]

Réaction d'un ménage concerné : « Cette aide me permettrait d'accepter un emploi plus loin \
de chez moi, que je refusais jusqu'ici à cause du coût du transport. »

Réaction d'une entreprise de transport collectif : « Nous nous attendons à une hausse de la \
fréquentation, mais aussi à des coûts supplémentaires pour augmenter la capacité de nos \
lignes les plus demandées. »

Réaction d'une association de défense de l'environnement : « Nous saluons l'effet attendu \
de réduction de l'usage de la voiture individuelle, mais rappelons que cet effet dépendra de \
la capacité réelle du réseau à absorber la demande supplémentaire — un effet incertain à \
court terme, qui pourrait ne se concrétiser qu'à plus long terme si le réseau est renforcé en \
conséquence. »"""

# Ticket #115 : présentation réaliste — texte brut ci-dessus inchangé (banque de questions,
# `app.v1.fse_bank.import_fse16_to_bank`, document « document 3 » référencé dans les
# exercices). Chaque partie prenante garde la même couleur (`.jc-social-avatar--pN`).
FSE16_REACTIONS_CARD_HTML = """<div class="jc-doc" id="document-reactions">
<div class="jc-doc-header"><strong>💬 Réactions — trois groupes concernés</strong><span class="jc-doc-fictive-badge">Fictif</span></div>
<div class="jc-doc-body">
<div class="jc-quote-card">
<span class="jc-social-avatar jc-social-avatar--p1" aria-hidden="true">🏠</span>
<div><span class="jc-quote-author">Un ménage concerné</span><p class="jc-quote-text">« Cette aide me permettrait d'accepter un emploi plus loin de chez moi, que je refusais jusqu'ici à cause du coût du transport. »</p></div>
</div>
<div class="jc-quote-card">
<span class="jc-social-avatar jc-social-avatar--p2" aria-hidden="true">🚌</span>
<div><span class="jc-quote-author">Une entreprise de transport collectif</span><p class="jc-quote-text">« Nous nous attendons à une hausse de la fréquentation, mais aussi à des coûts supplémentaires pour augmenter la capacité de nos lignes les plus demandées. »</p></div>
</div>
<div class="jc-quote-card">
<span class="jc-social-avatar jc-social-avatar--p3" aria-hidden="true">🌱</span>
<div><span class="jc-quote-author">Une association de défense de l'environnement</span><p class="jc-quote-text">« Nous saluons l'effet attendu de réduction de l'usage de la voiture individuelle, mais rappelons que cet effet dépendra de la capacité réelle du réseau à absorber la demande supplémentaire — un effet incertain à court terme, qui pourrait ne se concrétiser qu'à plus long terme si le réseau est renforcé en conséquence. »</p></div>
</div>
</div>
</div>"""
