from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Testimonial
from .forms import TestimonialForm

@login_required
def add_testimonial(request):
    # Get existing testimonial for update, or None for new
    existing_testimonial = Testimonial.objects.filter(user=request.user).first()

    if request.method == 'POST':
        form = TestimonialForm(request.POST, instance=existing_testimonial)
        if form.is_valid():
            testimonial = form.save(commit=False)
            testimonial.user = request.user
            testimonial.save()

            if existing_testimonial:
                messages.success(request, 'Your testimonial has been updated.')
            else:
                messages.success(request, 'Thank you for sharing your experience! Your testimonial is our testimony.')
            return redirect('users:profile')
    else:
        form = TestimonialForm(instance=existing_testimonial)

    context = {
        'form': form
    }
    return render(request, 'testimonials/add_testimonial.html', context)



@login_required
def edit_testimonial(request, testimonial_id):
    testimonial = get_object_or_404(Testimonial, id=testimonial_id, user=request.user)

    # Allow editing regardless of status
    if request.method == 'POST':
        form = TestimonialForm(request.POST, instance=testimonial)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your testimonial has been updated.')
            return redirect('users:profile')
    else:
        form = TestimonialForm(instance=testimonial)

    context = {
        'form': form,
        'testimonial': testimonial
    }
    return render(request, 'testimonials/edit_testimonial.html', context)

@login_required
def delete_testimonial(request, testimonial_id):
    testimonial = get_object_or_404(Testimonial, id=testimonial_id, user=request.user)
    
    # Only allow deletion if testimonial is pending
    if testimonial.status != 'pending':
        messages.error(request, 'You can only delete testimonials that are pending review.')
        return redirect('users:profile')
    
    if request.method == 'POST':
        testimonial.delete()
        messages.success(request, 'Your testimonial has been deleted.')
        return redirect('users:profile')
    
    context = {
        'testimonial': testimonial
    }
    return render(request, 'testimonials/delete_testimonial.html', context)