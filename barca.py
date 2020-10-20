# coding=utf-8
"""
The module contains functions for the operation of Alice's
"Football Club Barcelona"
skill on the Yandex.Dialogs platform.
"""

from bs4 import BeautifulSoup
import requests
import datetime


def getDateTTS(datestr):
    """
    :param datestr: Date in numeric format, string
    :return: Date in text format on russian for TTS
    """
    date = datetime.datetime.strptime(datestr, '%d.%m.%Y')
    day_list = ['первого', 'второго', 'третьего', 'четвёртого',
                'пятого', 'шестого', 'седьмого', 'восьмого',
                'девятого', 'десятого', 'одиннадцатого', 'двенадцатого',
                'тринадцатого', 'четырнадцатого', 'пятнадцатого', 'шестнадцатого',
                'семнадцатого', 'восемнадцатого', 'девятнадцатого', 'двадцатого',
                'двадцать первого', 'двадцать второго', 'двадцать третьего',
                'двадацать четвёртого', 'двадцать пятого', 'двадцать шестого',
                'двадцать седьмого', 'двадцать восьмого', 'двадцать девятого',
                'тридцатого', 'тридцать первого']
    month_list = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
                  'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']

    day = day_list[date.day - 1]
    month = month_list[int(date.month) - 1]

    return f"{day} {month}"

def getSourcePageSoup(link):
    """
    Get BeautifulSoup data from link
    :param link: Page source link
    :return: BeautifulSoup structure
    """
    page_source = requests.get(link, timeout=3).content
    return BeautifulSoup(page_source, 'html.parser')


def getLastMatch():
    """
    :return: Dictionary with info about the last match of FCB
    """
    soup = getSourcePageSoup("https://m.liveresult.ru/football/teams/Barcelona/")

    # get info
    mb4 = soup.findAll("div", {"class": "mb-4"})
    last_matches = mb4[1].findAll('a', {"class": "matches-list-match"})
    last_date = last_matches[0].findAll('span', {"class": "match-time-date"})[0].text
    last_team1 = last_matches[0].findAll('span', {"class": "team1"})[0].text
    last_team2 = last_matches[0].findAll('span', {"class": "team2"})[0].text
    last_team2 = last_team2
    last_tournament = last_matches[0].findAll('abbr')[0].text
    last_score = last_matches[0].findAll('span', {"class": "has-score"})[0].text
    last_score = last_score.replace(":", " - ")

    return {'date': last_date, 'team1': last_team1, 'team2': last_team2, 'score': last_score,
            'tournament': last_tournament}


def getNextMatch():
    """
    :return: Dictionary with info about the next match of FCB
    """
    soup = getSourcePageSoup("https://m.liveresult.ru/football/teams/Barcelona/")

    # get info
    mb4 = soup.findAll("div", {"class": "mb-4"})
    next_matches = mb4[0].findAll('a', {"class": "matches-list-match"})
    next_time_date = next_matches[0].findAll('span', {"class": "match-time-date"})
    next_date = next_time_date[0].text
    next_time = next_time_date[1].text
    next_team1 = next_matches[0].findAll('span', {"class": "team1"})[0].text
    next_team2 = next_matches[0].findAll('span', {"class": "team2"})[0].text
    next_team2 = next_team2.replace("\n", "")
    next_tournament = next_matches[0].findAll('abbr')[0].text

    return {'date': next_date, 'time': next_time, 'team1': next_team1, 'team2': next_team2,
            'tournament': next_tournament}


def handler(event, context):
    """
    Entry-point for Serverless Function.
    :param event: request payload.
    :param context: information about current execution context.
    :return: response to be serialized as JSON.
    """

    # hello text
    text = "Привет! Вы можете спросить как закончился последний матч каталонцев или когда," \
           " с кем и во сколько будет следующая игра Барселоны. Просто спросите."
    tts = "Привет! Вы можете спросить как закончился последний матч каталонцев или когда, " \
          "с кем и во сколько будет следующая игра Барселоны. Просто спросите."

    end_session = 'false'
    if 'request' in event and \
            'original_utterance' in event['request'] \
            and len(event['request']['original_utterance']) > 0:

        origin_utter = event['request']['original_utterance'].lower()

        # next game
        if "следующ" in origin_utter or "когда" in origin_utter or "как скоро" in origin_utter \
                or "во сколько" in origin_utter or "ближайш" in origin_utter or "предстоящ" in origin_utter \
                or "будущ" in origin_utter or "next" in origin_utter:
            try:
                info = getNextMatch()
                text = f"Следующий матч {info['team1']} - {info['team2']} состоится {info['date']} " \
                       f"в {info['time']}. {info['tournament']}."
                date_tts = getDateTTS(info['date'])
                tts = f"Следующий матч {info['team1']} - {info['team2']} состоится {date_tts} " \
                      f"в {info['time']}. {info['tournament']}."
            except:
                text = f"Извините, произошла ошибка получения информации"
                tts = f"Извините, произошла ошибка получения информации"

        # last game
        if "последн" in origin_utter or "предыдущ" in origin_utter or "счет" in origin_utter or "счёт" in origin_utter \
                or "прошёл" in origin_utter or "прошел" in origin_utter or "закончил" in origin_utter \
                or "завершил" in origin_utter or "сыграл" in origin_utter or "итог" in origin_utter \
                or "результат" in origin_utter:
            try:
                info = getLastMatch()
                text = f"Матч {info['team1']} - {info['team2']} завершился " \
                       f"со счетом {info['score']}. {info['tournament']}."

                tts = f"Матч {info['team1']} - {info['team2']} завершился " \
                      f"со счетом {info['score']}. {info['tournament']}."
            except:
                text = f"Извините, произошла ошибка получения информации"
                tts = f"Извините, произошла ошибка получения информации"

        # help
        if "помощь" in origin_utter or "помоги" in origin_utter or "умеешь" in origin_utter or "могу" in origin_utter:
            text = "Чтобы узнать, когда и с кем будет следующая игра, спросите Когда следующая игра? " \
                   "Во сколько матч? Ближайшая игра. Также вы можете спросить как закончилась последняя встеча: " \
                   "Как прошел матч? Как закончилась последняя игра? Какой счет в матче?"

            tts = "Чтобы узнать, когда и с кем будет следующая игра, спросите  когда следующая игра? во сколько матч? " \
                  "ближайшая игра. Также вы можете спросить как закончилась последняя встеча: " \
                  "Как прошел матч?, как закончилась последняя игра?, какой счет в матче?"

        # end
        if "спасиб" in origin_utter or "хватит" in origin_utter or "выход" in origin_utter or "понятн" in origin_utter or "понял" in origin_utter or "ясно" in origin_utter:
            text = "Обращайтесь."
            tts = "Обращайтесь."
            end_session = 'true'

    return {
        'version': event['version'],
        'session': event['session'],
        'response': {
            # Respond with the original request or welcome the user if this is the beginning of the dialog and
            # the request has not yet been made.
            'text': text,
            'tts': tts,
            # Don't finish the session after this response.
            'end_session': end_session
        },
    }
