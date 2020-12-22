import builtins

input_values = []


def mock_input(s):
    return input_values.pop(0)


def mock_input_start():
    global input_values

    input_values = []
    builtins.input = mock_input


def set_keyboard_input(mocked_inputs):
    global input_values

    mock_input_start()
    input_values = mocked_inputs
