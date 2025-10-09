document.addEventListener('DOMContentLoaded', function () {
    let formToSubmit = null;

    // ----- Elements -----
    const form = document.getElementById('diabetesForm');
    const predictionDiv = document.getElementById('predictionResult'); // for inline messages
    const popup = document.getElementById('predictionPopup');
    const predictionText = document.getElementById('predictionText');
    const predictionEmoji = document.getElementById('predictionEmoji');
    const closePredictionBtn = document.getElementById('closePredictionBtn');
    const clearBtn = document.getElementById('clearBtn');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    const searchInput = document.getElementById('searchInput');

    function showPredictionPopup(result) {
    if (!popup || !predictionText || !predictionEmoji || !closePredictionBtn) return;

    if (result === 'Diabetic') {
        predictionEmoji.textContent = '⚠️';
        predictionText.textContent = "Diabetic - Please follow health tips!";
        predictionText.className = 'diabetic';
    } else {
        predictionEmoji.textContent = '✅';
        predictionText.textContent = "Non-Diabetic - Keep maintaining healthy lifestyle!";
        predictionText.className = 'non-diabetic';
    }

    popup.style.display = 'flex';
    closePredictionBtn.style.display = 'block'; // button show

    // Auto-hide after 8 sec
    setTimeout(() => {
        popup.style.display = 'none';
        closePredictionBtn.style.display = 'none'; // button hide
    }, 8000);
}


    // ----- Close Prediction Popup -----
    if (closePredictionBtn) {
        closePredictionBtn.addEventListener('click', function () {
            popup.style.display = 'none';
        });
    }

    // ----- Form Submit via AJAX -----
    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const formData = new FormData(form);

            fetch(form.action, {
                method: 'POST',
                body: formData
            })
                .then(res => res.json())
                .then(data => {
                    if (predictionDiv) predictionDiv.innerHTML = '';

                    if (data.status === 'success') {
                        showPredictionPopup(data.result);
                        console.log("✅ Prediction Success:", data.result);
                    } else if (data.status === 'error') {
                        console.error("❌ Prediction Error:", data.messages);
                        if (predictionDiv) {
                            data.messages.forEach(msg => {
                                const div = document.createElement('div');
                                div.className = 'flash error';
                                div.textContent = "❌ " + msg;
                                predictionDiv.appendChild(div);
                                setTimeout(() => div.remove(), 10000);
                            });
                        }
                    }
                })
                .catch(err => {
                    console.error("⚠ AJAX Fetch Error:", err);
                    if (predictionDiv) {
                        const div = document.createElement('div');
                        div.className = 'flash error';
                        div.textContent = "❌ Something went wrong!";
                        predictionDiv.appendChild(div);
                        setTimeout(() => div.remove(), 10000);
                    }
                });
        });
    }

    // ----- Clear Button -----
    if (clearBtn && form) {
        clearBtn.addEventListener('click', function () {
            form.reset();
            if (predictionDiv) predictionDiv.innerHTML = '';
            console.log("🧹 Form cleared");
        });
    }

    // ----- Delete Modal -----
    window.showDeleteModal = function (btn) {
        formToSubmit = btn.closest('form');
        const modal = document.getElementById('deleteModal');
        if (modal) modal.style.display = 'flex';
    }

    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', function () {
            if (formToSubmit) {
                formToSubmit.submit();
                console.log("🗑 Patient delete submitted");
            }
            const modal = document.getElementById('deleteModal');
            if (modal) modal.style.display = 'none';
        });
    }

    window.closeModal = function () {
        const modal = document.getElementById('deleteModal');
        if (modal) modal.style.display = 'none';
    }

    // ----- Search Filter -----
    if (searchInput) {
        searchInput.addEventListener('keyup', function () {
            const filter = this.value.toLowerCase();
            const table = document.getElementById('patientsTable');
            if (!table) return;

            Array.from(table.tBodies[0].rows).forEach(row => {
                const name = row.cells[1]?.textContent.toLowerCase() || '';
                const prediction = row.cells[row.cells.length - 2]?.textContent.toLowerCase() || '';
                row.style.display = (name.includes(filter) || prediction.includes(filter)) ? '' : 'none';
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
    }
});
