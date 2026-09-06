const form = document.getElementById("prediction-form");

const contextInput =
    document.getElementById("context");

const submitButton =
    document.getElementById("submit-button");

const resultSection =
    document.getElementById("result-section");

const predictionElement =
    document.getElementById("prediction");

const confidenceElement =
    document.getElementById("confidence");

const confidenceBar =
    document.getElementById("confidence-bar");

const probabilitiesElement =
    document.getElementById("probabilities");

const errorElement =
    document.getElementById("error-message");

const characterCount =
    document.getElementById("character-count");



/* Character counter */

contextInput.addEventListener(
    "input",
    () => {

        characterCount.textContent =
            `${contextInput.value.length} / 5000`;
    }
);


/* Prediction request */

form.addEventListener(
    "submit",
    async (event) => {

        event.preventDefault();

        const context =
            contextInput.value.trim();

        const selectedModel =
            document.getElementById(
                "model-selector"
            ).value;

        errorElement.classList.add("hidden");

        submitButton.disabled = true;
        submitButton.textContent =
            "CLASSIFYING...";

        try {

            const response =
                await fetch(
                    "/api/v1/predict",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify({
                                context: context,
                                model: selectedModel
                            })
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                let message =
                    "Prediction request failed.";

                if (Array.isArray(data.detail)) {

                    message =
                        data.detail
                            .map(error => error.msg)
                            .join(" ");
                }

                throw new Error(message);
            }


            renderPrediction(data);

        }

        catch (error) {

            errorElement.textContent =
                error.message;

            errorElement.classList.remove(
                "hidden"
            );

        }

        finally {

            submitButton.disabled = false;

            submitButton.textContent =
                "✦ CLASIFICAR INTENCIÓN DE CITA";
        }

    }
);


/* Render API response */

function renderPrediction(data) {

    predictionElement.textContent =
        data.prediction.toUpperCase();

    const confidencePercentage =
        data.confidence * 100;

    confidenceElement.textContent =
        `${confidencePercentage.toFixed(1)}%`;

    confidenceBar.style.width =
        `${confidencePercentage}%`;

    probabilitiesElement.innerHTML = "";


    const preferredOrder = [
        "Application",
        "Gap",
        "Background",
        "Improvement",
        "Comparison"
    ];


    for (const label of preferredOrder) {

        const probability =
            data.probabilities[label];

        const percentage =
            probability * 100;


        const row =
            document.createElement("div");

        row.className =
            "probability-row";


        const cssLabel =
            label.toLowerCase();


        row.innerHTML = `

            <span class="probability-label">
                ● ${label}
            </span>

            <div class="probability-track">

                <div
                    class="
                        probability-fill
                        fill-${cssLabel}
                    "
                    style="
                        width:
                        ${percentage}%
                    "
                ></div>

            </div>

            <span class="probability-value">
                ${percentage.toFixed(1)}%
            </span>
        `;


        probabilitiesElement.appendChild(
            row
        );

    }


    resultSection.classList.remove(
        "hidden"
    );


    resultSection.scrollIntoView({
        behavior: "smooth",
        block: "nearest"
    });
}


/* Tabs */

const tabs =
    document.querySelectorAll(".tab");

const contents =
    document.querySelectorAll(
        ".tab-content"
    );


tabs.forEach(tab => {

    tab.addEventListener(
        "click",
        () => {

            tabs.forEach(
                item =>
                    item.classList.remove(
                        "active"
                    )
            );

            contents.forEach(
                item =>
                    item.classList.remove(
                        "active"
                    )
            );


            tab.classList.add("active");


            const target =
                document.getElementById(
                    `${tab.dataset.tab}-tab`
                );

            target.classList.add("active");

        }
    );

});


async function loadModels() {

    const response =
        await fetch("/api/v1/models");

    const data =
        await response.json();

    const selector =
        document.getElementById("model-selector");

    selector.innerHTML = "";

    for (const model of data.models) {

        const option =
            document.createElement("option");

        option.value = model.id;
        option.textContent = model.name;

        selector.appendChild(option);
    }
}

loadModels();