import re

import praw.objects

from Mind import memory
from Utilities import CASexcepts as excs
from Utilities.loggingSetup import create_logger
"""
Module for letting the Chroma Automation Suite sense users both signing up
to receive alerts from their generals and to sense which side players are on.
"""
LOG = create_logger(__name__)


def recruit_getter(cfg, db, antenna, side):
    """
    Get all of the new recruits from the proper side's recruitment thread
    and return them in a list. Note that this will only return new
    recruits.

    :param cfg: Global configuration information to be used
    :param db: Database to be used
    :param antenna: Antenna connection to Reddit
    :param side: Side to gather recruits from
    :return: A list of new recruits.
    """
    # retrieve majors from DB
    majors = memory.get_players_with(db, recruited=True)

    # retrieve sign up thread from reddit
    if side == 0:
        signup_thread = antenna.get_submission(
            submission_id=cfg['OR_RECRUIT_THREAD'],
            comment_limit=None,
            comment_sort='new')
    elif side == 1:
        signup_thread = antenna.get_submission(
            submission_id=cfg['PW_RECRUIT_THREAD'],
            comment_limit=None,
            comment_sort='new')
    else:
        raise excs.InvalidSideError(__name__, side)
    LOG.debug('Got signup thread for side {} from {}'.format(
        side,
        signup_thread.id))
    # and replace more comments
    signup_thread.replace_more_comments()
    LOG.debug('Replaced more comments')

    # list comment authors from comment generator
    all_recruits = [cmnt for cmnt in signup_thread.comments]

    # filter out already registered recruits
    new_recruits = [recr for recr in all_recruits if
                    str(recr.author) not in majors]

    return new_recruits


def retrieve_combatants(antenna):
    """
    Look through old battles and skirmishes to retrieve users that have
    battled and their respective sides. Maybe later also keep track of
    troop counts and attendance?

    :param antenna: Antenna connection to Reddit
    :return: A dictionary of usernames and their side
    """
    # retrieve old battle threads
    skirms = get_old_skirms(antenna)

    # regex pattern to extract name and side
    idPattern = re.compile(r"\w+\s+\(+\w+\)")

    combatant_dict = {}

    # look through each skirm post and extract players
    for skirm in skirms:
        players = idPattern.findall(skirm.body)

        #go through each player and add or update dict entry
        for player in players:
            # username is the first part of player
            username = player.split()[0]
            # side is the second part
            side = player.split()[1]

            if side == '(Orangered)':
                combatant_dict[username] = 0
            elif side == '(Periwinkle)':
                combatant_dict[username] = 1
            else:
                raise excs.InvalidSideError(__name__, side)
    return combatant_dict


def get_old_skirms(antenna):
    """
    Retrieve old battles and extract old skirmishes from them. Meant to be a
    helper method for retrieve_combatants, but may have uses elsewhere.

    :param antenna: Antenna to connect to Reddit
    :return: a list of old skirmishes, in the form of Chrommabot's comments
    """
    # get old battles
    battle_gen = antenna.search('[Invasion]', subreddit='FieldOfKarmicGlory')
    battles = [b for b in battle_gen if str(b.author) == 'Chromabot']

    #get skirmish comments
    skirms = []
    for battle in battles:
        battle.replace_more_comments()
        comments = praw.helpers.flatten_tree(battle.comments)
        for cmnt in comments:
            if hasattr(cmnt, 'author') and cmnt.author == 'Chromabot':
                skirms.append(cmnt)

    return skirms


def reply_to_signup(sign_up, side, cfg):
    """
    As labeled, replies to a sign up with the appropriate message

    :param sign_up: Top-level commment to reply to
    :param side: Side the bot represents
    :param cfg: Config to be used

    :return: True if successful
    """
    if side == 0:
        message = cfg['OR_RECRUIT_RESPONSE']
    elif side == 1:
        message = cfg['PW_RECRUIT_RESPONSE']
    else:
        raise excs.InvalidSideError(__name__, side)

    # reply with a customized message
    sign_up.reply(message.format(str(sign_up.author)))


def send_message(antenna, subject, content, recipients, bot_name):
    antenna.set_user(bot_name)
    for user in recipients:
        antenna.send_message(recipient=user, subject=subject, message=content)