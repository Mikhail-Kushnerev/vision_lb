"""Тесты для оптимизированного HTTP клиента."""

import asyncio
import time
import pytest
from unittest.mock import AsyncMock, patch
from typing import Dict, Any, List

from services.http_client import (
    OptimizedHTTPClient,
    generate_event,
    get_http_client,
    cleanup_http_client
)


@pytest.fixture
async def http_client():
    """Фикстура для создания HTTP клиента."""
    client = OptimizedHTTPClient()
    yield client
    await client.close()


@pytest.fixture  
def mock_endpoints():
    """Фикстура с тестовыми эндпоинтами."""
    return [
        "http://test-service-1:8080/events",
        "http://test-service-2:8081/events", 
        "http://test-service-3:8082/events",
    ]


class TestOptimizedHTTPClient:
    """Тесты для оптимизированного HTTP клиента."""
    
    def test_connector_configuration(self):
        """Тест настроек TCPConnector."""
        from config.settings import HTTP_CLIENT_SETTINGS
        
        client = OptimizedHTTPClient()
        connector = client._create_connector()
        
        # Проверяем ключевые настройки производительности
        assert connector._limit == HTTP_CLIENT_SETTINGS.connection_limit, "Лимит подключений из конфигурации"
        assert connector._limit_per_host == HTTP_CLIENT_SETTINGS.connection_limit_per_host, "Лимит на хост из конфигурации"
        assert connector._ttl_dns_cache == HTTP_CLIENT_SETTINGS.dns_cache_ttl, "DNS кеш TTL из конфигурации"
        assert connector._use_dns_cache == HTTP_CLIENT_SETTINGS.use_dns_cache, "DNS кеш из конфигурации"
        assert connector._keepalive_timeout == HTTP_CLIENT_SETTINGS.keepalive_timeout, "Keep-alive из конфигурации"
        assert connector._tcp_nodelay == HTTP_CLIENT_SETTINGS.tcp_nodelay, "TCP_NODELAY из конфигурации"
        
    def test_timeout_configuration(self):
        """Тест настроек таймаута."""
        from config.settings import HTTP_CLIENT_SETTINGS
        
        client = OptimizedHTTPClient()
        timeout = client._create_timeout()
        
        assert timeout.total == HTTP_CLIENT_SETTINGS.total_timeout, "Общий таймаут из конфигурации"
        assert timeout.connect == HTTP_CLIENT_SETTINGS.connect_timeout, "Таймаут подключения из конфигурации"
        assert timeout.sock_connect == HTTP_CLIENT_SETTINGS.sock_connect_timeout, "Таймаут сокета из конфигурации"
        assert timeout.sock_read == HTTP_CLIENT_SETTINGS.sock_read_timeout, "Таймаут чтения из конфигурации"
    
    async def test_session_reuse(self, http_client):
        """Тест переиспользования сессии."""
        session1 = await http_client.get_session()
        session2 = await http_client.get_session()
        
        assert session1 is session2, "Сессия должна переиспользоваться"
    
    async def test_session_recreation_after_close(self, http_client):
        """Тест пересоздания сессии после закрытия."""
        session1 = await http_client.get_session()
        await http_client.close()
        
        session2 = await http_client.get_session()
        assert session1 is not session2, "После закрытия должна создаваться новая сессия"


class TestGenerateEvent:
    """Тесты для функции generate_event."""
    
    @pytest.mark.asyncio
    async def test_sequential_requests(self, mock_endpoints):
        """Тест последовательной отправки запросов."""
        event_data = {"test": "data"}
        
        with patch('services.http_client._send_event_to_endpoint') as mock_send:
            mock_send.return_value = {
                'endpoint': 'test',
                'status': 200,
                'success': True,
                'response': {},
                'duration_ms': 100
            }
            
            results = await generate_event(
                event_type="test_event",
                event_data=event_data,
                endpoints=mock_endpoints,
                concurrent_requests=False
            )
            
            assert len(results) == len(mock_endpoints), "Должны быть результаты для всех эндпоинтов"
            assert mock_send.call_count == len(mock_endpoints), "Должно быть вызовов по количеству эндпоинтов"
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, mock_endpoints):
        """Тест параллельной отправки запросов."""
        event_data = {"test": "data"}
        
        with patch('services.http_client._send_event_to_endpoint') as mock_send:
            mock_send.return_value = {
                'endpoint': 'test',
                'status': 200, 
                'success': True,
                'response': {},
                'duration_ms': 100
            }
            
            start_time = time.time()
            
            results = await generate_event(
                event_type="test_event",
                event_data=event_data,
                endpoints=mock_endpoints,
                concurrent_requests=True
            )
            
            end_time = time.time()
            
            assert len(results) == len(mock_endpoints), "Должны быть результаты для всех эндпоинтов"
            # Параллельное выполнение должно быть быстрее последовательного
            assert end_time - start_time < 1.0, "Параллельные запросы должны выполняться быстро"
    
    @pytest.mark.asyncio
    async def test_default_endpoints_from_config(self):
        """Тест использования эндпоинтов по умолчанию из конфигурации."""
        from config.settings import HTTP_CLIENT_SETTINGS
        
        event_data = {"test": "data"}
        
        with patch('services.http_client._send_event_to_endpoint') as mock_send:
            mock_send.return_value = {
                'endpoint': 'test',
                'status': 200,
                'success': True,
                'response': {},
                'duration_ms': 100
            }
            
            # Не передаем endpoints, должны использоваться из конфигурации
            results = await generate_event(
                event_type="test_event",
                event_data=event_data,
                concurrent_requests=True
            )
            
            # Проверяем что использовались эндпоинты из конфигурации
            expected_calls = len(HTTP_CLIENT_SETTINGS.event_endpoints)
            assert mock_send.call_count == expected_calls, f"Должно быть {expected_calls} вызовов"
    
    @pytest.mark.asyncio
    async def test_performance_comparison(self, mock_endpoints):
        """Тест сравнения производительности параллельных vs последовательных запросов."""
        event_data = {"test": "data"}
        
        async def slow_mock_send(*args, **kwargs):
            await asyncio.sleep(0.1)  # Эмуляция сетевой задержки
            return {
                'endpoint': 'test',
                'status': 200,
                'success': True,
                'response': {},
                'duration_ms': 100
            }
        
        with patch('services.http_client._send_event_to_endpoint', side_effect=slow_mock_send):
            # Последовательные запросы
            start_sequential = time.time()
            await generate_event(
                event_type="test_event",
                event_data=event_data,
                endpoints=mock_endpoints,
                concurrent_requests=False
            )
            sequential_time = time.time() - start_sequential
            
            # Параллельные запросы
            start_concurrent = time.time()
            await generate_event(
                event_type="test_event", 
                event_data=event_data,
                endpoints=mock_endpoints,
                concurrent_requests=True
            )
            concurrent_time = time.time() - start_concurrent
            
            # Параллельные запросы должны быть значительно быстрее
            assert concurrent_time < sequential_time * 0.8, (
                f"Параллельные запросы ({concurrent_time:.3f}s) должны быть быстрее "
                f"последовательных ({sequential_time:.3f}s)"
            )
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_endpoints):
        """Тест обработки ошибок."""
        event_data = {"test": "data"}
        
        with patch('services.http_client._send_event_to_endpoint') as mock_send:
            mock_send.side_effect = Exception("Network error")
            
            # Функция не должна падать при ошибках
            results = await generate_event(
                event_type="test_event",
                event_data=event_data,
                endpoints=mock_endpoints[:1],  # Один эндпоинт для простоты
                concurrent_requests=True
            )
            
            assert len(results) == 1, "Должен быть результат даже при ошибке"


class TestPerformanceMetrics:
    """Тесты производительности и метрик."""
    
    @pytest.mark.asyncio
    async def test_connection_reuse(self):
        """Тест переиспользования соединений."""
        client = OptimizedHTTPClient()
        
        try:
            session1 = await client.get_session()
            session2 = await client.get_session()
            
            # Проверяем, что используется та же сессия
            assert session1 is session2, "Сессия должна переиспользоваться"
            
            # Проверяем настройки connector
            connector = session1.connector
            assert hasattr(connector, '_limit'), "Connector должен иметь лимиты"
            assert connector._limit == 100, "Лимит соединений должен быть настроен"
            
        finally:
            await client.close()
    
    @pytest.mark.asyncio
    async def test_dns_caching(self):
        """Тест DNS кеширования."""
        client = OptimizedHTTPClient()
        
        try:
            session = await client.get_session()
            connector = session.connector
            
            assert connector._use_dns_cache is True, "DNS кеширование должно быть включено"
            assert connector._ttl_dns_cache == 300, "TTL DNS кеша должен быть 300 секунд"
            
        finally:
            await client.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])