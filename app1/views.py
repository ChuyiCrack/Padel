from django.shortcuts import render,redirect
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q,Count
from django.http import HttpResponse, HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import login,logout
from .models import Region,Courts,Account,Match,result,friend_requests,party_invite,Party
from django.conf import settings
import googlemaps
from PIL import Image
from django.utils import timezone

def rewrite_activity(user):
    account=Account.objects.get(owner=user.id)
    account.last_activity=timezone.now()
    account.save()
    return account

def delete_matches():
    Matches=Match.objects.filter(
        Q(Active=True) & ((Q(started=False) & Q(want_to_start__lt=((timezone.now()- timezone.timedelta(seconds=43200)))) | (Q(started=True) & Q(date_started__lt=(timezone.now()- timezone.timedelta(seconds=50400))))))
    )
    for target_match in Matches:

        target_match.delete()
    return



        

def check_matches(account:Account):
    any_match=Match.objects.filter(
        ((Q(Creator=account))|(Q(Joined=account))) & (Q(Active=True))
    )
    if any_match.exists():
        return any_match.first().id
    
    return False

def calculate_notifications(account:Account):
    party_notifications=party_invite.objects.filter(receiver=account)
    for party in party_notifications:
        if party.sender.party_group:
            party.delete() 
    friend_notifications=friend_requests.objects.filter(receiver=account)
    return (friend_notifications.count() + party_notifications.count())

def get_resolution(image):
    try:
        with Image.open(image) as img:
            width, height = img.size
            return width, height
    except FileNotFoundError:
        return None

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
    account=rewrite_activity(request.user)
    delete_matches()
    if 'kick' in request.POST:
        party_to_delete=Party.objects.get(id=request.POST.get('kick', None))
        party_to_delete.delete()
        return redirect('home')
    
    context={
        'account':account,
        'notifications':calculate_notifications(account),
        'any_match':check_matches(account),
    }
    return render(request,'home.html',context)

def regions(request):
    account=rewrite_activity(request.user)
    any_matche=check_matches(account)
    if any_matche:
        return redirect('match',any_matche)
    all_regions=Region.objects.all()
    context={
        'regions':all_regions,
        'account':account,
        'notifications':calculate_notifications(account)
    }
    return render(request,'regions.html',context)

def courts(request,pk):
    account=rewrite_activity(request.user)
    Region_Obtained=Region.objects.get(id=pk)
    any_matche=check_matches(account)
    if any_matche:
        return redirect('match',any_matche)
    region_courts=Courts.objects.filter(region=Region_Obtained)
    context={
        'region':Region_Obtained,
        'courts':region_courts,
        'account':account,
        'notifications':calculate_notifications(account)
    }
    return render(request,'courts.html',context)

def Matching(request,pk):
    account=rewrite_activity(request.user)
    target_court=Courts.objects.get(id=pk)
    secret_key=settings.SECRET_KEY
    any_matche=check_matches(account)
    if any_matche:
        return redirect('match',any_matche)
    
    if request.method == 'POST':
        if 'checkbox' in request.POST:
            checkbox_value=True

        else:
            checkbox_value=False

        date=request.POST.get('datetime', None)
        if date > (timezone.now() + timezone.timedelta(seconds=64800)).strftime('%Y-%m-%dT%H:%M') or date< (timezone.now() - timezone.timedelta(seconds=21600)).strftime('%Y-%m-%dT%H:%M'):
            messages.error(request,'You can only make matches for the next 24 hours')
            return redirect('matching',pk)


        new_match=Match.objects.create(Creator=account,court=target_court,ranked=checkbox_value,want_to_start=date)
        new_match.Joined.add(account.party_group.Joined)
        new_match.save()
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
        'account':account,
        'notifications':calculate_notifications(account),
        'time':(timezone.now()- timezone.timedelta(seconds=21600)).strftime('%Y-%m-%dT%H:%M')
    }
    return render(request,'matching.html',context)


def profile(request,pk):
    try:
        target_account=Account.objects.get(id=pk)
        account=rewrite_activity(request.user)

    except ObjectDoesNotExist:
         return HttpResponseNotFound('''
            <style> body{text-align:center; background-color:#000; color:#fff;}</style><h1>User not Found</h1>''')

    if 'send' in request.POST:
        fr_request=friend_requests.objects.create(sender=account,receiver=target_account)
        return redirect('profile',target_account.id)
    
    elif 'accept' in request.POST:
        account.friends.add(target_account)
        account.save()
        fr_request=friend_requests.objects.get(sender=target_account,receiver=account).delete()
        return redirect('profile',target_account.id)
    
    
    context={
        'target_account':target_account,
        'account':account,
        'notifications':calculate_notifications(account),
    }
    
    requestes=friend_requests.objects.filter(((Q(sender=account))&(Q(receiver=target_account)))|(Q(sender=target_account))&(Q(receiver=account)))
    is_friends=account.friends.filter(id=target_account.id).exists()
    
    if requestes.exists():
        context['friend_request']=requestes[0]
    
    else:
        context['friend_request']=None

    if is_friends:
        context['friends']=True
    else:
        context['friends']=False   
    
    return render(request,'profile.html',context)


def edit_profile_picture(request):
    account=rewrite_activity(request.user)
    if request.method == 'POST':
        my_uploaded_file = request.FILES.get('profile_picture')
        resolution = get_resolution(my_uploaded_file)
        if resolution:
            width,height=resolution
            ratio=round((width/height),2)
            print(ratio)
            if ratio >= 0.85 and ratio<=1.2:
                account.profile_picture=my_uploaded_file
                account.save()
                return redirect('profile',account.id)
            
            else:
                messages.error(request,'you need to upload images with ratio 1:1')
            

        else:
            messages.error(request,'Something went wrong')

        return redirect('profile_picture')
        
    
    context={
       'account':account, 
    }
    return render(request,'change_profilepicture.html',context)

def edit_background(request):
    account=rewrite_activity(request.user)
    if request.method == 'POST':
        my_uploaded_file = request.FILES.get('profile_picture')
        resolution = get_resolution(my_uploaded_file)
        if resolution:
            width,height=resolution
            ratio=round((width/height),2)
            if ratio >= 1.5 and ratio<=1.8:
                account.homepage_picture=my_uploaded_file
                account.save()
                return redirect('profile',account.id)
            
            else:
                messages.error(request,'Try to upload an image with those ratios (3:2,4:3,16:9)')
            

        else:
            messages.error(request,'Something went wrong')

        return redirect('profile_picture')
    context={
       'account':account, 
    }
    return render(request,'edit_cover.html',context)

def match(request,pk):
    account=rewrite_activity(request.user)
    try:
        The_Match=Match.objects.get(id=pk)

    except ObjectDoesNotExist:
        messages.error(request,'The Match does not exist or has been removed')
        return redirect('home')

    if The_Match.ranked and not account.party_group:
        if The_Match.Creator == account:
            The_Match.delete()
            return redirect('home')

        else:
            The_Match.Joined.remove(account)
            return redirect('home')
    
    
    if not The_Match.Active:
        return redirect('history_matches')

    if account not in The_Match.Joined.all() and account != The_Match.Creator:
        return redirect('home')
    
    if 'delete' in request.POST:
        The_Match.delete()
        return redirect('home')

    elif 'start' in request.POST:
        The_Match.started=True
        The_Match.date_started=(timezone.now()- timezone.timedelta(seconds=21600))
        The_Match.save()
        return redirect('match',The_Match.id)

    elif 'leave' in request.POST:
        if account.party_group:
            if account.party_group.Joined == account and account.party_group.Creator == The_Match.Creator:
                The_Match.delete()
                party_to_delete=Party.objects.get(id=account.party_group.id)
                party_to_delete.delete()
                messages.error(request,'The Team of the party leader has left the match')
                return redirect('home')

            if account.party_group.Creator == account:
                The_Match.Joined.remove(account,account.party_group.Joined)
                The_Match.save()
                return redirect('home')
            
            elif account.party_group.Joined == account and The_Match.ranked:
                The_Match.Joined.remove(account,account.party_group.Creator)
                The_Match.save()
                party_to_delete=Party.objects.get(id=account.party_group.id)
                party_to_delete.delete()
                return redirect('home')
            else:
                The_Match.Joined.remove(account)
                The_Match.save()
                party=Party.objects.get(Joined=account)
                party.delete()
                return redirect('home')


        else:
            The_Match.Joined.remove(account)
            The_Match.save()
            return redirect('home')
    
    elif 'kick_rank' in request.POST:
        for user in The_Match.Joined.all():
            if user != The_Match.Creator.party_group.Joined:
                if (The_Match.Joined.all().count()) >= 3:
                    user1=user.party_group.Joined if user.party_group.Creator == user else user.party_group.Creator
                    The_Match.Joined.remove(user,user1)
                    
                else:
                    The_Match.Joined.remove(user)

                The_Match.save()
                return redirect('match',The_Match.id)

    elif 'kick' in request.POST:
        targeted_account=Account.objects.get(id=request.POST.get('kick', None))
        The_Match.Joined.remove(targeted_account)
        The_Match.save()
        return redirect('match',The_Match.id)
    
    elif 'end' in request.POST:
        The_Match.Active=False
        The_Match.save()
        new_result=result.objects.create(type_match='casual',target_match=The_Match)
        return redirect('history_matches')



    context={
        'match':The_Match,
        'account':account,
        'notifications':calculate_notifications(account),
        'user_reminder':[x for x in range(3-(The_Match.Joined.count()))],
        'time':(timezone.now()- timezone.timedelta(seconds=21600))
    }
    return render(request,'match.html',context)

def history_matches(request):
    account=rewrite_activity(request.user)
    message=messages.get_messages(request)
    context={
        'account':account,
        'messages':message,
        'notifications':calculate_notifications(account),
    }
    current=Match.objects.filter(Q(Active=True)&(Q(Creator=account)|Q(Joined=account)))
    

    if current.exists():
        context['current']=current[0]

    else:
        context['current']=None

    match_completed=result.objects.filter((Q(target_match__Active=False)&(Q(target_match__Creator=account)|Q(target_match__Joined__in=[account])))).order_by('-target_match__date_started').distinct()
    context['history_matches']=match_completed
    print(match_completed)

    return render(request,'history_matches.html',context)


def search_match(request):
    account=rewrite_activity(request.user)
    Matches=Match.objects.annotate(num_joined=Count('Joined')).filter(Q(num_joined__lte=2) & Q(Active=True) & Q(started=False))
    number_matches=Matches.count()
    delete_matches()
    context={
        'account':account,
        'matches':Matches,
        'total_matches':number_matches,
        'notifications':calculate_notifications(account),
        'time_server':timezone.now()+ timezone.timedelta(seconds=21600)
    }
    
    if request.method == 'POST':
        ranked_s= True if 'ranked' in request.POST else False
        casual_s= False if 'casual' in request.POST else True
        search= request.POST.get('search',None)
        if casual_s and ranked_s:
            new_matches=Matches.filter((Q(Creator__owner__username__icontains=search) | Q(Joined__owner__username__icontains=search)) & Q(ranked=ranked_s))
        elif casual_s == False and ranked_s == False:
            new_matches=Matches.filter((Q(Creator__owner__username__icontains=search) | Q(Joined__owner__username__icontains=search)) & Q(ranked=casual_s))

        else:
            new_matches=Matches.filter((Q(Creator__owner__username__icontains=search) | Q(Joined__owner__username__icontains=search)))
        
        print(new_matches)
        context['matches']=new_matches
        return render(request,'search_match.html',context)
            
    
    return render(request,'search_match.html',context)


def join_match(request,pk):
    account=rewrite_activity(request.user)
    target_match=Match.objects.get(id=pk)
    any_matche=check_matches(account)
    if any_matche == pk:
        return redirect('match',any_matche)
    lat=target_match.court.lat
    lng=target_match.court.lng

    if 'join' in request.POST:
        target_match.Joined.add(account)
        
        if account.party_group:
            target_match.Joined.add(account.party_group.Joined)

        target_match.save()
        return redirect('match',target_match.id)


    context={
        'account':account,
        'match':target_match,
        'lat':lat,
        'lng':lng,
        'key':settings.SECRET_KEY,
        'notifications':calculate_notifications(account)
    }
    return render(request,'join_match.html',context)

def submit_result(request,pk):
    def end_match_function(creator_win:bool,Match:Match,Result:result):
        for x in Match.Joined.all():
            if x != Match.Creator.party_group.Joined:
                joined_leader=x.party_group.Creator
                break
        
        if creator_win:
            Result.winner.add(Match.Creator,Match.Creator.party_group.Joined)
            Result.looser.add(joined_leader,joined_leader.party_group.Joined)
            creator_points=35
            joined_points=-35

            
        else:
            Result.looser.add(Match.Creator,Match.Creator.party_group.Joined)
            Result.winnerr.add(joined_leader,joined_leader.party_group.Joined)
            creator_points=-35
            joined_points=35

        Match.Creator.played_matches+=1
        Match.Creator.points+=creator_points
        Match.Creator.party_group.Joined.played_matches+=1
        Match.Creator.party_group.Joined.points+=creator_points
        joined_leader.played_matches+=1
        joined_leader.points+=joined_points
        joined_leader.party_group.Joined.played_matches+=1
        joined_leader.party_group.Joined.points+=joined_points
        Match.Creator.save()
        Match.Creator.party_group.Joined.save()
        joined_leader.save()
        joined_leader.party_group.Joined.save()
        return

    account=rewrite_activity(request.user)
    targeted_match=Match.objects.get(id=pk)
    if account != targeted_match.Creator and account != targeted_match.Joined.all()[1].party_group.Creator:
        print(True)

    try:
        Result=result.objects.get(target_match=targeted_match)

    except result.DoesNotExist:
        Result=result.objects.create(target_match=targeted_match)


    if request.method == 'POST':
        creator=request.POST.get('creator')
        oponent=request.POST.get('oponent')
        if targeted_match.Creator == account:
            Result.res_creator=f'{creator}-{oponent}'
        else:
            Result.res_joined=f'{creator}-{oponent}'
            
        Result.save()
        return redirect('submit_result',targeted_match.id)

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
                end_match_function(True,targeted_match,Result)


            elif score_creator<score_joined:
                end_match_function(False,targeted_match,Result)

            else:
                Result.winner=None
                Result.looser=None

            Result.creator_score=score_creator
            Result.joined_score=score_joined
            Result.type_match= 'ranked' if targeted_match.ranked else 'casual'
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
        'result':Result,
        'notifications':calculate_notifications(account)
    }
    return render(request,'submit_result.html',context)


def notifications_friends(request):
    account=rewrite_activity(request.user)
    context={
        'account':account,
        'notifications':calculate_notifications(account)
    }
    all_friend_request=friend_requests.objects.filter(receiver=account)
    if calculate_notifications(account) >= 1 and not all_friend_request.exists():
        return redirect('notifications_party')

    
    if request.method == 'POST':
        id_friend_request= request.POST.get('added', None)
        fr_request=friend_requests.objects.get(id=id_friend_request)
        fr_request.sender.friends.add(fr_request.receiver)
        fr_request.sender.save()
        fr_request.delete()
        return redirect('notifications_friends')
    
    context['friend_request']=all_friend_request
    return render(request,'notifications_friends.html',context)

def notifications_party(request):
    account=rewrite_activity(request.user)
    all_invitation_party=party_invite.objects.filter(receiver=account)

    if 'join' in request.POST:
        id_party_sender= request.POST.get('join', None)
        sender_account=Account.objects.get(id=id_party_sender)
        if sender_account.party_group:
            party_notification=party_invite.objects.get(receiver=account,sender=sender_account).delete()
            return redirect('notifications_party')
        
        new_party=Party.objects.create(Creator=sender_account,Joined=account)
        account.party_group=new_party
        sender_account.party_group=new_party
        account.save()
        sender_account.save()
        party_notification=party_invite.objects.get(receiver=account,sender=sender_account).delete()
        return redirect('home')
    context={
        'account':account,
        'partys':all_invitation_party,
        'current_time':(timezone.now() - timezone.timedelta(seconds=900)),
        'notifications':calculate_notifications(account)
    }
    any_matche=check_matches(account)
    if any_matche:
        context['any_macth']=True
    else:
        context['any_macth']=False
    return render(request,'notifications_party.html',context)

def invite_party(request):
    account=rewrite_activity(request.user)
    friends=account.friends.order_by('-last_activity')
    if account.party_group:
        return redirect('home')
    
    if 'invitation' in request.POST:
        all_party_invitations=party_invite.objects.filter(sender=account)
        id_party_receiver= request.POST.get('invitation', None)
        receiver_party=Account.objects.get(id=id_party_receiver)
        if all_party_invitations.exists():
            invitation_to_delete=all_party_invitations.first()
            invitation_to_delete.delete()

        party_invitation=party_invite.objects.create(sender=account,receiver=receiver_party)
        return redirect('party')
    
    context={
        'account':account,
        'friends':friends,
        'current_time':(timezone.now() - timezone.timedelta(seconds=900)),
        '2min':(timezone.now() - timezone.timedelta(seconds=120)),
        'notifications':calculate_notifications(account),
        'any_match':check_matches(account)
    }

    party_invitation=party_invite.objects.filter(sender=account)
    if party_invitation.exists:
        context['party']=party_invitation.first()
    
    else:
        context['party']=None

    
    return render(request,'invite_party.html',context)


def search_friends(request):
    account=rewrite_activity(request.user)
    context={
        'account':account,
        'notifications':calculate_notifications(account),
    }
    if 'submit_search' in request.POST:
        searched=request.POST.get('search', None)
        Selected_Users=Account.objects.filter(owner__username__icontains=searched)
        context['filtered']=Selected_Users
        return render(request,'search_friends.html',context)
    return render(request,'search_friends.html',context)