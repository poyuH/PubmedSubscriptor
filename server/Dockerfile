FROM tiangolo/meinheld-gunicorn:python3.6

LABEL maintainer="Sebastian Ramirez <tiangolo@gmail.com>"

RUN wget http://download.redis.io/redis-stable.tar.gz
RUN tar xvzf redis-stable.tar.gz
RUN cd redis-stable && make && make install
RUN pip install rq
RUN pip install pymongo[srv]==3.10.0
RUN pip install beautifulsoup4==4.8.2
RUN pip install requests==2.22.0
