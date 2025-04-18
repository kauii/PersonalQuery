<script setup lang="ts">
import { ref } from 'vue';

const input = ref('');
const messages = ref<{ role: 'user' | 'assistant'; content: string }[]>([]);

function sendMessage() {
  if (!input.value.trim()) return;

  messages.value.push({ role: 'user', content: input.value });

  // Stubbed response — replace with Python call later
  setTimeout(() => {
    messages.value.push({
      role: 'assistant',
      content: `You said: "${input.value}"`
    });
  }, 300);

  input.value = '';
}
</script>

<template>
  <div class="flex h-screen flex-col bg-base-100 p-4">
    <div class="flex-1 space-y-4 overflow-y-auto pr-1">
      <div
        v-for="(msg, index) in messages"
        :key="index"
        :class="msg.role === 'user' ? 'chat chat-end' : 'chat chat-start'"
      >
        <div :class="msg.role === 'user' ? 'chat-bubble chat-bubble-primary' : 'chat-bubble'">
          {{ msg.content }}
        </div>
      </div>
    </div>

    <form @submit.prevent="sendMessage" class="mt-4 flex items-center gap-2">
      <input
        v-model="input"
        class="input input-bordered w-full"
        placeholder="Type your message..."
      />
      <button class="btn btn-primary" type="submit">Send</button>
    </form>
  </div>
</template>

<style scoped lang="less"></style>
