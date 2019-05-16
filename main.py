# %% Imports and functions
import subprocess
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import callbacks, layers, models, optimizers, regularizers
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# %% Data pre-processing
train_dir = "data/train/"
test_dir = "data/test/"

# Parameters
batch_size = 64
input_dimension = (32, 32)
model_name = 'model_18'

# Train/Val
train_datagen = ImageDataGenerator(
    rescale=1. / 255,
    validation_split=0.1)

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=input_dimension,
    color_mode="rgb",
    batch_size=batch_size,
    class_mode='categorical',
    subset='training')

validation_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=input_dimension,
    color_mode="rgb",
    batch_size=batch_size,
    class_mode='categorical',
    subset='validation')

# Test
test_datagen = ImageDataGenerator(rescale=1. / 255)

test_generator = test_datagen.flow_from_directory(
    test_dir,
    target_size=input_dimension,
    color_mode="rgb",
    shuffle=False,
    batch_size=2)


# %% Model - Initialization

# Conv(size, input_channels, output_channels, strides=1
## Group - 1
model = tf.keras.Sequential()
model.add(layers.Conv2D(filters=16, kernel_size=(3, 3), strides=1))
model.add(layers.BatchNormalization())
model.add(layers.ReLU())
model.add(layers.Conv2D(filters=96, kernel_size=(3, 3), strides=1))
model.add(layers.BatchNormalization())
model.add(layers.ReLU())
model.add(layers.Conv2D(filters=96, kernel_size=(3, 3), strides=1))
model.add(layers.BatchNormalization())
model.add(layers.ReLU())
model.add(layers.Conv2D(filters=96, kernel_size=(3, 3), strides=1))
model.add(layers.BatchNormalization())
model.add(layers.ReLU())
model.add(layers.Conv2D(filters=96, kernel_size=(3, 3), strides=1))
model.add(layers.BatchNormalization())
model.add(layers.ReLU())
model.add(layers.Conv2D(filters=96, kernel_size=(3, 3), strides=1))
model.add(layers.BatchNormalization())
model.add(layers.ReLU())
## Group - 2
model.add(layers.Conv2D(filters=192, kernel_size=(3, 3), strides=1))
model.add(layers.BatchNormalization())
model.add(layers.ReLU())
model.add(layers.Conv2D(filters=192, kernel_size=(3, 3), strides=1))
model.add(layers.BatchNormalization())
model.add(layers.ReLU())
model.add(layers.Conv2D(filters=192, kernel_size=(3, 3), strides=1))
model.add(layers.BatchNormalization())
model.add(layers.ReLU())
model.add(layers.Conv2D(filters=192, kernel_size=(3, 3), strides=1))
model.add(layers.BatchNormalization())
model.add(layers.ReLU())
model.add(layers.Conv2D(filters=192, kernel_size=(3, 3), strides=1))
model.add(layers.BatchNormalization())
model.add(layers.ReLU())
model.add(layers.Conv2D(filters=192, kernel_size=(3, 3), strides=1))
model.add(layers.BatchNormalization())
model.add(layers.ReLU())
model.add(layers.GlobalAvgPool2D())
## Group - Dense
model.add(layers.Flatten())
model.add(layers.Dense(128, activation='relu'))
model.add(layers.BatchNormalization())
model.add(layers.Dropout(0.4))
model.add(layers.Dense(64, activation='relu'))
model.add(layers.BatchNormalization())
model.add(layers.Dropout(0.4))
model.add(layers.Dense(12, activation='relu'))
model.add(layers.BatchNormalization())
model.add(layers.Dense(2, activation='softmax'))


# Compile
optimizer = optimizers.RMSprop(learning_rate=0.0005)
model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['accuracy'])


# %% Model - Training
n_epochs = 50
data_augmentation_coef = 1.0

# Callbacks
early_stop = callbacks.EarlyStopping(monitor='val_loss', min_delta=0.025, patience=10, verbose=1)
reduce_lr = callbacks.ReduceLROnPlateau(monitor='val_loss', min_delta=0.025, patience=5, min_lr=0.00001,
                                        factor=0.5, verbose=1)
model_checker = callbacks.ModelCheckpoint(filepath='models/' + model_name, monitor='val_accuracy', save_best_only=True,
                                          save_weights_only=True, verbose=1)
tensorboard = callbacks.TensorBoard(log_dir='logs/' + model_name)  # tensorboard --logdir=logs/model_18/

model.fit_generator(train_generator, steps_per_epoch=train_generator.samples * data_augmentation_coef // batch_size,
                    validation_data=validation_generator,
                    validation_steps=validation_generator.samples // batch_size,
                    epochs=n_epochs,
                    callbacks=[early_stop, reduce_lr, model_checker, tensorboard],
                    workers=15,
                    use_multiprocessing=True)


# %% Model - Predict
predictions = model.predict_generator(test_generator, steps=test_generator.samples//2, verbose=1,
                                      workers=15, use_multiprocessing=True)


# %% Predictions - Post-processing
predicted_class = np.argmax(predictions, axis=1)
filenames = test_generator.filenames
filenames = [file.split(sep='/')[1].split(sep='.')[0] for file in filenames]

results = pd.DataFrame({"id": filenames,
                        "label": predicted_class})

results.to_csv('submissions/' + model_name + '.csv', index=False)

# %% Model - Kaggle evaluation
subprocess.run('kaggle competitions submit -c histopathologic-cancer-detection -f submissions/' + model_name + '.csv'
               ' -m ' + '"' + model_name + '"', shell=True)
