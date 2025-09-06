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

    return render_template("items/index.html", items=items, current_user=current_user)   #TODO

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

        flash('Listing created successfully!', 'success')    #!Not for AI: "It will be available after admin approval."
        return redirect(url_for('item.index'))

    except Exception as e:
        db.session.rollback()
        flash('An error occurred while creating the listing. Please try again.', 'danger')
        return redirect(url_for('item.renderNewPage'))
