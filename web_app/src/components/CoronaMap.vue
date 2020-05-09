<template>
    <div class="row justify-content-center">
        <div class="card worldlist text-xl-left pl-2" style="max-height: 670px;">
            <div class="row h6">
                <span class="col">Country</span>
                <span class="col">confirmed</span>
                <span class="col">death</span>
            </div>
            <ul class="list-group list-group-flush overflow-auto">
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
        <div class="card worldlist text-xl-left pl-2" style="max-height: 670px;">
            <div class="row dem" style="height:230px;">
                <demographics class="col h-40" title="Age of Coronavirus Deaths (%)" :data="age"></demographics>
            </div>
            <div class="row dem" style="height:220px;">
                <demographics class="col" title="Sex Ratio (%)" :data="sex"></demographics>
            </div>
            <ul class="list-group list-group-flush overflow-auto" style="max-height:220px;">
                <li
                    class="list-group-item"
                    :key="date"
                    :title="date"
                    v-for="date in dateList"
                    :class="date === currentDate? 'bg-secondary text-light': ''"
                >
                    <div class="row">
                        <span class="col" @click="changeDate">{{date}}</span>
                    </div>
                </li>
            </ul>
        </div>
    </div>
</template>

<script>
import axios from "axios";
import demographics from "./demographics.vue";
// import dateQuickSlider from "vue-date-quick-slider";
export default {
    // components: {
    //     dateQuickSlider
    // },
    name: "CoronaMap",
    methods: {
        onload() {
            // set date range, show most current map
            axios
                .get("/api/daterange")
                .then(response => {
                    let data = response.data;
                    if (this.currentDate === "") {
                        this.currentDate = data.max;
                    }
                    this.maxDate = data.max;
                    this.minDate = data.min;
                    this.mapSrc = `api/map/${this.currentDate}/countries`;
                    // get world list
                    axios
                        .get(`/api/${this.currentDate}/countries`)
                        .then(response => {
                            this.countryCases = response.data;
                        })
                        .catch(error => console.log(error));
                    this.getDateList();
                })
                .catch(error => console.log(error));
            this.getSexAge();
        },
        dateToString(date) {
            const dtf = new Intl.DateTimeFormat("en-US", {
                year: "numeric",
                month: "2-digit",
                day: "2-digit"
            });
            const [
                { value: mo },
                ,
                { value: da },
                ,
                { value: ye }
            ] = dtf.formatToParts(date);
            return `${ye}-${mo}-${da}`;
        },
        getDateList() {
            let date = new Date(this.maxDate);
            date.setDate(date.getDate() + 1);
            let minDate = new Date(this.minDate);
            // minDate.setDate(minDate.getDate()-1);
            let minDateStr = this.dateToString(minDate);
            while (this.dateToString(date) != minDateStr) {
                this.dateList.push(this.dateToString(date));
                console.log(this.dateToString(date));
                date.setDate(date.getDate() - 1);
            }
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
        changeStateMap(event) {
            let element = event.target;
            while (!element.title) {
                element = element.parentElement;
            }
            if (element.title === "Unknow") {
                return;
            }
            if (element.title !== this.currentState) {
                this.currentState = element.title;
                this.mapSrc = `/api/map/${this.currentDate}/${this.currentCountry}/${this.currentState}`;
            } else {
                this.currentState = "";
                this.mapSrc = `/api/map/${this.currentDate}/${this.currentCountry}`;
            }
        },
        changeDate(event) {
            let element = event.target;
            while (!element.title) {
                element = element.parentElement;
            }
            if (element.title !== this.currentDate) {
                this.currentDate = element.title;
                this.onload();
            }
        },
        changeCountryMap(event) {
            let element = event.target;
            while (!element.title) {
                element = element.parentElement;
            }
            if (element.title !== this.currentCountry) {
                this.currentCountry = element.title;
                this.mapSrc = `/api/map/${this.currentDate}/${this.currentCountry}`;
                this.getStates(this.currentCountry);
            } else {
                this.currentCountry = "";
                this.mapSrc = `/api/map/${this.currentDate}/countries`;
            }
        },
        getStates(country) {
            this.stateCases = {};
            axios
                .get(`/api/${this.currentDate}/${country}`)
                .then(response => {
                    this.stateCases = response.data;
                })
                .catch(error => console.log(error));
        },
        getSexAge() {
            axios
                .get("/api/age")
                .then(response => {
                    this.age = [];
                    let data = response.data.data;
                    for (let i in data) {
                        for (let k in data[i]) {
                            this.age.unshift([k, data[i][k]]);
                        }
                    }
                })
                .catch(error => console.log(error));
            axios
                .get("/api/sex")
                .then(response => {
                    this.sex = [];
                    let data = response.data.data;
                    for (let i in data) {
                        for (let k in data[i]) {
                            this.sex.push([k, data[i][k]]);
                        }
                    }
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
            age: [],
            sex: [],
            currentDate: "",
            dateList: []
        };
    },
    mounted() {
        this.onload();
    },
    components: {
        demographics
    }
};
</script>

<style scoped>
.map {
    width: 800px;
    height: 670px;
}

.worldlist {
    width: 18rem;
}

li {
    cursor: pointer;
}

.dem {
    width: 300px;
}
</style>
