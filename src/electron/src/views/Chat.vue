<script setup lang="ts">
import { ref } from 'vue';
import { marked } from 'marked';

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

async function sendMessageToBackend(message: string): Promise<string> {
  try {
    const response = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ question: message })
    });

    if (!response.ok) throw new Error('Backend error');

    const data = await response.json();
    return data.answer || '[No answer]';
  } catch (err) {
    console.error('Error contacting backend:', err);
    return '[Error contacting backend]';
  }
}

async function sendMessage() {
  if (!input.value.trim()) return;

  const userMessage = input.value;
  messages.value.push({ role: 'user', content: userMessage });
  input.value = '';

  const assistantReply = await sendMessageToBackend(userMessage);
  messages.value.push({ role: 'assistant', content: assistantReply });
}

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
            <div v-html="formatMessage(msg.content)" class="flex-1"></div>

            <!-- Info button only if assistant and has meta -->
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
    <dialog ref="metaDialog" class="modal modal-bottom sm:modal-middle">
      <div class="modal-box max-w-2xl">
        <h3 class="mb-2 text-lg font-bold">Details</h3>
        <div v-if="currentMeta">
          <p><strong>Query:</strong> {{ currentMeta.query }}</p>
          <p><strong>Tables:</strong> {{ currentMeta.tables?.join(', ') }}</p>
          <p><strong>Activities:</strong> {{ currentMeta.activities?.join(', ') }}</p>
          <p><strong>Result:</strong></p>
          <pre class="whitespace-pre-wrap rounded bg-base-200 p-2 text-sm"
            >{{ currentMeta.result }}
          </pre>
        </div>
        <div class="modal-action">
          <form method="dialog">
            <button class="btn" @click="closeMetaModal">Close</button>
          </form>
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
