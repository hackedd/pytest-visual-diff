#!/usr/bin/env bash
set -e

version=$(curl --silent "https://chromedriver.storage.googleapis.com/LATEST_RELEASE")
curl -o chromedriver.zip "https://chromedriver.storage.googleapis.com/$version/chromedriver_linux64.zip"
unzip -o chromedriver.zip
rm chromedriver.zip
