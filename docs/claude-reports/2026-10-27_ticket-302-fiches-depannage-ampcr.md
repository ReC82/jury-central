# Ticket #302 — Six fiches de dépannage AMPCR Pratique écrite

**Statut : installé, à tester.** Les six fiches sont en ligne. Elles ont été livrées une par une le 27/10/2026, entre 17 h 50 et 18 h 30 environ.
SHA installé : `ee4b7bb` (PR #303 à #309).

## Liens
- Toutes les fiches : https://jury-central.lodylands.com/ampcr-pratique/fiches
  Elles sont aussi accessibles depuis l'encadré en haut de https://jury-central.lodylands.com/ampcr-pratique et à la fin de chaque module.

| Fiche | Cours | Lire | HTML autonome | Volume (estimation) |
|---|---|---|---|---|
| 1 — Maintenance matérielle | PR01–PR06 · EX01 | [/fiches/1](https://jury-central.lodylands.com/ampcr-pratique/fiches/1) | [télécharger](https://jury-central.lodylands.com/ampcr-pratique/fiches/1/telecharger) | ~25 300 mots : 40 lignes de matrice, 29 procédures, 7 dossiers |
| 2 — Systèmes Windows/Linux | PR07–PR12 · EX02 | [/fiches/2](https://jury-central.lodylands.com/ampcr-pratique/fiches/2) | [télécharger](https://jury-central.lodylands.com/ampcr-pratique/fiches/2/telecharger) | ~35 200 mots : 44 lignes, 39 procédures, 8 dossiers |
| 3 — Câblage et installation physique | PR13–PR18 · EX03 | [/fiches/3](https://jury-central.lodylands.com/ampcr-pratique/fiches/3) | [télécharger](https://jury-central.lodylands.com/ampcr-pratique/fiches/3/telecharger) | ~19 300 mots : 34 lignes, 17 procédures, 7 dossiers |
| 4 — Réseau | PR19–PR25 · EX04 | [/fiches/4](https://jury-central.lodylands.com/ampcr-pratique/fiches/4) | [télécharger](https://jury-central.lodylands.com/ampcr-pratique/fiches/4/telecharger) | ~31 900 mots : 32 lignes, 28 procédures, 8 dossiers |
| 5 — Méthode d'intervention | PR26–PR29 | [/fiches/5](https://jury-central.lodylands.com/ampcr-pratique/fiches/5) | [télécharger](https://jury-central.lodylands.com/ampcr-pratique/fiches/5/telecharger) | ~19 100 mots : 25 situations, 17 procédures, 10 modèles remplis, 6 dossiers |
| 6 — Synthèse et épreuve écrite | PR30 · EX05 · EX06 | [/fiches/6](https://jury-central.lodylands.com/ampcr-pratique/fiches/6) | [télécharger](https://jury-central.lodylands.com/ampcr-pratique/fiches/6/telecharger) | ~20 600 mots : méthode d'examen, 28 lignes transversales, 11 dossiers intégrés /20, laboratoire PR30 /100 |

## Ce qui a été fait
- **Six modules** : la découpe suit les six modules du programme du propriétaire. Le parcours installé n'en a que cinq : les fiches 5 et 6 sont donc toutes deux proposées à la fin du module P5.
- **Format de chaque fiche** : il suit le ticket.
  - Démarche en 60 s, puis une grande matrice des pannes.
  - Procédures selon le patron en 9 rubriques : symptômes, causes, questions et sécurité, diagnostic SI/SINON, confirmation, correction, validation, réponse d'examen modèle, pièges.
  - Outils et commandes avec des sorties commentées.
  - Dossiers d'examen résolus avec une réponse rédigée.
  - Pièges et checklist « diagnostiquer, agir, justifier, contrôler ».
  - Renvois théoriques brefs.
- **Aucun doublon** : chaque procédure est rattachée à une seule fiche. Les autres fiches y renvoient par un lien vers son ancre. Les 553 liens ont été contrôlés et aucune ancre n'est cassée.
- **Contenu** : il est versionné en fragments HTML dans `app/v1/ampcr_fiches/f<N>/`. Une fiche n'apparaît que si son contenu existe, ce qui a permis la livraison incrémentale. Rien n'est stocké en base.
- **Code** :
  - `app/v1/ampcr_fiches.py` ;
  - routes `/ampcr-pratique/fiches`, `/fiches/{n}`, `/fiches/{n}/telecharger` ;
  - templates `ampcr_fiche.html`, `ampcr_fiche_standalone.html`, `ampcr_fiches_index.html`, `_ampcr_fiches_list.html` ;
  - CSS `app/static/css/fiches.css` (écran, mobile, impression A4) ;
  - liens ajoutés dans `ampcr_pratique_home.html`.
- **Téléchargement** : il produit un fichier HTML unique, avec le CSS inclus et sans script ni feuille externe.
  - Les liens internes deviennent des ancres locales.
  - Les liens vers d'autres fiches deviennent des URL complètes du site.
- **Impression** : `@page A4`, chaque grande partie commence sur une nouvelle page, les blocs et les lignes de tableau ne sont pas coupés, le rendu est en noir et blanc et aucun bouton n'est imprimé.
- **Mobile** : les matrices de 4 colonnes ou plus s'affichent en cartes, chaque cellule portant le nom de sa colonne.

## Tests
- `tests/test_ticket302_fiches_depannage.py` (3 tests) et les tests #192 du parcours pratique : **42 passed**.
- `ruff` : aucune erreur sur le code ajouté.
- Script de contrôle de chaque fiche : balises équilibrées, ids uniques, ancres internes et entre fiches, aucun style inline, aucun script, aucune image. Les six fiches sont **OK**.
- Après chaque installation : `/health` ok, et chaque page et chaque téléchargement renvoient HTTP 200.
- La suite complète n'a pas été lancée : le ticket demande des tests ciblés.
- Le rendu PDF n'a pas pu être vérifié : aucun navigateur headless n'est installé sur le serveur. Il faut faire un test « Imprimer / PDF » à la main.

## Limites et points à vérifier
- Les fiches ont été rédigées par des agents à partir des cours du dépôt, des consignes officielles et des tickets. Elles n'ont pas été relues ligne à ligne par un humain.
- PR27 à PR30 et EX05/EX06 ne sont pas encore publiés. Les fiches 5 et 6 s'appuient donc sur leurs tickets (#226 à #229, #201, #234).
- Points à vérifier, cités de mémoire et signalés comme tels dans les fiches :
  - codes POST des fabricants (exemples indicatifs, « consulter le manuel ») ;
  - le code 55 des cartes ASUS ;
  - certains libellés exacts de messages Windows en français ;
  - l'écran d'arrêt noir des Windows 11 récents ;
  - les filières de recyclage Recupel et Bebat ;
  - OM5, ajouté alors qu'il n'est pas dans le tableau du cours.
- La durée de l'épreuve ne figure pas dans la consigne officielle. La fiche 6 renvoie à l'horaire publié par le Jury.
- Le ticket #299 a été interrompu. Son travail partiel est sauvegardé sur `feature/299-lisibilite-consignes-examens` (commit WIP `e684e6f`, non testé) et sera repris ensuite.

## Vérification manuelle
1. Ouvrir https://jury-central.lodylands.com/ampcr-pratique : l'encadré « Fiches de dépannage » doit lister les six fiches, et chaque module doit afficher sa fiche en fin de carte.
2. Ouvrir une fiche, puis « Télécharger HTML ». Ouvrir le fichier hors connexion : la mise en forme doit être intacte.
3. Lancer « Imprimer / PDF » en A4 : aucun bouton ne doit apparaître, et les tableaux et encadrés ne doivent pas être coupés.
4. Sur mobile, les matrices doivent s'afficher en cartes lisibles.
