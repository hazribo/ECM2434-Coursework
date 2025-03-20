
from .models import *

def get_leaderboard_data(leaderboard_type='users', limit=10):
    try:
        if leaderboard_type == 'teams':
            queryset = Team.objects.order_by('-score')
        else:
            queryset = Profile.objects.select_related('user').order_by('-score')

        if limit:
            queryset = queryset[:limit]

        top3 = queryset[:3]
        top_rest = queryset[3:limit] if limit else queryset[3:]

        return {
            'top3_items': top3,
            'top_rest_items': top_rest,
            'leaderboard_type': leaderboard_type,
            'limit': limit
        }

    except Exception as e:
        print(f"Error generating leaderboard: {e}")
        return None

