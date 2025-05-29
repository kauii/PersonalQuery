import { ref } from 'vue';

export interface Meta {
  tables?: string[];
  activities?: string[];
  query?: string;
  result?: string;
}

export type Role = 'system' | 'ai' | 'human';

export interface Message {
  role: Role;
  content: string;
  meta?: Meta;
}

export function useChatWebSocket() {
  const socket = ref<WebSocket | null>(null);
  const messages = ref<Message[]>([]);
  const steps = ref<string[]>([]);
  const isConnected = ref(false);
  const onFinalResponse = ref<(() => void) | null>(null);

  const connect = () => {
    socket.value = new WebSocket('ws://localhost:8000/ws');

    socket.value.onopen = () => {
      isConnected.value = true;
    };

    socket.value.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'step') {
        steps.value = [data.node];
      } else if (data.role === 'ai') {
        messages.value.push({
          role: data.role,
          content: data.content,
          meta: data.additional_kwargs.meta
        });
        if (onFinalResponse.value) {
          onFinalResponse.value();
        }
        steps.value = [];
      }
    };

    socket.value.onclose = () => {
      isConnected.value = false;
    };
  };

  const send = (question: string, chatId: string) => {
    steps.value = [];
    messages.value.push({ role: 'human', content: question });
    socket.value?.send(JSON.stringify({ question, chat_id: chatId }));
  };
  return { connect, send, messages, steps, isConnected, onFinalResponse };
}
