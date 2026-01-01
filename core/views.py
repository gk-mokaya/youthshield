from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import WebsiteSetting, CoreValue, BoardMember, ExecutiveCommittee
from programs.models import Program, Service, Objective
from testimonials.models import Testimonial
from django.shortcuts import redirect
from django.contrib import messages

def home(request):
    context = {
        'core_values': CoreValue.objects.filter(is_active=True),  # Add is_active filter
        'programs': Program.objects.filter(is_active=True)[:3],
        'services': Service.objects.filter(is_active=True),
        'objectives': Objective.objects.filter(is_active=True),
        'testimonials': Testimonial.objects.filter(status='approved')[:4],
    }
    return render(request, 'index.html', context)

def about(request):
    context = {
        'core_values': CoreValue.objects.filter(is_active=True).order_by('order'),
        'board_members': BoardMember.objects.filter(is_active=True),  # Add is_active filter
        'executive_committee': ExecutiveCommittee.objects.filter(is_active=True),  # Add is_active filter
    }
    return render(request, 'about.html', context)

def programs(request):
    # Filter by category if provided
    category = request.GET.get('category')
    if category:
        programs = Program.objects.filter(is_active=True, category=category)
    else:
        programs = Program.objects.filter(is_active=True)

    services = Service.objects.filter(is_active=True)
    objectives = Objective.objects.filter(is_active=True)

    context = {
        'programs': programs,
        'services': services,
        'objectives': objectives,
        'categories': Program.PROGRAM_CATEGORIES,
    }
    return render(request, 'programs/program_list.html', context)

def testimonials_page(request):
    from testimonials.models import Testimonial
    context = {
        'testimonials': Testimonial.objects.filter(status='approved'),
    }
    return render(request, 'testimonials.html', context)

def contact(request):
    if request.method == 'POST':
        from .models import ContactMessage
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if name and email and phone and subject and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message
            )
            messages.success(request, 'Your message has been sent successfully! We will get back to you soon.')
        else:
            messages.error(request, 'Please fill in all required fields.')

        return redirect('core:contact')

    return render(request, 'contact.html')

def newsletter_subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            # Here you would typically save to database or send to email service
            # For now, we'll just show a success message
            messages.success(request, 'Thank you for subscribing to our newsletter!')
        else:
            messages.error(request, 'Please enter a valid email address.')

    return redirect('core:home')

