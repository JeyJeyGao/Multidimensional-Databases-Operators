<template>
    <div>
        <span>{{ title }}</span>
        <bar-chart :data="data" style="height: 150px;"></bar-chart>
    </div>
</template>

<script>
    export default {
        name: "demographics",
        props: {
            title: String,
            data: Array
        }
    }
</script>

<style scoped>

</style>