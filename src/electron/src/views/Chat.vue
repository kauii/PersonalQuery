<script setup lang="ts">
import ChatSidebar from '../components/ChatSideBar.vue';
</script>

<template>
  <div class="flex h-screen">
    <ChatSidebar />
    <router-view class="flex-1" />
  </div>
</template>
<style scoped lang="less"></style>
