

class repository(object):

    def since(self, artid):
        '''
        '''

        if artid is None:
            artid = self.first()
