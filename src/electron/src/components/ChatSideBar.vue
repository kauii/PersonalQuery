<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const chats = ref<string[]>([]);
const router = useRouter();

async function fetchChats() {
  const res = await fetch('http://localhost:8000/chats');
  const data = await res.json();
  chats.value = data.chats;
}

async function createNewChat() {
  const res = await fetch('http://localhost:8000/chats', {
    method: 'POST'
  });
  const data = await res.json();
  router.push(`/chat/${data.chat_id}`);
}

onMounted(fetchChats);
</script>

<template>
  <div class="flex h-screen w-64 flex-col gap-2 bg-base-200 p-4">
    <button class="btn btn-primary mb-2 w-full" @click="createNewChat">+ New Chat</button>

    <div v-for="chat in chats" :key="chat">
      <router-link :to="`/chat/${chat}`" class="btn btn-sm block w-full truncate text-left">
        {{ chat }}
      </router-link>
    </div>
  </div>
</template>

<style scoped lang="less"></style>
