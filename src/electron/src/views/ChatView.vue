<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import { marked } from 'marked';
import { Meta, Message, useChatWebSocket } from '../utils/WebSocketHandler';

const route = useRoute();
const chatId = ref(route.params.chatId as string);
const input = ref('');

const { connect, send, messages: wsMessages, steps, onFinalResponse } = useChatWebSocket();

function formatMessage(message: string) {
  return marked.parse(message);
}

const metaDialog = ref<HTMLDialogElement | null>(null);
const currentMeta = ref<Meta | null>(null);
const bottomAnchor = ref<HTMLElement | null>(null);

function openMetaModal(meta: Meta) {
  currentMeta.value = meta;
  metaDialog.value?.showModal();
}

function closeMetaModal() {
  metaDialog.value?.close();
}

async function fetchChatHistory() {
  const res = await fetch(`http://localhost:8000/chats/${chatId.value}`);
  if (!res.ok) return;

  const data = await res.json();
  const fetchedMessages: Message[] = data.messages
    .filter((msg: Message) => msg.role !== 'system')
    .map((msg: any) => ({
      role: msg.role,
      content: msg.content,
      meta: msg.meta || msg.additional_kwargs?.meta
    }));

  wsMessages.value.push(...fetchedMessages);
}

onMounted(() => {
  connect();
  fetchChatHistory();
});

watch(
  () => route.params.chatId,
  (newChatId) => {
    chatId.value = newChatId as string;
    wsMessages.value = [];
    fetchChatHistory();
  }
);

watch(
  wsMessages,
  async () => {
    await nextTick();
    bottomAnchor.value?.scrollIntoView({ behavior: 'smooth' });
  },
  { deep: true }
);

watch(
  steps,
  async () => {
    await nextTick();
    bottomAnchor.value?.scrollIntoView({ behavior: 'smooth' });
  },
  { deep: true }
);

watch(steps, () => {
  console.log('Live steps:', steps.value);
});

function sendMessage() {
  if (!input.value.trim()) return;
  const userMessage = input.value;
  input.value = '';
  send(userMessage, chatId.value);
}

function cleanQuery(query: string): string {
  return query
    .split('\n')
    .map((line) => line.trimStart())
    .join('\n')
    .trim();
}

onFinalResponse.value = async () => {
  console.log('Message complete – refreshing sidebar...');
  await fetch(`http://localhost:8000/chats`)
    .then((res) => res.json())
    .then((data) => {
      window.dispatchEvent(new CustomEvent('refreshSidebar', { detail: data.chats }));
    });
};
</script>

<template>
  <div class="flex h-screen flex-col bg-base-100 p-4">
    <div class="scrollable flex-1 space-y-4 overflow-y-auto pr-1">
      <div v-for="(msg, index) in wsMessages" :key="index" class="w-full">
        <!-- User message -->
        <div v-if="msg.role === 'human'" class="chat chat-end mb-4">
          <div class="chat-bubble chat-bubble-primary max-w-[80%] px-4 py-2 text-base">
            <div v-html="formatMessage(msg.content)" class="prose prose-base text-black" />
          </div>
        </div>
        <!-- Loading steps appear directly after the last user message -->
        <div
          v-if="index === wsMessages.length - 1 && msg.role === 'human' && steps.length"
          class="mb-4 flex w-full justify-center px-4"
        >
          <div class="prose prose-sm mx-auto w-full max-w-4xl px-2 text-left text-gray-400">
            <p v-if="steps.length" class="flex items-center gap-2">
              <span class="loading loading-spinner loading-sm"></span>
              {{ steps[steps.length - 1].replaceAll('_', ' ') }}
            </p>
          </div>
        </div>
        <!-- AI message -->
        <div v-else-if="msg.role === 'ai'" class="mb-4 flex w-full justify-center px-4">
          <div
            class="prose prose-lg mx-auto w-full max-w-4xl rounded-lg border border-white/10 px-6 py-5 text-left text-base-content"
          >
            <div v-html="formatMessage(msg.content)" />
            <button
              v-if="msg.meta"
              class="btn btn-circle btn-ghost btn-xs float-right mt-2 text-info"
              @click="openMetaModal(msg.meta)"
              title="View details"
            >
              ℹ️
            </button>
          </div>
        </div>
      </div>

      <div ref="bottomAnchor"></div>
    </div>

    <form @submit.prevent="sendMessage" class="mt-4 flex items-center gap-2">
      <input
        v-model="input"
        class="input input-bordered w-full"
        placeholder="Type your message..."
      />
      <button class="btn btn-primary" type="submit">Send</button>
    </form>

    <!-- Info Modal -->
    <dialog ref="metaDialog" class="modal">
      <div class="modal-box w-[90vw] max-w-none">
        <div class="mb-4 flex items-start justify-between">
          <h3 class="text-lg font-bold">Details</h3>
          <button class="btn btn-circle btn-ghost btn-sm" @click="closeMetaModal" title="Close">
            ✕
          </button>
        </div>

        <div v-if="currentMeta" class="space-y-4">
          <div>
            <p class="font-semibold">Tables:</p>
            <p class="text-sm">{{ currentMeta.tables?.join(', ') }}</p>
          </div>
          <div>
            <p class="font-semibold">Activities:</p>
            <p class="text-sm">{{ currentMeta.activities?.join(', ') }}</p>
          </div>
          <div>
            <p class="font-semibold">Query:</p>
            <pre class="overflow-x-auto whitespace-pre-wrap rounded bg-base-200 p-2 text-sm"
              >{{ cleanQuery(currentMeta.query) }}
</pre
            >
          </div>
          <div>
            <p class="font-semibold">Result:</p>
            <div
              class="prose prose-sm max-w-none overflow-x-auto overflow-y-auto rounded bg-base-200 p-4 text-sm"
              style="max-height: 300px"
              v-html="formatMessage(currentMeta.result)"
            ></div>
          </div>
        </div>
      </div>
    </dialog>
  </div>
</template>

<style scoped lang="less">
.chat-bubble h1,
.chat-bubble h2,
.chat-bubble h3 {
  font-weight: bold;
  margin: 1rem 0 0.5rem;
  font-size: 1.125rem;
}

.chat-bubble p {
  margin-bottom: 0.5rem;
  line-height: 1.5;
}

.chat-bubble ul {
  padding-left: 1.2rem;
  list-style: disc;
  margin-bottom: 0.5rem;
}
</style>
