# Intégration automatique d'une UAA dans Jury Central

Tu travailles sur le projet Jury Central.

Avant toute chose :

1. Lis entièrement la documentation présente dans le dossier `docs/`.
2. Lis en particulier :
   - ARCHITECTURE.md
   - current_state.md
   - development.md
   - IMPORT_WORKFLOW.md
   - content_workflow.md
3. Respecte strictement les conventions déjà utilisées dans le projet.
4. Analyse le code existant avant de modifier quoi que ce soit.

---

## Sources des cours

Toutes les sources officielles se trouvent dans :

docs/sources_cours/

Chaque UAA possède :

- cours.html
- cours.pdf
- metadata.yaml

Le HTML est toujours la source principale.

Le PDF sert uniquement à vérifier que le contenu n'a pas été perdu.

---

## Travail demandé

Je veux intégrer complètement la prochaine UAA dans Jury Central.

Tu dois :

- analyser l'UAA
- analyser l'UAA1 déjà intégrée
- reproduire exactement la même architecture
- créer automatiquement tous les objets nécessaires
- créer les pages
- créer les liens
- créer les menus
- créer les chapitres
- créer les exercices
- créer les quiz
- créer les fiches mémo
- créer les éventuelles illustrations SVG
- intégrer le contenu dans la base de données ou le format utilisé par le projet
- respecter le design actuel

---

## Important

Ne reconstruis jamais le cours.

Le cours existe déjà.

Tu dois uniquement transformer le HTML existant en contenu utilisable par Jury Central.

Ne résume jamais.

Ne reformule jamais.

Ne supprime jamais de contenu.

---

## Workflow

Travaille entièrement de manière autonome.

Si une information manque :

- regarde l'UAA précédente
- regarde les modèles Django
- regarde les templates
- regarde les migrations
- regarde les vues
- regarde les composants
- regarde la documentation

Déduis la solution.

Ne pose aucune question si la réponse peut être trouvée dans le projet.

---

## Vérifications obligatoires

Avant de terminer :

- vérifier que le projet compile
- vérifier que toutes les routes fonctionnent
- vérifier que les pages s'affichent
- vérifier que les menus sont corrects
- vérifier les liens
- corriger automatiquement les erreurs éventuelles

---

## Git

Lorsque tout fonctionne :

- faire un commit propre
- rester sur la branche actuelle

---

Tu ne dois interrompre ton travail que lorsqu'il est complètement terminé.