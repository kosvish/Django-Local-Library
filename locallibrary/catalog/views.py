from django.shortcuts import render
from .models import Book, BookInstance, Author, Genre
from django.views import generic
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from .forms import RenewBookForm
from django.contrib.auth.decorators import permission_required
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin


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
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()
    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    return render(request, 'index.html', context={
        'num_books': num_books, 'num_instances': num_instances, 'num_instance_available': num_instances_available,
        'num_authors': num_authors, "num_visits": num_visits
    })


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_inst = get_object_or_404(BookInstance, pk=pk)
    # Если данный метод это POST запрос, тогда
    if request.method == "POST":
        # создаем экземпляр формы и заполняем данными из запроса (связывание)
        form = RenewBookForm(request.POST)
        # Проверка подлинности формы
        if form.is_valid():
            # обработка данных из form.cleaned_data
            # здесь просто присваем данные формы их полю due_back
            book_inst.due_back = form.cleaned_data["renewal_date"]
            book_inst.save()

            # Переход по новому адрессу
            return HttpResponseRedirect(reverse('index'))
    # Если это GET запрос, создать форму по умолчанию
    else:
        proposed_renewal_date = datetime.datetime.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={"renewal_date": proposed_renewal_date})
        return render(request, 'catalog/book_renew_librarian.html',
                      {"form": form, "bookinst": book_inst})


class BookListView(generic.ListView):
    model = Book

    # def get_queryset(self):
    #     return


class BookDetailView(generic.DetailView):
    model = Book


class AuthorDetailView(generic.DetailView):
    model = Author


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10


class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial = {"date_of_birt": "12/10/2020"}


class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name', "last_name", 'date_of_birth', "date_of_death"]


class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """
    Общий просмотр на основе классов со списком книг, которые можно одолжить текущему пользователю
    """
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


