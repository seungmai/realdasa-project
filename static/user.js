$(document).ready(function () {
  
  // 사용자 개인 화면 열릴(JJIM 버튼 화면) 때 개인 찜 상품 목록 조회
  getMyProducts();
});

// 사용자 개인 찜 상품 목록 조회하여 #my-item-list에 붙이기
function getMyProducts() {
  $.ajax({
    type: "GET",
    url: "/user/getListJJIM",
    data: {},
    success: function (response) {
      my_products = response["my_products"];
      for (i = 0; i < my_products.length; i++) {
        let product = my_products[i];
        let title = product.title;
        let link = product.link;
        let lprice = product.lprice;
        let image = product.image;
        let productId = product.productId;

        let temp_html = `<div class="jjim-list box">
        <div>
            <img class="item-img" src="${image}">
        </div>
        <div class="list-text">
        <div>
            <ul class="list-title">
                <li>${title}</li>
                <li class="price" style="color:red;">최저가 ${lprice}원</li>
            </ul>
        </div>
        <div>
            <button class="button is-danger is-light buy-btn"><a href=${link} target='_blank' style="color: #ea4c89">최저가 구매하기</a></button>
            <button class="button is-success is-light"><a style="color: #69ADB8" onclick="delete_jjim('${productId}')">찜삭제 <i class="fas fa-times-circle"></i></a></button>
        </div>
        </div>
</div>`;

        $("#my-item-list").append(temp_html);
      }
    },
  });
}
