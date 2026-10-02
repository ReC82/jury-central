"""Documents support — FSE01 « Communiquer : le schéma de communication » (ticket #96,
cahier des charges détaillé du ticket #97).

Trois situations originales, rédigées pour ce cours (jamais une modification d'une source
officielle — `docs/content_workflow.md`, § « Contenu rédigé à partir d'un cahier des
charges »), couvrant les trois applications explicitement demandées par le ticket #97 :
un mail, une affiche et une publication sur un réseau social. Chacune permet d'identifier
émetteur/récepteur/message/code/canal/contexte, un obstacle (bruit) et la rétroaction
disponible — ou son absence — selon le canal utilisé."""

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
