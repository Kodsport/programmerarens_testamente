# Problem types

## `pass-fail` (kattis)

Uses the [Kattis problem package format](https://www.kattis.com/problem-package-format/spec/2025-09.html).

Next location is given when all test cases pass.

Needs to have test cases in data/sample or data/secret
You can use `max_time` in the config file to limit the cpu time the submitted program is allowed to use

Example: deladChoklad

## `pt_what-is-code-doing`

Problem has code, shown to user in a non-copyable way.

Needs to have a `generate.py` with the function `generateCode()`

Next location *is* the answer.

Example: minMax

## `pt_text`

Question in text form.

Next location *is* the answer.

Needs to have a `generate.py` with the function `generateCode()`

Example: caesarchiffer

## `pt_input-text`

Same as [`text`](#text), but the answer is submitted.

Next location is given when a correct answer is submitted.

Needs to have correct answers defined with `correct: ` in the config file. Multiple correct answers are allowed

Example: nameTheSort
