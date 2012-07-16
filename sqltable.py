"""
sqlite interface for CutFlowChallenge

author: Dan Guest <dguest@cern.ch>
"""
import sqlite3

def add_cutflow(connection, cut_dict): 
    """
    adds or updates one user's cutflow in sql 'connection'. 

    cut_dict should include keys 'user' + all cut names to change
    """
    all_users = connection.execute('select user from cutflow').fetchall()
    if not all_users or cut_dict['user'] not in [g for (g,) in all_users]: 
        connection .execute(
            'insert into cutflow (user) values (?)',(cut_dict['user'],))

    cuts = {k:v for k,v in cut_dict.items() if k != 'user'}
    for cut, value in cuts.items(): 
        connection .execute(
            'update cutflow set {} = :v where user = :s'.format(cut), 
            {'v': value, 's': cut_dict['user']})

def constructSqlTable(cuts, file_name = 'cutflow.db'): 
    """
    builds initial cutflow sqlite file
    """
    with sqlite3.connect(file_name) as con: 
        # some magic with quotes needed to get non-standard column names
        col_str = '(user,"' + '","'.join(cuts) + '")'
        con.execute(
            'create table if not exists cutflow {}'.format(col_str)) 

def writeCutsToSql(user_cut_flows, file_name): 

    with sqlite3.connect(file_name) as con: 

        for user, cutflow in user_cut_flows.iteritems(): 
            quote_cutflow = {'"{}"'.format(k):v for k,v in cutflow.items()}
            cut_dict = {'user':user}
            cut_dict.update(quote_cutflow)

            add_cutflow(con, cut_dict)

def readCutsFromSql(file_name):
    with sqlite3.connect(file_name) as con: 
        con.row_factory = sqlite3.Row
        user_cut_flows = {}
        sql_table = con.execute('select * from cutflow').fetchall()
        for line in sql_table: 
            user_cut_flows[line['user']] = {
                k: v for k, v in zip(line.keys(),line) if k != 'user'
                }

        return user_cut_flows
