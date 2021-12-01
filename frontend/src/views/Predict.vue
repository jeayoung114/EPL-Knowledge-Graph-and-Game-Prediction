<template>
  <div class="predict">
    <timeline ref="timeline" :items="items" :groups="groups" :options="options"> </timeline>
  </div>
</template>

<script>
import { Timeline } from 'vue-visjs'
import items from '../../tkg/items.json'
import groups from '../../tkg/groups.json'

export default {
  name: "App",

  components: {
    Timeline,
  },

  data() {
    return {
      groups: groups,
      items: items,
      // options: {
      //   editable: true
      // }
    }
  }
}
</script>
