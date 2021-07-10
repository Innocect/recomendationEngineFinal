import pandas as pd
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib import messages
from django.db.models import Case, When
from django.db.models import Q
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect

from .forms import *
from .models import Movie, Myrating
import random

moviesLiked = set()
movi = Movie.objects.all()


# Create your views here

def index(request):
    mo = []

    for m in movi:
        mo.append(m)
    action = []
    a = []
    drama = []
    d = []
    comedy = []
    r = []
    crime = []
    ani = []

    for movie in movi:
        x = movie.genre.split(',')
        if ("Action" in x):
            action.append(movie)
        if ("Drama" in x):
            drama.append(movie)
        if ("Comedy" in x):
            comedy.append(movie)
        if ("Crime" in x):
            crime.append(movie)

    random.shuffle(action)
    random.shuffle(drama)
    random.shuffle(comedy)
    random.shuffle(crime)

    for i in range(5):
        a.append(action[i])
        d.append(drama[i])
        r.append(comedy[i])
        ani.append(crime[i])

    Recmovies = list(recommend(request))
    likedMovies(request)
    print("Liked")
    print(list(moviesLiked))

    # print("Recommendation Movies: ")
    print("Recmovies: ")
    print(Recmovies)
    Searchquery = request.GET.get('searchIt')
    # print(Searchquery)
    if Searchquery:
        moviesSearch = Movie.objects.filter(Q(title__icontains=Searchquery)).distinct()
        # print(moviesSearch)
        context = {'moviesLiked': list(set(moviesLiked)), 'moviesBeh': Recmovies[-4:], 'movies': Recmovies[:3],
                   'drama': d,
                   'action': a,
                   'comedy': r,
                   'crime': ani,
                   'moviesSearch': moviesSearch}
        # context = {'moviesLiked': list(set(moviesLiked)), 'moviesBeh': Recmovies, 'movies': Recmovies,
        #            'drama': drama,
        #            'action': action,
        #            'romance': romance,
        #            'moviesSearch': moviesSearch}
        return render(request, 'SidHtml/views/home.html',
                      context)
    # print(drama)
    # return render(request, 'SidHtml/views/home.html',
    #               {'moviesLiked': list(set(moviesLiked)), 'moviesBeh': Recmovies, 'movies': Recmovies,
    #                'drama': drama,
    #                'action': action,
    #                'romance': romance})
    return render(request, 'SidHtml/views/home.html',
                  {'moviesLiked': list(set(moviesLiked))[:5], 'moviesBeh': Recmovies[-3:], 'movies': Recmovies[:4],
                   'drama': d,
                   'action': a,
                   'comedy': r,
                   'crime': ani,
                   'mo': mo})


def likedMovies(request):
    likedList = list(Myrating.objects.filter(user=request.user.id).values())
    for each in likedList:
        movie = Movie.objects.get(id=each['movie_id'])
        if int(each['rating']) > 3:
            moviesLiked.add(movie)
        if int(each['rating']) < 3 and (movie in moviesLiked):
            moviesLiked.remove(movie)


# For similar Movies
def get_similar(movie_name, rating, corrMatrix):
    similar_ratings = corrMatrix[movie_name] * (rating - 2.5)
    similar_ratings = similar_ratings.sort_values(ascending=False)
    return similar_ratings


# Main Recommendation Logic
def recommend(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if not request.user.is_active:
        raise Http404

    movie_rating = pd.DataFrame(list(Myrating.objects.all().values()))  # "1.."
    new_user = movie_rating.user_id.unique().shape[0]
    current_user_id = request.user.id
    print("Current user id")
    print(current_user_id)
    # if new user not rated any movie       "2.."
    if current_user_id > new_user:
        movie = Movie.objects.get(id=19)
        q = Myrating(user=request.user, movie=movie, rating=0)
        q.save()

    # "3.."
    userRatings = movie_rating.pivot_table(index=['user_id'], columns=['movie_id'], values='rating')
    userRatings = userRatings.fillna(0, axis=1)
    corrMatrix = userRatings.corr(method='pearson')
    print("Corr MAtrix")
    print(corrMatrix)

    # "4"
    user = pd.DataFrame(list(Myrating.objects.filter(user=request.user).values())).drop(['user_id', 'id'], axis=1)
    user_filtered = [tuple(x) for x in user.values]

    #"5.."
    similar_movies = pd.DataFrame()
    # print(similar_movies)
    for movie, rating in user_filtered:
        similar_movies = similar_movies.append(get_similar(movie, rating, corrMatrix), ignore_index=True)

    #"6.."
    movies_id = list(similar_movies.sum().sort_values(ascending=False).index)
    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(movies_id)])
    movie_list = list(Movie.objects.filter(id__in=movies_id).order_by(preserved)[:7])
    return movie_list


# Rating System
def rating(request, m_id):
    movies = get_object_or_404(Movie, id=m_id)
    movie = Movie.objects.get(id=m_id)
    print(m_id)
    if request.method == "POST":
        rate = request.POST.get('rating')
        if Myrating.objects.all().values().filter(movie_id=m_id, user=request.user):
            Myrating.objects.all().values().filter(movie_id=m_id, user=request.user).update(rating=rate)
        else:
            temp = Myrating(user=request.user, movie=movie, rating=rate)
            temp.save()
        print("else part")
        messages.success(request, "Rating has been saved successfully!")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    valList = list(Myrating.objects.filter(user=request.user.id).values())
    movie_rating = 0
    rate_flag = False
    for each in valList:
        if int(each['movie_id']) == int(m_id):
            movie_rating = each['rating']
            rate_flag = True
            break
    print("Rate Flag:" + str(rate_flag))

    context = {'movies': movies, 'movie_rating': movie_rating, 'rate_flag': rate_flag}

    return render(request, 'SidHtml/views/rating.html', context)


# SignUp
def signUp(request):
    moviesLiked = {}
    form = UserForm(request.POST or None)

    if form.is_valid():
        user = form.save(commit=True)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("index")

    context = {'form': form}

    return render(request, 'SidHtml/views/signup.html', context)


# Login
def Login(request):
    moviesLiked = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("index")
            else:
                return render(request, 'SidHtml/views/sign.html', {'error_message': 'Your account disable'})
        else:
            return render(request, 'SidHtml/views/sign.html', {'error_message': 'Invalid Login'})

    return render(request, 'SidHtml/views/sign.html')


# Logout user


def Logout(request):
    moviesLiked.clear()
    logout(request)
    return redirect("login")
