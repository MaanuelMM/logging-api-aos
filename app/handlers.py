#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Authors:      MaanuelMM
# Created:      2020/06/01
# Last update:  2020/06/03

import json

from io import StringIO
from csv import DictWriter
from flask import request
from responses import make_response, http_message
from http import HTTPStatus
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConflictError, NotFoundError
from uuid import uuid1, UUID
from datetime import datetime, timezone
from strict_rfc3339 import rfc3339_to_timestamp, timestamp_to_rfc3339_utcoffset


# the biggest $#*! i've ever done - in a bad way
class EventHandler():

    def __init__(self, host: str, port: int, index: str, prefix: str):
        try:
            self.es = Elasticsearch(hosts=[(host + ':' + str(port))])
            self.index = index
            self.prefix = prefix
        except:
            raise

    @staticmethod
    def _order_data(data: dict, schema_order: list):
        new_data = dict()

        for element in schema_order:
            new_data[element] = data[element]

        return new_data

    @staticmethod
    def _generate_query(query: dict):
        if query:
            match_dict = dict()
            date_dict = dict()

            new_query = {'bool': {}}

            for key, value in query.items():
                if key == 'dateFrom':
                    date_dict['gte'] = rfc3339_to_timestamp(value)
                elif key == 'dateTo':
                    date_dict['lte'] = rfc3339_to_timestamp(value)
                else:
                    match_dict[key] = value

            if match_dict:
                new_query['bool']['must'] = [{'match': {key: value}}
                                             for key, value in match_dict.items()]

            if date_dict:
                new_query['bool']['filter'] = {'range': {'date': date_dict}}

            return new_query

        else:
            return {'match_all': {}}

    def _generate_dict_body(self, data: dict, event_id: int):
        new_data = dict()

        data['date'] = timestamp_to_rfc3339_utcoffset(data['date'])

        new_data["eventId"] = event_id
        new_data.update(data)
        new_data["_links"] = {
            "parent": {
                "href": self.prefix
            },
            "self": {
                "href": self.prefix + f"/{event_id}"
            }
        }

        return new_data

    def _get_event_by_id(self, event_id: UUID):
        data = None

        try:
            data = self.es.get(index=self.index, id=event_id)["_source"]
        except NotFoundError:
            data = dict()
        except Exception:
            pass

        return data

    def _search_events(self, query: dict):
        result = None

        try:
            query = EventHandler._generate_query(query)
            result = self.es.search(index=self.index, body={
                                    'size': '10000', 'query': query, 'sort': [
                                        {'date': 'desc'}]})['hits']['hits']
        except NotFoundError:
            result = dict()
        except Exception:
            pass

        return result

    @staticmethod
    def options_handler(allow_header):
        response = make_response(request.headers)
        response.headers.add("Allow", allow_header)
        return response

    def post_handler(self, data: dict, schema_order: list):
        response = make_response(request.headers, HTTPStatus.INTERNAL_SERVER_ERROR, json.dumps(
            http_message(HTTPStatus.INTERNAL_SERVER_ERROR)))
        retries = 0

        while retries <= 3:
            try:
                body = EventHandler._order_data(data, schema_order)
                body['date'] = rfc3339_to_timestamp(body['date'])
                event_id = uuid1()
                self.es.create(index=self.index, id=event_id, body=body)
                body = self._generate_dict_body(body, event_id.int)
                response = make_response(
                    request.headers, HTTPStatus.CREATED, json.dumps(body))
                response.headers.add(
                    "Location", body["_links"]["self"]["href"])
                break
            except ConflictError:  # it's pretty impossible an uuid collision, but who knows...
                retries += 1
                continue
            except Exception:  # here is if something really bad happens, so let's exit and thow a 500 error
                break

        return response

    @staticmethod
    def _generate_csv(dict_list: list):
        with StringIO() as csvfile:
            writer = DictWriter(csvfile, fieldnames=dict_list[0].keys())
            writer.writeheader()
            writer.writerows(dict_list)
            return csvfile.getvalue()

    def get_handler(self, event_id: UUID):
        response = None

        data = self._get_event_by_id(event_id)
        if data:
            data = self._generate_dict_body(data, event_id.int)
            if str(request.accept_mimetypes) == 'text/csv':
                response = make_response(
                    request.headers, HTTPStatus.OK, EventHandler._generate_csv([data]), True, 'text/csv')
            else:  # default to 'application/json'
                response = make_response(
                    request.headers, HTTPStatus.OK, json.dumps(data), True)
        elif data is not None:
            response = make_response(request.headers, HTTPStatus.NOT_FOUND, json.dumps(
                http_message(HTTPStatus.NOT_FOUND)))
        else:
            response = make_response(request.headers, HTTPStatus.INTERNAL_SERVER_ERROR, json.dumps(
                http_message(HTTPStatus.INTERNAL_SERVER_ERROR)))

        return response

    def cget_handler(self, query):
        response = None

        data = self._search_events(query)
        if data:
            data = [self._generate_dict_body(
                event['_source'], UUID(event['_id']).int) for event in data]
            if str(request.accept_mimetypes) == 'text/csv':
                response = make_response(
                    request.headers, HTTPStatus.OK, EventHandler._generate_csv(data), True, 'text/csv')
            else:
                response = make_response(
                    request.headers, HTTPStatus.OK, json.dumps({'events': data}), True)
        elif data is not None:
            response = make_response(request.headers, HTTPStatus.NOT_FOUND, json.dumps(
                http_message(HTTPStatus.NOT_FOUND)))
        else:
            response = make_response(request.headers, HTTPStatus.INTERNAL_SERVER_ERROR, json.dumps(
                http_message(HTTPStatus.INTERNAL_SERVER_ERROR)))

        return response
