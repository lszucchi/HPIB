#!/bin/bash

cd ./HPIB

function update {
	git checkout $1 git pull $1
}