class ActionRouter:

    def route(self, task):

        if "video" in str(task):
            return self.video_pipeline(task)

        if "audio" in str(task):
            return self.tts_pipeline(task)

        return self.llm_response(task)
