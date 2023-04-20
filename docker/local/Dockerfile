FROM python:3.8

# Install system stuff
RUN apt-get update
# RUN apt-get -y install \
#     software-properties-common \
#     build-essential \
#     gcc \
#     curl \
#     dirmngr \
#     apt-transport-https \
#     lsb-release \
#     ca-certificates \
#     locales

# Installing Node
# We do this first as it has the regrettable habit of installing Python 2.7
# and symlinking it in place of the version we actually want
ENV NODE_VERSION 18
# Configure the node apt repository
RUN curl -sL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs

# Installing Python
ENV PYTHON_VERSION 3.8
# Configure the Deadsnakes Python apt repository
RUN add-apt-repository -y ppa:deadsnakes/ppa


# Install pip
RUN python3.8 -m ensurepip
# Ensure we use the right copies of python and pip
# In particular, get rid of the /usr/bin/python symlink to 2.7 that Node installation kindly created
RUN rm -f /usr/bin/python \
    && ln -s /usr/bin/python3.8 /usr/bin/python \
    && ln -s /usr/local/bin/pip3.8 /usr/bin/pip

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
RUN curl -sLO https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

# Set locale to en GB
RUN localedef -c -i en_GB -f UTF-8 en_GB.UTF-8
ENV LANG en_GB.utf-8
ENV LC_ALL en_GB.utf-8

# Set PYTHONUNBUFFERED so output is displayed in the Docker log
ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.1.8 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=200 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /usr/src/app

# Poetry commands reference https://python-poetry.org/docs/cli/#run
COPY pyproject.toml poetry.lock ./
RUN pip install poetry==$POETRY_VERSION \
    && poetry export --without-hashes -f requirements.txt -o requirements.txt \
    && poetry export --dev --without-hashes -f requirements.txt -o requirements-dev.txt \
    && pip install -r requirements-dev.txt

COPY package.json package-lock.json ./
RUN npm install -g npm \
    && npm ci

# Set up Playwright
RUN playwright install
RUN playwright install-deps
