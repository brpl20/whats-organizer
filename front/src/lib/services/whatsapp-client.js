/**
 * WhatsApp API client — handles backend communication and WebSocket.
 */

/** @typedef {import('socket.io-client').Socket} SocketType */

/** @type {import('socket.io-client').default | null} */
let io = null;

/** @type {SocketType | null} */
let socket = null;

const SOCKET_TIMEOUT = 5000;

/**
 * Connect to the backend WebSocket for progress updates.
 * @param {string} apiUrl
 * @param {string} uid
 * @param {(msg: string) => void} onMessage
 */
export async function connectSocket(apiUrl, uid, onMessage) {
	if (socket?.connected) return;

	io ??= (await import('socket.io-client')).default;
	socket ??= io(apiUrl, {
		reconnectionAttempts: 5,
		transports: ['websocket', 'polling', 'webtransport'],
		timeout: SOCKET_TIMEOUT,
		query: `uid=${uid}`
	});

	/** @type {Promise<void>} */
	const connect = new Promise((resolve) => socket.on('connect', resolve));
	/** @type {Promise<void>} */
	const timeout = new Promise((_, reject) =>
		setTimeout(() => reject(new Error('Connection timed out')), SOCKET_TIMEOUT)
	);

	Promise.race([connect, timeout]).catch((e) => {
		console.error(e);
		socket = null;
	});

	socket.on('Smessage', (data) => {
		if (data?.data) onMessage(data.data);
	});
}

/** Disconnect the WebSocket. */
export function disconnectSocket() {
	socket?.disconnect?.();
}

/**
 * Upload a ZIP file to the backend for processing.
 * @param {string} apiUrl
 * @param {string} uid
 * @param {File} file
 * @returns {Promise<{ok: boolean, data: any, status?: number}>}
 */
export async function uploadZip(apiUrl, uid, file) {
	const formData = new FormData();
	formData.append('file', file);

	try {
		const response = await fetch(`${apiUrl}/process?uid=${uid}`, {
			method: 'POST',
			body: formData
		});

		const data = await response.json().catch(() => null);
		return { ok: response.ok, data, status: response.status };
	} catch (e) {
		console.error(e);
		return { ok: false, data: null };
	}
}

/**
 * Request PDF generation from the backend.
 * @param {string} apiUrl
 * @param {import('./types').Message[]} messages
 * @param {boolean} isApple
 * @returns {Promise<Blob|null>}
 */
export async function generatePdfBlob(apiUrl, messages, isApple) {
	const response = await fetch(`${apiUrl}/download-pdf`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ messages, isApple })
	});

	if (!response.ok) {
		console.error('PDF error', await response.text());
		return null;
	}

	return response.blob();
}
