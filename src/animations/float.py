class FloatAnimation:
    def __init__(self, base_y):
        self.base_y = base_y
        self.offset = 0
        self.direction = 1

    def tick(self):
        """
        Calculates the next relative offset in the float sequence.
        Returns the computed absolute Y offset.
        """
        self.offset += self.direction
        if self.offset >= 5:
            self.direction = -1
        elif self.offset <= -5:
            self.direction = 1
        return self.base_y + self.offset
