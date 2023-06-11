from django.urls import include
from django.contrib import admin
from django.urls import path
from . import views

app_name = 'WEBGO'

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    #path('profile/', views.profile, name='profile'),
    path('accounts/', include('allauth.account.urls')),
    path('admin/', admin.site.urls),
    path('edit_user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('quiz_list/', views.quiz_list, name='quiz_list'),
    path('quiz_start/<int:quiz_id>/<int:question_id>/', views.quiz_start, name='quiz_start'),
    path('quiz_next_question/<int:quiz_attempt_id>/', views.quiz_next_question, name='quiz_next_question'),
    path('quiz_submit_answer/<int:quiz_attempt_id>/', views.quiz_submit_answer, name='quiz_submit_answer'),
    path('add_question/', views.add_question, name='add_question'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.signup, name='login'),
    path('logout/', views.signup, name='logout'),
    path('password_reset/', views.signup, name='password_reset'),
    path('password_reset_done/', views.signup, name='password_reset_done'),
    path('accounts/profile/', views.profile, name='profile'),
    path('accounts/', views.accounts, name='accounts'),
    path('password_change/', views.signup, name='password_change'),
    path('quiz/<int:quiz_id>/add_question/', views.add_question, name='add_question'),
    path('add_question/<int:quiz_id>/', views.add_question, name='add_question'),
    path('add_quiz/', views.add_quiz, name='add_quiz'),
    path('quiz_edit/<int:quiz_id>/', views.quiz_edit, name='quiz_edit'),
    path('quiz_detail/<int:quiz_id>/', views.quiz_edit, name='quiz_detail'),
    path('profile/', views.profile, name='profile'),
    path('quiz/<int:quiz_id>/edit/', views.quiz_edit, name='quiz_edit'),
    path('question/<int:question_id>/edit/', views.question_edit, name='question_edit'),
    path('question/<int:question_id>/delete/', views.question_delete, name='delete_question'),
    path('add_geo_objects', views.add_geo_objects, name='add_geo_objects'),
    path('quiz_result/<int:quiz_id>/', views.quiz_result, name='quiz_result'),
    path('quiz_submit_answer/', views.quiz_submit_answer, name='quiz_submit_answer'),
    path('quiz_submit_answer/<int:quiz_attempt_id>/', views.quiz_submit_answer, name='quiz_submit_answer'),
    #path('check_answer/', check_answer, name='check_answer'),
]
