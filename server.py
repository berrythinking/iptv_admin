#!/usr/bin/env python3

from app import app
import argparse

PROJECT_NAME = 'iptv_admin'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=PROJECT_NAME, usage='%(prog)s [options]')
    argv = parser.parse_args()

    app.run(debug=True, use_reloader=False)  # debug=True, use_reloader=False
