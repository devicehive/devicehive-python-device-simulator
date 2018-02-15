[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=flat-square)](LICENSE)

# DeviceHive Python Device Simulator

Device activity simulating tool.

## Pre-requirements
To run this tool locally you need to install python dependencies by pip:
```bash
pip install -r requirements.txt
```

## Configuration
Each argument can be passed to script in three different ways:
* Specified as command line argument (priority 1)
* Specified as environment variable (priority 2)
* Specified in config file (priority 3)

_Note: If argument specified in more than one place it will be used according to priority_

### Available arguments
* `devices` Number of devices to simulate. Default is 1.
* `url` (**required**) DeviceHive server url in format http://server.name/api/rest or ws://server.name/api/websocket.
* `delay` Delay between messages in seconds. Default is 1.
* `base_device_name` Base device name. Default is "python-test-".
* `cleanup` Delete devices after stop.
* `verbose` Show debug information.
* `access_token` (**required**) DeviceHive access token.
* `refresh_token` (**required**) DeviceHive refresh token.
* `message_limit` Number of messages to be sent before stop. Default is 0 (infinite loop).
* `time_limit` Number of seconds to work before stop. Default is 0 (infinite loop).
* `message_type` Type of message to be send. Can be either "notification" or "command". Default is "notification".
* `message_name` Message name. Default is "python-test".
* `message_payload` JSON-like message payload. Default is {"key": "value"}.

_Note: Only `access_token` or `refresh_token` can be passed at the same time. Not both._

### Command line arguments
You can pass command line arguments in format --arg_name=arg_value e.g. --devices=5
More info about CLI available in help
```bash
python run.py --help
```

### Environment variables
Corresponding environment variables have `DHDS_` prefix and can be set in format DHDS_ARG_NAME=arg_value e.g. DHDS_DEVICES=5

### Config file
Config file uses JSON syntax.
Path to config file can be specified by command line argument `--config` or by environment variable `DHDS_CONFIG`

[Here](config_example.json) you can found simple config example.

## Usage
This tool can be run using python 2.7+
But i strongly recommend to use python 3.5+ for better performance.

To start simulation locally run:
```bash
python run.py --url="SERVER_URL" --access_token="ACCESS_TOKEN"
```

To start simulation in docker run:
```bash
docker-compose up
```
