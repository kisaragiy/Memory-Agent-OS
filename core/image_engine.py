class ImageEngine:
    def __init__(self):
        self.output_dir = "output/images"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_image(self, prompt):
        request_action(prompt)
