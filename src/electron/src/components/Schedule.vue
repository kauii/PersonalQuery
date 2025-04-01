<script setup lang="ts">
import { ref, PropType } from 'vue';
import StudyInfoDto from '../../shared/dto/StudyInfoDto';
import { DataExportType } from '../../shared/DataExportType.enum';

const props = defineProps({
  studyInfo: {
    type: Object as PropType<StudyInfoDto>,
    default: null,
    required: false
  }
});

const startHour = ref<number>(props.studyInfo.scheduleStartHour);
const endHour = ref<number>(props.studyInfo.scheduleEndHour);

const emits = defineEmits(['startHourChanged', 'endHourChanged']);

const emitStartHourChanged = async () => {
  emits('startHourChanged', startHour.value);
};

const emitEndHourChanged = async () => {
  emits('endHourChanged', endHour.value);
};

</script>
<template>
  <div class="my-5 border border-slate-400 p-2">
    <div class="prose">
      <h2>When do you want to receive experience sampling notifications?</h2>
    </div>
    <div class="mt-4 flex w-1/3 flex-col">
      <div class="form-control">
        <label class="label flex cursor-pointer items-center justify-start">
          <span class="label-text ml-2">Start-Hour</span>
          <input
            v-model="startHour"
            type="text"
            @change="emitStartHourChanged"
          />
        </label>
        <label class="label flex cursor-pointer items-center justify-start">
          <span class="label-text ml-2">End-Hour</span>
          <input
            v-model="endHour"
            type="text"
            @change="emitEndHourChanged"
          />
        </label>
      </div>
    </div>
  </div>
</template>
<style lang="less">
@import '../styles/index';
</style>
