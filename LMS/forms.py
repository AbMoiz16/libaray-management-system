from django import forms
from .models import (
    Book,
    Student
)


class IssueBookForm(forms.Form):
    book = forms.ModelChoiceField(queryset=Book.objects.all(), empty_label="Book Name [ISBN]",
                                  to_field_name="id", label="Book (Name and ISBN)")
    # quantity = forms.ModelChoiceField(queryset=Book.objects.all(), empty_label="Book Name [ISBN]",
    #                                   to_field_name="quantity", label="Book (Name and ISBN)")
    student = forms.ModelChoiceField(queryset=Student.objects.all(), empty_label='Name [Roll no]',
                                     to_field_name='id', label='Student Details')

    book.widget.attrs.update({'class': 'form-control'})
    # quantity.widget.attrs.update({'class': 'form-control'})
    student.widget.attrs.update({'class': 'form-control'})
