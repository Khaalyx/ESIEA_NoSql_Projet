import re
from database import get_mongodb
from database import get_neo4j

db = get_mongodb()
films_collection = db['films']

driver = get_neo4j()

def create_nodes_and_relations():
    with driver.session() as session:
        
        # extraction des données depuis mongoDB
        for film in films_collection.find():
            title = film.get("title")

            if not title:
                continue

            genres = film.get("genre", "").split(",")
            director = film.get("Director")
            actors = re.split(r',\s*', film.get("Actors", ""))
            
            # Création des noeuds Film
            session.run(
                """
                MERGE (f:Film {title: $title})
                SET f.year = $year, f.votes = $votes, f.revenue = $revenue, f.rating = $rating, f.metascore = $metascore
                """,
                title=title,
                year=film.get("year"),
                votes=film.get("Votes"),
                revenue=film.get("Revenue (Millions)"),
                rating=film.get("rating"),
                metascore=film.get("Metascore")
            )

            # Realisateur
            session.run(
                """
                MERGE (d:Realisateur {name: $director})
                """,
                director=director
            )
            
            # Relation A_REALISE
            session.run(
                """
                MATCH (f:Film {title: $title})
                MATCH (d:Realisateur {name: $director})
                MERGE (d)-[:A_REALISE]->(f)
                """,
                title=title,
                director=director
            )

            # Création des noeuds Genre et des relations APPARTIENT_A
            for genre in genres:
                session.run(
                    """
                    MERGE (g:Genre {name: $genre})
                    WITH g
                    MATCH (f:Film {title: $title})
                    MERGE (f)-[:APPARTIENT_A]->(g)
                    """,
                    genre=genre.strip(),
                    title=title
                )

            # Création des noeuds Actor et des relations A_JOUE
            for actor in actors:
                session.run(
                    """
                    MERGE (a:Actor {name: $actor})
                    WITH a
                    MATCH (f:Film {title: $title})
                    MERGE (a)-[:A_JOUE]->(f)
                    """,
                    actor=actor.strip(),
                    title=title
                )

def main():
    create_nodes_and_relations()
    print("Les données ont été transférées de MongoDB vers Neo4j.")

if __name__ == "__main__":
    main()
