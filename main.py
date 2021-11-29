from matplotlib import animation

from animations import animate
from conv_lstm import get_data_for_conv_lstm, run_conv_lstm, plot_conv_lstm
from data_fetcher import DataFetcher
from data_reader import DataReader
import numpy as np




def main():
    #data_fetcher = DataFetcher()
    #data_fetcher.get_day('https://thredds.met.no/thredds/catalog/weamyl/Satellite/meteosat-0deg/2018/06/11/')

    data_reader = DataReader()
    convections = data_reader.get_numpy_arrays('convection')
    print('got convections')
    x_train, y_train, x_val, y_val, train_dataset, val_dataset = get_data_for_conv_lstm(convections)
    model = run_conv_lstm(x_train, y_train, x_val, y_val)
    predictions = []
    for img in train_dataset:
        predictions.append(model.predict(np.expand_dims(img, axis=0))[0, 0, :, :, :])
    #plot_conv_lstm(model, train_dataset, val_dataset)
    animate(predictions)


if __name__ == '__main__':
    main()
