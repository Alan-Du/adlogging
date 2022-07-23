# adlogging

adlogging is a Python library for convert python print into formatted logs and keeps printing ability at the same time. 
It supports customized logging configuration, automatic trace of function calls from different objects and classes.
For now, due to some library issue, it only works for MAC/LINUX machines, WINDOWS machine will not work.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install adlogging.

```bash
pip install adlogging
```

## Usage

```python
import adlogging
adlogging.init({"STYLE": "SIMPLE", "FILE":"SAME"})

# after calling adlogging.init() all prints will go into logs
print("Hello World") # will be in logs file name "~/logs/SAME"

adlogging.info("This is info msg")
adlogging.debug("This is debug msg")
adlogging.warning("This is warning msg")
adlogging.error("This is error msg")
adlogging.critical("This is critical msg")
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.
