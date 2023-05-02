# vision_lb

API сервис построения треков на изображении по точкам

## Содержание
- [Описание](#описание)
- [Технологии](#технологии)
- [Запуск](#запуск)
- <a href="#endpoints">Список эндпоинтов</a>
- [Авторы](#авторы)

## Описание

Сервис, развёрнутый в **Docker**, предлагает две ручки:
- задание координат точек по осям X, Y, а также `id` трека;
- построение трека на входном изображении.

## Технологии
- Python
- FastAPI
- PostgreSQL
- Docker
- Nginx

## Запуск

- Из главной директории выполните команду:

    ```
    make run
    ```

- или перейдите в директорию `docker_app/` и соберите образы:

    ```docker
    docker-compose -f docker-compose.prod.yml up -d --build
    ```


Сервер стартует по адресу http://127.0.0.1.  
Дока http://127.0.0.1/api/openapi

<details>
  <summary>
    <h2 id="endpoints">Список эндпоинтов</h2>
  </summary>

1. Задание параметров трека

```
POST /track/api/v1/set-points
Content-Type: application/json
```

**Request Body**
```json
{
  "track_id": <UUID>,
  "points": [
    {
      "x": <float>,
      "y": <float>
    }
  ]
}
```

2. Отрисовка трека

```
POST /track/api/v1/plot
Content-Type: multipart/form-data
```

**Request Body**
```
track_id = <UUID>
image = <image.png>
```

</details>

## Авторы

[Mikhail Kushnerev](https://github.com/Mikhail-Kushnerev)  

[На верх](#visionlb)