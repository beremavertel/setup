#!/bin/bash

tmp=$PWD

cd ~
ln -s $tmp/.vimrc
ln -s $tmp/.inputrc

echo ". $tmp/mybashrc" >> .bashrc
