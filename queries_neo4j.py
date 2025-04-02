from database import get_neo4j
import streamlit as st
import networkx as nx
import json

driver = get_neo4j()

# 14. Acteur ayant joué dans le plus grand nombre de films
def actor_with_most_films():
    query = """
    MATCH (a:Actor)-[:A_JOUE]->(f:Film)
    RETURN a.name AS Acteur, COUNT(f) AS nbFilms
    ORDER BY nbFilms DESC
    LIMIT 1
    """

    records, _, _ = driver.execute_query(query, database_="neo4j")

    for record in records:
        st.info(f"{record['Acteur']} ({record['nbFilms']} films)")

# 15. Quels sont les acteurs ayant joué dans des films où l’actrice Anne Hathaway a également joué ?
def get_coactors_of_anne_hathaway():
    query = """
    MATCH (a:Actor)-[:A_JOUE]->(f:Film)<-[:A_JOUE]-(anne:Actor {name: "Anne Hathaway"})
    WHERE a.name <> "Anne Hathaway"
    RETURN DISTINCT a.name AS Acteur
    """

    records, _, _ = driver.execute_query(query, database_="neo4j")

    str = ""
    for record in records:
        str += f"{record['Acteur']}  \n"
    
    st.info(str)

# 16. Quel est l’acteur ayant joué dans des films totalisant le plus de revenus ?
def most_rich_actor():
    query = """
    MATCH (a:Actor)-[:A_JOUE]->(f:Film)
    WHERE f.revenue IS NOT NULL
    WITH a.name AS Acteur, SUM(toFloat(f.revenue)) AS TotalRevenus
    ORDER BY TotalRevenus DESC
    LIMIT 1
    RETURN Acteur, TotalRevenus
    """

    records, _, _ = driver.execute_query(query, database_="neo4j")

    str = ""
    for record in records:
        str += f"{record['Acteur'] } ({record['TotalRevenus']} millions)"
    
    st.info(str)

# 17. Quelle est la moyenne des votes ?
def avg_votes():
    query = """
    MATCH (f:Film)
    WHERE f.votes IS NOT NULL
    RETURN avg(f.votes) AS avgVotes
    """

    records, _, _ = driver.execute_query(query, database_="neo4j")

    str = ""
    for record in records:
        str += f"{ "{:.2f}".format(record['avgVotes']) } votes"
    
    st.info(str)

# 18. Quel est le genre le plus représenté dans la base de données ?
def genre_with_most_films():
    query = """
    MATCH (f:Film)-[:APPARTIENT_A]->(g:Genre)
    RETURN g.name AS Genre, COUNT(f) AS NombreFilms
    ORDER BY NombreFilms DESC
    LIMIT 1
    """

    records, _, _ = driver.execute_query(query, database_="neo4j")

    str = ""
    for record in records:
        str += f"{record['Genre'] } ({record['NombreFilms']} films)"
    
    st.info(str)

# 19. Quels sont les films dans lesquels les acteurs ayant joué avec vous ont également joué ?
def create_my_actor():
    query = """
    MERGE (a:Actor {name: "Me"})
    WITH a
    MATCH (f:Film {title: "Interstellar"})
    MERGE (a)-[:A_JOUE]->(f)
    """

    try:
        driver.execute_query(query, database_="neo4j")
        st.success("Acteur créé avec succès.")
    except Exception as e:
        st.error(e)

def my_coactors_films():
    create_my_actor()

    query = """
    MATCH (me:Actor {name: "Me"})-[:A_JOUE]->(myMovies:Film)<-[:A_JOUE]-(coActor:Actor)
    MATCH (coActor)-[:A_JOUE]->(otherMovies:Film)
    WHERE NOT (me)-[:A_JOUE]->(otherMovies)
    RETURN DISTINCT otherMovies.title AS Films
    """

    records, _, _ = driver.execute_query(query, database_="neo4j")

    str = ""
    for record in records:
        str += f"{record['Films'] }  \n"
    
    st.info(str)

# 20. Quel réalisateur Director a travaillé avec le plus grand nombre d’acteurs distincts ?
def director_with_most_distinct_actors():
    query = """
    MATCH (d:Realisateur)-[:A_REALISE]->(f:Film)<-[:A_JOUE]-(a:Actor)
    WITH d, COUNT(DISTINCT a) AS nb_acteurs
    ORDER BY nb_acteurs DESC
    LIMIT 1
    RETURN d.name AS realisateur, nb_acteurs
    """

    records, _, _ = driver.execute_query(query, database_="neo4j")

    str = ""
    for record in records:
        str += f"{record['realisateur']} ({record['nb_acteurs']} acteurs)"
    
    st.info(str)

# 21. Quels sont les films les plus ”connectés”, c’est-à-dire ceux qui ont le plus d’acteurs en commun avec d’autres films ?
def most_connected_films():
    query = """
    MATCH (f1:Film)<-[:A_JOUE]-(a:Actor)-[:A_JOUE]->(f2:Film)
    WHERE f1 <> f2
    WITH f1, COUNT(DISTINCT a) AS nb_acteurs_communs
    ORDER BY nb_acteurs_communs DESC
    LIMIT 5
    RETURN f1.title AS film, nb_acteurs_communs
    """

    records, _, _ = driver.execute_query(query, database_="neo4j")

    str = ""
    for record in records:
        str += f"{record['film']} ({record['nb_acteurs_communs']} acteurs)  \n"
    
    st.info(str)

# 22. Trouver les 5 acteurs ayant joué avec le plus de réalisateurs différents.
def actors_with_most_directors():
    query = """
    MATCH (a:Actor)-[:A_JOUE]->(f:Film)<-[:A_REALISE]-(r:Realisateur)
    WITH a, COUNT(DISTINCT r) AS nb_realisateurs
    ORDER BY nb_realisateurs DESC
    LIMIT 5
    RETURN a.name AS acteur, nb_realisateurs
    """

    records, _, _ = driver.execute_query(query, database_="neo4j")

    str = ""
    for record in records:
        str += f"{record['acteur']} ({record['nb_realisateurs']} réalisateurs)  \n"
    
    st.info(str)

# Récupérer tous les acteurs pour les selectbox
def get_all_actors():
    query = """
    MATCH (a:Actor)
    RETURN a.name AS Acteur
    ORDER BY a.name
    """
    
    records, _, _ = driver.execute_query(query, database_="neo4j")
    acteurs_list = [record['Acteur'] for record in records]

    return list(acteurs_list)

# 23. Recommander un film à un acteur en fonction des genres des films où il a déjà joué.
def recommendations_for_actors(actor):
    query = """
    MATCH (a:Actor {name: $actor})-[:A_JOUE]->(f:Film)-[:APPARTIENT_A]->(g:Genre)
    WITH a, g, COUNT(*) AS genre_count
    ORDER BY genre_count DESC
    LIMIT 1

    MATCH (rec:Film)-[:APPARTIENT_A]->(g)
    WHERE NOT EXISTS { (a)-[:A_JOUE]->(rec) }
    WITH rec, g
    ORDER BY rec.votes DESC
    RETURN rec.title AS Film_Recommande, g.name AS Genre, rec.votes AS Nombre_De_Votes
    LIMIT 1
    """

    records, _, _ = driver.execute_query(query, database_="neo4j", actor=actor)

    str = ""
    if records:
        for record in records:
            str += f"**{record['Film_Recommande']}** ({record['Genre']} - {record['Nombre_De_Votes']} votes)"
    else:
        str = "Pas de recommandation pour cet acteur."
        
    st.info(str)

# 24. Créer une relation INFLUENCE_PAR entre les réalisateurs en se basant sur des similarités dans les genres de films qu’ils ont réalisés
def create_influence_par():
    query = """
    MATCH (d1:Realisateur)-[:A_REALISE]->(f1:Film)-[:APPARTIENT_A]->(g:Genre)
    WITH d1, COLLECT(g) AS genres1
    MATCH (d2:Realisateur)-[:A_REALISE]->(f2:Film)-[:APPARTIENT_A]->(g)
    WHERE d1 <> d2
    WITH d1, d2, COLLECT(g) AS genres2, genres1
    WITH d1, d2, SIZE([genre IN genres1 WHERE genre IN genres2]) AS common_genres_count
    WHERE common_genres_count > 0
    MERGE (d1)-[:INFLUENCE_PAR {common_genres: common_genres_count}]->(d2)
    """

    try:
        driver.execute_query(query, database_="neo4j")
        st.success("Relation INFLUENCE_PAR créée avec succès.")
    except Exception as e:
        st.error(e)


# 25. Quel est le ”chemin” le plus court entre deux acteurs donnés (ex : Tom Hanks et Scarlett Johansson) ?
def shortest_path_between_actors(actor1, actor2):
    query = """
    MATCH (a1:Actor {name: $actor1}), (a2:Actor {name: $actor2})
    MATCH path = shortestPath((a1)-[:A_JOUE*]-(a2))
    RETURN path
    """
    try:
        records, _, _ = driver.execute_query(query, database_="neo4j", actor1=actor1, actor2=actor2)

        if records:
            path = records[0]["path"]

            formatted_path = " → ".join(node["name"] if "name" in node else node["title"] for node in path.nodes)
            st.info(f"Chemin le plus court entre {actor1} et {actor2} :\n\n{formatted_path}")
        else:
            st.info(f"Aucun chemin trouvé entre {actor1} et {actor2}")

    except Exception as e:
        st.error(e)

# 26. Analyser les communautés d’acteurs : Quels sont les groupes d’acteurs qui ont tendance à travailler ensemble ? (Utilisation d’algorithmes de détection de communautés comme Louvain.)
def analyze_actor_communities():
    query = """
    MATCH (a1:Actor)-[:A_JOUE]->(f:Film)<-[:A_JOUE]-(a2:Actor)
    WHERE a1 <> a2
    RETURN a1.name AS actor1, a2.name AS actor2, COUNT(f) AS weight
    """

    with driver.session() as session:
        result = session.run(query)
        test = [(record["actor1"], record["actor2"], record["weight"]) for record in result]

    # Construire le graphe
    G = nx.Graph()
    for actor1, actor2, weight in test:
        G.add_edge(actor1, actor2, weight=weight)

    # Appliquer Louvain
    partition = nx.community.louvain_communities(G)

    # Regrouper les acteurs par communauté
    communities = {}
    for community_id, actor in enumerate(partition):
        communities.setdefault(community_id, []).append(actor)

    result_str = ""
    for community_id, actors in communities.items():
        flat_actors = {str(actor) for group in actors for actor in group}  # Aplatis les sets
        result_str += (f"**Communauté {community_id} :**  \n{', '.join(sorted(flat_actors))}  \n\n")

    st.info(result_str)