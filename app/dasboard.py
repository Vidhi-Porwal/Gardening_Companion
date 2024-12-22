from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import db, PlantInfo, UserPlant

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    user_plants = (
        db.session.query(UserPlant)
        .join(PlantInfo, UserPlant.plant_id == PlantInfo.ID)
        .filter(UserPlant.user_id == current_user.id)
        .all()
    )
    return render_template('dashboard.html', user_plants=user_plants)

# Add your search and add-plant-to-user routes here as well.
