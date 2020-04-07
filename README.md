# UnacademyJEE
Simple Command line Utility to batch download Unacdemy notes of chapter

## Getting Started
This tool help you to easily download all the unacademy notes via one command, no need of google account or any link.

this tool fetches link directly from google sheet provided by unacademy so if new content added there then it will be visible here as well

### Prerequisites

python3

_check version using_

```
python --version
```

### Installing and Running

first install all required libraries

```
python -m pip install -r requirements.txt
```
now,run it

```
python main.py -s SUBJECT -c "CHAPTER" "CHAPTER2"..
```

example command
```
python main.py -s physics -c "Calorimetry" "Basic Kinematics"
```

### Help
```
python main.py -h
```
```
python main.py --show
```
## Acknowledgments

* Unacademy JEE team for helping JEE aspirants .
