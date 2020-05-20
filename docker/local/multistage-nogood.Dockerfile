FROM centos:8 as base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    # Seems to speed things up
    PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

# === BUILDER =====
FROM base as builder

# Sets utf-8 encoding for Python
ENV LANG=C.UTF-8
# Turns off writing .pyc files. Superfluous on an ephemeral container.
ENV PYTHONDONTWRITEBYTECODE=1
# Seems to speed things up
ENV PYTHONUNBUFFERED=1

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.0.5 \
    PYTHON_VERSION=3.7.6 \
    PYTHON_FILENAME=python3.7 \
    PIP_FILENAME=pip3.7 \
    DOCKERIZE_VERSION=v0.6.1

# Ensures that the python and pip executables used
# in the image will be those from our virtualenv.
ENV PATH="/venv/bin:$PATH"

# Install OS package dependencies.
# Do all of this in one RUN to limit final image size.
RUN dnf -y update \
 && dnf -y install \
    gcc \
	wget \
#    postgresql \
    # packages so python can be compiled
	make \
#	which \
    openssl-devel \
    bzip2-devel \
	zlib-devel \
    libffi \
	libffi-devel \
    # packages for pytest
    sqlite-devel \
#    # packages for localdef
#    glibc-locale-source \
#    glibc-langpack-en \
#    # packages for ssh server
#    openssh-server \
#    openssh-clients \
 && dnf -y clean all \
 && rm -rf /var/cache/dnf

# Install Dockerize
RUN wget --no-verbose https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

# Install Python
RUN wget --no-verbose https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz \
    && tar -C /usr/local/bin -xzvf Python-$PYTHON_VERSION.tgz \
    && rm Python-$PYTHON_VERSION.tgz \
    && cd /usr/local/bin/Python-$PYTHON_VERSION \
    && ./configure --enable-optimizations \
    && make altinstall

#RUN ln -s /usr/local/bin/$PYTHON_FILENAME /usr/bin/python \
# && ln -s /usr/local/bin/$PIP_FILENAME /usr/bin/pip

# Build the venv
RUN $PIP_FILENAME install "poetry==$POETRY_VERSION"
RUN $PYTHON_FILENAME -m venv --copies /venv

COPY pyproject.toml poetry.lock ./
RUN poetry update --lock
RUN poetry export --dev -f requirements.txt -o requirements.txt

RUN source /venv/bin/activate
RUN $PIP_FILENAME install --no-cache-dir -r requirements.txt

RUN python --version
RUN $PYTHON_FILENAME --version

#RUN poetry export -f requirements.txt | /venv/bin/pip install -r /dev/stdin

# === FINAL =====
FROM base as final

# Extra python env
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PATH="/venv/bin:$PATH"

RUN dnf -y install \
    postgresql \
    # packages for localdef
    glibc-locale-source \
    glibc-langpack-en \
    # packages for ssh server
    openssh-server \
    openssh-clients \
 && dnf -y clean all \
 && rm -rf /var/cache/dnf

COPY --from=builder /venv /venv
COPY --from=builder /usr/local/bin /usr/local/bin

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

# Set locale to en GB
RUN localedef -c -i en_GB -f UTF-8 en_GB.UTF-8
ENV LANG en_GB.utf-8
ENV LC_ALL en_GB.utf-8

