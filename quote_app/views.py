from django.shortcuts import render, redirect
from django.contrib import messages
import bcrypt
from .models import *



def index(request):
    return render(request, 'index.html')

# # Create your views here.
# def index(request):
#     context={
#         'all_quotes': Quote.objects.all()
#     }
#     return render(request, 'index.html', context)

def register(request):
    errors = User.objects.validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/')
    else:
        password = request.POST['password']
        hashed = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
        print(hashed)
        user = User.objects.create(
            first_name=request.POST['first_name'], 
            last_name=request.POST['last_name'],
            email=request.POST['email'], 
            password=hashed,
        )
        request.session['uid'] = user.id
        return redirect('/quotes')

def login(request):
    
    if not request.POST['email'] or not request.POST['password']:
        messages.error(request, "Cannot submit blank data!")
        return redirect('/')
    errors = User.objects.login_validator(request.POST)
    if len(errors):
        for key, value in errors.items():
            messages.error(request, value)
            return redirect('/')
    else:
        user = User.objects.get(email=request.POST['email'])
        request.session['uid'] = user.id
        request.session['first_name'] = user.first_name
        request.session['last_name'] = user.last_name
        # messages.error(request, "Successfully logged in")
        return redirect('/quotes')

def edit_user(request, user_id):
    if 'uid' not in request.session:
        messages.error(request, "Must be logged in to view quotes!")
        return redirect('/') 
    user = User.objects.get(id=request.session['uid'])

    context = {
        'user': User.objects.get(id=request.session['uid']),
        'first_name' : user.first_name,
        'last_name' : user.last_name,
        'email' : user.email,
        'id' : user.id
    }
    return render(request, "edit_user.html", context)

def update_user(request):
    if 'uid' not in request.session:
        messages.error(request, "Must be logged in to view quotes!")
        return redirect('/') 
    
    errors = User.objects.update_validator(request.POST)
    if len(errors):
        id = request.POST['id']
        for key, value in errors.items():
            messages.error(request, value)
            return redirect('/edit/<user_id>')
    else:
        user = User.objects.get(id=request.POST['id'])
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        user.email = request.POST['email']
        user.save()
        request.session['uid'] = user.id
        request.session['first_name'] = user.first_name
        request.session['last_name'] = user.last_name
        messages.error(request, "Successfully changed their information")    
    id = request.POST['id']
    return redirect('/edit/<user_id>')


def quotes(request):
    if 'uid' not in request.session:
        messages.error(request, "Must be logged in to view quotes!")
        return redirect('/')
    id = request.session['uid']
    user = User.objects.get(id=id)

    context = {
        'quotes': Quote.objects.annotate(count_likes=Count('users_who_like')).order_by('-count_likes'),
        'user' : user
    }
    return render(request,'quotes.html',context)

def user_quotes(request, uploader_id):
    if 'uid' not in request.session:
        messages.error(request, "Must be logged in to view this page!")
        return redirect('/')
    uid = User.objects.get(id=request.session['uid'])
    user = User.objects.get(id=uploader_id)
    context = {
        "quotes": user.quote_uploaded.all(),
        'user': user,
        'id' : uid.id
    }
    return render(request, "user_quotes.html", context)        


def add_quote(request, user_id):
    print(request.POST)
    errors = Quote.objects.validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/')
    else:
        user = User.objects.get(id=user_id)
        new_quote = Quote.objects.create(
            author=request.POST['author'], quote=request.POST['quote'], uploaded_by=user)
        new_quote.users_who_like.add(user)
        return redirect('/quotes')

def quote_profile(request, quote_id):
    quote = Quote.objects.get(id=quote_id)
    context = {
        'quote': quote,
        'user': User.objects.get(id=request.session['uid'])
    }
    return render(request, 'quote_profile.html', context)


def edit_quote(request, quote_id):
    errors = Quote.objects.validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/')
    else:
        quote_in_question = Quote.objects.get(id=quote_id)
        quote_in_question.author = request.POST['author']
        quote_in_question.quote = request.POST['quote']
        quote_in_question.save()
        messages.error(request, "Successfully Updated Quote!") 
    return redirect(f'/quotes/{quote_id}')



# Unfavorite a quote
def unfavorite(request, quote_id, user_id):
    quote_in_question = Quote.objects.get(id=quote_id)
    unlike_user = User.objects.get(id=user_id)
    quote_in_question.users_who_like.remove(unlike_user)
    return redirect(f'/quotes')

# Add to Like
def like(request):
    id = request.session['uid']
    users_who_like = Quote.objects.process_like(request.POST, id)
    return redirect('/quotes')


def delete(request):
    
    this_quote = Quote.objects.get(id=request.POST['quote_id'])
    this_quote.delete()
    return redirect('/quotes')

# List of favorite quotes for user who is logged in
def favorite_quotes(request):
    context = {
        'user': User.objects.get(id=request.session['uid']),
    }
    return render(request, 'favorite_quotes.html', context)

def logout(request):
    request.session.clear()
    messages.error(request, "You have successfully logged out.")
    return redirect('/')