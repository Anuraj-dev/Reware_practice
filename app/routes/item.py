from flask import render_template, Blueprint, redirect, url_for, request, flash, session, jsonify
from app import db
from app.models import Item,  User, SwapRequest
from app.routes.auth import login_required, get_current_user
from sqlalchemy import or_, and_
from datetime import datetime

item = Blueprint('item', __name__)

@item.route("/")
def index():
    #Get all index listings from db
    try:
        # Get all approved items from database
        items = Item.query.all()  # Add .filter_by(status='approved') when you implement admin approval
        current_user = get_current_user()
        
        return render_template("items/index.html", current_user=current_user, items=items)
    except Exception as e:
        flash('Error loading listings', 'danger')
        return render_template("items/index.html", current_user=get_current_user(), items=[])

@item.route("/new")
@login_required
def renderNewPage():
    current_user = get_current_user()
    return render_template("items/new.html", current_user=current_user)

@item.route("/", methods=["POST"])
@login_required
def createListing():
    try:
        current_user = get_current_user()

        # Get form Data
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip()
        size = request.form.get('size', 'M')
        condition = request.form.get('condition', 'male')
        image_url = request.form.get('image_url', '').strip()
        points_cost = request.form.get('points_cost', type=int)

        # Validation
        if not title or len(title) < 3:
            flash('Title must be at least 3 characters long', 'danger')
            return redirect(url_for('item.renderNewPage'))
        
        if not category:
            flash('Category is required', 'danger')
            return redirect(url_for('item.renderNewPage'))
        
        if not points_cost or points_cost <= 0:
            flash('Points cost must be a positive number', 'danger')
            return redirect(url_for('item.renderNewPage'))
        
        if condition not in ['male', 'female', 'kids']:
            flash('Invalid condition selected', 'danger')
            return redirect(url_for('item.renderNewPage'))
        
        if size not in ['S', 'M', 'L', 'XL']:
            flash('Invalid size selected', 'danger')
            return redirect(url_for('item.renderNewPage'))

        # Create new Listing
        new_item = Item(
            user_id=current_user.id,
            title=title,
            description=description,
            category=category,
            size=size,
            condition=condition,
            image_url=image_url if image_url else None,
            points_cost=points_cost
        )
        
        db.session.add(new_item)
        db.session.commit()

        flash('Listing created successfully!', 'success')    #!Not for AI: "It will be available after admin approval."
        return redirect(url_for('item.index'))

    except Exception as e:
        db.session.rollback()
        flash('An error occurred while creating the listing. Please try again.', 'danger')
        return redirect(url_for('item.renderNewPage'))

@item.route("/<int:item_id>")
def showListing(item_id):
    current_item = Item.query.get_or_404(item_id)
    current_user = get_current_user()
    
    # Check if user has already requested this item
    existing_request = None
    if current_user:
        existing_request = SwapRequest.query.filter_by(
            requester_id=current_user.id,
            requested_item_id=item_id,
            status='pending'
        ).first()

    return render_template("items/show.html", item=current_item, current_user=current_user, existing_request=existing_request)

@item.route("/<int:item_id>/edit")
@login_required
def renderEditPage(item_id):
    current_item = Item.query.get_or_404(item_id)
    current_user = get_current_user()

    # Check if user owns this listing
    if current_item.user_id != current_user.id and not current_user.is_admin:
        flash('You are not authorized to edit this listing', 'danger')
        return redirect(url_for('item.showListing', item_id=item_id))

    return render_template("items/edit.html", item=current_item, current_user=current_user)

@item.route("/<int:item_id>", methods=["POST"])
@login_required
def upadateListing(item_id):  # Kept your typo as requested
    try:
        current_item = Item.query.get_or_404(item_id)
        current_user = get_current_user()

        # Check if current user owns listing
        if current_item.user_id != current_user.id and not current_user.is_admin:
            flash('You are not authorized to edit this listing', 'danger')
            return redirect(url_for('item.showListing', item_id=item_id))

        # Get form data
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip()
        size = request.form.get('size', 'M')
        condition = request.form.get('condition', 'male')
        image_url = request.form.get('image_url', '').strip()
        points_cost = request.form.get('points_cost', type=int)

        # Validation
        if not title or len(title) < 3:
            flash('Title must be at least 3 characters long', 'danger')
            return redirect(url_for('item.renderEditPage', item_id=item_id))
        
        if not category:
            flash('Category is required', 'danger')
            return redirect(url_for('item.renderEditPage', item_id=item_id))
        
        if not points_cost or points_cost <= 0:
            flash('Points cost must be a positive number', 'danger')
            return redirect(url_for('item.renderEditPage', item_id=item_id))

        # Update Listing
        current_item.title = title
        current_item.description = description
        current_item.category = category
        current_item.size = size
        current_item.condition = condition
        current_item.image_url = image_url if image_url else None
        current_item.points_cost = points_cost

        #!Not for AI: Admin here

        db.session.commit()

        flash('Listing updated successfully!', 'success')
        return redirect(url_for('item.showListing', item_id=item_id))

    except Exception as e:
        db.session.rollback()
        flash('An error occurred while updating the listing. Please try again.', 'danger')
        return redirect(url_for('item.renderEditPage', item_id=item_id))

@item.route("/<int:item_id>/delete", methods=["POST"])
@login_required
def deleteListing(item_id):
    try:
        current_item = Item.query.get_or_404(item_id)
        current_user = get_current_user()
        
        # Check if user owns this listing
        if current_item.user_id != current_user.id and not current_user.is_admin:
            flash('You are not authorized to delete this listing', 'danger')
            return redirect(url_for('item.showListing', item_id=item_id))
        
        db.session.delete(current_item)
        db.session.commit()
        
        flash('Listing deleted successfully!', 'success')
        return redirect(url_for('item.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the listing. Please try again.', 'danger')
        return redirect(url_for('item.showListing', item_id=item_id))

# Create a route for item dashboard in which user will be redirected towards and should contain all user data
@item.route("/dashboard")
@login_required
def dashboard():
    return render_template("items/index.html")
              
