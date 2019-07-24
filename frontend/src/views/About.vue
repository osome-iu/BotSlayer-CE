<template>
  <div class="about">
    <h3 style="color: #00bb00; margin: 10px;">About BotSlayer (Community Edition)</h3>
    <div class="container">
      <p class="text-left">The "CE" version of BotSlayer is not meant for research, as it uses simple heuristics to calculate bot scores. We strongly recommend the "Pro" version of BotSlayer, which has proprietary BotometerLite software and many other improvements. It is available for free, but will share data with Indiana University for research purposes.</p>

      <p class="text-left">BotSlayer is an application that helps track and detect potential manipulation of information spreading on Twitter. The tool is developed by the <a href="https://osome.iuni.iu.edu/" target="_blank ">Observatory on Social Media</a> at Indiana University --- the same lab that brought to you Botometer and Hoaxy.</p>

      <p class="text-left">BotSlayer can be used, for example, by journalists, corporations, and political candidates to discover in real-time new coordinated campaigns in their domains of interest, without any prior knowledge of these campaigns. The system is easily installed and configured in the cloud to monitor bot activity around a standing user-defined query. All you need is a Twitter developer app key to fetch data from the Twitter streaming API.</p> 

      <p class="text-left">BotSlayer uses an anomaly detection algorithm to flag hashtags, links, accounts, and media that are trending and amplified in a coordinated fashion by likely bots. A Web dashboard lets users explore the tweets and accounts associated with suspicious campaigns via Twitter, visualize their spread via Hoaxy, and search related images and content on Google.</p>

      <p class="text-left">BotSlayer is designed as a crowdsourcing platform: in exchange for the free service, the system provides anonymous data back to our lab for research, in a way that is compliant with Twitter’s terms and guidelines. The data will aid in the study and early detection of social media manipulation phenomena.</p>
    </div>
    <div class="footer">
      <a href="https://osome.iuni.iu.edu/" target="_blank ">OSoMe</a>
          | 
      <a href="http://iuni.iu.edu/" target="_blank ">IUNI</a>
          | 
      <a href="http://cnets.indiana.edu/" target="_blank ">CNetS</a>
      <p>© BotSlayer-CE</p>
    </div>
  </div>
</template>

<style>
  .footer
  {
      color: white;
      background-color: #147340;
  }
  .footer a
  {
      color: lightgray;
  }
  .footer a:hover
  {
      color: white;
  }
  .footer p
  {
      margin-bottom: 0px;
  }
</style>
