// Staff Dashboard JavaScript

$(document).ready(function() {
    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();
    
    // Initialize popovers
    $('[data-bs-toggle="popover"]').popover();
    
    // Handle modal forms
    $('.modal').on('shown.bs.modal', function() {
        $(this).find('input:first').focus();
    });
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        $('.alert').alert('close');
    }, 5000);
    
    // Confirm before destructive actions
    $('a[data-confirm], button[data-confirm]').click(function(e) {
        const message = $(this).data('confirm') || 'Are you sure?';
        if (!confirm(message)) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        }
    });
    
    // AJAX CSRF token setup
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    const csrftoken = getCookie('csrftoken');
    
    function csrfSafeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    
    // Toggle status functions
    window.toggleStatus = function(url, elementId) {
        const checkbox = $('#' + elementId);
        const isActive = checkbox.is(':checked');
        
        $.ajax({
            url: url,
            method: 'POST',
            data: JSON.stringify({ is_active: isActive }),
            contentType: 'application/json',
            success: function(response) {
                if (response.success) {
                    showToast('Status updated successfully', 'success');
                } else {
                    checkbox.prop('checked', !isActive);
                    showToast('Failed to update status: ' + response.message, 'error');
                }
            },
            error: function() {
                checkbox.prop('checked', !isActive);
                showToast('Failed to update status. Please try again.', 'error');
            }
        });
    };
    
    // Delete confirmation modal
    window.showDeleteModal = function(url, itemName, callback) {
        $('#deleteModalLabel').text(`Delete ${itemName}`);
        $('#deleteModalBody').text(`Are you sure you want to delete ${itemName}? This action cannot be undone.`);
        $('#deleteModalBtn').off('click').on('click', function() {
            $.ajax({
                url: url,
                method: 'POST',
                success: function(response) {
                    if (response.success) {
                        $('#deleteModal').modal('hide');
                        showToast(`${itemName} deleted successfully`, 'success');
                        if (typeof callback === 'function') {
                            callback();
                        } else {
                            location.reload();
                        }
                    } else {
                        showToast('Failed to delete: ' + response.message, 'error');
                    }
                },
                error: function() {
                    showToast('Failed to delete. Please try again.', 'error');
                }
            });
        });
        $('#deleteModal').modal('show');
    };
    
    // Toast notification function
    window.showToast = function(message, type = 'info') {
        const toastId = 'toast-' + Date.now();
        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center text-bg-${type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        $('.toast-container').append(toastHtml);
        const toast = new bootstrap.Toast(document.getElementById(toastId));
        toast.show();
        
        setTimeout(() => {
            $('#' + toastId).remove();
        }, 5000);
    };
    
    // File upload preview
    $('input[type="file"][data-preview]').change(function() {
        const input = $(this);
        const previewId = input.data('preview');
        const preview = $('#' + previewId);
        
        if (this.files && this.files[0]) {
            const reader = new FileReader();
            
            reader.onload = function(e) {
                preview.attr('src', e.target.result);
                preview.show();
            }
            
            reader.readAsDataURL(this.files[0]);
        }
    });
    
    // Dynamic modal loading
    $('a[data-modal-target]').click(function(e) {
        e.preventDefault();
        const target = $(this).data('modal-target');
        const url = $(this).attr('href');
        
        $(target).find('.modal-content').load(url, function() {
            $(target).modal('show');
        });
    });
    
    // Form validation
    $('form.needs-validation').on('submit', function(e) {
        if (!this.checkValidity()) {
            e.preventDefault();
            e.stopPropagation();
        }
        $(this).addClass('was-validated');
    });
    
    // Search functionality
    $('.dataTables_filter input').attr('placeholder', 'Search...');
    
    // Export buttons
    $('.export-btn').click(function(e) {
        e.preventDefault();
        const format = $(this).data('format');
        const url = $(this).attr('href') + '?format=' + format;
        window.location.href = url;
    });
});

// Global utility functions
window.formatDate = function(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
};

window.formatDateTime = function(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
};

window.formatCurrency = function(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
};

// Image upload handler
window.handleImageUpload = function(inputId, previewId) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);
    
    input.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const reader = new FileReader();
            
            reader.onload = function(e) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            };
            
            reader.readAsDataURL(this.files[0]);
        }
    });
};

// Bulk actions
window.selectAll = function(checkbox) {
    $('.row-checkbox').prop('checked', checkbox.checked);
};

window.performBulkAction = function(action) {
    const selectedIds = [];
    $('.row-checkbox:checked').each(function() {
        selectedIds.push($(this).val());
    });
    
    if (selectedIds.length === 0) {
        alert('Please select at least one item.');
        return;
    }
    
    if (confirm(`Are you sure you want to ${action} ${selectedIds.length} item(s)?`)) {
        // Implement bulk action here
        console.log(`Performing ${action} on:`, selectedIds);
    }
};

// Real-time updates (optional - for WebSocket integration)
window.setupRealTimeUpdates = function() {
    // This would connect to a WebSocket or use Server-Sent Events
    // For now, we'll use periodic AJAX polling as an example
    
    setInterval(function() {
        $.ajax({
            url: '/staff-dashboard/updates/',
            method: 'GET',
            success: function(data) {
                if (data.new_messages > 0) {
                    updateNotificationBadge('messages', data.new_messages);
                }
                if (data.new_donations > 0) {
                    updateNotificationBadge('donations', data.new_donations);
                }
            }
        });
    }, 30000); // Poll every 30 seconds
};

function updateNotificationBadge(type, count) {
    const badge = $(`.nav-link[href*="${type}"] .badge`);
    if (badge.length) {
        const currentCount = parseInt(badge.text()) || 0;
        badge.text(currentCount + count);
    } else {
        $(`.nav-link[href*="${type}"]`).append(
            `<span class="badge bg-danger rounded-pill float-end">${count}</span>`
        );
    }
}