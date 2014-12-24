import pandas as pd
import re
import datetime

__author__ = 'Sam Hall'

################################################################################

class Data(object):
    def __init__(self):
        self.data = {
            'Code' : [],
            'Name' : [],
            'Details' : [],
            'Cost' : [],
        }
        self.reset_current()
        self.reg = re.compile('^(\d+)\s*-\s*(.*)$')
        return

    def reset_current(self):
        self.current = {'Code':False, 'Name':False, 'Details':'', 'Cost':False}
        return

    def row_to_data(self):
        if all(self.current):
            if len(self.current['Details']) < 200:
                for key in self.data.keys():
                    self.data[key].append(self.current[key])
        self.reset_current()
        return

    def add_row(self, row):
        data = [x for x in row if x==x]
        if not len(data):
            return
        search = self.reg.search(data[0])
        if search is not None:
            self.row_to_data()
            self.current['Code'] = search.groups()[0]
            self.current['Name'] = search.groups()[1]
            self.current['Cost'] = data[-1]
            self.current['Details'] = '{} '.format(data[-2])
        else:
            #data = [x for x in data if not x.lower().startswith('api')]
            try:
                self.current['Details'] += ' '.join(data) + ' '
            except TypeError:
                pass
        return

    def save(self, filename):
        pddata = pd.DataFrame.from_dict(self.data)
        pddata.to_excel(filename)
        return

################################################################################


def convert(*args, **kwargs):
    """
    Convert totally unhelpful spreadsheet of specific format into useful one
    """
    output = 'output.xls'
    if kwargs.has_key('output'):
        output = kwargs['output']
    elif len(kwargs):
        print 'Unknown option(s): {}'.format(kwargs.keys())
    data = Data()
    for arg in args:
        ex = pd.io.excel.read_excel(arg)
        for ex_row in ex.values:
            data.add_row(ex_row)
    data.save(output)


if __name__ == "__main__":
    convert('Book1.xlsx')


