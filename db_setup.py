from hello import db, Role, User
from passlib.hash import sha256_crypt

db.drop_all()
db.create_all()

admin_role = Role(name='Administrator')
mod_role = Role(name='Moderator')
user_role = Role(name='User')

admin_user = User(name="Administrator", username='admin', email='admin@admin.com', password=sha256_crypt.hash('admin'),
                    role=admin_role)
regular_user = User(name="Shivam", username='shivam', email='shivamflash@gmail.com', password=sha256_crypt.hash('password'),
                    role=user_role)

db.session.add_all([admin_role, mod_role, user_role, admin_user, regular_user])
db.session.commit()