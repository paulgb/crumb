
class OrderedSet(set):
    def __init__(self, initial):
        super(OrderedSet, self).__init__(self)
        self.elements = list()
        self.update(initial)

    def update(self, elements):
        for element in elements:
            self.add(element)

    def add(self, element):
        if element in self:
            return
        super(OrderedSet, self).add(element)
        self.elements.append(element)

    def __iter__(self):
        return iter(self.elements)

