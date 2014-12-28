import pandas as pd
import re
import datetime

__author__ = 'Sam Hall'

################################################################################

class Data(object):
    def __init__(self):
        self.columns = ['Code', 'Name', 'Cost', 'Measure', 'Details']
        self.data = {x:[] for x in self.columns}
        self.reset_current()
        self.reg = re.compile('^(\d+)\s*-\s*(.*)$')
        self.reg2 = re.compile('^length|quantity|area|volume')
        return

    def reset_current(self):
        self.current = {
            'Code':False, 'Name':False, 'Details':'', 'Cost':False, 'Measure':'-'
        }
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
            try:
                measures = []
                for i, datum in enumerate(data):
                    search = self.reg2.search(datum.lower())
                    if search is not None:
                        measures.append(i)
                        measures.append(i+1)
                        break
                if len(measures):
                    self.current['Measure'] = data.pop(measures[1])
                    data.pop(measures[0])
                    #print data
                    #print self.current['Measure']
                self.current['Details'] += ' '.join(data) + ' '
            except:
                pass
        return

    def save(self, filename):
        pddata = pd.DataFrame.from_dict(self.data)#, columns=self.columns)
        pddata = pddata[self.columns]
        pddata.to_excel(filename)
        return

################################################################################


def convert(*args, **kwargs):
    """
    Convert totally unhelpful spreadsheet of specific format into useful one
    """
    opts = {'output' : 'output.xls', 'sheet' : 0}
    for k, i in kwargs.iteritems():
        if opts.has_key(k):
            opts[k] = i
        else:
            print 'Unknown option: {}'.format(k)
    output = opts['output']
    sheet = opts['sheet']
    data = Data()
    for arg in args:
        print 'Input file:  {:50}\tsheet: {}'.format(arg, sheet)
        ex = pd.io.excel.read_excel(arg, sheetname=sheet)
        for ex_row in ex.values:
            data.add_row(ex_row)
    data.save(output)
    print 'Output file: {}'.format(output)
    return


if __name__ == "__main__":
    convert('Book2.xls')
    convert('Book2.xls', output='out2.xls', sheet=1)


