# AMPCR — Pratique écrite : modèles de tickets PR01–PR30 et EX01–EX06 (ticket #192)

Document généré par `python -m app.v1.ampcr_pratique_tickets` depuis le plan (`app/v1/ampcr_pratique_plan.py`) ; ne pas l'éditer à la main.

## 1. Mode d'emploi

1. Le propriétaire crée un ticket GitHub par cours (PR) ou examen de module (EX), en copiant l'amorce correspondante du § 4 et en **rédigeant la matière** dans les sections « À compléter ». Les tickets #193 (PR06), #194 (PR11) et #197 (PR15) sont les références de niveau de détail attendu.
2. Titre : `[P0][AMPCR pratique PRxx] …` ou `[P0][AMPCR pratique EXxx] …` (priorité au choix du propriétaire) ; l'orchestrateur traite les tickets par priorité puis ancienneté.
3. Un EX dépend des PR de son module ; une session qui reçoit un EX avant ses PR rend `READY` avec la dépendance.
4. Si le titre ou le périmètre d'un ticket diffère du plan, **le ticket fait foi** : la session réaligne le plan et la matrice dans la même PR.
5. Livraison incrémentale : chaque cours est publié dès qu'il est complet, sans attendre le module entier.

## 2. Gabarit commun

Un ticket de cours contient, dans cet ordre : en-tête (parcours, module, examen du module, socle) ; exigences officielles couvertes (texte exact) ; théorie existante ; objectifs observables ; matière obligatoire — à enseigner explicitement ; compléments autorisés ; supports visuels exigés ; pédagogie, cas et exercices ; critères d'acceptation spécifiques ; exigences transversales ; contrat de fin de ticket.

Un ticket d'examen contient : en-tête et dépendances ; exigences à évaluer ; composition de l'examen ; exercices et documents ; supports visuels exigés ; critères d'acceptation spécifiques ; exigences transversales ; contrat de fin de ticket.

Blocs communs à recopier à la fin de chaque ticket PR/EX (`python -m app.v1.ampcr_pratique_tickets PR07` produit un ticket complet) :

##### Exigences transversales (ticket socle #192 — rappel obligatoire)
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
- **Checklist** : `docs/ampcr_pratique_tickets.md` § 3, cochée dans le rapport.

##### Contrat de fin de ticket (obligatoire, même bloqué)
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
   ticket après validation.

## 3. Checklist de validation éditoriale et visuelle

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
- [ ] Rapport, email (via l'orchestrateur) et commentaire GitHub faits.

## 4. Amorces des 36 tickets

### Module P1 — Matériel du PC

#### [P0][AMPCR pratique PR01] Structure d'un ordinateur, composants et périphériques

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P1 — Matériel du PC · **examen du module** EX01 · **socle** #192.

##### Exigences officielles couvertes (matrice #192)
- **AP-01** (p. 5) — « La structure d’un ordinateur, ses composants et ses périphériques. »
- **AP-02** (p. 5) — « Les différents éléments qui peuvent constituer un ordinateur (Processeur, mémoire RAM-ROM, carte mère, BIOS, UEFI, etc.). »

**Théorie existante à réutiliser** : MC01, MC02, MC03, MC07.

##### Objectifs observables
_À compléter — Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, décrire une procédure, interpréter un document, diagnostiquer, justifier)._

##### Matière obligatoire — à enseigner explicitement
_À compléter — Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs fréquentes ; diagnostics ; cas pratiques._

##### Compléments autorisés
_À compléter — Explications, techniques actuelles, exercices ou illustrations que la session peut ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la matière obligatoire._

##### Supports visuels exigés
_À compléter — Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration générée par API / tableau / capture fictive identifiée comme telle), données de référence, orientation de lecture, légende et texte alternatif attendus._

##### Pédagogie, cas et exercices
_À compléter — Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur répartition (procédures écrites, analyses de documents, choix justifiés) ; mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée avant soumission, barème détaillé)._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [P0][AMPCR pratique PR02] Carte mère, processeur, mémoire RAM-ROM, BIOS et UEFI

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P1 — Matériel du PC · **examen du module** EX01 · **socle** #192.

##### Exigences officielles couvertes (matrice #192)
- **AP-02** (p. 5) — « Les différents éléments qui peuvent constituer un ordinateur (Processeur, mémoire RAM-ROM, carte mère, BIOS, UEFI, etc.). »
- **AP-07** (p. 5) — « La carte mère et ses éléments constitutifs. »

**Théorie existante à réutiliser** : MC01, MC02, MC03, MC07.

##### Objectifs observables
_À compléter — Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, décrire une procédure, interpréter un document, diagnostiquer, justifier)._

##### Matière obligatoire — à enseigner explicitement
_À compléter — Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs fréquentes ; diagnostics ; cas pratiques._

##### Compléments autorisés
_À compléter — Explications, techniques actuelles, exercices ou illustrations que la session peut ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la matière obligatoire._

##### Supports visuels exigés
_À compléter — Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration générée par API / tableau / capture fictive identifiée comme telle), données de référence, orientation de lecture, légende et texte alternatif attendus._

##### Pédagogie, cas et exercices
_À compléter — Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur répartition (procédures écrites, analyses de documents, choix justifiés) ; mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée avant soumission, barème détaillé)._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [P0][AMPCR pratique PR03] Disques, unités de stockage, formatage et défragmentation

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P1 — Matériel du PC · **examen du module** EX01 · **socle** #192.

##### Exigences officielles couvertes (matrice #192)
- **AP-03** (p. 5) — « Les différents types de disque dur et unités de stockage, le formatage, la défragmentation. »

**Théorie existante à réutiliser** : MC04, MC08.

##### Objectifs observables
_À compléter — Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, décrire une procédure, interpréter un document, diagnostiquer, justifier)._

##### Matière obligatoire — à enseigner explicitement
_À compléter — Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs fréquentes ; diagnostics ; cas pratiques._

##### Compléments autorisés
_À compléter — Explications, techniques actuelles, exercices ou illustrations que la session peut ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la matière obligatoire._

##### Supports visuels exigés
_À compléter — Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration générée par API / tableau / capture fictive identifiée comme telle), données de référence, orientation de lecture, légende et texte alternatif attendus._

##### Pédagogie, cas et exercices
_À compléter — Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur répartition (procédures écrites, analyses de documents, choix justifiés) ; mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée avant soumission, barème détaillé)._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [P0][AMPCR pratique PR04] Caractéristiques d'une alimentation PC

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P1 — Matériel du PC · **examen du module** EX01 · **socle** #192.

##### Exigences officielles couvertes (matrice #192)
- **AP-04** (p. 5) — « Les caractéristiques d’une alimentation PC. »

**Théorie existante à réutiliser** : MC05.

##### Objectifs observables
_À compléter — Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, décrire une procédure, interpréter un document, diagnostiquer, justifier)._

##### Matière obligatoire — à enseigner explicitement
_À compléter — Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs fréquentes ; diagnostics ; cas pratiques._

##### Compléments autorisés
_À compléter — Explications, techniques actuelles, exercices ou illustrations que la session peut ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la matière obligatoire._

##### Supports visuels exigés
_À compléter — Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration générée par API / tableau / capture fictive identifiée comme telle), données de référence, orientation de lecture, légende et texte alternatif attendus._

##### Pédagogie, cas et exercices
_À compléter — Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur répartition (procédures écrites, analyses de documents, choix justifiés) ; mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée avant soumission, barème détaillé)._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [P0][AMPCR pratique PR05] Branchements, interfaces, connexions et compatibilité

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P1 — Matériel du PC · **examen du module** EX01 · **socle** #192.

##### Exigences officielles couvertes (matrice #192)
- **AP-06** (p. 5) — « Branchements, interfaces et connexions. »
- **AP-17** (p. 5) — « Notion de compatibilité. »

**Théorie existante à réutiliser** : MC02, MC04, MC12.

##### Objectifs observables
_À compléter — Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, décrire une procédure, interpréter un document, diagnostiquer, justifier)._

##### Matière obligatoire — à enseigner explicitement
_À compléter — Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs fréquentes ; diagnostics ; cas pratiques._

##### Compléments autorisés
_À compléter — Explications, techniques actuelles, exercices ou illustrations que la session peut ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la matière obligatoire._

##### Supports visuels exigés
_À compléter — Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration générée par API / tableau / capture fictive identifiée comme telle), données de référence, orientation de lecture, légende et texte alternatif attendus._

##### Pédagogie, cas et exercices
_À compléter — Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur répartition (procédures écrites, analyses de documents, choix justifiés) ; mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée avant soumission, barème détaillé)._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [P0][AMPCR pratique EX01] Examen écrit du module P1 — Matériel du PC

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **socle** #192 · **cours du module** PR01, PR02, PR03, PR04, PR05 (dépendances : leurs tickets doivent être livrés avant).

##### Exigences à évaluer (matrice #192)
- **AP-01** (p. 5) — « La structure d’un ordinateur, ses composants et ses périphériques. »
- **AP-02** (p. 5) — « Les différents éléments qui peuvent constituer un ordinateur (Processeur, mémoire RAM-ROM, carte mère, BIOS, UEFI, etc.). »
- **AP-03** (p. 5) — « Les différents types de disque dur et unités de stockage, le formatage, la défragmentation. »
- **AP-04** (p. 5) — « Les caractéristiques d’une alimentation PC. »
- **AP-06** (p. 5) — « Branchements, interfaces et connexions. »
- **AP-07** (p. 5) — « La carte mère et ses éléments constitutifs. »
- **AP-17** (p. 5) — « Notion de compatibilité. »

Une exigence passe à « validé » dans la matrice (`VALIDATED_REQUIREMENT_IDS`) seulement quand ses cours ET cet examen sont publiés et relus.

##### Composition de l'examen
_À compléter — Nombre d'exercices, points par exercice, total /20 ; chaque exigence AP du module évaluée au moins une fois. Aucune durée inventée (les consignes n'en fixent pas)._

##### Exercices et documents
_À compléter — Pour chaque exercice : situation, documents/schémas fournis, consignes numérotées, réponse libre, barème par critère, correction justifiée (format `/ampcr-pratique/format-exercice`)._

##### Supports visuels exigés
_À compléter — Schémas et documents à produire, avec leurs données de référence._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

### Module P2 — Intervention et dépannage matériel

#### [P0][AMPCR pratique PR06] Diagnostic des pannes matérielles

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P2 — Intervention et dépannage matériel · **examen du module** EX02 · **socle** #192.
**Ticket déjà rédigé : #193** (il fait foi).

##### Exigences officielles couvertes (matrice #192)
- **AP-15** (p. 5) — « Dépannage sur les dysfonctionnements courants (hardware ou software). »
- **AP-17** (p. 5) — « Notion de compatibilité. »
- **AP-C02** (complément pédagogique) — « Sécurité électrique et protection ESD lors d'une intervention sur un PC. » _Note : Prérequis des interventions de montage/démontage (AP-14)._

**Théorie existante à réutiliser** : MC04, MC05, MC12, MC29, MC30.

##### Objectifs observables
_À compléter — Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, décrire une procédure, interpréter un document, diagnostiquer, justifier)._

##### Matière obligatoire — à enseigner explicitement
_À compléter — Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs fréquentes ; diagnostics ; cas pratiques._

##### Compléments autorisés
_À compléter — Explications, techniques actuelles, exercices ou illustrations que la session peut ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la matière obligatoire._

##### Supports visuels exigés
_À compléter — Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration générée par API / tableau / capture fictive identifiée comme telle), données de référence, orientation de lecture, légende et texte alternatif attendus._

##### Pédagogie, cas et exercices
_À compléter — Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur répartition (procédures écrites, analyses de documents, choix justifiés) ; mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée avant soumission, barème détaillé)._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [P0][AMPCR pratique PR07] Montage et démontage d'un PC en sécurité

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P2 — Intervention et dépannage matériel · **examen du module** EX02 · **socle** #192.

##### Exigences officielles couvertes (matrice #192)
- **AP-14** (p. 5) — « Montage, démontage et reconditionnement d’un PC. »
- **AP-C02** (complément pédagogique) — « Sécurité électrique et protection ESD lors d'une intervention sur un PC. » _Note : Prérequis des interventions de montage/démontage (AP-14)._

**Théorie existante à réutiliser** : MC05, MC06.

##### Objectifs observables
_À compléter — Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, décrire une procédure, interpréter un document, diagnostiquer, justifier)._

##### Matière obligatoire — à enseigner explicitement
_À compléter — Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs fréquentes ; diagnostics ; cas pratiques._

##### Compléments autorisés
_À compléter — Explications, techniques actuelles, exercices ou illustrations que la session peut ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la matière obligatoire._

##### Supports visuels exigés
_À compléter — Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration générée par API / tableau / capture fictive identifiée comme telle), données de référence, orientation de lecture, légende et texte alternatif attendus._

##### Pédagogie, cas et exercices
_À compléter — Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur répartition (procédures écrites, analyses de documents, choix justifiés) ; mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée avant soumission, barème détaillé)._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [P0][AMPCR pratique PR08] Reconditionnement d'un PC

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P2 — Intervention et dépannage matériel · **examen du module** EX02 · **socle** #192.

##### Exigences officielles couvertes (matrice #192)
- **AP-14** (p. 5) — « Montage, démontage et reconditionnement d’un PC. »
- **AP-17** (p. 5) — « Notion de compatibilité. »

**Théorie existante à réutiliser** : MC04, MC06, MC12.

##### Objectifs observables
_À compléter — Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, décrire une procédure, interpréter un document, diagnostiquer, justifier)._

##### Matière obligatoire — à enseigner explicitement
_À compléter — Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs fréquentes ; diagnostics ; cas pratiques._

##### Compléments autorisés
_À compléter — Explications, techniques actuelles, exercices ou illustrations que la session peut ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la matière obligatoire._

##### Supports visuels exigés
_À compléter — Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration générée par API / tableau / capture fictive identifiée comme telle), données de référence, orientation de lecture, légende et texte alternatif attendus._

##### Pédagogie, cas et exercices
_À compléter — Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur répartition (procédures écrites, analyses de documents, choix justifiés) ; mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée avant soumission, barème détaillé)._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [P0][AMPCR pratique EX02] Examen écrit du module P2 — Intervention et dépannage matériel

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **socle** #192 · **cours du module** PR06, PR07, PR08 (dépendances : leurs tickets doivent être livrés avant).

##### Exigences à évaluer (matrice #192)
- **AP-14** (p. 5) — « Montage, démontage et reconditionnement d’un PC. »
- **AP-15** (p. 5) — « Dépannage sur les dysfonctionnements courants (hardware ou software). »
- **AP-17** (p. 5) — « Notion de compatibilité. »
- **AP-C02** (complément pédagogique) — « Sécurité électrique et protection ESD lors d'une intervention sur un PC. » _Note : Prérequis des interventions de montage/démontage (AP-14)._

Une exigence passe à « validé » dans la matrice (`VALIDATED_REQUIREMENT_IDS`) seulement quand ses cours ET cet examen sont publiés et relus.

##### Composition de l'examen
_À compléter — Nombre d'exercices, points par exercice, total /20 ; chaque exigence AP du module évaluée au moins une fois. Aucune durée inventée (les consignes n'en fixent pas)._

##### Exercices et documents
_À compléter — Pour chaque exercice : situation, documents/schémas fournis, consignes numérotées, réponse libre, barème par critère, correction justifiée (format `/ampcr-pratique/format-exercice`)._

##### Supports visuels exigés
_À compléter — Schémas et documents à produire, avec leurs données de référence._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

### Module P3 — Systèmes d'exploitation et messages d'erreur

#### [P0][AMPCR pratique PR09] Systèmes d'exploitation actuellement sur le marché

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P3 — Systèmes d'exploitation et messages d'erreur · **examen du module** EX03 · **socle** #192.

##### Exigences officielles couvertes (matrice #192)
- **AP-08** (p. 5) — « Les différents systèmes d’exploitation actuellement sur le marché. »

**Théorie existante à réutiliser** : MC09, MC11.

##### Objectifs observables
_À compléter — Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, décrire une procédure, interpréter un document, diagnostiquer, justifier)._

##### Matière obligatoire — à enseigner explicitement
_À compléter — Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs fréquentes ; diagnostics ; cas pratiques._

##### Compléments autorisés
_À compléter — Explications, techniques actuelles, exercices ou illustrations que la session peut ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la matière obligatoire._

##### Supports visuels exigés
_À compléter — Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration générée par API / tableau / capture fictive identifiée comme telle), données de référence, orientation de lecture, légende et texte alternatif attendus._

##### Pédagogie, cas et exercices
_À compléter — Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur répartition (procédures écrites, analyses de documents, choix justifiés) ; mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée avant soumission, barème détaillé)._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [P0][AMPCR pratique PR10] Installation complète d'un système d'exploitation courant

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P3 — Systèmes d'exploitation et messages d'erreur · **examen du module** EX03 · **socle** #192.

##### Exigences officielles couvertes (matrice #192)
- **AP-10** (p. 5) — « Installation complète des différents systèmes d’exploitation courants. »

**Théorie existante à réutiliser** : MC08, MC09.

##### Objectifs observables
_À compléter — Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, décrire une procédure, interpréter un document, diagnostiquer, justifier)._

##### Matière obligatoire — à enseigner explicitement
_À compléter — Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs fréquentes ; diagnostics ; cas pratiques._

##### Compléments autorisés
_À compléter — Explications, techniques actuelles, exercices ou illustrations que la session peut ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la matière obligatoire._

##### Supports visuels exigés
_À compléter — Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration générée par API / tableau / capture fictive identifiée comme telle), données de référence, orientation de lecture, légende et texte alternatif attendus._

##### Pédagogie, cas et exercices
_À compléter — Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur répartition (procédures écrites, analyses de documents, choix justifiés) ; mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée avant soumission, barème détaillé)._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [P0][AMPCR pratique PR11] Messages d'erreur Windows/Linux et démarches d'intervention

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P3 — Systèmes d'exploitation et messages d'erreur · **examen du module** EX03 · **socle** #192.
**Ticket déjà rédigé : #194** (il fait foi).

##### Exigences officielles couvertes (matrice #192)
- **AP-09** (p. 5) — « Les principaux messages d’erreurs, l’interprétation et les démarches d’intervention y afférant. » _Note : Proche de AP-13 (les deux puces figurent au PDF)._
- **AP-13** (p. 5) — « Connaître les principaux messages d’erreurs, comment interpréter ceux-ci et comment intervenir si possible. » _Note : Proche de AP-09 (les deux puces figurent au PDF)._
- **AP-15** (p. 5) — « Dépannage sur les dysfonctionnements courants (hardware ou software). »

**Théorie existante à réutiliser** : MC07, MC29, MC30.

##### Objectifs observables
_À compléter — Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, décrire une procédure, interpréter un document, diagnostiquer, justifier)._

##### Matière obligatoire — à enseigner explicitement
_À compléter — Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs fréquentes ; diagnostics ; cas pratiques._

##### Compléments autorisés
_À compléter — Explications, techniques actuelles, exercices ou illustrations que la session peut ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la matière obligatoire._

##### Supports visuels exigés
_À compléter — Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration générée par API / tableau / capture fictive identifiée comme telle), données de référence, orientation de lecture, légende et texte alternatif attendus._

##### Pédagogie, cas et exercices
_À compléter — Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur répartition (procédures écrites, analyses de documents, choix justifiés) ; mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée avant soumission, barème détaillé)._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [P0][AMPCR pratique PR12] Paramètres et commandes de base

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P3 — Systèmes d'exploitation et messages d'erreur · **examen du module** EX03 · **socle** #192.

##### Exigences officielles couvertes (matrice #192)
- **AP-11** (p. 5) — « Paramètres et commandes de base des systèmes d'exploitation courants. »

**Théorie existante à réutiliser** : MC10, MC11.

##### Objectifs observables
_À compléter — Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, décrire une procédure, interpréter un document, diagnostiquer, justifier)._

##### Matière obligatoire — à enseigner explicitement
_À compléter — Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs fréquentes ; diagnostics ; cas pratiques._

##### Compléments autorisés
_À compléter — Explications, techniques actuelles, exercices ou illustrations que la session peut ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la matière obligatoire._

##### Supports visuels exigés
_À compléter — Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration générée par API / tableau / capture fictive identifiée comme telle), données de référence, orientation de lecture, légende et texte alternatif attendus._

##### Pédagogie, cas et exercices
_À compléter — Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur répartition (procédures écrites, analyses de documents, choix justifiés) ; mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée avant soumission, barème détaillé)._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [P0][AMPCR pratique PR13] Interface graphique et interface de ligne de commande

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P3 — Systèmes d'exploitation et messages d'erreur · **examen du module** EX03 · **socle** #192.

##### Exigences officielles couvertes (matrice #192)
- **AP-12** (p. 5) — « Interface graphique et interface de ligne de commande. »

**Théorie existante à réutiliser** : MC10, MC11.

##### Objectifs observables
_À compléter — Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, décrire une procédure, interpréter un document, diagnostiquer, justifier)._

##### Matière obligatoire — à enseigner explicitement
_À compléter — Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs fréquentes ; diagnostics ; cas pratiques._

##### Compléments autorisés
_À compléter — Explications, techniques actuelles, exercices ou illustrations que la session peut ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la matière obligatoire._

##### Supports visuels exigés
_À compléter — Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration générée par API / tableau / capture fictive identifiée comme telle), données de référence, orientation de lecture, légende et texte alternatif attendus._

##### Pédagogie, cas et exercices
_À compléter — Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur répartition (procédures écrites, analyses de documents, choix justifiés) ; mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée avant soumission, barème détaillé)._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [P0][AMPCR pratique PR14] Périphériques d'entrée et de sortie, rôle d'un pilote

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P3 — Systèmes d'exploitation et messages d'erreur · **examen du module** EX03 · **socle** #192.

##### Exigences officielles couvertes (matrice #192)
- **AP-05** (p. 5) — « Les périphériques d’entrée et de sortie et le rôle d'un pilote. »
- **AP-17** (p. 5) — « Notion de compatibilité. »

**Théorie existante à réutiliser** : MC04, MC12.

##### Objectifs observables
_À compléter — Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, décrire une procédure, interpréter un document, diagnostiquer, justifier)._

##### Matière obligatoire — à enseigner explicitement
_À compléter — Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs fréquentes ; diagnostics ; cas pratiques._

##### Compléments autorisés
_À compléter — Explications, techniques actuelles, exercices ou illustrations que la session peut ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la matière obligatoire._

##### Supports visuels exigés
_À compléter — Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration générée par API / tableau / capture fictive identifiée comme telle), données de référence, orientation de lecture, légende et texte alternatif attendus._

##### Pédagogie, cas et exercices
_À compléter — Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur répartition (procédures écrites, analyses de documents, choix justifiés) ; mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée avant soumission, barème détaillé)._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [P0][AMPCR pratique EX03] Examen écrit du module P3 — Systèmes d'exploitation et messages d'erreur

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **socle** #192 · **cours du module** PR09, PR10, PR11, PR12, PR13, PR14 (dépendances : leurs tickets doivent être livrés avant).

##### Exigences à évaluer (matrice #192)
- **AP-05** (p. 5) — « Les périphériques d’entrée et de sortie et le rôle d'un pilote. »
- **AP-08** (p. 5) — « Les différents systèmes d’exploitation actuellement sur le marché. »
- **AP-09** (p. 5) — « Les principaux messages d’erreurs, l’interprétation et les démarches d’intervention y afférant. » _Note : Proche de AP-13 (les deux puces figurent au PDF)._
- **AP-10** (p. 5) — « Installation complète des différents systèmes d’exploitation courants. »
- **AP-11** (p. 5) — « Paramètres et commandes de base des systèmes d'exploitation courants. »
- **AP-12** (p. 5) — « Interface graphique et interface de ligne de commande. »
- **AP-13** (p. 5) — « Connaître les principaux messages d’erreurs, comment interpréter ceux-ci et comment intervenir si possible. » _Note : Proche de AP-09 (les deux puces figurent au PDF)._
- **AP-15** (p. 5) — « Dépannage sur les dysfonctionnements courants (hardware ou software). »
- **AP-17** (p. 5) — « Notion de compatibilité. »

Une exigence passe à « validé » dans la matrice (`VALIDATED_REQUIREMENT_IDS`) seulement quand ses cours ET cet examen sont publiés et relus.

##### Composition de l'examen
_À compléter — Nombre d'exercices, points par exercice, total /20 ; chaque exigence AP du module évaluée au moins une fois. Aucune durée inventée (les consignes n'en fixent pas)._

##### Exercices et documents
_À compléter — Pour chaque exercice : situation, documents/schémas fournis, consignes numérotées, réponse libre, barème par critère, correction justifiée (format `/ampcr-pratique/format-exercice`)._

##### Supports visuels exigés
_À compléter — Schémas et documents à produire, avec leurs données de référence._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

### Module P4 — Câbles et supports de transmission

#### [P0][AMPCR pratique PR15] Câblage RJ45, normes T568A/B, réalisation et tests

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P4 — Câbles et supports de transmission · **examen du module** EX04 · **socle** #192.
**Ticket déjà rédigé : #197** (il fait foi).

##### Exigences officielles couvertes (matrice #192)
- **AP-18** (p. 5) — « Les différents types de câbles : UTP, FTP, STP, Coax. » _Note : FTP et coaxial absents de la théorie actuelle._
- **AP-20** (p. 6) — « Les caractéristiques des câbles : atténuation, notion d’impédance, sensibilité aux parasites, blindage, précautions d’utilisation, les avantages, les inconvénients des uns par rapport aux autres, la longueur maximale d’un tronçon suivant le débit, les connecteurs, etc. » _Note : Atténuation et impédance absentes de la théorie actuelle._
- **AP-34** (p. 6) — « Description de la réalisation d’un câble avec connecteurs RJ45 (code des couleurs). »

**Théorie existante à réutiliser** : MC15.

##### Objectifs observables
_À compléter — Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, décrire une procédure, interpréter un document, diagnostiquer, justifier)._

##### Matière obligatoire — à enseigner explicitement
_À compléter — Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs fréquentes ; diagnostics ; cas pratiques._

##### Compléments autorisés
_À compléter — Explications, techniques actuelles, exercices ou illustrations que la session peut ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la matière obligatoire._

##### Supports visuels exigés
_À compléter — Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration générée par API / tableau / capture fictive identifiée comme telle), données de référence, orientation de lecture, légende et texte alternatif attendus._

##### Pédagogie, cas et exercices
_À compléter — Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur répartition (procédures écrites, analyses de documents, choix justifiés) ; mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée avant soumission, barème détaillé)._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [P0][AMPCR pratique PR16] Types de câbles et débits : UTP, FTP, STP, coaxial

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P4 — Câbles et supports de transmission · **examen du module** EX04 · **socle** #192.

##### Exigences officielles couvertes (matrice #192)
- **AP-18** (p. 5) — « Les différents types de câbles : UTP, FTP, STP, Coax. » _Note : FTP et coaxial absents de la théorie actuelle._
- **AP-19** (p. 6) — « Les débits binaires des câbles. »

**Théorie existante à réutiliser** : MC15.

##### Objectifs observables
_À compléter — Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, décrire une procédure, interpréter un document, diagnostiquer, justifier)._

##### Matière obligatoire — à enseigner explicitement
_À compléter — Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs fréquentes ; diagnostics ; cas pratiques._

##### Compléments autorisés
_À compléter — Explications, techniques actuelles, exercices ou illustrations que la session peut ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la matière obligatoire._

##### Supports visuels exigés
_À compléter — Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration générée par API / tableau / capture fictive identifiée comme telle), données de référence, orientation de lecture, légende et texte alternatif attendus._

##### Pédagogie, cas et exercices
_À compléter — Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur répartition (procédures écrites, analyses de documents, choix justifiés) ; mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée avant soumission, barème détaillé)._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [P0][AMPCR pratique PR17] Caractéristiques des câbles : atténuation, impédance, parasites, longueurs

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P4 — Câbles et supports de transmission · **examen du module** EX04 · **socle** #192.

##### Exigences officielles couvertes (matrice #192)
- **AP-20** (p. 6) — « Les caractéristiques des câbles : atténuation, notion d’impédance, sensibilité aux parasites, blindage, précautions d’utilisation, les avantages, les inconvénients des uns par rapport aux autres, la longueur maximale d’un tronçon suivant le débit, les connecteurs, etc. » _Note : Atténuation et impédance absentes de la théorie actuelle._

**Théorie existante à réutiliser** : MC15.

##### Objectifs observables
_À compléter — Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, décrire une procédure, interpréter un document, diagnostiquer, justifier)._

##### Matière obligatoire — à enseigner explicitement
_À compléter — Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs fréquentes ; diagnostics ; cas pratiques._

##### Compléments autorisés
_À compléter — Explications, techniques actuelles, exercices ou illustrations que la session peut ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la matière obligatoire._

##### Supports visuels exigés
_À compléter — Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration générée par API / tableau / capture fictive identifiée comme telle), données de référence, orientation de lecture, légende et texte alternatif attendus._

##### Pédagogie, cas et exercices
_À compléter — Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur répartition (procédures écrites, analyses de documents, choix justifiés) ; mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée avant soumission, barème détaillé)._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [P0][AMPCR pratique PR18] La fibre optique et sa comparaison avec les câbles

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P4 — Câbles et supports de transmission · **examen du module** EX04 · **socle** #192.

##### Exigences officielles couvertes (matrice #192)
- **AP-21** (p. 6) — « La fibre optique et ses caractéristiques : support d’information, débit binaire, longueur d’un tronçon, notion d’atténuation, connexion, avantages et inconvénients, etc. » _Note : La théorie actuelle ne fait que citer la fibre._
- **AP-22** (p. 6) — « Comparaison entre la fibre optique et les autres types de câbles. » _Note : Aucune théorie existante._

**Théorie existante à réutiliser** : MC14.

##### Objectifs observables
_À compléter — Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, décrire une procédure, interpréter un document, diagnostiquer, justifier)._

##### Matière obligatoire — à enseigner explicitement
_À compléter — Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs fréquentes ; diagnostics ; cas pratiques._

##### Compléments autorisés
_À compléter — Explications, techniques actuelles, exercices ou illustrations que la session peut ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la matière obligatoire._

##### Supports visuels exigés
_À compléter — Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration générée par API / tableau / capture fictive identifiée comme telle), données de référence, orientation de lecture, légende et texte alternatif attendus._

##### Pédagogie, cas et exercices
_À compléter — Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur répartition (procédures écrites, analyses de documents, choix justifiés) ; mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée avant soumission, barème détaillé)._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [P0][AMPCR pratique PR19] Réaliser un câble à connecteurs BNC

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P4 — Câbles et supports de transmission · **examen du module** EX04 · **socle** #192.

##### Exigences officielles couvertes (matrice #192)
- **AP-35** (p. 6) — « Description de la réalisation d’un câble avec connecteurs BNC. » _Note : Aucune théorie existante._

**Théorie existante à réutiliser** : aucune (notion absente des MC publiés).

##### Objectifs observables
_À compléter — Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, décrire une procédure, interpréter un document, diagnostiquer, justifier)._

##### Matière obligatoire — à enseigner explicitement
_À compléter — Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs fréquentes ; diagnostics ; cas pratiques._

##### Compléments autorisés
_À compléter — Explications, techniques actuelles, exercices ou illustrations que la session peut ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la matière obligatoire._

##### Supports visuels exigés
_À compléter — Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration générée par API / tableau / capture fictive identifiée comme telle), données de référence, orientation de lecture, légende et texte alternatif attendus._

##### Pédagogie, cas et exercices
_À compléter — Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur répartition (procédures écrites, analyses de documents, choix justifiés) ; mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée avant soumission, barème détaillé)._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [P0][AMPCR pratique EX04] Examen écrit du module P4 — Câbles et supports de transmission

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **socle** #192 · **cours du module** PR15, PR16, PR17, PR18, PR19 (dépendances : leurs tickets doivent être livrés avant).

##### Exigences à évaluer (matrice #192)
- **AP-18** (p. 5) — « Les différents types de câbles : UTP, FTP, STP, Coax. » _Note : FTP et coaxial absents de la théorie actuelle._
- **AP-19** (p. 6) — « Les débits binaires des câbles. »
- **AP-20** (p. 6) — « Les caractéristiques des câbles : atténuation, notion d’impédance, sensibilité aux parasites, blindage, précautions d’utilisation, les avantages, les inconvénients des uns par rapport aux autres, la longueur maximale d’un tronçon suivant le débit, les connecteurs, etc. » _Note : Atténuation et impédance absentes de la théorie actuelle._
- **AP-21** (p. 6) — « La fibre optique et ses caractéristiques : support d’information, débit binaire, longueur d’un tronçon, notion d’atténuation, connexion, avantages et inconvénients, etc. » _Note : La théorie actuelle ne fait que citer la fibre._
- **AP-22** (p. 6) — « Comparaison entre la fibre optique et les autres types de câbles. » _Note : Aucune théorie existante._
- **AP-34** (p. 6) — « Description de la réalisation d’un câble avec connecteurs RJ45 (code des couleurs). »
- **AP-35** (p. 6) — « Description de la réalisation d’un câble avec connecteurs BNC. » _Note : Aucune théorie existante._

Une exigence passe à « validé » dans la matrice (`VALIDATED_REQUIREMENT_IDS`) seulement quand ses cours ET cet examen sont publiés et relus.

##### Composition de l'examen
_À compléter — Nombre d'exercices, points par exercice, total /20 ; chaque exigence AP du module évaluée au moins une fois. Aucune durée inventée (les consignes n'en fixent pas)._

##### Exercices et documents
_À compléter — Pour chaque exercice : situation, documents/schémas fournis, consignes numérotées, réponse libre, barème par critère, correction justifiée (format `/ampcr-pratique/format-exercice`)._

##### Supports visuels exigés
_À compléter — Schémas et documents à produire, avec leurs données de référence._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

### Module P5 — Réseau : architecture et adressage

#### [P0][AMPCR pratique PR20] Topologies, câblage et installation physique d'un réseau

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P5 — Réseau : architecture et adressage · **examen du module** EX05 · **socle** #192.

##### Exigences officielles couvertes (matrice #192)
- **AP-23** (p. 6) — « Topologies de réseaux. »
- **AP-36** (p. 6) — « Câblage et installation physique d’un réseau informatique. »

**Théorie existante à réutiliser** : MC15, MC23.

##### Objectifs observables
_À compléter — Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, décrire une procédure, interpréter un document, diagnostiquer, justifier)._

##### Matière obligatoire — à enseigner explicitement
_À compléter — Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs fréquentes ; diagnostics ; cas pratiques._

##### Compléments autorisés
_À compléter — Explications, techniques actuelles, exercices ou illustrations que la session peut ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la matière obligatoire._

##### Supports visuels exigés
_À compléter — Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration générée par API / tableau / capture fictive identifiée comme telle), données de référence, orientation de lecture, légende et texte alternatif attendus._

##### Pédagogie, cas et exercices
_À compléter — Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur répartition (procédures écrites, analyses de documents, choix justifiés) ; mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée avant soumission, barème détaillé)._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [P0][AMPCR pratique PR21] Notions de base sur les protocoles

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P5 — Réseau : architecture et adressage · **examen du module** EX05 · **socle** #192.

##### Exigences officielles couvertes (matrice #192)
- **AP-29** (p. 6) — « Notions de base sur les protocoles (TCP/IP, OSI, NETBEUI…). » _Note : NetBEUI absent de la théorie actuelle._

**Théorie existante à réutiliser** : MC13, MC21.

##### Objectifs observables
_À compléter — Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, décrire une procédure, interpréter un document, diagnostiquer, justifier)._

##### Matière obligatoire — à enseigner explicitement
_À compléter — Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs fréquentes ; diagnostics ; cas pratiques._

##### Compléments autorisés
_À compléter — Explications, techniques actuelles, exercices ou illustrations que la session peut ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la matière obligatoire._

##### Supports visuels exigés
_À compléter — Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration générée par API / tableau / capture fictive identifiée comme telle), données de référence, orientation de lecture, légende et texte alternatif attendus._

##### Pédagogie, cas et exercices
_À compléter — Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur répartition (procédures écrites, analyses de documents, choix justifiés) ; mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée avant soumission, barème détaillé)._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [P0][AMPCR pratique PR22] Adressage IP et adresses MAC

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P5 — Réseau : architecture et adressage · **examen du module** EX05 · **socle** #192.

##### Exigences officielles couvertes (matrice #192)
- **AP-30** (p. 6) — « L’adressage IP, les adresses MAC, l’identification d’une adresse MAC et d’une adresse IP. »

**Théorie existante à réutiliser** : MC16, MC20.

##### Objectifs observables
_À compléter — Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, décrire une procédure, interpréter un document, diagnostiquer, justifier)._

##### Matière obligatoire — à enseigner explicitement
_À compléter — Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs fréquentes ; diagnostics ; cas pratiques._

##### Compléments autorisés
_À compléter — Explications, techniques actuelles, exercices ou illustrations que la session peut ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la matière obligatoire._

##### Supports visuels exigés
_À compléter — Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration générée par API / tableau / capture fictive identifiée comme telle), données de référence, orientation de lecture, légende et texte alternatif attendus._

##### Pédagogie, cas et exercices
_À compléter — Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur répartition (procédures écrites, analyses de documents, choix justifiés) ; mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée avant soumission, barème détaillé)._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [P0][AMPCR pratique PR23] Hub, switch, passerelle, routeur, modem

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P5 — Réseau : architecture et adressage · **examen du module** EX05 · **socle** #192.

##### Exigences officielles couvertes (matrice #192)
- **AP-31** (p. 6) — « Hub, switch, passerelle, routeur, modem. » _Note : Hub absent de la théorie actuelle._

**Théorie existante à réutiliser** : MC14.

##### Objectifs observables
_À compléter — Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, décrire une procédure, interpréter un document, diagnostiquer, justifier)._

##### Matière obligatoire — à enseigner explicitement
_À compléter — Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs fréquentes ; diagnostics ; cas pratiques._

##### Compléments autorisés
_À compléter — Explications, techniques actuelles, exercices ou illustrations que la session peut ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la matière obligatoire._

##### Supports visuels exigés
_À compléter — Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration générée par API / tableau / capture fictive identifiée comme telle), données de référence, orientation de lecture, légende et texte alternatif attendus._

##### Pédagogie, cas et exercices
_À compléter — Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur répartition (procédures écrites, analyses de documents, choix justifiés) ; mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée avant soumission, barème détaillé)._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [P0][AMPCR pratique PR24] Wi-Fi : principe, sécurisation, cryptage, répéteur

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P5 — Réseau : architecture et adressage · **examen du module** EX05 · **socle** #192.

##### Exigences officielles couvertes (matrice #192)
- **AP-33** (p. 6) — « WIFI : principe, sécurisation, cryptage, répéteur. » _Note : Répéteur absent de la théorie actuelle._

**Théorie existante à réutiliser** : MC25, MC26.

##### Objectifs observables
_À compléter — Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, décrire une procédure, interpréter un document, diagnostiquer, justifier)._

##### Matière obligatoire — à enseigner explicitement
_À compléter — Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs fréquentes ; diagnostics ; cas pratiques._

##### Compléments autorisés
_À compléter — Explications, techniques actuelles, exercices ou illustrations que la session peut ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la matière obligatoire._

##### Supports visuels exigés
_À compléter — Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration générée par API / tableau / capture fictive identifiée comme telle), données de référence, orientation de lecture, légende et texte alternatif attendus._

##### Pédagogie, cas et exercices
_À compléter — Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur répartition (procédures écrites, analyses de documents, choix justifiés) ; mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée avant soumission, barème détaillé)._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [P0][AMPCR pratique EX05] Examen écrit du module P5 — Réseau : architecture et adressage

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **socle** #192 · **cours du module** PR20, PR21, PR22, PR23, PR24 (dépendances : leurs tickets doivent être livrés avant).

##### Exigences à évaluer (matrice #192)
- **AP-23** (p. 6) — « Topologies de réseaux. »
- **AP-29** (p. 6) — « Notions de base sur les protocoles (TCP/IP, OSI, NETBEUI…). » _Note : NetBEUI absent de la théorie actuelle._
- **AP-30** (p. 6) — « L’adressage IP, les adresses MAC, l’identification d’une adresse MAC et d’une adresse IP. »
- **AP-31** (p. 6) — « Hub, switch, passerelle, routeur, modem. » _Note : Hub absent de la théorie actuelle._
- **AP-33** (p. 6) — « WIFI : principe, sécurisation, cryptage, répéteur. » _Note : Répéteur absent de la théorie actuelle._
- **AP-36** (p. 6) — « Câblage et installation physique d’un réseau informatique. »

Une exigence passe à « validé » dans la matrice (`VALIDATED_REQUIREMENT_IDS`) seulement quand ses cours ET cet examen sont publiés et relus.

##### Composition de l'examen
_À compléter — Nombre d'exercices, points par exercice, total /20 ; chaque exigence AP du module évaluée au moins une fois. Aucune durée inventée (les consignes n'en fixent pas)._

##### Exercices et documents
_À compléter — Pour chaque exercice : situation, documents/schémas fournis, consignes numérotées, réponse libre, barème par critère, correction justifiée (format `/ampcr-pratique/format-exercice`)._

##### Supports visuels exigés
_À compléter — Schémas et documents à produire, avec leurs données de référence._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

### Module P6 — Partages, comptes et dépannage réseau

#### [P0][AMPCR pratique PR25] Domaine, groupe de travail, comptes et groupes

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P6 — Partages, comptes et dépannage réseau · **examen du module** EX06 · **socle** #192.

##### Exigences officielles couvertes (matrice #192)
- **AP-24** (p. 6) — « Notions de domaine, groupe de travail, comptes utilisateurs et groupes d’utilisateurs. » _Note : Domaine / groupe de travail absents de la théorie actuelle._

**Théorie existante à réutiliser** : MC33.

##### Objectifs observables
_À compléter — Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, décrire une procédure, interpréter un document, diagnostiquer, justifier)._

##### Matière obligatoire — à enseigner explicitement
_À compléter — Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs fréquentes ; diagnostics ; cas pratiques._

##### Compléments autorisés
_À compléter — Explications, techniques actuelles, exercices ou illustrations que la session peut ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la matière obligatoire._

##### Supports visuels exigés
_À compléter — Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration générée par API / tableau / capture fictive identifiée comme telle), données de référence, orientation de lecture, légende et texte alternatif attendus._

##### Pédagogie, cas et exercices
_À compléter — Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur répartition (procédures écrites, analyses de documents, choix justifiés) ; mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée avant soumission, barème détaillé)._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [P0][AMPCR pratique PR26] Partages, droits et permissions

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P6 — Partages, comptes et dépannage réseau · **examen du module** EX06 · **socle** #192.

##### Exigences officielles couvertes (matrice #192)
- **AP-25** (p. 6) — « Partage de ressources (imprimantes, disques, répertoires…). »
- **AP-26** (p. 6) — « Mise en partage sur un réseau informatique de documents et applications. »
- **AP-27** (p. 6) — « Les notions de droit et de permission. »

**Théorie existante à réutiliser** : MC10, MC33.

##### Objectifs observables
_À compléter — Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, décrire une procédure, interpréter un document, diagnostiquer, justifier)._

##### Matière obligatoire — à enseigner explicitement
_À compléter — Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs fréquentes ; diagnostics ; cas pratiques._

##### Compléments autorisés
_À compléter — Explications, techniques actuelles, exercices ou illustrations que la session peut ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la matière obligatoire._

##### Supports visuels exigés
_À compléter — Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration générée par API / tableau / capture fictive identifiée comme telle), données de référence, orientation de lecture, légende et texte alternatif attendus._

##### Pédagogie, cas et exercices
_À compléter — Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur répartition (procédures écrites, analyses de documents, choix justifiés) ; mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée avant soumission, barème détaillé)._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [P0][AMPCR pratique PR27] Connexion directe et mini réseau entre plusieurs machines

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P6 — Partages, comptes et dépannage réseau · **examen du module** EX06 · **socle** #192.

##### Exigences officielles couvertes (matrice #192)
- **AP-28** (p. 6) — « Connexion de deux machines en direct. »
- **AP-38** (p. 6) — « Création d’un mini réseau entre plusieurs machines. »

**Théorie existante à réutiliser** : MC15, MC16, MC37.

##### Objectifs observables
_À compléter — Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, décrire une procédure, interpréter un document, diagnostiquer, justifier)._

##### Matière obligatoire — à enseigner explicitement
_À compléter — Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs fréquentes ; diagnostics ; cas pratiques._

##### Compléments autorisés
_À compléter — Explications, techniques actuelles, exercices ou illustrations que la session peut ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la matière obligatoire._

##### Supports visuels exigés
_À compléter — Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration générée par API / tableau / capture fictive identifiée comme telle), données de référence, orientation de lecture, légende et texte alternatif attendus._

##### Pédagogie, cas et exercices
_À compléter — Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur répartition (procédures écrites, analyses de documents, choix justifiés) ; mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée avant soumission, barème détaillé)._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [P0][AMPCR pratique PR28] Panne internet : connexions et interventions

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P6 — Partages, comptes et dépannage réseau · **examen du module** EX06 · **socle** #192.

##### Exigences officielles couvertes (matrice #192)
- **AP-32** (p. 6) — « Connexions et interventions en cas de panne internet. »

**Théorie existante à réutiliser** : MC22, MC31.

##### Objectifs observables
_À compléter — Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, décrire une procédure, interpréter un document, diagnostiquer, justifier)._

##### Matière obligatoire — à enseigner explicitement
_À compléter — Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs fréquentes ; diagnostics ; cas pratiques._

##### Compléments autorisés
_À compléter — Explications, techniques actuelles, exercices ou illustrations que la session peut ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la matière obligatoire._

##### Supports visuels exigés
_À compléter — Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration générée par API / tableau / capture fictive identifiée comme telle), données de référence, orientation de lecture, légende et texte alternatif attendus._

##### Pédagogie, cas et exercices
_À compléter — Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur répartition (procédures écrites, analyses de documents, choix justifiés) ; mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée avant soumission, barème détaillé)._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [P0][AMPCR pratique PR29] Dépannage de problèmes simples d'accès au réseau

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P6 — Partages, comptes et dépannage réseau · **examen du module** EX06 · **socle** #192.

##### Exigences officielles couvertes (matrice #192)
- **AP-37** (p. 6) — « Dépannage de problèmes simples d’accès au réseau. »

**Théorie existante à réutiliser** : MC31.

##### Objectifs observables
_À compléter — Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, décrire une procédure, interpréter un document, diagnostiquer, justifier)._

##### Matière obligatoire — à enseigner explicitement
_À compléter — Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs fréquentes ; diagnostics ; cas pratiques._

##### Compléments autorisés
_À compléter — Explications, techniques actuelles, exercices ou illustrations que la session peut ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la matière obligatoire._

##### Supports visuels exigés
_À compléter — Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration générée par API / tableau / capture fictive identifiée comme telle), données de référence, orientation de lecture, légende et texte alternatif attendus._

##### Pédagogie, cas et exercices
_À compléter — Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur répartition (procédures écrites, analyses de documents, choix justifiés) ; mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée avant soumission, barème détaillé)._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [P0][AMPCR pratique PR30] Vocabulaire technique et rédaction d'une intervention

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P6 — Partages, comptes et dépannage réseau · **examen du module** EX06 · **socle** #192.

##### Exigences officielles couvertes (matrice #192)
- **AP-16** (p. 5) — « Vocabulaire technique. » _Note : Transversal : lexique AMPCR existant._
- **AP-C01** (complément pédagogique) — « Rédiger une réponse écrite de technicien : décrire une intervention étape par étape et justifier chaque choix. » _Note : Méthode : l'épreuve pratique se fait uniquement par écrit (p. 3)._

**Théorie existante à réutiliser** : MC36.

##### Objectifs observables
_À compléter — Ce que le candidat sait faire **par écrit** à la fin du cours (identifier, choisir, décrire une procédure, interpréter un document, diagnostiquer, justifier)._

##### Matière obligatoire — à enseigner explicitement
_À compléter — Rédigée par le propriétaire, exhaustive et structurée, chaque partie rattachée à un id AP ci-dessus : définitions utiles ; principes ; composants et outils ; procédures détaillées ; valeurs et limites (avec leur source) ; prérequis ; sécurité ; erreurs fréquentes ; diagnostics ; cas pratiques._

##### Compléments autorisés
_À compléter — Explications, techniques actuelles, exercices ou illustrations que la session peut ajouter, **signalés comme compléments pédagogiques** ; jamais à la place de la matière obligatoire._

##### Supports visuels exigés
_À compléter — Liste numérotée : nature (schéma SVG construit sur données vérifiées / illustration générée par API / tableau / capture fictive identifiée comme telle), données de référence, orientation de lecture, légende et texte alternatif attendus._

##### Pédagogie, cas et exercices
_À compléter — Nombre de cas intégralement résolus ; nombre minimal d'exercices corrigés et leur répartition (procédures écrites, analyses de documents, choix justifiés) ; mini-examen du cours (ex. 10 questions notées /20, réponses libres, correction cachée avant soumission, barème détaillé)._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [P0][AMPCR pratique EX06] Examen écrit du module P6 — Partages, comptes et dépannage réseau

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **socle** #192 · **cours du module** PR25, PR26, PR27, PR28, PR29, PR30 (dépendances : leurs tickets doivent être livrés avant).

##### Exigences à évaluer (matrice #192)
- **AP-16** (p. 5) — « Vocabulaire technique. » _Note : Transversal : lexique AMPCR existant._
- **AP-24** (p. 6) — « Notions de domaine, groupe de travail, comptes utilisateurs et groupes d’utilisateurs. » _Note : Domaine / groupe de travail absents de la théorie actuelle._
- **AP-25** (p. 6) — « Partage de ressources (imprimantes, disques, répertoires…). »
- **AP-26** (p. 6) — « Mise en partage sur un réseau informatique de documents et applications. »
- **AP-27** (p. 6) — « Les notions de droit et de permission. »
- **AP-28** (p. 6) — « Connexion de deux machines en direct. »
- **AP-32** (p. 6) — « Connexions et interventions en cas de panne internet. »
- **AP-37** (p. 6) — « Dépannage de problèmes simples d’accès au réseau. »
- **AP-38** (p. 6) — « Création d’un mini réseau entre plusieurs machines. »
- **AP-C01** (complément pédagogique) — « Rédiger une réponse écrite de technicien : décrire une intervention étape par étape et justifier chaque choix. » _Note : Méthode : l'épreuve pratique se fait uniquement par écrit (p. 3)._

Une exigence passe à « validé » dans la matrice (`VALIDATED_REQUIREMENT_IDS`) seulement quand ses cours ET cet examen sont publiés et relus.

##### Composition de l'examen
_À compléter — Nombre d'exercices, points par exercice, total /20 ; chaque exigence AP du module évaluée au moins une fois. Aucune durée inventée (les consignes n'en fixent pas)._

##### Exercices et documents
_À compléter — Pour chaque exercice : situation, documents/schémas fournis, consignes numérotées, réponse libre, barème par critère, correction justifiée (format `/ampcr-pratique/format-exercice`)._

##### Supports visuels exigés
_À compléter — Schémas et documents à produire, avec leurs données de référence._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).
