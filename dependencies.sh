#!/bin/sh
sudo apt-get update
sudo apt-get -y install git vim python3-pip libilmbase-dev libopenexr-dev libgstreamer1.0-dev libtiff5-dev libjasper-dev libpng-dev libjpeg-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libgtk2.0-dev libatlas-base-dev gfortran libgdk-pixbuf2.0-dev libpango1.0-dev libcairo2-dev libqtgui4 libqt4-test
sudo pip3 install pafy numpy opencv-python
sudo pip3 install --upgrade youtube_dl