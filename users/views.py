from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .forms import CustomUserCreationForm, CustomUserChangeForm, CustomPasswordChangeForm
from .models import CustomUser
from testimonials.models import Testimonial
from donations.models import Donation

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'redirect_url': redirect('users:redirect_based_on_role').url})
            else:
                return redirect('users:redirect_based_on_role')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
            else:
                messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    # If user is already authenticated but doesn't have a tab token, treat as not logged in
    if request.user.is_authenticated:
        tab_token = request.session.get('tab_token')
        if not tab_token:
            # User is authenticated but missing tab token - treat as not logged in
            from django.contrib.auth import logout
            logout(request)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Generate unique tab token for this session
            import uuid
            tab_token = str(uuid.uuid4())
            request.session['tab_token'] = tab_token
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('users:redirect_based_on_role')
        # Inactive user handling
        elif CustomUser.objects.filter(username=username, is_active=False).exists():
            messages.error(request, 'Your account is inactive. Please contact support.')
            
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'users/login.html')

@login_required
def redirect_based_on_role(request):
    if request.user.is_staff_member():
        return redirect('staff_dashboard:dashboard')
    else:
        return redirect('core:home')

@login_required
def profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
    else:
        form = CustomUserChangeForm(instance=request.user)
    
    donations = Donation.objects.filter(donor=request.user)
    testimonial = Testimonial.objects.filter(user=request.user).first()
    
    context = {
        'form': form,
        'donations': donations,
        'testimonial': testimonial,
    }
    return render(request, 'users/profile.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Password changed successfully!'})
            else:
                return redirect('users:profile')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
            else:
                messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'users/change_password.html', {'form': form})

@csrf_exempt
@require_POST
def session_check(request):
    """
    Check if the user is authenticated and session is valid.
    Used for tab change security.
    """
    if request.user.is_authenticated:
        return JsonResponse({'authenticated': True})
    else:
        return JsonResponse({'authenticated': False, 'login_url': '/login/'})

@login_required
def user_logout(request):
    """
    Log out the user and redirect to login page.
    """
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('users:login')
