from django.shortcuts import render
from .models import Book, BookInstance, Author, Language, Genre
from django.views import generic


def index(request):
    """
    Функция для отображения для домашней страницы сайта
    :param request:
    :return:
    """
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Доступные книги в статусе "a"
    available_genres = Genre.objects.all().count()
    # num_books_with_word =
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()

    return render(request, 'index.html', context={
        'num_books': num_books, 'num_instances': num_instances, 'num_instance_available': num_instances_available,
        'num_authors': num_authors
    })


class BookListView(generic.ListView):
    model = Book

    # def get_queryset(self):
    #     return


class BookDetailView(generic.DetailView):
    model = Book


