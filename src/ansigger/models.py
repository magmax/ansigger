from django.db import models
import uuid
import datetime
import json
import time

EPOCH = datetime.datetime(1970,1,1)


class Job(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    finished = models.BooleanField(default=False)

    def __string__(self):
        return id

    def get_logs(self):
        last_id=-1
        while True:
            for log in Log.objects.filter(job=self, id__gt=last_id).order_by('id'):
                yield log
                last_id = log.id
            time.sleep(0.2)
            if self.finished:
                break

    def get_logs_as_json(self):
        for log in self.get_logs():
            yield log.as_json()
            yield('\n')

    def add_line(self, timestamp, stream, message):
        Log.objects.create(
            job=self,
            timestamp=timestamp,
            message=message,
            stream=stream,
        )
        print(message)

    def finish(self):
        self.finished = True
        self.save()


class Log(models.Model):
    message = models.CharField(max_length=1024)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='jobs')
    timestamp = models.DateTimeField()
    stream = models.CharField(max_length=30)

    def __string__(self):
        return "%s - %s" % (self.job.id, self.message)

    def as_json(self):
        return json.dumps(dict(
            message=self.message,
            timestamp=(self.timestamp - EPOCH).total_seconds(),
            stream=self.stream,
        ))
