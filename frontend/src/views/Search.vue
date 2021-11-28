<template>
  <v-card>
    <v-container fluid>
      <v-row
        align="center"
      >
        <v-col cols="12">
          <v-autocomplete
            v-model="value"
            :items="items"
            dense
            filled
            label="Search"
          ></v-autocomplete>
        </v-col>
        <v-col cols="12" v-if="value !== null">
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
                  <v-btn primary>
                    Search
                  </v-btn>
                </div>
            </v-layout>
        </v-col>
      </v-row>
    </v-container>
  </v-card>
</template>

<script>
import axios from "axios";
export default {
  name: "App",
  data: () => ({
    items: ['[Player]\'s match against [Team]', 'bar'],
    values: ['[Player]\'s match against [Team]', 'bar'],
    value: null,
    sentence: '[Player]\'s match against [Team]'
  }),

  async beforeMount() {
    const { data } = await axios.post(
      "https://jsonplaceholder.typicode.com/posts",
      {
        title: "foo",
        body: "bar",
        userId: 1
      }
    );
    console.log(data);
  },

  methods: {
    reset () {
      const re = /(\[[^\]]*\])/
      // The filter removes empty strings
      const parts = this.value.split(re).filter(text => text)

      this.sentenceParts = parts.map(segment => {
        const isInput = re.test(segment)
        return {
          guess: '',
          input: isInput,
          text: isInput ? segment.slice(1, -1) : segment,
          value: segment
        }
      })
    }
  },

  watch: {
    value: {
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
</style>
