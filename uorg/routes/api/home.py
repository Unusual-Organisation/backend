import os

from flask import Blueprint

from uorg.static import ROOT_PATH
from uorg.utils.success import SuccessOutput

home_bp = Blueprint("home", __name__)

version_file = os.path.join(ROOT_PATH, "VERSION")


@home_bp.route("/")
def home():
    with open(version_file, "r") as handle:
        version = handle.read().strip()
    return SuccessOutput("uorg", {"version": version, "website": "https://uevents.fr"})
