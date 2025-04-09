import streamlit as st
import requests
import pandas as pd

API_KEY = "2ecec1e390mshbb4646b5177fc1ep1e38f7jsn4ff0e195cb54"
API_URL = "https://movie-database-alternative.p.rapidapi.com/"
FLIXSTER_API_URL = "https://flixster.p.rapidapi.com/search"

headers = {
    'X-RapidAPI-Key': API_KEY,
    'X-RapidAPI-Host': "movie-database-alternative.p.rapidapi.com"
}


def get_movie_recommendation(genre, year, language):
    params = {
        's': genre,
        'y': year,
        'l': language,
        'r': 'json',
        'page': '1'
    }
    response = requests.get(API_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_imdb_rating(imdb_id):
    url = f"{API_URL}?i={imdb_id}&r=json"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if 'imdbRating' in data:
            return data['imdbRating']
    return None

def show_question_page(question, question_index):
    st.title(question['title'])
    if question['type'] == 'select':
        answer = st.selectbox(question['label'], question['options'])
    elif question['type'] == 'number':
        min_value = question['options']['min_value']
        max_value = question['options']['max_value']
        answer = st.number_input(question['label'], min_value=min_value, max_value=max_value, value=min_value, key=f"{question_index}_input")
        if not min_value <= answer <= max_value:
            st.error(f"Please enter a year between {min_value} and {max_value}.")
            answer = None
    elif question['type'] == 'text':
        answer = st.text_input(question['label'], **question['options'], key=f"{question_index}_input")
    return answer

# Function to get theaters based on zip code and radius
def get_theaters(zip_code, radius):
    url = "https://flixster.p.rapidapi.com/theaters/list"
    headers = {
        "X-RapidAPI-Key": "2ecec1e390mshbb4646b5177fc1ep1e38f7jsn4ff0e195cb54",
        "X-RapidAPI-Host": "flixster.p.rapidapi.com"
    }
    params = {
        "zipCode": zip_code,
        "radius": radius
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

def main():
    if 'current_question_index' not in st.session_state:
        st.session_state['current_question_index'] = 0
        st.session_state['answers'] = [None, None, None]

    questions = [
        {"title": "Select Genre", "type": "select", "label": "Select a genre:", "options": ["Action", "Comedy", "Drama", "Horror", "Sci-Fi"]},
        {"title": "Enter Year", "type": "number", "label": "Enter a year (1900-2024):", "options": {"min_value": 1900, "max_value": 2024}},
        {"title": "Select Language", "type": "select", "label": "Select a language:", "options": ["English", "Spanish", "French", "German", "Other"]},
    ]

    current_question_index = st.session_state['current_question_index']

    if current_question_index < len(questions):
        st.progress((current_question_index + 1) / len(questions))
        answer = show_question_page(questions[current_question_index], current_question_index)
        st.session_state['answers'][current_question_index] = answer

        if st.button("Previous") and current_question_index > 0:
            st.session_state['current_question_index'] -= 1
            st.rerun()

        if st.button("Next") and answer is not None:
            st.session_state['current_question_index'] += 1
            st.rerun()

    else:
        if None in st.session_state['answers']:
            st.warning("Please answer all questions.")
        else:
            genre, year, language = st.session_state['answers']
            movie_info = get_movie_recommendation(genre, year, language)

            if movie_info and 'Search' in movie_info:
                st.subheader("🎬 Recommended Movies")
                for movie in movie_info['Search']:
                    st.write(f"**Title:** {movie['Title']}")
                    if movie['Poster'] != 'N/A':
                        st.image(movie['Poster'], caption=movie['Title'], use_column_width=True)
                    st.write(f"**Year:** {movie['Year']}")
                    imdb_id = movie['imdbID']
                    imdb_rating = get_imdb_rating(imdb_id)
                    st.write(f"**IMDb Rating:** {imdb_rating if imdb_rating else 'Not available'}")
                    st.write("---")
            else:
                st.error("No movie recommendation found.")
                return

            # 🔻 Theater Location Input Section (separate from movie results)
            st.subheader("📍 Find Theaters Near You")
            zip_code = st.text_input("Enter Zip Code", "90002", key="zip_code_input_global")
            radius = st.text_input("Enter Radius (in miles)", "50", key="radius_input_global")

            if st.button("Get Theaters"):
                with st.spinner("Getting theaters near you..."):
                    theaters_data = get_theaters(zip_code, radius)
                    theaters = theaters_data.get('data', {}).get('theaters', [])
                    if theaters:
                        st.subheader("🎭 Theaters Nearby")
                        theater_list = []
                        for theater in theaters:
                            name = theater.get('name', 'No Name')
                            address = theater.get('address', 'No Address')
                            lat = theater.get('latitude')
                            lon = theater.get('longitude')
                            if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                                theater_list.append({'Theater Name': name, 'Theater Address': address, 'LAT': lat, 'LON': lon})
                        df = pd.DataFrame(theater_list)
                        st.map(df)
                    else:
                        st.info("No theaters found near your location.")


if __name__ == "__main__":
    main()
