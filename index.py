import os
from time import time

import librosa
import utils

from twilio.rest import Client

config = utils.load_yaml('config.yml')

client = Client(
  config['twilio']['account_sid'],
  config['twilio']['auth_token']
)

# Holding the counts of the last five recorded sessions
count_log = []

# Timestamp when the client was contacted the last time
message_sent = False

# Phone numbers that get notified then alarm signal detected
receivers = ['+491731586539']

while True:
  # Print recording message in appropriate colors
  print()
  print('Recording… ')
  print()

  # save microphone input to wav file
  utils.record('./dist/record.wav')

  # load temporary recorded wav file
  # https://librosa.github.io/librosa/generated/librosa.core.load.html
  x, sr = librosa.load('./dist/record.wav')

  # Get peaks of sound signal
  count = utils.get_peaks_count(x, sr)

  # Add count to count log
  count_log.insert(0, count)

  # Make sure count log only contains 5 items
  if(len(count_log) > 5): del count_log[-1]

  # Log count log
  print('---'*10)
  print('Peeps of count_log records:', count_log)
  print('---'*10)

  # If more then five alarm signals were found and
  # the no message was sent in the last 30 minutes
  if sum(count_log) > 5 and message_sent < time() - 60*30:

    for phone_number in receivers:
      message = client.messages.create(
        from_=config['twilio']['phone_number'],
        to=phone_number,
        body=config['message']
      )

      # Log when client gets contacted
      print('Send message:')
      print('{} to {}: {}'.format(config['twilio']['phone_number'], phone_number, config['message']))

    # Update timestamp when message was sent
    message_sent = time()
