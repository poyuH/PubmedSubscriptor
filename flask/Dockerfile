FROM tiangolo/meinheld-gunicorn:python3.6

LABEL maintainer="PoYu Huang <pubmedsubscription@gmail.com>"

RUN pip install flask==1.1.1

RUN pip install beautifulsoup4==4.8.2

RUN pip install pymongo[srv]==3.10.0

RUN pip install passlib==1.7.2

RUN pip install requests==2.22.0

COPY ./flaskr /app/flaskr

CMD export FLASK_APP=flaskr && flask run -h 0.0.0.0 -p 80
