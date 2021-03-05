import pandas as pd
import re

#   ======= PART 1 =======

def analyse_nba_game(play_by_play_moves):

    description = play_by_play_moves["DESCRIPTION"].tolist()
    away_team_name = play_by_play_moves.iloc[0]["AWAY_TEAM"]
    home_team_name = play_by_play_moves.iloc[0]["HOME_TEAM"]

    #  --- creating intermediate dataframe 'df' to collect statistics from play_by_play_moves  ---
    df = pd.DataFrame(columns=('TEAM_NAME', 'player_name'))

    #  --- filling in 'df' with players' name and corresponding team names  ---
    for i in range(len(play_by_play_moves)):
        regex = '[A-ZÃ]. [a-zA-ZÃ¶]+'
        team_name = play_by_play_moves.loc[i, 'RELEVANT_TEAM']
        player_name = re.search(regex, play_by_play_moves.loc[i, 'DESCRIPTION'])
        shooting_foul = re.search('Shooting', play_by_play_moves.loc[i, 'DESCRIPTION'])
        personal_foul = re.search('Personal', play_by_play_moves.loc[i, 'DESCRIPTION'])

        if ((shooting_foul != None) or (personal_foul != None)):
            if (team_name == away_team_name):
                df.loc[i] = [home_team_name, player_name.group()]
            else:
                df.loc[i] = [away_team_name, player_name.group()]

        elif (player_name != None):
            df.loc[i] = [team_name, player_name.group()]

    df = df.drop_duplicates(ignore_index = True)
    df = df.sort_values('TEAM_NAME')
    # print(df)

    #  --- making index column with players' surnames ---
    array = df["player_name"].tolist()
    for i in range (len(array)):
        count = 0
        for j in range (len(array[i])):
            count += 1
            if (array[i][j] == ' '):
                array[i] = array[i][count:]
                break
    df.index = array

    #  --- additional columns with intermediate statistics (values = zero) ---
    statistics = ["FG", "FGA", "FG%","3P", "3PA", "3P%", "FT", "FTA", "FT%", "ORB", "DRB", "TRB", "AST", "STL", "BLK", "TOV", "PF", "PTS", "2P", "2PA"]
    for i in statistics:
        df[i] = 0

    # --- iterating through DESCRIPTION to fill in players statistics ---
    for i in range (len(description)):
        description[i] = description[i].split()
        for j in range (len(description[i])):
            if (description[i][j] == "makes" and description[i][j+1] == "3-pt"):
                df.at[description[i][j-1], "3P"] += 1
            if (description[i][j] == "3-pt"):
                df.at[description[i][j-2], "3PA"] += 1
            if (description[i][j] == "makes" and description[i][j+1] == "free"):
                df.at[description[i][j-1], "FT"] += 1
            if ((description[i][j] == "free" and description[i][j+1] == "throw" and description[i][j-1] != "path")):
                df.at[description[i][j-2], "FTA"] += 1
            if (description[i][j] == "Offensive" and description[i][j+1] == "rebound" and description[i][j+3] != "Team"):
                df.at[description[i][j+4], "ORB"] += 1
            if (description[i][j] == "Defensive" and description[i][j+1] == "rebound" and description[i][j+3] != "Team"):
                df.at[description[i][j+4], "DRB"] += 1
            if (description[i][j] == "(assist"):
                df.at[description[i][j+3][:-1], "AST"] += 1
            if (description[i][j] == "steal"):
                df.at[description[i][j+3][:-1], "STL"] += 1
            if (description[i][j] == "(block"):
                df.at[description[i][j+3][:-1], "BLK"] += 1
            if (description[i][j] == "Turnover" and description[i][j+2] != "Team"):
                df.at[description[i][j+3], "TOV"] += 1
            if (description[i][j] == "foul"):
                df.at[description[i][j+3], "PF"] += 1
            if (description[i][j] == "makes" and description[i][j+1] == "2-pt"):
                df.at[description[i][j-1], "2P"] += 1
            if (description[i][j] == "2-pt"):
                df.at[description[i][j-2], "2PA"] += 1
    
    df['FG'] = df['3P'] + df['2P']
    df['FGA'] = df['3PA'] + df['2PA']
    df['FG%'] = df['FG'] / df['FGA']
    df['3P%'] = df['3P'] / df['3PA']
    df['FT%'] = df['FT'] / df['FTA']
    df['TRB'] = df['ORB'] + df['DRB']
    df['PTS'] = 2*df['2P'] + 3*df['3P'] + df['FT']
    df = df.round({'FG%': 3, '3P%': 3, 'FT%': 3})
    df = df.fillna(0)

    df = df.drop(columns=['2P', '2PA'])
    df = df.reset_index(drop = True)
    
    #  --- 'df' division by teams' name into two dataframes  ---
    grouped = df.groupby(df.TEAM_NAME)
    DATA_home_df = grouped.get_group(home_team_name)
    DATA_home_df = DATA_home_df.drop(columns=['TEAM_NAME'])
    DATA_away_df = grouped.get_group(away_team_name)
    DATA_away_df = DATA_away_df.drop(columns=['TEAM_NAME'])
    # print(DATA_home_df)
    # print(DATA_away_df)

    #  --- dictionaries creation ---
    DATA_home = DATA_home_df.to_dict('records')
    DATA_away = DATA_away_df.to_dict('records')
    # print(DATA_home)
    # print(DATA_away)

    home_team = {"name": home_team_name, "players_data": DATA_home}
    away_team = {"name": away_team_name, "players_data": DATA_away}
    result = {"home_team": home_team, "away_team": away_team}
    # print(result)

    return result

#  -------------------------------------------------------

#   ======= PART 2 =======

def print_nba_game_stats(team_dict):
    #  --- Home Team printing ---
    print("HOME TEAM: " + str(team_dict["home_team"]["name"]))
    print("Players FG FGA FG% 3P 3PA 3P% FT FTA FT% ORB DRB TRB AST STL BLK TOV PF PTS")
    temp_list = []
    for i in range(len(team_dict["home_team"]["players_data"])):
        temp_dict = team_dict["home_team"]["players_data"][i]
        temp_list.append(list(temp_dict.values()))
        temp_str = ""
        for key in temp_dict:
            temp_str += str(temp_dict[key]) + " "
        print(temp_str)
    #  --- Home Team Totals printing ---
    total_list = []
    total_list.append("Team Totals")
    for i in range(len(temp_list)):
        for j in range(1, len(temp_list[i])):
            if (i == 0):
                total_list.append(0)
            total_list[j] += temp_list[i][j]
    total_list[3] = round(total_list[1]/total_list[2], 3)
    total_list[6] = round(total_list[4]/total_list[5], 3)
    total_list[9] = round(total_list[7]/total_list[8], 3)
    temp_str = ""
    for i in range(len(total_list)):
        temp_str += str(total_list[i]) + " "
    print(temp_str)

    print("========================================")

    #  --- Away Team printing ---
    print("AWAY TEAM: " + str(team_dict["away_team"]["name"]))
    print("Players FG FGA FG% 3P 3PA 3P% FT FTA FT% ORB DRB TRB AST STL BLK TOV PF PTS")
    temp_list = []
    for i in range(len(team_dict["away_team"]["players_data"])):
        temp_dict = team_dict["away_team"]["players_data"][i]
        temp_list.append(list(temp_dict.values()))
        temp_str = ""
        for key in temp_dict:
            temp_str += str(temp_dict[key]) + " "
        print(temp_str)
    #  --- Away Team Totals printing ---
    total_list = []
    total_list.append("Team Totals")
    for i in range(len(temp_list)):
        for j in range(1, len(temp_list[i])):
            if (i == 0):
                total_list.append(0)
            total_list[j] += temp_list[i][j]
    total_list[3] = round(total_list[1]/total_list[2], 3)
    total_list[6] = round(total_list[4]/total_list[5], 3)
    total_list[9] = round(total_list[7]/total_list[8], 3)
    temp_str = ""
    for i in range(len(total_list)):
        temp_str += str(total_list[i]) + " "
    print(temp_str)


#  --- reading csv data ---
play_by_play_moves = pd.read_csv("data.txt", sep = '|', names=["PERIOD","REMAINING_SEC","RELEVANT_TEAM","AWAY_TEAM","HOME_TEAM","AWAY_SCORE","HOME_SCORE","DESCRIPTION"])
# print(play_by_play_moves)
analyse_nba_game(play_by_play_moves)

team_dict = analyse_nba_game(play_by_play_moves)              
print_nba_game_stats(team_dict)
