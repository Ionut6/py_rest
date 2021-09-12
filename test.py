import random
import requests
from flask import Flask, jsonify, request, make_response
import jwt
import datetime
import binascii
import imghdr
import sqlite3
from sqlite3 import Error
from flask_sqlalchemy import SQLAlchemy
from skimage import io, color
from PIL import Image

app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'secret_key'
image_file = 'photo.png'
db_file = r"C:\Users\panfi\PycharmProjects\test\pythonsqlite.db"

class JsonModel(object):  # Class for making objects JSON serializable
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class image(db.Model, JsonModel):  # Class which is a model for the Todo table in the database
    id = db.Column(db.Integer, primary_key = True)
    binary = db.Column(db.String(5000))
    formal = db.Column(db.String(10))

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn



@app.route('/images/')
def images():
    try:
        # pick an image file you have in the working directory
        # or give the full file path ...

        fin = open(image_file, "rb")
        data = fin.read()
        fin.close()
    except IOError:
        print("Image file %s not found" % image_file)
        raise SystemExit
    # convert every byte of data to the corresponding 2-digit hexadecimal
    hex_str = str(binascii.hexlify(data))
    # now create a list of 2-digit hexadecimals
    hex_list = []
    bin_list = []
    for ix in range(2, len(hex_str) - 1, 2):
        hex = hex_str[ix] + hex_str[ix + 1]
        hex_list.append(hex)
        bin_list.append(bin(int(hex, 16))[2:])

    # print(bin_list)
    bin_str = "".join(bin_list)
    # print(bin_str)

    #login
    auth = request.authorization

    if auth and auth.password == 'secret':
        #post image
        #random id photo
        id_photo = random.randint(1, 10)

        image = {'id': id_photo,
                 'binary image': bin_str,
                 'format image': imghdr.what(image_file)}

        response = requests.post("http://127.0.0.1:5000/images/", image)

        #insert to sqlite
        # create a db_file connection
        try:
            sqliteConnection = sqlite3.connect(db_file)
            cursor = sqliteConnection.cursor()
            print("Connected to SQLite")

            sqlite_insert_with_param = """INSERT INTO image
                                  (id,binImage,format) 
                                  VALUES (?,?,?);"""

            data_tuple = (id_photo, bin_str, imghdr.what(image_file))
            cursor.execute(sqlite_insert_with_param, data_tuple)
            sqliteConnection.commit()
            print("Python Variables inserted successfully into SqliteDb_developers table")

            cursor.close()

        except sqlite3.Error as error:
            print("Failed to insert Python variable into sqlite table", error)
        finally:
            if sqliteConnection:
                sqliteConnection.close()
                print("The SQLite connection is closed")


        #token
        token = jwt.encode({'user' : auth.username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])

        #return
        return jsonify({'token' : token},
                       {'id photo' : id_photo})

    return make_response('Could verify!', 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})

@app.route('/images/<int:id>', methods=['GET'])
def get(id):
    response = {}
    images = image.query.get(id)
    response['id'] = images.id
    response['binImage'] = images.binary
    response['format'] = images.format
    response.status_code = 201
    return jsonify(response)

    try:
        id = request.json['id']
        binImage = request.json['binImage']
        format = request.json['format']

        images = image.query.filter_by(id=id1).first()
        images.id = id
        images.binImage = binImage
        images.format = format

        db.session.commit()
        return response.ok('', 'Successfully update data!')

    except Exception as e:
        print(e)

    try:
        images1 = image.query.filter_by(id=id).first()
        if not images1:
            return response.badRequest([], 'Empty....')

        db.session.delete(images1)
        db.session.commit()

        return response.ok('', 'Successfully delete data!')
    except Exception as e:
        print(e)

@app.route('/apply/')
def apply():
    img = io.imread(image_file)
    imgGray = color.rgb2gray(img)
    img_rotate = Image.open(image_file)
    rotate = img_rotate.rotate(45)
    return  "<img src=", imgGray, ">\br<img src=", rotate, ">"

if __name__ == '__main__':
    app.run(debug=True)