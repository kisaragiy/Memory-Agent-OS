class ToolNormalizer:

    def normalize(self, output):
        if "timestamp" in output:
            del output["timestamp"]
        if "random_id" in output:
            del output["random_id"]
        return output
