from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Quiz, Question, AnswerOption
import re

# Formulário de Registro
class UserRegistrationForm(forms.ModelForm):
    #confirm_password = forms.CharField(
    #    widget=forms.PasswordInput(attrs={'placeholder': 'Confirme sua senha', 'class': 'form-control'}),
    #    label='Confirme a Senha'
    #)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Digite seu nome de usuário',
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Digite seu email',
                'class': 'form-control'
            }),
            'password': forms.PasswordInput(attrs={
                'placeholder': 'Digite sua senha',
                'class': 'form-control'
            }),
        }
        labels = {
            'username': 'Nome de Usuário',
            'email': 'Email',
            'password': 'Senha',
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Este nome de usuário já está em uso.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este email já está em uso.')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError("A senha deve ter pelo menos 8 caracteres.")
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("A senha deve conter pelo menos uma letra maiúscula.")
        if not re.search(r'[0-9]', password):
            raise forms.ValidationError("A senha deve conter pelo menos um número.")
        return password

    #def clean(self):
    #    cleaned_data = super().clean()
    #    password = cleaned_data.get('password')
    #    confirm_password = cleaned_data.get('confirm_password')
    #    if password and confirm_password and password != confirm_password:
    #        raise forms.ValidationError('As senhas não coincidem.')
    #    return cleaned_data

class UserLoginForm(forms.Form):
    username = forms.CharField(
        label="Nome de Usuário",
        widget=forms.TextInput(attrs={'placeholder': 'Digite seu nome de usuário', 'class': 'form-control'})
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={'placeholder': 'Digite sua senha', 'class': 'form-control'})
    )

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'category', 'difficulty']
        labels = {
            'title': 'Título',
            'description': 'Descrição',
            'category': 'Categoria',
            'difficulty': 'Dificuldade',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o título do quiz',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Digite a descrição do quiz',
                'rows': 4,
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'difficulty': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise forms.ValidationError("O título deve ter pelo menos 5 caracteres.")
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description) < 10:
            raise forms.ValidationError("A descrição deve ter pelo menos 10 caracteres.")
        return description

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona classes de erro do Bootstrap para validação frontend
        for field in self.fields:
            self.fields[field].error_messages = {
                'required': f'O campo {self.fields[field].label} é obrigatório.',
                'invalid': f'Por favor, insira um valor válido para {self.fields[field].label}.'
            }

class AnswerOptionForm(forms.ModelForm):
    class Meta:
        model = AnswerOption
        fields = ['option_text', 'is_correct']
        widgets = {
            'option_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite a opção de resposta'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'points']
        labels = {
            'question_text': 'Texto da Pergunta',
            'points': 'Pontos',
        }
        widgets = {
            'question_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite a pergunta'}),
            'points': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class QuestionWithOptionsForm(forms.Form):
    question = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label="Texto da Pergunta")

    # Campo de seleção de pontos para as três opções fornecidas para cada nível de dificuldade
    points_choice = forms.ChoiceField(
        choices=[],  # Opções serão passadas dinamicamente pela view
        widget=forms.RadioSelect,
        label="Escolha a Pontuação para esta Pergunta"
    )

    option1 = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False, label="Opção 1")
    option2 = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False, label="Opção 2")
    option3 = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False, label="Opção 3")
    option4 = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False, label="Opção 4")

    correct_answer = forms.ChoiceField(
        choices=[('1', 'Opção 1 é a correta'), ('2', 'Opção 2 é a correta'), ('3', 'Opção 3 é a correta'), ('4', 'Opção 4 é a correta')],
        widget=forms.RadioSelect,
        label="Selecione a Resposta Correta"
    )

    def __init__(self, *args, **kwargs):
        # Receber as opções de pontuação dinâmicas
        points_choices = kwargs.pop('points_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['points_choice'].choices = points_choices  # Define as opções de pontuação
