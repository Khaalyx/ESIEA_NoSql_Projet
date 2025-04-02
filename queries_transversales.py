# Questions Transversales
from database import get_neo4j
import streamlit as st
import pandas as pd

driver = get_neo4j()

# 27. Quels sont les films qui ont des genres en commun mais qui ont des réalisateurs différents ?
def common_genre_different_director():
    query = """
    MATCH (f:Film)-[:APPARTIENT_A]->(g:Genre)
    WITH f, COLLECT(DISTINCT g.name) AS genres

    MATCH (f)-[:A_REALISE]-(r:Realisateur)
    WITH genres, f.title AS film, r.name AS realisateur
    ORDER BY genres, film

    WITH genres, COLLECT({film: film, realisateur: realisateur}) AS films_info
    WHERE SIZE(films_info) > 1

    RETURN genres, films_info;
    """

    records, _, _ = driver.execute_query(query, database_="neo4j")

    str = ""
    for record in records:
        genres = ", ".join(record["genres"])
        films_info = record["films_info"]

        films_details = "  \n".join(
            [f"- **{f['film']}** ({f['realisateur']})" for f in films_info]
        )

        str += f"**{genres}**  \n{films_details}\n\n"

    st.info(str)


# 28. Recommander des films aux utilisateurs en fonction des préférences d’un acteur donné.
def recommend_film_by_actor_preferences(actor):
    query = """
    MATCH (a:Actor {name: $actor})-[:A_JOUE]->(f:Film)-[:APPARTIENT_A]->(g:Genre)
    WITH g, COUNT(*) AS genre_count
    ORDER BY genre_count DESC
    LIMIT 3  

    WITH COLLECT(g) AS genres_favoris

    MATCH (rec:Film)-[:APPARTIENT_A]->(g)
    WHERE g IN genres_favoris

    WITH rec, COLLECT(DISTINCT g.name) AS genres_list
    ORDER BY rec.votes DESC
    RETURN rec.title AS Film_Recommande, genres_list AS Genres
    LIMIT 5
    """

    records, _, _ = driver.execute_query(query, database_="neo4j", actor=actor)

    output_str = ""
    for record in records:
        genres = ", ".join(record["Genres"])
        output_str += f"**{record['Film_Recommande']}** ({genres})  \n"

    st.info(output_str)


# 29. Créer une relation de ”concurrence” entre réalisateurs ayant réalisé des films similaires la même année.
def create_concurrence():
    query = """
    MATCH (f1:Film)-[:APPARTIENT_A]->(g:Genre)<-[:APPARTIENT_A]-(f2:Film)
    WHERE f1.year = f2.year AND f1 <> f2
    WITH f1, f2, COLLECT(DISTINCT g.name) AS genres_communs
    MATCH (d1:Realisateur)-[:A_REALISE]->(f1)
    MATCH (d2:Realisateur)-[:A_REALISE]->(f2)
    WHERE d1 <> d2
    MERGE (d1)-[:EN_CONCURRENCE_AVEC]->(d2)
    """
    
    try:
        driver.execute_query(query, database_="neo4j")
        st.success("Relation EN_CONCURRENCE_AVEC créée avec succès.")
    except Exception as e:
        st.error(e)

# 30. Identifier les collaborations les plus fréquentes entre réalisateurs et acteurs, puis analyser si ces collaborations sont associées à un succès commercial ou critique
def collab_success():
    query = """
    MATCH (r:Realisateur)-[:A_REALISE]->(f:Film)<-[:A_JOUE]-(a:Actor)
    WITH r, a, COUNT(f) AS collaboration_count, 
        AVG(CASE WHEN f.revenue IS NOT NULL AND f.revenue <> "" THEN toFloat(f.revenue) ELSE 0 END) AS avg_revenue,
        AVG(CASE WHEN f.metascore IS NOT NULL AND f.metascore <> "" THEN toFloat(f.metascore) ELSE 0 END) AS avg_metascore
    RETURN r.name AS Realisateur, a.name AS Actor, collaboration_count, avg_revenue, avg_metascore
    ORDER BY collaboration_count DESC
    LIMIT 10
    """

    result, _, _ = driver.execute_query(query, database_="neo4j")

    # Définir des seuils pour les succès commercial et critique
    SUCCES_COMMERCIAL = 100
    SUCCES_CRITIQUE= 70

    # Convertir les résultats en liste de dictionnaires
    records = []
    for record in result:
        records.append({
            "Realisateur": record["Realisateur"],
            "Actor": record["Actor"],
            "collaboration_count": record["collaboration_count"],
            "avg_revenue": record["avg_revenue"],
            "avg_metascore": record["avg_metascore"]
        })

    df = pd.DataFrame(records)

    df["Succès Commercial"] = df["avg_revenue"].apply(lambda x: "Oui" if x >= SUCCES_COMMERCIAL else "Non")
    df["Succès Critique"] = df["avg_metascore"].apply(lambda x: "Oui" if x >= SUCCES_CRITIQUE else "Non")

    # Afficher le DataFrame avec Streamlit
    st.dataframe(df, column_config={
            "Realisateur": "Réalisateur",
            "Actor": "Acteur",
            "collaboration_count": "Nombre de collaboration",
            "avg_revenue": "Revenue moyen",
            "avg_metascore": "Score moyen",
            "Succès Commercial": "Succès Commercial",
            "Succès Critique": "Succès Critique"
        },
        hide_index=True
    )