async function submitQuizAnswer(blockId, answer) {
    return postJson(`/practice/api/quiz/${blockId}/verify`, { answer: String(answer) });
}

function showQuizFeedback(widget, result) {
    const feedback = widget.querySelector(".quiz-feedback");
    feedback.textContent = result.correct ? "Bonne réponse !" : "Ce n'est pas la bonne réponse.";
    feedback.className = "quiz-feedback small mb-2 " + (result.correct ? "text-success" : "text-danger");

    const explanation = widget.querySelector(".quiz-explanation");
    if (explanation && result.explanation) {
        explanation.textContent = result.explanation;
        explanation.classList.remove("d-none");
    }
}

async function handleQuizChoiceClick(button) {
    const widget = button.closest(".quiz-widget");
    const result = await submitQuizAnswer(widget.dataset.blockId, button.dataset.index);
    if (!result) {
        return;
    }

    widget.querySelectorAll(".quiz-choice-btn").forEach((choiceButton) => {
        choiceButton.classList.remove("list-group-item-success", "list-group-item-danger");
        choiceButton.disabled = true;
    });
    button.classList.add(result.correct ? "list-group-item-success" : "list-group-item-danger");
    if (!result.correct && result.correct_index !== null && result.correct_index !== undefined) {
        const correctButton = widget.querySelector(`.quiz-choice-btn[data-index="${result.correct_index}"]`);
        if (correctButton) {
            correctButton.classList.add("list-group-item-success");
        }
    }
    showQuizFeedback(widget, result);
}

async function handleQuizNumericSubmit(button) {
    const widget = button.closest(".quiz-widget");
    const input = widget.querySelector(".quiz-numeric-input");
    if (!input.value.trim()) {
        return;
    }
    const result = await submitQuizAnswer(widget.dataset.blockId, input.value);
    if (!result) {
        return;
    }
    input.disabled = true;
    button.disabled = true;
    showQuizFeedback(widget, result);
}

document.addEventListener("click", (event) => {
    if (event.target.classList.contains("quiz-choice-btn")) {
        handleQuizChoiceClick(event.target);
    }
    if (event.target.classList.contains("quiz-numeric-check-btn")) {
        handleQuizNumericSubmit(event.target);
    }
});

/* --- Parcours de quiz groupé : une question à la fois, score, recommencer --- */

function appendNextButton(runEl, questionBox) {
    const state = runEl.quizState;
    const nextBtn = document.createElement("button");
    nextBtn.type = "button";
    nextBtn.className = "btn btn-dark btn-sm mt-2 quiz-run-next-btn";
    nextBtn.textContent = state.index + 1 >= state.questions.length ? "Voir le score" : "Question suivante";
    nextBtn.addEventListener("click", () => {
        state.index += 1;
        renderQuizRunQuestion(runEl);
    });
    questionBox.appendChild(nextBtn);
}

function renderQuizRunQuestion(runEl) {
    const state = runEl.quizState;
    const progress = runEl.querySelector(".quiz-run-progress");
    const questionBox = runEl.querySelector(".quiz-run-question");
    const resultBox = runEl.querySelector(".quiz-run-result");

    if (state.index >= state.questions.length) {
        progress.textContent = "";
        questionBox.innerHTML = "";
        resultBox.classList.remove("d-none");
        resultBox.innerHTML = "";

        const scoreP = document.createElement("p");
        scoreP.className = "fw-semibold";
        scoreP.textContent = `Score : ${state.score} / ${state.questions.length}`;

        const restartBtn = document.createElement("button");
        restartBtn.type = "button";
        restartBtn.className = "btn btn-dark btn-sm quiz-run-restart-btn";
        restartBtn.textContent = "Recommencer";

        resultBox.appendChild(scoreP);
        resultBox.appendChild(restartBtn);
        return;
    }

    resultBox.classList.add("d-none");
    const question = state.questions[state.index];
    progress.textContent = `Question ${state.index + 1} / ${state.questions.length}`;
    state.answered = false;

    questionBox.innerHTML = "";
    const questionP = document.createElement("p");
    questionP.className = "fw-semibold mb-3";
    questionP.textContent = question.question;
    questionBox.appendChild(questionP);

    const feedback = document.createElement("div");
    feedback.className = "quiz-run-feedback small mb-2";

    if (question.answer_type === "numeric") {
        const inputGroup = document.createElement("div");
        inputGroup.className = "input-group mb-2";
        inputGroup.style.maxWidth = "320px";

        const input = document.createElement("input");
        input.type = "text";
        input.className = "form-control";
        input.placeholder = "Ta réponse";

        const checkBtn = document.createElement("button");
        checkBtn.type = "button";
        checkBtn.className = "btn btn-outline-primary";
        checkBtn.textContent = "Valider";
        checkBtn.addEventListener("click", async () => {
            if (state.answered || !input.value.trim()) {
                return;
            }
            const result = await submitQuizAnswer(question.block_id, input.value);
            if (!result) {
                return;
            }
            state.answered = true;
            input.disabled = true;
            checkBtn.disabled = true;
            if (result.correct) {
                state.score += 1;
            }
            feedback.textContent = result.correct ? "Correct !" : "Incorrect.";
            feedback.className =
                "quiz-run-feedback small mb-2 " + (result.correct ? "text-success" : "text-danger");
            appendNextButton(runEl, questionBox);
        });

        inputGroup.appendChild(input);
        inputGroup.appendChild(checkBtn);
        questionBox.appendChild(inputGroup);
    } else {
        const list = document.createElement("div");
        list.className = "list-group mb-3";
        question.choices.forEach((choice, index) => {
            const choiceBtn = document.createElement("button");
            choiceBtn.type = "button";
            choiceBtn.className = "list-group-item list-group-item-action";
            choiceBtn.textContent = choice;
            choiceBtn.addEventListener("click", async () => {
                if (state.answered) {
                    return;
                }
                const result = await submitQuizAnswer(question.block_id, index);
                if (!result) {
                    return;
                }
                state.answered = true;
                Array.from(list.children).forEach((btn) => {
                    btn.disabled = true;
                });
                choiceBtn.classList.add(result.correct ? "list-group-item-success" : "list-group-item-danger");
                if (!result.correct && result.correct_index !== null && result.correct_index !== undefined) {
                    const correctBtn = list.children[result.correct_index];
                    if (correctBtn) {
                        correctBtn.classList.add("list-group-item-success");
                    }
                }
                if (result.correct) {
                    state.score += 1;
                }
                feedback.textContent = result.correct ? "Correct !" : "Incorrect.";
                feedback.className =
                    "quiz-run-feedback small mb-2 " + (result.correct ? "text-success" : "text-danger");
                appendNextButton(runEl, questionBox);
            });
            list.appendChild(choiceBtn);
        });
        questionBox.appendChild(list);
    }

    questionBox.appendChild(feedback);
}

function initQuizRun(runEl) {
    let questions = [];
    try {
        questions = JSON.parse(runEl.dataset.questions || "[]");
    } catch (error) {
        questions = [];
    }
    runEl.quizState = { questions, index: 0, score: 0, answered: false };
    renderQuizRunQuestion(runEl);
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".quiz-run").forEach(initQuizRun);
});

document.addEventListener("click", (event) => {
    if (event.target.classList.contains("quiz-run-restart-btn")) {
        const runEl = event.target.closest(".quiz-run");
        if (runEl && runEl.quizState) {
            runEl.quizState.index = 0;
            runEl.quizState.score = 0;
            renderQuizRunQuestion(runEl);
        }
    }
});
