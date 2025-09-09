#!/usr/bin/env python3
"""
Скрипт бенчмарка для демонстрации производительности оптимизированного HTTP клиента.
"""

import asyncio
import time
import statistics
from typing import List
import aiohttp
from aiohttp import ClientSession, TCPConnector, ClientTimeout

from services.http_client import OptimizedHTTPClient, generate_event


async def basic_http_client() -> ClientSession:
    """Создает базовый HTTP клиент без оптимизаций."""
    return ClientSession()


async def unoptimized_http_client() -> ClientSession:
    """Создает неоптимизированный HTTP клиент для сравнения."""
    connector = TCPConnector(
        limit=10,  # Низкий лимит
        limit_per_host=5,  # Низкий лимит на хост
        ttl_dns_cache=60,  # Короткий DNS кеш
        use_dns_cache=False,  # DNS кеш отключен
        keepalive_timeout=10,  # Короткий keep-alive
        enable_cleanup_closed=False,
        tcp_nodelay=False,  # TCP_NODELAY отключен
    )
    
    timeout = ClientTimeout(
        total=60,  # Длинный таймаут
        connect=30,
        sock_connect=30,
        sock_read=30,
    )
    
    return ClientSession(connector=connector, timeout=timeout)


class MockServer:
    """Мок-сервер для тестирования."""
    
    def __init__(self, delay: float = 0.1):
        self.delay = delay
        self.app = None
        self.runner = None
        self.site = None
        
    async def handle_event(self, request):
        """Обработчик событий."""
        await asyncio.sleep(self.delay)  # Эмулируем задержку обработки
        return aiohttp.web.json_response({"status": "ok"})
    
    async def start(self, port: int = 8080):
        """Запускает мок-сервер."""
        self.app = aiohttp.web.Application()
        self.app.router.add_post('/events', self.handle_event)
        
        self.runner = aiohttp.web.AppRunner(self.app)
        await self.runner.setup()
        
        self.site = aiohttp.web.TCPSite(self.runner, 'localhost', port)
        await self.site.start()
        
    async def stop(self):
        """Останавливает мок-сервер."""
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()


async def benchmark_requests(
    client_session: ClientSession, 
    endpoints: List[str], 
    num_requests: int = 50,
    concurrent: bool = True
) -> dict:
    """
    Бенчмарк HTTP запросов.
    
    Args:
        client_session: HTTP сессия
        endpoints: список эндпоинтов
        num_requests: количество запросов
        concurrent: использовать параллельные запросы
        
    Returns:
        Метрики производительности
    """
    payload = {
        'event_type': 'benchmark',
        'data': {'test': True},
        'timestamp': time.time()
    }
    
    durations = []
    errors = 0
    
    async def single_request(endpoint: str):
        start_time = time.time()
        try:
            async with client_session.post(endpoint, json=payload) as response:
                await response.json()
                return time.time() - start_time
        except Exception:
            nonlocal errors
            errors += 1
            return time.time() - start_time
    
    start_total = time.time()
    
    if concurrent:
        # Параллельные запросы
        tasks = []
        for _ in range(num_requests):
            for endpoint in endpoints:
                tasks.append(single_request(endpoint))
        
        durations = await asyncio.gather(*tasks, return_exceptions=True)
        durations = [d for d in durations if isinstance(d, (int, float))]
    else:
        # Последовательные запросы
        for _ in range(num_requests):
            for endpoint in endpoints:
                duration = await single_request(endpoint)
                durations.append(duration)
    
    total_time = time.time() - start_total
    
    return {
        'total_requests': len(durations) + errors,
        'successful_requests': len(durations),
        'failed_requests': errors,
        'total_time': total_time,
        'requests_per_second': (len(durations) + errors) / total_time,
        'avg_response_time': statistics.mean(durations) if durations else 0,
        'min_response_time': min(durations) if durations else 0,
        'max_response_time': max(durations) if durations else 0,
        'median_response_time': statistics.median(durations) if durations else 0,
    }


async def run_benchmark():
    """Запускает полный бенчмарк."""
    print("🚀 Запуск бенчмарка производительности HTTP клиента...")
    
    # Запускаем мок-серверы
    servers = []
    endpoints = []
    
    for i, port in enumerate([8080, 8081, 8082]):
        server = MockServer(delay=0.05)  # 50ms задержка
        await server.start(port)
        servers.append(server)
        endpoints.append(f"http://localhost:{port}/events")
    
    try:
        print(f"📡 Мок-серверы запущены на портах: {[8080, 8081, 8082]}")
        
        # Тестируем разные клиенты
        clients_to_test = [
            ("Базовый клиент", basic_http_client),
            ("Неоптимизированный клиент", unoptimized_http_client),
            ("Оптимизированный клиент", lambda: OptimizedHTTPClient().get_session()),
        ]
        
        results = {}
        
        for client_name, client_factory in clients_to_test:
            print(f"\n⚡ Тестирование: {client_name}")
            
            client = await client_factory()
            
            # Последовательные запросы
            seq_results = await benchmark_requests(
                client, endpoints, num_requests=20, concurrent=False
            )
            
            # Параллельные запросы
            par_results = await benchmark_requests(
                client, endpoints, num_requests=20, concurrent=True
            )
            
            await client.close()
            
            results[client_name] = {
                'sequential': seq_results,
                'parallel': par_results
            }
            
            print(f"  📊 Последовательные: {seq_results['requests_per_second']:.1f} req/s, "
                  f"avg: {seq_results['avg_response_time']*1000:.1f}ms")
            print(f"  📊 Параллельные: {par_results['requests_per_second']:.1f} req/s, "
                  f"avg: {par_results['avg_response_time']*1000:.1f}ms")
        
        # Показываем сравнение
        print("\n📈 РЕЗУЛЬТАТЫ БЕНЧМАРКА:")
        print("=" * 80)
        
        print(f"{'Клиент':<25} {'Тип':<15} {'RPS':<10} {'Avg(ms)':<10} {'Min(ms)':<10} {'Max(ms)':<10}")
        print("-" * 80)
        
        for client_name, client_results in results.items():
            for test_type, metrics in client_results.items():
                print(f"{client_name:<25} {test_type:<15} "
                      f"{metrics['requests_per_second']:<10.1f} "
                      f"{metrics['avg_response_time']*1000:<10.1f} "
                      f"{metrics['min_response_time']*1000:<10.1f} "
                      f"{metrics['max_response_time']*1000:<10.1f}")
        
        # Показываем улучшения
        print("\n🎯 УЛУЧШЕНИЯ ПРОИЗВОДИТЕЛЬНОСТИ:")
        print("=" * 50)
        
        optimized = results["Оптимизированный клиент"]["parallel"]
        basic = results["Базовый клиент"]["parallel"]
        unoptimized = results["Неоптимизированный клиент"]["parallel"]
        
        print(f"Оптимизированный vs Базовый:")
        print(f"  RPS улучшение: {(optimized['requests_per_second'] / basic['requests_per_second'] - 1) * 100:.1f}%")
        print(f"  Время ответа улучшение: {(1 - optimized['avg_response_time'] / basic['avg_response_time']) * 100:.1f}%")
        
        print(f"\nОптимизированный vs Неоптимизированный:")
        print(f"  RPS улучшение: {(optimized['requests_per_second'] / unoptimized['requests_per_second'] - 1) * 100:.1f}%")
        print(f"  Время ответа улучшение: {(1 - optimized['avg_response_time'] / unoptimized['avg_response_time']) * 100:.1f}%")
        
    finally:
        # Останавливаем мок-серверы
        for server in servers:
            await server.stop()
        
        print("\n✅ Бенчмарк завершен!")


if __name__ == "__main__":
    asyncio.run(run_benchmark())