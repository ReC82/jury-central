# Ticket #129 — FSE : varier les questions et afficher de vrais supports visuels

- **Ticket** : [#129 — FSE — varier les questions et afficher de vrais supports visuels en entraînement et examen blanc](https://github.com/ReC82/jury-central/issues/129)
- **État réel** : **Partiel — installé, reste à faire** (mécanisme commun + cas nouveaux FSE01 à FSE04 ; FSE05 à FSE16 restent à enrichir)
- **Branche** : `feature/129-fse-variantes-visuels`
- **SHA installé** : `1b15c71ae42155f4876180b349214b8bbdf7c525` (PR #181)
- **Date** : 2026-10-22

## 1. Diagnostic

- Les banques FSE01–FSE16 (14 questions par cours en moyenne) sont écrites sur les
  **exemples commentés du cours** : en FSE01, 8 questions sur 14 portent sur le mail de
  Karim Haddad, l'affiche de sécurité routière ou l'offre d'emploi de Techno Services, que
  le cours analyse déjà en détail. L'entraînement et l'examen blanc réinterrogeaient donc
  l'élève sur des cas déjà corrigés devant lui.
- La sélection tirait au hasard dans cette banque (après la difficulté et l'anti-répétition
  par question) : rien ne faisait passer un cas neuf avant un exemple du cours, et une
  question différente sur un document déjà vu comptait comme « nouvelle ».
- L'affiche de FSE01 en session était celle du cours, accompagnée d'une légende descriptive
  (« Image : silhouette noire… », « logo du SPW… ») ; l'illustration réelle ne correspond
  pas à cette description (lettres et enfant en rouge, voir #149 question 2), et la
  situation est incohérente (enfant qui traverse au bord d'une autoroute).
- **Génération d'images par API impossible actuellement** : la clé OpenAI du serveur est
  refusée (`401 invalid_api_key` dans les journaux du worker, dernier essai le 21/10 à
  16 h 31 ; fichier de configuration inchangé depuis le 17/09 ; aucune correction IA réussie
  depuis le 03/10). Je n'ai pas lu la configuration.

## 2. Ce qui est livré

### Mécanisme commun (sans second moteur)

- `app/v1/fse_cases.py` : un **cas** = un document structuré (`SourceDocument` + version,
  texte exact + `content_json["layout"]`, mêmes composants que #149) et ses questions.
  Import idempotent (un cas déjà présent, reconnu au titre exact de son document, n'est ni
  recréé ni modifié), questions `MANUAL` (ne bloque pas l'import historique `IMPORTED`),
  difficulté déclarée sur chaque question. Appelé par l'amorçage paresseux existant
  (`_ensure_bank_seeded`) ; l'ouverture de FSE17 amorce les banques et les cas de
  FSE01→FSE16 (même principe que FR20). Aucune question ni aucun document existant n'est
  modifié : les anciennes sessions gardent leurs versions.
- **Ordre de sélection** (`case_ranker`, utilisé par `compose_selection`) : la difficulté
  demandée reste prioritaire ; à l'intérieur de chaque difficulté : (0) cas nouveaux jamais
  vus par l'élève (ou questions sans document), (1) cas nouveaux dont l'élève a déjà vu le
  document — en entraînement OU en examen —, (2) exemples commentés du cours. Ce n'est
  jamais un filtre : une session n'est jamais raccourcie. FSE17 garde sa répartition par
  cours et applique le même ordre dans chaque cours. No-op strict pour les matières sans
  exemples déclarés (Informatique, Français).
- **Vrai visuel ou rien** : une illustration est un `Asset` (fichier livré, empreinte
  SHA-256, méthode de production, prompt, modèle) rattaché à la version du document
  (`SourceDocumentVersion.asset_id`). Fichier absent → le cas n'est pas importé ; asset
  invalidé par l'admin ou fichier disparu → ses questions ne sont plus servies
  (`unusable_document_question_ids`, appliqué aussi à FSE17). Aucune génération d'image à
  l'affichage, à la reprise, au seed ou au déploiement.
- **Composant `poster_sheet`** (`_document_layouts.html` + CSS) : affiche réellement
  composée — émetteur, bandeau, titre, illustration, slogan, informations pratiques,
  mention en bas — texte exact en HTML ; clic = agrandissement ; « Ouvrir en grand » =
  page imprimable ; texte alternatif complet. Le contexte non visible sur le support (lieu
  d'installation, public) est affiché à part, dans un encadré « situation » au-dessus du
  document (tous composants). Statut « lu par… » ajouté au composant conversation.

### Contenu

| Cours | Cas nouveaux (supports) | Questions | Facile / moyen / difficile |
|---|---|---|---|
| FSE01 | Affiche d'un atelier de réparation de quartier (dessin + texte) ; conversation d'une équipe de futsal (consigne ambiguë, rétroaction, « lu par 8 des 12 ») ; note de service jargonneuse d'un supermarché (obstacle de code) ; 3 mini-situations (SMS « ne pas répondre », appel vidéo figé, panneau lumineux) | 17 | 5 / 7 / 5 |
| FSE02 | Page « Qui finance votre radio ? » d'une radio locale à financement mixte (publicité 65 %, subvention 35 %, prix du spot selon l'audience, émission où l'on appelle le studio) ; couverture d'un magazine sans publicité (vente au numéro + abonnement) ; publication d'un site gratuit qui devient payant et réactions des lecteurs ; 2 mini-situations (publicité avant une vidéo en ligne, télévision publique sans publicité pour les enfants) | 13 | 5 / 5 / 3 |
| FSE03 | Cinq résultats d'une recherche en ligne sur un candidat apprenti électricien (profil, vidéo publiée par son club, palmarès scolaire, avis laissé sur une pizzeria, adresse déduite par un réseau) ; 2 mini-situations (vidéo de mariage publiée par un invité, profil qui ne montre que des voyages) | 8 | 3 / 3 / 2 |
| FSE04 | Conversation de l'équipe d'un garage quand un apprenti part sans ranger son poste (norme, valeur, besoin, frustration, socialisation, limites de l'influence) ; affiche du règlement d'une maison de jeunes (normes écrites / valeur affichée) ; 2 mini-situations (tri des déchets appris en famille, refus de suivre le groupe) | 9 | 3 / 4 / 2 |

Total : 47 questions nouvelles, 10 nouveaux documents. Exemples du cours déclarés
(titres + noms propres) : FSE01 (Karim Haddad, affiche routière, Techno Services), FSE02
(Hebdo du Littoral, Flash Infos, RCW), FSE03 (Sophie Lambert), FSE04 (« Fous rires du
quotidien », Karim).

FSE01 passe de 14 à 31 questions, dont 23 hors exemples du cours (deux entraînements de 10 sans aucun exemple du cours). Le nouveau cas d'affiche
évite la situation incohérente : affiche collée sur la porte d'une boulangerie de
quartier, public de passants, rétroaction possible seulement par un autre canal (mail ou
sur place) — cohérent avec le cours (« une affiche ne permet pas de rétroaction directe »).

### Illustration

`app/static/img/fse/cases/fse01_atelier_reparation.svg` : dessin vectoriel original (deux
bénévoles réparent un vélo sur un pied d'atelier, outils au mur), sans texte ni visage
détaillé. La description transmise à la correction (« deux bénévoles réparent un vélo
installé sur un pied d'atelier ; des outils sont accrochés au mur derrière eux ») correspond
exactement au dessin, et est aussi affichée sous l'affiche.

## 3. Tester

Connecte-toi d'abord sur le site.

- Entraînement FSE01 : https://jury-central.lodylands.com/uaa/fse-fse01/practice
- Entraînements FSE02 / FSE03 / FSE04 : https://jury-central.lodylands.com/uaa/fse-fse02/practice — https://jury-central.lodylands.com/uaa/fse-fse03/practice — https://jury-central.lodylands.com/uaa/fse-fse04/practice
- Examen FSE01 : https://jury-central.lodylands.com/uaa/fse-fse01/exam
- Examen blanc FSE17 : https://jury-central.lodylands.com/uaa/fse-fse17/exam

Procédure courte : démarrer un entraînement FSE01 (10 questions) ; vérifier que les
questions portent sur l'atelier de réparation, le groupe de futsal, la note du magasin ou
des mini-situations, et plus sur le mail de Karim/l'affiche routière/Techno Services ;
cliquer sur l'affiche (agrandissement) et sur « Ouvrir en grand » (page imprimable) ;
quitter puis reprendre la session (mêmes questions, même affiche) ; terminer et regarder
« Revoir le document » dans les résultats ; démarrer un deuxième entraînement : aucune
question répétée, encore des cas nouveaux ; sur téléphone, vérifier l'affiche en une
colonne.

## 4. Vérifications

- Tests ciblés `tests/test_ticket129_fse_cases.py` (43, dont vérification mot pour mot de chaque document et absence des exemples du cours pour chaque cas) : import additif/idempotent, texte
  affiché = extraits exacts du document et couverture de son contenu, affiche rendue avec
  l'illustration et sans crochets, page de session et page document (HTTP), détection des
  exemples du cours, deux puis trois sessions successives (0, 0 puis 7 exemples, aucune
  répétition), cas déjà vu classé après un cas jamais vu, difficulté prioritaire, no-op
  strict sans rangs, autres cours inchangés, illustration absente → cas non importé, asset
  invalide → questions non servies, reprise identique sans appel de génération, FSE17
  (cas nouveaux amorcés, plusieurs cours couverts, pas d'exemples FSE01 en tête).
- Suite complète (moteur de sélection partagé modifié) : 2047 passed, 1 échec attendu
  corrigé (`test_ticket96…persists_through_resume` comptait 3 questions difficiles en
  FSE01 ; il y en a désormais 5). Un premier passage avait aussi montré un échec AMPCR
  intermittent préexistant (`test_ticket55…json_autosave_api…` : le type de la première
  question est aléatoire, une remise en ordre refuse une réponse texte), qui passe à
  nouveau et ne touche pas FSE — signalé, non corrigé ici.
- Essai à blanc sur une **copie** de la base réelle (sauvegarde d'avant installation,
  fichier temporaire supprimé ensuite) : l'ouverture de FSE17 importe les 47 questions et
  10 documents, un second passage n'ajoute rien ; un entraînement FSE01 « moyen » se compose
  normalement.
- `ruff check` des fichiers modifiés : aucune erreur.
- Rendu visuel : captures headless Chromium des dix nouveaux documents avec les vraies
  feuilles de style (desktop 1100 px, mobile 390 px), examinées. La page complète du site
  reste à valider par toi.
- Non vérifié : qualité réelle de la correction IA sur ces nouvelles questions (la clé IA
  est refusée ; les tests utilisent le fournisseur simulé).

## 5. Choix techniques faits seul

1. **Illustration en SVG dessiné plutôt que générée par API** : la clé est refusée (401) ;
   le ticket admet le SVG/HTML et demande des dessins plutôt que des photos. Le prompt
   équivalent est conservé dans les métadonnées de l'asset pour une éventuelle génération.
2. **Exemples du cours dépriorisés, pas archivés** : aucune question existante n'est
   modifiée ni retirée ; les exemples ne servent plus qu'en complément quand les cas
   nouveaux d'une difficulté sont épuisés.
3. **Un même support sert plusieurs questions complémentaires** (4 à 5 par document), comme
   le demande le ticket ; un cas déjà vu passe après un cas jamais vu.
4. **Questions à choix multiple sur mini-situations** : le registre des types n'autorise pas
   de document pour `multiple_choice` ; la situation tient dans l'énoncé.
5. **Questions `MANUAL`** pour ne pas perturber l'import historique (`IMPORTED`).
6. **Pas d'import au seed** : les cas s'importent à l'ouverture du cours (ou de FSE17),
   comme les banques existantes.

## 6. Décisions demandées au propriétaire

1. **Clé API OpenAI refusée (401)**. Elle bloque la génération d'illustrations ET la
   correction IA des réponses ouvertes. Options : (a) remplacer la clé dans la
   configuration du serveur ; (b) continuer en dessins SVG uniquement. **Recommandation :
   (a)** ; les dessins SVG livrés restent valables.
2. **Ancienne affiche FSE01 (autoroute + enfant qui traverse)**, incohérente et non conforme
   à sa légende. Elle n'est plus servie qu'en dernier recours. Options : (a) l'archiver dans
   la banque (anciennes sessions intactes) ; (b) la garder en dernier recours.
   **Recommandation : (a)**, à faire avec la correction du cours lui-même (hors périmètre).

## 7. Restant à réaliser

- Cas nouveaux pour FSE05 à FSE16 (lots suivants), même mécanisme.
- Génération d'illustrations raster via l'API quand la clé sera valide (si souhaité).

## 8. Installation (2026-10-22)

- PR #181 fusionnée dans `develop`, installée en avance rapide : `3de3aec` → `1b15c71`.
- Sauvegarde de la base avant installation (dossier de l'orchestrateur). Pas de seed : les
  cas s'importent à la première ouverture d'un cours FSE ou de l'examen blanc FSE17. Aucune
  dépendance ajoutée.
- Services `jury-central` et `jury-central-correction-worker` redémarrés : actifs ;
  `/health` local et public : `ok` ; pages FSE01/FSE17 : 303 (connexion requise, normal) ;
  illustration et feuille de style servies (200).
- Compteurs utilisateurs/sessions/réponses : 18 / 71 / 584 avant et après.
