FROM python:3.9-slim-buster
# #Using non standard build to enable Playwright tests
FROM mcr.microsoft.com/playwright/python:v1.39.0-jammy

# Install system stuff
RUN apt-get update
RUN apt-get install -y build-essential python3-dev libffi-dev libmagic-dev

# Configure the node apt repository
RUN curl -sL https://deb.nodesource.com/setup_23.x | bash -
RUN apt-get install -y nodejs

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

# Set PYTHONUNBUFFERED so output is displayed in the Docker log
ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.6.1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=200 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /usr/src/app

# Poetry commands reference https://python-poetry.org/docs/cli/#run
COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip \
    && pip install poetry==$POETRY_VERSION \
    && poetry export --without-hashes -f requirements.txt -o requirements.txt \
    && poetry export --with dev --without-hashes -f requirements.txt -o requirements-dev.txt \
    && pip install -r requirements-dev.txt

COPY package.json package-lock.json ./
RUN npm install -g npm \
    && npm ci

# Set up Playwright
RUN playwright install
RUN playwright install-deps
