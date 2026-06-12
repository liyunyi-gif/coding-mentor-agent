<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { EditorView, keymap, lineNumbers, highlightActiveLine } from '@codemirror/view'
import { EditorState } from '@codemirror/state'
import { python } from '@codemirror/lang-python'
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
      updateListener,
      EditorState.tabSize.of(4),
      EditorView.theme({
        '&': { height: '120px', backgroundColor: '#fafafa', borderRadius: '6px', border: '1px solid #e5e7eb' },
        '.cm-scroller': { overflow: 'auto', fontFamily: "'Fira Code', 'Consolas', monospace", fontSize: '13px' },
        '.cm-gutters': { backgroundColor: '#f3f4f6', color: '#9ca3af', borderRight: '1px solid #e5e7eb' },
        '.cm-activeLineGutter': { backgroundColor: '#e5e7eb' },
        '.cm-activeLine': { backgroundColor: '#f3f4f6' },
        '.cm-cursor': { borderLeftColor: '#374151' },
        '.cm-selectionBackground': { backgroundColor: '#bfdbfe !important' },
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
  <div ref="editorRef"></div>
</template>
