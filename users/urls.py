from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    # Fluxo de Autenticação Customizado
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard e Perfil
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),

    # Recuperação de Senha (Apontando para a nova pasta password_recovery)
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='password_recovery/password_reset_form.html',
             email_template_name='password_recovery/password_reset_email.html',
             subject_template_name='password_recovery/password_reset_subject.txt',
             success_url=reverse_lazy('users:password_reset_done')
         ),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='password_recovery/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='password_recovery/password_reset_confirm.html',
             success_url=reverse_lazy('users:password_reset_complete')
         ),
         name='password_reset_confirm'),

    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='password_recovery/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]