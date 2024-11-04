import time
import argparse
from helpers.connection import conn
from helpers.utils import print_rows
from helpers.utils import print_rows_to_file
from helpers.utils import is_valid_genre
from helpers.utils import print_command_to_file
from helpers.utils import make_csv


def display_info(search_type, search_value):
    try:
        cur = conn.cursor()
        cur.execute("SET search_path to s_2021034448")
        if search_type == 'id' :
            sql = """
            SELECT 
            cu.c_id, 
            cu.c_name, 
            cu.email, 
            cu.gender, 
            cu.phone, 
            STRING_AGG(DISTINCT gr.gr_name, ', ') AS preferred_genres
            FROM customer cu 
            JOIN prefer p ON cu.c_id = p.c_id 
            JOIN genre gr ON p.gr_id = gr.gr_id
            WHERE cu.c_id = %(id)s
            GROUP BY cu.c_id, cu.c_name, cu.email, cu.gender, cu.phone
            ORDER BY cu.c_id ASC;
            """
            cur.execute(sql, {"id": search_value})

        elif search_type == 'name' :
            sql = """
            SELECT
            cu.c_id, 
            cu.c_name, 
            cu.email, 
            cu.gender, 
            cu.phone, 
            STRING_AGG(DISTINCT gr.gr_name, ', ') AS preferred_genres
            FROM customer cu 
            JOIN prefer p ON cu.c_id = p.c_id 
            JOIN genre gr ON p.gr_id = gr.gr_id
            WHERE cu.c_name ILIKE %(name)s
            GROUP BY cu.c_id, cu.c_name, cu.email, cu.gender, cu.phone
            ORDER BY cu.c_id ASC;
            """
            cur.execute(sql, {"name": search_value})

        elif search_type == 'genre' :
            sql = """
            SELECT 
                cu.c_id, 
                cu.c_name, 
                cu.email, 
                cu.gender, 
                cu.phone, 
                STRING_AGG(DISTINCT gr.gr_name, ', ') AS preferred_genres
            FROM customer cu JOIN prefer p ON cu.c_id = p.c_id JOIN genre gr ON p.gr_id = gr.gr_id
            WHERE cu.c_id IN (
                    SELECT cu.c_id
                    FROM customer cu
                    JOIN prefer p ON cu.c_id = p.c_id
                    JOIN genre gr ON p.gr_id = gr.gr_id
                    WHERE gr.gr_name = %(genre)s
                    )
            GROUP BY cu.c_id, cu.c_name, cu.email, cu.gender, cu.phone
            ORDER BY cu.c_id ASC;
            """
            cur.execute(sql, {"genre": search_value})

        elif search_type == 'all' :
            sql = """
            SELECT
            cu.c_id, 
            cu.c_name, 
            cu.email, 
            cu.gender, 
            cu.phone, 
            STRING_AGG(DISTINCT gr.gr_name, ', ') AS preferred_genres
            FROM customer cu 
            JOIN prefer p ON cu.c_id = p.c_id 
            JOIN genre gr ON p.gr_id = gr.gr_id
            GROUP BY cu.c_id, cu.c_name, cu.email, cu.gender, cu.phone
            ORDER BY cu.c_id ASC
            LIMIT %(all)s;
            """
            cur.execute(sql, {"all": search_value})

        else :
            print("can't search by", search_type)
            return False

        rows = cur.fetchall()
        if not rows:
            print("No results found.")
            return False
        else:
            column_names = [desc[0] for desc in cur.description]
            #
            #print_rows_to_file(column_names, rows)
            #make_csv(column_names, rows)
            #
            print_rows(column_names, rows)
            return True

    except Exception as err:
        print(err)
    
    finally:
        cur.close()
    # end
    pass

def insert_customer(id, name, email, pwd, gender, phone, genres):
    if not id:
        print("Error: c_id 값이 필요합니다.")
        return
    try:
        cur = conn.cursor()
        cur.execute("SET search_path to s_2021034448") #스키마 지정

        # customer 테이블에 데이터 삽입
        sql_insert_customer = """
        INSERT INTO customer (c_id, c_name, email, pwd, gender, phone)
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        cur.execute(sql_insert_customer, (id, name, email, pwd, gender, phone))

        # 장르가 있으면 선호 장르 삽입
        if genres:
            for genre in genres:
                cur.execute("SELECT gr_id FROM genre WHERE gr_name = %s", (genre,))
                genre_row = cur.fetchone() # 해당 장르의 ID를 가지고 오며 ID가 존재하면 gr_id에 삽입.
                if genre_row:
                    gr_id = genre_row[0]
                    sql_insert_prefer = """
                    INSERT INTO prefer (c_id, gr_id)
                    VALUES (%s, %s);
                    """
                    cur.execute(sql_insert_prefer, (id, gr_id))
                else:
                    print(f"Warning: Genre '{genre}' does not exist in the database.")
        conn.commit()
        print("Customer inserted successfully.")

        # 삽입된 데이터 출력
        display_info('id', id)
        
    except Exception as err:
        print(f"Error inserting customer: {err}")
        conn.rollback()
    finally:
        cur.close()


def update_customer(id, target, value) :
    # TODO
    if not id: 
        print("Error: c_id값이 존재하지 않습니다.")
        return
    try:
        cur=conn.cursor()
        cur.execute("SET search_path to s_2021034448")
       #print("Before update")
        display_info('id',id)

        if target=="email":
            sql="UPDATE customer SET email= %s WHERE c_id=%s"
            cur.execute(sql,(value,id))
        elif target=="pwd":
            sql="UPDATE customer SET pwd=%s WHERE c_id=%s"
            cur.execute(sql,(value,id))
        elif target=="phone":
            sql="UPDATE customer SET phone=%s WHERE c_id=%s"
            cur.execute(sql,(value,id))
        elif target=="genres":
            #기존 장르 아예 삭제 후 새로 추가-> 복수개 일수도 있어서?
            cur.execute("DELETE FROM prefer WHERE c_id=%s",(id))
            genre_list=value.split(" ")#공백으로 split
            for genre in genre_list:
                cur.execute("SELECT gr_id FROM genre WHERE gr_name=%s",(genre,))
                genre_row=cur.fetchone()
                if genre_row:
                    gr_id=genre_row[0]
                    sql_insert_prefer="INSERT INTO prefer (c_id,gr_id) VALUES (%s,%s)"
                    cur.execute(sql_insert_prefer,(id,gr_id))
                else: 
                    print(f"Warning: Genre '{genre} does not exist in the database")
        else:
            print(f"Error: '{target}' is not a valid field")
            return
        
        conn.commit()
        display_info('id',id)


    except Exception as err:
        print(f"Error update customer:{err}")
        conn.rollback()
    finally:
        cur.close()

def delete_customer(id) :
    if not id:
        print("Error: c_id값이 존재하지 않습니다.")
        return
    try:
        cur=conn.cursor()
        cur.execute("SET search_path to s_2021034448")

        # prefer 테이블에서 관련 데이터 삭제
        sql_delete_prefer = """
        DELETE FROM prefer 
        WHERE c_id = %s
        """
        cur.execute(sql_delete_prefer, (id,))
        
        sql_delete_customer="""
        DELETE FROM customer 
        WHERE c_id=%s
        """
        cur.execute(sql_delete_customer,(id,))
        conn.commit()
        display_info('id',id)

    except Exception as err:
        print(f"Error delete customer: {err}")
        conn.rollback()
    finally:
        cur.close()

    # TODO

def main(args):
    if args.command == "info":
        if args.id:
            display_info('id',args.id)
        elif args.name:
            display_info('name', args.name)
        elif args.genre:
            if not is_valid_genre(args.genre):
                print(f"Error: '{args.genre}' is not a valid genre.")
            else:
                display_info('genre', args.genre)
        elif args.all:
            display_info('all', args.all)

    elif args.command == "insert":
        insert_customer(args.id, args.name, 
            args.email, args.pwd, args.gender, args.phone, args.genres)

    elif args.command == "update":
        # TODO
        value = ' '.join(args.value)
        update_customer(args.id,args.target,value)

    elif args.command == "delete":
        # TODO
        delete_customer(args.id)
    else :
        print("Error: query command error.")


if __name__ == "__main__":
    
    print_command_to_file()
    
    start = time.time()
    
    parser = argparse.ArgumentParser(description = """
    how to use
    1. info [-i(c_id) / -n(c_name) / -g(genre) / -a (all)] [value]
    2. insert c_id, c_name, email, pwd, gender, phone -g (genre1, genre2, genre3)
    3. update -i [c_id] [-m(e-mail) / -p(password) / -ph(phone)] [new_value]
    4. delete -i [c_id]
    """, formatter_class=argparse.RawTextHelpFormatter)
    subparsers = parser.add_subparsers(dest='command', 
        help='select one of query types [info, insert, update, delete]')

    #[1-1]info
    parser_info = subparsers.add_parser('info', help='Display target customers info')
    group_info = parser_info.add_mutually_exclusive_group(required=True)
    group_info.add_argument('-i', dest='id', type=int, help='c_id of customer entity')
    group_info.add_argument('-n', dest='name', type=str, help='c_name of customer entity')
    group_info.add_argument('-g', dest='genre', type=str, help='genre which customer prefer')
    group_info.add_argument('-a', dest='all', type=str, help='display rows with top [value]')

    #[1-2]insert : 파싱해서 각자 attribute에 넣어주는 거임
    parser_insert = subparsers.add_parser('insert', help='Insert new customer data')
    #parser_insert.add_argument('-i', dest='id', type=int, required=True, help='Customer ID')
    #parser_insert.add_argument('-n', dest='name', type=str, required=True, help='Customer name')
    #parser_insert.add_argument('-e', dest='email', type=str, required=True, help='Customer email')
    #parser_insert.add_argument('-p', dest='pwd', type=str, required=True, help='Customer password')
    #parser_insert.add_argument('-g', dest='gender', type=str, required=True, choices=['M', 'F'], help='Customer gender')
    #parser_insert.add_argument('-ph', dest='phone', type=str, required=True, help='Customer phone number')
    #parser_insert.add_argument('-genres', dest='genres', type=str, required=True, help='Preferred genres, separated by spaces')
    parser_insert.add_argument('id', type=int, help='Customer ID')
    parser_insert.add_argument('name', type=str, help='Customer name')
    parser_insert.add_argument('email', type=str, help='Customer email')
    parser_insert.add_argument('pwd', type=str, help='Customer password')
    parser_insert.add_argument('gender', type=str, choices=['M', 'F'], help='Customer gender')
    parser_insert.add_argument('phone', type=str, help='Customer phone number')
    parser_insert.add_argument('genres', type=str, help='Preferred genres, separated by spaces')
    parser_insert.add_argument('-g', dest='genres', nargs='+', help='Preferred genres, separated by spaces')
    # TODO
    
    #[1-3]update
    parser_update = subparsers.add_parser('update', help='Update one of customer data')
    parser_update.add_argument('-i', dest='id', type=int, required=True, help='Customer ID')
    parser_update.add_argument('-m', dest='target', action='store_const', const='email', help='Update email')
    parser_update.add_argument('-p', dest='target', action='store_const', const='pwd', help='Update password')
    parser_update.add_argument('-ph', dest='target', action='store_const', const='phone', help='Update phone')
    parser_update.add_argument('-gs', dest='target', action='store_const', const='genres', help='Update genres')
    parser_update.add_argument('value', nargs='+', help='New field value')  # nargs='+'를 사용하여 여러 단어를 받음
    #parser_update.add_argument('value', type=str, help='New field value')  # 위치 인자로 설정
    # TODO

    #[1-4]delete
    parser_delete = subparsers.add_parser('delete',help='Delete customer data with associated data')
    parser_delete.add_argument('-i',dest='id',type=int,required=True,help='Customer ID')
    # TODO
    
    args = parser.parse_args()
    main(args)
    print("Running Time: ", end="")
    print(time.time() - start)
