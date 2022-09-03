from __future__ import annotations
import sys
from typing import List, TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from .server import Server

__initialized: bool
log_last_update: float
log_content: List[str]
server: Optional[Server]

def init():
    global __initialized
    global log_content
    global log_last_update
    global server

    thismodule = sys.modules[__name__]
    if hasattr(thismodule, "__initialized") and __initialized:
        return
    else:
        __initialized = True

    log_content = []
    log_last_update = 0
    server = None
