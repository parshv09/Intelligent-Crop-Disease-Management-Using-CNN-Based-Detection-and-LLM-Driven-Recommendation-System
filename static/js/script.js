// static/js/script.js
document.addEventListener('DOMContentLoaded', function() {
    // 1. Core UI Selectors
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadTriggerBtn = document.getElementById('upload-trigger-btn');
    const uploadSection = document.getElementById('upload-section');
    const loadingSection = document.getElementById('loading-section');
    const resultsSection = document.getElementById('results-section');
    const errorSection = document.getElementById('error-section');
    const errorMessage = document.getElementById('error-message');
    const analyzeAnotherBtn = document.getElementById('analyze-another-btn');

    // 2. Result Display Selectors
    const previewImage = document.getElementById('preview-image');
    const healthStatus = document.getElementById('health-status');
    const healthStatusIcon = document.getElementById('health-status-icon');
    const diseaseName = document.getElementById('disease-name');
    const confidenceBar = document.getElementById('confidence-bar');
    const confidenceText = document.getElementById('confidence-text');
    const topPredictionsContainer = document.getElementById('top-predictions-container');

    // 3. AI Advisory Selectors
    const secExplanation = document.getElementById('section-explanation');
    const secActions = document.getElementById('section-actions');
    const secPrevention = document.getElementById('section-prevention');
    const secOrganic = document.getElementById('section-organic');
    const secChemical = document.getElementById('section-chemical');
    const secDisclaimer = document.getElementById('section-disclaimer');

    let myChart = null; 

    /**
     * Helper: Parse AI Text Sections based on numbered formatting
     */
    function parseSection(text, sectionNumber) {
        const regex = new RegExp(`${sectionNumber}\\.\\s(?:\\*\\*.*?\\*\\*|.*?):\\s?([\\s\\S]*?)(?=\\n\\d\\.|$)`);
        const match = text.match(regex);
        return match ? match[1].replace(/\*\*/g, '').trim() : "Information not available for this diagnostic step.";
    }

    /**
     * Helper: Format strings with hyphens into clean HTML list items
     */
    function formatBullets(text) {
        if (!text || text.includes("Data unavailable") || text.includes("Information not available")) return text;
        
        const points = text.split('-').filter(p => p.trim().length > 3);
        if (points.length === 0) return text;

        return `<ul class="space-y-3">
                    ${points.map(point => `
                        <li class="flex items-start">
                            <i class="fas fa-check-circle text-green-500 mt-1 mr-3 text-[10px]"></i>
                            <span class="text-slate-600 text-sm leading-relaxed">${point.trim()}</span>
                        </li>`).join('')}
                </ul>`;
    }

    /**
     * Chart Logic: Renders the visual confidence doughnut using Chart.js
     */
    function updateConfidenceChart(confidence) {
        const canvas = document.getElementById('confidenceChart');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        const remaining = 100 - confidence;
        
        if (myChart) { myChart.destroy(); }

        myChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Match', 'Uncertainty'],
                datasets: [{
                    data: [confidence, remaining],
                    backgroundColor: ['#10b981', '#f1f5f9'],
                    borderWidth: 0
                }]
            },
            options: {
                cutout: '80%',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                }
            }
        });
    }

    /**
     * API Handling: Manages the file upload and results rendering
     */
    function handleFile(file) {
        if (!file) return;

        uploadSection.classList.add('hidden');
        loadingSection.classList.remove('hidden');
        errorSection.classList.add('hidden');

        const formData = new FormData();
        formData.append('file', file);

        fetch('/predict', { method: 'POST', body: formData })
            .then(res => res.json())
            .then(data => {
                if (data.error) throw new Error(data.error);

                loadingSection.classList.add('hidden');
                resultsSection.classList.remove('hidden');
                
                // 1. Set Image Evidence
                previewImage.src = URL.createObjectURL(file);

                // 2. Set Health Badge status
                if (data.is_healthy) {
                    healthStatus.textContent = "Healthy Specimen";
                    healthStatus.parentElement.className = "px-6 py-2 rounded-2xl flex items-center shadow-sm bg-green-50 border border-green-100 text-green-700";
                    healthStatusIcon.className = "fas fa-check-circle mr-3";
                } else {
                    healthStatus.textContent = "Infection Detected";
                    healthStatus.parentElement.className = "px-6 py-2 rounded-2xl flex items-center shadow-sm bg-red-50 border border-red-100 text-red-700";
                    healthStatusIcon.className = "fas fa-exclamation-triangle mr-3";
                }

                // 3. Populate Main Prediction Data
                diseaseName.textContent = data.prediction.replace(/_/g, ' ');
                confidenceText.textContent = `${data.confidence}% Match`;
                confidenceBar.style.width = `${data.confidence}%`;
                
                // 4. Update Visual Charts
                updateConfidenceChart(data.confidence);

                // 5. Render Likely Alternatives (Probabilities)
                topPredictionsContainer.innerHTML = '';
                if (data.all_predictions && data.all_predictions.length > 1) {
                    data.all_predictions.slice(1, 3).forEach(pred => {
                        const div = document.createElement('div');
                        div.className = "flex justify-between items-center bg-slate-50 p-3 rounded-xl border border-slate-100";
                        div.innerHTML = `
                            <span class="text-xs font-bold text-slate-700 capitalize">${pred.class.replace(/_/g, ' ')}</span>
                            <span class="text-[10px] font-black text-slate-400">${pred.confidence}%</span>
                        `;
                        topPredictionsContainer.appendChild(div);
                    });
                }

                // 6. Populate AI Advisory Dashboard
                if (data.llm_advisory) {
                    const raw = data.llm_advisory;
                    secExplanation.textContent = parseSection(raw, 1);
                    secActions.innerHTML    = formatBullets(parseSection(raw, 2));
                    secOrganic.innerHTML    = formatBullets(parseSection(raw, 3));
                    secChemical.innerHTML   = formatBullets(parseSection(raw, 4));
                    secPrevention.innerHTML = formatBullets(parseSection(raw, 5));
                    secDisclaimer.textContent = parseSection(raw, 7);
                }
            })
            .catch(err => {
                loadingSection.classList.add('hidden');
                uploadSection.classList.remove('hidden');
                errorMessage.textContent = err.message || "An error occurred during analysis.";
                errorSection.classList.remove('hidden');
            });
    }

    // --- Interaction Event Listeners ---
    uploadTriggerBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) handleFile(e.target.files[0]);
    });

    ['dragover', 'drop'].forEach(name => {
        dropZone.addEventListener(name, (e) => {
            e.preventDefault();
            if (name === 'drop') handleFile(e.dataTransfer.files[0]);
        });
    });

    analyzeAnotherBtn.addEventListener('click', () => {
        resultsSection.classList.add('hidden');
        uploadSection.classList.remove('hidden');
        fileInput.value = '';
    });
});