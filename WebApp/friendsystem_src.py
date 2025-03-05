from codecs import getdecoder
from .models import *


class DistilledProfileData:
    hasPfp = None
    name = None
    pfpUrl = None
    link = None
    acceptURL = None; rejectURL = None

def getDataForList(item, askerProfile):

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

    data.acceptURL = f'accept/{askerProfile.id}/{item.id}'
    data.rejectURL = f'reject/{askerProfile.id}/{item.id}'

    return data





def recordFriendRequestResponse(senderId, recipientId, accepted):
        
    # print("accepted ", accepted)
    selfModel = Profile.objects.get(user_id=senderId)
    targetUser = User.objects.get(id=recipientId)

    if (accepted):
        selfModel.friend_list.add(targetUser)
        targetUser.profile.friend_list.add(selfModel.user)

    selfModel.friend_requests.remove(targetUser)





def get_friend_list(profile):

    # get all friend User objects of current profile
    # then find profile obects for those corresponding User objects
    # then call getdataforlist function on all profiles
    friends = [user.profile for user in profile.friend_list.all()];
    return [getDataForList(element, profile) for element in friends]


def get_friend_request_list(profile):
    friends = [element.profile for element in profile.friend_requests.all()];
    return [getDataForList(e, profile) for e in friends]





def send_friend_request(toId, fromId):
    # print(f"SENDING FRIEND REQ TO {toId} FROM {fromId}")

    targetModel = Profile.objects.get(user_id=fromId);
    selfModel = User.objects.get(id=toId);

    targetModel.friend_requests.add(selfModel);
    
   