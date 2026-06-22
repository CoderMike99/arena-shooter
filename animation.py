class Animation():
    def __init__(self,
                 frames,
                 frame_duration):
        
        self.frames = frames
        self.frame_duration = frame_duration
        self.current_index = 0
        self.timer = 0

    def update(self):
        self.timer += 1
        if self.timer >= self.frame_duration:
            self.timer = 0
            self.current_index = (self.current_index + 1) % len(self.frames)

    def get_current_frame(self):
        return self.frames[self.current_index]


