function buildConstantFunctionGraph(container) {
    const initialP = parseFloat(container.dataset.p || "1");
    const minP = parseFloat(container.dataset.min || "-10");
    const maxP = parseFloat(container.dataset.max || "10");

    const wrapper = document.createElement("div");

    const controls = document.createElement("div");
    controls.className = "d-flex align-items-center gap-2 mb-2 flex-wrap";

    const label = document.createElement("label");
    label.className = "form-label mb-0";
    label.textContent = "p =";

    const valueSpan = document.createElement("span");
    valueSpan.className = "fw-semibold";
    valueSpan.textContent = initialP;

    const slider = document.createElement("input");
    slider.type = "range";
    slider.className = "form-range";
    slider.min = String(minP);
    slider.max = String(maxP);
    slider.step = "1";
    slider.value = String(initialP);
    slider.style.maxWidth = "300px";

    controls.appendChild(label);
    controls.appendChild(valueSpan);
    controls.appendChild(slider);

    const plotDiv = document.createElement("div");
    plotDiv.style.height = "320px";

    wrapper.appendChild(controls);
    wrapper.appendChild(plotDiv);
    container.appendChild(wrapper);

    const xValues = [-10, 10];

    function traceForP(p) {
        return [
            {
                x: xValues,
                y: [p, p],
                mode: "lines",
                line: { color: "#0d6efd", width: 3 },
                name: `f(x) = ${p}`,
            },
        ];
    }

    Plotly.newPlot(
        plotDiv,
        traceForP(initialP),
        {
            title: "Fonction constante f(x) = p",
            xaxis: { title: "x", range: [-10, 10], zeroline: true, gridcolor: "#e9ecef" },
            yaxis: { title: "f(x)", range: [minP - 2, maxP + 2], zeroline: true, gridcolor: "#e9ecef" },
            margin: { t: 40, r: 20, b: 40, l: 50 },
        },
        { displayModeBar: false, responsive: true }
    );

    slider.addEventListener("input", () => {
        const p = parseFloat(slider.value);
        valueSpan.textContent = p;
        Plotly.react(plotDiv, traceForP(p), plotDiv.layout);
    });
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".jc-graph-constant").forEach(buildConstantFunctionGraph);
});
