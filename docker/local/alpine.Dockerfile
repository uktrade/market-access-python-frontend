#FROM python:3.7
FROM python:3.7.5-alpine
MAINTAINER Wibble Wobble

ARG PROJECT_PATH=/usr/src/app/
ENV SSH_SERVER_KEYS /etc/ssh/host_keys/

#
# Install virtualenv for developing
#

RUN pip install --no-cache-dir virtualenv

#
# Copy rootfs files
#

COPY /docker/local/rootfs /

#
# Install ssh-server for connect remote python interpreter
#

EXPOSE 22

RUN apk update && \
    apk add bash openssh sudo && \
    mkdir -p ${SSH_SERVER_KEYS} && \
    mkdir ${PROJECT_PATH} && \
    echo -e "HostKey ${SSH_SERVER_KEYS}ssh_host_rsa_key" >> /etc/ssh/sshd_config && \
    echo -e "HostKey ${SSH_SERVER_KEYS}ssh_host_dsa_key" >> /etc/ssh/sshd_config && \
    echo -e "HostKey ${SSH_SERVER_KEYS}ssh_host_ecdsa_key" >> /etc/ssh/sshd_config && \
    echo -e "HostKey ${SSH_SERVER_KEYS}ssh_host_ed25519_key" >> /etc/ssh/sshd_config && \
    sed -i "s/#PermitRootLogin.*/PermitRootLogin\ yes/" /etc/ssh/sshd_config && \
    echo "root:root" | chpasswd && \
    chmod a+x /usr/local/bin/* && \
    rm -rf /var/cache/apk/* /tmp/*

RUN apk add alpine-sdk postgresql-dev libffi-dev openssl-dev python3-dev musl-dev && \
    rm -rf /var/cache/apk/* /tmp/*

# PIP packages
RUN pip install pipenv
ADD Pipfile* ./
RUN pipenv lock --requirements > requirements.txt
RUN pip install -r requirements.txt

WORKDIR ${PROJECT_PATH}

#
# Saving dev virtualenv and ssh host keys
#

VOLUME ["${SSH_SERVER_KEYS}", "/root/"]

ENTRYPOINT ["entrypoint.sh"]

CMD ["/usr/sbin/sshd", "-D", "-e"]

#ADD Pipfile* ./
#RUN pipenv install
#RUN pipenv sync --dev





#ENV PYTHON_VERSION 3.7.2
#RUN wget --no-verbose https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz \
#    && tar -C /usr/local/bin -xzvf Python-$PYTHON_VERSION.tgz \
#    && rm Python-$PYTHON_VERSION.tgz \
#    && cd /usr/local/bin/Python-$PYTHON_VERSION \
#    && ./configure --enable-optimizations \
#    && make altinstall
#
## Set locale to en GB
#RUN localedef -c -i en_GB -f UTF-8 en_GB.UTF-8
#
## Download and install dockerize.
#ENV DOCKERIZE_VERSION v0.6.1
#RUN wget --no-verbose https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
#    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
#    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz
#
## Add aliases
#RUN echo "alias py3='python3.7'" >> ~/.bashrc
#
## Set PYTHONUNBUFFERED so output is displayed in the Docker log
#ENV PYTHONUNBUFFERED=1
#
#WORKDIR /usr/src/app
#
#ENV LANG en_GB.utf-8
#ENV LC_ALL en_GB.utf-8
#
## create virtualenv directory in WORKDIR called ".venv"
#ENV PIPENV_VENV_IN_PROJECT="enabled"
#
#RUN python3.7 -m pip install pipenv
#ADD Pipfile* ./
#RUN pipenv sync --dev
