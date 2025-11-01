import json
import os
from pathlib import Path

from argparse import ArgumentParser
from datetime import datetime
from flask_bcrypt import Bcrypt
from sqlalchemy.orm.session import Session

from app.models import Price, Security, User
from app.extensions import db
from app import create_app


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = "data"

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

application = create_app()
bcrypt = Bcrypt()

arg_parser = ArgumentParser()
arg_parser.add_argument("--users", type=bool, default=False, help="Enable / disbale hydrate users")
arg_parser.add_argument("--securities", type=bool, default=False, help="Enablne / disable securities")
arg_parser.add_argument("--prices", type=bool, default=False, help="Enable / disbale prices")


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


def security_from_dict(security: dict[str, any]) -> Security:
    return Security(
        ticker=security['Symbol'],
        security_name=security['Security'],
        gics_sector=security['GICS Sector'],
        gics_sub_industry=security['GICS Sub-Industry'],
        headquarters_location=security['Headquarters Location'],
        date_added=security['Date added'],
        cik=security['CIK'],
        year_founded=security['Founded'] if isinstance(security['Founded'], int) else int(security['Founded'][:4])
    )


def hydrate_securities(db_session: Session):

    data_dir = "../data"
    file_name = "constituents.json"
    file_path = os.path.join(data_dir, file_name)
    if os.path.exists(file_path):
        with open(file_path) as f:
            data = json.load(f)
            securities = [security_from_dict(s) for s in data]
            db_session.add_all(securities)
            db_session.commit()
    else:
        raise Exception(f'{file_path} does not exist')


def price_from_csv_line(line: str) -> list[Price]:
    values = line.strip().split(',')
    return Price(
        ticker=values[0],
        utc_time=datetime.strptime(values[1], DATE_FORMAT),
        price=float(values[2])
    )


def hydrate_prices(db_session: Session) -> None:
    data_dir_path = os.path.join(BASE_DIR, DATA_DIR)
    prices_files_names = [f for f in os.listdir(data_dir_path) if f.endswith("_prices.csv")]
    print(prices_files_names)
    for price_file_name in prices_files_names:
        with open(os.path.join(data_dir_path, price_file_name), 'r') as file:
            lines = file.readlines()
            unique_keys = []
            prices = []
            for line in lines:
                key = ','.join(line.strip().split(',')[:2])
                if key not in unique_keys:
                    unique_keys.append(key)
                    prices.append(price_from_csv_line(line))

            db_session.add_all(prices)
            db_session.commit()


if __name__ == '__main__':

    with application.app_context():
        db_session = db.session()

        args = arg_parser.parse_args()

        if (args.users):
            print("hydrating users")
            hydrate_users(db_session)

        if (args.securities):
            print("hydrating securities")
            hydrate_securities(db_session)

        if (args.prices):
            hydrate_prices(db_session)

        # q = db_session.qu
        # securities = db_session.query(Security).all()

        # tickers = [s.ticker for s in securities]
        # print(','.join(tickers))
