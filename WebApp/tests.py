from django.test import TestCase, Client
from django.urls import reverse
from django.utils.timezone import now, localtime
from .models import *
from .forms import *
from datetime import timedelta

# ------------------------------------------------------
# ALL MODELS.PY RELATED TESTS:
# ------------------------------------------------------
class UserModelTest(TestCase):
    # Initialise test user account; ensure saved correctly in db
    def test_create_user(self):
        user = User.objects.create_user(username='testuser', password='testpass123', user_type='player')
        # Assert all values are valid/as expected:
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.user_type, 'player')

    def test_create_superuser(self):
        # Initialise test superuser account; ensure saved correctly in db
        admin_user = User.objects.create_superuser(username='admin', password='adminpass123')
        # Assert all values are valid/as expected:
        self.assertEqual(admin_user.username, 'admin')
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_staff)

    def test_user_profile_creation(self):
        # Initialise test profile; ensure saved correctly in db
        # Create new user:
        user = User.objects.create_user(username='testuser', password='testpass123', user_type='player')
        # Get profile (created automatically on user creation):
        profile = Profile.objects.get(user=user)
        # Assert all values are valid/as expected:
        self.assertEqual(profile.user.username, 'testuser')
        self.assertEqual(profile.score, 0)
        self.assertEqual(profile.bio, '')
        self.assertFalse(profile.profile_picture.name)

class UserLoginStreakTest(TestCase):
    # Generate user for test purposes:
    def setUp(self):
        self.user = User.objects.create_user(username='testuser2', password='testpass123', user_type='player')
        self.profile = Profile.objects.get(user=self.user)

    # Streak on account creation must equal 1:
    def test_initial_login_streak(self):
        # Login date None = new account:
        self.user.last_login_date = None
        self.user.calc_login_streak()
        self.user.refresh_from_db()
        # Assert streak now equals 1; first day of account existing:
        self.assertEqual(self.user.login_streak, 1)

    # Logging in the next day must increment the streak by 1:
    def test_consecutive_day_login_increments_streak(self):
        # Set last login date to day before current:
        self.user.last_login_date = localtime(now()).date() - timedelta(days=1)
        # Get current login streak:
        current_streak = self.user.login_streak
        self.user.save()
        # Calculate new login streak:
        self.user.calc_login_streak()
        self.user.refresh_from_db()
        # Assert streak is now 1 higher than previous:
        self.assertEqual(self.user.login_streak, current_streak + 1)

    # Logging in non-consecutively should reset streak to 1:
    def test_non_consecutive_day_resets_streak(self):
        # Set last login date to 2 days before current:
        self.user.last_login_date = localtime(now()).date() - timedelta(days=2)
        # Calculate login streak; no streak active:
        self.user.calc_login_streak()
        self.user.refresh_from_db()
        # Assert streak set to 1:
        self.assertEqual(self.user.login_streak, 1)

    # Multiple logins per day should not increment streak:
    def test_multiple_logins_dont_increase_streak(self):
        # Set last login date to current date:
        self.user.last_login_date = localtime(now()).date()
        initial_streak = self.user.login_streak
        # Calculate login streak; streak should not change.
        self.user.calc_login_streak()
        self.user.refresh_from_db()
        # Assert streak equal to initial streak before calc:
        self.assertEqual(self.user.login_streak, initial_streak)

    # Ensure reward given when 7 day login streak achieved:
    def test_reward_given_on_seven_day_streak(self):
        # Get current score of user:
        current_score = self.profile.score
        # Set last login date to day before current: 
        self.user.last_login_date = localtime(now()).date() - timedelta(days=1)
        # Initialise user's streak as 6:
        self.user.login_streak = 6
        self.user.save()
        # Calc login streak; 6 + 1 = 7, should reward user.
        self.user.calc_login_streak()
        self.profile.refresh_from_db()
        # Assert user has been rewarded:
        self.assertEqual(self.profile.score, current_score + 100)

    # Ensure correct reward given:
    def test_reward_user_adds_score(self):
        # Get current score, reward user:
        current_score = self.profile.score
        self.user.reward_user()
        self.profile.refresh_from_db()
        # Assert reward given:
        self.assertEqual(self.profile.score, current_score + 100) # PLACEHOLDER REWARD: CHANGE IF REWARD GIVEN CHANGES.

    # Ensure rewarding user resets streak to 0:
    def test_reward_user_resets_streak(self):
        # Initialise user's streak as 7, reward user:
        self.user.login_streak = 7
        self.user.reward_user()
        self.user.refresh_from_db()
        # Assert streak has been reset to 0:
        self.assertEqual(self.user.login_streak, 0)

class TeamModelTest(TestCase):
    # Generate 2 users & team for test purposes:
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password123') # user 1 created to be owner of test team.
        self.user2 = User.objects.create_user(username='user2', password='password123') # user 2 created to join/leave team.
        self.team = Team.objects.create(name='Test Team', team_owner=self.user1)

    def test_add_member(self):
        self.team.add_member(self.user2)
        # Assert user2 has been added to team:
        self.assertIn(self.user2, self.team.members.all())

    def test_remove_member(self):
        self.team.add_member(self.user2)
        self.team.remove_member(self.user2)
        # Assert user2 is not in team:
        self.assertNotIn(self.user2, self.team.members.all())

class MissionModelTest(TestCase):
    # Generate user and mission for test purposes:
    def setUp(self):
        self.user = User.objects.create_user(username='missionuser', password='password123')
        self.mission = Mission.objects.create(name='Test Mission', points=10, mission_type='daily')

    def test_user_mission_creation(self):
        # Create UserMission object:
        user_mission = UserMission.objects.create(user=self.user, mission=self.mission)
        # Assert user and mission are defined in UserMission object:
        self.assertEqual(user_mission.user, self.user)
        self.assertEqual(user_mission.mission, self.mission)

    def test_user_mission_completion(self):
        # Create UserMission object:
        user_mission = UserMission.objects.create(user=self.user, mission=self.mission)
        # Set mission as completed:
        user_mission.completed = True
        user_mission.date_completed = int(now().timestamp())
        user_mission.save()
        # Assert mission has been completed:
        self.assertTrue(user_mission.completed)

class MissionPhotoModelTest(TestCase):
    # Generate user, profile, and mission for test purposes:
    def setUp(self):
        self.user = User.objects.create_user(username='photouser', password='password123')
        self.profile = self.user.profile
        self.mission = Mission.objects.create(name='Photo Mission', points=20)

    def test_mission_photo_creation(self):
        # Create MissionPhoto object with valid image:
        photo = MissionPhoto.objects.create(profile=self.profile, mission=self.mission, image='test.jpg')
        # Assert profile, mission, image are defined in MissionPhoto object:
        self.assertEqual(photo.profile, self.profile)
        self.assertEqual(photo.mission, self.mission)
        self.assertEqual(photo.image, 'test.jpg')

# ------------------------------------------------------
# ALL FORMS.PY RELATED TESTS:
# ------------------------------------------------------
class UserRegistrationFormTest(TestCase):
    def test_form_labels(self):
        # Assert all form fields and labels initialised correctly:
        form = UserRegistrationForm()
        self.assertEqual(form.fields['username'].label, 'Username')
        self.assertEqual(form.fields['email'].label, 'Email Address')
        self.assertEqual(form.fields['password1'].label, 'Password')
        self.assertEqual(form.fields['password2'].label, 'Confirm Password')
        self.assertEqual(form.fields['user_type'].label, 'Select user type')

    def test_form_help_text(self):
        # Assert all form fields and help text initialised correctly:
        form = UserRegistrationForm()
        self.assertEqual(form.fields['username'].help_text, '')
        self.assertEqual(form.fields['email'].help_text, '')
        self.assertEqual(form.fields['password2'].help_text, '')
        self.assertEqual(form.fields['user_type'].help_text, 'DEV SETTING - REMOVE FROM OFFICIAL RELEASE.')

    def test_form_valid_data(self):
        # Initialise test form data:
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'user_type': 'player'
        }
        form = UserRegistrationForm(data=form_data)
        # Assert that data is valid, form passes:
        self.assertTrue(form.is_valid())

    def test_form_invalid_data(self):
        # Initialise test form data (invalid - no username):
        form_data = {
            'username': '',
            'email': 'invalid-email',
            'password1': 'testpass123',
            'password2': 'mismatch',
            'user_type': 'player'
        }
        form = UserRegistrationForm(data=form_data)
        # Assert that data is NOT valid, form does not pass:
        self.assertFalse(form.is_valid())

# Test user and profile must be created for every function.
# Not sure why doesn't work otherwise with setup function like other classes, but this still works.
class ProfileUpdateFormTest(TestCase):
    # Tests profile forms:
    def test_form_labels(self):
        # Assert default form fields, labels initialised correctly:
        form = ProfileUpdateForm()
        self.assertEqual(form.fields['bio'].label, 'Bio')
        self.assertEqual(form.fields['profile_picture'].label, 'Profile Picture')

    def test_form_help_text(self):
        # Assert default form fields, help text initialised correctly:
        form = ProfileUpdateForm()
        self.assertEqual(form.fields['bio'].help_text, 'Write a short bio about yourself.')
        self.assertEqual(form.fields['profile_picture'].help_text, 'Upload a profile picture.')

    def test_form_valid_data(self):
        # Create test user, profile:
        user = User.objects.create_user(username='testuser', password='testpass123', user_type='player')
        profile = Profile.objects.get(user=user)
        # Initialise test form data:
        form_data = {
            'bio': 'This is a test bio.',
            'profile_picture': None
        }
        form = ProfileUpdateForm(data=form_data, instance=profile)
        # Assert data is valid, form passes:
        self.assertTrue(form.is_valid())

    def test_form_invalid_data(self):
        # Create test user, profile:
        user = User.objects.create_user(username='invaliduser', password='testpass123', user_type='player')
        profile = Profile.objects.get(user=user)
        # Initialise test form data (invalid - bio exceeds max length):
        form_data = {
            'bio': 'x' * 600,  # Exceeding max_length (500).
            'profile_picture': None
        }
        form = ProfileUpdateForm(data=form_data, instance=profile)
        # Assert data is invalid due to error in 'bio', form does NOT pass:
        self.assertFalse(form.is_valid())
        self.assertIn('bio', form.errors)

    def test_profile_creation_signal(self):
        # Create test user:
        user = User.objects.create_user(username='signaluser', password='testpass123', user_type='player')
        # Assert profile exists for created user:
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_profile_str_method(self):
        # Create test user, profile:
        user = User.objects.create_user(username='struser', password='testpass123', user_type='player')
        profile = Profile.objects.get(user=user)
        # Assert profile str function works as intended:
        self.assertEqual(str(profile), 'struser Profile')

# ------------------------------------------------------
# ALL VIEWS.PY RELATED TESTS:
# ------------------------------------------------------
# response code 200 = success.
class ViewTests(TestCase):
    # Initialise test user, test profile:
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123', user_type='player')
        self.profile = Profile.objects.get(user=self.user)

    # Home view request success:
    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'WebApp/home.html')

    # About view request success:
    def test_about_view(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'WebApp/about.html')

    # Game view request success (requires auth):
    def test_game_view_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('game'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'WebApp/game.html')

    # Game view request fail (no auth):
    def test_game_view_unauthenticated(self):
        response = self.client.get(reverse('game'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('game')}")

    # Mission view request success (requires auth):
    def test_missions_view_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('missions'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'WebApp/missions.html')

    # Missions view request fail (no auth):
    def test_missions_view_unauthenticated(self):
        response = self.client.get(reverse('missions'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('missions')}")

    # Register view request success:
    def test_register_view(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'WebApp/register.html')

    # Login view request success:
    def test_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'WebApp/login.html')

    # Logout view request success:
    def test_logout_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

    # Profile view request success:
    def test_profile_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'WebApp/profile.html')

    # Profile update view request success:
    def test_profile_update_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile_update'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'WebApp/profile_update.html')