class FollowAnimation:
    def __init__(self, speed=0.08):
        self.speed = speed
        # Offsets to align Boo's center with the mouse cursor pointer (Boo size is 160x200)
        self.offset_x = 80
        self.offset_y = 100

    def calculate_next_position(self, current_wx, current_wy, target_mx, target_my):
        """
        Calculates the next step coordinates towards the mouse position.
        Uses a smooth LERP (Linear Interpolation) factor.
        """
        dest_x = target_mx - self.offset_x
        dest_y = target_my - self.offset_y

        new_x = int(current_wx + (dest_x - current_wx) * self.speed)
        new_y = int(current_wy + (dest_y - current_wy) * self.speed)

        return new_x, new_y
