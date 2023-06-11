from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect, Http404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from django.utils import timezone

from django.contrib.auth.models import User, Group
from .forms import QuestionForm, QuizForm, GeoObjectForm, GeoObjectGroupForm, ChooseOnMapForm, MarkOnMapForm, TextForm, \
    AnswerForm
from .models import QuizAttempt, Answer, Question, Quiz, GeoObject, GeoObjectGroup, QuizResult, UserAnswer, \
    CompletedQuiz, AttemptAnswer


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
def quiz_start(request, quiz_id, question_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    quiz_attempt, created = QuizAttempt.objects.get_or_create(user=request.user, quiz=quiz)
    question = get_object_or_404(Question, pk=question_id)


    if request.method == 'POST':
        form = None
        if question.question_type == 'choose_on_map':
            form = ChooseOnMapForm(request.POST)
        elif question.question_type == 'mark_on_map':
            form = MarkOnMapForm(request.POST)
        else:
            form = TextForm(request.POST)

        if form.is_valid():
            answer = form.save(commit=False)
            attempt_answer = AttemptAnswer.objects.create(question=question, answer=answer, quiz_attempt=quiz_attempt)
            messages.success(request, 'Ваш ответ на вопрос был сохранен.')
            next_question = Question.objects.filter(quiz=quiz, pk__gt=question_id).order_by('pk').first()
            if next_question:
                # если есть следующий вопрос, перенаправляем на страницу со следующим вопросом
                return redirect(reverse('quiz_start', args=[quiz_id, next_question.id]))
            else:
                # иначе, перенаправляем на страницу результатов
                return redirect(reverse('quiz_result', args=[quiz_id]))
        else:
            messages.error(request, 'Проверьте правильность заполнения формы.')

    form = None
    if question.question_type == 'choose_on_map':
        form = ChooseOnMapForm()
    elif question.question_type == 'mark_on_map':
        form = MarkOnMapForm()
    else:
        form = TextForm()

    return render(request, 'quiz_start.html', {
        'quiz': quiz,
        'question': question,
        'questions': questions,
        'form': form,
        'quiz_attempt': quiz_attempt,
        'quiz_attempt_id': quiz_attempt.id,
    })


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
            question.max_score = 10
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

@login_required
def quiz_question(request, quiz_attempt_id, current_question):
    # получаем текущий вопрос из базы данных
    question = Question.objects.get(quiz__attempt__id=quiz_attempt_id, number=current_question)

    # получаем список ответов на текущий вопрос
    answers = Answer.objects.filter(question=question)

    # рендерим шаблон и передаем в него данные
    return render(request, 'quiz_question.html', {'question': question, 'answers': answers})


@login_required
def quiz_result(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    quiz_results = QuizResult.objects.filter(user=request.user, quiz=quiz)
    if not quiz_results:
        raise Http404("No results found for the current user and quiz.")
    quizzes_results_count = quiz_results.count()
    correct_answers_count = sum(result.is_correct for result in quiz_results)
    return render(request, 'quiz_result.html', {
        'quiz': quiz,
        'correct_answers_count': correct_answers_count,
        'quizzes_results_count': quizzes_results_count,
        'quiz_results': quiz_results,
    })


@login_required
def check_answer(request):
    """
    Обработка ответа пользователя
    """
    if request.method == "POST":
        # Получение данных из POST-запроса
        data = json.loads(request.body)
        answer = data['answer']
        question_id = int(data['question_id'])
        quiz_id = int(data['quiz_id'])
        # Получение объекта вопроса по ID
        question = Question.objects.get(pk=question_id)
        # Получение объекта викторины по ID
        quiz = Quiz.objects.get(pk=quiz_id)
        # Проверка ответа и начисление баллов
        if question.question_type == 'c':
            correct_answer = (question.options.first().latitude, question.options.first().longitude)
            distance = calc_distance(answer, correct_answer)
            score = round(question.max_score - distance / 1000, 2)
            if score < 0:
                score = 0
        elif question.question_type == 't':
            correct_answer = question.options.first().text
            if answer.lower() == correct_answer.lower():
                score = question.max_score
            else:
                score = 0
        # Сохранение результатов ответа на вопрос
        user_answer = UserAnswer.objects.create(user=request.user, quiz=quiz, question=question,
                                                user_answer=answer, score=score)
        # Вычисление общего количества баллов по всем ответам пользователя
        total_score = get_user_score(request.user, quiz)
        # Отправка уведомления на почту в случае получения максимального количества баллов
        if total_score == user_answer.quiz.max_score:
            print("TRUE")
            # send_mail(
            #    'Вы набрали максимальный балл на викторине',
            #    f'Пользователь {request.user} получил максимальный балл {total_score} на викторине {quiz.title}.',
            #    'your_email@gmail.com',
            #    ['admin_email@gmail.com'],
            #    fail_silently=False,
            # )
        # Формирование и возврат JSON-ответа
        response_data = {'result': 'correct' if score > 0 else 'wrong', 'score': score, 'total_score': total_score}
        return JsonResponse(response_data)
    else:
        return JsonResponse({'result': 'error', 'message': 'Метод запроса должен быть POST.'})


@login_required
def quiz_submit_answer(request):
    if request.method == 'POST':
        question = Question.objects.get(id=request.POST['question_id'])
        quiz = question.quiz
        if question.question_type == 'ChooseOne':
            selected_choice = get_object_or_404(Answer, id=request.POST.get('answer_id'))
            if selected_choice.is_correct:
                score = 1
            else:
                score = 0
            result, created = QuizResult.objects.get_or_create(quiz=quiz, user=request.user)
            result.score += score
            result.save()
            return JsonResponse({'status': 'OK', 'score': score})
        elif question.question_type == 'EnterText':
            submitted_text = request.POST.get('answer_text', '').strip()
            if submitted_text.lower() == question.answer_set.first().text.lower():
                score = 1
            else:
                score = 0
            result, created = QuizResult.objects.get_or_create(quiz=quiz, user=request.user)
            result.score += score
            result.save()
            return JsonResponse({'status': 'OK', 'score': score})
    else:
        return JsonResponse({'status': 'ERROR', 'message': 'Invalid request method.'})
