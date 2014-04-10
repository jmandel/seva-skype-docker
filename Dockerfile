FROM ubuntu:12.04
MAINTAINER Josh Mandel "Joshua.Mandel@childrens.harvard.edu"

RUN echo "deb http://archive.ubuntu.com/ubuntu precise main universe" >  /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y xvfb fluxbox x11vnc dbus libasound2 libqt4-dbus libqt4-network libqtcore4 libqtgui4 libxss1 libpython2.7 libqt4-xml libaudio2 libmng1 fontconfig liblcms1 lib32stdc++6 lib32asound2 lib32z1 lib32ncurses5 lib32bz2-1.0 libc6-i386 lib32gcc1 nano curl python-gobject-2 git  python-pip
RUN curl -L http://www.skype.com/go/getskype-linux-beta-ubuntu-64 -o skype-linux-beta.deb
RUN git clone git://github.com/opensourcehacker/sevabot.git
RUN (cd sevabot && python setup.py develop)
RUN useradd -m skype
RUN apt-get install gcc-4.6-base:i386 iso-codes libasound2:i386 libasound2-plugins:i386 libasyncns0:i386 libaudio2:i386 libavahi-client3:i386 libavahi-common-data:i386 libavahi-common3:i386 libc6:i386 libcomerr2:i386 libcups2:i386 libdbus-1-3:i386 libelf1:i386 libexpat1:i386 libffi6:i386 libflac8:i386 libfontconfig1:i386 libfreetype6:i386 libgcc1:i386 libgcrypt11:i386 libglib2.0-0:i386 libglib2.0-data libgnutls26:i386 libgpg-error0:i386 libgssapi-krb5-2:i386 libgstreamer-plugins-base0.10-0:i386 libgstreamer0.10-0:i386 libice6:i386 libjack-jackd2-0:i386 libjpeg-turbo8:i386 libjpeg8:i386 libjson0:i386 libk5crypto3:i386 libkeyutils1:i386 libkrb5-3:i386 libkrb5support0:i386 liblcms1:i386 libmng1:i386 libmysqlclient18:i386 libogg0:i386 liborc-0.4-0:i386 libp11-kit0:i386 libpcre3:i386 libpng12-0:i386 libpulse0:i386 libqt4-dbus:i386 libqt4-declarative:i386 libqt4-network:i386 libqt4-script:i386 libqt4-sql:i386 libqt4-sql-mysql:i386 libqt4-xml:i386 libqt4-xmlpatterns:i386 libqtcore4:i386 libqtgui4:i386 libqtwebkit4:i386 libsamplerate0:i386 libselinux1:i386 libsm6:i386 libsndfile1:i386 libspeexdsp1:i386 libsqlite3-0:i386 libssl1.0.0:i386 libstdc++6:i386 libtasn1-3:i386 libtiff4:i386 libuuid1:i386 libvorbis0a:i386 libvorbisenc2:i386 libwrap0 libwrap0:i386 libx11-6:i386 libxau6:i386 libxcb1:i386 libxdmcp6:i386 libxext6:i386 libxi6:i386 libxml2 libxml2:i386 libxrender1:i386 libxss1:i386 libxt6:i386 libxv1:i386 sgml-base shared-mime-info tcpd uuid-runtime xml-core zlib1g:i386 
RUN dpkg -i skype-linux-beta.deb
ADD start.sh /usr/bin/start
ADD configure.sh /usr/bin/configure
RUN chmod +x /usr/bin/start /usr/bin/configure
CMD /usr/bin/configure
