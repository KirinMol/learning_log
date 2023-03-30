from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
# import pytz
# from django.utils import timezone

from .models import Topic, Entry
from .forms import TopicForm, EntryForm



def index(request):
    return render(request, 'learning_logs/index.html')

@login_required()
def topics(request):
    """Выводит список всех тем"""
    # timezone.activate(pytz.timezone("Europe/Moscow"))
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': topics}
    return render(request, 'learning_logs/topics.html', context)

def check_topic_owner(topic, request):
    """Проверяет, что пользователь, связанный с темой, является текущим пользователем"""
    if topic.owner != request.user:
        raise Http404

@login_required()
def topic(request, topic_id):
    """Выводит одну тему и все ее записи"""
    topic = Topic.objects.get(id=topic_id)
    # Проверка того, что тема принадлежит текущему пользователю
    check_topic_owner(topic, request)
    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'learning_logs/topic.html', context)

@login_required()
def new_topic(request):
    """Определяет новую тему"""
    if request.method != 'POST':
        # Данные не отправились; создается пустая форма
        form = TopicForm()
    else:
        # Отправлены данные POST; обратботать данные
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect('learning_logs:topics')
    # Вывести пустую или недействительную форму
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)

@login_required()
def new_entry(request, topic_id):
    """Добавляет новую запись по конкретной теме"""
    topic = Topic.objects.get(id=topic_id)
    check_topic_owner(topic, request)

    if request.method != 'POST':
        # Данные не отправились; создается пустая форма
        form = EntryForm()
    else:
        # Отправлены данные POST; обратботать данные
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect('learning_logs:topic', topic_id=topic_id)

    # Вывести недействительную или пустую форму
    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)

@login_required()
def edit_entry(request,entry_id):
    """Редактирует существующую запись"""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    check_topic_owner(topic, request)

    if request.method != 'POST':
        # Исходный запрос; форма заполняется данными текущей записи
        form = EntryForm(instance=entry)
    else:
        # Отправка данных POST; обработать данные
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topic', topic_id=topic.id)

    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context)

@login_required()
def delete_entry(request, entry_id):
    try:
        entry = Entry.objects.get(id=entry_id)
    except Entry.DoesNotExist:
        raise Http404("Запись не найдена")
    entry.delete()
    return redirect('learning_logs:topic', topic_id=entry.topic.id)

@login_required()
def delete_topic(request, topic_id):
    """Удаляет тему"""
    topic = Topic.objects.get(id=topic_id)
    # Проверка того, что тема принадлежит текущему пользователю
    check_topic_owner(topic, request)

    if request.method == 'POST':
        # Подтверждение удаления темы
        topic.delete()
        return redirect('learning_logs:topics')

    # Вывести страницу подтверждения удаления темы
    context = {'topic': topic}
    return render(request, 'learning_logs/delete_topic.html', context)

def edit_topic(request, topic_id):
    """Редактирует существующую тему."""
    topic = Topic.objects.get(id=topic_id)

    if request.method != 'POST':
        # Исходный запрос; форма заполняется данными текущей записи.
        form = TopicForm(instance=topic)
    else:
        # Отправка данных POST; обработать данные.
        form = TopicForm(instance=topic, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topic', topic_id=topic.id)

    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/edit_topic.html', context)
