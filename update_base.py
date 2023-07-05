from base.models import Base
from utils.config import engine

if __name__ == '__main__':
    Base.metadata.create_all(engine)
