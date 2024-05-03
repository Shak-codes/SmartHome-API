from flask import Flask, request, jsonify
import json
import hashlib
from datetime import datetime
import requests
from .constants import PARAMS
from .lights.lights import Light
from .credentials import PHUE, HASH1, HASH2, CLIENT_ID

app = Flask(__name__)


LIGHTS = {
    f"{PHUE.LIGHT1_ID.value}": Light(PHUE.LIGHT1_ID.value),
    f"{PHUE.LIGHT2_ID.value}": Light(PHUE.LIGHT2_ID.value),
}


@app.route("/listener")
def generate_refresh_token():
    url = PHUE.TOKEN_URL.value
    realm = PHUE.REALM.value
    state = PHUE.STATE.value
    uri = PHUE.URI.value
    # If response has been tampered with
    if request.args.get('state') != state:
        return 'Tampered response', 400
    # Continue otherwise
    code = request.args.get(PARAMS.CODE.value)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'grant_type': 'authorization_code', 'code': code}
    response = requests.post(url, headers=headers, data=data)
    nonce = response.headers['WWW-Authenticate'].split(',')[1]
    nonce_length = len(nonce)
    nonce = nonce[7:nonce_length-1]
    hash = hashlib.md5(f"{HASH1}:{nonce}:{HASH2}".encode())
    headers['Authorization'] = f'Digest username = "{CLIENT_ID}", realm = "{
        realm}", nonce = "{nonce}", uri = "{uri}", response = "{hash.hexdigest()}"'
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    response = requests.post(url, headers=headers, data=data)
    response = response.json()
    token_data = {
        'generated_at': generated_at,
        'access_token': response['access_token'],
        'refresh_token': response['refresh_token'],
    }
    with open("./tokens.json", "w") as file:
        json.dump(token_data, file, indent=4)
    return jsonify(token_data)


@app.route("/light", methods=['PUT'])
def modify_light():
    refresh()
    id = request.args.get('id', default=1, type=str)
    on = request.args.get('on', default="true", type=str)
    return LIGHTS[id].set_light(on)


def refresh():
    file = open("./tokens.json")
    tokens = json.load(file)
    generated_at = datetime.strptime(
        tokens['generated_at'], "%Y-%m-%d %H:%M:%S.%f")
    current = datetime.now()
    age = current - generated_at
    if age.total_seconds() > 600000:
        refresh_token()


@app.route("/refresh")
def refresh_token():
    file = open("./tokens.json")
    tokens = json.load(file)
    url = PHUE.TOKEN_URL.value
    realm = PHUE.REALM.value
    uri = PHUE.URI.value

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'grant_type': 'refresh_token',
            'refresh_token': tokens['refresh_token']}
    response = requests.post(url, headers=headers, data=data)
    nonce = response.headers['WWW-Authenticate'].split(',')[1]
    nonce_length = len(nonce)
    nonce = nonce[7:nonce_length-1]
    hash = hashlib.md5(f"{HASH1}:{nonce}:{HASH2}".encode())
    headers['Authorization'] = f'Digest username = "{CLIENT_ID}", realm = "{
        realm}", nonce = "{nonce}", uri = "{uri}", response = "{hash.hexdigest()}"'
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    response = requests.post(url, headers=headers, data=data)
    response = response.json()
    token_data = {
        'generated_at': generated_at,
        'access_token': response['access_token'],
        'refresh_token': response['refresh_token'],
    }
    with open("./tokens.json", "w") as file:
        json.dump(token_data, file, indent=4)
    return jsonify(token_data)
