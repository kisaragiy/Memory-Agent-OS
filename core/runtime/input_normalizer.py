class InputNormalizer:
    def normalize(self, raw_input):
        if isinstance(raw_input, str):
            input_type = 'text'
        else:
            input_type = type(raw_input).__name__

        return {
            'raw': raw_input,
            'type': input_type
        }
