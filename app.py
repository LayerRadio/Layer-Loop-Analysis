"""
Run app on Dev server
"""
from os import environ, system

from layeranalysis import layerapp, db

import model.models
with layerapp.app_context():
    db.create_all()

if __name__ == "__main__":
    layerapp.run(host='0.0.0.0')
