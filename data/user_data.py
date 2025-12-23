from models.user import UserModel

admin_user = UserModel(username="admin", email="admin@example.com", role="admin")
admin_user.set_password("admin123")

staff_user1 = UserModel(username="staff1", email="staff1@example.com", role="staff")
staff_user1.set_password("staff123")

staff_user2 = UserModel(username="staff2", email="staff2@example.com", role="staff")
staff_user2.set_password("staff123")

user1 = UserModel(username="user1", email="user1@example.com", role="customer")
user1.set_password("user123")

user2 = UserModel(username="user2", email="user2@example.com", role="customer")
user2.set_password("user123")

user_list = [admin_user, staff_user1, staff_user2, user1, user2]
