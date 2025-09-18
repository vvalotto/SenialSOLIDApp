// Senial SOLID - Optimized JavaScript
// Import Bootstrap for components
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

// Performance optimizations
const requestIdleCallback = window.requestIdleCallback || function(cb) {
    return setTimeout(cb, 1);
};

const cancelIdleCallback = window.cancelIdleCallback || clearTimeout;

// Debounce utility for performance
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func.apply(this, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(this, args);
    };
}

// Throttle utility for performance
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Bootstrap 5 form validation - Optimized
function initFormValidation() {
    const forms = document.getElementsByClassName('needs-validation');
    
    Array.prototype.forEach.call(forms, function(form) {
        form.addEventListener('submit', function(event) {
            if (form.checkValidity() === false) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
        
        // Real-time validation feedback
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(function(input) {
            input.addEventListener('blur', debounce(function() {
                if (input.checkValidity()) {
                    input.classList.remove('is-invalid');
                    input.classList.add('is-valid');
                } else {
                    input.classList.remove('is-valid');
                    input.classList.add('is-invalid');
                }
            }, 150));
            
            input.addEventListener('input', debounce(function() {
                if (input.classList.contains('was-validated') || input.classList.contains('is-invalid')) {
                    if (input.checkValidity()) {
                        input.classList.remove('is-invalid');
                        input.classList.add('is-valid');
                    } else {
                        input.classList.remove('is-valid');
                        input.classList.add('is-invalid');
                    }
                }
            }, 300));
        });
    });
}

// Enhanced form interactions
function initFormInteractions() {
    // Auto-focus first input
    const firstInput = document.querySelector('input[type="text"], input[type="email"], textarea');
    if (firstInput) {
        firstInput.focus();
    }
    
    // Form submission loading state
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn && form.checkValidity()) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Procesando...';
            }
        });
    });
}

// Table functionality - Optimized with event delegation
function initializeTables() {
    // Add sorting functionality
    document.addEventListener('click', function(e) {
        if (e.target.matches('th[aria-sort]') || e.target.closest('th[aria-sort]')) {
            const header = e.target.closest('th[aria-sort]');
            sortTable(header);
        }
    });
    
    // Add cursor pointer to sortable headers
    const sortableHeaders = document.querySelectorAll('th[aria-sort]');
    sortableHeaders.forEach(header => {
        header.style.cursor = 'pointer';
    });
    
    // Optimized hover effects using delegation
    const tables = document.querySelectorAll('tbody');
    tables.forEach(tbody => {
        tbody.addEventListener('mouseenter', function(e) {
            if (e.target.matches('tr') && !e.target.querySelector('.text-muted')) {
                e.target.style.backgroundColor = 'var(--bs-primary-bg-subtle)';
            }
        }, true);
        
        tbody.addEventListener('mouseleave', function(e) {
            if (e.target.matches('tr')) {
                e.target.style.backgroundColor = '';
            }
        }, true);
    });
}

// Optimized table refresh function
function refreshTable() {
    const refreshBtn = document.querySelector('[data-action="refresh"]');
    if (refreshBtn) {
        const originalContent = refreshBtn.innerHTML;
        refreshBtn.innerHTML = '<i class="bi bi-arrow-clockwise spin"></i>';
        refreshBtn.disabled = true;
        
        // Use requestAnimationFrame for smooth animation
        requestAnimationFrame(() => {
            setTimeout(() => {
                location.reload();
            }, 1000);
        });
    }
}

// Optimized CSV export
function exportTable() {
    const table = document.getElementById('signals-table');
    if (!table) return;
    
    // Use DocumentFragment for better performance
    const fragment = document.createDocumentFragment();
    let csv = '';
    const rows = table.querySelectorAll('tr');
    
    rows.forEach(row => {
        const cells = row.querySelectorAll('th, td');
        const rowData = Array.from(cells).map(cell => {
            return '"' + cell.textContent.trim().replace(/"/g, '""') + '"';
        });
        if (rowData.some(cell => cell !== '""')) {
            csv += rowData.join(',') + '\\n';
        }
    });
    
    // Download CSV using modern approach
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'seniales_' + new Date().toISOString().slice(0, 10) + '.csv';
    link.click();
    URL.revokeObjectURL(url);
}

// Modern event handlers using delegation
function initializeButtonHandlers() {
    // Use event delegation for better performance
    document.addEventListener('click', function(e) {
        const target = e.target.closest('[data-action]');
        if (!target) return;
        
        const action = target.dataset.action;
        
        switch (action) {
            case 'refresh':
                refreshTable();
                break;
            case 'export':
                exportTable();
                break;
            case 'view':
                viewSignal(target.dataset.signalId);
                break;
            case 'edit':
                editSignal(target.dataset.signalId);
                break;
            case 'delete':
                deleteSignal(target.dataset.signalId);
                break;
        }
    });
}

// Signal action functions
function viewSignal(signalId) {
    showInfoToast('Ver detalles de señal: ' + signalId, 'Funcionalidad próximamente');
}

function editSignal(signalId) {
    showInfoToast('Editar señal: ' + signalId, 'Funcionalidad próximamente');
}

function deleteSignal(signalId) {
    if (confirm('¿Estás seguro de que deseas eliminar la señal "' + signalId + '"?\\n\\nEsta acción no se puede deshacer.')) {
        showSuccessToast('Señal "' + signalId + '" eliminada exitosamente.');
        // In real app, this would be an AJAX call
        setTimeout(() => location.reload(), 1500);
    }
}

// Optimized table sorting
function sortTable(header) {
    const table = header.closest('table');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr')).filter(row => !row.querySelector('.text-muted'));
    
    if (rows.length === 0) return;
    
    const columnIndex = Array.from(header.parentNode.children).indexOf(header);
    const currentSort = header.getAttribute('aria-sort');
    const isAscending = currentSort !== 'ascending';
    
    // Reset all sort indicators efficiently
    table.querySelectorAll('th[aria-sort]').forEach(th => {
        th.setAttribute('aria-sort', 'none');
        const icon = th.querySelector('.sort-icon');
        if (icon) {
            icon.className = 'bi bi-arrow-down-up text-muted ms-2 sort-icon';
        }
    });
    
    // Set current sort
    header.setAttribute('aria-sort', isAscending ? 'ascending' : 'descending');
    const icon = header.querySelector('.sort-icon');
    if (icon) {
        icon.className = isAscending ? 
            'bi bi-arrow-up text-primary ms-2 sort-icon' : 
            'bi bi-arrow-down text-primary ms-2 sort-icon';
    }
    
    // Optimized sorting with Intl.Collator
    const collator = new Intl.Collator('es', { numeric: true, sensitivity: 'base' });
    rows.sort((a, b) => {
        const aText = a.cells[columnIndex].textContent.trim();
        const bText = b.cells[columnIndex].textContent.trim();
        return isAscending ? collator.compare(aText, bText) : collator.compare(bText, aText);
    });
    
    // Use DocumentFragment for efficient DOM manipulation
    const fragment = document.createDocumentFragment();
    rows.forEach(row => fragment.appendChild(row));
    tbody.appendChild(fragment);
}

// Enhanced Toast Notification System
function showToast(message, type = 'info', title = null, duration = 5000) {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;
    
    const toastId = 'toast-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    
    const icons = {
        'success': 'bi-check-circle',
        'error': 'bi-exclamation-triangle',
        'warning': 'bi-exclamation-triangle',
        'info': 'bi-info-circle'
    };
    
    const titles = {
        'success': title || 'Éxito',
        'error': title || 'Error',
        'warning': title || 'Advertencia',
        'info': title || 'Información'
    };
    
    const toastTemplate = document.createElement('div');
    toastTemplate.id = toastId;
    toastTemplate.className = `toast toast-${type}`;
    toastTemplate.setAttribute('role', 'alert');
    toastTemplate.setAttribute('aria-live', 'assertive');
    toastTemplate.setAttribute('aria-atomic', 'true');
    toastTemplate.setAttribute('data-bs-autohide', 'true');
    toastTemplate.setAttribute('data-bs-delay', duration);
    
    toastTemplate.innerHTML = `
        <div class="toast-header">
            <i class="bi ${icons[type]} me-2" aria-hidden="true"></i>
            <strong class="me-auto">${titles[type]}</strong>
            <small class="text-muted">ahora</small>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Cerrar notificación"></button>
        </div>
        <div class="toast-body">${message}</div>
    `;
    
    toastContainer.appendChild(toastTemplate);
    
    // Initialize Bootstrap toast
    const toast = new bootstrap.Toast(toastTemplate);
    toast.show();
    
    // Clean up after hiding
    toastTemplate.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
    
    return toast;
}

// Global toast functions
window.showSuccessToast = function(message, title) {
    return showToast(message, 'success', title);
};

window.showErrorToast = function(message, title) {
    return showToast(message, 'error', title);
};

window.showWarningToast = function(message, title) {
    return showToast(message, 'warning', title);
};

window.showInfoToast = function(message, title) {
    return showToast(message, 'info', title);
};

// Loading State Management - Optimized
function showGlobalLoading(message = 'Cargando...') {
    const overlay = document.getElementById('loading-overlay');
    const loadingText = overlay?.querySelector('.loading-text');
    if (overlay && loadingText) {
        loadingText.textContent = message;
        overlay.style.display = 'flex';
        overlay.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    }
}

function hideGlobalLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'none';
        overlay.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }
}

function setButtonLoading(button, loading = true, originalText = null) {
    if (!button) return;
    
    if (loading) {
        if (!originalText) {
            originalText = button.innerHTML;
        }
        button.dataset.originalText = originalText;
        button.classList.add('btn-loading');
        button.disabled = true;
        button.innerHTML = '<span class="btn-text">' + originalText + '</span>';
        button.setAttribute('aria-busy', 'true');
    } else {
        button.classList.remove('btn-loading');
        button.disabled = false;
        button.innerHTML = button.dataset.originalText || button.innerHTML;
        button.removeAttribute('data-original-text');
        button.setAttribute('aria-busy', 'false');
    }
}

// Global loading utilities
window.showLoading = showGlobalLoading;
window.hideLoading = hideGlobalLoading;
window.setButtonLoading = setButtonLoading;

// Intersection Observer for lazy loading (future use)
function createLazyLoader() {
    if ('IntersectionObserver' in window) {
        const lazyImages = document.querySelectorAll('[data-src]');
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        lazyImages.forEach(img => imageObserver.observe(img));
    }
}

// Performance monitoring
function initPerformanceMonitoring() {
    // Core Web Vitals
    if ('PerformanceObserver' in window) {
        // Largest Contentful Paint
        const lcpObserver = new PerformanceObserver((list) => {
            const entries = list.getEntries();
            const lastEntry = entries[entries.length - 1];
            console.log('LCP:', lastEntry.startTime);
        });
        lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
        
        // First Input Delay
        const fidObserver = new PerformanceObserver((list) => {
            list.getEntries().forEach(entry => {
                console.log('FID:', entry.processingStart - entry.startTime);
            });
        });
        fidObserver.observe({ entryTypes: ['first-input'] });
        
        // Cumulative Layout Shift
        let clsValue = 0;
        const clsObserver = new PerformanceObserver((list) => {
            list.getEntries().forEach(entry => {
                if (!entry.hadRecentInput) {
                    clsValue += entry.value;
                    console.log('CLS:', clsValue);
                }
            });
        });
        clsObserver.observe({ entryTypes: ['layout-shift'] });
    }
}

// Initialize everything when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Use requestIdleCallback for non-critical tasks
    requestIdleCallback(() => {
        initFormValidation();
        initFormInteractions();
        initializeTables();
        initializeButtonHandlers();
        createLazyLoader();
        
        if (process.env.NODE_ENV === 'development') {
            initPerformanceMonitoring();
        }
    });
});

// Handle page visibility for performance optimization
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Pause heavy operations when page is not visible
        console.log('Page hidden - pausing operations');
    } else {
        // Resume operations when page is visible
        console.log('Page visible - resuming operations');
    }
});

// Export for webpack
export {
    showToast,
    showGlobalLoading,
    hideGlobalLoading,
    setButtonLoading,
    debounce,
    throttle
};