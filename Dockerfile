FROM python:3.11

STOPSIGNAL SIGUSR1

RUN pip install --upgrade pip
RUN pip install PyYAML
RUN pip install requests
RUN pip install dateutils
RUN pip install lxml


RUN mkdir -p /srv/metroterm/out
COPY *.py config.yml run.sh  /srv/metroterm/
RUN chmod 755 /srv/metroterm/run.sh
WORKDIR /srv/metroterm
CMD /srv/metroterm/run.sh
