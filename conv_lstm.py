import numpy as np
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

import io
import imageio
from IPython.display import Image, display
from ipywidgets import widgets, Layout, HBox
from tensorflow.keras import backend as K
from tensorflow.keras.callbacks import CSVLogger
from keras_self_attention import SeqSelfAttention


def get_data_for_conv_lstm(dataset):

    # Split into train and validation sets using indexing to optimize memory.
    indexes = np.arange(dataset.shape[0])
    np.random.shuffle(indexes)
    train_val_index = indexes[: int(0.8 * dataset.shape[0])]
    test_index = indexes[int(0.8 * dataset.shape[0]) :]
    train_val_dataset = dataset[train_val_index]
    test_dataset = dataset[test_index]

    train_val_index = np.arange(train_val_dataset.shape[0])
    train_index = train_val_index[: int(0.9 * train_val_dataset.shape[0])]
    val_index = train_val_index[int(0.9 * train_val_dataset.shape[0]):]
    train_dataset = train_val_dataset[train_index]
    val_dataset = train_val_dataset[val_index]

    # Normalize the data to the 0-1 range.
    train_dataset[train_dataset < 0] = 0
    train_dataset[train_dataset > 255] = 255
    val_dataset[val_dataset < 0] = 0
    val_dataset[val_dataset > 255] = 255
    test_dataset[test_dataset < 0] = 0
    test_dataset[test_dataset > 255] = 255

    min_train = np.min(train_dataset)
    max_train = np.max(train_dataset)

    print(min_train, max_train)

    train_dataset = train_dataset
    val_dataset = val_dataset
    test_dataset = test_dataset

    # We'll define a helper function to shift the frames, where
    # `x` is frames 0 to n - 1, and `y` is frames 1 to n.
    def create_shifted_frames(data):
        x = data[:, 0 : data.shape[1] - 1, :, :]
        y = data[:, -1:    , :, :]
        return x, y


    # Apply the processing function to the datasets.
    x_train, y_train = create_shifted_frames(train_dataset)
    x_val, y_val = create_shifted_frames(val_dataset)
    x_test, y_test = create_shifted_frames(test_dataset)

    # Inspect the dataset.
    print("Training Dataset Shapes: " + str(x_train.shape) + ", " + str(y_train.shape))
    print("Validation Dataset Shapes: " + str(x_val.shape) + ", " + str(y_val.shape))

    # # Construct a figure on which we will visualize the images.
    # fig, axes = plt.subplots(4, 5, figsize=(10, 8))
    #
    # # Plot each of the sequential images for one random data example.
    # data_choice = np.random.choice(range(len(train_dataset)), size=1)[0]
    # for idx, ax in enumerate(axes.flat):
    #     ax.imshow(np.squeeze(train_dataset[data_choice][idx]), cmap="gray")
    #     ax.set_title(f"Frame {idx + 1}")
    #     ax.axis("off")
    #
    # # Print information and display the figure.
    # print(f"Displaying frames for example {data_choice}.")
    # plt.show()

    return x_train, y_train, x_val, y_val, x_test, y_test, train_dataset, val_dataset, test_dataset




def run_conv_lstm(x_train, y_train, x_val, y_val):
    # Construct the input layer with no definite frame size.
    inp = layers.Input(shape=(None, *x_train.shape[2:]))

    # We will construct 3 `ConvLSTM2D` layers with batch normalization,
    # followed by a `Conv3D` layer for the spatiotemporal outputs.
    x = layers.ConvLSTM2D(
        filters=128,
        kernel_size=(5, 5),
        padding="same",
        return_sequences=True,
        activation="relu",
    )(inp)
    x = layers.BatchNormalization()(x)
    x = layers.ConvLSTM2D(
        filters=256,
	strides=(2, 2),
        kernel_size=(5, 5),
        padding="same",
        return_sequences=True,
        activation="relu",
    )(x)
    x = layers.BatchNormalization()(x)
    x = layers.ConvLSTM2D(
        filters=256,
        kernel_size=(3, 3),
        padding="same",
        return_sequences=True,
        activation="relu",
    )(x)
    x = layers.BatchNormalization()(x)
    x = layers.ConvLSTM2D(
        filters=512,
	strides=(2, 2),
        kernel_size=(1, 1),
        padding="same",
        return_sequences=True,
        activation="relu",
    )(x)
    x = layers.BatchNormalization()(x)
    x = layers.TimeDistributed(layers.Conv2DTranspose(
        filters=256,
        kernel_size=(2, 2),
        activation="relu",
        padding="same",
        strides=(2, 2))
    )(x)
    x = layers.BatchNormalization()(x)
    x = layers.TimeDistributed(layers.Conv2DTranspose(
        filters=128,
        kernel_size=(2, 2),
        activation="relu",
        padding="same",
        strides=(2, 2))
    )(x)
    x = layers.Conv3D(
        filters=3,
        kernel_size=(1, 1, 1),
        activation="relu",
        padding="same"
    )(x)
    #x = layers.Conv3D(
    #    filters=512, kernel_size=(1, 1, 1), activation="relu", padding="same"
    #)(x)
    #x = layers.BatchNormalization()(x)
    #x = layers.Conv3DTranspose(
    #    filters=256,
    #    kernel_size=(2, 2, 2),
    #    activation="relu",
    #    padding="same",
    #    strides=(2, 2, 2)
    #)(x)
    #x = layers.BatchNormalization()(x)
    #x = layers.Conv3DTranspose(
    #    filters=3,
    #    kernel_size=(1, 1, 1),
    #    activation="relu",
    #    padding="same",
    #    strides=(2, 2, 2)
    #)(x)

    # Next, we will build the complete model and compile it.
    model = keras.models.Model(inp, x)
    model.compile(
        loss=keras.losses.mean_absolute_error, optimizer=keras.optimizers.Adam(learning_rate=0.001), metrics=['mae', 'mse']
    )

    # Define some callbacks to improve training.
    early_stopping = keras.callbacks.EarlyStopping(monitor="val_loss",
                                                   patience=10)
    reduce_lr = keras.callbacks.ReduceLROnPlateau(monitor="val_loss",
						  factor=0.5,
                                                  patience=5,
						  min_delta=0.1,
						  verbose=1)

    # Define modifiable training hyperparameters.
    epochs = 25
    batch_size = 8

    # Fit the model to the training data.
    csv_logger = CSVLogger('log.csv', append=True, separator=';')
    model.fit(
        x_train,
        y_train,
        batch_size=batch_size,
        epochs=epochs,
        validation_data=(x_val, y_val),
        callbacks=[reduce_lr, csv_logger]
    )

    return model


def plot_conv_lstm(model, train_dataset, val_dataset):

    # Select a random example from the validation dataset.
    example = val_dataset[np.random.choice(range(len(val_dataset)), size=1)[0]]

    # Pick the first/last ten frames from the example.
    frames = example[:10, ...]
    original_frames = example[10:, ...]

    # Predict a new set of 10 frames.
    for _ in range(10):
        # Extract the model's prediction and post-process it.
        new_prediction = model.predict(np.expand_dims(frames, axis=0))
        new_prediction = np.squeeze(new_prediction, axis=0)
        predicted_frame = np.expand_dims(new_prediction[-1, ...], axis=0)

        # Extend the set of prediction frames.
        frames = np.concatenate((frames, predicted_frame), axis=0)

    # Construct a figure for the original and new frames.
    fig, axes = plt.subplots(2, 10, figsize=(20, 4))

    # Plot the original frames.
    for idx, ax in enumerate(axes[0]):
        ax.imshow(np.squeeze(original_frames[idx]), cmap="gray")
        ax.set_title(f"Frame {idx + 11}")
        ax.axis("off")

    # Plot the new frames.
    new_frames = frames[10:, ...]
    for idx, ax in enumerate(axes[1]):
        ax.imshow(np.squeeze(new_frames[idx]), cmap="gray")
        ax.set_title(f"Frame {idx + 11}")
        ax.axis("off")

    # Display the figure.
    plt.show()
