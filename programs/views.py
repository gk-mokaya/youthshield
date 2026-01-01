from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Program, Service, Objective
from .forms import ProgramForm, ServiceForm, ObjectiveForm

def program_detail(request, program_id):
    """Display detailed information about a specific program"""
    program = get_object_or_404(Program, id=program_id, is_active=True)

    # Get related programs from the same category (excluding current program)
    related_programs = Program.objects.filter(
        category=program.category,
        is_active=True
    ).exclude(id=program.id)[:3]

    context = {
        'program': program,
        'related_programs': related_programs,
    }
    return render(request, 'programs/program_detail.html', context)

def program_modal(request, program_id):
    """Return program details for modal display"""
    program = get_object_or_404(Program, id=program_id, is_active=True)

    context = {
        'program': program,
    }
    return render(request, 'programs/program_modal.html', context)

def program_list(request):
    programs = Program.objects.filter(is_active=True)

    # Filter by category if provided
    category = request.GET.get('category')
    if category:
        programs = programs.filter(category=category)

    services = Service.objects.filter(is_active=True)
    objectives = Objective.objects.filter(is_active=True)

    context = {
        'programs': programs,
        'services': services,
        'objectives': objectives,
        'categories': Program.PROGRAM_CATEGORIES,
    }
    return render(request, 'programs/program_list.html', context)

@login_required
def add_program(request):
    if not request.user.is_staff_member():
        messages.error(request, 'Access denied. Staff members only.')
        return redirect('core:home')

    if request.method == 'POST':
        form = ProgramForm(request.POST, request.FILES)
        if form.is_valid():
            program = form.save()
            messages.success(request, f'Program "{program.title}" created successfully!')
            return redirect('programs:program_list')
    else:
        form = ProgramForm()

    context = {
        'form': form
    }
    return render(request, 'programs/add_program.html', context)

@login_required
def edit_program(request, program_id):
    if not request.user.is_staff_member():
        messages.error(request, 'Access denied. Staff members only.')
        return redirect('core:home')

    program = get_object_or_404(Program, id=program_id)

    if request.method == 'POST':
        form = ProgramForm(request.POST, request.FILES, instance=program)
        if form.is_valid():
            form.save()
            messages.success(request, f'Program "{program.title}" updated successfully!')
            return redirect('staff_dashboard:manage_programs')
    else:
        form = ProgramForm(instance=program)

    context = {
        'form': form,
        'program': program
    }
    return render(request, 'staff_dashboard/edit_program.html', context)

@login_required
def toggle_program(request, program_id):
    if not request.user.is_staff_member():
        messages.error(request, 'Access denied. Staff members only.')
        return redirect('core:home')

    program = get_object_or_404(Program, id=program_id)

    if request.method == 'POST':
        justification = request.POST.get('justification', '').strip()
        if not justification:
            messages.error(request, 'Justification is required for status changes.')
            return redirect('programs:toggle_program', program_id=program_id)

        program.is_active = not program.is_active
        program.save()

        action = "activated" if program.is_active else "deactivated"
        messages.success(request, f'Program "{program.title}" {action} successfully!')

        # Log the justification (you might want to store this in a separate model or log file)
        # For now, we'll just include it in the success message or log it
        print(f"Program {action}: {program.title} - Justification: {justification}")

        return redirect('staff_dashboard:manage_programs')
    else:
        context = {
            'program': program,
        }
        return render(request, 'staff_dashboard/toggle_program.html', context)

@login_required
def add_service(request):
    if not request.user.is_staff_member():
        messages.error(request, 'Access denied. Staff members only.')
        return redirect('core:home')

    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save()
            messages.success(request, f'Service "{service.title}" created successfully!')
            return redirect('programs:program_list')
    else:
        form = ServiceForm()

    context = {
        'form': form
    }
    return render(request, 'programs/add_service.html', context)

@login_required
def add_objective(request):
    if not request.user.is_staff_member():
        messages.error(request, 'Access denied. Staff members only.')
        return redirect('core:home')

    if request.method == 'POST':
        form = ObjectiveForm(request.POST)
        if form.is_valid():
            objective = form.save()
            messages.success(request, f'Objective "{objective.title}" created successfully!')
            return redirect('programs:program_list')
    else:
        form = ObjectiveForm()

    context = {
        'form': form
    }
    return render(request, 'programs/add_objective.html', context)
