document.addEventListener('DOMContentLoaded', () => {
    const predictionForm = document.getElementById('predictionForm');
    const resultDiv = document.getElementById('result');

    const showPlotBtn = document.getElementById('showPlotBtn');
    const plotContainer = document.getElementById('plotContainer');
    const plotImage = document.getElementById('plotImage');

    const showPlotBtn2 = document.getElementById('showPlotBtn2');
    const scoringHistoryContainer = document.getElementById('scoringHistoryContainer');
    const scoringHistoryImage = document.getElementById('scoringHistoryImage');

    const showPartialPlotBtn = document.getElementById('showPartialPlotBtn');
    const partialPlotImage = document.getElementById('partialPlot');
    const partialPlotContainer = document.getElementById('partialPlotContainer');
    const featureSelect = document.getElementById('featureSelect');

    const satisfactionScoreSlider = document.getElementById('SatisfactionScore');
    const satisfactionScoreValue = document.getElementById('satisfactionScoreValue');

    const tenureSlider = document.getElementById('Tenure');
    const tenureValue = document.getElementById('tenureValue');

    const numOfProductsSlider = document.getElementById('NumOfProducts');
    const numOfProductsValue = document.getElementById('numOfProductsValue');

    // Initialize displayed values for sliders
    satisfactionScoreValue.textContent = satisfactionScoreSlider.value;
    tenureValue.textContent = tenureSlider.value;
    numOfProductsValue.textContent = numOfProductsSlider.value;

    // Update displayed values on slider change
    satisfactionScoreSlider.addEventListener('input', () => {
        satisfactionScoreValue.textContent = satisfactionScoreSlider.value;
    });

    tenureSlider.addEventListener('input', () => {
        tenureValue.textContent = tenureSlider.value;
    });

    numOfProductsSlider.addEventListener('input', () => {
        numOfProductsValue.textContent = numOfProductsSlider.value;
    });

    // Hover effect functions (no hover effect on sliders)
    const addHoverEffect = (element) => {
        element.style.borderColor = '#007bff'; // Blue border
        element.style.boxShadow = '0 0 8px rgba(0, 123, 255, 0.3)'; // Blue shadow
        element.style.transition = 'all 0.2s ease-in-out';
    };

    const removeHoverEffect = (element) => {
        element.style.borderColor = ''; // Reset border
        element.style.boxShadow = ''; // Reset shadow
    };

    // Apply hover effects only to input fields and select elements
    const inputs = document.querySelectorAll('input.form-control, select.form-control');
    const buttons = document.querySelectorAll('button');

    inputs.forEach((input) => {
        input.addEventListener('mouseenter', () => addHoverEffect(input));
        input.addEventListener('mouseleave', () => removeHoverEffect(input));
    });

    buttons.forEach((button) => {
        button.addEventListener('mouseenter', () => {
            button.style.backgroundColor = '#0056b3'; // Darker shade on hover
            button.style.color = '#ffffff';
            button.style.boxShadow = '0 0 10px rgba(0, 86, 179, 0.5)';
            button.style.transition = 'all 0.2s ease-in-out';
        });
        button.addEventListener('mouseleave', () => {
            button.style.backgroundColor = ''; // Reset background color
            button.style.color = ''; // Reset text color
            button.style.boxShadow = ''; // Reset shadow
        });
    });

    // Toggle card type dropdown based on 'Has Credit Card' value
    const hasCrCardInput = document.getElementById('HasCrCard');
    const cardTypeDropdown = document.getElementById('CardType');

    function toggleCardTypeDropdown() {
        if (hasCrCardInput.value === "0") {
            cardTypeDropdown.disabled = true;
            cardTypeDropdown.value = ""; // Clear selection if disabled
        } else {
            cardTypeDropdown.disabled = false;
        }
    }

    toggleCardTypeDropdown();
    hasCrCardInput.addEventListener('input', toggleCardTypeDropdown);

    // Handle errors
    const showError = (message, error) => {
        alert(message);
        console.error(error || message);
        resultDiv.innerHTML = `<div class="alert alert-danger">${message}</div>`;
    };

    // Display prediction result
    const displayPredictionResult = (prediction) => {
        const predictionText = prediction === 1
            ? "The customer is likely to leave (Churn)."
            : "The customer is not likely to leave (No Churn).";
        resultDiv.innerHTML = `<div class="alert alert-success">${predictionText}</div>`;
    };

    // Form submission for prediction
    predictionForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const formData = new FormData(predictionForm);

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            if (data.success) {
                displayPredictionResult(data.prediction);
            } else {
                showError(`Error: ${data.error}`);
            }
        } catch (error) {
            showError("An error occurred during the prediction request.", error);
        }
    });

    // Show Variable Importance Plot
    showPlotBtn.addEventListener('click', async () => {
        try {
            const response = await fetch('/plot');
            const data = await response.json();
            if (data.success) {
                plotImage.src = 'data:image/png;base64,' + data.plot_data;
                plotContainer.style.display = 'block';
            } else {
                showError(`Error fetching plot data: ${data.error}`);
            }
        } catch (error) {
            showError("Failed to fetch the plot data.", error);
        }
    });

    // Show Scoring History Plot
    showPlotBtn2.addEventListener('click', async () => {
        try {
            const response = await fetch('/scoring_history_plot');
            const data = await response.json();
            if (data.success) {
                scoringHistoryImage.src = 'data:image/png;base64,' + data.plot_data;
                scoringHistoryContainer.style.display = 'block';
            } else {
                showError(`Error fetching scoring history data: ${data.error}`);
            }
        } catch (error) {
            showError("Failed to fetch the scoring history data.", error);
        }
    });

    // Show Partial Dependency Plot
// Show Partial Dependency Plot
showPartialPlotBtn.addEventListener('click', async () => {
    const selectedFeature = featureSelect.value;
    if (!selectedFeature) {
        alert("Please select a feature for the Partial Dependency Plot.");
        return;
    }

    try {
        const response = await fetch(`/partial_plot/${selectedFeature}`);
        const data = await response.json();

        if (data.success && data.plot_data) {
            // Ensure the base64 string is correctly formatted
            const base64Image = `data:image/png;base64,${data.plot_data.trim()}`;
            partialPlotImage.src = base64Image;
            partialPlotContainer.style.display = 'block';
            partialPlotImage.style.display = 'block'; // Ensure the image element is visible
        } else {
            partialPlotContainer.style.display = 'none';
            partialPlotImage.style.display = 'none';
            showError(`Error fetching partial plot data: ${data.error || 'No plot data received'}`);
        }
    } catch (error) {
        console.error("Fetch error:", error);
        showError("Failed to fetch the partial dependency plot data.");
    }
});

});
