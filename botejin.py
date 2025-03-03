import math
import pyxel
import random  # 必要に応じてランダム選択にする場合など

def rotated_blt(
    img_bank: int,
    src_x: int,
    src_y: int,
    w: int,
    h: int,
    pivot_screen_x: float,
    pivot_screen_y: float,
    pivot_local_x: float,
    pivot_local_y: float,
    angle_deg: float,
):
    """
    pivot_local_x, pivot_local_y (画像のローカル座標) が
    pivot_screen_x, pivot_screen_y (画面座標) に固定されるように、
    angle_deg [度] 回転(反時計回り)して描画する。
    """
    angle_rad = math.radians(angle_deg)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)

    for i in range(w):
        for j in range(h):
            color = pyxel.images[img_bank].pget(src_x + i, src_y + j)
            if color == 0:
                continue

            dx = i - pivot_local_x
            dy = j - pivot_local_y
            rx = dx * cos_a - dy * sin_a
            ry = dx * sin_a + dy * cos_a

            sx = pivot_screen_x + rx
            sy = pivot_screen_y + ry
            pyxel.pset(round(sx), round(sy), color)

  
class App:
    def __init__(self):
        pyxel.init(160, 120, title="Rolling Animation Sample")
        pyxel.mouse(True)
        # botejin.pyxres はユーザ環境に合わせて読み込んでください
        pyxel.load("botejin.pyxres")

        # 画像として切り替える領域のリスト
        # (src_x, src_y, 幅, 高さ) ※例では上記3種類
        self.image_rects = [
            (0, 0, 13, 13, 0),    # 領域1: (0,0)～(12,12)
            (13, 0, 9, 9, 1),     # 領域2: (13,0)～(21,8)
            (22, 0, 11, 19, 2),   # 領域3: (22,0)～(32,18)
            (33, 0, 9, 15, 3),
            (42, 0, 13, 11, 4),
            (55, 0, 15, 15, 5)
        ]
        self.current_image_index = 0  # どの画像を使うか

        # 初期状態に戻す (画像領域も変更)
        self.reset_state()

        # 回転アニメ用の変数
        self.is_rotating = False
        self.angle_to_rotate = 0      # 残りの回転角度
        self.angle_per_frame = 15     # 1フレームあたりの回転角度(度)

        pyxel.run(self.update, self.draw)

    def reset_state(self):
        """初期状態に戻し、画像を切り替える"""
        # 画像領域を選択
        #self.src_x, self.src_y, self.img_w, self.img_h, self.sound = self.image_rects[self.current_image_index]
        image_index = random.randint(0, len(self.image_rects) - 1)
        self.src_x, self.src_y, self.img_w, self.img_h, self.sound = self.image_rects[image_index]
        # 次に使う画像のためのインデックス更新（リスト末尾なら先頭に）
        self.current_image_index = (self.current_image_index + 1) % len(self.image_rects)

        # 画像の四隅 (ローカル座標) の更新
        self.corners_local = [
            (0, 0),
            (self.img_w, 0),
            (self.img_w, self.img_h),
            (0, self.img_h),
        ]

        # pivot（回転軸）の初期設定: ここでは右下を初期軸として設定
        self.pivot_local_x = self.img_w      # 右下
        self.pivot_local_y = self.img_h
        # 画面上の位置（任意にオフセット調整）
        self.pivot_screen_x = 80 - 40
        self.pivot_screen_y = 60 - 40
        self.current_angle = 0
        
        self.is_rotating = False
        self.angle_to_rotate = 0

    def update(self):
        # マウス左クリックで回転トリガー
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and (not self.is_rotating):
            # 回転して「一番下かつ右」にある頂点を新たな軸とする
            self.set_new_pivot_to_lowest_right_corner()
            # 90度回転させる
            self.angle_to_rotate = 90
            self.is_rotating = True
            pyxel.play(0, self.sound, loop=False)

        # 回転アニメーション処理
        if self.is_rotating:
            if self.angle_to_rotate > 0:
                rotate_now = min(self.angle_to_rotate, self.angle_per_frame)
                self.current_angle += rotate_now
                self.angle_to_rotate -= rotate_now

            if self.angle_to_rotate <= 0:
                self.angle_to_rotate = 0
                self.is_rotating = False

        # 回転中でなければ、画像が画面外に出ていないかチェック
        if not self.is_rotating:
            self.check_bounds()

    def draw(self):
        pyxel.cls(0)
        rotated_blt(
            img_bank=0,
            src_x=self.src_x,
            src_y=self.src_y,
            w=self.img_w,
            h=self.img_h,
            pivot_screen_x=self.pivot_screen_x,
            pivot_screen_y=self.pivot_screen_y,
            pivot_local_x=self.pivot_local_x,
            pivot_local_y=self.pivot_local_y,
            angle_deg=self.current_angle
        )

    def set_new_pivot_to_lowest_right_corner(self):
        """
        現在の回転状態 (self.current_angle 回転) で、
        一番下でかつ一番右にある頂点を探し、その頂点を
        次回の回転軸 (pivot_local, pivot_screen) に設定する。
        """
        best_corner_local = None
        best_screen_x = 0
        best_screen_y = -999999

        for (cx, cy) in self.corners_local:
            sx, sy = self.get_screen_coords(cx, cy)
            # yが大きい＝下、かつ同じyならxが大きい＝右
            if (sy > best_screen_y) or (sy == best_screen_y and sx > best_screen_x):
                best_corner_local = (cx, cy)
                best_screen_x = sx
                best_screen_y = sy

        # 新たな回転軸として設定
        self.pivot_local_x, self.pivot_local_y = best_corner_local
        self.pivot_screen_x = best_screen_x
        self.pivot_screen_y = best_screen_y

    def get_screen_coords(self, local_x, local_y):
        """
        (local_x, local_y) (画像ローカル座標) が
        pivot_local を軸に current_angle 度回転したとき、
        画面上の座標 (sx, sy) を返す。
        """
        angle_rad = math.radians(self.current_angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        dx = local_x - self.pivot_local_x
        dy = local_y - self.pivot_local_y

        rx = dx * cos_a - dy * sin_a
        ry = dx * sin_a + dy * cos_a
        sx = self.pivot_screen_x + rx
        sy = self.pivot_screen_y + ry
        return sx, sy

    def check_bounds(self):
        """
        現在の画像の全4頂点の位置を取得し、
        画面内 (0～pyxel.width, 0～pyxel.height) に収まっているかチェック。
        画面外に出た場合は初期状態に戻す（かつ画像を切り替える）。
        """
        xs = []
        ys = []
        for (lx, ly) in self.corners_local:
            sx, sy = self.get_screen_coords(lx, ly)
            xs.append(sx)
            ys.append(sy)
        min_x = min(xs)
        max_x = max(xs)
        min_y = min(ys)
        max_y = max(ys)

        if (min_x < 0 or max_x > pyxel.width or
            min_y < 0 or max_y > pyxel.height):
            # 範囲外の場合、初期状態にリセット（画像も変更）
            self.reset_state()


App()
