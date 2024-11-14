import subprocess


# insert customer
insert_command = [
    "python", "customer.py", "insert", "9999", "dblab", "dblab@hanyang.ac.kr", "password", "M", "+82 123-456-7890", "-g", "Action", "Drama", "Romance"
]

# info customer
info_command = [
    "python", "customer.py", "info", "-a", "10"
]
info_g_command = [
    "python", "customer.py", "info", "-g", "Action"
]
info_t_command = [
    "python", "customer.py", "info", "-i", "9999"
]
info_n_command = [
    "python", "customer.py", "info", "-n", "dblab"
]


# update email customer
update_email_command = [
    "python", "customer.py", "update", "-i", "9999", "-m", "dblab@gmail.com"
]

# update pwd customer
update_pwd_command = [
    "python", "customer.py", "update", "-i", "9999", "-p", "password", "dblab"
]

# update phone customer
update_phone_command = [
    "python", "customer.py", "update", "-i", "9999", "-ph", "+82 010-1234-5678"
]

# update phone customer
update_genres_command = [
    "python", "customer.py", "update", "-i", "9999", "-gs", "Action", "Drama", "Family"
]


# delete customer
delete_command = [
    "python", "customer.py", "delete", "-i", "9999"
]

customer = [insert_command, info_command, info_g_command, info_t_command, info_n_command,
            update_email_command, update_pwd_command, update_phone_command, delete_command]
# info movie
info_movie_a_command = [
    "python", "movie.py", "info", "-a", "5"
]

# info movie
info_movie_i_command = [
    "python", "movie.py", "info", "-i", "71002"
]

# info movie
info_movie_n_command = [
    "python", "movie.py", "info", "-n", "the hathaways"
]

# info movie
info_movie_g_command = [
    "python", "movie.py", "info", "-g", "Action"
]

# info movie
info_movie_t_command = [
    "python", "movie.py", "info", "-t", "tvSeries"
]

# info movie
info_movie_sy_command = [
    "python", "movie.py", "info", "-sy", "2023"
]

# info movie
info_movie_ey_command = [
    "python", "movie.py", "info", "-ey", "2023"
]

# info movie
info_movie_ad_command = [
    "python", "movie.py", "info", "-ad", "false"
]

# info movie
info_movie_r_command = [
    "python", "movie.py", "info", "-r", "8.2"
]

movies = [info_movie_a_command, info_movie_i_command, info_movie_n_command, info_movie_g_command, info_movie_t_command, info_movie_sy_command, info_movie_ey_command, info_movie_ad_command, info_movie_r_command]
# info role
info_role_a_command = [
    "python", "role.py", "info", "-a", "5", "actor"
]

# info role
info_role_i_command = [
    "python", "role.py", "info", "-i", "71002", "actor"
]

role = [info_role_a_command, info_role_i_command]

# participant role
info_participant_a_command = [
    "python", "participant.py", "info", "-a", "5"
]

# participant role
info_participant_i_command = [
    "python", "participant.py", "info", "-i", "92"
]

# participant role
info_participant_n_command = [
    "python", "participant.py", "info", "-n", "john Cleese"
]

# participant role
info_participant_pr_command = [
    "python", "participant.py", "info", "-pr", "actor"
]
participant = [info_participant_a_command, info_participant_i_command, info_participant_n_command, info_participant_pr_command]


# Run the command
if __name__ == "__main__":
    for c in customer:
        subprocess.run(c)

    for m in movies:
        subprocess.run(m)

    for r in role:
        subprocess.run(r)

    for p in participant:
        subprocess.run(p)