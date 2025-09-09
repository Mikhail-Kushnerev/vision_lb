# HTTP Client Optimization Guide

## Обзор

Данная документация описывает оптимизации HTTP клиента на основе aiohttp, направленные на улучшение производительности сетевых запросов в приложении vision_lb.

## Проблемы, которые решают оптимизации

1. **Непостоянная производительность сетевых запросов** - иногда быстро, иногда медленно
2. **Увеличенная задержка при параллельных запросах** с использованием TaskGroup
3. **Неоптимальная конфигурация ClientSession** для высоконагруженных сценариев
4. **Функция `generate_event` периодически выполняется более 300ms**

## Ключевые оптимизации

### 1. Оптимизированный Connection Pooling

```python
TCPConnector(
    limit=100,                      # Общий лимит подключений
    limit_per_host=30,              # Лимит подключений на хост
    keepalive_timeout=60,           # Keep-alive таймаут 60 секунд
    enable_cleanup_closed=True,     # Автоочистка закрытых подключений
)
```

**Преимущества:**
- Переиспользование TCP соединений снижает latency
- Больший пул соединений для параллельных запросов
- Автоматическая очистка неиспользуемых соединений

### 2. DNS Кеширование

```python
TCPConnector(
    ttl_dns_cache=300,              # DNS кеш на 5 минут
    use_dns_cache=True,             # Включить DNS кеширование
    resolver=aiohttp.resolver.AsyncResolver(),  # Асинхронный resolver
)
```

**Преимущества:**
- Устранение повторных DNS запросов
- Снижение времени установки соединения
- Асинхронное разрешение DNS

### 3. TCP Оптимизации

```python
TCPConnector(
    tcp_nodelay=True,               # TCP_NODELAY для малых пакетов
    sock_family=socket.AF_INET,     # Принудительное использование IPv4
)
```

**Преимущества:**
- TCP_NODELAY отключает алгоритм Нагла, ускоряя передачу малых пакетов
- IPv4 зачастую быстрее IPv6 в локальных сетях

### 4. Настроенные Таймауты

```python
ClientTimeout(
    total=30,                       # Общий таймаут запроса
    connect=5,                      # Таймаут подключения
    sock_connect=5,                 # Таймаут сокета
    sock_read=10,                   # Таймаут чтения
)
```

**Преимущества:**
- Быстрое обнаружение недоступных сервисов
- Предотвращение зависания запросов
- Балансировка между надежностью и скоростью

### 5. Параллельные Запросы с TaskGroup

```python
async with asyncio.TaskGroup() as tg:
    tasks = [
        tg.create_task(_send_event_to_endpoint(session, endpoint, payload))
        for endpoint in endpoints
    ]

results = [task.result() for task in tasks]
```

**Преимущества:**
- Истинно параллельное выполнение HTTP запросов
- Structured concurrency с автоматической обработкой ошибок
- Значительное сокращение общего времени выполнения

## Конфигурация

Все параметры HTTP клиента настраиваются через переменные окружения:

```bash
# Connection pooling
HTTP_CONNECTION_LIMIT=100
HTTP_CONNECTION_LIMIT_PER_HOST=30

# DNS settings
HTTP_DNS_CACHE_TTL=300
HTTP_USE_DNS_CACHE=True

# Keep-alive settings
HTTP_KEEPALIVE_TIMEOUT=60
HTTP_ENABLE_CLEANUP_CLOSED=True

# Performance settings
HTTP_TCP_NODELAY=True

# Timeout settings
HTTP_TOTAL_TIMEOUT=30
HTTP_CONNECT_TIMEOUT=5
HTTP_SOCK_CONNECT_TIMEOUT=5
HTTP_SOCK_READ_TIMEOUT=10

# Event endpoints
HTTP_EVENT_ENDPOINTS=["http://analytics-service:8080/events","http://notification-service:8081/events"]
```

## Использование

### Базовое использование

```python
from services.http_client import generate_event

# Отправка событий с использованием настроек по умолчанию
results = await generate_event(
    event_type="track_created",
    event_data={"track_id": "123", "points_count": 10},
    concurrent_requests=True  # Использовать параллельные запросы
)
```

### Кастомные эндпоинты

```python
custom_endpoints = [
    "http://service1:8080/events",
    "http://service2:8081/events"
]

results = await generate_event(
    event_type="custom_event",
    event_data={"data": "value"},
    endpoints=custom_endpoints,
    concurrent_requests=True
)
```

### Последовательные запросы

```python
# Для случаев, когда важен порядок выполнения
results = await generate_event(
    event_type="ordered_event",
    event_data={"data": "value"},
    concurrent_requests=False
)
```

## Метрики производительности

Функция `generate_event` теперь возвращает детальные метрики:

```python
{
    'endpoint': 'http://service:8080/events',
    'status': 200,
    'success': True,
    'response': {...},
    'duration_ms': 45.2  # Время выполнения в миллисекундах
}
```

## Бенчмарки

Запустите бенчмарк для сравнения производительности:

```bash
cd src
python benchmark.py
```

### Ожидаемые улучшения

- **RPS (Requests Per Second):** +40-60% для параллельных запросов
- **Время ответа:** -20-35% среднее время ответа
- **Стабильность:** Значительно меньше выбросов в времени ответа
- **Ресурсы:** Более эффективное использование сетевых ресурсов

## Тестирование

Запустите тесты для проверки функциональности:

```bash
cd src
python -m pytest tests/test_http_client.py -v
```

Тесты покрывают:
- Правильность конфигурации connector и timeout
- Переиспользование сессий
- Параллельные vs последовательные запросы
- Обработку ошибок
- Метрики производительности

## Интеграция в приложение

HTTP клиент автоматически интегрирован в сервис треков:

```python
# В services/track.py
async def create_track(self, points: BodySchema):
    # ... создание трека в БД ...
    
    # Автоматическая отправка события с оптимизированным клиентом
    await self._send_track_created_event(points.track_id, points.points)
```

## Жизненный цикл

HTTP клиент корректно управляется жизненным циклом FastAPI:

```python
# В main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Автоматическая очистка ресурсов при завершении
    await cleanup_http_client()
```

## Мониторинг

Для мониторинга производительности в продакшене рекомендуется:

1. Логирование метрик `duration_ms` из результатов
2. Мониторинг количества успешных/неуспешных запросов
3. Отслеживание времени ответа по перцентилям (P50, P95, P99)
4. Мониторинг утилизации connection pool

## Дальнейшие оптимизации

Для еще большего улучшения производительности можно рассмотреть:

1. **HTTP/2 поддержку** для мультиплексирования запросов
2. **Circuit breaker** для обработки недоступных сервисов
3. **Adaptive timeout** на основе исторических данных
4. **Request/response compression** для больших payload
5. **Connection warming** для критических эндпоинтов

## Устранение неполадок

### Частые проблемы

1. **TimeoutError:** Увеличьте соответствующие таймауты
2. **ConnectionError:** Проверьте доступность эндпоинтов
3. **DNS resolution errors:** Проверьте настройки DNS кеширования
4. **Too many connections:** Уменьшите connection limits

### Отладка

Включите debug логирование для aiohttp:

```python
import logging
logging.getLogger('aiohttp.client').setLevel(logging.DEBUG)
```