from flask import Blueprint, render_template
from modules.models import Agent

agents_bp = Blueprint(
    "agents",
    __name__,
    template_folder="../../templates"
)

@agents_bp.route("/agents")
def agents():

    agents_list = Agent.query.filter_by(verified=True).all()

    return render_template(
        "agents.html",
        agents=agents_list
    )
