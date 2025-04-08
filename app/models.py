from flask_login import UserMixin


class Profile(UserMixin):
    def __init__(self, user_data):
        """Initialize Profile object with data from MongoDB."""
        self._id = str(user_data['_id'])  # Convert ObjectId to string for Flask
        self.email = user_data['email']
        self.username = user_data['username']
        self.password = user_data['password']
        self.sessions = user_data['sessions']

    def get_id(self):
        """Return the user ID (used by Flask-Login)."""
        return self._id

class Listing:
    def __init__(self, listing_data):
        """Initialize Profile object with data from MongoDB."""
        self._id = str(listing_data['_id'])  # Convert ObjectId to string for Flask
        self.title = listing_data['title']
        self.author = listing_data['author']
        self.price = listing_data['price']
        self.description = listing_data['description']
        self.image = listing_data['image']
        self.category = listing_data['category']
        self.isbn = listing_data['isbn']
        self.quantity = listing_data['quantity']
        self.listing_poster = listing_data['listing_poster']

    def get_id(self):
        """Return the user ID (used by Flask-Login)."""
        return self._id

class chat_room:
    def __init__(self, room_data):
        """Initialize Profile object with data from MongoDB."""
        self._id = str(room_data['_id'])  # Convert ObjectId to string for Flask
        self.room_name = room_data['room_name']
        self.room_id = room_data['room_id']
        self.room_poster = room_data['room_poster']
        self.room_description = room_data['room_description']
        self.room_image = room_data['room_image']
        self.room_members = room_data['room_members']