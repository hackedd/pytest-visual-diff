#!/usr/bin/env bash
set -e

url=$(curl --silent "https://api.github.com/repos/mozilla/geckodriver/releases/latest" | \
      jq -r '.assets | map(select(.name | contains("linux64"))) | first | .browser_download_url')
curl -o geckodriver.tar.gz --location "$url"
tar xf geckodriver.tar.gz
rm geckodriver.tar.gz
