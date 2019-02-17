import subprocess
import threading
import datetime
from queue import Queue, Empty
from multiprocessing import Pool


def read_to_queue(stream, queue, kind):
    for line in iter(stream.readline, b''):
        queue.put(
            dict(
                timestamp=datetime.datetime.now(),
                kind=kind,
                line=line.rstrip()
            )
        )


def run_ansible(playbook):
    process = subprocess.Popen(
        [f'./playbooks/{playbook}.yaml'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        shell=True
    )

    queue = Queue()
    out = threading.Thread(target=read_to_queue, args=(process.stdout, queue, "O"))
    err = threading.Thread(target=read_to_queue, args=(process.stderr, queue, "E"))
    out.daemon = True
    err.daemon = True
    out.start()
    err.start()
   
    try: 
        while process.poll() is None or not queue.empty():
            try:
                output = queue.get(timeout=.5)
        
            except Empty:
                continue
        
            if not output:
                continue
            yield output    
    finally:
        out.join()
        err.join()


