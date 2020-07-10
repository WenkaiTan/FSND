import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')

def get_drinks():

    drinks = Drink.query.all()
    ##if len(drinks) == 0:
    ##    abort(404)

    formatted_drinks = [drink.short() for drink in drinks]

    return jsonify({
        'success': True,
        "drinks": formatted_drinks
    }), 200


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')

@requires_auth('get:drinks-detail')
def get_drink_detail(payload):
    drinks = Drink.query.all()
    ##if len(drinks) == 0:
    ##    abort(404)
    formatted_drinks = [drink.long() for drink in drinks]
    return jsonify({
        "success": True,
        "drinks": formatted_drinks
    }), 200

    raise AuthError({"code":"Unauthorized",
                    "description":"You don't have access to this resource."}, 403)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(paylod):
    """Creates a new drink"""
    body = request.get_json()
    if not body:
        abort(400)
    if 'title' not in body or 'recipe' not in body:
        abort(400)
        new_drink = Drink(title=body['title'],
        recipe=json.dumps(body['recipe']))
    try:
        new_drink.insert()
    except SystemError:
        abort(500)
    selection = Drink.query.all()
    drinks = [drink.long() for drink in selection if drink.id == new_drink.id]
    if not drinks:
        abort(404)

    return jsonify({
    'success': True,
    'drinks': drinks
    }), 201



'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:id>", methods=['PATCH'])

@requires_auth('patch:drinks')
def patch_drink(payload, id):
    body = request.get_json()
    title = body['title']
    receipe = body['recipe']
    try:
        if 'title' not in body or 'recipe' not in body:
            abort(422)
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink:
            drink.title = title
            drink.recipe = json.dumps(receipe)

            drink.update()

            return jsonify({
                "success": True,
                "drinks": [drink.long()]
            }), 200
        else:
            abort(404)
    except:
        abort(422)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])

@requires_auth("delete:drinks")
def delete_drink(payload, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink:
            drink.delete()

            return jsonify({
                "success": True,
                "delete": id
            }), 200
        else:
            abort(404)
    except:
        abort(422)
    


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@T implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "not found"
    }), 404

'''
@ implement error handler for 404
    error handler should conform to general task above 
'''


'''
 implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
