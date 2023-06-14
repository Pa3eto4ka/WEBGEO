from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.shortcuts import redirect
from django.views.generic import View
from django.utils import timezone
from django.db.models.fields import IntegerField
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView

QUESTION_TYPE_CHOICES = [('text', 'Текстовый'), ('single_choice', 'Указать позицию'),
                         ('multiple_choice', 'Выбрать правильный')]


class Object(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()


class Continent(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Country(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=2)
    continent = models.ForeignKey(Continent, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class City(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    quiz_count = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class CategoryCreateView(CreateView):
    model = Category
    fields = ['name', 'description']
    success_url = reverse_lazy('add_quiz')
    template_name = 'category.html'


class Question(models.Model):
    id = models.BigAutoField(primary_key=True)
    quiz = models.ForeignKey('Quiz', related_name='question', on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='category_questions')
    text = models.CharField(max_length=255)
    question_type = models.CharField(choices=QUESTION_TYPE_CHOICES, max_length=20)
    latitude = models.DecimalField(max_digits=20, decimal_places=13, default=0)
    longitude = models.DecimalField(max_digits=20, decimal_places=13, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    correct_answer_text = models.CharField(max_length=100, blank=True, null=True)
    max_score = models.IntegerField()  # Максимальное количество баллов за вопрос
    objects = models.Manager()

    def clean(self):
        super().clean()
        if not self.title:
            raise ValidationError('Title is required.')

    def __str__(self):
        return self.text


class Quiz(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category_quizzes')
    description = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_private = models.BooleanField(default=True)
    allowed_users = models.ManyToManyField(User, related_name='allowed_users', blank=True)
    time_limit = models.IntegerField(
        default=0, help_text='Quiz time limit in seconds. 0 = No limit')
    questions_per_attempt = models.IntegerField(
        default=0, help_text='Number of questions displayed for each quiz attempt. 0 = All questions')

    objects = models.Manager()
    random_order = models.BooleanField(default=False)
    questions = models.ManyToManyField(Question, related_name='quiz_questions')

    def __str__(self):
        return self.title

    def clean(self):
        if not self.title:
            raise ValidationError("Title is required.")

    def get_absolute_url(self):
        return reverse('quiz-detail', args=[str(self.id)])


class Answer(models.Model):
    id = models.BigAutoField(primary_key=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField()
    is_correct = models.BooleanField()
    objects = models.Manager()
    score = models.IntegerField()

    def __str__(self):
        return self.text


class QuizAttempt(models.Model):
    id = models.BigAutoField(primary_key=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='quiz_attempts')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_started = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(null=True)
    score = models.IntegerField(default=0)
    objects = models.Manager()

    def __str__(self):
        return str(self.id)

    def get_score(self):
        total_questions = self.quiz.questions.count()
        correct_answers = self.results.filter(is_correct=True).count()
        return int((correct_answers / total_questions) * 100)

    def save(self, *args, **kwargs):
        if not self.id and not kwargs.get('force_insert', False):
            self.date_started = timezone.now()
        if self.date_completed:
            self.score = self.get_score()
        super().save(*args, **kwargs)


class MapObject(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return self.title


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('text', 'correct_answer_text', 'question_type', 'category', 'quiz', 'latitude', 'longitude')


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)

    id = models.BigAutoField(primary_key=True)

    def __str__(self):
        return self.user.name


class GeoObject(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class GeoObjectGroup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    objects = models.ManyToManyField(GeoObject, related_name='groups')

    def __str__(self):
        return self.name


class UserAnswer(models.Model):
    id = models.BigAutoField(primary_key=True)
    quiz_attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    objects = models.Manager()


class QuizResult(models.Model):
    id = models.AutoField(primary_key=True)
    quiz_attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='results')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, verbose_name='Quiz')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="Question")
    answer = models.CharField(max_length=255, verbose_name="Answer", blank=True, null=True)
    is_correct = models.BooleanField(verbose_name="Is Correct", default=False)

    class Meta:
        verbose_name = 'User quiz result'
        verbose_name_plural = 'User quiz results'

    def __str__(self):
        return f"{self.user.name} - {self.question.text}"

    def save(self, *args, **kwargs):
        if not self.quiz_attempt:
            raise ValueError('QuizResult must have a quiz_attempt.')
        super().save(*args, **kwargs)


class QuizSubmitAnswerView(View):
    def post(self, request, quiz_attempt_id):
        quiz_attempt = QuizAttempt.objects.get(id=quiz_attempt_id)
        answer_id = request.POST.get("answer_id")
        if not answer_id:
            return redirect("quiz_next_question", quiz_attempt_id=quiz_attempt_id)

        answer = Answer.objects.get(id=answer_id)
        quiz_attempt.submit_answer(answer)
        if quiz_attempt.current_question_number == quiz_attempt.quiz.question_set.count():
            return redirect("quiz_result", quiz_attempt.quiz.id)

        return redirect("quiz_next_question", quiz_attempt_id=quiz_attempt_id)


class CompletedQuiz(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    completed_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quiz.title} - {self.user.name}"


class AttemptAnswer(models.Model):
    id = models.BigAutoField(primary_key=True)
    quiz_attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user_answer = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quiz_attempt.name} - {self.question.text}"
