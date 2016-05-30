#!/usr/bin/env bash


curl -c dropboxCookies https://www.dropbox.com/login

curl -b dropboxCookies -c dropboxCookies -d login_email=benchbox@outlook.com -d login_password=salou2010 -d login_submit=Login

