# AMPCR — Pratique écrite : modèles de tickets PR01–PR30 et EX01–EX06 (tickets #192, #236)

Document généré par `python -m app.v1.ampcr_pratique_tickets` depuis le plan (`app/v1/ampcr_pratique_plan.py`) ; ne pas l'éditer à la main.

## 1. Mode d'emploi

1. Les 36 tickets existent sur GitHub (audit #236 du 26/10/2026) : **chaque ticket fait foi** pour son code, son titre et sa matière. Le § 4 donne, pour chacun, le numéro du ticket et les exigences AP rattachées dans la matrice ; le tableau complet est dans `docs/ampcr_pratique_v1.md` § 5.
2. Titre : `[Px][AMPCR pratique PRxx] …` ou `[Px][AMPCR pratique EXxx] …` (priorité P0–P3 au choix du propriétaire) ; l'orchestrateur traite les tickets par priorité puis ancienneté.
3. Un examen EX01–EX04 dépend des cours de son module ; EX05 et EX06 (globaux) portent sur tout le parcours. Une session qui reçoit un EX avant ses PR rend `READY` avec la dépendance.
4. Un nouveau ticket ou un changement de périmètre : la session réaligne `_COURSE_ROWS` / `_EXERCISE_ROWS`, la matrice et ce document dans la même PR ; `tests/test_ticket236_ampcr_pratique_numerotation.py` fige la correspondance code → ticket → titre.
5. Livraison incrémentale : chaque cours est publié dès qu'il est complet, sans attendre le module entier.

## 2. Gabarit commun

Un ticket de cours contient, dans cet ordre : en-tête (parcours, module, examens du module, socle) ; exigences officielles couvertes (texte exact) ; théorie existante ; objectifs observables ; matière obligatoire — à enseigner explicitement ; compléments autorisés ; supports visuels exigés ; pédagogie, cas et exercices ; critères d'acceptation spécifiques ; exigences transversales ; contrat de fin de ticket.

Un ticket d'examen contient : en-tête et dépendances ; exigences à évaluer ; composition de l'examen ; exercices et documents ; supports visuels exigés ; critères d'acceptation spécifiques ; exigences transversales ; contrat de fin de ticket.

Blocs communs à recopier à la fin de chaque ticket PR/EX (`python -m app.v1.ampcr_pratique_tickets PR07` produit un ticket complet) :

##### Exigences transversales (ticket socle #192 — rappel obligatoire)
- **Programme** : enseigner la matière ci-dessus, sans l'improviser ni la réduire ; recouper
  avec le PDF officiel versionné (`docs/references-officielles/ampcr/2026-2027-1/`, PDF +
  transcription). Distinguer théorie et compétence
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

## 4. Fiches des 36 tickets

### Module P1 — Matériel du PC : composants, montage et diagnostic

#### [AMPCR pratique PR01] Structure d'un PC et identification des composants

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P1 — Matériel du PC : composants, montage et diagnostic · **examen(s) du module** EX01 · **socle** #192.
**Ticket déjà rédigé : #202** (https://github.com/ReC82/jury-central/issues/202) — il fait foi pour le code, le titre et la matière.

##### Exigences officielles couvertes (matrice #192, audit #236)
- **AP-01** (p. 5) — « La structure d’un ordinateur, ses composants et ses périphériques. »
- **AP-02** (p. 5) — « Les différents éléments qui peuvent constituer un ordinateur (Processeur, mémoire RAM-ROM, carte mère, BIOS, UEFI, etc.). »
- **AP-05** (p. 5) — « Les périphériques d’entrée et de sortie et le rôle d'un pilote. »
- **AP-07** (p. 5) — « La carte mère et ses éléments constitutifs. »
- **AP-17** (p. 5) — « Notion de compatibilité. »

**Théorie existante à réutiliser** : MC01, MC02, MC03, MC04, MC07, MC12.

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

#### [AMPCR pratique PR02] Alimentation, connectique, compatibilité et sécurité

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P1 — Matériel du PC : composants, montage et diagnostic · **examen(s) du module** EX01 · **socle** #192.
**Ticket déjà rédigé : #203** (https://github.com/ReC82/jury-central/issues/203) — il fait foi pour le code, le titre et la matière.

##### Exigences officielles couvertes (matrice #192, audit #236)
- **AP-04** (p. 5) — « Les caractéristiques d’une alimentation PC. »
- **AP-06** (p. 5) — « Branchements, interfaces et connexions. »
- **AP-17** (p. 5) — « Notion de compatibilité. »
- **AP-C02** (complément pédagogique) — « Sécurité électrique et protection ESD lors d'une intervention sur un PC. » _Note : Prérequis des interventions de montage/démontage (AP-14)._

**Théorie existante à réutiliser** : MC02, MC04, MC05, MC12.

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

#### [AMPCR pratique PR03] Montage et démontage d'un PC — procédure écrite

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P1 — Matériel du PC : composants, montage et diagnostic · **examen(s) du module** EX01 · **socle** #192.
**Ticket déjà rédigé : #204** (https://github.com/ReC82/jury-central/issues/204) — il fait foi pour le code, le titre et la matière.

##### Exigences officielles couvertes (matrice #192, audit #236)
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

#### [AMPCR pratique PR04] Reconditionnement, entretien et contrôles après intervention

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P1 — Matériel du PC : composants, montage et diagnostic · **examen(s) du module** EX01 · **socle** #192.
**Ticket déjà rédigé : #205** (https://github.com/ReC82/jury-central/issues/205) — il fait foi pour le code, le titre et la matière.

##### Exigences officielles couvertes (matrice #192, audit #236)
- **AP-14** (p. 5) — « Montage, démontage et reconditionnement d’un PC. »
- **AP-C03** (complément pédagogique) — « Protéger les données du client : sauvegarde préalable, confidentialité et autorisation avant tout effacement ou toute réinstallation. » _Note : Ajouté à l'audit #236 : matière commune des tickets PR04, PR12 et PR28._

**Théorie existante à réutiliser** : MC06, MC32.

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

#### [AMPCR pratique PR05] Stockage, partitions, formatage et défragmentation

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P1 — Matériel du PC : composants, montage et diagnostic · **examen(s) du module** EX01 · **socle** #192.
**Ticket déjà rédigé : #206** (https://github.com/ReC82/jury-central/issues/206) — il fait foi pour le code, le titre et la matière.

##### Exigences officielles couvertes (matrice #192, audit #236)
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

#### [AMPCR pratique PR06] Diagnostic des pannes matérielles

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P1 — Matériel du PC : composants, montage et diagnostic · **examen(s) du module** EX01 · **socle** #192.
**Ticket déjà rédigé : #193** (https://github.com/ReC82/jury-central/issues/193) — il fait foi pour le code, le titre et la matière.

##### Exigences officielles couvertes (matrice #192, audit #236)
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

#### [AMPCR pratique EX01] Examen blanc écrit — maintenance et dépannage matériel

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P1 — Matériel du PC : composants, montage et diagnostic · **cours du module** PR01, PR02, PR03, PR04, PR05, PR06 · **socle** #192.
**Ticket déjà rédigé : #230** (https://github.com/ReC82/jury-central/issues/230) — il fait foi ; les cours qui portent ses exigences doivent être livrés avant.

##### Exigences à évaluer (matrice #192, audit #236)
- **AP-01** (p. 5) — « La structure d’un ordinateur, ses composants et ses périphériques. »
- **AP-02** (p. 5) — « Les différents éléments qui peuvent constituer un ordinateur (Processeur, mémoire RAM-ROM, carte mère, BIOS, UEFI, etc.). »
- **AP-03** (p. 5) — « Les différents types de disque dur et unités de stockage, le formatage, la défragmentation. »
- **AP-04** (p. 5) — « Les caractéristiques d’une alimentation PC. »
- **AP-06** (p. 5) — « Branchements, interfaces et connexions. »
- **AP-07** (p. 5) — « La carte mère et ses éléments constitutifs. »
- **AP-14** (p. 5) — « Montage, démontage et reconditionnement d’un PC. »
- **AP-15** (p. 5) — « Dépannage sur les dysfonctionnements courants (hardware ou software). »
- **AP-17** (p. 5) — « Notion de compatibilité. »
- **AP-C02** (complément pédagogique) — « Sécurité électrique et protection ESD lors d'une intervention sur un PC. » _Note : Prérequis des interventions de montage/démontage (AP-14)._

Une exigence passe à « validé » dans la matrice (`VALIDATED_REQUIREMENT_IDS`) seulement quand tous ses cours ET examens blancs sont publiés et que l'audit #235 en a réuni les preuves (`app.v1.ampcr_pratique_audit`).

##### Composition de l'examen
_À compléter — Nombre d'exercices, points par exercice, total /20 ; chaque exigence AP du module évaluée au moins une fois. Aucune durée inventée (les consignes n'en fixent pas)._

##### Exercices et documents
_À compléter — Pour chaque exercice : situation, documents/schémas fournis, consignes numérotées, réponse libre, barème par critère, correction justifiée (format `/ampcr-pratique/format-exercice`)._

##### Supports visuels exigés
_À compléter — Schémas et documents à produire, avec leurs données de référence._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

### Module P2 — Systèmes d'exploitation : installation et dépannage

#### [AMPCR pratique PR07] Systèmes d'exploitation, GUI/CLI et prérequis d'installation

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P2 — Systèmes d'exploitation : installation et dépannage · **examen(s) du module** EX02 · **socle** #192.
**Ticket déjà rédigé : #207** (https://github.com/ReC82/jury-central/issues/207) — il fait foi pour le code, le titre et la matière.

##### Exigences officielles couvertes (matrice #192, audit #236)
- **AP-08** (p. 5) — « Les différents systèmes d’exploitation actuellement sur le marché. »
- **AP-12** (p. 5) — « Interface graphique et interface de ligne de commande. »

**Théorie existante à réutiliser** : MC09, MC10, MC11.

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

#### [AMPCR pratique PR08] Installation complète de Windows — préparation et dépannage

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P2 — Systèmes d'exploitation : installation et dépannage · **examen(s) du module** EX02 · **socle** #192.
**Ticket déjà rédigé : #208** (https://github.com/ReC82/jury-central/issues/208) — il fait foi pour le code, le titre et la matière.

##### Exigences officielles couvertes (matrice #192, audit #236)
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

#### [AMPCR pratique PR09] Installation complète de Linux — préparation et dépannage

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P2 — Systèmes d'exploitation : installation et dépannage · **examen(s) du module** EX02 · **socle** #192.
**Ticket déjà rédigé : #209** (https://github.com/ReC82/jury-central/issues/209) — il fait foi pour le code, le titre et la matière.

##### Exigences officielles couvertes (matrice #192, audit #236)
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

#### [AMPCR pratique PR10] Comptes, pilotes, paramètres et commandes

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P2 — Systèmes d'exploitation : installation et dépannage · **examen(s) du module** EX02 · **socle** #192.
**Ticket déjà rédigé : #214** (https://github.com/ReC82/jury-central/issues/214) — il fait foi pour le code, le titre et la matière.

##### Exigences officielles couvertes (matrice #192, audit #236)
- **AP-05** (p. 5) — « Les périphériques d’entrée et de sortie et le rôle d'un pilote. »
- **AP-11** (p. 5) — « Paramètres et commandes de base des systèmes d'exploitation courants. »
- **AP-12** (p. 5) — « Interface graphique et interface de ligne de commande. »

**Théorie existante à réutiliser** : MC10, MC11, MC12.

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

#### [AMPCR pratique PR11] Messages d'erreur Windows/Linux — diagnostic et interventions écrites

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P2 — Systèmes d'exploitation : installation et dépannage · **examen(s) du module** EX02 · **socle** #192.
**Ticket déjà rédigé : #194** (https://github.com/ReC82/jury-central/issues/194) — il fait foi pour le code, le titre et la matière.

##### Exigences officielles couvertes (matrice #192, audit #236)
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

#### [AMPCR pratique PR12] Dépannage logiciel et restauration du système

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P2 — Systèmes d'exploitation : installation et dépannage · **examen(s) du module** EX02 · **socle** #192.
**Ticket déjà rédigé : #215** (https://github.com/ReC82/jury-central/issues/215) — il fait foi pour le code, le titre et la matière.

##### Exigences officielles couvertes (matrice #192, audit #236)
- **AP-15** (p. 5) — « Dépannage sur les dysfonctionnements courants (hardware ou software). »
- **AP-C03** (complément pédagogique) — « Protéger les données du client : sauvegarde préalable, confidentialité et autorisation avant tout effacement ou toute réinstallation. » _Note : Ajouté à l'audit #236 : matière commune des tickets PR04, PR12 et PR28._

**Théorie existante à réutiliser** : MC29, MC30, MC32.

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

#### [AMPCR pratique EX02] Examen blanc écrit — installation et dépannage des systèmes

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P2 — Systèmes d'exploitation : installation et dépannage · **cours du module** PR07, PR08, PR09, PR10, PR11, PR12 · **socle** #192.
**Ticket déjà rédigé : #231** (https://github.com/ReC82/jury-central/issues/231) — il fait foi ; les cours qui portent ses exigences doivent être livrés avant.

##### Exigences à évaluer (matrice #192, audit #236)
- **AP-03** (p. 5) — « Les différents types de disque dur et unités de stockage, le formatage, la défragmentation. »
- **AP-05** (p. 5) — « Les périphériques d’entrée et de sortie et le rôle d'un pilote. »
- **AP-08** (p. 5) — « Les différents systèmes d’exploitation actuellement sur le marché. »
- **AP-09** (p. 5) — « Les principaux messages d’erreurs, l’interprétation et les démarches d’intervention y afférant. » _Note : Proche de AP-13 (les deux puces figurent au PDF)._
- **AP-10** (p. 5) — « Installation complète des différents systèmes d’exploitation courants. »
- **AP-11** (p. 5) — « Paramètres et commandes de base des systèmes d'exploitation courants. »
- **AP-12** (p. 5) — « Interface graphique et interface de ligne de commande. »
- **AP-13** (p. 5) — « Connaître les principaux messages d’erreurs, comment interpréter ceux-ci et comment intervenir si possible. » _Note : Proche de AP-09 (les deux puces figurent au PDF)._
- **AP-15** (p. 5) — « Dépannage sur les dysfonctionnements courants (hardware ou software). »
- **AP-24** (p. 6) — « Notions de domaine, groupe de travail, comptes utilisateurs et groupes d’utilisateurs. » _Note : Domaine / groupe de travail absents de la théorie actuelle._
- **AP-27** (p. 6) — « Les notions de droit et de permission. »
- **AP-C03** (complément pédagogique) — « Protéger les données du client : sauvegarde préalable, confidentialité et autorisation avant tout effacement ou toute réinstallation. » _Note : Ajouté à l'audit #236 : matière commune des tickets PR04, PR12 et PR28._

Une exigence passe à « validé » dans la matrice (`VALIDATED_REQUIREMENT_IDS`) seulement quand tous ses cours ET examens blancs sont publiés et que l'audit #235 en a réuni les preuves (`app.v1.ampcr_pratique_audit`).

##### Composition de l'examen
_À compléter — Nombre d'exercices, points par exercice, total /20 ; chaque exigence AP du module évaluée au moins une fois. Aucune durée inventée (les consignes n'en fixent pas)._

##### Exercices et documents
_À compléter — Pour chaque exercice : situation, documents/schémas fournis, consignes numérotées, réponse libre, barème par critère, correction justifiée (format `/ampcr-pratique/format-exercice`)._

##### Supports visuels exigés
_À compléter — Schémas et documents à produire, avec leurs données de référence._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

### Module P3 — Câblage : cuivre, coaxial et fibre optique

#### [AMPCR pratique PR13] Câbles UTP, FTP, STP et coaxial — choix et pose

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P3 — Câblage : cuivre, coaxial et fibre optique · **examen(s) du module** EX03 · **socle** #192.
**Ticket déjà rédigé : #216** (https://github.com/ReC82/jury-central/issues/216) — il fait foi pour le code, le titre et la matière.

##### Exigences officielles couvertes (matrice #192, audit #236)
- **AP-18** (p. 5) — « Les différents types de câbles : UTP, FTP, STP, Coax. » _Note : FTP et coaxial absents de la théorie actuelle._
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

#### [AMPCR pratique PR14] Débits, distances, atténuation et impédance

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P3 — Câblage : cuivre, coaxial et fibre optique · **examen(s) du module** EX03 · **socle** #192.
**Ticket déjà rédigé : #217** (https://github.com/ReC82/jury-central/issues/217) — il fait foi pour le code, le titre et la matière.

##### Exigences officielles couvertes (matrice #192, audit #236)
- **AP-19** (p. 6) — « Les débits binaires des câbles. »
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

#### [AMPCR pratique PR15] Câblage RJ45 T568A/B — fabrication, schémas et tests

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P3 — Câblage : cuivre, coaxial et fibre optique · **examen(s) du module** EX03 · **socle** #192.
**Ticket déjà rédigé : #197** (https://github.com/ReC82/jury-central/issues/197) — il fait foi pour le code, le titre et la matière.

##### Exigences officielles couvertes (matrice #192, audit #236)
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

#### [AMPCR pratique PR16] Câble coaxial et BNC — impédance, fabrication et diagnostic écrit

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P3 — Câblage : cuivre, coaxial et fibre optique · **examen(s) du module** EX03 · **socle** #192.
**Ticket déjà rédigé : #198** (https://github.com/ReC82/jury-central/issues/198) — il fait foi pour le code, le titre et la matière.

##### Exigences officielles couvertes (matrice #192, audit #236)
- **AP-18** (p. 5) — « Les différents types de câbles : UTP, FTP, STP, Coax. » _Note : FTP et coaxial absents de la théorie actuelle._
- **AP-20** (p. 6) — « Les caractéristiques des câbles : atténuation, notion d’impédance, sensibilité aux parasites, blindage, précautions d’utilisation, les avantages, les inconvénients des uns par rapport aux autres, la longueur maximale d’un tronçon suivant le débit, les connecteurs, etc. » _Note : Atténuation et impédance absentes de la théorie actuelle._
- **AP-35** (p. 6) — « Description de la réalisation d’un câble avec connecteurs BNC. » _Note : Aucune théorie existante._

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

#### [AMPCR pratique PR17] Fibre optique — choix, raccordement et diagnostic

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P3 — Câblage : cuivre, coaxial et fibre optique · **examen(s) du module** EX03 · **socle** #192.
**Ticket déjà rédigé : #218** (https://github.com/ReC82/jury-central/issues/218) — il fait foi pour le code, le titre et la matière.

##### Exigences officielles couvertes (matrice #192, audit #236)
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

#### [AMPCR pratique EX03] Examen blanc écrit — câblage RJ45, BNC et fibre

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P3 — Câblage : cuivre, coaxial et fibre optique · **cours du module** PR13, PR14, PR15, PR16, PR17 · **socle** #192.
**Ticket déjà rédigé : #232** (https://github.com/ReC82/jury-central/issues/232) — il fait foi ; les cours qui portent ses exigences doivent être livrés avant.

##### Exigences à évaluer (matrice #192, audit #236)
- **AP-18** (p. 5) — « Les différents types de câbles : UTP, FTP, STP, Coax. » _Note : FTP et coaxial absents de la théorie actuelle._
- **AP-19** (p. 6) — « Les débits binaires des câbles. »
- **AP-20** (p. 6) — « Les caractéristiques des câbles : atténuation, notion d’impédance, sensibilité aux parasites, blindage, précautions d’utilisation, les avantages, les inconvénients des uns par rapport aux autres, la longueur maximale d’un tronçon suivant le débit, les connecteurs, etc. » _Note : Atténuation et impédance absentes de la théorie actuelle._
- **AP-21** (p. 6) — « La fibre optique et ses caractéristiques : support d’information, débit binaire, longueur d’un tronçon, notion d’atténuation, connexion, avantages et inconvénients, etc. » _Note : La théorie actuelle ne fait que citer la fibre._
- **AP-22** (p. 6) — « Comparaison entre la fibre optique et les autres types de câbles. » _Note : Aucune théorie existante._
- **AP-34** (p. 6) — « Description de la réalisation d’un câble avec connecteurs RJ45 (code des couleurs). »
- **AP-35** (p. 6) — « Description de la réalisation d’un câble avec connecteurs BNC. » _Note : Aucune théorie existante._

Une exigence passe à « validé » dans la matrice (`VALIDATED_REQUIREMENT_IDS`) seulement quand tous ses cours ET examens blancs sont publiés et que l'audit #235 en a réuni les preuves (`app.v1.ampcr_pratique_audit`).

##### Composition de l'examen
_À compléter — Nombre d'exercices, points par exercice, total /20 ; chaque exigence AP du module évaluée au moins une fois. Aucune durée inventée (les consignes n'en fixent pas)._

##### Exercices et documents
_À compléter — Pour chaque exercice : situation, documents/schémas fournis, consignes numérotées, réponse libre, barème par critère, correction justifiée (format `/ampcr-pratique/format-exercice`)._

##### Supports visuels exigés
_À compléter — Schémas et documents à produire, avec leurs données de référence._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

### Module P4 — Réseau : installation, configuration et dépannage

#### [AMPCR pratique PR18] Installation physique d'un mini-réseau

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P4 — Réseau : installation, configuration et dépannage · **examen(s) du module** EX04 · **socle** #192.
**Ticket déjà rédigé : #219** (https://github.com/ReC82/jury-central/issues/219) — il fait foi pour le code, le titre et la matière.

##### Exigences officielles couvertes (matrice #192, audit #236)
- **AP-36** (p. 6) — « Câblage et installation physique d’un réseau informatique. »
- **AP-38** (p. 6) — « Création d’un mini réseau entre plusieurs machines. »

**Théorie existante à réutiliser** : MC15, MC16, MC23, MC37.

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

#### [AMPCR pratique PR19] Topologies, OSI, TCP/IP, NetBEUI et équipements

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P4 — Réseau : installation, configuration et dépannage · **examen(s) du module** EX04 · **socle** #192.
**Ticket déjà rédigé : #220** (https://github.com/ReC82/jury-central/issues/220) — il fait foi pour le code, le titre et la matière.

##### Exigences officielles couvertes (matrice #192, audit #236)
- **AP-23** (p. 6) — « Topologies de réseaux. »
- **AP-29** (p. 6) — « Notions de base sur les protocoles (TCP/IP, OSI, NETBEUI…). » _Note : NetBEUI absent de la théorie actuelle._
- **AP-31** (p. 6) — « Hub, switch, passerelle, routeur, modem. » _Note : Hub absent de la théorie actuelle._

**Théorie existante à réutiliser** : MC13, MC14, MC21, MC23.

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

#### [AMPCR pratique PR20] IPv4, MAC, masques et passerelles — configuration et diagnostics écrits

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P4 — Réseau : installation, configuration et dépannage · **examen(s) du module** EX04 · **socle** #192.
**Ticket déjà rédigé : #199** (https://github.com/ReC82/jury-central/issues/199) — il fait foi pour le code, le titre et la matière.

##### Exigences officielles couvertes (matrice #192, audit #236)
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

#### [AMPCR pratique PR21] Connexion directe de deux PC et mini-réseau

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P4 — Réseau : installation, configuration et dépannage · **examen(s) du module** EX04 · **socle** #192.
**Ticket déjà rédigé : #221** (https://github.com/ReC82/jury-central/issues/221) — il fait foi pour le code, le titre et la matière.

##### Exigences officielles couvertes (matrice #192, audit #236)
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

#### [AMPCR pratique PR22] Domaine, groupe de travail, comptes et groupes

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P4 — Réseau : installation, configuration et dépannage · **examen(s) du module** EX04 · **socle** #192.
**Ticket déjà rédigé : #222** (https://github.com/ReC82/jury-central/issues/222) — il fait foi pour le code, le titre et la matière.

##### Exigences officielles couvertes (matrice #192, audit #236)
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

#### [AMPCR pratique PR23] Partage de dossiers, imprimantes et permissions

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P4 — Réseau : installation, configuration et dépannage · **examen(s) du module** EX04 · **socle** #192.
**Ticket déjà rédigé : #223** (https://github.com/ReC82/jury-central/issues/223) — il fait foi pour le code, le titre et la matière.

##### Exigences officielles couvertes (matrice #192, audit #236)
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

#### [AMPCR pratique PR24] Dépannage réseau et Internet — dossiers d'intervention écrits

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P4 — Réseau : installation, configuration et dépannage · **examen(s) du module** EX04 · **socle** #192.
**Ticket déjà rédigé : #200** (https://github.com/ReC82/jury-central/issues/200) — il fait foi pour le code, le titre et la matière.

##### Exigences officielles couvertes (matrice #192, audit #236)
- **AP-32** (p. 6) — « Connexions et interventions en cas de panne internet. »
- **AP-37** (p. 6) — « Dépannage de problèmes simples d’accès au réseau. »

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

#### [AMPCR pratique PR25] Wi-Fi : configuration, couverture, sécurité et diagnostic

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P4 — Réseau : installation, configuration et dépannage · **examen(s) du module** EX04 · **socle** #192.
**Ticket déjà rédigé : #224** (https://github.com/ReC82/jury-central/issues/224) — il fait foi pour le code, le titre et la matière.

##### Exigences officielles couvertes (matrice #192, audit #236)
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

#### [AMPCR pratique EX04] Examen blanc écrit — réseau, configuration et dépannage

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P4 — Réseau : installation, configuration et dépannage · **cours du module** PR18, PR19, PR20, PR21, PR22, PR23, PR24, PR25 · **socle** #192.
**Ticket déjà rédigé : #233** (https://github.com/ReC82/jury-central/issues/233) — il fait foi ; les cours qui portent ses exigences doivent être livrés avant.

##### Exigences à évaluer (matrice #192, audit #236)
- **AP-23** (p. 6) — « Topologies de réseaux. »
- **AP-25** (p. 6) — « Partage de ressources (imprimantes, disques, répertoires…). »
- **AP-26** (p. 6) — « Mise en partage sur un réseau informatique de documents et applications. »
- **AP-27** (p. 6) — « Les notions de droit et de permission. »
- **AP-28** (p. 6) — « Connexion de deux machines en direct. »
- **AP-29** (p. 6) — « Notions de base sur les protocoles (TCP/IP, OSI, NETBEUI…). » _Note : NetBEUI absent de la théorie actuelle._
- **AP-30** (p. 6) — « L’adressage IP, les adresses MAC, l’identification d’une adresse MAC et d’une adresse IP. »
- **AP-31** (p. 6) — « Hub, switch, passerelle, routeur, modem. » _Note : Hub absent de la théorie actuelle._
- **AP-32** (p. 6) — « Connexions et interventions en cas de panne internet. »
- **AP-33** (p. 6) — « WIFI : principe, sécurisation, cryptage, répéteur. » _Note : Répéteur absent de la théorie actuelle._
- **AP-37** (p. 6) — « Dépannage de problèmes simples d’accès au réseau. »
- **AP-38** (p. 6) — « Création d’un mini réseau entre plusieurs machines. »

Une exigence passe à « validé » dans la matrice (`VALIDATED_REQUIREMENT_IDS`) seulement quand tous ses cours ET examens blancs sont publiés et que l'audit #235 en a réuni les preuves (`app.v1.ampcr_pratique_audit`).

##### Composition de l'examen
_À compléter — Nombre d'exercices, points par exercice, total /20 ; chaque exigence AP du module évaluée au moins une fois. Aucune durée inventée (les consignes n'en fixent pas)._

##### Exercices et documents
_À compléter — Pour chaque exercice : situation, documents/schémas fournis, consignes numérotées, réponse libre, barème par critère, correction justifiée (format `/ampcr-pratique/format-exercice`)._

##### Supports visuels exigés
_À compléter — Schémas et documents à produire, avec leurs données de référence._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

### Module P5 — Méthode d'intervention et examens blancs globaux

#### [AMPCR pratique PR26] Analyser une demande d'intervention technique

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P5 — Méthode d'intervention et examens blancs globaux · **examen(s) du module** EX05, EX06 · **socle** #192.
**Ticket déjà rédigé : #225** (https://github.com/ReC82/jury-central/issues/225) — il fait foi pour le code, le titre et la matière.

##### Exigences officielles couvertes (matrice #192, audit #236)
- **AP-16** (p. 5) — « Vocabulaire technique. » _Note : Transversal : aucun cours dédié ; travaillé en rédaction (PR26, PR29) et dans le lexique AMPCR._
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

#### [AMPCR pratique PR27] Construire et justifier une procédure de diagnostic

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P5 — Méthode d'intervention et examens blancs globaux · **examen(s) du module** EX05, EX06 · **socle** #192.
**Ticket déjà rédigé : #226** (https://github.com/ReC82/jury-central/issues/226) — il fait foi pour le code, le titre et la matière.

##### Exigences officielles couvertes (matrice #192, audit #236)
- **AP-15** (p. 5) — « Dépannage sur les dysfonctionnements courants (hardware ou software). »
- **AP-C01** (complément pédagogique) — « Rédiger une réponse écrite de technicien : décrire une intervention étape par étape et justifier chaque choix. » _Note : Méthode : l'épreuve pratique se fait uniquement par écrit (p. 3)._

**Théorie existante à réutiliser** : MC29, MC30, MC36.

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

#### [AMPCR pratique PR28] Outillage, sécurité et protection des données

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P5 — Méthode d'intervention et examens blancs globaux · **examen(s) du module** EX05, EX06 · **socle** #192.
**Ticket déjà rédigé : #227** (https://github.com/ReC82/jury-central/issues/227) — il fait foi pour le code, le titre et la matière.

##### Exigences officielles couvertes (matrice #192, audit #236)
- **AP-C02** (complément pédagogique) — « Sécurité électrique et protection ESD lors d'une intervention sur un PC. » _Note : Prérequis des interventions de montage/démontage (AP-14)._
- **AP-C03** (complément pédagogique) — « Protéger les données du client : sauvegarde préalable, confidentialité et autorisation avant tout effacement ou toute réinstallation. » _Note : Ajouté à l'audit #236 : matière commune des tickets PR04, PR12 et PR28._

**Théorie existante à réutiliser** : MC05, MC32.

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

#### [AMPCR pratique PR29] Contrôles finaux et rapport professionnel d'intervention

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P5 — Méthode d'intervention et examens blancs globaux · **examen(s) du module** EX05, EX06 · **socle** #192.
**Ticket déjà rédigé : #228** (https://github.com/ReC82/jury-central/issues/228) — il fait foi pour le code, le titre et la matière.

##### Exigences officielles couvertes (matrice #192, audit #236)
- **AP-16** (p. 5) — « Vocabulaire technique. » _Note : Transversal : aucun cours dédié ; travaillé en rédaction (PR26, PR29) et dans le lexique AMPCR._
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

#### [AMPCR pratique PR30] Grand laboratoire écrit — installation et dépannage d'un réseau complet

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **module** P5 — Méthode d'intervention et examens blancs globaux · **examen(s) du module** EX05, EX06 · **socle** #192.
**Ticket déjà rédigé : #229** (https://github.com/ReC82/jury-central/issues/229) — il fait foi pour le code, le titre et la matière.

##### Exigences officielles couvertes (matrice #192, audit #236)
- **AP-36** (p. 6) — « Câblage et installation physique d’un réseau informatique. »
- **AP-37** (p. 6) — « Dépannage de problèmes simples d’accès au réseau. »
- **AP-38** (p. 6) — « Création d’un mini réseau entre plusieurs machines. »

**Théorie existante à réutiliser** : MC15, MC16, MC23, MC31, MC37.

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

#### [AMPCR pratique EX05] Examen blanc global standard — épreuve pratique écrite

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **examen blanc global** · **cours concernés** : tout le parcours (PR01–PR30) · **socle** #192.
**Ticket déjà rédigé : #201** (https://github.com/ReC82/jury-central/issues/201) — il fait foi ; les cours qui portent ses exigences doivent être livrés avant.

##### Exigences à évaluer (matrice #192, audit #236)
- **AP-01** (p. 5) — « La structure d’un ordinateur, ses composants et ses périphériques. »
- **AP-10** (p. 5) — « Installation complète des différents systèmes d’exploitation courants. »
- **AP-15** (p. 5) — « Dépannage sur les dysfonctionnements courants (hardware ou software). »
- **AP-16** (p. 5) — « Vocabulaire technique. » _Note : Transversal : aucun cours dédié ; travaillé en rédaction (PR26, PR29) et dans le lexique AMPCR._
- **AP-25** (p. 6) — « Partage de ressources (imprimantes, disques, répertoires…). »
- **AP-30** (p. 6) — « L’adressage IP, les adresses MAC, l’identification d’une adresse MAC et d’une adresse IP. »
- **AP-34** (p. 6) — « Description de la réalisation d’un câble avec connecteurs RJ45 (code des couleurs). »
- **AP-35** (p. 6) — « Description de la réalisation d’un câble avec connecteurs BNC. » _Note : Aucune théorie existante._
- **AP-36** (p. 6) — « Câblage et installation physique d’un réseau informatique. »
- **AP-37** (p. 6) — « Dépannage de problèmes simples d’accès au réseau. »
- **AP-C01** (complément pédagogique) — « Rédiger une réponse écrite de technicien : décrire une intervention étape par étape et justifier chaque choix. » _Note : Méthode : l'épreuve pratique se fait uniquement par écrit (p. 3)._

Une exigence passe à « validé » dans la matrice (`VALIDATED_REQUIREMENT_IDS`) seulement quand tous ses cours ET examens blancs sont publiés et que l'audit #235 en a réuni les preuves (`app.v1.ampcr_pratique_audit`).

##### Composition de l'examen
_À compléter — Nombre d'exercices, points par exercice, total /20 ; chaque exigence AP du module évaluée au moins une fois. Aucune durée inventée (les consignes n'en fixent pas)._

##### Exercices et documents
_À compléter — Pour chaque exercice : situation, documents/schémas fournis, consignes numérotées, réponse libre, barème par critère, correction justifiée (format `/ampcr-pratique/format-exercice`)._

##### Supports visuels exigés
_À compléter — Schémas et documents à produire, avec leurs données de référence._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).

#### [AMPCR pratique EX06] Examen blanc global avancé — dossiers complexes

**Parcours** AMPCR — Pratique écrite, cycle 2026-2027/1 · **examen blanc global** · **cours concernés** : tout le parcours (PR01–PR30) · **socle** #192.
**Ticket déjà rédigé : #234** (https://github.com/ReC82/jury-central/issues/234) — il fait foi ; les cours qui portent ses exigences doivent être livrés avant.

##### Exigences à évaluer (matrice #192, audit #236)
- **AP-03** (p. 5) — « Les différents types de disque dur et unités de stockage, le formatage, la défragmentation. »
- **AP-10** (p. 5) — « Installation complète des différents systèmes d’exploitation courants. »
- **AP-15** (p. 5) — « Dépannage sur les dysfonctionnements courants (hardware ou software). »
- **AP-16** (p. 5) — « Vocabulaire technique. » _Note : Transversal : aucun cours dédié ; travaillé en rédaction (PR26, PR29) et dans le lexique AMPCR._
- **AP-17** (p. 5) — « Notion de compatibilité. »
- **AP-25** (p. 6) — « Partage de ressources (imprimantes, disques, répertoires…). »
- **AP-27** (p. 6) — « Les notions de droit et de permission. »
- **AP-30** (p. 6) — « L’adressage IP, les adresses MAC, l’identification d’une adresse MAC et d’une adresse IP. »
- **AP-33** (p. 6) — « WIFI : principe, sécurisation, cryptage, répéteur. » _Note : Répéteur absent de la théorie actuelle._
- **AP-34** (p. 6) — « Description de la réalisation d’un câble avec connecteurs RJ45 (code des couleurs). »
- **AP-35** (p. 6) — « Description de la réalisation d’un câble avec connecteurs BNC. » _Note : Aucune théorie existante._
- **AP-C01** (complément pédagogique) — « Rédiger une réponse écrite de technicien : décrire une intervention étape par étape et justifier chaque choix. » _Note : Méthode : l'épreuve pratique se fait uniquement par écrit (p. 3)._
- **AP-C03** (complément pédagogique) — « Protéger les données du client : sauvegarde préalable, confidentialité et autorisation avant tout effacement ou toute réinstallation. » _Note : Ajouté à l'audit #236 : matière commune des tickets PR04, PR12 et PR28._

Une exigence passe à « validé » dans la matrice (`VALIDATED_REQUIREMENT_IDS`) seulement quand tous ses cours ET examens blancs sont publiés et que l'audit #235 en a réuni les preuves (`app.v1.ampcr_pratique_audit`).

##### Composition de l'examen
_À compléter — Nombre d'exercices, points par exercice, total /20 ; chaque exigence AP du module évaluée au moins une fois. Aucune durée inventée (les consignes n'en fixent pas)._

##### Exercices et documents
_À compléter — Pour chaque exercice : situation, documents/schémas fournis, consignes numérotées, réponse libre, barème par critère, correction justifiée (format `/ampcr-pratique/format-exercice`)._

##### Supports visuels exigés
_À compléter — Schémas et documents à produire, avec leurs données de référence._

##### Critères d'acceptation spécifiques
_À compléter — Ce que le propriétaire vérifiera en priorité._

> Ajouter ici, tels quels, les blocs « Exigences transversales » et « Contrat de fin de ticket » du § 2 de `docs/ampcr_pratique_tickets.md` (ils s'appliquent de toute façon).
