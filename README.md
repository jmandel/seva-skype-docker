## To build the docker image

```
$ sudo docker build -t sevabot .
```

## To configure the docker image

Configure the container passing in a "secret" (sevabot password) + skype admin
username:

```
sudo docker  run  -e secret=123456 -e skype_user=jcmandel  sevabot
export CID=`sudo docker ps -l -q`
export IP=`sudo docker inspect -format '{{ .NetworkSettings.IPAddress }}' $CID`
vncviewer $IP
```

In the vnc viewer, agree to the Skype terms of service, enter a skype bot
username + password, and check off the "sign in automatically" option. Then
sign in, and approve sevabot's connection request (choosing "remember this
devision).

Once that's done, kill the container and commit:

```
sudo docker kill $CID
sudo docker commit $CID sevabot
```

At this point you've got a configured image that you can launch via:

```
sudo docker run -p 5000:5000 sevabot start
```
