<template>
  <div id="app">
    <img alt="Vue logo" src="./assets/logo.png">
    <CoronaMap v-bind:api-url="apiUrl"></CoronaMap>
    <HelloWorld msg="Welcome to Your Vue.js App"/>
  </div>
</template>

<script>
import HelloWorld from './components/HelloWorld.vue'
import CoronaMap from './components/CoronaMap.vue'

export default {
  name: 'App',
  components: {
    HelloWorld,
    CoronaMap
  },
  data: function () {
    return {
      // apiUrl: "http://localhost:5000"
      apiUrl: ""
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
