from django.shortcuts import render, get_object_or_404, redirect
from .models import Question, Choice
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm
from django.contrib.auth import login, authenticate, logout
from .models import Vote

def index(request):
    questions = Question.objects.all().order_by('-pub_date')
    return render(request, 'polls/index.html', {'questions': questions})

@login_required
def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    # Если пользователь уже голосовал — отправляем его на результаты
    from .models import Vote
    if Vote.objects.filter(user=request.user, question=question).exists():
        return redirect('polls:results', question.id)

    return render(request, 'polls/detail.html', {'question': question})

@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])

        # Проверка: голосовал ли уже пользователь
        existing_vote = Vote.objects.filter(user=request.user, question=question).first()
        if existing_vote:
            return render(request, 'polls/detail.html', {
                'question': question,
                'error_message': 'Вы уже голосовали в этом опросе.',
            })

        selected_choice.votes += 1
        selected_choice.save()

        # Создаём запись в таблице Vote
        Vote.objects.create(user=request.user, choice=selected_choice, question=question)

        return redirect('polls:results', question.id)
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': 'Выберите вариант ответа.',
        })

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    choices = question.choice_set.all()
    total_votes = sum(choice.votes for choice in choices)

    return render(request, 'polls/results.html', {
        'question': question,
        'choices': choices,
        'total_votes': total_votes
    })


from django.shortcuts import render, redirect
from .models import Question, Choice
from .forms import QuestionForm, ChoiceForm

@login_required
def create_poll(request):
    if request.method == 'POST':
        # Создаём вопрос
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            question = question_form.save()

            # Создаём варианты для этого вопроса
            choices = request.POST.getlist('choices')  # Список вариантов, отправленных в форме
            for choice_text in choices:
                if choice_text.strip():
                    Choice.objects.create(question=question, choice_text=choice_text)

            return redirect('polls:index')  # Перенаправляем на главную страницу после создания опроса
    else:
        question_form = QuestionForm()
        choice_form = ChoiceForm()

    return render(request, 'polls/create_poll.html', {
        'question_form': question_form,
        'choice_form': choice_form
    })




def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('polls:index')
    else:
        form = RegisterForm()
    return render(request, 'polls/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('polls:index')
    else:
        form = AuthenticationForm()
    return render(request, 'polls/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('polls:index')