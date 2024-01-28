from django.shortcuts import render,redirect
from django.contrib import messages
from .forms import CustomUserCreationForm,Edit_Account
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.http import HttpResponse, HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import login,logout
from .models import Region,Courts,Account,Match,result
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
    message=messages.get_messages(request)
    context={
        'account':account,
        'messages':message,
    }
    current=Match.objects.filter(Q(Active=True)&(Q(Creator=account)|Q(Joined=account)))
    
    
    if current.exists():
        context['current']=current[0]
    
    else:
        context['current']=None

    match_completed=result.objects.filter((Q(target_match__Active=False)&(Q(target_match__Creator=account)|Q(target_match__Joined=account)))).order_by('-target_match__date_created')
    context['history_matches']=match_completed

    
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
    targeted_match=Match.objects.get(id=pk)
    try:
        Result=result.objects.get(target_match=targeted_match)

    except result.DoesNotExist:
        Result=result.objects.create(target_match=targeted_match)

    if not (account==targeted_match.Joined or account==targeted_match.Creator):
        return redirect('home')
    
    if request.method == 'POST':
        creator=request.POST.get('creator')
        oponent=request.POST.get('oponent')
        if targeted_match.Creator == account:
            Result.res_creator=f'{creator}-{oponent}'
            print(Result)
            Result.save()
            return redirect('submit_result',targeted_match.id)
        
        else:
            Result.res_joined=f'{creator}-{oponent}'
            Result.save()
    
    if Result.res_joined!='NONE' and Result.res_creator!='NONE' and Result.submited == False:
        if not (Result.res_joined==Result.res_creator):
            messages.error(request,'The submits does not match')
            Result.res_creator='NONE'
            Result.res_joined='NONE'
            Result.save()
            return redirect('submit_result',targeted_match.id)

        else:
            targeted_match.Active=False
            targeted_match.save()
            count=0
            score_creator=''
            score_joined=''
            for score in (Result.res_creator):
                if score != '-':
                    if count==0:
                        score_creator=int(score)
                        count+=1

                    else:
                        score_joined=int(score)
            if score_creator>score_joined:
                Result.winner=targeted_match.Creator
                Result.looser=targeted_match.Joined
                targeted_match.Creator.points+=35
                targeted_match.Creator.wins+=1
                targeted_match.Joined.points-=35
                
            
            elif score_creator<score_joined:
                Result.winner=targeted_match.Joined
                Result.looser=targeted_match.Creator
                targeted_match.Creator.points-=35
                targeted_match.Joined.wins+=1
                targeted_match.Joined.points+=35
        
            else:
                Result.winner=None
                Result.looser=None
            
            targeted_match.Creator.played_matches+=1
            targeted_match.Joined.played_matches+=1
            targeted_match.Creator.save()
            targeted_match.Joined.save()
            Result.creator_score=score_creator
            Result.joined_score=score_joined
            Result.submited=True
            Result.save()
            messages.info(request,'The match was successfully completed')
            return redirect ('history_matches')
    
    elif Result.submited == True:
        messages.info(request,'The match was successfully completed')
        return redirect ('history_matches')

            
    context={
        'account':account,
        'match':targeted_match,
        'result':Result
    }
    return render(request,'submit_result.html',context)

