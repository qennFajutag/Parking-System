/**
 * Park Smart - Modern Parking Management System
 * Enhanced JavaScript for better UX
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize date-time inputs with current date/time
    initializeDateTimeInputs();
    
    // Add validation for booking form
    const bookingForm = document.getElementById('booking-form');
    if (bookingForm) {
        bookingForm.addEventListener('submit', validateBookingForm);
    }
    
    // Add confirmation for cancel actions
    setupCancelConfirmations();
    
    // Format dates and times
    formatDateTimeElements();
    
    // Flash message handling
    setupFlashMessages();
    
    // Add smooth scrolling for anchor links
    setupSmoothScrolling();
    
    // Add input focus effects
    setupInputFocusEffects();
    
    // Add responsive menu toggle if on mobile
    setupMobileMenu();
    
    // Add tooltip functionality
    setupTooltips();
    
    // Calculate booking prices dynamically if on booking form
    setupDynamicPricing();
});

/**
 * Initialize date-time inputs with appropriate values
 */
function initializeDateTimeInputs() {
    const startTimeInput = document.getElementById('start_time');
    const endTimeInput = document.getElementById('end_time');
    
    if (startTimeInput && endTimeInput) {
        // Set start time to current time (rounded to nearest 30 min)
        const now = new Date();
        now.setMinutes(Math.ceil(now.getMinutes() / 30) * 30);
        now.setSeconds(0);
        const formattedNow = formatDateForInput(now);
        startTimeInput.value = formattedNow;
        startTimeInput.min = formattedNow;
        
        // Set end time to current time + 2 hours
        const twoHoursLater = new Date(now.getTime() + 2 * 60 * 60 * 1000);
        const formattedLater = formatDateForInput(twoHoursLater);
        endTimeInput.value = formattedLater;
        endTimeInput.min = formattedNow;
        
        // Ensure end time is after start time
        startTimeInput.addEventListener('change', function() {
            const startTime = new Date(startTimeInput.value);
            const endTime = new Date(endTimeInput.value);
            
            if (endTime <= startTime) {
                const newEndTime = new Date(startTime.getTime() + 2 * 60 * 60 * 1000);
                endTimeInput.value = formatDateForInput(newEndTime);
            }
            
            endTimeInput.min = startTimeInput.value;
            updateBookingPrice();
        });
        
        endTimeInput.addEventListener('change', updateBookingPrice);
    }
}

/**
 * Format date object for input datetime-local
 */
function formatDateForInput(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    
    return `${year}-${month}-${day}T${hours}:${minutes}`;
}

/**
 * Validate booking form before submission
 */
function validateBookingForm(event) {
    const startTimeInput = document.getElementById('start_time');
    const endTimeInput = document.getElementById('end_time');
    const spotSelect = document.getElementById('spot_id');
    
    let isValid = true;
    let errorMessages = [];
    
    if (!spotSelect.value) {
        errorMessages.push('Please select a parking spot');
        isValid = false;
    }
    
    const startTime = new Date(startTimeInput.value);
    const endTime = new Date(endTimeInput.value);
    const now = new Date();
    
    // Validate start time is in the future
    if (startTime < now) {
        errorMessages.push('Start time must be in the future');
        isValid = false;
    }
    
    // Validate end time is after start time
    if (endTime <= startTime) {
        errorMessages.push('End time must be after start time');
        isValid = false;
    }
    
    // Validate booking duration (max 24 hours)
    const durationHours = (endTime - startTime) / (1000 * 60 * 60);
    if (durationHours > 24) {
        errorMessages.push('Booking duration cannot exceed 24 hours');
        isValid = false;
    }
    
    if (!isValid) {
        event.preventDefault();
        showFormErrors(errorMessages);
        return false;
    }
    
    return true;
}

/**
 * Display form errors in a better way than alert
 */
function showFormErrors(messages) {
    // Remove any existing error containers
    const existingError = document.getElementById('form-errors');
    if (existingError) {
        existingError.remove();
    }
    
    // Create error container
    const errorContainer = document.createElement('div');
    errorContainer.id = 'form-errors';
    errorContainer.className = 'flash-message flash-error';
    errorContainer.style.marginBottom = '1rem';
    
    // Add icon
    const icon = document.createElement('i');
    icon.className = 'fas fa-exclamation-circle';
    errorContainer.appendChild(icon);
    
    // Add messages
    const messagesList = document.createElement('ul');
    messagesList.style.margin = '0';
    messagesList.style.paddingLeft = '1.5rem';
    
    messages.forEach(message => {
        const li = document.createElement('li');
        li.textContent = message;
        messagesList.appendChild(li);
    });
    
    errorContainer.appendChild(messagesList);
    
    // Add close button
    const closeBtn = document.createElement('button');
    closeBtn.innerHTML = '&times;';
    closeBtn.className = 'close-btn';
    closeBtn.style.marginLeft = 'auto';
    closeBtn.style.background = 'transparent';
    closeBtn.style.border = 'none';
    closeBtn.style.fontSize = '1.25rem';
    closeBtn.style.cursor = 'pointer';
    closeBtn.style.color = 'inherit';
    closeBtn.onclick = function() {
        errorContainer.remove();
    };
    
    errorContainer.appendChild(closeBtn);
    
    // Add to form
    const form = document.getElementById('booking-form');
    form.prepend(errorContainer);
    
    // Smooth scroll to error
    errorContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Setup confirmation prompts for cancel actions
 */
function setupCancelConfirmations() {
    const cancelLinks = document.querySelectorAll('.cancel-booking');
    
    cancelLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            
            // Create modern confirmation dialog
            const overlay = document.createElement('div');
            overlay.className = 'modal-overlay';
            overlay.style.position = 'fixed';
            overlay.style.top = '0';
            overlay.style.left = '0';
            overlay.style.width = '100%';
            overlay.style.height = '100%';
            overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
            overlay.style.display = 'flex';
            overlay.style.justifyContent = 'center';
            overlay.style.alignItems = 'center';
            overlay.style.zIndex = '1000';
            
            const dialog = document.createElement('div');
            dialog.className = 'confirmation-dialog';
            dialog.style.background = 'white';
            dialog.style.borderRadius = 'var(--radius)';
            dialog.style.padding = '1.5rem';
            dialog.style.boxShadow = 'var(--shadow)';
            dialog.style.maxWidth = '400px';
            dialog.style.width = '90%';
            
            const title = document.createElement('h3');
            title.textContent = 'Confirm Cancellation';
            title.style.marginTop = '0';
            title.style.color = 'var(--primary)';
            
            const message = document.createElement('p');
            message.textContent = 'Are you sure you want to cancel this booking? This action cannot be undone.';
            
            const buttons = document.createElement('div');
            buttons.style.display = 'flex';
            buttons.style.justifyContent = 'flex-end';
            buttons.style.gap = '0.75rem';
            buttons.style.marginTop = '1.5rem';
            
            const cancelBtn = document.createElement('button');
            cancelBtn.textContent = 'No, Keep It';
            cancelBtn.className = 'btn btn-outline';
            cancelBtn.onclick = function() {
                document.body.removeChild(overlay);
            };
            
            const confirmBtn = document.createElement('button');
            confirmBtn.textContent = 'Yes, Cancel';
            confirmBtn.className = 'btn btn-danger';
            confirmBtn.onclick = function() {
                window.location.href = link.href;
            };
            
            buttons.appendChild(cancelBtn);
            buttons.appendChild(confirmBtn);
            
            dialog.appendChild(title);
            dialog.appendChild(message);
            dialog.appendChild(buttons);
            
            overlay.appendChild(dialog);
            document.body.appendChild(overlay);
        });
    });
}

/**
 * Format date and time elements for better readability
 */
function formatDateTimeElements() {
    const dateTimeElements = document.querySelectorAll('.format-datetime');
    
    dateTimeElements.forEach(element => {
        const dateObj = new Date(element.textContent);
        if (!isNaN(dateObj)) {
            const options = { 
                weekday: 'short',
                year: 'numeric', 
                month: 'short', 
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            };
            element.textContent = dateObj.toLocaleDateString(undefined, options);
        }
    });
    
    // Format duration elements
    const durationElements = document.querySelectorAll('.format-duration');
    durationElements.forEach(element => {
        const hours = parseFloat(element.textContent);
        if (!isNaN(hours)) {
            const hoursInt = Math.floor(hours);
            const minutes = Math.round((hours - hoursInt) * 60);
            
            if (hoursInt > 0 && minutes > 0) {
                element.textContent = `${hoursInt}h ${minutes}m`;
            } else if (hoursInt > 0) {
                element.textContent = `${hoursInt} hour${hoursInt !== 1 ? 's' : ''}`;
            } else {
                element.textContent = `${minutes} minute${minutes !== 1 ? 's' : ''}`;
            }
        }
    });
}

/**
 * Setup auto-hiding for flash messages and add close buttons
 */
function setupFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash-message');
    
    flashMessages.forEach(message => {
        // Add close button
        const closeBtn = document.createElement('span');
        closeBtn.innerHTML = '&times;';
        closeBtn.style.marginLeft = 'auto';
        closeBtn.style.cursor = 'pointer';
        closeBtn.style.fontSize = '1.25rem';
        closeBtn.onclick = function() {
            message.style.opacity = '0';
            setTimeout(() => {
                message.style.display = 'none';
            }, 300);
        };
        
        message.appendChild(closeBtn);
        
        // Auto hide flash messages after 5 seconds
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.style.display = 'none';
            }, 300);
        }, 5000);
    });
}

/**
 * Setup smooth scrolling for anchor links
 */
function setupSmoothScrolling() {
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
}

/**
 * Setup focus effects for form inputs
 */
function setupInputFocusEffects() {
    const inputs = document.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
        // Add focus effect to parent form-group if inside one
        input.addEventListener('focus', function() {
            const formGroup = this.closest('.form-group');
            if (formGroup) {
                formGroup.classList.add('focused');
            }
        });
        
        input.addEventListener('blur', function() {
            const formGroup = this.closest('.form-group');
            if (formGroup) {
                formGroup.classList.remove('focused');
            }
        });
    });
}

/**
 * Setup mobile menu toggle
 */
function setupMobileMenu() {
    const header = document.querySelector('header');
    
    if (window.innerWidth < 768 && header) {
        const nav = header.querySelector('nav');
        const menuToggle = document.createElement('button');
        menuToggle.className = 'menu-toggle';
        menuToggle.innerHTML = '<i class="fas fa-bars"></i>';
        menuToggle.style.background = 'transparent';
        menuToggle.style.border = 'none';
        menuToggle.style.fontSize = '1.5rem';
        menuToggle.style.color = 'var(--dark)';
        menuToggle.style.cursor = 'pointer';
        menuToggle.style.display = 'none';
        
        header.insertBefore(menuToggle, nav);
        
        menuToggle.addEventListener('click', function() {
            nav.classList.toggle('active');
            this.innerHTML = nav.classList.contains('active') ? 
                '<i class="fas fa-times"></i>' : '<i class="fas fa-bars"></i>';
        });
    }
}

/**
 * Setup tooltips for elements with data-tooltip attribute
 */
function setupTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.style.position = 'relative';
        element.style.cursor = 'help';
        
        element.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = this.getAttribute('data-tooltip');
            tooltip.style.position = 'absolute';
            tooltip.style.bottom = 'calc(100% + 10px)';
            tooltip.style.left = '50%';
            tooltip.style.transform = 'translateX(-50%)';
            tooltip.style.backgroundColor = 'var(--dark)';
            tooltip.style.color = 'white';
            tooltip.style.padding = '0.5rem 0.75rem';
            tooltip.style.borderRadius = 'var(--radius)';
            tooltip.style.fontSize = '0.875rem';
            tooltip.style.whiteSpace = 'nowrap';
            tooltip.style.zIndex = '100';
            tooltip.style.opacity = '0';
            tooltip.style.transition = 'opacity 0.2s';
            
            const arrow = document.createElement('div');
            arrow.style.position = 'absolute';
            arrow.style.top = '100%';
            arrow.style.left = '50%';
            arrow.style.transform = 'translateX(-50%)';
            arrow.style.width = '0';
            arrow.style.height = '0';
            arrow.style.borderLeft = '6px solid transparent';
            arrow.style.borderRight = '6px solid transparent';
            arrow.style.borderTop = '6px solid var(--dark)';
            
            tooltip.appendChild(arrow);
            this.appendChild(tooltip);
            
            setTimeout(() => {
                tooltip.style.opacity = '1';
            }, 10);
        });
        
        element.addEventListener('mouseleave', function() {
            const tooltip = this.querySelector('.tooltip');
            if (tooltip) {
                tooltip.style.opacity = '0';
                setTimeout(() => {
                    this.removeChild(tooltip);
                }, 200);
            }
        });
    });
}

/**
 * Calculate and display booking price dynamically
 */
function setupDynamicPricing() {
    const priceDisplay = document.getElementById('booking-price');
    const spotSelect = document.getElementById('spot_id');
    
    if (priceDisplay && spotSelect) {
        spotSelect.addEventListener('change', updateBookingPrice);
        updateBookingPrice(); // Initial calculation
    }
}

/**
 * Calculate and update the booking price based on spot and duration
 */
function updateBookingPrice() {
    const priceDisplay = document.getElementById('booking-price');
    const spotSelect = document.getElementById('spot_id');
    const startTimeInput = document.getElementById('start_time');
    const endTimeInput = document.getElementById('end_time');
    
    if (priceDisplay && spotSelect && spotSelect.value && startTimeInput && endTimeInput) {
        const startTime = new Date(startTimeInput.value);
        const endTime = new Date(endTimeInput.value);
        
        // Get selected option to find price per hour
        const selectedOption = spotSelect.options[spotSelect.selectedIndex];
        const pricePerHour = parseFloat(selectedOption.getAttribute('data-price') || '0');
        
        if (!isNaN(pricePerHour) && !isNaN(startTime) && !isNaN(endTime) && endTime > startTime) {
            // Calculate duration in hours
            const durationHours = (endTime - startTime) / (1000 * 60 * 60);
            
            // Calculate total price
            const totalPrice = (durationHours * pricePerHour).toFixed(2);
            
            // Update price display
            priceDisplay.innerHTML = `
                <div class="price-calculation">
                    <div class="price-row">
                        <span>Duration:</span>
                        <span>${formatDuration(durationHours)}</span>
                    </div>
                    <div class="price-row">
                        <span>Rate:</span>
                        <span>$${pricePerHour.toFixed(2)}/hour</span>
                    </div>
                    <div class="price-row total">
                        <span>Total:</span>
                        <span>$${totalPrice}</span>
                    </div>
                </div>
            `;
            
            // Add styles if not already in document
            if (!document.getElementById('price-calculation-styles')) {
                const style = document.createElement('style');
                style.id = 'price-calculation-styles';
                style.textContent = `
                    .price-calculation {
                        background-color: #f8fafc;
                        border-radius: var(--radius);
                        padding: 1rem;
                        margin-top: 1rem;
                    }
                    .price-row {
                        display: flex;
                        justify-content: space-between;
                        margin-bottom: 0.5rem;
                    }
                    .price-row.total {
                        margin-top: 0.5rem;
                        padding-top: 0.5rem;
                        border-top: 1px solid var(--border);
                        font-weight: 600;
                        font-size: 1.1rem;
                    }
                `;
                document.head.appendChild(style);
            }
        }
    }
}

/**
 * Format duration in hours to a readable string
 */
function formatDuration(hours) {
    const hoursInt = Math.floor(hours);
    const minutes = Math.round((hours - hoursInt) * 60);
    
    if (hoursInt > 0 && minutes > 0) {
        return `${hoursInt}h ${minutes}m`;
    } else if (hoursInt > 0) {
        return `${hoursInt} hour${hoursInt !== 1 ? 's' : ''}`;
    } else {
        return `${minutes} minute${minutes !== 1 ? 's' : ''}`;
    }
} 