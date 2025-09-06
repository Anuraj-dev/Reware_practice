from app import db
from datetime import datetime
from sqlalchemy import CheckConstraint


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    points = db.Column(db.Integer, default=10, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    items = db.relationship('Item', backref='owner', lazy=True, cascade='all, delete-orphan')
    swap_requests = db.relationship('SwapRequest', foreign_keys='[SwapRequest.requester_id]', backref='requester', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'


class Item(db.Model):
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), default='male', nullable=False)
    size = db.Column(db.String(20), default='M', nullable=True)
    image_url = db.Column(db.String(200), nullable=True)
    points_cost = db.Column(db.Integer, default=10, nullable=False)
    # status = db.Column(db.String(20), default='pending', nullable=False)  # pending/approved
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Check constraints
    __table_args__ = (
        CheckConstraint("category IN ('male', 'female', 'kids')", name='check_category'),
        CheckConstraint("size IN ('S', 'M', 'L', 'XL')", name='check_size'),
    )
    
    # Relationships
    swap_requests = db.relationship('SwapRequest', foreign_keys='[SwapRequest.item_id]', backref='item', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Item {self.title}>'


class SwapRequest(db.Model):
    __tablename__ = 'swap_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)  
    offered_item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending/completed/declined
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'completed', 'declined')", name='check_status'),
    )
    
    # Relationships
    offered_item = db.relationship('Item', foreign_keys=[offered_item_id])
    
    def __repr__(self):
        return f'<SwapRequest {self.id}>'

