from typing import Callable, Any, Union, Awaitable, Type, Optional
from asyncio import to_thread, iscoroutinefunction
import asyncio

from nonebot.drivers import (
    Request,
    Response,
    ASGIMixin,
    WebSocket,
    HTTPServerSetup,
    HTTPClientMixin,
    WebSocketServerSetup
)

from .utils import log
from .event import OfficalEvent
from .exception import OfficialReplyError


class OfficialReplyResult:
    """ 公众号被动回复内容储存 """

    def __init__(self) -> None:
        self._futures: dict[int, asyncio.Future] = {}

    def set_resp(self, event_id: str, resp: Response) -> None:
        """ 设置响应 """
        if future := self._futures.get(event_id):
            future.set_result(resp)
        else:
            raise OfficialReplyError()

    async def get_resp(self, event_id: str, timeout: float) -> Response:
        """ 获取响应 """
        future = asyncio.get_event_loop().create_future()
        self._futures[event_id] = future
        try:
            return await asyncio.wait_for(future, timeout)
        finally:
            try:
                del self._futures[event_id]
            except:
                pass

    def clear(self, event_id: str) -> None:
        """ 清除响应 """
        if future := self._futures.get(event_id):
            try:
                future.cancel()
                del self._futures[event_id]
            except:
                pass
