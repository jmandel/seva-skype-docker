#!/bin/bash

cd sevabot
python setup.py develop

cp settings.py.example settings.py
sed -i 's/koskela/'"$secret"'/' settings.py
sed -i 's/oulu/'"$skype_user"'/' settings.py
sed -i 's/localhost/0.0.0.0/' settings.py
sed -i 's/{{mongo_url}}/'"$mongo_url"'/' settings.py

Xvfb :1 -screen 0 800x600x16 &
sleep 3
DISPLAY=:1 fluxbox &
sleep 5
x11vnc -display :1 -bg -xkb 
DISPLAY=:1 skype  &

trap ctrl_c INT
function ctrl_c() {
  echo "Done!"
  exit;
}

while true;
 do DISPLAY=:1 sevabot;
 sleep 1;
done;
