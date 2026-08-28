from omero.gateway import BlitzGateway
from omero.clients import BaseClient

from omero_search_engine import search_omero_app


def connect_omero(datasource, omename, password, session_id):
    data = {}
    # sessionId="3107e04f-6b55-421e-9494-397289aebbde"
    from omero_search_engine.api.auth.utils import get_data_source_server_url

    host, port = get_data_source_server_url(datasource)
    if not host:
        raise Exception("Auth host is not configured for %s" % datasource)

    search_omero_app.logger.info("Host %s, port %s" % (host, port))
    if not session_id:
        conn = BlitzGateway(
            username=omename, passwd=password, host=host, port=port, secure=True
        )
    else:
        client = BaseClient(host=host, port=port)
        client.joinSession(session_id)
        conn = BlitzGateway(client_obj=client)

    is_connected = conn.connect()
    print("https://192.168.1.201/::::", is_connected)
    if is_connected:

        # conn.SERVICE_OPTS.setOmeroGroup('-1')
        groups = get_user_groups(conn)
        ctx = conn.getEventContext()
        # print (ctx.__dict__.keys())
        data["is_admin"] = ctx.isAdmin
        data["session_id"] = ctx.sessionUuid
        data["sessionId"] = ctx.sessionId
        data["user_id"] = ctx.userId
        data["groups"] = groups
        data["data_source"] = datasource
        # search_omero_app.logger.info (conn.SERVICE_OPTS.setOmeroGroup('-1'))
        conn.keepAlive()
    else:
        search_omero_app.logger.info("FAILED to connect")
    return data


def get_user_groups(conn):
    groups = {}
    for g in conn.getGroupsMemberOf():
        # if not g.isPrivate():
        groups[g.getId()] = {"name": g.getName()}
        # , "is_Private": g.isPrivate(), "is_Public": g.isPublic(),
        # "owner":g.getOwner()})#,"owner_1":g.isOwned})

    owned_groups = conn.listOwnedGroups()
    for group in owned_groups:
        print(f"Name: {group.getName()} | ID: {group.getId()}")
        if group.getId() not in groups:
            groups[group.getId()] = {"name": group.getName()}
    return groups


def check_sessiion_id(session_idd):
    host = search_omero_app.config.get("OMERO_URL")
    port = search_omero_app.config.get("OMERO_PORT")
    conn = BaseClient(host=host, port=port)
    conn.joinSession(session_idd)


def verify_session(datasource, session_id):
    from omero_search_engine.api.auth.utils import get_data_source_server_url

    host, port = get_data_source_server_url(datasource)
    client = BaseClient(host=host, port=port)
    try:
        client.joinSession(session_id)
    except Exception as e:
        print("Error is %s" % str(e))
        return False

    conn = BlitzGateway(client_obj=client)
    is_connected = conn.connect()
    if is_connected:
        conn.keepAlive()
    return is_connected
