#!/bin/bash

trap kill_ssh_agent INT
SSH_AGENT_PID=

function kill_ssh_agent() {
  if [ -n "$SSH_AGENT_PID" ]; then
    kill "$SSH_AGENT_PID"
    SSH_AGENT_PID=
  fi
}

eval $(ssh-agent -s)
ssh-add <(echo "$SSH_PRIVATE_KEY")

"$@"

kill_ssh_agent
