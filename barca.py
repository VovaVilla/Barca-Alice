from bs4 import BeautifulSoup
import requests
import datetime
import os


def getDateTTS(datestr):
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


def getLastMatch():
    link = "https://m.liveresult.ru/football/teams/Barcelona/"

    page_source = requests.get(link, timeout=3).content

    soup = BeautifulSoup(page_source, 'html.parser')

    mb4 = soup.findAll("div", {"class": "mb-4"})
    last_matches = mb4[1].findAll('a', {"class": "matches-list-match"})
    last_match_time_date = last_matches[0].findAll('span', {"class": "match-time-date"})
    last_match_team1 = last_matches[0].findAll('span', {"class": "team1"})
    last_match_team2 = last_matches[0].findAll('span', {"class": "team2"})
    last_match_tournament = last_matches[0].findAll('abbr')
    last_match_score = last_matches[0].findAll('span', {"class": "has-score"})

    last_date = last_match_time_date[0].text
    last_team1 = last_match_team1[0].text
    last_team2 = last_match_team2[0].text
    last_team2 = last_team2.replace("\n", "")
    last_score = last_match_score[0].text.replace(":", " - ")
    last_tournament = last_match_tournament[0].text

    return {'date': last_date, 'team1': last_team1, 'team2': last_team2, 'score': last_score,
            'tournament': last_tournament}


def getNextMatch():
    link = "https://m.liveresult.ru/football/teams/Barcelona/"

    page_source = requests.get(link, timeout=3).content

    soup = BeautifulSoup(page_source, 'html.parser')

    mb4 = soup.findAll("div", {"class": "mb-4"})
    next_matches = mb4[0].findAll('a', {"class": "matches-list-match"})
    next_match_time_date = next_matches[0].findAll('span', {"class": "match-time-date"})
    next_match_team1 = next_matches[0].findAll('span', {"class": "team1"})
    next_match_team2 = next_matches[0].findAll('span', {"class": "team2"})
    next_match_tournament = next_matches[0].findAll('abbr')

    next_date = next_match_time_date[0].text
    next_time = next_match_time_date[1].text
    next_team1 = next_match_team1[0].text
    next_team2 = next_match_team2[0].text
    next_team2 = next_team2.replace("\n", "")
    next_tournament = next_match_tournament[0].text

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
    text = "Привет! Вы можете спросить как закончился последний матч каталонцев или когда, с кем и во сколько будет следующая игра Барселоны. Просто спросите."
    tts = "Привет! Вы можете спросить как закончился последний матч каталонцев или когда, с кем и во сколько будет следующая игра Барселоны. Просто спросите."

    end_session = 'false'
    if 'request' in event and \
            'original_utterance' in event['request'] \
            and len(event['request']['original_utterance']) > 0:

        origin_utter = event['request']['original_utterance'].lower()

        # next game
        if "следующ" in origin_utter or "когда" in origin_utter or "как скоро" in origin_utter or "во сколько" in origin_utter or "ближайш" in origin_utter or "предстоящ" in origin_utter or "будущ" in origin_utter or "next" in origin_utter:
            info = getNextMatch()
            text = f"Следующий матч {info['team1']} - {info['team2']} состоится {info['date']} в {info['time']}. {info['tournament']}."
            date_tts = getDateTTS(info['date'])
            tts = f"Следующий матч {info['team1']} - {info['team2']} состоится {date_tts} в {info['time']}. {info['tournament']}."

        # last game
        if "последн" in origin_utter or "предыдущ" in origin_utter or "счет" in origin_utter or "счёт" in origin_utter or "прошёл" in origin_utter or "прошел" in origin_utter or "закончил" in origin_utter or "завершил" in origin_utter or "сыграл" in origin_utter or "итог" in origin_utter or "результат" in origin_utter:
            info = getLastMatch()
            text = f"Матч {info['team1']} - {info['team2']} завершился со счетом {info['score']}. {info['tournament']}."
            date_tts = getDateTTS(info['date'])
            tts = f"Матч {info['team1']} - {info['team2']} завершился со счетом {info['score']}. {info['tournament']}."

        # # goals
        # if "забил" in origin_utter or "забивал" in origin_utter or "автор" in origin_utter or "гол" in origin_utter:
        #     text = "За Барселону забивали Артуро Видаль на 39 минуте и Арамбарри на 89 в свои ворота."

        # help
        if "помощь" in origin_utter or "помоги" in origin_utter or "умеешь" in origin_utter or "могу" in origin_utter:
            text = "Привет! Вы можете спросить как закончился последний матч каталонцев или когда, с кем и во сколько будет следующая игра Барселоны. Просто спросите."
            tts = "Привет! Вы можете спросить как закончился последний матч каталонцев или когда, с кем и во сколько будет следующая игра Барселоны. Просто спросите."

        # end
        if "спасиб" in origin_utter or "хватит" in origin_utter or "выход" in origin_utter or "понятн" in origin_utter or "понял" in origin_utter or "ясно" in origin_utter:
            text = "Обращайтесь."
            tts = "Обращайтесь."
            end_session = 'true'

    return {
        'version': event['version'],
        'session': event['session'],
        'response': {
            # Respond with the original request or welcome the user if this is the beginning of the dialog and the request has not yet been made.
            'text': text,
            'tts': tts,
            # Don't finish the session after this response.
            'end_session': end_session
        },
    }
