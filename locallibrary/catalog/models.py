from django.db import models
from django.urls import reverse
import uuid
from django.contrib.auth.models import User
from datetime import date


class Genre(models.Model):
    """
    Модель представляющая жанр книги (Научная фантастика, Комедия, Триллер и т.д)
    """
    name = models.CharField(max_length=200, help_text="Введите жанр книги")

    def __str__(self):
        """
        Строка представляющая модель Таблицы в административной панеле
        :return: имя жанра
        """
        return self.name


class Language(models.Model):
    """
    Модель представляющая язык книги (Русский, Французский и т.д)
    """
    LANGUAGE_CHOICES = (
        ("ru", "Russian"),
        ("fr", "French"),
        ("de", "Germany"),
        ("en", "English"),
    )
    name = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)

    def get_absolute_url(self):
        """
        :return: Возращает url-адресс для доступа к определенному экземпляру языка
        """
        return reverse('language-detail', args=[str(self.id)])

    def __str__(self):
        """
        :return: Строка представляющая модель таблицы
        """
        return self.name


class Book(models.Model):
    """
    Модель представляющая книгу (но не конкретный экземпляр книги)
    """
    title = models.CharField(max_length=200)
    author = models.ForeignKey("Author", on_delete=models.SET_NULL, null=True)
    summary = models.TextField(max_length=1000, help_text="Введите краткое описание книги")
    isbn = models.CharField("ISBN", max_length=13,
                            help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN'
                                      'number</a>')
    genre = models.ManyToManyField(Genre, help_text="Выберите жанр книги")
    language = models.ForeignKey('Language', null=True,
                                 help_text="Введите язык желаемой книги", on_delete=models.SET_NULL)

    def __str__(self):
        """
        Строка представляющая модель таблицы
        :return: Заголовок книги
        """
        return self.title

    def display_genre(self):
        """
        Создает строку для Жанров. Это обязательно для отображения жанров в панеле Администраторов в Django
        :return: Строка жанров
        """
        return ', '.join([genre.name for genre in
                          self.genre.all()[:3]])

    display_genre.short_description = "Genre"

    def get_absolute_url(self):
        """
        :return: Возращает url-адресс для доступа к определенному экземпляру книги
        """
        return reverse("book-detail", args=[str(self.id)])


class BookInstance(models.Model):
    """
    Модель представляющая конкретный экземпляр книги (ту которую можно взять из библеотеки)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Уникальный индефикатор для этой конкретной книги во всей библеотеки")
    book = models.ForeignKey("Book", on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On Loan'),
        ('a', 'Available'),
        ('r', 'Reversed'),
    )
    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True, default='m',
                              help_text="Забронировать книгу")
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['due_back']
        permissions = (
            ('can_mark_returned', 'Set book as returned.'),
        )

    def __str__(self):
        """
        :return: Строка представляющая модель объекта
        """
        return '%s (%s)' % (self.id, self.book.title)

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False


class Author(models.Model):
    """
    Модель представляющая автора
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    def get_absolute_url(self):
        """
        :return: Возращает url-адресс для доступа к определенному экземпляру автора
        """

    def __str__(self):
        """
        :return: Строка представляющая модель объекта
        """
        return '%s, %s' % (self.last_name, self.first_name)
