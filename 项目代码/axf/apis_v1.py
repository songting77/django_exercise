from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Sum
from django.forms import model_to_dict
from django.http import HttpResponse, QueryDict, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic.base import View
from axf import models
import json

# 操作成功
SUCCESS = 1
# 没登录
UNLOGIN = 2
# 库存不够
NOSTORENUM = 3
# 商品不在购物车
ITEMNOTEXISTS = 4
# 下单失败
ORDERFAILED = 5

DATA = {
        "code": SUCCESS,
        "msg": "ok",
        "data": ""
    }
#商品加入购物车
# @login_required(login_url="/axf/login")
def cart_api(req):
    data = DATA
    if req.method == "GET":
        user = req.user
        if isinstance(user, models.MyUser):
            param = req.GET
            item_id = param.get("item_id")
            operate_type = param.get("operate_type")
            carts = models.Cart.objects.filter(
                user_id=user.id,
                item_id=item_id)
            # 判断操作类型 是加还是减
            if operate_type == "add":

                my_item = models.Goods.objects.get(pk=item_id)
                # 看库存
                if my_item.storenums < 1:
                    data['code'] = NOSTORENUM
                    data["msg"] = "已售罄"
                    return HttpResponse(json.dumps(data))
                # 说明用户第一次添加这个商品
                if carts.count() == 0:

                    # 创建了一条购物车记录
                    my_cart = models.Cart.objects.create(
                        user=user,
                        item_id=item_id
                    )
                    data['data'] = my_cart.num
                    return HttpResponse(json.dumps(data))
                # 不是第一次加
                else:
                    my_cart = carts.first()
                    my_cart.num += 1
                    my_cart.save()
                    data['data'] = my_cart.num
                    return HttpResponse(json.dumps(data))
            else:
                # 能找到对应的商品
                if carts.count() == 1:
                    my_cart = carts.first()
                    my_cart.num = my_cart.num - 1
                    my_cart.save()
                    # 商品数量是0的时候
                    if my_cart.num == 0:
                        my_cart.delete()
                        data['data'] = 0
                        return HttpResponse(json.dumps(data))
                    # 商品数量不是0的时候
                    else:
                        data['data'] = my_cart.num
                        return HttpResponse(json.dumps(data))
                else:
                    data['code'] = ITEMNOTEXISTS
                    data['msg'] = "商品不在您的购物车"
                    return HttpResponse(json.dumps(data))

        else:
            data = {
                "code": UNLOGIN,
                "msg":"需要登录",
                "data":"/axf/login"
            }
            return HttpResponse(json.dumps(data))

# 对购物车内商品的加减操作
class CartItemApi(View):
    def put(self, req):
        param = QueryDict(req.body)
        c_id = param.get("c_id")
        operate_type = param.get("operate_type")
        user = req.user
        my_cart = models.Cart.objects.get(pk=int(c_id))
        if isinstance(user, models.MyUser):
            #     判断操作是什么
            if operate_type == "sub":
                # my_cart = models.Cart.objects.get(pk=int(c_id))
                my_cart.num = my_cart.num - 1
                my_cart.save()
                if my_cart.num == 0:
                    my_cart.delete()
                    DATA['code'] = ITEMNOTEXISTS
                    return JsonResponse(DATA)
                else:
                    DATA['data'] = my_cart.num
                    return JsonResponse(DATA)
            else:
                # 看库存够不够
                if my_cart.item.storenums > 0:
                    my_cart.num += 1
                    my_cart.save()
                    DATA['data'] = my_cart.num
                    return JsonResponse(DATA)
                else:
                    DATA['code'] = NOSTORENUM
                    return JsonResponse(DATA)
        else:
            return redirect("/axf/login")


class CartItemStatusApi(View):

    def put(self, req):
        param = QueryDict(req.body)
        # 确认用户登录
        user = req.user
        if isinstance(user, models.MyUser):
            pass
        else:
            return redirect("/axf/login")
        # 拿参数获取购物车商品
        c_id = int(param.get('c_id'))
        cart_item = models.Cart.objects.get(pk=c_id)
        # 选中状态取反
        cart_item.is_selected = not cart_item.is_selected
        cart_item.save()

        # 为了算钱 看全选状态 我们先拿到全部的某个用户的购物车商品
        cart_items = models.Cart.objects.filter(
            user=user
        )
        # 找选中
        select_items = cart_items.filter(is_selected=True)
        # 找没选中
        unselect_items = cart_items.filter(is_selected=False)
        #         算钱
        sum = 0
        for i in select_items:
            sum += i.num * i.item.price
#         看全选按钮的状态
        is_all_selected = True if unselect_items.count()==0 else False
        # 把全选按钮的状态，总价，当前点击的那个购物车状态返回给前端
        DATA['data'] = {
            'is_all_selected': is_all_selected,
            'sum_price': round(sum, 2),
            'current_btn_status': cart_item.is_selected
        }
        return JsonResponse(DATA)

class CartAllSelectAPI(View):
    def post(self, req):
        user = req.user
        if isinstance(user, models.MyUser):
            pass
        else:
            return redirect("/axf/login")
        param = req.POST
        is_all_select = param.get("is_all_select")
        # 拿到要操作的商品
        cart_items = models.Cart.objects.filter(user=user)
        if is_all_select == 'false':
        #     全都不全
            cart_items.update(is_selected=False)
            DATA['data'] = "0.0"
        else:
            cart_items.update(is_selected=True)
            sum = 0
            for i in cart_items:
                sum += i.num * i.item.price
            DATA['data'] = round(sum, 2)
        return JsonResponse(DATA)

class OrderAPI(View):

    def post(self, req):
        user = req.user
        if isinstance(user, models.MyUser):
            pass
        else:
            return redirect("/axf/login")
        # 拿购物车的商品
        cart_items = models.Cart.objects.filter(
            user=user,
            is_selected=True
        )
        if (cart_items.count() == 0):
            DATA['code'] = ORDERFAILED
            DATA['msg'] = "购物车内无选中商品"
            return  JsonResponse(DATA)
        # 算钱
        sum = 0
        for i in cart_items:
            sum += i.num * i.item.price
        # 创建订单
        my_order = models.Order.objects.create(
            user=user,
            sum_price=sum
        )
        result = {}
        result['order_id'] = my_order.id
        result['sum_price'] = sum
        order_items = []
        # 创建订单详情
        for i in cart_items:
            models.OrderItem.objects.create(
                order=my_order,
                item=i.item,
                num=i.num
            )
            order_items.append(model_to_dict(i.item))
        result['order_items'] = order_items
        DATA['data'] = result
        return JsonResponse(DATA)
        # return render(req, "order/order_pay.html", result)


def many_params(req):
    data=req.GET.get('data')
    print(data, type(data))
    # 将json字符串转字典或者数组
    my_data = json.loads(data)
    print(my_data, type(my_data))
    return HttpResponse("ok")