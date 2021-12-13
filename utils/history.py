"""
Class storing the history of all items in a map in RAM.
In production one would use a database in addition to this class.
"""
class History:
    history = {}

    def __init__(self):
        self.history = {}

    def add(self, id, timestamp, price):
        if not id in self.history:
            self.history[id] = []
        item = self.history[id]

        # If the last two history-entries contain the same price as the new one, delete the last one.
        # This can safely be done, as we don't loose any information, if the price between the new one and the second to last one hasn't changed.
        # We basically only store the beginning and the end of a segment of unchanging price.
        # This keeps the history from growing too large, while still containing all the information.
        if len(item) >= 2 and item[-1][1] == price and item[-2][1] == price:
            item.pop()

        item.append((timestamp, price))

    def get(self, item_id):
        return self.history[item_id]

    def contains(self, item_id):
        return item_id in self.history