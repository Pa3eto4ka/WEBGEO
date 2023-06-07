from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

from django.contrib.auth.models import User, Group
from .forms import QuestionForm, QuizForm, GeoObjectForm, GeoObjectGroupForm
from .models import QuizAttempt, Answer, Question, Quiz, GeoObject, GeoObjectGroup


# функция для проверки, является ли пользователь суперпользователем
@login_required
def is_superuser(request):
    if not request.user.is_superuser:
        messages.add_message(request, messages.ERROR, "Вы не являетесь суперпользователем")
        return HttpResponseRedirect('/')
    return None


@login_required
def edit_user(request, user_id):
    """
    Изменение роли пользователя
    """
    if not request.user.is_superuser:
        return redirect('home')

    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        # обработка POST-запроса на изменение роли пользователя
        role = int(request.POST.get('role'))
        user.groups.set([role])
        messages.success(request, "Роль пользователя успешно изменена")
        return redirect('home')

    # инициализация формы для изменения роли пользователя
    user_roles = user.groups.all()
    roles = Group.objects.all()
    context = {'user': user, 'user_roles': user_roles, 'all_roles': roles}
    return render(request, 'edit_user.html', context)


def index(request):
    context = {
        'quizzes': Quiz.objects.all(),
    }
    return render(request, 'home.html', context)


def home(request):
    return render(request, 'home.html')


@login_required
def profile(request):
    user = request.user
    quizzes_list = Quiz.objects.filter(user=user).order_by('id')

    paginator = Paginator(quizzes_list, 6)  # 6 - количество элементов на одной странице
    page = request.GET.get('page')

    try:
        quizzes = paginator.page(page)
    except PageNotAnInteger:
        quizzes = paginator.page(1)
    except EmptyPage:
        quizzes = paginator.page(paginator.num_pages)

    context = {
        'user': user,
        'quizzes': quizzes,
    }

    return render(request, 'accounts/profile.html', context)


def accounts(request):
    data = {'key': 'value'}
    return render(request, 'accounts.html', {'data': data})


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounts/profile')  # Вернуться на главную страницу после регистрации.
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def quiz_list(request):
    """
    Список тестов
    """
    quizzes = Quiz.objects.all()
    return render(request, 'quiz_list.html', {'quizzes': quizzes})


@login_required
def quiz_start(request, quiz_id):
    """
    Начало прохождения теста
    """
    quiz = get_object_or_404(Quiz, id=quiz_id)
    attempt = QuizAttempt.objects.create(quiz=quiz, user=request.user)
    return render(request, 'quiz_start.html', {'quiz': quiz, 'attempt': attempt})


@login_required
def quiz_take(request, quiz_id):
    """
    Прохождение теста
    """
    quiz = get_object_or_404(Quiz, pk=quiz_id)

    if request.method == 'POST':
        user_answers = {}
        for question in quiz.questions.all():
            answer_id = request.POST.get(str(question.id), None)
            if answer_id:
                user_answers[question.id] = int(answer_id)

        correct_answers = Answer.objects.filter(question__quiz=quiz, is_correct=True)

        total_questions = quiz.questions.count()
        correct_answers_count = sum(1 for question in quiz.questions.all()
                                    if user_answers.get(question.id) and Answer.objects.get(
            pk=user_answers[question.id]).is_correct)
        incorrect_answers_count = total_questions - correct_answers_count

        context = {
            'quiz': quiz,
            'total_questions': total_questions,
            'correct_answers_count': correct_answers_count,
            'incorrect_answers_count': incorrect_answers_count,
            'correct_answers': correct_answers,
            'user_answers': user_answers,
        }
        return render(request, 'quiz_result.html', context)

    context = {'quiz': quiz}
    return render(request, 'quiz_start.html', context)


@login_required
def quiz_next_question(request, quiz_attempt_id):
    """
    Получение следующего вопроса при прохождении теста
    """
    quiz_attempt = get_object_or_404(QuizAttempt, id=quiz_attempt_id)
    question = quiz_attempt.get_next_question()
    return JsonResponse({'question_text': question.text})


@login_required
def quiz_submit_answer(request, quiz_attempt_id):
    """
    Отправка ответа при прохождении теста
    """
    quiz_attempt = get_object_or_404(QuizAttempt, id=quiz_attempt_id)
    answer_text = request.POST.get('answer_text')
    question = quiz_attempt.get_current_question()
    answer = Answer.objects.create(question=question, text=answer_text, attempt=quiz_attempt)
    correct = answer.check_correctness()
    return JsonResponse({'correct': correct})


def add_quiz(request):
    """
    Добавление нового теста
    """
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.user = request.user
            quiz.save()
            return redirect('home')

    form = QuizForm()
    return render(request, 'add_quiz.html', {'form': form})


def questions(request, quiz_id):
    """
    Страница с вопросами теста
    """
    quiz = Quiz.objects.get(id=quiz_id)
    return render(request, 'quiz_start.html', {'quiz': quiz})


@login_required
def quiz_edit(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    quiz_questions = quiz.questions.all()

    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, 'Викторина успешно изменена')
            return redirect('profile')
    else:
        form = QuizForm(instance=quiz)

    context = {
        'quiz': quiz,
        'form': form,
        'quiz_questions': quiz_questions,
    }
    return render(request, 'quiz_edit.html', context)


@login_required
def question_edit(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Вопрос успешно изменен')
            return redirect('quiz_edit', quiz_id=question.quiz.id)
    else:
        form = QuestionForm(instance=question)

    context = {
        'form': form,
        'question': question,
    }
    return render(request, 'question_edit.html', context)


@login_required
def question_delete(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    quiz = question.quiz  # сохраняем ссылку на викторину перед удалением вопроса
    question.delete()
    messages.success(request, 'Вопрос успешно удален')
    return redirect('quiz_edit', quiz_id=quiz.id)  # используем сохраненную ссылку на викторину после удаления вопроса


def can_edit_quiz(user, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    return quiz.user == user


@login_required
def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.created_at = timezone.now()
            question.updated_at = timezone.now()
            question.save()
            return redirect('quiz_detail', quiz_id=quiz_id)
    else:
        form = QuestionForm()
    context = {'form': form, 'quiz': quiz, 'quiz_id': quiz_id}  # добавляем переменную quiz_id в контекст
    return render(request, 'add_question.html', context)


@login_required
def add_geo_objects(request):
    if request.method == 'POST':
        geo_object_form = GeoObjectForm(request.POST)
        geo_object_group_form = GeoObjectGroupForm(request.POST)

        if geo_object_form.is_valid():
            geo_object = geo_object_form.save(commit=False)
            # дополнительная обработка объекта, если нужно
            geo_object.save()
            return redirect('add_geo_objects')

        elif geo_object_group_form.is_valid():
            geo_object_group = geo_object_group_form.save(commit=False)
            geo_object_group.save()

            object_ids = request.POST.getlist('objects')
            for object_id in object_ids:
                geo_object = GeoObject.objects.get(id=object_id)
                geo_object_group.objects.objects.add(geo_object)

            # дополнительная обработка группы объектов, если нужно
            geo_object_group.save()
            return redirect('add_geo_objects')

    else:
        geo_object_form = GeoObjectForm()
        geo_object_group_form = GeoObjectGroupForm()

    geo_objects = GeoObject.objects.all()

    return render(request, 'add_geo_objects.html',
                  {'geo_object_form': geo_object_form,
                   'geo_object_group_form': geo_object_group_form,
                   'geo_objects': geo_objects})