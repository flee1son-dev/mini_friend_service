import unittest
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from backend.core.database import Base, get_db
from backend.main import app


"""Setting up SQLite in-memory"""
DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

"""Base class for tests"""
class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """create all tables before testing"""
        Base.metadata.create_all(engine)
    
    @classmethod
    def tearDownClass(cls):
        """delete all tables after testing"""
        Base.metadata.drop_all(engine)
        engine.dispose()


    def setUp(self):
        """Create a new session before each test"""
        self.db = TestingSessionLocal()

        self.db.execute(text("DELETE FROM users"))
        self.db.execute(text("DELETE FROM friendships"))
        self.db.commit()


        
    def tearDown(self):
        """Roll back changes after each test"""
        self.db.rollback()
        self.db.close()

        app.dependency_overrides.clear()


