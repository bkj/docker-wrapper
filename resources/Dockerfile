FROM continuumio/anaconda

MAINTAINER QCR

ADD . /src

EXPOSE 5000

RUN chmod -x /src/docker-wrapper-bootstrap.sh
RUN cd /src; sh /src/docker-wrapper-bootstrap.sh

RUN chmod -x /src/bootstrap.sh
RUN cd /src; sh /src/bootstrap.sh

RUN chmod -x /src/launch.sh
CMD sh /src/launch.sh