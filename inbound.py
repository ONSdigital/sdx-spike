import requests
from os import listdir
from os.path import isfile, join

folder = "./upload/bres/1"
files = {filename: join(folder, filename) for filename in listdir(folder) if isfile(join(folder, filename))}

#content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

for file, file_path in files.items():
    print(file)
    print(file_path)
    files = {'file': (file, open(file_path, 'rb'), 'application/vnd.ms-excel', {'Expires': '0'})}
    response = requests.post("http://localhost:8091/upload/1/" + file, files=files)
    print(response)


