import sys
from typing import Dict

class REPL:
    def __init__(self, runtime):
        self.runtime = runtime
        self.input_buffer = []
        self.execution_output = []
        self.error_output = []

    def run(self):
        while True:
            try:
                user_input = input(">>> ")
                if not user_input.strip():
                    continue

                request = {'input': user_input}
                response = self.runtime.entry(request)
                self.handle_response(response)

            except EOFError:
                print("\nExiting REPL...")
                break
            except Exception as e:
                self.error_output.append(f"Error: {str(e)}")

    def handle_response(self, response: Dict):
        if response.get('status') == 'error':
            self.error_output.append(response['error'])
        else:
            self.execution_output.append(str(response))

        for output in self.error_output:
            print(output)

        for output in self.execution_output:
            print(output)

        # Clear buffers after processing
        self.input_buffer.clear()
        self.execution_output.clear()
        self.error_output.clear()

        # Reset state for the next cycle
        self.runtime.reset_state()
