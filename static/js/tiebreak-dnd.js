/**
 * Tiebreak Drag & Drop
 * Handles drag-and-drop reordering of tiebreak items
 */

function initTiebreakDnd() {
    const list = document.getElementById('tiebreak-list');
    if (!list) return;

    let draggedItem = null;

    // Make items draggable
    document.querySelectorAll('.tiebreak-item').forEach(item => {
        item.setAttribute('draggable', 'true');

        item.addEventListener('dragstart', function(e) {
            draggedItem = this;
            setTimeout(() => this.classList.add('tb-dragging'), 0);
            e.dataTransfer.effectAllowed = 'move';
        });

        item.addEventListener('dragend', function() {
            this.classList.remove('tb-dragging');
            draggedItem = null;
        });

        item.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
        });
    });

    list.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';

        const afterElement = getDragAfterElement(list, e.clientY);
        if (draggedItem) {
            if (afterElement == null) {
                list.appendChild(draggedItem);
            } else {
                list.insertBefore(draggedItem, afterElement);
            }
        }
    });

    list.addEventListener('drop', function(e) {
        e.preventDefault();
        // Update checkbox order to match visual order
        updateCheckboxOrder();
    });

    function getDragAfterElement(container, y) {
        const draggableElements = [...container.querySelectorAll('.tiebreak-item:not(.tb-dragging)')];

        return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;
            if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child };
            } else {
                return closest;
            }
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    }

    function updateCheckboxOrder() {
        // The form will submit checkboxes in DOM order, which now matches visual order
        // No additional action needed since checkboxes move with their parent .tiebreak-item
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', initTiebreakDnd);

// Export for potential external use
window.TiebreakDnd = {
    init: initTiebreakDnd
};