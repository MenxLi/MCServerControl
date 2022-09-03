import os, argparse, string, datetime, sys, re
from typing import Callable, List, Optional
from multiprocessing import Queue
from threading import Thread
from . import globalVar
from .serverLogParser import EVENT_ALL

import tornado.ioloop
import tornado.web
import tornado.autoreload

def readLogLines() -> List[str]:
    return globalVar.log_content

def getLogTime() -> float:
    return globalVar.log_last_update

def updateLog(event_queue: Queue):
    while True:
        ev: EVENT_ALL = event_queue.get()
        globalVar.log_content.append(ev["log_line"])
        globalVar.log_last_update = ev["time"]

class RequestHandlerBase():
    get_argument: Callable
    get_cookie: Callable[[str, Optional[str]], Optional[str]]
    set_header: Callable

    def setDefaultHeader(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, PUT, DELETE, OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header("Access-Control-Expose-Headers", "*")

class LogParser:
    def __init__(self):
        ...

    def addColor(self, line: str):
        start = 0
        counter = 0
        new_line = ""
        while True:
            counter += 1
            match = re.search(r"\[[^[^\]]*\]", line[start:])
            if not match or counter > 2:
                leftout = line[start:]
                if "joined the game" in leftout:
                    leftout = f"<highlight_join>{leftout}</highlight_join>"
                elif "left the game" in leftout:
                    leftout = f"<highlight_left>{leftout}</highlight_left>"
                new_line += leftout
                break
            span = match.span()
            if counter == 1:
                # first match
                new_line += f"<cyan>{line[start + span[0]: start + span[1]]}</cyan>" 
            if counter == 2:
                new_line += f"<gray>{line[start + span[0] - 1: start + span[1]]}</gray>" 
            start = start + span[1]
        return new_line # + "|...|" + line
            

class InfoHandler(tornado.web.RequestHandler, RequestHandlerBase):
    def _getLog(self) -> str:
        content = readLogLines()
        html = string.Template("""
        <!DOCTYPE html>
        <html>
            <head>
                <title>SERVER LOG</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
            </head>
            <style>
                body {
                    background-color: #000000;
                    /* Set the size of 1em to 10px in all browsers */
                    font-size: 62.5%;
                }
                body.extraWide {font-size:85%;}
                body.wide {font-size:75%;}
                body.narrow {font-size:50%;}
                body.extraNarrow {font-size:40%;}

                p {
                    color: #ffffff;
                    line-height: 1.05;
                    margin: 1px;
                    font-family: monospace;
                }
                p:hover {
                    background-color: #333333;
                }
                cyan {
                    color: #00FFFF;
                }
                gray {
                    color: #555555;
                }
                highlight_join {
                    background-color: #ffff33;
                    color: #000000;
                }
                highlight_left {
                    /*border-bottom: 1px solid #ffff33;*/
                    color: #ffff33;
                }

            </style>
            ${body}
            <script type="text/javascript">

                // Set font size
                const viewPortWidth = window.screen.availWidth;
                console.log("Avaliable window width: " + viewPortWidth);
                const body = document.querySelector('body');

                if (viewPortWidth > 1900) {body.setAttribute('class', 'extraWide')}
                else if (viewPortWidth > 1400) {body.setAttribute('class', 'wide')}
                else if (viewPortWidth > 1000) {body.setAttribute('class', 'standard')}
                else if (viewPortWidth > 700) {body.setAttribute('class', 'narrow')}
                else {body.setAttribute('class', 'extraNarrow')}

                // Auto scroll to bottom
                window.onload = () => {
                    window.scrollTo(0, document.body.scrollHeight);
                    console.log(document.body.scrollHeight);
                }

                // Query reload
                const QUERY_INTERVAL = 7500;
                const MAX_QUERY = parseInt(3600000 / QUERY_INTERVAL);      // 1 hour
                let QUERY_COUNTER = 0;

                setInterval(updateWindow, QUERY_INTERVAL)

                function updateWindow(){
                    if (QUERY_COUNTER > MAX_QUERY){
                        return null;
                    }
                    else { QUERY_COUNTER += 1; }

                    const host = window.location.hostname;
                    const port = window.location.port;

                    let reqURL = host + ":" + port + "/info/log_time";
                    if (!reqURL.startsWith("http://")){
                        reqURL = "http://" + reqURL;
                    }

                    const xhr = new XMLHttpRequest();
                    xhr.open('GET', reqURL);
                    xhr.onreadystatechange = function() {
                        if (this.readyState === 4) {
                            if (this.status == 200){
                                const res = xhr.response;
                                const mTime = parseFloat(res);
                                const LOG_TIME = window.sessionStorage.getItem("LOG_TIME");
                                if (mTime > LOG_TIME) {
                                    window.sessionStorage.setItem('LOG_TIME', mTime);
                                    window.location.reload(true);
                                }
                            }
                        }
                    }
                    xhr.send();
                }
            </script>
        </html>
        """)
        body = ""
        line_parser = LogParser()
        for line in content[::]:
            line = line_parser.addColor(line)
            body += f'<p>{line}</p>'
        return html.substitute(body=body)

    def get(self, key):
        self.setDefaultHeader()
        if key != "log_time":
            _log(f"Get request: {key} | (ip: {self.request.remote_ip})")
        if key=="log":
            self.write(self._getLog())

        elif key=="log_time":
            #  m_time = os.path.getmtime(SERVER_LOG_FILE)
            m_time = getLogTime()
            self.write(str(m_time))

        else:
            # not implemented
            raise tornado.web.HTTPError(404)

class Application(tornado.web.Application):
    def __init__(self) -> None:
        root = os.path.dirname(__file__)
        frontend_root = os.path.join(root, "frontend")
        handlers = [
            (r'/(favicon.ico)', tornado.web.StaticFileHandler, {"path": frontend_root}),
            (r'/info/(.*)', InfoHandler)
        ]
        super().__init__(handlers)

def auto_reload_hook():
    _log("Server is auto-reloading")

def startServer(port: int, event_queue: Queue):
    """
     - log_queue: queue to receive log lines
    """
    globalVar.init()
    _log("Starting broadcast server on port %s" % port)
    app = Application()
    app.listen(port) 
    #  tornado.autoreload.add_reload_hook(auto_reload_hook)
    #  tornado.autoreload.start()

    # Start new thread listening to minecraft server event
    Thread(target = updateLog, args = (event_queue, ), daemon=True).start()

    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        print("Exit.")
        sys.exit(0)

def _log(txt: str):
    print(f"BROADCAST - {datetime.datetime.now()}: {txt}")

#  if __name__ == "__main__":
#      _description = ""
#      parser = argparse.ArgumentParser(description = _description)
#      parser.add_argument("-p", "--port", type = int, default=25566)
#      args = parser.parse_args()
#
#      startServer(args.port)
