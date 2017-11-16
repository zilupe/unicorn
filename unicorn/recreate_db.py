import unicorn.db.connection
from unicorn.app import run_in_app_context
from unicorn.db.base import Base
import unicorn.models


@run_in_app_context
def main():
    Base.metadata.drop_all(unicorn.db.connection.engine)
    Base.metadata.create_all(unicorn.db.connection.engine)


if __name__ == '__main__':
    main()
