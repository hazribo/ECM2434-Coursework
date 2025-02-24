from .models import User
from django.db import connection


# function to return true if datbase_username is to be returned
# from seach bar when input_username is searched for
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

# get list of names that match with input_username
def searchForUsername(input_username):

    if input_username is None: return []
    
    database = User.objects.values_list;
    matches = []

    with connection.cursor() as SQL_reader:

        for database_username in database("username"):

            if _match(input_username, database_username[0]):

                result = SearchResult()
                result.username = database_username[0]
                result.score = None # todo
                result.link = f"../../profile/{result.username}"

                query = get_profile_picture_path_SQL(result.username)
                SQL_reader.execute(query)
                sql_result = SQL_reader.fetchall()

                result.profile_picture_path = \
                    None if sql_result == [('',)] else ("../WebApp/media/" + sql_result[0][0])
            
                result.has_profile_pic = result.profile_picture_path is not None

                matches.append(result)

    return matches;