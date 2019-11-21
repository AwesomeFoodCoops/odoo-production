# -*- coding: utf-8 -*-

import xmlrpc.client

host = "http://localhost:8069"
user_id = 1
password = "admin"
database = "lebaudet_9"

db = xmlrpc.client.ServerProxy(host + "/xmlrpc/object")

# db.execute(database, user_id, password, 'product.history',
#            'update_product_history_script', ([]))

db.execute(database, user_id, password, 'product.history',
           'update_product_history_script_background', ([]))
