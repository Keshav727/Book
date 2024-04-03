from flask import Flask, make_response, jsonify, request
import dataset

app = Flask(__name__)
db = dataset.connect('sqlite:///api.db')

table = db.get_table('books')

if 'books' not in db.tables:
    table = db.create_table('books', primary_id='book_id')

@app.route('/api/db_populate', methods=['GET'])
def db_populate():
    table.insert({
        "book_id": "1",
        "name": "A Game of Thrones.",
        "author": "George R. R. Martin"
    })

    table.insert({
        "book_id": "2",
        "name": "Lord of the Rings",
        "author": "J. R. R. Tolkien"
    })

    return make_response(jsonify(fetch_db_all()), 200)

def fetch_db_all():
    return list(table.all())

@app.route('/api/books', methods=['GET', 'POST'])
def api_books():
    if request.method == "GET":
        return make_response(jsonify(fetch_db_all()), 200)
    elif request.method == 'POST':
        content = request.json
        if 'book_id' not in content or 'name' not in content or 'author' not in content:
            return make_response(jsonify({"error": "Missing required fields"}), 400)
        book_id = content['book_id']
        table.insert(content)
        return make_response(jsonify(fetch_db(book_id)), 201)

@app.route('/api/books/<book_id>', methods=['GET', 'PUT', 'DELETE'])
def api_each_book(book_id):
    book_obj = fetch_db(book_id)
    if request.method == "GET":
        if book_obj:
            return make_response(jsonify(book_obj), 200)
        else:
            return make_response(jsonify({"error": "Book not found"}), 404)
    elif request.method == "PUT":
        content = request.json
        if not book_obj:
            return make_response(jsonify({"error": "Book not found"}), 404)
        table.update(content, ['book_id'])
        return make_response(jsonify(fetch_db(book_id)), 200)
    elif request.method == "DELETE":
        if not book_obj:
            return make_response(jsonify({"error": "Book not found"}), 404)
        table.delete(book_id=book_id)
        return make_response(jsonify({}), 204)

def fetch_db(book_id):
    return table.find_one(book_id=book_id)

if __name__ == '__main__':
    app.run(debug=True)

