<template>
    <div class="hello">
        <input type="text" v-on:input="changeText" placeholder="Type something">
        <p>{{ title }}</p>
        <iframe v-bind:src="apiUrl + '/api/map'" style="height: 700px; width: 1150px"></iframe>
    </div>
</template>

<script>
    export default {
        name: 'CoronaMap',
        props: {
            apiUrl: String
        },
        methods: {
            changeText: function (event) {
                this.title = event.target.value;
            }
        },
        data: function () {
            return {
                title: "Hello Wolrd!"
            }
        }
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    h3 {
        margin: 40px 0 0;
    }
    ul {
        list-style-type: none;
        padding: 0;
    }
    li {
        display: inline-block;
        margin: 0 10px;
    }
    a {
        color: #42b983;
    }
</style>
