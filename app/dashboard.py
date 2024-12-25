### dashboard.py ###
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import UserPlant, PlantInfo

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def dashboard():
    user_plants = UserPlant.get_user_plants(current_user.id)
    plants = PlantInfo.get_all_plants()  # Fetch all plants from the database
    print(plants)
    return render_template('dashboard.html', user_plants=user_plants, plants=plants)

@dashboard_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search_plants():
    if request.method == 'POST':
        search_query = request.form.get('search')
        plants = UserPlant.search_plants(search_query)
        return render_template('search_results.html', plants=plants)
    return render_template('search.html')

@dashboard_bp.route('/add_plant/<int:plant_id>', methods=['POST'])
@login_required
def add_plant_to_user(plant_id):
    UserPlant.add_plant_to_user(current_user.id, plant_id, quantity=1)
    return redirect(url_for('dashboard.dashboard'))

@dashboard_bp.route('/remove_plant/<int:plant_id>', methods=['POST'])
@login_required
def remove_plant_from_user(plant_id):
    UserPlant.remove_plant_from_user(current_user.id, plant_id)
    return redirect(url_for('dashboard.dashboard'))

@dashboard_bp.route('/get_plants', methods=['GET'])
def get_plants():
    import pdb; pdb.set_trace();
    try:
        plants = PlantInfo.get_all_plants()  # Fetch all plants from the database
        print("plants")
        return jsonify(plants), 200
    except Exception as e:
        print(f"Error fetching plants: {e}")
        return jsonify({'error': 'Failed to fetch plant data'}), 500

