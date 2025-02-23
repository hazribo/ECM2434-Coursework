from .models import User


# function to return true if datbase_username is to be returned
# from seach bar when input_username is searched for
def _match(input_username, database_username):
    return                                      \
        input_username in database_username     \
        or                                      \
        database_username in input_username
        

class SearchResult:
    username = None
    link = None
    score = None

# get list of names that match with input_username
def searchForUsername(input_username):

    if input_username is None: return []
    
    database = User.objects.values_list;
    matches = []

    for database_username in database("username"):

        if _match(input_username, database_username[0]):

            result = SearchResult()
            result.username = database_username[0]
            result.score = None # todo
            result.link = f"../../profile/{result.username}"
            
            matches.append(result)

    return matches;