FROM daocloud.io/doitian/hugo

WORKDIR /usr/src/app
COPY . /usr/src/app
RUN hugo

CMD ["hugo", "server"]
