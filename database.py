# Fichier de connexion aux bases de données
import pymongo
from neo4j import GraphDatabase
import os
from dotenv  import load_dotenv

load_dotenv()

MONGO_URI=os.getenv("MONGO_URI")

NEO4J_URI=os.getenv("NEO4J_URI")
NEO4J_USERNAME=os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD=os.getenv("NEO4J_PASSWORD")

# Connection à la base de données MongoDB
def get_mongodb():
    client = pymongo.MongoClient(MONGO_URI)
    print(MONGO_URI)
    try:
        # Sélectionner la base de données
        db = client["entertainment"]
        return db
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")

# Connection à la base de données Neo4J
def get_neo4j():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        driver.verify_connectivity()
        return driver
    except Exception as e:
        print(f"Failed to connect to Neo4j: {e}")