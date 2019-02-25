import asyncio
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
                message=line.rstrip(),
                stream=kind,
            )
        )


def run_ansible(playbook, line_callback, end_callback):
    process = subprocess.Popen(
        [f'./playbooks/{playbook}.yaml'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        shell=True
    )

    queue = Queue()
    out = threading.Thread(
        target=read_to_queue,
        args=(process.stdout, queue, "stdout")
    )
    err = threading.Thread(
        target=read_to_queue,
        args=(process.stderr, queue, "stderr")
    )
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
            line_callback(**output)
    finally:
        out.join()
        err.join()
    end_callback()

def run_ansible_async(playbook, line_callback, end_callback):
    thread = threading.Thread(
        target=run_ansible,
        args=(playbook, line_callback, end_callback),
    )
    thread.daemon = False
    thread.start()
