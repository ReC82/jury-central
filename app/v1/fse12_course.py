"""Contenu de cours — FSE12 « Le budget de l'État » (ticket #99, cahier des charges
détaillé).

Même structure que FSE01-FSE11 : 1. Ce que tu dois savoir faire à l'examen —
2. Théorie progressive — 3. Définitions importantes — 4. Méthode étape par étape —
5. Exemples commentés — 6. Mauvaises réponses comparées aux bonnes — 7. Pièges et erreurs
fréquentes — 8. Exercices guidés (corrigés masqués par défaut) — 9. Corrigés très
expliqués — 10. Fiche mémo.

Périmètre strict (ticket #96/#99, programme p. 61) : l'IPP n'est nommée QUE comme catégorie
de recette possible — aucune déclaration, aucun calcul ni mécanisme d'imposition personnel
n'est enseigné ni évalué ici (exclusion explicite du ticket #96, confirmée par le ticket
#99). Les calculs portent uniquement sur les données fictives du tableau fourni."""

from app.v1.fse12_content import FSE12_BUDGET_TEXT

from app.v1.fse_course_sections import build_course_sections


def fse12_course_markdown() -> str:
    return f"""# FSE12 — Le budget de l'État

## 1. Ce que tu dois savoir faire à l'examen

Tu dois être capable de classer des recettes et des dépenses de l'État selon leur type, et \
de calculer le total des recettes, le total des dépenses et le solde budgétaire à partir de \
données fournies. **L'IPP n'est ici qu'un nom de catégorie de recette : aucun calcul \
d'impôt personnel n'est jamais demandé.**

**Prérequis** : ce cours réutilise la notion de sécurité sociale comme destination d'une \
partie des dépenses (vue plus en détail en FSE13-14).

## 2. Théorie progressive

L'État perçoit des **recettes** de plusieurs types : les **recettes fiscales** (impôts, \
comme la TVA, les accises ou l'impôt des personnes physiques — l'IPP), les **recettes \
parafiscales** (cotisations sociales versées par les travailleurs et les employeurs) et les \
**recettes non fiscales** (ex. revenus du patrimoine public, comme des participations dans \
des entreprises).

L'État effectue aussi des **dépenses** de plusieurs types : les **dépenses de \
fonctionnement** (faire tourner les administrations), les **dépenses d'investissement** \
(construire ou financer des infrastructures) et les **dépenses de transfert** (verser de \
l'argent à d'autres, notamment via la sécurité sociale).

La différence entre le total des recettes et le total des dépenses s'appelle le **solde \
budgétaire**. Si les dépenses dépassent les recettes, le solde est négatif : c'est un \
**déficit**. Les déficits accumulés au fil des années forment la **dette publique** : \
l'ensemble de ce que l'État doit encore rembourser. Le paiement des **intérêts sur la \
dette** est lui-même une dépense qui s'ajoute aux autres.

## 3. Définitions importantes

- **Recette fiscale** : recette provenant d'un impôt (TVA, accises, IPP...).
- **Recette parafiscale** : recette provenant des cotisations sociales.
- **Recette non fiscale** : recette ne provenant ni d'un impôt ni de cotisations (ex. \
revenus du patrimoine public).
- **Dépense de fonctionnement** : dépense pour faire fonctionner les administrations.
- **Dépense d'investissement** : dépense pour financer des infrastructures.
- **Dépense de transfert** : dépense versée à d'autres (ex. sécurité sociale).
- **Solde budgétaire** : différence entre le total des recettes et le total des dépenses.
- **Déficit** : solde budgétaire négatif (dépenses supérieures aux recettes).
- **Dette publique** : ensemble des déficits accumulés, que l'État doit encore rembourser.

## 4. Méthode étape par étape

Face à un tableau de recettes/dépenses, procède dans cet ordre :

1. Classe chaque ligne du tableau comme **recette** (fiscale/parafiscale/non fiscale) ou \
**dépense** (fonctionnement/investissement/transfert).
2. Additionne séparément le **total des recettes** et le **total des dépenses**.
3. Calcule le **solde budgétaire** = total des recettes − total des dépenses.
4. Si le solde est négatif, nomme-le explicitement **déficit** ; explique que les déficits \
accumulés forment la **dette**.

## 5. Exemples commentés

### Exemple 1 — Classer la recette 3 (IPP)

{FSE12_BUDGET_TEXT.splitlines()[5]}

**Analyse commentée :** l'IPP est un impôt : c'est une **recette fiscale**. Aucun calcul \
d'impôt personnel n'est demandé ici — seule sa nature de recette compte.

### Exemple 2 — Classer la dépense 3 (transferts sécu)

{FSE12_BUDGET_TEXT.splitlines()[12]}

**Analyse commentée :** cette dépense consiste à verser de l'argent à la sécurité sociale, \
pour financer des prestations : c'est une **dépense de transfert**.

### Exemple 3 — Calculer le solde budgétaire

D'après le tableau, le total des recettes est de 1 100 (400+50+350+280+20) et le total des \
dépenses est de 1 200 (150+100+700+70+180).

**Analyse commentée :** solde budgétaire = 1 100 − 1 200 = **−100**. Le solde étant négatif, \
il s'agit d'un **déficit** de 100.

## 6. Mauvaises réponses comparées aux bonnes

- ❌ **Mauvaise réponse** : « L'IPP est une cotisation sociale. » → confond impôt (recette \
fiscale) et cotisation (recette parafiscale).
- ✅ **Bonne réponse** : « L'IPP est un impôt, donc une recette fiscale ; les cotisations \
sociales sont une recette parafiscale distincte. »

- ❌ **Mauvaise réponse** (calcul du solde) : « Le solde est de 2 300 » (en additionnant \
recettes et dépenses au lieu de les soustraire). → confond addition et soustraction dans le \
calcul du solde.
- ✅ **Bonne réponse** : « Solde = total des recettes − total des dépenses = 1 100 − 1 200 = \
−100, soit un déficit. »

## 7. Pièges et erreurs fréquentes

- **Confondre recette fiscale et recette parafiscale** : l'impôt (fiscale) et la cotisation \
sociale (parafiscale) ont des origines différentes.
- **Oublier qu'un solde négatif se nomme un déficit**, et qu'un déficit accumulé forme la \
dette.
- **Chercher à calculer un impôt personnel (IPP)** : ce cours ne l'enseigne jamais — l'IPP \
n'est qu'une catégorie de recette à classer.
- **Confondre dépense d'investissement et dépense de fonctionnement** : l'investissement \
finance des infrastructures durables, le fonctionnement fait tourner l'administration au \
quotidien.

## 8. Exercices guidés

<details>
<summary>Exercice 1 — Classer une recette et une dépense (essaie avant de regarder la \
correction)</summary>

Classe la recette 5 (revenus du patrimoine public) et la dépense 4 (intérêts sur la dette). \
Justifie chaque réponse.

<details>
<summary>Voir la correction expliquée</summary>

La recette 5 est une **recette non fiscale** : elle ne provient ni d'un impôt ni de \
cotisations sociales, mais de participations publiques. La dépense 4 est une dépense liée \
au remboursement de la **dette publique** (paiement des intérêts), distincte du \
fonctionnement ou de l'investissement.

Ce corrigé fonctionne parce qu'il applique directement les catégories définies, sans \
mélanger recette et dépense.
</details>
</details>

<details>
<summary>Exercice 2 — Calculer le solde (essaie avant de regarder la correction)</summary>

À partir du tableau, calcule le total des recettes, le total des dépenses, puis le solde \
budgétaire. Le résultat est-il un déficit ou un excédent ?

<details>
<summary>Voir la correction expliquée</summary>

Total des recettes : 400 + 50 + 350 + 280 + 20 = 1 100. Total des dépenses : 150 + 100 + 700 \
+ 70 + 180 = 1 200. Solde budgétaire : 1 100 − 1 200 = −100. Le solde étant négatif, il \
s'agit d'un **déficit** de 100.

Ce corrigé fonctionne parce qu'il détaille chaque étape du calcul (addition des recettes, \
addition des dépenses, soustraction) plutôt que de donner seulement le résultat final.
</details>
</details>

## 9. Corrigés très expliqués

**Question :** « Pourquoi un déficit répété d'année en année augmente-t-il la dette \
publique ? »

**Corrigé expliqué :** chaque déficit correspond à un montant que l'État a dépensé sans \
l'avoir couvert par ses recettes de l'année : ce montant doit être emprunté. La dette \
publique est l'accumulation de tous ces emprunts non encore remboursés. Plus les déficits se \
répètent, plus la dette augmente — et plus les intérêts à payer sur cette dette \
(eux-mêmes une dépense) augmentent à leur tour, ce qui peut rendre l'équilibre budgétaire \
plus difficile à atteindre les années suivantes.

Ce corrigé fonctionne parce qu'il relie explicitement déficit, emprunt, dette et intérêts \
dans un raisonnement enchaîné, plutôt que de les présenter comme des notions séparées.

## 10. Fiche mémo

- Recettes : fiscales (impôts, dont l'IPP, nommée sans calcul), parafiscales (cotisations \
sociales), non fiscales (ex. patrimoine public).
- Dépenses : fonctionnement, investissement, transfert (ex. sécurité sociale).
- Solde budgétaire = total des recettes − total des dépenses.
- Solde négatif = déficit ; déficits accumulés = dette publique ; la dette génère des \
intérêts, eux-mêmes une dépense.
- L'IPP n'est jamais calculée ni déclarée dans ce cours : seule sa nature de recette fiscale \
compte.
"""


def fse12_course_sections() -> list[tuple[str, str]]:
    """Sections (titre, Markdown) du cours FSE12 — refonte pédagogique et visuelle
    (ticket #105), voir `app.v1.fse_course_sections.build_course_sections`."""
    return build_course_sections("FSE12", fse12_course_markdown())
