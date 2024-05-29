from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('book/<int:pk>/', views.BookDetailView.as_view(), name="book-detail"),
    path('book/<int:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
    path('author/create/', views.AuthorCreate.as_view, name="author_create"),
    path('author/<int: pk/update/', views.AuthorUpdate.as_view, name='author_update'),
    path('author/<int: pk/delete/', views.AuthorDelete.as_view, name='author_delete')
]

