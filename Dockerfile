FROM daocloud.io/doitian/hugo

WORKDIR /srv/app

ENV SSH_PRIVATE_KEY= \
    COS_APPID= \
    COS_SECRET_ID= \
    COS_SECRET_KEY= \
    COS_BUCKET= \
    COS_REGION=

RUN mkdir -p /srv/app && \
  apk add --no-cache \
    tini bash git openssh-client python py2-pip \
    gcc python2-dev musl-dev libffi-dev openssl-dev

RUN mkdir -p /root/.ssh && chmod 750 /root/.ssh && touch /root/.ssh/known_hosts && ssh-keyscan -t rsa git.coding.net >> /root/.ssh/known_hosts

COPY requirements.txt /srv/app
RUN pip install -r requirements.txt
COPY . /srv/app/

EXPOSE 5000  

ENTRYPOINT ["/sbin/tini", "-g", "--", "./entrypoint.sh"]
CMD ["./autobuild.py"]

