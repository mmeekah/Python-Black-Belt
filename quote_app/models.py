from django.db import models
import bcrypt
import re
from django.db.models import Count

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
LETTER_REGEX = re.compile(r'^[a-zA-Z]*$')

class UserManager(models.Manager):
    def validator(self, post_data):
        errors = {}

        if not LETTER_REGEX.match(post_data['first_name']) or len(post_data['first_name']) < 2 :
            errors['first_name'] = "The first name field is required and should be at least 2 characters long."
        if not LETTER_REGEX.match(post_data['last_name']) or len(post_data['last_name']) < 2:
            errors['last_name'] = "The last name field is required and should be at least 2 characters long."
        if not EMAIL_REGEX.match(post_data['email']):
            errors['email'] = ("Invalid email address or email!")
        if User.objects.filter(email = post_data['email']).exists():
            errors['email'] = ("Email already exists, try logging in.")
        if len(post_data['password']) < 8 or len(post_data['password']) == 0:
            errors['password'] = "The password field is required and should be at least 8 characters long."
        if post_data['password'] != post_data['confirm']:
            errors['confirm'] = "Your passwords do not match, try again!"
        
        return errors
    
    def login_validator(self, postData):
        errors = {}
        if not User.objects.filter(email= postData['email']):
            errors['email'] = 'Account does not exist.'
            return errors
        if User.objects.filter(email = postData['email']):
            user = User.objects.get(email=postData['email'])
        if bcrypt.checkpw(postData['password'].encode(), user.password.encode()):
            return errors
        else:
            if re.match(user.email, postData['email']):
                if not bcrypt.checkpw(postData['password'].encode(), user.password.encode()):
                    errors['password'] = "Password is incorrect."
            else:
                errors['email'] = "Invalid email address."
        return errors
    
    def update_validator(self, postData):
        errors = {}
        if not postData['first_name'].isalpha():
            errors['first_name'] = 'First name contains non-alpha characters.'
        if len(postData['first_name']) < 2:
            errors['first_name'] = 'First name should be at least 2 characters.'
        if len(postData['last_name']) < 2:
            errors['last_name'] = 'Last name should be at least 2 characters.'
        if not postData['last_name'].isalpha():
            errors['last_name'] = 'Last name contains non-alpha characters.'
        if not re.match(EMAIL_REGEX, postData['email']):
            errors['email'] = 'Email is not valid.'
        # if User.objects.filter(email = postData['email']):
        #     errors['email'] = 'Email already exists.'
        return errors




class User(models.Model):
    first_name =  models.CharField(max_length=255)
    last_name =  models.CharField(max_length=255)
    email = models.CharField(max_length=60)
    password = models.CharField(max_length=60)
    confirm = models.CharField(max_length=60)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    def __repr__(self):
        return "<User object: {} {} {}".format(self.first_name, self.last_name, self.email)
    # Create your models here.



class QuoteManager(models.Manager):
    def validator(self, post_data):
        errors = {}
        if len(post_data['author']) < 3 :
            errors['author'] = "The author's name should be at least 3 charachters, please enter it!"
        if len(post_data['quote']) < 10:
            errors['quote'] = "The quote must be at least 10 characters long."
        
        return errors
    
    def process_like(self, postData, id):
        this_user = User.objects.get(id = id)
        this_quote = Quote.objects.get(id = postData['quote_id'])
        this_quote.users_who_like.add(this_user)
        users_who_like = Quote.objects.annotate(count_likes=Count('users_who_like'))
        return users_who_like


class Quote(models.Model):
    author = models.CharField(max_length=60)
    quote = models.TextField()
    uploaded_by = models.ForeignKey(User, related_name="quote_uploaded",on_delete=models.CASCADE)
    # the user who uploaded a given quote
    users_who_like = models.ManyToManyField(User, related_name="liked_quotes")
    # a list of users who like a given quote
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = QuoteManager()

    def __repr__(self):
        return f"<Quote Object: {self.id} {self.title} {self.desc}>"