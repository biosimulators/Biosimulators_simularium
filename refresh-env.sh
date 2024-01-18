#!/bin/bash
# !/bin/zsh

env_name="$1"

conda remove -n "$env_name" --all \
  && conda create -n "$env_name" python=3.10 \
  && conda activate "$env_name"
