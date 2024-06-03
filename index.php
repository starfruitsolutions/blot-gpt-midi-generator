<?php
	$exampleOutput = 'token-schemas/schema_v1.token';
	$exampleMidi = 'token-schemas/schema_v1.midi';
?>

<div id="container">
	<h1>BLoT Gen</h1>
	<code id="token-text"><?= file_get_contents($exampleOutput) ?></code>
	<div id="midi">
		<div id="player">
			<midi-player id="midi-player" src="<?= $exampleMidi ?>" sound-font></midi-player>
		</div>
		<button id="download" class="button">Download</button>
	</div>
	<form id="form">
		<input id="prompt" type="text" autocomplete="off">
		<input id="submit" class="button" type="submit" value="Generate">
	<form>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
<script src="https://cdn.jsdelivr.net/combine/npm/tone@14.7.58,npm/@magenta/music@1.22.1/es6/core.js,npm/focus-visible@5,npm/html-midi-player@1.4.0"></script>
<script>
	// hide download buttone by default
	$('#download').hide()
	$('#download').on('click', () => {
		console.log('downloading midi file')
		window.location.href = 'generated/output.midi'
	})

	let processing =false

	$('#form').on('submit', (e) => {
		e.preventDefault()
		if(processing) return
		processing = true

		// change the button text to processing
		$('#submit').val('Processing...')

		// send the prompt to Agent
		fetch('agent.php', {
			method: "POST",
			body: JSON.stringify({
				prompt: $('#prompt').val()
			}),
			headers: {
				'Content-Type': 'application/json; charset=UTF-8'
			},
		}).then((response) => response.json()).then((data) => {
			console.log(data.cmdOutput)// log python output

			if (!data.success) alert('Error generating midi file.')

			// update the token text
			$('#token-text').text(data.notation)

			// refresh the midi player
			$('#midi-player').attr('src', 'generated/output.midi')

		}).finally(() => {
			processing = false
			$('#download').show()
			$('#submit').val('Generate')
		})
	})

</script>

<style>
	body {
		display: flex;
		justify-content: center;
		align-items: center;
		font-weight: 500;
		color: white;
		background-color: #121212;
	}

	#container {
		height: 80%;
		width: 830px;
		padding: 20px;
		border-radius: 5px;
		display: flex;
		flex-direction: column;
		justify-content: space-between;
		background-color: #212121;
	}

	#token-text {
		padding: 15px;
		background-color: #121212;
		color: white;
		white-space: pre-wrap;
		overflow-y: scroll;
	}

	#midi {
		height: 40px;
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin: 30px 0px;
	}

	#player {
		width: 80%;
		margin-right: 10px;
		color: black;
	}

	midi-player {
		width: 100%;
		height: 100%;
	}

	.download-link {
		background-color: #212121;
		color: white;
		font-size: 1.1em;
	}

	#form {
		margin: 0;
		height: 40px;
		display: flex;
		justify-content: space-between;
		color: white;
	}

	#prompt {
		width: 80%;
		height: 100%;
		padding: 15px;
		background-color: #121212;
		color: white;
	}

	.button {
		width: 20%;
		height: 100%;
		background-color: #212121;
		color: white;
		font-size: 1.1em;
		cursor: pointer;
	}

</style>
