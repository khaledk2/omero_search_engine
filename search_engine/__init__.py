from flask import Flask, request
import os
import logging
from elasticsearch import Elasticsearch
from flasgger import Swagger, LazyString, LazyJSONEncoder

from search_engine.database.database_connector import DatabaseConnector
from configurations.configuration import configLooader,load_configuration_variables_from_file,set_database_connection_variables
from logging.handlers import RotatingFileHandler

from configurations.configuration import  app_config as config_
from urllib.parse import urlparse
from flask import request, url_for as _url_for

template = dict(swaggerUiPrefix=LazyString(lambda : request.environ.get('HTTP_X_SCRIPT_NAME', '')))

main_folder=os.path.dirname(os.path.realpath(__file__))

static_folder=os.path.join(main_folder, "searchenginestatic")

search_omero_app = Flask(__name__, static_url_path="/searchenginestatic", static_folder="searchenginestatic")

search_omero_app.json_encoder = LazyJSONEncoder

'''
Refernce for the following two methods is:
https://stackoverflow.com/questions/25962224/running-a-flask-application-at-a-url-that-is-not-the-domain-root
'''
def url_with_host(path):
    return '/'.join((urlparse(request.host_url).path.rstrip('/'), path.lstrip('/')))

def url_for(*args, **kwargs):
    if kwargs.get('_external') is True:
        return _url_for(*args, **kwargs)
    else:
        return url_with_host(_url_for(*args, **kwargs))


search_omero_app.config['SWAGGER'] = {
    'title': 'Omero Search Engine API',
    #'uiversion': 3
}
#search_omero_app.json_encoder = LazyJSONEncoder

swagger = Swagger(search_omero_app, template=template)

app_config =load_configuration_variables_from_file(config_)

def create_app(config_name="development"):
    app_config=configLooader.get(config_name)
    load_configuration_variables_from_file(app_config)
    set_database_connection_variables(app_config)
    database_connector = DatabaseConnector(app_config.DATABAS_NAME, app_config.DATABASE_URI)
    #print (app_config.DATABAS_NAME, app_config.DATABASE_URI)
    search_omero_app.config.from_object(app_config)
    search_omero_app.app_context()
    search_omero_app.app_context().push()
    search_omero_app.app_context()
    search_omero_app.app_context().push()
    es_connector = Elasticsearch(app_config.ELASTICSEARCH_URL,
                                 timeout=130, max_retries=20, retry_on_timeout=True)

    search_omero_app.config["database_connector"]=database_connector
    search_omero_app.config["es_connector"] = es_connector
    log_folder = os.path.join(os.path.expanduser('~'), 'logs')
    if not os.path.exists(log_folder):
        os.mkdir(log_folder)
    file_handler = RotatingFileHandler(os.path.join(log_folder, 'omero_search_engine.log'), maxBytes=100240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    search_omero_app.logger.addHandler(file_handler)

    search_omero_app.logger.setLevel(logging.INFO)
    search_omero_app.logger.info('app assistant startup')
    search_omero_app.jinja_env.globals['url_for'] = url_for


    return search_omero_app

create_app()


from search_engine.api.v1.resources import resources as resources_routers_blueprint_v1
search_omero_app.register_blueprint(resources_routers_blueprint_v1, url_prefix='/api/v1/resources')

from search_engine.searchresults import searchresults as search_results_routers_blueprint
search_omero_app.register_blueprint(search_results_routers_blueprint, url_prefix='/searchresults')

'''
#commented as it is ebaled at the NGINX confiuration level
#add it to account for CORS
@search_omero_app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header["Access-Control-Allow-Headers"]= "*"
    return response  
'''

