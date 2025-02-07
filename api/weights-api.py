import os, re, json, sys
import urllib.parse
import logging, argparse
import base64

from botocore.config import Config

import boto3
from boto3.dynamodb.conditions import Key, Attr


config = Config(
   connect_timeout = 3.0,
   read_timeout = 3.0
)

session = boto3.Session()
dynamodb = session.resource('dynamodb',
                          config = config,
                          endpoint_url = "http://localhost:8000/")

def initialize_logger(name: str = __name__):
    '''
    initialize logger
    '''

    FORMAT = '[%(levelname)s]:%(asctime)s %(message)s'
    logging.basicConfig(format = FORMAT)
    logger = logging.getLogger(name)
    logger.setLevel(os.getenv('LOGGING_LEVEL', 'DEBUG'))
    return logger


logger = initialize_logger()

path_data_new = re.compile(r'\/new')
path_data_available_years = re.compile(r'\/years')
path_data_by_year_month = re.compile(r'\/year\/(\d{4})\/month\/(\d{2})')
path_data_by_year_trend = re.compile(r'\/year\/(\d{4})\/trend')
path_data_by_year_monthly_avg = re.compile(r'\/year\/(\d{4})\/avg')
path_data_by_year = re.compile(r'\/year\/(\d{4})')

def request_handler(event: str, context: dict):

    path = event['rawPath']
    queryString = event['rawQueryString']

    if(match_result := path_data_new.fullmatch(path)):
        put_entry(req_payload)
    
    elif(match_result := path_data_by_year.fullmatch(path)):
        get_data_by_year(path)


def put_entry(payload):
    '''
    Put a single entry into the table
    '''
    logger.info(f'put_entry: {payload}')

    table = dynamodb.Table('Weights')
    table.put_item(
        Item = {
            'guid': payload['guid'],
            'entry-date': payload['entry-date'],
            'value': payload['value']
        }
    )


def get_available_years():
    '''
    Collect availible years to select from
    '''
    pass


def get_data_by_year_trend(match_result):
    '''
    Collect the min or max value for the year
    '''
    pass


def get_data_monthly_avg_by_year(match_result):
    '''
    Collect monthly averages by year

    e.g., /year/2022?avg
    '''
    pass


def get_data_by_year_month(match_result):
    '''
    Collect data for a single month and year.

    e.g., /year/2022/month/02
    '''
    pass


def get_data_by_year(match_result):
    '''
    Collect data for a given year

    e.g., /year/2021
    '''

    logger.info(f'get_data_by_year: {match_result}')

    table = dynamodb.Table('Weights')
    response = table.query(
        KeyConditionExpression = Key('pk').eq('id#1') \
            & Key('sk').begins_with('cart#'),
        FilterExpression = Attr('name').eq('SomeName')
    )



def get_payload_from_input(input):
    '''
    Parse the argparge --payload data and create a dictionary
    structure that simulates what would come through the request handler
    '''
    split = [s.strip() for s in input.split(',')]
    if len(split) != 3:
        raise Exception(f'Payload input {input} must contain 3 values in '
            + 'the form USERGUID,DATE,VALUE')
    
    dict = str({
        'guid': split[0],
        'entry-date': split[1],
        'value': split[2] 
    })

    return base64.b64encode(dict.encode('utf-8'))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog = 'Weight Tracking Access', description='Database interactions by request routes.')
    parser.add_argument('path', default = '/', type = str, help = 'Path to execute. e.g., /year/2023')
    parser.add_argument('--body', type = str, help = 'Comma-separate values of post data - USERGUID,DATE,VALUE e.g., 9842-1232-2321-0923,2025-01-01,175.0')
    parser.add_argument('--indent', default = None, type = int, help = 'Indentation size on json pretty print.  Default None to be less verbose during dev/test.')
    args = parser.parse_args()

    # parse input into a request body
    post_body = get_payload_from_input(args.body) \
        if args.body else {}

    event = {}
    with open('./test/api-gateway-http-api.json', 'r') as api_sample:
        event = json.load(api_sample)

    logger.info(post_body)

    # verify path and response
    # response = request_handler(args.path, payload)
    # json.dump(response, sys.stdout
    #           , indent = args.indent
    #           , default = str)