from flask import render_template, Blueprint, redirect, url_for, request, flash, session, jsonify
from app import db
from app.models import Item, User, SwapRequest
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
        category = request.form.get('category', 'male').strip()
        size = request.form.get('size', 'M').strip()
        image_url = request.form.get('image_url', '').strip()
        points_cost = request.form.get('points_cost', type=int)

        # Validation
        if not title or len(title) < 3:
            flash('Title must be at least 3 characters long', 'danger')
            return redirect(url_for('item.renderNewPage'))
        
        if not points_cost or points_cost <= 0:
            flash('Points cost must be a positive number', 'danger')
            return redirect(url_for('item.renderNewPage'))

        if not category or category not in ['male', 'female', 'kids']:
            flash('Invalid category selected', 'danger')
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
    
    # Get user's items for swap modal (exclude the current item and items with pending swaps)
    user_items = []
    pending_swap = None
    
    if current_user and current_user.id != current_item.user_id:
        # Check if user already has pending swap request for this item
        pending_swap = SwapRequest.query.filter_by(
            requester_id=current_user.id,
            item_id=item_id,
            status='pending'
        ).first()
        
        # Get user's available items (not currently in pending swap requests as offered items)
        pending_offered_items = db.session.query(SwapRequest.offered_item_id).filter_by(
            requester_id=current_user.id,
            status='pending'
        ).subquery()
        
        user_items = Item.query.filter(
            Item.user_id == current_user.id,
            Item.id != item_id,
            ~Item.id.in_(pending_offered_items)
        ).all()

    return render_template("items/show.html", 
                         item=current_item, 
                         current_user=current_user,
                         user_items=user_items,
                         pending_swap=pending_swap)

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
        category = request.form.get('category', 'male').strip()
        size = request.form.get('size', 'M').strip()
        image_url = request.form.get('image_url', '').strip()
        points_cost = request.form.get('points_cost', type=int)

        # Validation
        if not title or len(title) < 3:
            flash('Title must be at least 3 characters long', 'danger')
            return redirect(url_for('item.renderEditPage', item_id=item_id))
        
        if not category or category not in ['male', 'female', 'kids']:
            flash('Invalid category selected', 'danger')
            return redirect(url_for('item.renderEditPage', item_id=item_id))
        
        if not points_cost or points_cost <= 0:
            flash('Points cost must be a positive number', 'danger')
            return redirect(url_for('item.renderEditPage', item_id=item_id))

        # Update Listing
        current_item.title = title
        current_item.description = description
        current_item.category = category
        current_item.size = size
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
    
    # Get swap requests user has made
    outgoing_requests = SwapRequest.query.filter_by(requester_id=current_user.id).all()
    
    # Get swap requests for user's items
    incoming_requests = SwapRequest.query.join(Item).filter(Item.user_id == current_user.id).all()
    
    return render_template("items/dashboard.html", 
                         current_user=current_user,
                         user_items=user_items,
                         outgoing_requests=outgoing_requests,
                         incoming_requests=incoming_requests)

# Swap System Routes
@item.route("/<int:item_id>/request-swap", methods=["POST"])
@login_required
def requestSwap(item_id):
    """User A requests to swap their item for User B's item"""
    try:
        current_user = get_current_user()
        requested_item = Item.query.get_or_404(item_id)
        offered_item_id = request.form.get('offered_item_id', type=int)
        
        # Validation
        if not offered_item_id:
            flash('Please select an item to offer', 'danger')
            return redirect(url_for('item.showListing', item_id=item_id))
        
        offered_item = Item.query.get_or_404(offered_item_id)
        
        # Check if user owns the offered item
        if offered_item.user_id != current_user.id:
            flash('You can only offer your own items', 'danger')
            return redirect(url_for('item.showListing', item_id=item_id))
        
        # Check if user is trying to swap with their own item
        if requested_item.user_id == current_user.id:
            flash('You cannot swap with your own item', 'danger')
            return redirect(url_for('item.showListing', item_id=item_id))
        
        # Check if swap request already exists
        existing_request = SwapRequest.query.filter_by(
            requester_id=current_user.id,
            item_id=item_id,
            status='pending'
        ).first()
        
        if existing_request:
            flash('You already have a pending swap request for this item', 'warning')
            return redirect(url_for('item.showListing', item_id=item_id))
        
        # Check if offered item is already in a pending swap
        pending_offer = SwapRequest.query.filter_by(
            offered_item_id=offered_item_id,
            status='pending'
        ).first()
        
        if pending_offer:
            flash('This item is already offered in another pending swap', 'warning')
            return redirect(url_for('item.showListing', item_id=item_id))
        
        # Create swap request
        swap_request = SwapRequest(
            requester_id=current_user.id,
            item_id=item_id,
            offered_item_id=offered_item_id,
            status='pending'
        )
        
        db.session.add(swap_request)
        db.session.commit()
        
        flash(f'Swap request sent! You offered "{offered_item.title}" for "{requested_item.title}"', 'success')
        return redirect(url_for('item.showListing', item_id=item_id))
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while creating the swap request', 'danger')
        return redirect(url_for('item.showListing', item_id=item_id))

@item.route("/swap/<int:swap_id>/accept", methods=["POST"])
@login_required
def acceptSwap(swap_id):
    """User B accepts the swap request"""
    try:
        current_user = get_current_user()
        swap_request = SwapRequest.query.get_or_404(swap_id)
        
        # Check if user owns the requested item
        if swap_request.item.user_id != current_user.id:
            flash('You are not authorized to accept this swap', 'danger')
            return redirect(url_for('item.dashboard'))
        
        # Check if swap is still pending
        if swap_request.status != 'pending':
            flash('This swap request is no longer pending', 'warning')
            return redirect(url_for('item.dashboard'))
        
        # Perform the swap - exchange item ownership
        requested_item = swap_request.item
        offered_item = swap_request.offered_item
        
        # Store original owners
        original_requested_owner = requested_item.user_id
        original_offered_owner = offered_item.user_id
        
        # Swap ownership
        requested_item.user_id = original_offered_owner
        offered_item.user_id = original_requested_owner
        
        # Update swap status
        swap_request.status = 'completed'
        
        db.session.commit()
        
        flash(f'Swap completed! You exchanged "{requested_item.title}" for "{offered_item.title}"', 'success')
        return redirect(url_for('item.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while completing the swap', 'danger')
        return redirect(url_for('item.dashboard'))

@item.route("/swap/<int:swap_id>/decline", methods=["POST"])
@login_required
def declineSwap(swap_id):
    """User B declines the swap request"""
    try:
        current_user = get_current_user()
        swap_request = SwapRequest.query.get_or_404(swap_id)
        
        # Check if user owns the requested item
        if swap_request.item.user_id != current_user.id:
            flash('You are not authorized to decline this swap', 'danger')
            return redirect(url_for('item.dashboard'))
        
        # Check if swap is still pending
        if swap_request.status != 'pending':
            flash('This swap request is no longer pending', 'warning')
            return redirect(url_for('item.dashboard'))
        
        # Update swap status
        swap_request.status = 'declined'
        db.session.commit()
        
        flash('Swap request declined', 'info')
        return redirect(url_for('item.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while declining the swap', 'danger')
        return redirect(url_for('item.dashboard'))

@item.route("/swap/<int:swap_id>/cancel", methods=["POST"])
@login_required
def cancelSwap(swap_id):
    """User A cancels their own swap request"""
    try:
        current_user = get_current_user()
        swap_request = SwapRequest.query.get_or_404(swap_id)
        
        # Check if user is the requester
        if swap_request.requester_id != current_user.id:
            flash('You are not authorized to cancel this swap', 'danger')
            return redirect(url_for('item.dashboard'))
        
        # Check if swap is still pending
        if swap_request.status != 'pending':
            flash('This swap request cannot be cancelled', 'warning')
            return redirect(url_for('item.dashboard'))
        
        # Delete the swap request
        db.session.delete(swap_request)
        db.session.commit()
        
        flash('Swap request cancelled', 'info')
        return redirect(url_for('item.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while cancelling the swap', 'danger')
        return redirect(url_for('item.dashboard'))