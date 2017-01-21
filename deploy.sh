#!/bin/bash

export deploy_sh_counter=$(( deploy_sh_counter + 1 ))

if [ -z "$TOKEN" ] && [ "$deploy_sh_counter" = 1 ]; then
  DOTENV=dotenv
  if type godotenv; then
    DOTENV=godotenv
  fi
  exec $DOTENV "$0" "$@"
fi

if [ "$1" == "status" ]; then
  $DOTENV curl -s $AUTOBUILD | jq
else
  $DOTENV curl -s -XPOST -H'Content-Type:application/json' -d '{"token":"'$TOKEN'","ref":"refs/heads/master"}' $AUTOBUILD
fi
