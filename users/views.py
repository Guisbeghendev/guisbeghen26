from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, ProfileForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Cadastro realizado com sucesso! Você foi vinculado ao grupo Free.")
            return redirect('users:dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('users:dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('users:login')

@login_required
def dashboard_view(request):
    return render(request, 'users/dashboard.html')

@login_required
def profile_view(request):
    return render(request, 'users/profile.html')

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Seu perfil foi atualizado com sucesso!")
            return redirect('users:profile')
    else:
        form = ProfileForm(instance=request.user.profile)
    return render(request, 'users/edit_profile.html', {'form': form})