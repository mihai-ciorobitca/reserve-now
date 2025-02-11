from flask import Blueprint, render_template

errors_blueprint = Blueprint("errors", __name__)

@errors_blueprint.app_errorhandler(413)
def request_entity_too_large(error):
    return 'File Too Large', 413

@errors_blueprint.app_errorhandler(404)
def page404(error):
    return render_template("errors/page404.html"), 404


@errors_blueprint.app_errorhandler(500)
def page500(error):
    return render_template("errors/page500.html"), 505
