from django import forms  
from p_library.models import Author, Book, Friend, Rent
from django.forms import formset_factory
from p_library.validators import validate_zero
  
class AuthorForm(forms.ModelForm):  

    full_name = forms.CharField(widget=forms.TextInput)
    
    class Meta:  
        model = Author  
        fields = '__all__'

class BookForm(forms.ModelForm):
    copy_count = forms.IntegerField(validators=[validate_zero])
    class Meta:
        model = Book
        fields = "__all__"

class FriendForm(forms.ModelForm):
    class Meta:
        model = Friend
        fields = "__all__"

class RentForm(forms.ModelForm):
    class Meta:
        model = Rent
        fields = "__all__"

class ContactForm(forms.Form):
    name = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)

    def send_email(self):
        # send email using the self.cleaned_data dictionary
        pass

