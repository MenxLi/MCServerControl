

import sys
from typing import List

__initialized: bool
log_last_update: float
log_content: List[str]

def init():
    global __initialized
    global log_content
    global log_last_update

    thismodule = sys.modules[__name__]
    if hasattr(thismodule, "__initialized") and __initialized:
        return
    else:
        __initialized = True

    log_content = []
    log_last_update = 0
