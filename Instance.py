import pickle


class Instance:
    def __init__(self, test):
        self.test = test

    def set_test(self, val):
        self.test = val

    def get_test(self):
        return self.test


'''    
    def save(x, filename):
        file = open(filename, 'wb+')
        pickle.dump(x, file)
        file.close()

        # Files info update
        files = Instance.load('files.txt')
        files.append(filename)
        Instance.overwrite(files, 'files.txt')

    def overwrite(x, filename):
        file = open(filename, 'wb')
        pickle.dump(x, file)
        file.close()

    def load(filename):
        return pickle.load(open(filename, 'rb'))

    def show():
        return Instance.load('files.txt')
'''
