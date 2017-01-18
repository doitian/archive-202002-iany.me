#!/usr/bin/env python
# -*- coding: utf8 -*-
import os
import sys
import traceback

from flask import Flask, Response, json, jsonify
from fabric.api import env, local as run, lcd as cd
from time import time
from datetime import datetime
from qcloud_cos import CosClient, StatFileRequest, UploadFileRequest
from hashlib import sha1
from threading import Thread, Lock, current_thread

app = Flask(__name__)
env.shell = u'/bin/bash'
tzoffset = 8 * 60 * 60
bufsize = 8192
worker_mutex = Lock()
seq_id = 0
max_jobs = 3


if sys.version_info < (3,):
    _u = unicode
else:
    _u = str


def _status():
    status = None
    if os.path.exists(u'status.json'):
        with open(u'status.json', u'r') as f:
            status = json.load(f)

    if not isinstance(status, dict):
        status = {}

    jobs = status.get(u'jobs', [])
    if not isinstance(jobs, list):
        jobs = []

    status[u'jobs'] = jobs
    return status


status = _status()


def _save():
    with open('status.json', 'wb') as f:
        json.dump(status, f)


def _isoformat(ts):
    ts_with_tz = int(ts + tzoffset)
    dt = datetime.utcfromtimestamp(ts_with_tz)
    return dt.isoformat()


def _git(job):
    if os.path.exists(u'src'):
        run(u'git -C src pull')
    else:
        run(u'rm -rf src src.tmp')
        run(u'git clone git@git.coding.net:doitian/iany.me.git src.tmp')
        run(u'mv src.tmp src')

    git_log = run(u'git -C src log -1 --pretty=oneline', capture=True)
    with open('gitcommit.txt', 'w') as fd:
        fd.write(git_log)
    job['git_sha1'], job['git_message'] = git_log.split(' ', 1)
    job['steps']['git'] = True
    _save()


def _hugo(job):
    with cd(u'src'):
        run(u'rm -rf public')
        run(u'hugo')
    job[u'steps'][u'hugo'] = True
    _save()


def _cos_compare(client, bucket, cos_path, file_path=None):
    stat_req = StatFileRequest(bucket, cos_path)
    stat_resp = client.stat_file(stat_req)

    if stat_resp[u'code'] == -2:
        if stat_resp[u'message'].endswith(u'status_code:404'):
            return u'CREATED'

    if stat_resp[u'code'] != 0:
        message = stat_resp.get(
                u'message',
                u'stat failed: {}'.format(cos_path)
                )
        assert stat_resp[u'code'] == 0, message

    if file_path is None:
        file_path = os.path.abspath(u'src/public' + cos_path)
    file_stat = os.stat(file_path)

    if file_stat.st_size == stat_resp[u'data'][u'filesize']:
        file_sha1 = sha1()
        with open(file_path, u'rb') as fd:
            chunk = fd.read(bufsize)
            while chunk != '':
                file_sha1.update(chunk)
                chunk = fd.read(bufsize)
        if file_sha1.hexdigest() == stat_resp[u'data'][u'sha']:
            return u'SKIPPED'

    return u'UPDATED'


def _cos_file(job, client, bucket, cos_path, file_path=None):
    if file_path is None:
        file_path = os.path.abspath(u'src/public' + cos_path)

    compare_result = _cos_compare(client, bucket, cos_path, file_path)

    if compare_result == u'SKIPPED':
        print('SKIP ' + cos_path)
        job[u'files'][cos_path] = compare_result
        return

    print('UPLOAD ' + cos_path)
    upload_req = UploadFileRequest(bucket, cos_path, file_path, insert_only=0)
    upload_resp = client.upload_file(upload_req)

    assert upload_resp[u'code'] == 0, upload_resp.get(
            u'message',
            u'upload failed: {}'.format(cos_path)
            )

    job[u'files'][cos_path] = compare_result
    _save()


def _cos(job):
    job[u'files'] = {}

    appid = int(os.environ['COS_APPID'])
    secret_id = _u(os.environ['COS_SECRET_ID'])
    secret_key = _u(os.environ['COS_SECRET_KEY'])
    region = _u(os.environ['COS_REGION'])
    bucket = _u(os.environ['COS_BUCKET'])
    client = CosClient(appid, secret_id, secret_key, region=region)

    gitcommit_file_path = os.path.abspath(u'gitcommit.txt')
    gitcommit_compare_result = _cos_compare(
            client,
            bucket,
            u'/gitcommit.txt',
            gitcommit_file_path
            )
    if gitcommit_compare_result == u'SKIPPED':
        job[u'files'][u'/gitcommit.txt'] = 'SKIPPED'
        job['steps']['cos'] = True
        return

    top_dir = u'src/public'
    for root, _, files in os.walk(u'src/public'):
        cos_dir = root[len(top_dir):] + '/'
        for basename in files:
            cos_path = cos_dir + basename
            _cos_file(job, client, bucket, cos_path)

    _cos_file(job, client, bucket, u'/gitcommit.txt', gitcommit_file_path)
    job['steps']['cos'] = True
    _save()


def _build(job_id):
    job = {'id': job_id, 'steps': {}}
    status['jobs'].append(job)
    if len(status['jobs']) > max_jobs:
        status['jobs'] = status['jobs'][-max_jobs:]

    started_ts = time()
    job['started_at'] = _isoformat(started_ts)

    try:
        _git(job)
        _hugo(job)
        _cos(job)

    except Exception as e:
        job['status'] = 'failed'
        job['error'] = e.message
        print('ERROR: ' + str(e))
        traceback.print_exc(file=sys.stdout)
    else:
        job['status'] = 'suceeded'
    finally:
        completed_ts = time()
        job['duration'] = completed_ts - started_ts
        job['completed_at'] = _isoformat(completed_ts)

        _save()


def worker(job_id):
    global current_worker
    try:
        worker_mutex.acquire()
        current_worker = current_thread()
        _build(job_id)
    finally:
        worker_mutex.release()


@app.route('/')
def get_status():
    return Response(
            json.dumps(status, indent=2),
            mimetype=u'text/json'
            )


@app.route('/', methods=['POST'])
def start_build():
    global seq_id
    seconds = str(int(time() * 1000))
    seq_id = (seq_id + 1) % 1000
    job_id = '{}{:>03}'.format(seconds, seq_id)

    Thread(target=worker, args=(job_id,)).start()
    return jsonify(job_id=job_id)


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=False, processes=1)
