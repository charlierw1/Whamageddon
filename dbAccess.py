import mariadb
import os
from dotenv import load_dotenv
load_dotenv()

conn = mariadb.connect( # DB Connection Initiation
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    database=os.getenv("DB")
)

def test(): # Select all from guilds to test db connection
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM guilds WHERE GuildID>0")
        for row in cur:
            print(row)

def getToggle(GuildID): # Get state of whitelist for guild
    with conn.cursor() as cur:
        cur.execute("SELECT WhitelistEnabled FROM guilds WHERE GuildID=?", (GuildID,))
        return cur.fetchone()[0] == 1
    
def toggleWhitelist(GuildID): # Flip the Boolean value of the WhitelistEnabled of the handed guild
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

def getChannels(GuildID): # Return all channels whitelisted in the handed guild
    with conn.cursor() as cur:
        cur.execute("SELECT WhitelistedChannels FROM guilds WHERE GuildID=?", (GuildID,))
        return cur.fetchone()

def setChannels(GuildID, Channels): # Set the channel whitelist in the guild to the handed jsonified list
    with conn.cursor() as cur:
        cur.execute(
                "UPDATE guilds SET WhitelistedChannels = ? WHERE GuildID = ?", 
                (Channels, GuildID)
            )
        conn.commit()

def getYears(YearID): # If a year is handed with the function call select that year otherwise select all
    if YearID:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM years WHERE YearID=?", (YearID,))
            return cur.fetchone()
    else:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM years")
            conn.commit()
            return cur.fetchall()
    

def insertYear(YearID): # Add new year entry into years
    with conn.cursor() as cur:
        cur.execute(
                "INSERT INTO years (YearID) VALUES (?)", 
                (YearID,)
            )
        conn.commit()

def setYears(ActiveYear, state): # Set year active state
    for year in getYears(False):
        if year[0] == ActiveYear:
            with conn.cursor() as cur:
                cur.execute("UPDATE years SET Active = ? WHERE YearID=?", (state, year[0]))
                conn.commit()
        else:
            with conn.cursor() as cur:
                cur.execute("UPDATE years SET Active = FALSE WHERE YearID=?", (year[0],))
                conn.commit()

def checkGuild(GuildID): # Check guild exist
    with conn.cursor() as cur:
        cur.execute("SELECT GuildID FROM guilds WHERE GuildID=?", (GuildID,))
        return cur.fetchone() is not None

def insertGuild(GuildID): # Add a guild
    with conn.cursor() as cur:
        cur.execute("INSERT INTO guilds (GuildID) VALUES (?)", (GuildID,))
        conn.commit()

def checkUser(UserID): # Check user entry exists
    with conn.cursor() as cur:
        cur.execute("SELECT UserID FROM users WHERE UserID=?", (UserID,))
        return cur.fetchone() is not None

def insertUser(UserID, TimeZone): # Add user entry
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO users (UserId, TimeZone) VALUES (?, ?)",
            (UserID, TimeZone)
        )
        conn.commit()

def checkAttempt(Year, UserID): # Check attempt exists
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM attempts WHERE YearID=? AND UserID=?",
            (Year, UserID)
        )
        return cur.fetchone() is not None

def insertAttempt(Year, UserID): # Add user attempt
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO attempts (YearID, UserID) VALUES (?, ?)",
            (Year, UserID)
        )
        conn.commit()

def addLoss(Year, LossDate, LossReason, UserID): # Add loss to user attempt
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE attempts SET Lost = TRUE, LossDate = ?, LossReason = ? WHERE UserID = ? AND YearID = ?", 
            (LossDate, LossReason, UserID, Year)
        )
        conn.commit()

def getLoss(userID): # Get loss from user ID
    with conn.cursor() as cur:
        cur.execute(
            "SELECT Lost, LossDate, LossReason FROM attempts WHERE UserID = ?", 
            (userID,)
        )
        return cur.fetchone()
        
def closeConnection(): # Close connection
    conn.close()
