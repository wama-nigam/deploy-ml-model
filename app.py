from flask import Flask, render_template, request, jsonify
import numpy as np
import pandas as pd
import requests
import pickle
import difflib
app = Flask(__name__)
model = pickle.load(open(
    'C:/Users/DELL/Desktop/deploying model/movieRecommend/MLmodel/model.pkl', 'rb'))

app = Flask(__name__, template_folder='template')
app.static_folder = 'static'
movies = pd.read_csv(
    'C:/Users/DELL/Desktop/deploying model/movieRecommend/datasets/movies.csv')
required = ['genres', 'keywords', 'title', 'cast', 'director']
for idx in required:
    movies[idx] = movies[idx].fillna('')

json_obj=[]

@app.route("/", methods=['GET', 'POST'])
def home():
    json_obj.clear()
    return render_template("index.html")


@app.route('/recommend', methods=['POST'])
def recommend():
    if (request.method == 'POST'):
        movie_name = request.form.get('movieName')

        def find_movie(movie_name, movies):

            list_of_title = movies['title'].tolist()

            # print(list_of_title)
            close_match = difflib.get_close_matches(movie_name, list_of_title)
            # print(close_match,close_match[0])
            index = movies[movies.title == close_match[0]]['index'].values[0]
            # print(index)
            similarity_score = list(enumerate(model[index]))
            # print(similarity_score)
            sorted_sim_score = sorted(
                similarity_score, key=lambda x: x[1], reverse=True)
            # print(sorted_sim_score)

            # print top 10 movies
            i = 1
            top_suggestions = []
            for idx in sorted_sim_score:
                m_idx = idx[0]
                name = movies[movies.index == m_idx]['title'].values[0]
                if i <= 10:
                    top_suggestions.append(name)
                else:
                    break
                i += 1
            return top_suggestions

        top_sug = find_movie(movie_name, movies)

        def helper(name):
            api_key = '7d8fd2f8'
            base_url = 'http://www.omdbapi.com/'

            movie_name = name  # Replace with the movie name you want to search for

            # Create a dictionary of query parameters
            params = {
                'apikey': api_key,
                't': movie_name  # 't' stands for 'title'
            }

            # Make a GET request to fetch movie data
            response = requests.get(base_url, params=params)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                data = response.json()

                # Check if the response contains movie data
                if data.get('Response') == 'True':
                    return data
                #     # Extract movie details from the response
                #     movie_title = data['Title']
                #     movie_plot = data['Plot']
                #     movie_poster = data['Poster']
                #     movie_year = data['Year']

                #     print(f"Movie Title: {movie_title}")
                #     print(f"Plot: {movie_plot}")
                #     print(f"Poster URL: {movie_poster}")
                #     print(f"Year: {movie_year}")
                else:
                    print("Movie not found.")
            else:
                print("Error: Unable to fetch data from OMDB API.")
        
        for name in top_sug:
            json_obj.append(helper(name))

    return render_template('recommend.html', recommendations=json_obj)


app.run(debug=True)
