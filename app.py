from pymongo import MongoClient
import requests
import json
from functools import wraps
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for, Response
import urllib.request
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta


#네이버 api 
Client_id = "zdqMoIkFaK8uKvC2oNY2"
Client_Secret ="LiZfsgtuD5"

#네이버 쇼핑 api 요청 주소
NAVER_SHOP_API_URL="https://openapi.naver.com/v1/search/shop?query="


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

client = MongoClient('mongodb://54.180.151.195', 27017, username="test", password="test")
db = client.dbsparta_plus_week4


# index HTML 화면 보여주기
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('index.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


#리턴값 변환 함수
def as_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        res = f(*args, **kwargs)
        res = json.dumps(res, ensure_ascii=False).encode('utf8')
        return Response(res, content_type='application/json; charset=utf-8')

    return decorated_function


# login page
@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


# login server
@app.route('/sign_in', methods=['POST'])
def sign_in():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# 회원가입
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    # DB에 저장
    doc = {
        "username": username_receive,                               # 아이디
        "password": password_hash,                                  # 비밀번호
        "profile_name": username_receive,                           # 프로필 이름 기본값은 아이디
        "profile_pic": "",                                          # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png", # 프로필 사진 기본 이미지
        "profile_info": ""                                          # 프로필 한 마디
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


# ID 중복확인
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})



#naver api 가져오기 함수
def getSearchList(keyword,URL):
    itemList =[]
    encText = urllib.parse.quote(keyword) 
    url=URL + encText
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",Client_id)
    request.add_header("X-Naver-Client-Secret",Client_Secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    response_body = response.read()
    jsonString = response_body.decode("utf-8")
    jsonDict =json.loads(jsonString)
    items = jsonDict['items']

    for item in items:
        title = item['title']
        link =item['link']
        image =item['image']
        lprice = item['lprice']
        productId = item['productId']
        itemList.append({'title':title,'link': link, 'image': image, 'lprice': lprice, 'productId': productId})

    return itemList;

# API 역할을 하는 부분
@app.route('/api/getItemList', methods=['GET'])
@as_json
def getShops():

    if 'keyword' in request.args:
        keyword = str(request.args['keyword'])
    else:
        return jsonify({'msg': '검색어를 입력해주세요.'})
    
    return getSearchList(keyword,NAVER_SHOP_API_URL)

# 찜 추가
@app.route('/user/saveJJIM', methods=['POST'])
def save_jjim():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        productId = request.form['productId']
        title = request.form['title']
        link = request.form['link']
        lprice = request.form['lprice']
        image = request.form['image']

        product = db.product.find_one({"userid": payload["id"], "productId": productId}, {"_id": False})
        if( product is not None ):
            return jsonify({'msg': '해당 상품은 이미 찜하셨어요🙌'})
        
        db.product.insert_one({"userid":payload["id"], "productId":productId, "image":image, "title":title, "lprice":lprice, "link":link})
        return jsonify({'msg': '찜 완료❤'})
        
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

# 찜 삭제
@app.route('/user/deleteJJIM', methods=['POST'])
def delete_jjim():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        productId = request.form['productId']
        product = db.product.delete_one({"userid": payload["id"], "productId": productId})

        if( product is None ):
            return jsonify({'msg': '존재하지 않는 상품입니다.'})
        else:
            return jsonify({'result': 'success', 'msg': '찜이 삭제되었습니다😢'})
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 찜 목록
@app.route('/user/getListJJIM', methods=['GET'])
def get_jjim():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        products = list(db.product.find({"userid": payload["id"]},{'_id':False}))

        return jsonify({'my_products': products})
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)