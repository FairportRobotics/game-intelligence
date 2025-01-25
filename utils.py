import sqlite3
import matplotlib.pyplot as plt
import numpy as np

def get_win_loss_data(team_number):
    conn = sqlite3.connect('frc-data.db') 

    # Create a cursor object
    cursor = conn.cursor()

    cursor.execute(f'''SELECT data.* FROM data
    INNER JOIN event ON data.event_code = event.code AND data.year = event.year
    WHERE event.type = "Regional"
    --AND  data.tournamentLevel = "Qualification"
    AND (
        data.Blue1 = {team_number} OR data.Blue2 = {team_number} OR data.Blue3 = {team_number} OR data.Red1 = {team_number} OR data.Red2 = {team_number} OR data.Red3 = {team_number} 
    )
    ORDER BY event_date, matchNumber''')

    names = [description[0] for description in cursor.description]

    win_loss_data = {}
    for row in cursor.fetchall():
        i = dict(zip(names, row))

        try:
            i["scoreRedTeleop"] = i["scoreRedFinal"] - i["scoreRedAuto"] - i["scoreRedFoul"]
            i["scoreBlueTeleop"] = i["scoreBlueFinal"] - i["scoreBlueAuto"] - i["scoreBlueFoul"] 
        
            if i["scoreBlueTeleop"] == i["scoreRedTeleop"]:
                i["winnerTeleop"] = "Tie"
            elif i["scoreBlueTeleop"] > i["scoreRedTeleop"]:
                i["winnerTeleop"] = "Blue"
            else:
                i["winnerTeleop"] = "Red"
        except:
            i["winnerTeleop"] = "Unknown"
            continue
        

        if i["scoreBlueAuto"] == None or i["scoreRedAuto"] == None:
            i["winnerAuto"] = "Unknown"
        elif i["scoreBlueAuto"] == i["scoreRedAuto"]:
            i["winnerAuto"] = "Tie"
        elif i["scoreBlueAuto"] > i["scoreRedAuto"]:
            i["winnerAuto"] = "Blue"
        else:
            i["winnerAuto"] = "Red"  
        
        
        if i["scoreBlueFinal"] == None or i["scoreRedFinal"] == None:
            i["winnerFinal"] = "Unknown"
        elif i["scoreBlueFinal"] == i["scoreRedFinal"]:
            i["winnerFinal"] = "Tie"
        elif i["scoreBlueFinal"] > i["scoreRedFinal"]:
            i["winnerFinal"] = "Blue"
        else:
            i["winnerFinal"] = "Red"


        if int(i["Blue1"]) == team_number or int(i["Blue2"]) == team_number or int(i["Blue3"]) == team_number:
            i["teamColor"] = "Blue"
        elif int(i["Red1"]) == team_number or int(i["Red2"]) == team_number or int(i["Red3"]) == team_number:
            i["teamColor"] = "Red"
        else:
            i["teamColor"] = "Error"

        win_loss_data_row = win_loss_data.get(i["year"], {})
        
        
        
        if int(i["year"]) >= 2015:
            # Auto
            auto = win_loss_data_row.get("Auto", "")
            dash = "-"
            if len(auto) == 0:
                dash = ""

            if i["winnerAuto"] == "Tie":
                auto = f"{auto}{dash}T"
            elif i["teamColor"] == i["winnerAuto"]:
                auto = f"{auto}{dash}W"
            elif i["winnerAuto"] == "Unknown":
                _ = 1
            else:
                auto = f"{auto}{dash}L"
            win_loss_data_row["Auto"] = auto

            # Teleop
            teleop = win_loss_data_row.get("Teleop", "")
            dash = "-"
            if len(teleop) == 0:
                dash = ""

            if i["winnerTeleop"] == "Tie":
                teleop = f"{teleop}{dash}T"
            elif i["teamColor"] == i["winnerTeleop"]:
                teleop = f"{teleop}{dash}W"
            elif i["winnerTeleop"] == "Unknown":
                _ = 1
            else:
                teleop = f"{teleop}{dash}L"
            win_loss_data_row["Teleop"] = teleop

        
        # Final
        final = win_loss_data_row.get("Final", "")
        dash = "-"
        if len(final) == 0:
            dash = ""

        if i["winnerFinal"] == "Tie":
            final=f"{final}{dash}T"
        elif i["teamColor"] == i["winnerFinal"]:
            final=f"{final}{dash}W"
        elif i["winnerFinal"] == "Unknown":
            _ = 1
        else:
            final=f"{final}{dash}L"
        win_loss_data_row["Final"] = final
        win_loss_data[i["year"]] = win_loss_data_row
    return win_loss_data

def beta_mu(wins, losses, priors=0.5):
     # Define parameters
    alpha = wins + priors
    beta = losses + priors
    return alpha / (alpha + beta)

def beta_sd(wins, losses, priors=0.5):
    alpha = wins + priors
    beta = losses + priors
    return pow((alpha * beta) / (pow(alpha + beta, 2) * (alpha + beta + 1)), 0.5)


def get_viz(win_loss_data, team_number, measure = "Final"):
    mean_1, std_1, years_1 = getGraphData(win_loss_data, measure)
    i = 0
    current_label = ''
    labels = []
    labels_x = []
    for y in years_1:
        if not y == current_label:
            labels_x.append(i)
            labels.append(y)
            current_label = y
        i += 1

    last_mu = round(mean_1[-1], 3) * 100
    mean_1 = np.array(mean_1)
    std_1 = np.array(std_1)

    x = np.arange(len(mean_1))
    plt.plot(x, mean_1, 'b-', label='mean_1')
    plt.fill_between(x, mean_1 - (2*std_1), mean_1 + (2*std_1), color='b', alpha=0.2)
    plt.ylim(0, 1)
    plt.xticks(labels_x, labels, rotation=45)
    plt.title(f"Team {team_number} - {measure} - P win {last_mu}%")
    plt.margins(x=0)
    plt.axhline(y=0.5, color='r', linestyle='--')
    plt.grid(axis = 'y')
    plt.savefig(f'viz/{team_number}-{measure}.png')
    plt.show()
    return(None)

def getGraphData(win_loss_data, measure="Final"):
    if not measure in ['Final', 'Auto', 'Teleop']:
        raise ValueError(f'Invalid measure: {measure}')
    w = 0
    l = 0
    mean_1 = []
    std_1 = []
    years_1 = []
    for year in win_loss_data.keys():
        try:
            for f in  win_loss_data.get(year).get(measure).split("-"):
                if f == "W":
                    w += 1
                else:
                    l += 1
                mu = beta_mu(w,l)
                sigma = beta_sd(w,l)
                mean_1.append(mu)
                std_1.append(sigma)
                years_1.append(year)
        except:
            continue
    return mean_1, std_1, years_1

def currentWinProb(mean_1):
    return(round(mean_1[-1], 3) * 100)