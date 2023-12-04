from sqlalchemy import create_engine, text
import os


engine = create_engine("sqlite:///module/data/appdb.db",echo=True)

with engine.connect() as connection:
    result = connection.execute(text('select "connected"'))

    print(result.all())