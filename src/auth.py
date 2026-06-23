import jwt
import datetime

def generate_jwt_token(client_id, secret):
    payload = {
        'sub': client_id,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, secret, algorithm='HS256')
