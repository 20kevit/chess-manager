/**
 * Registration Price Calculator
 * Handles dynamic price recalculation on registration form
 */

function initRegistrationCalculator() {
    const form = document.getElementById('reg-form');
    if (!form) return;

    // Get configuration from data attributes
    const apiUrl = form.dataset.apiUrl;
    const basePrice = form.dataset.basePrice;

    if (!apiUrl) return;

    const inputs = ['first_name', 'last_name', 'fide_id', 'birth_date', 'gender', 'promo_code'];
    const basePriceEl = document.getElementById('base-price');
    const finalPriceEl = document.getElementById('final-price');
    const discountListEl = document.getElementById('discount-list');

    let debounceTimer = null;

    function recalculatePrice() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            doRecalculatePrice();
        }, 300);
    }

    function doRecalculatePrice() {
        const data = {};
        inputs.forEach(id => {
            const el = document.getElementById(id);
            if (el) data[id] = el.value;
        });

        const csrfToken = getCSRFToken();

        fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error(data.error);
                return;
            }

            if (basePriceEl) basePriceEl.textContent = data.base_price;
            if (finalPriceEl) finalPriceEl.textContent = data.final_price;

            if (discountListEl) {
                discountListEl.innerHTML = '';
                if (data.discounts && data.discounts.length > 0) {
                    data.discounts.forEach(d => {
                        const div = document.createElement('div');
                        div.className = 'price-row';
                        div.style.fontSize = '0.9rem';
                        div.style.color = '#059669';
                        div.innerHTML = `<span>${escapeHtml(d.reason)}:</span><span>- ${d.amount} تومان</span>`;
                        discountListEl.appendChild(div);
                    });
                }
            }
        })
        .catch(error => console.error('Error:', error));
    }

    // Attach event listeners
    inputs.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('change', recalculatePrice);
            el.addEventListener('input', recalculatePrice);
        }
    });

    // Initial calculation
    recalculatePrice();
}

function getCSRFToken() {
    const tokenMeta = document.querySelector('meta[name="csrf-token"]');
    return tokenMeta ? tokenMeta.getAttribute('content') : '';
}

function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', initRegistrationCalculator);

// Export for potential external use
window.RegistrationCalculator = {
    init: initRegistrationCalculator
};