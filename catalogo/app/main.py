from flask import jsonify, request, Flask
from catalog import get_products, create_product, get_product
import os
import redis

app = Flask(__name__)

#redis_client = redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=0, decode_responses=True)

redis_host = os.environ.get('REDIS_HOST', None)
redis_port = os.environ.get('REDIS_PORT', None)

if redis_host and redis_port:
    redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST'),
            port=os.getenv('REDIS_PORT'),
            db=0, decode_responses=True
    )
else:
    redis_client = None

@app.route('/product/<sku>', methods=['GET', ])
def get_product_by_sku(sku):
    #product = redis_client.hgetall(sku)
    product = redis_client.hgetall(sku) if redis_client else None
    if not product:
        product = get_product(sku)
        product['cache'] = 'miss'
        #redis_client.hmset(product['sku'], product)
        if redis_client:
            redis_client.hmset(product['sku'], product)
    else:
        pass
        product['cache'] = 'hit'

    return jsonify(product)

@app.route('/product', methods=['GET', 'POST'])
def list_all_products():
    '''This view maneges the CRUD of products'''
    if request.method == 'GET':
        response = get_products()
        return jsonify(response)

    if request.method == 'POST':
        data = request.get_json()
        new_sku = create_product(
                None,
                data['title'],
                data['long_description'],
                data['price_euro'])
        return jsonify({"status": "ok", "sku": new_sku})

@app.route('/hello')
def hello_world():
    #return ("Helo, world!")
    message = "Hola Mundo, soy Python! Ahora con CloudBuild y hablando JSON. Cambio"
    response = {
            "message": message,
            "length": len(message)
            }
    return jsonify(response)

@app.route('/bye')
def bye_world():
    return ("Bye")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
