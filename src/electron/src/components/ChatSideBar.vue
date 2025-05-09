<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';

interface ChatEntry {
  id: string;
  title: string;
  last_activity: string | null;
}

const chats = ref<ChatEntry[]>([]);
const openMenuId = ref<string | null>(null);
const router = useRouter();

function toggleMenu(chatId: string) {
  openMenuId.value = openMenuId.value === chatId ? null : chatId;
}

function closeMenu() {
  openMenuId.value = null;
}

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

async function deleteChat(chatId: string) {
  closeMenu();
  if (!confirm('Are you sure you want to delete this chat?')) return;
  await fetch(`http://localhost:8000/chats/${chatId}`, { method: 'DELETE' });
  await fetchChats();
  if (chatId === router.currentRoute.value.params.chatId) {
    router.push('/');
  }
}

async function renameChat(chatId: string) {
  closeMenu();
  const newTitle = prompt('Enter new title for the chat:');
  if (!newTitle?.trim()) return;
  await fetch(`http://localhost:8000/chats/${chatId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: newTitle.trim() })
  });
  await fetchChats();
}

// Global click listener to close dropdown
function handleClickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement;
  const dropdowns = document.querySelectorAll('.chat-dropdown');

  let clickedInsideDropdown = false;
  dropdowns.forEach(dropdown => {
    if (dropdown.contains(target)) {
      clickedInsideDropdown = true;
    }
  });

  if (!clickedInsideDropdown) {
    closeMenu();
  }
}

onMounted(() => {
  fetchChats();
  document.addEventListener('click', handleClickOutside);
});

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside);
});

</script>

<template>
  <div class="flex h-screen w-64 flex-col gap-2 bg-base-200 p-4">
    <button class="btn btn-primary mb-2 w-full" @click="createNewChat">+ New Chat</button>

    <div class="flex-1 overflow-y-auto space-y-2">
      <div
        v-for="chat in chats"
        :key="chat.id"
        class="relative group flex items-center"
      >
        <!-- Chat title button -->
        <router-link
          :to="`/chat/${chat.id}`"
          class="btn btn-sm flex-1 justify-start truncate"
          :class="{
            'btn-primary': chat.id === $route.params.chatId,
            'btn-ghost': chat.id !== $route.params.chatId
          }"
        >
          {{ chat.title }}
        </router-link>

        <!-- Kebab icon and dropdown menu -->
        <div
          class="relative ml-1 transition-opacity"
          :class="{
            'opacity-0 group-hover:opacity-100': openMenuId !== chat.id,
            'opacity-100': openMenuId === chat.id
          }"
        >
          <!-- Kebab button -->
          <button
            class="btn btn-xs btn-ghost"
            @click.stop="toggleMenu(chat.id)"
            title="Chat options"
          >
            ⋮
          </button>

          <!-- Dropdown -->
          <div
            v-if="openMenuId === chat.id"
            class="chat-dropdown absolute right-0 mt-1 w-28 rounded border border-base-300 bg-base-100 shadow z-10"
            @click.stop
          >
            <button
              class="block w-full px-3 py-2 text-left hover:bg-base-200"
              @click="renameChat(chat.id)"
            >
              Rename
            </button>
            <button
              class="block w-full px-3 py-2 text-left hover:bg-base-200 text-error"
              @click="deleteChat(chat.id)"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>






<style scoped lang="less"></style>
