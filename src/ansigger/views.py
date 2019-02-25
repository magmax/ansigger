import os
from django.shortcuts import render
from django.http import Http404
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import redirect

from ansigger import models
from utils import read_to_queue, run_ansible_async


def index(request):
    pb = [
        os.path.splitext(x)[0]
        for x in os.listdir('playbooks/')
        if x.endswith('.yaml')
    ]
    return render(request, 'index.html', context=dict(playbooks=pb))


def _ansible(request, playbook):
    if any(x in playbook for x in '/.'):
        app.logger.error(f'Invalid playbook {playbook}')
        raise(Http404())
    if f"{playbook}.yaml" not in os.listdir('playbooks/'):
        app.logger.error(f'Playbook {playbook} not found')
        raise(Http404())
    return StreamingHttpResponse(
        ansible_response_generator(playbook),
    )

def ansible_response_generator(playbook):
    for line in run_ansible(playbook):
        yield line

def ansible(request, playbook):
    job = models.Job.objects.create()
    run_ansible_async(playbook, job.add_line, job.finish)
    return redirect('/job/%s' % job.id)

def job(request, job_id):
    if request.method == 'GET':
        if 'text/html' in request.META.get('HTTP_ACCEPT'):
            return render(request, 'job.html', context=dict(job_id=job_id))
        job = models.Job.objects.get(id=job_id)
        return StreamingHttpResponse(
            job.get_logs_as_json()
        )

