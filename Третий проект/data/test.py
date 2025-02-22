from requests import get

print(get('http://localhost:5000/api/news').json())  # вернет все новости
print(get('http://localhost:5000/api/news/1').json())  # вернет 1 новость
print(get('http://localhost:5000/api/news/999').json())  # новости с id = 999 нет в базе - ошибка 404
print(get('http://localhost:5000/api/news/q').json())  # неправильный формат - ошибка 404
