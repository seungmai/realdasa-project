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


#네이버 api 의 요청받은 정보
Client_id = "zdqMoIkFaK8uKvC2oNY2"
Client_Secret ="LiZfsgtuD5"

#네이버 쇼핑 api 요청 주소
NAVER_SHOP_API_URL="https://openapi.naver.com/v1/search/shop?query="


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

# AWS 배포 DB 정보
client = MongoClient('mongodb://54.180.151.195', 27017, username="test", password="test")
db = client.dbsparta_plus_week4


# index.html 또는 login.html 화면 보여주기
@app.route('/')
def home():
    # jwt 토큰 방식으로 사용자 정보 가져옴
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        return render_template('index.html', username=payload["id"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


#리턴값 json으로 변환 함수
def as_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        res = f(*args, **kwargs)
        res = json.dumps(res, ensure_ascii=False).encode('utf8')
        return Response(res, content_type='application/json; charset=utf-8')

    return decorated_function


# 로그인 page
@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


# 사용자 로그인
@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 사용자 id, pw 정보
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    # 사용자 pw 는 sha256 방식으로 암호화하여 pw_hash 받아 DB 테이블 중 users 에서 사용자 find 할 때 사용
    # 사용자가 회원가입 할 때 입력한 pw를 sha256 방식으로 암호화 하여 저장하였기 때문
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    # 회원가입 정보가 있는 사용자일 경우
    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }

        # 사용자 정보를 jwt 인증 방식을 사용하여 (토큰 타입 & 알고리즘 타입 HS256) 암호화된 token을 제공
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        # 사용자의 정보가 jwt 인증 방식으로 암호화된 token을 return
        # 후에 사용자의 token명은 mytoken이 됨 (login.html 참고.)
        return jsonify({'result': 'success', 'token': token})
    
    # 아이디/비밀번호가 일치하는 사용자가 없을 경우 또는 회원가입 정보가 없는 사용자일 경우
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# 회원가입
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    # 사용자 pw는 sha256 방식으로 암호화
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

    # 사용자 저장
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


# ID 중복확인
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():

    # username_receive(username_give, username) 가 userid 입니다.
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})



# 검색어를 통해 Naver Api에서 상품 가져오기
def getSearchList(keyword,URL):
    itemList =[]

    # api 주소에 client의 정보를 넣어 정보 받아오기
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
        title = item['title']               # 상품명
        link =item['link']                  # 최저가 구매 화면 연결 링크
        image =item['image']                # 상품 이미지
        lprice = item['lprice']             # 최저가
        productId = item['productId']       # 상품 id
        itemList.append({'title':title,'link': link, 'image': image, 'lprice': lprice, 'productId': productId})

    return itemList;

# 검색어가 제대로 넘어왔는지 확인
@app.route('/api/getItemList', methods=['GET'])
@as_json
def getShops():

    if 'keyword' in request.args:
        keyword = str(request.args['keyword'])
    else:
        return jsonify({'msg': '검색어를 입력해주세요.'})
    
     # 검색어를 통해 Naver Api에서 상품 가져오기
    return getSearchList(keyword,NAVER_SHOP_API_URL)

# 찜한 상품 추가
@app.route('/user/saveJJIM', methods=['POST'])
def save_jjim():
    # mytoken(사용자의 token)을 받아 사용자의 정보 token_receive을 받기
    token_receive = request.cookies.get('mytoken')
    try:
        # jwt 인증방식 복호화하여 사용자 정보 받기
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        # 상품 id로 조회하기 위해 값 받아오기(상품id는 고유)
        productId = request.form['productId']
        title = request.form['title']
        link = request.form['link']
        lprice = request.form['lprice']
        image = request.form['image']

        # 사용자id와 상품id로 찜한 목록에 이미 존재하는지 확인하여 찜 중복 방지 
        product = db.product.find_one({"userid": payload["id"], "productId": productId}, {"_id": False})    
        if( product is not None ):
            return jsonify({'msg': '해당 상품은 이미 찜하셨어요🙌'})
        
        # 찜한 상품 저장
        db.product.insert_one({"userid":payload["id"], "productId":productId, "image":image, "title":title, "lprice":lprice, "link":link})
        return jsonify({'msg': '찜 완료❤'})
        
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))      # 해당 사용자의 payload 정보가 만료되었을 경우, login.html로 이동
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))   # 해당 사용자의 payload 정보가 존재하지 않을 경우, login.html로 이동

# 찜한 상품 삭제
@app.route('/user/deleteJJIM', methods=['POST'])
def delete_jjim():
    # mytoken(사용자의 token)을 받아 사용자의 정보 token_receive을 받기
    token_receive = request.cookies.get('mytoken')
    try:
        # jwt 인증방식으로 복호화하여 사용자 정보 받기
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        # 사용자 id와 상품 id로 조회하여 사용자가 찜한 상품 삭제(상품id는 고유)
        productId = request.form['productId']
        product = db.product.delete_one({"userid": payload["id"], "productId": productId})

        # 데이터에 해당하는 상품이 없을 경우
        if( product is None ):
            return jsonify({'msg': '존재하지 않는 상품입니다.'})                    # 해당 사용자의 payload 정보가 만료되었을 경우, login.html로 이동
        else:
            return jsonify({'result': 'success', 'msg': '찜이 삭제되었습니다😢'})   # 해당 사용자의 payload 정보가 존재하지 않을 경우, login.html로 이동
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 찜한 상품 목록 가져오기
@app.route('/user/getListJJIM', methods=['GET'])
def get_jjim():
    # mytoken(사용자의 token)을 받아 사용자의 정보 token_receive을 받기
    token_receive = request.cookies.get('mytoken')
    try:
        # jwt 인증방식으로 복호화하여 사용자 정보 받기
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 사용자가 찜한 상품 가져와 list방식으로, 그리고 json으로 만들기
        products = list(db.product.find({"userid": payload["id"]},{'_id':False}))

        return jsonify({'my_products': products})
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))      # 해당 사용자의 payload 정보가 만료되었을 경우, login.html로 이동
    except jwt.exceptions.DecodeError:  
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))   # 해당 사용자의 payload 정보가 존재하지 않을 경우, login.html로 이동


# 프로필 업데이트
@app.route('/update_profile', methods=['POST'])
def save_img():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


## 멘토님과 논의하고 싶은 함수
# 각 사용자의 찜한 상품 목록 보여주기
@app.route('/user/<username>')
def user(username):
    # mytoken(사용자의 token)을 받아 사용자의 정보 token_receive 받기
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = (username == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

        # products = list(db.product.find({"userid": payload["id"]},{'_id':False}))
        # return render_template('user.html', username=payload["id"], status=status, products=products )
        # ---> render_template에는 products 같은 json은 사용 할 수 있다고 들었는데, 
        # user.html의 function에서 사용 시, 변수에 담을 수 없는 것 같습니다.
        # 수업 내용 예시에서의 user_info.username도 let name = {{user_info.username}} 으로 사용하면 console에서 에러가 발생합니다.
        return render_template('user.html', username=payload["id"], status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)