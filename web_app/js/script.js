new Vue({
    el: "#app",
    data: {
        title: "Hello world"
    },
    methods: {
        changeText: function(event) {
            this.title = event.target.value;
        }
    }
})