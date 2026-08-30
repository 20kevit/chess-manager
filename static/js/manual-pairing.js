/**
 * Manual Pairing Validation
 * Handles board swap validation for manual pairing page
 */

function initManualPairingValidation() {
    const board1Select = document.getElementById('board1');
    const board2Select = document.getElementById('board2');
    const submitBtn = document.getElementById('swap-submit-btn');
    const warning = document.getElementById('swap-warning');

    if (!board1Select || !board2Select || !submitBtn || !warning) return;

    function validateBoards() {
        const b1 = board1Select.value;
        const b2 = board2Select.value;

        if (b1 && b2 && b1 === b2) {
            warning.style.display = 'block';
            submitBtn.disabled = true;
        } else {
            warning.style.display = 'none';
            submitBtn.disabled = false;
        }
    }

    board1Select.addEventListener('change', validateBoards);
    board2Select.addEventListener('change', validateBoards);

    // Initial validation
    validateBoards();
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', initManualPairingValidation);

// Export for potential external use
window.ManualPairing = {
    init: initManualPairingValidation
};