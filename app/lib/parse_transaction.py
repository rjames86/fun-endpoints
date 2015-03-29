from utils import APP_STATIC
import os
from datetime import datetime
from operator import itemgetter

""" Parses a file that looks like this, delimited by tabs

    Monday, March 9, 2015
            Transaction Detail Report
            8/7/14 through 3/2/15


    Date        Payee   Memo    Category        Amount
    <bunch of weird crap>

    Unit #2

    8/7/14      Application Fee     Fees:Application Fee        -25.00
    ...
                        <more weird crap>
    Total Unit #2                       20.00
                        ========

"""


class TransactionParser(object):
    @classmethod
    def parse(cls, filename):
        f = TransactionParser._get_file(filename)
        f = f.readlines()
        trans_file = [i.strip().split('\t') for i in f]
        trans_file = [i for i in trans_file if len(i) == 7]

        # get the headers
        headers = trans_file[0]

        # get rid of non-transactional lines
        # the first 2 lines are the headers and a line break
        # the last line is the total
        transactions = map(lambda t: dict(zip(headers, t)), trans_file[2:-1])
        transactions = TransactionParser.cleanup(transactions)
        transactions = sorted(transactions, key=itemgetter('Date'), reverse=False)

        return dict(
            headers=headers,
            transactions=transactions,
            total=reduce(lambda j, k: j+k, map(lambda x: x['Amount'], transactions))
        )

    @classmethod
    def _get_file(cls, filename):
        return open(os.path.join(APP_STATIC, filename), 'r')

    @classmethod
    def cleanup(cls, transactions):
        for transaction in transactions:
            transaction['Amount'] = float(transaction['Amount'].replace(',', ''))
            month, day, year = transaction['Date'].split('/')
            month = '0' + month if len(month) == 1 else month
            day = '0' + day if len(day) == 1 else day
            year = '20' + year

            transaction['Date'] = datetime.strptime('/'.join([month, day, year]), '%m/%d/%Y')
        return transactions
