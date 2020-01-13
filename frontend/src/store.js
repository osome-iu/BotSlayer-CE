import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
    state: 
    {
        configINIFields:
        {
            consumerKey: '',
            consumerSecret: '',
            accessToken: '',
            accessTokenSecret: '',
            seed: {},
            pinned: {},
            dbname: 'bev',
            user: 'bev',
            password: 'bev'
        }
    },
    mutations: 
    {

    },
    actions: 
    {
        
    }
})
