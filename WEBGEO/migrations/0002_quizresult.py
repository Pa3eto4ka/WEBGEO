# Generated by Django 4.2.1 on 2023-06-08 01:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('WEBGEO', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuizResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.CharField(blank=True, max_length=255, null=True, verbose_name='Answer')),
                ('is_correct', models.BooleanField(default=False, verbose_name='Is Correct')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='WEBGEO.question', verbose_name='Question')),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='WEBGEO.quiz', verbose_name='Quiz')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'User quiz result',
                'verbose_name_plural': 'User quiz results',
            },
        ),
    ]
