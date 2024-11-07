import numpy as np
import random
import keras
from keras import layers


# Simulated example corpus (adjust this with your own dataset)
train_text = "import keras\nimport numpy as np\nimport pandas as pd\n" * 100


# Define the padding character and the max sequence length
padding_char = '\x00'  # Padding character (you can use any non-existing char)
max_seq_length = 40  # Set your max sequence length

# Create vocabulary of unique characters (including the padding character)
vocabulary_chars = sorted(list(set(train_text + padding_char)))
char_to_index = {char: index for index, char in enumerate(vocabulary_chars)}
index_to_char = {index: char for index, char in enumerate(vocabulary_chars)}


input_sequences = []
output_chars = []
for sequence_index in range(0, len(train_text) - max_seq_length):
    input_sequence = train_text[sequence_index: sequence_index + max_seq_length]
    padded_input_sequence = input_sequence.ljust(max_seq_length, padding_char)
    input_sequences.append(padded_input_sequence)
    output_chars.append(train_text[sequence_index + max_seq_length])

print(f"Number of input sequences: {len(input_sequences):,}.")
print(f"Number of output chars: {len(output_chars):,}.")

# One-hot encode the input sequences and output characters
X_train_ds = np.zeros((len(input_sequences), max_seq_length, len(vocabulary_chars)), dtype="bool")
y_train_ds = np.zeros((len(input_sequences), len(vocabulary_chars)), dtype="bool")

for sequence_index, input_sequence in enumerate(input_sequences):
    for char_index, input_char in enumerate(input_sequence):
        X_train_ds[sequence_index, char_index, char_to_index[input_char]] = 1
    output_char = output_chars[sequence_index]
    y_train_ds[sequence_index, char_to_index[output_char]] = 1

# Define the model
model = keras.Sequential([
    # Masking layer: ignores the padding value
    layers.Masking(mask_value=char_to_index[padding_char], input_shape=(None, len(vocabulary_chars))),
    #layers.LSTM(128, return_sequences=True),
    layers.LSTM(128),
    layers.Dense(len(vocabulary_chars), activation="softmax"),
])

optimizer = keras.optimizers.RMSprop(learning_rate=0.01)
model.compile(loss="categorical_crossentropy", optimizer=optimizer)

# Train the model
epochs = 5  # For demonstration, use more epochs for real training
batch_size = 32
model.fit(X_train_ds, y_train_ds, batch_size=batch_size, epochs=epochs)


# Sampling function (to generate text based on model predictions)
def sample(predictions: np.array, temperature: float = 1.0) -> int:
    predictions = np.asarray(predictions).astype("float64")
    predictions = np.log(predictions) / temperature
    exp_predictions = np.exp(predictions)
    predictions = exp_predictions / np.sum(exp_predictions)
    probas = np.random.multinomial(1, predictions, 1)
    return np.argmax(probas)


# Inference with variable input length (pad input dynamically)
start_index = random.randint(0, len(train_text) - max_seq_length - 1)
#input_sequence = train_text[start_index:start_index + 25]  # Example input of variable length (25 chars)
original_input_sequence = "import"


for temperature in [0.8, 1.0, 1.2]:
    print(f"Temperature: {temperature}")
    input_sequence = original_input_sequence
    generated = original_input_sequence
    next_char = ''
    while next_char != '\n':
        padded_input_sequence = input_sequence.ljust(max_seq_length, padding_char)
        #print("Input sequence: ", input_sequence)
        #print("Padded input sequence: ", padded_input_sequence)
        X_to_predict = np.zeros((1, max_seq_length, len(vocabulary_chars)))
        for char_index, input_char in enumerate(padded_input_sequence):
            X_to_predict[0, char_index, char_to_index[input_char]] = 1.0

        preds = model.predict(X_to_predict, verbose=0)[0]
        next_index = sample(preds, temperature)
        next_char = index_to_char[next_index]
        input_sequence = (input_sequence + next_char)[-max_seq_length:]  # get the last max_seq_length characters
        input_sequence = input_sequence
        generated += next_char
    print("Generated: ", generated)
