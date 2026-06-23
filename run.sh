#!/usr/bin/env bash

PYWEB_VERSION="0.0.2-alpha"

logo="""
 _______  __   __  _     _  _______  _______
|       ||  | |  || | _ | ||       ||  _    |
|    _  ||  |_|  || || || ||    ___|| |_|   |
|   |_| ||       ||       ||   |___ |       |
|    ___||_     _||       ||    ___||  _   |
|   |      |   |  |   _   ||   |___ | |_|   |
|___|      |___|  |__| |__||_______||_______|
▄▖▖▖▄▖  ▄▖▖▖▄▖▖▖▄▖▖ ▖  ▄▖▖ ▖  ▄▖▖▖▄▖  ▖  ▖▄▖▄
▐ ▙▌▙▖  ▙▌▌▌▐ ▙▌▌▌▛▖▌  ▐ ▛▖▌  ▐ ▙▌▙▖  ▌▞▖▌▙▖▙▘
▐ ▌▌▙▖  ▌ ▐ ▐ ▌▌▙▌▌▝▌  ▟▖▌▝▌  ▐ ▌▌▙▖  ▛ ▝▌▙▖▙▘
"""

echo "$logo"
echo "Welcome to PyWeb version $PYWEB_VERSION"
echo "Built with ♥︎ by YeudaBy"
echo
echo "Source repository: https://github.com/YeudaBy/PyWeb"
echo
echo "Hit ctrl+c to exit"

# Make sure python installed
command -v python3 >/dev/null 2>&1 || echo "Sorry, python3 not installed. exiting..." && exit
