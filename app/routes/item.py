from flask import render_template, Blueprint, redirect, url_for, request, flash, session, jsonify
from app import db
from app.models import Item,  User, SwapRequest
from app.routes.auth import login_required, get_current_user, update_user_session
from sqlalchemy import or_, and_
from datetime import datetime

item = Blueprint('item', __name__)