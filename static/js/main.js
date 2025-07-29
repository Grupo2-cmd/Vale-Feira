// Main JavaScript file for Vale Feira

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeFormValidation();
    initializeImagePreviews();
    initializeLoadingStates();
    initializeTooltips();
    
    console.log('Vale Feira initialized successfully');
});

// Form validation enhancements
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Focus on first invalid field
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                }
            }
            
            form.classList.add('was-validated');
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (this.checkValidity()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                }
            });
        });
    });
}

// Image preview functionality
function initializeImagePreviews() {
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    
    imageInputs.forEach(input => {
        input.addEventListener('change', function(event) {
            const file = event.target.files[0];
            const previewId = this.id + 'Preview';
            
            // Remove existing preview
            const existingPreview = document.getElementById(previewId);
            if (existingPreview) {
                existingPreview.remove();
            }
            
            if (file && file.type.startsWith('image/')) {
                // Check file size (16MB limit)
                if (file.size > 16 * 1024 * 1024) {
                    showAlert('Arquivo muito grande! Tamanho máximo: 16MB', 'error');
                    this.value = '';
                    return;
                }
                
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.createElement('div');
                    preview.id = previewId;
                    preview.className = 'mt-3 text-center';
                    preview.innerHTML = `
                        <div class="position-relative d-inline-block">
                            <img src="${e.target.result}" class="img-thumbnail" 
                                 style="max-width: 200px; max-height: 200px;" alt="Preview">
                            <button type="button" class="btn btn-sm btn-danger position-absolute top-0 end-0 rounded-circle" 
                                    onclick="removeImagePreview('${previewId}', '${input.id}')" title="Remover imagem">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                        <div class="text-muted small mt-1">${file.name}</div>
                    `;
                    input.parentNode.appendChild(preview);
                };
                reader.readAsDataURL(file);
            }
        });
    });
}

// Remove image preview
function removeImagePreview(previewId, inputId) {
    const preview = document.getElementById(previewId);
    const input = document.getElementById(inputId);
    
    if (preview) preview.remove();
    if (input) input.value = '';
}

// Loading states for form submissions
function initializeLoadingStates() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && form.checkValidity()) {
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;
                
                // Re-enable after 10 seconds as fallback
                setTimeout(() => {
                    submitBtn.classList.remove('loading');
                    submitBtn.disabled = false;
                }, 10000);
            }
        });
    });
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Utility function to show alerts
function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.container');
    if (!alertContainer) return;
    
    const alertClass = type === 'error' ? 'danger' : type;
    const iconClass = type === 'error' ? 'exclamation-triangle' : 
                     type === 'success' ? 'check-circle' : 'info-circle';
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${alertClass} alert-dismissible fade show mt-3`;
    alert.innerHTML = `
        <i class="fas fa-${iconClass} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.insertBefore(alert, alertContainer.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

// Price formatting
function formatPrice(input) {
    let value = input.value.replace(/\D/g, '');
    value = (value / 100).toFixed(2);
    input.value = value;
}

// WhatsApp contact function
function contactSeller(productName, price, sellerName = '') {
    const message = `Olá${sellerName ? ` ${sellerName}` : ''}! Tenho interesse no produto: ${productName} (${price}). Podemos conversar?`;
    const encodedMessage = encodeURIComponent(message);
    const whatsappUrl = `https://wa.me/?text=${encodedMessage}`;
    window.open(whatsappUrl, '_blank');
}

// Search functionality enhancements
function initializeSearch() {
    const searchForm = document.querySelector('form[action*="site"]');
    if (!searchForm) return;
    
    const searchInput = searchForm.querySelector('input[name="busca"]');
    if (!searchInput) return;
    
    // Add search suggestions (if needed in future)
    let searchTimeout;
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            // Implement search suggestions here if needed
        }, 300);
    });
}

// Initialize search when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeSearch);

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Handle network errors gracefully
window.addEventListener('online', function() {
    showAlert('Conexão restaurada!', 'success');
});

window.addEventListener('offline', function() {
    showAlert('Conexão perdida. Verifique sua internet.', 'error');
});

// Back to top functionality
function addBackToTop() {
    const backToTop = document.createElement('button');
    backToTop.innerHTML = '<i class="fas fa-arrow-up"></i>';
    backToTop.className = 'btn btn-primary position-fixed';
    backToTop.style.cssText = `
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        display: none;
    `;
    backToTop.title = 'Voltar ao topo';
    
    document.body.appendChild(backToTop);
    
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTop.style.display = 'block';
        } else {
            backToTop.style.display = 'none';
        }
    });
    
    backToTop.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Initialize back to top button
document.addEventListener('DOMContentLoaded', addBackToTop);
