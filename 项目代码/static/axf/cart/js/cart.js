$(function () {
//    给加按钮添加点击事件
    $(".subBtn").click(function () {
        var $current_btn = $(this);
        var $parent_li = $current_btn.parents("li");
        // console.log($parent_li.attr("cartid"));
        $.ajax({
            url:"/axf/api/v1/itemcart",
            method:"put",
            data:{
                'c_id': $parent_li.attr("cartid"),
                'operate_type': 'sub'
            },
            success:function (result) {
                console.log(result);
                if (result.code == 1){
                //    不是减到0的情况
                    $current_btn.next().html(result.data);

                } else {
                    $parent_li.remove();
                }
            }
        })
    })

    //加操作
    $(".addBtn").click(function () {
        var $current_btn = $(this);
        var $parent_li = $current_btn.parents("li");
        // console.log($parent_li.attr("cartid"));
        $.ajax({
            url:"/axf/api/v1/itemcart",
            method:"put",
            data:{
                'c_id': $parent_li.attr("cartid"),
                'operate_type': 'add'
            },
            success:function (result) {
                console.log(result);
                if (result.code == 1){
                //    不是减到0的情况
                    $current_btn.prev().html(result.data);

                } else {
                    alert(result.msg);
                }
            }
        })
    })


    $(".confirm").click(function () {
        $current_btn = $(this);
        $parent_li = $(this).parents("li");
        var c_id = $parent_li.attr("cartid");
        $.ajax({
            url:"/axf/api/v1/statusofcartitem",
            data:{
                'c_id':c_id
            },
            method:"put",
            success:function (res) {
                // console.log(res);
                //判断当前按钮的状态如何修改
                if (res.data.current_btn_status){
                    $current_btn.find("span").find("span").html("√");
                } else {
                    $current_btn.find("span").find("span").html("");
                }
            //    判断全选按钮
                if(res.data.is_all_selected){
                    $(".all_select > span > span").html("√");
                } else {
                    $(".all_select > span > span").html("");
                }
            //    设置金额

                $("#sum_price").html(res.data.sum_price);
            }
        })
    })

    $(".all_select").click(function () {
        var $myspan = $(this).find("span").find("span");
        // 默认 全选上
        var is_all_select = true;
        if ($myspan.html().length > 0){
            // 如果现在是又对勾的情况 告诉后台 全都不选
            is_all_select = false
        }

        $.ajax({
            url:"/axf/api/v1/allselect",
            data:{
                "is_all_select": is_all_select
            },
            method:"post",
            success:function (res) {
                console.log(res);
                // 拿钱
                var money = res.data;
                $("#sum_price").html(money);

                if (is_all_select){
                    //全选按钮
                    $myspan.html("√");
                    $(".confirm").each(function () {
                        $(this).find("span").find("span").html("√")
                    })
                } else {
                    $myspan.html("");
                    $(".confirm").each(function () {
                        $(this).find("span").find("span").html("")
                    })
                }
            }
        })
    })

    $("#order").click(function () {
       // 看看是不是有选中的商品
        var money = parseFloat($("#sum_price").html());
        if (money == 0) {
            alert("不选东西 你下什么单");
        } else {
            $.ajax({
                url:"/axf/api/v1/order",
                method:"post",
                success:function (res) {
                    console.log(res)
                    if (res.code != 1){
                        alert("服务器睡着了");
                    }
                }
            })
        }
    });
})