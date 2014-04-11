FROM ubuntu:12.04
MAINTAINER Josh Mandel "Joshua.Mandel@childrens.harvard.edu"

RUN echo "deb http://archive.ubuntu.com/ubuntu precise main universe" >  /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y nano curl git
RUN curl -L http://www.skype.com/go/getskype-linux-beta-ubuntu-64 -o skype-linux-beta.deb
RUN git clone git://github.com/jmandel/sevabot.git
RUN apt-get install -y python python-setuptools python-pip
RUN (cd sevabot && git checkout custom && python setup.py develop)
RUN apt-get install -y  gdebi-core
RUN gdebi --non-interactive skype-linux-beta.deb
RUN apt-get install -y xvfb fluxbox python x11vnc dbus  libpython2.7 nano curl python-gobject-2 git  python-pip gcc-4.6-base:i386 iso-codes 
ADD start.sh /usr/bin/start
ADD configure.sh /usr/bin/configure
RUN chmod +x /usr/bin/start /usr/bin/configure
CMD /usr/bin/configure
