from typing import Optional

from game.hero import Hero


class SingletonMeta(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class Game(metaclass=SingletonMeta):

    def __init__(self):
        self.player = None
        self.enemy = None
        self.game_processing = False
        self.game_results = ''

    def run(self, player: Hero, enemy: Hero):
        self.player = player
        self.enemy = enemy
        self.game_processing = True

    def _check_hp(self) -> Optional[str]:
        if self.player.hp <= 0 and self.enemy.hp <= 0:
            return self.end_game(results='В этой битве никто не победил')
        if self.player.hp <= 0:
            return self.end_game(results='Игрок проиграл')
        if self.enemy.hp <= 0:
            return self.end_game(results='Игрок победил')
        return None

    def end_game(self, results: str):
        self.game_processing = False
        self.game_results = results
        return results

    def next_turn(self) -> str:
        if results := self._check_hp():
            return results

        if not self.game_processing:
            return self.game_results

        results = self.enemy_hit()
        self._stamina_regenerate()
        return results

    def _stamina_regenerate(self):
        self.player.regenerate_stamina()
        self.enemy.regenerate_stamina()

    def enemy_hit(self) -> str:
        dealt_damage: Optional[float] = self.enemy.hit(self.player)
        if dealt_damage is not None:
            self.player.take_hit(dealt_damage)
            results = f'Enemy deals you {dealt_damage} damage'
        else:
            results = f'Enemy not enough stamina to hit you'
        return results

    def player_hit(self) -> str:
        dealt_damage: Optional[float] = self.player.hit(self.enemy)
        if dealt_damage is not None:
            self.enemy.take_hit(dealt_damage)
            return f'<p>You deals enemy {dealt_damage} damage</p>'f'<p>{self.next_turn()}</p>'
        return f'<p>Not enough stamina to hit</p>'f'<p>{self.next_turn()}</p>'

    def player_use_skill(self) -> str:
        dealt_damage: Optional[float] = self.player.use_skill()
        if dealt_damage is not None:
            self.enemy.take_hit(dealt_damage)
            return f'<p>You deals enemy {dealt_damage} damage</p>'f'<p>{self.next_turn()}</p>'
        return f'<p>Not enough stamina to use skill</p>'f'<p>{self.next_turn()}</p>'