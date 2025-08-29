// PhantomEye Frontend JavaScript

class PhantomEye {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.startLiveUpdates();
        this.setupFormValidation();
    }

    setupEventListeners() {
        // Auto-refresh dashboard
        if (window.location.pathname === '/dashboard') {
            this.setupDashboardRefresh();
        }

        // Form submissions
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', this.handleFormSubmit.bind(this));
        });

        // URL validation
        const urlInput = document.getElementById('url');
        if (urlInput) {
            urlInput.addEventListener('input', this.validateURL.bind(this));
        }
    }

    setupDashboardRefresh() {
        // Refresh dashboard every 5 seconds
        setInterval(() => {
            this.refreshDashboard();
        }, 5000);
    }

    refreshDashboard() {
        // Only refresh if user is active (not idle)
        if (document.visibilityState === 'visible') {
            fetch('/dashboard')
                .then(response => response.text())
                .then(html => {
                    const parser = new DOMParser();
                    const newDoc = parser.parseFromString(html, 'text/html');
                    const newTable = newDoc.querySelector('.table-responsive');
                    const currentTable = document.querySelector('.table-responsive');
                    
                    if (newTable && currentTable) {
                        currentTable.innerHTML = newTable.innerHTML;
                        this.animateNewAttacks();
                    }
                })
                .catch(error => console.error('Dashboard refresh failed:', error));
        }
    }

    animateNewAttacks() {
        const attackRows = document.querySelectorAll('.attack-row');
        attackRows.forEach((row, index) => {
            if (index < 3) { // Animate first 3 rows (newest)
                row.style.animation = 'slideIn 0.5s ease-out';
            }
        });
    }

    handleFormSubmit(event) {
        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Processing...';
            
            // Re-enable after 3 seconds
            setTimeout(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = submitBtn.dataset.originalText || 'Submit';
            }, 3000);
        }
    }

    validateURL(event) {
        const input = event.target;
        const url = input.value;
        const feedback = input.parentNode.querySelector('.invalid-feedback') || 
                        this.createFeedbackElement(input);

        try {
            new URL(url);
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
            feedback.style.display = 'none';
        } catch {
            if (url.length > 0) {
                input.classList.remove('is-valid');
                input.classList.add('is-invalid');
                feedback.textContent = 'Please enter a valid URL (e.g., https://example.com)';
                feedback.style.display = 'block';
            }
        }
    }

    createFeedbackElement(input) {
        const feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        input.parentNode.appendChild(feedback);
        return feedback;
    }

    setupFormValidation() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (event) => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });
    }

    startLiveUpdates() {
        // Update live indicators
        const indicators = document.querySelectorAll('.live-indicator');
        indicators.forEach(indicator => {
            setInterval(() => {
                indicator.style.opacity = indicator.style.opacity === '0.5' ? '1' : '0.5';
            }, 1000);
        });
    }

    // Utility methods
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleString();
    }

    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showNotification('Copied to clipboard!', 'success');
        }).catch(() => {
            this.showNotification('Failed to copy', 'danger');
        });
    }
}

// Honeypot specific functionality
class HoneypotLogger {
    constructor() {
        this.logs = [];
        this.setupLogging();
    }

    setupLogging() {
        // Log all interactions in honeypot
        if (window.location.pathname.includes('honeypot')) {
            this.logPageView();
            this.setupInteractionLogging();
        }
    }

    logPageView() {
        this.log('page_view', {
            url: window.location.href,
            referrer: document.referrer,
            userAgent: navigator.userAgent,
            timestamp: new Date().toISOString()
        });
    }

    setupInteractionLogging() {
        // Log clicks
        document.addEventListener('click', (event) => {
            this.log('click', {
                element: event.target.tagName,
                id: event.target.id,
                className: event.target.className,
                text: event.target.textContent?.substring(0, 50),
                timestamp: new Date().toISOString()
            });
        });

        // Log form inputs
        document.addEventListener('input', (event) => {
            this.log('input', {
                element: event.target.tagName,
                name: event.target.name,
                type: event.target.type,
                value: event.target.value?.substring(0, 100), // Limit for security
                timestamp: new Date().toISOString()
            });
        });

        // Log form submissions
        document.addEventListener('submit', (event) => {
            event.preventDefault(); // Prevent actual submission
            
            const formData = new FormData(event.target);
            const data = {};
            for (let [key, value] of formData.entries()) {
                data[key] = value?.substring(0, 100); // Limit for security
            }
            
            this.log('form_submit', {
                formData: data,
                timestamp: new Date().toISOString()
            });

            // Show fake error message
            setTimeout(() => {
                alert('Login failed. Please check your credentials and try again.');
            }, 1000);
        });
    }

    log(action, data) {
        const logEntry = {
            action,
            data,
            sessionId: this.getSessionId(),
            ip: 'client-side' // Will be replaced by server
        };
        
        this.logs.push(logEntry);
        
        // Send to server (in real implementation)
        this.sendToServer(logEntry);
    }

    getSessionId() {
        let sessionId = sessionStorage.getItem('honeypot_session');
        if (!sessionId) {
            sessionId = 'session_' + Math.random().toString(36).substr(2, 9);
            sessionStorage.setItem('honeypot_session', sessionId);
        }
        return sessionId;
    }

    sendToServer(logEntry) {
        // In a real implementation, this would send data to the server
        console.log('Honeypot Log:', logEntry);
        
        // Simulate server call
        fetch('/api/honeypot-log', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(logEntry)
        }).catch(() => {
            // Silently fail - we don't want to alert the attacker
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PhantomEye();
    new HoneypotLogger();
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .fade-in {
        animation: slideIn 0.5s ease-out;
    }
`;
document.head.appendChild(style);

