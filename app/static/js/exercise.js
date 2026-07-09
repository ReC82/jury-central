function parseAnswer(raw) {
    const trimmed = (raw || "").trim();
    if (trimmed === "") {
        return null;
    }
    if (trimmed.includes("/")) {
        const parts = trimmed.split("/");
        if (parts.length !== 2) {
            return null;
        }
        const numerator = parseFloat(parts[0].replace(",", "."));
        const denominator = parseFloat(parts[1].replace(",", "."));
        if (Number.isNaN(numerator) || Number.isNaN(denominator) || denominator === 0) {
            return null;
        }
        return numerator / denominator;
    }
    const value = parseFloat(trimmed.replace(",", "."));
    return Number.isNaN(value) ? null : value;
}

function checkAnswer(button) {
    const widget = button.closest(".exercise-widget");
    const input = widget.querySelector(".exercise-answer-input");
    const feedback = widget.querySelector(".exercise-feedback");
    const expected = parseFloat(button.dataset.answer);
    const submitted = parseAnswer(input.value);

    if (submitted === null) {
        feedback.textContent = "Merci d'entrer une réponse.";
        feedback.className = "exercise-feedback small mb-2 text-warning";
        return;
    }

    const isCorrect = Math.abs(submitted - expected) < 1e-6;
    feedback.textContent = isCorrect ? "Correct !" : "Incorrect, réessaie.";
    feedback.className = "exercise-feedback small mb-2 " + (isCorrect ? "text-success" : "text-danger");
}

async function newExercise(button) {
    const widget = button.closest(".exercise-widget");
    const generator = widget.dataset.generator;
    const difficulty = widget.dataset.difficulty;

    const response = await fetch(
        `/practice/api/generate?generator=${encodeURIComponent(generator)}&difficulty=${encodeURIComponent(difficulty)}`
    );
    if (!response.ok) {
        return;
    }
    const data = await response.json();

    widget.querySelector(".exercise-statement").textContent = data.statement;
    widget.querySelector(".exercise-answer-input").value = "";

    const feedback = widget.querySelector(".exercise-feedback");
    feedback.textContent = "";
    feedback.className = "exercise-feedback small mb-2";

    widget.querySelector(".exercise-check-btn").dataset.answer = data.answer_value;

    const stepsList = widget.querySelector(".exercise-steps");
    stepsList.innerHTML = "";
    data.solution_steps.forEach((step) => {
        const li = document.createElement("li");
        li.textContent = step;
        stepsList.appendChild(li);
    });

    const details = widget.querySelector("details");
    if (details) {
        details.open = false;
    }
}

document.addEventListener("click", (event) => {
    if (event.target.classList.contains("exercise-check-btn")) {
        checkAnswer(event.target);
    }
    if (event.target.classList.contains("exercise-new-btn")) {
        newExercise(event.target);
    }
});
