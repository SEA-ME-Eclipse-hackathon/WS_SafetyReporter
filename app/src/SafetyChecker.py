from statistics import mean


class SafetyChecker:
    def __init__(self):
        self.speed_window = []

    def is_speed_safe(self, current_speed):
        if len(self.speed_window) < 5:
            self.speed_window.append(current_speed)
            return True
        avg_speed = mean(self.speed_window)
        self.speed_window.pop(0)
        self.speed_window.append(current_speed)
        if current_speed < avg_speed and (avg_speed - current_speed) > 10:
            return True
        self.speed_window.clear()
        return False
