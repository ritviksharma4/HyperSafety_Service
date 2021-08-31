import json
from os import name

# a Python object (dict):
x = {
  "John": [4],
  "Cena" : [1,2,3]
}

name_file = open("xyz.txt", "w")
name_file.write(json.dumps(x))
name_file.close()

name_file = open("xyz.txt", "r")
y = name_file.read()

y = json.loads(y)
print(y, type(y))