<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { marked } from 'marked';

const route = useRoute();
const chatId = ref(route.params.chatId as string);

const input = ref('');
const messages = ref<
  {
    role: 'user' | 'assistant';
    content: string;
    meta?: {
      tables?: string[];
      activities?: string[];
      query?: string;
      result?: string;
    };
  }[]
>([]);

function formatMessage(message: string) {
  return marked.parse(message);
}

const metaDialog = ref<HTMLDialogElement | null>(null);
const currentMeta = ref<any>(null);

function openMetaModal(meta: any) {
  currentMeta.value = meta;
  metaDialog.value?.showModal();
}

function closeMetaModal() {
  metaDialog.value?.close();
}

async function fetchChatHistory() {
  const res = await fetch(`http://localhost:8000/chats/${chatId.value}`);
  if (res.ok) {
    const data = await res.json();
    messages.value = data.messages.map((msg: any) => ({
      role: msg.type === 'human' ? 'user' : 'assistant',
      content: msg.content,
      meta: msg.meta || msg.additional_kwargs?.meta
    }));
  }
}

onMounted(fetchChatHistory);

watch(
  () => route.params.chatId,
  (newChatId) => {
    chatId.value = newChatId as string;
    fetchChatHistory();
  }
);

async function sendMessage() {
  if (!input.value.trim()) return;

  const userMessage = input.value;
  messages.value.push({ role: 'user', content: userMessage });
  input.value = '';

  try {
    const response = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        question: userMessage,
        chat_id: chatId.value
      })
    });

    const data = await response.json();
    messages.value.push({
      role: 'assistant',
      content: data.answer,
      meta: {
        tables: data.tables,
        activities: data.activities,
        query: data.query,
        result: data.result
      }
    });
  } catch (err) {
    console.error('Backend error:', err);
    messages.value.push({
      role: 'assistant',
      content: '[Error contacting backend]'
    });
  }
}

function cleanQuery(query: string): string {
  return query
    .split('\n')
    .map(line => line.trimStart())
    .join('\n')
    .trim();
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
          <div class="flex items-start justify-between gap-2">
            <!-- Message content -->
            <div
              v-html="formatMessage(msg.content)"
              :class="[
                'prose prose-sm max-w-none flex-1',
                msg.role === 'user' ? 'text-black' : ''
              ]"
            />

            <!-- Info button only for assistant with meta -->
            <button
              v-if="msg.role === 'assistant' && msg.meta"
              class="btn btn-circle btn-ghost btn-xs text-info"
              @click="openMetaModal(msg.meta)"
              title="View details"
            >
              ℹ️
            </button>
          </div>
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
            <pre class="whitespace-pre-wrap overflow-x-auto bg-base-200 p-2 rounded text-sm">
{{ cleanQuery(currentMeta.query) }}
</pre>

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
