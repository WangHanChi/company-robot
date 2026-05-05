import math
import copy
import os
import pygame

from .model import CENTER_BLOCK, COLOR_ZH, ZH_TO_COLOR


# _BUNDLED_FONT = os.path.join(
#     os.path.dirname(os.path.abspath(__file__)),
#     '..', 'assets', 'fonts', 'NotoSansTC-Regular.ttf')
_BUNDLED_FONT = "assets/fonts/NotoSansTC-Regular.ttf"

COLORS = {
    'Red': (220, 50, 50),
    'Blue': (50, 100, 220),
    'Green': (50, 200, 50),
    'Yellow': (220, 200, 50),
    'Black': (40, 40, 40),
    'White': (245, 245, 245),
    'Gray': (200, 200, 200),
    'Highlight': (200, 255, 200),
    'Panel': (230, 230, 235),
    'CellLight': (248, 248, 242),
    'CellDark': (238, 238, 230),
}


class Renderer:
    def __init__(self, screen, board):
        self.screen = screen
        self.board = board
        self.cell_size = 40
        self.margin_top = 60
        self.margin_bottom = 100
        self.offset_x = 0
        if os.path.exists(_BUNDLED_FONT):
            self._font_path = _BUNDLED_FONT
        else:
            self._font_path = pygame.font.match_font(
                'stheitilight,arialunicode,pingfanghk,microsoftjhonghei,simhei,'
                'notosanscjk,notosanscjktc,notosanscjksc,notosansctc,'
                'wqyzenhei,wqymicrohei,droidsansfallback,unifont'
            )
        self.font = None
        self.title_font = None
        self.on_resize(*screen.get_size())

    def set_screen(self, screen):
        self.screen = screen

    def on_resize(self, w, h):
        cs_h = h // 20
        if cs_h < 32:
            cs_h = (h - 125) // 16
        self.cell_size = max(20, min(w // self.board.width, cs_h))
        self.margin_top = max(45, int(self.cell_size * 1.5))
        self.margin_bottom = max(80, int(self.cell_size * 2.5))
        self.offset_x = (w - self.board.width * self.cell_size) // 2
        self._load_fonts()

    def _load_fonts(self):
        cs = self.cell_size
        size = max(14, cs // 2)
        title_size = max(16, cs // 2 + 4)
        if self._font_path:
            self.font = pygame.font.Font(self._font_path, size)
            self.title_font = pygame.font.Font(self._font_path, title_size)
        else:
            self.font = pygame.font.Font(None, size + 4)
            self.title_font = pygame.font.Font(None, title_size + 4)

    def cell_center_px(self, cx, cy):
        cs = self.cell_size
        return (self.offset_x + cx * cs + cs // 2,
                self.margin_top + cy * cs + cs // 2)

    def px_to_cell(self, mx, my):
        cs = self.cell_size
        if cs <= 0: return None
        gx = (mx - self.offset_x) // cs
        gy = (my - self.margin_top) // cs
        if 0 <= gx < self.board.width and 0 <= gy < self.board.height:
            return int(gx), int(gy)
        return None

    def render(self, *, anim=None, particles=None, flash=None,
               hover_robot=None, drag_state=None, show_hint=False,
               arrow_robot=None):
        self.screen.fill(COLORS['White'])
        cs = self.cell_size
        ox = self.offset_x
        oy = self.margin_top
        gw = self.board.width * cs
        gh = self.board.height * cs

        screen_w, screen_h = self.screen.get_size()
        pygame.draw.rect(self.screen, COLORS['Panel'], (0, 0, screen_w, oy))
        pygame.draw.rect(self.screen, COLORS['Panel'],
                         (0, oy + gh, screen_w, max(0, screen_h - oy - gh)))
        pygame.draw.line(self.screen, COLORS['Gray'], (0, oy), (screen_w, oy), 1)
        pygame.draw.line(self.screen, COLORS['Gray'],
                         (0, oy + gh), (screen_w, oy + gh), 1)

        self._draw_status_text()
        self._draw_grid()
        self._draw_target()
        self._draw_selection(anim)
        self._draw_walls()
        if hover_robot and not drag_state and not anim and not self.board.won:
            self._draw_path_preview(hover_robot)
        if drag_state and not anim:
            self._draw_drag_indicator(drag_state)
        self._draw_robots(anim)
        arrow_rects = {}
        if arrow_robot and not anim and not self.board.won and not drag_state:
            arrow_rects = self._draw_direction_buttons(arrow_robot)
        self._draw_controls()
        if self.board.calculating:
            self._draw_spinner()
        if show_hint:
            self._draw_hint()
        if particles is not None:
            particles.draw(self.screen)
        if flash and not flash.done:
            self._draw_flash(flash)

        pygame.display.flip()
        return arrow_rects

    def _draw_status_text(self):
        b = self.board
        tc, tx, ty, _ = b.current_target
        tname = COLOR_ZH[tc]
        if b.calculating:
            opt_str = "計算最佳解中..."
        elif b.show_optimal:
            opt_str = (f"最佳解: {b.optimal_steps} 步" if b.optimal_steps != -1
                       else "最佳解: 20步以上 (或無解)")
        else:
            opt_str = "最佳解: (點擊畫面顯示)"
        if b.won:
            msg = f"太棒了！共花 {b.moves} 步。按「空白鍵」下一關！"
            color = COLORS['Green']
        else:
            msg = f"目標：【{tname}色】到方塊處 (已走:{b.moves}步 | {opt_str})"
            color = COLORS['Black']
        surf = self.title_font.render(msg, True, color)
        h = surf.get_height()
        self.screen.blit(surf, (self.offset_x, (self.margin_top - h) // 2))

    def _draw_grid(self):
        cs = self.cell_size
        ox = self.offset_x
        oy = self.margin_top
        for x in range(self.board.width):
            for y in range(self.board.height):
                rect = pygame.Rect(ox + x * cs, oy + y * cs, cs, cs)
                if (x, y) in CENTER_BLOCK:
                    pygame.draw.rect(self.screen, COLORS['Black'], rect)
                else:
                    cc = COLORS['CellDark'] if (x + y) % 2 == 0 else COLORS['CellLight']
                    pygame.draw.rect(self.screen, cc, rect)
                pygame.draw.rect(self.screen, COLORS['Gray'], rect, 1)

    def _draw_target(self):
        cs = self.cell_size
        ox = self.offset_x
        oy = self.margin_top
        tc, tx, ty, _ = self.board.current_target
        pulse = abs(math.sin(pygame.time.get_ticks() / 500)) * (cs // 8)
        inner = max(2, cs // 4 - int(pulse))
        rect = pygame.Rect(ox + tx * cs + inner, oy + ty * cs + inner,
                           cs - inner * 2, cs - inner * 2)
        pygame.draw.rect(self.screen, COLORS[tc], rect, border_radius=max(2, inner))
        pygame.draw.rect(self.screen, COLORS['Black'], rect, 2, border_radius=max(2, inner))

    def _draw_selection(self, anim):
        b = self.board
        if not b.selected_robot or b.won: return
        if anim and anim.color == b.selected_robot: return
        cs = self.cell_size
        rx, ry = b.robots[b.selected_robot]
        rect = pygame.Rect(self.offset_x + rx * cs, self.margin_top + ry * cs, cs, cs)
        pygame.draw.rect(self.screen, COLORS['Highlight'], rect, 0)

    def _draw_walls(self):
        b = self.board
        cs = self.cell_size
        ox = self.offset_x
        oy = self.margin_top
        wt = max(2, cs // 10)
        for y in range(b.height):
            for x in range(b.width):
                x0 = ox + x * cs
                y0 = oy + y * cs
                if b.h_walls[y][x] or y == 0:
                    pygame.draw.line(self.screen, COLORS['Black'],
                                     (x0, y0), (x0 + cs, y0), wt)
                if b.v_walls[y][x] or x == 0:
                    pygame.draw.line(self.screen, COLORS['Black'],
                                     (x0, y0), (x0, y0 + cs), wt)
        gw = b.width * cs
        gh = b.height * cs
        pygame.draw.line(self.screen, COLORS['Black'],
                         (ox, oy + gh), (ox + gw, oy + gh), wt)
        pygame.draw.line(self.screen, COLORS['Black'],
                         (ox + gw, oy), (ox + gw, oy + gh), wt)

    def _draw_robots(self, anim):
        b = self.board
        cs = self.cell_size
        radius = max(5, cs // 2 - cs // 8)
        for name, pos in b.robots.items():
            if anim and anim.color == name:
                cx, cy = anim.current_cell()
                center = (self.offset_x + cx * cs + cs // 2,
                          self.margin_top + cy * cs + cs // 2)
            else:
                center = self.cell_center_px(pos[0], pos[1])
            ix, iy = int(center[0]), int(center[1])
            pygame.draw.circle(self.screen, COLORS[name], (ix, iy), radius)
            pygame.draw.circle(self.screen, COLORS['Black'], (ix, iy), radius, 2)
            if name == b.selected_robot and not b.won and not anim:
                pygame.draw.circle(self.screen, COLORS['Black'], (ix, iy), radius + 2, 4)

    def _draw_path_preview(self, robot):
        cs = self.cell_size
        sx, sy = self.cell_center_px(*self.board.robots[robot])
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            ex, ey = self.board.predict(robot, dx, dy)
            if (ex, ey) == tuple(self.board.robots[robot]):
                continue
            ecx, ecy = self.cell_center_px(ex, ey)
            self._draw_dashed(sx, sy, ecx, ecy, COLORS[robot],
                              dash=max(4, cs // 6), width=max(2, cs // 14))
            r = max(4, cs // 4)
            ghost = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(ghost, (*COLORS[robot], 90), (r + 2, r + 2), r)
            pygame.draw.circle(ghost, (*COLORS['Black'], 130), (r + 2, r + 2), r, 2)
            self.screen.blit(ghost, (ecx - r - 2, ecy - r - 2))

    def _draw_dashed(self, x1, y1, x2, y2, color, dash=8, width=3):
        dxv = x2 - x1
        dyv = y2 - y1
        dist = math.hypot(dxv, dyv)
        if dist < 1: return
        nx = dxv / dist
        ny = dyv / dist
        t = 0.0
        while t < dist:
            seg_end = min(t + dash, dist)
            sx = x1 + nx * t
            sy = y1 + ny * t
            ex = x1 + nx * seg_end
            ey = y1 + ny * seg_end
            pygame.draw.line(self.screen, color, (sx, sy), (ex, ey), width)
            t += dash * 2

    def _draw_drag_indicator(self, drag):
        sx, sy = drag['start_px']
        ex, ey = drag['cur_px']
        cs = self.cell_size
        rc = drag['robot']
        pygame.draw.line(self.screen, COLORS[rc], (sx, sy), (ex, ey),
                         max(2, cs // 12))
        pygame.draw.circle(self.screen, COLORS[rc], (int(ex), int(ey)),
                           max(4, cs // 10))
        ddx = ex - sx; ddy = ey - sy
        if math.hypot(ddx, ddy) > 8:
            if abs(ddx) > abs(ddy):
                dx, dy = (1 if ddx > 0 else -1), 0
            else:
                dx, dy = 0, (1 if ddy > 0 else -1)
            rxe, rye = self.board.predict(rc, dx, dy)
            rsx, rsy = self.board.robots[rc]
            if (rxe, rye) != (rsx, rsy):
                rscx, rscy = self.cell_center_px(rsx, rsy)
                recx, recy = self.cell_center_px(rxe, rye)
                self._draw_dashed(rscx, rscy, recx, recy, COLORS[rc],
                                  dash=max(4, cs // 6), width=max(2, cs // 12))
                r = max(5, cs // 3)
                ghost = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(ghost, (*COLORS[rc], 140), (r + 2, r + 2), r)
                pygame.draw.circle(ghost, (*COLORS['Black'], 180), (r + 2, r + 2), r, 2)
                self.screen.blit(ghost, (recx - r - 2, recy - r - 2))

    def _draw_controls(self):
        cs = self.cell_size
        b = self.board
        gh = b.height * cs
        gw = b.width * cs
        oy = self.margin_top
        ox = self.offset_x

        key_defs = [('↑↓←→', '移動'), ('R', '回原位'), ('H', '提示'),
                    ('空白', '換目標'), ('N', '重生')]
        key_color = (60, 60, 80)
        bg_color = (210, 210, 218)
        pad_x = max(3, cs // 10)
        pad_y = max(2, cs // 14)
        gap = pad_x * 3
        text_y = oy + gh + cs // 3

        rendered = [(self.font.render(k, True, key_color),
                     self.font.render(d, True, COLORS['Black'])) for k, d in key_defs]
        total_w = sum(ks.get_width() + pad_x * 2 + ds.get_width()
                      for ks, ds in rendered) + gap * (len(rendered) - 1)
        kx = ox + (gw - total_w) // 2

        for ks, ds in rendered:
            kw = ks.get_width() + pad_x * 2
            kh = ks.get_height() + pad_y * 2
            pygame.draw.rect(self.screen, bg_color, (kx, text_y, kw, kh),
                             border_radius=max(2, cs // 16))
            pygame.draw.rect(self.screen, (150, 150, 165), (kx, text_y, kw, kh),
                             1, border_radius=max(2, cs // 16))
            self.screen.blit(ks, (kx + pad_x, text_y + pad_y))
            self.screen.blit(ds, (kx + kw + pad_x, text_y + pad_y))
            kx += kw + ds.get_width() + gap

    def _draw_hint(self):
        b = self.board
        cs = self.cell_size
        ox = self.offset_x
        oy = self.margin_top
        gh = b.height * cs

        if not (b.optimal_steps != -1 and b.solution_path):
            if b.calculating:
                s = self.font.render("解答: 計算中...", True, COLORS['Blue'] if 'Blue' in COLORS else (50, 100, 220))
            else:
                s = self.font.render("解答: 20 步內無解 (按 N 重生)", True, (50, 100, 220))
            self.screen.blit(s, (ox, oy + gh + cs))
            return

        sim = copy.deepcopy(b.initial_robots)
        dmap = {'上': (0, -1), '下': (0, 1), '左': (-1, 0), '右': (1, 0)}

        for idx, (color_zh, dn) in enumerate(b.solution_path):
            rc = ZH_TO_COLOR.get(color_zh)
            if not rc: continue
            dx, dy = dmap.get(dn, (0, 0))
            cx0, cy0 = sim[rc]
            shift_unit = cs // 8
            sh = (idx % 3) * shift_unit - shift_unit

            tx, ty = cx0, cy0
            while True:
                if dx == 1 and (tx + 1 >= b.width or b.v_walls[ty][tx + 1]): break
                if dx == -1 and (tx <= 0 or b.v_walls[ty][tx]): break
                if dy == 1 and (ty + 1 >= b.height or b.h_walls[ty + 1][tx]): break
                if dy == -1 and (ty <= 0 or b.h_walls[ty][tx]): break
                nx, ny = tx + dx, ty + dy
                if (nx, ny) in CENTER_BLOCK: break
                collision = False
                for c, pos in sim.items():
                    if pos[0] == nx and pos[1] == ny:
                        collision = True; break
                if collision: break
                tx, ty = nx, ny
            sim[rc] = [tx, ty]

            sx = ox + cx0 * cs + cs // 2 + sh
            sy = oy + cy0 * cs + cs // 2 + sh
            ex = ox + tx * cs + cs // 2 + sh
            ey = oy + ty * cs + cs // 2 + sh
            if (sx, sy) == (ex, ey): continue
            pygame.draw.line(self.screen, COLORS[rc], (sx, sy), (ex, ey),
                             max(2, cs // 10))
            head = max(6, cs // 5)
            if dx == 1:
                pts = [(ex, ey), (ex - head, ey - head), (ex - head, ey + head)]
            elif dx == -1:
                pts = [(ex, ey), (ex + head, ey - head), (ex + head, ey + head)]
            elif dy == 1:
                pts = [(ex, ey), (ex - head, ey - head), (ex + head, ey - head)]
            else:
                pts = [(ex, ey), (ex - head, ey + head), (ex + head, ey + head)]
            pygame.draw.polygon(self.screen, COLORS[rc], pts)

            mx = sx + (ex - sx) * 0.7
            my = sy + (ey - sy) * 0.7
            sr = max(7, cs // 4)
            pygame.draw.circle(self.screen, COLORS['White'], (int(mx), int(my)), sr)
            pygame.draw.circle(self.screen, COLORS['Black'], (int(mx), int(my)), sr, 1)
            t = self.font.render(str(idx + 1), True, COLORS['Black'])
            r = t.get_rect(center=(int(mx), int(my)))
            self.screen.blit(t, r)

    def _draw_direction_buttons(self, robot):
        cs = self.cell_size
        rx, ry = self.board.robots[robot]
        cx, cy = self.cell_center_px(rx, ry)
        offset = int(cs * 1.1)
        size = max(28, int(cs * 0.8))
        rcolor = COLORS[robot]

        positions = {
            'up':    (cx, cy - offset),
            'down':  (cx, cy + offset),
            'left':  (cx - offset, cy),
            'right': (cx + offset, cy),
        }
        screen_w = self.screen.get_width()
        rects = {}
        for d, (bx, by) in positions.items():
            r = size // 2
            bx = max(r + 2, min(screen_w - r - 2, bx))
            by = max(self.margin_top + r + 2,
                     min(self.margin_top + self.board.height * cs - r - 2, by))
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*rcolor, 200), (r, r), r)
            pygame.draw.circle(surf, (*COLORS['Black'], 230), (r, r), r, 2)
            self._draw_arrow_glyph(surf, d, r, size)
            self.screen.blit(surf, (bx - r, by - r))
            rects[d] = pygame.Rect(bx - r, by - r, size, size)
        return rects

    def _draw_arrow_glyph(self, surf, direction, r, size):
        c = (245, 245, 245)
        a = max(6, size // 4)
        cx = cy = r
        if direction == 'up':
            pts = [(cx, cy - a), (cx - a, cy + a // 2), (cx + a, cy + a // 2)]
        elif direction == 'down':
            pts = [(cx, cy + a), (cx - a, cy - a // 2), (cx + a, cy - a // 2)]
        elif direction == 'left':
            pts = [(cx - a, cy), (cx + a // 2, cy - a), (cx + a // 2, cy + a)]
        else:
            pts = [(cx + a, cy), (cx - a // 2, cy - a), (cx - a // 2, cy + a)]
        pygame.draw.polygon(surf, c, pts)

    def _draw_spinner(self):
        cs = self.cell_size
        sw, sh = self.screen.get_size()
        cx = sw // 2
        cy = sh // 2
        r = max(20, cs)
        t = pygame.time.get_ticks() / 100.0
        for i in range(8):
            ang = t + i * (math.pi / 4)
            x = cx + math.cos(ang) * r
            y = cy + math.sin(ang) * r
            alpha = 60 + (i * 24) % 200
            dot = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(dot, (*COLORS['Black'], alpha), (6, 6), 5)
            self.screen.blit(dot, (int(x) - 6, int(y) - 6))

    def _draw_flash(self, flash):
        a = flash.alpha()
        if a <= 0: return
        s = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        s.fill((*flash.color, a))
        self.screen.blit(s, (0, 0))
