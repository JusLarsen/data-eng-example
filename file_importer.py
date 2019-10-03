"""
Author: Justin Alan Larsen
Date: September 30th, 2019
Purpose: A homework assignment for the Divvy Data Engineering Team.
"""
from functools import reduce
import urllib
import boto3

S3_CLIENT = boto3.client('s3')
## TODO: Move constants to environment variables from SSM.
DYNAMO_TABLE_NAME = 'object_relationships'
MINIMUM_STRING_LENGTH = 8

def lambda_handler(event, _context=None):
    """
    Main entry point for lambdas. Intended to be triggered when a file is uploaded to S3.
    """
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(
        event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    response = S3_CLIENT.get_object(Bucket=bucket, Key=key)
    input_lines = response['Body'].readlines()
    records_to_insert = map(prepare_relationships_for_insertion, input_lines)
    _write_relationship_to_dynamodb(records_to_insert)

def prepare_relationships_for_insertion(input_lines):
    """
    Inputs:
        A list of input lines as read from s3
    Returns:
        A dictionary of the form {"noun": "children"[]}
    """
    combined_lines = input_lines
    raw_relationships = combined_lines.split(',')
    valid_relationships = filter(_is_valid, raw_relationships)
    relationship_arrays = map(_extract_objects, valid_relationships)
    relationships = list(map(_build_initial_relationships, relationship_arrays))
    combined_relationships = reduce(_combine_relationships, relationships)
    return combined_relationships

def _write_relationship_to_dynamodb(combined_relationships):
    for relationship in combined_relationships.items():
        _add_relationship_to_dynamo(relationship)
    return combined_relationships

def _is_valid(relationship):
    return ('is a' in relationship
            and len(relationship) >= MINIMUM_STRING_LENGTH)


def _extract_objects(relationship):
    objects = relationship.replace(' is an ', ' is a ').split(' is a ')
    return list(map(lambda x: x.strip(), objects))

def _build_initial_relationships(object_array):
    return {
        object_array[1]: [object_array[0]],
        object_array[0]: []
    }

def _combine_relationships(current_relationship, next_relationship):
    for parent, children in next_relationship.items():
        if parent not in current_relationship.keys():
            current_relationship[parent] = children
        else:
            for child in children:
                current_relationship[parent].append(child)
    return current_relationship

def _add_relationship_to_dynamo(relationship_tuple):
    formatted_relationship = {
        "name": relationship_tuple[0],
        "children": relationship_tuple[1]
    }
    table = boto3.resource("dynamodb").Table(DYNAMO_TABLE_NAME) # pylint: disable=E1101
    table.put_item(Item=formatted_relationship)
    return formatted_relationship
