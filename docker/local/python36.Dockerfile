FROM centos:8

RUN dnf -y update \
 && dnf -y install \
    gcc \
	wget \
    python3 \
    postgresql \
    # packages for localdef
    glibc-locale-source \
    glibc-langpack-en \
    # packages for ssh server
    openssh-server \
    openssh-clients \
 && dnf -y clean all\
 && rm -rf /var/cache/dnf

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
RUN echo root:pass | chpasswd
CMD ["/usr/sbin/sshd", "-D"]

## Install Python 3 and OS dependencies
#RUN dnf -y install \
#	gcc \
#	wget \
#    openssl-devel \
#    bzip2-devel \
#    libffi \
#    libffi-devel \
#	postgresql \
#    make \
#    zlib-devel \
#    which \
#    sqlite-devel \
#    # packages for localdef
#    glibc-locale-source \
#    glibc-langpack-en \
#    sudo \
#    && dnf -y clean all \
#    && rm -rf /var/cache/dnf


# Download and install dockerize.
ENV DOCKERIZE_VERSION v0.6.1
RUN wget --no-verbose https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

# Set locale to en GB
RUN localedef -c -i en_GB -f UTF-8 en_GB.UTF-8

#RUN sudo dnf install python3
#RUN python3 --version
#RUN sudo alternatives --set python /usr/bin/python3
#RUN python --version

# Try this
# alternatives --install /usr/local/bin/python python /usr/local/bin/python3.7 1

# Add aliases
RUN echo "alias py3='python3.7'" >> ~/.bashrc

# Set PYTHONUNBUFFERED so output is displayed in the Docker log
ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

ENV LANG en_GB.utf-8
ENV LC_ALL en_GB.utf-8

# create virtualenv directory in WORKDIR called ".venv"
ENV PIPENV_VENV_IN_PROJECT="enabled"

##RUN python3.7 -m pip install pipenv
#RUN python -m pip install pipenv
#ADD Pipfile* ./
#RUN pipenv sync --dev
