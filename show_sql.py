
from os import popen


__appName = "WebApp"
string = (popen(f'python manage.py sqlmigrate {__appName} 0001').read())

print(
    string  
    .replace(" (", " (\n")
    .replace(",", ",\n")
    .replace(";", ";\n")
)

_ = input();