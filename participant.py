import time
import argparse
from helpers.connection import conn
from helpers.utils import print_rows
from helpers.utils import print_rows_to_file
from helpers.utils import is_valid_genre
from helpers.utils import print_command_to_file
from helpers.utils import make_csv
from helpers.utils import is_valid_pro

def display_info(search_type, search_value):
    # TODO
    try:
        cur=conn.cursor()
        cur.execute("SET search_path to s_2021034448")
        if search_type=='all':
            sql="""
            SELECT pp.p_id,
            pp.p_name,
            pp.major_work,
            STRING_AGG(o.ocu_name, ', ') AS profession
            FROM participant pp
            JOIN profession pf ON pf.p_id=pp.p_id
            JOIN occupation o ON o.ocu_id=pf.ocu_id
            GROUP BY 
                pp.p_id, pp.p_name, pp.major_work
            ORDER BY pp.p_id ASC
            """
            if search_value is not None:
                sql += " LIMIT %(limit)s"
                cur.execute(sql, {'limit': search_value})
            else:
                cur.execute(sql)

        elif search_type=='id':
            sql="""
            SELECT pp.p_id,
                pp.p_name,
                pp.major_work,
                STRING_AGG(o.ocu_name, ', ') AS profession
            FROM participant pp
            JOIN profession pf ON pf.p_id=pp.p_id
            JOIN occupation o ON o.ocu_id = pf.ocu_id
            WHERE pp.p_id=%(search_value)s
            GROUP BY 
                pp.p_id, pp.p_name, pp.major_work
            ORDER BY pp.p_id ASC
            """
            cur.execute(sql,{'search_value':search_value})
        
        elif search_type=='name':
            sql="""
            SELECT pp.p_id,
            pp.p_name,
            pp.major_work,
            STRING_AGG(o.ocu_name, ', ') AS profession
            FROM participant pp
            JOIN profession pf ON pf.p_id=pp.p_id
            JOIN occupation o ON o.ocu_id=pf.ocu_id
            WHERE pp.p_name ILIKE %(search_value)s
            GROUP BY 
                pp.p_id, pp.p_name, pp.major_work
            ORDER BY pp.p_id ASC
            """
            cur.execute(sql,{'search_value':search_value})

        elif search_type == 'profession':
            # 문자열로 변환 후 와일드카드 추가하여 전달
            search_value_with_wildcard = f"%{search_value}%"
            sql = """
            SELECT pp.p_id,
            pp.p_name,
            pp.major_work,
            STRING_AGG(o.ocu_name, ', ') AS profession
            FROM participant pp
            JOIN profession pf ON pf.p_id=pp.p_id
            JOIN occupation o ON o.ocu_id=pf.ocu_id
            WHERE pp.p_id IN (
                SELECT pf.p_id
                FROM profession pf
                JOIN occupation o ON o.ocu_id = pf.ocu_id
                WHERE (o.ocu_name) ILIKE %(search_value_with_wildcard)s
            )
            GROUP BY 
                pp.p_id, pp.p_name, pp.major_work
            ORDER BY pp.p_id ASC
            """
            cur.execute(sql, {'search_value_with_wildcard': search_value_with_wildcard})

        rows = cur.fetchall()

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
    if args.command == "info":
        if args.all:
            display_info('all', args.all)
        elif args.id:
            display_info('id',args.id)
        elif args.name:
            name = ' '.join(args.name) if isinstance(args.name, list) else args.name #공백처리하려고
            display_info('name', name)
        elif args.profession:
            profession = ' '.join(args.profession).lower() if isinstance(args.profession, list) else args.profession #공백처리하려고
            if not is_valid_pro(profession):
                print(f"Error: {args.profession} is not a valid profession.")
                return
            else:
                #profession = ' '.join(args.profession) if isinstance(args.profession, list) else args.profession #공백처리하려고
                display_info('profession', profession)
    
    else :
        print("Error: query command error.")
    

    pass


if __name__ == "__main__":
    #
    #print_command_to_file()
    #
    start = time.time()
    parser = argparse.ArgumentParser(description = """
    how to use
    1. info [-a(all) / -i(p_id) / -n(p_name) / -pr(profession name)] [value]
    2. ...
    3. ...
    """, formatter_class=argparse.RawTextHelpFormatter)
    subparsers = parser.add_subparsers(dest='command', 
        help='select one of query types [info, ...]')

    #info
    parser_info = subparsers.add_parser('info', help='Display target participant info')
    group_info = parser_info.add_mutually_exclusive_group(required=True)
    # TODO
    group_info.add_argument('-a',dest='all',type=int,help='Show all participants')
    group_info.add_argument('-i',dest='id',type=int,help='Search by participants by id')
    group_info.add_argument('-n',dest='name',type=str, nargs='+', help='Search participants by name')
    group_info.add_argument('-pr',dest='profession',type=str,nargs='+',help='Search participants by profession')
    
    

    args = parser.parse_args()
    main(args)
    print("Running Time: ", end="")
    print(time.time() - start)
