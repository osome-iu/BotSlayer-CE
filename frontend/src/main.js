import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

import axios from "axios";
import VueAxios from "vue-axios";

import VueTimeago from 'vue-timeago'

import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-vue/dist/bootstrap-vue.min.css'

import { library } from '@fortawesome/fontawesome-svg-core'
import { faGoogle, faTwitter, faFacebookSquare, faYoutube, faRedditAlien } from '@fortawesome/free-brands-svg-icons'
import { faRetweet, faHeartbeat, faRobot, faQuestionCircle, faChartLine } from '@fortawesome/free-solid-svg-icons'
import { faSquare, faCheckSquare } from '@fortawesome/free-regular-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

import KonamiCode from "vue-konami-code"

import Datetime from 'vue-datetime'
import 'vue-datetime/dist/vue-datetime.css'

import VueApexCharts from 'vue-apexcharts'

Vue.use(VueAxios, axios);

// Used for the "Last Seen" column
Vue.use(VueTimeago, {
  name: 'Timeago',
  locale: 'en'
});

// Used in the b-button, b-table, etc.
// Very reactive bootstrap elements this way
import BootstrapVue from 'bootstrap-vue'
Vue.use(BootstrapVue);

// FontAwesome inclusions
library.add(faGoogle, faTwitter, faFacebookSquare, faYoutube, faRedditAlien, faRetweet, faHeartbeat, faRobot, faQuestionCircle, faChartLine, faSquare, faCheckSquare);
Vue.component('font-awesome-icon', FontAwesomeIcon);

Vue.use(KonamiCode, {callback: function (){
  var canvas = document.getElementById("myCanvas");
  var image = document.createElement("img");
  image.src = 'assets/bottousai.png';
  image.onload = function (a) {
    var h = a.target.height,
        w = a.target.width;
    var c = canvas.getContext('2d');
    canvas.width = w;
    canvas.height = h;
    c.drawImage(image, 0, 0);
  }}});

// Mobile-esque calendar date-picker
Vue.use(Datetime)

Vue.use(VueApexCharts)
Vue.component('apexchart', VueApexCharts)

Vue.config.productionTip = false;

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
