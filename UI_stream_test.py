from pylsl import StreamInlet, resolve_stream
import numpy as np
import time

def main():
    print('Looking for stream...')
    streams = resolve_stream('name', 'PressureSensor_1')
    inlet = StreamInlet(streams[0])

    while True:
        data, _ = inlet.pull_sample(0.1, sample=1)
        #print(np.array(data).shape)
        #print(data)
        matrix = np.array(data).reshape(16, 6)
        print(matrix.shape)

if __name__ == "__main__":
    main()
