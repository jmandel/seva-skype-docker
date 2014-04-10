#!/bin/bash
Xvfb :1 -screen 0 800x600x16 &
sleep 3
DISPLAY=:1 skype &

sleep 5
cd sevabot
DISPLAY=:1 sevabot
