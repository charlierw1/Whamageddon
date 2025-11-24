import mariadb

# Load DB credentials from file
db_data = ["user", "password", "host", "port", "database"]

with open("../DB-DATA/Whamageddon.txt") as file:
    for i, line in enumerate(file.readlines()):
        db_data[i] = line.strip()

# -----------------------
# Shared connection
# -----------------------
conn = mariadb.connect(
    user=db_data[0],
    password=db_data[1],
    host=db_data[2],
    port=int(db_data[3]),
    database=db_data[4]
)

# -----------------------
# Test function
# -----------------------
def test():
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM guilds WHERE GuildID>0")
        for row in cur:
            print(row)

   
def getToggle(GuildID):
    with conn.cursor() as cur:
        cur.execute("SELECT WhitelistEnabled FROM guilds WHERE GuildID=?", (GuildID,))
        return cur.fetchone()[0] == 1

# -----------------------
# Guild functions
# -----------------------
def checkGuild(GuildID):
    with conn.cursor() as cur:
        cur.execute("SELECT GuildID FROM guilds WHERE GuildID=?", (GuildID,))
        return cur.fetchone() is not None

def insertGuild(GuildID):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO guilds (GuildID) VALUES (?)", (GuildID,))
        conn.commit()

# -----------------------
# User functions
# -----------------------
def checkUser(UserID):
    with conn.cursor() as cur:
        cur.execute("SELECT UserID FROM users WHERE UserID=?", (UserID,))
        return cur.fetchone() is not None

def insertUser(UserID, TimeZone):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO users (UserId, TimeZone) VALUES (?, ?)",
            (UserID, TimeZone)
        )
        conn.commit()

# -----------------------
# Attempt functions
# -----------------------
def checkAttempt(Year, UserID):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM attempts WHERE YearID=? AND UserID=?",
            (Year, UserID)
        )
        return cur.fetchone() is not None

def insertAttempt(Year, UserID):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO attempts (YearID, UserID) VALUES (?, ?)",
            (Year, UserID)
        )
        conn.commit()

def addLoss(Year, LossDate, LossReason, UserID):
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE attempts SET Lost = TRUE, LossDate = ?, LossReason = ? WHERE UserID = ? AND YearID = ?", 
            (LossDate, LossReason, UserID, Year)
        )
        conn.commit()

def toggleWhitelist(GuildID):
    cur = conn.cursor()
    try:
        # Toggle 0/1
        cur.execute(
            "UPDATE guilds SET WhitelistEnabled = 1 - WhitelistEnabled WHERE GuildID = ?", 
            (GuildID,)
        )
        conn.commit()

        # Return the new value
        cur.execute(
            "SELECT WhitelistEnabled FROM guilds WHERE GuildID = ?", 
            (GuildID,)
        )
        result = cur.fetchone()
        return bool(result[0])
    finally:
        cur.close()

def getChannels(GuildID):
    with conn.cursor() as cur:
        cur.execute("SELECT WhitelistedChannels FROM guilds WHERE GuildID=?", (GuildID,))
        return cur.fetchone()

def setChannels(GuildID, Channels):
    with conn.cursor() as cur:
        cur.execute(
                "UPDATE guilds SET WhitelistedChannels = ? WHERE GuildID = ?", 
                (Channels, GuildID)
            )
        conn.commit()

def getYear(YearID):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM years WHERE YearID=?", (YearID,))
        return cur.fetchone()

def insertYear(YearID):
    with conn.cursor() as cur:
        cur.execute(
                "INSERT INTO years (YearID) VALUES (?)", 
                (YearID,)
            )
        conn.commit()

# -----------------------
# Close connection
# -----------------------
def closeConnection():
    conn.close()
