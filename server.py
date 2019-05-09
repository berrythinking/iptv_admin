#!/usr/bin/env python3

# https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04

from app import app
import argparse

PROJECT_NAME = 'iptv_admin'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=PROJECT_NAME, usage='%(prog)s [options]')
    argv = parser.parse_args()
    app.run(host=app.HOST, port=app.PORT, debug=True, use_reloader=False)  # debug=True, use_reloader=False
