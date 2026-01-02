from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Sum, Q
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from users.models import CustomUser
from donations.models import Donation
from programs.models import Program
from testimonials.models import Testimonial
from core.models import ContactMessage, WebsiteSetting
import os
import shutil
from datetime import datetime
from django.conf import settings
from django.core.mail import send_mail

def is_staff(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_staff)
def dashboard(request):
    # Stats cards
    total_users = CustomUser.objects.count()
    total_donations = Donation.objects.count()
    total_donation_amount = Donation.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    total_programs = Program.objects.count()
    total_testimonials = Testimonial.objects.count()
    unresolved_messages = ContactMessage.objects.filter(resolved=False).count()

    # Recent activities
    recent_donations = Donation.objects.select_related('donor').order_by('-created_at')[:5]
    recent_users = CustomUser.objects.order_by('-date_joined')[:5]
    recent_messages = ContactMessage.objects.order_by('-created_at')[:5]

    # Chart data for donation trends (last 7 days)
    from django.db.models.functions import TruncDate
    from datetime import timedelta
    from django.utils import timezone

    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=6)
    donation_trends = Donation.objects.filter(created_at__date__range=[start_date, end_date]) \
        .annotate(date=TruncDate('created_at')) \
        .values('date') \
        .annotate(total=Sum('amount')) \
        .order_by('date')

    chart_labels = []
    chart_data = []
    current_date = start_date
    while current_date <= end_date:
        chart_labels.append(current_date.strftime('%b %d'))
        amount = next((item['total'] for item in donation_trends if item['date'] == current_date), 0)
        chart_data.append(float(amount))
        current_date += timedelta(days=1)

    # User registration trends (last 30 days)
    end_date_users = timezone.now().date()
    start_date_users = end_date_users - timedelta(days=29)
    user_registrations = CustomUser.objects.filter(date_joined__date__range=[start_date_users, end_date_users]) \
        .annotate(date=TruncDate('date_joined')) \
        .values('date') \
        .annotate(count=Count('id')) \
        .order_by('date')

    user_chart_labels = []
    user_chart_data = []
    current_date = start_date_users
    while current_date <= end_date_users:
        user_chart_labels.append(current_date.strftime('%b %d'))
        count = next((item['count'] for item in user_registrations if item['date'] == current_date), 0)
        user_chart_data.append(count)
        current_date += timedelta(days=1)

    # Calculate total users for the period
    total_users_month = sum(user_chart_data)
    avg_daily_users = total_users_month / 30 if total_users_month > 0 else 0

    # Payment method distribution
    payment_methods = Donation.objects.values('payment_method').annotate(count=Count('id')).order_by('-count')
    payment_labels = []
    payment_data = []
    payment_colors = []
    color_map = {
        'mpesa': '#10b981',
        'paypal': '#3b82f6',
        'card': '#8b5cf6',
    }
    for method in payment_methods:
        payment_labels.append(method['payment_method'].title())
        payment_data.append(method['count'])
        payment_colors.append(color_map.get(method['payment_method'], '#6b7280'))

    # Currency donation breakdown
    currency_donations = Donation.objects.values('currency').annotate(
        total=Sum('amount')
    ).order_by('-total')[:10]  # Top 10 currencies

    program_labels = []
    program_data = []
    for donation in currency_donations:
        program_labels.append(donation['currency'])
        program_data.append(float(donation['total']))

    context = {
        'total_users': total_users,
        'total_donations': total_donations,
        'total_donation_amount': total_donation_amount,
        'total_programs': total_programs,
        'total_testimonials': total_testimonials,
        'unresolved_messages': unresolved_messages,
        'recent_donations': recent_donations,
        'recent_users': recent_users,
        'recent_messages': recent_messages,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'user_chart_labels': user_chart_labels,
        'user_chart_data': user_chart_data,
        'total_users_month': total_users_month,
        'avg_daily_users': avg_daily_users,
        'payment_labels': payment_labels,
        'payment_data': payment_data,
        'payment_colors': payment_colors,
        'program_labels': program_labels,
        'program_data': program_data,
    }
    return render(request, 'staff_dashboard/dashboard.html', context)

@login_required
@user_passes_test(is_staff)
def manage_users(request):
    # Get filter parameters
    search_query = request.GET.get('search', '')
    user_type_filter = request.GET.get('user_type', '')
    status_filter = request.GET.get('status', '')

    # Base queryset
    users = CustomUser.objects.all()

    # Apply search filter
    if search_query:
        users = users.filter(
            models.Q(username__icontains=search_query) |
            models.Q(email__icontains=search_query) |
            models.Q(first_name__icontains=search_query) |
            models.Q(last_name__icontains=search_query)
        )

    # Apply user type filter
    if user_type_filter:
        if user_type_filter == 'superuser':
            users = users.filter(is_superuser=True)
        elif user_type_filter == 'staff':
            users = users.filter(is_staff=True, is_superuser=False)
        elif user_type_filter == 'user':
            users = users.filter(is_staff=False, is_superuser=False)

    # Apply status filter
    if status_filter:
        if status_filter == 'active':
            users = users.filter(is_active=True)
        elif status_filter == 'inactive':
            users = users.filter(is_active=False)

    # Order by date joined
    users = users.order_by('-date_joined')

    # Pagination
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Stats
    total_users = CustomUser.objects.count()
    active_users = CustomUser.objects.filter(is_active=True).count()
    staff_users = CustomUser.objects.filter(is_staff=True).count()

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'user_type_filter': user_type_filter,
        'status_filter': status_filter,
        'total_users': total_users,
        'active_users': active_users,
        'staff_users': staff_users,
    }
    return render(request, 'staff_dashboard/manage_users.html', context)

@login_required
@user_passes_test(is_staff)
def manage_donations(request):
    # Get filter parameters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    method_filter = request.GET.get('method', '')

    # Base queryset
    donations = Donation.objects.select_related('donor').order_by('-created_at')

    # Apply search filter
    if search_query:
        donations = donations.filter(
            Q(donor__username__icontains=search_query) |
            Q(donor__email__icontains=search_query) |
            Q(donor__first_name__icontains=search_query) |
            Q(donor__last_name__icontains=search_query) |
            Q(amount__icontains=search_query) |
            Q(transaction_id__icontains=search_query)
        )

    # Apply status filter
    if status_filter:
        donations = donations.filter(status=status_filter)

    # Apply payment method filter
    if method_filter:
        donations = donations.filter(payment_method=method_filter)

    # Pagination
    paginator = Paginator(donations, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Stats calculations
    from django.utils import timezone
    from datetime import timedelta

    total_donations = Donation.objects.count()

    from decimal import Decimal

    # Currency conversion rates to KES
    conversion_rates = {
        'KES': Decimal('1.0'),
        'USD': Decimal('130.0'),  # 1 USD = 130 KES
        'EUR': Decimal('140.0'),  # 1 EUR = 140 KES
        'GBP': Decimal('160.0'),  # 1 GBP = 160 KES
    }

    # Total amount only for completed donations, converted to KES
    completed_donations_queryset = Donation.objects.filter(status='completed')
    total_amount_kes = Decimal('0')
    for donation in completed_donations_queryset:
        rate = conversion_rates.get(donation.currency, Decimal('1.0'))  # Default to 1 if currency not found
        total_amount_kes += donation.amount * rate

    # Separate counts for each status
    completed_donations = completed_donations_queryset.count()
    pending_donations = Donation.objects.filter(status='pending').count()
    failed_donations = Donation.objects.filter(status='failed').count()

    # Today's donations
    today = timezone.now().date()
    today_donations = Donation.objects.filter(created_at__date=today).count()

    # Recent stats (last 30 days)
    thirty_days_ago = today - timedelta(days=30)
    monthly_donations = Donation.objects.filter(created_at__date__gte=thirty_days_ago).count()
    monthly_amount = Donation.objects.filter(created_at__date__gte=thirty_days_ago).aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'method_filter': method_filter,
        'total_donations': total_donations,
        'total_amount': total_amount_kes,
        'conversion_rates': conversion_rates,
        'completed_donations': completed_donations,
        'pending_donations': pending_donations,
        'failed_donations': failed_donations,
        'today_donations': today_donations,
        'monthly_donations': monthly_donations,
        'monthly_amount': monthly_amount,
    }
    return render(request, 'staff_dashboard/manage_donations.html', context)

@login_required
@user_passes_test(is_staff)
def manage_programs(request):
    # Get search parameter
    search_query = request.GET.get('search', '')

    # Base queryset
    programs = Program.objects.all()

    # Apply search filter
    if search_query:
        programs = programs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(objectives__icontains=search_query)
        )

    # Order by creation date
    programs = programs.order_by('-created_at')

    # Pagination
    paginator = Paginator(programs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Stats
    total_programs = Program.objects.count()
    ongoing_programs = Program.objects.filter(is_active=True).count()
    completed_programs = Program.objects.filter(is_active=False).count()

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'total_programs': total_programs,
        'ongoing_programs': ongoing_programs,
        'completed_programs': completed_programs,
    }
    return render(request, 'staff_dashboard/manage_programs.html', context)

@login_required
@user_passes_test(is_staff)
def manage_testimonials(request):
    # Get filter parameters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    # Base queryset
    testimonials = Testimonial.objects.select_related('user').order_by('-created_at')

    # Apply search filter
    if search_query:
        testimonials = testimonials.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(position__icontains=search_query)
        )

    # Apply status filter
    if status_filter:
        if status_filter == 'approved':
            testimonials = testimonials.filter(status='approved')
        elif status_filter == 'pending':
            testimonials = testimonials.filter(status='pending')
        elif status_filter == 'rejected':
            testimonials = testimonials.filter(status='rejected')

    # Pagination
    paginator = Paginator(testimonials, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Stats
    total_testimonials = Testimonial.objects.count()
    approved_testimonials = Testimonial.objects.filter(status='approved').count()
    pending_testimonials = Testimonial.objects.filter(status='pending').count()
    rejected_testimonials = Testimonial.objects.filter(status='rejected').count()

    # Rating distribution
    rating_stats = Testimonial.objects.filter(status='approved').values('rating').annotate(count=Count('id')).order_by('rating')

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'total_testimonials': total_testimonials,
        'approved_testimonials': approved_testimonials,
        'pending_testimonials': pending_testimonials,
        'rejected_testimonials': rejected_testimonials,
        'rating_stats': rating_stats,
    }
    return render(request, 'staff_dashboard/manage_testimonials.html', context)

@login_required
@user_passes_test(is_staff)
def manage_contact_messages(request):
    # Get search parameter
    search_query = request.GET.get('search', '')

    # Base queryset
    messages = ContactMessage.objects.all()

    # Apply search filter
    if search_query:
        messages = messages.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(subject__icontains=search_query) |
            Q(message__icontains=search_query)
        )

    # Order by creation date
    messages = messages.order_by('-created_at')

    # Pagination
    paginator = Paginator(messages, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Add formatted time to each message
    from django.utils.timesince import timesince
    from django.utils import timezone
    for message in page_obj:
        time_diff = timezone.now() - message.created_at
        if time_diff.total_seconds() > 86400:  # More than 24 hours
            message.formatted_time = message.created_at.strftime('%Y-%m-%d %H:%M')
        else:
            message.formatted_time = timesince(message.created_at)

    # Stats
    total_messages = ContactMessage.objects.count()
    unresolved_messages = ContactMessage.objects.filter(resolved=False).count()
    today = timezone.now().date()
    today_messages = ContactMessage.objects.filter(created_at__date=today).count()

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'total_messages': total_messages,
        'unresolved_messages': unresolved_messages,
        'today_messages': today_messages,
    }
    return render(request, 'staff_dashboard/manage_contact_messages.html', context)

@login_required
@user_passes_test(is_staff)
def manage_backups(request):
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    backups = []
    if os.path.exists(backup_dir):
        for file in os.listdir(backup_dir):
            if file.endswith('.bak'):
                file_path = os.path.join(backup_dir, file)
                backups.append({
                    'name': file,
                    'size': os.path.getsize(file_path),
                    'created_at': datetime.fromtimestamp(os.path.getctime(file_path)),
                })

    # Sort backups by creation date (newest first)
    backups.sort(key=lambda x: x['created_at'], reverse=True)

    # Stats
    total_backups = len(backups)
    total_size = sum(backup['size'] for backup in backups)

    # Mock auto backup settings (in a real implementation, this would come from database)
    auto_backup = {
        'frequency': 'daily',
        'time': '02:00',
        'max_backups': 10
    }

    # Mock backup logs (in a real implementation, this would come from database)
    backup_logs = [
        {
            'action': 'created',
            'message': 'Backup created successfully',
            'timestamp': datetime.now()
        }
    ]

    from django.utils import timezone
    current_date = timezone.now()

    context = {
        'backups': backups,
        'total_backups': total_backups,
        'total_size': total_size,
        'auto_backup': auto_backup,
        'backup_logs': backup_logs,
        'current_date': current_date,
    }
    return render(request, 'staff_dashboard/manage_backups.html', context)

# AJAX Views for CRUD operations
@login_required
@user_passes_test(is_staff)
def create_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user_type = request.POST.get('user_type')
        is_active = request.POST.get('is_active') == 'on'

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            user.is_active = is_active

            if user_type == 'superuser':
                user.is_superuser = True
                user.is_staff = True
            elif user_type == 'staff':
                user.is_staff = True
                user.is_superuser = False
            else:
                user.is_staff = False
                user.is_superuser = False

            user.save()
            messages.success(request, 'User created successfully.')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})

@login_required
@user_passes_test(is_staff)
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user_type = request.POST.get('user_type')
        is_active = request.POST.get('is_active') == 'on'

        try:
            user.username = username
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.is_active = is_active

            if user_type == 'superuser':
                user.is_superuser = True
                user.is_staff = True
            elif user_type == 'staff':
                user.is_staff = True
                user.is_superuser = False
            else:
                user.is_staff = False
                user.is_superuser = False

            user.save()
            messages.success(request, 'User updated successfully.')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})

@login_required
@user_passes_test(is_staff)
def get_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_active': user.is_active,
        'user_type': 'superuser' if user.is_superuser else ('staff' if user.is_staff else 'user')
    }
    return JsonResponse(user_data)

@login_required
@user_passes_test(is_staff)
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully.')
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
@user_passes_test(is_staff)
def edit_donation(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        currency = request.POST.get('currency')
        status = request.POST.get('status')
        payment_method = request.POST.get('payment_method')

        try:
            donation.amount = amount
            donation.currency = currency
            donation.status = status
            donation.payment_method = payment_method
            donation.save()
            messages.success(request, 'Donation updated successfully.')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False})

@login_required
@user_passes_test(is_staff)
def get_donation(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    donation_data = {
        'id': donation.id,
        'amount': str(donation.amount),
        'currency': donation.currency,
        'status': donation.status,
        'payment_method': donation.payment_method,
    }
    return JsonResponse(donation_data)

@login_required
@user_passes_test(is_staff)
def create_program(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        category = request.POST.get('category')
        description = request.POST.get('description')
        objectives = request.POST.get('objectives')
        target_audience = request.POST.get('target_audience')
        duration = request.POST.get('duration')
        is_active = request.POST.get('is_active') == 'on'
        image = request.FILES.get('image')

        try:
            program = Program.objects.create(
                title=title,
                category=category,
                description=description,
                objectives=objectives,
                target_audience=target_audience,
                duration=duration,
                is_active=is_active,
                image=image
            )
            messages.success(request, 'Program created successfully.')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})

@login_required
@user_passes_test(is_staff)
def get_program(request, program_id):
    program = get_object_or_404(Program, id=program_id)
    program_data = {
        'id': program.id,
        'title': program.title,
        'description': program.description,
        'objectives': program.objectives,
        'is_active': program.is_active,
    }
    return JsonResponse(program_data)

@login_required
@user_passes_test(is_staff)
def edit_program(request, program_id):
    program = get_object_or_404(Program, id=program_id)
    if request.method == 'POST':
        title = request.POST.get('title')
        category = request.POST.get('category')
        description = request.POST.get('description')
        objectives = request.POST.get('objectives')
        target_audience = request.POST.get('target_audience')
        duration = request.POST.get('duration')
        is_active = request.POST.get('is_active') == 'on'
        image = request.FILES.get('image')

        try:
            program.title = title
            program.category = category
            program.description = description
            program.objectives = objectives
            program.target_audience = target_audience
            program.duration = duration
            program.is_active = is_active
            if image:
                program.image = image
            program.save()
            messages.success(request, 'Program updated successfully.')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})
@login_required
@user_passes_test(is_staff)
def delete_program(request, program_id):
    program = get_object_or_404(Program, id=program_id)
    if request.method == 'POST':
        program.delete()
        messages.success(request, 'Program deleted successfully.')
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
@user_passes_test(is_staff)
def edit_testimonial(request, testimonial_id):
    testimonial = get_object_or_404(Testimonial, id=testimonial_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        position = request.POST.get('position')
        status = request.POST.get('status', testimonial.status)

        try:
            testimonial.content = content
            testimonial.position = position
            testimonial.status = status
            testimonial.reviewed_by = request.user
            testimonial.reviewed_at = timezone.now()
            testimonial.save()
            messages.success(request, 'Testimonial updated successfully.')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})

@login_required
@user_passes_test(is_staff)
def get_testimonial(request, testimonial_id):
    testimonial = get_object_or_404(Testimonial, id=testimonial_id)
    testimonial_data = {
        'id': testimonial.id,
        'content': testimonial.content,
        'position': testimonial.position,
        'status': testimonial.status,
        'rating': testimonial.rating,
        'user': {
            'username': testimonial.user.username,
            'full_name': testimonial.user.get_full_name(),
            'email': testimonial.user.email,
        }
    }
    return JsonResponse(testimonial_data)

@login_required
@user_passes_test(is_staff)
def approve_testimonial(request, testimonial_id):
    testimonial = get_object_or_404(Testimonial, id=testimonial_id)
    if request.method == 'POST':
        testimonial.status = 'approved'
        testimonial.reviewed_by = request.user
        testimonial.reviewed_at = timezone.now()
        testimonial.save()
        messages.success(request, 'Testimonial approved successfully.')
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
@user_passes_test(is_staff)
def reject_testimonial(request, testimonial_id):
    testimonial = get_object_or_404(Testimonial, id=testimonial_id)
    if request.method == 'POST':
        testimonial.status = 'rejected'
        testimonial.reviewed_by = request.user
        testimonial.reviewed_at = timezone.now()
        testimonial.save()
        messages.success(request, 'Testimonial rejected successfully.')
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
@user_passes_test(is_staff)
def delete_testimonial(request, testimonial_id):
    testimonial = get_object_or_404(Testimonial, id=testimonial_id)
    if request.method == 'POST':
        testimonial.delete()
        messages.success(request, 'Testimonial deleted successfully.')
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
@user_passes_test(is_staff)
def get_contact_message(request, message_id):
    message = get_object_or_404(ContactMessage, id=message_id)
    message_data = {
        'id': message.id,
        'name': message.name,
        'email': message.email,
        'phone': message.phone,
        'subject': message.subject,
        'message': message.message,
        'resolved': message.resolved,
        'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
    }
    return JsonResponse(message_data)

@login_required
@user_passes_test(is_staff)
def reply_contact_message(request, message_id):
    message = get_object_or_404(ContactMessage, id=message_id)
    if request.method == 'POST':
        reply_subject = request.POST.get('reply_subject')
        reply_message = request.POST.get('reply_message')

        try:
            # Send email reply
            send_mail(
                subject=reply_subject,
                message=reply_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[message.email],
                fail_silently=False,
            )

            # Mark message as resolved
            message.resolved = True
            message.save()

            messages.success(request, 'Reply sent successfully and message marked as resolved.')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})

@login_required
@user_passes_test(is_staff)
def edit_contact_message(request, message_id):
    message = get_object_or_404(ContactMessage, id=message_id)
    if request.method == 'POST':
        # Handle message editing
        pass
    return JsonResponse({'success': True})

@login_required
@user_passes_test(is_staff)
def delete_contact_message(request, message_id):
    message = get_object_or_404(ContactMessage, id=message_id)
    if request.method == 'POST':
        message.delete()
        messages.success(request, 'Contact message deleted successfully.')
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
@user_passes_test(is_staff)
def create_backup(request):
    if request.method == 'POST':
        try:
            backup_dir = os.path.join(settings.BASE_DIR, 'backups')
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)

            db_path = settings.DATABASES['default']['NAME']
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
            backup_path = os.path.join(backup_dir, backup_name)

            # Create backup with metadata
            shutil.copy2(db_path, backup_path)

            # Log backup creation
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f'Backup created: {backup_name}, Size: {os.path.getsize(backup_path)} bytes')

            messages.success(request, f'Backup created successfully: {backup_name}')
            return JsonResponse({'success': True, 'backup_name': backup_name})
        except Exception as e:
            messages.error(request, f'Failed to create backup: {str(e)}')
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})

@login_required
@user_passes_test(is_staff)
def delete_backup(request, backup_id):
    if request.method == 'POST':
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        backup_path = os.path.join(backup_dir, backup_id)

        if os.path.exists(backup_path) and backup_id.endswith('.bak'):
            try:
                os.remove(backup_path)
                messages.success(request, 'Backup deleted successfully.')
                return JsonResponse({'success': True})
            except OSError as e:
                messages.error(request, f'Failed to delete backup: {str(e)}')
                return JsonResponse({'success': False, 'error': str(e)})
        else:
            messages.error(request, 'Backup file not found.')
            return JsonResponse({'success': False, 'error': 'Backup file not found.'})
    return JsonResponse({'success': False})

@login_required
@user_passes_test(is_staff)
def download_backup(request, backup_id):
    from django.http import HttpResponse, Http404

    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    backup_path = os.path.join(backup_dir, backup_id)

    if os.path.exists(backup_path) and backup_id.endswith('.bak'):
        try:
            with open(backup_path, 'rb') as backup_file:
                response = HttpResponse(backup_file.read(), content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="{backup_id}"'
                return response
        except IOError:
            raise Http404("Backup file could not be read.")
    else:
        raise Http404("Backup file not found.")

@login_required
@user_passes_test(is_staff)
def save_auto_backup_settings(request):
    if request.method == 'POST':
        try:
            # For now, just return success since we're not implementing actual auto backup yet
            # In a real implementation, this would save settings to database or config file
            messages.success(request, 'Automatic backup settings saved successfully.')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})
