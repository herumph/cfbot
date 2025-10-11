from db.models import Game

# TODO: add tests
def game_header(game: Game, streak_info: dict[str, str]) -> str:
    """Format information into posting format.

    Args:
        game (Game): game information from the game database
        streak_info (dict[str, str]): dictionary of the streak information for the home and away teams

    Returns:
        string: post text
    """
    away_team = f"{game.away_team} ({game.away_wins}-{game.away_losses}, "
    away_team_conference = f"{(game.away_conf_wins)}-{game.away_conf_losses}) {streak_info[game.away_team_id]} @ "
    home_team = f"{game.home_team} ({game.home_wins}-{game.home_losses}, "
    home_team_conference = f"{game.home_conf_wins}-{game.home_conf_losses}) {streak_info[game.home_team_id]}"
    return (
        away_team
        + away_team_conference
        + home_team
        + home_team_conference
        + f" has kicked off on {game.networks}!"
    )


# TODO: add tests
def scoring_play(drive: dict[str, str]) -> str:
    """Format the scoring play for a drive.

    Args:
        drive (dict): dictionary containing drive information

    Returns:
        string: scoring play formatted for posting
    """
    play_text = f"""{drive["scoring_team"]} scores! {drive["play_text"].strip()}"""
    drive_text = (
        f""" after a drive of {drive["drive_description"]} minutes.\n"""
        if drive["drive_description"]
        else ".\n"
    )
    score_text = f"""{drive["away"]} {drive["away_score"]} - {drive["home"]} {drive["home_score"]}"""
    return play_text + drive_text + score_text