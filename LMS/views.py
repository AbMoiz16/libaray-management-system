import datetime
import functools
from django.shortcuts import render, redirect, HttpResponse
from .models import *
from .forms import IssueBookForm
from django.contrib.auth import authenticate, login, logout
from . import forms, models
from datetime import date
from django.contrib.auth.decorators import login_required
from django.utils import timezone


# Create your views here.
def index(request):
    return render(request, 'index.html')


@login_required(login_url='/admin_login')
def add_book(request):
    if request.method == 'POST':
        name = request.POST['name']
        auther = request.POST['author']
        isbn = request.POST['isbn']
        category = request.POST['category']
        quantity = request.POST['quantity']

        books = Book.objects.create(name=name, auther=auther, isbn=isbn, category=category, quantity=quantity)
        books.save()
        alert = True
        return render(request, 'add_book.html', {'alert': alert})
    return render(request, 'add_book.html')


@login_required(login_url='/admin_login')
def view_books(request):
    books = Book.objects.all()
    return render(request, 'view_books.html', {'books': books})


@login_required(login_url='/admin_login')
def view_students(request):
    students = Student.objects.all()
    return render(request, 'view_students.html', {'students': students})


@login_required(login_url='/admin_login')
def issue_book(request):
    form = forms.IssueBookForm()
    if request.method == 'POST':
        form = forms.IssueBookForm(request.POST)
        # print("request.POST====>", request.POST)
        if form.is_valid():
            # print("form====>", form.cleaned_data)
            book = form.cleaned_data.get('book')
            student = form.cleaned_data.get('student')
            is_exist = Book.objects.filter(id=request.POST.get('book')).first()
            # print(is_exist.quantity, "...............")
            if is_exist.quantity > 0:
                issue_date = timezone.now()
                issue_book_obj = IssueBook(book=book, student=student, issue_date=issue_date, is_issued=True)
                issue_book_obj.save()
                Book.objects.filter(id=request.POST.get('book')).update(quantity=is_exist.quantity - 1)
            else:
                return HttpResponse('Book is not available at the moment')
            alert = True
            return render(request, 'issue_book.html', {'alert': alert})
    return render(request, 'issue_book.html', {'form': form})


@login_required(login_url='/student_login')
def student_request_book(request, my_id):
    try:
        book = Book.objects.get(id=my_id)
        student = Student.objects.get(user__username=request.user)
        # print("student---->>", student.id)
    except:
        return HttpResponse(f'Book with id {my_id} does not exists')
    else:
        try:
            issued_book = IssueBook.objects.get(book__id=my_id, student=student.id)
        except:
            request_created = IssueBook.objects.create(book=book, student=student)
            return HttpResponse('Your request to issue a book has been received')
        else:
            return HttpResponse('Your request is already in queue')


@login_required(login_url='/admin_login')
def approve_book_request(request):
    approve_book = IssueBook.objects.filter(is_issued=0)
    # print("approve_book---->", approve_book)
    return render(request, 'approve_book_request.html', {'approve_book': approve_book})


@login_required(login_url='/admin_login')
def issued_book_request(request, my_id):
    approved_book = IssueBook.objects.filter(id=my_id).update(issue_date=timezone.now(), is_issued=True)
    book_name = IssueBook.objects.filter(id=my_id).values_list('book__name').first()
    # print("is_available------>", book_name)
    book_quantity = IssueBook.objects.filter(id=my_id).values_list('book__quantity').first()
    # print("is_available------>", book_quantity)
    convert_tuple_into_int = functools.reduce(lambda sub, ele: sub * 10 + ele, book_quantity)
    # print(res, '------->>>>>')
    convert_tuple_into_int = convert_tuple_into_int - 1
    # print(res, '------->>>>>')
    convert_tuple_into_str = convertTuple(book_name)
    # print(book, '------->>>>>')
    Book.objects.filter(name=convert_tuple_into_str).update(quantity=convert_tuple_into_int)

    return redirect('/view_issued_book')


@login_required(login_url='/admin_login')
def view_issued_book(request):
    current_time = timezone.now()
    issued_books = IssueBook.objects.filter(is_issued=1)
    details = []

    for issued_book_obj in issued_books:
        expiry_date = issued_book_obj.issue_date + timedelta(days=10)
        book_details = {
            'id': issued_book_obj.id,
            'student_id': issued_book_obj.student.user,
            'student': issued_book_obj.student.id,
            'name': issued_book_obj.book.name,
            'auther': issued_book_obj.book.auther,
            'issue_date': issued_book_obj.issue_date,
            'expiry_date': expiry_date
        }
        # print("book_details====>", book_details)
        if current_time > expiry_date:
            differance_in_days = (current_time - expiry_date).days
            book_details['fine'] = differance_in_days * 50
        else:
            book_details['fine'] = 0
        details.append(book_details)
    return render(request, 'view_issued_book.html', {'details': details})


@login_required(login_url='/student_login')
def view_books_student(request):
    books = Book.objects.all()
    # print("books---->>>", books)
    return render(request, 'view_books_student.html', {'books': books})


@login_required(login_url='/student_login')
def student_issued_books(request):
    current_time = timezone.now()
    student = Student.objects.get(user=request.user)
    student_issue_books = IssueBook.objects.filter(student=student, is_issued=1)
    data = []
    for student_issued_book in student_issue_books:
        expiry_date = student_issued_book.issue_date + timedelta(days=10)
        # print(expiry_date,"?????")
        student_books_detail = {
            # 'student_id': student_issued_book.student.id,
            'student': student_issued_book.student.user,
            'book': student_issued_book.book.name,
            'auther': student_issued_book.book.auther,
            'issue_date': student_issued_book.issue_date,
            'expiry_date': expiry_date
        }
        if current_time > expiry_date:
            differance_in_days = (current_time - expiry_date).days
            student_books_detail['fine'] = differance_in_days * 50
        else:
            student_books_detail['fine'] = 0
        data.append(student_books_detail)
    return render(request, 'student_issued_books.html', {'list_of_issue_book': data})


@login_required(login_url='/student_login')
def profile(request):
    return render(request, 'profile.html')


@login_required(login_url='/student_login')
def edit_profile(request):
    student = Student.objects.get(user=request.user)
    if request.method == 'POST':
        email = request.POST['email']
        phone = request.POST['phone']
        roll_no = request.POST['roll_no']

        student.user.email = email
        student.user.phone = phone
        student.user.roll_no = roll_no
        student.user.save()
        student.save()
        alert = True
        return render(request, 'edit_profile.html', {'alert': alert})
    return render(request, 'edit_profile.html')


def delete_book(request, myid):
    books = Book.objects.filter(id=myid)
    books.delete()
    return redirect('/view_books')


def delete_student(request, myid):
    students = Student.objects.filter(id=myid)
    students.delete()
    return redirect('/view_students')


def delete_view_issued_book(request, myid):
    # print(myid, '------->>>><<<<>><><><<<<<<<')
    books = IssueBook.objects.filter(id=myid)
    books.delete()
    # print(books, '---------------->>>>')
    return redirect('/view_issued_book')


def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        u = User.objects.get(id=request.user.id)
        if u.check_password(current_password):
            u.set_password(new_password)
            u.save()
            alert = True
            return render(request, 'change_password.html', {'alert': alert})
        else:
            currpasswrong = True
            return render(request, 'change_password.html', {'currpasswrong': currpasswrong})
    return render(request, 'change_password.html')


def student_registration(request):
    if request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone = request.POST['phone']
        roll_no = request.POST['roll_no']
        image = request.FILES['image']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            return HttpResponse('password and confirm password does not match')
        if User.objects.filter(username=username).exists():
            return HttpResponse('This User is already Exist')
        user = User.objects.create_user(username=username, email=email,
                                        password=password, first_name=first_name, last_name=last_name)
        student = Student.objects.create(user=user, phone=phone, roll_no=roll_no, image=image)

        user.save()
        student.save()
        alert = True
        return render(request, 'student_registration.html', {'alert': alert})
    return render(request, 'student_registration.html')


def student_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            if request.user.is_superuser:
                return HttpResponse('You are not a student!!!')
            return redirect('profile')
        else:
            alert = True
            return render(request, 'student_login.html', {'alert': alert})
    return render(request, 'student_login.html')


def convertTuple(tup):
    # initialize an empty string
    str = ''
    for item in tup:
        str = str + item
    return str


def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            if request.user.is_superuser:
                return redirect('add_book')
            else:
                return HttpResponse('Your are not an admin')
        else:
            alert = True
            return render(request, 'admin_login.html', {'alert': alert})
    return render(request, 'admin_login.html')


def logout_view(request):
    logout(request)
    return redirect('/')
