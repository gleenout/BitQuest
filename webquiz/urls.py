from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'webquiz'
urlpatterns = [
    path('', views.firstpage, name='firstpage'),
    path('home/', views.home, name='home'),
    path('perfil/', views.profile, name='profile'),
    path('entrar/', views.user_login, name='login'),
    path('registro/', views.register, name='register'),
    path('sair/', views.user_logout, name='logout'),

    path('dm/criar_quiz/', views.create_quiz, name='create_quiz'),
    path('dm/editar_quiz/<int:quiz_id>/', views.edit_quiz, name='edit_quiz'),

    path('questao/<int:question_id>/opcoes/', views.add_answer_options, name='add_answer_options'),
    path('dm/painel/', views.manage_quizzes, name='manage_quizzes'),
    path('dm/deletar_quiz/<int:quiz_id>/', views.delete_quiz, name='delete_quiz'),
    path('dm/quiz/detalhes/<int:quiz_id>/', views.quiz_details, name='quiz_details'),
    path('dm/quiz/<int:quiz_id>/', views.quiz_details, name='quiz_details'),
    path('dm/quiz/<int:quiz_id>/adicionar_pergunta/', views.add_question, name='add_question'),
    path('dm/quiz/<int:quiz_id>/editar_pergunta/<int:question_id>/', views.edit_question, name='edit_question'),
    path('dm/quiz/<int:quiz_id>/publicar/', views.publish_quiz, name='publish_quiz'),
    path('dm/quiz/<int:quiz_id>/despublicar/', views.unpublish_quiz, name='unpublish_quiz'),
    path('quiz/<int:quiz_id>/excluir_pergunta/<int:question_id>/', views.delete_question, name='delete_question'),

    path('play/<int:quiz_id>/', views.quiz_start, name='start_quiz'),
    path('play/<int:quiz_id>/perguntas/', views.quiz_question, name='quiz_questions'),
    # Rota para uma pergunta específica
    path('play/<int:quiz_id>/perguntas/<int:question_id>/', views.quiz_question, name='quiz_question_with_id'),
    path('play/<int:quiz_id>/resultados/', views.quiz_results, name='quiz_results'),

    path('convidado/', views.guest_home, name='guest_home'),
    path('convidado/resultados/<int:quiz_id>/', views.guest_quiz_results, name='guest_quiz_results'),

    path('random-question/', views.get_random_question, name='random_question'),


    path('test/', views.test, name='tests'),
]
