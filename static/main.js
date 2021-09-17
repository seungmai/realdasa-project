function searchItems() {
    $('#item-list').empty();
    let keyword = $("#keyword").val();
    console.log(keyword);
    $.ajax({
        type: "GET",
        url: "/api/getItemList?keyword=" + keyword,
        data: {},
        success: function (response) {
            for (let i in response) {
                let product = response[i];
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
                                        <a href=${link} style="color: #f2d184">최저가 구매하기</a>
                                        <a style="color: #f2d184" onclick="save_jjim('${productId}', '${title}',' ${link}',' ${lprice}', '${image}')" >찜하기하트</a>
                                    </div>
                                </div>`;
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

function save_jjim(productId, title, link, image, lprice) {
    console.log(productId, title, link, image, lprice);
    $.ajax({
      type:"POST",
      url:"/user/saveJJIM",
      dataType : "json",
      data:{
        "productId": productId,
        "title": title,
        "image": image,
        "lprice": lprice,
        "link": link
      },
      success: function(response){
        alert(response['msg']);
          window.location.href="/user/{{ user_info.username }}"
      }
    });
}
  
function delete_jjim() {
    $.ajax({
        type:"POST",
        url:"/user/deleteJJIM",
        data:{
            productId: productId
        },
        success: function(response){
            alert(response['msg']);
            window.location.href="/user/{{ user_info.username }}"
        }
    });
}

function getMyProducts(products) {
    let my_products = products;
    for( i=0; i<my_products.length; i++)
    {
        let product = my_products[i];
        let title = product.title;
        let link = product.link;
        let lprice = product.lprice;
        let image = product.image;
        let productId = product.productId;
        // console.log( title, lprice );
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
                                <a style="color: #f2d184" onclick="save_jjim('${productId}', '${title}',' ${link}',' ${lprice}', '${image}')" >찜하기하트</a>
                            </div>
                        </div>`;
        $("#my-item-list").append(temp_html);
    }
}
