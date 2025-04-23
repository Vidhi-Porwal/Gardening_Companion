from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from .models import User, Plant, PlantRequest
from bson.objectid import ObjectId

admin_bp = Blueprint('admin', __name__)

@admin_bp.route("/admin", methods=["GET", "POST"])
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for('dashboard.dashboard'))
    
    users = User.get_all_users()
    plants = Plant.get_all_plants()
    return render_template("admin.html", users=users, plants=plants)

@admin_bp.route("/delete_plant/<plant_id>", methods=["DELETE"])
@login_required
def delete_plant(plant_id):
    if current_user.role != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    
    Plant.delete_plant(plant_id)
    return jsonify({"message": "Plant deleted successfully!"})

@admin_bp.route("/delete_user/<user_id>", methods=["DELETE"])
@login_required
def delete_user(user_id):
    if current_user.role != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    
    User.delete_user(user_id)
    return jsonify({"message": "User deleted successfully!"})

@admin_bp.route("/update_user_role/<user_id>", methods=["PUT"])
@login_required
def update_user_role(user_id):
    if current_user.role != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    new_role = data.get("role", "")
    User.update_user_role(user_id, new_role)
    return jsonify({"message": "User role updated successfully!"})

@admin_bp.route('/add_plant', methods=['POST'])
@login_required
def add_plant():
    if current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    new_plant = {
        "commonName": data.get('commonName'),
        "scientificName": data.get('scientificName'),
        "rank": data.get('rank'),
        "familyCommonName": data.get('familyCommonName'),
        "genus": data.get('genus'),
        "imageURL": data.get('imageURL'),
        "edible": data.get('edible', False),
        "saplingDescription": data.get('saplingDescription')
    }
    
    plant_id = Plant.add_plant(new_plant)
    request_id = request.args.get('request_id')
    if request_id:
        PlantRequest.delete_request(request_id)
    
    return jsonify({"message": "Plant added successfully!", "plant_id": plant_id})

@admin_bp.route('/edit_plant/<plant_id>', methods=['PUT'])
@login_required
def edit_plant(plant_id):
    if current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    update_data = {
        "commonName": data.get("commonName"),
        "scientificName": data.get("scientificName"),
        "rank": data.get("rank"),
        "familyCommonName": data.get("familyCommonName"),
        "genus": data.get("genus"),
        "imageURL": data.get("imageURL"),
        "edible": data.get("edible"),
        "saplingDescription": data.get("saplingDescription")
    }
    
    Plant.update_plant(plant_id, update_data)
    return jsonify({"message": "Plant updated successfully!"})

@admin_bp.route("/get_plant/<plant_id>", methods=["GET"])
@login_required
def get_plant(plant_id):
    plant = Plant.get_plant_by_id(plant_id)
    if not plant:
        return jsonify({"error": "Plant not found"}), 404
    
    plant["_id"] = str(plant["_id"])
    return jsonify(plant)

@admin_bp.route('/admin/pending_plants', methods=['GET'])
@login_required
def pending_plants():
    if current_user.role != "admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for('dashboard.dashboard'))
    
    pending_requests = PlantRequest.get_pending_requests()
    if not pending_requests:
        flash("No pending plant requests!", "info")
        return redirect(url_for('dashboard.dashboard'))
    
    return render_template('pending_plants.html', pending_requests=pending_requests)

@admin_bp.route('/admin/approve_plant/<request_id>', methods=['POST'])
@login_required
def approve_plant(request_id):
    if current_user.role != "admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for('dashboard.dashboard'))
    
    request_data = PlantRequest.get_request_by_id(request_id)
    if not request_data:
        flash("Plant request not found!", "danger")
        return redirect(url_for('admin.pending_plants'))
    
    return redirect(url_for('admin.add_plant', 
                         request_id=request_id,
                         commonName=request_data["plantName"], 
                         saplingDescription=request_data.get("description", "")))

@admin_bp.route('/admin/reject_plant/<request_id>', methods=['POST'])
@login_required
def reject_plant(request_id):
    if current_user.role != "admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for('dashboard.dashboard'))
    
    PlantRequest.delete_request(request_id)
    flash("Plant request rejected!", "danger")
    return redirect(url_for('admin.pending_plants'))