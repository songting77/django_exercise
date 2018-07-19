$(function () {
    initTopSwiper();
    initMustSwiper();
})

function initTopSwiper() {
    var mySwiper = new Swiper ('#topSwiper', {
    // direction: 'vertical',
    loop: true,
    autoplay:2000,
    // 如果需要分页器
    pagination: '.swiper-pagination',

    // 如果需要前进后退按钮
    nextButton: '.swiper-button-next',
    prevButton: '.swiper-button-prev',


  })
}

function initMustSwiper() {
    var mySwipers = new Swiper ('#swiperMenu', {
    // direction: 'vertical',
        slidesPerView: 3,
  })
}