document.addEventListener('DOMContentLoaded', function () {
    let formToSubmit = null;

    // ----- Elements -----
    const form = document.getElementById('diabetesForm');
    const predictBtn = document.getElementById('predictBtn');
    const predictionDiv = document.getElementById('predictionResult');
    const popup = document.getElementById('predictionPopup');
    const predictionText = document.getElementById('predictionText');
    const predictionEmoji = document.getElementById('predictionEmoji');
    const predictionTips = document.getElementById('predictionTips');
    const closePredictionBtn = document.getElementById('closePredictionBtn');
    const clearBtn = document.getElementById('clearBtn');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    const searchInput = document.getElementById('searchInput');

    // Chart Elements
    const chartContainer = document.getElementById("chartContainer");
    const chartCanvas = document.getElementById("featureChart");
    let featureChartInstance = null;

    // ----- Accuracy Elements -----
    const accuracyWrapper = document.getElementById('accuracyWrapper');
    const accuracyText = document.getElementById('accuracyText');
    const accuracyBar = document.getElementById('accuracyBar');

    // ----- Show Prediction Popup -----
    function showPredictionPopup(result) {
        if (!popup || !predictionText || !predictionEmoji || !closePredictionBtn || !predictionTips) return;

        let tipsList = [];
        if (result === 'Diabetic') {
            predictionEmoji.textContent = '⚠️😟';
            predictionText.textContent = "Diabetic - Please follow health tips!";
            predictionText.className = 'diabetic';
            tipsList = [
                "Check blood sugar 2–3 times daily",
                "Follow low-carb, high-fiber diet",
                "Avoid sweets & sugary drinks completely",
                "Exercise 30–60 mins daily",
                "Take medications on time",
                "Monitor blood pressure & weight"
            ];
        } else {
            predictionEmoji.textContent = '😇';
            predictionText.textContent = "Non-Diabetic - Keep maintaining healthy lifestyle!";
            predictionText.className = 'non-diabetic';
            tipsList = [
                "Maintain a balanced diet",
                "Exercise 3–5 times/week",
                "Keep BMI in healthy range",
                "Limit sugar and processed foods",
                "Regular health checkups"
            ];
        }

        // Tips list
        predictionTips.innerHTML = '';
        const ul = document.createElement('ul');
        tipsList.forEach(tip => {
            const li = document.createElement('li');
            li.textContent = tip;
            ul.appendChild(li);
        });
        predictionTips.appendChild(ul);

        popup.style.display = 'flex';
        closePredictionBtn.style.display = 'block';
    }

    // ----- Show Accuracy -----
    function showAccuracy(acc) {
        if (!accuracyWrapper || acc === null || acc === undefined) return;

        accuracyWrapper.style.display = 'block';
        accuracyText.textContent = `Accuracy Score: ${acc}%`;
        accuracyBar.style.width = acc + '%';

        if (acc >= 80) accuracyBar.style.background = '#10b981';
        else if (acc >= 60) accuracyBar.style.background = '#f59e0b';
        else accuracyBar.style.background = '#ef4444';
    }

    // ----- Feature Importance Chart -----
    function renderFeatureChart(featureData) {
        if (!chartContainer || !chartCanvas) return;

        if (!featureData || Object.keys(featureData).length === 0) {
            chartContainer.style.display = "none";
            return;
        }

        chartContainer.style.display = "block";
        const ctx = chartCanvas.getContext("2d");

        if (featureChartInstance) featureChartInstance.destroy();

        featureChartInstance = new Chart(ctx, {
            type: "bar",
            data: {
                labels: Object.keys(featureData),
                datasets: [{
                    label: "Feature Importance",
                    data: Object.values(featureData),
                    backgroundColor: "rgba(54, 162, 235, 0.6)",
                    borderColor: "rgba(54, 162, 235, 1)",
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false, 
                plugins: {
                    legend: { display: false },
                    title: {
                        display: true,
                        font: { size: 16, weight: 'bold' },
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Feature Names',
                            font: { size: 14 },
                            color: '#444'
                        },
                        ticks: {
                            color: '#333',
                            font: { size: 12 },
                            autoSkip: false,
                            maxRotation: 90,
                            minRotation: 45
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Feature Importance Score (0 to 1)',
                            font: { size: 12 },
                            color: '#444'
                        },
                        ticks: {
                            stepSize: 0.05,
                            color: '#333',
                            font: { size: 12 }
                        }
                    }
                }
            }

        });
    }

    // ----- Close Popup -----
    if (closePredictionBtn) {
        closePredictionBtn.addEventListener('click', function () {
            popup.style.display = 'none';
            closePredictionBtn.style.display = 'none';
            if (accuracyWrapper) accuracyWrapper.style.display = 'none';
        });
    }

    // ----- Form Submit via AJAX -----
    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            if (predictBtn) predictBtn.disabled = true; 

            const formData = new FormData(form);

            fetch(form.action, {
                method: 'POST',
                body: formData
            })
                .then(res => res.json())
                .then(data => {
                    if (predictBtn) predictBtn.disabled = false; 
                    if (predictionDiv) predictionDiv.innerHTML = '';

                    if (data.status === 'success') {
                        const div = document.createElement('div');
                        div.className = 'flash success';
                        div.textContent = "✅ Prediction successful!";
                        predictionDiv.appendChild(div);
                        setTimeout(() => div.remove(), 5000);

                        showPredictionPopup(data.result);
                        renderFeatureChart(data.feature_importance);
                        showAccuracy(data.confidence);

                        console.log("✅ Prediction Success:", data.result, "Confidence:", data.confidence);
                    } else if (data.status === 'error') {
                        console.error("❌ Prediction Error:", data.messages);
                        if (predictionDiv) {
                            data.messages.forEach(msg => {
                                const div = document.createElement('div');
                                div.className = 'flash error';
                                div.textContent = "❌ " + msg;
                                predictionDiv.appendChild(div);
                                setTimeout(() => div.remove(), 5000);
                            });
                        }
                    }
                })
                .catch(err => {
                    if (predictBtn) predictBtn.disabled = false;
                    console.error("⚠ AJAX Fetch Error:", err);
                    if (predictionDiv) {
                        const div = document.createElement('div');
                        div.className = 'flash error';
                        div.textContent = "❌ Something went wrong!";
                        predictionDiv.appendChild(div);
                        setTimeout(() => div.remove(), 5000);
                    }
                });
        });
    }

    // ----- Clear Button -----
    if (clearBtn && form) {
        clearBtn.addEventListener('click', function () {
            form.reset();
            if (predictionDiv) predictionDiv.innerHTML = '';
            popup.style.display = 'none';
            closePredictionBtn.style.display = 'none';
            predictionTips.innerHTML = '';
            if (chartContainer) chartContainer.style.display = "none";
            if (accuracyWrapper) accuracyWrapper.style.display = "none";
            console.log("🧹 Form cleared");
        });
    }

    // ----- Delete Modal -----
    window.showDeleteModal = function (btn) {
        formToSubmit = btn.closest('form');
        const modal = document.getElementById('deleteModal');
        if (modal) modal.style.display = 'flex';
    };

    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', function () {
            if (formToSubmit) formToSubmit.submit();
            const modal = document.getElementById('deleteModal');
            if (modal) modal.style.display = 'none';
        });
    }

    window.closeModal = function () {
        const modal = document.getElementById('deleteModal');
        if (modal) modal.style.display = 'none';
    };

    // ----- Search Filter -----
    if (searchInput) {
        searchInput.addEventListener('keyup', function () {
            const filter = this.value.toLowerCase();
            const table = document.getElementById('patientsTable');
            if (!table) return;

            Array.from(table.tBodies[0].rows).forEach(row => {
                const name = row.cells[1]?.textContent.toLowerCase() || '';
                row.style.display = (name.includes(filter)) ? '' : 'none';
            });
        });
    }

    // ----- Change Per Page -----
    window.changePerPage = function () {
        const perPageSelect = document.getElementById('perPageSelect');
        if (!perPageSelect) return;
        const perPage = perPageSelect.value;
        const url = new URL(window.location.href);
        url.searchParams.set('per_page', perPage);
        window.location.href = url;
    };
});
