<template>
        <div class="row justify-content-center">
            <div class="card worldlist text-xl-left" style="max-height: 670px;">
                <ul class="list-group list-group-flush overflow-auto">
                    <li class="list-group-item"
                        :key="c[0]"
                        @click="changeCountryMap"
                        :title="c[0]"
                        v-for="c in sortCountries(countryCases, 'confirmed')"
                        :class="c[0] === currentCountry? 'bg-secondary text-light': ''">
                        <div class="row">
                            <span class="col">{{c[0]}}</span><span class="col">{{c[1].confirmed}}</span>
                        </div>
                    </li>
                </ul>
            </div>
            <iframe class="map justify-content-center rounded border-left-0 border-light" :src="mapSrc"></iframe>
        </div>
</template>

<script>
    import axios from 'axios';
    export default {
        name: 'CoronaMap',
        methods: {
            onload() {
                // set date range, show most current map
                axios.get('/api/daterange').then(
                    response => {
                        let data = response.data;
                        this.maxDate = data.max;
                        this.minDate = data.min;
                        this.mapSrc = `api/map/${this.maxDate}/countries`;

                        // get world list
                        axios.get(`/api/${this.maxDate}/countries`).then(
                            response => {
                                console.log(response.data);
                                this.countryCases = response.data;
                            }
                        ).catch(
                            error => console.log(error)
                        );
                    }
                ).catch(
                    error => console.log(error)
                );
            },

            sortCountries(countriesJson, compareValue) {
                let countriesArray = [];
                for (let c in countriesJson) {
                    countriesArray.push([c, countriesJson[c]]);
                }
                return countriesArray.sort((a, b) => b[1][compareValue] - a[1][compareValue]);
            },

            changeCountryMap(event) {
                let element = event.target;
                while (!element.title) {
                    element = element.parentElement;
                }
                if (element.title !== this.currentCountry) {
                    this.currentCountry = element.title;
                    this.mapSrc = `/api/map/${this.maxDate}/${this.currentCountry}`;
                }
                else {
                    this.currentCountry = '';
                    this.mapSrc = this.mapSrc = `/api/map/${this.maxDate}/countries`;
                }
            }
        },
        data() {
            return {
                mapSrc: "",
                maxDate: "",
                minDate: "",
                countryCases: {},
                currentCountry: ""
            }
        },
        mounted() {
            this.onload();
        }
    }
</script>

<style scoped>
    .map {
        width: 1115px;
        height: 670px;
    }

    .worldlist {
        width: 18rem;
    }

    li {
        cursor: pointer;
    }
</style>
