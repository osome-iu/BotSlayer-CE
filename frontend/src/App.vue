<template>
  <div id="app" style="overflow: auto;">
    <div>
      <b-navbar toggleable="lg" style="background-color: #147340; padding: 0px">
        <b-navbar-brand style="padding: 0px"><h1 style="margin: 0px"><router-link to="/dataPage" style="color: white"><img class="m-2" src="assets/BotSlayer-Navbar.png">BotSlayer-CE&nbsp;<span style="color: rgb(160, 255, 64)">beta</span><canvas id="myCanvas" width="1" height="1"></canvas></router-link></h1></b-navbar-brand>
        <b-navbar-toggle class="navbar-dark ml-auto" target="nav-collapse"></b-navbar-toggle>
        <b-collapse id="nav-collapse" is-nav>
        <b-navbar-nav class="ml-auto">
          <b-nav-item><h4><router-link to="/dataPage" style="color: white">Data</router-link></h4></b-nav-item>
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
                    pinned: {},
                    user: {},
                    location: ''
                }
            }
        },
        methods:
        {
            sendConfigHandler: function(event, payload)
            {
                this.appConfigINI = payload;
                this.readConfigSeed();
            },
            readConfigSeed: function()
            {
                let vm = this;

                var readConfigSeedPromise = this.axios.get(Config.api_host + '/configReadSeed',
                {
                    responseType: "json",
                });
                readConfigSeedPromise.then
                (
                    function(response)
                    {
                        vm.appConfigINI.seed = response.data.seed;
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
            document.title = "BotSlayer-CE beta";
            this.readConfigSeed();
            this.axios.defaults.headers = {
              'X-CSRFToken': csrf_token
            }
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
