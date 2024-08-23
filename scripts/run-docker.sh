#!/bin/bash
# !/bin/zsh

docker build -t biosimularium . \
  && docker run -it biosimularium
