import psycopg2
from dotenv import load_dotenv
import os
load_dotenv()

dbname = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
dbpassword = os.getenv("DB_PASS")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")

def dbInit():
  print("Init Started")
  conn = psycopg2.connect(
    dbname=dbname,
    user=user,
    password=dbpassword,
    host=host,
    port=port
  )
  cursor = conn.cursor()
  print("Connection Successful")

  cursor.execute("SELECT to_regclass('public.candidates')")
  result = cursor.fetchone()
  if result[0] == None:
    cursor.execute("CREATE TABLE candidates (user_id TEXT PRIMARY KEY, name TEXT, title TEXT, votes INT, url TEXT)")
    conn.commit()

  cursor.execute("SELECT to_regclass('public.statuses')")
  result = cursor.fetchone()
  if result[0] == None:
    cursor.execute("CREATE TABLE statuses (name TEXT PRIMARY KEY)")
    conn.commit()
  
  cursor.execute("SELECT to_regclass('public.voters')")
  result = cursor.fetchone()
  if result[0] == None:
    cursor.execute("CREATE TABLE voters (user_id TEXT PRIMARY KEY, candidate_id TEXT)")
    conn.commit()

  cursor.close()
  conn.close()

def addCandidate(user_uuid, name, gc_name, url):
    print("\n\n",user_uuid, name, gc_name)
    dbInit()
    print("Init Done")
  
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=dbpassword,
        host=host,
        port=port
    )
    cursor = conn.cursor()

    cursor.execute("INSERT INTO candidates VALUES (%s, %s, %s, 0, %s); ",(str(user_uuid),str(name),str(gc_name),str(url)))
    conn.commit()

    cursor.close()
    conn.close()
    print("User added")
    return True

def removeCandidate(user_uuid):
    print("\n\n",user_uuid)
    dbInit()
    print("Init Done")
  
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=dbpassword,
        host=host,
        port=port
    )
    cursor = conn.cursor()

    cursor.execute("DELETE FROM candidates WHERE user_id=%s;",(str(user_uuid),))
    conn.commit()

    cursor.close()
    conn.close()
    print("User Removed")
    return True

def listCandidates():
    dbInit()
    options = []
    index = 0
    names = []
    titles = []
    user_ids = []
    urls = []
    conn = psycopg2.connect(
      dbname=dbname,
      user=user,
      password=dbpassword,
      host=host,
      port=port
    )
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM candidates;")
    results = cursor.fetchall()
    
    for result in results:
      names.append(result[0])
    
    cursor.execute("SELECT title FROM candidates;")
    results = cursor.fetchall()
    
    for result in results:
      titles.append(result[0])
    
    cursor.execute("SELECT user_id FROM candidates;")
    results = cursor.fetchall()
    
    for result in results:
      user_ids.append(result[0])

    cursor.execute("SELECT url FROM candidates;")
    results = cursor.fetchall()
    
    for result in results:
      urls.append(result[0])

    for i in range(len(names)):
      options.append(titles[i] + " (" + names[i] + ") " + "(" + user_ids[i] + ")")

    cursor.close()
    conn.close()
    return options, urls

def vote(author_id,candidate_id):
  dbInit()
  conn = psycopg2.connect(
    dbname=dbname,
    user=user,
    password=dbpassword,
    host=host,
    port=port
  )
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM voters WHERE user_id=%s;",(str(author_id),))
  result = cursor.fetchone()
  if result == None:
    cursor.execute("INSERT INTO voters VALUES (%s, %s); ",(str(author_id),str(candidate_id),))
    cursor.execute("SELECT votes FROM candidates WHERE user_id=%s;",(str(candidate_id),))
    votes_old = cursor.fetchone()
    votes_new = votes_old[0] +1
    cursor.execute("UPDATE candidates SET votes=%s WHERE user_id=%s;",(votes_new,str(candidate_id),))
    conn.commit()
    
    cursor.close()
    conn.close()
    return True
  else:
    cursor.close()
    conn.close()
    return False
  cursor.close()
  conn.close()

def reset_db():
  dbInit()
  conn = psycopg2.connect(
    dbname=dbname,
    user=user,
    password=dbpassword,
    host=host,
    port=port
  )
  cursor = conn.cursor()
  cursor.execute("DELETE FROM candidates")
  cursor.execute("DELETE FROM voters")
  conn.commit()
  cursor.close()
  conn.close()

def end_election():
  runoff_candidates = []
  runoff_candidatesS = ""
  index = 0
  first = 0
  second = 0

  dbInit()
  conn = psycopg2.connect(
    dbname=dbname,
    user=user,
    password=dbpassword,
    host=host,
    port=port
  )
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM candidates ORDER BY votes DESC;")
  results = cursor.fetchall()

  if results[0] != None:
    runoff_candidatesS += "Runoff Candidates:\n\n"

  if len(results) <= 2:
    return(results[0][1] + " has won the election")
  else:
    for result in results:
      index += 1
      if index == 1:
        first = result[3]
      elif index == 2:
        second = result[3]
    
    for result in results:
      if result[3] == first or result[3] == second:
        runoff_candidates.append(result[0])

    for i in range(len(runoff_candidates)):
      runoff_candidatesS += runoff_candidates[i] + "\n\n"

    print(str(runoff_candidates).replace('[', '(').replace(']', ')'))
    
    # wild card not working for some reason
    # cursor.execute("DELETE FROM candidates WHERE user_id NOT IN (%s)", runoff_candidates)

    cursor.execute("DELETE FROM candidates WHERE user_id NOT IN " + (str(runoff_candidates).replace('[', '(').replace(']', ')')) + ";")
    
    cursor.execute("UPDATE candidates SET votes = 0")

    cursor.execute("DELETE FROM voters")
    conn.commit()

    return runoff_candidatesS

  cursor.close()
  conn.close()

def getGraphData():
  dbInit()

  conn = psycopg2.connect(
    dbname=dbname,
    user=user,
    password=dbpassword,
    host=host,
    port=port
  )
  cursor = conn.cursor()

  cursor.execute("SELECT * FROM candidates ORDER BY votes DESC;")
  results = cursor.fetchall()

  cursor.close()
  conn.close()
  if results != None:
    return results
  else:
    return False

def get_statuses():
  dbInit()

  conn = psycopg2.connect(
    dbname=dbname,
    user=user,
    password=dbpassword,
    host=host,
    port=port
  )

  cursor = conn.cursor()

  cursor.execute("SELECT * FROM statuses;")
  results = cursor.fetchall()
  return results

  cursor.close()
  conn.close()