#!/bin/sh

tor &
./prometheus-*/prometheus &
python main.py