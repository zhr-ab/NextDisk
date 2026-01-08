"""
The flask application package.
"""

from flask import Flask
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'  # 用于session加密

import NextDisk.views
