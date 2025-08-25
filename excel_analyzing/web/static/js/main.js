/* Main JavaScript for Excel Analyzing */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // File upload progress
    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            const fileInput = document.getElementById('file');
            const file = fileInput.files[0];
            
            if (file && file.size > 50 * 1024 * 1024) { // 50MB limit
                e.preventDefault();
                alert('File size exceeds 50MB limit. Please choose a smaller file.');
                return false;
            }
        });
    }
});

// Utility functions
function showSpinner(buttonId) {
    const button = document.getElementById(buttonId);
    const spinner = button.querySelector('.spinner-border');
    if (spinner) {
        spinner.classList.remove('d-none');
        button.disabled = true;
    }
}

function hideSpinner(buttonId) {
    const button = document.getElementById(buttonId);
    const spinner = button.querySelector('.spinner-border');
    if (spinner) {
        spinner.classList.add('d-none');
        button.disabled = false;
    }
}