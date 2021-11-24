class HistoryCache:
    cache = {}

    def __init__(self):
        self.cache = {}

    def add(self, id, timestamp, price):
        if not id in self.cache:
            self.cache[id] = []
        item = self.cache[id]
        if len(item) >= 2 and item[-1][1] == price and item[-2][1] == price:
            item.pop()

        item.append((timestamp, price))

    def get(self, item_id):
        return self.cache[item_id]
