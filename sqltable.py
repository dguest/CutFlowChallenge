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
    if cut_dict['user'] not in [g for (g,) in all_users]: 
        connection .execute(
            'insert into cutflow (user) values (:user)',cut_dict)

    cuts = {k:v for k,v in cut_dict.items() if k != 'user'}
    for cut, value in cuts.items(): 
        connection .execute(
            'update cutflow set {} = :v where user = :s'.format(cut), 
            {'v': value, 's': cut_dict['user']})

def constructSqlTable(cuts, file_name = 'cutflow.db'): 
    """
    builds initial cutflow sqlite file
    """
    name_dict = {'cut' + str(i): n for i, n in enumerate(cuts)}
    with sqlite3.connect(file_name) as con: 
        columns = ['user'] + sorted(name_dict.keys())
        col_str = '(' + ','.join(columns) + ')'
        print col_str
        con.execute(
            'create table if not exists cutflow {}'.format(col_str)) 
        con.execute('create table cut_names (number, name)')
        for number, name in name_dict.iteritems(): 
            con.execute('insert into cut_names values (?,?)',(number,name))

def writeCutsToSql(user_cut_flows, file_name): 

    with sqlite3.connect(file_name) as con: 

        for user, cutflow in user_cut_flows.iteritems(): 
            
            cut_dict = {'user':user}.update(cutflow)
            add_cutflow(con, cut_dict)

def readCutsFromSql(file_name):
    with sqlite3.connect(file_name) as con: 
        user_cut_flows = {}
        sql_table = connection.execute('select * from cutflow').fetchall()
        for line in sql_table: 
            user_cut_flows[line['user']] = {
                k: v for k, v in line.iteritems() if k != 'user'
                }

        return user_cut_flows
