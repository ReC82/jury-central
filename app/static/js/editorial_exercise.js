/*
 * Jury Central — widget générique des exercices éditoriaux structurés (ticket #17).
 *
 * Un bloc `.editorial-exercise-block` porte `data-verify-url` (POST accepte
 * {exercise_id, answer}, voir app/practice.py et app/editorial_exercise.py) et
 * `data-items` (JSON, représentation publique — jamais la réponse correcte). Ce fichier
 * construit un composant par item selon son `type` : première tranche (ticket #17) :
 * single_choice, true_false, short_answer. Aucune correction n'est présente dans le DOM
 * avant l'appel de vérification ; aucun rechargement de page.
 */

async function submitEditorialAnswer(verifyUrl, exerciseId, answer) {
    let response;
    try {
        response = await fetch(verifyUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ exercise_id: exerciseId, answer: String(answer) }),
        });
    } catch (networkError) {
        return null;
    }
    if (!response.ok) {
        return null;
    }
    return response.json();
}

function renderEditorialCorrection(resultBox, result) {
    resultBox.innerHTML = "";

    const verdict = document.createElement("p");
    verdict.className = "fw-semibold mb-1 " + (result.correct ? "text-success" : "text-danger");
    verdict.textContent = result.correct ? "✓ Correct" : "✗ Incorrect";
    resultBox.appendChild(verdict);

    if (!result.correct && result.correct_answer) {
        const expectedLabel = document.createElement("p");
        expectedLabel.className = "small text-muted mb-1 fw-semibold";
        expectedLabel.textContent = "Réponse attendue :";
        resultBox.appendChild(expectedLabel);

        const expectedBody = document.createElement("div");
        expectedBody.className = "small mb-1";
        resultBox.appendChild(expectedBody);
        renderRichContent(expectedBody, result.correct_answer_html || result.correct_answer);
    }

    if (result.explanation) {
        const explanationBody = document.createElement("div");
        explanationBody.className = "small text-muted";
        resultBox.appendChild(explanationBody);
        renderRichContent(explanationBody, result.explanation_html || result.explanation);
    }

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
            Array.from(controls.children).forEach((child) => {
                child.disabled = true;
            });
            onAnswer(index);
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
    button.textContent = "Vérifier";
    button.addEventListener("click", () => {
        if (!input.value.trim()) {
            return;
        }
        input.disabled = true;
        button.disabled = true;
        onAnswer(input.value);
    });

    controls.appendChild(input);
    controls.appendChild(button);
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

    const onAnswer = async (answer) => {
        const result = await submitEditorialAnswer(verifyUrl, item.exercise_id, answer);
        if (!result) {
            return;
        }
        renderEditorialCorrection(resultBox, result);
    };

    if (item.type === "single_choice" || item.type === "true_false") {
        card.appendChild(buildChoiceControl(item, onAnswer));
    } else if (item.type === "short_answer") {
        card.appendChild(buildShortAnswerControl(item, onAnswer));
    } else {
        // Type non pris en charge par cette version du widget (ex. long_answer,
        // classification, ordering — tickets suivants) : pas de contrôle, pas d'appel.
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
