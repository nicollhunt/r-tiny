class EventBus:
    def __init__(self):
        self._subscribers = {}
        
    def subscribe(self, event_type, callback):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type, callback):
        if event_type not in self._subscribers:
            return
        
        self._subscribers[event_type].remove(callback)

    def dispatch(self, event_type, *args):
        if event_type not in self._subscribers:
            return
        
        for callback in self._subscribers[event_type]:
            callback(args)

bus = EventBus()