#!/bin/bash

if [[ `id -u` -ne 0 ]] ; then echo "Please run as root" ; exit 1 ; fi

# First, get the base library
wget https://labjack.com/sites/default/files/software/labjack_ljm_software_2018_08_30_x86_64.tar.gz
tar -zvxf labjack_ljm_software_2018_08_30_x86_64.tar.gz
sudo ./labjack_ljm_software_2018_08_30_x86_64/labjack_ljm_installer.run

# Next, get the Python wrapper
wget https://labjack.com/sites/default/files/software/Python_LJM_2018_10_19.zip
unzip Python_LJM_2018_10_19.zip
cd Python_LJM_2018_10_19
sudo pip install .
cd ..

usage() { echo "Usage: $0 [-t]" 1>&2; exit 1; }


while getopts ":ht" opt; do
  case ${opt} in
    h ) # Show help
        usage
      ;;
    t ) # Install our package
        sudo pip install .
      ;;
    \? ) usage
      ;;
  esac
done