import time

count = 200

class Info:
    def __init__(self, ui, font, color):
        self.ui = ui
        self.font = font
        self.color = color
        self.frame_count = 0
        self.frame_rate = 0
        self.t0 = time.clock()
        
    def display(self):    
        global count
        # Do other bits of logic for the game here
        self.frame_count += 1
        if self.frame_count % count == 0:
            self.t1 = time.clock()
            self.frame_rate = count / (self.t1-self.t0)
            self.t0 = self.t1
        
        self.text = self.font.render(
            "Frame = {0}, rate = {1:.2f} fps".format(
                self.frame_count, 
                self.frame_rate
            ), 
            True, 
            self.color
        )
        self.ui.blit(self.text, (10, 10))
        