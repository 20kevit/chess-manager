// Main script for handling backup import from Coronate

/**
 * Previews tournaments from the uploaded backup file
 * This function is called when the user clicks the preview button
 */
function previewTournaments() {
    // Get DOM elements
    const fileInput = document.getElementById('backup-file');
    const previewBtn = document.getElementById('preview-btn');
    const btnText = document.getElementById('btn-text');
    const btnSpinner = document.getElementById('btn-spinner');
    const alertContainer = document.getElementById('alert-container');
    const previewResults = document.getElementById('preview-results');
    const csrfTokenInput = document.getElementById('csrf-token');
    
    // Clear previous alerts
    alertContainer.innerHTML = '';
    
    // Validate file selection
    if (!fileInput.files || fileInput.files.length === 0) {
        showAlert('لطفاً یک فایل را انتخاب کنید.', 'error');
        return;
    }
    
    const file = fileInput.files[0];
    
    // Validate file extension
    if (!file.name.toLowerCase().endsWith('.json')) {
        showAlert('لطفاً یک فایل با پسوند .json انتخاب کنید.', 'error');
        return;
    }
    
    // Show loading state
    previewBtn.disabled = true;
    btnText.style.display = 'none';
    btnSpinner.style.display = 'inline';
    
    // Prepare FormData with the file
    const formData = new FormData();
    formData.append('json_file', file);
    
    // Get CSRF token
    const csrfToken = csrfTokenInput.value;
    
    // Send AJAX request to preview endpoint
    fetch('/create/from-backup/coronate', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: formData
    })
    .then(response => {
        // Check if response is OK
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Handle backend errors
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Handle empty tournament list
        if (!data.tournaments || data.tournaments.length === 0) {
            throw new Error('هیچ تورنمنتی در فایل یافت نشد.');
        }
        
        // Render tournament list
        renderTournamentList(data.tournaments, csrfToken);
        previewResults.style.display = 'block';
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert(error.message || 'خطا در پردازش فایل. لطفاً دوباره تلاش کنید.', 'error');
    })
    .finally(() => {
        // Reset button state
        previewBtn.disabled = false;
        btnText.style.display = 'inline';
        btnSpinner.style.display = 'none';
    });
}

/**
 * Renders the list of tournaments as individual forms
 * @param {Array} tournaments - Array of tournament objects
 * @param {string} csrfToken - CSRF token for form submission
 */
function renderTournamentList(tournaments, csrfToken) {
    const previewResults = document.getElementById('preview-results');
    
    // Clear previous results
    previewResults.innerHTML = '<h3 class="section-title">تورنمنت‌های موجود در فایل</h3>' +
        '<p class="file-hint">تورنمنت مورد نظر خود را برای وارد کردن به سیستم انتخاب کنید:</p>';
    
    // Create a form for each tournament
    tournaments.forEach(tournament => {
        const formDiv = document.createElement('div');
        formDiv.className = 'tournament-preview-item';
        
        // Create form HTML
        formDiv.innerHTML = `
            <span class="tournament-name">${escapeHtml(tournament.name)}</span>
            <form method="POST" action="/create/execute/coronate" style="display: inline;">
                <input type="hidden" name="csrf_token" value="${csrfToken}">
                <input type="hidden" name="target_tournament_id" value="${escapeHtml(tournament.internal_id)}">
                <button type="submit" class="btn btn-primary">
                    وارد کردن این تورنمنت
                </button>
            </form>
        `;
        
        previewResults.appendChild(formDiv);
    });
}

/**
 * Displays an alert message
 * @param {string} message - The message to display
 * @param {string} type - The alert type (error, success)
 */
function showAlert(message, type) {
    const alertContainer = document.getElementById('alert-container');
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `
        ${message}
        <button class="alert-close" onclick="this.parentElement.remove()">&times;</button>
    `;
    alertContainer.appendChild(alertDiv);
}

/**
 * Escapes HTML characters to prevent XSS
 * @param {string} text - The text to escape
 * @returns {string} - The escaped HTML string
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}