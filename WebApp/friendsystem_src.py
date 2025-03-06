from codecs import getdecoder
from .models import *

class DistilledProfileData:
    hasPfp = None
    name = None
    pfpUrl = None
    link = None
    acceptURL = None; rejectURL = None

def get_data_for_list(item, asker_profile):
    data = DistilledProfileData()

    # i know this is bad but i dont know how else 
    try:
        x = item.profile_picture.path
        data.hasPfp = True
        data.pfpUrl = item.profile_picture.url
    except ValueError:
        data.pfpUrl = False

    data.name = item.user.username
    data.link = f"../../profile/{data.name}"

    data.acceptURL = f'accept/{asker_profile.id}/{item.id}'
    data.rejectURL = f'reject/{asker_profile.id}/{item.id}'

    return data

def record_friend_request_response(sender_id, recipient_id, accepted):       
    # print("accepted ", accepted)
    self_model = Profile.objects.get(user_id=sender_id)
    target_user = User.objects.get(id=recipient_id)

    if (accepted):
        self_model.friend_list.add(target_user)
        target_user.profile.friend_list.add(self_model.user)

    self_model.friend_requests.remove(target_user)

def get_friend_list(profile):
    # get all friend User objects of current profile
    # then find profile obects for those corresponding User objects
    # then call getdataforlist function on all profiles
    friends = [user.profile for user in profile.friend_list.all()];
    return [get_data_for_list(element, profile) for element in friends]

def get_friend_request_list(profile):
    friends = [element.profile for element in profile.friend_requests.all()];
    return [get_data_for_list(e, profile) for e in friends]

def send_friend_request(to_id, from_id):
    # print(f"SENDING FRIEND REQ TO {to_id} FROM {from_id}")

    target_model = Profile.objects.get(user_id=from_id);
    self_model = User.objects.get(id=to_id);

    target_model.friend_requests.add(self_model);
    
   