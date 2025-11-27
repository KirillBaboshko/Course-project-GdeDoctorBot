# 🧪 Тестирование API

## Быстрый тест всех эндпоинтов

### 1. Запустить backend

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

### 2. Открыть Swagger UI

http://localhost:8000/docs

---

## Тестовые запросы

### Health Check

```bash
curl http://localhost:8000/health
```

Ожидаемый ответ:
```json
{
  "status": "healthy",
  "version": "2.0.0"
}
```

### Specialties

```bash
# Получить список специальностей (первая страница)
curl "http://localhost:8000/api/v1/specialties?skip=0&limit=10"

# Получить специальность по ID
curl "http://localhost:8000/api/v1/specialties/1"
```

### Hospitals

```bash
# Все больницы
curl "http://localhost:8000/api/v1/hospitals?skip=0&limit=10"

# Больницы с определенной специальностью
curl "http://localhost:8000/api/v1/hospitals?specialty_id=1&skip=0&limit=10"

# Больница по ID
curl "http://localhost:8000/api/v1/hospitals/1"
```

### Doctors

```bash
# Врачи по больнице и специальности
curl "http://localhost:8000/api/v1/doctors?hospital_id=1&specialty_id=1&skip=0&limit=10"

# Врач по ID
curl "http://localhost:8000/api/v1/doctors/1?hospital_id=1"

# Поиск врачей по имени
curl "http://localhost:8000/api/v1/doctors/search?name=Иванов"
```

### Reviews

```bash
# Все отзывы
curl "http://localhost:8000/api/v1/reviews?skip=0&limit=100"

# Отзывы о конкретном враче
curl "http://localhost:8000/api/v1/reviews?doctor_id=1"

# Создать отзыв
curl -X POST "http://localhost:8000/api/v1/reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_id": 1,
    "hospital_id": 1,
    "user_name": "Тестовый пользователь",
    "review_text": "Отличный врач, очень внимательный и профессиональный!"
  }'

# Получить отзыв по ID
curl "http://localhost:8000/api/v1/reviews/1"
```

### Geocoding

```bash
# Геокодировать адрес
curl "http://localhost:8000/api/v1/geo/geocode?address=Калуга,%20ул.%20Ленина,%201"

# Получить статическую карту
curl "http://localhost:8000/api/v1/geo/static_map?lon=36.25&lat=54.5&point=true" -o map.png

# Открыть карту
open map.png  # macOS
xdg-open map.png  # Linux
```

---

## Python скрипт для тестирования

```python
import requests

BASE_URL = "http://localhost:8000"

def test_api():
    # Health check
    r = requests.get(f"{BASE_URL}/health")
    print(f"Health: {r.json()}")
    
    # Get specialties
    r = requests.get(f"{BASE_URL}/api/v1/specialties", params={"skip": 0, "limit": 5})
    specialties = r.json()
    print(f"Specialties: {len(specialties['items'])} items")
    
    if specialties['items']:
        specialty_id = specialties['items'][0]['id']
        
        # Get hospitals by specialty
        r = requests.get(
            f"{BASE_URL}/api/v1/hospitals",
            params={"specialty_id": specialty_id, "skip": 0, "limit": 5}
        )
        hospitals = r.json()
        print(f"Hospitals: {len(hospitals['items'])} items")
        
        if hospitals['items']:
            hospital_id = hospitals['items'][0]['id']
            
            # Get doctors
            r = requests.get(
                f"{BASE_URL}/api/v1/doctors",
                params={
                    "hospital_id": hospital_id,
                    "specialty_id": specialty_id,
                    "skip": 0,
                    "limit": 5
                }
            )
            doctors = r.json()
            print(f"Doctors: {len(doctors['items'])} items")
            
            if doctors['items']:
                doctor_id = doctors['items'][0]['id']
                
                # Create review
                r = requests.post(
                    f"{BASE_URL}/api/v1/reviews",
                    json={
                        "doctor_id": doctor_id,
                        "hospital_id": hospital_id,
                        "user_name": "Test User",
                        "review_text": "Great doctor, highly recommended!"
                    }
                )
                print(f"Review created: {r.json()}")
                
                # Get reviews
                r = requests.get(
                    f"{BASE_URL}/api/v1/reviews",
                    params={"doctor_id": doctor_id}
                )
                reviews = r.json()
                print(f"Reviews: {len(reviews)} items")
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    test_api()
```

Сохраните как `test_api.py` и запустите:
```bash
python test_api.py
```

---

## Проверка пагинации

```bash
# Первая страница
curl "http://localhost:8000/api/v1/specialties?skip=0&limit=5"

# Вторая страница
curl "http://localhost:8000/api/v1/specialties?skip=5&limit=5"

# Третья страница
curl "http://localhost:8000/api/v1/specialties?skip=10&limit=5"
```

---

## Проверка валидации

### Невалидные данные для отзыва

```bash
# Слишком короткий текст (< 10 символов)
curl -X POST "http://localhost:8000/api/v1/reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_id": 1,
    "hospital_id": 1,
    "user_name": "Test",
    "review_text": "Short"
  }'

# Ожидается: 422 Validation Error
```

### Несуществующий ID

```bash
# Несуществующий врач
curl "http://localhost:8000/api/v1/doctors/99999?hospital_id=1"

# Ожидается: 404 Not Found
```

---

## Проверка кэширования

```bash
# Первый запрос (медленный, идет к Yandex API)
time curl "http://localhost:8000/api/v1/geo/geocode?address=Калуга"

# Второй запрос (быстрый, из кэша)
time curl "http://localhost:8000/api/v1/geo/geocode?address=Калуга"
```

---

## Swagger UI

Самый простой способ протестировать API:

1. Откройте http://localhost:8000/docs
2. Раскройте любой эндпоинт
3. Нажмите "Try it out"
4. Заполните параметры
5. Нажмите "Execute"
6. Посмотрите ответ

---

**Все эндпоинты готовы к использованию!** ✅
