FROM ubuntu:trusty
MAINTAINER Nikolai Kordulla kordulla@googlemail.com

ENV DEBIAN_FRONTEND noninteractive
# install add-apt-repository for php5.6
RUN apt-get update && apt-get install -y python-software-properties software-properties-common

RUN apt-get update && \
  apt-get -y --force-yes install supervisor git curl

RUN apt-get update && apt-get -y --force-yes install mysql-server-5.6

# ADD startScripts
ADD start-mysqld.sh /start-mysqld.sh
ADD run.sh /run.sh
RUN chmod 755 /*.sh
ADD mycnf_confd.cnf /etc/mysql/conf.d/my.cnf

#configuring the timezone
RUN rm -rf /etc/timezone
ADD timezone /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata



# install python tornado for getting the performance
RUN apt-get update && apt-get -y install wget python-setuptools python-dev build-essential python3-pip libmysqlclient-dev \
  && pip3 install tornado && pip3 install torndb && pip3 install mysqlclient \
  && pip3 install mock \
  && cd / && wget https://raw.githubusercontent.com/bdarnell/torndb/master/torndb.py && mv torndb.py /usr/local/lib/python3.4/dist-packages/torndb.py

VOLUME  ["/src/fhrdb"]
EXPOSE 80 9200 5044
CMD /run.sh

