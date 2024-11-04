import datetime
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
        
        if search_type == 'all':
            sql = """
            SELECT 
                m.m_id, 
                m.m_name, 
                m.m_type, 
                m.start_year, 
                m.end_year, 
                m.is_adult, 
                m.runtimes, 
                m.m_rating AS imdb_rating, 
                COALESCE(
                    (m.m_rating * m.votes + COALESCE(SUM(ct.rating), 0)) / 
                    (m.votes + COUNT(ct.rating)), 
                    m.m_rating
                ) AS final_rating,
                STRING_AGG(DISTINCT g.gr_name, ', ') AS genres
            FROM 
                movie m
            LEFT JOIN 
                classify c ON m.m_id = c.m_id
            LEFT JOIN 
                genre g ON c.gr_id = g.gr_id
            LEFT JOIN 
                comment_to ct ON m.m_id = ct.m_id
            GROUP BY 
                m.m_id
            ORDER BY 
                m.m_id ASC
            """
            # LIMIT 값이 None이 아닌 경우에만 추가
            if search_value is not None:
                sql += " LIMIT %s"
                cur.execute(sql, (search_value,))
            else:
                cur.execute(sql)
    
        elif search_type == 'id':
            sql = """
                SELECT 
                m.m_id, 
                m.m_name, 
                m.m_type, 
                m.start_year, 
                m.end_year, 
                m.is_adult, 
                m.runtimes, 
                m.m_rating AS imdb_rating, 
                COALESCE(
                    (m.m_rating * m.votes + COALESCE(SUM(ct.rating), 0)) / 
                    (m.votes + COUNT(ct.rating)), 
                    m.m_rating
                ) AS final_rating,
                STRING_AGG(DISTINCT g.gr_name, ', ') AS genres
            FROM 
                movie m
            LEFT JOIN 
                classify c ON m.m_id = c.m_id
            LEFT JOIN 
                genre g ON c.gr_id = g.gr_id
            LEFT JOIN 
                comment_to ct ON m.m_id = ct.m_id
            WHERE m.m_id=%s
            GROUP BY 
                m.m_id
            ORDER BY 
                m.m_id ASC
            """
            cur.execute(sql, (search_value,))

        elif search_type == 'name':
            #sql = "SELECT * FROM movie WHERE m_name ILIKE %s;"
            sql = """
                SELECT 
                m.m_id, 
                m.m_name, 
                m.m_type, 
                m.start_year, 
                m.end_year, 
                m.is_adult, 
                m.runtimes, 
                m.m_rating AS imdb_rating, 
                COALESCE(
                    (m.m_rating * m.votes + COALESCE(SUM(ct.rating), 0)) / 
                    (m.votes + COUNT(ct.rating)), 
                    m.m_rating
                ) AS final_rating,
                STRING_AGG(DISTINCT g.gr_name, ', ') AS genres
            FROM 
                movie m
            LEFT JOIN 
                classify c ON m.m_id = c.m_id
            LEFT JOIN 
                genre g ON c.gr_id = g.gr_id
            LEFT JOIN 
                comment_to ct ON m.m_id = ct.m_id
            WHERE m.m_name ILIKE %s
            GROUP BY 
                m.m_id
            ORDER BY 
                m.m_id ASC
            """
            cur.execute(sql, (f"%{search_value}%",))

        elif search_type == 'genre':
            genres = search_value.split(',')
            genre_conditions = " AND ".join(
                [f"'{genre.strip()}' = ANY(ARRAY_AGG(g.gr_name))" for genre in genres]
            )

            sql = f"""
                SELECT 
                    m.m_id, 
                    m.m_name, 
                    m.m_type, 
                    m.start_year, 
                    m.end_year, 
                    m.is_adult, 
                    m.runtimes, 
                    m.m_rating AS imdb_rating, 
                    COALESCE(
                        (m.m_rating * m.votes + COALESCE(SUM(ct.rating), 0)) / 
                        (m.votes + COUNT(ct.rating)), 
                        m.m_rating
                    ) AS final_rating,
                    STRING_AGG(DISTINCT g.gr_name, ', ') AS genres
                FROM 
                    movie m
                LEFT JOIN 
                    classify c ON m.m_id = c.m_id
                LEFT JOIN 
                    genre g ON c.gr_id = g.gr_id
                LEFT JOIN 
                    comment_to ct ON m.m_id = ct.m_id
                GROUP BY 
                    m.m_id
                HAVING 
                    {genre_conditions}
                ORDER BY 
                    m.m_id ASC
            """
            cur.execute(sql)

        elif search_type == 'start_year':
            #sql = "SELECT * FROM movie WHERE start_year >= %s;"
            start_date = datetime.date(int(search_value), 1, 1)
            sql="""
                SELECT 
                    m.m_id, 
                    m.m_name, 
                    m.m_type, 
                    m.start_year, 
                    m.end_year, 
                    m.is_adult, 
                    m.runtimes, 
                    m.m_rating AS imdb_rating, 
                    COALESCE(
                        (m.m_rating * m.votes + COALESCE(SUM(ct.rating), 0)) / 
                        (m.votes + COUNT(ct.rating)), 
                        m.m_rating
                    ) AS final_rating,
                    STRING_AGG(DISTINCT g.gr_name, ', ') AS genres
                FROM 
                    movie m
                LEFT JOIN 
                    classify c ON m.m_id = c.m_id
                LEFT JOIN 
                    genre g ON c.gr_id = g.gr_id
                LEFT JOIN 
                    comment_to ct ON m.m_id = ct.m_id
                WHERE start_year >= %s
                GROUP BY 
                    m.m_id
                ORDER BY 
                    m.m_id ASC
                """
            cur.execute(sql, (start_date,))

        elif search_type == 'end_year':
            end_date = datetime.date(int(search_value), 1, 1)
            sql="""
                SELECT 
                    m.m_id, 
                    m.m_name, 
                    m.m_type, 
                    m.start_year, 
                    m.end_year, 
                    m.is_adult, 
                    m.runtimes, 
                    m.m_rating AS imdb_rating, 
                    COALESCE(
                        (m.m_rating * m.votes + COALESCE(SUM(ct.rating), 0)) / 
                        (m.votes + COUNT(ct.rating)), 
                        m.m_rating
                    ) AS final_rating,
                    STRING_AGG(DISTINCT g.gr_name, ', ') AS genres
                FROM 
                    movie m
                LEFT JOIN 
                    classify c ON m.m_id = c.m_id
                LEFT JOIN 
                    genre g ON c.gr_id = g.gr_id
                LEFT JOIN 
                    comment_to ct ON m.m_id = ct.m_id
                WHERE end_year >= %s
                GROUP BY 
                    m.m_id
                ORDER BY 
                    m.m_id ASC
                """
            cur.execute(sql, (end_date,))

        elif search_type == 'is_adult':
            #sql = "SELECT * FROM movie WHERE is_adult = %s;"
            sql="""
                SELECT 
                    m.m_id, 
                    m.m_name, 
                    m.m_type, 
                    m.start_year, 
                    m.end_year, 
                    m.is_adult, 
                    m.runtimes, 
                    m.m_rating AS imdb_rating, 
                    COALESCE(
                        (m.m_rating * m.votes + COALESCE(SUM(ct.rating), 0)) / 
                        (m.votes + COUNT(ct.rating)), 
                        m.m_rating
                    ) AS final_rating,
                    STRING_AGG(DISTINCT g.gr_name, ', ') AS genres
                FROM 
                    movie m
                LEFT JOIN 
                    classify c ON m.m_id = c.m_id
                LEFT JOIN 
                    genre g ON c.gr_id = g.gr_id
                LEFT JOIN 
                    comment_to ct ON m.m_id = ct.m_id
                WHERE m.is_adult=%s
                GROUP BY 
                    m.m_id
                ORDER BY 
                    m.m_id ASC
                """
            cur.execute(sql, (search_value,))

        elif search_type == 'rating':
            #sql = "SELECT * FROM movie WHERE m_rating >= %s;"
            sql="""
                SELECT 
                    m.m_id, 
                    m.m_name, 
                    m.m_type, 
                    m.start_year, 
                    m.end_year, 
                    m.is_adult, 
                    m.runtimes, 
                    m.m_rating AS imdb_rating, 
                    COALESCE(
                        (m.m_rating * m.votes + COALESCE(SUM(ct.rating), 0)) / 
                        (m.votes + COUNT(ct.rating)), 
                        m.m_rating
                    ) AS final_rating,
                    STRING_AGG(DISTINCT g.gr_name, ', ') AS genres
                FROM 
                    movie m
                LEFT JOIN 
                    classify c ON m.m_id = c.m_id
                LEFT JOIN 
                    genre g ON c.gr_id = g.gr_id
                LEFT JOIN 
                    comment_to ct ON m.m_id = ct.m_id
                WHERE m.m_rating>=%s
                GROUP BY 
                    m.m_id
                ORDER BY 
                    m.m_id ASC
                """
            cur.execute(sql, (search_value,))

        rows = cur.fetchall()
        
        if not rows:
            print("No results found")
        else:
            column_names = [desc[0] for desc in cur.description]
            print(f"Total rows: {len(rows)}")  # 결과의 총 개수 출력
            print_rows(column_names, rows)
    
    except Exception as err:
        print(f"Error: {err}")

    finally:
        cur.close()

        
        
def main(args):
    # TODO
    if args.command=="info":
        if args.all:
            display_info('all',args.all)
        elif args.id:
            display_info('id',args.id)
        elif args.name:
            # nargs='+'로 받은 name 인자를 공백으로 이어 붙여 하나의 문자열로 변환
            name = ' '.join(args.name) if isinstance(args.name, list) else args.name
            display_info('name', name)
        elif args.genre:
            display_info('genre', args.genre)
        elif args.start_year:
            display_info('start_year', args.start_year)
        elif args.end_year:
            display_info('end_year', args.end_year)
        elif args.is_adult:
            # 문자열로 받은 값을 bool로 변환
            is_adult = args.is_adult.lower() == 'true'
            display_info('is_adult', is_adult)
        elif args.rating:
            display_info('rating', args.rating)


if __name__ == "__main__":
    #
    #print_command_to_file()
    #
    start = time.time()
    parser = argparse.ArgumentParser(description = """
    how to use
    1-1. info [-a(all) / -i(m_id) / -n(m_name) / -g(genre)] [value]
    1-2. info [-sy(start_year) / -ey(end_year) / -ad(is_adult) / -r(rating)] [value]
    2. ...
    3. ...
    """, formatter_class=argparse.RawTextHelpFormatter)
    subparsers = parser.add_subparsers(dest='command', 
        help='select one of query types [info, ...]')

    #info
    parser_info = subparsers.add_parser('info', help='Display target movie info')
    group_info = parser_info.add_mutually_exclusive_group(required=True)
    
    group_info.add_argument('-a', dest='all', type=int, help='Show all movies')
    group_info.add_argument('-i', dest='id', type=int, help='Search by movie ID')
    #group_info.add_argument('-n', dest='name', type=str, help='Search by movie name')
    group_info.add_argument('-n', dest='name', type=str, nargs='+', help='Search by movie name')
    group_info.add_argument('-g', dest='genre', type=str, help='Search by genre')
    group_info.add_argument('-sy', dest='start_year', type=int, help='Search by start year')
    group_info.add_argument('-ey', dest='end_year', type=int, help='Search by end year')
    group_info.add_argument('-ad', dest='is_adult', type=str, help='Search by adult content')
    group_info.add_argument('-r', dest='rating', type=float, help='Search by rating')
    
    # TODO


    
    args = parser.parse_args()
    main(args)
    print("Running Time: ", end="")
    print(time.time() - start)
