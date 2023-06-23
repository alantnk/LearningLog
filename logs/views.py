from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import Entry, Topic
from .forms import EntryForm, TopicForm


def index(request):
    """A página inicial de Learning Log"""
    return render(request, "logs/index.html")


@login_required
def topics(request):
    """Mostra todos os assuntos."""
    topics = Topic.objects.filter(owner=request.user).order_by("date_added")
    context = {"topics": topics}
    return render(request, "logs/topics.html", context)


@login_required
def topic(request, pk):
    """Mostra um único assunto e todas as suas entradas."""
    topic = get_object_or_404(Topic, id=pk)
    if topic.owner != request.user:
        raise Http404
    entries = topic.entry_set.order_by("-date_added")
    context = {"topic": topic, "entries": entries}
    return render(request, "logs/topic.html", context)


@login_required
def new_topic(request):
    """Adiciona um novo assunto."""

    if request.method != "POST":
        # Nenhum dado submetido; cria um formulário em branco

        form = TopicForm()
    else:
        # Dados de POST submetidos; processa os dados

        form = TopicForm(request.POST)

        if form.is_valid():

            new_topic = form.save(commit=False)

            new_topic.owner = request.user

            new_topic.save()

            return HttpResponseRedirect(reverse("logs:topics"))

    context = {"form": form}
    return render(request, "logs/new_topic.html", context)


@login_required
def new_entry(request, pk):
    """Acrescenta uma nova entrada para um assunto em particular."""

    topic = Topic.objects.get(id=pk)

    if request.method != "POST":
        # Nenhum dado submetido; cria um formulário em brancow

        form = EntryForm()
    else:
        # Dados de POST submetidos; processa os dados
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return HttpResponseRedirect(reverse("logs:topic", args=[pk]))
    context = {"topic": topic, "form": form}
    return render(request, "logs/new_entry.html", context)


@login_required
def edit_entry(request, pk):
    """Edita uma entrada existente."""

    entry = Entry.objects.get(id=pk)
    topic = entry.topic
    if topic.owner != request.user:
        raise Http404
    if request.method != "POST":
        # Requisição inicial; preenche previamente o formulário

        form = EntryForm(instance=entry)
    else:
        # Dados de POST submetidos; processa os dados

        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():

            form.save()

            return HttpResponseRedirect(reverse("logs:topic", args=[topic.id]))
    context = {"entry": entry, "topic": topic, "form": form}
    return render(request, "logs/edit_entry.html", context)
