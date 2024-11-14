import time
import argparse
from helpers.connection import conn
from helpers.utils import print_rows
from helpers.utils import print_rows_to_file
from helpers.utils import print_command_to_file
from helpers.utils import make_csv

def display_info(search_type, search_value, search_role):
    # TODO
    try:
        cur=conn.cursor()
        cur.execute("SET search_path to s_2021034448")
        if search_type == 'all':
            sql = """
            SELECT p.p_id,
                    pp.p_name, 
                    p.role ,
                    m.m_name,
                    STRING_AGG(p.casting, ', ') AS casting
            FROM participate p
            LEFT JOIN participant pp ON pp.p_id=p.p_id
            LEFT JOIN movie m ON m.m_id = p.m_id
            WHERE p.role ILIKE %(search_role)s
            GROUP BY p.p_id, pp.p_name, p.role, m.m_name
            ORDER BY p.p_id ASC
            """

            if search_value is not None:
                sql += " LIMIT %(limit)s"
                cur.execute(sql, {'search_role': search_role, 'limit': search_value})
            else:
                cur.execute(sql, {'search_role': search_role})
        
        elif search_type=='id':
            sql="""
            SELECT pp.p_id,
                pp.p_name,
                p.role, 
                STRING_AGG(p.casting, ', ') AS casting
            FROM participant pp
            JOIN participate p ON pp.p_id = p.p_id
            JOIN movie m ON m.m_id=p.m_id
            WHERE m.m_id = %(search_value)s AND p.role ILIKE %(search_role)s
            GROUP BY 
                pp.p_id, pp.p_name, p.role
            """

            cur.execute(sql,{'search_value':search_value,'search_role':search_role})
        
        rows=cur.fetchall()
        if rows:
            column_names=[desc[0] for desc in cur.description]
            print(f"Total rows: {len(rows)}")
            print_rows(column_names,rows)
        else:
            print("No results found")
    
    except Exception as err:
        print(f"Error: {err}")

    finally:
        cur.close()

def main(args):
    # TODO
    if args.command=="info":
        if args.all:
            display_info('all',args.all,args.role)
        elif args.id:
            display_info('id',args.id, args.role)

if __name__ == "__main__":
    #
    #print_command_to_file()
    #
    start = time.time()
    parser = argparse.ArgumentParser(description = """
    how to use
    1. info [-a(all) / -o(one)] value role
    2. ...
    3. ...
    """, formatter_class=argparse.RawTextHelpFormatter)
    subparsers = parser.add_subparsers(dest='command', 
        help='select one of query types [info, ...]')

    #info
    parser_info = subparsers.add_parser('info', help='Display participant associated to genre info')
    group_info = parser_info.add_mutually_exclusive_group(required=True)
    # TODO
    group_info.add_argument('-a',dest='all',type=int, help='Show all paricipants on the role')
    group_info.add_argument('-i',dest='id',type=int, help='Search by paricipants by movie_id')
    parser_info.add_argument('role',type=str,help='Role of the participant')

    args = parser.parse_args()
    main(args)
    print("Running Time: ", end="")
    print(time.time() - start)
