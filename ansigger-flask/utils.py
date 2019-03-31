import datetime
import subprocess
import threading
from queue import Empty, Queue


def read_to_queue(stream, queue, kind):
    for line in iter(stream.readline, b""):
        now = datetime.datetime.now()
        queue.put(dict(timestamp=now, kind=kind, line=line.rstrip()))


def run_ansible(playbook):
    process = subprocess.Popen(
        [f"./playbooks/{playbook}.yaml"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        shell=True,
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
                output = queue.get(timeout=0.5)

            except Empty:
                continue

            if not output:
                continue
            yield output
    finally:
        out.join()
        err.join()
