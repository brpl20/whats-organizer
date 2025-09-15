<script>
	import { io } from 'socket.io-client';
	import { onMount } from 'svelte';

	let socket;
	let messages = [];

	onMount(() => {
		socket = io('https://api.whatsorganizer.com.br:8443');

		socket.on('connect', () => {
			console.log('Conectado ao servidor');
		});

		socket.on('message', (msg) => {
			console.log('Mensagem do servidor:', msg);
			messages = [...messages, { from: 'server', text: msg }];
		});

		socket.on('response', (msg) => {
			console.log('Resposta do servidor:', msg);
			messages = [...messages, { from: 'server', text: msg }];
		});

		socket.on('disconnect', () => {
			console.log('Desconectado do servidor');
		});

		return () => {
			socket.disconnect();
		};
	});

	function sendMessage() {
		const message = prompt('Digite sua mensagem:');
		if (message) {
			socket.emit('message', message);
			messages = [...messages, { from: 'client', text: message }];
		}
	}
</script>

<main>
	<h1>Cliente Socket.IO</h1>

	<button on:click={sendMessage}>Enviar Mensagem</button>

	<h2>Mensagens:</h2>
	<ul>
		{#each messages as message}
			<li><strong>{message.from}:</strong> {message.text}</li>
		{/each}
	</ul>
</main>
