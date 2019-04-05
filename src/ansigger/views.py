import os

from ansigger import models
from django.http import StreamingHttpResponse
from django.shortcuts import redirect, render
from utils import run_ansible_async


def index(request):
    pb = [os.path.splitext(x)[0] for x in os.listdir("playbooks/") if x.endswith(".yaml")]
    return render(request, "index.html", context=dict(playbooks=pb))


def ansible_response_generator(playbook):
    for line in run_ansible_async(playbook):
        yield line


def ansible(request, playbook):
    job = models.Job.objects.create()
    run_ansible_async(playbook, job.add_line, job.finish)
    return redirect("/job/%s" % job.id)


def job(request, job_id):
    if request.method == "GET":
        print(request.META.get("HTTP_ACCEPT"))
        if "application/x-ndjson" in request.META.get("HTTP_ACCEPT"):
            job = models.Job.objects.get(id=job_id)
            return StreamingHttpResponse(job.get_logs_as_json())
    return render(request, "job.html", context=dict(job_id=job_id))


def job_html(request, job_id):
    job = models.Job.objects.get(id=job_id)
    return StreamingHttpResponse(job.get_logs_as_html())
