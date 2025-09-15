/**
 * @typedef {object} ToastProps
 * @property {() => SvelteComponent=} [svg]
 * @property {string} text - Se for falseável, toast não aparece
 * @property {() => void} [onClose]
 * @property {boolean} closed
 * @property {boolean} error - Layout vermelho se true
 */

/**
 * @typedef {'transcribe' | 'print' | 'error' | 'all'} ToastTypes
 */

export {}
