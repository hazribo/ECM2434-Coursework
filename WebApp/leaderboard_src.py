
from .models import Profile

# HAS TO BE RUN BEFORE import pyplot
# or server crashes becuase django tries to run matplot lib gui in non
# main thread, this line disables renderer which causes issues
# (renderer) not needed anyway because only image png is needed
from matplotlib import use as setGraphicsEngine; setGraphicsEngine('Agg')
import matplotlib.pyplot as plt

__leaderboard_image_path = "WebApp/static/leaderboard.png"

# generate leaderboard image and save to image path to be used by 
# leaderboard.html, returns path if sucessful else None
def generate_leaderboard_image():

    try:
        # get data
        profiles = Profile.objects.all().order_by('-score')  
        names = [profile.user.username for profile in profiles]  
        scores = [profile.score for profile in profiles]  
        
        # plot data
        plt.bar(names, scores)
        plt.xlabel("Username"); plt.ylabel("Score");
        plt.title("Leaderboard")

        # save png
        open(__leaderboard_image_path, "w").close()
        plt.savefig(__leaderboard_image_path)
        plt.close()

        return __leaderboard_image_path

    except Exception as e:
        print(e)
        return None

