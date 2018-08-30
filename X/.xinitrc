#!/bin/bash
xhost +local:0
xset s off
xset -dpms
xset s noblank
xrdb -load $HOME/.Xresources
xbindkeys
exec ck-launch-session dbus-launch --sh-syntax --exit-with-session i3
