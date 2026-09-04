/**
 * Modal Utility
 * Generic modal open/close functionality
 */

const Modal = (function() {
    const openModals = new Set();

    function open(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        modal.classList.add('active');
        openModals.add(modalId);
        document.body.style.overflow = 'hidden';

        // Focus first focusable element
        const focusable = modal.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
        if (focusable) {
            focusable.focus();
        }

        // Trap focus within modal
        modal.addEventListener('keydown', trapFocus);
    }

    function close(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        modal.classList.remove('active');
        openModals.delete(modalId);

        if (openModals.size === 0) {
            document.body.style.overflow = '';
        }

        modal.removeEventListener('keydown', trapFocus);
    }

    function closeAll() {
        openModals.forEach(id => close(id));
    }

    function trapFocus(e) {
        if (e.key !== 'Tab') return;

        const modal = e.currentTarget;
        const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );

        if (focusableElements.length === 0) return;

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        if (e.shiftKey) {
            if (document.activeElement === firstElement) {
                e.preventDefault();
                lastElement.focus();
            }
        } else {
            if (document.activeElement === lastElement) {
                e.preventDefault();
                firstElement.focus();
            }
        }
    }

    // Close on overlay click
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal-overlay')) {
            const modalId = e.target.id;
            if (modalId) close(modalId);
        }
    });

    // Close on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && openModals.size > 0) {
            closeAll();
        }
    });

    // Auto-init for data-modal-trigger attributes
    document.addEventListener('DOMContentLoaded', function() {
        document.querySelectorAll('[data-modal-trigger]').forEach(trigger => {
            trigger.addEventListener('click', function(e) {
                e.preventDefault();
                const modalId = this.getAttribute('data-modal-trigger');
                open(modalId);
            });
        });

        document.querySelectorAll('[data-modal-close]').forEach(closeBtn => {
            // Overlays close only via direct overlay clicks (see handler
            // above): never wire an overlay element itself as a close
            // button, otherwise every bubbled click from inside .modal-box
            // would immediately close the menu. This guard keeps the modal
            // usable even if the attribute is ever re-added to an overlay.
            if (closeBtn.classList.contains('modal-overlay')) return;
            closeBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                const modalId = this.getAttribute('data-modal-close');
                close(modalId);
            });
        });
    });

    return {
        open,
        close,
        closeAll
    };
})();

// Global access
window.Modal = Modal;