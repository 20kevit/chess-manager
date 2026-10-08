/**
 * Tournament View JavaScript
 * Handles standings highlighting/filtering on the public standings page.
 */

function initTournamentView() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    const standingsBody = document.getElementById('standings-body');
    const playerRows = document.querySelectorAll('.player-row');

    // Check if we're on the standings page with a filter bar
    if (!filterBtns.length) return;

    // Get cumulative mode from data attribute
    const cumulativeMode = document.body.dataset.cumulativeAgeCategory === 'true';

    // Age order for cumulative filtering
    const ageOrder = {
        'U08': 8, 'U10': 10, 'U12': 12, 'U14': 14,
        'U16': 16, 'U18': 18, 'U20': 20,
        'S50': 50, 'S65': 65
    };

    // Standings highlighting/filtering
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const filterType = this.getAttribute('data-filter');
            if (!filterType) return;

            filterBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            if (filterType === 'none') {
                standingsBody.classList.remove('table-filtered');
                playerRows.forEach(row => row.classList.remove('row-highlighted'));
                return;
            }

            standingsBody.classList.add('table-filtered');
            const targetAge = filterType.replace('age-', '');

            playerRows.forEach(row => {
                row.classList.remove('row-highlighted');
                const rowAge = row.getAttribute('data-age');

                let shouldHighlight = false;

                if (cumulativeMode && targetAge.startsWith('U') && rowAge.startsWith('U')) {
                    const selectedLimit = ageOrder[targetAge] || 0;
                    const playerLimit = ageOrder[rowAge] || 0;
                    if (playerLimit > 0 && playerLimit <= selectedLimit) {
                        shouldHighlight = true;
                    }
                } else if (cumulativeMode && targetAge.startsWith('S') && rowAge.startsWith('S')) {
                    const selectedLimit = ageOrder[targetAge] || 0;
                    const playerLimit = ageOrder[rowAge] || 0;
                    if (playerLimit > 0 && playerLimit >= selectedLimit) {
                        shouldHighlight = true;
                    }
                } else {
                    if (rowAge === targetAge) {
                        shouldHighlight = true;
                    }
                }

                if (shouldHighlight) {
                    row.classList.add('row-highlighted');
                }
            });
        });
    });
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', initTournamentView);

// Export for potential external use
window.TournamentView = {
    init: initTournamentView
};