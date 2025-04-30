from event_bus import bus

import engine_io as io

class Rumble:
    def __init__(self, amount: float, decay: float):
        self.amount = amount
        self._decay = decay
        
    def tick(self) -> float:
        self.amount -= self._decay
        return self.amount
        
    def is_done(self):
        return self.amount <= 0
        

class RumbleController:
    def __init__(self):
        self._active = []
        self._decay = 0.05
        self._currentRumble = 0
        self._frame = 0
        self._frame_delay = 2
        self._is_active = True

        bus.subscribe("play_rumble", self.on_rumble)
        
    def on_rumble(self, evt):
        amount = evt[0]
        decay = evt[1]
        
        self._active.append(Rumble(amount, decay))

    def set_active(self, active: bool):
        self._is_active = active

    def tick(self):
        max_rumble = 0;
        
        self._frame += 1
        if (self._frame % self._frame_delay) != 0:
            return
     
        for rumble in self._active:
            amount = rumble.tick()
            if amount > max_rumble:
                max_rumble = amount
            elif amount <= 0:
                self._active.remove(rumble)
        
        if not self._is_active:
            max_rumble = 0
        
        if self._currentRumble != max_rumble:
            self._currentRumble = max_rumble
                   
            print("set rumble:" + str(self._currentRumble))
            io.rumble(self._currentRumble)
        
    