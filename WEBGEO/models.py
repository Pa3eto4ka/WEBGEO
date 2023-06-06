from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

QUESTION_TYPE_CHOICES = [('text', 'Текстовый'), ('single_choice', 'Указать позицию'),
                         ('multiple_choice', 'Выбрать правильный')]


class Object(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()


class Quiz(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    description = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_private = models.BooleanField(default=True)
    allowed_users = models.ManyToManyField(User, related_name='allowed_users', blank=True)

    objects = models.Manager()

    def __str__(self):
        return self.title

    def clean(self):
        if not self.title:
            raise ValidationError("Title is required.")


class Question(models.Model):
    id = models.BigAutoField(primary_key=True)
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    text = models.CharField(max_length=255)
    question_type = models.CharField(choices=QUESTION_TYPE_CHOICES, max_length=20)
    latitude = models.DecimalField(max_digits=20, decimal_places=13, default=0)
    longitude = models.DecimalField(max_digits=20, decimal_places=13, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    correct_answer_text = models.CharField(max_length=100, blank=True, null=True)
    objects = models.Manager()

    def clean(self):
        super().clean()
        if not self.title:
            raise ValidationError('Title is required.')

    def __str__(self):
        return self.text


class Answer(models.Model):
    id = models.BigAutoField(primary_key=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField()
    is_correct = models.BooleanField()
    objects = models.Manager()

    def __str__(self):
        return self.text


class QuizAttempt(models.Model):
    id = models.BigAutoField(primary_key=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_started = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(null=True)
    score = models.IntegerField(default=0)
    objects = models.Manager()

    def __str__(self):
        return str(self.id)


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
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    objects = models.Manager()