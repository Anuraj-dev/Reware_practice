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

    current_user = get_current_user()

    return render_template("items/index.html", current_user=current_user)   #TODO- Here write items=items,

@item.route("/new")
@login_required
def renderNewPage():
    current_user = get_current_user()
    return render_template("items/new.html", get_current_user)

@item.route("/", method=["POST"])
def createListing():
    try:
        current_user=get_current_user()

        #Get form Data

        #Validation

        #Create new Listing
        db.session.commit()

        flash('Listing created successfully!', 'success')    #!Not for AI: "It will be available after admin approval."
        return redirect(url_for('item.index'))

    except Exception as e:
        db.session.rollback()
        flash('An error occurred while creating the listing. Please try again.', 'danger')
        return redirect(url_for('item.renderNewPage'))

@item.route("/<item_id>")
def showListing(item_id):
    current_item = Item.query.get_or_404(item_id)

    return render_template("item/show.html", item=current_item)

@item.route("/<item_id>/edit")
@login_required
def renderEditPage(item_id):
    current_item = Item.query.get_or_404(item_id)
    current_user = get_current_user()

    #Check if user owns this listing

    return render_template("/item/edit.html", item=current_item, current_user=current_user)

@item.route("/<item_id>", methods=["POST"])
@login_required
def upadateListing(item_id):
    try:
        current_item = Item.query.get_or_404(item_id)
        current_user = get_current_user()

        #Check if current user owns listing

        #Get form data

        #Validation

        #Update Listing

        #!Not for AI: Admin here

        db.session.commit()

        flash('Listing updated successfully!', 'success')
        return redirect(url_for('item.showListing', item_id=item_id))

    except Exception as e:
        db.session.rollback()
        flash('An error occurred while updating the listing. Please try again.', 'danger')
        return redirect(url_for('item.renderEditPage', item_id=item_id))
    
#Create Swap request route
@item.route("/<item_id>/swap", methods=["POST"])
@login_required
def createSwapRequest(item_id):
    
    return redirect(url_for('item.showListing', item_id=item_id))