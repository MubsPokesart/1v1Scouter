import asyncio
import aiohttp
import re
import itertools
from util import *

class Scouter:
    def __init__(self, replays=list, names=list):
        self.names = set(names)
        self.replay_list = replays
        self.valid_replays = 0
        self.replay_data = self.retrieve_data(replays)
        self.mon_data = []
        self.completed_data = []
        self.mon_usage = {}
        self.mon_duos = {}
    
    def get_data(self):
        print(self.completed_data)
    
    def find_replay(self, replayid):
        for item in self.replay_list:
            if (item.find(replayid) > -1):
                return item[:item.find('.json')]    
        return "No Replay Availible."

    def find_mon(self, name):
        for mon in self.mon_data:
            if mon.get_name() ==  name:
                return mon
        new_mon = Pokemon(name)
        self.mon_data.append(new_mon)
        return new_mon


    def retrieve_data(self, urls):
        #Some Windows thing: https://stackoverflow.com/questions/45600579/asyncio-event-loop-is-closed-when-getting-loop
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        return [item for item in asyncio.run(main(urls)) if item and item != 'Could not connect']
    
    @staticmethod
    def format_string(text: str):
        text = re.sub('\\[u][a-zA-Z0-9]{4}', '', text)
        text = re.sub('[^a-zA-Z0-9]+', '', text)
        return text.lower().replace(' ', '')

    def add_action(self, team, actions, winner, data):
        team_arr = []
        picked_mon = ''

        if len(actions) > 0:
            picked_mon = actions[0]
            if len(actions) > 1:
                completed_actions = list(set(actions[1:len(actions)]))
            else:
                completed_actions = []
        else:
            completed_actions = []
        
        for mon in team:
            team_arr.append(mon)
            if ((mon == picked_mon) or (mon == 'Urshifu-*' and re.match('Urshifu', picked_mon)) or (mon == 'Silvally' and re.match('Silvally', picked_mon)) or (mon == 'Arceus' and re.match('Arceus', picked_mon))):
                team_arr.append(completed_actions)
        
        team_arr.append({True: 'W', False: 'L'}[winner])
        team_arr.append(self.find_replay(data[0]))

        return team_arr

    def sort_data(self):
        for item in self.replay_data:
            win_start = find_after(item, '|win')
            winner = item[win_start:item.find('\\n', win_start)]
            data_id = re.findall('id":"(.+?)"', item)
            if data_id[1] in self.names:
                player_index = 1
            elif data_id[2] in self.names:
                player_index = 2
            else:
                continue

            item = item.replace('\\n', '')
            
            preview_data = re.findall('p' + str(player_index) + '\|(.+?)\|', item)
            team_preview = preview_data[2:len(preview_data)]
            team_actions = re.findall('\|p' + str(player_index) + 'a: .+?\|(.+?)\|', item)

            team_preview = [re.sub(',.+', '', mon) for mon in team_preview]
            #Mons with multiple forms edge case
            if ('Genesect-*' in team_preview):
                team_preview[team_preview.index('Genesect-*')] = 'Genesect'
            if ('Arceus-*' in team_preview):
                team_preview[team_preview.index('Arceus-*')] = 'Arceus'
            if ('Silvally-*' in team_preview):
                team_preview[team_preview.index('Silvally-*')] = 'Silvally'
            team_preview = [mon for mon in team_preview if find_type(mon) != 'notype']
            team_actions = [re.sub(',.+', '', action) for action in team_actions if re.match('^[A-Z]', action)]
            
            for duo in itertools.combinations(team_preview, 2):
                duo = tuple(sorted(duo))
                if duo in self.mon_duos:
                    self.mon_duos[duo] += 1
                else:
                    self.mon_duos[duo] = 1
            
            if (len(team_preview) == 3):
                self.find_mon(team_preview[0]).add_duos((team_preview[1], team_preview[2]))
                self.find_mon(team_preview[1]).add_duos((team_preview[0], team_preview[2]))
                self.find_mon(team_preview[2]).add_duos((team_preview[1], team_preview[0]))

            check_winner = (data_id[player_index] == self.format_string(winner))

            for mon in team_preview:
                if mon in self.mon_usage:
                    self.mon_usage[mon] += 1
                else:
                    self.mon_usage[mon] = 1

                current_mon = self.find_mon(mon)
                current_mon.increment_brought()
                if check_winner:
                    current_mon.increment_brought_won()

            #Explaining the below code for documentation purposes
            #The people who I made the scouter for asked for consise information with regards to Urshifu and Silvally pick/brought data
            #The issue is with these Pokemon is that they have multiple forms, necessitating very specific usage of methods to get
            #The most useful data possible, which leads to this 'mumbo jumbo' for lack of a better word.
            if (len(team_actions) > 0 and find_type(team_actions[0]) != 'notype'):
                #Urshifu Edge Case
                if re.match('Urshifu', (team_actions[0])):
                    urshifu = self.find_mon('Urshifu-*')
                    urshifu.increment_picked()
                    picked_urshifu = self.find_mon(team_actions[0])
                    picked_urshifu.increment_picked()
                    picked_urshifu.increment_brought()
                    if check_winner:
                        urshifu.increment_picked_won()
                        picked_urshifu.increment_brought_won()
                        picked_urshifu.increment_picked_won()
                #Silvally and Arceus Edge case
                elif re.match('Silvally-', team_actions[0]):
                    silvally = self.find_mon('Silvally')
                    silvally.increment_picked()
                    picked_val = self.find_mon(team_actions[0])
                    picked_val.increment_picked()
                    picked_val.increment_brought()
                    if check_winner:
                        urshifu.increment_picked_won()
                        picked_val.increment_brought_won()
                        picked_val.increment_picked_won()
                elif re.match('Arceus-', team_actions[0]):
                    arceus = self.find_mon('Arceus')
                    arceus.increment_picked()
                    picked_arc = self.find_mon(team_actions[0])
                    picked_arc.increment_picked()
                    picked_arc.increment_brought()
                    if check_winner:
                        arceus.increment_picked_won()
                        picked_arc.increment_brought_won()
                        picked_arc.increment_picked_won()
                else:
                    self.find_mon(team_actions[0]).increment_picked()
                    if check_winner:
                         self.find_mon(team_actions[0]).increment_picked_won()

            #print(f'{team_preview}\n{team_actions}\n{check_winner}\n{data_id}\n\n')

            self.completed_data.append(self.add_action(team_preview, team_actions, check_winner, data_id))
            self.valid_replays += 1
            
    def get_complete_data(self):
        self.sort_data()
        full_data = {}

        if len(self.completed_data) > 0:
            full_data['replays'] = (sorted(self.completed_data, key=lambda item: item[len(item) -1], reverse=True))
            if len(self.mon_data) > 0:
                sorted_mons = sorted(self.mon_data, key=lambda item: item.brought_count, reverse=True)
                usage_data = {}
                for mon in sorted_mons:
                    usage_data[mon.get_name()] = mon.compile_data(self.valid_replays)
                
                full_data['usage'] = usage_data
        
        return full_data

class Pokemon:
    def __init__(self, name):
        self.name = name
        self.brought_count = 0
        self.brought_won = 0
        self.picked_count = 0
        self.picked_won = 0
        self.type = find_type(self.name)
        self.teammates = {}
        self.teammate_duos = {}
        self.type_duos = {}

    def get_name(self):
        return self.name

    def get_type(self):
        return self.type

    def get_brought_count(self):
        return self.brought_count
    
    def get_picked_count(self):
        return self.picked_count

    def get_teammates(self):
        return self.teammates

    def add_teammate(self, name=str):
        if name in self.teammates:
            self.teammates[name] += 1
        else:
            self.teammates[name] = 1
    
    def add_duos(self, duo=tuple):
        duo = tuple(sorted(duo))
        if duo in self.teammate_duos:
            self.teammate_duos[duo] += 1
        else:
            self.teammate_duos[duo] = 1

        self.add_teammate(duo[0])
        self.add_teammate(duo[1])

        type_duo = (find_type(duo[0]), find_type(duo[1]))

        for found_type in type_duo[0]:
            for other_found_type in type_duo[1]:
                type_combo = tuple(sorted([found_type, other_found_type]))
                if type_combo in self.type_duos:
                    self.type_duos[type_combo] += 1
                else:
                    self.type_duos[type_combo] = 1

    def increment_brought(self):
        self.brought_count += 1

    def increment_brought_won(self):
        self.brought_won += 1

    def increment_picked(self):
        self.picked_count += 1
    
    def increment_picked_won(self):
        self.picked_won += 1
    
    def make_json_valid(self, item:dict):
        return dict([(f'{item[0][0]} / {item[0][1]}', item[1]) for item in item.items()])

    def compile_data(self, value):
        if self.brought_count > 0:
            self.type_duos = self.make_json_valid(self.type_duos)
            self.teammate_duos = self.make_json_valid(self.teammate_duos)

            try:
                return ({'brought': self.brought_count, 'brought_percentage': round((self.brought_count/value) * 100, 2), 'brought_win_percentage': round((self.brought_won/self.brought_count) * 100, 2),
                'picked': self.picked_count, 'brought_picked_percentage': round((self.picked_count/self.brought_count) * 100, 2), 'picked_win_percentage': round((self.picked_won/self.picked_count) * 100, 2), 
                'teammates': sort_dict(self.teammates), 'teammate_duos': sort_dict(self.teammate_duos), 'type_duos': sort_dict(self.type_duos)})
            
            except ZeroDivisionError:
                return ({'brought': self.brought_count, 'brought_percentage': round((self.brought_count/value) * 100, 2), 'brought_win_percentage': round((self.brought_won/self.brought_count) * 100, 2),
                'picked': self.picked_count, 'brought_picked_percentage': round((self.picked_count/self.brought_count) * 100, 2), 'picked_win_percentage': 0, 
                'teammates': sort_dict(self.teammates), 'teammate_duos': sort_dict(self.teammate_duos), 'type_duos':sort_dict(self.type_duos)})
        else:
            return ({'brought': 0, 'brought_percentage': 0, 'brought_win_percentage': 0, 'picked': 0, 
            'brought_picked_percentage': 0, 'picked_win_percentage': 0, 'teammates': {}, 'teammate_duos': {}, 'type_duos':{}})

# Two async commands is basic web scrapping. Check out https://youtu.be/lUwZ9rS0SeM?t=234
async def get_page(session, url):
    try:
        async with session.get(url) as r:
            return await r.text()
    except:
        pass

async def main(urls):
    async with aiohttp.ClientSession() as session:
        return await asyncio.gather(*(get_page(session, url) for url in urls))


def get_data(form_text, players):
    if (players.find(',') > -1):
        players = {Scouter.format_string(p) for p in players.split(', ')}
    else:
        players = [Scouter.format_string(players)]
    replays_list = [f'{replay.rstrip()}.json' for replay in form_text.split('\n') if re.match('^https://replay.pokemonshowdown.com.+?gen.1v1', replay)]
    REPLAY_SCOUTER = Scouter(replays_list, players)
    return (REPLAY_SCOUTER.get_complete_data())

def convertUsage(usage_data):
    try:
        usage_data = usage_data['usage']
        usage_data = dict(sorted(usage_data.items(),key=lambda item: item[1]['brought'],reverse=True))
        returned_string = ''
        for key, value in usage_data.items():
            returned_string += ('+----------------------------------------+')
            returned_string += (f'\n{box_string(42, key)}')
            returned_string += ('\n+----------------------------------------+')
            message = (f'Brought: {value["brought"]} ({value["brought_percentage"]}%)')
            returned_string += (f'\n{box_string(42, message)}')
            message = (f'Won when brought: {value["brought_win_percentage"]}%')
            returned_string += (f'\n{box_string(42, message)}')
            message = (f' - Picked: {value["picked"]} (Win %: {value["picked_win_percentage"]}%)')
            returned_string += (f'\n{box_string(42, message)}')
            returned_string += ('\n+----------------------------------------+')
            returned_string += (f'\n{box_string(42, "[Teammates]")}')
            returned_string += ('\n+----------------------------------------+')
            for key1, value1 in value['teammates'].items():
                returned_string += (f'\n{box_string(42, key1, str(value1))}')
            returned_string += ('\n+----------------------------------------+')
            returned_string += (f'\n{box_string(42, "[Type Duos]")}')
            returned_string += ('\n+----------------------------------------+')
            for key1, value1 in value['type_duos'].items():
                returned_string += (f'\n{box_string(42, key1, str(value1))}')
            returned_string += ('\n+----------------------------------------+')
            returned_string += ('\n\n')
        return returned_string
    except:
        return 'Failed to Parse.'