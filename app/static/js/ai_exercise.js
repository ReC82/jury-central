/*
 * Jury Central — Widget d'exercice généré et corrigé par IA (ticket #10, complément IA).
 *
 * Ne contient et ne transmet jamais de clé API : ce widget n'appelle que
 * /practice/api/ai/generate et /practice/api/ai/correct, exécutés côté serveur.
 */

async function postJsonWithDetail(url, body) {
    let response;
    try {
        response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });
    } catch (networkError) {
        return { ok: false, error: "Connexion impossible. Vérifie ta connexion et réessaie." };
    }

    let data = null;
    try {
        data = await response.json();
    } catch (parseError) {
        data = null;
    }

    if (!response.ok) {
        const detail = (data && data.detail) || "Une erreur est survenue.";
        return { ok: false, error: detail };
    }
    return { ok: true, data };
}

function aiExerciseSetLoading(widget, loading) {
    widget.querySelector(".ai-exercise-loading").classList.toggle("d-none", !loading);
    widget.querySelectorAll("button").forEach((button) => {
        button.disabled = loading;
    });
}

function aiExerciseShowError(widget, message) {
    const errorBox = widget.querySelector(".ai-exercise-error");
    errorBox.textContent = message;
    errorBox.classList.remove("d-none");
}

function aiExerciseClearError(widget) {
    const errorBox = widget.querySelector(".ai-exercise-error");
    errorBox.textContent = "";
    errorBox.classList.add("d-none");
}

async function generateAIExercise(button) {
    const widget = button.closest(".ai-exercise-widget");
    const blockId = parseInt(widget.dataset.blockId, 10);
    const difficulty = widget.querySelector(".ai-exercise-difficulty").value;

    aiExerciseClearError(widget);
    aiExerciseSetLoading(widget, true);

    const result = await postJsonWithDetail("/practice/api/ai/generate", {
        block_id: blockId,
        difficulty: difficulty,
    });

    aiExerciseSetLoading(widget, false);

    if (!result.ok) {
        aiExerciseShowError(widget, result.error);
        return;
    }

    const data = result.data;
    widget.dataset.exerciseType = data.exercise_type;
    widget.dataset.difficulty = data.difficulty;
    widget.dataset.statement = data.statement;
    widget.dataset.statementToken = data.statement_token;

    widget.querySelector(".ai-exercise-body").classList.remove("d-none");
    renderRichContent(
        widget.querySelector(".ai-exercise-statement"),
        data.statement_html || data.statement
    );
    widget.querySelector(".ai-exercise-answer").value = "";

    const resultBox = widget.querySelector(".ai-exercise-result");
    resultBox.classList.add("d-none");
    resultBox.innerHTML = "";
}

function aiExerciseAddList(resultBox, title, items, className) {
    if (!items || items.length === 0) {
        return;
    }
    const heading = document.createElement("div");
    heading.className = "small fw-semibold mt-2";
    heading.textContent = title;
    resultBox.appendChild(heading);

    const list = document.createElement("ul");
    list.className = `small ${className}`;
    items.forEach((text) => {
        const item = document.createElement("li");
        item.textContent = text;
        list.appendChild(item);
    });
    resultBox.appendChild(list);
}

function renderAICorrection(widget, correction) {
    const resultBox = widget.querySelector(".ai-exercise-result");
    resultBox.innerHTML = "";

    const appreciation = document.createElement("div");
    appreciation.className = "fw-semibold mb-2";
    renderRichContent(appreciation, correction.appreciation_html || correction.appreciation);
    resultBox.appendChild(appreciation);

    if (correction.score !== null && correction.score !== undefined) {
        const score = document.createElement("div");
        score.className = "small text-muted mb-2";
        score.textContent = `Score : ${correction.score} / ${correction.max_score}`;
        resultBox.appendChild(score);
    }

    aiExerciseAddList(resultBox, "Ce qui est correct", correction.correct_points, "text-success");
    aiExerciseAddList(resultBox, "Erreurs ou éléments manquants", correction.errors, "text-danger");

    if (correction.expected_answer_explained) {
        const expectedLabel = document.createElement("div");
        expectedLabel.className = "small fw-semibold mt-2";
        expectedLabel.textContent = "Réponse attendue";
        resultBox.appendChild(expectedLabel);

        const expectedBody = document.createElement("div");
        expectedBody.className = "small";
        renderRichContent(
            expectedBody,
            correction.expected_answer_explained_html || correction.expected_answer_explained
        );
        resultBox.appendChild(expectedBody);
    }

    resultBox.classList.remove("d-none");
}

async function correctAIExercise(button) {
    const widget = button.closest(".ai-exercise-widget");
    const answerInput = widget.querySelector(".ai-exercise-answer");

    if (!answerInput.value.trim()) {
        aiExerciseShowError(widget, "Merci d'entrer une réponse avant de demander une correction.");
        return;
    }

    aiExerciseClearError(widget);
    aiExerciseSetLoading(widget, true);

    const result = await postJsonWithDetail("/practice/api/ai/correct", {
        block_id: parseInt(widget.dataset.blockId, 10),
        exercise_statement: widget.dataset.statement,
        exercise_type: widget.dataset.exerciseType,
        difficulty: widget.dataset.difficulty,
        statement_token: widget.dataset.statementToken,
        answer: answerInput.value,
    });

    aiExerciseSetLoading(widget, false);

    if (!result.ok) {
        aiExerciseShowError(widget, result.error);
        return;
    }

    renderAICorrection(widget, result.data);
}

document.addEventListener("click", (event) => {
    if (event.target.classList.contains("ai-exercise-generate-btn")) {
        generateAIExercise(event.target);
    }
    if (event.target.classList.contains("ai-exercise-correct-btn")) {
        correctAIExercise(event.target);
    }
});
