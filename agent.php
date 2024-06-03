<?php
require_once 'config.php';
require_once 'classes.php';

$gptClient = new OpenAIClient(
	apiKey: API_KEY,
	model: GPT_MODEL
);

// load token schema and prompt
$tokenSchema = file_get_contents(TOKEN_SCHEMA);
$prompt = file_get_contents(PROMPT);

$fullPrompt = str_replace('{{tokenSchema}}', $tokenSchema, $prompt);

$agent = new GptAgent(
	client: $gptClient,
	purpose: $fullPrompt
);

// accept a message in json and forward it to the agent
$request = json_decode(file_get_contents('php://input'), true);
$notation = $agent->sendMessage($request['prompt']);

// save and run the python script to generate the midi file
file_put_contents('generated/input.token', $notation);
$cmdOutput = shell_exec('python3 token2midi.py generated/input.token generated/output.midi');

$response = [
	'success' => $cmdOutput ? true : false,
	'notation' => $notation,
	'cmdOutput' => $cmdOutput,
];

echo json_encode($response);
