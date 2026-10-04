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
        // Checkboxes move with their parent .tiebreak-item, so DOM order
        // already matches visual order — nothing else to update.
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

    // Keyboard fallback: up/down buttons reorder without a mouse.
    // (DOM order is the submit order, so moving the node is sufficient.)
    document.querySelectorAll('.tiebreak-item').forEach(item => {
        var up = item.querySelector('.tb-up');
        var down = item.querySelector('.tb-down');
        if (up) up.addEventListener('click', function () {
            var prev = item.previousElementSibling;
            if (prev) { list.insertBefore(item, prev); item.querySelector('.tb-up').focus(); }
        });
        if (down) down.addEventListener('click', function () {
            var next = item.nextElementSibling;
            if (next) { list.insertBefore(next, item); item.querySelector('.tb-down').focus(); }
        });
    });
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', initTiebreakDnd);

// Export for potential external use
window.TiebreakDnd = {
    init: initTiebreakDnd
};