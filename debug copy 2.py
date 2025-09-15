import cv2
import numpy as np
import yaml
import os

# ========= 1) 填入你的内参（直接贴 calibrate 输出） =========
K = np.array([[1.15606416e+03, 0.00000000e+00, 6.77657233e+02],
              [0.00000000e+00, 1.13401624e+03, 3.56755428e+02],
              [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]], dtype=float)
D = np.array([ 0.17635026, -0.55319393, -0.00916703, -0.01075132,  0.26090491], dtype=float)

# ========= 2) 基本参数（按你的棋盘修改） =========
# 你前面如果使用的是“内角点 9x6”，这里就 (cols=9, rows=6)；如果其实是格子 9x6，则改为 (8,5)
cols, rows   = 8, 5          # 内角点数
square_size  = 25.0          # mm
img_path     = "20250913_163337_509660.jpg"   # 一张包含棋盘的图片（建议清晰、棋盘占画面大一些）
save_A_npy   = "A.npy"       # 输出的2x3矩阵
save_yaml    = "A.yaml"      # 同时保存到yaml（便于查看）
# =================================================

# ========= 3) 三点的机器人平面坐标 (mm) =========
# O = 左上角，I = O右邻角，J = O下邻角（相邻角点，沿棋盘列/行各前进1格）
# 用机械臂依次"轻触"这三个物理角点中心，记录 get_coords() 的 X、Y 填入
O_r = np.array([254.90, -128.90], dtype=float)   # TODO: 改成你实测的
I_r = np.array([236.10, -129.50], dtype=float)   # TODO: 改成你实测的（通常X+25）
J_r = np.array([257.90, -109.70], dtype=float)   # TODO: 改成你实测的（通常Y+25）
# =================================================

def undistort(img, K, D):
    return cv2.undistort(img, K, D)

def detect_uv(img, cols, rows):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 优先用更鲁棒的SB；失败则退回老API
    if hasattr(cv2, "findChessboardCornersSB"):
        corners = cv2.findChessboardCornersSB(gray, (cols, rows), flags=cv2.CALIB_CB_EXHAUSTIVE)
        if corners is not None and len(corners) == cols*rows:
            return corners.reshape(-1,2)
    ret, corners = cv2.findChessboardCorners(
        gray, (cols, rows),
        flags=cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE | cv2.CALIB_CB_FILTER_QUADS
    )
    if not ret:
        raise RuntimeError("未检测到棋盘角点，请检查 cols/rows 是否为 '内角点数'，或让棋盘更清晰/更大。")
    # 亚像素
    corners = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1),
                               (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-3))
    return corners.reshape(-1,2)

def build_XY_from_three_points(cols, rows, square_size, O_r, I_r, J_r):
    # 如果 I/J 不是相邻点（隔k格），这里要除以 (k*square_size)
    e_i = (I_r - O_r) / square_size  # 每跨1列的平移向量
    e_j = (J_r - O_r) / square_size  # 每跨1行的平移向量
    XY = []
    for j in range(rows):
        for i in range(cols):
            XY_ij = O_r + i*square_size*e_i + j*square_size*e_j
            XY.append(XY_ij)
    return np.asarray(XY, dtype=float)

def fit_A(uv, XY):
    U = np.c_[uv, np.ones(len(uv))]            # N×3
    A, _, _, _ = np.linalg.lstsq(U, XY, rcond=None)  # 3×2
    return A.T  # 2×3

def eval_err(A, uv, XY):
    U = np.c_[uv, np.ones(len(uv))]
    pred = (A @ U.T).T
    err  = pred - XY
    rmse_xy = np.sqrt((err**2).mean(axis=0))
    mean_rmse = np.linalg.norm(err, axis=1).mean()
    max_abs = np.abs(err).max()
    return rmse_xy, mean_rmse, max_abs

# ==== 主流程 ====
img = cv2.imread(img_path)
if img is None:
    raise FileNotFoundError(f"读不到图片: {img_path}")

img_u = undistort(img, K, D)
uv    = detect_uv(img_u, cols, rows)
XY    = build_XY_from_three_points(cols, rows, square_size, O_r, I_r, J_r)
A     = fit_A(uv, XY)

rmse_xy, mean_rmse, max_abs = eval_err(A, uv, XY)

print("A (2x3) =\n", A)
print("误差统计(mm): RMSE_x, RMSE_y =", rmse_xy, "  mean_RMSE =", mean_rmse, "  max_abs_err =", max_abs)

np.save(save_A_npy, A)
print(f"已保存: {save_A_npy}")

with open(save_yaml, "w") as f:
    yaml.dump({"A_2x3": A.tolist(),
               "square_size_mm": float(square_size),
               "cols_rows_inner_corners": [int(cols), int(rows)],
               "rmse_xy_mm": [float(rmse_xy[0]), float(rmse_xy[1])],
               "rmse_mean_mm": float(mean_rmse),
               "rmse_max_abs_mm": float(max_abs)}, f)
print(f"已保存: {save_yaml}")

# 使用示例
def pixel_to_xy(A, u, v):
    return (A @ np.array([u, v, 1.0]))[:2]

u0, v0 = uv[0]
X0, Y0 = pixel_to_xy(A, u0, v0)
print(f"示例: 角点0 预测XY=({X0:.2f},{Y0:.2f})  真值=({XY[0,0]:.2f},{XY[0,1]:.2f})")
