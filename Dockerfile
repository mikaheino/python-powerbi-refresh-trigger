FROM python:3

ADD refresh_pbi.py /

RUN pip3 install adal requests

CMD [ "python", "./refresh_pbi.py" ]
