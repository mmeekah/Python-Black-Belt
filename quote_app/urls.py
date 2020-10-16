from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('register', views.register),
    path('login', views.login),
    path('edit/<user_id>', views.edit_user),
    path('update', views.update_user),
    path('quotes', views.quotes),
    path('user/<uploader_id>', views.user_quotes),
    path('logout', views.logout),
    path('add_quote/<user_id>', views.add_quote),
    path('quotes/<quote_id>', views.quote_profile),
    path('edit_quote/<quote_id>', views.edit_quote),
    path('delete', views.delete),
    # path('delete_quote/<quote_id>', views.delete_quote),
    path('unfavorite/<quote_id>/<user_id>', views.unfavorite),
    path('like', views.like),
    path('favorite_quotes', views.favorite_quotes)

    
]
