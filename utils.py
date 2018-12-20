import pyaudio
import wave
import librosa
import numpy as np
import yaml

def load_yaml(path):
  with open(path, 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
  return cfg

# Record example from pyaduio
# https://people.csail.mit.edu/hubert/pyaudio/#record-example
def record(path, seconds=2):
  CHUNK = 1024
  FORMAT = pyaudio.paInt16
  CHANNELS = 2
  RATE = 22050
  RECORD_SECONDS = seconds
  WAVE_OUTPUT_FILENAME = path

  p = pyaudio.PyAudio()

  stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK
  )

  frames = []

  for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

  stream.stop_stream()
  stream.close()
  p.terminate()

  wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
  wf.setnchannels(CHANNELS)
  wf.setsampwidth(p.get_sample_size(FORMAT))
  wf.setframerate(RATE)
  wf.writeframes(b''.join(frames))
  wf.close()

# Get the sum of a specific frequency band
def sum_freq(values, freq):
  return sum(np.array(values)[freq[0]:freq[1]])

# Get peaks of sound signal by threshold
def get_peaks_max(x, y, threshold):
  peaks_x = []
  peaks_y = []
  start = None
  end = None

  for b in range(len(y)):
    if y[b] > threshold and start is None:
      start = b
    if y[b] < threshold and start is not None:
      end = b
    if start is not None and end is not None:
      delta = end - start
      peaks_x.append(x[end - int(delta / 2)])
      peaks_y.append(max(y[start:end]))
      start = None
      end = None

  return peaks_x, peaks_y

# Get peak count with of sound signal by threshold using fast fourier transformation
# https://musicinformationretrieval.com/stft.html
def get_peaks_count(x, sr, threshold=20, frequency_band=[330, 340]):
  hop_length = int(sr / 10)
  X = librosa.stft(x, hop_length=hop_length)
  X = abs(X)

  seconds_total = len(x) / sr
  seconds_window_size = seconds_total / (len(x) / hop_length)

  # print('sample rate: {}'.format(sr))
  # print('window size in samples: {} of {}'.format(hop_length, len(x)))
  # print('window size in seconds: {} of {}'.format(seconds_window_size, seconds_total))

  x = [] # time series in seconds
  y = [] # frequency sum between 3300 and 3400

  for i in range(X.shape[1]):
      x.append(i*seconds_window_size)
      sums = []
      for j in range(X.shape[0]):
          sums.append(X[j][i])
      y.append(sum_freq(sums, frequency_band))

  p_x, p_y = get_peaks_max(x, y, threshold)

  return len(p_y)
