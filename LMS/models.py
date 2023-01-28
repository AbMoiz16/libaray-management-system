from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta


# Create your models here.
class Book(models.Model):
    name = models.CharField(max_length=200)
    auther = models.CharField(max_length=200)
    isbn = models.PositiveIntegerField()
    category = models.CharField(max_length=250)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return str(self.name) + " [" + str(self.isbn)+']'


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_no = models.CharField(max_length=5, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    image = models.ImageField(upload_to="", blank=True)

    def __str__(self):
        return str(self.user) + " [" + str(self.roll_no)+']'


def expire():
    return datetime.today() + timedelta(days=10)


class IssueBook(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    issue_date = models.DateTimeField(auto_now=True)
    is_issued = models.BooleanField(default=False)
