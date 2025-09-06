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
    return render_template("items/new.html", current_user=current_user)  # Fixed the parameter

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
            item_id=item_id,
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
    current_user = get_current_user()
    
    # Get user's items
    user_items = Item.query.filter_by(user_id=current_user.id).all()
    
    # Get user's swap requests (requests made by user)
    user_requests = SwapRequest.query.filter_by(requester_id=current_user.id).all()
    
    # Get requests for user's items (requests received by user)
    item_ids = [item.id for item in user_items]
    received_requests = SwapRequest.query.filter(SwapRequest.item_id.in_(item_ids)).all() if item_ids else []
    
    return render_template("items/dashboard.html", 
                         current_user=current_user,
                         user_items=user_items,
                         user_requests=user_requests,
                         received_requests=received_requests)

# Route to handle swap requests
@item.route("/<int:item_id>/request", methods=["POST"])
@login_required
def requestSwap(item_id):
    try:
        current_user = get_current_user()
        current_item = Item.query.get_or_404(item_id)
        
        # Check if user is trying to request their own item
        if current_item.user_id == current_user.id:
            flash('You cannot request your own item', 'danger')
            return redirect(url_for('item.showListing', item_id=item_id))
        
        # Check if user has enough points
        if current_user.points < current_item.points_cost:
            flash('You do not have enough points for this item', 'danger')
            return redirect(url_for('item.showListing', item_id=item_id))
        
        # Check if user already has a pending request for this item
        existing_request = SwapRequest.query.filter_by(
            requester_id=current_user.id,
            item_id=item_id,
            status='pending'
        ).first()
        
        if existing_request:
            flash('You already have a pending request for this item', 'warning')
            return redirect(url_for('item.showListing', item_id=item_id))
        
        # Create new swap request
        new_request = SwapRequest(
            requester_id=current_user.id,
            item_id=item_id,
            status='pending'
        )
        
        db.session.add(new_request)
        db.session.commit()
        
        flash('Swap request sent successfully!', 'success')
        return redirect(url_for('item.showListing', item_id=item_id))
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while sending the request. Please try again.', 'danger')
        return redirect(url_for('item.showListing', item_id=item_id))

# Route to handle swap request responses
@item.route("/requests/<int:request_id>/respond", methods=["POST"])
@login_required
def respondToRequest(request_id):
    try:
        current_user = get_current_user()
        swap_request = SwapRequest.query.get_or_404(request_id)
        action = request.form.get('action')  # 'accept' or 'decline'
        
        # Check if user owns the item being requested
        if swap_request.item.user_id != current_user.id:
            flash('You are not authorized to respond to this request', 'danger')
            return redirect(url_for('item.dashboard'))
        
        if action == 'accept':
            # Process the swap
            requester = swap_request.requester
            item = swap_request.item
            
            # Transfer points
            requester.points -= item.points_cost
            current_user.points += item.points_cost
            
            # Update request status
            swap_request.status = 'completed'
            
            # Remove the item (since it's been swapped)
            db.session.delete(item)
            
            flash('Swap completed successfully!', 'success')
            
        elif action == 'decline':
            # Just delete the request
            db.session.delete(swap_request)
            flash('Request declined', 'info')
        
        db.session.commit()
        return redirect(url_for('item.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while processing the request. Please try again.', 'danger')
        return redirect(url_for('item.dashboard'))

# API route to get items with filters
@item.route("/api/items")
def getItems():
    try:
        # Get query parameters
        category = request.args.get('category')
        condition = request.args.get('condition')
        size = request.args.get('size')
        min_points = request.args.get('min_points', type=int)
        max_points = request.args.get('max_points', type=int)
        search = request.args.get('search')
        
        # Build query
        query = Item.query
        
        if category:
            query = query.filter(Item.category == category)
        
        if condition:
            query = query.filter(Item.condition == condition)
        
        if size:
            query = query.filter(Item.size == size)
        
        if min_points:
            query = query.filter(Item.points_cost >= min_points)
        
        if max_points:
            query = query.filter(Item.points_cost <= max_points)
        
        if search:
            query = query.filter(
                or_(
                    Item.title.contains(search),
                    Item.description.contains(search)
                )
            )
        
        items = query.all()
        
        # Convert to JSON
        items_data = []
        for item in items:
            items_data.append({
                'id': item.id,
                'title': item.title,
                'description': item.description,
                'category': item.category,
                'size': item.size,
                'condition': item.condition,
                'image_url': item.image_url,
                'points_cost': item.points_cost,
                'owner': item.owner.user_name,
                'created_at': item.created_at.isoformat()
            })
        
        return jsonify({'items': items_data, 'count': len(items_data)})
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch items'}), 500

