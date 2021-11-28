<template>
<nav>
  <v-toolbar elevation="8">
    <v-toolbar-title class="text-uppercase grey--text" style="cursor: pointer"  @click="$router.push('/')">
        <span class="font-weight-light">DSCI558</span>
        <span> - EPL Knowledge Graph </span>
    </v-toolbar-title>
    <v-divider
      class="mx-4"
      vertical
    ></v-divider>
    <v-spacer></v-spacer>

    <v-toolbar-items class="hidden-sm-and-down">
      <v-btn text to="/search">
        Search
      </v-btn>
      <v-divider vertical></v-divider>

      <v-btn text to="/predict">
        TKG Predict
      </v-btn>
      <v-divider vertical></v-divider>

    </v-toolbar-items>
  </v-toolbar>
</nav>
</template>

<script>
export default {

}
</script>
