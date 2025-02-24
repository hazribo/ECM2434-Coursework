# ECM2434-Coursework
Group Coursework for ECM2434 Group Software Engineering Project using Python &amp; Django framework.

# Setup Guide: 
## 1. Clone the Git Repository
Open a terminal and run the following command to clone the repository:

```bash
git clone https://github.com/hazribo/ECM2434-Coursework/
```

## 2. Navigate to the Project Directory
Change into the project directory:

```bash
cd <directory of cloned repo>
```

## 3. Activate a Virtual Environment (venv)
Create a virtual environment using `venv`:

```bash
python -m venv venv
```

Activate the virtual environment:

- On **Windows** (Command Prompt):
  ```bash
  venv\Scripts\activate
  ```
- On **Mac/Linux**:
  ```bash
  source venv/bin/activate
  ```

## 4. Install Dependencies
Install the required dependencies to the virtual environment:

```bash
pip install -r requirements.txt
```

## 5. Migrate Database
Run the `migrate_database.bat` file to ensure a valid database is created for the app to use.

## 6. Run the Server
Start the server using:

```bash
python manage.py runserver
```

By default, the server will run at `http://127.0.0.1:8000/`.

## 7. Exit Venv
To exit the virtual environment, run:

```bash
deactivate
```

# How to test basic functionalities:
`http://127.0.0.1:8000/register/` - debug option for setting user type (player, game keeper, developer).

Any other tests can be found in the tests.py file.
You can run them by using:
```bash
python manage.py test
```
in the terminal in the project directory.

