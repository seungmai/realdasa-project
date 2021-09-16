$(document).ready(function () {});

function searchItems(keyword) {
  $("#item-list").empty();
  $.ajax({
    type: "GET",
    url: "/api/getItemList?keyword=" + keyword,
    data: {},
    success: function (response) {
      for (let i = 0; i < 9; i++ && i in response) {
        let title = response[i].title;
        let link = response[i].link;
        let lprice = response[i].lprice;
        let image = response[i].image;
        let productId = response[i].productId;

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
                                        <a href=${link} target='_blank' style="color: #f2d184">최저가 구매하기</a>
                                        <a href=${productId} style="color: #f2d184">찜하기하트</a>
                                    </div>
                                </div>`;

        console.log(i);
        $("#item-list").append(temp_html);
      }
    },
  });
}

function searchClick() {
  let keyword = $("#keyword").val();
  searchItems(keyword);
}

function sign_out() {
  $.removeCookie("mytoken", { path: "/" });
  alert("안전하게 로그아웃이 되었습니다.");
  window.location.href = "/login";
}

function main() {
  window.location.href = "/";
}
