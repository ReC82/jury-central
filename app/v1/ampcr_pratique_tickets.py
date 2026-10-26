"""Modèles de tickets PR01–PR30 / EX01–EX06 du parcours AMPCR pratique écrite (ticket #192).

Chaque futur ticket de cours ou d'examen est un **cahier des charges pédagogique** rédigé
par le propriétaire AVANT exécution : la session qui le traite n'improvise pas le programme.
Ce module produit, depuis le plan (`app.v1.ampcr_pratique_plan`), l'amorce de chaque ticket :
titre, exigences officielles couvertes (texte exact du PDF), théorie MC à réutiliser,
écarts connus, puis les sections à compléter et les exigences transversales (visuels,
évaluation, contrat de fin de ticket).

`docs/ampcr_pratique_tickets.md` contient la sortie de `render_document()` ; un test vérifie
qu'il reste synchronisé avec le plan. Régénération :
`python -m app.v1.ampcr_pratique_tickets > docs/ampcr_pratique_tickets.md`
Amorce d'un seul ticket : `python -m app.v1.ampcr_pratique_tickets PR07`.
"""

import sys

from app.v1 import ampcr_pratique_plan as plan

# Tickets de cours déjà rédigés par le propriétaire (le ticket fait foi pour son contenu).
EXISTING_TICKETS: dict[str, int] = {"PR06": 193, "PR11": 194, "PR15": 197}
SOCLE_TICKET = 192

COURSE_SECTIONS: tuple[tuple[str, str], ...] = (
    ("Objectifs observables",
     ("Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, "
     "décrire une procédure, interpréter un document, diagnostiquer, justifier).")),
    ("Matière obligatoire — à enseigner explicitement",
     ("Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id "
     "AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures "
     "détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs "
     "fréquentes ; diagnostics ; cas pratiques.")),
    ("Compléments autorisés",
     ("Explications, techniques actuelles, exercices ou illustrations que la session peut "
     "ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la "
     "matière obligatoire.")),
    ("Supports visuels exigés",
     ("Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration "
     "générée par API / tableau / capture fictive identifiée comme telle), données de "
     "référence, orientation de lecture, légende et texte alternatif attendus.")),
    ("Pédagogie, cas et exercices",
     ("Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur "
     "répartition (procédures écrites, analyses de documents, choix justifiés) ; "
     "mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée "
     "avant soumission, barème détaillé).")),
    ("Critères d'acceptation spécifiques", "Ce que le propriétaire vérifiera en priorité."),
)

EXAM_SECTIONS: tuple[tuple[str, str], ...] = (
    ("Composition de l'examen",
     ("Nombre d'exercices, points par exercice, total /20 ; chaque exigence AP du module "
     "évaluée au moins une fois. Aucune durée inventée (les consignes n'en fixent pas).")),
    ("Exercices et documents",
     ("Pour chaque exercice : situation, documents/schémas fournis, consignes numérotées, "
     "réponse libre, barème par critère, correction justifiée (format "
     "`/ampcr-pratique/format-exercice`).")),
    ("Supports visuels exigés",
     "Schémas et documents à produire, avec leurs données de référence."),
    ("Critères d'acceptation spécifiques", "Ce que le propriétaire vérifiera en priorité."),
)

TRANSVERSAL_RULES = """\
### Exigences transversales (ticket socle #192 — rappel obligatoire)
- **Programme** : enseigner la matière ci-dessus, sans l'improviser ni la réduire ; recouper
  avec le PDF officiel (`docs/ampcr_pratique_v1.md` § 1). Distinguer théorie et compétence
  d'intervention écrite. Ne jamais inventer de modalité d'examen, de question officielle, de
  durée ou de valeur technique.
- **Visuels** : schémas techniques (brochages, couleurs, topologies, plans d'adressage,
  partitions, flux de diagnostic, procédures) en **SVG construit à partir de données
  vérifiées** (`app/v1/ampcr_pratique_visuals.py`) et testés ; illustrations d'ambiance par
  l'API d'images existante (commande manuelle, fichier statique + JSON du prompt, quotas
  respectés, clé jamais exposée), **jamais** comme source de broches, couleurs, textes ou
  valeurs. Légende, texte alternatif, lisibilité mobile et A4 (y compris noir et blanc).
  Nouvelle bibliothèque seulement après examen licence / sécurité / poids / dépendances.
- **Évaluation** : chaque question a un contexte non ambigu, les données nécessaires, une
  tâche professionnelle claire, des critères et un barème ; pas de récitation d'acronymes ;
  une réponse juste formulée autrement est acceptée.
- **Intégration** : module `AMPCR-PRATIQUE`, UAA de code `PRxx`/`EXxx`
  (slug `ampcr-pratique-prxx`), moteur de sessions, correction et progression existants ;
  pas de duplication de la théorie MC (y renvoyer).
- **Checklist** : `docs/ampcr_pratique_tickets.md` § 3, cochée dans le rapport."""

END_CONTRACT = """\
### Contrat de fin de ticket (obligatoire, même bloqué)
1. **Rapport final daté** `docs/claude-reports/AAAA-MM-JJ_ticket-<n>-<sujet>.md` : travaux,
   commits/PR, tests, limites, procédure de test ; copie dans le dossier de rapports de
   l'orchestrateur.
2. **Email de fin de ticket** : envoyé par l'orchestrateur `jcorch` via la configuration
   SMTP existante de Jury Central dès que la session rend `WAITING_OWNER` (« Livré ») ou
   `BLOCKED` (« Question bloquante »), avec numéro/lien, état réel, résumé, liens de test,
   questions et rapport joint. La session ne configure ni n'appelle le SMTP elle-même ; le
   résultat d'envoi est journalisé par l'orchestrateur (heure d'envoi, essais, type
   d'erreur), sans adresse inventée ni secret.
3. **Commentaire GitHub** de synthèse (ligne `<!-- jcorch -->`) et statut conforme au
   workflow ; rien n'est annoncé « livré » avant les contrôles. Le propriétaire ferme le
   ticket après validation."""


def _requirement_lines(requirement_ids: tuple[str, ...]) -> list[str]:
    lines = []
    for requirement_id in requirement_ids:
        requirement = plan.REQUIREMENTS_BY_ID[requirement_id]
        where = f"p. {requirement.page}" if requirement.page else "complément pédagogique"
        line = f"- **{requirement.id}** ({where}) — « {requirement.text} »"
        if requirement.note:
            line += f" _Note : {requirement.note}_"
        lines.append(line)
    return lines


def _theory_codes(requirement_ids: tuple[str, ...]) -> list[str]:
    codes: set[str] = set()
    for requirement_id in requirement_ids:
        codes.update(plan.REQUIREMENTS_BY_ID[requirement_id].theory_codes)
    return sorted(codes)


def _sections(sections: tuple[tuple[str, str], ...]) -> list[str]:
    lines = []
    for title, hint in sections:
        lines += [f"### {title}", f"_À compléter — {hint}_", ""]
    return lines


_RULES_REFERENCE = (
    "> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de "
    "ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon)."
)


def _closing(full: bool) -> list[str]:
    return [TRANSVERSAL_RULES, "", END_CONTRACT, ""] if full else [_RULES_REFERENCE, ""]


def course_ticket(code: str, *, full: bool = True) -> str:
    course = plan.COURSE_SLOTS_BY_CODE[code]
    module = plan.MODULES_BY_KEY[course.module_key]
    theory = _theory_codes(course.requirement_ids)
    lines = [
        f"## [P0][AMPCR pratique {code}] {course.title}",
        "",
        (f"**Parcours** AMPCR — Pratique écrite, cycle {plan.CYCLE_LABEL} · **module** "
        f"{module.key} — {module.title} · **examen du module** {module.exercise_code} · "
        f"**socle** #{SOCLE_TICKET}."),
    ]
    if code in EXISTING_TICKETS:
        lines.append(f"**Ticket déjà rédigé : #{EXISTING_TICKETS[code]}** (il fait foi).")
    lines += ["", "### Exigences officielles couvertes (matrice #192)"]
    lines += _requirement_lines(course.requirement_ids)
    lines += [
        "",
        "**Théorie existante à réutiliser** : "
        + (", ".join(theory) if theory else "aucune (notion absente des MC publiés)") + ".",
        "",
    ]
    lines += _sections(COURSE_SECTIONS)
    lines += _closing(full)
    return "\n".join(lines)


def exam_ticket(code: str, *, full: bool = True) -> str:
    exercise = plan.EXERCISE_SLOTS_BY_CODE[code]
    module = plan.MODULES_BY_KEY[exercise.module_key]
    requirement_ids = tuple(
        r.id for r in plan.ALL_REQUIREMENTS
        if exercise in plan.exercises_for_requirement(r.id)
    )
    lines = [
        f"## [P0][AMPCR pratique {code}] Examen écrit du module {module.key} — {module.title}",
        "",
        (f"**Parcours** AMPCR — Pratique écrite, cycle {plan.CYCLE_LABEL} · **socle** "
        f"#{SOCLE_TICKET} · **cours du module** {', '.join(module.course_codes)} "
        "(dépendances : leurs tickets doivent être livrés avant)."),
        "",
        "### Exigences à évaluer (matrice #192)",
    ]
    lines += _requirement_lines(requirement_ids)
    lines += [
        "",
        ("Une exigence passe à « validé » dans la matrice (`VALIDATED_REQUIREMENT_IDS`) "
        "seulement quand ses cours ET cet examen sont publiés et relus."),
        "",
    ]
    lines += _sections(EXAM_SECTIONS)
    lines += _closing(full)
    return "\n".join(lines)


CHECKLIST = """\
Recopier dans chaque rapport PR/EX, chaque case cochée ou justifiée.

**Contenu**
- [ ] Toute la matière obligatoire du ticket est enseignée, dans l'ordre logique annoncé.
- [ ] Chaque section est rattachée à un id AP ; les compléments sont signalés comme tels.
- [ ] Valeurs, normes, commandes et messages vérifiés contre une source citée dans le rapport.
- [ ] Aucune modalité d'examen, durée, question « officielle » ou valeur inventée.
- [ ] Sécurité (électrique, ESD, données) rappelée avant toute manipulation décrite ; aucune
      action destructive proposée en premier réflexe.
- [ ] Renvois vers la théorie MC au lieu de la dupliquer.

**Exercices et évaluation**
- [ ] Chaque question : contexte suffisant, données fournies, tâche claire, barème, correction
      justifiée ; aucune récitation d'acronyme.
- [ ] Correction invisible avant soumission ; une réponse juste formulée autrement est acceptée.
- [ ] Nombre de cas, d'exercices et de questions conforme au ticket.

**Visuels**
- [ ] Chaque schéma technique est un SVG construit depuis des données vérifiées, avec un test
      qui contrôle ces données (ordre, couleurs, valeurs, étapes).
- [ ] Orientation de lecture indiquée quand elle compte (broches, faces, sens du flux).
- [ ] Légende, texte alternatif complet, mention « non officiel » si pertinent.
- [ ] Lisible sur téléphone (360 px) et à l'impression A4, y compris en noir et blanc
      (l'information ne repose pas sur la seule couleur).
- [ ] Image générée : uniquement pour une scène ou un geste, sans texte ni valeur technique,
      prompt et modèle conservés dans un JSON ; jamais générée à la consultation.
- [ ] Rendu réellement contrôlé (capture d'écran mobile et aperçu d'impression).

**Intégration et livraison**
- [ ] UAA du module `AMPCR-PRATIQUE`, seed idempotent, publiée seulement une fois complète.
- [ ] Matrice `/ampcr-pratique/matrice` à jour ; parcours MC01–MC38 inchangé.
- [ ] Tests ciblés verts, ruff sans nouvelle erreur.
- [ ] Rapport, email (via l'orchestrateur) et commentaire GitHub faits."""


def render_document() -> str:
    parts = [
        "# AMPCR — Pratique écrite : modèles de tickets PR01–PR30 et EX01–EX06 (ticket #192)",
        "",
        ("Document généré par `python -m app.v1.ampcr_pratique_tickets` depuis le plan "
        "(`app/v1/ampcr_pratique_plan.py`) ; ne pas l'éditer à la main."),
        "",
        "## 1. Mode d'emploi",
        "",
        ("1. Le propriétaire crée un ticket GitHub par cours (PR) ou examen de module (EX), "
        "en copiant l'amorce correspondante du § 4 et en **rédigeant la matière** dans les "
        "sections « À compléter ». Les tickets #193 (PR06), #194 (PR11) et #197 (PR15) "
        "sont les références de niveau de détail attendu."),
        ("2. Titre : `[P0][AMPCR pratique PRxx] …` ou `[P0][AMPCR pratique EXxx] …` (priorité "
        "au choix du propriétaire) ; l'orchestrateur traite les tickets par priorité puis "
        "ancienneté."),
        ("3. Un EX dépend des PR de son module ; une session qui reçoit un EX avant ses PR "
        "rend `READY` avec la dépendance."),
        ("4. Si le titre ou le périmètre d'un ticket diffère du plan, **le ticket fait foi** : "
        "la session réaligne le plan et la matrice dans la même PR."),
        ("5. Livraison incrémentale : chaque cours est publié dès qu'il est complet, sans "
        "attendre le module entier."),
        "",
        "## 2. Gabarit commun",
        "",
        "Un ticket de cours contient, dans cet ordre : en-tête (parcours, module, examen du "
        "module, socle) ; exigences officielles couvertes (texte exact) ; théorie existante ; "
        + " ; ".join(title.lower() for title, _ in COURSE_SECTIONS)
        + " ; exigences transversales ; contrat de fin de ticket.",
        "",
        "Un ticket d'examen contient : en-tête et dépendances ; exigences à évaluer ; "
        + " ; ".join(title.lower() for title, _ in EXAM_SECTIONS)
        + " ; exigences transversales ; contrat de fin de ticket.",
        "",
        ("Blocs communs à recopier à la fin de chaque ticket PR/EX "
        "(`python -m app.v1.ampcr_pratique_tickets PR07` produit un ticket complet) :"),
        "",
        _demote(TRANSVERSAL_RULES),
        "",
        _demote(END_CONTRACT),
        "",
        "## 3. Checklist de validation éditoriale et visuelle",
        "",
        CHECKLIST,
        "",
        "## 4. Amorces des 36 tickets",
        "",
    ]
    for module in plan.MODULES:
        parts += [f"### Module {module.key} — {module.title}", ""]
        for code in module.course_codes:
            parts += [_demote(course_ticket(code, full=False)), ""]
        parts += [_demote(exam_ticket(module.exercise_code, full=False)), ""]
    return "\n".join(parts).rstrip() + "\n"


def _demote(markdown: str) -> str:
    """Décale les titres d'un niveau pour l'intégration dans le document complet."""
    return "\n".join(
        "##" + line if line.startswith("#") else line for line in markdown.splitlines()
    )


def main() -> None:
    if len(sys.argv) > 1:
        code = sys.argv[1].upper()
        if code in plan.COURSE_SLOTS_BY_CODE:
            print(course_ticket(code))
        elif code in plan.EXERCISE_SLOTS_BY_CODE:
            print(exam_ticket(code))
        else:
            sys.exit(f"Code inconnu : {code} (PR01–PR30 ou EX01–EX06).")
        return
    sys.stdout.write(render_document())


if __name__ == "__main__":
    main()
