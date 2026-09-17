/*
 * Jury Central — widget générique des exercices éditoriaux structurés (ticket #17,
 * étendu aux #21/#29).
 *
 * Un bloc `.editorial-exercise-block` porte `data-verify-url` (POST accepte
 * {exercise_id, answer}, voir app/practice.py et app/editorial_exercise.py) et
 * `data-items` (JSON, représentation publique — jamais la réponse correcte, jamais la
 * grille de correction IA). Ce fichier construit un composant par item selon son `type` :
 * single_choice, true_false, short_answer (ticket #17), classification, ordering
 * (ticket #21), long_answer, diagnostic, vocabulary (ticket #29). Aucune correction n'est
 * présente dans le DOM avant l'appel de vérification ; aucun rechargement de page.
 *
 * classification/ordering envoient une réponse `list[int]` (et non une chaîne) : voir
 * `answer: Any` côté serveur (app/practice.py). L'interaction est exclusivement au clic
 * (boutons de catégorie pour classification, boutons monter/descendre pour ordering) —
 * aucun glisser-déposer requis, pour rester utilisable au clavier comme au tactile.
 *
 * `item.requires_ai` (ticket #29, jamais un secret — indique seulement la MODALITÉ de
 * correction) détermine le libellé du bouton (« Vérifier » local / « Corriger » IA) et le
 * comportement en cas d'échec réseau/503/502 : le champ de saisie reste toujours
 * utilisable, un message clair s'affiche, jamais la solution, jamais un plantage silencieux.
 */

async function submitEditorialAnswer(verifyUrl, exerciseId, answer) {
    let response;
    try {
        response = await fetch(verifyUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                exercise_id: exerciseId,
                answer: Array.isArray(answer) ? answer : String(answer),
            }),
        });
    } catch (networkError) {
        return { ok: false, status: 0 };
    }

    let body = null;
    try {
        body = await response.json();
    } catch (parseError) {
        body = null;
    }

    if (!response.ok) {
        return { ok: false, status: response.status, detail: body && body.detail };
    }
    return { ok: true, result: body };
}

function renderEditorialList(resultBox, title, entries) {
    if (!entries || !entries.length) {
        return;
    }
    const label = document.createElement("p");
    label.className = "small fw-semibold mb-1 mt-2";
    label.textContent = title;
    resultBox.appendChild(label);

    const list = document.createElement("ul");
    list.className = "small mb-1 ps-3";
    entries.forEach((entry) => {
        const item = document.createElement("li");
        item.textContent = entry;
        list.appendChild(item);
    });
    resultBox.appendChild(list);
}

function renderEditorialCorrection(resultBox, result) {
    resultBox.innerHTML = "";
    resultBox.classList.remove("editorial-exercise-unavailable");

    const verdict = document.createElement("p");
    verdict.className = "fw-semibold mb-1 " + (result.correct ? "text-success" : "text-danger");
    let verdictText = result.correct ? "✓ Correct" : "✗ Incorrect";
    if (typeof result.points_awarded === "number" && typeof result.points_max === "number") {
        verdictText += " (" + result.points_awarded + " / " + result.points_max + " points)";
    }
    verdict.textContent = verdictText;
    resultBox.appendChild(verdict);

    renderEditorialList(resultBox, "Points forts :", result.strengths);
    renderEditorialList(resultBox, "Erreurs :", result.errors);
    renderEditorialList(resultBox, "Manquant :", result.missing);

    if (!result.correct && result.correct_answer) {
        const expectedLabel = document.createElement("p");
        expectedLabel.className = "small text-muted mb-1 fw-semibold mt-2";
        expectedLabel.textContent = "Réponse attendue :";
        resultBox.appendChild(expectedLabel);

        const expectedBody = document.createElement("div");
        expectedBody.className = "small mb-1";
        resultBox.appendChild(expectedBody);
        renderRichContent(expectedBody, result.correct_answer_html || result.correct_answer);
    }

    if (result.explanation) {
        const explanationBody = document.createElement("div");
        explanationBody.className = "small text-muted mt-2";
        resultBox.appendChild(explanationBody);
        renderRichContent(explanationBody, result.explanation_html || result.explanation);
    }

    resultBox.classList.remove("d-none");
}

function renderEditorialUnavailable(resultBox, outcome) {
    resultBox.innerHTML = "";
    const message = document.createElement("p");
    message.className = "small text-muted mb-0 editorial-exercise-unavailable";
    if (outcome.status === 503) {
        message.textContent =
            "Correction IA indisponible sur ce serveur pour le moment. Ta réponse n'a pas " +
            "été perdue : réessaie dans un instant.";
    } else if (outcome.status === 404) {
        message.textContent = "Exercice introuvable. Recharge la page et réessaie.";
    } else {
        message.textContent =
            "La correction n'a pas pu être obtenue (problème réseau ou serveur). " +
            "Réessaie dans un instant.";
    }
    resultBox.appendChild(message);
    resultBox.classList.remove("d-none");
}

function buildResultBox() {
    const box = document.createElement("div");
    box.className = "editorial-exercise-result mt-2 d-none";
    return box;
}

function buildChoiceControl(item, onAnswer) {
    const controls = document.createElement("div");
    controls.className = "list-group mb-2 d-print-none";

    item.choices.forEach((choice, index) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "list-group-item list-group-item-action editorial-choice-btn";
        button.textContent = choice;
        button.dataset.index = String(index);
        button.addEventListener("click", () => {
            const buttons = Array.from(controls.children);
            buttons.forEach((child) => {
                child.disabled = true;
            });
            onAnswer(index, () => {
                buttons.forEach((child) => {
                    child.disabled = false;
                });
            });
        });
        controls.appendChild(button);
    });

    return controls;
}

function buildShortAnswerControl(item, onAnswer) {
    const controls = document.createElement("div");
    controls.className = "d-flex flex-wrap gap-2 align-items-start mb-2 d-print-none";

    const input = document.createElement("input");
    input.type = "text";
    input.className = "form-control editorial-short-answer-input";
    input.style.maxWidth = "320px";
    input.setAttribute("aria-label", "Ta réponse");

    const button = document.createElement("button");
    button.type = "button";
    button.className = "btn btn-outline-primary editorial-verify-btn";
    button.textContent = item.requires_ai ? "Corriger" : "Vérifier";
    button.addEventListener("click", () => {
        if (!input.value.trim()) {
            return;
        }
        input.disabled = true;
        button.disabled = true;
        onAnswer(input.value, () => {
            input.disabled = false;
            button.disabled = false;
        });
    });

    controls.appendChild(input);
    controls.appendChild(button);
    return controls;
}

function buildTextareaControl(item, onAnswer) {
    const controls = document.createElement("div");
    controls.className = "mb-2 d-print-none";

    const textarea = document.createElement("textarea");
    textarea.className = "form-control editorial-textarea-input mb-2";
    textarea.rows = 5;
    textarea.setAttribute("aria-label", "Ta réponse");
    controls.appendChild(textarea);

    const actionRow = document.createElement("div");
    actionRow.className = "d-flex align-items-center gap-2";

    const button = document.createElement("button");
    button.type = "button";
    button.className = "btn btn-dark editorial-correct-btn";
    button.textContent = "Corriger";
    actionRow.appendChild(button);

    const loading = document.createElement("span");
    loading.className = "small text-muted d-none";
    loading.textContent = "Un instant…";
    actionRow.appendChild(loading);

    controls.appendChild(actionRow);

    button.addEventListener("click", async () => {
        if (!textarea.value.trim()) {
            return;
        }
        textarea.disabled = true;
        button.disabled = true;
        loading.classList.remove("d-none");
        await onAnswer(textarea.value, () => {
            textarea.disabled = false;
            button.disabled = false;
        });
        loading.classList.add("d-none");
    });

    return controls;
}

function buildClassificationControl(item, onAnswer) {
    const controls = document.createElement("div");
    controls.className = "mb-2 d-print-none";

    const assignment = item.elements.map(() => null);

    const verifyButton = document.createElement("button");
    verifyButton.type = "button";
    verifyButton.className = "btn btn-outline-primary editorial-verify-btn mt-1";
    verifyButton.textContent = "Vérifier";
    verifyButton.disabled = true;

    const groups = [];

    item.elements.forEach((element, elementIndex) => {
        const row = document.createElement("div");
        row.className = "mb-3";

        const label = document.createElement("p");
        label.className = "fw-semibold small mb-1";
        label.textContent = element;
        row.appendChild(label);

        const group = document.createElement("div");
        group.className = "d-flex flex-wrap gap-2";
        group.setAttribute("role", "group");
        group.setAttribute("aria-label", "Catégorie pour " + element);
        groups.push(group);

        item.categories.forEach((category, categoryIndex) => {
            const button = document.createElement("button");
            button.type = "button";
            button.className = "btn btn-outline-secondary btn-sm classification-category-btn";
            button.textContent = category;
            button.addEventListener("click", () => {
                Array.from(group.children).forEach((sibling) => {
                    sibling.classList.remove("active");
                });
                button.classList.add("active");
                assignment[elementIndex] = categoryIndex;
                verifyButton.disabled = assignment.some((value) => value === null);
            });
            group.appendChild(button);
        });

        row.appendChild(group);
        controls.appendChild(row);
    });

    verifyButton.addEventListener("click", () => {
        const allButtons = controls.querySelectorAll("button");
        allButtons.forEach((btn) => {
            btn.disabled = true;
        });
        onAnswer(assignment, () => {
            allButtons.forEach((btn) => {
                btn.disabled = false;
            });
            verifyButton.disabled = assignment.some((value) => value === null);
        });
    });
    controls.appendChild(verifyButton);

    return controls;
}

function buildOrderingControl(item, onAnswer) {
    const controls = document.createElement("div");
    controls.className = "mb-2 d-print-none";

    const list = document.createElement("ol");
    list.className = "list-group list-group-numbered mb-2 editorial-ordering-list";
    controls.appendChild(list);

    // Ordre courant : index originaux dans item.order_items, dans l'ordre affiché.
    let currentOrder = item.order_items.map((_, index) => index);

    function renderList() {
        list.innerHTML = "";
        currentOrder.forEach((originalIndex, position) => {
            const row = document.createElement("li");
            row.className =
                "list-group-item d-flex justify-content-between align-items-center gap-2 flex-wrap";

            const label = document.createElement("span");
            label.className = "flex-grow-1";
            label.textContent = item.order_items[originalIndex];
            row.appendChild(label);

            const buttonGroup = document.createElement("div");
            buttonGroup.className = "btn-group";

            const upButton = document.createElement("button");
            upButton.type = "button";
            upButton.className = "btn btn-outline-secondary btn-sm";
            upButton.textContent = "↑";
            upButton.setAttribute("aria-label", "Monter : " + item.order_items[originalIndex]);
            upButton.disabled = position === 0;
            upButton.addEventListener("click", () => {
                [currentOrder[position - 1], currentOrder[position]] = [
                    currentOrder[position],
                    currentOrder[position - 1],
                ];
                renderList();
            });

            const downButton = document.createElement("button");
            downButton.type = "button";
            downButton.className = "btn btn-outline-secondary btn-sm";
            downButton.textContent = "↓";
            downButton.setAttribute(
                "aria-label",
                "Descendre : " + item.order_items[originalIndex]
            );
            downButton.disabled = position === currentOrder.length - 1;
            downButton.addEventListener("click", () => {
                [currentOrder[position], currentOrder[position + 1]] = [
                    currentOrder[position + 1],
                    currentOrder[position],
                ];
                renderList();
            });

            buttonGroup.appendChild(upButton);
            buttonGroup.appendChild(downButton);
            row.appendChild(buttonGroup);
            list.appendChild(row);
        });
    }
    renderList();

    const verifyButton = document.createElement("button");
    verifyButton.type = "button";
    verifyButton.className = "btn btn-outline-primary editorial-verify-btn";
    verifyButton.textContent = "Vérifier";
    verifyButton.addEventListener("click", () => {
        const allButtons = list.querySelectorAll("button");
        allButtons.forEach((btn) => {
            btn.disabled = true;
        });
        verifyButton.disabled = true;
        onAnswer(currentOrder, () => {
            renderList();
            verifyButton.disabled = false;
        });
    });
    controls.appendChild(verifyButton);

    return controls;
}

function initEditorialExerciseItem(container, verifyUrl, item) {
    const card = document.createElement("div");
    card.className = "border rounded p-3 mb-3 editorial-exercise-item";

    const prompt = document.createElement("div");
    prompt.className = "content-markdown mb-2";
    card.appendChild(prompt);
    renderRichContent(prompt, item.prompt_html || item.prompt);

    const resultBox = buildResultBox();

    const onAnswer = async (answer, reEnable) => {
        const outcome = await submitEditorialAnswer(verifyUrl, item.exercise_id, answer);
        if (!outcome.ok) {
            renderEditorialUnavailable(resultBox, outcome);
            reEnable();
            return;
        }
        renderEditorialCorrection(resultBox, outcome.result);
    };

    if (item.type === "single_choice" || item.type === "true_false") {
        card.appendChild(buildChoiceControl(item, onAnswer));
    } else if (item.type === "short_answer") {
        card.appendChild(buildShortAnswerControl(item, onAnswer));
    } else if (item.type === "classification") {
        card.appendChild(buildClassificationControl(item, onAnswer));
    } else if (item.type === "ordering") {
        card.appendChild(buildOrderingControl(item, onAnswer));
    } else if (
        item.type === "long_answer" ||
        item.type === "diagnostic" ||
        item.type === "vocabulary"
    ) {
        card.appendChild(buildTextareaControl(item, onAnswer));
    } else {
        // Type non pris en charge par cette version du widget : pas de contrôle, pas
        // d'appel — ne devrait jamais arriver pour un item publié (voir la validation
        // stricte à l'auteurisation, app/editorial_exercise.py).
        return;
    }

    card.appendChild(resultBox);
    container.appendChild(card);
}

function initEditorialExerciseBlock(root) {
    let items = [];
    try {
        items = JSON.parse(root.dataset.items || "[]");
    } catch (error) {
        items = [];
    }
    const verifyUrl = root.dataset.verifyUrl;
    items.forEach((item) => initEditorialExerciseItem(root, verifyUrl, item));
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".editorial-exercise-block").forEach(initEditorialExerciseBlock);
});
