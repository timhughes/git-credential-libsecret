#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Tim Hughes <thughes@thegoldfish.org>
#
# Distributed under terms of the MIT license.

"""
Handles storing and providing usernames and passwords to Git using libsecret.
"""

import os
import sys
if __name__ == '__main__':
    githelper = __import__(os.path.splitext(os.path.basename(__file__))[0])
    raise SystemExit(githelper.main(sys.argv))


import sys
import argparse
from urllib.parse import urlparse
from datetime import datetime
import gi
gi.require_version('Secret', '1')
from gi.repository import Secret

GIT_CREDENTIALS_SCHEMA = Secret.Schema.new("org.timhughes.git.Credentials.",
        Secret.SchemaFlags.NONE,
        {
            "protocol": Secret.SchemaAttributeType.STRING,
            "host": Secret.SchemaAttributeType.STRING,
            "path": Secret.SchemaAttributeType.STRING,
            "username": Secret.SchemaAttributeType.STRING,
            "application": Secret.SchemaAttributeType.STRING,
            "last_updated": Secret.SchemaAttributeType.STRING,
            }
        )

def main(argv):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    parser_get = subparsers.add_parser('get', help='get help')
    parser_get.set_defaults(func=get)

    parser_store = subparsers.add_parser('store', help='store shelp')
    parser_store.set_defaults(func=store)

    parser_reject = subparsers.add_parser('reject', help='reject help')
    parser_reject.set_defaults(func=reject)
    args = parser.parse_args(argv[1:])
    if hasattr(args, 'func'):
        try:
            args.func()
        except KeyboardInterrupt:
            print('Interrupted')
            sys.exit(0)



def get_attributes():
    timestamp = "%d" % datetime.timestamp(datetime.now())
    attributes = {
            'application': 'git-credential-libsecret.py',
            'last_updated': timestamp,
            }
    for line in sys.stdin:
        key, var = line.partition("=")[::2]
        if key == "\n":
            break

        if key in ['protocol','host','path','username','password','url']:
            if key == 'url':
                o = urlparse(var.strip())
                if o.scheme:
                    attributes['protocol'] = o.scheme
                if o.netloc:
                    attributes['host'] = o.netloc
                if o.path:
                    attributes['path'] = o.path
                if o.username:
                    attributes['username'] = o.username
                if o.password:
                    attributes['password'] = o.password
            else:
                attributes[key.strip()] = var.strip()
    if len(attributes) > 0:
        return attributes
    else:
        return

def get():
    attributes = get_attributes()

    if 'password' in attributes:
        del attributes['password']
    password = Secret.password_lookup_sync(
        GIT_CREDENTIALS_SCHEMA,
        attributes,
        None
        )
    if password:
        secret_item = find_secret_item(attributes)
        print('protocol=%s' % secret_item['protocol'])
        print('host=%s' % secret_item['host'])
        print('username=%s' % secret_item['username'])
        print('password=%s' % secret_item['password'])


def store():
    attributes = get_attributes()

    if 'password' in attributes:
        password = attributes['password']
        del attributes['password']
    else:
        sys.exit(1)

    Secret.password_store_sync(
            GIT_CREDENTIALS_SCHEMA,
            attributes,
            Secret.COLLECTION_DEFAULT,
            "%s://%s@%s" %(attributes['protocol'], attributes['username'], attributes['host'] ),
            password,
            None
            )


def reject():
    attributes = get_attributes()

    if 'password' in attributes:
        del attributes['password']

    Secret.password_clear_sync(
            GIT_CREDENTIALS_SCHEMA,
            attributes,
            None
            )

def find_secret_item(attributes):
    service = Secret.Service.get_sync(Secret.ServiceFlags.LOAD_COLLECTIONS)
    collection = Secret.Collection.for_alias_sync(service,Secret.COLLECTION_DEFAULT,Secret.CollectionFlags.LOAD_ITEMS,None)
    item = collection.search_sync(GIT_CREDENTIALS_SCHEMA,attributes,Secret.SearchFlags.LOAD_SECRETS,None)[0]
    item.load_secret_sync()
    ret_attributes = item.get_attributes()
    ret_attributes['password'] = item.get_secret().get().decode('utf-8')
    return ret_attributes

