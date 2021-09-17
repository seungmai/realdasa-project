function searchItems() {
  $("#item-list").empty();
  let keyword = $("#keyword").val();

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

        let temp_html = `<div class="card border-warning  mb-3" style="width:18rem;">
                                  <div class=" border-warning  mb-3">
                                      <img class="card-img-top" style="width: 18rem; height:20rem;"src="${image}" alt="Card image cap">
                                  </div>
                                  <div class="card-body text-warning card-text">
                                      <ul class="list-group list-group-flush">
                                          <li class="list-group-item">${title}</li>
                                          <li class="list-group-item row-price">최저가 ${lprice}원</li>
                                      </ul>
                                  </div>
                                  <div class="btn-box">
                                  <button class="button is-danger is-light"><a href=${link} target='_blank' style="color: #ea4c89">최저가 구매하기</a></button>
                                  <button class="button is-info is-light"><a style="color: f4c046" onclick="save_jjim('${productId}', '${title}',' ${link}',' ${lprice}', '${image}')" >찜하기<i class="fab fa-gratipay"></i></a></button>    
                                  </div>
                              </div>`;
        $("#item-list").append(temp_html);
      }
    },
  });
}

function sign_out() {
  $.removeCookie("mytoken", { path: "/" });
  alert("안전하게 로그아웃이 되었습니다.");
  window.location.href = "/login";
}

function main() {
  window.location.href = "/";
}

function save_jjim(productId, title, link, lprice, image) {
  $.ajax({
    type: "POST",
    url: "/user/saveJJIM",
    data: {
      productId: productId,
      title: title,
      link: link,
      lprice: lprice,
      image: image,
    },
    success: function (response) {
      alert(response["msg"]);
      searchItems();
    },
  });
}

function delete_jjim(productId) {
  $.ajax({
    type: "POST",
    url: "/user/deleteJJIM",
    data: {
      productId: productId,
    },
    success: function (response) {
      alert(response["msg"]);
      window.location.href = "/user/{{ user_info.username }}";
    },
  });
}

function Enter_search() {
  if (event.keyCode == 13) {
    searchItems();

    return;
  }
}
