#!/bin/bash

if [ "$(uname)" = Darwin ]; then
  curl -L -O https://github.com/gohugoio/hugo/releases/download/v0.18.1/hugo_0.18.1_macOS-64bit.zip
  unzip hugo_0.18.1_macOS-64bit.zip
  mv -f hugo_0.18.1_darwin_amd64/hugo_0.18.1_darwin_amd64 $HOME/bin/hugo
else
  wget https://github.com/gohugoio/hugo/releases/download/v0.18.1/hugo_0.18.1-64bit.deb
  sudo dpkg -i hugo_0.18.1-64bit.deb
fi
