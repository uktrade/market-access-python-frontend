FROM centos:8

RUN dnf -y update \
 && dnf -y install \
    gcc \
	wget \
    postgresql \
    # packages so python can be compiled
	nano \
	make \
	which \
    openssl-devel \
    bzip2-devel \
	zlib-devel \
    libffi \
	libffi-devel \
    # packages for pytest
    sqlite-devel \
    # packages for localdef
    glibc-locale-source \
    glibc-langpack-en \
    # packages for ssh server
    openssh-server \
    openssh-clients \
 && dnf -y clean all \
 && rm -rf /var/cache/dnf

ENV PYTHON_VERSION 3.7.9
RUN wget --no-verbose https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz \
    && tar -C /usr/local/bin -xzvf Python-$PYTHON_VERSION.tgz \
    && rm Python-$PYTHON_VERSION.tgz \
    && cd /usr/local/bin/Python-$PYTHON_VERSION \
    && ./configure --enable-optimizations \
    && make altinstall

RUN ln -s /usr/local/bin/python3.7 /usr/bin/python \
 && ln -s /usr/local/bin/pip3.7 /usr/bin/pip

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

# Download and install dockerize.
ENV DOCKERIZE_VERSION v0.6.1
RUN wget --no-verbose https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

# Set locale to en GB
RUN localedef -c -i en_GB -f UTF-8 en_GB.UTF-8
ENV LANG en_GB.utf-8
ENV LC_ALL en_GB.utf-8

# Set PYTHONUNBUFFERED so output is displayed in the Docker log
ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.0.10

WORKDIR /usr/src/app

# Poetry commands reference https://python-poetry.org/docs/cli/#run
COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip \
 && pip install poetry==$POETRY_VERSION \
 && poetry lock \
 && poetry export --without-hashes -f requirements.txt -o requirements.txt \
 && poetry export --dev --without-hashes -f requirements.txt -o requirements-dev.txt \
 && pip install -r requirements-dev.txt
