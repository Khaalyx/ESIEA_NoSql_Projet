import streamlit as st
import queries_mongo as mongo
import queries_neo4j as neo4j
import queries_transversales as transversales

st.title("NoSQL Databases - Projet")
st.write("Exploration et Interrogation de Bases de Données NoSQL avec Python")

# Récupérer la liste des acteurs pour les selectbox
actors = neo4j.get_all_actors() 

st.divider() # --------------------------------------------

# ---------------------------------------------------------#
#                          MongoDB                         #
# ---------------------------------------------------------#

st.header("Requêtes MongoDB")

st.subheader("1. Année avec le plus de films")
mongo.year_with_most_films()

st.subheader("2. Nombre de films sortis après 1999")
mongo.count_films_after_1999()

st.subheader("3. Moyenne des votes des films sortis en 2007")
mongo.avg_votes_after_2007()

st.subheader("4. Nombre de films par année")
mongo.films_per_year()

st.subheader("5. Genres")
mongo.genres()

st.subheader("6. Le film ayant généré le plus de revenus")
mongo.max_revenue_film()

st.subheader("7. Réalisateurs ayant réalisé plus de 5 films")
mongo.director_more_than_5_films()

st.subheader("8. Le genre qui rapporte en moyenne le plus de revenus")
mongo.genre_with_more_revenue()

st.subheader("9. Les 3 films les mieux notés pour chaque décennie")
mongo.top_movies_by_decade()

st.subheader("10. Les films les plus longs par genre")
mongo.longest_movie_genre()

st.subheader("11. Créer une vue MongoDB affichant uniquement les films ayant une note supérieure à 80 (Metascore) et générant plus de 50 millions de dollars")
mongo.create_view_high_rated_revenue()

st.subheader("12. Corrélation entre la durée des films (Runtime) et leur revenu (Revenue)")
mongo.analyze_runtime_revenue_correlation()

st.subheader("13. Evolution de la durée moyenne des films par décennie")
mongo.avg_runtime_per_decade()

st.divider() # --------------------------------------------

# ---------------------------------------------------------#
#                           Neo4j                          #
# ---------------------------------------------------------#

st.header("Neo4J - Requêtes Cypher")

st.subheader("14. Acteur ayant joué dans le plus grand nombre de films")
neo4j.actor_with_most_films()

st.subheader("15. Co-acteurs d'Anne Hathaway")
neo4j.get_coactors_of_anne_hathaway()

st.subheader("16. Acteur ayant joué dans des films totalisant le plus de revenus")
neo4j.most_rich_actor()

st.subheader("17. Moyenne des votes")
neo4j.avg_votes()

st.subheader("18. Genre le plus représenté dans la base de données")
neo4j.genre_with_most_films()

st.subheader("19. Films de mes co-acteurs")
neo4j.my_coactors_films()

st.subheader("20. Réalisateur ayant travaillé avec le plus grand nombre d’acteurs distincts")
neo4j.director_with_most_distinct_actors()

st.subheader("21. Films les plus \"connectés\"")
neo4j.most_connected_films()

st.subheader("22. Les 5 acteurs ayant joué avec le plus de réalisateurs différents")
neo4j.actors_with_most_directors()

st.subheader("23. Recommander un film à un acteur en fonction des genres des films où il a déjà joué")
actor = st.selectbox("Sélectionner un acteur", actors, key="recommendations_for_actors")
neo4j.recommendations_for_actors(actor)

st.subheader("24. Création des relations INFLUENCE_PAR")
neo4j.create_influence_par()

st.subheader("25. Chemin le plus court entre deux acteurs donnés")
actor2 = st.selectbox("Sélectionner un acteur", actors, key="shortest_path_actor1", index=0)
actor3 = st.selectbox("Sélectionner un acteur", actors, key="shortest_path_actor2", index=1)
neo4j.shortest_path_between_actors(actor2, actor3)

st.subheader("26. Analyse des communautés d’acteurs")
neo4j.analyze_actor_communities()

st.divider() # --------------------------------------------

# ---------------------------------------------------------#
#                  Questions Transversales                 #
# ---------------------------------------------------------#

st.header("Questions transversales")

st.subheader("27. Quels sont les films qui ont des genres en commun mais qui ont des réalisateurs différents ?")
transversales.common_genre_different_director()

st.subheader("28. Recommander des films aux utilisateurs en fonction des préférences d’un acteur donné.")
actor4 = st.selectbox("Sélectionner un acteur", actors, key="recommend_film_by_actor_preferences")
transversales.recommend_film_by_actor_preferences(actor4)

st.subheader("29. Créer une relation de ”concurrence” entre réalisateurs ayant réalisé des films similaires la même année.")
transversales.create_concurrence()

st.subheader("30. Identifier les collaborations les plus fréquentes entre réalisateurs et acteurs, puis analyser si ces collaborations sont associées à un succès commercial ou critique")
transversales.collab_success()
