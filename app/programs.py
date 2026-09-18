"""Arborescence de parcours CESS (ticket #67, passe UX accueil/navigation).

Structure STATIQUE, volontairement indépendante de toute table de base de données :
CESS → filière (P/G/TTR/TQ) → matière → (module) → UAA. Aucune des priorités du produit
(génération, correction, banque, rating, admin, paiement) n'est modifiée par ce ticket —
cette arborescence sert uniquement à la NAVIGATION/DÉCOUVERTE, elle réutilise telle quelle
la hiérarchie déjà en place (`app.models.Subject`/`Module`/`UAA`) pour tout ce qui a un
contenu réel.

Seule la filière « P » (Professionnel) et la matière « Informatique » sont réellement
câblées aujourd'hui (le programme AMPCR, `app.v1.ampcr_plan`). Les autres entrées
(`available=False`) existent pour que l'écran affiche déjà la structure cible complète
(§ 5 du ticket : « ne hardcode pas une architecture impossible à étendre ») sans qu'un
lien mène nulle part : une entrée non disponible n'est jamais un lien cliquable côté
template, seulement un intitulé avec un badge « Bientôt disponible »."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CessFiliere:
    slug: str
    title: str
    available: bool


@dataclass(frozen=True)
class CessSubjectLink:
    slug: str
    title: str
    # Slug de la Subject réelle (`app.models.Subject.slug`) quand la matière est câblée à
    # du contenu existant — `None` pour un placeholder futur sans contenu.
    subject_slug: str | None
    available: bool


CESS_FILIERES: tuple[CessFiliere, ...] = (
    CessFiliere(slug="p", title="CESS Professionnel", available=True),
    CessFiliere(slug="g", title="CESS Général", available=False),
    CessFiliere(slug="ttr", title="CESS Technique de Transition", available=False),
    CessFiliere(slug="tq", title="CESS Technique de Qualification", available=False),
)

# Matières de la filière CESS Professionnel — seule « Informatique » est câblée à du
# contenu réel aujourd'hui (programme AMPCR). Les autres sont des emplacements réservés,
# explicitement demandés par le ticket (§ 5 : Français/Maths/Sciences/autres options
# professionnelles), jamais implémentés ici.
CESS_P_SUBJECTS: tuple[CessSubjectLink, ...] = (
    CessSubjectLink(slug="informatique", title="Informatique", subject_slug="informatique", available=True),
    CessSubjectLink(slug="francais", title="Français", subject_slug=None, available=False),
    CessSubjectLink(slug="maths", title="Mathématiques", subject_slug=None, available=False),
    CessSubjectLink(slug="sciences", title="Sciences", subject_slug=None, available=False),
)

# {filiere_slug: matières} — un seul groupe câblé pour l'instant ; une future filière
# ajoutera simplement sa propre entrée ici, sans toucher aux routes/templates.
CESS_SUBJECTS_BY_FILIERE: dict[str, tuple[CessSubjectLink, ...]] = {
    "p": CESS_P_SUBJECTS,
}


def get_filiere(slug: str) -> CessFiliere | None:
    return next((f for f in CESS_FILIERES if f.slug == slug), None)


def get_subject_link(filiere_slug: str, subject_slug: str) -> CessSubjectLink | None:
    subjects = CESS_SUBJECTS_BY_FILIERE.get(filiere_slug, ())
    return next((s for s in subjects if s.slug == subject_slug), None)
