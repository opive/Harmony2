# from dotenv import load_dotenv
# import os
# import json
# import base64
# from requests import post
# from requests import get

# load_dotenv()

# client_id = os.getenv("CLIENT_ID")
# client_secret = os.getenv("CLIENT_SECRET")


# def get_token():
#     '''
#     creates the authorization string
#     takes in client ID and client secret
#     outputs them concatenated and encoded in base64

#     '''
#     auth_string = client_id + ":" + client_secret
#     auth_bytes = auth_string.encode("utf-8")
#     auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

#     url = "https://accounts.spotify.com/api/token"
#     headers = {
#     "Authorization": "Basic " + auth_base64, "Content-Type": "application/x-www-form-urlencoded"
#     } #SPACES MATTER WTF I ADDED A SPACE AFTER "BASIC" AND EVERYTHING WORKED
#     data = {"grant_type": "client_credentials"}
#     result = post(url, headers=headers, data=data)
#     json_result = json.loads(result.content)
#     token = json_result["access_token"]
#     return token

# def get_auth_header(token): #header is used to send future requests to API
#     return {"Authorization": "Bearer " + token}

# def search_for_artist(token, artist_name): #allows to search for artists, get their ID, and find associated track
#     url = "https://api.spotify.com/v1/search"
#     headers = get_auth_header(token)
#     query = f"?q={artist_name}&type=artist&limit=3"

#     query_url = url + query
#     result = get(query_url, headers=headers)
#     json_result = json.loads(result.content)["artists"]["items"]
#     if len(json_result) == 0:
#         print("Artist does not exist")
#         return None
    
#     return json_result[0]
     
# def get_artist_albums(token,artist_id):
#     url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
#     headers = get_auth_header(token)
#     result = get(url, headers = headers)
#     json_result = json.loads(result.content)
#     if "items" in json_result:
#         return json_result["items"]
#     else:
#         return None

# def get_related_artists(token,artist_id):
#     url = f"https://api.spotify.com/v1/artists/{artist_id}/related-artists"
#     headers = get_auth_header(token)
#     result = get(url, headers = headers)
#     json_result = json.loads(result.content)
#     if len(json_result) == 0:
#         print("Artist does not exist")
#         return None
#     return json_result
    


# token = get_token()
# result = search_for_artist(token, "Sabrina Carpenter")
# print(result["name"])
# artist_id = result["id"]
# albums = get_artist_albums(token, artist_id)
# for i, album in enumerate(albums):
#     print(f"{i + 1}. {album['name']}")

# related_artists = get_related_artists(token,artist_id)

# # for j, artist in related_artists:
# #     print(artist['name'])






# '''The access token is a string which contains the credentials and permissions to access a given 
# resource (e.g artists, albums or tracks) or user's data (e.g your profile or your playlists).'''


