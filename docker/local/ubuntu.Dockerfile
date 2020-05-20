# Kinda works but can't run pytest due to an error
FROM ubuntu:20.10

ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

RUN ln -fs /usr/share/zoneinfo/Europe/London /etc/localtime \
 && apt-get update \
 && apt-get install -y \
    openssh-server \
    postgresql-client \
    python3-pip \
    python3-venv \
    nano \
    wget \
    locales \
 && rm -rf /var/lib/apt/lists/* \
 && localedef -c -i en_GB -f UTF-8 en_GB.UTF-8

ENV LANG en_GB.utf-8
ENV LC_ALL en_GB.utf-8

RUN mkdir /var/run/sshd \
 && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
 # SSH login fix. Otherwise user is kicked off after login
 && sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd \
 && echo root:pass | chpasswd
CMD ["/usr/sbin/sshd", "-D"]

#ENV NOTVISIBLE "in users profile"
#RUN echo "export VISIBLE=now" >> /etc/profile


ENV DOCKERIZE_VERSION=v0.6.1
# Install Dockerize
RUN wget --no-verbose https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

WORKDIR /usr/src/app

# Poetry commands reference https://python-poetry.org/docs/cli/#run
# Without virtualenv (.venv)
COPY pyproject.toml poetry.lock ./
RUN pip3 install poetry \
 && poetry lock \
 && poetry export --dev -f requirements.txt -o requirements.txt \
 && pip3 install -r requirements.txt

## With a virtualenv (.venv) in project root
#RUN pip install --upgrade pip \
# && pip install "poetry==$POETRY_VERSION"
#
#COPY *.toml poetry.lock ./
#RUN poetry install --no-interaction --no-ansi


#COPY ./docker/local/entrypoint.sh /
#ENTRYPOINT ["/entrypoint.sh"]
