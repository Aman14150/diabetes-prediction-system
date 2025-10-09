document.addEventListener('DOMContentLoaded', function () {
    let formToSubmit = null;

    // ----- Predict Form Submit via AJAX -----
    const form = document.getElementById('diabetesForm');
    const predictionDiv = document.getElementById('predictionResult');

    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const formData = new FormData(form);

            fetch("/predict", {
                method: "POST",
                body: formData
            })
                .then(res => res.json())
                .then(data => {
                    predictionDiv.innerHTML = '';

                    if (data.status === 'success') {
                        const span = document.createElement('span');
                        span.textContent = data.result;
                        span.className = data.result === 'Diabetic' ? 'diabetic' : 'non-diabetic';
                        predictionDiv.appendChild(span);
                        setTimeout(() => predictionDiv.innerHTML = '', 10000);
                    } else if (data.status === 'error') {
                        data.messages.forEach(msg => {
                            const div = document.createElement('div');
                            div.className = 'flash error';
                            div.textContent = "❌ " + msg;
                            predictionDiv.appendChild(div);
                            setTimeout(() => div.remove(), 10000);
                        });
                    }
                })
                .catch(err => {
                    console.error("AJAX Error:", err);
                    const div = document.createElement('div');
                    div.className = 'flash error';
                    div.textContent = "❌ Something went wrong!";
                    predictionDiv.appendChild(div);
                    setTimeout(() => div.remove(), 10000);
                });
        });
    }

    // ----- Clear Button -----
    const clearBtn = document.getElementById('clearBtn');
    if (clearBtn && form) {
        clearBtn.addEventListener('click', function () {
            form.reset();
            predictionDiv.innerHTML = '';
        });
    }

    // ----- Delete Modal -----
    window.showDeleteModal = function (btn) {
        formToSubmit = btn.closest('form');
        document.getElementById('deleteModal').style.display = 'flex';
    }

    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', function () {
            if (formToSubmit) {
                formToSubmit.submit();
            }
            document.getElementById('deleteModal').style.display = 'none';
        });
    }

    window.closeModal = function () {
        document.getElementById('deleteModal').style.display = 'none';
    }

    // ----- Search Filter -----
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keyup', function () {
            const filter = this.value.toLowerCase();
            const table = document.getElementById('patientsTable');
            Array.from(table.tBodies[0].rows).forEach(row => {
                const name = row.cells[1].textContent.toLowerCase();
                const prediction = row.cells[row.cells.length - 2].textContent.toLowerCase();
                row.style.display = (name.includes(filter) || prediction.includes(filter)) ? '' : 'none';
            });
        });
    }

    // ----- Change Per Page -----
    window.changePerPage = function () {
        const perPage = document.getElementById('perPageSelect').value;
        const url = new URL(window.location.href);
        url.searchParams.set('per_page', perPage);
        window.location.href = url;
    }
});
