import os
import sys
import signal
import time
import socket
import logging
import logging.config
import subprocess
from threading import Thread
from multiprocessing import Process, Queue
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import re

logger = logging.getLogger('tunnels')
MAX_DEATH_COUNT = 5
SLEEP = 3


def load_configs(fname=os.path.join(os.getcwd(), 'config.json')):
    """
    Load config parameter
    :param path: path
    :return: log
    """
    if not os.path.isfile(fname):
        return None
    return json.load(open(fname))


def get_tunnels(jdata):
    tunns = []
    i = 0
    for t in jdata['tunnels']:
        tun = {}
        tun['id'] = i
        tun['name'] = t.get('name', '')
        tun['note'] = t.get('note', '')
        tun['enabled'] = t.get('enabled', False)
        tun['cmd'] = t.get('cmd', '')
        tun['local_port'] = t.get('local_port', 0)
        tun['url'] = t.get('url', '')
        tun['num'] = 0
        i += 1
        
        tunns.append(tun)
    return tunns

def run_cmd(args, queue):
    """
    :param args: tuple
    :return: str
    """
    logger.info('Start: {}'.format(args))
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    queue.put(proc.pid)
    output, err = proc.communicate()
    logger.info('output: {}, return_code: {}, err: {}'.format(output, proc.wait(), err))
    return output
    


def start_process(args):
    """
    :param args: tuple
    :return: Process
    """
    q = Queue()
    p = Process(target=run_cmd, args=(args, q,))
    p.start()
    pid = q.get()
    logger.debug('pid: {}'.format(pid))
    return p, pid


def ping(port):
    """
    :param port: str
    :return: bool True if port is used or False if port is down
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect(('127.0.0.1', int(port)))
        s.shutdown(socket.SHUT_RD)
    except (socket.timeout, ConnectionRefusedError):
        return False
    return True


class StatusHTTPRequestHandler(BaseHTTPRequestHandler):
    thrs = []
    root_templates = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    rx_id = re.compile('.*id=(?P<id>[0-9]+)')

    def log_message(self, format, *args):
        return

    def send_headers(self, content_type):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()
    
    
    def get_id(self):
        match = self.rx_id.match(self.path)
        if match is None:
            logging.debug("enabled request without id {}".format(self.path))
            self.wfile.write(b'{}')
            return None

        th_id = int(match.group(1))
        if th_id not in self.thrs:
            logging.debug("id {} not found in threads".format(self.path))
            self.wfile.write(b'{}')
            return None
        return th_id
    

    def get_content_type(self, filename):
        p, ext = os.path.splitext(filename)
        ext = ext.lower()
        if ext == ".html":
            return "text/html"
        elif ext == ".js":
            return "text/javascript"
        elif ext == ".svg":
            return "image/svg+xml"
        elif ext == ".jpg" or ext == ".jpeg":
            return "image/jpeg"
        elif ext == ".png":
            return "image/png"
        elif ext == ".ico":
            return "image/x-icon"
        else:
            return "text/plain"
        
    
    def do_GET(self):
        if self.path == '/list':
            self.send_headers("application/json")
            text = '['
            for tun_id in self.thrs:
                tun = self.thrs[tun_id]
                text += '{'
                text += '"id":"{}",'.format(tun['id'])
                text += '"name":"{}",'.format(tun['name'])
                text += '"note":"{}",'.format(tun['note'])
                if tun['enabled'] == True:
                    text += '"enabled": true,'
                else:
                    text += '"enabled": false,'
                if ping(tun['local_port']):
                    text += '"status": true,'
                else:
                    text += '"status": false,'
                text += '"cmd":"{}",'.format(tun['cmd'])
                text += '"local_port":"{}",'.format(tun['local_port'])
                text += '"url":"{}",'.format(tun['url'])
                text += '"num":"{}"'.format(tun['num'])
                text += '},'
            text = text[:-1] + ']'
            self.wfile.write(bytes(text, 'utf8'))
            return

        elif self.path.startswith('/enabled'):
            self.send_headers("application/json")
            th_id = self.get_id()
            if th_id is not None:
                enabled = self.thrs[th_id]['enabled']
                self.wfile.write(
                    bytes('{' + '"enabled": {}'.format(enabled) + '}', 'utf8'))
                return
        
        elif self.path.startswith('/status'):
            self.send_headers("application/json")
            th_id = self.get_id()
            if th_id is not None:
                port = self.thrs[th_id]['local_port']
                is_on = ping(port)
                self.wfile.write(bytes('{' + '"on": {}'.format(is_on) + '}', 'utf8'))
                return
        
        elif self.path.startswith('/switch'):
            self.send_headers("application/json")
            th_id = self.get_id()
            if th_id is not None:
                if self.thrs[th_id]['enabled']:
                    self.thrs[th_id]['enabled'] = False
                else:
                    self.thrs[th_id]['enabled'] = True
                
                self.wfile.write(
                    bytes('{' + '"enabled": {}'.format(self.thrs[th_id]['enabled']) + '}', 'utf8'))
                return
        else:
            if self.path == '/':
                #self.send_headers("text/html")
                filename = self.root_templates + '/index.html'
            else:
                filename = self.root_templates + self.path
            if os.path.exists(filename):
                content_type = self.get_content_type(filename)
                self.send_headers(content_type)
                if content_type.startswith('image'):
                    with open(filename, 'rb') as fh:
                        self.wfile.write(fh.read())
                else:
                    with open(filename, 'r') as fh:
                        self.wfile.write(bytes(fh.read(), 'utf8'))
            

def run_http(thrs, port):
    StatusHTTPRequestHandler.thrs = thrs
    httpd = HTTPServer(('localhost', port), StatusHTTPRequestHandler)
    logging.debug('listen server localhost:{}'.format(port))
    print('open: http://localhost:{}'.format(port))
    httpd.serve_forever()


def threads_loop(thrs, max_death_count, timeout):
    death_count = 0
    max_death_count = len(thrs) * max_death_count
    while True:
        for tun_id in thrs:
            logging.debug(thrs)
            if thrs[tun_id]['enabled']:
                # ping
                logger.debug('thread {} enabled: {}, obj: {}'.format(
                    tun_id, thrs[tun_id]['enabled'], thrs[tun_id]))
                if not ping(thrs[tun_id]['local_port']):
                    logger.debug('thread cycle - enabled')
                    if thrs[tun_id]['process'] is not None:
                        thrs[tun_id]['process'].terminate()
                    death_count += 1
                else:
                    death_count = 0

                # restart or start
                if thrs[tun_id]['process'] is None or not thrs[tun_id]['process'].is_alive():
                    thrs[tun_id]['process'], thrs[tun_id]['pid'] = start_process(
                        thrs[tun_id]['cmd'].split(' '))
                    logger.debug('started process: {}'.format(
                        thrs[tun_id]['name']))
            else:
                # not enabled - terminate
                logger.debug('thread {} enabled: {}, obj: {}'.format(
                    tun_id, thrs[tun_id]['enabled'], thrs[tun_id]))
                if thrs[tun_id]['process'] is not None and thrs[tun_id]['process'].is_alive():
                    logger.debug('thread cycle - not enabled')
                    logger.debug('terminate: {}'.format(thrs[tun_id]))
                    pid = thrs[tun_id]['pid']
                    os.kill(pid, signal.SIGTERM)
                    thrs[tun_id]['process'].terminate()
                    logger.debug('process {} stoped, pid: {}'.format(
                        thrs[tun_id]['name'], pid))
            thrs[tun_id]['num'] += 1

        if death_count >= max_death_count:
            logger.info('exceeded death count!')
            return -1
        time.sleep(SLEEP)

def print_help():
    print("usage:")
    print("  {} - for run with default config".format(sys.argv[0]))
    print("  {} [path-to-config-file] - for run with custom config".format(sys.argv[0]))
    print("  {} [-h|--help] - print this help".format(sys.argv[0]))


def main():
    """
    Enter point
    :return:
    """
    port = 8000
    os.makedirs('logs', exist_ok=True)
    tun_id = 0
    threads = {}
    if len(sys.argv) >= 2:
        if sys.argv[1].lower() == '-h' or sys.argv[1].lower() == '--h':
            print_help()
            return 0
        else:
            jconf = load_configs(sys.argv[1])
    else:
        jconf = load_configs()
    
    port = int(jconf.get('ui_port', 8000))
    max_death_count = int(jconf.get('max_death_count', 5))
    timeout = int(jconf.get('timeout', 3))
    loging_conf = jconf['logging_conf']
    logging.config.dictConfig(loging_conf)
    
    
    tunns = get_tunnels(jconf)
    for tunnel in tunns:
        if tunnel['enabled']:
            tunnel['process'], tunnel['pid'] = start_process(
                tunnel['cmd'].split(' '))
        else:
            tunnel['process'] = None
        threads[tun_id] = tunnel
        tun_id += 1

    th_http = Thread(target=run_http, args=(threads, port))
    th_http.start()
    time.sleep(1)
    threads_loop(threads, max_death_count, timeout)

if __name__ == '__main__':
    main()
