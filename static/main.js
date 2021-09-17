function searchItems() {

    // 재검색 시, 검색 목록 초기화
    $("#item-list").empty();

    // 검색어 keyword 변수에 받아오기
    let keyword = $("#keyword").val();

    // 검색어(keyword)로 검색된 결과 상품목록 조회하여 index.html의 #item-list에 붙이기
    $.ajax({
        type: "GET",
        url: "/api/getItemList?keyword=" + keyword,
        data: {},
        success: function (response) {
            for (let i = 0; i < 9; i++ && i in response) {
                let product = response[i];
                let title = product.title;
                let link = product.link;
                let lprice = product.lprice;
                let image = product.image;
                let productId = product.productId;
           
                let temp_html = `<div class="card border-warning  mb-3" style="width:18rem">
                                <div class=" border-warning  mb-3">
                                    <img class="card-img-top" style="width: 18rem;"src="${image}" alt="Card image cap">
                                </div>
                                <div class="card-body text-warning ">
                                    <ul class="list-group list-group-flush">
                                        <li class="list-group-item" style="font-weight: bold">${title}</li>
                                        <li class="list-group-item">최저가 ${lprice}</li>
                                    </ul>
                                </div>
                                <div>
                                    
                                <button class="button is-danger is-light"><a href=${link} target='_blank' style="color: #ea4c89">최저가 구매하기</a></button>
                                <button class="button is-info is-light"><a style="color: f4c046" onclick="save_jjim('${productId}', '${title}',' ${link}',' ${lprice}', '${image}'" >찜하기<i class="fab fa-gratipay"></i></a></button>    
                                </div>
                            </div>`;
                $("#item-list").append(temp_html);
            }
        },
    });
}

// 로그아웃 시 메시지 띄워준 후 로그인 화면으로 이동
function sign_out() {
  $.removeCookie("mytoken", { path: "/" });
  alert("안전하게 로그아웃이 되었습니다.");
  window.location.href = "/login";
}

// 메인 화면 이동
function main() {
  window.location.href = "/";
}

// 찜 삼품 추가
function save_jjim(productId, title, link, lprice, image) {
    $.ajax({
        type: "POST",
        url: "/user/saveJJIM",
        data: {
            productId: productId,   // 상품 id
            title: title,           // 상품명
            link: link,             // 최저가 구매 화면 연결 링크
            lprice: lprice,         // 최저가
            image: image,           // 상품 이미지
        },
        success: function (response) {
            alert(response["msg"]); // "찜 완료❤"
            searchItems();          // 상품 재조회(index.xml 화면에 고정)
        },
    });
}

// 찜 삼품 삭제
function delete_jjim(productId) {
  $.ajax({
    type: "POST",
    url: "/user/deleteJJIM",
    data: {
      productId: productId,         // 상품 id
    },
    success: function (response) {
      alert(response["msg"]);       // "찜이 삭제되었습니다😢"
      window.location.href = "/user/{{ user_info.username }}";  // 사용자 개인 화면 (찜 버튼 화면)에 고정
    },
  });
}

// 검색어 입력 후 엔터 클릭 시, 상품 목록 조회
function Enter_search() {
  if (event.keyCode == 13) {
    searchItems();

    return;
  }
}
