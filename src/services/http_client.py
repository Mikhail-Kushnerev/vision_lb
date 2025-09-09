"""Модуль для оптимизированных HTTP-клиентов."""

import asyncio
from typing import Optional, Dict, Any, List
import aiohttp
from aiohttp import ClientSession, TCPConnector, ClientTimeout
import aiohttp.resolver
import socket

from config.settings import HTTP_CLIENT_SETTINGS


class OptimizedHTTPClient:
    """Оптимизированный HTTP-клиент с настроенной конфигурацией для высокой производительности."""
    
    def __init__(self):
        self._session: Optional[ClientSession] = None
        self._connector: Optional[TCPConnector] = None
    
    def _create_connector(self) -> TCPConnector:
        """Создает оптимизированный TCPConnector с настройками из конфигурации."""
        return TCPConnector(
            # Connection pooling settings
            limit=HTTP_CLIENT_SETTINGS.connection_limit,
            limit_per_host=HTTP_CLIENT_SETTINGS.connection_limit_per_host,
            ttl_dns_cache=HTTP_CLIENT_SETTINGS.dns_cache_ttl,
            use_dns_cache=HTTP_CLIENT_SETTINGS.use_dns_cache,
            
            # Keep-alive settings  
            keepalive_timeout=HTTP_CLIENT_SETTINGS.keepalive_timeout,
            enable_cleanup_closed=HTTP_CLIENT_SETTINGS.enable_cleanup_closed,
            
            # Performance optimizations
            tcp_nodelay=HTTP_CLIENT_SETTINGS.tcp_nodelay,
            sock_family=socket.AF_INET,  # Использовать IPv4
            resolver=aiohttp.resolver.AsyncResolver(),  # Асинхронный resolver
            
            # SSL settings
            ssl=False,  # Для внутренних запросов можно отключить SSL
        )
    
    def _create_timeout(self) -> ClientTimeout:
        """Создает оптимизированные настройки таймаута из конфигурации."""
        return ClientTimeout(
            total=HTTP_CLIENT_SETTINGS.total_timeout,
            connect=HTTP_CLIENT_SETTINGS.connect_timeout,
            sock_connect=HTTP_CLIENT_SETTINGS.sock_connect_timeout,
            sock_read=HTTP_CLIENT_SETTINGS.sock_read_timeout,
        )
    
    async def get_session(self) -> ClientSession:
        """Получить или создать оптимизированную сессию."""
        if self._session is None or self._session.closed:
            self._connector = self._create_connector()
            self._session = ClientSession(
                connector=self._connector,
                timeout=self._create_timeout(),
                headers={
                    'User-Agent': 'VisionLB/1.0',
                    'Connection': 'keep-alive'
                },
                # Дополнительные настройки
                connector_owner=True,
                read_timeout=None,  # Используем таймауты из ClientTimeout
                conn_timeout=None,
            )
        
        return self._session
    
    async def close(self):
        """Закрыть сессию и коннектор."""
        if self._session and not self._session.closed:
            await self._session.close()
        if self._connector:
            await self._connector.close()
    
    async def __aenter__(self):
        return await self.get_session()
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# Глобальный экземпляр клиента
_http_client = OptimizedHTTPClient()


async def get_http_client() -> ClientSession:
    """Получить оптимизированный HTTP клиент."""
    return await _http_client.get_session()


async def generate_event(
    event_type: str,
    event_data: Dict[str, Any],
    endpoints: Optional[List[str]] = None,
    concurrent_requests: bool = True
) -> List[Dict[str, Any]]:
    """
    Генерирует и отправляет события на указанные эндпоинты.
    
    Args:
        event_type: тип события
        event_data: данные события
        endpoints: список эндпоинтов для отправки (если None, используются из конфигурации)
        concurrent_requests: использовать параллельные запросы
        
    Returns:
        Список результатов отправки
    """
    if endpoints is None:
        endpoints = HTTP_CLIENT_SETTINGS.event_endpoints
    
    if not endpoints:
        return []
        
    session = await get_http_client()
    
    payload = {
        'event_type': event_type,
        'data': event_data,
        'timestamp': asyncio.get_event_loop().time()
    }
    
    results = []
    
    if concurrent_requests and len(endpoints) > 1:
        # Используем TaskGroup для параллельных запросов
        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(_send_event_to_endpoint(session, endpoint, payload))
                for endpoint in endpoints
            ]
        
        results = [task.result() for task in tasks]
    else:
        # Последовательная отправка
        for endpoint in endpoints:
            result = await _send_event_to_endpoint(session, endpoint, payload)
            results.append(result)
    
    return results


async def _send_event_to_endpoint(
    session: ClientSession, 
    endpoint: str, 
    payload: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Отправляет событие на конкретный эндпоинт.
    
    Args:
        session: HTTP сессия
        endpoint: URL эндпоинта
        payload: данные для отправки
        
    Returns:
        Результат отправки
    """
    start_time = asyncio.get_event_loop().time()
    
    try:
        async with session.post(
            endpoint,
            json=payload,
            headers={'Content-Type': 'application/json'}
        ) as response:
            response_data = await response.json()
            duration_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return {
                'endpoint': endpoint,
                'status': response.status,
                'success': response.status < 400,
                'response': response_data,
                'duration_ms': round(duration_ms, 2)
            }
    
    except asyncio.TimeoutError:
        duration_ms = (asyncio.get_event_loop().time() - start_time) * 1000
        return {
            'endpoint': endpoint,
            'status': None,
            'success': False,
            'error': 'Request timeout',
            'duration_ms': round(duration_ms, 2)
        }
    
    except Exception as e:
        duration_ms = (asyncio.get_event_loop().time() - start_time) * 1000
        return {
            'endpoint': endpoint,
            'status': None,
            'success': False,
            'error': str(e),
            'duration_ms': round(duration_ms, 2)
        }


async def cleanup_http_client():
    """Очистка ресурсов HTTP клиента."""
    await _http_client.close()