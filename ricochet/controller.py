import sys
import math
import asyncio
import pygame

from .model import Board
from .view import Renderer, COLORS
from .audio import Audio
from .animation import SlideAnimation, ParticleSystem, FlashEffect


DRAG_THRESHOLD = 8
ARROW_DIRS = [('up', (0, -1)), ('down', (0, 1)),
              ('left', (-1, 0)), ('right', (1, 0))]


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("碰撞機器人 (Ricochet Robots)")
        self.board = Board()
        screen_w = self.board.width * 40
        screen_h = self.board.height * 40 + 60 + 100
        self.screen = pygame.display.set_mode((screen_w, screen_h), pygame.RESIZABLE)
        self.renderer = Renderer(self.screen, self.board)
        self.audio = Audio()
        self.particles = ParticleSystem()
        self.flash = None
        self.anim = None
        self.show_hint = False
        self.hover_robot = None
        self.drag = None
        self.is_touch = False
        self.arrow_robot = None
        self.arrow_rects = {}

    def _robot_under(self, mx, my):
        cell = self.renderer.px_to_cell(mx, my)
        if not cell: return None
        return self.board.get_robot_at(*cell)

    def _arrow_hit(self, mx, my):
        for d, rect in self.arrow_rects.items():
            if rect.collidepoint(mx, my):
                return d
        return None

    def _start_move(self, color, dx, dy):
        if self.anim or self.board.won or self.board.calculating: return
        info = self.board.apply_move(color, dx, dy)
        if not info: return
        self.audio.slide()
        self.anim = SlideAnimation(color, info['start'], info['end'],
                                   info['dir'], won=info['won'])
        self.arrow_robot = None

    def _on_anim_end(self):
        if not self.anim: return
        color = self.anim.color
        ex, ey = self.anim.end
        cx_px, cy_px = self.renderer.cell_center_px(ex, ey)
        dx, dy = self.anim.direction
        if self.anim.won:
            self.audio.win()
            self.particles.emit_burst(cx_px, cy_px, COLORS[color],
                                      count=32, speed_range=(0.08, 0.28), life=750)
            self.flash = FlashEffect(COLORS[color], duration_ms=420, max_alpha=110)
        else:
            self.audio.thunk()
            self.particles.emit_directional(cx_px, cy_px, dx, dy, COLORS[color])
        self.anim = None

    def _handle_mousedown(self, ev):
        if ev.button != 1: return
        self.board.show_optimal = True
        if self.anim or self.board.won or self.board.calculating: return

        if self.arrow_robot:
            dname = self._arrow_hit(*ev.pos)
            if dname:
                ddx, ddy = dict(ARROW_DIRS)[dname]
                self._start_move(self.arrow_robot, ddx, ddy)
                return

        robot = self._robot_under(*ev.pos)
        if robot:
            self.drag = {
                'robot': robot,
                'start_px': ev.pos,
                'cur_px': ev.pos,
            }
            self.board.selected_robot = robot
        else:
            self.arrow_robot = None

    def _handle_mousemotion(self, ev):
        if not self.is_touch and not self.drag and not self.anim:
            self.hover_robot = self._robot_under(*ev.pos)
        if self.drag:
            self.drag['cur_px'] = ev.pos

    def _handle_mouseup(self, ev):
        if ev.button != 1 or not self.drag: return
        drag = self.drag
        self.drag = None
        sx, sy = drag['start_px']
        cx, cy = drag['cur_px']
        ddx = cx - sx
        ddy = cy - sy
        if math.hypot(ddx, ddy) < DRAG_THRESHOLD:
            self.audio.select()
            self.arrow_robot = drag['robot']
            return
        if abs(ddx) > abs(ddy):
            dx, dy = (1 if ddx > 0 else -1), 0
        else:
            dx, dy = 0, (1 if ddy > 0 else -1)
        self._start_move(drag['robot'], dx, dy)

    def _handle_keydown(self, ev):
        if ev.key == pygame.K_UP: self._key_move(0, -1)
        elif ev.key == pygame.K_DOWN: self._key_move(0, 1)
        elif ev.key == pygame.K_LEFT: self._key_move(-1, 0)
        elif ev.key == pygame.K_RIGHT: self._key_move(1, 0)
        elif ev.key == pygame.K_h:
            self.show_hint = not self.show_hint
        elif ev.key == pygame.K_r:
            if not self.anim:
                self.board.reset_robots()
                self.flash = None
                self.arrow_robot = None
        elif ev.key == pygame.K_SPACE:
            self.board.select_next_target()
            self.anim = None
            self.flash = None
            self.particles.particles.clear()
            self.arrow_robot = None
        elif ev.key == pygame.K_n:
            self.board.generate_random_board()
            self.anim = None
            self.flash = None
            self.particles.particles.clear()
            self.arrow_robot = None

    def _key_move(self, dx, dy):
        if self.board.selected_robot:
            self._start_move(self.board.selected_robot, dx, dy)

    def _render(self):
        self.arrow_rects = self.renderer.render(
            anim=self.anim,
            particles=self.particles,
            flash=self.flash,
            hover_robot=self.hover_robot if not self.is_touch else None,
            drag_state=self.drag,
            show_hint=self.show_hint,
            arrow_robot=self.arrow_robot,
        )

    async def run(self):
        clock = pygame.time.Clock()
        last = pygame.time.get_ticks()
        while True:
            now = pygame.time.get_ticks()
            dt = now - last
            last = now

            if self.board.calculating:
                done = self.board.solve_bfs_step(budget=1200)
                if done:
                    if 4 <= self.board.optimal_steps <= 20:
                        self.board.calculating = False
                    else:
                        self.board.generate_random_board()

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif ev.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(
                        (ev.w, ev.h), pygame.RESIZABLE)
                    self.renderer.set_screen(self.screen)
                    self.renderer.on_resize(ev.w, ev.h)
                elif hasattr(pygame, 'WINDOWRESIZED') and ev.type == pygame.WINDOWRESIZED:
                    w, h = self.screen.get_size()
                    self.renderer.on_resize(w, h)
                elif hasattr(pygame, 'FINGERDOWN') and ev.type == pygame.FINGERDOWN:
                    self.is_touch = True
                    self.hover_robot = None
                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_mousedown(ev)
                elif ev.type == pygame.MOUSEMOTION:
                    self._handle_mousemotion(ev)
                elif ev.type == pygame.MOUSEBUTTONUP:
                    self._handle_mouseup(ev)
                elif ev.type == pygame.KEYDOWN:
                    self._handle_keydown(ev)

            if self.anim and self.anim.done:
                self._on_anim_end()
            self.particles.update(dt)
            if self.flash and self.flash.done:
                self.flash = None

            self._render()
            clock.tick(60)
            await asyncio.sleep(0)
