/**
 * StrategiX Agent Frontend JavaScript
 * Main application JavaScript file
 */

// Global variables
let currentAnalysisId = null;
let progressInterval = null;

// Utility functions
const Utils = {
    // Show notification
    showNotification: function(message, type = 'info') {
        const alertClass = `alert-${type}`;
        const notification = $(`
            <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `);
        
        // Add to page
        $('main').prepend(notification);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            notification.alert('close');
        }, 5000);
    },

    // Format date
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // Validate form
    validateForm: function(formData) {
        const errors = [];
        
        if (!formData.research_topic || formData.research_topic.trim() === '') {
            errors.push('Research topic is required');
        }
        
        // Drug name and indication are optional even for pipeline research
        // Users can just enter the drug name in the research topic field
        
        return errors;
    },

    // Debounce function
    debounce: function(func, wait) {
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
};

// API functions
const API = {
    // Get system status
    getStatus: function() {
        return $.get('/api/status');
    },

    // Get examples
    getExamples: function() {
        return $.get('/api/examples');
    },

    // Start analysis
    startAnalysis: function(data) {
        return $.ajax({
            url: '/api/start_analysis',
            method: 'POST',
            data: data
        });
    }
};

// Form handling
const FormHandler = {
    // Initialize form handlers
    init: function() {
        this.handleResearchTypeChange();
        this.handleFormSubmission();
        this.handleExampleSelection();
    },

    // Handle research type change
    handleResearchTypeChange: function() {
        $('input[name="research_type"]').on('change', function() {
            const type = $(this).val();
            if (type === 'pipeline') {
                $('#pipelineFields').slideDown();
                // Don't make fields required - they're optional
            } else {
                $('#pipelineFields').slideUp();
            }
        });
    },

    // Handle form submission
    handleFormSubmission: function() {
        $('#researchForm').on('submit', function(e) {
            e.preventDefault();
            
            const formData = {
                research_topic: $('#research_topic').val(),
                research_type: $('input[name="research_type"]:checked').val(),
                drug_name: $('#drug_name').val(),
                indication: $('#indication').val()
            };

            // Validate form
            const errors = Utils.validateForm(formData);
            if (errors.length > 0) {
                Utils.showNotification(errors.join('<br>'), 'error');
                return;
            }

            // Show loading state
            const submitBtn = $('#submitBtn');
            const originalText = submitBtn.html();
            submitBtn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-2"></i>Processing...');

            // Submit form
            $.ajax({
                url: $(this).attr('action'),
                method: 'POST',
                data: formData,
                success: function(response) {
                    if (response.success) {
                        Utils.showNotification('Research configuration created successfully!', 'success');
                        setTimeout(() => {
                            window.location.href = response.redirect;
                        }, 1000);
                    } else {
                        Utils.showNotification(response.error, 'error');
                    }
                },
                error: function(xhr) {
                    let error = 'An error occurred';
                    if (xhr.responseJSON && xhr.responseJSON.error) {
                        error = xhr.responseJSON.error;
                    }
                    Utils.showNotification(error, 'error');
                },
                complete: function() {
                    submitBtn.prop('disabled', false).html(originalText);
                }
            });
        });
    },

    // Handle example selection
    handleExampleSelection: function() {
        $(document).on('click', '.example-card', function() {
            const topic = $(this).data('topic');
            const type = $(this).data('type');
            
            $('#research_topic').val(topic);
            $(`input[name="research_type"][value="${type}"]`).prop('checked', true).trigger('change');
            
            // Highlight selected example
            $('.example-card').removeClass('border-primary bg-light');
            $(this).addClass('border-primary bg-light');
        });
    }
};

// Progress tracking
const ProgressTracker = {
    // Initialize progress tracking
    init: function() {
        this.updateProgressBar();
        this.updateTimeRemaining();
    },

    // Update progress bar
    updateProgressBar: function() {
        const progressBar = $('#progressBar');
        if (progressBar.length) {
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 10;
                if (progress > 90) {
                    progress = 90;
                    clearInterval(interval);
                }
                progressBar.css('width', progress + '%');
            }, 2000);
        }
    },

    // Update time remaining
    updateTimeRemaining: function() {
        const timeElement = $('#timeRemaining');
        if (timeElement.length) {
            let timeLeft = 300; // 5 minutes in seconds
            const interval = setInterval(() => {
                timeLeft -= 10;
                const minutes = Math.floor(timeLeft / 60);
                const seconds = timeLeft % 60;
                timeElement.text(`${minutes}:${seconds.toString().padStart(2, '0')}`);
                
                if (timeLeft <= 0) {
                    clearInterval(interval);
                    timeElement.text('Completing...');
                }
            }, 10000); // Update every 10 seconds
        }
    }
};

// Animation handler
const AnimationHandler = {
    // Initialize animations
    init: function() {
        this.animateOnScroll();
        this.animateCards();
    },

    // Animate elements on scroll
    animateOnScroll: function() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);

        // Observe elements with animation classes
        $('.feature-card, .step-card, .card').each(function() {
            observer.observe(this);
        });
    },

    // Animate cards on hover
    animateCards: function() {
        $('.card, .feature-card, .step-card').hover(
            function() {
                $(this).addClass('shadow-lg');
            },
            function() {
                $(this).removeClass('shadow-lg');
            }
        );
    }
};

// Document ready handler
$(document).ready(function() {
    // Initialize all handlers
    FormHandler.init();
    ProgressTracker.init();
    AnimationHandler.init();

    // Add smooth scrolling
    $('a[href^="#"]').on('click', function(e) {
        e.preventDefault();
        const target = $(this.getAttribute('href'));
        if (target.length) {
            $('html, body').animate({
                scrollTop: target.offset().top - 80
            }, 800);
        }
    });

    // Add loading states to buttons
    $('.btn').on('click', function() {
        const btn = $(this);
        if (!btn.prop('disabled')) {
            btn.addClass('loading');
            setTimeout(() => {
                btn.removeClass('loading');
            }, 2000);
        }
    });

    // Handle mobile menu
    $('.navbar-toggler').on('click', function() {
        $(this).toggleClass('active');
    });

    // Auto-hide alerts
    $('.alert').on('show.bs.alert', function() {
        setTimeout(() => {
            $(this).alert('close');
        }, 5000);
    });

    // Add tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();

    // Handle form validation
    $('input, select, textarea').on('blur', function() {
        const field = $(this);
        const value = field.val();
        
        if (field.prop('required') && (!value || value.trim() === '')) {
            field.addClass('is-invalid');
        } else {
            field.removeClass('is-invalid');
        }
    });

    // Console log for debugging
    console.log('StrategiX Agent Frontend loaded successfully!');
});

// Export for global access
window.StrategiXAgent = {
    Utils,
    API,
    FormHandler,
    ProgressTracker,
    AnimationHandler
}; 