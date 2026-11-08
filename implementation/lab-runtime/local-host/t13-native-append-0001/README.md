# T13 disposable native append of 88 technical successors

`append.py` executes the captured, SHA-256-pinned T13 predecessor/intent preparation, verifies the original 176-event archive and 88 intent bodies, and seals 88 inert governance successors with the selected native executable. In a fresh private temporary root it appends the 88 original semantic/governance event pairs, rejects a correctly resealed successor with the wrong predecessor, then appends all 88 correct successors. A fresh native `read` returns 88 semantic and 176 governance events with checkpoint parity `PASS`, exact event bodies and predecessor links. Repeating the successor batch refuses without changing the cold view. The original bodies are written to mode-0700 temporary storage for the native call, do not enter the public receipt, and are removed with the temporary root on return.

[RESULT.json](RESULT.json) records counts and pins only. No owner Decision, original representation adoption, current live predecessor head, repository write, or authority effect occurs. The source is the frozen historical candidate archive, so this is technical append mechanics rather than T13 completion.

Run from repository root:

```sh
python3 -B implementation/lab-runtime/local-host/t13-native-append-0001/append.py
python3 -B -m unittest discover -s implementation/lab-runtime/local-host/t13-native-append-0001 -p 'test*.py' -q
python3 -O -B -m unittest discover -s implementation/lab-runtime/local-host/t13-native-append-0001 -p 'test*.py' -q
```
