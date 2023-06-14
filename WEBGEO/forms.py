from django import forms
from .models import Quiz, Question, Answer, MapObject, GeoObject, GeoObjectGroup, QuizResult, QuizAttempt
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
            'title', 'content', 'category', 'text', 'question_type', 'latitude', 'longitude', 'correct_answer_text',
            'quiz')


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


class TextForm(forms.Form):
    answer_text = forms.CharField(label='Ваш ответ', max_length=255, required=True)


class MarkOnMapForm(forms.Form):
    latitude = forms.DecimalField(label='Широта', max_digits=20, decimal_places=10, widget=forms.HiddenInput())
    longitude = forms.DecimalField(label='Долгота', max_digits=20, decimal_places=10, widget=forms.HiddenInput())


class ChooseOnMapForm(forms.Form):
    latitude = forms.DecimalField(label='Широта', max_digits=20, decimal_places=10, widget=forms.HiddenInput())
    longitude = forms.DecimalField(label='Долгота', max_digits=20, decimal_places=10, widget=forms.HiddenInput())


class QuizResultForm(forms.ModelForm):
    question = forms.ModelChoiceField(queryset=Question.objects.all(), widget=forms.HiddenInput())

    class Meta:
        model = QuizResult
        fields = ['question', 'answer']

    def __init__(self, quiz, user, *args, **kwargs):
        self.quiz = quiz
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields['question'].queryset = Question.objects.filter(quiz=quiz)

    def save(self, commit=True):
        question = self.cleaned_data['question']
        quiz_result, created = QuizResult.objects.get_or_create(
            quiz=self.quiz,
            user=self.user,
            question=question
        )
        quiz_result.answer = self.cleaned_data['answer']
        if commit:
            quiz_result.save()
        return quiz_result
