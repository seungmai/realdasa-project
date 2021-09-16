
// AOS
AOS.init();

$(document).ready(function () {
});

product_id = soup.select_onee()

function searchItems(keyword) {
    $.ajax({
        type: "GET",
        url: "/api/getItemList?keyword=" + keyword,
        data: {},
        success: function (response) {
            for (let i in response) {
                let title = response[i].title;
                let link = response[i].link;
                let lprice = response[i].lprice;
                let image = response[i].image;



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
                                        <a href=${link} style="color: #f2d184">최저가 구매하기</a>
                                        <a href=${link} style="color: #f2d184">최저가 구매하기</a>
                                    </div>
                                </div>`;

                console.log(temp_html);
                $("#item-list").append(temp_html);
            }
        },
    });
}

function sign_out() {
    $.removeCookie("mytoken", {path: "/"});
    alert("안전하게 로그아웃이 되었습니다.");
    window.location.href = "/login";
}

function main() {
    window.location.href = "/";
}
