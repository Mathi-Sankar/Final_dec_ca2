from flask import Flask, jsonify, render_template, request
import requests

app = Flask(__name__)

IMDB_SEARCH_URL = "https://imdb8.p.rapidapi.com/title/find"
IMDB_CAST_URL = "https://imdb8.p.rapidapi.com/title/get-full-credits"
HEADERS = {
    'x-rapidapi-key': 'd9045911f0msha288e25cc902400p1dd65ejsn15a51e9fa5c0',
    'x-rapidapi-host': 'imdb8.p.rapidapi.com',
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/movie_cast', methods=['GET'])
def get_movie_cast():
    movie_name = request.args.get('q')
    if not movie_name:
        return jsonify({'error': 'Movie name is required'}), 400
    
    try:
        params = {'q': movie_name}
        search_response = requests.get(IMDB_SEARCH_URL, headers=HEADERS, params=params)
        search_response.raise_for_status()
        search_data = search_response.json()
        results = search_data.get('results', [])
        if not results:
            return jsonify({'error': 'No movies found'}), 404
        
        movie = results[0]
        imdb_id = movie.get('id', '').replace('/title/', '').replace('/', '')
        
        params = {'tconst': imdb_id}
        cast_response = requests.get(IMDB_CAST_URL, headers=HEADERS, params=params)
        cast_response.raise_for_status()
        cast_data = cast_response.json()
        
        if 'cast' not in cast_data:
            return jsonify({'error': 'No cast details found'}), 404

        cast = cast_data.get('cast', [])
        top_cast = [
            {
                'name': member.get('name', 'Unknown'),
                'character': member.get('characters', ['Unknown'])[0]
            }
            for member in cast[:5]
        ]
        url = "https://film-show-ratings.p.rapidapi.com/item/"

        querystring = {"id":imdb_id}

        headerss = {
            "x-rapidapi-key": "ecaf0c8bccmshee3d876d67e2a4ap18a848jsn1d9f76910f29",
            "x-rapidapi-host": "film-show-ratings.p.rapidapi.com"
        }

        response = requests.get(url, headers=headerss, params=querystring)
        dataa = response.json()
        details = dataa['result']['overview']
        return jsonify({
            'title': movie.get('title', 'Unknown'),
            'imdb_id': imdb_id,
            'top_cast': top_cast,
            'details' : details,
        })
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to fetch data: {str(e)}'}), 500

@app.route('/api/search/cast', methods=['GET'])
def search_by_cast():
    cast_name = request.args.get('q')
    if not cast_name:
        return jsonify({'error': 'Cast name is required'}), 400
    
    try:
        params = {'q': cast_name}
        response = requests.get(IMDB_SEARCH_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        
        data = response.json()
        results = data.get('results', [])
        movies = [
            {
                'title': result.get('title', 'Unknown'),
                'imdb_id': result.get('id', '').replace('/title/', '').replace('/', '')
            }
            for result in results if 'title' in result
        ]
        return jsonify({'movies': movies[:5]}) 
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to search cast: {str(e)}'}), 500

if __name__ == '__main__':
    app.run()