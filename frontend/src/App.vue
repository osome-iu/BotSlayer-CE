<template>
  <div id="app" style="overflow: auto;">
    <div>
      <b-navbar toggleable="lg" style="background-color: #147340; padding: 0px">
        <b-navbar-brand style="padding: 0px"><h1 style="margin: 0px"><router-link to="/dataPage" style="color: white"><img class="m-2" src="https://i.imgur.com/3hA1d9H.png">BotSlayer-CE</router-link></h1></b-navbar-brand>
        <b-navbar-toggle class="navbar-dark ml-auto" target="nav-collapse"></b-navbar-toggle>
        <b-collapse id="nav-collapse" is-nav>
        <b-navbar-nav class="ml-auto">
          <b-nav-item><h4><router-link to="/dataPage" style="color: white">Data</router-link></h4></b-nav-item>
          <b-nav-item><h4><router-link to="/config" style="color: white">Config</router-link></h4></b-nav-item>
          <b-nav-item><h4><router-link to="/about" style="color: white">About</router-link></h4></b-nav-item>
          <b-nav-item><h4><router-link to="/help" style="color: white">Help</router-link></h4></b-nav-item>
        </b-navbar-nav>
        </b-collapse>
      </b-navbar>
    </div>
    <router-view
    :configINI = "appConfigINI"
    @sendConfig="sendConfigHandler"/>
  </div>
</template>

<script>
    import Config from "../config.json"
    export default{
        name: 'app',
        data: function()
        {
          return{
          appConfigINI: 
          {
            consumerKey: '',
            consumerSecret: '',
            accessToken: '',
            accessTokenSecret: '',
            seed: {},
            dbname: 'bev',
            user: 'bev',
            password: 'bev'
          }
        }
        },
        methods:
        {
            sendConfigHandler: function(event, payload)
            {
                this.appConfigINI = payload;
                this.readConfig();
            },
            readConfig: function()
            {
                let vm = this;

                var readConfigPromise = this.axios.get(Config.api_host + '/configRead',
                {
                    responseType: "json",
                });
                readConfigPromise.then
                (
                    function(response)
                    {
                        vm.appConfigINI = response.data;
                    },
                    function(error)
                    {
                        console.warn("No JSON retrieved.");
                    }
                )
            }
        },
        created()
        {
            document.title = "BotSlayer-CE";
            this.readConfig();
        }
    }
</script>

<style lang="scss">
  #app 
  {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    font-display: swap;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    color: #2c3e50;
    background-color: #fafafa;
  }
</style>
