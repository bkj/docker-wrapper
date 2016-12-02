FROM continuumio/anaconda

MAINTAINER QCR

EXPOSE 5000

ADD ./dw-bootstrap /dw-bootstrap
RUN chmod -x /dw-bootstrap/bootstrap.sh
RUN cd /src; sh /dw-bootstrap/bootstrap.sh

ADD ./app-bootstrap /app-bootstrap
RUN chmod -x /app-bootstrap/bootstrap.sh
RUN cd /src; sh /app-bootstrap/bootstrap.sh

ADD . /src
RUN chmod -x /src/launch.sh
CMD sh /src/launch.sh