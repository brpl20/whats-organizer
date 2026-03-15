/**
 * File processing utilities — ZIP handling, MIME types, media info extraction.
 */

/** @type {import('jszip') | null} */
let JSZip = null;

/** @type {import('mammoth') | null} */
let mammoth = null;

/**
 * Get the file extension (lowercase).
 * @param {string} filename
 * @returns {string}
 */
export const getExt = (filename) => filename.split('.').pop()?.toLowerCase() ?? '';

/**
 * Get the filename from a path.
 * @param {string} path
 * @returns {string}
 */
export const getFileName = (path) => path.split('/').pop() ?? path;

/**
 * Get MIME type from filename extension.
 * @param {string} filename
 * @returns {string}
 */
export function getFileType(filename) {
	const ext = getExt(filename);
	/** @type {Record<string, string>} */
	const types = {
		pdf: 'application/pdf',
		docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
		docm: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
		doc: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
		odt: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
		pptx: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
		ppt: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
		odp: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
		xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
		xls: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
		ods: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
		jpg: 'image/jpeg',
		jpeg: 'image/jpeg',
		png: 'image/png',
		gif: 'image/gif',
		mp4: 'video/mp4',
		opus: 'audio/opus'
	};
	return types[ext] || 'application/octet-stream';
}

/**
 * Extract all files from a ZIP as object URLs.
 * @param {File} file
 * @returns {Promise<[string, string, Blob][]>} Array of [url, filename, blob]
 */
export async function extractZipFiles(file) {
	JSZip ??= (await import('jszip')).default;
	const zip = new JSZip();
	const contents = await zip.loadAsync(file);

	return Promise.all(
		Object.entries(contents.files).map(async ([filename, zipEntry]) => {
			const arrayBuffer = await zipEntry.async('arraybuffer');
			const blob = new Blob([arrayBuffer], { type: getFileType(filename) });
			const url = URL.createObjectURL(blob);
			return /** @type {[string, string, Blob]} */ ([url, filename, blob]);
		})
	);
}

/**
 * Add messages JSON into a ZIP file (for backend PDF injection).
 * @param {File} file
 * @param {import('./types').Message[]} messages
 * @returns {Promise<File>}
 */
export async function addMessagesJsonToZip(file, messages) {
	JSZip ??= (await import('jszip')).default;
	const zip = new JSZip();
	const contents = await zip.loadAsync(file);
	contents.file('whats_organizer/messages.json', JSON.stringify(messages));
	const updatedFile = await zip.generateAsync({ type: 'blob' });
	return new File([updatedFile], file.name, { type: file.type });
}

/**
 * Extract messages JSON from a ZIP file (for backend PDF injection).
 * @param {File} file
 * @returns {Promise<import('./types').Message[]>}
 */
export async function extractMessagesJsonFromZip(file) {
	JSZip ??= (await import('jszip')).default;
	const zip = new JSZip();
	const contents = await zip.loadAsync(file);
	const msgFile = contents.files['whats_organizer/messages.json'];
	return JSON.parse(await msgFile.async('text'));
}

/**
 * Get detailed info about a file (dimensions, duration, pages, etc).
 * @param {Blob} blob
 * @param {string} filename
 * @returns {Promise<Partial<import('./types').Message>>}
 */
export async function getFileInfo(blob, filename) {
	const ext = getExt(filename);
	switch (ext) {
		case 'pdf':
			return { type: 'pdf' };
		case 'docx':
		case 'docm':
			return await getDocxInfo(blob);
		case 'jpg':
		case 'jpeg':
		case 'png':
		case 'gif':
			return await getImageInfo(blob);
		case 'mp4':
			return await getVideoInfo(blob);
		case 'opus':
			return { type: 'audio' };
		default:
			return {};
	}
}

/** @param {Blob} blob */
async function getDocxInfo(blob) {
	const arrayBuffer = await blob.arrayBuffer();
	mammoth ??= await import('mammoth');
	const htmlResult = await mammoth.convertToHtml({ arrayBuffer });
	const text = htmlResult.value;
	const pages = text.split('\n\n').slice(0, 6);
	return { type: 'docx', pages };
}

/** @param {Blob} blob */
function getImageInfo(blob) {
	return new Promise((resolve) => {
		const img = new Image();
		img.onload = () => resolve({ type: 'image', width: img.width, height: img.height });
		img.src = URL.createObjectURL(blob);
	});
}

/** @param {Blob} blob */
function getVideoInfo(blob) {
	return new Promise((resolve) => {
		const video = document.createElement('video');
		video.src = URL.createObjectURL(blob);
		video.onloadedmetadata = () => {
			resolve({ type: 'video', duration: video.duration });
		};
	});
}

// --- File type checkers ---

/** @param {string} filename */
export const isAudioFile = (filename) => filename?.endsWith?.('.opus');

/** @param {string} filename */
export const isVideoFile = (filename) => filename?.endsWith?.('.mp4');

/** @param {string} filename */
export const isImgFile = (filename) => {
	const lower = filename?.toLowerCase() ?? '';
	return lower.includes('.jpg') || lower.includes('.jpeg') || lower.includes('.png');
};

/** @param {string} filename */
export const isWordFile = (filename) => {
	const lower = filename?.toLowerCase() ?? '';
	return lower.includes('.docx') || lower.includes('.docm');
};

/**
 * Format time to remove seconds (HH:MM:SS -> HH:MM).
 * @param {string} time
 * @returns {string}
 */
export function formatTime(time) {
	if (!time) return '';
	const parts = time.split(':');
	if (parts.length === 3) return `${parts[0]}:${parts[1]}`;
	return time;
}

/**
 * Get chat bubble sides based on device type.
 * @param {boolean} isApple
 * @returns {[string, string]}
 */
export const getSideByDevice = (isApple) =>
	isApple ? /** @type {[string, string]} */ (['left', 'right']) : ['right', 'left'];
