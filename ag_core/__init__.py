# Antigravity Core Engine (ag_core)
# 反重力核心引擎包初始化

from .event_logger import log_event
from .dispatcher import AsyncGlobalDispatcher

__version__ = "3.5.0"
__all__ = [
    "log_event",
    "AsyncGlobalDispatcher",
]
