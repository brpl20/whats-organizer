/**
 * Shared type definitions for the WhatsApp Organizer frontend.
 *
 * @typedef {object} ApiResult
 * @property {string} Date
 * @property {string|false} FileAttached
 * @property {number} ID
 * @property {string} Message
 * @property {string} Name
 * @property {string} Time
 * @property {boolean} IsApple
 * @property {string} [ERRO]
 */

/**
 * @typedef {object} ApiError
 * @property {string} [Erro]
 */

/**
 * @typedef {object} Message
 * @property {string} Date
 * @property {string|false} FileAttached
 * @property {number} ID
 * @property {string} Message
 * @property {string} Name
 * @property {string} Time
 * @property {string} [FileURL]
 * @property {string} [type]
 * @property {number} [width]
 * @property {number} [height]
 * @property {number} [duration]
 * @property {string} [thumbnail]
 * @property {string[]} [links]
 * @property {string} [AudioTranscription]
 * @property {string[]} [pages]
 */

/**
 * @typedef {object} MediaModalData
 * @property {string} type - 'image' | 'pdf'
 * @property {string} src - URL da midia
 * @property {string} filename - Nome do arquivo
 * @property {string[]} [links] - Para PDFs com multiplas paginas
 */

/**
 * @typedef {'transcribe' | 'print' | 'error'} ToastType
 */

/**
 * @typedef {object} ToastState
 * @property {string|null} text
 * @property {ToastType} type
 * @property {boolean} isSecurityError
 */

export {};
