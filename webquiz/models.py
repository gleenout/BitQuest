from django.db import models

class Quiz(models.Model):
    CATEGORY_CHOICES = [
        ('geral', 'Geral'),
        ('computational_literacy', 'Letramento Computacional'),
        ('digital_culture', 'Cultura Digital'),
        ('computational_thinking', 'Pensamento Computacional'),
        ('enade', 'ENADE'),
        ('algorithms', 'Algoritmos'),
        ('data_structures', 'Estruturas de Dados'),
        ('cybersecurity', 'Cibersegurança'),
    ]

    DIFFICULTY_CHOICES = [
        ('facil', 'Fácil'),
        ('medio', 'Médio'),
        ('dificil', 'Difícil'),
        ('avancado', 'Avançado'),
        ('expert', 'Especialista'),
        ('master', 'Mestre'),
        ('legend', 'Lendário'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)  # Permite null e blank
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='geral')
    difficulty = models.CharField(max_length=50, choices=DIFFICULTY_CHOICES, default='facil')
    ccreated_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    question_text = models.TextField(null=True, blank=True)  # Permite null e blank
    points = models.IntegerField(default=1)  # Define um valor padrão

    def __str__(self):
        return self.question_text

class AnswerOption(models.Model):
    question = models.ForeignKey(Question, related_name='answer_options', on_delete=models.CASCADE)
    option_text = models.CharField(max_length=255, null=True, blank=True)  # Permite null e blank
    is_correct = models.BooleanField(default=False)  # Define False como padrão

    def __str__(self):
        return self.option_text

from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    level = models.IntegerField(default=1)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s profile"