## Installation

```
python setup.py install
```

## Usage
Usage: list_yt_channel [OPTIONS]

Options:
  -k, --api-key TEXT           Google Data API key to use. You can get one
                               here: https://console.developers.google.com
                               [required]
  -c, --channel_id TEXT        Youtube channel to get videos from  [required]
  -o, --output-file-path TEXT  File to write found video links to (content
                               replaced each time)
  -f, --published-after TEXT   Only list videos published after this date,
                               otherwise list all
  -t, --published-before TEXT  Only list videos published before this date,
                               otherwise list all
  -v, --verbose                Verbosity level, WARN, INFO, DEBUG
  --help                       Show this message and exit.
