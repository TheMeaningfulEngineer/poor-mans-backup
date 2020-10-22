# Overview

A quick and dirty way to set up your RPi so it does backup of your files on Google drive.
If something goes wrong you will get an email notification.

Conceptually the following is happens:

1. A scripts daily pulls the content of your drive to the RPi (overwriting yesterdays content)
2. Once a month the content is archived and stored to the USB stick
3. If any of the scripts fail, an email is sent with the logs


# Installation

An overview of the installation is:

1. Populate the variables with needed data
    * This means having credentials for the gmail bot account ready
2. Run the scrips on the PC which sets up the RPi
3. ssh on the RPi and conclude the configuration

## Manual work

Not everything could have been automated. These include:

* Setting up a bot email account which
    * This account will be used to send mails if something goes wrong
    * You will be asked for its username and password below
* [Setting up authentication for the google drive API](https://rclone.org/drive/)
    * You will have to trigger this from the RPi in the steps below

## Prerequisites

It's assumed you have a RPi flashed with Raspbian you can SSH to. 
For a tip on how to get there check [this link](https://meaningfulengineer.com/rpi-sdcard-setup/)

[ansible](https://www.ansible.com/) is used to automate some of the setup.
It must be available on the PC. i.e `apt-get install ansible`.

## Steps


Plug in the USB stick in the RPi.

Power on the RPi.


```
# Email and password of the gmail bot which will send the emails on failure
EMAIL_SENDER=
EMAIL_SENDER_PASS=

# The recipients of the email in case of failure
EMAIL_RECEIVER=

# Info so the scripts can ssh to the RPi
# For the RPi the defau HOST_USERNAME=pi
HOST_USERNAME=
HOST_IP=

# Rclone parameters
# You will need to remeber these and reenter them in the configure rclone part.
# The names for the remote location (as specified in rclone)
RCLONE_REMOTE_NAME=
# The path of the directly to clone from the persective of google drive.
# RCLONE_REMOTE_DIR=Local_and_drive/Important
RCLONE_REMOTE_DIR=


# This will prompt you for the RPi password
ansible-playbook -k -K -i $HOST_IP, --extra-vars "\
email_sender=$EMAIL_SENDER \
email_sender_pass=$EMAIL_SENDER_PASS \
ansible_user=$HOST_USERNAME \
rclone_remote_name=$RCLONE_REMOTE_NAME \
rclone_remote_dir=$RCLONE_REMOTE_DIR \
email_receiver=$EMAIL_RECEIVER " \
main-play.yml
```


[**Configure rclone**](https://rclone.org/drive/)

```
# ssh on the RPi
rclone config

When prompted for `name>` insert the same value as for `RCLONE_REMOTE_NAME`.
```

# Testing/confirming success

```
# Disable ntp to be able to modify the system time
timedatectl set-ntp 0


# List all the systemd timers and check
# There is a daily/monthly timer listed
systemctl list-timers --all


# Set the time either relatively or absolutely 
# to trigger the timer
timedatectl set-time +1h18m
timedatectl set-time '2019-03-01 00:00:05'
```
