FROM daocloud.io/doitian/hugo

WORKDIR /srv/app

ENV SSH_PRIVATE_KEY= \
    COS_APPID= \
    COS_SECRET_ID= \
    COS_SECRET_KEY= \
    COS_BUCKET= \
    COS_REGION=

RUN mkdir -p /srv/app && \
  apk add --no-cache tini bash git openssh-client python py2-pip

COPY requirements.txt /srv/app
RUN pip install -r requirements.txt
COPY . /srv/app/

EXPOSE 5000  

ENTRYPOINT ["tini", "--", "./entrypoint.sh"]
CMD ["./autobuild.py"]
