# -*- coding: utf-8 -*-
# Module: default
# Author: Zero-0
# Created on: 29/06/2020
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import sys
import os

current_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(current_dir, 'resources', 'lib'))

import app

if __name__ == '__main__':
    app.router()