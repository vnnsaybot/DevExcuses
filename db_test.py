import requests
import sqlite3 


# responce = requests.get("http://127.0.0.1:8080/api/")
# print(responce.text)
json_data = {
    "author": "RoBert",
    "content": "Papa Rimski tak Skazal",
    "rating": 100,      
    "is_prime": True
}
responce = requests.post("http://127.0.0.1:8080/api/excuses", json=json_data)
print(responce.status_code)

# responce = requests.delete("http://127.0.0.1:8080/api/v2/users/4")
# print(responce.status_code)

