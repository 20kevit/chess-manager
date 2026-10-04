/**
 * Tournament View JavaScript
 * Handles tab switching and standings highlighting/filtering
 */

function initTournamentView() {
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');
    const filterBtns = document.querySelectorAll('.filter-btn');
    const standingsBody = document.getElementById('standings-body');
    const playerRows = document.querySelectorAll('.player-row');

    // Check if we're on the tournament view page
    if (!tabs.length && !filterBtns.length) return;

    // Get cumulative mode from data attribute
    const cumulativeMode = document.body.dataset.cumulativeAgeCategory === 'true';

    // Age order for cumulative filtering
    const ageOrder = {
        'U08': 8, 'U10': 10, 'U12': 12, 'U14': 14,
        'U16': 16, 'U18': 18, 'U20': 20,
        'S50': 50, 'S65': 65
    };

    // Tab switching (tablist pattern: arrows move, ARIA stays in sync)
    function selectTab(tab, focus) {
        const tabName = tab.getAttribute('data-tab');
        if (!tabName) return;
        tabs.forEach(t => {
            t.classList.remove('active');
            t.setAttribute('aria-selected', 'false');
            t.tabIndex = -1;
        });
        tabContents.forEach(c => c.classList.remove('active'));
        tab.classList.add('active');
        tab.setAttribute('aria-selected', 'true');
        tab.tabIndex = 0;
        const targetContent = document.getElementById('tab-' + tabName);
        if (targetContent) targetContent.classList.add('active');
        if (focus) tab.focus();
    }
    tabs.forEach((tab, i) => {
        tab.addEventListener('click', function() { selectTab(this, false); });
        tab.addEventListener('keydown', function(e) {
            // In RTL, ArrowLeft moves forward visually; support both directions.
            var next = null;
            if (e.key === 'ArrowRight') next = tabs[(i - 1 + tabs.length) % tabs.length];
            else if (e.key === 'ArrowLeft') next = tabs[(i + 1) % tabs.length];
            else if (e.key === 'Home') next = tabs[0];
            else if (e.key === 'End') next = tabs[tabs.length - 1];
            if (next) { e.preventDefault(); selectTab(next, true); }
        });
    });

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