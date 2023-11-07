from statistics import mean


class SafetyChecker:
    def __init__(self):
        self.speed_window = []

    def is_speed_safe(self, current_speed):
        if len(self.speed_window) < 10:
            self.speed_window.append(current_speed)
            return True
        avg_speed = mean(self.speed_window)
        self.speed_window.pop(0)
        self.speed_window.append(current_speed)
        return abs(current_speed - avg_speed) > 20
