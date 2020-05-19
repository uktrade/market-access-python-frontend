#!/usr/bin/env bash

echo `python --version`

if ls /root/.ssh/id_rsa 1> /dev/null 2>&1; then
    find /root/.ssh -type f -exec chmod 600 {} \;

    SSH_ENV="$HOME/.ssh/environment"
    # Source SSH settings, if applicable

    if [ -f "${SSH_ENV}" ]; then
        . "${SSH_ENV}" > /dev/null
        #ps ${SSH_AGENT_PID} doesn't work under cywgin
        ps -ef | grep ${SSH_AGENT_PID} | grep ssh-agent$ > /dev/null || {
            /usr/bin/ssh-agent -s | sed 's/^echo/#echo/' > "${SSH_ENV}"
            chmod 600 "${SSH_ENV}"
            . "${SSH_ENV}" > /dev/null
            /usr/bin/ssh-add;
        }
    else
        /usr/bin/ssh-agent -s | sed 's/^echo/#echo/' > "${SSH_ENV}"
        chmod 600 "${SSH_ENV}"
        . "${SSH_ENV}" > /dev/null
        /usr/bin/ssh-add;
    fi
fi

source /usr/local/bin/activate.sh
