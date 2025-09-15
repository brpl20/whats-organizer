<script>
	import { onDestroy } from 'svelte';
	/** @type {string} */
	export let filename;
	/** @type {string} */
	export let fileUrl;
	/** @type {string} */
	export let audioTranscription;

	/** @type {string} */
	let browser = '';

	/** svelte 5 derived rune */
	$: if (window?.chrome) browser = 'chrome'; 

</script>

<div class={`audio-message ${browser}`} data-testid="audio">
	<div class="audio-filename">{filename}</div>
	<div class="wrap">
		<audio
			preload="metadata"
			data-rendered="false"
			on:loadedmetadata={({ target }) => {
				// Para mostrar a duração do áudio ao gerar PDF;
				target.setAttribute('data-rendered', 'true');
			}}
			controls
			src={fileUrl}
		/>
	</div>
	{#if audioTranscription}
		<div class="transcription">
			{audioTranscription}
		</div>
	{/if}
</div>

<style>
	.audio-message {
		display: grid;
		width: 100%;
	}

    .audio-filename {
		font-size: 0.8em;
		color: #666;
		margin-bottom: 5px;
	}
    
    .transcription {
		margin-top: 5px;
		font-style: italic;
		color: #666;
	}

	.audio-message audio {
		width: 100%;
	}

	.audio-message.chrome audio {
		width: 300px;
		border-radius: 20px;
		display: flex;
		background-color: #e0f5e9;
		border-radius: 25px;
		padding: 5px 10px;
		position: relative;
		outline: none;
		-webkit-appearance: none;
		appearance: none;
	}

	.audio-message audio::-webkit-media-controls-enclosure {
		background-color: #e0f5e9;
		border-radius: 25px;
	}

	.audio-message audio::-webkit-media-controls {
		background-color: #e0f5e9;
	}

	.audio-message audio::-webkit-media-controls-play-button,
	.audio-message audio::-webkit-media-controls-pause-button {
		background-color: #25d366;
		color: #fff;
		border-radius: 50%;
		width: 30px;
		height: 30px;
		border: none;
	}

	.audio-message audio::-webkit-media-controls-play-button:hover,
	.audio-message audio::-webkit-media-controls-pause-button:hover {
		background-color: #1bb257;
	}

	.audio-message audio::-webkit-media-controls-volume-control-container,
	.audio-message audio::-webkit-media-controls-volume-slider-container,
	.audio-message audio::-webkit-media-controls-overflow-menu-button {
		display: none !important;
	}

	.audio-message audio::-webkit-media-controls-current-time-display {
		display: none;
	}

    .audio-message :is(audio::-webkit-media-controls-time-remaining-display, .wrap) {
        --audio-message-time-left: 50px;
        --audio-message-time-bottom: 0;
    }

	.audio-message audio::-webkit-media-controls-time-remaining-display {
		position: absolute;
		left: var(--audio-message-time-left);
		bottom: var(--audio-message-time-bottom);
	}

	/**
	Esconde a "/" no player de audio, delimitando tempo atual/ tempo total,
	agradeço https://stackoverflow.com/users/2817442/iorgu pela resposta
	no stackoverflow sobre como esconder essa "/"
	Aplica somente no Chrome (Chromium, Brave e Edge acho?)
	*/

	.audio-message .wrap {
		position: relative;
		width: fit-content;
		height: fit-content;
		display: block;
		margin: 10px auto;
	}

	.audio-message.chrome .wrap::before {
		content: '';
		background: #e0f5e9;
		width: 10px;
		height: 15px;
		position: absolute;
		left: var(--audio-message-time-left);
		bottom: var(--audio-message-time-bottom);
		z-index: 1;
		margin-bottom: 5px;
		margin-left: 10px;
	}

	.audio-message audio::after {
		content: attr(data-duration);
		position: absolute;
		bottom: -15px;
		left: 50%;
		transform: translateX(-50%);
		font-size: small;
		color: #1a3e1a;
		font-family: Arial, sans-serif;
	}

	@-moz-document url-prefix() {
		.audio-message .wrap::before {
			content: none !important;
		}
	}

	/* Firefox styles don't work as firefox has no pseudo attributes
	when inspecting the shadow dom, only webkit
	.audio-message audio::-moz-media-controls-enclosure {
		background-color: #e0f5e9;
		border-radius: 25px;
	}

	.audio-message audio::-moz-media-controls-button {
		background-color: #25d366;
		color: white;
		border-radius: 50%;
		border: none;
	}

	.audio-message audio::-moz-media-controls-button:hover {
		background-color: #1bb257;
	}

	.audio-message audio::-moz-time-slider-thumb {
		width: 10px;
		height: 10px;
		background-color: #25d366;
		border-radius: 50%;
		border: 2px solid #fff;
		box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
	}
	*/
</style>
