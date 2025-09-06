from app import create_app, db
from app.models import User, Item, SwapRequest
from werkzeug.security import generate_password_hash
import random
from datetime import datetime, timedelta

# Sample images provided
sample_images = [
    'https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8dCUyMHNoaXJ0fGVufDB8fDB8fHww',
    'https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8dCUyMHNoaXJ0fGVufDB8fDB8fHww',
    'https://images.unsplash.com/photo-1523381294911-8d3cead13475?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8OHx8dCUyMHNoaXJ0fGVufDB8fDB8fHww',
    'https://plus.unsplash.com/premium_photo-1673356301514-2cad91907f74?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8OXx8dCUyMHNoaXJ0fGVufDB8fDB8fHww',
    'https://plus.unsplash.com/premium_photo-1718913931807-4da5b5dd27fa?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NXx8dCUyMHNoaXJ0fGVufDB8fDB8fHww',
    'https://plus.unsplash.com/premium_photo-1661416497808-2319460830cb?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8c2xlZXZlfGVufDB8fDB8fHww',
    'https://images.unsplash.com/photo-1675668409245-955188b96bf6?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8c2xlZXZlfGVufDB8fDB8fHww',
    'https://plus.unsplash.com/premium_photo-1664202526559-e21e9c0fb46a?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8ZmFzaGlvbnxlbnwwfHwwfHx8MA%3D%3D'
]

def create_sample_users():
    """Create sample users for testing"""
    users_data = [
        {'username': 'alice_style', 'email': 'alice@example.com', 'points': 250},
        {'username': 'bob_fashion', 'email': 'bob@example.com', 'points': 180},
        {'username': 'carol_trends', 'email': 'carol@example.com', 'points': 320},
        {'username': 'david_wear', 'email': 'david@example.com', 'points': 150},
        {'username': 'emma_closet', 'email': 'emma@example.com', 'points': 400},
        {'username': 'frank_swap', 'email': 'frank@example.com', 'points': 90},
    ]
    
    users = []
    for user_data in users_data:
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            password=generate_password_hash('password123'),
            points=user_data['points'],
            is_admin=False
        )
        users.append(user)
        db.session.add(user)
    
    # Add an admin user
    admin = User(
        username='admin',
        email='admin@rewear.com',
        password=generate_password_hash('admin123'),
        points=1000,
        is_admin=True
    )
    users.append(admin)
    db.session.add(admin)
    
    db.session.commit()
    return users

def create_sample_items(users):
    """Create sample items for testing"""
    items_data = [
        {
            'title': 'Vintage Blue Denim Shirt',
            'description': 'Classic blue denim shirt in excellent condition. Perfect for casual outings and layering.',
            'category': 'male',
            'size': 'M',
            'points_cost': 120,
        },
        {
            'title': 'Elegant Black Evening Dress',
            'description': 'Stunning black evening dress, worn only once. Perfect for special occasions.',
            'category': 'female',
            'size': 'S',
            'points_cost': 200,
        },
        {
            'title': 'Casual White Cotton T-Shirt',
            'description': 'Comfortable white cotton t-shirt. Great for everyday wear and easy to style.',
            'category': 'male',
            'size': 'L',
            'points_cost': 80,
        },
        {
            'title': 'Floral Summer Dress',
            'description': 'Beautiful floral print summer dress. Light and breezy, perfect for warm weather.',
            'category': 'female',
            'size': 'M',
            'points_cost': 150,
        },
        {
            'title': 'Kids Rainbow Striped Shirt',
            'description': 'Colorful rainbow striped shirt for kids. Fun and vibrant design.',
            'category': 'kids',
            'size': 'S',
            'points_cost': 60,
        },
        {
            'title': 'Dark Blue Jeans',
            'description': 'Classic dark blue jeans in great condition. Comfortable fit and timeless style.',
            'category': 'male',
            'size': 'L',
            'points_cost': 140,
        },
        {
            'title': 'Red Silk Blouse',
            'description': 'Elegant red silk blouse. Professional and stylish, perfect for work or special events.',
            'category': 'female',
            'size': 'M',
            'points_cost': 180,
        },
        {
            'title': 'Leather Jacket',
            'description': 'Genuine leather jacket in black. Edgy and stylish, adds attitude to any outfit.',
            'category': 'male',
            'size': 'XL',
            'points_cost': 300,
        },
        {
            'title': 'Summer Maxi Dress',
            'description': 'Flowing maxi dress perfect for summer occasions. Comfortable and elegant.',
            'category': 'female',
            'size': 'L',
            'points_cost': 160,
        },
        {
            'title': 'Designer Polo Shirt',
            'description': 'High-quality designer polo shirt. Sophisticated and versatile for various occasions.',
            'category': 'male',
            'size': 'M',
            'points_cost': 220,
        },
        {
            'title': 'Kids Blue Hoodie',
            'description': 'Comfortable blue hoodie for kids. Perfect for cooler weather and playtime.',
            'category': 'kids',
            'size': 'M',
            'points_cost': 90,
        },
        {
            'title': 'Pink Party Dress',
            'description': 'Adorable pink party dress for little girls. Perfect for special occasions.',
            'category': 'kids',
            'size': 'S',
            'points_cost': 70,
        },
        {
            'title': 'Classic Black Suit Jacket',
            'description': 'Professional black suit jacket. Perfect for business meetings and formal events.',
            'category': 'male',
            'size': 'L',
            'points_cost': 250,
        },
        {
            'title': 'Bohemian Style Blouse',
            'description': 'Free-spirited bohemian blouse with beautiful patterns. Great for casual outings.',
            'category': 'female',
            'size': 'M',
            'points_cost': 130,
        },
        {
            'title': 'Sports Jersey',
            'description': 'Official team sports jersey in excellent condition. Perfect for game days.',
            'category': 'male',
            'size': 'XL',
            'points_cost': 110,
        }
    ]
    
    items = []
    # Skip admin user for item creation
    regular_users = users[:-1]
    
    for i, item_data in enumerate(items_data):
        # Create some variation in created dates
        days_ago = random.randint(1, 30)
        created_date = datetime.utcnow() - timedelta(days=days_ago)
        
        item = Item(
            user_id=random.choice(regular_users).id,
            title=item_data['title'],
            description=item_data['description'],
            category=item_data['category'],
            size=item_data['size'],
            image_url=random.choice(sample_images),
            points_cost=item_data['points_cost'],
            created_at=created_date
        )
        items.append(item)
        db.session.add(item)
    
    db.session.commit()
    return items

def create_sample_swaps(users, items):
    """Create sample swap requests for testing"""
    if len(items) < 4:
        print("Not enough items to create swaps")
        return []
    
    # Skip admin user for swap creation
    regular_users = users[:-1]
    
    swaps_data = [
        {
            'requester': regular_users[0],
            'requested_item': items[0],
            'offered_item': items[1],
            'status': 'pending'
        },
        {
            'requester': regular_users[1],
            'requested_item': items[2],
            'offered_item': items[3],
            'status': 'pending'
        },
        {
            'requester': regular_users[2],
            'requested_item': items[4],
            'offered_item': items[5],
            'status': 'completed'
        },
        {
            'requester': regular_users[3],
            'requested_item': items[6],
            'offered_item': items[7],
            'status': 'declined'
        }
    ]
    
    swaps = []
    for swap_data in swaps_data:
        # Ensure the requester is not the same as the item owner
        if swap_data['requester'].id == swap_data['requested_item'].user_id:
            continue  # Skip this swap to avoid self-swapping
            
        # Also ensure requester owns the offered item
        if swap_data['requester'].id != swap_data['offered_item'].user_id:
            # Reassign offered item to requester for this demo
            swap_data['offered_item'].user_id = swap_data['requester'].id
        
        swap = SwapRequest(
            requester_id=swap_data['requester'].id,
            item_id=swap_data['requested_item'].id,
            offered_item_id=swap_data['offered_item'].id,
            status=swap_data['status']
        )
        swaps.append(swap)
        db.session.add(swap)
    
    db.session.commit()
    return swaps

def populate_sample_data():
    """Main function to populate the database with sample data"""
    app = create_app()
    with app.app_context():
        print("Creating sample data...")
        
        # Clear existing data
        print("Clearing existing data...")
        SwapRequest.query.delete()
        Item.query.delete()
        User.query.delete()
        db.session.commit()
        
        # Create sample users
        print("Creating sample users...")
        users = create_sample_users()
        print(f"Created {len(users)} users")
        
        # Create sample items
        print("Creating sample items...")
        items = create_sample_items(users)
        print(f"Created {len(items)} items")
        
        # Create sample swaps
        print("Creating sample swap requests...")
        swaps = create_sample_swaps(users, items)
        print(f"Created {len(swaps)} swap requests")
        
        print("Sample data creation completed!")
        print("\nSample accounts created:")
        print("Admin: admin@rewear.com / admin123")
        print("Users: alice@example.com, bob@example.com, carol@example.com, etc. / password123")

if __name__ == '__main__':
    populate_sample_data()
