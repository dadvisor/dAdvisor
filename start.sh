#!/usr/bin/env sh

# Run cAdvisor as a daemon
cadvisor --logtostderr &
python main.py