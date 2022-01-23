
from animations import animate
from conv_lstm import get_data_for_conv_lstm, run_conv_lstm, plot_conv_lstm
from data_reader import DataReader
import numpy as np




def main():

    data_reader = DataReader()
    convections = data_reader.get_numpy_arrays('convection')
    print('got convections')
    x_train, y_train, x_val, y_val, train_dataset, val_dataset = get_data_for_conv_lstm(convections)
    model = run_conv_lstm(x_train, y_train, x_val, y_val)
    predictions = []
    max_preds = 100
    for img in train_dataset[:100]:
        predictions.append(np.asarray(model.predict(np.expand_dims(img, axis=0))[0, 0, :, :, :], dtype=np.int32))
    #plot_conv_lstm(model, train_dataset, val_dataset)
    animate(predictions, 'predictions.gif')

    trains = []
    for img in train_dataset[1:max_preds+1]:
        trains.append(img[0, :, :, :])
    animate(trains, 'train.gif')

if __name__ == '__main__':
    main()
