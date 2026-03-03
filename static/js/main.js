// Toggle features section
function toggleFeatures() {
    const featuresSection = document.getElementById('features');
    if (featuresSection) {
        if (featuresSection.classList.contains('features-hidden')) {
            featuresSection.classList.remove('features-hidden');
            featuresSection.classList.add('features-visible');
        } else {
            featuresSection.classList.remove('features-visible');
            featuresSection.classList.add('features-hidden');
        }
    }
}

// Modal handlers
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// Close modal when clicking outside
window.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
});

// Form validation
function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    for (let input of inputs) {
        if (!input.value.trim()) {
            alert('Please fill in all required fields');
            input.focus();
            return false;
        }
    }
    return true;
}

// Format date for display
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: '2-digit', day: '2-digit' });
}

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Search functionality
const searchInputs = document.querySelectorAll('input[data-search]');
searchInputs.forEach(input => {
    input.addEventListener('keyup', debounce(function() {
        const searchTerm = this.value.toLowerCase();
        const targetTable = document.querySelector(this.dataset.search);
        if (!targetTable) return;
        
        const rows = targetTable.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    }, 300));
});

// Status transition animation
document.addEventListener('DOMContentLoaded', function() {
    const statusBadges = document.querySelectorAll('.status-badge');
    statusBadges.forEach(badge => {
        badge.style.animationDelay = Math.random() * 0.5 + 's';
    });
});

// Loading spinner
function showLoading() {
    const loader = document.createElement('div');
    loader.className = 'loader';
    loader.id = 'pageLoader';
    document.body.appendChild(loader);
}

function hideLoading() {
    const loader = document.getElementById('pageLoader');
    if (loader) loader.remove();
}

// Smooth scroll to section
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}
