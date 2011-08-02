import dogmax

class ProbeDogmaItem(dogmax.BaseDogmaItem):
    __guid__ = 'dogmax.ProbeDogmaItem'

    def Load(self, item, instanceRow):
        super(ProbeDogmaItem, self).Load(item, instanceRow)
        self.ownerID = item.ownerID




