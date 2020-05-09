<template>
    <div class="row justify-content-center">
        <div class="card worldlist text-xl-left" style="max-height: 670px;">
            <ul class="list-group list-group-flush overflow-auto">
                <div class="row h6">
                    <span class="col">Country</span>
                    <span class="col">confirmed</span>
                    <span class="col">death</span>
                </div>
                <li
                    class="list-group-item"
                    :key="c[0]"
                    :title="c[0]"
                    v-for="c in sortCountries(countryCases, 'confirmed')"
                    :class="c[0] === currentCountry? 'bg-secondary text-light': ''"
                >
                    <div class="row" @click="changeCountryMap">
                        <span class="col">{{c[0]}}</span>
                        <span class="col">{{c[1].confirmed}}</span>
                        <span class="col">{{c[1].death}}</span>
                    </div>
                    <div class="row text-dark" v-if="c[0] === currentCountry">
                        <ul class="col">
                            <li
                                class="list-group-item"
                                :key="s[0]"
                                :title="s[0]"
                                v-for="s in sortData(stateCases, 'confirmed')"
                                :class="s[0] === currentState? 'bg-secondary text-light': ''"
                            >
                                <div class="row" @click="changeStateMap">
                                    <div class="col">{{s[0]}}</div>
                                    <div class="col">{{s[1].confirmed}}</div>
                                    <div class="col">{{s[1].death}}</div>
                                </div>
                            </li>
                        </ul>
                    </div>
                </li>
            </ul>
        </div>
        <iframe class="map justify-content-center rounded border-left-0 border-light" :src="mapSrc"></iframe>
    </div>
</template>

<script>
import axios from "axios";
export default {
    name: "CoronaMap",
    methods: {
        onload() {
            // set date range, show most current map
            axios
                .get("/api/daterange")
                .then(response => {
                    let data = response.data;
                    this.maxDate = data.max;
                    this.minDate = data.min;
                    this.mapSrc = `api/map/${this.maxDate}/countries`;

                    // get world list
                    axios
                        .get(`/api/${this.maxDate}/countries`)
                        .then(response => {
                            console.log(response.data);
                            this.countryCases = response.data;
                        })
                        .catch(error => console.log(error));
                })
                .catch(error => console.log(error));
        },

        sortCountries(countriesJson, compareValue) {
            let countriesArray = [];
            for (let c in countriesJson) {
                countriesArray.push([c, countriesJson[c]]);
            }
            return countriesArray.sort(
                (a, b) => b[1][compareValue] - a[1][compareValue]
            );
        },
        sortData(dataJson, compareValue) {
            let dataArray = [];
            for (let c in dataJson) {
                if (c === "null") {
                    dataArray.push(["Unknow", dataJson[c]]);
                } else {
                    dataArray.push([c, dataJson[c]]);
                }
            }
            return dataArray.sort(
                (a, b) => b[1][compareValue] - a[1][compareValue]
            );
        },
        changeStateMap(event){
            let element = event.target;
            while (!element.title) {
                element = element.parentElement;
            }
            if (element.title !== this.currentState){
                this.currentState = element.title;
                this.mapSrc = `/api/map/${this.maxDate}/${this.currentCountry}/${this.currentState}`
            }else{
                this.currentState = ""
                this.mapSrc = `/api/map/${this.maxDate}/${this.currentCountry}`;
            }
        },
        changeCountryMap(event) {
            let element = event.target;
            while (!element.title) {
                element = element.parentElement;
            }
            if (element.title !== this.currentCountry) {
                this.currentCountry = element.title;
                this.mapSrc = `/api/map/${this.maxDate}/${this.currentCountry}`;
                this.getStates(this.currentCountry);
            } else {
                this.currentCountry = "";
                this.mapSrc = `/api/map/${this.maxDate}/countries`;
            }
        },
        getStates(country) {
            this.stateCases = {};
            axios
                .get(`/api/${this.maxDate}/${country}`)
                .then(response => {
                    console.log(response.data);
                    this.stateCases = response.data;
                })
                .catch(error => console.log(error));
        }
    },
    data() {
        return {
            mapSrc: "",
            maxDate: "",
            minDate: "",
            countryCases: {},
            stateCases: {},
            currentCountry: "",
            currentState: "",
        };
    },
    mounted() {
        this.onload();
    }
};
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
