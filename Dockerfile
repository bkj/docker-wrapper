FROM continuumio/anaconda

MAINTAINER QCR

ADD . /src

EXPOSE 5000

RUN chmod -x /src/build.sh
CMD sh /src/build.sh

RUN chmod -x /src/launch.sh
CMD sh /src/launch.sh