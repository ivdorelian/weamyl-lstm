
from animations import animate
from conv_lstm import get_data_for_conv_lstm, run_conv_lstm, plot_conv_lstm
from data_reader import DataReader
import numpy as np




def main():

    data_reader = DataReader()
    convections = data_reader.get_numpy_arrays('convection')
    print('got convections')
    x_train, y_train, x_val, y_val, x_test, y_test, train_dataset, val_dataset, test_dataset = get_data_for_conv_lstm(convections)
    model = run_conv_lstm(x_train, y_train, x_val, y_val)
    all = []
    max_preds = 100
    for img, truth in zip(x_test[:100], y_test[:100]):
        print(img.shape, truth.shape)
        pred = np.asarray(model.predict(np.expand_dims(img, axis=0)), dtype=np.int32)

        all.append(np.concatenate([img[0, :, :, :], img[1, :, :, :], img[2, :, :, :], img[3, :, :, :], pred[0, 0, :, :, :], truth[0, :, :, :]], axis=0))
    #plot_conv_lstm(model, train_dataset, val_dataset)
    animate(all, 'all.gif')


if __name__ == '__main__':
    main()
