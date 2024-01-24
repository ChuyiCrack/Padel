from django.shortcuts import render,redirect
from .forms import CustomUserCreationForm,Edit_Account
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.http import HttpResponse, HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import login,logout
from .models import Region,Courts,Account,Match
from django.conf import settings
import googlemaps

def index(request):
    user=request.user
    if request.method == 'POST':
        form=AuthenticationForm(data=request.POST)
        if form.is_valid():
            user=form.get_user()
            login(request,user)
            return redirect('home')
        
    elif user.is_authenticated:
        return redirect('home')

    else:
        form=AuthenticationForm()
    
    
    
    
    context={
        'form':form
    }
    return render(request,'index.html',context)

def register(request):
    if request.method == 'POST':
        form=CustomUserCreationForm(request.POST)
        if form.is_valid():
            user=form.save()
            account=Account(owner=user)
            account.save()
            login(request,user)
            return redirect('home')

    else:
        form=CustomUserCreationForm()

    context={
        'form':form
    }
    
    return render(request,'register.html',context)

def logout_user(request):
    logout(request)
    return redirect('index')

def home(request):
    account=Account.objects.get(owner=request.user)
    context={
        'account':account
    }
    return render(request,'home.html',context)

def regions(request):
    account=Account.objects.get(owner=request.user)
    all_regions=Region.objects.all()
    context={
        'regions':all_regions,
        'account':account
    }
    return render(request,'regions.html',context)

def courts(request,pk):
    account=Account.objects.get(owner=request.user)
    Region_Obtained=Region.objects.get(id=pk)
    region_courts=Courts.objects.filter(region=Region_Obtained)
    context={
        'region':Region_Obtained,
        'courts':region_courts,
        'account':account
    }
    return render(request,'courts.html',context)

def Matching(request,pk):
    account=Account.objects.get(owner=request.user)
    target_court=Courts.objects.get(id=pk)
    secret_key=settings.SECRET_KEY
    if request.method == 'POST':
        new_match=Match.objects.create(Creator=account,court=target_court)
        return redirect('match',new_match.id)


    if not (target_court.lat and target_court.lng and target_court.place_id):
        if target_court.Location:
            gmaps=googlemaps.Client(key=secret_key)
            result =gmaps.geocode(target_court.Location)[0]
            lat=result.get('geometry',{}).get('location',{}).get('lat',None)
            lng=result.get('geometry',{}).get('location',{}).get('lng',None)
            place_id=result.get('place_id',{})

            target_court.lat=lat
            target_court.lng=lng
            target_court.place_id=place_id
            target_court.save()

    else:
        lat=target_court.lat
        lng=target_court.lng
        place_id=target_court.place_id

    context={
        'court':target_court,
        'lat':lat,
        'lng':lng,
        'place_id':place_id,
        'key':secret_key,
        'account':account
    }
    return render(request,'matching.html',context)


def profile(request,pk):
    
    try:
        target_account=Account.objects.get(id=pk)
        account=Account.objects.get(owner=target_account.owner)

    except ObjectDoesNotExist:
         return HttpResponseNotFound('''
            <style> body{text-align:center; background-color:#000; color:#fff;}</style><h1>User not Found</h1>''')
    
    context={
        'target_account':account,
        'account':Account.objects.get(owner=request.user)
    }
    return render(request,'profile.html',context)


def edit_profile(request):
    account=Account.objects.get(owner=request.user)
    print(account.owner.username)
    if request.method=='POST':
        form=Edit_Account(request.POST,request.FILES,instance=account)
        print('step1')
        if form.is_valid():
            print('final step')
            form.save()
            return redirect('profile',account.id)
    else:
        form=Edit_Account(instance=account)
    
    context={
        'account':account,
        'form':form
    }
    return render(request,'edit_profile.html',context)

def match(request,pk):
    account=Account.objects.get(owner=request.user)
    The_Match=Match.objects.get(id=pk)

    if 'delete' in request.POST:
        The_Match.delete()
        return redirect('home')

    elif 'start' in request.POST:
        The_Match.started=True
        The_Match.save()
        return redirect('match',The_Match.id)

    elif 'leave' in request.POST:
        The_Match.Joined=None
        The_Match.save()
        return redirect('history_matches')
    
    
    
    context={
        'match':The_Match,
        'account':account
    }
    return render(request,'match.html',context)

def history_matches(request):
    account=Account.objects.get(owner=request.user)
    context={
        'account':account,
    }
    current=Match.objects.filter(Q(Active=True)&(Q(Creator=account)|Q(Joined=account)))
    
    if current.exists():
        context['current']=current[0]
    
    else:
        context['current']=None
    
    
    return render(request,'history_matches.html',context)


def search_match(request):
    account=Account.objects.get(owner=request.user)
    Matches=Match.objects.filter(Active=True,Joined__isnull=True)
    context={
        'account':account,
        'matches':Matches
    }
    return render(request,'search_match.html',context)


def join_match(request,pk):
    account=Account.objects.get(owner=request.user)
    target_match=Match.objects.get(id=pk)
    lat=target_match.court.lat
    lng=target_match.court.lng

    if 'join' in request.POST:
        target_match.Joined=account
        target_match.save()
        return redirect('match',target_match.id)


    context={
        'account':account,
        'match':target_match,
        'lat':lat,
        'lng':lng,
        'key':settings.SECRET_KEY
    }
    return render(request,'join_match.html',context)

def submit_result(request,pk):
    account=Account.objects.get(owner=request.user)
    target_match=Match.objects.get(id=pk)
    if not (account==target_match.Joined or account==target_match.Creator):
        return redirect('home')
    context={
        'account':account,
        'match':target_match
    }
    return render(request,'submit_result.html',context)


