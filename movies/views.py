from django.shortcuts import render, redirect
import tmdbsimple as tmdb
import json
from time import mktime
import time
from datetime import datetime, date
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

from django.contrib.auth import authenticate, login, logout
from . forms import CreateUserForm
from . models import *

# API KEYS and Request Parameters
tmdb.API_KEY = '26731892a5e9d4990bdabe9dca773a49'
DEVELOPER_KEY = 'AIzaSyBpOpUxmOX6x5oKJeXGF_Gs7-1uaK-WB3A'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
# Create your views here.


def movies(request):
    popular_movies_tmdb = tmdb.Movies('popular')
    popular_movies = popular_movies_tmdb.info()['results']

    upcoming_movies_tmdb = tmdb.Movies('upcoming')
    upcoming_movies = upcoming_movies_tmdb.info()['results']

    horror_movies_tmdb = tmdb.Movies('popular')
    horror_movies = popular_movies_tmdb.info()['results']
    horror =[]
    for x in popular_movies:
        for y in x['genre_ids']:
            if(y==27):
                horror.append(x)

    action_movies_tmdb = tmdb.Movies('popular')
    action_movies = popular_movies_tmdb.info()['results']
    action =[]
    for x in popular_movies:
        for y in x['genre_ids']:
            if(y==28):
                action.append(x)

    drama_movies_tmdb = tmdb.Movies('popular')
    drama_movies = drama_movies_tmdb.info()['results']
    drama =[]
    for x in drama_movies:
        for y in x['genre_ids']:
            if(y==18):
                drama.append(x)

    comedy_movies_tmdb = tmdb.Movies('top_rated')
    comedy_movies = comedy_movies_tmdb.info()['results']
    comedy =[]
    for x in comedy_movies:
        for y in x['genre_ids']:
            if(y==35):
                comedy.append(x)

    return render(request, 'movies.html', {'popular': popular_movies, 'upcoming': upcoming_movies, 'horror':horror, 'action':action, 'drama':drama, 'comedy':comedy})



def single_movie(request, movie_id):
    movies_tmdb = tmdb.Movies(movie_id)
    movies = movies_tmdb.info()
    date_created = movies['release_date']
    date_created_time_struct = time.strptime(date_created, '%Y-%m-%d')
    date_created_date = datetime.fromtimestamp(
        mktime(date_created_time_struct)).date()
    year = date_created_date.year
    # Get movie name and use it to pass it as an argument to the youtube api.
    movie_name = movies['original_title']
    youtube = build(YOUTUBE_API_SERVICE_NAME,
                    YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
    search_response = youtube.search().list(
        q=movie_name, part='id,snippet', maxResults=1).execute()
    for search_result in search_response.get('items', []):
        if search_result['id']['kind'] == 'youtube#video':
            video_id = search_result['id']['videoId']
    return render(request, 'single_movie.html', {'movies': movies, 'year': year, 'videoId': video_id})


def home(request):

    return render(request, 'accounts/home.html')


def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
            login(request, user)
            return redirect('myMovies')
        else:
            messages.info(request, 'Username OR Password is incorrect')
            return render(request, 'accounts/login.html')

    return render(request, 'accounts/login.html')


def logoutUser(request):
    logout(request)
    return redirect('login')


def register(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(
                request, 'Account was successfully created for ' + user)
            return redirect('login')

    return render(request, 'accounts/register.html', {'form': form})
