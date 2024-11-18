from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .forms import UserRegistrationForm, UserLoginForm, QuizForm, QuestionForm, AnswerOptionForm, \
    QuestionWithOptionsForm

from django.db.models import Count

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import Quiz, UserProfile, Question, AnswerOption
from django.urls import reverse
from django.http import HttpResponseRedirect
from functools import wraps

#================================ACESSO================================
def staff_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            # Redireciona para uma página de acesso negado
            return HttpResponseRedirect(reverse('webquiz:restricted_access'))
    return _wrapped_view
def restricted_access_view(request):
    return render(request, 'restricted_access.html')
#================================ACESSO================================

#================================INICIO================================
def firstpage(request):
    if request.user.is_authenticated:
        return redirect('webquiz:home')

    return render(request, 'firstpage.html')
@login_required
def home(request):
    all_quizzes = Quiz.objects.filter(is_published=True)
    recent_quizzes = Quiz.objects.filter(is_published=True).order_by('-ccreated_at')[:6]
    return render(request, 'home.html', {
        'recent_quizzes': recent_quizzes,
        'all_quizzes': all_quizzes
    })
#================================INICIO================================

#================================AUTENTIFICAÇÃO================================
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            user = User.objects.create_user(
                username=email,  # Definimos o email como username para manter único
                email=email,
                password=password,
                first_name=first_name
            )
            messages.success(request, 'Conta criada com sucesso! Agora você pode fazer login.')
            return redirect('webquiz:login')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('webquiz:home')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            try:
                user = User.objects.filter(email=email).first()  # Retorna o primeiro usuário com aquele email
                if user:
                    user = authenticate(request, username=user.username, password=password)
                    if user is not None:
                        login(request, user)
                        messages.success(request, f'Bem-vindo, {user.username}!')
                        return redirect('webquiz:home')
                    else:
                        messages.error(request, 'Email ou senha incorretos.')
                else:
                    messages.error(request, 'Usuário com este email não foi encontrado.')
            except User.DoesNotExist:
                messages.error(request, 'Usuário com este email não foi encontrado.')
        else:
            messages.error(request, 'Email ou senha inválidos')

    else:
        form = UserLoginForm()

    return render(request, 'login.html', {'form': form})

# View para logout
@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso.')
    return redirect('webquiz:login')

@login_required
def profile(request):
    user_profile = request.user.userprofile
    current_experience = user_profile.score

    # Calcula o nível atual do usuário com base na experiência total
    current_level = calculate_user_level(current_experience)
    user_profile.level = current_level  # Atualiza o nível no perfil, se necessário

    # Mapa de experiência necessária para cada nível
    level_experience_map = {
        1: 0,
        2: 1100,
        3: 1900,
        4: 2900,
        5: 4200,
        6: 5800,
        7: 7800,
        8: 10300,
        9: 13300,
        10: 16300,
    }

    # Definir o próximo nível e a experiência necessária para alcançá-lo
    next_level = current_level + 1 if current_level < max(level_experience_map.keys()) else current_level
    next_level_experience = level_experience_map.get(next_level, level_experience_map[current_level])

    # Experiência acumulada necessária para o próximo e o nível atual
    previous_level_experience = level_experience_map.get(current_level - 1, 0)
    experience_needed = next_level_experience - previous_level_experience

    # Calcula o percentual de progresso em direção ao próximo nível
    if experience_needed > 0:
        progress_percentage = ((current_experience - previous_level_experience) / experience_needed) * 100
    else:
        progress_percentage = 100  # Já no nível máximo ou erro no mapeamento

    return render(request, 'profile.html', {
        'user_profile': user_profile,
        'progress_percentage': progress_percentage,
        'next_level': next_level,
        'next_level_experience': next_level_experience
    })

def calculate_user_level(experience):
    # Mapa de experiência necessária para cada nível
    level_experience_map = {
        1: 0,
        2: 1100,
        3: 1900,
        4: 2900,
        5: 4200,
        6: 5800,
        7: 7800,
        8: 10300,
        9: 13300,
        10: 16300,
    }

    # Itera pelos níveis para encontrar o nível atual com base na experiência
    for level, required_experience in level_experience_map.items():
        if experience < required_experience:
            return level - 1  # Retorna o nível anterior
    return max(level_experience_map.keys())  # Nível máximo se a experiência exceder todos os níveis
#================================AUTENTIFICAÇÃO================================

@login_required(login_url='webquiz:login')
@staff_required
def create_quiz(request):
    if request.method == "POST":
        quiz_form = QuizForm(request.POST)
        if quiz_form.is_valid():
            quiz_form.save()
            messages.success(request, 'Quiz criado com sucesso!')
            return redirect('webquiz:manage_quizzes')
    else:
        quiz_form = QuizForm()

    return render(request, 'manager_quiz/quiz_form.html', {
        'quiz_form': quiz_form,
        'quiz': None
    })

@login_required(login_url='webquiz:login')
@staff_required
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == 'POST':
        quiz_form = QuizForm(request.POST, instance=quiz)
        if quiz_form.is_valid():
            quiz_form.save()
            messages.success(request, 'Quiz atualizado com sucesso!')
            return redirect('webquiz:manage_quizzes')
    else:
        quiz_form = QuizForm(instance=quiz)

    return render(request, 'manager_quiz/quiz_form.html', {
        'quiz_form': quiz_form,
        'quiz': quiz
    })

@login_required(login_url='webquiz:login')
@staff_required
def quiz_details(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = Question.objects.filter(quiz=quiz)

    # Form para adicionar pergunta
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.quiz = quiz  # Relaciona a pergunta ao quiz
            question.save()
            return redirect('webquiz:quiz_details', quiz_id=quiz.id)  # Redireciona para a página de detalhes
    else:
        question_form = QuestionForm()

    return render(request, 'manager_quiz/quiz_details.html', {
        'quiz': quiz,
        'questions': questions,
        'question_form': question_form  # Adiciona o formulário de perguntas na mesma página
    })
@login_required(login_url='webquiz:login')
@staff_required
def edit_question(request, quiz_id, question_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    question = get_object_or_404(Question, id=question_id, quiz=quiz)
    answer_options = question.answer_options.all()

    # Verifica se o quiz está publicado
    if quiz.is_published:
        messages.error(request, 'Não é possível editar questões de um quiz publicado.')
        return redirect('webquiz:quiz_details', quiz_id=quiz.id)

    if request.method == 'POST':
        form = QuestionWithOptionsForm(request.POST)
        if form.is_valid():
            # Atualizar a pergunta
            question.question_text = form.cleaned_data['question']
            question.points = form.cleaned_data['points']
            question.save()

            # Atualizar as opções de resposta
            options_data = [
                (form.cleaned_data['option1'], form.cleaned_data['option1_correct']),
                (form.cleaned_data['option2'], form.cleaned_data['option2_correct']),
                (form.cleaned_data['option3'], form.cleaned_data['option3_correct']),
                (form.cleaned_data['option4'], form.cleaned_data['option4_correct']),
            ]

            # Atualizando ou criando as opções de resposta
            for i, (text, is_correct) in enumerate(options_data):
                if i < len(answer_options):
                    option = answer_options[i]
                    option.option_text = text
                    option.is_correct = is_correct
                    option.save()
                else:
                    if text:  # Adiciona uma nova resposta se estiver preenchida
                        AnswerOption.objects.create(
                            question=question,
                            option_text=text,
                            is_correct=is_correct
                        )

            return redirect('webquiz:quiz_details', quiz_id=quiz_id)
    else:
        # Pré-preencher o formulário com os dados existentes
        form_data = {
            'question': question.question_text,
            'points': question.points,
            'option1': answer_options[0].option_text if len(answer_options) > 0 else '',
            'option1_correct': answer_options[0].is_correct if len(answer_options) > 0 else False,
            'option2': answer_options[1].option_text if len(answer_options) > 1 else '',
            'option2_correct': answer_options[1].is_correct if len(answer_options) > 1 else False,
            'option3': answer_options[2].option_text if len(answer_options) > 2 else '',
            'option3_correct': answer_options[2].is_correct if len(answer_options) > 2 else False,
            'option4': answer_options[3].option_text if len(answer_options) > 3 else '',
            'option4_correct': answer_options[3].is_correct if len(answer_options) > 3 else False,
        }
        form = QuestionWithOptionsForm(initial=form_data)

    return render(request, 'manager_quiz/add_question.html', {'form': form, 'quiz': quiz, 'question': question})

@login_required(login_url='webquiz:login')
@staff_required
def delete_question(request, quiz_id, question_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    question = get_object_or_404(Question, pk=question_id)

    # Verifica se o quiz está publicado
    if quiz.is_published:
        messages.error(request, 'Não é possível excluir questões de um quiz publicado.')
        return redirect('webquiz:quiz_details', quiz_id=quiz.id)

    if request.method == 'POST':
        question.delete()
        messages.success(request, 'A pergunta foi excluída com sucesso.')
        return redirect('webquiz:quiz_details', quiz_id=quiz.id)

    return render(request, 'manager_quiz/delete_question_confirm.html', {'quiz': quiz, 'question': question})


@login_required(login_url='webquiz:login')
@staff_required
def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Mapeamento das opções de pontos para cada nível de dificuldade
    difficulty_points_map = {
        'facil': [(10, '10 XP'), (15, '15 XP'), (20, '20 XP')],
        'medio': [(20, '20 XP'), (30, '30 XP'), (40, '40 XP')],
        'dificil': [(40, '40 XP'), (50, '50 XP'), (60, '60 XP')],
        'avancado': [(60, '60 XP'), (80, '80 XP'), (100, '100 XP')],
        'expert': [(100, '100 XP'), (120, '120 XP'), (150, '150 XP')],
        'master': [(150, '150 XP'), (180, '180 XP'), (220, '220 XP')],
        'legend': [(220, '220 XP'), (270, '270 XP'), (320, '320 XP')],
    }

    points_choices = difficulty_points_map.get(quiz.difficulty, [])

    if request.method == 'POST':
        form = QuestionWithOptionsForm(request.POST, points_choices=points_choices)
        if form.is_valid():
            # Criação da pergunta com pontos selecionados
            question = Question.objects.create(
                quiz=quiz,
                question_text=form.cleaned_data['question'],
                points=int(form.cleaned_data['points_choice'])  # Define os pontos com base na escolha
            )

            # Criação das opções de resposta
            options_data = [
                (form.cleaned_data['option1'], '1'),
                (form.cleaned_data['option2'], '2'),
                (form.cleaned_data['option3'], '3'),
                (form.cleaned_data['option4'], '4'),
            ]

            for text, option_number in options_data:
                if text:
                    is_correct = form.cleaned_data['correct_answer'] == option_number
                    AnswerOption.objects.create(
                        question=question,
                        option_text=text,
                        is_correct=is_correct
                    )

            return redirect('webquiz:quiz_details', quiz_id=quiz_id)
    else:
        form = QuestionWithOptionsForm(points_choices=points_choices)

    return render(request, 'manager_quiz/add_question.html', {'form': form, 'quiz': quiz})


@login_required(login_url='webquiz:login')
@staff_required
def add_answer_options(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    if request.method == 'POST':
        form = AnswerOptionForm(request.POST)
        if form.is_valid():
            answer_option = form.save(commit=False)
            answer_option.question = question
            answer_option.save()
            return redirect('webquiz:add_answer_options', question_id=question.id)  # Permite adicionar mais opções

    else:
        form = AnswerOptionForm()

    return render(request, 'manager_quiz/add_answer_options.html', {'form': form, 'question': question})
@login_required(login_url='webquiz:login')
@staff_required
def manage_quizzes(request):
    quizzes = Quiz.objects.all().annotate(
        question_count=Count('question')
    )
    return render(request, 'manager_quiz/manage_quizzes.html', {'quizzes': quizzes})

@login_required(login_url='webquiz:login')
@staff_required
def delete_quiz(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    quiz.delete()
    return redirect('webquiz:manage_quizzes')

@login_required(login_url='webquiz:login')
@staff_required
def publish_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Conta o número de questões associadas ao quiz
    question_count = quiz.questions.count()

    # Verifica se tem o número mínimo de questões
    if question_count < 6:
        messages.error(
            request,
            f'Não é possível publicar o quiz. É necessário ter no mínimo 6 questões (atual: {question_count}).'
        )
        return redirect('webquiz:manage_quizzes')

    quiz.is_published = True
    quiz.save()
    messages.success(request, 'Quiz publicado com sucesso!')
    return redirect('webquiz:manage_quizzes')

@login_required(login_url='webquiz:login')
@staff_required
def manage_quizzes(request):
    quizzes = Quiz.objects.all().annotate(
        question_count=Count('questions')  # Mudado de 'question' para 'questions'
    )
    return render(request, 'manager_quiz/manage_quizzes.html', {'quizzes': quizzes})

@login_required(login_url='webquiz:login')
@staff_required
def unpublish_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    quiz.is_published = False
    quiz.save()
    messages.success(request, 'Quiz despublicado com sucesso!')
    return redirect('webquiz:manage_quizzes')

def quiz_start(request, quiz_id):
    # Obtenha o quiz e a primeira pergunta
    quiz = get_object_or_404(Quiz, id=quiz_id)
    first_question = quiz.questions.first()

    if not first_question:
        messages.error(request, "Este quiz não tem perguntas.")
        return redirect('webquiz:home')

    # Redireciona para a primeira pergunta
    return redirect('webquiz:quiz_question', quiz_id=quiz_id, question_id=first_question.id)

def quiz_question(request, quiz_id, question_id=None):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Identifica a primeira pergunta se question_id não for fornecido
    if question_id is None:
        first_question = quiz.questions.first()
        if first_question:
            return redirect('webquiz:quiz_question_with_id', quiz_id=quiz_id, question_id=first_question.id)
        else:
            return render(request, 'no_questions.html', {'quiz': quiz})

    # Pega a pergunta atual
    question = get_object_or_404(Question, id=question_id, quiz=quiz)

    if request.method == "POST":
        selected_option_id = request.POST.get("selected_option")
        if selected_option_id:
            # Salva a resposta na sessão
            selected_option = get_object_or_404(question.answer_options, id=selected_option_id)
            if 'quiz_answers' not in request.session:
                request.session['quiz_answers'] = {}
            request.session['quiz_answers'][str(question.id)] = selected_option.is_correct
            request.session.modified = True

            # Redireciona para a próxima pergunta se existir
            next_question = quiz.questions.filter(id__gt=question.id).first()
            if next_question:
                return redirect('webquiz:quiz_question_with_id', quiz_id=quiz_id, question_id=next_question.id)
            else:
                return redirect('webquiz:quiz_results', quiz_id=quiz.id)  # Redireciona para a tela de resultados

    return render(request, 'quiz/play_question.html', {'quiz': quiz, 'question': question})

from django.contrib.auth.decorators import login_required

@login_required
def quiz_results(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    answers = request.session.get('quiz_answers', {})

    total_questions = quiz.questions.count()
    correct_answers = 0
    total_score = 0
    question_results = []  # Para armazenar o status de cada questão

    # Processa cada pergunta e resposta
    for question in quiz.questions.all():
        user_answer = answers.get(str(question.id))
        is_correct = user_answer == True  # True indica acerto
        question_points = question.points if is_correct else 0  # Soma os pontos se correto

        # Acumula dados para exibição
        question_results.append({
            'question_text': question.question_text,
            'is_correct': is_correct,
            'points_awarded': question_points
        })

        # Contabiliza acertos e pontuação
        if is_correct:
            correct_answers += 1
            total_score += question_points

    # Atualiza a experiência do usuário com a pontuação total
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    user_profile.score += total_score
    user_profile.save()

    # Limpa as respostas da sessão após calcular o resultado
    if 'quiz_answers' in request.session:
        del request.session['quiz_answers']

    return render(request, 'quiz/quiz_results.html', {
        'quiz': quiz,
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'question_results': question_results,
        'total_score': total_score,
        'user_experience': user_profile.score
    })



def test(request):
    messages.success(request, 'Operação TESTE realizada com sucesso!')
    return render(request, 'test.html')