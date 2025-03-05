from .models import User, Profile

# Function to return true if database_username is to be returned
# from search bar when input_username is searched for:
def _match(input_username, database_username):
    return                                      \
        input_username in database_username     \
        or                                      \
        database_username in input_username


def get_profile_picture_path_SQL(username):
    return                                    \
        "SELECT profile_picture "            + \
        "FROM WebApp_user,"         + \
        "     WebApp_profile "    + \
        "WHERE WebApp_user.id = WebApp_profile.id "        + \
       f"AND WebApp_user.username = '{username}'"

class SearchResult:
    username = None
    link = None
    score = None
    profile_picture_path = None
    has_profile_pic = None
    idVal = None

# Get list of names that match with input_username:
def search_for_username(input_username):
    if input_username is None: 
        return []

    # Django ORM - filter users that match input:
    users = User.objects.filter(username__icontains=input_username)

    matches = []
    for user in users:
        result = SearchResult()
        result.username = user.username
        result.score = None
        result.link = f"../../profile/{user.username}"
        result.idVal = f'{user.id}/'

        profile = Profile.objects.filter(user=user).first()
        if profile and profile.profile_picture:
            result.profile_picture_path = f"../WebApp/media/{profile.profile_picture}"
            result.has_profile_pic = True
        else:
            result.profile_picture_path = f"../WebApp/static/nopfp.png"
            result.has_profile_pic = False

        matches.append(result)

    return matches