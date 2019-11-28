import json

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.views.generic import CreateView, DeleteView, UpdateView, ListView, View 
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.forms import formset_factory  
from django.http.response import HttpResponseRedirect
from django.http import HttpResponseServerError
from .models import Book, Redaction, Author, Rent, Friend, Publisher
from p_library.forms import AuthorForm, BookForm, FriendForm, RentForm, ContactForm

# Create your views here.

def books_list(request):
	books = Book.objects.all()
	return HttpResponse(books)

def index(request):
	template = loader.get_template('index.html')
	books = Book.objects.all()
	biblio_data = {
		"title": "мою библиотеку", 
		"books": books,
	}
	return HttpResponse(template.render(biblio_data, request))


def book_increment(request):
    if request.method == 'POST':
        book_id = request.POST['id']
        if not book_id:
            return redirect('/index/')
        else:
            book = Book.objects.filter(id=book_id).first()
            if not book:
                return redirect('/index/')
            book.copy_count += 1
            book.save()
        return redirect('/index/')
    else:
        return redirect('/index/')


def book_decrement(request):
    if request.method == 'POST':
        book_id = request.POST['id']
        if not book_id:
            return redirect('/index/')
        else:
            book = Book.objects.filter(id=book_id).first()
            if not book:
                return redirect('/index/')
            if book.copy_count < 1:
                book.copy_count = 0
            else:
                book.copy_count -= 1
            book.save()
        return redirect('/index/')
    else:
        return redirect('/index/')


def redaction(request):
    template = loader.get_template('redaction.html')
    # books = Book.objects.all()
    redact = Redaction.objects.all()
    data_ = {
        "redact": redact,
    }
    return HttpResponse(template.render(data_, request))

class AuthorEdit(CreateView):  
    model = Author  
    form_class = AuthorForm  
    success_url = reverse_lazy('p_library:author_list')  
    template_name = 'author_edit.html'  
  
  
class AuthorList(ListView):  
    model = Author  
    template_name = 'author_list.html'

def author_create_many(request):  
    AuthorFormSet = formset_factory(AuthorForm, extra=2)  #  Первым делом, получим класс, который будет создавать наши формы. Обратите внимание на параметр `extra`, в данном случае он равен двум, это значит, что на странице с несколькими формами изначально будет появляться 2 формы создания авторов.
    if request.method == 'POST':  #  Наш обработчик будет обрабатывать и GET и POST запросы. POST запрос будет содержать в себе уже заполненные данные формы
        author_formset = AuthorFormSet(request.POST, request.FILES, prefix='authors')  #  Здесь мы заполняем формы формсета теми данными, которые пришли в запросе. Обратите внимание на параметр `prefix`. Мы можем иметь на странице не только несколько форм, но и разных формсетов, этот параметр позволяет их отличать в запросе.
        if author_formset.is_valid():  #  Проверяем, валидны ли данные формы
            for author_form in author_formset:  
                author_form.save()  #  Сохраним каждую форму в формсете
            return HttpResponseRedirect(reverse_lazy('p_library:author_list'))  #  После чего, переадресуем браузер на список всех авторов.
    else:  #  Если обработчик получил GET запрос, значит в ответ нужно просто "нарисовать" формы.
        author_formset = AuthorFormSet(prefix='authors')  #  Инициализируем формсет и ниже передаём его в контекст шаблона.
    return render(request, 'manage_authors.html', {'author_formset': author_formset})

def books_author_create_many(request):
    AuthorFormSet = formset_factory(AuthorForm, extra=2)
    BookFormSet = formset_factory(BookForm, extra=2)

    if request.method == 'POST':
        author_formset = AuthorFormSet(request.POST, request.FILES, prefix='author')
        book_formset = BookFormSet(request.POST, request.FILES, prefix='books')
        if author_formset.is_valid() and book_formset.is_valid():
            for author_form in author_formset:
                author_form.save()
            for book_form in book_formset:
                book_form.save()
            return HttpResponseRedirect(reverse_lazy('p_library:author_list'))
    else:
        author_formset = AuthorFormSet(prefix='author')
        book_formset = BookFormSet(prefix='books')
    return render(request, 'manage_books_authors.html', {'author_formset': author_formset, 'book_formset': book_formset})

def rent(request):
    rents = Rent.objects.all()
    books = Book.objects.all()
    return render(request, 'rent.html', {'rents': rents, 'books': books})

def create_friend(request):
    if request.method != 'POST':
        new_friend = FriendForm()
    else:
        new_friend = FriendForm(data=request.POST)
        if new_friend.is_valid():
            new_friend.save()
            return HttpResponseRedirect(reverse('rent'))

    context = {'new_friend': new_friend}
    return render(request, 'create_friend.html', context)

def rent_edit(request):
    if request.method != 'POST':
        new_rent = RentForm()
    else:
        new_rent = RentForm(data=request.POST)
        rent_id = request.POST['book']
        book = Book.objects.get(id=rent_id)
        if new_rent.is_valid():
            new_rent = new_rent.save(commit=False)
            book.copy_count -= new_rent.count
            if book.copy_count < 0:
                return HttpResponseServerError('В библиотеке нет такого количества копий данной книги')   
            else:        
                new_rent.save()
                return HttpResponseRedirect(reverse('rent'))

    context = {'new_rent': new_rent}
    return render(request, 'rent_edit.html', context)

    
def rent_delete(request):
    if request.method == 'POST':
        rent_id = request.POST['id']
        if not rent_id:
            return redirect('/rent/')
        else:
            rent = Rent.objects.filter(id=rent_id).first()
            book = Book.objects.get(id=rent.book.id)
            if not rent:
                return redirect('/rent/')
            book.copy_count +=rent.count
            book.save()
            rent.delete()
        return redirect('/rent/')
    else:
        return redirect('/rent/')

class AuthorPageView(TemplateView):

    template_name = "authors.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["authors"] = Author.objects.all()
        return context

class PublisherList(ListView):
    model = Publisher
    # queryset = Publisher.objects.filter(country="Russia") # Позволяет задать фильтры для чтения данных из БД.
    template_name = 'publishers.html' # Название шаблона

    # context_object_name = "publishers" # Позволяет задать имя переменной, в которой хранится список объектов для отображения
    
    # paginate_by = 50 # Для создания постраничного вывода данных некоторой модели предусмотрен атрибут paginate_by. В нём указывается количество элементов списка, которое сервер будет выводить.
        
        # def get_queryset(self): # Метод get_queryset предназначен для выполнения тонкой фильтрации данных на каждый запрос. Например, мы можем использовать авторизационные данные пользователя для фильтрации и сортировки данных. Предположим, что при регистрации на нашем ресурсе пользователи указывают полный адрес своего проживания. Тогда мы можем ограничить список издательств только теми, которые находятся в одном городе с пользователем.
        # user_city = self.request.user.city
        # return Publisher.objects.filter(city=user_city)

# class PublisherList(View):
#     model = Publisher
    
#     def get(self):
#         publishers_list = self.model.objects.all()
#         return publishers_list
    
#     def put(self, request):
#         data = json.loads(request.body)
#         publisher = self.model(**data)
#         publisher.save()

# class PublisherDetailView(DetailView): #DetailView позволяет отобразить данные по одному объекту внутри базы данных

#     model = Publisher
#     pk_url_kwarg = 'id'
    

#     def get_context_data(self, **kwargs):
#         context = super(PublisherDetailView).get_context_data(**kwargs)
#         context["now"] = timezone.now()
#         return context

class ContactView(FormView):
    template_name = 'contact.html'
    form_class = ContactForm
    success_url = '/index/'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.send_email()
        return super(ContactView, self).form_valid(form)

# для тестов CreateView, UpdateView, DeleteView
class AuthorCreate(CreateView):
    model = Author
    fields = ['full_name', 'birth_year']
    template_name = 'test_author_create.html'

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['full_name']
    template_name = 'test_author_update.html'

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('p_library:authors')