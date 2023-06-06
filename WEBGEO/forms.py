from django import forms
from .models import Quiz, Question, Answer, MapObject, GeoObject, GeoObjectGroup
from django.core.validators import MinValueValidator, MaxValueValidator


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description']


class QuestionForm(forms.ModelForm):
    latitude = forms.FloatField(
        widget=forms.HiddenInput(attrs={'id': 'id_latitude'}),
        validators=[MinValueValidator(-900000000), MaxValueValidator(900000000)],
        required=False
    )
    longitude = forms.FloatField(
        widget=forms.HiddenInput(attrs={'id': 'id_longitude'}),
        validators=[MinValueValidator(-1800000000), MaxValueValidator(1800000000)],
        required=False
    )

    class Meta:
        model = Question
        fields = (
        'title', 'content', 'category', 'text', 'question_type', 'latitude', 'longitude', 'correct_answer_text', 'quiz')


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'is_correct', 'question']


class MapObjectForm(forms.ModelForm):
    class Meta:
        model = MapObject
        fields = ['title', 'description', 'latitude', 'longitude']


class GeoObjectForm(forms.ModelForm):
    class Meta:
        model = GeoObject
        fields = ['name', 'latitude', 'longitude']


class GeoObjectGroupForm(forms.ModelForm):
    class Meta:
        model = GeoObjectGroup
        fields = ['name', 'description', 'objects']
