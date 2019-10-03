"""
Author: Justin Alan Larsen
Date: September 30th, 2019
Purpose: A homework assignment for the Divvy Data Engineering Team.
"""
import collections
from functools import reduce
import urllib

import boto3

S3_CLIENT = boto3.client('s3')

def lambda_handler(event, _context=None):
    """
    Main entry point for lambdas. Intended to be triggered when a file is uploaded to S3.
    """
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(
        event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    response = S3_CLIENT.get_object(Bucket=bucket, Key=key)
    input_lines = response['Body'].read().splitlines()
    lines_to_process = map(_write_line_to_dynamodb, input_lines)
    collections.deque(lines_to_process)

def _write_line_to_dynamodb(input_line):
    raw_relationships = input_line.split(',')
    valid_lines = filter(_is_valid, raw_relationships)
    object_arrays = map(_extract_objects, valid_lines)
    relationships = map(_build_initial_relationships, object_arrays)
    combined_relationships = reduce(_combine_relationships, relationships)
    for relationship in combined_relationships.items():
        _add_relationship_to_dynamo(relationship)
    return combined_relationships

def _is_valid(relationship):
    valid_string = False
    if 'is a' in relationship and len(relationship) > 6:
        valid_string = True
    return valid_string

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
    table = boto3.resource("dynamodb").Table("object_relationships") # pylint: disable=E1101
    table.put_item(Item=formatted_relationship)
    return formatted_relationship
