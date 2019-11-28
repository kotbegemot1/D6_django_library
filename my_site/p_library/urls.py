from django.contrib import admin
from django.urls import path  
from .views import AuthorEdit, AuthorList, author_create_many, books_author_create_many, create_friend, rent_edit, AuthorPageView, PublisherList

app_name = 'p_library'  
urlpatterns = [
    path('author/create', AuthorEdit.as_view(), name='author_create'),
    path('authors', AuthorList.as_view(), name='author_list'),
    path('author/create_many', author_create_many, name='author_create_many'),
    path('author_book/create_many', books_author_create_many, name='author_book_create_many'),
    path('create/friend', create_friend, name='create_friend'),
    path('create/rent', rent_edit, name='rent_create'),
    path('authors_list_test', AuthorPageView.as_view(template_name = "authors.html"), name='authors_list_test'),
    path("publishers", PublisherList.as_view(template_name = 'publishers.html'), name='publishers'),
    # path("<str:name>/", PublisherDetailView.as_view(), name="publisher-detail"),
]
