from numerize import numerize
from response import data


def get_response(log_id):
    fight_data = data(log_id)

    print("Formating data for discord!")

    player_damage_data = fight_data[0]
    player_cleanse_data = fight_data[1]
    player_strip_data = fight_data[2]
    kills_info = fight_data[5]
    downs_info = fight_data[6]
    resses_info = fight_data[7]

    def general_squad_info():
        general_formating = (f" Allies: {fight_data[3][3]:^4} | Kills: {fight_data[8]:^3} | Damage dealt: {numerize.numerize(fight_data[11], decimals = 1):^6}" # Number of squad members | Squad kills | Damage dealt by squad
                           + "\n--------------------------------------------------"
                           + f"\n Enemies: {fight_data[3][2]:^3} | Kills: {fight_data[9]:^3} | Damage dealt: {numerize.numerize(fight_data[10], decimals = 1):^6}") # Number of enemies | Enemy kills/Squad deaths | Damage dealt by enemies/Incoming damage to squad

        return general_formating

    def top_damage():
        damage_formating = (
            " #"
            + " " * 3
            + "Class"
            + " " * 4
            + "Player"
            + " " * 20
            + "Damage (DPS)"
            # + " " * 5
            # + "DPS"
            + "\n--- -------- ----------------------- -----------------"
        )

        for n in range(len(player_damage_data[:10])):
            if n < 9:
                player = (
                    f"\n {n+1}"
                    + " " * 4
                    + f"{(player_damage_data[n][1][1])[:4]}" # Class
                    + " " * 4
                    + f"{player_damage_data[n][0]:<24}" # Player character name
                    + f"{numerize.numerize(player_damage_data[n][1][0], decimals = 1):<6} ({numerize.numerize((player_damage_data[n][1][2]), decimals = 1)}/s)" # Total damage dealt (DPS)
                    # + " " * 3
                    # + f"{numerize.numerize((player_damage_data[n][1][2]), decimals = 1):^4}"  #DPS
                )
                damage_formating += player
            else:
                player = (
                    f"\n{n+1}"
                    + " " * 4
                    + f"{(player_damage_data[n][1][1])[:4]}"
                    + " " * 4
                    + f"{player_damage_data[n][0]:<24}"
                    + f"{numerize.numerize(player_damage_data[n][1][0], decimals = 1):<6} ({numerize.numerize((player_damage_data[n][1][2]), decimals = 1)}/s)"
                    # + " " * 3
                    # + f"{numerize.numerize((player_damage_data[n][1][2]), decimals = 1):^4}"
                )
                damage_formating += player

        return damage_formating

    def top_cleanse():
        cleanse_formating = (
            "\n #"
            + " " * 3
            + "Class"
            + " " * 3
            + "Player"
            + " " * 18
            + "Cleanse"
            + "\n--- ------- ----------------------- ---------"
        )

        for n in range(len(player_cleanse_data[:10])):
            if n < 9:
                player = (
                    f"\n {n+1}"
                    + " " * 3
                    + f"{(player_cleanse_data[n][1][1])[:4]}" # Class
                    + " " * 4
                    + f"{player_cleanse_data[n][0]:<26}" # Char name
                    + f"{numerize.numerize(player_cleanse_data[n][1][0]):<4}" # Number of cleanses
                )
                cleanse_formating += player
            else:
                player = (
                    f"\n{n+1}"
                    + " " * 3
                    + f"{(player_cleanse_data[n][1][1])[:4]}"
                    + " " * 4
                    + f"{player_cleanse_data[n][0]:<26}"
                    + f"{numerize.numerize(player_cleanse_data[n][1][0]):<4}"
                )
                cleanse_formating += player
        return cleanse_formating

    def top_strips():
        strip_formating = (
            "\n #"
            + " " * 3
            + "Class"
            + " " * 3
            + "Player"
            + " " * 19
            + "Strip"
            + "\n--- ------- ----------------------- ---------"
        )

        for n in range(len(player_strip_data[:10])):
            if n < 9:
                player = (
                    f"\n {n+1}"
                    + " " * 3
                    + f"{(player_strip_data[n][1][1])[:4]}" # Class
                    + " " * 4
                    + f"{player_strip_data[n][0]:<26}" # Char name
                    + f"{numerize.numerize(player_strip_data[n][1][0]):<4}" # Number of strips
                )
                strip_formating += player
            else:
                player = (
                    f"\n{n+1}"
                    + " " * 3
                    + f"{(player_strip_data[n][1][1])[:4]}"
                    + " " * 4
                    + f"{player_strip_data[n][0]:<26}"
                    + f"{numerize.numerize(player_strip_data[n][1][0]):<4}" 
                )
                strip_formating += player
        return strip_formating

    def top_kills():
        kills_formating = (
            "\n #"
            + " " * 3
            + "Class"
            + " " * 3
            + "Player"
            + " " * 18
            + "Kills"
            + "\n--- ------- ----------------------- -------"
        )

        for n in range(len(kills_info[:10])):
            if n < 9:
                player = (
                    f"\n {n+1}"
                    + " " * 3
                    + f"{(kills_info[n][1][1])[:4]}"
                    + " " * 4
                    + f"{kills_info[n][0]:<26}"
                    + f"{numerize.numerize(kills_info[n][1][0]):<2}"
                )
                kills_formating += player
            else:
                player = (
                    f"\n{n+1}"
                    + " " * 3
                    + f"{(kills_info[n][1][1])[:4]}"
                    + " " * 4
                    + f"{kills_info[n][0]:<26}"
                    + f"{numerize.numerize(kills_info[n][1][0]):<2}"
                )
                kills_formating += player
        return kills_formating

    def top_downs():
        downs_formating = (
            "\n #"
            + " " * 3
            + "Class"
            + " " * 3
            + "Player"
            + " " * 18
            + "Downs"
            + "\n--- ------- ----------------------- -------"
        )

        for n in range(len(downs_info[:10])):
            if n < 9:
                player = (
                    f"\n {n+1}"
                    + " " * 3
                    + f"{(downs_info[n][1][1])[:4]}"
                    + " " * 4
                    + f"{downs_info[n][0]:<26}"
                    + f"{numerize.numerize(downs_info[n][1][0]):<2}"
                )
                downs_formating += player
            else:
                player = (
                    f"\n{n+1}"
                    + " " * 3
                    + f"{(downs_info[n][1][1])[:4]}"
                    + " " * 4
                    + f"{downs_info[n][0]:<26}"
                    + f"{numerize.numerize(downs_info[n][1][0]):<2}"
                )
                downs_formating += player
        return downs_formating

    def top_resses():
        resses_formating = (
            "\n #"
            + " " * 3
            + "Class"
            + " " * 3
            + "Player"
            + " " * 18
            + "Resses"
            + "\n--- ------- ----------------------- --------"
        )

        for n in range(len(resses_info[:5])):
            player = (
                f"\n {n+1}"
                + " " * 3
                + f"{(resses_info[n][1][1])[:4]}"
                + " " * 4
                + f"{resses_info[n][0]:<26}"
                + f"{numerize.numerize(resses_info[n][1][0]):<2}"
            )
            resses_formating += player

        return resses_formating 

    return top_damage(), top_cleanse(), top_strips(), fight_data[3], fight_data[4], top_kills(), top_downs(), top_resses(), general_squad_info()
