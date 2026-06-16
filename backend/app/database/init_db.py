from app.database.connection import Base, engine

def init_db():
    """
    Initializes the database by creating all tables defined in the Base metadata.
    Make sure to import all your SQLAlchemy models before calling this function
    so that they are registered with Base.metadata.
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

if __name__ == "__main__":
    init_db()
