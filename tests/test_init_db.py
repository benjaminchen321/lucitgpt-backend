from init_db import Base, engine

def test_create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        assert True
    except Exception as e:
        print("Error creating tables:", e)
        assert False

def test_drop_tables():
    try:
        Base.metadata.drop_all(bind=engine)
        assert True
    except Exception as e:
        print("Error dropping tables:", e)
        assert False
