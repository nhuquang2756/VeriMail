// Tab Switching Logic
document.querySelectorAll('.nav-item').forEach(button => {
    button.addEventListener('click', () => {
        const tabName = button.dataset.tab;

        // Update Sidebar Active State
        document.querySelectorAll('.nav-item').forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');

        // Update Content
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
        document.getElementById(`${tabName}-tab`).classList.add('active');
    });
});

// Select All Models
document.getElementById('select-all').addEventListener('change', function () {
    const checkboxes = document.querySelectorAll('.model-checkbox');
    checkboxes.forEach(cb => cb.checked = this.checked);
});

// File Upload Handling
const fileInput = document.getElementById('csv-file');
const fileInfo = document.getElementById('file-info');
const fileName = document.getElementById('file-name');
const uploadPlaceholder = document.querySelector('.upload-placeholder');

fileInput.addEventListener('change', function () {
    if (this.files[0]) {
        fileName.textContent = this.files[0].name;
        fileInfo.style.display = 'flex';
        uploadPlaceholder.style.display = 'none';
    }
});

document.querySelector('.remove-file').addEventListener('click', () => {
    fileInput.value = '';
    fileInfo.style.display = 'none';
    uploadPlaceholder.style.display = 'block';
});

// Helper Functions
function getSelectedModels() {
    const checkboxes = document.querySelectorAll('.model-checkbox:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

function showLoading() {
    document.getElementById('loading').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

// ============================================
// TEXT ANALYSIS
// ============================================
document.getElementById('analyze-btn').addEventListener('click', async () => {
    const message = document.getElementById('message-input').value.trim();
    const models = getSelectedModels();

    if (!message) return alert('Vui lòng nhập nội dung tin nhắn!');
    if (models.length === 0) return alert('Vui lòng chọn ít nhất một mô hình!');

    showLoading();
    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, models })
        });
        const data = await response.json();

        if (data.success) {
            displayResults(data.results);
        } else {
            alert('Lỗi: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        alert('Lỗi kết nối: ' + error.message);
    } finally {
        hideLoading();
    }
});

function displayResults(results) {
    const container = document.getElementById('results-grid');
    container.innerHTML = '';

    for (const [model, prediction] of Object.entries(results)) {
        const isSpam = prediction === 'Spam';
        const card = document.createElement('div');
        card.className = 'result-card';
        card.innerHTML = `
            <div style="display:flex; align-items:center; gap:0.8rem;">
                <div style="width:32px; height:32px; background:#F1F5F9; border-radius:8px; display:flex; align-items:center; justify-content:center;">
                    <i class="fa-solid fa-robot" style="color:#64748B;"></i>
                </div>
                <span style="font-weight:600; color:#334155;">${model}</span>
            </div>
            <span class="result-badge ${isSpam ? 'badge-spam' : 'badge-ham'}">
                <i class="fa-solid ${isSpam ? 'fa-circle-xmark' : 'fa-circle-check'}"></i>
                ${isSpam ? 'SPAM' : 'HAM'}
            </span>
        `;
        container.appendChild(card);
    }
    document.getElementById('results').style.display = 'block';
}

// ============================================
// CSV ANALYSIS
// ============================================
document.getElementById('analyze-csv-btn').addEventListener('click', async () => {
    const models = getSelectedModels();
    if (!fileInput.files[0]) return alert('Vui lòng chọn file CSV!');
    if (models.length === 0) return alert('Vui lòng chọn ít nhất một mô hình!');

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    models.forEach(model => formData.append('models[]', model));

    showLoading();
    try {
        const response = await fetch('/api/predict-batch', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        if (data.success) {
            displayTableResults(data.data, data.columns);
        } else {
            alert('Lỗi: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        alert('Lỗi kết nối: ' + error.message);
    } finally {
        hideLoading();
    }
});

function displayTableResults(data, columns) {
    const thead = document.getElementById('table-head');
    const tbody = document.getElementById('table-body');

    thead.innerHTML = '<tr>' + columns.map(col => `<th>${col}</th>`).join('') + '</tr>';

    tbody.innerHTML = data.map(row => {
        return '<tr>' + columns.map(col => {
            let value = row[col];
            if (value === 'Spam' || value === 'Ham') {
                const isSpam = value === 'Spam';
                value = `<span class="result-badge ${isSpam ? 'badge-spam' : 'badge-ham'}">
                            <i class="fa-solid ${isSpam ? 'fa-circle-xmark' : 'fa-circle-check'}"></i>
                            ${value}
                         </span>`;
            }
            return `<td>${value}</td>`;
        }).join('') + '</tr>';
    }).join('');

    document.getElementById('csv-results').style.display = 'block';
    window.csvData = { data, columns };
}

// ============================================
// EMAIL MONITOR
// ============================================
let gmailSessionId = null;

document.getElementById('connect-gmail-btn').addEventListener('click', async () => {
    const email = document.getElementById('gmail-email').value.trim();
    const password = document.getElementById('gmail-password').value.replace(/ /g, '');

    if (!email || !password) return alert('Vui lòng nhập đầy đủ thông tin!');

    showLoading();
    try {
        const response = await fetch('/api/gmail/connect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await response.json();

        if (data.success) {
            gmailSessionId = data.session_id;
            document.getElementById('connected-email').textContent = email;
            document.getElementById('gmail-login-form').style.display = 'none';
            document.getElementById('gmail-connected').style.display = 'block';
        } else {
            alert('❌ ' + (data.error || 'Lỗi kết nối'));
        }
    } catch (error) {
        alert('❌ Lỗi: ' + error.message);
    } finally {
        hideLoading();
    }
});

document.getElementById('disconnect-btn').addEventListener('click', async () => {
    if (gmailSessionId) {
        await fetch('/api/gmail/disconnect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: gmailSessionId })
        });
    }
    gmailSessionId = null;
    document.getElementById('gmail-login-form').style.display = 'block';
    document.getElementById('gmail-connected').style.display = 'none';
    document.getElementById('email-list').style.display = 'none';
});

document.getElementById('fetch-emails-btn').addEventListener('click', async () => {
    if (!gmailSessionId) return;
    const model = document.getElementById('email-model-select').value;
    showLoading();

    try {
        const response = await fetch('/api/gmail/fetch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: gmailSessionId, model, limit: 20 })
        });
        const data = await response.json();

        if (data.success) {
            displayEmails(data.emails);
        } else {
            alert('❌ ' + (data.error || 'Lỗi'));
        }
    } catch (error) {
        alert('❌ ' + error.message);
    } finally {
        hideLoading();
    }
});

function displayEmails(emails) {
    const container = document.getElementById('emails-container');
    container.innerHTML = '';
    document.getElementById('email-count').textContent = emails.length;

    emails.forEach((email, idx) => {
        const isSpam = email.prediction === 'Spam';
        const card = document.createElement('div');
        card.className = 'result-card';
        card.innerHTML = `
            <div style='flex:1;'>
                <div style='display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;'>
                    <span style='background:#E2E8F0; padding:2px 8px; border-radius:4px; font-size:0.8rem; font-weight:600;'>#${idx + 1}</span>
                    <span style='color:#64748B; font-size:0.9rem;'><i class="fa-regular fa-clock"></i> ${email.date}</span>
                </div>
                <h4 style='font-size:1.1rem; margin-bottom:0.5rem; color:#1E293B;'>${email.subject}</h4>
                <div style='color:#475569; font-size:0.95rem;'><i class="fa-solid fa-user-tag"></i> ${email.from}</div>
            </div>
            <span class='result-badge ${isSpam ? 'badge-spam' : 'badge-ham'}'>
                <i class="fa-solid ${isSpam ? 'fa-triangle-exclamation' : 'fa-shield-check'}"></i>
                ${isSpam ? 'SPAM' : 'HAM'}
            </span>
        `;
        container.appendChild(card);
    });
    document.getElementById('email-list').style.display = 'block';
}
