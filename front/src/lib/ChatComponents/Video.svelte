<script>
	import { onDestroy } from 'svelte';
	/**
	 * @type {string}
	 * Cria um componente de vídeo e um thumbnail quando exporta para PDF.
	 */
	export let fileURL;

	/** @type {HTMLVideoElement | null} */
	let video;

	/** @type {HTMLCanvasElement | null} */
	let canvas;

	/** @type {((this: HTMLVideoElement, ev: Event) => any) | null} */
	let loadListener = null;

	let renderedThumb = false;

	$: if (video && canvas && !loadListener) {
		loadListener = () => {
			const renderFrame = (rendered = false) => {
				if (!video?.videoWidth || !video?.videoHeight) return
				const ctx = canvas.getContext('2d');
				canvas.width = video.videoWidth;
				canvas.height = video.videoHeight;

				if (rendered) requestAnimationFrame(() => {
					renderedThumb = true;
				});

				// const proportion = video.videoWidth / video.videoHeight;
				ctx.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
				requestAnimationFrame(() => renderFrame(true));
			};

			try {
				renderFrame();
			} catch (e) {
				renderedThumb = true;
				throw e;
			}
		};

		video.addEventListener('loadeddata', loadListener);
	}

	$: if (video && renderedThumb && loadListener)
		video.removeEventListener('loadeddata', loadListener);

	onDestroy(() => {
		if (video && loadListener) {
			video.removeEventListener('loadeddata', loadListener);
		}
	});
</script>

<video bind:this={video} controls src={fileURL} data-rendered={renderedThumb} preload='auto'>
	<track kind="captions" label="Vídeo enviado pelo WhatsApp" />
</video>
<div class="video-thumb" data-rendered={renderedThumb}>
	<canvas bind:this={canvas}></canvas>
	<div class="play-icon">
		<div class="tri"></div>
	</div>
</div>

<style>
	video {
		display: block;
		aspect-ratio: 1;
	}

	.video-thumb {
		display: none;
		position: relative;
	}

	video,
	.video-thumb,
	canvas {
		max-width: 100%;
		height: 400px;
		overflow: hidden;
	}

	.play-icon {
		background: rgba(0, 0, 0, 0.55);
		width: 100px;
		height: 48px;
		border-radius: 5px;
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		z-index: 9;
		display: grid;
		place-content: center;
	}

	.tri {
		width: 0;
		height: 0;
		border-style: solid;
		border-width: 14px 0 14px 28px;
		border-color: transparent transparent transparent #ffffff;
		margin: auto auto;
	}

	@media print {
		video {
			display: none !important;
		}
		.video-thumb {
			display: flex !important;
			justify-content: center;
			aspect-ratio: 1;
		}
	}
</style>
