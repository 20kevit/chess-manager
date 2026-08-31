/**
 * Main Application JavaScript
 * Global functionality: CSRF token injection, notification dropdown
 */

// Auto-inject CSRF token into all POST forms
function injectCSRFToken() {
    const tokenMeta = document.querySelector('meta[name="csrf-token"]');
    if (!tokenMeta) return;

    const csrfValue = tokenMeta.getAttribute('content');
    const forms = document.querySelectorAll('form[method="POST"], form[method="post"]');

    forms.forEach(function(form) {
        if (!form.querySelector('input[name="csrf_token"]')) {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'csrf_token';
            input.value = csrfValue;
            form.appendChild(input);
        }
    });
}

// Notification Dropdown
function initNotificationDropdown() {
    const bell = document.getElementById('notifBell');
    const dropdown = document.getElementById('notifDropdown');
    const body = document.getElementById('notifDropdownBody');
    const countBadge = document.getElementById('notifCount');

    if (!bell || !dropdown || !body) return;

    let isLoaded = false;

    bell.addEventListener('click', function(e) {
        e.preventDefault();
        const expanded = bell.getAttribute('aria-expanded') === 'true';
        bell.setAttribute('aria-expanded', !expanded);
        if (dropdown.style.display === 'none') {
            dropdown.style.display = 'block';
            if (!isLoaded) {
                body.innerHTML = '<p style="text-align:center; padding:10px; color:var(--gray-500);">در حال بارگذاری...</p>';
                fetch('/api/notifications')
                    .then(res => res.json())
                    .then(data => {
                        isLoaded = true;
                        if (!data.notifications || data.notifications.length === 0) {
                            body.innerHTML = '<p style="text-align:center; padding:10px; color:var(--gray-500);">اعلان جدیدی وجود ندارد.</p>';
                            return;
                        }
                        body.innerHTML = '';
                        data.notifications.forEach(n => {
                            const item = document.createElement('div');
                            item.className = 'notif-dropdown-item' + (n.is_read ? '' : ' unread');
                            item.innerHTML = `
                                <strong>${escapeHtml(n.title)}</strong>
                                <p>${escapeHtml(n.message)}</p>
                                <small>${escapeHtml(n.created_at)}</small>
                            `;
                            if (n.link_url) {
                                item.style.cursor = 'pointer';
                                item.addEventListener('click', () => {
                                    window.location.href = n.link_url;
                                });
                            }
                            body.appendChild(item);
                        });

                        // Update badge
                        if (data.unread_count === 0 && countBadge) {
                            countBadge.remove();
                        } else if (countBadge) {
                            countBadge.textContent = data.unread_count;
                        }
                    })
                    .catch(() => {
                        body.innerHTML = '<p style="text-align:center; padding:10px; color:var(--error);">خطا در بارگذاری اعلان‌ها</p>';
                        isLoaded = false;
                    });
            }
        } else {
            dropdown.style.display = 'none';
        }
    });

    // Close dropdown when clicking outside or ESC
    document.addEventListener('click', function(e) {
        if (!bell.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.style.display = 'none';
            bell.setAttribute('aria-expanded', 'false');
        }
    });
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && dropdown.style.display === 'block') {
            dropdown.style.display = 'none';
            bell.setAttribute('aria-expanded', 'false');
            bell.focus();
        }
    });
}

// Utility: Escape HTML to prevent XSS
function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Generic toggle handler for elements with data-target/data-action/data-class
function initToggleHandlers() {
    document.querySelectorAll('[data-target][data-action="toggle-class"]').forEach(trigger => {
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            const targetSelector = this.getAttribute('data-target');
            const className = this.getAttribute('data-class');
            if (!targetSelector || !className) return;

            const target = document.querySelector(targetSelector);
            if (target) {
                target.classList.toggle(className);
            }
        });
    });
}

// Double-submit protection
function initDoubleSubmitProtection() {
    document.querySelectorAll('form[method="POST"]').forEach(form => {
        form.addEventListener('submit', function() {
            const btn = form.querySelector('button[type="submit"]');
            if (btn && !btn.dataset.noDisable) {
                btn.disabled = true;
                btn.dataset.originalText = btn.textContent;
                btn.innerHTML = '<span class="loading-spinner" aria-hidden="true"></span> در حال ارسال...';
                setTimeout(() => { btn.disabled = false; if (btn.dataset.originalText) btn.textContent = btn.dataset.originalText; }, 5000);
            }
        });
    });
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    injectCSRFToken();
    initNotificationDropdown();
    initToggleHandlers();
    initDoubleSubmitProtection();
});

// Expose utilities globally for other scripts
window.AppUtils = {
    injectCSRFToken,
    initNotificationDropdown,
    escapeHtml,
    getCSRFToken: function() {
        const tokenMeta = document.querySelector('meta[name="csrf-token"]');
        return tokenMeta ? tokenMeta.getAttribute('content') : '';
    }
};