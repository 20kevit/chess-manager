/**
 * Notifications Page JavaScript
 * Handles mark-as-read (individual + bulk), bell badge updates
 */

function initNotificationsPage() {
    function settleRow(row) {
        row.classList.remove('unread');
        row.style.cursor = 'default';
        const dot = row.querySelector('.unread-dot');
        if (dot) dot.remove();
        const btn = row.querySelector('.notif-read-btn');
        if (btn) btn.remove();
        updateBellBadge(-1);
        if (document.querySelectorAll('.notif-row.unread').length === 0) {
            const markAllBtn = document.getElementById('markAllReadBtn');
            if (markAllBtn) markAllBtn.remove();
        }
    }

    // Explicit icon-only mark-as-read buttons (keyboard + touch first-class).
    document.querySelectorAll('.notif-read-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const id = this.dataset.id;
            const row = this.closest('.notif-row');
            markAsRead(id).then(success => { if (success && row) settleRow(row); });
        });
    });

    // Mark individual notification as read on row click (convenience).
    document.querySelectorAll('.notif-row.unread').forEach(item => {
        item.addEventListener('click', function(e) {
            // Don't trigger if clicking on a link/button inside
            if (e.target.closest('a, button')) return;

            const id = this.dataset.id;
            const row = this;

            markAsRead(id).then(success => { if (success) settleRow(row); });
        });
    });

    // Mark all as read
    const markAllBtn = document.getElementById('markAllReadBtn');
    if (markAllBtn) {
        markAllBtn.addEventListener('click', function(e) {
            e.preventDefault();
            markAllAsRead().then(success => {
                if (success) {
                    document.querySelectorAll('.notif-row.unread').forEach(el => {
                        el.classList.remove('unread');
                        el.style.cursor = 'default';
                        const dot = el.querySelector('.unread-dot');
                        if (dot) dot.remove();
                        const btn = el.querySelector('.notif-read-btn');
                        if (btn) btn.remove();
                    });

                    const badge = document.getElementById('notifCount');
                    if (badge) badge.remove();

                    this.remove();
                }
            });
        });
    }
}

function markAsRead(notificationId) {
    return fetch(`/api/notifications/${notificationId}/read`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCSRFToken() }
    })
    .then(res => res.json())
    .then(data => data.success === true)
    .catch(() => false);
}

function markAllAsRead() {
    return fetch('/api/notifications/read-all', {
        method: 'POST',
        headers: { 'X-CSRFToken': getCSRFToken() }
    })
    .then(res => res.json())
    .then(data => data.success === true)
    .catch(() => false);
}

function updateBellBadge(delta) {
    const badge = document.getElementById('notifCount');
    if (!badge) return;

    let currentCount = parseInt(badge.textContent) || 0;
    currentCount = Math.max(0, currentCount + delta);

    if (currentCount === 0) {
        badge.remove();
    } else {
        badge.textContent = currentCount;
    }
}

function getCSRFToken() {
    const tokenMeta = document.querySelector('meta[name="csrf-token"]');
    return tokenMeta ? tokenMeta.getAttribute('content') : '';
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', initNotificationsPage);

// Export for potential external use
window.Notifications = {
    markAsRead,
    markAllAsRead,
    updateBellBadge,
    getCSRFToken
};