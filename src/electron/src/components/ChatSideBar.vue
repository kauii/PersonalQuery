<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

interface ChatEntry {
  id: string;
  title: string;
  last_activity: string | null;
}

const chats = ref<ChatEntry[]>([]);
const router = useRouter();

async function fetchChats() {
  const res = await fetch('http://localhost:8000/chats');
  const data = await res.json();
  chats.value = data.chats.sort((a: ChatEntry, b: ChatEntry) => {
    if (!a.last_activity) return 1;
    if (!b.last_activity) return -1;
    return new Date(b.last_activity).getTime() - new Date(a.last_activity).getTime();
  });
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

    <div v-for="chat in chats" :key="chat.id">
      <router-link :to="`/chat/${chat.id}`" class="btn btn-sm block w-full truncate text-left">
        {{ chat.title }}
      </router-link>
    </div>
  </div>
</template>


<style scoped lang="less"></style>
