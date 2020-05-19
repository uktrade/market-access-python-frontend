FROM centos:7

# SSH
RUN (cd /lib/systemd/system/sysinit.target.wants/; for i in *; do [ $i == \
    systemd-tmpfiles-setup.service ] || rm -f $i; done); \
    rm -f /lib/systemd/system/multi-user.target.wants/*;\
    rm -f /etc/systemd/system/*.wants/*;\
    rm -f /lib/systemd/system/local-fs.target.wants/*; \
    rm -f /lib/systemd/system/sockets.target.wants/*udev*; \
    rm -f /lib/systemd/system/sockets.target.wants/*initctl*; \
    rm -f /lib/systemd/system/basic.target.wants/*;\
    rm -f /lib/systemd/system/anaconda.target.wants/*;
VOLUME [ "/sys/fs/cgroup" ]
RUN yum -y install openssh-server openssh-clients \
    &&  yum -y clean all
RUN echo root:pass | chpasswd
CMD ["/usr/sbin/sshd", "-D"]

# Update OS (IUP - Inline with Upstream Stable)
# more info here - https://ius.io/
RUN yum -y install https://centos7.iuscommunity.org/ius-release.rpm \
    &&  yum -y clean all

# Install Python 3 and OS dependencies
RUN yum -y install \
	gcc \
	wget \
	python36u \
	python36u-pip \
	python36u-devel \
	postgresql \
    && yum -y clean all \
    && rm -rf /var/cache/yum


#ENV PYTHON_VERSION 3.7.2
#RUN wget --no-verbose https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz \
#    && tar -C /usr/local/bin -xzvf Python-$PYTHON_VERSION.tgz \
#    && rm Python-$PYTHON_VERSION.tgz \
#    && cd /usr/local/bin/Python-$PYTHON_VERSION \
#    && ./configure --enable-optimizations \
#    && make altinstall

# Set locale to en GB
RUN localedef -c -i en_GB -f UTF-8 en_GB.UTF-8

# Download and install dockerize.
ENV DOCKERIZE_VERSION v0.6.1
RUN wget --no-verbose https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

# Add aliases
RUN echo "alias py3='python3.6'" >> ~/.bashrc

# Set PYTHONUNBUFFERED so output is displayed in the Docker log
ENV PYTHONUNBUFFERED=1

# Create pip cache folder
ENV PIP_CACHE_FOLDER /pip-cache
RUN mkdir -p $PIP_CACHE_FOLDER

WORKDIR /usr/src/app

ENV LANG en_GB.utf-8
ENV LC_ALL en_GB.utf-8

# create virtualenv directory in WORKDIR called ".venv"
#ENV PIPENV_VENV_IN_PROJECT="enabled"

# PIP Requirements
COPY requirements*.txt ./

RUN pip3.6 install --upgrade pip
RUN pip3.6 install --upgrade setuptools
RUN pip3.6 install -r requirements.txt
