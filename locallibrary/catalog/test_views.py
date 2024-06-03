from django.test import TestCase
from .models import Author, Book, Genre, Language, BookInstance
from django.urls import reverse
import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission


class AuthorListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Создание 13 тестовых авторов
        number_of_authors = 13
        for author_num in range(number_of_authors):
            Author.objects.create(first_name=f"Christian {author_num}", last_name=f"Surname {author_num}")

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/catalog/authors/')
        self.assertEquals(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse("authors"))
        self.assertEquals(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'catalog/author_list.html')

    def test_pagination_is_ten(self):
        resp = self.client.get(reverse("authors"))
        self.assertEquals(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] is True)
        self.assertTrue(len(resp.context["author_list"]) == 10)


class LoanedBookInstancesByUserListViewTest(TestCase):

    def setUp(self):
        # Создание двух пользователей
        test_user1 = User.objects.create_user(username="testuser1", password='12345')
        test_user1.save()
        test_user2 = User.objects.create_user(username="testuser2", password="12345")
        test_user2.save()

        # Создание книги
        test_author = Author.objects.create(first_name="John", last_name="Smith")
        test_genre = Genre.objects.create(name="Fantasy")
        test_language = Language.objects.create(name="en")
        test_book = Book.objects.create(title="Book Title", summary="My book summary", isbn="ABCDEFG",
                                        author=test_author, language=test_language)
        genry_objects_for_book = Genre.objects.all()
        test_book.genre.set(genry_objects_for_book)
        test_book.save()

        # Создание 30 объектов BookInstance
        number_of_copies_book = 30
        for book_copy in range(number_of_copies_book):
            return_date = timezone.now() + datetime.timedelta(days=book_copy % 5)
            if book_copy % 2:
                the_borrower = test_user1
            else:
                the_borrower = test_user2

            status = "m"
            BookInstance.objects.create(book=test_book, imprint="Unlikely imprint 2016", due_back=return_date,
                                        borrower=the_borrower, status=status)

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse("my-borrowed"))
        self.assertRedirects(resp, '/accounts/login/?next=/catalog/mybooks/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username="testuser1", password='12345')
        resp = self.client.get(reverse('my-borrowed'))

        # Проверка что пользователь залогинился
        self.assertEqual(str(resp.context["user"]), 'testuser1')
        self.assertEqual(resp.status_code, 200)

        # Проверка на то что мы используем правильный шаблон
        self.assertTemplateUsed(resp, 'catalog/bookinstance_list_borrowed_user.html')

    def test_only_borrowed_books_in_list(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse("my-borrowed"))

        self.assertEqual(str(resp.context["user"]), 'testuser1')
        self.assertEqual(resp.status_code, 200)

        self.assertTrue("bookinstance_list" in resp.context)

        self.assertEqual(len(resp.context["bookinstance_list"]), 0)

        # Берем все книги на прокат
        get_ten_books = BookInstance.objects.all()[:10]

        for copy in get_ten_books:
            copy.status = "o"
            copy.save()

        resp = self.client.get(reverse("my-borrowed"))

        self.assertEqual(str(resp.context["user"]), 'testuser1')
        self.assertEqual(resp.status_code, 200)

        self.assertTrue("bookinstance_list" in resp.context)

        for book_item in resp.context["bookinstance_list"]:
            self.assertEqual(resp.context["user"], book_item.borrower)
            self.assertEqual(book_item.status, 'o')

    def test_pages_ordered_by_due_date(self):
        for copy in BookInstance.objects.all():
            copy.status = 'o'
            copy.save()

        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('my-borrowed'))

        self.assertEqual(str(resp.context["user"]), 'testuser1')

        self.assertEqual(resp.status_code, 200)

        self.assertEqual(len(resp.context["bookinstance_list"]), 10)

        last_date = 0

        for copy in resp.context["bookinstance_list"]:
            if last_date == 0:
                last_date = copy.due_back
            else:
                self.assertTrue(last_date <= copy.due_back)


class RenewBookInstancesViewTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()

        test_user2 = User.objects.create_user(username="testuser2", password='12345')

        permission = Permission.objects.get(name="Set book as returned.")

        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Создание книги
        test_author = Author.objects.create(first_name="John", last_name="Smith")
        test_genre = Genre.objects.create(name="Fantasy")
        test_language = Language.objects.create(name="en")
        test_book = Book.objects.create(title="Book Title", summary="My Book summary", isbn="ABCDEFG",
                                        author=test_author, language=test_language
                                        )
        # Создание жанра
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)
        test_book.save()

        # Создание объекта BookInstance для пользователя test_user1
        return_date = datetime.date.today() + datetime.timedelta(days=5)

        self.test_bookinstance1 = BookInstance.objects.create(book=test_book, imprint="Unlikely imprint, 2016",
                                                              due_back=return_date, borrower=test_user1, status="o"
                                                              )
        # Создание объекта BookInstance для пользователя test_user2

        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance2 = BookInstance.objects.create(book=test_book, imprint="Unlikely imprint, 2016",
                                                              due_back=return_date, borrower=test_user2, status="o"
                                                              )

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('renew-book-librarian', kwargs={
            'pk': self.test_bookinstance1.pk
        }))
        # Вручную проверить перенаправление (невозможно использовать AssertRedirect,
        # посколько URL-адресс перенаправления непредсказуем
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/accounts/login/"))

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username="testuser1", password='12345')
        resp = self.client.get(reverse("renew-book-librarian", kwargs={
            'pk': self.test_bookinstance1.pk
        }))

        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith('/accounts/login'))

    def test_logged_in_with_permission_borrowed_book(self):
        login = self.client.login(username="testuser2", password="12345")
        resp = self.client.get(reverse('renew-book-librarian', kwargs={
            'pk': self.test_bookinstance2.pk
        }))
        # Проверка позволяет ли нам войти в систему и это наша книга, и у нас есть необходимые разрешения
        self.assertEqual(resp.status_code, 200)

    def test_logged_in_with_permission_another_users_borrowed_book(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={
            'pk': self.test_bookinstance1.pk
        }))

        self.assertEqual(resp.status_code, 200)

    def test_HTTP404_for_invalid_book_logged_in(self):
        import uuid
        test_uid = uuid.uuid4()
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renew-librarian-book', kwargs={
            'pk': 1234
        }))
        self.assertEqual(resp.status_code, 404)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={
            'pk': 1
        }))

        self.assertEqual(resp.status_code, 302)


    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={
            'pk': self.test_bookinstance1.pk
        }))

        self.assertEqual(resp.status_code, 200)

        date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)

        self.assertEqual(resp.context['form'].initial['renewal_date'], date_3_weeks_in_future)

    def test_redirects_to_all_borrowed_book_list_on_success(self):
        login = self.client.login(username='testuser2', password='12345')
        valid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=4)

        resp = self.client.post(reverse('renew-book-librarian', kwargs={
            'pk': self.test_bookinstance1.pk
        }), {"renewal_date": valid_date_in_future})

        self.assertRedirects(resp, reverse('all-borrowed'))