# Requêtes MongoDB

import streamlit as st
from database import get_mongodb
import pandas as pd
from scipy.stats import pearsonr

db = get_mongodb()
collection = db["films"]

# 1. Afficher l'année où le plus grand nombre de films ont été sortis.
def year_with_most_films():
    year = collection.aggregate([
        { "$group": { "_id": "$year", "count": { "$sum": 1 } } },
        { "$sort": { "count": -1 } },
        { "$limit": 1 }
    ])
    
    for y in year:
        st.info(f"{y['_id']} ({y['count']} films)")

# 2. Quel est le nombre de films sortis après l'année 1999.
def count_films_after_1999():
    nb_films = collection.count_documents({"year": {"$gt": 1999}})

    st.info(nb_films)

# 3. Quelle est la moyenne des votes des films sortis en 2007.
def avg_votes_after_2007():
    avg = collection.aggregate([
        { "$match": { "year": 2007 } },
        { "$group": { "_id": None, "avg_votes": {"$avg": "$Votes" } } }
    ])

    for result in avg:
        st.info(result['avg_votes'])

# 4. Afficher un histogramme qui permet de visualiser le nombre de films par année.
def films_per_year():
    results = collection.aggregate([
        { "$match": { "year": { "$exists": True } } },
        { "$group": { "_id": "$year", "count": { "$sum": 1 } } },
        { "$sort": { "_id": 1 } }
    ])

    results = list(results)

    st.bar_chart(results, x="_id", y="count", x_label="Année", y_label="Nombre de films", stack=False)

 # 5. Quelles sont les genres de films disponibles dans la bases
def genres():
    genres = collection.aggregate([
        { "$project": { "genres": { "$split": ["$genre", ","] } } }, # Séparer les genres dans un tableau
        { "$unwind": "$genres" },
        { "$group": { "_id": None, "genres": { "$addToSet": "$genres" } } }
    ])

    all_genres = []
    for genre in genres:
        all_genres.extend(genre['genres'])

    genres_str = ", ".join(sorted(all_genres))

    st.info(genres_str)

# 6. Quel est le film qui a généré le plus de revenus.
def max_revenue_film():
    film = collection.find_one(
        { "Revenue (Millions)": { "$exists": True, "$ne": "" } },
        sort=[("Revenue (Millions)", -1)]
    )

    st.info(f"{film['title']} ({film['Revenue (Millions)']} millions)")

# 7. Quels sont les réalisateurs ayant réalisé plus de 5 films dans la base de données ?
def director_more_than_5_films():
    directors = collection.aggregate([
        { "$group": { "_id": "$Director", "count": { "$sum": 1 } } },
        { "$match": { "count": { "$gt": 5 } } }
    ])

    if not list(directors):
        st.info("Aucun réalisateur n'a réalisé plus de 5 films.")
    else:
        for director in directors:
            st.info(f"\t{director['_id']} ({director['count']} films)")

# 8. Quel est le genre de film qui rapporte en moyenne le plus de revenus ?
def genre_with_more_revenue():
    genres_revenue = collection.aggregate([
        { "$project": { "genres": { "$split": ["$genre", ","] }, "Revenue (Millions)": 1 } },
        { "$unwind": { "path": "$genres" } },
        { "$group": {
            "_id": "$genres",
            "average_revenue": { "$avg": "$Revenue (Millions)" }
        }},
        { "$sort": { "average_revenue": -1 } },
        { "$limit": 1 }
    ])

    for genre in genres_revenue:
        st.info(f"{genre['_id']} ({"{:.2f}".format(genre['average_revenue'])} millions)")

# 9. Quels sont les 3 films les mieux notés (rating) pour chaque décennie (1990-1999, 2000-2009, etc.) ?
def top_movies_by_decade():
    top_movies_by_decade = collection.aggregate([
        { "$match": { "year": { "$exists": True, "$ne": None }, "Metascore": { "$ne": "" } } },
        { "$addFields": { "decade": { "$subtract": ["$year", { "$mod": ["$year", 10] }] } } },
        { "$sort": { "Metascore": -1 } },
        { "$group": {
            "_id": "$decade",
            "top_movies": { "$push": { "title": "$title", "Metascore": "$Metascore" } }
        }},
        { "$project": { "top_movies": { "$slice": ["$top_movies", 3] } } },
        { "$sort": { "_id": 1 } }
    ])

    str = ""

    for decade in top_movies_by_decade:
        str += f"**Décennie {decade['_id']}**  \n"
        for movie in decade['top_movies']:
            str += f"- {movie['title']} ({movie['Metascore']})  \n"
        str += "  \n"

    st.info(str)


# 10. Quel est le film le plus long (Runtime) par genre ?
def longest_movie_genre():
    longest_movies = collection.aggregate([
        { "$project": { "genres": { "$split": ["$genre", ","] }, "title": 1, "Runtime (Minutes)": 1 } },
        { "$unwind": "$genres" },
        { "$sort": { "Runtime (Minutes)": -1 } },
        { "$group": {
            "_id": "$genres",
            "longest_movie": { "$first": { "title": "$title", "runtime": "$Runtime (Minutes)" } }
        }},
        { "$sort": { "_id": 1 } }
    ])

    str = ""
    for movie in longest_movies:
        str += f"**{movie['_id']}** : {movie['longest_movie']['title']} ({movie['longest_movie']['runtime']} min)  \n"

    st.info(str)

# 11. Créer une vue MongoDB affichant uniquement les films ayant une note supérieure à 80 (Metascore) et générant plus de 50 millions de dollars.
def create_view_high_rated_revenue():
    try:
        db.command({
            "create": "HighRatedRevenueFilms",
            "viewOn": "films",
            "pipeline": [
                { "$match": { "Metascore": { "$gt": 80 }, "Revenue (Millions)": { "$gt": 50 } } }
            ]
        })
        
        st.success("La vue 'HighRatedRevenueFilms' a été créée avec succès.")
    except Exception as e:
        st.error(str(e))

# 12. Calculer la corrélation entre la durée des films (Runtime) et leur revenu (Revenue). (réaliser une analyse statistique.)
def analyze_runtime_revenue_correlation():
    data = collection.find(
        { "Runtime (Minutes)": { "$exists": True, "$ne": "" }, "Revenue (Millions)": { "$exists": True, "$ne": "" } },
        { "Runtime (Minutes)": 1, "Revenue (Millions)": 1, "_id": 0 }
    )

    df = pd.DataFrame(list(data))

    df["Runtime (Minutes)"] = pd.to_numeric(df["Runtime (Minutes)"], errors="coerce")
    df["Revenue (Millions)"] = pd.to_numeric(df["Revenue (Millions)"], errors="coerce")

    df = df.dropna()

    # Calcul de la corrélation de Pearson
    correlation, _ = pearsonr(df["Runtime (Minutes)"], df["Revenue (Millions)"])

    interpretation = ""
    if correlation == 1:
        interpretation = "Corrélation parfaite"
    elif correlation >= 0.8:
        interpretation = "Corrélation forte"
    elif correlation >= 0.5:
        interpretation = "Corrélation modérée"
    elif correlation >= 0.2:
        interpretation = "Corrélation faible"
    elif correlation == 0:
        interpretation = "Aucune corrélation"

    st.info(f"**Coefficient de corrélation de Pearson :** {correlation:.2f}  \n"
            f"{interpretation}")


# 13. Y a-t-il une évolution de la durée moyenne des films par décennie ?
def avg_runtime_per_decade():
    results = collection.aggregate([
        { "$match": { "year": { "$exists": True, "$ne": None }, "Runtime (Minutes)": { "$exists": True, "$ne": "" } } },
        { "$addFields": { "decade": { "$subtract": ["$year", { "$mod": ["$year", 10] }] } } },
        { "$group": { "_id": "$decade", "avg_runtime": { "$avg": "$Runtime (Minutes)" } } },
        { "$sort": { "_id": 1 } }
    ])

    results = list(results)

    st.line_chart(results, x="_id", y="avg_runtime", x_label="Décennie", y_label="Durée moyenne (Minutes)")