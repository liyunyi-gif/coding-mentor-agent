<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { EditorView, keymap, lineNumbers, highlightActiveLine } from '@codemirror/view'
import { EditorState } from '@codemirror/state'
import { python } from '@codemirror/lang-python'
import { oneDark } from '@codemirror/theme-one-dark'
import { defaultKeymap } from '@codemirror/commands'

const props = defineProps<{ modelValue?: string }>()
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

const editorRef = ref<HTMLDivElement>()
let view: EditorView | null = null

onMounted(() => {
  if (!editorRef.value) return

  const updateListener = EditorView.updateListener.of((update) => {
    if (update.docChanged) {
      emit('update:modelValue', update.state.doc.toString())
    }
  })

  view = new EditorView({
    doc: props.modelValue || '',
    extensions: [
      lineNumbers(),
      highlightActiveLine(),
      keymap.of(defaultKeymap),
      python(),
      oneDark,
      updateListener,
      EditorState.tabSize.of(4),
      EditorView.theme({
        '&': { height: '120px' },
        '.cm-scroller': { overflow: 'auto' },
      }),
    ],
    parent: editorRef.value,
  })
})

onUnmounted(() => {
  view?.destroy()
})

watch(
  () => props.modelValue,
  (val) => {
    if (val !== undefined && view && val !== view.state.doc.toString()) {
      view.dispatch({
        changes: { from: 0, to: view.state.doc.length, insert: val || '' },
      })
    }
  },
)

function clear() {
  if (view) {
    view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: '' } })
  }
}

defineExpose({ clear })
</script>

<template>
  <div class="border border-brand-border rounded overflow-hidden mb-2">
    <div ref="editorRef" class="cm-editor-container"></div>
  </div>
</template>
