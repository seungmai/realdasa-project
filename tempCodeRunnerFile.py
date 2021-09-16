# 찜 추가
@app.route('/user/saveJJIM', methods=['POST'])
@as_json
def save_jjim():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # productId = request.form['productId']
        # image = request.form['image']
        # title = request.form['title']
        # lprice = request.form['lprice']
        # link = request.form['link']

        # productId = request.form['productId']
        # image = request.form['image']
        # title = request.form['title']
        # lprice = request.form['lprice']
        # link = request.form['link']

        # print( product )
        # if( db.product.find_one({"userid": payload["id"], "itemId": productId}).count() > 0 ):
        #     return jsonify({'msg': '해당 상품은 이미 저장되어있습니다.'})
        
        # db.product.insert_one({"userid": payload["id"], "itemId": productId, "image": image, "title": title, "lprice": lprice, "link": link})
        # product = jsonify({productId: productId, image: image, title: title, lprice: lprice, link: link });
        return render_template('user.html')
        
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))