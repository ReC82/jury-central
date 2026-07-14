/*
 * Jury Central — renderer unique de contenu riche (VS003.1).
 *
 * Un seul point d'entrée pour insérer du HTML déjà rendu côté serveur (voir
 * app/content.py::render_markdown) dans la page : cours, quiz, corrections d'exercices,
 * fiches mémo utilisent tous cette même fonction plutôt que de dupliquer la logique
 * d'affichage. Le contenu inséré est déjà rendu (tableaux, listes, MathJax) — jamais du
 * texte brut ni une reformulation en JS.
 *
 * `container` reçoit `html` puis :
 *   - le même traitement que le contenu Markdown des cours (tableaux responsives, cellules
 *     éditables, citations transformées en WarningCard — voir design_system.js) ;
 *   - un nouveau passage MathJax scopé à `container` (MathJax ne rescane pas
 *     automatiquement le contenu inséré après le chargement initial de la page).
 */
function renderRichContent(container, html) {
    if (!container) {
        return;
    }
    container.classList.add("content-markdown");
    container.innerHTML = html || "";

    if (typeof enhanceRichContent === "function") {
        enhanceRichContent(container);
    }

    if (window.MathJax && typeof window.MathJax.typesetPromise === "function") {
        window.MathJax.typesetPromise([container]).catch(() => {
            // Rendu MathJax best-effort : une erreur ne doit jamais bloquer l'affichage
            // du contenu lui-même (déjà inséré ci-dessus).
        });
    }
}
