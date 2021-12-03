<template >
  <v-card>
    <v-container fluid>
      <v-row
        align="center"
      >
        <v-col cols="12" >
          <v-autocomplete
            v-model="item"
            :items="items"
            item-text="name"
            item-value="value"
            return-object
            dense
            filled
            label="Search"
          ></v-autocomplete>
        </v-col>
        <v-col cols="12" v-if="item !== null">
            <v-layout row align-center justify-center>
                <span v-for="(part, index) in sentenceParts" :key="index">
                  <label>
                    <v-text-field
                      class="pt-6 centered-input"
                      v-if="part.input"
                      v-model="part.guess"
                      :aria-colindex="index"
                      v-bind:label="part.value"
                      solo outlined clearable
                    ></v-text-field>
                    <span v-else>&nbsp;&nbsp;{{ part.text }}&nbsp;&nbsp;</span>
                  </label>
                </span>
                <span>&nbsp;&nbsp;</span>
                <div class="text-xs-center">
                  <v-btn primary @click="search">
                    Search
                  </v-btn>
                </div>
            </v-layout>
        </v-col>
        <v-col cols="12"  v-if="fields !== null">
          <div id="app">
            <vuetable ref="vuetable"
              :fields="fields"
              :api-url="api_url"
              :css="css.table"
              :sort-order="fields"
            ></vuetable>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </v-card>
</template>

<script>
import Vuetable from 'vuetable-2'
import CssForBootstrap4 from '@/assets/VuetableCssBootstrap4.js'
import axios from "axios";

export default {
  name: "App",

  components: {
    Vuetable,
  },

  data: () => ({
    items: [
      {name: 'Information of [Player]', value: 'player'},
      {name: 'Information of [Team]', value: 'team'},
      {name: 'List of teams in [Season]', value: 'season'},
      {name: '[Player]\'s birthplace', value: 'birthplace'},
      {name: 'Play style of [Player]', value: 'style'},
      {name: '[Player]\'s match records against each team', value: 'record'},
      {name: 'Players who has [Skill] strength in [Team]', value: 'skill'},
      {name: 'Best players in [Team1] against [Team2]', value: 'best'},
    ],
    item: null,
    api_url: null,
    fields: null,
    css: CssForBootstrap4,
  }),

  methods: {
    reset () {
      const re = /(\[[^\]]*\])/
      // The filter removes empty strings
      const parts = this.item.name.split(re).filter(text => text)

      this.sentenceParts = parts.map(segment => {
        const isInput = re.test(segment)
        return {
          guess: '',
          input: isInput,
          text: isInput ? segment.slice(1, -1) : segment,
          value: segment
        }
      })
    },
    async search () {
      let url = "http://localhost:5000/api/v0/" + this.item.value + "?"
      this.sentenceParts.map(part => {
        if (part.input) {
          url += part.value.slice(1,-1).toLowerCase()
          url += "="
          url += part.guess.replace(" ", '%20')
          url += "&"
        }
      })

      const fetchedResult = [];
      await axios.get(url).then(
          response => {
            for (let key in response.data.data['0']) {
              fetchedResult.push(key)
            }
            this.fields = fetchedResult
            this.api_url = url
          }
      );
    }
  },

  watch: {
    item: {
      immediate: true,
      handler: 'reset'
    }
  }
};
</script>

<style scoped>
    .centered-input >>> input {
      text-align: center;
      align-content: center;
    }
    #app {
      font-family: "Avenir", Helvetica, Arial, sans-serif;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      color: #2c3e50;
      margin-top: 20px;
    }
    button.ui.button {
      padding: 8px 3px 8px 10px;
      margin-top: 1px;
      margin-bottom: 1px;
    }
</style>

