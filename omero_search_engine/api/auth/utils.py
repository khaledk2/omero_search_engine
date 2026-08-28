import jwt
from flask import request, jsonify
from flask import current_app
import datetime

from omero_search_engine.api.auth.OMERO_connector.utils import (
    connect_omero,
    verify_session,
)


def create_token(datasource, omename, password, session_id):
    from omero_search_engine import search_omero_app

    data = connect_omero(datasource, omename, password, session_id)
    if len(data) > 0:
        # JWT expire after 2 hrs by default unless
        # it has been configured otherwise using
        # set_JWT_expire_time
        jwt_exp = search_omero_app.config.get("JWT_EXPIRE_TIME")
        if not jwt_exp:
            jwt_exp = 120
        exp = int(
            round(
                (
                    datetime.datetime.utcnow() + datetime.timedelta(minutes=jwt_exp)
                ).timestamp()
            )
        )
        token = jwt.encode(
            {**{"omename": omename, "exp": exp}, **data},
            current_app.config["SECRET_KEY"],
            "HS256",
        )
        return jsonify({"token": token})
    else:
        return jsonify(
            {
                "message": "could not verify",
                "code": 401,
                "Authentication": "login required",
            }
        )


"""
def token_required_(f):
    @wraps(f)
    def decorator(res, *args, **kwargs):
        user_groups = {}
        is_admin = False
        is_expired = True
        token = request.headers.get("Authorization")
        if token:
            try:
                token_data = jwt.decode(
                    token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
                )
                user_groups = token_data.get("all_groups")
                is_admin = token_data.get("is_admin")
                is_expired = False
                is_valid = True
            except jwt.ExpiredSignature as e:
                print("1. Error: %s" % e)
                is_expired = True
                is_valid = False
            except Exception as e:
                print("2. Error: %s" % e)
                is_valid = False
        return f(res, user_groups, is_admin, is_expired, request, *args, **kwargs)

    return decorator

"""


def check_tocken(token):
    try:
        token_data = jwt.decode(
            token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
        )
    except Exception as e:
        print("Error is %s" % str(e))
        return None
    if token_data.get("session_id"):
        if not verify_session(
            token_data.get("data_source"), token_data.get("session_id")
        ):
            return {"is_valid": False}
    else:
        return {"is_valid": False}

    user_groups = token_data.get("groups")
    is_admin = token_data.get("is_admin")
    user_id = token_data.get("user_id")
    is_expired = False
    is_valid = True
    return {
        token_data.get("data_source"): {
            "is_valid": is_valid,
            "is_expired": is_expired,
            "user_groups": user_groups,
            "is_admin": is_admin,
            "user_id": user_id,
            "data_source": token_data.get("data_source"),
        }
    }


def get_jwt_from_request():
    auth_header = request.headers.get("Authorization")
    auth = None
    if auth_header and len(auth_header.split(" ")) == 2:
        token = auth_header.split(" ")[1]
    else:
        token = auth_header
    if token:
        # check if the token is valid
        auth = check_tocken(token)

    return auth


def is_datasource_public(datasource):
    from omero_search_engine import search_omero_app

    for data_source in search_omero_app.config.get("DATA_SOURCES"):
        if type(datasource) is list:
            if data_source.get("name").lower() in datasource:
                return data_source.get("public")
        else:
            if data_source.get("name").lower() == datasource.lower():
                return data_source.get("public")
    return None


def get_data_source_server_url(datasource):
    from omero_search_engine import search_omero_app

    for data_source in search_omero_app.config.get("DATA_SOURCES"):
        if type(datasource) is list:
            if data_source.get("name").lower() in datasource:
                host = data_source.get("SERVER_URL")
                port = data_source.get("SERVER_PORT")
                return host, port
        else:
            if data_source.get("name").lower() == datasource.lower():
                host = data_source.get("SERVER_URL")
                port = data_source.get("SERVER_PORT")
                return host, port
    return None, None
