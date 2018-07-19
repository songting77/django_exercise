from django.conf.urls import url
from axf import apis_v1 as apis

urlpatterns = [
url(r"^cart$", apis.cart_api, name="item_cart"),
url(r"^itemcart$", apis.CartItemApi.as_view()),
url(r"^statusofcartitem$", apis.CartItemStatusApi.as_view()),
url(r"^allselect$", apis.CartAllSelectAPI.as_view()),
url(r"^order$", apis.OrderAPI.as_view()),
url(r"^many_params$", apis.many_params)
]