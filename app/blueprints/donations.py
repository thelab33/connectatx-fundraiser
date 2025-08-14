from flask import Blueprint

bp = Blueprint('donations', __name__)

@bp.route('/donations/test')
def test():
    return "Donations blueprint placeholder."
