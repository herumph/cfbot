from db.create_db import init_db_session
from post.login import init_client

USERNAME = "arethegoodnamesaretaken+devbot@gmail.com"

DB_SESSION = init_db_session()
CLIENT = init_client(db_session=DB_SESSION, username=USERNAME)
