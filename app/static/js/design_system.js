/*
 * Jury Central — Design System (interactions)
 *
 * Ces fonctions opèrent uniquement sur le HTML déjà rendu (jamais sur le contenu
 * pédagogique lui-même) : elles habillent les tableaux, les citations et les exercices
 * rédigés pour les rendre conformes à docs/UI_GUIDELINES.md, de façon générique et
 * réutilisable par toute future UAA qui suit les mêmes conventions Markdown.
 */

function wrapBlockquotesAsWarningCards(root) {
    root.querySelectorAll("blockquote").forEach((blockquote) => {
        const card = document.createElement("div");
        card.className = "jc-card jc-card--warning jc-card--inline";

        const header = document.createElement("div");
        header.className = "jc-card-header";
        header.innerHTML =
            '<span class="jc-card-icon" aria-hidden="true">⚠️</span>' +
            '<span class="jc-card-label">Attention</span>';

        const body = document.createElement("div");
        body.className = "jc-card-body";
        while (blockquote.firstChild) {
            body.appendChild(blockquote.firstChild);
        }

        card.appendChild(header);
        card.appendChild(body);
        blockquote.replaceWith(card);
    });
}

function wrapTablesResponsively(root) {
    root.querySelectorAll("table").forEach((table) => {
        if (table.closest(".table-responsive")) {
            return;
        }
        // Bordures, padding et alignement des cellules sont gérés par design-system.css
        // (.content-markdown table ...) plutôt que par les classes utilitaires Bootstrap,
        // pour un rendu homogène indépendant de la version de Bootstrap chargée par CDN.
        table.classList.add("table", "align-middle");
        const wrapper = document.createElement("div");
        wrapper.className = "table-responsive";
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
    });
}

function makeEmptyCellsEditable(root) {
    root.querySelectorAll("table td").forEach((cell) => {
        if (cell.children.length > 0 || cell.textContent.trim() !== "") {
            return;
        }
        const input = document.createElement("input");
        input.type = "text";
        input.className = "jc-fill-input";
        input.setAttribute("aria-label", "Complète cette cellule");
        cell.appendChild(input);
    });
}

/*
 * Point d'entrée unique du rendu de contenu riche (voir app/static/js/rich_content.js) :
 * habille tout le HTML déjà présent dans `root` (rendu Markdown côté serveur — tableaux,
 * citations, cellules à compléter), qu'il s'agisse du contenu d'un cours affiché au
 * chargement de la page, ou de contenu inséré dynamiquement ensuite (question de quiz,
 * énoncé d'exercice généré, correction) — même traitement partout, aucune duplication.
 */
function enhanceRichContent(root) {
    wrapBlockquotesAsWarningCards(root);
    wrapTablesResponsively(root);
    makeEmptyCellsEditable(root);
}

/* --- Exercices rédigés : ne jamais afficher la correction immédiatement --- */

function insertRevealControl(nodesToHide, { withAnswerField, buttonLabel }) {
    if (nodesToHide.length === 0) {
        return;
    }
    const anchor = nodesToHide[0];

    const controls = document.createElement("div");
    controls.className = "jc-exercise-controls";

    let textarea = null;
    if (withAnswerField) {
        const label = document.createElement("label");
        label.className = "form-label small text-muted";
        label.textContent = "Ta réponse (comparaison libre, non vérifiée automatiquement)";
        textarea = document.createElement("textarea");
        textarea.className = "jc-exercise-answer form-control mb-2";
        textarea.setAttribute("aria-label", "Ta réponse");
        controls.appendChild(label);
        controls.appendChild(textarea);
    }

    const button = document.createElement("button");
    button.type = "button";
    button.className = "btn btn-outline-primary btn-sm jc-exercise-reveal-btn";
    button.textContent = buttonLabel;

    const wrapper = document.createElement("div");
    wrapper.className = "jc-exercise-correction d-none";
    nodesToHide.forEach((node) => wrapper.appendChild(node));

    button.addEventListener("click", () => {
        wrapper.classList.remove("d-none");
        button.disabled = true;
        button.textContent = "Correction affichée";
    });

    controls.appendChild(button);
    anchor.before(controls);
    controls.after(wrapper);
}

function groupIntoSegments(children) {
    const segments = [];
    let current = [];
    children.forEach((node) => {
        const isBoundary = node.tagName === "H2" || node.tagName === "HR";
        if (isBoundary && current.length > 0) {
            segments.push(current);
            current = [];
        }
        current.push(node);
    });
    if (current.length > 0) {
        segments.push(current);
    }
    return segments.length > 0 ? segments : [children];
}

function hideExerciseSegment(segment) {
    const [first] = segment;
    if (!first) {
        return;
    }

    const isCorrectionHeading =
        (first.tagName === "H1" || first.tagName === "H2") && /correction/i.test(first.textContent);
    if (isCorrectionHeading) {
        insertRevealControl(segment, {
            withAnswerField: false,
            buttonLabel: "Afficher la correction",
        });
        return;
    }

    const correctionStart = segment.findIndex(
        (node, index) => index > 0 && /correction\s*:/i.test(node.textContent) && node.querySelector("strong")
    );
    if (correctionStart === -1) {
        return;
    }
    insertRevealControl(segment.slice(correctionStart), {
        withAnswerField: true,
        buttonLabel: "Afficher la correction",
    });
}

function splitExerciseCorrections() {
    document.querySelectorAll(".jc-card--exercise .content-markdown, .jc-card--exam .content-markdown")
        .forEach((container) => {
            const segments = groupIntoSegments(Array.from(container.children));
            segments.forEach(hideExerciseSegment);
        });
}

/* --- Progression de lecture de la leçon --- */

function initLessonProgress() {
    const bar = document.querySelector(".jc-lesson-progress-bar");
    if (!bar) {
        return;
    }
    const update = () => {
        const doc = document.documentElement;
        const scrollable = doc.scrollHeight - doc.clientHeight;
        const ratio = scrollable > 0 ? Math.min(1, Math.max(0, window.scrollY / scrollable)) : 0;
        bar.style.width = `${Math.round(ratio * 100)}%`;
    };
    document.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
    update();
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".content-markdown").forEach(enhanceRichContent);
    splitExerciseCorrections();
    initLessonProgress();
});
