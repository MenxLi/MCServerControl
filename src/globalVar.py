

import sys
from typing import Callable, List, Any

__initialized: bool
log_last_update: float
log_content: List[str]
server_cmd_entry: Callable[[str], Any]

def init():
    global __initialized
    global log_content
    global log_last_update
    global server_cmd_entry

    thismodule = sys.modules[__name__]
    if hasattr(thismodule, "__initialized") and __initialized:
        return
    else:
        __initialized = True

    log_content = []
    log_last_update = 0
    server_cmd_entry = lambda x: print("Server action enty not set.")
