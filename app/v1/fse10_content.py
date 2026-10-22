"""Documents support — FSE10 « Élections et participation citoyenne » (ticket #99, cahier
des charges détaillé).

Deux documents : un tableau daté des scrutins belges (vérifié auprès de sources belges
officielles/publiques — voir `app.v1.fse10_course` § Sources officielles vérifiées) et des
bulletins fictifs illustrant vote valable/blanc/nul. Conformément au ticket #99 : « Toute
condition d'âge, obligation, calendrier ou exception doit être vérifiée par scrutin et
région à la date du cours » — le tableau ci-dessous porte explicitement une date de
vérification et distingue les régions là où la règle diffère (vote obligatoire en
Wallonie/Bruxelles mais plus en Flandre pour les communales/provinciales depuis 2024)."""

FSE10_TABLE_TITLE = "Tableau daté des scrutins belges (vérifié le 2026-10-01)"
FSE10_TABLE_TEXT = """[Tableau original, rédigé pour ce cours à partir de sources belges officielles/\
publiques vérifiées le 2026-10-01 — voir le cours pour les références]

SCRUTIN FÉDÉRAL — élit la Chambre des représentants. Vote obligatoire sur tout le \
territoire belge. Scrutin proportionnel (les sièges sont répartis entre les listes selon \
leur nombre de voix, pas seulement à la liste arrivée en tête).

SCRUTIN RÉGIONAL — élit les parlements de Région/Communauté. Vote obligatoire sur tout le \
territoire belge. Scrutin proportionnel, comme le scrutin fédéral.

SCRUTIN EUROPÉEN — élit les député·e·s belges au Parlement européen. Vote obligatoire pour \
les personnes de 18 ans et plus. Depuis une loi du 25 décembre 2023, confirmée par un arrêt \
de la Cour constitutionnelle du 21 mars 2024, les jeunes de 16 et 17 ans peuvent voter à ce \
scrutin et y sont également soumis à l'obligation de vote.

SCRUTIN COMMUNAL ET PROVINCIAL — élit les conseils communaux et provinciaux. Depuis le \
scrutin du 13 octobre 2024, le vote n'est plus obligatoire en Région flamande pour ces deux \
scrutins. Il reste obligatoire en Région wallonne et en Région de Bruxelles-Capitale pour \
ces mêmes scrutins.

NOTE IMPORTANTE : ce tableau reflète la situation vérifiée à la date indiquée ci-dessus. \
Les règles électorales peuvent évoluer : avant toute affirmation sur un scrutin réel, \
vérifie la date, le scrutin précis et la région concernée auprès d'une source officielle."""

FSE10_BALLOTS_TITLE = "Quatre bulletins fictifs à analyser"
FSE10_BALLOTS_TEXT = """[Bulletins fictifs, rédigés pour cet exercice — aucune liste ni aucun candidat réel]

Bulletin A — Le bulletin ne porte aucune marque, aucune case n'est remplie.

Bulletin B — Une seule case est remplie, en face du nom d'une liste précise.

Bulletin C — Une case est remplie en face d'une liste, mais l'électeur a aussi écrit un \
commentaire personnel dans la marge du bulletin.

Bulletin D — Deux cases sont remplies, chacune en face d'une liste différente."""
