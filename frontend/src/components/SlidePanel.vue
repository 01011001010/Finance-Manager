<script setup>
const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
  tabLabel: {
    type: String,
    default: "TAB",
  },
  tabPosition: {
    type: String,
    default: "100px",
  },
});

const emit = defineEmits(["update:modelValue", "open", "opened"]);

const handleToggle = () => {
  const newState = !props.modelValue;
  if (newState === true) {
    emit("open");
  }
  emit("update:modelValue", newState);
  emit("opened");
};
</script>

<template>
  <div class="panel-container" :style="{ zIndex: modelValue ? 1001 : 1000 }">
    <div class="slide-group" :class="{ open: modelValue }">
      <div
        class="slide-tab"
        :style="{ marginTop: tabPosition }"
        @click="handleToggle"
      >
        {{ modelValue ? "✕" : tabLabel }}
      </div>

      <div class="slide-panel">
        <slot />
      </div>
    </div>
  </div>
</template>

<style scoped>
.panel-container {
  position: fixed;
  right: 0;
  top: 0;
  height: 100vh;
  z-index: 1000;
  pointer-events: none;
  --panel-width: 300px;
}

.slide-group {
  display: flex;
  height: 100%;
  align-items: flex-start;
  transform: translateX(var(--panel-width));
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-group.open {
  transform: translateX(0);
}

.slide-tab {
  pointer-events: auto;
  background: rgba(34, 34, 34, 0.95);
  backdrop-filter: blur(4px);
  color: #fff;
  width: 30px;
  height: 100px;
  padding: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  writing-mode: vertical-rl;
  border-radius: 12px 0 0 12px;
  box-shadow: -2px 0 10px rgba(0, 0, 0, 0.2);
}

.slide-panel {
  pointer-events: auto;
  width: var(--panel-width);
  height: 100%;
  background: rgba(34, 34, 34, 0.95);
  backdrop-filter: blur(8px);
  color: white;
  padding: 20px;
  box-shadow: -5px 0 15px rgba(0, 0, 0, 0.3);
  box-sizing: border-box;
}
</style>
