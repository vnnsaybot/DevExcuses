import requests


response = requests.get("http://127.0.0.1:8081/api/excuses")
print("Все отмазки:", response.json())

print()

response = requests.get("http://127.0.0.1:8081/api/excuses", params={"profession": "frontend"})
print("Только Frontend:", response.json())

print()

resp = requests.get("http://127.0.0.1:8081/api/comments/", params={"excuse_id": 1})
print(resp.json())

# new_comment = {
#     "author": "Tester",
#     "content": "API работает отлично!",
#     "excuse": 1
# }
# post_resp = requests.post("http://127.0.0.1:8081/api/comments/", json=new_comment)
# print(f"Создан комментарий с ID: {post_resp.json().get('id')}")