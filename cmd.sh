#!/bin/bash

if [ $1 = "a" ]; then
	echo "aaa" > /data/a
elif [ $1 = "b" ]; then
	echo "bbb" > /data/b
elif [ $1 = "c" ]; then
	echo "cccc" > /data/c
else
	echo "No option provided"
fi

