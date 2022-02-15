from murmur import murmur3

BIP37_CONSTANT = 0xfba4c795

class BloomFilter:
    def __init__(self, size, function_count, tweak):
        self.size = size
        self.bit_field = [0] * (size * 8)
        self.function_count = function_count
        self.tweak = tweak

    def add(self, data):
        for i in range(self.function_count):
            seed = i * BIP37_CONSTANT + self.tweak
            h = murmur3(data, seed)
            bit = h % (self.size * 8)
            self.bit_field[bit] = 1

