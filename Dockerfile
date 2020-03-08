FROM python:3.6.10
RUN apt-get update && apt-get upgrade && apt-get install -y gettext libgettextpo-dev
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
RUN python manage.py migrate
RUN python manage.py data
RUN python manage.py compilemessages
RUN python manage.py createcachetable
RUN python manage.py collectstatic
EXPOSE 8888
CMD [ "python", "tornado_main.py" ]