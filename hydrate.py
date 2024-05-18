import os

from flask_bcrypt import Bcrypt
from sqlalchemy.orm.session import Session

from app.extensions import db
from app import create_app
from app.models.auth import User

application = create_app()
bcrypt = Bcrypt()


def hydrate_users(db_session: Session):
    # TODO: use Config Class
    admin_password = os.environ.get('POSTGRES_PASSWORD')
    if admin_password is None:
        raise Exception('Environment variable "POSTGRES_PASSWORD" not set')
    
    hashed_password = bcrypt.generate_password_hash(admin_password).decode('utf-8')

    print(f'hashed password: {hashed_password}')

    admin = User(
        first_name='admin',
        last_name='super',
        email='admin@email.com',
        password_hash=hashed_password
    )

    db_session.add(admin)
    db_session.commit()


if __name__ == '__main__':

    with application.app_context():
        db_session = db.session()

        hydrate_users(db_session)