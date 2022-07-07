from functools import wraps
from typing import Dict, Type

from flask import Flask, render_template, request, redirect, url_for

from game.controller import Game
from game.equipment import EquipmentData
from game.hero import Hero, Enemy, Player
from game.personages import personage_classes
from game.utils import load_equipment

app = Flask(__name__)
app.url_map.strict_slashes = False

heroes: Dict[str, Hero] = dict()

EQUIPMENT: EquipmentData = load_equipment()

game = Game()


def game_processing(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if game.game_processing:
            return func(*args, **kwargs)
        if game.game_results:
            return render_template('fight.html', heroes=heroes, resoult=game.game_results)
        return redirect(url_for('index'))

    return wrapper


def render_choose_personage_template(*args, **kwargs) -> str:
    return render_template(
        'hero_choosing.html',
        classes=personage_classes.values(),
        equipment=EQUIPMENT,
        **kwargs
    )


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/choose-hero/', methods=['GET', 'POST'])
def choose_hero():
    if request.method == 'GET':
        return render_choose_personage_template(header='Выберете героя', next_button='Выберете врага')

    heroes['player'] = Player(
        class_=personage_classes[request.form['unit_class']],
        weapon=EQUIPMENT.get_weapon(request.form['weapon']),
        armor=EQUIPMENT.get_armor(request.form['armor']),
        name=request.form['name']
    )
    return redirect(url_for('choose_enemy'))


@app.route('/choose-enemy/', methods=['GET', 'POST'])
def choose_enemy():
    if request.method == 'GET':
        return render_choose_personage_template(header='Выберете врага', next_button='Начать сражение')

    heroes['enemy'] = Enemy(
        class_=personage_classes[request.form['unit_class']],
        weapon=EQUIPMENT.get_weapon(request.form['weapon']),
        armor=EQUIPMENT.get_armor(request.form['armor']),
        name=request.form['name']
    )

    return redirect(url_for('start_fight'))


@app.route('/fight')
def start_fight():
    if 'player' in heroes and 'enemy' in heroes:
        game.run(**heroes)
        return render_template('fight.html', heroes=heroes, resoult='Fight!')
    return redirect(url_for('index'))


@app.route('/fight/hit')
@game_processing
def hit():
    return render_template('fight.html', heroes=heroes, resoult=game.player_hit())


@app.route('/fight/use-skill')
@game_processing
def user_skill():
    return render_template('fight.html', heroes=heroes, resoult=game.player_use_skill())


@app.route('/fight/pass-turn')
@game_processing
def pass_turn():
    return render_template('fight.html', heroes=heroes, resoult=game.next_turn())


@app.route('/fight/end-fight')
def end_fight():
    return redirect(url_for('index'))
